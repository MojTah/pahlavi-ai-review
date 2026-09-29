"""Local blind DEV48 comparison of retained step280 and the fixed mixed continuation."""
import argparse
import json
import math
from pathlib import Path, PurePosixPath
import random
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloud_pilot import mixed_run as driver
from scripts import prepare_blind_dev_assisted as prep, score_blind_dev_assisted as scoring

require, sha, canonical = prep.require, prep.sha, prep.shared.canonical
EXP = ROOT / 'experiments/mixed-supervision-20260929'
GEMMA = ROOT / 'experiments/translation-review-20260928/lead-only/raw/gemma280'
TRAIN = ROOT / 'resources/local/mixed-supervision-20260929/data/train.jsonl'
TOKENIZER = ROOT / 'resources/local/cloud-pilot-qualified-20260927/tokenizer'
CONDITIONS = ('gemma280_plain', 'mixed96_plain')
PAIR = ' -> '.join(CONDITIONS)
SEEDS = {'A': 2026092901, 'B': 2026092902}
RUN_ID = 'ad548e0f8b7b454682dc2fd6c3298966'
PREPARATION_SHA = '129d8ec1d0c58ebb815517792af7694dfd1d0557fa3494629a3d13fa218eb933'
MUTABLE = {'identity_sha256', 'status', 'schedule', 'scheduled_outputs', 'attempted_outputs',
           'recorded_outputs', 'completed_outputs', 'completed_cases', 'active_output_id',
           'unattempted_output_ids', 'canary', 'error_type', 'error'}


def validate_recovery(folder, manifest_bytes, export, proof, preparation):
    require(proof.get('run_id') == preparation['run_id'] == RUN_ID
            and proof.get('manifest_sha256') == sha(manifest_bytes)
            and proof.get('provider_inventory_committed') is True
            and proof.get('model_weights_downloaded') is False
            and proof.get('mixed_status') == export.get('mixed_status'), 'Recovery proof binding differs')
    prefix, files, inventory = preparation['output_prefix'], export['files'], proof['provider_inventory']
    require(set(inventory) == {prefix + '/manifest.json', *(prefix + '/' + n for n in files)}, 'Provider inventory differs')
    require(inventory[prefix + '/manifest.json']['bytes'] == len(manifest_bytes)
            and inventory[prefix + '/manifest.json'].get('xet_hash'), 'Manifest is not provider committed')
    raw = {'export-manifest.json': manifest_bytes}
    small = []
    for name, entry in files.items():
        path = PurePosixPath(name)
        require(not path.is_absolute() and '..' not in path.parts and path.as_posix() == name
                and '\\' not in name and ':' not in name and type(entry.get('bytes')) is int
                and entry['bytes'] >= 0 and re.fullmatch('[a-f0-9]{64}', entry.get('sha256', '')), 'Unsafe export record')
        remote = inventory[prefix + '/' + name]
        require(remote.get('bytes') == entry['bytes'] and remote.get('xet_hash'), 'Artifact is not provider committed')
        if name.endswith(('.json', '.jsonl', '.md', '.log')):
            small.append(name)
            local = Path(folder) / name
            require(local.is_file() and not local.is_symlink()
                    and local.resolve().is_relative_to(Path(folder).resolve()), 'Missing/unsafe recovered artifact')
            raw[name] = local.read_bytes()
            require(len(raw[name]) == entry['bytes'] and sha(raw[name]) == entry['sha256'], 'Recovered artifact hash/size differs: ' + name)
        else:
            require(name in {'mixed/training/' + arm + '/adapter_model.safetensors'
                             for arm in ('adapter', 'bounded-adapter-step20')}, 'Unexpected binary export')
    require(sorted(proof.get('local_sha_verified_files', [])) == sorted(small), 'Verified small-file set differs')
    return raw


def validate_artifacts(top, training, evaluation, predictions, rows, preparation, train_rows, manifest, gemma_run, tokenizer):
    prompts = [{k: p[k] for k in ('id', 'input_tokens', 'rendered_input_ids_sha256')}
               for p in gemma_run['prompts'] if p['id'].endswith(':plain')]
    require(preparation['prompt_identities'] == prompts, 'Retained source-only prompt parity differs')
    expected = dict(experiment_id='mixed-supervision-20260929', settings=driver.SETTINGS,
        data_manifest_sha256=preparation['data_manifest_sha256'], train_sha256=preparation['train_sha256'],
        inputs_sha256=driver.frozen.INPUTS_SHA256, original_adapter_files=prep.shared.ADAPTER_FILES,
        original_adapter_manifest_sha256=prep.shared.ADAPTER_MANIFEST_SHA256, original_adapter_step=280,
        runner_sha256=preparation['script_hashes']['mixed_run.py'], script_hashes=preparation['script_hashes'],
        model_id=driver.runtime.MODEL_ID, model_revision=driver.runtime.REVISION, seed=42, decoding='greedy',
        enable_thinking=False, max_new_tokens=4096, evaluation_prompt='dev_assisted.messages(row, plain, [])',
        prompts=prompts, quality_validated=False, expert_adjudicated=False, scoring_performed=False)
    for key, value in expected.items():
        require(top.get(key) == evaluation.get(key) == value, 'Run identity differs: ' + key)
    for key in ('adapters', 'deadline_utc', 'environment'):
        require(top.get(key) == evaluation.get(key), 'Top/evaluation identity differs: ' + key)
    require(training.get('status') == 'completed' and training.get('settings') == driver.SETTINGS
            and training.get('runner_sha256') == preparation['script_hashes']['mixed_train.py']
            and training.get('completed_steps') == 96 and training.get('consumed_slots') == 1536
            and training.get('ordered_ids') == manifest['pilot']['selected_ids_in_order']
            and training.get('stream_sha256') == sha(canonical(train_rows))
            and training.get('parent_order_verified') is True and training.get('fresh_optimizer') is True
            and training.get('model_accepts_loss_kwargs') is False
            and training.get('loss_reduction') == 'mean of per-example supervised-token means'
            and training.get('accelerator_accumulation_steps') == 1, 'Training recipe/order differs')
    require(top.get('numerical_canary', {}).get('status') == 'passed'
            and top['numerical_canary']['adapter_sha256'] == training['initial_adapter_sha256']
            and training.get('canary_adapter_changed') is True
            and training.get('admission', {}).get('admitted') is True
            and training['admission']['canary_steps'] == 20
            and training['final_adapter_sha256'] != training['initial_adapter_sha256'], 'Training canary/lineage differs')
    require(top.get('adapters') == {'candidate': dict(files=training['adapter_files'],
            final_tensor_sha256=training['final_adapter_sha256'], new_phase_steps=96, original_adapter_step=280)}, 'Adapter lineage differs')
    require(training['adapter_files']['adapter_config.json'] == prep.shared.ADAPTER_FILES['adapter_config.json'], 'Adapter architecture differs')
    identity = {k: v for k, v in evaluation.items() if k not in MUTABLE}
    require(sha(canonical(identity)) == evaluation.get('identity_sha256'), 'Evaluation identity hash differs')
    ordered = [r for r, arm in prep.shared.schedule(rows) if arm == 'plain']
    ids = [r['id'] + ':candidate' for r in ordered]
    require(top.get('status') in {'completed', 'incomplete'} and evaluation.get('status') in {'completed', 'incomplete'}
            and evaluation.get('schedule') == ids and evaluation.get('scheduled_outputs') == 24, 'Evaluation schedule/state differs')
    for value, label in ((top, 'top'), (training, 'training'), (evaluation, 'evaluation')):
        prep.first_attempt(value, label)
    prep.unique(predictions)
    require([p['id'] for p in predictions] == ids[:len(predictions)] and len(predictions) <= 24, 'First-attempt order differs')
    require(evaluation.get('attempted_outputs') == evaluation.get('recorded_outputs') == len(predictions)
            and evaluation.get('active_output_id') is None
            and evaluation.get('unattempted_output_ids') == ids[len(predictions):], 'Attempt coverage differs')
    completed, vocab_size = 0, tokenizer.get_vocab_size()
    for i, (p, row, prompt) in enumerate(zip(predictions, ordered, prompts), 1):
        prep.first_attempt(p, p['id'])
        require((p.get('case_id'), p.get('record_id'), p.get('work_id'), p.get('arm'), p.get('condition'), p.get('sequence'))
                == (row['id'], row['record_id'], row['work_id'], 'candidate', 'candidate', i), 'Prediction identity differs')
        require(p.get('input_sha256') == sha(row['source_text'].encode())
                and p.get('identity_sha256') == evaluation['identity_sha256']
                and p.get('adapter_sha256') == training['adapter_files']['adapter_model.safetensors'], 'Source/run/adapter hash differs')
        require(all(p.get(k) == prompt[k] for k in ('input_tokens', 'rendered_input_ids_sha256')), 'Prediction prompt parity differs')
        tokens, text, elapsed, status = p.get('output_token_ids'), p.get('text'), p.get('elapsed_seconds'), p.get('status')
        require(isinstance(tokens, list) and all(type(t) is int and 0 <= t < vocab_size for t in tokens)
                and p.get('output_tokens') == len(tokens) <= 4096, 'Output token count differs')
        require(isinstance(text, str) and text == tokenizer.decode(tokens, skip_special_tokens=True)
                and p.get('output_sha256') == sha(text.encode()), 'Output text/token/hash differs')
        require(type(elapsed) in (int, float) and math.isfinite(elapsed) and elapsed >= 0
                and status in {'success', 'abstain', 'timeout', 'error'}, 'Invalid execution outcome')
        cap = len(tokens) == 4096 and tokens[-1] not in driver.protocol.EOS
        require(p.get('hit_output_cap_without_eos') is cap, 'Output cap evidence differs')
        if status in {'success', 'abstain'}:
            require(elapsed <= 1200 and not cap and p.get('stop_reason') is None and text.strip()
                    and (status == 'abstain') == (text.strip() == '[UNRESOLVED]')
                    and tokens[-1] in driver.protocol.EOS, 'Invalid completed output')
            completed += 1
        require(i == len(predictions) or status in {'success', 'abstain'}, 'Output after failed first attempt')
    require(evaluation.get('completed_outputs') == evaluation.get('completed_cases') == completed, 'Completion counters differ')
    require(not predictions or evaluation.get('canary', {}).get('status') == 'passed', 'Missing evaluation canary')
    complete = len(predictions) == completed == 24
    if evaluation['status'] == 'completed':
        require(complete, 'False evaluation completion')
    if top['status'] == 'completed':
        require(complete and evaluation['status'] == 'completed' and top.get('training_status') == 'completed'
                and top.get('training_steps') == 96 and top.get('evaluation_completed_outputs') == 24, 'False top-level completion')
    return dict(complete=complete and top['status'] == evaluation['status'] == 'completed',
                training_steps=96, training_slots=1536, candidate_recorded_outputs=len(predictions),
                candidate_completed_outputs=completed, prompt_parity=True,
                adapter_tensor_validation='Server lineage and export hashes only; no local weights opened')


def load_sources(experiment=EXP, gemma_dir=GEMMA):
    from tokenizers import Tokenizer
    experiment = Path(experiment)
    contract, rows, references, assessments, witnesses = prep.load_contract()
    preparation_bytes = (experiment / 'execution-preparation.json').read_bytes()
    require(sha(preparation_bytes) == PREPARATION_SHA, 'Frozen preparation changed')
    preparation = json.loads(preparation_bytes)
    execution_bytes = (experiment / 'execution.json').read_bytes()
    execution = json.loads(execution_bytes)
    require(execution.get('run_id') == RUN_ID and execution.get('job_id') == '6abb82b6e2f3c356be0389a3'
            and execution.get('source_commit') == 'e0ba397629b4e9d9c4962600080ae0d751e829f9'
            and execution.get('spec_sha256') == preparation['spec_sha256']
            and execution.get('output_prefix') == preparation['output_prefix'], 'Frozen launch differs')
    for name, digest in {**preparation['script_hashes'], **preparation['bootstrap_hashes']}.items():
        require(sha((ROOT / 'cloud_pilot' / name).read_bytes()) == digest, 'Launch helper changed: ' + name)
    recovered = experiment / 'recovered'
    manifest_bytes = (recovered / 'manifest.json').read_bytes()
    export = json.loads(manifest_bytes)
    recovery_bytes = (experiment / 'recovery.json').read_bytes()
    raw = validate_recovery(recovered, manifest_bytes, export, json.loads(recovery_bytes), preparation)
    for key in ('run_id', 'inputs_sha256', 'train_sha256', 'data_manifest_sha256', 'bundle_sha256',
                'trained_manifest_sha256', 'adapter_files', 'script_hashes', 'training_settings', 'prompt_identities', 'steps'):
        require(export.get(key) == preparation.get(key), 'Export/launch identity differs: ' + key)
    require(export.get('operation') == 'mixed_supervision' and export.get('quality_validated') is False, 'Export operation differs')
    train_rows, manifest = driver.read_data(TRAIN, recovered / 'data-manifest.json', preparation)
    top, training, evaluation = (json.loads(raw[n]) for n in ('mixed/run.json', 'mixed/training/run.json', 'mixed/evaluation/run.json'))
    for folder, field in (('adapter', 'adapter_files'), ('bounded-adapter-step20', 'canary_adapter_files')):
        prefix = 'mixed/training/' + folder + '/'
        require({n[len(prefix):] for n in export['files'] if n.startswith(prefix)} == set(training[field]), 'Adapter export inventory differs')
        for name, digest in training[field].items():
            require(export['files'][prefix + name]['sha256'] == digest and export['files'][prefix + name]['bytes'] > 0, 'Adapter export hash differs')
    driver.runtime.checked_files(TOKENIZER, driver.bundle.TOKENIZER_HASHES)
    tokenizer = Tokenizer.from_file(str(TOKENIZER / 'tokenizer.json'))
    gemma_run, gemma_predictions, gemma_raw = prep.load_run(gemma_dir, 'gemma280', rows, witnesses)
    predictions = prep.decode_lines(raw['mixed/evaluation/predictions.jsonl'])
    completion = validate_artifacts(top, training, evaluation, predictions, rows, preparation, train_rows, manifest, gemma_run, tokenizer)
    completion['retained_gemma_completed'] = gemma_run['status'] == 'completed' and gemma_run['completed_outputs'] == 48
    completion['complete'] &= completion['retained_gemma_completed'] and export.get('mixed_status') == 'complete'
    raw.update({'execution-preparation.json': preparation_bytes, 'execution.json': execution_bytes, 'recovery.json': recovery_bytes})
    raw.update({'gemma280/' + n: data for n, data in gemma_raw.items()})
    candidate = {p['case_id']: p for p in predictions}
    baseline = {p['case_id']: p for p in gemma_predictions if p['condition'] == 'plain'}
    records = {(condition, row['id']): source.get(row['id']) for condition, source in zip(CONDITIONS, (baseline, candidate)) for row in rows}
    return records, raw, completion, contract, rows, references, assessments


def build_files(records, raw, completion, contract, rows, references, assessments):
    files = {'lead-only/raw/' + n: data for n, data in raw.items()}
    for name in ('references.jsonl', 'assessment-contract.json', 'reviewer-clarification.json'):
        files['lead-only/frozen/' + name] = (prep.DEV / name).read_bytes()
    mapping, seen, source = [], set(), prep.unique(rows)
    for reviewer, seed in SEEDS.items():
        rng, order, packet = random.Random(seed), list(records), []
        rng.shuffle(order)
        for condition, cid in order:
            opaque = 'r' + format(rng.getrandbits(128), '032x')
            require(opaque not in seen, 'Opaque ID collision')
            seen.add(opaque)
            p, row, ref, assessment = records[condition, cid], source[cid], references[cid], assessments[cid]
            text, status = (p['text'], p['status']) if p is not None else ('', 'unattempted')
            packet.append(dict(review_id=opaque, source_text=row['source_text'],
                references={k: ref[k] for k in ('translations', 'edition', 'notes', 'reference_screen', 'expert_adjudicated')},
                assessment=assessment['assessment'], constraint=assessment['constraint'], execution_status=status,
                output_text=text, output_sha256=sha(text.encode())))
            mapping.append(dict(reviewer=reviewer, review_id=opaque, condition=condition, case_id=cid,
                work_id=row['work_id'], assessment=assessment['assessment'], execution_status=status,
                prediction_id=None if p is None else p['id'], output_present=p is not None,
                source_sha256=sha(row['source_text'].encode()), output_sha256=sha(text.encode())))
        require(len(packet) == 48, 'Exactly 48 blind records required')
        files[f'reviewer-{reviewer}/packet.jsonl'] = prep.lines(packet)
        files[f'reviewer-{reviewer}/INSTRUCTIONS.md'] = prep.instructions().replace(b'all 96 opaque records', b'all 48 opaque records')
    files['lead-only/mapping.jsonl'] = prep.lines(mapping)
    files['lead-only/provenance.json'] = prep.json_bytes(dict(status='LOCAL_BLIND_MIXED_DEV48_PREPARED',
        contract_sha256=prep.CONTRACT_SHA, conditions=CONDITIONS, seeds=SEEDS, reviewers=2, outputs_per_reviewer=48,
        completion=completion, expert_adjudicated=False, preparer_sha256=sha(Path(__file__).read_bytes()),
        reused_preparer_sha256=sha(Path(prep.__file__).read_bytes()), reused_scorer_sha256=sha(Path(scoring.__file__).read_bytes()),
        source_files_sha256=contract['source_files_sha256'], files={n: sha(data) for n, data in files.items()}))
    return files


def summarize(mapping, packets, reviews, contract, completion):
    require(len(mapping) == len(prep.unique(mapping, 'review_id')) == 96, 'Private mapping coverage differs')
    reports = {}
    for reviewer in SEEDS:
        ratings = scoring.validate_reviews(packets[reviewer], reviews[reviewer], expected_count=48)
        selected = [m for m in mapping if m['reviewer'] == reviewer]
        require({m['review_id'] for m in selected} == set(ratings), 'Mapping/review identity differs')
        by_packet, decoded = prep.unique(packets[reviewer], 'review_id'), {c: {} for c in CONDITIONS}
        for m in selected:
            p = by_packet[m['review_id']]
            require(m['condition'] in CONDITIONS and m['case_id'] not in decoded[m['condition']], 'Duplicate mapped case/condition')
            require(m['output_sha256'] == p['output_sha256'] and m['source_sha256'] == sha(p['source_text'].encode())
                    and m['assessment'] == p['assessment'] and m['execution_status'] == p['execution_status'], 'Mapping/packet mismatch')
            decoded[m['condition']][m['case_id']] = {**ratings[m['review_id']], **m}
        conditions = {}
        for condition, items in decoded.items():
            report = scoring.condition_report(list(items.values()))
            require((report['whole_denominator'], report['constrained_denominator']) == (15, 9), 'Fixed denominators differ')
            report['by_work'] = {w: scoring.condition_report([x for x in items.values() if x['work_id'] == w]) for w in sorted({x['work_id'] for x in items.values()})}
            conditions[condition] = report
        pair = scoring.paired_report(decoded[CONDITIONS[0]], decoded[CONDITIONS[1]], contract['comparison']['screen'], completion['complete'])
        pair['screen_checks']['required_pair_execution_complete'] = pair['screen_checks'].pop('full_four_condition_comparison_complete')
        reports[reviewer] = dict(conditions=conditions, paired={PAIR: pair})
    return dict(status='TWO_SEPARATE_PROVISIONAL_MIXED_DEV48_REVIEWS', reviewers=reports,
        both_reviewers_screen=all(reports[r]['paired'][PAIR]['screen_pass'] for r in SEEDS) if completion['complete'] else None,
        comparison_completion=completion, screen_status='assessed' if completion['complete'] else 'inconclusive',
        primary_pair=PAIR, contract_sha256=prep.CONTRACT_SHA, expert_adjudicated=False, not_palref_score=True,
        limits='Fixed exposed DEV; separate AI raters, no pooled score, significance, specialist certification or automatic promotion. The comparison does not isolate auxiliary data from further training.')


def prepare(output_dir, experiment=EXP, gemma_dir=GEMMA):
    loaded = load_sources(experiment, gemma_dir)
    files = build_files(*loaded)
    prep.write_fresh(output_dir, files)
    return dict(status='LOCAL_BLIND_MIXED_DEV48_PREPARED', completion=loaded[2], provenance_sha256=sha(files['lead-only/provenance.json']))


def score(packet_dir, output_dir, experiment=EXP, gemma_dir=GEMMA, review_a=None, review_b=None):
    loaded = load_sources(experiment, gemma_dir)
    rebuilt = build_files(*loaded)
    for name, data in rebuilt.items():
        require((Path(packet_dir) / name).read_bytes() == data, 'Frozen packet/evidence changed: ' + name)
    packets, reviews, freeze, files = {}, {}, {}, {}
    for r, explicit in (('A', review_a), ('B', review_b)):
        packets[r] = prep.decode_lines(rebuilt[f'reviewer-{r}/packet.jsonl'])
        data = (Path(explicit) if explicit else Path(packet_dir) / f'reviewer-{r}/reviews.jsonl').read_bytes()
        reviews[r] = prep.decode_lines(data)
        freeze[r] = dict(sha256=sha(data), rows=len(reviews[r]), reviewer_type='AI', expert_adjudicated=False)
        files[f'reviewer-{r}/reviews.jsonl'] = data
    summary = summarize(prep.decode_lines(rebuilt['lead-only/mapping.jsonl']), packets, reviews, loaded[3], loaded[2])
    summary.update(blind_review_freeze=freeze, packet_provenance_sha256=sha(rebuilt['lead-only/provenance.json']), scorer_sha256=sha(Path(__file__).read_bytes()))
    files['comparison.json'], files['blind-review-freeze.json'] = prep.json_bytes(summary), prep.json_bytes(freeze)
    prep.write_fresh(output_dir, files)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('prepare', 'score'):
        sub = commands.add_parser(name)
        if name == 'score':
            sub.add_argument('packet_dir', type=Path)
            sub.add_argument('--review-a', type=Path)
            sub.add_argument('--review-b', type=Path)
        sub.add_argument('output_dir', type=Path)
        sub.add_argument('--experiment', type=Path, default=EXP)
        sub.add_argument('--gemma-dir', type=Path, default=GEMMA)
    args = vars(parser.parse_args())
    command = args.pop('command')
    result = prepare(**args) if command == 'prepare' else score(**args)
    print(json.dumps({k: result[k] for k in ('status', 'completion', 'screen_status', 'both_reviewers_screen') if k in result}, indent=2))
