"""CPU child-stop and durable reconciliation checks; no cloud or weights."""
import copy
from contextlib import ExitStack
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid
from . import hf_learning_eval as launcher, learning_eval as evaluator
from .test_learning_eval import ROOT


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.scratch = ROOT / 'resources/local/learning-eval-check' / uuid.uuid4().hex
        self.scratch.mkdir(parents=True)
        self.output = self.scratch / 'result'
        self.output.mkdir()
        rows = [{'case_id': f'LD-{i:03d}', 'prompt': 'p'} for i in range(1, 29)]
        identity = {'adapters': {a: {'adapter_model.safetensors': a * 8} for a in evaluator.ARMS}}
        self.state = evaluator.initial_state(rows, identity)

    def save(self):
        (self.output / 'run.json').write_text(json.dumps(self.state), encoding='utf-8')

    def active(self):
        self.state.update(attempted_outputs=1, active_output_id=self.state['schedule'][0],
                          unattempted_output_ids=self.state['schedule'][1:])
        self.save()

    def test_unknown_active_attempt_is_recorded_once(self):
        self.active()
        result = launcher.reconcile_evaluation(self.output)
        row = json.loads((self.output / 'predictions.jsonl').read_bytes())
        self.assertEqual((result['status'], result['attempted_outputs'], result['recorded_outputs'],
                          result['successful_outputs'], len(result['unattempted_output_ids'])),
                         ('incomplete', 1, 1, 0, 55))
        self.assertEqual(row['status'], 'interrupted')
        self.assertIsNone(row['text'])
        self.assertIsNone(row['output_token_ids'])
        original = (self.output / 'predictions.jsonl').read_bytes()
        self.assertEqual(launcher.reconcile_evaluation(self.output), result)
        self.assertEqual((self.output / 'predictions.jsonl').read_bytes(), original)

    def test_committed_real_partial_output_is_preserved_without_promotion(self):
        self.active()
        row = dict(id=self.state['schedule'][0], case_id='LD-001', arm='reference', sequence=1,
                   identity_sha256=self.state['identity_sha256'], status='timeout', text='partial answer',
                   output_token_ids=[7], output_tokens=1)
        original = (json.dumps(row) + '\n').encode()
        (self.output / 'predictions.jsonl').write_bytes(original)
        result = launcher.reconcile_evaluation(self.output)
        self.assertEqual((result['recorded_outputs'], result['successful_outputs']), (1, 0))
        self.assertEqual((self.output / 'predictions.jsonl').read_bytes(), original)
        self.assertEqual(launcher.reconcile_evaluation(self.output), result)

    def test_loading_failure_keeps_all_56_unattempted(self):
        self.state['status'] = 'loading_bf16'
        self.save()
        result = launcher.reconcile_evaluation(self.output)
        self.assertEqual((result['status'], result['attempted_outputs'], result['recorded_outputs']),
                         ('incomplete', 0, 0))
        self.assertEqual(len(result['unattempted_output_ids']), 56)

    def test_child_cutoff_precedes_compute_kill_by_existing_reserve(self):
        stage = self.scratch / 'stage'
        evidence = self.scratch / 'evidence'
        evidence.mkdir()
        fake_runtime = SimpleNamespace(gpu_admission=lambda: {}, offline=lambda: None)
        fake_bundle = SimpleNamespace(verify=lambda folder: None)
        settings = dict(reference_manifest_sha256='r', candidate_manifest_sha256='c',
                        reference_adapter_files={}, candidate_adapter_files={}, inputs_name='inputs.jsonl',
                        export_reserve_seconds=180)
        deadline = time.monotonic() + 6600
        before = datetime.now(timezone.utc)
        with patch.dict(sys.modules, bundle=fake_bundle, runtime=fake_runtime), \
                patch.object(launcher, 'copy_adapter'), patch.object(launcher, 'emit'), \
                patch('shutil.copyfile'), patch('subprocess.run'), patch.object(launcher, 'run_logged') as logged:
            launcher.evaluation_body(settings, stage, deadline, evidence)
        command, _, timeout = logged.call_args.args
        cutoff = datetime.fromisoformat(command[command.index('--deadline-utc') + 1])
        self.assertLessEqual((cutoff - before).total_seconds(), 6420.1)
        self.assertGreater((cutoff - before).total_seconds(), 6419)
        self.assertGreater(timeout, 6599)
        self.assertLessEqual(timeout, 6600.000001)

    def test_parent_exports_original_evidence_when_reconciliation_fails(self):
        self.parent_export_case(partial=True)

    def test_parent_finalizes_driver_and_active_attempt_before_export(self):
        self.parent_export_case(partial=False)

    def parent_export_case(self, partial):
        stage = self.scratch / 'stage'
        stage.mkdir()
        settings = dict(internal_seconds=3300, compute_seconds=3000, maximum_wait_seconds=0,
                        inputs_name='inputs.jsonl', inputs_sha256='x', bundle_name='bundle.zip',
                        bundle_sha256='b', bootstrap_hashes={}, schema_version=1,
                        runner_sha256='r', helper_sha256={}, reference_adapter_files={},
                        candidate_adapter_files={}, generation=evaluator.GENERATION)
        def failed_body(settings, stage, deadline, evidence):
            folder = evidence / 'evaluation' / 'evaluation'
            folder.mkdir(parents=True)
            if not partial:
                self.state.update(attempted_outputs=1, active_output_id=self.state['schedule'][0],
                                  unattempted_output_ids=self.state['schedule'][1:])
            (folder / 'run.json').write_text(json.dumps(self.state), encoding='utf-8')
            (folder.parent / 'run.json').write_text(json.dumps({'status': 'evaluating'}), encoding='utf-8')
            if partial: (folder / 'predictions.jsonl').write_bytes(b'{"partial":')
            (evidence / 'driver.log').write_bytes(b'original failure log')
            raise TimeoutError('forced child stop')
        def export(evidence, output, deadline, identity):
            if partial:
                self.assertEqual((evidence / 'evaluation/evaluation/predictions.jsonl').read_bytes(), b'{"partial":')
                self.assertTrue((evidence / 'reconciliation-error.json').exists())
            else:
                row = json.loads((evidence / 'evaluation/evaluation/predictions.jsonl').read_bytes())
                self.assertEqual(row['status'], 'interrupted')
                driver = json.loads((evidence / 'evaluation/run.json').read_bytes())
                self.assertEqual((driver['status'], driver['attempted_outputs'], driver['recorded_outputs']),
                                 ('incomplete', 1, 1))
                self.assertFalse((evidence / 'reconciliation-error.json').exists())
            self.assertEqual((evidence / 'driver.log').read_bytes(), b'original failure log')
            self.assertEqual(identity['evaluation_status'], 'incomplete')
            return dict(manifest_sha256='local-test', manifest={'files': {}})
        with ExitStack() as stack:
            for name, value in [('fresh_output', lambda path: None), ('file_sha256', lambda path: 'x'),
                                ('safe_extract', lambda *a: None), ('emit', lambda *a, **k: None),
                                ('evaluation_body', failed_body), ('export_evidence', export)]:
                stack.enter_context(patch.object(launcher, name, value))
            stack.enter_context(patch('shutil.disk_usage', return_value=SimpleNamespace(free=100 * 1024**3)))
            stack.enter_context(patch.object(launcher.tempfile, 'mkdtemp', return_value=str(stage)))
            stack.enter_context(patch.object(launcher.signal, 'signal'))
            stack.enter_context(patch.object(launcher.signal, 'alarm', create=True))
            stack.enter_context(patch.object(launcher.signal, 'SIGALRM', 14, create=True))
            with self.assertRaisesRegex(TimeoutError, 'forced child stop'):
                launcher.execute_evaluation(settings, {}, '')

    def test_budget_override_is_explicit_versioned_and_serialized(self):
        packet = ROOT / 'experiments/corrected-learning-diagnosis-20260930'
        binding = json.loads((packet / 'binding.json').read_bytes())
        budget = dict(compute_seconds=6600, internal_seconds=6900, native_timeout_minutes=120)
        spec, receipt = launcher.prepare(packet / 'inputs.jsonl', '123456789abcdef0123456789abcdef0',
                                          corrected_binding=binding, timing_budget=budget)
        self.assertEqual(spec['timeout'], '120m')
        self.assertTrue(all(receipt[k] == v for k, v in budget.items()))
        self.assertEqual((receipt['export_reserve_seconds'], receipt['maximum_wait_seconds']), (180, 60))
        for altered in (dict(budget, compute_seconds=6601), dict(budget, compute_seconds=6600.0)):
            with self.assertRaises(ValueError):
                launcher.prepare(packet / 'inputs.jsonl', timing_budget=altered, corrected_binding=binding)
        with self.assertRaises(ValueError): launcher.prepare(packet / 'inputs.jsonl', timing_budget=budget)

    def test_inconsistent_ledger_and_partial_tail_fail_without_mutation(self):
        self.active()
        for kind in ('partial_tail', 'attempt_count', 'counter', 'schedule'):
            with self.subTest(kind=kind):
                altered = copy.deepcopy(self.state)
                raw = b''
                if kind == 'partial_tail': raw = b'{"id":"LD-001:reference"'
                elif kind == 'attempt_count': altered['attempted_outputs'] = 2
                elif kind == 'counter': altered['successful_outputs'] = 1
                else: altered['schedule'][0] = 'LD-999:reference'
                ledger = json.dumps(altered).encode()
                (self.output / 'run.json').write_bytes(ledger)
                (self.output / 'predictions.jsonl').write_bytes(raw)
                with self.assertRaises(ValueError): launcher.reconcile_evaluation(self.output)
                self.assertEqual((self.output / 'run.json').read_bytes(), ledger)
                self.assertEqual((self.output / 'predictions.jsonl').read_bytes(), raw)

    def test_actual_run_logged_kill_preserves_prior_rows_and_records_active(self):
        output = self.scratch / 'child'
        child = r'''
import sys,time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from datetime import datetime,timedelta,timezone
from cloud_pilot.test_learning_eval import StubModel
from cloud_pilot import learning_eval as run
class Slow(StubModel):
    def generate(self,**kwargs):
        if self.calls==2: time.sleep(40)
        return super().generate(**kwargs)
rows=[{'case_id':f'LD-{i:03d}','prompt':'p'} for i in range(1,29)]
identity={'adapters':{a:{'adapter_model.safetensors':a*8} for a in run.ARMS}}
with patch.object(run.qualified,'prefill_canary',return_value={'status':'passed'}),patch.object(run.old,'emit'):
    run.generate_pairs(Slow(),SimpleNamespace(decode=lambda *a,**k:'answer'),rows,
        {r['case_id']:[2,3,4] for r in rows},Path(sys.argv[1]),identity,
        (datetime.now(timezone.utc)+timedelta(hours=3)).isoformat(),device='cpu')
'''
        with self.assertRaises(subprocess.TimeoutExpired):
            launcher.run_logged([sys.executable, '-B', '-X', 'utf8', '-c', child, str(output)],
                                self.scratch / 'driver.log', 20)
        prior = (output / 'predictions.jsonl').read_bytes()
        self.assertEqual(len(prior.splitlines()), 2)
        state = launcher.reconcile_evaluation(output)
        self.assertEqual((state['attempted_outputs'], state['recorded_outputs'], state['successful_outputs']), (3, 3, 2))
        self.assertEqual(len(state['unattempted_output_ids']), 53)
        self.assertEqual(state['scheduled_outputs'], 56)
        final = (output / 'predictions.jsonl').read_bytes()
        self.assertTrue(final.startswith(prior))
        self.assertEqual(json.loads(final.splitlines()[-1])['status'], 'interrupted')
        self.assertEqual(launcher.reconcile_evaluation(output), state)
        self.assertEqual((output / 'predictions.jsonl').read_bytes(), final)


if __name__ == '__main__': unittest.main()
