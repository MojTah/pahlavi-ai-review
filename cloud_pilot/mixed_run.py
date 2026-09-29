"""Fixed mixed supervision continuation and candidate-only source-only DEV24."""
import argparse
from collections import Counter
import gc
import json
import os
from pathlib import Path
import time
try:
    from . import mixed_train as core, contextual_run as old, bundle, dev_assisted as qualified, dev_diagnostic as frozen, palref_eval as protocol, runtime
except ImportError:
    import mixed_train as core
    import contextual_run as old
    import bundle
    import dev_assisted as qualified
    import dev_diagnostic as frozen
    import palref_eval as protocol
    import runtime
SETTINGS = core.SETTINGS
sha, canonical, emit = qualified.sha, qualified.canonical, old.emit


def read_data(path, manifest_path, settings):
    if runtime.digest(manifest_path) != settings['data_manifest_sha256'] or runtime.digest(path) != settings['train_sha256']:
        raise ValueError('Mixed data/manifest checksum differs')
    manifest = runtime.read_json(manifest_path)
    entry = manifest['outputs']['train.jsonl']
    if entry['sha256'] != settings['train_sha256'] or entry['bytes'] != Path(path).stat().st_size or entry['rows'] != 1536:
        raise ValueError('Mixed manifest training binding differs')
    rows = [json.loads(line) for line in Path(path).read_text('utf-8').splitlines()]
    ids = core.validate_rows(rows)
    pilot = manifest['pilot']
    if (pilot['selected_ids_in_order'] != ids or pilot['updates'] != 96 or pilot['microbatch'] != 1
            or pilot['gradient_accumulation'] != 16 or pilot['per_update'] != {'historical': 12, 'lexical': 2, 'other': 2}):
        raise ValueError('Mixed pilot contract/order differs')
    for offset in range(0, len(rows), 16):
        tasks = [r['task'] for r in rows[offset:offset+16]]
        if (tasks[:12] != ['historical-control-fa'] * 12
                or any(t not in {'lexical-fa', 'lexical-en', 'lexical-mmp-en'} for t in tasks[12:14])
                or any(t not in {'pedagogy-fa', 'documentary-en', 'inscription-fa', 'edition-spans-en'} for t in tasks[14:])):
            raise ValueError('Exact per-update 12:2:2 task order differs')
    return rows, manifest


def generate_candidate(model, tokenizer, rows, prepared, output, identity, deadline_utc, device='cuda'):
    import torch
    from transformers import DynamicCache, StoppingCriteriaList
    deadline = runtime.check_deadline(deadline_utc)
    ordered = [(r, 'candidate') for r, c in qualified.schedule(rows) if c == 'plain']
    ids = [r['id'] + ':' + arm for r, arm in ordered]
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    run = {**identity, 'identity_sha256': sha(canonical(identity)), 'status': 'running', 'schedule': ids,
           'scheduled_outputs': 24, 'attempted_outputs': 0, 'recorded_outputs': 0, 'completed_outputs': 0,
           'completed_cases': 0, 'active_output_id': None, 'unattempted_output_ids': ids.copy(),
           'canary': {'status': 'not_started'}, 'scoring_performed': False, 'expert_adjudicated': False}
    runtime.write_json(output / 'run.json', run)
    try:
        model.set_adapter('candidate')
        model.requires_grad_(False)
        model.eval()
        run['canary'] = {'status': 'running'}
        runtime.write_json(output / 'run.json', run)
        run['canary'] = qualified.prefill_canary(model, {(r['id'], 'plain'): prepared[r['id']] for r in rows}, deadline_utc)
        runtime.write_json(output / 'run.json', run)
        completed = Counter()
        with (output / 'predictions.jsonl').open('x', encoding='utf-8') as stream:
            for index, (row, arm) in enumerate(ordered):
                runtime.check_deadline(deadline_utc)
                run.update(active_output_id=ids[index], attempted_outputs=index + 1)
                runtime.write_json(output / 'run.json', run)
                start, new_ids, failure, hit_cap = time.monotonic(), [], None, False
                stopper = protocol.GenerationDeadline(start, deadline)
                try:
                    model.set_adapter(arm)
                    model.requires_grad_(False)
                    model.eval()
                    state = model.get_model_status()
                    if (state.enabled is not True or state.active_adapters != [arm] or state.merged_adapters != []
                            or set(state.available_adapters) != {'candidate'} or model.training
                            or any(p.requires_grad for p in model.parameters())):
                        raise RuntimeError('Frozen named adapter switching failed')
                    tokens = torch.tensor([prepared[row['id']]], device=device)
                    with torch.inference_mode():
                        generated = model.generate(input_ids=tokens, attention_mask=torch.ones_like(tokens),
                            past_key_values=DynamicCache(), use_cache=True, do_sample=False, num_beams=1,
                            max_new_tokens=protocol.MAX_TOKENS, pad_token_id=0, eos_token_id=protocol.EOS,
                            stopping_criteria=StoppingCriteriaList([stopper]))
                    new_ids = generated[0, len(prepared[row['id']]):].tolist()
                    stopper(None, None)
                    hit_cap = len(new_ids) >= protocol.MAX_TOKENS and new_ids[-1] not in protocol.EOS
                    result = protocol.prediction(row, tokenizer.decode(new_ids, skip_special_tokens=True),
                        time.monotonic() - start, timed_out=stopper.reason is not None, hit_cap=hit_cap)
                except BaseException as error:
                    failure = error
                    result = protocol.prediction(row, '', time.monotonic() - start)
                    result.update(status='error', error_type=type(error).__name__, error=str(error))
                result.update(id=ids[index], case_id=row['id'], record_id=row['record_id'], work_id=row['work_id'],
                    arm=arm, condition=arm, sequence=index + 1, identity_sha256=run['identity_sha256'],
                    adapter_sha256=identity['adapters'][arm]['files']['adapter_model.safetensors'],
                    input_tokens=len(prepared[row['id']]), rendered_input_ids_sha256=sha(canonical(prepared[row['id']])),
                    output_tokens=len(new_ids), output_token_ids=new_ids, output_sha256=sha(result['text'].encode()),
                    hit_output_cap_without_eos=hit_cap, stop_reason=stopper.reason)
                stream.write(json.dumps(result, ensure_ascii=False) + '\n')
                stream.flush()
                os.fsync(stream.fileno())
                run.update(recorded_outputs=index + 1, active_output_id=None, unattempted_output_ids=ids[index + 1:])
                if result['status'] in {'success', 'abstain'}:
                    run['completed_outputs'] += 1
                    completed[row['id']] += 1
                run['completed_cases'] = sum(n == 1 for n in completed.values())
                runtime.write_json(output / 'run.json', run)
                emit('generation_case_recorded', case_id=row['id'], arm=arm, status=result['status'],
                     recorded_outputs=run['recorded_outputs'], completed_outputs=run['completed_outputs'])
                if failure is not None: raise failure
                if result['status'] not in {'success', 'abstain'}:
                    raise RuntimeError('First attempt failed: ' + result['status'])
        if run['completed_outputs'] != 24 or run['completed_cases'] != 24 or run['unattempted_output_ids']:
            raise RuntimeError('Incomplete candidate evaluation')
        run['status'] = 'completed'
        runtime.write_json(output / 'run.json', run)
        return run
    except BaseException as error:
        if run['canary']['status'] == 'running': run['canary']['status'] = 'failed'
        run.update(status='incomplete', error_type=type(error).__name__, error=str(error))
        runtime.write_json(output / 'run.json', run)
        raise


def run(args):
    runtime.offline()
    runtime.check_deadline(args.deadline_utc)
    settings = runtime.read_json(args.settings)
    for name, expected in settings['script_hashes'].items():
        if runtime.digest(Path(__file__).with_name(name)) != expected:
            raise ValueError('Mixed script checksum differs: ' + name)
    for module in (old.core, runtime, bundle, qualified, frozen, protocol):
        if runtime.digest(module.__file__) != old.HELPER_SHA256[Path(module.__file__).name]:
            raise ValueError('Qualified helper source differs')
    folder = runtime.verified_bundle(args.bundle)
    contract = runtime.contract_at(folder / 'contract.json')
    base = runtime.verify_base(args.base)
    runtime.checked_files(args.tokenizer, bundle.TOKENIZER_HASHES)
    qualified.verify_adapter(args.adapter, contract, base)
    original_config = runtime.read_json(Path(args.adapter) / 'adapter_config.json')
    if any(original_config[k] != v for k, v in {'r': 16, 'lora_alpha': 32, 'lora_dropout': 0.0}.items()):
        raise ValueError('Original LoRA configuration differs')
    train_rows, manifest = read_data(args.train, args.data_manifest, settings)
    rows = frozen.read_inputs(args.inputs)
    environment = runtime.gpu_admission()
    import torch
    from transformers import AutoTokenizer, BitsAndBytesConfig, Gemma4ForConditionalGeneration, set_seed
    from peft import PeftModel, prepare_model_for_kbit_training
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, local_files_only=True, trust_remote_code=False)
    context = runtime.read_json(Path(args.base) / 'config.json')['text_config']['max_position_embeddings']
    prepared = old.prepare_prompts(rows, settings['prompt_identities'], tokenizer, context)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    identity = dict(experiment_id='mixed-supervision-20260929', settings=SETTINGS,
        data_manifest_sha256=settings['data_manifest_sha256'], train_sha256=settings['train_sha256'],
        inputs_sha256=frozen.INPUTS_SHA256, original_adapter_files=qualified.ADAPTER_FILES,
        original_adapter_manifest_sha256=qualified.ADAPTER_MANIFEST_SHA256, original_adapter_step=280,
        runner_sha256=runtime.digest(__file__), script_hashes=settings['script_hashes'],
        model_id=runtime.MODEL_ID, model_revision=runtime.REVISION, environment=environment,
        seed=42, decoding='greedy', enable_thinking=False, max_new_tokens=protocol.MAX_TOKENS,
        evaluation_prompt='dev_assisted.messages(row, plain, [])', prompts=settings['prompt_identities'],
        deadline_utc=args.deadline_utc, quality_validated=False, expert_adjudicated=False, scoring_performed=False)
    state = {**identity, 'status': 'loading_nf4'}
    runtime.write_json(output / 'run.json', state)
    model = None
    try:
        set_seed(3407)
        emit('loading_nf4')
        model = Gemma4ForConditionalGeneration.from_pretrained(args.base, local_files_only=True, trust_remote_code=False,
            use_safetensors=True, device_map={'': 0}, dtype=torch.bfloat16, attn_implementation='eager',
            quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
                bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16))
        model = prepare_model_for_kbit_training(model, gradient_checkpointing_kwargs={'use_reentrant': False})
        model = PeftModel.from_pretrained(model, args.adapter, local_files_only=True, is_trainable=True)
        model.config.use_cache = model.config.text_config.use_cache = False
        state['numerical_canary'] = old.training_canary(model, {'candidate': train_rows}, args.deadline_utc)
        state['status'] = 'training'
        runtime.write_json(output / 'run.json', state)
        trained = core.train_one(model, train_rows, SETTINGS, output / 'training', args.deadline_utc)
        adapter = output / 'training/adapter'
        old.verify_adapter_architecture(runtime.read_json(adapter / 'adapter_config.json'), original_config)
        runtime.checked_files(adapter, trained['adapter_files'])
        identity['adapters'] = {'candidate': {'files': trained['adapter_files'],
            'final_tensor_sha256': trained['final_adapter_sha256'], 'new_phase_steps': 96, 'original_adapter_step': 280}}
        state.update(adapters=identity['adapters'], status='reloading_bf16', training_status=trained['status'])
        runtime.write_json(output / 'run.json', state)
        del model
        model = None
        gc.collect()
        torch.cuda.empty_cache()
        runtime.check_deadline(args.deadline_utc)
        set_seed(42)
        emit('reloading_bf16')
        model = Gemma4ForConditionalGeneration.from_pretrained(args.base, local_files_only=True, trust_remote_code=False,
            use_safetensors=True, device_map={'': 0}, dtype=torch.bfloat16, attn_implementation='eager')
        model = PeftModel.from_pretrained(model, adapter, adapter_name='candidate', local_files_only=True, is_trainable=False)
        old.verify_loaded_adapter(model, adapter, 'candidate')
        state['status'] = 'evaluating'
        runtime.write_json(output / 'run.json', state)
        evaluated = generate_candidate(model, tokenizer, rows, prepared, output / 'evaluation', identity, args.deadline_utc)
        state.update(status='completed', training_steps=96, evaluation_completed_outputs=evaluated['completed_outputs'])
        runtime.write_json(output / 'run.json', state)
        emit('completed', training_steps=96, evaluation_completed_outputs=evaluated['completed_outputs'])
    except BaseException as error:
        state.update(status='incomplete', error_type=type(error).__name__, error=str(error))
        runtime.write_json(output / 'run.json', state)
        raise
    finally:
        del model
        gc.collect()
        torch.cuda.empty_cache()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('bundle', 'base', 'tokenizer', 'adapter', 'train', 'data-manifest', 'settings', 'inputs', 'output', 'deadline-utc'):
        parser.add_argument('--' + name, required=True)
    run(parser.parse_args())


if __name__ == '__main__':
    main()

