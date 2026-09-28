"""Real tiny random-model checks; no pretrained model or network access."""
import copy
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import uuid

ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / 'resources/local/contextual-core-check'
SCRATCH.mkdir(parents=True, exist_ok=True)
os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_HUB_DISABLE_TELEMETRY='1',
                  HF_HOME=str(SCRATCH / 'hf-cache'), TEMP=str(SCRATCH), TMP=str(SCRATCH))
tempfile.tempdir = str(SCRATCH)
sys.path.extend([str(ROOT / 'resources/local/train-fit-deps'),
                 str(ROOT / 'resources/local/hf-client-venv/Lib/site-packages')])
import torch
from transformers import Gemma4Config, Gemma4TextConfig, Gemma4ForConditionalGeneration
from peft import LoraConfig, get_peft_model
try:
    from . import contextual_train as core
except ImportError:
    import contextual_train as core


def model():
    torch.set_num_threads(1)
    torch.manual_seed(42)
    config = Gemma4Config(text_config=Gemma4TextConfig(vocab_size=32, hidden_size=32, intermediate_size=48,
        num_hidden_layers=2, num_attention_heads=4, num_key_value_heads=2, head_dim=8, global_head_dim=8,
        max_position_embeddings=64, vocab_size_per_layer_input=32, hidden_size_per_layer_input=0,
        layer_types=['sliding_attention', 'full_attention'], sliding_window=16, final_logit_softcapping=30.0),
        vision_config=None, audio_config=None)
    config._attn_implementation = 'eager'
    result = get_peft_model(Gemma4ForConditionalGeneration(config), LoraConfig(r=2, lora_alpha=4,
        target_modules=['q_proj', 'v_proj'], lora_dropout=0.0, task_type='CAUSAL_LM', bias='none'))
    result.config.use_cache = result.config.text_config.use_cache = False
    with torch.no_grad():
        for name, value in result.named_parameters():
            if 'lora_B' in name:
                value.normal_(0.0, 0.2)
    return result


ROWS = [dict(id='parent-A', input_ids=[2, 3, 4, 7, 1], attention_mask=[1] * 5, labels=[-100] * 3 + [7, 1]),
        dict(id='parent-B', input_ids=[2, 11, 12, 13, 14, 15, 16, 1], attention_mask=[1] * 8,
             labels=[-100] * 3 + [13, 14, 15, 16, 1])]
SETTINGS = dict(seed=3407, max_steps=2, gradient_accumulation_steps=2, learning_rate=1e-3,
                warmup_steps=0, bf16=False, gradient_checkpointing=False)


class CoreTest(unittest.TestCase):
    def setUp(self):
        self.streams = {arm: copy.deepcopy(ROWS * 2) for arm in core.ARMS}
        self.output = SCRATCH / uuid.uuid4().hex
        self.deadline = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()

    def run_core(self, loaded=None):
        return core.train_two_arms(loaded or model(), self.streams, SETTINGS, self.output, self.deadline)

    def test_native_reset_equal_streams_and_exact_order(self):
        result = self.run_core()
        a, b = (result['arms'][x] for x in core.ARMS)
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(a['final_adapter_sha256'], b['final_adapter_sha256'])
        self.assertEqual(a['training_loss'], b['training_loss'])
        self.assertEqual(a['initial_rng_sha256'], b['initial_rng_sha256'])
        self.assertEqual(a['train_begin_rng_sha256'], b['train_begin_rng_sha256'])
        for name, arm in result['arms'].items():
            self.assertTrue(arm['optimizer_initially_empty'])
            self.assertEqual(arm['optimizer_initial_state_entries'], 0)
            self.assertEqual(arm['initial_scheduler_step'], 0)
            self.assertEqual(arm['completed_steps'], 2)
            self.assertEqual(arm['consumed_parent_ids'], ['parent-A', 'parent-B'] * 2)
            self.assertEqual(arm['accelerator_accumulation_steps'], 1)
            self.assertNotEqual(arm['initial_adapter_sha256'], arm['final_adapter_sha256'])
            self.assertEqual(len((self.output / name / 'progress.jsonl').read_text().splitlines()), 2)
            self.assertTrue((self.output / name / 'adapter/adapter_model.safetensors').is_file())

    def test_native_changed_targets_change_update(self):
        for row in self.streams['candidate']:
            row['input_ids'][-2] = row['labels'][-2] = 23
        result = self.run_core()
        self.assertNotEqual(result['arms']['control']['final_adapter_sha256'], result['arms']['candidate']['final_adapter_sha256'])

    def test_invalid_stream_length_order_and_mask(self):
        for kind in ('length', 'order', 'mask'):
            streams = copy.deepcopy(self.streams)
            if kind == 'length': streams['candidate'].pop()
            if kind == 'order': streams['candidate'][0]['id'] = 'wrong'
            if kind == 'mask': streams['control'][0]['labels'][0] = 2
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                core.validate_streams(streams, SETTINGS)
        self.assertFalse(self.output.exists())

    def test_fresh_output_rejects_overwrite(self):
        self.output.mkdir()
        with self.assertRaises(FileExistsError): self.run_core()

    def test_expired_deadline_makes_no_output(self):
        self.deadline = '2000-01-01T00:00:00+00:00'
        with self.assertRaises(TimeoutError): self.run_core()
        self.assertFalse(self.output.exists())

    def test_nonfinite_gradient_stops_before_update(self):
        loaded = model()
        parameter = next(iter(core.trainables(loaded).values()))
        hook = parameter.register_hook(lambda grad: grad * float('nan'))
        try:
            with self.assertRaises(FloatingPointError): self.run_core(loaded)
        finally: hook.remove()
        result = json.loads((self.output / 'run.json').read_text())
        self.assertEqual(result['arms']['control']['completed_steps'], 0)
        self.assertNotIn('candidate', result['arms'])

    def test_actual_order_corruption_is_rejected(self):
        from transformers import Trainer
        original = Trainer.get_train_dataloader
        def wrong_order(trainer):
            trainer.train_dataset = list(reversed(trainer.train_dataset))
            return original(trainer)
        with patch.object(Trainer, 'get_train_dataloader', wrong_order), self.assertRaisesRegex(ValueError, 'order/content'):
            self.run_core()
        self.assertEqual(json.loads((self.output / 'run.json').read_text())['status'], 'incomplete')

    def test_candidate_failure_preserves_completed_control(self):
        loaded = model()
        calls = [0]
        def fail(module, args, kwargs):
            calls[0] += 1
            if calls[0] == 5: raise RuntimeError('injected candidate failure')
        hook = loaded.register_forward_pre_hook(fail, with_kwargs=True)
        try:
            with self.assertRaisesRegex(RuntimeError, 'injected'):
                self.run_core(loaded)
        finally:
            hook.remove()
        result = json.loads((self.output / 'run.json').read_text())
        self.assertEqual(result['status'], 'incomplete')
        self.assertEqual(result['arms']['control']['status'], 'completed')
        self.assertEqual(result['arms']['candidate']['completed_steps'], 0)
        self.assertTrue((self.output / 'control/adapter/adapter_model.safetensors').is_file())
        self.assertFalse((self.output / 'candidate/adapter').exists())

    def test_buffer_mutation_rejected(self):
        loaded = model()
        loaded.register_buffer('untrusted_buffer', torch.tensor([1.0]))
        def mutate(module, args, kwargs): module.untrusted_buffer.add_(1)
        hook = loaded.register_forward_pre_hook(mutate, with_kwargs=True)
        try:
            with self.assertRaisesRegex(RuntimeError, 'buffers changed'):
                self.run_core(loaded)
        finally: hook.remove()
        self.assertEqual(json.loads((self.output / 'run.json').read_text())['status'], 'incomplete')


if __name__ == '__main__':
    unittest.main()
