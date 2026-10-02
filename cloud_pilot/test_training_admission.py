"""Offline admission checks. No service calls, model loads, or real approvals."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import uuid
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / 'resources/local/hf-client-venv/Lib/site-packages'))
from . import training_admission as gate


class AdmissionChecks(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / 'resources/local/training-admission-tests'
        scratch.mkdir(parents=True, exist_ok=True)
        self.root = scratch / uuid.uuid4().hex
        self.root.mkdir()
        @gate.draft
        def builder():
            return {'image': 'python:3.11', 'command': ['python', '-u', '-c', "print('TRAINING_SENTINEL')"], 'timeout': '1m'}, {'command_sha256': gate.digest(b"print('TRAINING_SENTINEL')"), 'steps': 1}
        self.spec, self.prep = builder()

    def save(self, name, value):
        p = self.root / name
        p.write_bytes(gate.canonical(value))
        return {'path': name, 'sha256': gate.digest(p.read_bytes()), 'bytes': p.stat().st_size}

    def evidence(self):
        marker = self.save('qualified.json', {'fixture': 'qualified local test only'})
        job = self.prep['training_admission']
        contract = self.save('contract.json', {'schema_version': 1, 'experiment_id': 'test', 'execution_owner': 'one-test-owner',
            'job_sha256': job['job_sha256'], 'job': job['job'],
            'acquisition': {'packet_sha256': marker['sha256'], 'expected_outputs': 56},
            'artifacts': {name: [marker] for name in gate.GROUPS}})
        results = self.save('results.json', {'status': 'completed', 'learning_gain': -1})
        acquisition = self.save('acquisition.json', {'status': 'completed', 'packet_sha256': marker['sha256'],
            'expected_outputs': 56, 'completed_outputs': 56, 'results': results})
        decision = self.save('decision.json', {'contract_sha256': contract['sha256'], 'acquisition_sha256': acquisition['sha256'],
            'status': 'training_justified', 'rationale': 'Negative acquisition motivates a controlled dose test.'})
        validation = self.save('validation.json', {'contract_sha256': contract['sha256'], 'status': 'PASS', 'checks': [marker]})
        review = self.save('review.json', {'contract_sha256': contract['sha256'], 'acquisition_sha256': acquisition['sha256'],
            'decision_sha256': decision['sha256'], 'validation_sha256': validation['sha256'], 'status': 'APPROVE',
            'model': 'gpt-6-astra', 'reviewer_id': 'astra-test-request', 'implementer_id': 'sol-test-request', 'rationale': 'Test fixture only.'})
        authorization = self.save('authorization.json', {'status': 'AUTHORIZE_TRAINING_JOB', 'human': 'TEST ONLY', 'execution_owner': 'one-test-owner',
            'job_sha256': job['job_sha256'], 'contract_sha256': contract['sha256'], 'review_sha256': review['sha256'], 'exact_action': 'Test only one bounded fixture.'})
        receipt = dict(schema_version=1, contract=contract, acquisition=acquisition, decision=decision,
                       validation=validation, review=review, authorization=authorization)
        self.save('training-admission.json', receipt)
        return receipt

    def test_default_draft_refuses_before_any_original_code(self):
        result = subprocess.run([sys.executable, '-'], input=self.spec['command'][3], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('TRAINING_SENTINEL', result.stdout)
        with self.assertRaises(ValueError): gate.admit(self.spec, self.prep, self.root)

    def test_negative_learning_result_can_support_reasoned_decision(self):
        self.evidence()
        spec = gate.admit(self.spec, self.prep, self.root)
        # Simulate the read-only /input mount locally; do not start a provider job.
        code = spec['command'][3].replace('/input/training-admission/' + self.prep['training_admission']['job_sha256'], self.root.as_posix())
        result = subprocess.run([sys.executable, '-'], input=code, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'TRAINING_SENTINEL')
        (self.root / 'qualified.json').write_text('{}')
        result = subprocess.run([sys.executable, '-'], input=code, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('TRAINING_SENTINEL', result.stdout)

    def test_changed_spec_settings_and_code_refuse(self):
        self.evidence()
        for where, field, value in [('spec', 'timeout', '2m'), ('prep', 'steps', 2)]:
            spec, prep = copy.deepcopy(self.spec), copy.deepcopy(self.prep)
            (spec if where == 'spec' else prep)[field] = value
            with self.assertRaises(ValueError): gate.admit(spec, prep, self.root)
        prep = copy.deepcopy(self.prep)
        prep['training_admission']['intended_command'] += '\nprint(1)'
        with self.assertRaises(ValueError): gate.admit(self.spec, prep, self.root)

    def test_missing_failed_mismatched_and_forged_types_refuse(self):
        for document, field, value in [('acquisition', 'status', 'failed'), ('acquisition', 'completed_outputs', 55),
            ('acquisition', 'expected_outputs', True), ('review', 'model', 'gpt-6.1-sol'),
            ('review', 'reviewer_id', 'sol-test-request'), ('review', 'status', 'PENDING'),
            ('review', 'decision_sha256', '0'*64), ('validation', 'status', 'FAIL'),
            ('authorization', 'status', 'LOCAL_FIXES_ONLY'), ('decision', 'status', 'diagnose_first')]:
            with self.subTest(document=document, field=field):
                receipt = self.evidence()
                data = gate.read_json(self.root / receipt[document]['path'])
                data[field] = value
                receipt[document] = self.save(receipt[document]['path'], data)
                self.save('training-admission.json', receipt)
                with self.assertRaises(ValueError): gate.admit(self.spec, self.prep, self.root)
        receipt = self.evidence(); (self.root / 'review.json').unlink()
        with self.assertRaises(ValueError): gate.admit(self.spec, self.prep, self.root)

    def test_duplicate_keys_bad_json_and_traversal_refuse(self):
        for body in ('{"schema_version":1,"schema_version":1}', '{', '{"schema_version":NaN}'):
            (self.root / 'training-admission.json').write_text(body)
            with self.assertRaises(ValueError): gate.admit(self.spec, self.prep, self.root)
        for name in ('../x', '/x', 'a\\b', 'C:x', 'a/./b', 'a//b'):
            receipt = self.evidence(); receipt['review']['path'] = name
            self.save('training-admission.json', receipt)
            with self.assertRaises(ValueError): gate.admit(self.spec, self.prep, self.root)

    def test_single_submit_boundary_blocks_invalid_and_repeat(self):
        from unittest.mock import Mock
        api = Mock()
        with self.assertRaises(ValueError): gate.submit(api, self.spec, self.prep, self.root)
        api.run_job.assert_not_called()
        self.evidence()
        api.run_job.return_value = 'fake-job'
        self.assertEqual(gate.submit(api, self.spec, self.prep, self.root), 'fake-job')
        self.assertEqual(api.run_job.call_count, 1)
        with self.assertRaises(ValueError): gate.submit(api, self.spec, self.prep, self.root)
        self.assertEqual(api.run_job.call_count, 1)

    def test_unknown_submit_outcome_is_never_retried(self):
        from unittest.mock import Mock
        self.evidence()
        api = Mock()
        api.run_job.side_effect = TimeoutError('unknown provider outcome')
        with self.assertRaises(TimeoutError): gate.submit(api, self.spec, self.prep, self.root)
        with self.assertRaises(ValueError): gate.submit(api, self.spec, self.prep, self.root)
        self.assertEqual(api.run_job.call_count, 1)

    def test_native_and_saved_json_reach_real_sdk_serializer_equally(self):
        from huggingface_hub import Volume
        from huggingface_hub.hf_api import _create_job_spec
        from . import hf_train

        class OfflineSDKBoundary:
            def run_job(self, **spec):
                self.spec = spec
                spec = dict(spec)
                spec.pop('namespace')
                return _create_job_spec(secrets=None, **spec)

        self.spec, self.prep = hf_train.specification('v5.zip', 'a'*64, 'b'*32)
        self.evidence()
        originals = gate.canonical(gate.plain([self.spec, self.prep]))
        native = OfflineSDKBoundary()
        native_payload = gate.submit(native, self.spec, self.prep, self.root)
        native_semantics = gate.plain(native.spec)
        self.assertEqual(originals, gate.canonical(gate.plain([self.spec, self.prep])))
        # Separate exclusive claims for equivalent synthetic fixtures.
        self.setUp()
        self.spec, self.prep = json.loads(originals)
        self.evidence()
        saved = OfflineSDKBoundary()
        saved_payload = gate.submit(saved, self.spec, self.prep, self.root)
        self.assertEqual(saved_payload, native_payload)
        self.assertEqual(gate.plain(saved.spec), native_semantics)
        self.assertTrue(all(type(v) is Volume for v in saved.spec['volumes']))
        self.assertEqual(originals, gate.canonical([self.spec, self.prep]))

    def test_malformed_sdk_specs_leave_no_claim(self):
        from unittest.mock import Mock
        good = {'type': 'bucket', 'source': 'test/bucket', 'mountPath': '/input', 'readOnly': True}
        bad_volumes = [dict(good, ignored='setting'), dict(good, readOnly=1),
                       dict(good, mountPath='input'), dict(good, type='unknown'),
                       dict(good, path=None), {'source': 'test/bucket'}, 'bucket']
        bad_specs = [{'volumes': [volume]} for volume in bad_volumes]
        bad_specs += [{'volumes': good}, {'timeout': 'invalid'}, {'extra_sdk_argument': True},
                      {'image': ['unsupported-image-representation']}]
        for mutation in bad_specs:
            with self.subTest(mutation=mutation):
                self.setUp()
                original = dict(self.spec, **mutation)
                @gate.draft
                def builder():
                    intended = copy.deepcopy(original)
                    intended['command'][3] = "print('TRAINING_SENTINEL')"
                    return intended, {'command_sha256': gate.digest(b"print('TRAINING_SENTINEL')"), 'steps': 1}
                self.spec, self.prep = builder()
                self.evidence()
                api = Mock()
                with self.assertRaises(ValueError): gate.submit(api, self.spec, self.prep, self.root)
                api.run_job.assert_not_called()
                self.assertFalse(list(self.root.glob('submission-*.json')))

    def test_all_five_real_builders_refuse_and_inference_still_prepares(self):
        from . import hf_train, hf_continue, hf_contextual, hf_mixed, hf_nllb, hf_preflight
        from .test_hf_continue import ContinuationPreparationTests
        builders = [(hf_train.specification, ('v5.zip', 'a'*64, 'b'*32)),
                    (hf_continue.specification, (), ContinuationPreparationTests().options()),
                    (hf_contextual.specification, ('c'*32,)),
                    (hf_mixed.prepare, (ROOT/'resources/local/training-ready-v2-20260929/data/train.jsonl', ROOT/'experiments/training-ready-v2-20260929/data-manifest.json', 'd'*32)),
                    (hf_nllb.specification, ('e'*32,))]
        with patch('huggingface_hub.HfApi.run_job', side_effect=AssertionError('No cloud submission')):
            for entry in builders:
                builder, args = entry[:2]; kwargs = entry[2] if len(entry) > 2 else {}
                with self.subTest(builder=builder.__module__):
                    spec, prep = builder(*args, **kwargs)
                    result = subprocess.run([sys.executable, '-'], input=spec['command'][3], capture_output=True, text=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('Training blocked:', result.stderr)
                    self.assertEqual(prep['training_admission']['status'], 'BLOCKED_DRAFT')
                    with self.assertRaises(ValueError): gate.admit(spec, prep, self.root)
            spec, _ = hf_preflight.specification('cuda')
            self.assertNotIn('Training blocked:', spec['command'][3])


if __name__ == '__main__':
    unittest.main()
