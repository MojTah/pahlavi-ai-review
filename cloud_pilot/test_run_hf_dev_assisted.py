"""Focused offline controller checks; never run main, authenticate or contact HF."""
import copy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, create_autospec

import httpx
from huggingface_hub import HfApi, Volume

from . import run_hf_dev_assisted as controller


def job(trial, family='gemma', stage='RUNNING', job_id='job'):
    return SimpleNamespace(id=job_id, labels={'trial_id': trial, 'family': family,
        'purpose': 'dev-plain-assisted'}, status=SimpleNamespace(stage=stage))


class ComparisonControllerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.now = datetime(2026, 9, 27, 12, tzinfo=timezone.utc)
        cls.allowed = {'gemma': 'a' * 32, 'qwen': 'b' * 32}
        cls.admission = {'allowed_trial_ids': cls.allowed, 'observed_credit_usd': 18.37,
            'observation_utc': cls.now.isoformat(), 'total_reserved_compute_usd': 4.58337, 'reserve_usd': .75}
        cls.specs, cls.identities = {}, {}
        for family in cls.allowed:
            spec, identity = controller.hf_dev_assisted.specification(family, cls.allowed[family])
            cls.specs[family] = json.loads(controller.canonical(spec))
            cls.identities[family] = json.loads(controller.canonical(identity))

    def test_exact_admission_funding_rate_and_incremental_cost(self):
        self.assertEqual(controller.checked_admission(self.admission, 'gemma', self.allowed['gemma'], self.now), self.allowed)
        controller.checked_admission(self.admission, 'gemma', self.allowed['gemma'], self.now + timedelta(minutes=30))
        changes = [
            ('observed_credit_usd', 5.33), ('observed_credit_usd', float('nan')),
            ('observed_credit_usd', float('inf')), ('total_reserved_compute_usd', 2.291685),
            ('total_reserved_compute_usd', 4.58), ('reserve_usd', .74),
            ('observation_utc', (self.now - timedelta(minutes=31)).isoformat()),
            ('observation_utc', (self.now + timedelta(seconds=1)).isoformat()),
            ('observation_utc', '2026-09-27T12:00:00'),
            ('allowed_trial_ids', {'gemma': 'a' * 32, 'qwen': 'a' * 32}),
            ('allowed_trial_ids', {**self.allowed, 'third': 'c' * 32}),
        ]
        for key, value in changes:
            altered = {**self.admission, key: value}
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                controller.checked_admission(altered, 'gemma', self.allowed['gemma'], self.now)
        with self.assertRaises(ValueError):
            controller.checked_admission(self.admission, 'qwen', self.allowed['gemma'], self.now)
        hardware = dict(name='a100-large', unit_label='minute', unit_cost_micro_usd=41667)
        controller.checked_hardware(SimpleNamespace(**hardware))
        for key, value in [('name', 'a100-small'), ('unit_label', 'hour'), ('unit_cost_micro_usd', 41668)]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                controller.checked_hardware(SimpleNamespace(**{**hardware, key: value}))
        self.assertEqual(controller.incremental_compute_usd(0), 0)
        self.assertEqual(controller.incremental_compute_usd(3300), 2.291685)

    def test_only_declared_sibling_is_permitted_and_current_trial_is_never_reused(self):
        sibling = job(self.allowed['qwen'], 'qwen')
        controller.checked_jobs([sibling, job('old', stage='COMPLETED')], self.allowed, 'gemma')
        controller.checked_jobs([], self.allowed, 'gemma')
        forbidden = [
            [job(self.allowed['gemma'])], [job(self.allowed['gemma'], stage='COMPLETED')],
            [job('unrelated')], [sibling, job(self.allowed['qwen'], 'qwen', job_id='duplicate')],
            [job(self.allowed['qwen'], 'gemma')], [job(None)],
        ]
        for jobs in forbidden:
            with self.subTest(jobs=jobs), self.assertRaises(ValueError):
                controller.checked_jobs(jobs, self.allowed, 'gemma')

    def test_preparation_checks_actual_generated_spec_and_all_hash_boundaries(self):
        admission_bytes = controller.canonical(self.admission).encode()
        for family in self.allowed:
            spec_bytes = controller.canonical(self.specs[family]).encode()
            identity = {**self.identities[family], 'spec_sha256': hashlib.sha256(spec_bytes).hexdigest(),
                'controller_sha256': hashlib.sha256(b'controller fixture').hexdigest(),
                'admission_sha256': hashlib.sha256(admission_bytes).hexdigest(), 'source_commit': 'c' * 40}
            args = (family, spec_bytes, identity, admission_bytes, 'c' * 40, b'controller fixture')
            self.assertEqual(controller.checked_preparation(*args), self.specs[family])
            self.assertEqual(controller.canonical([Volume(**v) for v in self.specs[family]['volumes']]),
                             controller.canonical(self.specs[family]['volumes']))
            for index, value in [(1, spec_bytes + b' '), (3, admission_bytes + b' '), (4, 'd' * 40), (5, b'changed')]:
                changed = list(args)
                changed[index] = value
                with self.subTest(family=family, index=index), self.assertRaises(ValueError):
                    controller.checked_preparation(*changed)
            altered = copy.deepcopy(self.specs[family])
            altered['timeout'] = '60m'
            altered_bytes = controller.canonical(altered).encode()
            altered_identity = {**identity, 'spec_sha256': hashlib.sha256(altered_bytes).hexdigest()}
            with self.assertRaisesRegex(ValueError, 'current frozen sources'):
                controller.checked_preparation(family, altered_bytes, altered_identity, admission_bytes, 'c' * 40, b'controller fixture')
            altered_identity = {**identity, 'command_sha256': '0' * 64}
            with self.assertRaisesRegex(ValueError, 'source identity'):
                controller.checked_preparation(family, spec_bytes, altered_identity, admission_bytes, 'c' * 40, b'controller fixture')

    def test_manifest_identity_paths_small_results_and_persistence(self):
        for family, identity in self.identities.items():
            prefix = identity['output_prefix']
            files = {name: {'bytes': 10, 'sha256': '1' * 64} for name in
                ('comparison/run.json', 'comparison/predictions.jsonl', 'comparison-status.json')}
            manifest = {**{key: identity[key] for key in controller.IDENTITY_KEYS}, 'operation': 'dev_plain_assisted',
                'training_performed': False, 'comparison_status': 'complete', 'files': files}
            entries = {prefix + '/' + name: SimpleNamespace(path=prefix + '/' + name, size=10, xet_hash='committed') for name in files}
            self.assertEqual(len(controller.checked_inventory(manifest, entries, prefix, identity)), 3)
            absent = dict(entries)
            absent.pop(prefix + '/comparison/run.json')
            self.assertIsNone(controller.checked_inventory(manifest, absent, prefix, identity))
            for key in controller.IDENTITY_KEYS:
                with self.subTest(family=family, key=key), self.assertRaises(ValueError):
                    controller.checked_inventory({**manifest, key: 'changed'}, entries, prefix, identity)
            for field, value in [('operation', 'other'), ('training_performed', True), ('comparison_status', 'unknown')]:
                with self.subTest(field=field), self.assertRaises(ValueError):
                    controller.checked_inventory({**manifest, field: value}, entries, prefix, identity)
            for name in ('../escape.json', 'weights.safetensors', 'adapter_model.bin'):
                with self.subTest(name=name), self.assertRaises(ValueError):
                    controller.checked_inventory({**manifest, 'files': {**files, name: {'bytes': 1, 'sha256': '1' * 64}}}, entries, prefix, identity)
            for record in ({'bytes': -1, 'sha256': '1' * 64}, {'bytes': True, 'sha256': '1' * 64}, {'bytes': 10, 'sha256': 'bad'}):
                altered = copy.deepcopy(manifest)
                altered['files']['comparison/run.json'] = record
                with self.assertRaises(ValueError):
                    controller.checked_inventory(altered, entries, prefix, identity)
            altered = copy.deepcopy(manifest)
            altered['files'].pop('comparison/run.json')
            with self.assertRaisesRegex(ValueError, 'lacks predictions'):
                controller.checked_inventory(altered, entries, prefix, identity)
            extra = {**entries, prefix + '/weights.safetensors': SimpleNamespace(size=1)}
            with self.assertRaisesRegex(ValueError, 'declared scope'):
                controller.checked_inventory(manifest, extra, prefix, identity)
            too_large = copy.deepcopy(manifest)
            too_large['files']['comparison/run.json']['bytes'] = 17 * 1024**2
            large_entries = {**entries, prefix + '/comparison/run.json': SimpleNamespace(path=prefix + '/comparison/run.json',
                size=17 * 1024**2, xet_hash='committed')}
            with self.assertRaisesRegex(ValueError, 'declared scope'):
                controller.checked_inventory(too_large, large_entries, prefix, identity)

    def test_observation_retries_only_transport_failures_and_is_bounded(self):
        sleep = Mock()
        call = Mock(side_effect=[httpx.ConnectError('offline'), httpx.ReadTimeout('offline'), 'ok'])
        self.assertEqual(controller.observe(call, sleep), 'ok')
        self.assertEqual((call.call_count, sleep.call_count), (3, 2))
        call = Mock(side_effect=httpx.ConnectError('offline'))
        with self.assertRaises(controller.ObservationUnavailable):
            controller.observe(call, sleep)
        self.assertEqual(call.call_count, 3)
        call = Mock(side_effect=ValueError('bad response'))
        with self.assertRaises(ValueError):
            controller.observe(call, sleep)
        self.assertEqual(call.call_count, 1)

    def test_failed_submission_never_reposts_and_reconciles_only_its_trial(self):
        api = create_autospec(HfApi, instance=True)
        api.run_job.side_effect = httpx.ReadTimeout('response lost')
        own = job(self.allowed['gemma'])
        sibling = job(self.allowed['qwen'], 'qwen', job_id='sibling')
        api.list_jobs.side_effect = [[sibling], [sibling, own]]
        with self.assertRaises(controller.SubmissionFailed) as caught:
            controller.submit_once(api, self.specs['gemma'], self.allowed['gemma'], Mock(), sleep=Mock())
        self.assertEqual(caught.exception.jobs, [own])
        self.assertEqual((api.run_job.call_count, api.list_jobs.call_count), (1, 2))
        api.list_jobs.side_effect = RuntimeError('observation unavailable')
        with self.assertRaises(controller.SubmissionFailed) as caught:
            controller.submit_once(api, self.specs['gemma'], self.allowed['gemma'], Mock(), sleep=Mock())
        self.assertEqual(caught.exception.jobs, [])
        self.assertEqual(api.run_job.call_count, 2)  # One call per explicit helper invocation.

    def test_shutdown_targets_only_owned_jobs_and_requires_terminal_confirmation(self):
        api = create_autospec(HfApi, instance=True)
        own = job(self.allowed['gemma'], job_id='owned')
        api.inspect_job.side_effect = [SimpleNamespace(status=SimpleNamespace(stage=s)) for s in ('RUNNING', 'CANCELED')]
        clock = [0]
        def sleep(seconds):
            clock[0] += seconds
        controller.shutdown(api, [own], Mock(), start=0, clock=lambda: clock[0], sleep=sleep)
        api.cancel_job.assert_called_once_with(job_id='owned', namespace='Mojionix')
        self.assertEqual(api.inspect_job.call_count, 2)
        api.list_jobs.assert_not_called()
        api.inspect_job.side_effect = None
        api.inspect_job.return_value = SimpleNamespace(status=SimpleNamespace(stage='RUNNING'))
        clock[0] = 0
        with self.assertRaisesRegex(RuntimeError, 'termination not confirmed'):
            controller.shutdown(api, [own], Mock(), start=0, clock=lambda: clock[0], sleep=sleep)
        self.assertEqual(clock[0], 300)


if __name__ == '__main__':
    unittest.main()
