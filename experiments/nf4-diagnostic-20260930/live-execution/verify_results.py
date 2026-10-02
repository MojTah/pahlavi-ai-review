"""Verify matched-NF4 outputs; jointly blind them with frozen BF16 outputs. Derived from the frozen BF16 verifier."""
from collections import Counter
from datetime import datetime
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import random
import statistics

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RECOVERED = HERE / 'recovered'
PACKET = ROOT / 'experiments/corrected-learning-diagnosis-20260930'


def read(path):
    return json.loads(path.read_bytes())


def rows(path):
    return [json.loads(line) for line in path.read_bytes().splitlines()]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    terminal, manifest = read(HERE / 'terminal.json'), read(RECOVERED / 'manifest.json')
    receipt = read(HERE.parent / 'execution-proposal/job-receipt.json')
    assert terminal['stage'] == 'COMPLETED'
    for key, item in manifest['files'].items():
        relative = Path(key)
        assert not relative.is_absolute() and '..' not in relative.parts
        raw = (RECOVERED / relative).read_bytes()
        assert len(raw) == item['bytes'] and sha(raw) == item['sha256']
    logged_manifest = [json.loads(x) for x in terminal['logs'] if x.startswith('{')]
    logged_manifest = next(x for x in logged_manifest if x.get('stage') == 'ready_to_persist')
    assert sha((RECOVERED / 'manifest.json').read_bytes()) == logged_manifest['manifest_sha256']
    assert manifest['run_id'] == receipt['run_id']
    assert all(manifest[k] == receipt[k] for k in manifest.keys() & receipt.keys())
    assert manifest['optimizer_updates'] == 0 and manifest['training_launched'] is False
    assert manifest['inputs_sha256'] == receipt['inputs_sha256'] == sha((PACKET / 'inputs.jsonl').read_bytes())
    outer = read(RECOVERED / 'evaluation/run.json')
    state = read(RECOVERED / 'evaluation/evaluation/run.json')
    identity = {k: v for k, v in outer.items() if k not in
                ('status', 'recorded_outputs', 'successful_outputs', 'final_adapters_unchanged', 'numerical_state')}
    assert sha(json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()) == state['identity_sha256']
    numerical = read(RECOVERED / 'evaluation/numerical-state.json')
    assert numerical == outer['numerical_state']
    assert numerical['condition'] == outer['numerical_condition'] == 'matched_nf4_doublequant_bf16_compute_nonquant_fp32'
    assert numerical['quantization'] == dict(load_in_4bit=True, quant_type='nf4', double_quant=True, compute_dtype='bfloat16')
    assert numerical['quantized_parameter_count'] > 0
    assert set(numerical['parameter_numel_by_dtype']) == {'torch.float32', 'torch.uint8'}
    assert numerical['nonquantized_parameter_dtype'] == 'float32'
    assert numerical['autocast_device'] == 'cuda' and numerical['autocast_dtype'] == 'bfloat16'
    assert numerical['adapter_autocast_dtype'] is True
    assert not any(numerical[k] for k in ('training', 'gradients_enabled', 'gradient_checkpointing', 'optimizer_updates'))
    previous = ROOT / 'experiments/readiness-repair-20260930/live-execution/recovered/evaluation/evaluation/predictions.jsonl'
    assert sha(previous.read_bytes()) == receipt['cached_bf16_predictions_sha256'] == 'f719d7e408d3db94afa2fb99cc77158aa732cd116e0970ae79229c91cfa24816'
    cached = rows(previous)
    predictions = rows(RECOVERED / 'evaluation/evaluation/predictions.jsonl')
    refs = {r['case_id']: r for r in rows(PACKET / 'references.jsonl')}
    inputs = {r['case_id']: r for r in rows(PACKET / 'inputs.jsonl')}
    expected = [c + ':' + a for i, c in enumerate(receipt['case_order'])
                for a in (('reference', 'candidate') if i % 2 == 0 else ('candidate', 'reference'))]
    assert len(set(expected)) == len(predictions) == 56
    assert state['schedule'] == expected == [p['id'] for p in predictions]
    assert state['status'] == 'completed' and state['recorded_outputs'] == state['attempted_outputs'] == 56
    assert state['successful_outputs'] == 56 and not state['unattempted_output_ids'] and state['active_output_id'] is None
    assert outer['final_adapters_unchanged'] is True and outer['optimizer_updates'] == 0
    assert state['generation'] == receipt['generation'] and state['enable_thinking'] is False
    for arm in ('reference', 'candidate'):
        assert state['canaries'][arm]['status'] == 'passed'
        assert state['adapters'][arm] == receipt[arm + '_adapter_files']
    for i, p in enumerate(predictions):
        ref = refs[p['case_id']]
        assert p['sequence'] == i + 1 and p['identity_sha256'] == state['identity_sha256']
        assert p['adapter_sha256'] == receipt[p['arm'] + '_adapter_files']['adapter_model.safetensors']
        assert p['prompt_sha256'] == sha(inputs[p['case_id']]['prompt'].encode())
        # Compare both arms with the exact token prefix recorded before generation.
        prompt = next(x for x in state['prompts'] if x['case_id'] == p['case_id'])
        assert p['rendered_input_ids_sha256'] == prompt['rendered_input_ids_sha256']
        assert p['rendered_input_ids_sha256'] == sha(json.dumps(ref['prompt_token_ids'], separators=(',', ':')).encode())
        audit = ref.get('corrected_row_audit')
        if audit:
            assert p['rendered_input_ids_sha256'] == audit['prefix_sha256']
        assert p['output_sha256'] == sha(p['text'].encode())
        assert p['output_tokens'] == len(p['output_token_ids']) > 0
        assert p['status'] == 'success' and not p['hit_output_cap_without_eos']
        assert p['output_token_ids'][-1] in state['eos_token_ids'] and p['stop_reason'] is None
        assert math.isfinite(p['elapsed_seconds']) and 0 < p['elapsed_seconds'] < 90
    assert len(cached) == 56
    for a,b in zip(predictions, cached):
        for key in ('id','case_id','arm','sequence','adapter_sha256','prompt_sha256','rendered_input_ids_sha256','input_tokens'):
            assert a[key] == b[key], key
    seconds = (datetime.fromisoformat(terminal['finished_at']) - datetime.fromisoformat(terminal['started_at'])).total_seconds()
    paired = {c: [next(p['text'] for p in predictions if p['case_id'] == c and p['arm'] == a)
                  for a in ('reference', 'candidate')] for c in refs}
    summary = dict(job_id=terminal['job_id'], provider_status=terminal['stage'], provider_run_seconds=seconds,
        conservative_compute_estimate_usd=str(Decimal(math.ceil(seconds / 60)) * Decimal('0.041667')),
        cost_is_invoice=False, recovered_bytes=sum(f['bytes'] for f in terminal['files']),
        remote_readback_hashes_verified=True, manifest_log_hash_verified=True, optimizer_updates=0,
        both_gpu_canaries_passed=True, final_adapters_unchanged=True, full_ordered_first_attempts=56,
        status_counts=dict(Counter(p['status'] for p in predictions)), caps_timeouts_missing=0,
        prompt_prefix_parity_verified=True, generation_seconds=sum(p['elapsed_seconds'] for p in predictions),
        generation_median_seconds=statistics.median(p['elapsed_seconds'] for p in predictions),
        generation_max_seconds=max(p['elapsed_seconds'] for p in predictions),
        output_tokens=sum(p['output_tokens'] for p in predictions), different_paired_texts=sum(a != b for a,b in paired.values()),
        semantic_quality_scored=False, no_weights_downloaded=True, matched_nf4_numerics_verified=True, paired_bf16_prefixes_equal=True)
    write(HERE / 'result-integrity.json', summary)
    blind, mapping = [], {}
    shuffled = [dict(p, precision='nf4') for p in predictions] + [dict(p, precision='bf16') for p in cached]
    random.Random(20260930112).shuffle(shuffled)
    for i, p in enumerate(shuffled):
        ref = refs[p['case_id']]
        bid = f'B{i + 1:03d}'
        evidence = {k: ref[k] for k in ('learning', 'expected_training_answer', 'existing_scoped_qualification', 'scope_gold', 'expert_certified') if k in ref}
        ledger = ref.get('qualified_train_ledger', {})
        if ledger:
            evidence['published_qualification'] = {k: ledger[k] for k in ('credit', 'edition', 'curation_alignment_scope', 'expert_status', 'disposition') if k in ledger}
            review = ledger.get('linguistic_review', {})
            evidence['linguistic_limits'] = {k: review[k] for k in ('qualifications', 'reason', 'meaning') if k in review}
        module = {'historical_context_retention': 'passage', 'targeted_sense_applicability': 'targeted_passage'}.get(ref['module'], ref['module'])
        blind.append(dict(blind_id=bid, module=module, prompt=inputs[p['case_id']]['prompt'], evidence=evidence, answer=p['text']))
        mapping[bid] = dict(case_id=p['case_id'], arm=p['arm'], module=ref['module'], precision=p['precision'], output_sha256=p['output_sha256'])
    assert len(mapping) == len(blind) == 112
    (HERE / 'blind-packet.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in blind), encoding='utf-8')
    write(HERE / 'blind-mapping.json', mapping)
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
