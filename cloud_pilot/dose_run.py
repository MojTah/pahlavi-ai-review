"""Offline dose continuation with baseline admission and frozen first-attempt panels."""
import argparse
from datetime import datetime, timezone
import gc
import json
import os
from pathlib import Path
import time

try:
    from . import dose_train as core, mixed_run as mixed, learning_eval as learning, nf4_learning_eval as nf4
except ImportError:
    import dose_train as core
    import mixed_run as mixed
    import learning_eval as learning
    import nf4_learning_eval as nf4

runtime, old, qualified = mixed.runtime, mixed.old, mixed.qualified
ARMS = ('reference', 'dose96', 'dose192', 'dose384')


def read_packet(path, settings):
    if runtime.digest(path) != settings['inputs_sha256']:
        raise ValueError('Dose packet checksum differs')
    rows = [json.loads(line) for line in Path(path).read_text('utf-8').splitlines()]
    seen = set()
    for row in rows:
        if (not {'case_id', 'module', 'arms'} <= set(row)
                or any(not isinstance(row[k], str) or not row[k].strip() for k in ('case_id', 'module'))
                or not (isinstance(row.get('prompt'), str) and row['prompt'].strip() or isinstance(row.get('messages'), list) and row['messages'])
                or row['case_id'] in seen or not isinstance(row['arms'], list) or not row['arms']
                or len(set(row['arms'])) != len(row['arms']) or set(row['arms']) - set(ARMS)
                or row['module'] not in settings['generation_by_module']):
            raise ValueError('Dose packet schema/order differs')
        seen.add(row['case_id'])
    schedule = [(row, arm) for arm in ARMS for row in rows if arm in row['arms']]
    if not rows or len(schedule) != settings['expected_outputs']:
        raise ValueError('Dose output coverage differs')
    for generation in settings['generation_by_module'].values():
        if (set(generation) != set(learning.GENERATION)
                or any(type(v) is not int or v <= 0 for v in generation.values()) or generation['seed'] != 42):
            raise ValueError('Invalid frozen generation policy')
    if [r['case_id'] + ':' + arm for r, arm in schedule] != settings['evaluation_schedule']:
        raise ValueError('Frozen output schedule differs')
    return rows, schedule


def prepare_prompts(rows, tokenizer, context, settings):
    prepared = {}
    entries = settings['prompt_identities']
    identities = ({entry['case_id']: entry for entry in entries} if isinstance(entries, list) else entries)
    if len(identities) != len(entries) or set(identities) != {row['case_id'] for row in rows}:
        raise ValueError('Frozen dose prompt identity coverage/uniqueness differs')
    for row in rows:
        messages = row['messages'] if 'messages' in row else [{'role': 'user', 'content': row['prompt']}]
        ids = tokenizer.apply_chat_template(messages, tokenize=True, return_dict=False,
                                           add_generation_prompt=True, enable_thinking=False)
        if (not isinstance(ids, list) or not ids or any(type(x) is not int or x < 0 for x in ids)
                or len(ids) + settings['generation_by_module'][row['module']]['max_new_tokens'] > context):
            raise ValueError('Invalid/untruncated dose prompt')
        prepared[row['case_id']] = ids
        expected = identities[row['case_id']]
        if (expected['input_tokens'] != len(ids)
                or expected['rendered_input_ids_sha256'] != qualified.sha(qualified.canonical(ids))):
            raise ValueError('Frozen dose prompt token identity differs')
    return prepared


def reserve_guard(deadline_utc, reserved):
    remaining = (runtime.check_deadline(deadline_utc) - datetime.now(timezone.utc)).total_seconds()
    if remaining <= reserved:
        raise TimeoutError('Insufficient remaining time for explicit evaluation reserve')
    return remaining


def select_adapter(model, arm, available=ARMS):
    model.set_adapter(arm)
    model.requires_grad_(False)
    model.eval()
    model.zero_grad(set_to_none=True)
    state = model.get_model_status()
    if (state.enabled is not True or state.active_adapters != [arm] or state.merged_adapters != []
            or set(state.available_adapters) != set(available) or model.training
            or any(p.requires_grad or p.grad is not None for p in model.parameters())):
        raise RuntimeError('Frozen named adapter switching failed')


def generate(model, tokenizer, schedule, prepared, output, identity, deadline_utc, settings, device='cuda', available=ARMS, allocation_seconds=None):
    import torch
    from transformers import DynamicCache, StoppingCriteriaList, set_seed
    deadline = runtime.check_deadline(deadline_utc)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    ids = [r['case_id'] + ':' + a for r, a in schedule]
    state = dict(identity_sha256=qualified.sha(qualified.canonical(identity)), status='running', schedule=ids,
                 scheduled_outputs=len(ids), attempted_outputs=0, recorded_outputs=0, successful_outputs=0,
                 active_output_id=None, unattempted_output_ids=ids.copy(), canaries={}, scoring_performed=False)
    runtime.write_json(output / 'run.json', state)
    try:
        started = time.monotonic()
        with (output / 'predictions.jsonl').open('x', encoding='utf-8') as stream:
            for arm in available:
                select_adapter(model, arm, ('reference',) if available == ('reference',) else ARMS)
                state['canaries'][arm] = {'status': 'running'}
                runtime.write_json(output / 'run.json', state)
                with torch.autocast(device_type=device, dtype=torch.bfloat16):
                    state['canaries'][arm] = qualified.prefill_canary(model,
                        {(r['case_id'], arm): prepared[r['case_id']] for r, a in schedule if a == arm}, deadline_utc)
                if state['canaries'][arm]['elapsed_seconds'] > settings['canary_seconds']:
                    raise TimeoutError('Prefill exceeded reserved canary cap')
                runtime.write_json(output / 'run.json', state)
                for row, current_arm in schedule:
                    if current_arm != arm:
                        continue
                    index = state['attempted_outputs']
                    reserve_guard(deadline_utc, settings['generation_by_module'][row['module']]['max_generation_seconds'] + settings['finalization_seconds'])
                    if (allocation_seconds is not None and allocation_seconds - (time.monotonic() - started)
                            < settings['generation_by_module'][row['module']]['max_generation_seconds'] + settings['finalization_seconds']):
                        raise TimeoutError('Evaluation allocation cannot admit next full-cap first attempt')
                    state.update(active_output_id=ids[index], attempted_outputs=index + 1,
                                 unattempted_output_ids=ids[index + 1:])
                    runtime.write_json(output / 'run.json', state)
                    policy = settings['generation_by_module'][row['module']]
                    start, new_ids, text, failure = time.monotonic(), [], '', None
                    class Stop(learning.GenerationDeadline):
                        def __call__(self, input_ids, scores, **kwargs):
                            if datetime.now(timezone.utc) >= self.deadline:
                                self.reason = 'global_deadline'
                            elif time.monotonic() - self.start >= policy['max_generation_seconds']:
                                self.reason = 'case_timeout'
                            return self.reason is not None
                    stopper = Stop(start, deadline)
                    result = {'status': 'error'}
                    try:
                        set_seed(policy['seed'])
                        tokens = torch.tensor([prepared[row['case_id']]], device=device)
                        with torch.inference_mode(), torch.autocast(device_type=device, dtype=torch.bfloat16):
                            generated = model.generate(input_ids=tokens, attention_mask=torch.ones_like(tokens),
                                past_key_values=DynamicCache(), use_cache=True, do_sample=False, num_beams=1,
                                max_new_tokens=policy['max_new_tokens'], pad_token_id=0, eos_token_id=mixed.protocol.EOS,
                                stopping_criteria=StoppingCriteriaList([stopper]))
                        if generated.ndim != 2 or generated.shape[0] != 1 or not torch.equal(generated[0, :tokens.shape[1]], tokens[0]):
                            raise RuntimeError('Generated sequence changed input prefix')
                        new_ids = generated[0, tokens.shape[1]:].tolist()
                        if len(new_ids) > policy['max_new_tokens']:
                            raise RuntimeError('Frozen generation cap exceeded')
                        text = tokenizer.decode(new_ids, skip_special_tokens=True)
                        stopper(None, None)
                        cap = len(new_ids) >= policy['max_new_tokens'] and new_ids[-1] not in mixed.protocol.EOS
                        result['status'] = ('timeout' if stopper.reason else 'error' if cap or not text.strip()
                                            else 'abstain' if text.strip() == '[UNRESOLVED]' else 'success')
                        result['hit_output_cap_without_eos'] = cap
                    except BaseException as error:
                        failure = error
                        result.update(error_type=type(error).__name__, error=str(error))
                    result.update(id=ids[index], case_id=row['case_id'], module=row['module'], arm=arm,
                        sequence=index + 1, text=text, elapsed_seconds=time.monotonic() - start,
                        identity_sha256=state['identity_sha256'], generation=policy,
                        adapter_sha256=identity['adapters'][arm]['adapter_model.safetensors'],
                        prompt_sha256=qualified.sha(qualified.canonical(row.get('messages', row.get('prompt')))),
                        rendered_input_ids_sha256=qualified.sha(qualified.canonical(prepared[row['case_id']])),
                        input_tokens=len(prepared[row['case_id']]), output_tokens=len(new_ids), output_token_ids=new_ids,
                        output_sha256=qualified.sha(text.encode()), stop_reason=stopper.reason)
                    stream.write(json.dumps(result, ensure_ascii=False) + '\n')
                    stream.flush()
                    os.fsync(stream.fileno())
                    state.update(recorded_outputs=index + 1, active_output_id=None)
                    state['successful_outputs'] += int(result['status'] in {'success', 'abstain'})
                    runtime.write_json(output / 'run.json', state)
                    old.emit('dose_case_recorded', case_id=row['case_id'], arm=arm, status=result['status'])
                    if failure is not None:
                        raise failure
                    if stopper.reason == 'global_deadline':
                        raise TimeoutError('Global generation deadline')
        state['elapsed_seconds'] = time.monotonic() - started
        if allocation_seconds is not None and state['elapsed_seconds'] > allocation_seconds:
            raise TimeoutError('Evaluation exceeded its empirical allocation')
        state['status'] = 'completed' if state['successful_outputs'] == len(ids) else 'completed_with_errors'
        runtime.write_json(output / 'run.json', state)
        return state
    except BaseException as error:
        state.update(status='incomplete', error_type=type(error).__name__, error=str(error))
        for canary in state['canaries'].values():
            if canary['status'] == 'running':
                canary['status'] = 'failed'
        runtime.write_json(output / 'run.json', state)
        raise


def reconcile_evaluation(output):
    """Reconcile durable first attempts after a killed child; never synthesize outputs."""
    output = Path(output)
    if not (output / 'run.json').is_file():
        return None
    state = runtime.read_json(output / 'run.json')
    predictions = output / 'predictions.jsonl'
    data = predictions.read_bytes() if predictions.exists() else b''
    lines = data.splitlines(keepends=True)
    records = []
    partial = False
    for i, line in enumerate(lines):
        try:
            record = json.loads(line)
        except (ValueError, UnicodeDecodeError):
            if i != len(lines) - 1:
                raise ValueError('Corrupted interior durable prediction')
            partial = True
            break
        if not line.endswith(b'\n'):
            partial = True
            break
        records.append(record)
    expected = state['schedule']
    actual = [r['id'] for r in records]
    if actual != expected[:len(records)] or len(set(actual)) != len(actual):
        raise ValueError('Durable prediction order/identity differs')
    attempted = state['attempted_outputs']
    if not len(records) <= attempted <= len(records) + 1:
        raise ValueError('Durable first-attempt count differs')
    active = expected[len(records)] if attempted > len(records) else None
    state.update(recorded_outputs=len(records), successful_outputs=sum(r['status'] in {'success','abstain'} for r in records),
                 active_output_id=active, active_incomplete_output_id=active,
                 unattempted_output_ids=expected[attempted:], interrupted_prediction_fragment=partial)
    if state['status'] == 'running' or active is not None or partial:
        state.update(status='incomplete', error_type='ChildInterrupted',
                     error='Child ended before durable completion; first attempts cannot be retried')
    for canary in state.get('canaries', {}).values():
        if canary['status'] == 'running':
            canary['status'] = 'incomplete'
    runtime.write_json(output / 'run.json', state)
    return state


def run(args):
    runtime.offline()
    settings = runtime.read_json(args.settings)
    if settings['training_settings'] != core.SETTINGS or settings['reference_adapter_files'] != qualified.ADAPTER_FILES:
        raise ValueError('Dose training/reference contract differs')
    runtime.checked_files(Path(__file__).parent, settings['script_hashes'])
    folder = runtime.verified_bundle(args.bundle)
    contract = runtime.contract_at(folder / 'contract.json')
    base = runtime.verify_base(args.base)
    runtime.checked_files(args.tokenizer, mixed.bundle.TOKENIZER_HASHES)
    qualified.verify_adapter(args.adapter, contract, base)
    original = runtime.read_json(Path(args.adapter) / 'adapter_config.json')
    if any(original[k] != v for k, v in {'r': 16, 'lora_alpha': 32, 'lora_dropout': 0.0}.items()):
        raise ValueError('Starting LoRA configuration differs')
    rows, manifest = mixed.read_data(args.train, args.data_manifest, settings)
    expanded = rows * 4
    core.validate_rows(expanded, core.SETTINGS)
    cases, schedule = read_packet(args.inputs, settings)
    environment = runtime.gpu_admission()
    import torch
    from transformers import AutoTokenizer, BitsAndBytesConfig, Gemma4ForConditionalGeneration, set_seed
    from peft import PeftModel, prepare_model_for_kbit_training
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, local_files_only=True, trust_remote_code=False)
    context = runtime.read_json(Path(args.base) / 'config.json')['text_config']['max_position_embeddings']
    prepared = prepare_prompts(cases, tokenizer, context, settings)
    reserve_guard(args.deadline_utc, settings['remaining_evaluation_seconds'] + settings['reload_seconds'])
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    identity = dict(experiment_id=settings['experiment_id'], settings_sha256=runtime.digest(args.settings),
        settings=settings, environment=environment, original_adapter_step=280, training_passes=4,
        data_manifest_sha256=settings['data_manifest_sha256'], train_sha256=settings['train_sha256'],
        inputs_sha256=settings['inputs_sha256'], base_files=base['files'], model_id=runtime.MODEL_ID,
        model_revision=runtime.REVISION, tokenizer_files=mixed.bundle.TOKENIZER_HASHES,
        evaluation_dtype='NF4 with prepare_model_for_kbit_training casting and BF16 autocast',
        quality_validated=False, scoring_performed=False, expert_adjudicated=False)
    state, model = {**identity, 'status': 'loading_nf4', 'training_status': 'not_started', 'evaluation_status': 'not_started'}, None
    runtime.write_json(output / 'run.json', state)
    def admission(train_rows, steps, elapsed, available):
        return mixed.core.forecast(train_rows, steps, elapsed, available,
            evaluation_seconds=settings['remaining_evaluation_seconds'], reload_seconds=settings['reload_seconds'])
    try:
        set_seed(core.SETTINGS['seed'])
        model = Gemma4ForConditionalGeneration.from_pretrained(args.base, local_files_only=True,
            trust_remote_code=False, use_safetensors=True, device_map={'': 0}, dtype=torch.bfloat16,
            attn_implementation='eager', quantization_config=BitsAndBytesConfig(load_in_4bit=True,
            bnb_4bit_quant_type='nf4', bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16))
        model = prepare_model_for_kbit_training(model, gradient_checkpointing_kwargs={'use_reentrant': False})
        baseline_base = model
        model = PeftModel.from_pretrained(baseline_base, args.adapter, adapter_name='reference', local_files_only=True, is_trainable=False)
        model.gradient_checkpointing_disable()
        model.config.use_cache = model.config.text_config.use_cache = True
        select_adapter(model, 'reference', ('reference',))
        old.verify_loaded_adapter(model, args.adapter, 'reference')
        state['baseline_numerical_state'] = nf4.numerical_state(model)
        identity['adapters'] = {'reference': qualified.ADAPTER_FILES}
        state.update(status='baseline_evaluating', baseline_status='running')
        runtime.write_json(output / 'run.json', state)
        baseline = generate(model, tokenizer, [(r,a) for r,a in schedule if a == 'reference'], prepared,
            output / 'evaluation-baseline', identity, args.deadline_utc, settings, available=('reference',),
            allocation_seconds=settings['baseline_allocation_seconds'])
        old.verify_loaded_adapter(model, args.adapter, 'reference')
        if nf4.numerical_state(model) != state['baseline_numerical_state']:
            raise ValueError('Baseline NF4 numerical state changed')
        if baseline['status'] != 'completed' or baseline['elapsed_seconds'] > settings['baseline_allocation_seconds']:
            raise RuntimeError('Baseline failed or exceeded allocation; no optimization allowed')
        state['baseline_status'] = 'completed'
        runtime.write_json(output / 'run.json', state)
        del model, baseline_base
        model = None
        gc.collect()
        torch.cuda.empty_cache()
        set_seed(core.SETTINGS['seed'])
        model = Gemma4ForConditionalGeneration.from_pretrained(args.base, local_files_only=True,
            trust_remote_code=False, use_safetensors=True, device_map={'': 0}, dtype=torch.bfloat16,
            attn_implementation='eager', quantization_config=BitsAndBytesConfig(load_in_4bit=True,
            bnb_4bit_quant_type='nf4', bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16))
        model = prepare_model_for_kbit_training(model, gradient_checkpointing_kwargs={'use_reentrant': False})
        model = PeftModel.from_pretrained(model, args.adapter, local_files_only=True, is_trainable=True)
        model.config.use_cache = model.config.text_config.use_cache = False
        state['numerical_canary'] = old.training_canary(model, {'candidate': expanded}, args.deadline_utc)
        reserve_guard(args.deadline_utc, settings['remaining_evaluation_seconds'] + settings['reload_seconds'])
        state.update(status='training', training_status='running')
        runtime.write_json(output / 'run.json', state)
        trained = core.train_one(model, expanded, core.SETTINGS, output / 'training', args.deadline_utc, admission=admission)
        if trained['status'] != 'completed' or trained['completed_steps'] != 384 or set(trained['snapshots']) != {'96','192','384'}:
            raise RuntimeError('All dose updates/snapshots required before inference')
        state.update(training_status='completed', training_steps=384)
        paths = {'reference': Path(args.adapter), **{'dose' + s: output / 'training' / ('adapter-step' + s) for s in ('96','192','384')}}
        identity['adapters'] = {'reference': qualified.ADAPTER_FILES}
        for step in ('96','192','384'):
            files = trained['snapshots'][step]['files']
            runtime.checked_files(paths['dose' + step], files)
            old.verify_adapter_architecture(runtime.read_json(paths['dose' + step] / 'adapter_config.json'), original)
            identity['adapters']['dose' + step] = files
        base_model = model.unload()
        # Reuse the exact prepared NF4 base, preserving its frozen dtype casts.
        model = None
        base_model.gradient_checkpointing_disable()
        base_model.config.use_cache = base_model.config.text_config.use_cache = True
        model = PeftModel.from_pretrained(base_model, paths['reference'], adapter_name='reference', local_files_only=True, is_trainable=False)
        for arm in ARMS[1:]:
            model.load_adapter(paths[arm], adapter_name=arm, local_files_only=True, is_trainable=False)
        for arm in ARMS:
            select_adapter(model, arm)
            old.verify_loaded_adapter(model, paths[arm], arm)
        state['final_numerical_state'] = nf4.numerical_state(model)
        state.update(status='evaluating', evaluation_status='running', adapters=identity['adapters'])
        runtime.write_json(output / 'run.json', state)
        evaluated = generate(model, tokenizer, [(r,a) for r,a in schedule if a != 'reference'], prepared, output / 'evaluation', identity, args.deadline_utc, settings, available=ARMS[1:], allocation_seconds=settings['remaining_evaluation_seconds'])
        for arm in ARMS:
            old.verify_loaded_adapter(model, paths[arm], arm)
        if nf4.numerical_state(model) != state['final_numerical_state']:
            raise ValueError('Final NF4 numerical state changed')
        state.update(status=evaluated['status'], evaluation_status=evaluated['status'], final_adapters_unchanged=True,
                     recorded_outputs=baseline['recorded_outputs'] + evaluated['recorded_outputs'], successful_outputs=baseline['successful_outputs'] + evaluated['successful_outputs'])
        runtime.write_json(output / 'run.json', state)
        return state
    except BaseException as error:
        for key in ('baseline_status', 'training_status', 'evaluation_status'):
            if state.get(key) == 'running':
                state[key] = 'incomplete'
        state.update(status='incomplete', error_type=type(error).__name__, error=str(error))
        runtime.write_json(output / 'run.json', state)
        raise
    finally:
        del model
        gc.collect()
        torch.cuda.empty_cache()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('bundle','base','tokenizer','adapter','train','data-manifest','settings','inputs','output','deadline-utc'):
        parser.add_argument('--' + name, required=True)
    return run(parser.parse_args(argv))


if __name__ == '__main__':
    main()
