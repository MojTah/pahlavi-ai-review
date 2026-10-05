"""Freeze one source-only system-instruction comparison; no provider or training."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / 'resources/local/dictionary-faithfulness-20261005'
ORIGIN = ROOT / 'resources/local/dev-comparability-20261003/ab-inputs.jsonl'
ORIGIN_SHA = '3b4eb9298882868bf197cd45c8144704f9d5522b394e3f2296624a28d4809c76'
OLD_CONTRACT = ORIGIN.with_name('ab-contract.json')
OLD_CONTRACT_SHA = '71d386912ac9325891bc5121efd51c6ef79dda399c0e7f4dc3f6380675aec21d'
CASES = tuple('QUALITYDEV1-' + n for n in
    ('002', '003', '005', '006', '007', '008', '009', '010', '012', '013', '014', '015', '017', '020', '021'))
RULE = ('Do not add explanatory glosses or equate alternative dictionary meanings '
        'unless the source context supports the added meaning.')
TOK = ROOT / 'resources/local/cloud-pilot-qualified-20260927/tokenizer'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')


def lines(rows):
    return b''.join((json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n')
                    .encode('utf-8') for row in rows)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def origin():
    raw, contract_raw = ORIGIN.read_bytes(), OLD_CONTRACT.read_bytes()
    require(sha(raw) == ORIGIN_SHA and sha(contract_raw) == OLD_CONTRACT_SHA, 'Original input/contract changed')
    original = [json.loads(line) for line in raw.splitlines()]
    require([r['id'] for r in original] == [c + ':' + a for c in CASES for a in 'AB'], 'Original panel order differs')
    return {r['case_id']: r for r in original if r['arm'] == 'B'}, json.loads(contract_raw)


def validate_pairs(rows, controls):
    require([r['id'] for r in rows] == [c + ':' + a for c in CASES for a in 'AB'], 'Exactly 30 ordered pairs required')
    for control, candidate in zip(rows[::2], rows[1::2]):
        original = controls[control['case_id']]
        for row, arm in ((control, 'A'), (candidate, 'B')):
            require(set(row) == set(original) and row['arm'] == arm, 'Pair schema/arm differs')
            require(all(row[k] == original[k] for k in ('case_id', 'work_id', 'source_sha256', 'dictionary_group_count')),
                    'Source/work/full dictionary metadata differs')
            require([m['role'] for m in row['messages']] == ['system', 'user']
                    and row['messages'][1] == original['messages'][1], 'Source/dictionary user payload changed')
        require(control['messages'] == original['messages'], 'Control must equal the original dictionary prompt')
        expected = deepcopy(original['messages'])
        expected[0]['content'] += '\n' + RULE
        require(candidate['messages'] == expected, 'Candidate must add only the frozen system sentence')


def build():
    from jinja2.sandbox import ImmutableSandboxedEnvironment
    from tokenizers import Tokenizer
    controls, old = origin()
    for name, checksum in old['tokenizer_files'].items():
        require(sha((TOK / name).read_bytes()) == checksum, 'Frozen tokenizer changed: ' + name)
    config = json.loads((TOK / 'tokenizer_config.json').read_bytes())
    template = ImmutableSandboxedEnvironment().from_string((TOK / 'chat_template.jinja').read_text('utf-8'))
    tokenizer = Tokenizer.from_file(str(TOK / 'tokenizer.json'))
    rows = []
    for cid in CASES:
        for arm in 'AB':
            row = deepcopy(controls[cid])
            row.update(id=cid + ':' + arm, arm=arm)
            if arm == 'B':
                row['messages'][0]['content'] += '\n' + RULE
            text = template.render(messages=row['messages'], add_generation_prompt=True,
                enable_thinking=False, bos_token=config['bos_token'], tools=None)
            ids = tokenizer.encode(text, add_special_tokens=False).ids
            ids_sha = sha(json.dumps(ids, separators=(',', ':')).encode())
            if arm == 'A':
                require(len(ids) == controls[cid]['input_tokens'] and ids_sha == controls[cid]['input_ids_sha256']
                        and sha(text.encode()) == controls[cid]['rendered_text_sha256'], 'Actual control token replay differs')
            require(0 < len(ids) <= 8192 and len(ids) + 4096 <= 12288
                    and tokenizer.token_to_id('<unk>') not in ids, 'Capacity/unknown-token failure; never truncate')
            row.update(input_tokens=len(ids), input_ids_sha256=ids_sha,
                rendered_text_sha256=sha(text.encode()), eligible_without_truncation=True)
            rows.append(row)
    validate_pairs(rows, controls)
    data = lines(rows)
    schedule = [c + ':' + a for i, c in enumerate(CASES) for a in ('AB' if i % 2 == 0 else 'BA')]
    contract = dict(schema='DICTIONARY_FAITHFULNESS_V1', status='LOCAL_INPUTS_VERIFIED_RUNTIME_HOLD',
        protocol='dictionary-faithfulness-v1', source_preparer_sha256=sha(Path(__file__).read_bytes()),
        origin_inputs_sha256=ORIGIN_SHA, historical_ab_contract_sha256=OLD_CONTRACT_SHA,
        model_inputs_sha256=sha(data), model_id=old['model_id'], model_revision=old['model_revision'],
        adapter_step=280, adapter_files=old['adapter_files'], tokenizer_files=old['tokenizer_files'],
        dictionary_sha256=old['dictionary_sha256'], case_ids=list(CASES),
        case_work_bindings={cid: controls[cid]['work_id'] for cid in CASES},
        instruction=RULE, instruction_location='system content suffix, exactly newline plus instruction',
        arm_A='original complete dictionary messages, byte-identical model-visible control',
        arm_B='same full dictionary/source user data plus one universal system sentence',
        data_selection='all 15 previously exposed development passages; no case exclusions or reference answers added',
        schedule=schedule, planned_outputs=30, first_attempt_only=True, fresh_context_each_output=True,
        no_cached_outputs=True, no_postprocessing=True, all_dictionary_alternatives_preserved=True,
        precision='bf16_base_fp32_retained_lora', seed=42, do_sample=False, enable_thinking=False,
        attention='eager', input_cap_tokens=8192, max_new_tokens=4096, context_limit=12288,
        max_generation_seconds=90, timing_contract='dictionary-faithfulness-90s-v1',
        compute_seconds=6600, internal_seconds=7020, native_timeout_minutes=120,
        post_canary_admission_reserve_seconds=3420, no_truncation=True,
        input_tokens_range=[min(r['input_tokens'] for r in rows), max(r['input_tokens'] for r in rows)],
        longest_input_id=max(rows, key=lambda r: r['input_tokens'])['id'],
        proposed_compute_allowance_usd='5.01', live_rate_and_funding_required=True,
        primary_requires_all_30_valid_and_independent_recovery=True,
        scoring='unchanged semantic rubric; two fresh opaque30-record provisional reviews; 15 denominator per arm',
        continuation=dict(each_rater_min_net_accepted_gain=2, min_named_works_with_newly_accepted=2,
            no_critical_count_increase=True, no_accepted_to_critical=True),
        unresolved='Case017 negation-scope specialist check remains separate; no inserted answer or targeted correction',
        limits='One hypothesis chosen from familiar DEV failures; no unseen accuracy, significance, expert certification or weight improvement',
        generation_admitted=False, training_admitted=False, paid_run_admitted=False,
        credentials_accessed=False, provider_called=False,
        execution_missing=['separate closed runtime/scorer and exact SDK preview', 'independent readiness review',
            'exact run-specific credential/transfer/paid approval', 'fresh account/rate/idle/private/provider gates'])
    return {'model-inputs.jsonl': data, 'contract.json': encode(contract)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    files = build()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        path = OUTPUT / name
        if args.check or path.exists():
            require(path.read_bytes() == data, 'Refusing changed frozen artifact: ' + name)
        else:
            with path.open('xb') as stream:
                stream.write(data)
    contract = json.loads(files['contract.json'])
    print(json.dumps({'status': contract['status'], 'rows': 30, 'input_tokens_range': contract['input_tokens_range'],
        'artifact_sha256': {n: sha(d) for n, d in files.items()}, 'paid_run_admitted': False}, indent=2))


if __name__ == '__main__':
    main()
