"""Synthetic integrity and unchanged-merit checks; no cloud, weights or semantic review."""
import copy
import unittest
from scripts import review_nllb as r


class ReviewChecks(unittest.TestCase):
    def test_first_attempt_integrity(self):
        rows = [dict(id=f'c{i}', record_id=f'p{i}', work_id=f'w{i % 4}', source_text=f'source {i}') for i in range(24)]
        run = dict(status='completed', step=700, quality_validated=False, completed_parent_exposures=11185, model=r.nllb.MODEL,
            revision=r.nllb.REVISION, settings=r.nllb.SETTINGS, train_sha256=r.nllb.TRAIN_SHA,
            dev_sha256=r.nllb.DEV_SHA, runner_sha256=r.RUNNER_SHA)
        predictions = [dict(id=row['id'] + ':' + arm, case_id=row['id'], arm=arm, record_id=row['record_id'],
            work_id=row['work_id'], input_sha256=r.sha(row['source_text'].encode()), sequence=i + 1,
            status='success', output_token_ids=[2, 256053, 42, 2], translation='example', failure=None, seconds=1.0)
            for arm in ('initialized', 'trained') for i, row in enumerate(rows)]
        r.validate_nllb(run, predictions, rows, 'continue')
        for change in ('missing', 'duplicate', 'source', 'retry', 'step', 'false_success'):
            changed, state = copy.deepcopy(predictions), copy.deepcopy(run)
            if change == 'missing': changed.pop()
            if change == 'duplicate': changed[-1] = copy.deepcopy(changed[0])
            if change == 'source': changed[0]['input_sha256'] = 'bad'
            if change == 'retry': changed[0]['retry_count'] = 1
            if change == 'step': state['step'] = 699
            if change == 'false_success': changed[0]['output_token_ids'] = [2, 256053] + [42] * 511
            with self.subTest(change=change), self.assertRaises(ValueError):
                r.validate_nllb(state, changed, rows, 'continue')
        predictions[0].update(status='failed', output_token_ids=[2, 256053] + [42] * 511,
                              failure='empty_or_cap_or_time_without_EOS')
        r.validate_nllb(run, predictions, rows, 'continue')
        run.update(status='incomplete', step=20)
        r.validate_nllb(run, predictions[:24], rows, 'continue')

    def test_separate_pair_gates_and_frozen_review_coverage(self):
        mapping, packets, reviews = [], {}, {}
        for reviewer in ('A', 'B'):
            packets[reviewer], reviews[reviewer] = [], []
            for condition in r.CONDITIONS:
                for i in range(24):
                    rid, text = reviewer + condition + str(i), 'example'
                    whole = i < 15
                    assessment = 'provisional_whole_translation' if whole else 'constrained_meanings_only'
                    status = 'error' if condition == 'nllb_initialized' and i == 0 else 'success'
                    accepted = condition == 'nllb_trained' and i in (0, 1)
                    judgment = ('accepted' if accepted else 'meaning_error') if whole else 'constrained_only'
                    cats = {k: 'pass' for k in r.prep.CATEGORIES}
                    severity = 'none' if accepted or not whole else 'meaning_error'
                    if whole and not accepted: cats['lexical_meaning'] = 'fail'
                    handling, span = 'no_unknown_span', text
                    if status != 'success':
                        judgment, severity, handling = 'not_assessable', 'uncertain', 'uncertain'
                        cats = {k: 'uncertain' for k in r.prep.CATEGORIES}
                    packet = dict(review_id=rid, source_text=f'source {i}', references={}, assessment=assessment,
                        constraint='', execution_status=status, output_text=text, output_sha256=r.sha(text.encode()))
                    packets[reviewer].append(packet)
                    reviews[reviewer].append(dict(review_id=rid, output_sha256=packet['output_sha256'], judgment=judgment,
                        categories=cats, supported_span_severity=severity, unknown_span_handling=handling,
                        reason='Synthetic test only', output_span=span))
                    mapping.append(dict(reviewer=reviewer, review_id=rid, condition=condition, case_id=f'c{i}',
                        work_id=f'w{i % 4}', assessment=assessment, execution_status=status,
                        output_sha256=packet['output_sha256'], source_sha256=r.sha(packet['source_text'].encode())))
        contract = {'comparison': {'screen': {'both_reviewers_min_net_accepted_gain': 2, 'min_works_with_gains': 2}}}
        completion = dict(training_completed=True, gemma_original_run_completed=True,
            conditions={c: {'usable_execution': c != 'nllb_initialized'} for c in r.CONDITIONS})
        result = r.summarize(mapping, packets, reviews, contract, completion)
        primary, descriptive = [' -> '.join(p) for p in r.PAIRS]
        self.assertIs(result['both_reviewers_screen'][primary], True)
        self.assertIsNone(result['both_reviewers_screen'][descriptive])
        self.assertEqual(result['reviewers']['A']['conditions']['nllb_initialized']['whole_denominator'], 15)
        for alteration in ('missing', 'duplicate', 'hash'):
            changed = copy.deepcopy(reviews)
            if alteration == 'missing': changed['A'].pop()
            elif alteration == 'duplicate': changed['A'][-1] = copy.deepcopy(changed['A'][0])
            else: changed['A'][0]['output_sha256'] = 'bad'
            with self.subTest(alteration=alteration), self.assertRaises(ValueError):
                r.summarize(mapping, packets, changed, contract, completion)
        changed = copy.deepcopy(reviews)
        adverse = next(x for x in changed['B'] if x['review_id'] == 'Bnllb_trained2')
        adverse.update(judgment='critical_error', supported_span_severity='critical_error')
        self.assertIs(r.summarize(mapping, packets, changed, contract, completion)['both_reviewers_screen'][primary], False)
        completion['conditions']['nllb_trained']['usable_execution'] = False
        self.assertIsNone(r.summarize(mapping, packets, reviews, contract, completion)['both_reviewers_screen'][primary])


if __name__ == '__main__': unittest.main()
