"""Version 1: identical ordered exposure cycles, one continuous fresh optimizer."""
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import time

try:
    from . import contextual_train as core, runtime, mixed_train
except ImportError:
    import contextual_train as core
    import runtime
    import mixed_train

SETTINGS = {**core.OPTIMIZER, 'seed': 3407, 'max_steps': 384, 'gradient_accumulation_steps': 16,
            'learning_rate': 0.0001, 'warmup_steps': 4, 'bf16': True, 'gradient_checkpointing': True}


def validate_rows(rows, settings=SETTINGS, passes=4):
    ids = mixed_train.validate_rows(rows, settings)
    if type(passes) is not int or passes < 1 or len(rows) % passes:
        raise ValueError('Invalid repetition count')
    size = len(rows) // passes
    base = rows[:size]
    if len(set(ids[:size])) != size:
        raise ValueError('Unique base IDs required')
    if any(core.canonical(rows[i * size:(i + 1) * size]) != core.canonical(base) for i in range(passes)):
        raise ValueError('Cycles must repeat identical ordered tokenized rows')
    return ids


forecast = mixed_train.forecast


def train_one(model, rows, settings, output, deadline_utc, canary_steps=20, admission=None, passes=4, snapshot_steps=(96, 192, 384)):
    import torch
    from transformers import Trainer, TrainingArguments, TrainerCallback, set_seed
    runtime.offline()
    ordered = validate_rows(rows, settings, passes)
    if (not snapshot_steps or any(type(s) is not int or not 1 <= s <= settings['max_steps'] for s in snapshot_steps)
            or tuple(sorted(set(snapshot_steps))) != tuple(snapshot_steps) or snapshot_steps[-1] != settings['max_steps']):
        raise ValueError('Ordered snapshot steps must include final update')
    if admission is None and settings['gradient_accumulation_steps'] != 16:
        raise ValueError('Nonproduction accumulation requires explicit test admission')
    runtime.check_deadline(deadline_utc)
    params = core.trainables(model)
    devices = {p.device for p in params.values()}
    if len(devices) != 1 or any(not torch.isfinite(p).all().item() for p in params.values()):
        raise ValueError('One device and finite starting adapter required')
    if not 1 <= canary_steps < settings['max_steps']:
        raise ValueError('Canary must leave further updates')
    if any(value.requires_grad for value in model.buffers()):
        raise ValueError('Learned buffers unsupported')
    initial = core.tensor_digest(params)
    buffers = core.tensor_digest(dict(model.named_buffers()))
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    run = dict(status='running', settings=settings, completed_steps=0, consumed_slots=0,
               initial_adapter_sha256=initial, fresh_optimizer=False, quality_validated=False,
               runner_sha256=runtime.digest(__file__), stream_sha256=hashlib.sha256(core.canonical(rows)).hexdigest(),
               model_accepts_loss_kwargs=False, loss_reduction='mean of per-example supervised-token means',
               schema_version=1, deadline_utc=deadline_utc, passes=passes, snapshots={}, inference_performed=False,
               pass_exposures=[], admission_observations=[], initial_buffers_sha256=buffers,
               base_cycle_sha256=hashlib.sha256(core.canonical(rows[:len(rows)//passes])).hexdigest())
    runtime.write_json(output / 'run.json', run)
    consumed = []
    cycle_size = len(rows) // passes
    forward_hash = hashlib.sha256(b'[')
    cycle_hash = hashlib.sha256(b'[')
    started = time.monotonic()
    set_seed(settings['seed'])
    trainer = None

    def save_adapter(name):
        folder = output / name
        model.save_pretrained(folder, safe_serialization=True)
        return {p.name: runtime.digest(p) for p in folder.iterdir() if p.is_file()}

    def collate(batch):
        runtime.check_deadline(deadline_utc)
        if len(batch) != 1:
            raise ValueError('Exactly one row per microbatch required')
        return {**{k: torch.tensor([batch[0][k]], dtype=torch.long)
                   for k in ('input_ids', 'labels', 'attention_mask')}, '_dose_row': batch[0]}

    class ExposureTrainer(Trainer):
        def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
            runtime.check_deadline(deadline_utc)
            row = inputs.pop('_dose_row')
            if len(consumed) >= len(rows) or row != rows[len(consumed)]:
                raise ValueError('Forwarded stream order/content differs')
            if any(inputs[k].detach().cpu().tolist() != [row[k]]
                   for k in ('input_ids', 'labels', 'attention_mask')):
                raise ValueError('Forwarded tokens differ from scheduled row')
            result = super().compute_loss(model, inputs, return_outputs=return_outputs,
                                          num_items_in_batch=num_items_in_batch)
            loss = result[0] if return_outputs else result
            nonlocal cycle_hash
            encoded = core.canonical(row)
            if consumed:
                forward_hash.update(b',')
            if len(consumed) % cycle_size:
                cycle_hash.update(b',')
            forward_hash.update(encoded)
            cycle_hash.update(encoded)
            if not torch.isfinite(loss).all().item():
                raise FloatingPointError('Nonfinite forwarded loss')
            consumed.append(row['id'])
            run['consumed_slots'] = len(consumed)
            if len(consumed) % cycle_size == 0:
                cycle_hash.update(b']')
                observed = cycle_hash.hexdigest()
                if observed != run['base_cycle_sha256']:
                    raise RuntimeError('Forwarded cycle hash differs')
                run['pass_exposures'].append(dict(pass_index=len(consumed)//cycle_size, slots=cycle_size,
                    ids=consumed[-cycle_size:], stream_sha256=observed))
                cycle_hash = hashlib.sha256(b'[')
            return result

    class Guard(TrainerCallback):
        def on_train_begin(self, args, state, control, optimizer=None, **kwargs):
            if optimizer is None or optimizer.state or state.global_step != 0 or trainer.lr_scheduler.last_epoch != 0:
                raise RuntimeError('Fresh optimizer/scheduler at step zero required')
            run['fresh_optimizer'] = True

        def on_step_begin(self, args, state, control, **kwargs):
            runtime.check_deadline(deadline_utc)

        def on_pre_optimizer_step(self, args, state, control, **kwargs):
            runtime.check_deadline(deadline_utc)
            grads = [p.grad for p in params.values() if p.grad is not None]
            if (not grads or any(not torch.isfinite(g).all().item() for g in grads)
                    or not any(g.abs().sum().item() > 0 for g in grads)):
                raise FloatingPointError('Nonzero finite adapter gradients required')
            if any(p.grad is not None for p in model.parameters() if not p.requires_grad):
                raise RuntimeError('Frozen parameter received gradient')

        def on_log(self, args, state, control, logs=None, **kwargs):
            if logs and 'loss' in logs and not math.isfinite(logs['loss']):
                raise FloatingPointError('Nonfinite loss')

        def on_step_end(self, args, state, control, **kwargs):
            if len(consumed) != state.global_step * settings['gradient_accumulation_steps']:
                raise RuntimeError('Forward exposure does not equal completed accumulation boundary')
            if core.tensor_digest(dict(model.named_buffers())) != buffers:
                raise RuntimeError('Frozen model buffers changed')
            if any(not torch.isfinite(p).all().item() for p in params.values()):
                raise FloatingPointError('Nonfinite adapter update')
            run['completed_steps'] = state.global_step
            elapsed = time.monotonic() - started
            run['forward_stream_prefix_sha256'] = forward_hash.hexdigest()
            event = dict(phase='dose_training_step', step=state.global_step, consumed_slots=len(consumed), seconds=elapsed)
            print(json.dumps(event), flush=True)
            with (output / 'progress.jsonl').open('a', encoding='utf-8') as stream:
                stream.write(json.dumps(event) + '\n')
                stream.flush()
                os.fsync(stream.fileno())
            steps = sorted({int(v['step'].item() if hasattr(v['step'], 'item') else v['step'])
                            for v in trainer.optimizer.state.values() if 'step' in v})
            if steps != [state.global_step] or trainer.lr_scheduler.last_epoch != state.global_step:
                raise RuntimeError('Optimizer/scheduler continuity differs')
            if state.global_step in snapshot_steps:
                run['snapshots'][str(state.global_step)] = dict(files=save_adapter('adapter-step' + str(state.global_step)),
                    adapter_sha256=core.tensor_digest(params), consumed_slots=len(consumed), optimizer_steps=steps,
                    scheduler_step=trainer.lr_scheduler.last_epoch)
            runtime.write_json(output / 'run.json', run)
            if state.global_step == canary_steps:
                run['canary_adapter_sha256'] = core.tensor_digest(params)
                run['canary_adapter_changed'] = run['canary_adapter_sha256'] != initial
                if not run['canary_adapter_changed']:
                    raise RuntimeError('Canary adapter did not change')
                run['canary_adapter_files'] = save_adapter('admission-adapter-step' + str(canary_steps))
            if state.global_step == canary_steps or (state.global_step in snapshot_steps and state.global_step < settings['max_steps']):
                remaining = (runtime.check_deadline(deadline_utc) - datetime.now(timezone.utc)).total_seconds()
                decision = admission(rows, state.global_step, elapsed, remaining) if admission else forecast(rows, state.global_step, elapsed, remaining)
                run['admission_observations'].append(dict(step=state.global_step, **decision))
                if state.global_step == canary_steps:
                    run['admission'] = decision
                runtime.write_json(output / 'run.json', run)
                print(json.dumps(dict(phase='dose_canary_admission', **decision)), flush=True)
                if decision.get('admitted') is not True:
                    raise TimeoutError('Measured admission cannot finish training and reserved evaluation before deadline')
            runtime.check_deadline(deadline_utc)

    try:
        arguments = TrainingArguments(output_dir=str(output), max_steps=settings['max_steps'],
            per_device_train_batch_size=1, gradient_accumulation_steps=settings['gradient_accumulation_steps'],
            train_sampling_strategy='sequential', learning_rate=settings['learning_rate'], warmup_steps=settings['warmup_steps'],
            seed=settings['seed'], data_seed=settings['seed'], bf16=settings['bf16'], fp16=False,
            use_cpu=next(iter(devices)).type == 'cpu', gradient_checkpointing=settings['gradient_checkpointing'],
            gradient_checkpointing_kwargs={'use_reentrant': False}, **core.OPTIMIZER,
            save_strategy='no', logging_steps=1, logging_nan_inf_filter=False, report_to='none', push_to_hub=False,
            disable_tqdm=True, label_smoothing_factor=0.0, dataloader_num_workers=0, dataloader_pin_memory=False,
            remove_unused_columns=False)
        trainer = ExposureTrainer(model=model, args=arguments, train_dataset=rows, data_collator=collate, callbacks=[Guard()])
        trainer.model_accepts_loss_kwargs = False
        result = trainer.train()
        if (consumed != ordered or trainer.state.global_step != settings['max_steps']
                or core.tensor_digest(dict(model.named_buffers())) != buffers):
            raise RuntimeError('Incomplete order/updates or changed model buffers')
        if not math.isfinite(result.training_loss):
            raise FloatingPointError('Nonfinite final loss')
        final = core.tensor_digest(params)
        if final == initial:
            raise RuntimeError('Adapter did not change')
        forward_hash.update(b']')
        if forward_hash.hexdigest() != run['stream_sha256'] or len(run['pass_exposures']) != passes:
            raise RuntimeError('Final forwarded stream hash/pass count differs')
        if any(not torch.isfinite(p).all().item() for p in params.values()):
            raise FloatingPointError('Nonfinite final adapter')
        run.update(status='completed', ordered_ids=consumed, parent_order_verified=True, final_adapter_sha256=final,
                   training_loss=result.training_loss,
                   forwarded_stream_sha256=forward_hash.copy().hexdigest(),
                   accelerator_accumulation_steps=trainer.accelerator.gradient_accumulation_steps)
        runtime.write_json(output / 'run.json', run)
        return run
    except BaseException as error:
        run.update(status='incomplete', error_type=type(error).__name__, error=str(error))
        runtime.write_json(output / 'run.json', run)
        raise
    finally:
        model.zero_grad(set_to_none=True)
