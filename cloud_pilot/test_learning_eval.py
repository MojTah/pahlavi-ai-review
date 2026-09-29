"""Local mock lifecycle and pinned-tokenizer checks; no pretrained weights or cloud."""
import ast
import base64
import copy
from datetime import datetime, timedelta, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import socket
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
from . import learning_eval as run


class StubModel(torch.nn.Module):
    def __init__(self, fail_at=None, cap_at=None, bad_switch=False):
        super().__init__()
        self.marker = torch.nn.Parameter(torch.tensor([1.0]))
        self.active, self.calls, self.caches, self.switches = 'reference', 0, [], []
        self.fail_at, self.cap_at, self.bad_switch = fail_at, cap_at, bad_switch

    def train(self, mode=True):
        if mode: raise AssertionError('Training is forbidden')
        return super().train(False)

    def set_adapter(self, arm):
        self.active = 'reference' if self.bad_switch else arm
        self.switches.append(arm)
        self.marker.requires_grad_(True)  # PEFT switching must be frozen again.

    def get_model_status(self):
        return SimpleNamespace(enabled=True, active_adapters=[self.active], merged_adapters=[],
                               available_adapters=list(run.ARMS))

    def generate(self, **kwargs):
        self.calls += 1
        assert not self.training and not self.marker.requires_grad and not torch.is_grad_enabled()
        assert kwargs['do_sample'] is False and kwargs['num_beams'] == 1
        assert kwargs['max_new_tokens'] == 512 and kwargs['eos_token_id'] == [1, 106, 50]
        assert not any(kwargs['past_key_values'] is cache for cache in self.caches)
        self.caches.append(kwargs['past_key_values'])
        if self.calls == self.fail_at: raise RuntimeError('injected generation failure')
        suffix = [7] * 512 if self.calls == self.cap_at else [8 if self.active == 'reference' else 9, 1]
        return torch.cat([kwargs['input_ids'], torch.tensor([suffix])], dim=1)


class LearningEvaluationTest(unittest.TestCase):
    def setUp(self):
        # TemporaryDirectory's private Windows ACL prevents this sandbox from
        # reopening its own directory. Retain small checks like adjacent tests.
        self.scratch = ROOT / 'resources/local/learning-eval-check' / uuid.uuid4().hex
        self.scratch.mkdir(parents=True)
        self.output = self.scratch / 'result'
        self.rows = [{'case_id': f'LD-{i:03d}', 'prompt': 'exact original task'} for i in range(1, 29)]
        self.prepared = {r['case_id']: [2, 3, 4] for r in self.rows}
        self.identity = {'adapters': {a: {'adapter_model.safetensors': a * 8} for a in run.ARMS}}
        self.deadline = (datetime.now(timezone.utc) + timedelta(minutes=3)).isoformat()
        # Windows indexing can briefly hold atomic JSON replacements. Retry only
        # local filesystem replacement, never generation or production code.
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

    def generate(self, model, canary_error=None):
        tokenizer = SimpleNamespace(decode=lambda ids, **kwargs: 'recorded answer')
        with patch.object(run.qualified, 'prefill_canary', side_effect=canary_error,
                          return_value={'status': 'passed', 'experimental_attempts': 0}), \
                patch.object(run.old, 'emit'), patch.object(torch.optim, 'AdamW', side_effect=AssertionError('No optimizer')):
            return run.generate_pairs(model, tokenizer, self.rows, self.prepared, self.output,
                                      self.identity, self.deadline, device='cpu')

    def records(self):
        return [json.loads(s) for s in (self.output / 'predictions.jsonl').read_text('utf-8').splitlines()]

    def test_all_56_exact_switches_caches_and_first_attempts(self):
        model = StubModel()
        result = self.generate(model)
        self.assertEqual((result['status'], result['recorded_outputs'], result['successful_outputs'],
                          result['completed_cases'], result['optimizer_updates']), ('completed', 56, 56, 28, 0))
        expected = [(r['case_id'], a) for i, r in enumerate(self.rows)
                    for a in (run.ARMS if i % 2 == 0 else run.ARMS[::-1])]
        records = self.records()
        self.assertEqual([(r['case_id'], r['arm']) for r in records], expected)
        self.assertEqual(model.switches, list(run.ARMS) + [a for _, a in expected])
        self.assertEqual([r['sequence'] for r in records], list(range(1, 57)))
        self.assertTrue(all(r['output_token_ids'][0] == (8 if r['arm'] == 'reference' else 9) for r in records))
        self.assertTrue(torch.equal(model.marker.detach(), torch.tensor([1.0])))
        self.assertEqual(result['unattempted_output_ids'], [])
        self.assertEqual(model.calls, 56)

    def test_cap_is_retained_and_remaining_cases_continue_without_retry(self):
        result = self.generate(StubModel(cap_at=1))
        self.assertEqual((result['status'], result['recorded_outputs'], result['successful_outputs']),
                         ('completed_with_errors', 56, 55))
        self.assertEqual(self.records()[0]['error_type'], 'OutputCapWithoutEOS')
        self.assertTrue(self.records()[0]['hit_output_cap_without_eos'])

    def test_generation_failure_stops_and_preserves_partial_ledger(self):
        model = StubModel(fail_at=3)
        with self.assertRaisesRegex(RuntimeError, 'injected'): self.generate(model)
        state = run.runtime.read_json(self.output / 'run.json')
        self.assertEqual((state['status'], state['attempted_outputs'], state['recorded_outputs']), ('incomplete', 3, 3))
        self.assertEqual((model.calls, len(state['unattempted_output_ids'])), (3, 53))
        self.assertEqual(self.records()[-1]['status'], 'error')

    def test_bad_switch_and_prefill_failure_prevent_any_generation(self):
        for kind in ('switch', 'prefill'):
            with self.subTest(kind=kind):
                self.output = self.scratch / kind
                model = StubModel(bad_switch=kind == 'switch')
                with self.assertRaises(RuntimeError):
                    self.generate(model, RuntimeError('prefill failure') if kind == 'prefill' else None)
                state = run.runtime.read_json(self.output / 'run.json')
                self.assertEqual((state['status'], state['attempted_outputs'], model.calls), ('incomplete', 0, 0))
                self.assertIn('failed', [r['status'] for r in state['canaries'].values()])

    def test_case_and_global_deadlines_are_distinct(self):
        deadline = datetime.now(timezone.utc) + timedelta(minutes=2)
        with patch.object(run.time, 'monotonic', return_value=95):
            stopper = run.GenerationDeadline(0, deadline)
            self.assertTrue(stopper(None, None))
            self.assertEqual(stopper.reason, 'case_timeout')
        stopper = run.GenerationDeadline(0, datetime.now(timezone.utc) - timedelta(seconds=1))
        self.assertTrue(stopper(None, None))
        self.assertEqual(stopper.reason, 'global_deadline')

    def test_frozen_input_and_real_original_token_prefixes(self):
        from transformers import AutoTokenizer
        path = ROOT / 'experiments/learning-diagnosis-20260929/inputs.jsonl'
        rows = run.read_inputs(path, run.INPUTS_SHA256)
        tokenizer_path = ROOT / 'resources/local/cloud-pilot-qualified-20260927/tokenizer'
        run.runtime.checked_files(tokenizer_path, run.bundle.TOKENIZER_HASHES)
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, local_files_only=True, trust_remote_code=False)
        actual = run.prepare_prompts(rows, tokenizer, 8192)
        refs = [json.loads(s) for s in (path.parent / 'references.jsonl').read_text('utf-8').splitlines()]
        pool = {r['id']: r for r in map(json.loads, (ROOT / 'resources/local/mixed-supervision-20260929/data/pool.jsonl').read_text('utf-8').splitlines())}
        for ref in refs:
            original = pool[ref['record_id']]
            self.assertEqual(actual[ref['case_id']], original['input_ids'][:original['prompt_tokens']])
        with self.assertRaises(ValueError): run.read_inputs(path, '0' * 64)
        with self.assertRaises(ValueError): run.prepare_prompts(rows, tokenizer, 512)

    def test_settings_and_cli_boundaries(self):
        settings = dict(schema_version=1, inputs_sha256=run.INPUTS_SHA256,
            runner_sha256=run.runtime.digest(run.__file__),
            helper_sha256={n: run.runtime.digest(Path(run.__file__).with_name(n)) for n in run.HELPERS},
            reference_adapter_files=run.qualified.ADAPTER_FILES,
            candidate_adapter_files={'adapter_config.json': 'a' * 64, 'adapter_model.safetensors': 'b' * 64},
            generation=run.GENERATION)
        run.validate_settings(settings)
        for key, value in [('generation', dict(run.GENERATION, max_new_tokens=4096)),
                           ('reference_adapter_files', settings['candidate_adapter_files']),
                           ('helper_sha256', {}), ('runner_sha256', '0' * 64)]:
            altered = copy.deepcopy(settings)
            altered[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): run.validate_settings(altered)
        with self.assertRaises(SystemExit): run.main([])

    def test_prepared_launcher_emits_accepted_evaluator_settings(self):
        from . import hf_learning_eval as launcher
        from huggingface_hub import HfApi
        path = ROOT / 'experiments/learning-diagnosis-20260929/inputs.jsonl'
        with patch.object(socket.socket, 'connect', side_effect=AssertionError('No network')), \
                patch.object(socket, 'create_connection', side_effect=AssertionError('No network')), \
                patch.object(HfApi, 'run_job', autospec=True, side_effect=AssertionError('No job')):
            spec, receipt = launcher.prepare(path, '0123456789abcdef0123456789abcdef')
        transport = ast.parse(spec['command'][3])
        payload = max((n.value for n in ast.walk(transport)
                       if isinstance(n, ast.Constant) and isinstance(n.value, str)), key=len)
        code = gzip.decompress(base64.b64decode(payload))
        self.assertEqual(hashlib.sha256(code).hexdigest(), receipt['decoded_command_sha256'])
        self.assertLess(max(receipt['command_arg_utf8_bytes']) + 1, 100 * 1024)
        self.assertLess(receipt['command_total_utf8_bytes_with_nul'], 1024**2)
        tree = ast.parse(code)
        # Execute only packed data assignments and the actual settings-write
        # statements, never the server lifecycle, bootstrap or model runner.
        assignments = [n for n in tree.body if isinstance(n, ast.Assign)
                       and any(isinstance(t, ast.Name) and t.id in {'settings', 'scripts'} for t in n.targets)]
        namespace = {'json': json, 'stage': self.scratch}
        exec(compile(ast.Module(body=assignments, type_ignores=[]), 'packed-data', 'exec'), namespace)
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'execute_evaluation')
        body = next(n for n in function.body if isinstance(n, ast.Try)).body
        start = next(i for i, n in enumerate(body) if isinstance(n, ast.Assign)
                     and any(isinstance(t, ast.Name) and t.id == 'evaluator_fields' for t in n.targets))
        stop = next(i for i in range(start, len(body)) if isinstance(body[i], ast.Expr)
                    and isinstance(body[i].value, ast.Call)
                    and isinstance(body[i].value.func, ast.Attribute)
                    and body[i].value.func.attr == 'write_text')
        exec(compile(ast.Module(body=body[start:stop + 1], type_ignores=[]), 'settings-boundary', 'exec'), namespace)
        settings = json.loads((self.scratch / 'settings.json').read_text('utf-8'))
        run.validate_settings(settings)
        self.assertEqual(len(run.read_inputs(path, settings['inputs_sha256'])), 28)
        with self.assertRaises(ValueError): run.validate_settings(namespace['settings'])
        self.assertEqual(set(namespace['scripts']), run.HELPERS | {'learning_eval.py'})
        for name, entry in namespace['scripts'].items():
            source = base64.b64decode(entry['content'])
            self.assertEqual(source, Path(run.__file__).with_name(name).read_bytes())
            self.assertEqual(hashlib.sha256(source).hexdigest(), entry['sha256'])
            compile(source, name, 'exec')


if __name__ == '__main__': unittest.main()
