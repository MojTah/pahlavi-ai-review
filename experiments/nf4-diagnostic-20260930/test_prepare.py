"""Offline transport/ledger checks; no provider or model call."""
import ast
import base64
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout
import io

import prepare


class PreparationTests(unittest.TestCase):
    def test_staging_entrypoint_serializes_overlapping_observation_fields(self):
        import execute
        with tempfile.TemporaryDirectory(dir=prepare.ROOT / 'resources/local') as tmp:
            folder = Path(tmp)
            (folder / 'job-spec.json').write_text('{}')
            (folder / 'job-receipt.json').write_text('{}')
            captured = io.StringIO()
            with patch.object(execute, 'PROPOSAL', folder), patch.object(execute, 'LIVE', folder), \
                    patch.object(prepare, 'verify'), patch.object(execute.training_admission, 'sdk_spec'), \
                    patch.object(execute, 'HfApi'), \
                    patch.object(execute, 'live_check', return_value={'utc': 'live'}), \
                    patch.object(execute, 'stage', return_value={'utc': 'staged', 'weights_downloaded': False}), \
                    patch.object(execute, 'submit_once', side_effect=AssertionError('No submission')), redirect_stdout(captured):
                execute.main(False)
            self.assertEqual(json.loads(captured.getvalue())['status'], 'STAGED_NOT_SUBMITTED')
            self.assertFalse((folder / 'submission-claim.json').exists())

    def test_only_declared_numerical_and_parent_changes(self):
        from cloud_pilot import hf_learning_eval, training_admission
        run_id = '20260930000000000000000000000003'
        payload = prepare.build(run_id)
        spec = json.loads(payload['job-spec.json'])
        receipt = json.loads(payload['job-receipt.json'])
        original, old_receipt = hf_learning_eval.prepare(prepare.PACKET / 'inputs.jsonl', run_id,
            corrected_binding=json.loads((prepare.PACKET / 'binding.json').read_bytes()),
            timing_budget=prepare.frozen.reviewed.BUDGET)
        old_program = prepare.frozen.decoded(original['command'][3])
        program = prepare.decoded(spec['command'][3])
        before, after = prepare.literals(old_program), prepare.literals(program)
        expected = dict(before['settings'])
        expected['helper_sha256'] = dict(expected['helper_sha256'],
            **{'bf16_learning_eval.py': before['settings']['runner_sha256']})
        expected.update(runner_sha256=prepare.sha((prepare.ROOT / 'cloud_pilot/nf4_learning_eval.py').read_bytes()),
                        numerical_condition='nf4_training_matched')
        self.assertEqual(after['settings'], expected)
        for name, entry in after['scripts'].items():
            local = 'nf4_learning_eval.py' if name == 'learning_eval.py' else ('learning_eval.py' if name == 'bf16_learning_eval.py' else name)
            raw = base64.b64decode(entry['content'])
            self.assertEqual(raw, (prepare.ROOT / 'cloud_pilot' / local).read_bytes())
            self.assertEqual(entry['sha256'], prepare.sha(raw))
            compile(raw, name, 'exec')
        old_functions = [ast.get_source_segment(old_program, n) for n in ast.parse(old_program).body if isinstance(n, ast.FunctionDef)]
        new_functions = [ast.get_source_segment(program, n) for n in ast.parse(program).body if isinstance(n, ast.FunctionDef)]
        self.assertEqual(new_functions[:-1], old_functions)
        self.assertEqual(len(new_functions), len(old_functions) + 1)
        expected_spec = training_admission.plain(original)
        expected_spec['command'][3] = spec['command'][3]
        expected_spec['labels']['purpose'] = 'nf4-learning-diagnosis'
        expected_spec['volumes'][-1]['path'] = receipt['output_prefix']
        self.assertEqual(spec, expected_spec)
        self.assertEqual(receipt['generation'], old_receipt['generation'])
        self.assertEqual(receipt['inputs_sha256'], old_receipt['inputs_sha256'])

    def test_interrupted_load_keeps_zero_attempts(self):
        from cloud_pilot import hf_learning_eval, learning_eval
        prepare.baseline_reconcile_evaluation = hf_learning_eval.reconcile_evaluation
        rows = [dict(case_id=f'LD-{i:03d}') for i in range(1, 29)]
        state = learning_eval.initial_state(rows, {'identity_sha256': 'test'})
        state['status'] = 'loading_nf4'
        with tempfile.TemporaryDirectory(dir=prepare.ROOT / 'resources/local') as tmp:
            path = Path(tmp)
            (path / 'run.json').write_text(json.dumps(state), encoding='utf-8')
            result = prepare.reconcile_evaluation(path)
            self.assertEqual(result['attempted_outputs'], 0)
            self.assertEqual(len(result['unattempted_output_ids']), 56)
            self.assertEqual(result['status'], 'incomplete')
            self.assertFalse((path / 'predictions.jsonl').exists())
            invalid = dict(state, scheduled_outputs=55)
            raw = json.dumps(invalid).encode()
            (path / 'run.json').write_bytes(raw)
            with self.assertRaises(ValueError):
                prepare.reconcile_evaluation(path)
            self.assertEqual((path / 'run.json').read_bytes(), raw)
            state['attempted_outputs'] = 1
            (path / 'run.json').write_text(json.dumps(state), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'loading ledger'):
                prepare.reconcile_evaluation(path)


if __name__ == '__main__':
    unittest.main()
