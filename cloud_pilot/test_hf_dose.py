"""Offline dose assembly, admission refusal, and export evidence checks."""
import ast
import base64
import copy
import hashlib
import json
import lzma
from pathlib import Path
import sys
import time
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / 'resources/local/hf-client-venv/Lib/site-packages'))
from . import hf_dose as job, training_admission as gate

HERE = ROOT / 'experiments/dose-acquisition-20260930'


def build():
    return job.prepare(ROOT / 'resources/local/training-ready-v2-20260929/data/train.jsonl',
        ROOT / 'experiments/training-ready-v2-20260929/data-manifest.json', HERE / 'inputs.jsonl',
        json.loads((HERE / 'packet-contract.json').read_bytes()), 'c' * 32)


class DosePackageTest(unittest.TestCase):
    def test_input_dict_order_and_json_roundtrip_preserve_exact_job(self):
        packet = json.loads((HERE / 'packet-contract.json').read_bytes())
        def reverse(value):
            if isinstance(value, dict):
                return {k: reverse(v) for k,v in reversed(list(value.items()))}
            if isinstance(value, list):
                return [reverse(v) for v in value]
            return value
        args = (ROOT / 'resources/local/training-ready-v2-20260929/data/train.jsonl',
                ROOT / 'experiments/training-ready-v2-20260929/data-manifest.json', HERE / 'inputs.jsonl')
        a = job.prepare(*args, reverse(packet), 'c' * 32)
        b = job.prepare(*args, json.loads(json.dumps(packet,sort_keys=True)), 'c' * 32)
        self.assertEqual(gate.plain(a), gate.plain(b))

    def test_real_sdk_draft_refuses_and_payload_is_exact(self):
        spec, receipt = build()
        self.assertEqual(gate.plain(gate.sdk_spec(gate.plain(spec))), gate.plain(spec))
        self.assertEqual(spec['timeout'], '360m')
        self.assertEqual(receipt['expected_outputs'], 98)
        self.assertEqual(receipt['compute_seconds'] + receipt['export_reserve_seconds'], receipt['internal_seconds'])
        with self.assertRaisesRegex(ValueError, 'Training blocked'):
            exec(spec['command'][3], {})
        with self.assertRaises(ValueError):
            gate.admit(spec, receipt, HERE / 'missing-admission-evidence')
        intended = receipt['training_admission']['intended_command']
        strings = [n.value for n in ast.walk(ast.parse(intended)) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        program = lzma.decompress(base64.b64decode(max(strings, key=len)))
        self.assertEqual(hashlib.sha256(program).hexdigest(), receipt['decoded_command_sha256'])
        compile(program, 'dose-test-parent', 'exec')
        assignments = {n.targets[0].id: ast.literal_eval(n.value) for n in ast.parse(program).body
            if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id in {'settings', 'scripts'}}
        for name, entry in assignments['scripts'].items():
            raw = base64.b64decode(entry['content'])
            original = ROOT / 'cloud_pilot' / ('learning_eval.py' if name == 'bf16_learning_eval.py' else name)
            self.assertEqual(raw, original.read_bytes())
            self.assertEqual(hashlib.sha256(raw).hexdigest(), entry['sha256'])
            compile(raw, name, 'exec')
        for key in ('expected_outputs', 'training_settings', 'inputs_sha256', 'evaluation_schedule'):
            self.assertEqual(assignments['settings'][key], receipt[key])

    def test_changed_data_and_packet_refuse(self):
        settings = json.loads((HERE / 'packet-contract.json').read_bytes())
        settings['inputs_sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            job.prepare(ROOT / 'resources/local/training-ready-v2-20260929/data/train.jsonl',
                ROOT / 'experiments/training-ready-v2-20260929/data-manifest.json', HERE / 'inputs.jsonl', settings, 'c' * 32)

    def test_adapter_snapshot_export_and_training_receipt(self):
        scratch = ROOT / 'resources/local/dose-package-tests' / uuid.uuid4().hex
        source, output = scratch / 'source', scratch / 'output'
        source.mkdir(parents=True)
        output.mkdir()
        dose = source / 'dose'
        training = dose / 'training'
        training.mkdir(parents=True)
        manifest = {'pilot': {'selected_ids_in_order': [str(i) for i in range(1536)]}}
        manifest_path = source / 'data-manifest.json'
        manifest_path.write_text(json.dumps(manifest))
        ordered = manifest['pilot']['selected_ids_in_order']
        record = dict(status='completed', completed_steps=384, consumed_slots=6144, ordered_ids=ordered*4,
            settings=job.dose_train.SETTINGS, runner_sha256=job.file_sha256(Path(job.dose_train.__file__)),
            fresh_optimizer=True, canary_adapter_changed=True, forwarded_stream_sha256='a', stream_sha256='a',
            initial_adapter_sha256='b', final_adapter_sha256='c', base_cycle_sha256='d',
            pass_exposures=[dict(pass_index=i, slots=1536, ids=ordered, stream_sha256='d') for i in range(1,5)],
            admission_observations=[dict(step=i, admitted=True) for i in (20,96,192)], snapshots={})
        for step in (20,96,192,384):
            folder = training / (('admission-adapter-step' if step == 20 else 'adapter-step') + str(step))
            folder.mkdir()
            (folder / 'adapter_model.safetensors').write_bytes(b'test-export-snapshot-' + str(step).encode())
            (folder / 'adapter_config.json').write_text('{}')
            if step != 20:
                record['snapshots'][str(step)] = dict(files={p.name: job.file_sha256(p) for p in folder.iterdir()},
                    consumed_slots=step*16, optimizer_steps=[step], scheduler_step=step)
        state_path = training / 'run.json'
        state_path.write_text(json.dumps(record))
        settings = dict(data_manifest_sha256=job.file_sha256(manifest_path), training_settings=job.dose_train.SETTINGS,
            script_hashes={'dose_train.py': record['runner_sha256']})
        self.assertEqual(job.completed_training(dose, settings)['completed_steps'], 384)
        job.export_evidence(source, output, time.monotonic()+60, {'max_export_bytes': 1024**2})
        exported = json.loads((output / 'manifest.json').read_bytes())['files']
        self.assertEqual(sum(n.endswith('adapter_model.safetensors') for n in exported), 4)
        record['pass_exposures'][3]['ids'] = ['wrong']
        state_path.write_text(json.dumps(record))
        with self.assertRaises(ValueError):
            job.completed_training(dose, settings)


if __name__ == '__main__':
    unittest.main()
