"""Real CPU Gemma4/LoRA Trainer repetition checks; no downloads."""
import copy
from datetime import datetime, timedelta, timezone
import json
import unittest
from unittest.mock import patch
import uuid
from .test_contextual_train import model, ROWS, SCRATCH
from . import dose_train as core, runtime
from .contextual_train import trainables

SETTINGS = dict(seed=3407, max_steps=4, gradient_accumulation_steps=2,
                learning_rate=1e-4, warmup_steps=1, bf16=False, gradient_checkpointing=True)


class DoseTest(unittest.TestCase):
    def setUp(self):
        self.rows = [{**copy.deepcopy(r), 'task': 'translation', 'prompt_tokens': 3} for r in ROWS * 4]
        self.output = SCRATCH / ('dose-' + uuid.uuid4().hex)
        self.deadline = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()

    def run_core(self, loaded=None, admission=None):
        return core.train_one(loaded or model(), self.rows, SETTINGS, self.output, self.deadline,
                              canary_steps=2, admission=admission or (lambda *args: {'admitted': True}),
                              passes=4, snapshot_steps=(1, 2, 4))

    def test_real_continuous_optimizer_exact_forward_exposure_and_reload(self):
        from peft import PeftModel
        result = self.run_core()
        self.assertEqual(result['status'], 'completed')
        self.assertTrue(result['fresh_optimizer'])
        self.assertEqual([o['step'] for o in result['admission_observations']], [1, 2])
        self.assertEqual(result['consumed_slots'], 8)
        self.assertEqual(result['forwarded_stream_sha256'], result['stream_sha256'])
        self.assertFalse(result['inference_performed'])
        self.assertEqual([p['ids'] for p in result['pass_exposures']], [['parent-A', 'parent-B']] * 4)
        self.assertEqual(len({p['stream_sha256'] for p in result['pass_exposures']}), 1)
        self.assertEqual(result['base_cycle_sha256'], result['pass_exposures'][0]['stream_sha256'])
        events = [json.loads(line) for line in (self.output / 'progress.jsonl').read_text().splitlines()]
        self.assertEqual([e['consumed_slots'] for e in events], [2, 4, 6, 8])
        hashes = []
        for step in (1, 2, 4):
            record = result['snapshots'][str(step)]
            self.assertEqual(record['optimizer_steps'], [step])
            self.assertEqual(record['scheduler_step'], step)
            self.assertEqual(record['consumed_slots'], step * 2)
            folder = self.output / ('adapter-step' + str(step))
            self.assertFalse((folder / 'optimizer.pt').exists())
            runtime.checked_files(folder, record['files'])
            wrapped = model().get_base_model()
            base = type(wrapped)(wrapped.config)
            loaded = PeftModel.from_pretrained(base, folder, local_files_only=True, is_trainable=True)
            self.assertEqual(core.core.tensor_digest(trainables(loaded)), record['adapter_sha256'])
            hashes.append(record['adapter_sha256'])
        self.assertEqual(len(set(hashes)), 3)
        self.assertFalse(any(p.name.startswith('checkpoint-') for p in self.output.iterdir()))

    def test_malformed_cycles_schema_and_settings(self):
        for kind in ('cycle', 'order', 'schema', 'settings'):
            rows = copy.deepcopy(self.rows)
            settings = dict(SETTINGS)
            if kind == 'cycle': rows[2]['input_ids'][-2] = rows[2]['labels'][-2] = 23
            if kind == 'order': rows[2:4] = rows[3:1:-1]
            if kind == 'schema': rows[0]['extra'] = True
            if kind == 'settings': settings['optim'] = 'sgd'
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                core.validate_rows(rows, settings)

    def test_actual_order_corruption(self):
        from transformers import Trainer
        original = Trainer.get_train_dataloader
        def wrong(trainer):
            trainer.train_dataset = list(reversed(trainer.train_dataset))
            return original(trainer)
        with patch.object(Trainer, 'get_train_dataloader', wrong), self.assertRaisesRegex(ValueError, 'order/content'):
            self.run_core()
        self.assertEqual(json.loads((self.output / 'run.json').read_text())['completed_steps'], 0)

    def test_nonfinite_gradient(self):
        loaded = model()
        hook = next(iter(trainables(loaded).values())).register_hook(lambda grad: grad * float('nan'))
        try:
            with self.assertRaises(FloatingPointError): self.run_core(loaded)
        finally: hook.remove()
        result = json.loads((self.output / 'run.json').read_text())
        self.assertEqual(result['completed_steps'], 0)
        self.assertEqual(result['status'], 'incomplete')

    def test_nonfinite_forwarded_loss_stops_before_update(self):
        loaded = model()
        def poison(module, args, result):
            result.loss = result.loss * float('nan')
            return result
        hook = loaded.register_forward_hook(poison)
        try:
            with self.assertRaisesRegex(FloatingPointError, 'forwarded loss'): self.run_core(loaded)
        finally: hook.remove()
        result = json.loads((self.output / 'run.json').read_text())
        self.assertEqual(result['completed_steps'], 0)
        self.assertFalse(result['snapshots'])

    def test_failure_preserves_intermediate_snapshot(self):
        def deny(rows, step, elapsed, remaining): return {'admitted': step < 2}
        with self.assertRaises(TimeoutError): self.run_core(admission=deny)
        result = json.loads((self.output / 'run.json').read_text())
        self.assertEqual(result['completed_steps'], 2)
        self.assertEqual(len(result['pass_exposures']), 2)
        runtime.checked_files(self.output / 'adapter-step1', result['snapshots']['1']['files'])
        self.assertFalse((self.output / 'adapter-step4').exists())

    def test_initial_nonfinite_and_buffer_guards(self):
        import torch
        loaded = model()
        with torch.no_grad(): next(iter(trainables(loaded).values())).fill_(float('nan'))
        with self.assertRaises(ValueError): self.run_core(loaded)
        self.assertFalse(self.output.exists())
        loaded = model()
        loaded.register_buffer('untrusted_buffer', torch.tensor([1.0]))
        def mutate(module, args):
            module.untrusted_buffer.add_(1)
        hook = loaded.register_forward_pre_hook(mutate)
        try:
            with self.assertRaisesRegex(RuntimeError, 'buffers changed'): self.run_core(loaded)
        finally: hook.remove()


if __name__ == '__main__': unittest.main()
