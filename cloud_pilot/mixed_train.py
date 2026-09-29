"""One ordered fresh-optimizer continuation, with admission after 20 real updates."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import time

try:
    from . import contextual_train as core, runtime
except ImportError:
    import contextual_train as core
    import runtime

SETTINGS = {**core.OPTIMIZER, 'seed': 3407, 'max_steps': 96, 'gradient_accumulation_steps': 16,
            'learning_rate': 0.0001, 'warmup_steps': 4, 'bf16': True, 'gradient_checkpointing': True}


def validate_rows(rows, settings=SETTINGS):
    ids = core.validate_streams({'control': rows, 'candidate': rows}, settings)
    for row in rows:
        if (set(row) != {'id', 'task', 'input_ids', 'labels', 'attention_mask', 'prompt_tokens'}
                or type(row['prompt_tokens']) is not int
                or row['prompt_tokens'] != next(i for i, t in enumerate(row['labels']) if t != -100)
                or not isinstance(row['task'], str) or not row['task']):
            raise ValueError('Mixed tokenized row schema/mask differs')
    return ids


def forecast(rows, completed_steps, elapsed, available, evaluation_seconds=900, reload_seconds=300):
    if (type(completed_steps) is not int or not 1 <= completed_steps < len(rows) // 16
            or any(not math.isfinite(x) or x <= 0 for x in (elapsed, available, evaluation_seconds, reload_seconds))):
        raise ValueError('Invalid measured admission inputs')
    split = completed_steps * 16
    ratios = [(len(rows) - split) / split]
    for power in (1, 2):
        ratios.append(sum(len(r['input_ids']) ** power for r in rows[split:]) /
                      sum(len(r['input_ids']) ** power for r in rows[:split]))
    training = elapsed * max(ratios) * 1.3
    result = dict(canary_steps=completed_steps, measured_seconds=elapsed, remaining_train_seconds=training,
                  evaluation_seconds=evaluation_seconds, reload_seconds=reload_seconds, safety_multiplier=1.3,
                  projected_seconds=training + evaluation_seconds + reload_seconds, available_seconds=available,
                  token_cost_ratios=ratios, admitted=training + evaluation_seconds + reload_seconds < available)
    return result


def train_one(model, rows, settings, output, deadline_utc, canary_steps=20, admission=None):
    import torch
    from transformers import Trainer, TrainingArguments, TrainerCallback, set_seed
    runtime.offline()
    ordered = validate_rows(rows, settings)
    runtime.check_deadline(deadline_utc)
    params = core.trainables(model)
    devices = {p.device for p in params.values()}
    if len(devices) != 1 or any(not torch.isfinite(p).all().item() for p in params.values()):
        raise ValueError('One device and finite starting adapter required')
    if not 1 <= canary_steps < settings['max_steps']:
        raise ValueError('Canary must leave further updates')
    initial = core.tensor_digest(params)
    buffers = core.tensor_digest(dict(model.named_buffers()))
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    run = dict(status='running', settings=settings, completed_steps=0, consumed_slots=0,
               initial_adapter_sha256=initial, fresh_optimizer=False, quality_validated=False,
               runner_sha256=runtime.digest(__file__), stream_sha256=hashlib.sha256(core.canonical(rows)).hexdigest(),
               model_accepts_loss_kwargs=False, loss_reduction='mean of per-example supervised-token means',
               deadline_utc=deadline_utc)
    runtime.write_json(output / 'run.json', run)
    consumed = []
    started = time.monotonic()
    set_seed(settings['seed'])
    trainer = None

    def save_adapter(name):
        folder = output / name
        model.save_pretrained(folder, safe_serialization=True)
        return {p.name: runtime.digest(p) for p in folder.iterdir() if p.is_file()}

    def collate(batch):
        runtime.check_deadline(deadline_utc)
        if len(batch) != 1 or len(consumed) >= len(rows) or batch[0] != rows[len(consumed)]:
            raise ValueError('Consumed stream order/content differs')
        consumed.append(batch[0]['id'])
        run['consumed_slots'] = len(consumed)
        return {k: torch.tensor([batch[0][k]], dtype=torch.long) for k in ('input_ids', 'labels', 'attention_mask')}

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
            if any(not torch.isfinite(p).all().item() for p in params.values()):
                raise FloatingPointError('Nonfinite adapter update')
            run['completed_steps'] = state.global_step
            elapsed = time.monotonic() - started
            event = dict(phase='mixed_training_step', step=state.global_step, consumed_slots=len(consumed), seconds=elapsed)
            print(json.dumps(event), flush=True)
            with (output / 'progress.jsonl').open('a', encoding='utf-8') as stream:
                stream.write(json.dumps(event) + '\n')
                stream.flush()
            runtime.write_json(output / 'run.json', run)
            if state.global_step == canary_steps:
                run['canary_adapter_sha256'] = core.tensor_digest(params)
                run['canary_adapter_changed'] = run['canary_adapter_sha256'] != initial
                if not run['canary_adapter_changed']:
                    raise RuntimeError('Canary adapter did not change')
                run['canary_adapter_files'] = save_adapter('bounded-adapter-step20')
                remaining = (runtime.check_deadline(deadline_utc) - datetime.now(timezone.utc)).total_seconds()
                decision = admission(rows, canary_steps, elapsed, remaining) if admission else forecast(rows, canary_steps, elapsed, remaining)
                run['admission'] = decision
                runtime.write_json(output / 'run.json', run)
                print(json.dumps(dict(phase='mixed_canary_admission', **decision)), flush=True)
                if decision.get('admitted') is not True:
                    raise TimeoutError('Measured 20-step forecast cannot finish training and DEV24 before export reserve')
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
        trainer = Trainer(model=model, args=arguments, train_dataset=rows, data_collator=collate, callbacks=[Guard()])
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
        run.update(status='completed', ordered_ids=consumed, parent_order_verified=True, final_adapter_sha256=final,
                   adapter_files=save_adapter('adapter'), training_loss=result.training_loss,
                   accelerator_accumulation_steps=trainer.accelerator.gradient_accumulation_steps)
        runtime.write_json(output / 'run.json', run)
        return run
    except BaseException as error:
        run.update(status='incomplete', error_type=type(error).__name__, error=str(error))
        runtime.write_json(output / 'run.json', run)
        raise
    finally:
        model.zero_grad(set_to_none=True)
