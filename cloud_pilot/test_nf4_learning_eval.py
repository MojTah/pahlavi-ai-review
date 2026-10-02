"""Local NF4-boundary stubs and real tiny CPU arithmetic; no weights/network."""
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import sys
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.extend([str(ROOT / 'resources/local/train-fit-deps'),
                 str(ROOT / 'resources/local/hf-client-venv/Lib/site-packages')])
os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_HUB_DISABLE_TELEMETRY='1')
import torch
from . import nf4_learning_eval as run
from .test_learning_eval import StubModel


class Params4bit(torch.nn.Parameter):
    def __new__(cls):
        result = super().__new__(cls, torch.ones(4, dtype=torch.uint8), requires_grad=False)
        result.quant_state = SimpleNamespace(quant_type='nf4', nested=True)
        return result


class Linear4bit(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.weight, self.compute_dtype = Params4bit(), torch.bfloat16


class AdapterWrapper(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.base_layer = Linear4bit()


# Match PEFT's class-name collision without requiring uninstalled BNB/GPU.
AdapterWrapper.__name__ = 'Linear4bit'
BNB_TYPES = {'bitsandbytes.nn': SimpleNamespace(Linear4bit=Linear4bit, Params4bit=Params4bit)}


def numerical_state(model):
    with patch.dict(sys.modules, BNB_TYPES):
        return run.numerical_state(model)


class LoadedStub(StubModel):
    def __init__(self):
        super().__init__()
        self.quantized = AdapterWrapper()
        self.is_loaded_in_4bit, self.is_gradient_checkpointing = True, False
        self.quantization = dict(load_in_4bit=True, load_in_8bit=False, bnb_4bit_quant_type='nf4',
            bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype='bfloat16')
        self.config = SimpleNamespace(quantization_config=self.quantization,
            get_text_config=lambda: SimpleNamespace(_attn_implementation='eager'))

    def gradient_checkpointing_disable(self):
        self.is_gradient_checkpointing = False

    def load_adapter(self, path, *, adapter_name, local_files_only, is_trainable, autocast_adapter_dtype):
        assert path == 'candidate-path' and adapter_name == 'candidate'
        assert local_files_only and not is_trainable and autocast_adapter_dtype

    def generate(self, **kwargs):
        assert torch.is_autocast_enabled('cpu') and torch.get_autocast_dtype('cpu') == torch.bfloat16
        return super().generate(**kwargs)


class NF4Checks(unittest.TestCase):
    def setUp(self):
        # Same bounded sandbox-only atomic-replace retry as the baseline suite.
        original_replace = os.replace
        def replace(source, destination):
            for attempt in range(5):
                try:
                    return original_replace(source, destination)
                except PermissionError:
                    if os.name != 'nt' or attempt == 4: raise
                    time.sleep(0.02)
        patcher = patch.object(os, 'replace', replace)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.output = ROOT / 'resources/local/nf4-learning-eval-tests' / uuid.uuid4().hex
        self.rows = run.read_inputs(ROOT / 'experiments/corrected-learning-diagnosis-20260930/inputs.jsonl',
            '02c5ecc82e187847377d5891c31fcb9fc5fb0d3714ea4aa66e686c0a3fabce3c', versioned=True)
        self.prepared = {row['case_id']: [2, 3, 4] for row in self.rows}
        binding = json.loads((ROOT / 'experiments/corrected-learning-diagnosis-20260930/binding.json').read_bytes())
        self.identity = {'settings': {'case_order': binding['case_order']},
            'adapters': {arm: {'adapter_model.safetensors': arm * 8} for arm in run.ARMS}}
        self.deadline = (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat()

    def evaluate(self, model, canary_error=None):
        def canary(model, prepared, deadline):
            self.assertFalse(torch.is_grad_enabled())
            self.assertTrue(torch.is_autocast_enabled('cpu'))
            if canary_error: raise canary_error
            return {'status': 'passed', 'experimental_attempts': 0}
        with patch.object(run.qualified, 'prefill_canary', side_effect=canary), \
                patch.object(run.old, 'emit'), \
                patch.object(torch.optim, 'AdamW', side_effect=AssertionError('No optimizer')):
            return run.generate_pairs(model, SimpleNamespace(decode=lambda ids, **kwargs: 'recorded answer'),
                self.rows, self.prepared, self.output, self.identity, self.deadline, device='cpu')

    def test_loading_boundary_strict_signature_and_numerical_validation(self):
        import peft
        import transformers
        model = LoadedStub()
        model.marker.data = model.marker.data.to(torch.bfloat16)
        calls = []
        class Config:
            def __init__(self, *, load_in_4bit, bnb_4bit_quant_type, bnb_4bit_use_double_quant, bnb_4bit_compute_dtype):
                assert load_in_4bit and bnb_4bit_quant_type == 'nf4' and bnb_4bit_use_double_quant
                assert bnb_4bit_compute_dtype == torch.bfloat16
        class Loader:
            @staticmethod
            def from_pretrained(base, *, local_files_only, trust_remote_code, use_safetensors,
                                device_map, dtype, attn_implementation, quantization_config):
                assert base == 'base-path' and local_files_only and not trust_remote_code and use_safetensors
                assert device_map == {'': 0} and dtype == torch.bfloat16 and attn_implementation == 'eager'
                assert isinstance(quantization_config, Config)
                calls.append('base')
                return model
        class Adapter:
            @staticmethod
            def from_pretrained(model, path, *, adapter_name, local_files_only, is_trainable, autocast_adapter_dtype):
                assert path == 'reference-path' and adapter_name == 'reference'
                assert local_files_only and not is_trainable and autocast_adapter_dtype
                calls.append('adapter')
                return model
        # Real installed PEFT preparation performs the FP32 cast and freezes all.
        original_prepare = peft.prepare_model_for_kbit_training
        def prepare(model, *, use_gradient_checkpointing):
            assert use_gradient_checkpointing is False
            calls.append('kbit')
            return original_prepare(model, use_gradient_checkpointing=False)
        with patch.object(transformers, 'BitsAndBytesConfig', Config), \
                patch.object(transformers, 'Gemma4ForConditionalGeneration', Loader), \
                patch.object(peft, 'PeftModel', Adapter), \
                patch.object(peft, 'prepare_model_for_kbit_training', side_effect=prepare), \
                patch.object(run.old, 'verify_loaded_adapter') as verified, patch.dict(sys.modules, BNB_TYPES):
            loaded, numerical = run.load_model('base-path', {'reference': 'reference-path', 'candidate': 'candidate-path'})
        self.assertEqual(calls, ['base', 'kbit', 'adapter'])
        self.assertIs(loaded, model)
        self.assertEqual(model.marker.dtype, torch.float32)
        self.assertEqual(verified.call_count, 2)
        self.assertEqual(numerical['optimizer_updates'], 0)
        self.assertEqual(numerical['quantized_parameter_count'], 1)
        self.assertFalse(any(p.requires_grad or p.grad is not None for p in loaded.parameters()))
        for key, value in [('bnb_4bit_quant_type', 'fp4'), ('bnb_4bit_use_double_quant', False),
                           ('bnb_4bit_compute_dtype', 'float16'), ('load_in_4bit', False)]:
            with self.subTest(key=key):
                saved = model.quantization[key]
                model.quantization[key] = value
                with self.assertRaises(ValueError): numerical_state(model)
                model.quantization[key] = saved
        model.quantized.base_layer.weight.quant_state.nested = False
        with self.assertRaises(ValueError): numerical_state(model)
        model.quantized.base_layer.weight.quant_state.nested = True
        model.marker.data = model.marker.data.to(torch.bfloat16)
        with self.assertRaises(ValueError): numerical_state(model)

    def test_all56_corrected_schedule_no_updates_no_grad_and_nf4_loading_ledger(self):
        model = LoadedStub()
        self.output.mkdir(parents=True)
        loading = run.initial_state(self.rows, self.identity)
        loading['status'] = 'loading_nf4'
        run.runtime.write_json(self.output / 'run.json', loading)
        before = model.marker.detach().clone()
        result = self.evaluate(model)
        self.assertEqual((result['status'], result['recorded_outputs'], result['completed_cases'],
                          result['optimizer_updates']), ('completed', 56, 28, 0))
        records = [json.loads(line) for line in (self.output / 'predictions.jsonl').read_text('utf-8').splitlines()]
        expected = run.initial_state(self.rows, self.identity)['schedule']
        self.assertEqual([row['id'] for row in records], expected)
        self.assertEqual(model.switches, list(run.ARMS) + [identity.split(':')[1] for identity in expected])
        self.assertTrue(torch.equal(before, model.marker))
        self.assertEqual(model.calls, 56)
        with self.assertRaises(ValueError): self.evaluate(model)

    def test_canary_and_bad_switch_fail_before_generation(self):
        for condition in ('canary', 'switch'):
            with self.subTest(condition=condition):
                self.output = self.output.parent / uuid.uuid4().hex
                model = LoadedStub()
                model.bad_switch = condition == 'switch'
                with self.assertRaises(RuntimeError): self.evaluate(model, RuntimeError('canary') if condition == 'canary' else None)
                state = run.runtime.read_json(self.output / 'run.json')
                self.assertEqual((state['status'], state['attempted_outputs'], model.calls), ('incomplete', 0, 0))
                self.assertEqual(len(state['unattempted_output_ids']), 56)

    def test_failed_first_attempt_and_partial_predictions_are_not_retried(self):
        model = LoadedStub()
        model.fail_at = 3
        with self.assertRaisesRegex(RuntimeError, 'injected'): self.evaluate(model)
        state = run.runtime.read_json(self.output / 'run.json')
        self.assertEqual((state['recorded_outputs'], state['attempted_outputs'], model.calls), (3, 3, 3))
        before = (self.output / 'predictions.jsonl').read_bytes()
        with self.assertRaises(ValueError): self.evaluate(model)
        self.assertEqual(before, (self.output / 'predictions.jsonl').read_bytes())

    def test_server_run_final_weight_checks_and_loading_failure_ledger(self):
        from transformers import AutoTokenizer
        self.output.parent.mkdir(parents=True, exist_ok=True)
        settings = dict(schema_version=2, experiment_id='corrected-learning-diagnosis-20260930',
            case_order=self.identity['settings']['case_order'],
            inputs_sha256='02c5ecc82e187847377d5891c31fcb9fc5fb0d3714ea4aa66e686c0a3fabce3c',
            runner_sha256=run.runtime.digest(run.__file__),
            helper_sha256={name: run.runtime.digest(Path(run.__file__).with_name(name))
                for name in run.shared.HELPERS}, reference_adapter_files=run.qualified.ADAPTER_FILES,
            candidate_adapter_files={'adapter_config.json': 'a' * 64, 'adapter_model.safetensors': 'b' * 64},
            generation=run.GENERATION)
        settings['helper_sha256']['bf16_learning_eval.py'] = run.runtime.digest(run.shared.__file__)
        run.validate_settings(settings)
        settings_path = self.output.parent / (uuid.uuid4().hex + '.json')
        settings_path.write_text(json.dumps(settings), 'utf-8')
        args = SimpleNamespace(settings=settings_path, inputs=ROOT / 'experiments/corrected-learning-diagnosis-20260930/inputs.jsonl',
            base=Path('base'), tokenizer=Path('tokenizer'), reference_adapter=Path('reference'),
            candidate_adapter=Path('candidate'), output=self.output, deadline_utc=self.deadline)
        original_read = run.runtime.read_json
        def read(path):
            if Path(path) == Path('base/config.json'):
                return {'text_config': {'max_position_embeddings': 8192}}
            if Path(path) in (Path('reference/adapter_config.json'), Path('candidate/adapter_config.json')):
                return {}
            return original_read(path)
        class Tokenizer:
            @staticmethod
            def from_pretrained(path, *, local_files_only, trust_remote_code):
                assert path == Path('tokenizer') and local_files_only and not trust_remote_code
                return SimpleNamespace(apply_chat_template=lambda *args, **kwargs: [2, 3, 4],
                                       decode=lambda ids, **kwargs: 'recorded answer')
        model = LoadedStub()
        run.select_adapter(model, 'reference')
        numerical = numerical_state(model)
        with patch.object(run.runtime, 'read_json', side_effect=read), \
                patch.object(run.runtime, 'verify_base', return_value={'files': {'base': 'hash'}}), \
                patch.object(run.runtime, 'checked_files'), \
                patch.object(run.runtime, 'gpu_admission', return_value={'stub': True}), \
                patch.object(run.old, 'verify_adapter_architecture'), \
                patch.object(AutoTokenizer, 'from_pretrained', side_effect=Tokenizer.from_pretrained), \
                patch.object(run, 'load_model', return_value=(model, numerical)) as loader, \
                patch.object(run.old, 'verify_loaded_adapter') as final_verify, \
                patch.object(run, 'generate_pairs', return_value={'status': 'completed', 'recorded_outputs': 56,
                                                                  'successful_outputs': 56}), \
                patch.object(run.old, 'emit'), patch.dict(sys.modules, BNB_TYPES):
            result = run.run(args)
            self.assertEqual(result['numerical_state'], numerical)
            self.assertTrue(result['final_adapters_unchanged'])
            self.assertEqual(final_verify.call_count, 2)
            loader.assert_called_once()
            args.output = self.output.parent / uuid.uuid4().hex
            loader.side_effect = RuntimeError('loading failed')
            with self.assertRaisesRegex(RuntimeError, 'loading failed'): run.run(args)
        loading = run.runtime.read_json(args.output / 'evaluation/run.json')
        self.assertEqual((loading['status'], loading['attempted_outputs']), ('loading_nf4', 0))
        self.assertEqual(len(loading['unattempted_output_ids']), 56)
        self.assertEqual(run.runtime.read_json(args.output / 'run.json')['status'], 'incomplete')

    def test_tiny_real_gemma_fp32_cast_and_bf16_autocast_forward(self):
        from transformers import Gemma4Config, Gemma4ForConditionalGeneration, Gemma4TextConfig
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        config = Gemma4Config(text_config=Gemma4TextConfig(vocab_size=128, hidden_size=64,
            intermediate_size=128, num_hidden_layers=2, num_attention_heads=4, num_key_value_heads=2,
            head_dim=16, global_head_dim=16, num_global_key_value_heads=2, hidden_size_per_layer_input=0,
            vocab_size_per_layer_input=128, num_kv_shared_layers=0, attention_k_eq_v=True,
            layer_types=['sliding_attention', 'full_attention'], sliding_window=16,
            max_position_embeddings=128, attention_dropout=0.0), vision_config=None, audio_config=None)
        config._attn_implementation = 'eager'
        model = Gemma4ForConditionalGeneration(config).to(torch.bfloat16)
        model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=False)
        model = get_peft_model(model, LoraConfig(r=4, lora_alpha=8, lora_dropout=0.0,
            bias='none', task_type='CAUSAL_LM', target_modules=['q_proj', 'v_proj']))
        model.requires_grad_(False)
        model.eval()
        before = {name: param.detach().clone() for name, param in model.named_parameters()}
        with torch.inference_mode(), torch.autocast(device_type='cpu', dtype=torch.bfloat16):
            logits = model(input_ids=torch.tensor([[2, 11, 12, 13]]), use_cache=False).logits
        self.assertTrue(torch.isfinite(logits).all())
        self.assertTrue(all(param.dtype == torch.float32 and not param.requires_grad and param.grad is None
                            and torch.equal(before[name], param) for name, param in model.named_parameters()))
        # CPU check proves casts/autocast/frozen arithmetic only; it is not NF4/GPU evidence.


if __name__ == '__main__':
    unittest.main()
