"""Closed frozen inference protocols from one retained BF16 adapter; no training."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import time

import runtime
from component_helpers import (ADAPTER_FILES, canonical, emit, prefill_canary,
                               publish_checked as publish, select_adapter, sha, verify_adapter,
                               verify_loaded_adapter)

CASES = ('KANHERI06', 'BERK25', 'TB3', 'ZAND301')
ORDERS = ('ABC', 'BCA', 'CAB', 'CBA')
PROTOCOLS = {'components-v1': (CASES, 'ABC', ORDERS, 887),
             'stages-v1': (CASES, 'IRS', ('IRS', 'RSI', 'SIR', 'SRI'), 1792),
             'own-analysis-v1': (('KANHERI01', 'AMOL1', 'BERLIN6'), 'DAP', ('DAP', 'APD', 'DAP'), 1536)}
DICTIONARY_CASES = tuple('QUALITYDEV1-' + number for number in
    ('002', '003', '005', '006', '007', '008', '009', '010', '012', '013', '014', '015', '017', '020', '021'))
DICTIONARY_WORKS = dict(zip(DICTIONARY_CASES,
    ('parsig:103',) * 4 + ('parsig:112',) * 5 + ('parsig:138',) * 4 + ('parsig:517',) * 2))
DICTIONARY_INPUTS_SHA256 = '3b4eb9298882868bf197cd45c8144704f9d5522b394e3f2296624a28d4809c76'
DICTIONARY_HISTORICAL_CONTRACT_SHA256 = '71d386912ac9325891bc5121efd51c6ef79dda399c0e7f4dc3f6380675aec21d'
DICTIONARY_TIMING_CONTRACT = 'dictionary-ab-90s-v1'
PROTOCOLS['dictionary-ab-v1'] = (DICTIONARY_CASES, 'AB',
    tuple('AB' if i % 2 == 0 else 'BA' for i in range(15)), 8192)
FIELDS = {'id', 'case_id', 'condition', 'prompt', 'prompt_tokens',
          'rendered_sha256', 'has_unknown_token'}
DICTIONARY_FIELDS = {'id', 'case_id', 'work_id', 'arm', 'source_sha256', 'messages',
    'input_tokens', 'rendered_text_sha256', 'input_ids_sha256', 'eligible_without_truncation',
    'dictionary_group_count'}


def dictionary_controls():
    """Prospective closed controls; the historical 1200-second proposal is unchanged."""
    return dict(input_cap_tokens=8192, max_new_tokens=4096, context_limit=12288,
        max_generation_seconds=90, slot_export_reserve_seconds=20, export_overhead_seconds=600,
        tail_reserve_seconds=120, first_attempt_admission_seconds=3420, no_truncation=True,
        first_attempt_only=True, timeout_or_output_cap_primary_inconclusive=True)


def dictionary_settings(settings):
    """Allow the new closed recipe only; callers cannot relax arbitrary protocols."""
    if settings.get('protocol', 'components-v1') != 'dictionary-ab-v1':
        return
    expected = dict(decode_controls=dictionary_controls(), timing_contract=DICTIONARY_TIMING_CONTRACT,
        compute_seconds=6600, internal_seconds=7020, native_timeout_minutes=120,
        planned_outputs=30, inputs_sha256=DICTIONARY_INPUTS_SHA256, schedule=schedule('dictionary-ab-v1'),
        reviewed_specimen_sha256=DICTIONARY_HISTORICAL_CONTRACT_SHA256,
        precision='bf16_base_fp32_retained_lora', training=False, automatic_retry=False)
    for key, value in expected.items():
        # Canonical bytes also reject booleans or floats masquerading as integer controls.
        if canonical(settings.get(key)) != canonical(value):
            raise ValueError('Closed dictionary settings differ: ' + key)


def read_inputs(path, expected_sha, protocol='components-v1'):
    cases, conditions, _, maximum = PROTOCOLS[protocol]
    raw = Path(path).read_bytes()
    if protocol == 'dictionary-ab-v1' and expected_sha != DICTIONARY_INPUTS_SHA256:
        raise ValueError('Frozen dictionary input checksum is not caller-selectable')
    if sha(raw) != expected_sha:
        raise ValueError('Frozen component input checksum differs')
    rows = [json.loads(line) for line in raw.splitlines()]
    separator = ':' if protocol == 'dictionary-ab-v1' else '-'
    expected = [case + separator + condition for case in cases for condition in conditions]
    if len(rows) != len(expected) or [r['id'] for r in rows] != expected:
        raise ValueError('Exactly the closed protocol inputs required')
    if protocol == 'dictionary-ab-v1':
        for row in rows:
            validate_dictionary_row(row)
        for a, b in zip(rows[::2], rows[1::2]):
            caution_a, payload_a = a['messages'][1]['content'].split('\n\n', 1)
            caution_b, payload_b = b['messages'][1]['content'].split('\n\n', 1)
            if (a['messages'][0] != b['messages'][0] or caution_a != caution_b
                    or a['source_sha256'] != b['source_sha256']
                    or json.loads(payload_a)['source_text'] != json.loads(payload_b)['source_text']):
                raise ValueError('Dictionary pair common instructions/source differ')
        return rows
    fields = FIELDS | {'dependency_id'} if protocol == 'own-analysis-v1' else FIELDS
    for r in rows:
        if (set(r) != fields or r['id'] != r['case_id'] + '-' + r['condition']
                or r['has_unknown_token'] is not False or not r['prompt'].strip()
                or type(r['prompt_tokens']) is not int or not 0 < r['prompt_tokens'] <= maximum):
            raise ValueError('Model-visible schema or capacity differs')
        if protocol == 'own-analysis-v1':
            dependency = r['case_id'] + '-A' if r['condition'] == 'P' else None
            if r['dependency_id'] != dependency: raise ValueError('Frozen analysis dependency differs')
    if protocol == 'own-analysis-v1':
        by_id = {r['id']:r for r in rows}
        for case in cases:
            if not by_id[case+'-P']['prompt'].startswith(by_id[case+'-D']['prompt']+'\n\n'):
                raise ValueError('P must retain the complete direct source prompt')
    return rows


def validate_dictionary_row(row):
    if (set(row) != DICTIONARY_FIELDS or row['case_id'] not in DICTIONARY_WORKS
            or row['arm'] not in ('A', 'B') or row['id'] != row['case_id'] + ':' + row['arm']
            or row['work_id'] != DICTIONARY_WORKS[row['case_id']]
            or row['eligible_without_truncation'] is not True
            or type(row['input_tokens']) is not int or not 0 < row['input_tokens'] <= 8192
            or type(row['dictionary_group_count']) is not int or row['dictionary_group_count'] < 0
            or any(not isinstance(row[key], str) or not re.fullmatch(r'[a-f0-9]{64}', row[key])
                   for key in ('source_sha256', 'rendered_text_sha256', 'input_ids_sha256'))):
        raise ValueError('Dictionary model-visible schema, source binding or capacity differs')
    messages = row['messages']
    if (not isinstance(messages, list) or len(messages) != 2
            or any(not isinstance(m, dict) or set(m) != {'role', 'content'}
                   or not isinstance(m['content'], str) or not m['content'].strip() for m in messages)
            or [m['role'] for m in messages] != ['system', 'user']):
        raise ValueError('Complete dictionary system/user messages required')
    try:
        caution, payload = messages[1]['content'].split('\n\n', 1)
        payload = json.loads(payload)
        if (not caution.strip() or set(payload) != {'source_text', 'dictionary_evidence'}
                or not isinstance(payload['source_text'], str) or not payload['source_text'].strip()
                or sha(payload['source_text'].encode()) != row['source_sha256']
                or not isinstance(payload['dictionary_evidence'], list)
                or len(payload['dictionary_evidence']) != row['dictionary_group_count']
                or (row['arm'] == 'A' and row['dictionary_group_count'] != 0)):
            raise ValueError('Dictionary payload source/evidence binding differs')
    except (TypeError, AttributeError, json.JSONDecodeError) as error:
        raise ValueError('Dictionary payload source/evidence binding differs') from error


def prepare_prompts(rows, tokenizer, protocol='components-v1'):
    prepared = {}
    for r in rows:
        dictionary = protocol == 'dictionary-ab-v1'
        if dictionary:
            validate_dictionary_row(r)
        messages = r['messages'] if dictionary else [{'role': 'user', 'content': r['prompt']}]
        rendered = tokenizer.apply_chat_template(messages, tokenize=False,
            add_generation_prompt=True, enable_thinking=False)
        ids = tokenizer.apply_chat_template(messages, tokenize=True, return_dict=False,
            add_generation_prompt=True, enable_thinking=False)
        if (sha(rendered.encode()) != r['rendered_text_sha256' if dictionary else 'rendered_sha256']
                or len(ids) != r['input_tokens' if dictionary else 'prompt_tokens'] or not ids
                or any(type(x) is not int or x < 0 or x == tokenizer.unk_token_id for x in ids)
                or (dictionary and sha(canonical(ids)) != r['input_ids_sha256'])
                or len(ids) + (4096 if dictionary else 512 if r.get('dependency_id') else 256)
                    > (12288 if dictionary else 2048)):
            raise ValueError('Actual tokenizer rendering differs; never truncate')
        prepared[r['id']] = ids
    return prepared


def schedule(protocol='components-v1'):
    cases, _, orders, _ = PROTOCOLS[protocol]
    separator = ':' if protocol == 'dictionary-ab-v1' else '-'
    return [case + separator + condition for case, order in zip(cases, orders) for condition in order]


def dependent_prompt(row, analysis, tokenizer):
    """Append first saved analysis verbatim; never substitute a corrected reading."""
    if (analysis['id'] != row['dependency_id'] or analysis['status'] != 'success'
            or not analysis['text'].strip() or analysis['hit_output_cap_without_eos']
            or sha(analysis['text'].encode()) != analysis['output_sha256']):
        raise ValueError('Only the intact successful first analysis can supply P')
    prompt = row['prompt'] + analysis['text']
    messages = [{'role':'user','content':prompt}]
    rendered = tokenizer.apply_chat_template(messages, tokenize=False,
        add_generation_prompt=True, enable_thinking=False)
    ids = tokenizer.apply_chat_template(messages, tokenize=True, return_dict=False,
        add_generation_prompt=True, enable_thinking=False)
    if (not ids or len(ids)+256 > 2048
            or any(type(x) is not int or x < 0 or x == tokenizer.unk_token_id for x in ids)):
        raise ValueError('Actual dynamic prompt fails capacity/token checks; never truncate')
    return prompt, ids, sha(rendered.encode())


def snapshot(output, remote, state, name, deadline):
    """Closed immutable phase/attempt files; mount readback is not remote proof."""
    runtime.write_json(output / 'run.json', state)
    source = output / 'snapshots' / name
    source.mkdir(parents=True, exist_ok=False)
    (source / 'run.json').write_bytes((output / 'run.json').read_bytes())
    if state.get('last_result') is not None:
        (source / 'result.json').write_bytes(canonical(state['last_result']) + b'\n')
        last = state['last_result']
        if last.get('analysis_output_id') and last.get('model_call_started'):
            # Preserve the resolved dependency input even if the final export fails.
            (source/'resolved-prompt.json').write_bytes(
                (output/'resolved-prompts'/f"{last['id']}.json").read_bytes())
    published = publish(source, remote / name, deadline, {'operation': 'component_inference_snapshot',
        'identity_sha256': state['identity_sha256'], 'training_performed': False})
    emit('component_snapshot_closed', name=name, manifest_sha256=published['manifest_sha256'],
         remote_inventory_verified=False)


def generate(model, tokenizer, rows, prepared, output, remote, state, deadline_utc, device='cuda'):
    import torch
    from transformers import DynamicCache, StoppingCriteria, StoppingCriteriaList, set_seed
    deadline = runtime.check_deadline(deadline_utc)
    monotonic_deadline = time.monotonic() + (deadline - datetime.now(timezone.utc)).total_seconds()
    by_id = {r['id']: r for r in rows}
    completed = {}
    count = len(state['schedule'])
    own_analysis = any(r.get('dependency_id') for r in rows)
    dictionary = state.get('protocol', 'components-v1') == 'dictionary-ab-v1'
    controls = dictionary_controls() if dictionary else None
    output_cap = 4096 if dictionary else 256
    if dictionary:
        if state['schedule'] != schedule('dictionary-ab-v1') or [r['id'] for r in rows] != [
                case + ':' + arm for case in DICTIONARY_CASES for arm in 'AB']:
            raise ValueError('Closed dictionary generation denominator differs')
        if canonical(state.get('decode_controls')) != canonical(controls):
            raise ValueError('Dictionary generation controls differ')
        state['primary_comparison_inconclusive'] = False

    def slot_reserve(remaining_slots):
        return remaining_slots * (90 + controls['slot_export_reserve_seconds']) + controls['tail_reserve_seconds']

    def attempt_snapshot(name):
        cutoff = monotonic_deadline
        if dictionary:
            cutoff = min(cutoff - controls['tail_reserve_seconds'],
                time.monotonic() + controls['slot_export_reserve_seconds'] / 2)
        snapshot(output, remote, state, name, cutoff)

    class Stop(StoppingCriteria):
        def __init__(self, reserve_cutoff=None):
            self.start, self.reason = time.monotonic(), None
            self.reserve_cutoff = reserve_cutoff
        def __call__(self, input_ids, scores, **kwargs):
            if time.monotonic() >= monotonic_deadline:
                self.reason = 'global_deadline'
            elif time.monotonic() - self.start >= 90:
                self.reason = 'case_timeout'
            elif self.reserve_cutoff is not None and time.monotonic() >= self.reserve_cutoff:
                self.reason = 'safe_reserve'
            return self.reason is not None

    # Admit every scheduled first slot after load/prefill, including export margins.
    required = controls['first_attempt_admission_seconds'] if dictionary else count * 90 + 180
    if monotonic_deadline - time.monotonic() < required:
        raise TimeoutError('Insufficient time for the full fixed first-attempt denominator')
    with (output / 'predictions.jsonl').open('x', encoding='utf-8') as stream:
        for index, key in enumerate(state['schedule']):
            runtime.check_deadline(deadline_utc)
            if dictionary and monotonic_deadline - time.monotonic() < slot_reserve(count-index):
                raise TimeoutError('Insufficient time for remaining first slots and safe export reserve')
            row = by_id[key]
            workflow_starts = state.setdefault('workflow_start_monotonic_seconds', {})
            if own_analysis and row['condition'] in {'D', 'A'}:
                workflow_starts[key] = time.monotonic()
            state.update(status='running', active_output_id=key, attempted_outputs=index + 1,
                         unattempted_output_ids=state['schedule'][index + 1:], last_result=None)
            attempt_snapshot(f'attempt-{index+1:02d}-start')
            start, new_ids, text, failure, cap = time.monotonic(), [], '', None, False
            generation_cutoff = (monotonic_deadline - slot_reserve(count-index-1)
                - controls['slot_export_reserve_seconds'] / 2) if dictionary else None
            stop = Stop(generation_cutoff)
            result = {'status': 'error'}
            prompt, input_ids = (row['messages'][1]['content'] if dictionary else row['prompt']), prepared[key]
            dependency_id = row.get('dependency_id')
            dependency = completed.get(dependency_id) if dependency_id else None
            called, rendered_hash = False, row['rendered_text_sha256' if dictionary else 'rendered_sha256']
            try:
                if dependency_id and (dependency is None or dependency['status'] != 'success'):
                    result.update(status='skipped_dependency', error_type='AnalysisUnavailable')
                    input_ids = []
                else:
                    if dependency_id:
                        prompt, input_ids, rendered_hash = dependent_prompt(row, dependency, tokenizer)
                        receipt = dict(prompt=prompt, input_token_ids=input_ids,
                            rendered_sha256=rendered_hash, analysis_output_id=dependency_id,
                            analysis_output_sha256=dependency['output_sha256'])
                        (output/'resolved-prompts').mkdir(exist_ok=True)
                        runtime.write_json(output/'resolved-prompts'/f'{key}.json', receipt)
                    select_adapter(model, 'reference', available=('reference',))
                    set_seed(42)
                    tokens = torch.tensor([input_ids], device=device)
                    if dictionary and stop(None, None):
                        raise TimeoutError('First slot stopped before dispatch to preserve the safe export reserve')
                    called = True
                    state['model_calls_started'] = state.get('model_calls_started', 0) + 1
                    runtime.write_json(output/'run.json', state)
                    with torch.inference_mode():
                        generated = model.generate(input_ids=tokens, attention_mask=torch.ones_like(tokens),
                            past_key_values=DynamicCache(), use_cache=True, do_sample=False, num_beams=1,
                            max_new_tokens=output_cap, pad_token_id=0, eos_token_id=[1, 106, 50],
                            stopping_criteria=StoppingCriteriaList([stop]))
                    if (generated.ndim != 2 or generated.shape[0] != 1
                            or not torch.equal(generated[0, :tokens.shape[1]], tokens[0])):
                        raise RuntimeError('Generated sequence changed its input prefix')
                    new_ids = generated[0, tokens.shape[1]:].tolist()
                    if len(new_ids) > output_cap: raise RuntimeError('Frozen output cap exceeded')
                    text = tokenizer.decode(new_ids, skip_special_tokens=True)
                    stop(None, None)
                    cap = len(new_ids) == output_cap and new_ids[-1] not in [1, 106, 50]
                    missing_eos = dictionary and bool(new_ids) and new_ids[-1] not in [1, 106, 50]
                    result['status'] = ('timeout' if stop.reason else 'error' if cap or missing_eos or not text.strip()
                                        else 'abstain' if text.strip() == '[UNRESOLVED]' else 'success')
                    if cap: result['error_type'] = 'OutputCapWithoutEOS'
                    elif missing_eos and not stop.reason: result['error_type'] = 'MissingEOS'
                    elif not text.strip(): result['error_type'] = 'EmptyOutput'
            except BaseException as error:
                failure = error
                result.update(status='error', error_type=type(error).__name__, error=str(error))
            result.update(id=key, case_id=row['case_id'], condition=row['arm' if dictionary else 'condition'], sequence=index+1,
                text=text, elapsed_seconds=time.monotonic()-start, output_token_ids=new_ids,
                output_tokens=len(new_ids), output_sha256=sha(text.encode()),
                identity_sha256=state['identity_sha256'], adapter_sha256=ADAPTER_FILES['adapter_model.safetensors'],
                input_tokens=len(input_ids), rendered_input_ids_sha256=sha(canonical(input_ids)),
                prompt_sha256=sha(prompt.encode()), hit_output_cap_without_eos=cap, stop_reason=stop.reason,
                model_call_started=called, analysis_output_id=dependency_id,
                analysis_output_sha256=dependency['output_sha256'] if dependency else None,
                rendered_sha256=rendered_hash if input_ids else None)
            if dictionary:
                result.update(arm=row['arm'], work_id=row['work_id'], source_sha256=row['source_sha256'],
                    messages=row['messages'], messages_sha256=sha(canonical(row['messages'])),
                    input_ids_sha256=sha(canonical(input_ids)), rendered_text_sha256=rendered_hash,
                    dictionary_group_count=row['dictionary_group_count'],
                    primary_comparison_eligible=result['status'] in {'success', 'abstain'})
                state['primary_comparison_inconclusive'] |= not result['primary_comparison_eligible']
            stream.write(canonical(result).decode() + '\n')
            stream.flush()
            os.fsync(stream.fileno())
            completed[key] = result
            state.update(recorded_outputs=index+1, active_output_id=None, last_result=result,
                successful_outputs=state['successful_outputs'] + int(result['status'] in
                    ({'success'} if own_analysis else {'success', 'abstain'})))
            attempt_snapshot(f'attempt-{index+1:02d}-done')
            if own_analysis and row['condition'] in {'D', 'P'}:
                arm = 'D' if row['condition'] == 'D' else 'AP'
                first = row['case_id'] + ('-D' if arm == 'D' else '-A')
                state.setdefault('workflow_elapsed_seconds', {}).setdefault(row['case_id'], {})[arm] = (
                    time.monotonic() - workflow_starts[first])
            emit('component_output_finished', id=key, status=result['status'], recorded_outputs=index+1,
                 scheduled_outputs=count, elapsed_seconds=result['elapsed_seconds'])
            if failure is not None: raise failure
            if stop.reason == 'global_deadline': raise TimeoutError('Global inference deadline reached')
    state['status'] = 'completed' if state['successful_outputs'] == count else 'completed_with_errors'
    runtime.write_json(output / 'run.json', state)


def run(args):
    runtime.offline()
    settings = runtime.read_json(args.settings)
    dictionary_settings(settings)
    runtime.checked_files(Path(__file__).parent, settings['script_hashes'])
    runtime.check_deadline(args.deadline_utc)
    folder = runtime.verified_bundle(args.bundle)
    contract = runtime.contract_at(folder / 'contract.json')
    base = runtime.verify_base(args.base)
    verify_adapter(args.adapter, contract, base)
    protocol = settings.get('protocol', 'components-v1')
    if settings['schedule'] != schedule(protocol):
        raise ValueError('Prepared protocol schedule differs')
    rows = read_inputs(args.inputs, settings['inputs_sha256'], protocol)
    environment = runtime.gpu_admission()
    import torch
    from transformers import AutoTokenizer, Gemma4ForConditionalGeneration, set_seed
    from peft import PeftModel
    tokenizer = AutoTokenizer.from_pretrained(args.base, local_files_only=True, trust_remote_code=False)
    prepared = prepare_prompts(rows, tokenizer, protocol)
    dictionary = protocol == 'dictionary-ab-v1'
    identity = dict(protocol=protocol, run_id=settings['run_id'], inputs_sha256=settings['inputs_sha256'],
        script_hashes=settings['script_hashes'], base_files=base['files'], model_id=runtime.MODEL_ID,
        revision=runtime.REVISION, adapter_files=ADAPTER_FILES, adapter_step=280, environment=environment,
        precision='bf16_base_fp32_retained_lora', attention='eager', enable_thinking=False,
        max_new_tokens=4096 if dictionary else 256, max_generation_seconds=90,
        context_limit=12288 if dictionary else 2048, seed=42,
        do_sample=False, eos_token_ids=[1,106,50], pad_token_id=0, num_beams=1,
        fresh_context_each_output=True, optimizer_updates=0, scoring_performed=False,
        expert_adjudicated=False, deadline_utc=args.deadline_utc)
    if dictionary:
        identity.update(decode_controls=dictionary_controls(), timing_contract=DICTIONARY_TIMING_CONTRACT,
            input_cap_tokens=8192, no_truncation=True, first_attempt_only=True,
            compute_seconds=settings['compute_seconds'], internal_seconds=settings['internal_seconds'],
            native_timeout_minutes=settings['native_timeout_minutes'],
            case_ids=list(DICTIONARY_CASES), case_work_bindings=DICTIONARY_WORKS,
            timeout_or_output_cap_primary_inconclusive=True,
            reviewed_specimen_sha256=DICTIONARY_HISTORICAL_CONTRACT_SHA256,
            historical_ab_contract_unchanged=True)
    state = dict(identity, identity_sha256=sha(canonical(identity)), status='loading_bf16',
        schedule=schedule(protocol), scheduled_outputs=len(schedule(protocol)), attempted_outputs=0, recorded_outputs=0,
        model_calls_started=0, slot_counter_definition='attempted_outputs counts started scheduled slots, including dependency skips',
        successful_outputs=0, active_output_id=None, unattempted_output_ids=schedule(protocol), last_result=None)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    remote = Path(args.incremental)
    try:
        cutoff = time.monotonic() + (runtime.check_deadline(args.deadline_utc)-datetime.now(timezone.utc)).total_seconds()
        snapshot(output, remote, state, 'loading', cutoff)
        set_seed(42)
        model = Gemma4ForConditionalGeneration.from_pretrained(args.base, local_files_only=True,
            trust_remote_code=False, torch_dtype=torch.bfloat16, device_map={'':'cuda'}, attn_implementation='eager')
        model = PeftModel.from_pretrained(model, args.adapter, adapter_name='reference',
            local_files_only=True, is_trainable=False)
        select_adapter(model, 'reference', available=('reference',))
        verify_loaded_adapter(model, args.adapter, 'reference')
        if (getattr(model.config, 'quantization_config', None)
                or any(p.device.type != 'cuda' or (p.is_floating_point() and p.dtype !=
                    (torch.float32 if '.lora_' in name else torch.bfloat16))
                       for name,p in model.named_parameters())):
            raise ValueError('Loaded numerical path differs from frozen BF16/FP32 single-GPU recipe')
        state['canary'] = prefill_canary(model, {(r['case_id'],r['arm' if dictionary else 'condition']):prepared[r['id']] for r in rows},args.deadline_utc)
        snapshot(output, remote, state, 'prefill-passed', cutoff)
        emit('component_prefill_passed', **state['canary'])
        generate(model, tokenizer, rows, prepared, output, remote, state, args.deadline_utc)
        select_adapter(model, 'reference', available=('reference',))
        verify_loaded_adapter(model, args.adapter, 'reference')
        state['adapter_unchanged_after_inference'] = True
    except BaseException as error:
        state.update(status='incomplete', error_type=type(error).__name__, error=str(error))
        if dictionary: state['primary_comparison_inconclusive'] = True
        raise
    finally:
        runtime.write_json(output / 'run.json', state)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('base','bundle','adapter','inputs','settings','output','incremental','deadline-utc'):
        p.add_argument('--'+name, required=True)
    run(p.parse_args())
