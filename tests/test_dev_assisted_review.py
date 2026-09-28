"""Synthetic in-memory tests; no real inference outputs or review ratings written."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts import prepare_blind_dev_assisted as prep
from scripts import score_blind_dev_assisted as scorer


class DevReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract, cls.rows, cls.references, cls.assessments, cls.witnesses = prep.load_contract()

    def fixture(self, family, count=48):
        module, runner_sha = prep.RUNNERS[family]
        gemma = family == 'gemma280'
        schedule = prep.shared.schedule(self.rows)
        ids = [row['id'] + ':' + arm for row, arm in schedule]
        prompts = [{'id': row['id'] + ':' + arm,
                    'messages': prep.shared.messages(row, arm, self.witnesses[row['id']]),
                    'input_tokens': 3, 'rendered_input_ids_sha256': 'e' * 64} for row, arm in schedule]
        identity = {'experiment_id': 'dev-assisted-qualified-20260927', 'runner_sha256': runner_sha,
            'model_id': prep.shared.runtime.MODEL_ID if gemma else prep.qwen.MODEL_ID,
            'model_revision': prep.shared.runtime.REVISION if gemma else prep.qwen.REVISION,
            'inputs_sha256': prep.shared.frozen.INPUTS_SHA256, 'evidence_sha256': prep.shared.EVIDENCE_SHA256,
            'audit_sha256': prep.shared.AUDIT_SHA256, 'local_evaluation_contract_sha256': prep.CONTRACT_SHA,
            'protocol_helper_sha256': prep.shared.PROTOCOL_SHA256, 'seed': 42, 'max_new_tokens': 4096,
            'max_generation_seconds': 1200, 'enable_thinking': False, 'fresh_context_each_case': True,
            'system_instruction': prep.shared.protocol.SYSTEM, 'common_caution': prep.shared.CAUTION,
            'conditions': list(prep.shared.CONDITIONS), 'schedule': ids, 'prompts': prompts,
            'eos_token_ids': prep.shared.protocol.EOS if gemma else prep.qwen.EOS, 'pad_token_id': 0 if gemma else prep.qwen.PAD}
        if gemma:
            identity.update(adapter_step=280, adapter_files=prep.shared.ADAPTER_FILES, train_sha256=prep.shared.TRAIN_SHA256, decoding='greedy')
        else:
            identity.update(adapter=None, source_identity_sha256=prep.qwen.SOURCE_IDENTITY_SHA256,
                shared_helper_sha256=prep.qwen.SHARED_HELPER_SHA256, sampling=prep.qwen.SAMPLING,
                presence_helper_sha256=prep.qwen.PRESENCE_SHA256, presence_penalty=1.5)
        identity_sha = prep.sha(prep.shared.canonical(identity))
        predictions = []
        for index, (row, arm) in enumerate(schedule[:count], 1):
            predictions.append({'id': row['id'] + ':' + arm, 'case_id': row['id'], 'record_id': row['record_id'],
                'work_id': row['work_id'], 'condition': arm, 'sequence': index, 'identity_sha256': identity_sha,
                'input_sha256': prep.sha(row['source_text'].encode('utf-8')), 'status': 'success', 'text': 'synthetic output',
                'elapsed_seconds': 1, 'input_tokens': 3, 'output_tokens': 2, 'rendered_input_ids_sha256': 'e' * 64,
                'hit_output_cap_without_eos': False, 'stop_reason': None})
        complete_cases = sum(sum(p['case_id'] == row['id'] for p in predictions) == 2 for row in self.rows)
        run = {**identity, 'identity_sha256': identity_sha, 'status': 'completed' if count == 48 else 'incomplete',
               'scheduled_outputs': 48, 'attempted_outputs': count, 'completed_outputs': count, 'completed_cases': complete_cases,
               'unattempted_output_ids': ids[count:], 'canary': {'status': 'passed'},
               'case_metadata': [{k: p[k] for k in ('id', 'condition', 'status', 'input_tokens', 'output_tokens')} for p in predictions]}
        prep.validate_run(run, predictions, family, self.rows, self.witnesses)
        return run, predictions, {'run.json': prep.json_bytes(run), 'predictions.jsonl': prep.lines(predictions)}

    def packets(self, gemma_count=48, qwen_count=48):
        loaded = {family: self.fixture(family, count) for family, count in zip(prep.RUNNERS, (gemma_count, qwen_count))}
        files = prep.build_files(loaded, self.contract, self.rows, self.references, self.assessments)
        mapping = prep.decode_lines(files['lead-only/mapping.jsonl'])
        packets = {reviewer: prep.decode_lines(files[f'reviewer-{reviewer}/packet.jsonl']) for reviewer in ('A', 'B')}
        return files, mapping, packets

    def full_completion(self):
        return scorer.comparison_completion({family: self.fixture(family) for family in prep.RUNNERS}, self.rows)

    def ratings(self, packets):
        result = {}
        for reviewer, packet in packets.items():
            result[reviewer] = []
            for row in packet:
                cats = {key: 'pass' for key in prep.CATEGORIES}
                if row['execution_status'] != 'success':
                    judgment, severity, handling, span = 'not_assessable', 'uncertain', 'uncertain', ''
                    cats = {key: 'uncertain' for key in prep.CATEGORIES}
                elif row['assessment'] == 'provisional_whole_translation':
                    judgment, severity, handling, span = 'meaning_error', 'meaning_error', 'no_unknown_span', 'synthetic'
                    cats['lexical_meaning'] = 'fail'
                else:
                    judgment, severity, handling, span = 'constrained_only', 'none', 'appropriately_uncertain', ''
                    cats['source_uncertainty'] = 'uncertain'
                result[reviewer].append({'review_id': row['review_id'], 'output_sha256': row['output_sha256'],
                    'judgment': judgment, 'categories': cats, 'supported_span_severity': severity,
                    'unknown_span_handling': handling, 'reason': 'Synthetic fixture only; no actual assessment.', 'output_span': span})
        return result

    def change(self, mapping, ratings, reviewer, condition, cid, judgment):
        rid = next(m['review_id'] for m in mapping if (m['reviewer'], m['condition'], m['case_id']) == (reviewer, condition, cid))
        row = next(r for r in ratings[reviewer] if r['review_id'] == rid)
        row['judgment'] = judgment
        row['categories'] = {key: 'pass' for key in prep.CATEGORIES}
        row['supported_span_severity'] = 'none' if judgment == 'accepted' else judgment
        row['unknown_span_handling'] = 'no_unknown_span'
        row['output_span'] = '' if judgment == 'accepted' else 'synthetic'
        if judgment != 'accepted': row['categories']['lexical_meaning'] = 'fail'
        return row

    def test_run_identity_first_attempt_missing_and_retry_rejection(self):
        for family in prep.RUNNERS:
            run, predictions, _ = self.fixture(family, 7)
            self.assertEqual(len(run['unattempted_output_ids']), 41)
            for mutate in ('duplicate', 'skip', 'retry', 'hash', 'order', 'condition', 'source'):
                r, p = copy.deepcopy(run), copy.deepcopy(predictions)
                if mutate == 'duplicate': p.append(p[0])
                elif mutate == 'skip': p.pop(0)
                elif mutate == 'retry': p[0]['attempt_number'] = 2
                elif mutate == 'hash': r['identity_sha256'] = '0' * 64
                elif mutate == 'order': p[0], p[1] = p[1], p[0]
                elif mutate == 'condition': p[0]['condition'] = 'wrong'
                else: p[0]['input_sha256'] = '0' * 64
                with self.subTest(family=family, mutate=mutate), self.assertRaises(ValueError):
                    prep.validate_run(r, p, family, self.rows, self.witnesses)

    def test_blinding_ids_hashes_qualified_references_and_duplicate_retention(self):
        files, mapping, packets = self.packets()
        self.assertEqual(len({m['review_id'] for m in mapping}), 192)
        self.assertTrue({p['review_id'] for p in packets['A']}.isdisjoint(p['review_id'] for p in packets['B']))
        self.assertEqual([len(packets[r]) for r in ('A', 'B')], [96, 96])
        self.assertNotEqual([p['source_text'] for p in packets['A']], [p['source_text'] for p in packets['B']])
        for reviewer, packet in packets.items():
            for p in packet:
                self.assertEqual(set(p), prep.PACKET_FIELDS)
                self.assertEqual(p['output_sha256'], prep.sha(b'synthetic output'))
                self.assertNotIn('QUALITYDEV1-', json.dumps(p))
                for secret in (*prep.CONDITIONS, 'google/gemma', 'Qwen/Qwen', 'support_examples', 'historical_scores'):
                    self.assertNotIn(secret, json.dumps(p))
            self.assertEqual(len({p['output_sha256'] for p in packet}), 1)  # Identical texts are retained independently.
        self.assertEqual(sum('en' in p['references']['translations'] for p in packets['A']), 16)
        self.assertEqual(files['lead-only/raw/gemma280/predictions.jsonl'], self.fixture('gemma280')[2]['predictions.jsonl'])
        self.assertEqual(files, self.packets()[0])

    def test_unattempted_is_not_generated_and_denominators_stay_fixed(self):
        _, mapping, packets = self.packets(gemma_count=7, qwen_count=0)
        self.assertEqual(sum(p['execution_status'] == 'unattempted' for p in packets['A']), 89)
        self.assertTrue(all(p['output_text'] == '' for p in packets['A'] if p['execution_status'] == 'unattempted'))
        ratings = self.ratings(packets)
        result = scorer.summarize(mapping, packets, ratings, self.contract)
        for reviewer in result['reviewers'].values():
            for report in reviewer['conditions'].values():
                self.assertEqual((report['total_cases'], report['whole_denominator'], report['constrained_denominator']), (24, 15, 9))
                self.assertEqual({w: v['whole_denominator'] for w, v in report['by_work'].items()}, {'parsig:103': 4, 'parsig:112': 5, 'parsig:138': 4, 'parsig:517': 2})
        self.assertFalse(any(result['both_reviewers_screen'].values()))

    def test_review_schema_hash_spans_and_false_acceptance_rejected(self):
        _, mapping, packets = self.packets()
        original = self.ratings(packets)['A']
        for mode in ('duplicate', 'missing', 'hash', 'extra', 'span', 'accepted_fail', 'constrained_accepted'):
            reviews = copy.deepcopy(original)
            if mode == 'duplicate': reviews.append(reviews[0])
            elif mode == 'missing': reviews.pop()
            elif mode == 'hash': reviews[0]['output_sha256'] = '0' * 64
            elif mode == 'extra': reviews[0]['condition'] = 'leaked'
            elif mode == 'span': reviews[0]['output_span'] = 'fabricated span'
            else:
                target = next(r for r in reviews if r['judgment'] == ('constrained_only' if mode == 'constrained_accepted' else 'meaning_error'))
                target['judgment'] = 'accepted'
            with self.subTest(mode=mode), self.assertRaises(ValueError): scorer.validate_reviews(packets['A'], reviews)

    def test_four_pairs_gain_screen_and_no_pooled_reviewers(self):
        _, mapping, packets = self.packets()
        reviews = self.ratings(packets)
        for cid in ('QUALITYDEV1-002', 'QUALITYDEV1-007'):
            self.change(mapping, reviews, 'A', 'gemma280_assisted', cid, 'accepted')
        result = scorer.summarize(mapping, packets, reviews, self.contract, self.full_completion())
        pair = 'gemma280_plain -> gemma280_assisted'
        self.assertEqual(len(result['both_reviewers_screen']), 4)
        self.assertTrue(result['reviewers']['A']['paired'][pair]['screen_pass'])
        self.assertFalse(result['reviewers']['B']['paired'][pair]['screen_pass'])
        self.assertFalse(result['both_reviewers_screen'][pair])
        for cid in ('QUALITYDEV1-002', 'QUALITYDEV1-007'):
            self.change(mapping, reviews, 'B', 'gemma280_assisted', cid, 'accepted')
        result = scorer.summarize(mapping, packets, reviews, self.contract, self.full_completion())
        self.assertTrue(result['both_reviewers_screen'][pair])
        self.assertEqual(result['reviewers']['A']['paired'][pair]['net_accepted_change'], 2)
        self.assertEqual(len(result['reviewers']['A']['paired'][pair]['cases']), 24)
        self.assertEqual(result['reviewers']['A']['conditions']['gemma280_assisted']['whole_counts']['accepted'], 2)

    def test_critical_regressions_and_new_overconfidence_block_screen(self):
        _, mapping, packets = self.packets()
        original = self.ratings(packets)
        for reviewer in ('A', 'B'):
            for cid in ('QUALITYDEV1-002', 'QUALITYDEV1-007', 'QUALITYDEV1-008'):
                self.change(mapping, original, reviewer, 'gemma280_assisted', cid, 'accepted')
        pair = 'gemma280_plain -> gemma280_assisted'
        for mode in ('accepted_to_critical', 'constrained_critical', 'overconfident'):
            reviews = copy.deepcopy(original)
            if mode == 'accepted_to_critical':
                self.change(mapping, reviews, 'A', 'gemma280_plain', 'QUALITYDEV1-003', 'accepted')
                self.change(mapping, reviews, 'A', 'gemma280_assisted', 'QUALITYDEV1-003', 'critical_error')
            else:
                rid = next(m['review_id'] for m in mapping if (m['reviewer'], m['condition'], m['case_id']) == ('A', 'gemma280_assisted', 'QUALITYDEV1-001'))
                review = next(r for r in reviews['A'] if r['review_id'] == rid)
                review['output_span'] = 'synthetic'
                if mode == 'constrained_critical':
                    review['supported_span_severity'] = 'critical_error'; review['categories']['lexical_meaning'] = 'fail'
                else:
                    review['unknown_span_handling'] = 'overconfident'; review['categories']['source_uncertainty'] = 'fail'
            result = scorer.summarize(mapping, packets, reviews, self.contract, self.full_completion())
            self.assertFalse(result['both_reviewers_screen'][pair])

    def test_work_with_canceling_gain_and_loss_still_counts_as_a_gain_work(self):
        _, mapping, packets = self.packets()
        reviews = self.ratings(packets)
        for reviewer in ('A', 'B'):
            for cid in ('QUALITYDEV1-002', 'QUALITYDEV1-007', 'QUALITYDEV1-008'):
                self.change(mapping, reviews, reviewer, 'gemma280_assisted', cid, 'accepted')
            self.change(mapping, reviews, reviewer, 'gemma280_plain', 'QUALITYDEV1-003', 'accepted')
        result = scorer.summarize(mapping, packets, reviews, self.contract, self.full_completion())
        pair = 'gemma280_plain -> gemma280_assisted'
        self.assertTrue(result['both_reviewers_screen'][pair])
        for reviewer in ('A', 'B'):
            value = result['reviewers'][reviewer]['paired'][pair]
            self.assertEqual(value['net_accepted_change'], 2)
            self.assertEqual(value['work_net_accepted_changes']['parsig:103'], 0)
            self.assertEqual(value['works_with_newly_accepted'], ['parsig:103', 'parsig:112'])

    def test_all_screens_inconclusive_for_final_failure_or_unfinished_other_run(self):
        for mode in ('gemma_error', 'gemma_timeout', 'qwen_error', 'qwen_missing', 'qwen_running'):
            with self.subTest(mode=mode):
                loaded = {family: self.fixture(family) for family in prep.RUNNERS}
                family = 'gemma280' if mode.startswith('gemma') else 'qwen36_27b'
                if mode == 'qwen_missing':
                    loaded[family] = self.fixture(family, 47)
                else:
                    run, predictions, _ = loaded[family]
                    if mode == 'qwen_running':
                        run['status'] = 'running'
                    else:
                        status = 'timeout' if mode.endswith('timeout') else 'error'
                        predictions[-1]['status'] = status
                        run['case_metadata'][-1]['status'] = status
                        run.update(status='incomplete', completed_outputs=47, completed_cases=23)
                    prep.validate_run(run, predictions, family, self.rows, self.witnesses)
                    loaded[family] = run, predictions, {'run.json': prep.json_bytes(run), 'predictions.jsonl': prep.lines(predictions)}
                files = prep.build_files(loaded, self.contract, self.rows, self.references, self.assessments)
                mapping = prep.decode_lines(files['lead-only/mapping.jsonl'])
                packets = {r: prep.decode_lines(files[f'reviewer-{r}/packet.jsonl']) for r in ('A', 'B')}
                reviews = self.ratings(packets)
                for reviewer in ('A', 'B'):
                    for cid in ('QUALITYDEV1-002', 'QUALITYDEV1-007'):
                        self.change(mapping, reviews, reviewer, 'gemma280_assisted', cid, 'accepted')
                result = scorer.summarize(mapping, packets, reviews, self.contract, scorer.comparison_completion(loaded, self.rows))
                self.assertEqual(result['screen_status'], 'inconclusive')
                self.assertTrue(all(value is None for value in result['both_reviewers_screen'].values()))
                for reviewer in ('A', 'B'):
                    for value in result['reviewers'][reviewer]['paired'].values():
                        self.assertEqual(value['screen_status'], 'inconclusive')
                        self.assertIsNone(value['screen_pass'])
                    report = result['reviewers'][reviewer]['conditions']['gemma280_assisted']
                    self.assertEqual(report['whole_counts']['accepted'], 2)
                    self.assertEqual((report['whole_denominator'], report['constrained_denominator']), (15, 9))

    def test_preparation_and_scoring_require_fresh_directories(self):
        with patch.object(Path, 'exists', return_value=True):
            with self.assertRaisesRegex(ValueError, 'fresh'): prep.prepare('unused', 'unused', 'unused')
            with self.assertRaisesRegex(ValueError, 'fresh'): scorer.score('unused', 'unused', 'unused', 'unused')
        with patch.object(Path, 'exists', return_value=False):
            with self.assertRaisesRegex(ValueError, 'benchmarks'):
                prep.write_fresh(prep.ROOT / 'benchmarks/forbidden-output', {})

    def test_execution_outcomes_stay_visible_without_semantic_passes(self):
        for status, text in (('error', ''), ('timeout', 'partial synthetic output'), ('abstain', '[UNRESOLVED]')):
            run, predictions, _ = self.fixture('gemma280', 3)
            predictions[-1].update(status=status, text=text)
            run['case_metadata'][-1]['status'] = status
            if status != 'abstain': run['completed_outputs'] -= 1
            prep.validate_run(run, predictions, 'gemma280', self.rows, self.witnesses)
            loaded = {'gemma280': (run, predictions, {'run.json': prep.json_bytes(run), 'predictions.jsonl': prep.lines(predictions)}),
                      'qwen36_27b': self.fixture('qwen36_27b', 0)}
            files = prep.build_files(loaded, self.contract, self.rows, self.references, self.assessments)
            mapping = prep.decode_lines(files['lead-only/mapping.jsonl'])
            packets = {r: prep.decode_lines(files[f'reviewer-{r}/packet.jsonl']) for r in ('A', 'B')}
            result = scorer.summarize(mapping, packets, self.ratings(packets), self.contract)
            condition = 'gemma280_' + predictions[-1]['condition']
            self.assertEqual(result['reviewers']['A']['conditions'][condition]['whole_counts'][status], 1)
            self.assertEqual(result['reviewers']['A']['conditions'][condition]['whole_denominator'], 15)

    def test_full_conversion_scoring_and_packet_tamper_in_memory(self):
        loaded = {family: self.fixture(family) for family in prep.RUNNERS}
        files = prep.build_files(loaded, self.contract, self.rows, self.references, self.assessments)
        packets = {r: prep.decode_lines(files[f'reviewer-{r}/packet.jsonl']) for r in ('A', 'B')}
        ratings = self.ratings(packets)
        memory = {str((prep.ROOT / 'synthetic-packet' / name).resolve()): data for name, data in files.items()}
        memory.update({str((prep.ROOT / 'synthetic-packet' / f'reviewer-{r}/reviews.jsonl').resolve()): prep.lines(ratings[r]) for r in ('A', 'B')})
        original_read = Path.read_bytes
        def read(path):
            return memory[str(path.resolve())] if str(path.resolve()) in memory else original_read(path)
        args = (prep.ROOT / 'synthetic-packet', 'unused-gemma', 'unused-qwen', prep.ROOT / 'synthetic-score')
        with patch.object(Path, 'read_bytes', autospec=True, side_effect=read), patch.object(Path, 'exists', return_value=False), \
                patch.object(prep, 'load_contract', return_value=(self.contract, self.rows, self.references, self.assessments, self.witnesses)), \
                patch.object(prep, 'load_run', side_effect=lambda directory, family, rows, witnesses: loaded[family]), \
                patch.object(prep, 'write_fresh') as write:
            result = scorer.score(*args)
            self.assertEqual(result['blind_review_freeze']['A']['rows'], 96)
            write.assert_called_once()
            self.assertIn('comparison.json', write.call_args.args[1])
            memory[str((args[0] / 'reviewer-A/packet.jsonl').resolve())] += b' '
            with self.assertRaisesRegex(ValueError, 'changed'): scorer.score(*args)
            self.assertEqual(write.call_count, 1, 'No output mutation may precede all validation')


if __name__ == '__main__':
    unittest.main()
