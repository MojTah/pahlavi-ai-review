"""Synthetic review fixtures only: no real model outputs or semantic ratings."""
import copy
from contextlib import nullcontext
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import uuid

from scripts import review_train_recall as review


class RecallReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.material = review.load_material()

    def fixture(self, count=40, active=False):
        rows, refs, scopes, original_audit, consumed = self.material
        audit = copy.deepcopy(original_audit)
        audit['rows'] = []
        prompts, token_map = [], {}
        ordered = review.runner.schedule(rows)
        for index, (row, condition) in enumerate(ordered):
            ids = [7, index + 20, 106]
            rid = row['id'] + ':' + condition
            digest = review.sha(review.runner.qualified.canonical(ids))
            audit['rows'].append({'id': row['id'], 'condition': condition, 'input_tokens': len(ids), 'input_ids_sha256': digest})
            token_map[rid] = {'input_tokens': len(ids), 'input_ids_sha256': digest}
            messages = review.runner.frozen.messages(row, condition)
            prompts.append({'id': rid, 'record_id': row['record_id'], 'work_id': row['work_id'],
                'source_sha256': review.sha(row['source_text'].encode()), 'messages': messages,
                'messages_sha256': review.sha(review.runner.qualified.canonical(messages)), 'input_tokens': len(ids),
                'input_token_ids': ids, 'rendered_input_ids_sha256': digest})
        r = review.runner
        identity = {'experiment_id': 'qualified-train-recall', 'diagnostic_scope': 'seen TRAIN recall; not generalization',
            'inputs_sha256': r.INPUTS_SHA256, 'train_sha256': r.qualified.TRAIN_SHA256,
            'model_id': r.runtime.MODEL_ID, 'model_revision': r.runtime.REVISION,
            'base_files': {**audit['tokenizer_files'], **{name: 'a' * 64 for name in
                ('config.json', 'generation_config.json', 'model.safetensors.index.json', 'model-00001.safetensors')}},
            'adapter_files': r.qualified.ADAPTER_FILES, 'adapter_metadata': r.qualified.ADAPTER_METADATA,
            'adapter_step': 280, 'adapter_manifest_sha256': r.qualified.ADAPTER_MANIFEST_SHA256,
            'tokenizer_files': audit['tokenizer_files'], 'runtime': {'packages': r.runtime.PINS,
                'runtime_sha256': review.sha(Path(r.runtime.__file__).read_bytes()), 'system': 'Linux', 'machine': 'x86_64',
                'python': '3.12.13', 'gpu': {'name': 'SYNTHETIC A100', 'bytes': 80 * 1024**3}},
            'runner_sha256': review.RUNNER_SHA, 'local_token_audit_sha256': r.TOKEN_AUDIT_SHA256,
            'expected_token_map_sha256': review.sha(r.qualified.canonical(token_map)),
            'actual_token_map_sha256': review.sha(r.qualified.canonical(token_map)), 'helper_sha256': r.HELPER_SHA256,
            'bundle_manifest_sha256': 'a' * 64, 'schedule': [p['id'] for p in prompts],
            'schedule_method': 'frozen parent order; alternate prompt order by zero-based parent index',
            'seed': 42, 'seed_policy': 'set once before the schedule; greedy generation', 'conditions': list(r.CONDITIONS),
            'max_new_tokens': 4096, 'max_generation_seconds': 1200, 'eos_token_ids': [1, 106, 50], 'pad_token_id': 0,
            'num_beams': 1, 'decoding': 'greedy', 'enable_thinking': False, 'fresh_context_each_case': True,
            'deadline_utc': '2999-01-01T00:00:00Z', 'scoring_performed': False, 'training_performed': False, 'prompts': prompts}
        identity_sha = review.sha(r.qualified.canonical(identity))
        predictions = []
        for index, (row, condition) in enumerate(ordered[:count]):
            p = prompts[index]
            predictions.append({'id': p['id'], 'case_id': row['id'], 'record_id': row['record_id'], 'work_id': row['work_id'],
                'condition': condition, 'sequence': index + 1, 'identity_sha256': identity_sha, 'input_sha256': p['source_sha256'],
                'input_tokens': 3, 'rendered_input_ids_sha256': p['rendered_input_ids_sha256'],
                'output_token_ids': [42, 106], 'output_tokens': 2, 'output_token_ids_sha256': review.sha(r.qualified.canonical([42, 106])),
                'text': 'SYNTHETIC OUTPUT', 'status': 'success', 'elapsed_seconds': 1.0,
                'hit_output_cap_without_eos': False, 'stop_reason': None})
        attempted = count + int(active)
        run = {**identity, 'identity_sha256': identity_sha, 'status': 'completed' if count == 40 else 'running',
            'scheduled_outputs': 40, 'attempted_outputs': attempted, 'recorded_outputs': count,
            'active_output_id': prompts[count]['id'] if active else None, 'completed_outputs': count, 'completed_cases': count // 2,
            'unattempted_output_ids': identity['schedule'][attempted:],
            'case_metadata': [{k: p[k] for k in ('id', 'condition', 'status', 'input_tokens', 'output_tokens')} for p in predictions],
            'canary': {'status': 'passed', 'id': prompts[0]['id'], 'input_tokens': 3,
                'rendered_input_ids_sha256': prompts[0]['rendered_input_ids_sha256'], 'experimental_attempts': 0, 'output_generated': False}}
        return run, predictions, (rows, refs, scopes, audit, consumed)

    @staticmethod
    def ratings(packet):
        result = []
        for item in packet:
            success = item['execution_status'] == 'success'
            result.append({'review_id': item['review_id'], 'output_sha256': item['output_sha256'],
                'judgment': 'uncertain' if success else 'not_assessable',
                'categories': {key: 'uncertain' for key in review.CATEGORIES}, 'supported_span_severity': 'uncertain',
                'unknown_span_handling': 'uncertain', 'reason': 'Synthetic schema fixture; no semantic judgment.',
                'output_span': item['output_text'], 'local_details': [{'scope_id': s['scope_id'], 'status': 'unassessable',
                    'reason': 'Synthetic scope fixture; no semantic judgment.', 'output_span': ''} for s in item['scopes']]})
        return result

    def test_frozen_material_and_synthetic_prepare_score_roundtrip(self):
        self.assertEqual((len(self.material[0]), sum(map(len, self.material[2].values()))), (20, 28))
        run, predictions, material = self.fixture()
        scratch = review.ROOT / 'resources/local/train-recall-packet-tmp'
        scratch.mkdir(parents=True, exist_ok=True)
        # Windows sandbox ACLs reject tempfile's private-mode directory; ordinary mkdir inherits the workspace ACL.
        with nullcontext(scratch / ('fixture-' + uuid.uuid4().hex)) as base:
            base.mkdir()
            rp, pp = base / 'run.json', base / 'predictions.jsonl'
            rp.write_bytes(review.json_bytes(run)); pp.write_bytes(review.lines(predictions))
            with patch.object(review, 'load_material', return_value=material):
                review.prepare(rp, pp, base / 'packet')
                packets = {who: review.decode_lines((base / 'packet' / f'reviewer-{who}/packet.jsonl').read_bytes()) for who in review.SEEDS}
                self.assertTrue(set(x['review_id'] for x in packets['A']).isdisjoint(x['review_id'] for x in packets['B']))
                for who, packet in packets.items():
                    self.assertEqual(len(packet), 40)
                    self.assertEqual(sum(len(x['scopes']) for x in packet), 56)
                    exposed = json.dumps(packet, ensure_ascii=False)
                    for secret in ('TRAINRECALL1-', 'parsig:', 'GROUNDEDLEX1-', '/root/', 'gemma-4', 'historical_scores'):
                        self.assertNotIn(secret, exposed)
                    (base / f'{who}.jsonl').write_bytes(review.lines(self.ratings(packet)))
                summary = review.score(base / 'packet', base / 'A.jsonl', base / 'B.jsonl', base / 'summary')
                for who in review.SEEDS:
                    for condition in review.runner.CONDITIONS:
                        info = summary['reviewers'][who]['conditions'][condition]
                        self.assertEqual(info['denominator'], 20)
                        self.assertEqual(info['meaning_and_execution_counts'], {'uncertain': 20})
                        self.assertEqual(sum(v['denominator'] for v in info['by_work'].values()), 20)
                    self.assertEqual(summary['reviewers'][who]['paired_transitions'], {'uncertain -> uncertain': 20})
                self.assertFalse(summary['scopes_are_merit'])
                with self.assertRaisesRegex(ValueError, 'fresh'): review.prepare(rp, pp, base / 'packet')

    def test_run_review_corruption_and_partial_denominators(self):
        run, predictions, material = self.fixture(count=1, active=True)
        raw = {'run.json': review.json_bytes(run), 'predictions.jsonl': review.lines(predictions)}
        files = review.build_files(run, predictions, raw, material)
        packets = {who: review.decode_lines(files[f'reviewer-{who}/packet.jsonl']) for who in review.SEEDS}
        ratings = {who: self.ratings(packet) for who, packet in packets.items()}
        for packet in packets.values():
            self.assertEqual(sum(p['execution_status'] == 'interrupted' for p in packet), 1)
            self.assertEqual(sum(p['execution_status'] == 'unattempted' for p in packet), 38)
        summary = review.summarize(review.decode_lines(files['lead-only/mapping.jsonl']), packets, ratings,
            json.loads(files['lead-only/provenance.json'])['completion'])
        self.assertFalse(summary['execution_completion']['complete'])
        for condition in review.runner.CONDITIONS:
            self.assertEqual(summary['reviewers']['A']['conditions'][condition]['denominator'], 20)
        stopped, failed, stopped_material = self.fixture(count=2)
        failed[-1].update(status='error', text='', output_tokens=0, output_token_ids=[],
            output_token_ids_sha256=review.sha(review.runner.qualified.canonical([])))
        stopped.update(status='incomplete', completed_outputs=1, completed_cases=0)
        stopped['case_metadata'][-1].update(status='error', output_tokens=0)
        self.assertFalse(review.validate_run(stopped, failed, stopped_material[0], stopped_material[3])['complete'])
        for mutate in (lambda p: p.append(copy.deepcopy(p[0])), lambda p: p[0].update(sequence=2),
                       lambda p: p[0].update(attempt_number=2), lambda p: p[0].update(output_token_ids_sha256='0' * 64)):
            changed = copy.deepcopy(predictions); mutate(changed)
            with self.assertRaises(ValueError): review.validate_run(run, changed, material[0], material[3])
        for mutate in (lambda r: r.update(status='completed'), lambda r: r['prompts'][0]['messages'][0].update(content='changed'),
                       lambda r: r['prompts'][0]['input_token_ids'].append(8)):
            changed = copy.deepcopy(run); mutate(changed)
            with self.assertRaises(ValueError): review.validate_run(changed, predictions, material[0], material[3])
        for mutate in (lambda r: r.pop(), lambda r: r[0].update(output_sha256='0' * 64),
                       lambda r: r[0]['categories'].pop('names'), lambda r: r[0].update(output_span='not in output'),
                       lambda r: r[0]['local_details'].pop(), lambda r: r[0]['local_details'][0].update(output_span='invented'),
                       lambda r: r[0]['local_details'][0].update(scope_id='leaked-parent')):
            changed = copy.deepcopy(ratings['A']); mutate(changed)
            with self.assertRaises(ValueError): review.validate_reviews(packets['A'], changed)


if __name__ == '__main__':
    unittest.main()
