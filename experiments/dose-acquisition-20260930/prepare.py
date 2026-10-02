"""Reconstruct source-only dose packet and blocked job; never launch or authenticate."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.extend([str(ROOT / 'resources/local/train-fit-deps'), str(ROOT / 'resources/local/hf-client-venv/Lib/site-packages')])
from cloud_pilot import bundle, dev_assisted, dev_diagnostic, learning_eval, palref_eval, runtime, training_admission


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode()


def lines(path):
    return [json.loads(s) for s in path.read_text('utf-8').splitlines()]


def put(path, raw):
    if path.exists():
        if path.read_bytes() != raw:
            raise ValueError('Frozen output differs; review before replacing: ' + str(path))
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)


def packet():
    from transformers import AutoTokenizer
    tokenizer_path = ROOT / 'resources/local/cloud-pilot-qualified-20260927/tokenizer'
    runtime.checked_files(tokenizer_path, bundle.TOKENIZER_HASHES)
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, local_files_only=True, trust_remote_code=False)
    source = ROOT / 'experiments/corrected-learning-diagnosis-20260930'
    diagnostic = learning_eval.read_inputs(source / 'inputs.jsonl',
        '02c5ecc82e187847377d5891c31fcb9fc5fb0d3714ea4aa66e686c0a3fabce3c', versioned=True)
    diagnostic_refs = {r['case_id']: r for r in lines(source / 'references.jsonl')}
    cached_run = ROOT / 'experiments/nf4-diagnostic-20260930/live-execution/recovered/evaluation/run.json'
    cached = {r['case_id']: r for r in json.loads(cached_run.read_bytes())['prompts']}
    rows = []
    for i, row in enumerate(diagnostic):
        rows.append(dict(row, module=diagnostic_refs[row['case_id']]['module'],
                         arms=['dose96', 'dose192', 'dose384'] if i < 6 else ['dose384']))
    merit_path = ROOT / 'experiments/dev-diagnostic-20260927/inputs.jsonl'
    merit = dev_diagnostic.read_inputs(merit_path)
    prompt_ids_path = ROOT / 'resources/local/contextual-run-package/dev-prompt-identities.json'
    merit_ids = {r['id'].removesuffix(':plain'): r for r in json.loads(prompt_ids_path.read_bytes())}
    for row, condition in dev_assisted.schedule(merit):
        if condition == 'plain':
            rows.append(dict(case_id=row['id'], module='fixed_merit', messages=dev_assisted.messages(row, 'plain', []),
                             arms=['reference', 'dose384'], work_id=row['work_id'], record_id=row['record_id']))
    confirmation = lines(HERE / 'confirmation/inputs.jsonl')
    confirmation_refs = {r['case_id']: r for r in lines(HERE / 'confirmation/references.jsonl')}
    assert len(confirmation) == 5
    rows.extend(dict(r, module='confirmation', arms=['reference', 'dose384']) for r in confirmation)
    identities = []
    for row in rows:
        messages = row.get('messages', [{'role': 'user', 'content': row.get('prompt')}])
        ids = tokenizer.apply_chat_template(messages, tokenize=True, return_dict=False,
            add_generation_prompt=True, enable_thinking=False)
        digest = sha(dev_assisted.canonical(ids))
        expected = (cached[row['case_id']]['rendered_input_ids_sha256'] if row['case_id'].startswith('LD-')
                    else merit_ids[row['case_id']]['rendered_input_ids_sha256'] if row['module'] == 'fixed_merit'
                    else sha(dev_assisted.canonical(confirmation_refs[row['case_id']]['prompt_token_ids'])))
        if digest != expected:
            raise ValueError('Pinned prompt token prefix differs: ' + row['case_id'])
        identities.append(dict(case_id=row['case_id'], input_tokens=len(ids), rendered_input_ids_sha256=digest,
                               messages_sha256=sha(dev_assisted.canonical(messages))))
    schedule = [r['case_id'] + ':' + arm for arm in ('reference', 'dose96', 'dose192', 'dose384')
                for r in rows if arm in r['arms']]
    assert len(rows) == 57 and len(schedule) == len(set(schedule)) == 98
    raw = b''.join(encode(r) for r in rows)
    generation = {m: learning_eval.GENERATION for m in {r['module'] for r in rows}}
    generation['fixed_merit'] = dict(max_new_tokens=palref_eval.MAX_TOKENS,
        max_generation_seconds=palref_eval.CASE_SECONDS, seed=42)
    contract = dict(inputs_sha256=sha(raw), expected_outputs=98, evaluation_schedule=schedule,
                    prompt_identities=identities, generation_by_module=generation,
                    canary_seconds=60, finalization_seconds=60)
    put(HERE / 'inputs.jsonl', raw)
    put(HERE / 'packet-contract.json', encode(contract))
    sources = [source / 'inputs.jsonl', source / 'references.jsonl', merit_path, prompt_ids_path, cached_run,
               HERE / 'confirmation/inputs.jsonl', HERE / 'confirmation/references.jsonl',
               HERE / 'confirmation/selection.json', ROOT / 'cloud_pilot/dev_assisted.py',
               ROOT / 'cloud_pilot/palref_eval.py']
    check = dict(status='PASS', case_count=57, scheduled_outputs=98, training_performed=False,
        weights_downloaded=False, all_prompt_token_prefixes_verified=True,
        files={str(p.relative_to(ROOT)).replace('\\','/'): sha(p.read_bytes()) for p in sources},
        tokenizer_files=bundle.TOKENIZER_HASHES, packet_sha256=sha(raw))
    put(HERE / 'packet-validation.json', encode(check))
    return contract


def materialize():
    from cloud_pilot import hf_dose
    contract = packet()
    run_id = uuid.uuid4().hex
    spec, receipt = hf_dose.prepare(ROOT / 'resources/local/training-ready-v2-20260929/data/train.jsonl',
        ROOT / 'experiments/training-ready-v2-20260929/data-manifest.json', HERE / 'inputs.jsonl', contract, run_id)
    folder = HERE / 'execution-proposal'
    folder.mkdir()
    put(folder / 'job-spec.json', encode(training_admission.plain(spec)))
    put(folder / 'job-receipt.json', encode(receipt))
    put(folder / 'check.json', encode(dict(status='BLOCKED_DRAFT', run_id=run_id,
        job_sha256=receipt['training_admission']['job_sha256'],
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'): sha(p.read_bytes()) for p in
            [Path(__file__), HERE / 'PLAN.md', ROOT / 'cloud_pilot/hf_dose.py', ROOT / 'cloud_pilot/dose_run.py',
             ROOT / 'cloud_pilot/dose_train.py', HERE / 'packet-contract.json']},
        files_sha256={p.name: sha(p.read_bytes()) for p in folder.iterdir()})))
    return folder


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet-only', action='store_true')
    args = parser.parse_args()
    print(packet() if args.packet_only else materialize())
