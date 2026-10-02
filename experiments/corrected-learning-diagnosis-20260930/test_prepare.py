"""Local serialization, pinned tokenizer and mocked56-attempt checks; no31B runtime."""
import ast
import base64
from datetime import datetime, timedelta, timezone
import gzip
import json
from pathlib import Path
import socket
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.extend([str(ROOT / 'resources/local/train-fit-deps'), str(ROOT / 'resources/local/hf-client-venv/Lib/site-packages')])
import prepare
from cloud_pilot import hf_learning_eval as launcher, learning_eval as run
from cloud_pilot.test_learning_eval import StubModel
from huggingface_hub import HfApi


class PacketTests(unittest.TestCase):
    def setUp(self):
        self.scratch = HERE / 'checks' / uuid.uuid4().hex
        self.scratch.mkdir(parents=True)
        self.binding = json.loads((HERE / 'binding.json').read_bytes())

    def packed(self, corrected=True):
        path = HERE / 'inputs.jsonl' if corrected else prepare.OLD / 'inputs.jsonl'
        with patch.object(socket.socket, 'connect', side_effect=AssertionError('No network')), \
                patch.object(socket, 'create_connection', side_effect=AssertionError('No network')), \
                patch.object(HfApi, 'run_job', side_effect=AssertionError('No launch')):
            spec, receipt = launcher.prepare(path, '20260930000000000000000000000001',
                **({'corrected_binding': self.binding} if corrected else {}))
        transport = ast.parse(spec['command'][3])
        payload = max((n.value for n in ast.walk(transport) if isinstance(n, ast.Constant) and isinstance(n.value, str)), key=len)
        source = gzip.decompress(base64.b64decode(payload))
        self.assertEqual(prepare.sha(source), receipt['decoded_command_sha256'])
        tree = ast.parse(source)
        assignments = [n for n in tree.body if isinstance(n, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id in {'settings', 'scripts'} for t in n.targets)]
        ns = {'json': json, 'stage': self.scratch}
        exec(compile(ast.Module(body=assignments, type_ignores=[]), 'packed-data', 'exec'), ns)
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'execute_evaluation')
        body = next(n for n in function.body if isinstance(n, ast.Try)).body
        start = next(i for i,n in enumerate(body) if isinstance(n, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == 'evaluator_fields' for t in n.targets))
        stop = next(i for i in range(start,len(body)) if isinstance(body[i], ast.Expr) and isinstance(body[i].value, ast.Call)
            and isinstance(body[i].value.func, ast.Attribute) and body[i].value.func.attr == 'write_text')
        exec(compile(ast.Module(body=body[start:stop + 1], type_ignores=[]), 'actual-settings-boundary', 'exec'), ns)
        settings = json.loads((self.scratch / 'settings.json').read_bytes())
        run.validate_settings(settings)
        self.assertLess(max(receipt['command_arg_utf8_bytes']) + 1, 100 * 1024)
        self.assertLess(receipt['command_total_utf8_bytes_with_nul'], 1024**2)
        for name, entry in ns['scripts'].items():
            content = base64.b64decode(entry['content'])
            self.assertEqual(prepare.sha(content), entry['sha256'])
            self.assertEqual(content, Path(run.__file__).with_name(name).read_bytes())
            compile(content, name, 'exec')
        return spec, settings

    def test_corrected_serialized_settings_and_mounts(self):
        spec, settings = self.packed()
        self.assertEqual(settings['schema_version'], 2)
        self.assertEqual(settings['candidate_adapter_files']['adapter_model.safetensors'], prepare.ADAPTER_SHA)
        self.assertEqual(next(v.path for v in spec['volumes'] if v.mount_path == '/mixed'), prepare.PREFIX)
        self.assertEqual(len(run.read_inputs(HERE / 'inputs.jsonl', settings['inputs_sha256'], versioned=True)), 28)
        with self.assertRaises(ValueError): run.read_inputs(HERE / 'inputs.jsonl', settings['inputs_sha256'])
        settings['case_order'][0] = settings['case_order'][1]
        with self.assertRaises(ValueError): run.validate_settings(settings)

    def test_old_default_is_old_candidate_and_packet(self):
        spec, settings = self.packed(False)
        self.assertEqual(settings['schema_version'], 1)
        self.assertEqual(settings['inputs_sha256'], run.INPUTS_SHA256)
        self.assertEqual(settings['candidate_adapter_files']['adapter_model.safetensors'], 'f01d10058f26c1fc6fc212820b183e42d033fed0b959d200a87befa3d142cbca')
        self.assertEqual(next(v.path for v in spec['volumes'] if v.mount_path == '/mixed'), launcher.MIXED_PREFIX)

    def test_pinned_original_training_prefixes(self):
        from transformers import AutoTokenizer
        rows = run.read_inputs(HERE / 'inputs.jsonl', self.binding['inputs_sha256'], versioned=True)
        tokenizer = AutoTokenizer.from_pretrained(ROOT / 'resources/local/cloud-pilot-qualified-20260927/tokenizer',
            local_files_only=True, trust_remote_code=False)
        prefixes = run.prepare_prompts(rows, tokenizer, 8192)
        refs = [json.loads(line) for line in (HERE / 'references.jsonl').read_bytes().splitlines()]
        self.assertEqual(prefixes, {r['case_id']: r['prompt_token_ids'] for r in refs})

    def test_mock56_schedule_and_failure_denominator(self):
        rows = run.read_inputs(HERE / 'inputs.jsonl', self.binding['inputs_sha256'], versioned=True)
        prepared = {r['case_id']: [2,3,4] for r in rows}
        identity = {'settings': {'case_order': self.binding['case_order']},
            'adapters': {a: {'adapter_model.safetensors': a * 8} for a in run.ARMS}}
        for fail_at in (None, 3):
            model = StubModel(fail_at=fail_at)
            output = self.scratch / str(fail_at)
            with patch.object(run.qualified, 'prefill_canary', return_value={'status':'passed','experimental_attempts':0}), patch.object(run.old,'emit'):
                args = (model, SimpleNamespace(decode=lambda *a,**k:'answer'), rows, prepared, output, identity,
                    (datetime.now(timezone.utc) + timedelta(minutes=100)).isoformat())
                if fail_at:
                    with self.assertRaises(RuntimeError): run.generate_pairs(*args, device='cpu')
                else:
                    result = run.generate_pairs(*args, device='cpu')
                    self.assertEqual((result['scheduled_outputs'],result['recorded_outputs'],result['completed_cases']), (56,56,28))
                    self.assertEqual(result['schedule'][::2], [k + (':reference' if i % 2 == 0 else ':candidate') for i,k in enumerate(self.binding['case_order'])])
            state = run.runtime.read_json(output / 'run.json')
            if fail_at:
                self.assertEqual((state['scheduled_outputs'],state['attempted_outputs'],state['recorded_outputs'],len(state['unattempted_output_ids'])), (56,3,3,53))
            self.assertEqual(model.calls, fail_at or 56)


if __name__ == '__main__':
    unittest.main()
