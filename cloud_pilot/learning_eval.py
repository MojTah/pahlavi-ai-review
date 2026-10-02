"""Offline, inference-only paired recall diagnosis; never provisions or trains."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import gc
import json
import os
from pathlib import Path
import time

try:
    from . import bundle, contextual_run as old, dev_assisted as qualified, palref_eval as protocol, runtime
except ImportError:
    import bundle
    import contextual_run as old
    import dev_assisted as qualified
    import palref_eval as protocol
    import runtime

ARMS = ('reference', 'candidate')
INPUTS_SHA256 = 'ec6217ac6e9d4cd501f93dbae7c3fb8d0694ea1e1a25003a2dfd5f1d28b6fa0d'
GENERATION = {'max_new_tokens': 512, 'max_generation_seconds': 90, 'seed': 42}
HELPERS = {'runtime.py', 'bundle.py', 'contextual_run.py', 'contextual_train.py',
           'dev_assisted.py', 'dev_diagnostic.py', 'palref_eval.py'}
sha, canonical = qualified.sha, qualified.canonical


def read_inputs(path, expected, *, versioned=False):
    if (not versioned and expected != INPUTS_SHA256) or runtime.digest(path) != expected:
        raise ValueError('Frozen diagnostic input checksum differs')
    rows = [json.loads(line) for line in Path(path).read_text('utf-8').splitlines()]
    if (len(rows) != 28 or any(not isinstance(r, dict) or set(r) != {'case_id', 'prompt'} for r in rows)
            or [r['case_id'] for r in rows] != [f'LD-{i:03d}' for i in range(1, 29)]
            or any(not isinstance(r['prompt'], str) or not r['prompt'].strip() for r in rows)):
        raise ValueError('Exactly 28 ordered prompt-only cases required')
    return rows


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
    runtime.checked_files(Path(__file__).parent, settings['helper_sha256'])
    if settings['reference_adapter_files'] != qualified.ADAPTER_FILES:
        raise ValueError('Exact retained step280 adapter required')
    candidate = settings['candidate_adapter_files']
    if (not {'adapter_config.json', 'adapter_model.safetensors'} <= set(candidate)
            or set(candidate) - {'adapter_config.json', 'adapter_model.safetensors', 'README.md'}
            or candidate['adapter_model.safetensors'] == qualified.ADAPTER_FILES['adapter_model.safetensors']):
        raise ValueError('Distinct mixed candidate adapter identity required')


def prepare_prompts(rows, tokenizer, context_limit):
    prepared = {}
    for row in rows:
        ids = tokenizer.apply_chat_template([{'role': 'user', 'content': row['prompt']}],
            tokenize=True, return_dict=False, add_generation_prompt=True, enable_thinking=False)
        if (not isinstance(ids, list) or not ids or any(type(x) is not int or x < 0 for x in ids)
                or len(ids) + GENERATION['max_new_tokens'] > context_limit):
            raise ValueError('Untruncated diagnostic prompt exceeds context or has invalid tokens')
        prepared[row['case_id']] = ids
    return prepared


def select_adapter(model, arm):
    model.set_adapter(arm)
    model.requires_grad_(False)
    model.eval()
    state = model.get_model_status()
    if (state.enabled is not True or state.active_adapters != [arm] or state.merged_adapters != []
            or set(state.available_adapters) != set(ARMS) or model.training
            or any(p.requires_grad or p.grad is not None for p in model.parameters())):
        raise RuntimeError('Frozen named adapter switching failed')


class GenerationDeadline(protocol.GenerationDeadline):
    def __call__(self, input_ids, scores, **kwargs):
        if datetime.now(timezone.utc) >= self.deadline:
            self.reason = 'global_deadline'
        elif time.monotonic() - self.start >= GENERATION['max_generation_seconds']:
            self.reason = 'case_timeout'
        return self.reason is not None


def initial_state(rows, identity):
    case_order = identity.get('settings', {}).get('case_order', [r['case_id'] for r in rows])
    ids = [k + ':' + arm for i, k in enumerate(case_order) for arm in (ARMS if i % 2 == 0 else ARMS[::-1])]
    return {**identity, 'identity_sha256': sha(canonical(identity)), 'status': 'running',
             'schedule': ids, 'scheduled_outputs': 56, 'attempted_outputs': 0, 'recorded_outputs': 0,
             'successful_outputs': 0, 'completed_cases': 0, 'active_output_id': None,
             'unattempted_output_ids': ids.copy(), 'canaries': {},
             'arms': {a: {'recorded': 0, 'successful': 0, 'errors': 0} for a in ARMS},
             'optimizer_updates': 0, 'scoring_performed': False, 'expert_adjudicated': False}


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
        if (loading.get('status') != 'loading_bf16' or loading.get('attempted_outputs') != 0
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
                    with torch.inference_mode():
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
    from transformers import AutoTokenizer, Gemma4ForConditionalGeneration, set_seed
    from peft import PeftModel
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
    state, model = {**identity, 'status': 'loading_bf16'}, None
    loading_state = initial_state(rows, identity)
    loading_state['status'] = 'loading_bf16'
    runtime.write_json(evaluation_output / 'run.json', loading_state)
    runtime.write_json(output / 'run.json', state)
    try:
        set_seed(GENERATION['seed'])
        old.emit('learning_loading_bf16')
        model = Gemma4ForConditionalGeneration.from_pretrained(args.base, local_files_only=True,
            trust_remote_code=False, use_safetensors=True, device_map={'': 0}, dtype=torch.bfloat16,
            attn_implementation='eager')
        model = PeftModel.from_pretrained(model, args.reference_adapter, adapter_name='reference',
                                         local_files_only=True, is_trainable=False)
        model.load_adapter(args.candidate_adapter, adapter_name='candidate', local_files_only=True, is_trainable=False)
        for arm, path in adapters.items():
            select_adapter(model, arm)
            old.verify_loaded_adapter(model, path, arm)
        runtime.check_deadline(args.deadline_utc)
        state['status'] = 'evaluating'
        runtime.write_json(output / 'run.json', state)
        result = generate_pairs(model, tokenizer, rows, prepared, output / 'evaluation', identity, args.deadline_utc)
        for arm, path in adapters.items():
            old.verify_loaded_adapter(model, path, arm)
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
