"""Versioned matched-NF4 paired diagnosis; inference only, no provisioning."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import gc
import json
import os
from pathlib import Path
import time

try:
    from . import learning_eval as shared
except ImportError:
    import bf16_learning_eval as shared

bundle, old, qualified, protocol, runtime = shared.bundle, shared.old, shared.qualified, shared.protocol, shared.runtime
ARMS, GENERATION = shared.ARMS, shared.GENERATION
HELPERS = shared.HELPERS | {'bf16_learning_eval.py'}
sha, canonical = shared.sha, shared.canonical
read_inputs, prepare_prompts, select_adapter = shared.read_inputs, shared.prepare_prompts, shared.select_adapter
initial_state, GenerationDeadline = shared.initial_state, shared.GenerationDeadline

def validate_settings(settings):
    fields = {'schema_version', 'inputs_sha256', 'runner_sha256', 'helper_sha256',
              'reference_adapter_files', 'candidate_adapter_files', 'generation'}
    if settings.get('schema_version') == 2:
        fields |= {'experiment_id', 'case_order'}
        if (settings.get('experiment_id') != 'corrected-learning-diagnosis-20260930'
                or sorted(settings.get('case_order', [])) != [f'LD-{i:03d}' for i in range(1, 29)]):
            raise ValueError('Versioned diagnostic identity/schedule differs')
    if (set(settings) != fields or settings['schema_version'] not in {1, 2}
            or settings['generation'] != GENERATION or set(settings['helper_sha256']) != HELPERS):
        raise ValueError('Diagnostic settings/schema/generation contract differs')
    if runtime.digest(__file__) != settings['runner_sha256']:
        raise ValueError('Diagnostic runner checksum differs')
    runtime.checked_files(Path(__file__).parent, {k: v for k, v in settings['helper_sha256'].items()
                                               if k != 'bf16_learning_eval.py'})
    if runtime.digest(shared.__file__) != settings['helper_sha256']['bf16_learning_eval.py']:
        raise ValueError('Frozen BF16 policy helper checksum differs')
    if settings['reference_adapter_files'] != qualified.ADAPTER_FILES:
        raise ValueError('Exact retained step280 adapter required')
    candidate = settings['candidate_adapter_files']
    if (not {'adapter_config.json', 'adapter_model.safetensors'} <= set(candidate)
            or set(candidate) - {'adapter_config.json', 'adapter_model.safetensors', 'README.md'}
            or candidate['adapter_model.safetensors'] == qualified.ADAPTER_FILES['adapter_model.safetensors']):
        raise ValueError('Distinct mixed candidate adapter identity required')


def numerical_state(model):
    """Fail closed on actual loaded NF4 representation, casts and frozen state."""
    import torch
    from bitsandbytes.nn import Linear4bit, Params4bit
    config = model.config.quantization_config
    config = config.to_dict() if hasattr(config, 'to_dict') else config
    if (not isinstance(config, dict) or config.get('load_in_4bit') is not True
            or config.get('load_in_8bit') is not False or config.get('bnb_4bit_quant_type') != 'nf4'
            or config.get('bnb_4bit_use_double_quant') is not True
            or config.get('bnb_4bit_compute_dtype') not in ('bfloat16', torch.bfloat16)
            or getattr(model, 'is_loaded_in_4bit', False) is not True):
        raise ValueError('Loaded model is not the required double-quantized BF16-compute NF4')
    if (model.training or getattr(model, 'is_gradient_checkpointing', False)
            or model.config.get_text_config()._attn_implementation != 'eager'):
        raise ValueError('NF4 inference must be eval/eager without checkpointing')
    counts, quantized = Counter(), 0
    for name, param in model.named_parameters():
        counts[str(param.dtype)] += param.numel()
        if param.requires_grad or param.grad is not None:
            raise ValueError('NF4 inference parameter has gradient state: ' + name)
        if isinstance(param, Params4bit):
            state = getattr(param, 'quant_state', None)
            if (param.dtype != torch.uint8 or state is None or state.quant_type != 'nf4'
                    or state.nested is not True):
                raise ValueError('Actual packed NF4/double-quantization state differs: ' + name)
            quantized += 1
        elif param.is_floating_point() and param.dtype != torch.float32:
            raise ValueError('Nonquantized NF4 inference parameters must match kbit FP32 preparation: ' + name)
    # PEFT's wrapper is also named Linear4bit; inspect only actual BNB bases.
    modules = [module for module in model.modules() if isinstance(module, Linear4bit)]
    if not quantized or len(modules) != quantized or any(module.compute_dtype != torch.bfloat16 for module in modules):
        raise ValueError('Actual NF4 linear modules/compute dtype differ')
    return dict(condition='matched_nf4_doublequant_bf16_compute_nonquant_fp32',
        quantization=dict(load_in_4bit=True, quant_type='nf4', double_quant=True, compute_dtype='bfloat16'),
        parameter_numel_by_dtype=dict(counts), buffer_numel_by_dtype=
            {dtype: sum(b.numel() for b in model.buffers() if str(b.dtype) == dtype)
             for dtype in {str(b.dtype) for b in model.buffers()}},
        quantized_parameter_count=quantized, nonquantized_parameter_dtype='float32',
        autocast_device='cuda', autocast_dtype='bfloat16', adapter_autocast_dtype=True,
        training=False, gradients_enabled=False, gradient_checkpointing=False, optimizer_updates=0)


def load_model(base, adapters):
    import torch
    from transformers import BitsAndBytesConfig, Gemma4ForConditionalGeneration
    from peft import PeftModel, prepare_model_for_kbit_training
    model = Gemma4ForConditionalGeneration.from_pretrained(base, local_files_only=True,
        trust_remote_code=False, use_safetensors=True, device_map={'': 0}, dtype=torch.bfloat16,
        attn_implementation='eager', quantization_config=BitsAndBytesConfig(load_in_4bit=True,
            bnb_4bit_quant_type='nf4', bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16))
    # Same FP32 preparation as the prior NF4 training, without backward-only setup.
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=False)
    model = PeftModel.from_pretrained(model, adapters['reference'], adapter_name='reference',
        local_files_only=True, is_trainable=False, autocast_adapter_dtype=True)
    model.load_adapter(adapters['candidate'], adapter_name='candidate', local_files_only=True,
                       is_trainable=False, autocast_adapter_dtype=True)
    model.gradient_checkpointing_disable()
    for arm, path in adapters.items():
        select_adapter(model, arm)
        old.verify_loaded_adapter(model, path, arm)
    return model, numerical_state(model)


def generate_pairs(model, tokenizer, rows, prepared, output, identity, deadline_utc, device='cuda'):
    import torch
    from transformers import DynamicCache, StoppingCriteriaList, set_seed
    deadline = runtime.check_deadline(deadline_utc)
    state = initial_state(rows, identity)
    ids = state['schedule']
    by_id = {r['case_id']: r for r in rows}
    ordered = [(by_id[k.split(':')[0]], k.split(':')[1]) for k in ids]
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    if (output / 'run.json').exists():
        loading = runtime.read_json(output / 'run.json')
        if (loading.get('status') != 'loading_nf4' or loading.get('attempted_outputs') != 0
                or loading.get('identity_sha256') != state['identity_sha256']):
            raise ValueError('Existing evaluation cannot be restarted or overwritten')
    if (output / 'predictions.jsonl').exists():
        raise ValueError('Existing predictions cannot be retried or overwritten')
    runtime.write_json(output / 'run.json', state)
    completed = Counter()
    try:
        for arm in ARMS:
            state['canaries'][arm] = {'status': 'running'}
            runtime.write_json(output / 'run.json', state)
            select_adapter(model, arm)
            with torch.inference_mode(), torch.autocast(device_type=device, dtype=torch.bfloat16):
                state['canaries'][arm] = qualified.prefill_canary(
                    model, {(r['case_id'], arm): prepared[r['case_id']] for r in rows}, deadline_utc)
            runtime.write_json(output / 'run.json', state)
            old.emit('learning_prefill_passed', arm=arm, **state['canaries'][arm])
        if (deadline - datetime.now(timezone.utc)).total_seconds() < 56 * GENERATION['max_generation_seconds'] + 60:
            raise TimeoutError('Insufficient remaining time for all 56 first attempts plus finalization margin')
        with (output / 'predictions.jsonl').open('x', encoding='utf-8') as stream:
            for index, (row, arm) in enumerate(ordered):
                runtime.check_deadline(deadline_utc)
                state.update(active_output_id=ids[index], attempted_outputs=index + 1,
                             unattempted_output_ids=ids[index + 1:])
                runtime.write_json(output / 'run.json', state)
                start, new_ids, text, failure, hit_cap = time.monotonic(), [], '', None, False
                stopper = GenerationDeadline(start, deadline)
                result = {'status': 'error'}
                try:
                    select_adapter(model, arm)
                    set_seed(GENERATION['seed'])
                    tokens = torch.tensor([prepared[row['case_id']]], device=device)
                    with torch.inference_mode(), torch.autocast(device_type=device, dtype=torch.bfloat16):
                        generated = model.generate(input_ids=tokens, attention_mask=torch.ones_like(tokens),
                            past_key_values=DynamicCache(), use_cache=True, do_sample=False, num_beams=1,
                            max_new_tokens=GENERATION['max_new_tokens'], pad_token_id=0,
                            eos_token_id=protocol.EOS, stopping_criteria=StoppingCriteriaList([stopper]))
                    if (generated.ndim != 2 or generated.shape[0] != 1
                            or not torch.equal(generated[0, :tokens.shape[1]], tokens[0])):
                        raise RuntimeError('Generated sequence does not preserve its input prefix')
                    new_ids = generated[0, tokens.shape[1]:].tolist()
                    if len(new_ids) > GENERATION['max_new_tokens']:
                        raise RuntimeError('Generation exceeded frozen output cap')
                    text = tokenizer.decode(new_ids, skip_special_tokens=True)
                    stopper(None, None)
                    hit_cap = len(new_ids) >= GENERATION['max_new_tokens'] and new_ids[-1] not in protocol.EOS
                    result['status'] = ('timeout' if stopper.reason else 'error' if hit_cap or not text.strip()
                                        else 'abstain' if text.strip() == '[UNRESOLVED]' else 'success')
                    if hit_cap: result['error_type'] = 'OutputCapWithoutEOS'
                    elif not text.strip(): result['error_type'] = 'EmptyOutput'
                except BaseException as error:
                    failure = error
                    result.update(status='error', error_type=type(error).__name__, error=str(error))
                result.update(id=ids[index], case_id=row['case_id'], arm=arm, sequence=index + 1, text=text,
                    elapsed_seconds=time.monotonic() - start, identity_sha256=state['identity_sha256'],
                    adapter_sha256=identity['adapters'][arm]['adapter_model.safetensors'],
                    prompt_sha256=sha(row['prompt'].encode()), input_tokens=len(prepared[row['case_id']]),
                    rendered_input_ids_sha256=sha(canonical(prepared[row['case_id']])),
                    output_tokens=len(new_ids), output_token_ids=new_ids, output_sha256=sha(text.encode()),
                    hit_output_cap_without_eos=hit_cap, stop_reason=stopper.reason)
                stream.write(json.dumps(result, ensure_ascii=False) + '\n')
                stream.flush()
                os.fsync(stream.fileno())
                state.update(recorded_outputs=index + 1, active_output_id=None, unattempted_output_ids=ids[index + 1:])
                state['arms'][arm]['recorded'] += 1
                succeeded = result['status'] in {'success', 'abstain'}
                state['arms'][arm]['successful' if succeeded else 'errors'] += 1
                state['successful_outputs'] += int(succeeded)
                completed[row['case_id']] += 1
                state['completed_cases'] = sum(n == 2 for n in completed.values())
                runtime.write_json(output / 'run.json', state)
                old.emit('learning_case_recorded', case_id=row['case_id'], arm=arm, status=result['status'],
                         recorded_outputs=state['recorded_outputs'])
                if failure is not None: raise failure
                if stopper.reason == 'global_deadline': raise TimeoutError('Global generation deadline reached')
        if state['recorded_outputs'] != 56 or state['completed_cases'] != 28:
            raise RuntimeError('Incomplete paired coverage')
        state['status'] = 'completed' if state['successful_outputs'] == 56 else 'completed_with_errors'
        runtime.write_json(output / 'run.json', state)
        return state
    except BaseException as error:
        for canary in state['canaries'].values():
            if canary['status'] == 'running': canary['status'] = 'failed'
        state.update(status='incomplete', error_type=type(error).__name__, error=str(error))
        runtime.write_json(output / 'run.json', state)
        raise


def run(args):
    runtime.offline()
    runtime.check_deadline(args.deadline_utc)
    settings = runtime.read_json(args.settings)
    validate_settings(settings)
    rows = read_inputs(args.inputs, settings['inputs_sha256'], versioned=settings['schema_version'] == 2)
    base = runtime.verify_base(args.base)
    runtime.checked_files(args.tokenizer, bundle.TOKENIZER_HASHES)
    adapters = {'reference': args.reference_adapter, 'candidate': args.candidate_adapter}
    for arm, path in adapters.items():
        runtime.checked_files(path, settings[arm + '_adapter_files'])
    original = runtime.read_json(Path(args.reference_adapter) / 'adapter_config.json')
    old.verify_adapter_architecture(runtime.read_json(Path(args.candidate_adapter) / 'adapter_config.json'), original)
    environment = runtime.gpu_admission()
    import torch
    from transformers import AutoTokenizer, set_seed
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, local_files_only=True, trust_remote_code=False)
    context = runtime.read_json(Path(args.base) / 'config.json')['text_config']['max_position_embeddings']
    prepared = prepare_prompts(rows, tokenizer, context)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    identity = {'experiment_id': settings.get('experiment_id', 'learning-diagnosis-20260929'), 'settings_sha256': runtime.digest(args.settings),
                'settings': settings, 'inputs_sha256': settings['inputs_sha256'], 'model_id': runtime.MODEL_ID,
                'model_revision': runtime.REVISION, 'base_files': base['files'], 'environment': environment,
                'adapters': {a: settings[a + '_adapter_files'] for a in ARMS},
                'generation': GENERATION, 'eos_token_ids': protocol.EOS, 'enable_thinking': False,
                'tokenizer_files': bundle.TOKENIZER_HASHES, 'deadline_utc': args.deadline_utc,
                'prompts': [{'case_id': r['case_id'], 'prompt_sha256': sha(r['prompt'].encode()),
                             'rendered_input_ids_sha256': sha(canonical(prepared[r['case_id']])),
                             'input_tokens': len(prepared[r['case_id']])} for r in rows],
                'training_performed': False, 'optimizer_updates': 0, 'quality_validated': False}
    evaluation_output = output / 'evaluation'
    evaluation_output.mkdir()
    identity['numerical_condition'] = 'matched_nf4_doublequant_bf16_compute_nonquant_fp32'
    state, model = {**identity, 'status': 'loading_nf4'}, None
    loading_state = initial_state(rows, identity)
    loading_state['status'] = 'loading_nf4'
    runtime.write_json(evaluation_output / 'run.json', loading_state)
    runtime.write_json(output / 'run.json', state)
    try:
        set_seed(GENERATION['seed'])
        old.emit('learning_loading_nf4')
        model, numerical = load_model(args.base, adapters)
        state['numerical_state'] = numerical
        runtime.write_json(output / 'numerical-state.json', numerical)
        runtime.check_deadline(args.deadline_utc)
        state['status'] = 'evaluating'
        runtime.write_json(output / 'run.json', state)
        result = generate_pairs(model, tokenizer, rows, prepared, output / 'evaluation', identity, args.deadline_utc)
        for arm, path in adapters.items():
            select_adapter(model, arm)
            old.verify_loaded_adapter(model, path, arm)
        if numerical_state(model) != numerical:
            raise RuntimeError('Final NF4 numerical state changed')
        state.update(status=result['status'], recorded_outputs=result['recorded_outputs'],
                     successful_outputs=result['successful_outputs'], final_adapters_unchanged=True)
        runtime.write_json(output / 'run.json', state)
        return state
    except BaseException as error:
        state.update(status='incomplete', error_type=type(error).__name__, error=str(error))
        runtime.write_json(output / 'run.json', state)
        raise
    finally:
        del model
        gc.collect()
        torch.cuda.empty_cache()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('base', 'tokenizer', 'reference-adapter', 'candidate-adapter', 'inputs', 'settings', 'output', 'deadline-utc'):
        parser.add_argument('--' + name, required=True)
    return run(parser.parse_args(argv))


if __name__ == '__main__':
    main()
