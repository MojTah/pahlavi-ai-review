"""Offline receipt-only regressions; no model, optimizer, cloud or network."""
import copy
import hashlib
import json
from pathlib import Path
from types import FunctionType, SimpleNamespace
import unittest
from unittest.mock import patch
import uuid

from . import hf_mixed

ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / 'resources/local/full-pretraining-audit-20260929/recovery-tests'


def raw(value):
    return json.dumps(value, sort_keys=True).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


class RecoveryTest(unittest.TestCase):
    def setUp(self):
        self.root = SCRATCH / uuid.uuid4().hex
        self.root.mkdir(parents=True)
        self.order = [f'row-{i}' for i in range(1536)]
        self.manifest = {'pilot': {'selected_ids_in_order': self.order},
                         'outputs': {'train.jsonl': {'sha256': 'a' * 64}}}
        self.settings = dict(training_settings=dict(hf_mixed.mixed_run.SETTINGS),
            script_hashes={'mixed_run.py': 'b' * 64, 'mixed_train.py': 'c' * 64},
            data_manifest_sha256=digest(raw(self.manifest)), train_sha256='a' * 64,
            internal_seconds=30, compute_seconds=20, maximum_wait_seconds=0,
            inputs_name='inputs.jsonl', inputs_sha256='d' * 64,
            train_name='train.jsonl', data_manifest_name='data-manifest.json',
            bundle_name='bundle.zip', bundle_sha256='e' * 64, bootstrap_hashes={})

    def fixture(self, evidence):
        output = evidence / 'mixed'
        adapter = output / 'training/adapter'
        adapter.mkdir(parents=True)
        (evidence / 'data-manifest.json').write_bytes(raw(self.manifest))
        outer = {k: copy.deepcopy(self.settings[k]) for k in
                 ('train_sha256', 'data_manifest_sha256', 'script_hashes')}
        outer.update(status='incomplete', settings=self.settings['training_settings'],
                     runner_sha256=self.settings['script_hashes']['mixed_run.py'])
        (output / 'run.json').write_bytes(raw(outer))
        files = {'adapter_config.json': b'{}', 'adapter_model.safetensors': b'synthetic fixture, not model weights'}
        for name, data in files.items():
            (adapter / name).write_bytes(data)
        training = dict(status='completed', completed_steps=96, consumed_slots=1536,
            ordered_ids=self.order, parent_order_verified=True, fresh_optimizer=True,
            canary_adapter_changed=True,
            admission={'admitted': True}, settings=self.settings['training_settings'],
            runner_sha256=self.settings['script_hashes']['mixed_train.py'],
            adapter_files={name: digest(data) for name, data in files.items()})
        (output / 'training/run.json').write_bytes(raw(training))
        return output

    def wrapper(self, mutation=None):
        stage = self.root / 'stage'
        stage.mkdir()
        captured = {}
        actual_hash = hf_mixed.file_sha256

        def checksum(path):
            if str(path.parent).replace('\\', '/') == '/input':
                return {self.settings['inputs_name']: self.settings['inputs_sha256'],
                        self.settings['train_name']: self.settings['train_sha256'],
                        self.settings['data_manifest_name']: self.settings['data_manifest_sha256']}[path.name]
            return actual_hash(path)

        def failure(settings, directory, deadline, evidence):
            output = self.fixture(evidence)
            if mutation:
                mutation(output)
            raise RuntimeError('evaluation failed after training')

        def export(evidence, output, deadline, identity):
            captured.update(copy.deepcopy(identity))
            self.assertTrue((evidence / 'mixed/training/adapter').is_dir())
            return {}

        namespace = dict(hf_mixed.__dict__)
        namespace.update(Path=lambda p: self.root / 'exported' if str(p) == '/output' else Path(p),
            tempfile=SimpleNamespace(mkdtemp=lambda **kw: str(stage)),
            signal=SimpleNamespace(SIGTERM=15, SIGALRM=14, signal=lambda *a: None, alarm=lambda *a: None),
            emit=lambda *a, **kw: None, fresh_output=lambda *a: None,
            file_sha256=checksum, safe_extract=lambda *a: None, mixed_body=failure, export_evidence=export)
        execute = FunctionType(hf_mixed.execute_mixed.__code__, namespace)
        with patch('shutil.disk_usage', return_value=SimpleNamespace(free=100 * 1024**3)):
            with self.assertRaisesRegex(RuntimeError, '^evaluation failed after training$'):
                execute(self.settings, {}, '')
        self.assertFalse(captured['evaluation_complete'])
        self.assertEqual(captured['mixed_status'], 'incomplete')
        self.assertFalse(captured['quality_validated'])
        return captured

    def test_completed_training_survives_evaluation_failure(self):
        self.assertTrue(self.wrapper()['training_schedule_completed'])

    def test_invalid_training_evidence_never_claims_completion(self):
        def mutate_receipt(key, value):
            def mutate(output):
                path = output / 'training/run.json'
                receipt = json.loads(path.read_text())
                receipt[key] = value
                path.write_bytes(raw(receipt))
            return mutate

        cases = [('steps', mutate_receipt('completed_steps', 95)),
                 ('unchanged_canary', mutate_receipt('canary_adapter_changed', False)),
                 ('order', mutate_receipt('ordered_ids', self.order[::-1])),
                 ('settings', mutate_receipt('settings', {})),
                 ('inventory', mutate_receipt('adapter_files', {})),
                 ('missing_weight_inventory', mutate_receipt('adapter_files', {'adapter_config.json': digest(b'{}')})),
                 ('bad_weight', lambda o: (o / 'training/adapter/adapter_model.safetensors').write_bytes(b'changed')),
                 ('empty_weight', lambda o: (o / 'training/adapter/adapter_model.safetensors').write_bytes(b'')),
                 ('unexpected_file', lambda o: (o / 'training/adapter/unrecorded.txt').write_bytes(b'x')),
                 ('bad_manifest', lambda o: (o.parent / 'data-manifest.json').write_bytes(b'{}')),
                 ('malformed_receipt', lambda o: (o / 'training/run.json').write_bytes(b'[]')),
                 ('bad_outer_identity', lambda o: (o / 'run.json').write_bytes(b'{}'))]
        for name, mutation in cases:
            with self.subTest(name=name):
                self.root = SCRATCH / uuid.uuid4().hex
                self.root.mkdir(parents=True)
                self.assertFalse(self.wrapper(mutation)['training_schedule_completed'])


if __name__ == '__main__':
    unittest.main()
