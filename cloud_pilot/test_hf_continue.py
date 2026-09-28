"""Offline continuation interface, evidence and projection checks; no paid execution."""
import base64
import ast
import gzip
import inspect
import json
from pathlib import Path
import signal
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, call, patch
try:
    from . import hf_continue as continuation, hf_preflight
except ImportError:
    import hf_continue as continuation
    import hf_preflight

class ContinuationPreparationTests(unittest.TestCase):

    def test_each_readiness_gate_requires_completed_evidence(self):
        keys = {"linux_container_verified", "stage_dev_ready", "base_weights_verified", "transfer_roundtrip_verified", "adapter_export_roundtrip_verified"}
        controls = {"full_training_authorized": True, "cloud_controls_verified": True}
        checks = {key: {"verified": True, "evidence": key} for key in keys}
        result = continuation.readiness_for(checks, controls)
        self.assertIs(result["local_model_verified"], False)
        for key in keys:
            missing = dict(checks)
            missing.pop(key)
            with self.subTest(key=key), self.assertRaises(ValueError):
                continuation.readiness_for(missing, controls)
            missing[key] = {"verified": False}
            with self.assertRaises(ValueError):
                continuation.readiness_for(missing, controls)

    def test_remote_canary_requires_each_sha_and_exact_run_identity(self):
        root = Path("/canary")
        manifest = {"run_id": "b" * 32, "global_step": 20, "canary_compute_pass": True,
                    "files": {"training/optimizer.pt": {"bytes": 12, "sha256": "c" * 64}}}
        def checksum(path):
            return "a" * 64 if path.name == "manifest.json" else "c" * 64
        with patch.object(continuation, "file_sha256", side_effect=checksum) as hashed, \
             patch.object(Path, "read_text", return_value=json.dumps(manifest)), \
             patch.object(Path, "rglob", return_value=[root / "manifest.json", root / "training/optimizer.pt"]), \
             patch.object(Path, "resolve", lambda self: self), patch.object(Path, "is_file", return_value=True), \
             patch.object(Path, "is_symlink", return_value=False), patch.object(Path, "stat", return_value=SimpleNamespace(st_size=12)):
            self.assertEqual(continuation.verify_canary(root, "a" * 64, "b" * 32), manifest)
            self.assertEqual(hashed.call_count, 2)
            with self.assertRaises(ValueError):
                continuation.verify_canary(root, "a" * 64, "f" * 32)
            hashed.side_effect = lambda path: "a" * 64 if path.name == "manifest.json" else "bad"
            with self.assertRaises(ValueError):
                continuation.verify_canary(root, "a" * 64, "b" * 32)

    def options(self):
        return dict(bundle_name='v5.zip', bundle_sha256='a' * 64, evaluator_name='palref_eval.py', evaluator_sha256=continuation.file_sha256(Path(continuation.__file__).with_name('palref_eval.py')), inputs_name='palref40.jsonl', inputs_sha256=continuation.INPUTS_SHA256, canary_run_id='b' * 32, canary_manifest_sha256='c' * 64, admission_name='admission.json', admission_sha256='d' * 64, max_minutes=120, run_id='e' * 32)

    def test_spec_uses_frozen_runtime_readonly_canary_and_bounded_single_job(self):
        with patch('huggingface_hub.HfApi.whoami', side_effect=AssertionError('No auth')), patch('huggingface_hub.HfApi.run_job', autospec=True) as submit:
            spec, evidence = continuation.specification(**self.options())
            submit.assert_not_called()
        original, hashes = hf_preflight.specification('cuda')
        self.assertEqual(spec['image'], original['image'])
        self.assertEqual(spec['command'][4:], original['command'][4:])
        self.assertEqual(evidence['bootstrap_hashes'], hashes)
        payload = json.loads(gzip.decompress(base64.b64decode(spec['command'][4])))
        self.assertEqual(base64.b64decode(payload['runtime.py']['content']), Path(continuation.__file__).with_name('runtime.py').read_bytes())
        self.assertEqual((spec['flavor'], spec['timeout']), ('a100-large', '120m'))
        self.assertEqual([(v.to_dict()['mountPath'], v.to_dict()['readOnly']) for v in spec['volumes']], [('/input', True), ('/canary', True), ('/output', False)])
        self.assertNotIn('secrets', spec)
        self.assertEqual(evidence['expected_total_steps'], 312)
        compile(spec['command'][3], 'continuation', 'exec')

    def test_qualified_schedule_reaches_compiled_bootstrap_without_changing_pins(self):
        old, old_evidence = continuation.specification(**self.options())
        with patch('huggingface_hub.HfApi.run_job', autospec=True) as submit:
            spec, evidence = continuation.specification(**dict(self.options(), expected_total_steps=280))
            submit.assert_not_called()
        self.assertEqual(evidence['expected_total_steps'], 280)
        self.assertEqual(evidence['bootstrap_hashes'], old_evidence['bootstrap_hashes'])
        self.assertEqual(spec['image'], old['image'])
        self.assertEqual(spec['command'][4:], old['command'][4:])
        generated = spec['command'][3]
        tree = ast.parse(generated)
        settings = next(node.value for node in tree.body if isinstance(node, ast.Assign)
                        and any(isinstance(name, ast.Name) and name.id == 'settings' for name in node.targets))
        self.assertEqual(ast.literal_eval(settings)['expected_total_steps'], 280)
        self.assertIn(inspect.getsource(continuation.training_schedule), generated)
        compile(generated, 'qualified-continuation', 'exec')

    def test_bad_identity_scope_and_unbounded_time_are_rejected(self):
        for change in ({'inputs_sha256': 'a' * 64}, {'evaluator_sha256': 'a' * 64}, {'bundle_name': '../bad.zip'}, {'canary_run_id': 'e' * 32}, {'max_minutes': 151}, {'max_minutes': 10}, {'admission_sha256': 'bad'}, {'expected_total_steps': 20}, {'expected_total_steps': 280.0}, {'expected_total_steps': True}):
            options = self.options()
            options.update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                continuation.specification(**options)

    def test_measured_projection_refuses_insufficient_time_and_wrong_recipe(self):
        result = continuation.projection({'train_runtime': 400}, {'global_step': 20, 'max_steps': 312}, 9000)
        self.assertAlmostEqual(result['projected_seconds'], 8492)
        self.assertEqual(result['final_evaluation_allowance_seconds'], 420)
        self.assertEqual(result['model_reload_reserve_seconds'], 180)
        with self.assertRaises(TimeoutError):
            continuation.projection({'train_runtime': 400}, {'global_step': 20, 'max_steps': 312}, 8491)
        for state in ({'global_step': 19, 'max_steps': 312}, {'global_step': 20, 'max_steps': 300}):
            with self.assertRaises(ValueError):
                continuation.projection({'train_runtime': 400}, state, 9000)

    def test_row_derived_schedule_preserves_partial_final_accumulation(self):
        recipe = {'micro_batch_size': 1, 'gradient_accumulation_steps': 16, 'num_train_epochs': 2}
        for rows, steps in ((2484, 312), (2237, 280), (2240, 280), (2241, 282)):
            with self.subTest(rows=rows):
                result = continuation.training_schedule(rows, recipe, {'global_step': 20, 'max_steps': steps}, steps)
                self.assertEqual(result, {'train_rows': rows, 'expected_total_steps': steps, 'remaining_steps': steps - 20})
        for rows, settings, state, total in (
            (2237, recipe, {'global_step': 20, 'max_steps': 312}, 312),
            (2237, recipe, {'global_step': 20, 'max_steps': 312}, 280),
            (2484, recipe, {'global_step': 20, 'max_steps': 280}, 280),
            (2237, dict(recipe, num_train_epochs=3), {'global_step': 20, 'max_steps': 280}, 280),
            (2237, dict(recipe, micro_batch_size=2), {'global_step': 20, 'max_steps': 280}, 280),
            (2237, dict(recipe, gradient_accumulation_steps=8), {'global_step': 20, 'max_steps': 280}, 280),
            (0, recipe, {'global_step': 20, 'max_steps': 280}, 280),
            (2237, recipe, {'global_step': 40, 'max_steps': 280}, 280),
        ):
            with self.subTest(rows=rows, recipe=settings, state=state, total=total), self.assertRaises(ValueError):
                continuation.training_schedule(rows, settings, state, total)
        result = continuation.projection({'train_runtime': 400}, {'global_step': 20, 'max_steps': 280}, 9000, 280)
        self.assertEqual(result['remaining_steps'], 260)
        self.assertEqual(result['expected_total_steps'], 280)
        self.assertAlmostEqual(result['projected_seconds'], 7660)
        for available in (float('inf'), float('nan'), True, -1):
            with self.subTest(available=available), self.assertRaises(ValueError):
                continuation.projection({'train_runtime': 400}, {'global_step': 20, 'max_steps': 280}, available, 280)

    def test_cloud_rejects_stale_schedule_or_dataset_before_base_download(self):
        recipe = {'micro_batch_size': 1, 'gradient_accumulation_steps': 16, 'num_train_epochs': 2}
        for total, saved_steps, saved_hash in ((280, 312, 'h'), (312, 312, 'h'), (280, 280, 'old')):
            settings = dict(self.options(), expected_total_steps=total, bootstrap_hashes={'runtime.py': 'r'})
            manifest = {'bundle_sha256': settings['bundle_sha256'], 'bootstrap_hashes': settings['bootstrap_hashes'],
                        'files': {'training/metrics.json': {'bytes': 10}}}
            responses = {'admission.json': {}, 'environment.json': {},
                         'trainer_state.json': {'global_step': 20, 'max_steps': saved_steps},
                         'metrics.json': {'train_runtime': 400},
                         'provenance.json': {'train_sha256': saved_hash, 'training': recipe}}
            def read(path, *args, **kwargs):
                if path.name == 'train.jsonl':
                    return '\n'.join(json.dumps({'id': i, 'work_id': 'train'}) for i in range(2237))
                return json.dumps(responses[path.name])
            runtime = SimpleNamespace(gpu_admission=Mock(return_value={}), checked_files=Mock(), resume_checkpoint=Mock(),
                                      contract_at=Mock(return_value={'training': recipe}))
            with self.subTest(total=total, saved_steps=saved_steps, saved_hash=saved_hash), \
                 patch.dict(sys.modules, {'runtime': runtime, 'bundle': SimpleNamespace(verify=Mock())}), \
                 patch.object(sys, 'path', list(sys.path)), patch.object(signal, 'alarm', create=True), \
                 patch.object(continuation, 'remaining', return_value=1000), \
                 patch.object(continuation, 'admit'), patch.object(continuation, 'emit'), \
                 patch.object(continuation, 'verify_canary', return_value=manifest), \
                 patch.object(continuation, 'verify_adapter'), patch.object(continuation, 'file_sha256', return_value='h'), \
                 patch.object(Path, 'read_text', read), patch('shutil.copytree'), patch('shutil.copyfile'), \
                 patch('subprocess.run') as child:
                with self.assertRaises(ValueError):
                    continuation.continuation(settings, Path('/stage'), 5000, Path('/evidence'), {})
                child.assert_not_called()

    def test_completion_fields_cannot_label_280_as_legacy_312(self):
        # Execute the production result gate, without evaluating a model or copying artifacts.
        tree = ast.parse(inspect.getsource(continuation.continuation))
        nodes = tree.body[0].body
        start = next(i for i, node in enumerate(nodes) if isinstance(node, ast.Assign)
                     and any(isinstance(target, ast.Name) and target.id == 'status' for target in node.targets)) + 1
        end = next(i for i, node in enumerate(nodes) if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                   and isinstance(node.value.func, ast.Name) and node.value.func.id == 'child'
                   and node.value.args[0].value == 'palref_final')
        gate = compile(ast.Module(body=nodes[start:end], type_ignores=[]), 'completion-gate', 'exec')
        for total in (280, 312):
            identity = {'training_schedule_completed': False, 'training_reached_step_312': False}
            scope = {'settings': {'expected_total_steps': total}, 'identity': identity,
                     'status': {'status': 'training_complete', 'global_step': total}}
            exec(gate, scope)
            self.assertEqual(identity['completed_global_step'], total)
            self.assertIs(identity['training_schedule_completed'], True)
            self.assertIs(identity['training_reached_step_312'], total == 312)
        for status in ({'status': 'training_complete', 'global_step': 312},
                       {'status': 'canary_pass', 'global_step': 280},
                       {'status': 'training_complete', 'global_step': 280.0}):
            with self.subTest(status=status), self.assertRaises(ValueError):
                exec(gate, {'settings': {'expected_total_steps': 280}, 'identity': {}, 'status': status})

    def test_admission_requires_external_facts_and_aggregate_budget(self):
        record = {'schema_version': 1, 'full_training_authorized': True, 'cloud_controls_verified': True, 'evidence': {'authorization': 'user turn', 'cloud_controls': 'controller tests', 'canary_terminal': 'terminal evidence', 'baseline_reported': 'reported before full training'}, 'max_minutes': 120, 'prior_cumulative_compute_usd': 1, 'canary_elapsed_minutes': 20, 'remaining_aggregate_a100_minutes': 150, 'budget_ceiling_usd': 10}
        continuation.admit(record, 120)
        for change in ({'full_training_authorized': False}, {'evidence': {}}, {'prior_cumulative_compute_usd': 6}, {'remaining_aggregate_a100_minutes': 119}, {'budget_ceiling_usd': 50}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                continuation.admit(dict(record, **change), 120)

    def test_explicit_25_dollar_ceiling_preserves_cash_reserve(self):
        record = {'schema_version': 1, 'full_training_authorized': True, 'cloud_controls_verified': True,
                  'evidence': {'authorization': 'explicit user USD25', 'cloud_controls': 'controller tests',
                               'canary_terminal': 'terminal evidence', 'baseline_reported': 'reported'},
                  'max_minutes': 150, 'prior_cumulative_compute_usd': 18, 'canary_elapsed_minutes': 20,
                  'remaining_aggregate_a100_minutes': 150, 'budget_ceiling_usd': 25}
        metrics, state = {'train_runtime': 400}, {'global_step': 20, 'max_steps': 280}
        result = continuation.pre_submission_check(metrics, state, record, 600, expected_total_steps=280)
        self.assertEqual(result['worst_cumulative_compute_usd'] + result['cash_reserve_usd'], 25)
        self.assertEqual(result['expected_total_steps'], 280)
        for change in ({'prior_cumulative_compute_usd': 18.01}, {'prior_cumulative_compute_usd': 19},
                       {'budget_ceiling_usd': 50}, {'budget_ceiling_usd': float('inf')},
                       {'prior_cumulative_compute_usd': float('nan')}, {'canary_elapsed_minutes': True}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                continuation.admit(dict(record, **change), 150)

    def test_local_presubmission_checks_actual_timing_setup_and_cash_reserve(self):
        record = {'schema_version': 1, 'full_training_authorized': True, 'cloud_controls_verified': True,
                  'evidence': {'authorization': 'user turn', 'cloud_controls': 'controller tests',
                               'canary_terminal': 'terminal evidence', 'baseline_reported': 'reported'},
                  'max_minutes': 150, 'prior_cumulative_compute_usd': 1.8594, 'canary_elapsed_minutes': 50,
                  'remaining_aggregate_a100_minutes': 154 + 7 / 60, 'budget_ceiling_usd': 10}
        metrics, state = {'train_runtime': 369.9246}, {'global_step': 20, 'max_steps': 312}
        with patch('huggingface_hub.HfApi.run_job', side_effect=AssertionError('No submission')):
            result = continuation.pre_submission_check(metrics, state, record, 600)
        self.assertAlmostEqual(result['projected_seconds'], 7921.168908)
        self.assertEqual(result['available_seconds'], 8100)
        self.assertEqual(result['internal_timeout_minutes'], 145)
        self.assertAlmostEqual(result['worst_cumulative_compute_usd'] + result['cash_reserve_usd'], 8.8594)
        with self.assertRaises(TimeoutError):
            continuation.pre_submission_check(metrics, state, record, 780)
        with self.assertRaises(ValueError):
            continuation.pre_submission_check(metrics, state, dict(record, prior_cumulative_compute_usd=3.01), 600)
        for change in ({'remaining_aggregate_a100_minutes': 149}, {'max_minutes': 151}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                continuation.pre_submission_check(metrics, state, dict(record, **change), 600)
        for setup in (-1, float('nan'), True):
            with self.subTest(setup=setup), self.assertRaises(ValueError):
                continuation.pre_submission_check(metrics, state, record, setup)

    def test_same_evaluation_allowance_reaches_generated_training_deadline(self):
        options = dict(self.options(), max_minutes=150)
        spec, _ = continuation.specification(**options)
        self.assertEqual(spec['timeout'], '150m')
        self.assertEqual(continuation.TRAINING_TAIL_SECONDS,
                         continuation.EXPORT_RESERVE_SECONDS + continuation.FINAL_EVALUATION_SECONDS)
        generated = spec['command'][3]
        self.assertIn('FINAL_EVALUATION_SECONDS = 420', generated)
        self.assertIn('TRAINING_TAIL_SECONDS = 720', generated)
        self.assertIn('utc(TRAINING_TAIL_SECONDS)], TRAINING_TAIL_SECONDS)', generated)
        self.assertNotIn('300 + BASELINE_SECONDS + 90', generated)

    def test_training_resume_and_one_final_frozen_evaluation_only(self):
        body = inspect.getsource(continuation.continuation)
        self.assertLess(body.index('runtime.gpu_admission()'), body.index('child("base_download"'))
        self.assertNotIn('child("palref_original"', body)
        self.assertLess(body.index('child("full_resume"'), body.index('child("palref_final"'))
        self.assertEqual(body.count('str(evaluator), *common'), 1)
        self.assertIn('"--full", "--resume"', body)
        self.assertNotIn('"--max-steps"', body)
        self.assertNotIn('"eval"', body)
        self.assertIn('readiness_for(checks, controls)', body)

    def test_recovery_alarm_bounds_all_checks_then_restores_export_reserve(self):
        tree = ast.parse(inspect.getsource(continuation.continuation))
        statements = tree.body[0].body
        alarms = [node for node in statements if isinstance(node, ast.Expr) and
                  isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute) and
                  isinstance(node.value.func.value, ast.Name) and node.value.func.value.id == 'signal' and
                  node.value.func.attr == 'alarm']
        self.assertEqual(len(alarms), 2)
        source = inspect.getsource(continuation.continuation).splitlines()
        for gate in ('manifest = verify_canary(', 'runtime.checked_files(', 'verify_adapter(training)',
                     'panel_rows = module.read_inputs(', 'if overlap:'):
            line = next(index + 1 for index, text in enumerate(source) if gate in text)
            self.assertLess(alarms[0].lineno, line)
            self.assertLess(line, alarms[1].lineno)
        next_statement = statements[statements.index(alarms[1]) + 1]
        self.assertEqual(ast.unparse(next_statement.value.func), 'child')
        self.assertEqual(next_statement.value.args[0].value, 'base_download')
        code = compile(ast.Module(body=alarms, type_ignores=[]), 'recovery-boundaries', 'exec')
        for available, expected in (([1000, 900], [180, 900]), ([90, 60], [90, 60])):
            alarm, remaining = Mock(), Mock(side_effect=available)
            exec(code, {'signal': SimpleNamespace(alarm=alarm), 'remaining': remaining,
                        'deadline': 5000, 'EXPORT_RESERVE_SECONDS': continuation.EXPORT_RESERVE_SECONDS})
            self.assertEqual(alarm.call_args_list, [call(value) for value in expected])
            self.assertEqual(remaining.call_args_list, [call(5000, 300), call(5000, 300)])
if __name__ == '__main__':
    unittest.main()
