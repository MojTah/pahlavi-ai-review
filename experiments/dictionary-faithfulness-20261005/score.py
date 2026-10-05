"""Offline immutable recovery, blind fresh faithfulness DEV15 A/B packets and descriptive scoring.

No provider access or semantic judgment. A recovery receipt is a lead's recorded
observation, not an authenticity guarantee or proof made by this offline tool.
"""
import argparse
from collections import Counter
from functools import lru_cache
import json
import math
from pathlib import Path, PurePosixPath
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'resources/local/hf-client-venv/Lib/site-packages'))
from cloud_pilot import hf_dictionary_faithfulness as hf_component, runtime
from scripts import prepare_blind_dev_assisted as prep
from scripts.score_blind_dev_assisted import validate_reviews

require, sha, encode, lines = prep.require, prep.sha, prep.json_bytes, prep.lines
PREVIEW = Path(__file__).with_name('preview.json')
CONTRACT = ROOT / 'resources/local/dictionary-faithfulness-20261005/contract.json'
INPUTS = CONTRACT.with_name('model-inputs.jsonl')
PROTOCOL = 'dictionary-faithfulness-v1'
RUBRIC_SHA = 'b21d70d8e1a92bd7fc1fbb2de73a9eaf7d856aeba0c396c18f9272c5369f1732'
TOKENIZER = ROOT / 'resources/local/cloud-pilot-qualified-20260927/tokenizer'
TOKENIZER_PINS = {
    'chat_template.jinja': 'ae53464bf3be25802b3a5b37def7fd89667067d7577049b3b2d74c4d8de4c6d4',
    'tokenizer.json': 'cc8d3a0ce36466ccc1278bf987df5f71db1719b9ca6b4118264f45cb627bfe0f',
    'tokenizer_config.json': '9f4fec4b1dc6ecddf8f4a92e9caea5971c0e67d81309f3f9066a2bee8c362633',
}
SEEDS = {'A': 2026100501, 'B': 2026100502}
MAX_BYTES = 16 * 1024**2
IDENTITY_FIELDS = ('protocol run_id inputs_sha256 script_hashes base_files model_id revision adapter_files adapter_step environment '
    'precision attention enable_thinking max_new_tokens max_generation_seconds context_limit seed do_sample eos_token_ids '
    'pad_token_id num_beams fresh_context_each_output optimizer_updates scoring_performed expert_adjudicated deadline_utc '
    'decode_controls timing_contract input_cap_tokens no_truncation first_attempt_only compute_seconds internal_seconds '
    'native_timeout_minutes case_ids case_work_bindings timeout_or_output_cap_primary_inconclusive contract_sha256 '
    'historical_ab_contract_unchanged').split()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def decode(data):
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'Duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=unique_pairs)


def decode_lines(data):
    require(not data or data.endswith(b'\n'), 'Partial JSONL tail; preserve and recover original evidence')
    return [decode(line) for line in data.splitlines() if line.strip()]


def safe_path(root, name):
    require(isinstance(name, str) and bool(name) and '\\' not in name and ':' not in name,
            'Unsafe artifact name')
    relative = PurePosixPath(name)
    require(not relative.is_absolute() and relative.as_posix() == name
            and all(part not in {'.', '..'} for part in relative.parts), 'Unsafe artifact path')
    path = root / name
    require(path.resolve().is_relative_to(root.resolve()) and not path.is_symlink(), 'Unsafe artifact escape')
    return path


def inventory(root):
    root = Path(root)
    require(root.is_dir() and not root.is_symlink(), 'Recovery folder missing or unsafe')
    paths = list(root.rglob('*'))
    for path in paths:
        require(not path.is_symlink() and path.resolve().is_relative_to(root.resolve()), 'Unsafe recovered tree')
    files = {p.relative_to(root).as_posix(): p for p in paths if p.is_file()}
    require(sum(p.stat().st_size for p in files.values()) <= MAX_BYTES, 'Closed evidence exceeds 16 MiB')
    require(len({name.casefold() for name in files}) == len(files), 'Case-colliding artifact inventory')
    return files


def reviewed_pins():
    """The lead freezes these identity records after review; never silently repin."""
    required = {
        'cloud_pilot/hf_dictionary_faithfulness.py', 'cloud_pilot/faithfulness_eval.py',
        'experiments/dictionary-faithfulness-20261005/preview.json',
        'resources/local/dictionary-faithfulness-20261005/contract.json',
        'resources/local/dictionary-faithfulness-20261005/model-inputs.jsonl',
    }
    snapshots = {}
    pins = {}
    for filename in ('review-pins.json', 'final-pins.json'):
        path = PREVIEW.with_name(filename)
        require(path.is_file(), 'Lead-frozen pin dependency missing: ' + filename)
        raw = path.read_bytes()
        current = decode(raw)
        require(isinstance(current, dict) and required <= set(current), 'Frozen pin coverage differs: ' + filename)
        if filename == 'final-pins.json':
            require('experiments/dictionary-faithfulness-20261005/score.py' in current,
                    'Final pins must bind this new scorer')
        for name, expected in current.items():
            require(isinstance(expected, str) and len(expected) == 64
                    and all(c in '0123456789abcdef' for c in expected), 'Invalid frozen source pin')
            require(sha(safe_path(ROOT, name).read_bytes()) == expected, 'Frozen source changed: ' + name)
            require(name not in pins or pins[name] == expected, 'Review/final pin conflict: ' + name)
            pins[name] = expected
        snapshots[filename] = raw
    return pins, snapshots


def load_preview():
    pins, snapshots = reviewed_pins()
    data = PREVIEW.read_bytes()
    require(sha((ROOT / 'scripts/score_blind_dev_assisted.py').read_bytes()) == RUBRIC_SHA,
            'Frozen rubric validator changed')
    preview = decode(data)
    run_id = preview.get('run_id')
    require(isinstance(run_id, str) and len(run_id) == 32 and all(c in '0123456789abcdef' for c in run_id)
            and preview['output_prefix'] == 'dictionary-faithfulness/' + run_id, 'Preview identity differs')
    pinned = {}
    require(set(preview['files']) == {'job-spec.json', 'prepared-receipt.json'}, 'Preview artifact coverage differs')
    for name, entry in preview['files'].items():
        raw = safe_path(ROOT, entry['path']).read_bytes()
        require(sha(raw) == entry['sha256'] and len(raw) == entry['bytes'], 'Preview file differs: ' + name)
        pinned[name] = raw
    receipt = decode(pinned['prepared-receipt.json'])
    require(receipt['run_id'] == run_id and receipt['output_prefix'] == preview['output_prefix'], 'Prepared preview differs')
    require(receipt['protocol'] == PROTOCOL and receipt['script_hashes'] == preview['script_hashes']
            and receipt['inputs_sha256'] == preview['frozen_messages_sha256'] == sha(INPUTS.read_bytes())
            and receipt['contract_sha256'] == preview['contract_sha256'] == sha(CONTRACT.read_bytes()),
            'Preview source pins differ')
    require(sha((ROOT / 'cloud_pilot/faithfulness_eval.py').read_bytes()) == preview['script_hashes']['faithfulness_eval.py']
            and sha(hf_component.helper_source()[0]) == preview['script_hashes']['component_helpers.py'],
            'Reviewed runtime scripts changed')
    require(receipt['schedule'] == hf_component.dictionary_schedule()
            and receipt['decode_controls'] == hf_component.dictionary_controls()
            and receipt['timing_contract'] == 'dictionary-faithfulness-90s-v1', 'Reviewed closed recipe differs')
    return preview, receipt, {'preview.json': data, **pinned, **snapshots}


def exposed_cases():
    contract, rows, refs, assessments, _ = prep.load_contract()
    rows = [row for row in rows if assessments[row['id']]['assessment'] == 'provisional_whole_translation']
    require(tuple(row['id'] for row in rows) == hf_component.DICTIONARY_CASES, 'Frozen DEV15 case order differs')
    works = dict(zip(hf_component.DICTIONARY_CASES, ('parsig:103',) * 4 + ('parsig:112',) * 5 + ('parsig:138',) * 4 + ('parsig:517',) * 2))
    require({row['id']: row['work_id'] for row in rows} == works, 'Frozen DEV15 work bindings differ')
    return contract, rows, refs, assessments, works


@lru_cache(maxsize=1)
def cached_tokenizer():
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER, local_files_only=True, trust_remote_code=False)
    require(len(tokenizer) == 262144 and set(tokenizer.get_vocab().values()) == set(range(262144)), 'Frozen tokenizer vocabulary IDs differ')
    return tokenizer


def verified_tokenizer():
    specimen = decode(CONTRACT.read_bytes())
    require(specimen['tokenizer_files'] == TOKENIZER_PINS, 'Frozen tokenizer contract differs')
    runtime.checked_files(TOKENIZER, TOKENIZER_PINS)
    return cached_tokenizer()


def load_closed(recovered_dir, recovery_receipt):
    """Check every local final byte; do not manufacture independent remote verification."""
    root = Path(recovered_dir)
    observed = inventory(root)
    require('manifest.json' in observed, 'Closed manifest missing')
    raw = {name: path.read_bytes() for name, path in observed.items()}
    manifest = decode(raw['manifest.json'])
    require(manifest.get('schema_version') == 1 and isinstance(manifest.get('files'), dict), 'Closed manifest schema differs')
    require(set(raw) == {'manifest.json', *manifest['files']}, 'Closed manifest/full inventory differs')
    objects = {'manifest.json': {'sha256': sha(raw['manifest.json']), 'bytes': len(raw['manifest.json'])}}
    for name, entry in manifest['files'].items():
        safe_path(root, name)
        require(name != 'manifest.json' and set(entry) == {'sha256', 'bytes'}
                and type(entry['bytes']) is int and entry['bytes'] >= 0, 'Invalid manifest file entry')
        require(len(raw[name]) == entry['bytes'] and sha(raw[name]) == entry['sha256'], 'Closed artifact hash/size differs: ' + name)
        objects[name] = entry
    require({'evaluation/run.json', 'evaluation/predictions.jsonl', 'model-inputs.jsonl', 'contract.json'} <= set(raw), 'Final evidence incomplete')
    preview, expected, preview_raw = load_preview()
    # The reviewed exporter embeds settings, which omit this transport-only field.
    # The independently recovered receipt below still binds the exact prefix.
    require('output_prefix' not in manifest or manifest['output_prefix'] == expected['output_prefix'],
            'Manifest preview identity differs: output_prefix')
    for key in ('run_id', 'protocol', 'inputs_sha256', 'script_hashes', 'decode_controls',
                'timing_contract', 'contract_sha256', 'precision', 'schedule', 'planned_outputs',
                'compute_seconds', 'internal_seconds', 'native_timeout_minutes', 'training', 'automatic_retry',
                'trained_manifest_sha256', 'retained_files'):
        require(canonical(manifest.get(key)) == canonical(expected[key]), 'Manifest preview identity differs: ' + key)
    require(manifest.get('training_performed') is False and manifest.get('optimizer_updates') == 0, 'Inference-only manifest required')
    receipt_raw = Path(recovery_receipt).read_bytes()
    receipt = decode(receipt_raw)
    require(receipt.get('schema') == 'dictionary-faithfulness-recovery-v1'
            and receipt.get('run_id') == preview['run_id'] and receipt.get('output_prefix') == preview['output_prefix']
            and receipt.get('manifest_sha256') == objects['manifest.json']['sha256']
            and type(receipt.get('independent_remote_verified')) is bool
            and canonical(receipt.get('objects')) == canonical(objects), 'Recovery receipt byte pins or identity differ')
    require(raw['contract.json'] == CONTRACT.read_bytes() and sha(raw['contract.json']) == expected['contract_sha256'],
            'Recovered faithfulness contract differs')
    contract, cases, references, assessments, works = exposed_cases()
    inputs = decode_lines(raw['model-inputs.jsonl'])
    require(sha(raw['model-inputs.jsonl']) == expected['inputs_sha256']
            and [row['id'] for row in inputs] == [cid + ':' + arm for cid in works for arm in 'AB'], 'Frozen model inputs differ')
    for item in inputs:
        case = next(row for row in cases if row['id'] == item['case_id'])
        require(item['work_id'] == works[item['case_id']] and item['source_sha256'] == sha(case['source_text'].encode('utf-8')), 'Model source/work binding differs')
    run = decode(raw['evaluation/run.json'])
    identity = {key: run.get(key) for key in IDENTITY_FIELDS}
    require(sha(canonical(identity)) == run.get('identity_sha256'), 'Run identity SHA differs')
    fixed = dict(protocol=PROTOCOL, run_id=preview['run_id'], inputs_sha256=expected['inputs_sha256'],
        script_hashes=expected['script_hashes'], model_id=runtime.MODEL_ID, revision=runtime.REVISION,
        adapter_files=prep.shared.ADAPTER_FILES, adapter_step=280, precision=expected['precision'], attention='eager',
        enable_thinking=False, max_new_tokens=4096, max_generation_seconds=90, context_limit=12288,
        seed=42, do_sample=False, eos_token_ids=[1,106,50], pad_token_id=0, num_beams=1,
        fresh_context_each_output=True, optimizer_updates=0, scoring_performed=False, expert_adjudicated=False,
        decode_controls=expected['decode_controls'], timing_contract=expected['timing_contract'], input_cap_tokens=8192,
        no_truncation=True, first_attempt_only=True, compute_seconds=6600, internal_seconds=7020,
        native_timeout_minutes=120, case_ids=list(works), case_work_bindings=works,
        timeout_or_output_cap_primary_inconclusive=True, contract_sha256=expected['contract_sha256'],
        historical_ab_contract_unchanged=True)
    for key, value in fixed.items():
        require(canonical(run.get(key)) == canonical(value), 'Run closed controls differ: ' + key)
    predictions = decode_lines(raw['evaluation/predictions.jsonl'])
    accounting = hf_component.reconcile(root / 'evaluation', expected['schedule'])
    tokenizer = verified_tokenizer()
    require(run.get('successful_outputs') == sum(row['status'] in {'success', 'abstain'} for row in predictions), 'Run successful counter differs')
    if predictions:
        longest = max(inputs, key=lambda row: row['input_tokens'])
        canary = run.get('canary', {})
        require(canary.get('status') == 'passed' and canary.get('id') == longest['id']
                and canary.get('input_tokens') == longest['input_tokens']
                and canary.get('rendered_input_ids_sha256') == longest['input_ids_sha256']
                and canary.get('output_generated') is False and canary.get('experimental_attempts') == 0, 'Longest-input canary evidence differs')
    vocabulary_size = len(tokenizer)
    for row in predictions:
        token_ids = row['output_token_ids']
        require(all(type(token) is int and 0 <= token < vocabulary_size for token in token_ids), 'Output token ID outside frozen vocabulary')
        decoded_text = tokenizer.decode(token_ids, skip_special_tokens=True)
        require(decoded_text == row['text'] and sha(decoded_text.encode('utf-8')) == row['output_sha256'], 'Output token decode/text/hash differs')
        elapsed = row.get('elapsed_seconds')
        require(type(elapsed) in (float, int) and math.isfinite(elapsed) and elapsed >= 0, 'Invalid elapsed time')
        require(row.get('adapter_sha256') == prep.shared.ADAPTER_FILES['adapter_model.safetensors'], 'Output adapter identity differs')
        if row['status'] in {'success', 'abstain'}:
            require(elapsed <= 90 and row.get('primary_comparison_eligible') is True, 'Invalid successful attempt cap/eligibility')
            require((row['text'].strip() == '[UNRESOLVED]') == (row['status'] == 'abstain'), 'Abstention status differs')
    # Reconciliation reads originals: require those files still equal the pinned snapshot.
    require(set(inventory(root)) == set(raw) and all((root / name).read_bytes() == data for name, data in raw.items()), 'Recovery changed during validation')
    return dict(raw=raw, manifest=manifest, receipt=receipt, receipt_raw=receipt_raw, preview_raw=preview_raw,
                predictions=predictions, accounting=accounting, contract=contract, cases=cases,
                references=references, assessments=assessments, works=works)


def technical_summary(loaded):
    complete = loaded['accounting']['pipeline_complete'] is True
    remote = loaded['receipt']['independent_remote_verified'] is True
    return dict(status='READY_FOR_BLIND_REVIEW' if complete and remote else 'HOLD', screen_status='inconclusive',
        pipeline_complete=complete, independent_remote_verified=remote, primary_eligible=complete and remote,
        accounting=loaded['accounting'], per_output_status=loaded['accounting']['per_output_status'],
        expected_output_ids=hf_component.dictionary_schedule(), expert_adjudicated=False,
        recovery_caveat='Independent remote verification is a lead-trusted observation recorded in the receipt, not an offline authenticity guarantee. Mounted readback alone does not establish it.')


def build_files(loaded):
    files = {'lead-only/raw/' + name: data for name, data in loaded['raw'].items()}
    files.update({'lead-only/preview/' + name: data for name, data in loaded['preview_raw'].items()})
    files['lead-only/recovery-receipt.json'] = loaded['receipt_raw']
    files['lead-only/technical-summary.json'] = encode(technical_summary(loaded))
    mapping = []
    if loaded['accounting']['pipeline_complete'] is True:
        predictions = {row['id']: row for row in loaded['predictions']}
        cases = {row['id']: row for row in loaded['cases']}
        seen = set()
        for reviewer, seed in SEEDS.items():
            rng = random.Random(seed)
            order = list(hf_component.dictionary_schedule())
            rng.shuffle(order)
            packet = []
            for pid in order:
                output = predictions[pid]
                cid, arm = pid.split(':')
                case, ref, assessment = cases[cid], loaded['references'][cid], loaded['assessments'][cid]
                rid = 'r' + format(rng.getrandbits(128), '032x')
                require(rid not in seen, 'Opaque ID collision')
                seen.add(rid)
                packet.append(dict(review_id=rid, source_text=case['source_text'],
                    references={key: ref[key] for key in ('translations', 'edition', 'notes', 'reference_screen', 'expert_adjudicated')},
                    assessment=assessment['assessment'], constraint=assessment['constraint'], execution_status=output['status'],
                    output_text=output['text'], output_sha256=sha(output['text'].encode('utf-8'))))
                mapping.append(dict(reviewer=reviewer, review_id=rid, arm=arm, case_id=cid, work_id=case['work_id'],
                    prediction_id=pid, source_sha256=sha(case['source_text'].encode('utf-8')),
                    output_sha256=sha(output['text'].encode('utf-8')), execution_status=output['status']))
            files[f'reviewer-{reviewer}/packet.jsonl'] = lines(packet)
            files[f'reviewer-{reviewer}/INSTRUCTIONS.md'] = prep.instructions().replace(b'all 96 opaque records', b'all 30 opaque records')
        files['lead-only/mapping.jsonl'] = lines(mapping)
    provenance = dict(contract_sha256=prep.CONTRACT_SHA, source_files_sha256=loaded['contract']['source_files_sha256'],
        protocol=PROTOCOL, faithfulness_contract_sha256=sha(CONTRACT.read_bytes()),
        frozen_messages_sha256=sha(INPUTS.read_bytes()),
        runtime_reconcile_sha256=sha(Path(hf_component.__file__).read_bytes()), rubric_validator_sha256=RUBRIC_SHA,
        tokenizer_files_sha256=TOKENIZER_PINS,
        manifest_sha256=sha(loaded['raw']['manifest.json']), recovery_receipt_sha256=sha(loaded['receipt_raw']),
        preparer_sha256=sha(Path(__file__).read_bytes()), seeds=SEEDS,
        files={name: {'sha256': sha(data), 'bytes': len(data)} for name, data in files.items()})
    files['lead-only/provenance.json'] = encode(provenance)
    return files


def write_fresh(output_dir, files):
    prep.write_fresh(output_dir, files)
    require(all((Path(output_dir) / name).read_bytes() == data for name, data in files.items()), 'Written handoff byte check failed')


def prepare(recovered_dir, recovery_receipt, output_dir):
    loaded = load_closed(recovered_dir, recovery_receipt)
    write_fresh(output_dir, build_files(loaded))
    return technical_summary(loaded)


def summarize(mapping, packets, reviews, contract, technical):
    require(technical['pipeline_complete'] is True and technical['primary_eligible'] is True, 'Primary semantic scoring requires complete independently recovered outputs')
    require(len(mapping) == 60 and len(prep.unique(mapping, 'review_id')) == 60, 'Mapping coverage differs')
    result, decoded_reviews = {}, {}
    for reviewer in ('A', 'B'):
        ratings = validate_reviews(packets[reviewer], reviews[reviewer], expected_count=30)
        selected = [m for m in mapping if m['reviewer'] == reviewer]
        require(len(selected) == 30 and {m['review_id'] for m in selected} == set(ratings), 'Mapping review coverage differs')
        decoded = {'A': {}, 'B': {}}
        by_packet = prep.unique(packets[reviewer], 'review_id')
        for item in selected:
            packet = by_packet[item['review_id']]
            require(item['arm'] in decoded and item['case_id'] not in decoded[item['arm']], 'Duplicate or unknown mapped arm/case')
            require(item['prediction_id'] == item['case_id'] + ':' + item['arm']
                    and item['output_sha256'] == packet['output_sha256']
                    and item['source_sha256'] == sha(packet['source_text'].encode('utf-8'))
                    and item['execution_status'] == packet['execution_status'], 'Private mapping binding differs')
            decoded[item['arm']][item['case_id']] = {**item, **ratings[item['review_id']]}
        require(all(set(arm) == set(hf_component.DICTIONARY_CASES) for arm in decoded.values()), 'Fixed arm denominator differs')
        decoded_reviews[reviewer] = decoded
        old, new = decoded['A'], decoded['B']
        # EOS abstention is technically valid; true failed A outputs never reach this gate.
        gained = [cid for cid in old if old[cid]['execution_status'] in {'success', 'abstain'} and new[cid]['execution_status'] == 'success'
                  and old[cid]['judgment'] != 'accepted' and new[cid]['judgment'] == 'accepted']
        lost = [cid for cid in old if old[cid]['judgment'] == 'accepted' and new[cid]['judgment'] != 'accepted']
        regressions = [cid for cid in old if old[cid]['judgment'] == 'accepted' and new[cid]['judgment'] == 'critical_error']
        works = sorted({old[cid]['work_id'] for cid in gained})
        counts = {arm: dict(Counter(row['judgment'] for row in records.values())) for arm, records in decoded.items()}
        critical_change = counts['B'].get('critical_error', 0) - counts['A'].get('critical_error', 0)
        screen = contract['comparison']['screen']
        checks = dict(net_accepted_gain=len(gained) - len(lost) >= screen['both_reviewers_min_net_accepted_gain'],
            gains_in_multiple_named_works=len(works) >= screen['min_works_with_gains'],
            no_critical_increase=critical_change <= 0, no_accepted_to_critical=not regressions)
        result[reviewer] = dict(denominator_per_arm=15, counts=counts,
            accepted_counts={arm: counts[arm].get('accepted', 0) for arm in 'AB'},
            critical_counts={arm: counts[arm].get('critical_error', 0) for arm in 'AB'},
            newly_accepted=gained, lost_acceptance=lost, net_accepted_change=len(gained) - len(lost),
            works_with_newly_accepted=works, critical_count_change=critical_change, accepted_to_critical=regressions,
            by_work={work: {arm: dict(Counter(row['judgment'] for row in records.values() if row['work_id'] == work))
                     for arm, records in decoded.items()} for work in sorted({row['work_id'] for row in old.values()})},
            screen_checks=checks, screen_pass=all(checks.values()))
    agreement = {}
    for arm in 'AB':
        a, b = decoded_reviews['A'][arm], decoded_reviews['B'][arm]
        fields = ('judgment', 'supported_span_severity', 'unknown_span_handling', 'categories')
        disagreement = [dict(case_id=cid, work_id=a[cid]['work_id'],
            reviewer_A={key: a[cid][key] for key in fields},
            reviewer_B={key: b[cid][key] for key in fields})
            for cid in hf_component.DICTIONARY_CASES if any(a[cid][key] != b[cid][key] for key in fields)]
        agreement[arm] = dict(total=15, disagreements=disagreement,
            acceptance_agreement=sum((a[cid]['judgment'] == 'accepted') == (b[cid]['judgment'] == 'accepted') for cid in a))
    passes = all(result[r]['screen_pass'] for r in ('A', 'B'))
    return dict(status='CONTINUATION_SCREEN_PASS' if passes else 'HOLD', screen_status='pass' if passes else 'fail',
        semantic_continuation=passes, reviewers=result, reviewer_agreement=agreement, technical=technical, expert_adjudicated=False,
        limits='Two separate provisional fresh faithfulness fixed-DEV15 reviews. No significance, unseen generalization, expert certification, training admission or automatic promotion.')


def score(packet_dir, recovered_dir, recovery_receipt, output_dir, review_a=None, review_b=None):
    loaded = load_closed(recovered_dir, recovery_receipt)
    rebuilt = build_files(loaded)
    packet_dir = Path(packet_dir)
    for name, data in rebuilt.items():
        require(safe_path(packet_dir, name).read_bytes() == data, 'Packet/private mapping differs from recovered raw: ' + name)
    technical = technical_summary(loaded)
    files = dict(rebuilt)
    if not technical['primary_eligible']:
        summary = {**technical, 'semantic_continuation': False, 'reason': 'Primary scoring held: incomplete pipeline or no independent recovery receipt.'}
    else:
        packets, reviews, freeze, missing = {}, {}, {}, []
        for reviewer, explicit in (('A', review_a), ('B', review_b)):
            path = Path(explicit) if explicit is not None else packet_dir / f'reviewer-{reviewer}/reviews.jsonl'
            if not path.is_file():
                missing.append(reviewer)
                continue
            data = path.read_bytes()
            packets[reviewer] = decode_lines(rebuilt[f'reviewer-{reviewer}/packet.jsonl'])
            reviews[reviewer] = decode_lines(data)
            validate_reviews(packets[reviewer], reviews[reviewer], expected_count=30)
            files[f'reviewer-{reviewer}/reviews.jsonl'] = data
            freeze[reviewer] = dict(sha256=sha(data), bytes=len(data), rows=len(reviews[reviewer]), reviewer_type='AI', expert_adjudicated=False)
        if missing:
            summary = dict(status='HOLD', screen_status='inconclusive', semantic_continuation=False,
                missing_reviewers=missing, technical=technical, expert_adjudicated=False)
        else:
            summary = summarize(decode_lines(rebuilt['lead-only/mapping.jsonl']), packets, reviews, loaded['contract'], technical)
        summary['review_freeze'] = freeze
    summary['scorer_sha256'] = sha(Path(__file__).read_bytes())
    summary['packet_provenance_sha256'] = sha(rebuilt['lead-only/provenance.json'])
    summary['recovered_manifest_sha256'] = sha(loaded['raw']['manifest.json'])
    summary['recovery_receipt_sha256'] = sha(loaded['receipt_raw'])
    files['comparison.json'] = encode(summary)
    write_fresh(output_dir, files)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'score'))
    parser.add_argument('recovered_dir', type=Path)
    parser.add_argument('recovery_receipt', type=Path)
    parser.add_argument('output_dir', type=Path)
    parser.add_argument('--packet-dir', type=Path)
    parser.add_argument('--review-a', type=Path)
    parser.add_argument('--review-b', type=Path)
    args = parser.parse_args()
    if args.action == 'prepare':
        result = prepare(args.recovered_dir, args.recovery_receipt, args.output_dir)
    else:
        parser.error('--packet-dir is required for score') if args.packet_dir is None else None
        result = score(args.packet_dir, args.recovered_dir, args.recovery_receipt, args.output_dir, args.review_a, args.review_b)
    print(json.dumps({'status': result['status'], 'screen_status': result['screen_status']}, indent=2))
