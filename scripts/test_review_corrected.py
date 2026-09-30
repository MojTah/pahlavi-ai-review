"""Offline integrity and synthetic arithmetic checks; no actual semantic ratings."""
import copy
from collections import Counter
import json
import unittest

from scripts import review_corrected as mod


class CorrectedReviewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files, cls.contract, cls.completion = mod.build_files()
        cls.mapping = mod.prep.decode_lines(cls.files['lead-only/mapping.jsonl'])
        cls.packets = {r: mod.prep.decode_lines(cls.files[f'reviewer-{r}/packet.jsonl']) for r in mod.SEEDS}

    def test_actual_integrity_reproducibility_and_blinding(self):
        self.assertEqual(self.files, mod.build_files()[0])
        root = mod.ROOT / 'experiments/corrected-review-20260930'
        for name, data in self.files.items():
            self.assertEqual((root / name).read_bytes(), data, name)
        self.assertTrue(self.completion['training_completed'])
        self.assertTrue(self.completion['gemma_original_run_completed'])
        self.assertEqual(mod.mixed.RUN_ID, 'ad548e0f8b7b454682dc2fd6c3298966')
        self.assertEqual(mod.three.CONDITIONS, ('nllb_initialized', 'nllb_trained', 'gemma280_plain'))
        seen = set()
        for reviewer, packet in self.packets.items():
            self.assertEqual(len(packet), 72)
            for row in packet:
                self.assertEqual(set(row), mod.prep.PACKET_FIELDS)
                self.assertNotIn(row['review_id'], seen)
                seen.add(row['review_id'])
                self.assertEqual(row['output_sha256'], mod.sha(row['output_text'].encode()))
            mapped = [m for m in self.mapping if m['reviewer'] == reviewer]
            self.assertEqual(Counter(m['condition'] for m in mapped), dict.fromkeys(mod.CONDITIONS, 24))
            for condition in mod.CONDITIONS:
                counts = Counter(m['assessment'] for m in mapped if m['condition'] == condition)
                self.assertEqual(counts, {'provisional_whole_translation': 15, 'constrained_meanings_only': 9})
            instructions = self.files[f'reviewer-{reviewer}/INSTRUCTIONS.md'].decode()
            self.assertIn('all 72 opaque records', instructions)
            for label in (*mod.CONDITIONS, mod.RUN_ID, mod.JOB_ID):
                self.assertNotIn(label, instructions)
        orders = [[(m['condition'], m['case_id']) for m in self.mapping if m['reviewer'] == r] for r in mod.SEEDS]
        self.assertNotEqual(*orders)

    def test_corrected_run_rejects_tampered_evidence(self):
        from tokenizers import Tokenizer
        raw = {name.removeprefix('lead-only/raw/corrected96_plain/'): data for name, data in self.files.items()
               if name.startswith('lead-only/raw/corrected96_plain/')}
        preparation = json.loads(raw['execution-preparation.json'])
        rows = mod.prep.load_contract()[1]
        train, manifest = mod.mixed.driver.read_data(mod.TRAIN, mod.EXP / 'recovered/data-manifest.json', preparation)
        tokenizer = Tokenizer.from_file(str(mod.mixed.TOKENIZER / 'tokenizer.json'))
        top, training, evaluation = (json.loads(raw[n]) for n in ('mixed/run.json', 'mixed/training/run.json', 'mixed/evaluation/run.json'))
        predictions = mod.prep.decode_lines(raw['mixed/evaluation/predictions.jsonl'])
        gemma = json.loads(self.files['lead-only/raw/gemma280/run.json'])
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
                mod.mixed.validate_artifacts(*changed, rows, preparation, train, manifest, gemma, tokenizer)
        proof = json.loads(raw['recovery.json'])
        proof['run_id'] = mod.mixed.RUN_ID
        with self.assertRaisesRegex(ValueError, 'Recovery proof'):
            mod.bound(mod.mixed.validate_recovery, RUN_ID=mod.RUN_ID)(mod.EXP / 'recovered',
                raw['export-manifest.json'], json.loads(raw['export-manifest.json']), proof, preparation)

    def synthetic(self):
        packets, mapping = copy.deepcopy(self.packets), copy.deepcopy(self.mapping)
        for rows in packets.values():
            for p in rows:
                p['output_text'] = 'SYNTHETIC CHECK ONLY ' + p['review_id']
                p['output_sha256'] = mod.sha(p['output_text'].encode())
        for m in mapping:
            m['output_sha256'] = next(p['output_sha256'] for p in packets[m['reviewer']] if p['review_id'] == m['review_id'])
        reviews = {r: [dict(review_id=p['review_id'], output_sha256=p['output_sha256'],
            judgment='accepted' if p['assessment'] == 'provisional_whole_translation' else 'constrained_only',
            categories={c: 'pass' for c in mod.prep.CATEGORIES}, supported_span_severity='none',
            unknown_span_handling='no_unknown_span', reason='Synthetic scorer check only.', output_span='')
            for p in rows] for r, rows in packets.items()}
        return mapping, packets, reviews

    def test_unchanged_paired_arithmetic_separate_reviewers_and_denominators(self):
        mapping, packets, reviews = self.synthetic()
        gains = {}
        for m in mapping:
            if m['reviewer'] == 'A' and m['condition'] == mod.CONDITIONS[0] and m['assessment'] == 'provisional_whole_translation':
                gains.setdefault(m['work_id'], m['case_id'])
        selected = list(gains.values())[:2]
        for m in mapping:
            if m['condition'] == mod.CONDITIONS[0] and m['case_id'] in selected:
                rating = next(r for r in reviews[m['reviewer']] if r['review_id'] == m['review_id'])
                rating.update(judgment='meaning_error', supported_span_severity='meaning_error', output_span='SYNTHETIC')
                rating['categories']['lexical_meaning'] = 'fail'
        result = mod.summarize(mapping, packets, reviews, self.contract, self.completion)
        primary = ' -> '.join(mod.PAIRS[0])
        self.assertTrue(result['both_reviewers_screen'][primary])
        self.assertEqual(set(result['both_reviewers_screen']), {' -> '.join(p) for p in mod.PAIRS})
        for reviewer in mod.SEEDS:
            for report in result['reviewers'][reviewer]['conditions'].values():
                self.assertEqual((report['whole_denominator'], report['constrained_denominator']), (15, 9))
        item = next(m for m in mapping if m['reviewer'] == 'B' and m['condition'] == mod.CONDITIONS[0] and m['case_id'] == selected[0])
        rating = next(r for r in reviews['B'] if r['review_id'] == item['review_id'])
        rating.update(judgment='accepted', supported_span_severity='none', output_span='')
        rating['categories']['lexical_meaning'] = 'pass'
        result = mod.summarize(mapping, packets, reviews, self.contract, self.completion)
        self.assertTrue(result['reviewers']['A']['paired'][primary]['screen_pass'])
        self.assertFalse(result['reviewers']['B']['paired'][primary]['screen_pass'])
        self.assertFalse(result['both_reviewers_screen'][primary])
        incomplete = dict(self.completion, training_completed=False)
        result = mod.summarize(mapping, packets, reviews, self.contract, incomplete)
        self.assertIsNone(result['both_reviewers_screen'][primary])
        with self.assertRaisesRegex(ValueError, 'coverage'):
            mod.scoring.validate_reviews(packets['A'], reviews['A'][:-1], expected_count=72)

    def test_blind_duplicate_conflict_requires_reconsideration(self):
        _, packets, reviews = self.synthetic()
        whole = [i for i, p in enumerate(packets['A']) if p['assessment'] == 'provisional_whole_translation']
        a, b = whole[:2]
        rid = packets['A'][b]['review_id']
        packets['A'][b] = dict(packets['A'][a], review_id=rid)
        reviews['A'][b] = dict(copy.deepcopy(reviews['A'][a]), review_id=rid)
        mod.duplicate_consistency(packets['A'], reviews['A'])
        reviews['A'][b].update(judgment='uncertain', supported_span_severity='uncertain', output_span='SYNTHETIC')
        reviews['A'][b]['categories']['lexical_meaning'] = 'uncertain'
        with self.assertRaisesRegex(ValueError, 'Blind duplicate ratings conflict'):
            mod.duplicate_consistency(packets['A'], reviews['A'])


if __name__ == '__main__':
    unittest.main()
