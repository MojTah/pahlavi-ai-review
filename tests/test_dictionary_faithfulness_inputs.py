"""The single prompt change preserves every complete source/dictionary payload."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('faithfulness_inputs',
    ROOT / 'experiments/dictionary-faithfulness-20261005/prepare.py')
prep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prep)


class InputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.controls, _ = prep.origin()
        cls.files = prep.build()
        cls.rows = [json.loads(x) for x in cls.files['model-inputs.jsonl'].splitlines()]

    def test_actual_token_replay_full_payloads_and_frozen_bytes(self):
        prep.validate_pairs(self.rows, self.controls)
        for name, data in self.files.items():
            self.assertEqual((prep.OUTPUT / name).read_bytes(), data)
        contract = json.loads(self.files['contract.json'])
        self.assertEqual(contract['planned_outputs'], 30)
        self.assertEqual(len(set(contract['schedule'])), 30)
        self.assertEqual(contract['native_timeout_minutes'], 120)
        self.assertEqual(contract['post_canary_admission_reserve_seconds'], 3420)
        self.assertFalse(contract['paid_run_admitted'])
        self.assertFalse(contract['training_admitted'])

    def test_payload_change_rejected_even_if_metadata_is_unchanged(self):
        rows = deepcopy(self.rows)
        rows[1]['messages'][1]['content'] += '\nextra instruction'
        with self.assertRaisesRegex(ValueError, 'user payload changed'):
            prep.validate_pairs(rows, self.controls)

    def test_case_specific_system_addition_rejected(self):
        rows = deepcopy(self.rows)
        rows[1]['messages'][0]['content'] += '\nUse a preferred sense.'
        with self.assertRaisesRegex(ValueError, 'only the frozen system sentence'):
            prep.validate_pairs(rows, self.controls)

    def test_control_change_rejected(self):
        rows = deepcopy(self.rows)
        rows[0]['messages'][0]['content'] += '\n' + prep.RULE
        with self.assertRaisesRegex(ValueError, 'Control must equal'):
            prep.validate_pairs(rows, self.controls)

    def test_missing_or_duplicate_case_rejected(self):
        for rows in (self.rows[:-1], [self.rows[0], self.rows[0], *self.rows[2:]]):
            with self.assertRaisesRegex(ValueError, '30 ordered pairs'):
                prep.validate_pairs(rows, self.controls)

    def test_dictionary_metadata_or_extra_field_rejected(self):
        rows = deepcopy(self.rows)
        rows[1]['dictionary_group_count'] -= 1
        with self.assertRaisesRegex(ValueError, 'dictionary metadata differs'):
            prep.validate_pairs(rows, self.controls)
        rows = deepcopy(self.rows)
        rows[1]['reference_answer'] = 'not model input'
        with self.assertRaisesRegex(ValueError, 'schema/arm differs'):
            prep.validate_pairs(rows, self.controls)


if __name__ == '__main__':
    unittest.main()
