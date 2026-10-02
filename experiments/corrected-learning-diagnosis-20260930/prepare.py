"""Offline corrected 28-task packet and existing-checkpoint inference specification."""
import argparse
from dataclasses import asdict
from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DATA = ROOT / 'resources/local/training-ready-v2-20260929/data'
RESULTS = DATA.parent / 'results'
OLD = ROOT / 'experiments/learning-diagnosis-20260929'
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / 'resources/local/hf-client-venv/Lib/site-packages'))
MANIFEST_SHA = '4ccf49623f1753efffc922a97f882cdbadbfcecabbda5ebccbe30e9f3e084dac'
ADAPTER_SHA = 'c2305fc9cdc1fb99a346e58c92ae2ba1faa030ff6961bf0be1452f75006a8df0'
PREFIX = 'mixed-supervision/157531204582c50f2d8f73aaa76ce8ac'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode()


def build():
    from cloud_pilot import bundle
    from jinja2.sandbox import ImmutableSandboxedEnvironment
    from tokenizers import Tokenizer
    bindings = {}
    def raw(path):
        content = path.read_bytes()
        bindings[path.relative_to(ROOT).as_posix()] = sha(content)
        return content
    def rows(path):
        return [json.loads(line) for line in raw(path).splitlines()]
    old_census = json.loads(raw(OLD / 'census.json'))
    assert sha(raw(OLD / 'diagnose.py')) == old_census['script_sha256']
    raw(OLD / 'REPORT.md')
    for name, expected in old_census['output_sha256'].items():
        assert sha(raw(OLD / name)) == expected, name
    old_refs = rows(OLD / 'references.jsonl')
    manifest_path = ROOT / 'experiments/training-ready-v2-20260929/data-manifest.json'
    manifest = json.loads(raw(manifest_path))
    loaded = {}
    for name in ('learning-projections.jsonl', 'pool.jsonl', 'train.jsonl', 'row-audit.jsonl', 'parent-map.jsonl'):
        content = raw(DATA / name)
        assert sha(content) == manifest['outputs'][name]['sha256']
        assert len(content) == manifest['outputs'][name]['bytes']
        loaded[name] = [json.loads(line) for line in content.splitlines()]
    cloud = json.loads(raw(RESULTS / 'manifest.json'))
    assert bindings[(RESULTS / 'manifest.json').relative_to(ROOT).as_posix()] == MANIFEST_SHA
    training_path = RESULTS / 'mixed/training/run.json'
    training = json.loads(raw(training_path))
    assert sha(training_path.read_bytes()) == cloud['files']['mixed/training/run.json']['sha256']
    assert training['status'] == 'completed' and training['completed_steps'] == 96 and training['consumed_slots'] == 1536
    assert training['stream_sha256'] == sha(encode(loaded['train.jsonl']).rstrip(b'\n'))
    assert training['ordered_ids'] == [r['id'] for r in loaded['train.jsonl']]
    recovery = json.loads(raw(RESULTS / 'recovery-check.json'))
    assert recovery['manifest_sha256'] == MANIFEST_SHA and recovery['small_results_sha256_verified']
    adapter = {name: cloud['files']['mixed/training/adapter/' + name]['sha256']
               for name in ('adapter_config.json', 'adapter_model.safetensors')}
    assert adapter['adapter_model.safetensors'] == ADAPTER_SHA
    from cloud_pilot import dev_assisted
    reference_manifest_path = DATA.parent / 'transfer-verified/trained-manifest.json'
    reference_manifest = json.loads(raw(reference_manifest_path))
    assert sha(reference_manifest_path.read_bytes()) == cloud['files']['trained-manifest.json']['sha256'] == dev_assisted.ADAPTER_MANIFEST_SHA256
    assert {name: reference_manifest['files']['training/adapter/' + name]['sha256']
            for name in adapter} == dev_assisted.ADAPTER_FILES
    spec = importlib.util.spec_from_file_location('corrected_prepare', manifest_path.with_name('prepare.py'))
    prep = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prep)
    raw(manifest_path.with_name('prepare.py'))
    projection = {r['id']: r for r in loaded['learning-projections.jsonl']}
    pool = {r['id']: r for r in loaded['pool.jsonl']}
    train = {r['id']: r for r in loaded['train.jsonl']}
    audit = {r['id']: r for r in loaded['row-audit.jsonl']}
    parents = {r['id']: r['output_id'] for r in loaded['parent-map.jsonl']}
    assert all(all(pool[k][field] == v[field] for field in v) for k, v in train.items())
    tokenizer_path = prep.old.TOKENIZER
    for name, expected in bundle.TOKENIZER_HASHES.items():
        assert sha(raw(tokenizer_path / name)) == expected
    tokenizer = Tokenizer.from_file(str(tokenizer_path / 'tokenizer.json'))
    config = json.loads((tokenizer_path / 'tokenizer_config.json').read_bytes())
    specials = [r['content'] for r in json.loads((tokenizer_path / 'tokenizer.json').read_bytes())['added_tokens'] if r['special']]
    env = ImmutableSandboxedEnvironment(trim_blocks=True, lstrip_blocks=True, extensions=['jinja2.ext.loopcontrols'])
    def reject(message):
        raise ValueError(message)
    env.globals['raise_exception'] = reject
    template = env.from_string((tokenizer_path / 'chat_template.jinja').read_text('utf-8'))
    ledger_path = ROOT / 'experiments/train-audit-20260927/qualified-v1/final-ledger.jsonl'
    ledger = {r['id']: r for r in rows(ledger_path)}
    ledger_manifest = json.loads(raw(ledger_path.with_name('manifest.json')))
    assert sha(ledger_path.read_bytes()) == ledger_manifest['files'][ledger_path.name]['sha256']
    assert sha(ledger_path.read_bytes()) == old_census['input_sha256'][ledger_path.relative_to(ROOT).as_posix()]
    inputs, refs = [], []
    for original in old_refs:
        key = parents[original['record_id']]
        row, check = projection[key], audit[key]
        prompt, answer = prep.prompt_answer(row)
        assert sha(prompt.encode()) == check['prompt_sha256']
        assert sha(answer.encode()) == check['answer_sha256']
        tokenized = prep.tokenize(row, tokenizer, template, config, specials)
        assert all(tokenized[k] == pool[key][k] for k in bundle.TOKEN_KEYS)
        prefix = tokenized['input_ids'][:tokenized['prompt_tokens']]
        assert sha(prep.js(prefix).encode()) == check['prefix_sha256']
        exposed = key in train
        if original['task'] != 'historical-control-fa':
            assert exposed, ('Auxiliary acquisition probe must be consumed', key)
        reference = dict(original, record_id=key, original_record_id=original['record_id'],
            learning=row['learning'], expected_training_answer=answer,
            corrected96_exact_record_exposed=exposed, corrected96_consumed_positions=[i for i,k in enumerate(training['ordered_ids'], 1) if k == key],
            corrected_row_audit=check, prompt_token_ids=prefix,
            corrected_target_changed=original['expected_training_answer'] != answer,
            exact_step280_target_parity=None, historical_reference_uncertainty_preserved=True)
        if original['task'] == 'historical-control-fa':
            proof = ledger[original['record_id']]
            assert proof == original['qualified_train_ledger']
            assert proof['source_sha256'] == sha(original['learning']['source'].encode())
            assert proof['target_sha256'] == sha(original['learning']['target'].encode())
            reference['exact_step280_target_parity'] = original['learning'] == row['learning']
        inputs.append({'case_id': original['case_id'], 'prompt': prompt})
        refs.append(reference)
    groups = defaultdict(list)
    for r in refs:
        groups[r['module']].append(r['case_id'])
    # Interleave two-case module blocks; every module has equally many first-arm positions.
    order = []
    for offset in range(0, max(map(len, groups.values())), 2):
        for ids in groups.values():
            order.extend(ids[offset:offset + 2])
    assert len(inputs) == len(refs) == len(order) == len(set(order)) == 28
    for ids in groups.values():
        assert sum(order.index(k) % 2 == 0 for k in ids) == len(ids) // 2
    payloads = {'inputs.jsonl': b''.join(encode(r) for r in inputs), 'references.jsonl': b''.join(encode(r) for r in refs)}
    binding = dict(inputs_sha256=sha(payloads['inputs.jsonl']), experiment_id=HERE.name, case_order=order,
        candidate_prefix=PREFIX, candidate_manifest_sha256=MANIFEST_SHA, candidate_adapter_files=adapter)
    payloads['binding.json'] = encode(binding)
    summary = dict(status='PREPARED_NOT_SUBMITTED', packet_records=28, scheduled_first_attempts=56,
        modules=dict(Counter(r['module'] for r in refs)), inputs_sha256=bindings,
        output_sha256={k: sha(v) for k,v in payloads.items()}, corrected_exposed_cases=sum(r['corrected96_exact_record_exposed'] for r in refs),
        nonexposed_case_ids=[r['case_id'] for r in refs if not r['corrected96_exact_record_exposed']],
        changed_target_case_ids=[r['case_id'] for r in refs if r['corrected_target_changed']],
        raw_unicode_preserved=True, runtime_canary_exercised=False, actual31B_runtime_exercised=False,
        remote_model_bytes_rehashed=False, inference_launched=False, heldout_answers_read=False,
        selection='Same purposive 28 cases; no replacements; nonexposed historical cases explicitly retained.',
        scoring='Frozen original REPORT module rubrics and whole-translation critical-error metric; no pooled accuracy, no new gold.',
        script_sha256=sha(Path(__file__).read_bytes()))
    payloads['census.json'] = encode(summary)
    return payloads


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--spec', action='store_true', help='Prepare local launcher spec only; no API calls')
    args = parser.parse_args()
    for name, content in build().items():
        path = HERE / name
        if args.check:
            assert path.read_bytes() == content, name
        else:
            if path.exists() and path.read_bytes() != content:
                raise FileExistsError('Refusing changed frozen output: ' + name)
            path.write_bytes(content)
    if args.spec:
        from cloud_pilot import hf_learning_eval
        spec, receipt = hf_learning_eval.prepare(HERE / 'inputs.jsonl', '20260930000000000000000000000001',
            corrected_binding=json.loads((HERE / 'binding.json').read_bytes()))
        spec['volumes'] = [asdict(volume) for volume in spec['volumes']]
        (HERE / 'job-spec.json').write_bytes(encode(spec))
        (HERE / 'job-receipt.json').write_bytes(encode(receipt))
    print('PASS: 28 corrected original-task prompts, exact audits/arrays/prefixes, exposure/ledger, 56 balanced first attempts; no inference')


if __name__ == '__main__':
    main()
