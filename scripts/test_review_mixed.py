"""Offline integrity and synthetic score checks; never writes semantic reviews."""
import copy
import json
import unittest

from scripts import review_mixed as mod


class MixedReviewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from tokenizers import Tokenizer
        cls.loaded = mod.load_sources()
        cls.files = mod.build_files(*cls.loaded)
        cls.mapping = mod.prep.decode_lines(cls.files['lead-only/mapping.jsonl'])
        cls.packets = {r: mod.prep.decode_lines(cls.files[f'reviewer-{r}/packet.jsonl']) for r in mod.SEEDS}
        cls.tokenizer = Tokenizer.from_file(str(mod.TOKENIZER / 'tokenizer.json'))

    def test_actual_completed_integrity_and_tampering(self):
        _, raw, completion, _, rows, references, assessments = self.loaded
        self.assertTrue(completion['complete'])
        self.assertEqual(completion['candidate_completed_outputs'], 24)
        self.assertEqual(self.files, mod.build_files(*self.loaded))
        seen = set()
        for r, packet in self.packets.items():
            self.assertEqual(len(packet), 48)
            self.assertEqual(self.files[f'reviewer-{r}/INSTRUCTIONS.md'].replace(b'all 48 opaque records', b'all 96 opaque records'), mod.prep.instructions())
            for p in packet:
                self.assertNotIn(p['review_id'], seen)
                seen.add(p['review_id'])
                self.assertEqual(set(p), mod.prep.PACKET_FIELDS)
                row = next(row for row in rows if row['source_text'] == p['source_text'])
                self.assertEqual(p['references'], {k: references[row['id']][k] for k in p['references']})
                self.assertEqual(p['constraint'], assessments[row['id']]['constraint'])
        preparation = json.loads(raw['execution-preparation.json'])
        train_rows, manifest = mod.driver.read_data(mod.TRAIN, mod.EXP / 'recovered/data-manifest.json', preparation)
        top, training, evaluation = (json.loads(raw[n]) for n in ('mixed/run.json', 'mixed/training/run.json', 'mixed/evaluation/run.json'))
        predictions = mod.prep.decode_lines(raw['mixed/evaluation/predictions.jsonl'])
        original = (top, training, evaluation, predictions)
        for mutate in (
            lambda v: v[3][0].update(input_sha256='f' * 64),
            lambda v: v[3][0].update(output_sha256='f' * 64),
            lambda v: v[3][0].update(rendered_input_ids_sha256='f' * 64),
            lambda v: v[3][0].update(adapter_sha256='f' * 64),
            lambda v: v[3][0].update(attempt=2),
            lambda v: v[3].reverse(),
            lambda v: v[1].update(completed_steps=95),
        ):
            changed = copy.deepcopy(original)
            mutate(changed)
            with self.assertRaises(ValueError):
                mod.validate_artifacts(*changed, rows, preparation, train_rows, manifest,
                                       json.loads(raw['gemma280/run.json']), self.tokenizer)
        proof = json.loads(raw['recovery.json'])
        proof['manifest_sha256'] = 'f' * 64
        with self.assertRaisesRegex(ValueError, 'Recovery proof'):
            mod.validate_recovery(mod.EXP / 'recovered', raw['export-manifest.json'],
                                  json.loads(raw['export-manifest.json']), proof, preparation)

    def test_separate_reviewers_frozen_screen_and_no_shrinking(self):
        # Synthetic categories exist only in memory to check aggregation, never as actual review evidence.
        reviews = {r: [dict(review_id=p['review_id'], output_sha256=p['output_sha256'],
            judgment='accepted' if p['assessment'] == 'provisional_whole_translation' else 'constrained_only',
            categories={c: 'pass' for c in mod.prep.CATEGORIES}, supported_span_severity='none',
            unknown_span_handling='no_unknown_span', reason='Synthetic scorer check only.', output_span='')
            for p in packet] for r, packet in self.packets.items()}
        gains = []
        for m in self.mapping:
            if (m['reviewer'] == 'A' and m['condition'] == mod.CONDITIONS[0]
                    and m['assessment'] == 'provisional_whole_translation' and m['work_id'] not in [w for _, w in gains]):
                gains.append((m['case_id'], m['work_id']))
                if len(gains) == 2:
                    break
        for m in self.mapping:
            if m['condition'] == mod.CONDITIONS[0] and m['case_id'] in {cid for cid, _ in gains}:
                review = next(x for x in reviews[m['reviewer']] if x['review_id'] == m['review_id'])
                packet = next(x for x in self.packets[m['reviewer']] if x['review_id'] == m['review_id'])
                review.update(judgment='meaning_error', supported_span_severity='meaning_error', output_span=packet['output_text'][:20])
                review['categories']['lexical_meaning'] = 'fail'
        result = mod.summarize(self.mapping, self.packets, reviews, self.loaded[3], self.loaded[2])
        self.assertTrue(result['both_reviewers_screen'])
        for r in mod.SEEDS:
            for report in result['reviewers'][r]['conditions'].values():
                self.assertEqual((report['whole_denominator'], report['constrained_denominator']), (15, 9))
        item = next(m for m in self.mapping if m['reviewer'] == 'B' and m['condition'] == mod.CONDITIONS[0] and m['case_id'] == gains[0][0])
        review = next(x for x in reviews['B'] if x['review_id'] == item['review_id'])
        review.update(judgment='accepted', supported_span_severity='none', output_span='')
        review['categories']['lexical_meaning'] = 'pass'
        result = mod.summarize(self.mapping, self.packets, reviews, self.loaded[3], self.loaded[2])
        self.assertTrue(result['reviewers']['A']['paired'][mod.PAIR]['screen_pass'])
        self.assertFalse(result['reviewers']['B']['paired'][mod.PAIR]['screen_pass'])
        self.assertFalse(result['both_reviewers_screen'])
        result = mod.summarize(self.mapping, self.packets, reviews, self.loaded[3], dict(self.loaded[2], complete=False))
        self.assertIsNone(result['both_reviewers_screen'])
        self.assertEqual(result['screen_status'], 'inconclusive')
        with self.assertRaisesRegex(ValueError, 'coverage'):
            mod.scoring.validate_reviews(self.packets['A'], reviews['A'][:-1], expected_count=48)


if __name__ == '__main__':
    unittest.main()
