"""Frozen contextual two-arm server experiment; no provisioning or semantic scoring."""
import argparse
from collections import Counter
import gc
import hashlib
import json
import math
import os
from pathlib import Path
import re
import time

try:
    from . import bundle, contextual_train as core, dev_assisted as qualified, dev_diagnostic as frozen, palref_eval as protocol, runtime
except ImportError:
    import bundle
    import contextual_train as core
    import dev_assisted as qualified
    import dev_diagnostic as frozen
    import palref_eval as protocol
    import runtime

PACKAGE_SHA256 = '7920e92e73bb1fee9d606b67c2055c0e114d225252d72bddcfb0071abbe7a7c1'
AUX_PROMPT = ('Translate the selected expression from this Middle Persian passage into Farsi, '
              'using the passage as context. Return only its contextual meaning. Preserve negation '
              'and uncertainty. Do not invent missing context.\nSource:\n{source}\nSelected expression:\n{focus}')
SETTINGS = {**core.OPTIMIZER, 'seed': 3407, 'max_steps': 48, 'gradient_accumulation_steps': 16,
            'learning_rate': 0.0001, 'warmup_steps': 2, 'bf16': True, 'gradient_checkpointing': True}
FILES = {'proposals.jsonl', 'extension-proposals.jsonl', 'qualification-decision-v2.json',
         'auxiliary-tokenized.jsonl', 'regular-id-order.jsonl', 'ordered-slots.jsonl', 'dev-prompt-identities.json'}
HELPER_SHA256 = {
    'contextual_train.py': '86ce4762a9a4e9356803ba2ed6e1c4c6689982a4cee3dab9b5e4bedd62b38122',
    'runtime.py': '5f42bcc70dd80de22c624130a07b179b134cec767164e33cb28604f1b497298d',
    'bundle.py': '60094706124ee58b78a2b73b6a43c30eb9310a2a1d3786f83749e95b597b1a2d',
    'dev_assisted.py': '4334db8c1097c220dbcce75b3d30287a29c43c5482ab71313c3db9cf287fec4d',
    'dev_diagnostic.py': '9d459482f3b7189cc2109bd68e36d14e77693df64f41574ff952d71bc6725d11',
    'palref_eval.py': '050a38880c68113ca5e5ebc4abd26945d05959eeda52f5df64f00292acfe4a49'}
sha, canonical = qualified.sha, qualified.canonical


def emit(phase, **details):
    print(json.dumps({'phase': phase, **details}), flush=True)


def read_package(path, expected_sha256):
    path = Path(path).resolve()
    if expected_sha256 != PACKAGE_SHA256 or runtime.digest(path / 'manifest.json') != expected_sha256:
        raise ValueError('Frozen package manifest differs')
    paths = list(path.rglob('*'))
    if any(p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(path) for p in paths):
        raise ValueError('Package must contain only its exact regular-file inventory')
    if {p.relative_to(path).as_posix() for p in paths} != FILES | {'manifest.json'}:
        raise ValueError('Package inventory differs')
    manifest = runtime.read_json(path / 'manifest.json')
    if (set(manifest['files']) != FILES or manifest['settings'] != SETTINGS
            or manifest['qualified_train_sha256'] != qualified.TRAIN_SHA256
            or manifest['evaluation_inputs_sha256'] != frozen.INPUTS_SHA256
            or manifest['uniform_evaluation_contract_sha256'] != qualified.LOCAL_EVALUATION_CONTRACT_SHA256
            or manifest['auxiliary_prompt_template'] != AUX_PROMPT
            or manifest['slots_per_arm'] != 768 or manifest['auxiliary_parents'] != 12
            or manifest['regular_parents'] != 720 or manifest['expert_adjudicated'] is not False):
        raise ValueError('Frozen package contract differs')
    payload = {}
    for name, entry in manifest['files'].items():
        data = (path / name).read_bytes()
        if len(data) != entry['bytes'] or sha(data) != entry['sha256']:
            raise ValueError('Package file hash/size differs: ' + name)
        payload[name] = bundle.jsonl(data) if name.endswith('.jsonl') else json.loads(data)
    return manifest, payload


def prepare_streams(manifest, payload, train_path, tokenizer):
    if runtime.digest(train_path) != qualified.TRAIN_SHA256:
        raise ValueError('Qualified TRAIN bytes differ')
    rows = bundle.jsonl(Path(train_path).read_bytes())
    by_id = {r['id']: r for r in rows}
    if len(rows) != len(by_id) or len(rows) != 2237:
        raise ValueError('Qualified TRAIN coverage differs')
    proposals = payload['proposals.jsonl'] + payload['extension-proposals.jsonl']
    decision = payload['qualification-decision-v2.json']
    decisions = {x['id']: x for x in decision['decisions']}
    if (len(proposals) != 12 or len({p['record_id'] for p in proposals}) != 12
            or len({p['work_id'] for p in proposals}) != 9 or len(decisions) != 12
            or set(decisions) != {p['id'] for p in proposals} or decision['expert_adjudicated'] is not False
            or manifest['qualification_decision_sha256'] != manifest['files']['qualification-decision-v2.json']['sha256']):
        raise ValueError('Qualification membership differs')
    for name in ('proposals.jsonl', 'extension-proposals.jsonl'):
        if decision['bindings'][name] != manifest['files'][name]['sha256']:
            raise ValueError('Qualification proposal binding differs')
    for name, checksum in manifest['source_review_paths'].items():
        if decision['bindings'].get(name) != checksum:
            raise ValueError('Source-review attribution differs')
    auxiliary = []
    for p in proposals:
        parent, d = by_id[p['train_id']], decisions[p['id']]
        source, focus, target = p['source_text'], p['source_focus'], p['proposed_target']
        if (d['status'] != 'PROVISIONAL_DEVELOPMENT_QUALIFIED' or d['source_focus'] != focus
                or d['target'] != target or not d['limits'] or p['expert_adjudicated'] is not False
                or p['parent_disposition'] not in {'ELIGIBLE', 'ELIGIBLE_WITH_QUALIFICATIONS'}
                or source != parent['text'] or p['reference_fa'] != parent['target']
                or any(p[k] != parent[k] for k in ('record_id', 'work_id', 'credit', 'source_language', 'target_language'))):
            raise ValueError('Annotation parent/source/qualification differs: ' + p['id'])
        for text, key in ((source, 'source_sha256'), (target, 'target_sha256'), (parent['target'], 'reference_sha256')):
            if sha(text.encode()) != p[key]:
                raise ValueError('Annotation text hash differs')
        for text in (source, focus, target):
            bundle.reject_controls(text, tokenizer.all_special_tokens)
            if text != text.strip():
                raise ValueError('Annotation whitespace must remain exact')
        starts = [m.start() for m in re.finditer('(?=' + re.escape(focus) + ')', source)]
        if len(starts) != 1:
            raise ValueError('Focus must identify one exact occurrence')
        start, end = starts[0], starts[0] + len(focus)
        if p['source_span'] != [start, end] or p['source_utf8_span'] != [len(source[:start].encode()), len(source[:end].encode())]:
            raise ValueError('Focus offsets differ')
        if p['target_kind'] == 'qualified_published_witness_subspan':
            a, b = p['reference_target_span']
            if parent['target'][a:b] != target:
                raise ValueError('Published target span differs')
        elif p['target_kind'] != 'published_occurrence_gloss' or p['id'] != 'CONTEXT1-108000001':
            raise ValueError('Unexpected target attribution')
        prefix = tokenizer.apply_chat_template([{'role': 'user', 'content': AUX_PROMPT.format(source=source, focus=focus)}],
            tokenize=False, add_generation_prompt=True, enable_thinking=False)
        prefix_ids = tokenizer(prefix, add_special_tokens=False)['input_ids']
        ids = tokenizer(prefix + target + bundle.TERMINATOR, add_special_tokens=False)['input_ids']
        if ids[:len(prefix_ids)] != prefix_ids or tokenizer.decode(ids[len(prefix_ids):], skip_special_tokens=False,
                clean_up_tokenization_spaces=False) != target + bundle.TERMINATOR:
            raise ValueError('Auxiliary answer token boundary/decoding differs')
        row = {k: parent[k] for k in bundle.SOURCE_KEYS}
        row.update(target=target, input_ids=ids, attention_mask=[1] * len(ids),
                   labels=[-100] * len(prefix_ids) + ids[len(prefix_ids):], prompt_tokens=len(prefix_ids))
        bundle.validate_row(row)
        auxiliary.append(dict(row, annotation_id=p['id'], task='contextual_expression', train_id=p['train_id']))
    if auxiliary != payload['auxiliary-tokenized.jsonl']:
        raise ValueError('Auxiliary token reconstruction differs')
    excluded = {p['record_id'] for p in proposals}
    regular = sorted((r for r in rows if r['record_id'] not in excluded),
                     key=lambda r: sha(('contextual-pilot-v1|3407|' + r['id']).encode()))[:720]
    if [{'id': r['id'], 'record_id': r['record_id']} for r in regular] != payload['regular-id-order.jsonl']:
        raise ValueError('Deterministic regular selection differs')
    for saved in regular + [by_id[p['train_id']] for p in proposals]:
        if bundle.tokenize_row({k: saved[k] for k in bundle.SOURCE_KEYS}, tokenizer) != saved:
            raise ValueError('Ordinary translation tokens changed')
    order = list(range(12))
    rotated = order[6:] + order[:6]
    indices = order + order[::-1] + rotated + rotated[::-1]
    slots, streams = [], {a: [] for a in core.ARMS}
    for update, index in enumerate(indices, 1):
        for microstep, row in enumerate(regular[(update - 1) * 15:update * 15], 1):
            slots.append(dict(update=update, microstep=microstep, record_id=row['record_id'],
                              control_id=row['id'], candidate_id=row['id'], kind='ordinary_translation'))
            for arm in core.ARMS: streams[arm].append(row)
        p, aux = proposals[index], auxiliary[index]
        slots.append(dict(update=update, microstep=16, record_id=p['record_id'], control_id=p['train_id'],
                          candidate_id=p['train_id'], candidate_annotation_id=p['id'], kind='designated_parent'))
        streams['control'].append(by_id[p['train_id']])
        streams['candidate'].append(aux)
    if slots != payload['ordered-slots.jsonl']:
        raise ValueError('Balanced ordered slot schedule differs')
    core.validate_streams(streams, SETTINGS)
    return streams


def prepare_prompts(rows, identities, tokenizer, context_limit):
    expected = {r['id']: r for r in identities}
    if len(identities) != len(expected) or set(expected) != {r['id'] + ':plain' for r in rows}:
        raise ValueError('Old plain-prompt identity coverage differs')
    prepared = {}
    for row in rows:
        ids = tokenizer.apply_chat_template(qualified.messages(row, 'plain', []), tokenize=True,
                return_dict=False, add_generation_prompt=True, enable_thinking=False)
        if (expected[row['id'] + ':plain'] != dict(id=row['id'] + ':plain', input_tokens=len(ids),
                rendered_input_ids_sha256=sha(canonical(ids))) or not ids or len(ids) + protocol.MAX_TOKENS > context_limit):
            raise ValueError('Frozen plain prompt tokens/context differ')
        prepared[row['id']] = ids
    return prepared


def training_canary(model, streams, deadline_utc):
    import torch
    import torch.nn.functional as F
    runtime.check_deadline(deadline_utc)
    row = max((r for rows in streams.values() for r in rows), key=lambda r: len(r['input_ids']))
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant': False})
    model.train()
    model.zero_grad(set_to_none=True)
    before = core.tensor_digest(core.trainables(model))
    torch.cuda.reset_peak_memory_stats()
    torch.cuda.synchronize()
    start = time.monotonic()
    try:
        inputs = {k: torch.tensor([row[k]], device='cuda') for k in ('input_ids', 'attention_mask', 'labels')}
        with torch.autocast(device_type='cuda', dtype=torch.bfloat16):
            response = model(**inputs, use_cache=False, logits_to_keep=0, return_dict=True)
        manual = F.cross_entropy(response.logits[:, :-1].float().reshape(-1, response.logits.shape[-1]),
                                 inputs['labels'][:, 1:].reshape(-1), ignore_index=-100, reduction='mean')
        if not torch.isfinite(response.loss).item() or not math.isclose(manual.item(), response.loss.item(), rel_tol=1e-4, abs_tol=1e-4):
            raise FloatingPointError('NF4 canary masked loss disagreement/nonfinite loss')
        response.loss.backward()
        grads = [p.grad for p in core.trainables(model).values() if p.grad is not None]
        if not grads or any(not torch.isfinite(g).all().item() for g in grads) or not any(g.abs().sum().item() > 0 for g in grads):
            raise FloatingPointError('NF4 canary requires nonzero finite LoRA gradients')
        if any(p.grad is not None for p in model.parameters() if not p.requires_grad):
            raise RuntimeError('NF4 canary updated frozen gradient state')
        if core.tensor_digest(core.trainables(model)) != before:
            raise RuntimeError('Zero-update canary changed adapter tensors')
        torch.cuda.synchronize()
        runtime.check_deadline(deadline_utc)
        return dict(status='passed', optimizer_updates=0, id=row['id'], input_tokens=len(row['input_ids']),
                    logits_shape=list(response.logits.shape), native_loss=response.loss.item(), manual_loss=manual.item(),
                    loss_atol=1e-4, loss_rtol=1e-4, autocast_dtype='bfloat16', gradient_checkpointing=True,
                    gradient_checkpointing_use_reentrant=False, elapsed_seconds=time.monotonic() - start,
                    peak_gpu_bytes=torch.cuda.max_memory_allocated(), adapter_sha256=before)
    finally:
        model.zero_grad(set_to_none=True)


def verify_adapter_architecture(config, original):
    for key in ('r', 'lora_alpha', 'lora_dropout', 'bias', 'peft_type', 'task_type'):
        if config[key] != original[key]:
            raise ValueError('New adapter architecture differs: ' + key)
    left, right = config['target_modules'], original['target_modules']
    if isinstance(left, list) and isinstance(right, list):
        if (any(not isinstance(x, str) or not x for x in left + right)
                or len(set(left)) != len(left) or len(set(right)) != len(right) or set(left) != set(right)):
            raise ValueError('New adapter target modules differ')
    elif not isinstance(left, str) or left != right:
        raise ValueError('New adapter target modules differ')


def verify_new_adapters(training, original_adapter):
    import torch
    from safetensors import safe_open
    root = Path(training)
    result = runtime.read_json(root / 'run.json')
    if result.get('status') != 'completed' or result['settings'] != SETTINGS:
        raise ValueError('Both fixed training phases must complete')
    original_config = runtime.read_json(Path(original_adapter) / 'adapter_config.json')
    identities = {}
    for arm in core.ARMS:
        info, path = result['arms'][arm], root / arm / 'adapter'
        if (info.get('status') != 'completed' or info['completed_steps'] != 48 or info['consumed_slots'] != 768
                or info['parent_order_verified'] is not True or info['initial_adapter_sha256'] != result['initial_adapter_sha256']
                or info['model_accepts_loss_kwargs'] is not False or info['optimizer_initially_empty'] is not True):
            raise ValueError('Incomplete/faulted arm training identity')
        if {p.name for p in path.iterdir()} != set(info['adapter_files']):
            raise ValueError('Saved adapter inventory differs')
        runtime.checked_files(path, info['adapter_files'])
        config = runtime.read_json(path / 'adapter_config.json')
        verify_adapter_architecture(config, original_config)
        with safe_open(path / 'adapter_model.safetensors', framework='pt', device='cpu') as saved:
            if not saved.keys() or any(not torch.isfinite(saved.get_tensor(k)).all().item() for k in saved.keys()):
                raise ValueError('Empty/nonfinite saved adapter')
        identities[arm] = dict(files=info['adapter_files'], final_tensor_sha256=info['final_adapter_sha256'],
                               new_phase_steps=48, original_adapter_step=280)
    return identities


def verify_loaded_adapter(model, path, arm):
    import torch
    from peft import get_peft_model_state_dict
    from safetensors import safe_open
    current = get_peft_model_state_dict(model, adapter_name=arm)
    with safe_open(Path(path) / 'adapter_model.safetensors', framework='pt', device='cpu') as saved:
        if set(current) != set(saved.keys()):
            raise ValueError('Loaded adapter tensor keys differ')
        for key, actual in current.items():
            expected = saved.get_tensor(key)
            actual = actual.detach().cpu()
            if actual.dtype != expected.dtype or actual.shape != expected.shape or not torch.equal(actual, expected):
                raise ValueError('Loaded adapter tensor differs: ' + key)


def generate_pairs(model, tokenizer, rows, prepared, output, identity, deadline_utc, device='cuda'):
    import torch
    from transformers import DynamicCache, StoppingCriteriaList
    deadline = runtime.check_deadline(deadline_utc)
    ordered = [(r, {'plain': 'control', 'assisted': 'candidate'}[c]) for r, c in qualified.schedule(rows)]
    ids = [r['id'] + ':' + arm for r, arm in ordered]
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    run = {**identity, 'identity_sha256': sha(canonical(identity)), 'status': 'running', 'schedule': ids,
           'scheduled_outputs': 48, 'attempted_outputs': 0, 'recorded_outputs': 0, 'completed_outputs': 0,
           'completed_cases': 0, 'active_output_id': None, 'unattempted_output_ids': ids.copy(),
           'canary': {'status': 'not_started'}, 'scoring_performed': False, 'expert_adjudicated': False}
    runtime.write_json(output / 'run.json', run)
    try:
        model.set_adapter('control')
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
                            or set(state.available_adapters) != set(core.ARMS) or model.training
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
                run['completed_cases'] = sum(n == 2 for n in completed.values())
                runtime.write_json(output / 'run.json', run)
                emit('generation_case_recorded', case_id=row['id'], arm=arm, status=result['status'],
                     recorded_outputs=run['recorded_outputs'], completed_outputs=run['completed_outputs'])
                if failure is not None: raise failure
                if result['status'] not in {'success', 'abstain'}:
                    raise RuntimeError('First attempt failed: ' + result['status'])
        if run['completed_outputs'] != 48 or run['completed_cases'] != 24 or run['unattempted_output_ids']:
            raise RuntimeError('Incomplete paired evaluation')
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
    for module in (core, runtime, bundle, qualified, frozen, protocol):
        if runtime.digest(module.__file__) != HELPER_SHA256[Path(module.__file__).name]:
            raise ValueError('Frozen helper source differs')
    manifest, payload = read_package(args.package, args.package_manifest_sha256)
    folder = runtime.verified_bundle(args.bundle)
    contract = runtime.contract_at(folder / 'contract.json')
    base = runtime.verify_base(args.base)
    runtime.checked_files(args.tokenizer, bundle.TOKENIZER_HASHES)
    qualified.verify_adapter(args.adapter, contract, base)
    rows = frozen.read_inputs(args.inputs)
    environment = runtime.gpu_admission()
    import torch
    from transformers import AutoTokenizer, BitsAndBytesConfig, Gemma4ForConditionalGeneration, set_seed
    from peft import PeftModel, prepare_model_for_kbit_training
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, local_files_only=True, trust_remote_code=False)
    streams = prepare_streams(manifest, payload, folder / 'train.jsonl', tokenizer)
    context = runtime.read_json(Path(args.base) / 'config.json')['text_config']['max_position_embeddings']
    prepared = prepare_prompts(rows, payload['dev-prompt-identities.json'], tokenizer, context)
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    identity = dict(experiment_id=manifest['experiment_id'], package_manifest_sha256=PACKAGE_SHA256,
        qualified_train_sha256=qualified.TRAIN_SHA256, evaluation_inputs_sha256=frozen.INPUTS_SHA256,
        inputs_sha256=frozen.INPUTS_SHA256,
        original_adapter_files=qualified.ADAPTER_FILES, original_adapter_manifest_sha256=qualified.ADAPTER_MANIFEST_SHA256,
        model_id=runtime.MODEL_ID, model_revision=runtime.REVISION, base_files=base['files'],
        tokenizer_files=bundle.TOKENIZER_HASHES, runner_sha256=runtime.digest(__file__), helper_sha256=HELPER_SHA256,
        environment=environment, settings=SETTINGS, seed=42, decoding='greedy', enable_thinking=False,
        max_new_tokens=protocol.MAX_TOKENS, max_generation_seconds=protocol.CASE_SECONDS, eos_token_ids=protocol.EOS,
        evaluation_prompt='dev_assisted.messages(row, plain, [])', uniform_evaluation_contract_sha256=qualified.LOCAL_EVALUATION_CONTRACT_SHA256,
        prompts=payload['dev-prompt-identities.json'], deadline_utc=args.deadline_utc,
        expert_adjudicated=False, quality_validated=False, scoring_performed=False)
    state = {**identity, 'status': 'preparing', 'training_canary': {'status': 'not_started'}}
    runtime.write_json(output / 'run.json', state)
    model = None
    try:
        set_seed(SETTINGS['seed'])
        runtime.check_deadline(args.deadline_utc)
        emit('loading_nf4')
        model = Gemma4ForConditionalGeneration.from_pretrained(args.base, local_files_only=True, trust_remote_code=False,
            use_safetensors=True, device_map={'': 0}, dtype=torch.bfloat16, attn_implementation='eager',
            quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
                                                  bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16))
        model = prepare_model_for_kbit_training(model, gradient_checkpointing_kwargs={'use_reentrant': False})
        model = PeftModel.from_pretrained(model, args.adapter, local_files_only=True, is_trainable=True)
        model.config.use_cache = model.config.text_config.use_cache = False
        runtime.assert_adapter(model)
        state['training_canary'] = {'status': 'running'}
        runtime.write_json(output / 'run.json', state)
        emit('training_canary')
        state['training_canary'] = training_canary(model, streams, args.deadline_utc)
        state['status'] = 'training'
        runtime.write_json(output / 'run.json', state)
        emit('training', canary_elapsed_seconds=state['training_canary']['elapsed_seconds'])
        trained = core.train_two_arms(model, streams, SETTINGS, output / 'training', args.deadline_utc)
        identity['adapters'] = verify_new_adapters(output / 'training', args.adapter)
        state.update(adapters=identity['adapters'], training_status=trained['status'], status='reloading_bf16')
        runtime.write_json(output / 'run.json', state)
        del model
        model = None
        gc.collect()
        torch.cuda.empty_cache()
        state['nf4_release_memory'] = dict(allocated_bytes=torch.cuda.memory_allocated(), reserved_bytes=torch.cuda.memory_reserved())
        runtime.write_json(output / 'run.json', state)
        emit('reloading_bf16', **state['nf4_release_memory'])
        runtime.check_deadline(args.deadline_utc)
        set_seed(42)
        model = Gemma4ForConditionalGeneration.from_pretrained(args.base, local_files_only=True, trust_remote_code=False,
            use_safetensors=True, device_map={'': 0}, dtype=torch.bfloat16, attn_implementation='eager')
        model = PeftModel.from_pretrained(model, output / 'training/control/adapter', adapter_name='control',
                                         local_files_only=True, is_trainable=False)
        model.load_adapter(output / 'training/candidate/adapter', adapter_name='candidate', local_files_only=True, is_trainable=False)
        for arm in core.ARMS:
            verify_loaded_adapter(model, output / 'training' / arm / 'adapter', arm)
        state['status'] = 'evaluating'
        runtime.write_json(output / 'run.json', state)
        emit('evaluating')
        evaluated = generate_pairs(model, tokenizer, rows, prepared, output / 'evaluation', identity, args.deadline_utc)
        state.update(status='completed', evaluation_completed_outputs=evaluated['completed_outputs'],
                     evaluation_completed_cases=evaluated['completed_cases'], training_steps_per_arm=48)
        runtime.write_json(output / 'run.json', state)
        emit('completed', training_steps_per_arm=48, evaluation_completed_outputs=evaluated['completed_outputs'])
        return state
    except BaseException as error:
        if state['training_canary']['status'] == 'running': state['training_canary']['status'] = 'failed'
        state.update(status='incomplete', error_type=type(error).__name__, error=str(error))
        runtime.write_json(output / 'run.json', state)
        raise
    finally:
        del model
        gc.collect()
        torch.cuda.empty_cache()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ('bundle', 'base', 'tokenizer', 'adapter', 'package', 'package-manifest-sha256', 'inputs', 'output', 'deadline-utc'):
        parser.add_argument('--' + field, required=True)
    run(parser.parse_args(argv))


if __name__ == '__main__':
    main()
