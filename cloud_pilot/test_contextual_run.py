"""Offline package/tokenizer and first-attempt lifecycle checks, without base weights."""
import copy
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid

ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / 'resources/local/contextual-run-check'
SCRATCH.mkdir(parents=True, exist_ok=True)
os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_HUB_DISABLE_TELEMETRY='1',
                  HF_HOME=str(SCRATCH / 'hf-cache'), TEMP=str(SCRATCH), TMP=str(SCRATCH))
tempfile.tempdir = str(SCRATCH)
sys.path.extend([str(ROOT / 'resources/local/train-fit-deps'),
                 str(ROOT / 'resources/local/hf-client-venv/Lib/site-packages')])
import torch
from transformers import AutoTokenizer
try:
    from . import contextual_run as run
except ImportError:
    import contextual_run as run

PACKAGE = ROOT / 'resources/local/contextual-run-package'
BUNDLE = ROOT / 'resources/local/cloud-pilot-qualified-20260927'
INPUTS = ROOT / 'experiments/dev-diagnostic-20260927/inputs.jsonl'
FS_RETRY_COUNT = 0


class StubModel(torch.nn.Module):
    def __init__(self, fail_at=None, cap=False, bad_switch=False):
        super().__init__()
        self.marker = torch.nn.Parameter(torch.tensor([1.0]))
        self.active = 'control'
        self.calls = 0
        self.switches = []
        self.fail_at, self.cap, self.bad_switch = fail_at, cap, bad_switch

    def set_adapter(self, arm):
        self.active = 'control' if self.bad_switch else arm
        self.switches.append(arm)

    def get_model_status(self):
        return SimpleNamespace(enabled=True, active_adapters=[self.active], merged_adapters=[],
                               available_adapters=['control', 'candidate'])

    def generate(self, **kwargs):
        self.calls += 1
        if self.calls == self.fail_at: raise RuntimeError('injected first-attempt failure')
        assert kwargs['max_new_tokens'] == 4096 and kwargs['do_sample'] is False
        assert kwargs['eos_token_id'] == [1, 106, 50] and kwargs['num_beams'] == 1
        suffix = [7] * 4096 if self.cap else [8, 1]
        return torch.cat([kwargs['input_ids'], torch.tensor([suffix])], dim=1)


class RunnerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        run.runtime.checked_files(BUNDLE / 'tokenizer', run.bundle.TOKENIZER_HASHES)
        cls.tokenizer = AutoTokenizer.from_pretrained(BUNDLE / 'tokenizer', local_files_only=True, trust_remote_code=False)
        cls.manifest, cls.payload = run.read_package(PACKAGE, run.PACKAGE_SHA256)
        cls.rows = run.frozen.read_inputs(INPUTS)

    def setUp(self):
        self.output = SCRATCH / uuid.uuid4().hex
        self.deadline = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
        # Windows AV/indexing can briefly lock rapid atomic JSON renames. Only retry
        # the local filesystem operation; never retry a model attempt or alter Linux code.
        original = os.replace
        def windows_replace(source, destination, *args, **kwargs):
            global FS_RETRY_COUNT
            for attempt in range(5):
                try:
                    return original(source, destination, *args, **kwargs)
                except PermissionError:
                    if os.name != 'nt' or attempt == 4: raise
                    FS_RETRY_COUNT += 1
                    time.sleep(0.02)
        patcher = patch.object(os, 'replace', windows_replace)
        patcher.start()
        self.addCleanup(patcher.stop)

    def generate(self, model, prefill=None):
        identity = {'adapters': {arm: {'files': {'adapter_model.safetensors': arm * 8}} for arm in run.core.ARMS},
                    'evaluation_inputs_sha256': run.frozen.INPUTS_SHA256}
        prepared = {r['id']: [2, 3, 4] for r in self.rows}
        fake_tokenizer = SimpleNamespace(decode=lambda ids, **kwargs: 'test translation')
        with patch.object(run.qualified, 'prefill_canary', side_effect=prefill,
                          return_value={'status': 'passed', 'experimental_attempts': 0}):
            return run.generate_pairs(model, fake_tokenizer, self.rows, prepared, self.output,
                                      identity, self.deadline, device='cpu')

    def test_real_pinned_package_and_all_token_reconstructions(self):
        streams = run.prepare_streams(self.manifest, self.payload, BUNDLE / 'train.jsonl', self.tokenizer)
        self.assertEqual([len(streams[a]) for a in run.core.ARMS], [768, 768])
        self.assertEqual([r['id'] for r in streams['control']], [r['id'] for r in streams['candidate']])
        self.assertEqual(sum(a != b for a, b in zip(streams['control'], streams['candidate'])), 48)
        self.assertEqual(max(len(r['input_ids']) for values in streams.values() for r in values), 660)

    def test_real_old_plain_prompts_are_identical(self):
        prepared = run.prepare_prompts(self.rows, self.payload['dev-prompt-identities.json'], self.tokenizer, 8192)
        self.assertEqual(len(prepared), 24)
        modified = copy.deepcopy(self.payload['dev-prompt-identities.json'])
        modified[0]['rendered_input_ids_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'plain prompt'):
            run.prepare_prompts(self.rows, modified, self.tokenizer, 8192)

    def test_manifest_file_inventory_and_hash_tamper(self):
        with self.assertRaisesRegex(ValueError, 'manifest'):
            run.read_package(PACKAGE, '0' * 64)
        for kind in ('extra', 'hash'):
            path = SCRATCH / uuid.uuid4().hex
            shutil.copytree(PACKAGE, path)
            if kind == 'extra': (path / 'unexpected').write_text('x')
            else:
                with (path / 'ordered-slots.jsonl').open('ab') as stream: stream.write(b' ')
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                run.read_package(path, run.PACKAGE_SHA256)

    def test_qualification_focus_and_schedule_tamper(self):
        for kind in ('qualification', 'focus', 'schedule', 'tokens'):
            payload = copy.deepcopy(self.payload)
            if kind == 'qualification': payload['qualification-decision-v2.json']['decisions'][0]['target'] = 'changed'
            if kind == 'focus': payload['proposals.jsonl'][0]['source_span'] = [0, 1]
            if kind == 'schedule': payload['ordered-slots.jsonl'][0]['microstep'] = 2
            if kind == 'tokens': payload['auxiliary-tokenized.jsonl'][0]['input_ids'][-3] += 1
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                run.prepare_streams(self.manifest, payload, BUNDLE / 'train.jsonl', self.tokenizer)

    def test_stubbed_48_first_attempts_exact_order_and_switches(self):
        model = StubModel()
        with patch.object(run, 'emit') as events:
            result = self.generate(model)
        self.assertEqual(events.call_count, 48)
        self.assertEqual(events.call_args.kwargs['recorded_outputs'], 48)
        self.assertEqual(result['status'], 'completed')
        for key in ('scheduled_outputs', 'attempted_outputs', 'recorded_outputs', 'completed_outputs'):
            self.assertEqual(result[key], 48)
        self.assertEqual(result['completed_cases'], 24)
        self.assertIsNone(result['active_output_id'])
        self.assertEqual(result['unattempted_output_ids'], [])
        records = run.bundle.jsonl((self.output / 'predictions.jsonl').read_bytes())
        self.assertEqual([r['id'] for r in records], result['schedule'])
        self.assertEqual([r['arm'] for r in records], model.switches[1:])
        self.assertEqual([r['sequence'] for r in records], list(range(1, 49)))
        self.assertTrue(all(r['output_token_ids'] == [8, 1] for r in records))
        self.assertEqual(model.calls, 48)

    def test_failed_first_attempt_is_retained_without_retry(self):
        model = StubModel(fail_at=3)
        with self.assertRaisesRegex(RuntimeError, 'injected'):
            self.generate(model)
        result = run.runtime.read_json(self.output / 'run.json')
        records = run.bundle.jsonl((self.output / 'predictions.jsonl').read_bytes())
        self.assertEqual((result['status'], result['attempted_outputs'], result['recorded_outputs'], result['completed_outputs']),
                         ('incomplete', 3, 3, 2))
        self.assertEqual(records[-1]['status'], 'error')
        self.assertEqual(model.calls, 3)
        self.assertEqual(len(result['unattempted_output_ids']), 45)

    def test_cap_and_bad_switch_fail_closed(self):
        for model in (StubModel(cap=True), StubModel(bad_switch=True)):
            self.output = SCRATCH / uuid.uuid4().hex
            with self.assertRaises(RuntimeError): self.generate(model)
            result = run.runtime.read_json(self.output / 'run.json')
            self.assertEqual(result['status'], 'incomplete')
            records = run.bundle.jsonl((self.output / 'predictions.jsonl').read_bytes())
            self.assertEqual(records[-1]['status'], 'error')
            self.assertLessEqual(model.calls, 1)

    def test_prefill_failure_preserves_zero_attempts(self):
        model = StubModel()
        with self.assertRaisesRegex(RuntimeError, 'prefill'):
            self.generate(model, prefill=RuntimeError('prefill failure'))
        result = run.runtime.read_json(self.output / 'run.json')
        self.assertEqual(result['canary']['status'], 'failed')
        self.assertEqual(result['attempted_outputs'], 0)
        self.assertEqual(model.calls, 0)

    def test_helpers_unchanged_and_cli_requires_identity(self):
        for module in (run.core, run.runtime, run.bundle, run.qualified, run.frozen, run.protocol):
            self.assertEqual(run.runtime.digest(module.__file__), run.HELPER_SHA256[Path(module.__file__).name])
        with self.assertRaises(SystemExit): run.main([])

    def test_adapter_target_module_order_is_semantically_irrelevant(self):
        original = dict(r=16, lora_alpha=32, lora_dropout=0.0, bias='none', peft_type='LORA',
                        task_type='CAUSAL_LM', target_modules=['q_proj', 'v_proj'])
        reordered = dict(original, target_modules=['v_proj', 'q_proj'])
        run.verify_adapter_architecture(reordered, original)
        for bad in (['q_proj'], ['q_proj', 'v_proj', 'v_proj'], ['q_proj', 'wrong']):
            with self.assertRaises(ValueError):
                run.verify_adapter_architecture(dict(original, target_modules=bad), original)


if __name__ == '__main__':
    program = unittest.main(exit=False)
    result = program.result
    summary = {'tests': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
               'status': 'PASS' if result.wasSuccessful() else 'FAIL',
               'windows_permission_retries': FS_RETRY_COUNT,
               'runtime_sha256': run.runtime.digest(run.runtime.__file__),
               'runner_sha256': run.runtime.digest(run.__file__),
               'test_sha256': run.runtime.digest(__file__)}
    (SCRATCH / 'test-result.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary))
    sys.exit(0 if result.wasSuccessful() else 1)
