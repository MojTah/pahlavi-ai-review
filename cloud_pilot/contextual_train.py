"""Two fresh, ordered LoRA optimization phases on an already loaded model."""
import hashlib
import json
import math
import os
from pathlib import Path
import pickle
import random

try:
    from . import runtime
except ImportError:
    import runtime

ARMS = ('control', 'candidate')
OPTIMIZER = dict(optim='adamw_torch', weight_decay=0.0, adam_beta1=0.9,
                 adam_beta2=0.999, adam_epsilon=1e-8, max_grad_norm=1.0,
                 lr_scheduler_type='linear')


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()


def validate_streams(streams, settings):
    required = {'seed', 'max_steps', 'gradient_accumulation_steps', 'learning_rate', 'warmup_steps'}
    if set(settings) - required - {'bf16', 'gradient_checkpointing'} - set(OPTIMIZER) or not required <= set(settings):
        raise ValueError('Unexpected or missing settings')
    if any(settings.get(key, value) != value for key, value in OPTIMIZER.items()):
        raise ValueError('Optimizer defaults differ from the declared fixed recipe')
    for key in ('seed', 'max_steps', 'gradient_accumulation_steps', 'warmup_steps'):
        if type(settings[key]) is not int or settings[key] < (1 if key in ('max_steps', 'gradient_accumulation_steps') else 0):
            raise ValueError('Invalid integer setting: ' + key)
    if settings['warmup_steps'] >= settings['max_steps']:
        raise ValueError('Warmup must leave at least one optimization step')
    if type(settings['learning_rate']) not in (int, float) or not math.isfinite(settings['learning_rate']) or not 0 < settings['learning_rate'] <= 0.01:
        raise ValueError('Invalid learning rate')
    for key in ('bf16', 'gradient_checkpointing'):
        if key in settings and type(settings[key]) is not bool:
            raise ValueError('Expected boolean: ' + key)
    slots = settings['max_steps'] * settings['gradient_accumulation_steps']
    if not isinstance(streams, dict) or set(streams) != set(ARMS):
        raise ValueError('Exactly control and candidate streams required')
    for arm in ARMS:
        if not isinstance(streams[arm], list) or len(streams[arm]) != slots:
            raise ValueError('Stream length must equal steps times accumulation')
        for row in streams[arm]:
            if not isinstance(row, dict) or not {'id', 'input_ids', 'attention_mask', 'labels'} <= set(row):
                raise ValueError('Missing tokenized row fields')
            if not isinstance(row['id'], str) or not row['id'].strip():
                raise ValueError('Invalid parent slot ID')
            ids, labels, mask = (row[k] for k in ('input_ids', 'labels', 'attention_mask'))
            if any(not isinstance(x, list) for x in (ids, labels, mask)) or not 1 < len(ids) <= 2048:
                raise ValueError('Invalid token array')
            if any(type(x) is not int or x < 0 for x in ids) or mask != [1] * len(ids) or len(labels) != len(ids):
                raise ValueError('Invalid tokens/mask/labels')
            supervised = [i for i, x in enumerate(labels) if x != -100]
            if not supervised or supervised[0] == 0 or labels != [-100] * supervised[0] + ids[supervised[0]:]:
                raise ValueError('Contiguous answer-only labels required')
            if any(type(x) is not int for x in labels):
                raise ValueError('Labels must be integer tokens')
    ids = [r['id'] for r in streams['control']]
    if [r['id'] for r in streams['candidate']] != ids:
        raise ValueError('Arms must have exactly the same ordered parent slots')
    return ids


def tensor_digest(values):
    import torch
    result = hashlib.sha256()
    for name, value in sorted(values.items()):
        value = value.detach().cpu().contiguous()
        result.update(canonical([name, str(value.dtype), list(value.shape)]))
        result.update(value.reshape(-1).view(torch.uint8).numpy().tobytes())
    return result.hexdigest()


def trainables(model):
    runtime.assert_adapter(model)
    return {name: p for name, p in model.named_parameters() if p.requires_grad}


def restore_adapter(model, initial):
    import torch
    current = trainables(model)
    if current.keys() != initial.keys():
        raise ValueError('Trainable tensor keys changed')
    with torch.no_grad():
        for name, p in current.items():
            value = initial[name]
            if p.shape != value.shape or p.dtype != value.dtype:
                raise ValueError('Trainable tensor shape/dtype changed: ' + name)
            p.copy_(value)
    model.zero_grad(set_to_none=True)
    if tensor_digest(current) != tensor_digest(initial) or any(p.grad is not None for p in model.parameters()):
        raise RuntimeError('Exact adapter restoration/gradient reset failed')


def rng_digest():
    import numpy as np
    import torch
    states = (random.getstate(), np.random.get_state(), torch.get_rng_state().numpy().tobytes(),
              [x.cpu().numpy().tobytes() for x in torch.cuda.get_rng_state_all()] if torch.cuda.is_available() else [])
    return hashlib.sha256(pickle.dumps(states, protocol=4)).hexdigest()


def train_two_arms(model, streams, settings, output, deadline_utc):
    """Return evidence paths/state; leave final candidate weights loaded. Never resume."""
    import torch
    from transformers import Trainer, TrainingArguments, TrainerCallback, set_seed
    runtime.offline()
    ordered_ids = validate_streams(streams, settings)
    settings = {**OPTIMIZER, 'bf16': True, 'gradient_checkpointing': True, **settings}
    runtime.check_deadline(deadline_utc)
    parameters = trainables(model)
    devices = {p.device for p in parameters.values()}
    if len(devices) != 1 or (next(iter(devices)).type == 'cuda' and torch.cuda.device_count() != 1):
        raise ValueError('Exactly one training device required')
    initial = {n: p.detach().cpu().clone() for n, p in parameters.items()}
    if any(not torch.isfinite(p).all().item() for p in initial.values()):
        raise ValueError('Nonfinite initial adapter')
    if any(value.requires_grad for value in model.buffers()):
        raise ValueError('Learned buffers are unsupported')
    buffers_sha = tensor_digest(dict(model.named_buffers()))
    initial_sha = tensor_digest(initial)
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    run = {'status': 'running', 'settings': dict(settings), 'initial_adapter_sha256': initial_sha,
           'initial_buffers_sha256': buffers_sha, 'arms': {}, 'quality_validated': False,
           'inference_performed': False, 'runtime_sha256': runtime.digest(runtime.__file__),
           'runner_sha256': runtime.digest(__file__), 'deadline_utc': deadline_utc,
           'stream_sha256': {a: hashlib.sha256(canonical(streams[a])).hexdigest() for a in ARMS},
           'scheduled_parent_ids': ordered_ids, 'scheduled_slots_per_arm': len(ordered_ids)}
    runtime.write_json(output / 'run.json', run)
    trainer = None
    first_rng = None
    try:
        for arm in ARMS:
            runtime.check_deadline(deadline_utc)
            trainer = None  # Discard the preceding optimizer/scheduler and callback references.
            restore_adapter(model, initial)
            if tensor_digest(dict(model.named_buffers())) != buffers_sha:
                raise RuntimeError('Model buffers changed between arms')
            set_seed(settings['seed'])
            pre_rng = rng_digest()
            if first_rng is not None and pre_rng != first_rng:
                raise RuntimeError('Initial RNG states differ')
            first_rng = pre_rng
            arm_dir = output / arm
            arm_dir.mkdir()
            consumed = []
            info = {'status': 'starting', 'completed_steps': 0, 'consumed_slots': 0,
                    'initial_adapter_sha256': tensor_digest(trainables(model)),
                    'initial_rng_sha256': pre_rng, 'optimizer_initially_empty': False,
                    'parent_order_verified': False}
            run['arms'][arm] = info
            runtime.write_json(output / 'run.json', run)

            def collate(batch):
                runtime.check_deadline(deadline_utc)
                if len(batch) != 1 or len(consumed) >= len(ordered_ids):
                    raise ValueError('Unexpected microbatch size or excess slot')
                row = batch[0]
                if row != streams[arm][len(consumed)]:
                    raise ValueError('Consumed stream order/content differs')
                consumed.append(row['id'])
                info['consumed_slots'] = len(consumed)
                return {k: torch.tensor([row[k]], dtype=torch.long)
                        for k in ('input_ids', 'attention_mask', 'labels')}

            with (arm_dir / 'progress.jsonl').open('x', encoding='utf-8') as progress:
                class Guard(TrainerCallback):
                    def on_train_begin(self, args, state, control, optimizer=None, **kwargs):
                        if optimizer is None or optimizer.state or state.global_step != 0:
                            raise RuntimeError('Fresh empty optimizer and step zero required')
                        info['optimizer_initially_empty'] = True
                        info['optimizer_initial_state_entries'] = len(optimizer.state)
                        info['initial_scheduler_step'] = trainer.lr_scheduler.last_epoch
                        if info['initial_scheduler_step'] != 0:
                            raise RuntimeError('Fresh scheduler step zero required')
                        info['train_begin_rng_sha256'] = rng_digest()
                        if arm == 'candidate' and info['train_begin_rng_sha256'] != run['arms']['control']['train_begin_rng_sha256']:
                            raise RuntimeError('Trainer initial RNG differs across arms')

                    def on_step_begin(self, args, state, control, **kwargs):
                        runtime.check_deadline(deadline_utc)

                    def on_pre_optimizer_step(self, args, state, control, **kwargs):
                        runtime.check_deadline(deadline_utc)
                        grads = [p.grad for p in trainables(model).values() if p.grad is not None]
                        if not grads or any(not torch.isfinite(g).all().item() for g in grads) or not any(g.abs().sum().item() > 0 for g in grads):
                            raise FloatingPointError('Nonzero finite adapter gradients required')
                        if any(p.grad is not None for p in model.parameters() if not p.requires_grad):
                            raise RuntimeError('Frozen parameter received a gradient')

                    def on_log(self, args, state, control, logs=None, **kwargs):
                        if logs and 'loss' in logs and not math.isfinite(logs['loss']):
                            raise FloatingPointError('Nonfinite training loss')

                    def on_step_end(self, args, state, control, **kwargs):
                        info['completed_steps'] = state.global_step
                        progress.write(json.dumps({'step': state.global_step, 'consumed_slots': len(consumed)}) + '\n')
                        progress.flush()
                        os.fsync(progress.fileno())
                        runtime.write_json(output / 'run.json', run)
                        runtime.check_deadline(deadline_utc)

                arguments = TrainingArguments(output_dir=str(arm_dir), max_steps=settings['max_steps'],
                    per_device_train_batch_size=1, gradient_accumulation_steps=settings['gradient_accumulation_steps'],
                    train_sampling_strategy='sequential', learning_rate=settings['learning_rate'],
                    warmup_steps=settings['warmup_steps'],
                    seed=settings['seed'], data_seed=settings['seed'], bf16=settings.get('bf16', True), fp16=False,
                    use_cpu=next(iter(devices)).type == 'cpu',
                    gradient_checkpointing=settings.get('gradient_checkpointing', True),
                    gradient_checkpointing_kwargs={'use_reentrant': False}, **OPTIMIZER,
                    save_strategy='no', logging_steps=1,
                    logging_nan_inf_filter=False, report_to='none', push_to_hub=False, disable_tqdm=True,
                    label_smoothing_factor=0.0, dataloader_num_workers=0, dataloader_pin_memory=False,
                    remove_unused_columns=False)
                trainer = Trainer(model=model, args=arguments, train_dataset=streams[arm],
                                  data_collator=collate, callbacks=[Guard()])
                trainer.model_accepts_loss_kwargs = False
                result = trainer.train()
            if consumed != ordered_ids or trainer.state.global_step != settings['max_steps'] or info['completed_steps'] != settings['max_steps']:
                raise RuntimeError('Incomplete ordered stream or optimizer updates')
            if not math.isfinite(result.training_loss):
                raise FloatingPointError('Nonfinite final training loss')
            if any(not torch.isfinite(p).all().item() for p in trainables(model).values()):
                raise FloatingPointError('Nonfinite final adapter tensor')
            if tensor_digest(dict(model.named_buffers())) != buffers_sha:
                raise RuntimeError('Unverified mutable model buffers changed')
            adapter = arm_dir / 'adapter'
            model.save_pretrained(adapter, safe_serialization=True)
            info.update(status='completed', parent_order_verified=True, consumed_parent_ids=consumed,
                        final_adapter_sha256=tensor_digest(trainables(model)), adapter=str(adapter.relative_to(output)),
                        adapter_files={p.name: runtime.digest(p) for p in adapter.iterdir() if p.is_file()},
                        training_loss=result.training_loss, model_accepts_loss_kwargs=False,
                        loss_reduction='mean of per-example supervised-token means, including provided terminator labels',
                        accelerator_accumulation_steps=trainer.accelerator.gradient_accumulation_steps)
            runtime.write_json(arm_dir / 'metrics.json', {**result.metrics, **info})
            runtime.write_json(output / 'run.json', run)
        run['status'] = 'completed'
        runtime.write_json(output / 'run.json', run)
        return run
    except BaseException as error:
        run.update(status='incomplete', error_type=type(error).__name__, error=str(error))
        for info in run['arms'].values():
            if info['status'] != 'completed':
                info['status'] = 'incomplete'
        runtime.write_json(output / 'run.json', run)
        raise
    finally:
        model.zero_grad(set_to_none=True)
