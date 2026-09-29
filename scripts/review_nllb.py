"""Local blind DEV72 preparation/scoring; no inference, cloud calls or semantic judging."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import prepare_blind_dev_assisted as prep, score_blind_dev_assisted as scoring
from cloud_pilot import nllb_train as nllb

EXP = ROOT / 'experiments/nllb-supervised-20260928'
RUNNER_SHA = '8a392db05c5a38ad75e7cc767bda05d3dc1218b9d61348d161f64fa757b7708d'
PACKAGE_SHA = '4ff0ae48c2de917af47525dc456d8d58604d914b3aea3a7e393dfa689e267229'
PACKAGE_MANIFEST_SHA = '3e6fe3f6a7327d1b725708c14b7c403a09be74592bd806fd0ddc6c2ead89de05'
CONDITIONS = ('nllb_initialized', 'nllb_trained', 'gemma280_plain')
PAIRS = (('gemma280_plain', 'nllb_trained'), ('nllb_initialized', 'nllb_trained'))
SEEDS = {'A': 2026092801, 'B': 2026092802}
require, sha = prep.require, prep.sha


def validate_nllb(run, predictions, rows, phase):
    """Validate a recorded first-attempt prefix; completed claims require full coverage."""
    require(phase in {'canary', 'continue'}, 'Unknown NLLB phase')
    for key, expected in dict(model=nllb.MODEL, revision=nllb.REVISION, settings=nllb.SETTINGS,
            train_sha256=nllb.TRAIN_SHA, dev_sha256=nllb.DEV_SHA, runner_sha256=RUNNER_SHA).items():
        require(run.get(key) == expected, 'NLLB identity differs: ' + key)
    prep.first_attempt(run, 'NLLB run')
    expected = [(row, arm) for arm in (('initialized',) if phase == 'canary' else ('initialized', 'trained')) for row in rows]
    prep.unique(predictions)
    require([p['id'] for p in predictions] == [r['id'] + ':' + arm for r, arm in expected[:len(predictions)]]
            and len(predictions) <= len(expected), 'NLLB first-attempt order/coverage differs')
    require(type(run.get('step')) is int and 0 <= run['step'] <= (20 if phase == 'canary' else 700), 'Invalid NLLB step')
    require(run.get('quality_validated') is False, 'Runtime must not certify translation quality')
    completed_status = 'canary_complete' if phase == 'canary' else 'completed'
    require(run.get('status') in {completed_status, 'incomplete'}, 'Invalid NLLB run state')
    if run['status'] == completed_status:
        require(run['step'] == (20 if phase == 'canary' else 700) and len(predictions) == len(expected), 'Completed NLLB run has missing attempts')
        if phase == 'continue': require(run.get('completed_parent_exposures') == 11185, 'Final parent exposure differs')
    for i, (p, (row, arm)) in enumerate(zip(predictions, expected)):
        prep.first_attempt(p, p['id'])
        require((p.get('case_id'), p.get('record_id'), p.get('work_id'), p.get('arm'), p.get('sequence')) ==
                (row['id'], row['record_id'], row['work_id'], arm, i % 24 + 1), 'NLLB prediction identity differs')
        require(p.get('input_sha256') == sha(row['source_text'].encode()), 'NLLB source hash differs')
        require(p.get('status') in {'success', 'failed'} and isinstance(p.get('translation'), str), 'Invalid NLLB outcome')
        require(type(p.get('seconds')) in (int, float) and math.isfinite(p['seconds']) and p['seconds'] >= 0, 'Invalid NLLB timing')
        tokens = p.get('output_token_ids')
        if tokens is not None:
            require(isinstance(tokens, list) and all(type(t) is int and 0 <= t < 256215 for t in tokens)
                    and 1 <= len(tokens) <= 513 and tokens[0] == 2, 'Invalid generated token record')
        natural = (tokens is not None and 2 < len(tokens) < 513 and tokens[1] == 256053
                   and tokens[-1] == 2 and bool(p['translation'].strip()))
        if p['status'] == 'success':
            require(natural and p.get('failure') is None and not p.get('error_type'), 'NLLB success contradicts cap/EOS/empty checks')
        else:
            require(p.get('error_type') or (not natural and p.get('failure') == 'empty_or_cap_or_time_without_EOS'), 'NLLB failure lacks raw reason')
        if p.get('error_type'):
            require(i == len(predictions) - 1 and run['status'] == 'incomplete', 'Output after fail-closed runtime error')
        if arm == 'trained': require(run['step'] == 700, 'Trained evaluation before frozen final checkpoint')


def read_phase(directory, phase, rows):
    directory = Path(directory)
    raw = {}
    def get(name):
        data = (directory / name).read_bytes()
        raw[name] = data
        return json.loads(data)
    manifest = get('recovered/manifest.json')
    recovery, execution = get('recovery.json'), get('execution.json')
    require(recovery.get('manifest_sha256') == sha(raw['recovered/manifest.json']) and
            recovery.get('provider_inventory_committed') is True, 'Unverified cloud manifest/inventory')
    require(recovery.get('run_id') == execution.get('run_id') == manifest.get('run_id') and
            execution.get('phase') == manifest.get('phase') == phase, 'Cloud run/phase identity differs')
    require(isinstance(execution.get('source_commit'), str) and len(execution['source_commit']) == 40, 'Missing launch source commit')
    for key, expected in dict(operation='nllb_supervised', model=nllb.MODEL, revision=nllb.REVISION,
            settings=nllb.SETTINGS, train_sha256=nllb.TRAIN_SHA, dev_sha256=nllb.DEV_SHA,
            package_sha256=PACKAGE_SHA, package_manifest_sha256=PACKAGE_MANIFEST_SHA).items():
        require(manifest.get(key) == expected, 'Cloud experiment identity differs: ' + key)
    required = ('nllb/run.json', 'nllb/predictions.jsonl', 'package-manifest.json', 'status.json')
    require(set(required) <= set(recovery.get('local_sha_verified_files', [])), 'Small-record recovery incomplete')
    for name, entry in manifest['files'].items():
        path = (directory / 'recovered' / name).resolve()
        require(path.is_relative_to((directory / 'recovered').resolve()), 'Unsafe manifest path')
        provider = recovery['provider_inventory'].get(manifest['output_prefix'] + '/' + name, {})
        require(provider.get('bytes') == entry['bytes'] and bool(provider.get('xet_hash')), 'Committed provider artifact differs')
        if name in recovery['local_sha_verified_files']:
            data = path.read_bytes()
            require(len(data) == entry['bytes'] and sha(data) == entry['sha256'], 'Recovered evidence changed: ' + name)
            raw['recovered/' + name] = data
    require(all('recovered/' + name in raw for name in required), 'Required manifest evidence absent')
    package = json.loads(raw['recovered/package-manifest.json'])
    require(sha(raw['recovered/package-manifest.json']) == PACKAGE_MANIFEST_SHA and
            package['files']['nllb_train.py']['sha256'] == RUNNER_SHA and
            package['files']['evaluation-contract.json']['sha256'] == prep.CONTRACT_SHA and
            package['settings'] == nllb.SETTINGS and package['includes_dev_targets'] is False, 'Frozen source package differs')
    status = json.loads(raw['recovered/status.json'])
    require(all(manifest.get(k) == v for k, v in status.items()), 'Cloud status differs from manifest')
    run = json.loads(raw['recovered/nllb/run.json'])
    predictions = prep.decode_lines(raw['recovered/nllb/predictions.jsonl'])
    validate_nllb(run, predictions, rows, phase)
    expected_status = ('canary_complete' if phase == 'canary' else 'complete') if run['status'] != 'incomplete' else 'incomplete'
    require(manifest['nllb_status'] == recovery['nllb_status'] == expected_status, 'Technical completion claim differs')
    if expected_status != 'incomplete': require(manifest['completed_steps'] == run['step'], 'Cloud completed step differs')
    if expected_status != 'incomplete':
        name = 'recovered/nllb/model/training-state.json'
        require(name in raw, 'Completed run lacks recovered checkpoint identity')
        checkpoint = json.loads(raw[name])
        require(checkpoint.get('step') == run['step'] and checkpoint.get('settings') == nllb.SETTINGS,
                'Persisted checkpoint differs from evaluated training state')
    return run, predictions, manifest, raw


def load_sources(continue_dir, canary_dir, contract, rows, witnesses):
    require(sha(Path(nllb.__file__).read_bytes()) == RUNNER_SHA, 'Frozen NLLB runner changed')
    canary_run, baseline, canary_manifest, canary_raw = read_phase(canary_dir, 'canary', rows)
    run, predictions, manifest, continued_raw = read_phase(continue_dir, 'continue', rows)
    require(canary_run['status'] == 'canary_complete' and len(baseline) == 24, 'Complete original baseline required')
    require(manifest.get('canary_manifest_sha256') == sha(canary_raw['recovered/manifest.json']) and
            manifest.get('canary_prefix') == canary_manifest['output_prefix'], 'Continuation checkpoint lineage differs')
    require(predictions[:24] == baseline, 'Initialized first attempts changed across continuation')
    comparator_bytes = (EXP / 'COMPARATOR-CHECK.json').read_bytes()
    comparator = json.loads(comparator_bytes)
    require(comparator['status'] == 'pass' and comparator['condition'] == 'plain', 'Comparator qualification differs')
    for name, expected in comparator['files'].items():
        require(sha((ROOT / name).read_bytes()) == expected, 'Cached comparator evidence changed')
    paths = [ROOT / name for name in comparator['files'] if name.endswith('/gemma280/run.json')]
    require(len(paths) == 1, 'One frozen Gemma comparator required')
    gemma_run, gemma_predictions, gemma_raw = prep.load_run(paths[0].parent, 'gemma280', rows, witnesses)
    plain = {p['case_id']: p for p in gemma_predictions if p['condition'] == 'plain'}
    observed = prep.unique(predictions)
    records = {}
    for row in rows:
        for arm in ('initialized', 'trained'):
            p = observed.get(row['id'] + ':' + arm)
            records['nllb_' + arm, row['id']] = None if p is None else dict(p, text=p['translation'],
                execution_status='success' if p['status'] == 'success' else 'error')
        p = plain.get(row['id'])
        records['gemma280_plain', row['id']] = None if p is None else dict(p, execution_status=p['status'])
    complete = {}
    for condition in CONDITIONS:
        selected = [records[condition, row['id']] for row in rows]
        attempted = sum(p is not None for p in selected)
        complete[condition] = dict(attempted=attempted, scheduled=24,
            usable_execution=attempted == 24 and all(p['execution_status'] in {'success', 'abstain'} for p in selected))
    completion = dict(training_completed=run['status'] == 'completed' and run['step'] == 700,
        nllb_all_48_first_attempts_recorded=len(predictions) == 48, conditions=complete,
        gemma_original_run_completed=gemma_run['status'] == 'completed')
    files = {'lead-only/raw/COMPARATOR-CHECK.json': comparator_bytes}
    for family, raw in (('canary', canary_raw), ('continue', continued_raw), ('gemma280', gemma_raw)):
        files.update({'lead-only/raw/' + family + '/' + name: data for name, data in raw.items()})
    return records, completion, files


def build_files(continue_dir, canary_dir):
    contract, rows, references, assessments, witnesses = prep.load_contract()
    records, completion, files = load_sources(continue_dir, canary_dir, contract, rows, witnesses)
    mapping, seen = [], set()
    by_case = prep.unique(rows)
    for reviewer, seed in SEEDS.items():
        rng = random.Random(seed)
        order = list(records)
        rng.shuffle(order)
        packet = []
        for condition, cid in order:
            opaque = 'r' + format(rng.getrandbits(128), '032x')
            require(opaque not in seen, 'Opaque ID collision')
            seen.add(opaque)
            p, row, ref, assessment = records[condition, cid], by_case[cid], references[cid], assessments[cid]
            text, status = (p['text'], p['execution_status']) if p is not None else ('', 'unattempted')
            packet.append(dict(review_id=opaque, source_text=row['source_text'],
                references={k: ref[k] for k in ('translations', 'edition', 'notes', 'reference_screen', 'expert_adjudicated')},
                assessment=assessment['assessment'], constraint=assessment['constraint'], execution_status=status,
                output_text=text, output_sha256=sha(text.encode())))
            mapping.append(dict(reviewer=reviewer, review_id=opaque, condition=condition, case_id=cid,
                work_id=row['work_id'], assessment=assessment['assessment'], execution_status=status,
                prediction_id=None if p is None else p['id'], output_present=p is not None,
                raw_failure=None if p is None else {k: p[k] for k in ('failure', 'error_type', 'error', 'stop_reason') if k in p},
                source_sha256=sha(row['source_text'].encode()), output_sha256=sha(text.encode())))
        require(len(packet) == 72, 'Exactly 72 blind records required')
        files[f'reviewer-{reviewer}/packet.jsonl'] = prep.lines(packet)
        files[f'reviewer-{reviewer}/INSTRUCTIONS.md'] = prep.instructions().replace(b'all 96 opaque records', b'all 72 opaque records')
    files['lead-only/mapping.jsonl'] = prep.lines(mapping)
    provenance = dict(status='LOCAL_BLIND_DEV72_PREPARED', contract_sha256=prep.CONTRACT_SHA,
        conditions=CONDITIONS, seeds=SEEDS, outputs_per_reviewer=72, expert_adjudicated=False,
        completion=completion, preparer_sha256=sha(Path(__file__).read_bytes()),
        reused_preparer_sha256=sha(Path(prep.__file__).read_bytes()), reused_scorer_sha256=sha(Path(scoring.__file__).read_bytes()),
        source_files_sha256=contract['source_files_sha256'], files={k: sha(v) for k, v in files.items()})
    files['lead-only/provenance.json'] = prep.json_bytes(provenance)
    return files, contract, completion


def summarize(mapping, packets, reviews, contract, completion):
    require(len(mapping) == len(prep.unique(mapping, 'review_id')) == 144, 'Private mapping coverage differs')
    result = {}
    for reviewer in ('A', 'B'):
        ratings = scoring.validate_reviews(packets[reviewer], reviews[reviewer], expected_count=72)
        selected = [m for m in mapping if m['reviewer'] == reviewer]
        require({m['review_id'] for m in selected} == set(ratings), 'Mapping/review coverage differs')
        by_packet = prep.unique(packets[reviewer], 'review_id')
        decoded = {condition: {} for condition in CONDITIONS}
        for m in selected:
            p = by_packet[m['review_id']]
            require(m['condition'] in CONDITIONS and m['case_id'] not in decoded[m['condition']], 'Duplicate mapped case/condition')
            require(m['output_sha256'] == p['output_sha256'] and m['source_sha256'] == sha(p['source_text'].encode())
                    and m['assessment'] == p['assessment'] and m['execution_status'] == p['execution_status'], 'Mapping/packet mismatch')
            decoded[m['condition']][m['case_id']] = {**ratings[m['review_id']], **m}
        conditions, pairs = {}, {}
        for condition, items in decoded.items():
            require(len(items) == 24, 'Missing condition cases')
            report = scoring.condition_report(list(items.values()))
            require((report['whole_denominator'], report['constrained_denominator']) == (15, 9), 'Fixed denominators differ')
            report['by_work'] = {w: scoring.condition_report([x for x in items.values() if x['work_id'] == w]) for w in sorted({x['work_id'] for x in items.values()})}
            conditions[condition] = report
        for old, new in PAIRS:
            admitted = completion['training_completed'] and all(completion['conditions'][c]['usable_execution'] for c in (old, new))
            if old == 'gemma280_plain': admitted = admitted and completion['gemma_original_run_completed']
            report = scoring.paired_report(decoded[old], decoded[new], contract['comparison']['screen'], admitted)
            # Reuse the exact merit arithmetic; rename its legacy four-condition completion label only.
            report['screen_checks']['required_pair_execution_complete'] = report['screen_checks'].pop('full_four_condition_comparison_complete')
            pairs[old + ' -> ' + new] = report
        result[reviewer] = dict(conditions=conditions, paired=pairs)
    both = {}
    for old, new in PAIRS:
        key = old + ' -> ' + new
        values = [result[r]['paired'][key]['screen_pass'] for r in ('A', 'B')]
        both[key] = None if None in values else all(values)
    return dict(status='TWO_SEPARATE_PROVISIONAL_DEV72_REVIEWS', reviewers=result, both_reviewers_screen=both,
        comparison_completion=completion, primary_pair='gemma280_plain -> nllb_trained',
        descriptive_pair='nllb_initialized -> nllb_trained', contract_sha256=prep.CONTRACT_SHA,
        expert_adjudicated=False, not_palref_score=True,
        limits='Fixed exposed DEV; separate AI raters, no pooled score or specialist certification. Baseline failures remain in denominators but cannot veto a complete Gemma-versus-trained comparison.')


def prepare(continue_dir, output_dir, canary_dir=EXP / 'canary'):
    files, _, completion = build_files(continue_dir, canary_dir)
    prep.write_fresh(output_dir, files)
    return dict(status='LOCAL_BLIND_DEV72_PREPARED', completion=completion,
                provenance_sha256=sha(files['lead-only/provenance.json']))


def score(packet_dir, continue_dir, output_dir, canary_dir=EXP / 'canary', review_a=None, review_b=None):
    packet_dir = Path(packet_dir)
    rebuilt, contract, completion = build_files(continue_dir, canary_dir)
    for name, data in rebuilt.items():
        require((packet_dir / name).read_bytes() == data, 'Frozen packet/evidence changed: ' + name)
    packets, reviews, freeze, files = {}, {}, {}, {}
    for r, explicit in (('A', review_a), ('B', review_b)):
        packets[r] = prep.decode_lines(rebuilt[f'reviewer-{r}/packet.jsonl'])
        path = Path(explicit) if explicit is not None else packet_dir / f'reviewer-{r}/reviews.jsonl'
        data = path.read_bytes()
        reviews[r] = prep.decode_lines(data)
        freeze[r] = dict(sha256=sha(data), rows=len(reviews[r]), expert_adjudicated=False)
        files[f'reviewer-{r}/reviews.jsonl'] = data
    summary = summarize(prep.decode_lines(rebuilt['lead-only/mapping.jsonl']), packets, reviews, contract, completion)
    summary.update(blind_review_freeze=freeze, packet_provenance_sha256=sha(rebuilt['lead-only/provenance.json']),
                   scorer_sha256=sha(Path(__file__).read_bytes()))
    files['comparison.json'], files['blind-review-freeze.json'] = prep.json_bytes(summary), prep.json_bytes(freeze)
    prep.write_fresh(output_dir, files)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('prepare')
    p.add_argument('continue_dir', type=Path)
    p.add_argument('output_dir', type=Path)
    p.add_argument('--canary-dir', type=Path, default=EXP / 'canary')
    p = commands.add_parser('score')
    p.add_argument('packet_dir', type=Path)
    p.add_argument('continue_dir', type=Path)
    p.add_argument('output_dir', type=Path)
    p.add_argument('--canary-dir', type=Path, default=EXP / 'canary')
    p.add_argument('--review-a', type=Path)
    p.add_argument('--review-b', type=Path)
    args = vars(parser.parse_args())
    command = args.pop('command')
    value = prepare(**args) if command == 'prepare' else score(**args)
    print(json.dumps({k: value[k] for k in ('status', 'completion', 'both_reviewers_screen') if k in value}, indent=2))
