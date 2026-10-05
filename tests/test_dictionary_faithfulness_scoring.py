"""Synthetic outputs/ratings only; real exposed input/reference byte contracts."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('dictionary_faithfulness_scoring', ROOT / 'experiments/dictionary-faithfulness-20261005/score.py')
scoring = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scoring)


class FaithfulnessScoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.preview, cls.settings, _ = scoring.load_preview()
        cls.input_raw = (ROOT / 'resources/local/dictionary-faithfulness-20261005/model-inputs.jsonl').read_bytes()
        cls.inputs = scoring.decode_lines(cls.input_raw)
        cls.contract, cls.cases, cls.references, cls.assessments, cls.works = scoring.exposed_cases()
        cls.tokenizer = scoring.verified_tokenizer()

    def setUp(self):
        # Windows restricted execution cannot reopen TemporaryDirectory's 0700
        # directory. Use a fresh project-local fixture and preserve it for audit.
        self.root = ROOT / 'resources/local' / ('dictionary-faithfulness-scoring-' + uuid.uuid4().hex)
        self.root.mkdir(parents=True)
        self.fixture_parent = self.root

    def closed(self, kind='success', remote=True):
        root = self.root / 'final'
        (root / 'evaluation').mkdir(parents=True)
        identity = dict(protocol='dictionary-faithfulness-v1', run_id=self.preview['run_id'], inputs_sha256=self.settings['inputs_sha256'],
            script_hashes=self.settings['script_hashes'], base_files={}, model_id=scoring.runtime.MODEL_ID,
            revision=scoring.runtime.REVISION, adapter_files=scoring.prep.shared.ADAPTER_FILES, adapter_step=280, environment={},
            precision='bf16_base_fp32_retained_lora', attention='eager', enable_thinking=False, max_new_tokens=4096,
            max_generation_seconds=90, context_limit=12288, seed=42, do_sample=False, eos_token_ids=[1,106,50], pad_token_id=0,
            num_beams=1, fresh_context_each_output=True, optimizer_updates=0, scoring_performed=False, expert_adjudicated=False,
            deadline_utc='2026-10-05T16:00:00+00:00', decode_controls=self.settings['decode_controls'],
            timing_contract=self.settings['timing_contract'], input_cap_tokens=8192, no_truncation=True, first_attempt_only=True,
            compute_seconds=6600, internal_seconds=7020, native_timeout_minutes=120, case_ids=list(self.works),
            case_work_bindings=self.works, timeout_or_output_cap_primary_inconclusive=True,
            contract_sha256=self.settings['contract_sha256'], historical_ab_contract_unchanged=True)
        identity_sha = scoring.sha(scoring.canonical(identity))
        order = scoring.hf_component.dictionary_schedule()
        inputs = {row['id']: row for row in scoring.decode_lines(self.input_raw)}
        predictions = []
        for index, pid in enumerate(order):
            source = inputs[pid]
            status = 'abstain' if kind == 'abstain' else 'error' if kind == 'failed_a' and pid.endswith(':A') else 'success'
            text = '[UNRESOLVED]' if status == 'abstain' else 'synthetic output ' + pid
            output_ids = self.tokenizer.encode(text, add_special_tokens=False) + [1]
            predictions.append(dict(id=pid, case_id=source['case_id'], condition=source['arm'], arm=source['arm'],
                sequence=index + 1, identity_sha256=identity_sha, status=status, text=text, elapsed_seconds=1.0,
                output_token_ids=output_ids, output_tokens=len(output_ids), output_sha256=scoring.sha(text.encode()),
                hit_output_cap_without_eos=False, stop_reason=None, messages=source['messages'],
                messages_sha256=scoring.sha(scoring.canonical(source['messages'])), work_id=source['work_id'],
                source_sha256=source['source_sha256'], input_tokens=source['input_tokens'],
                rendered_input_ids_sha256=source['input_ids_sha256'], rendered_sha256=source['rendered_text_sha256'],
                model_call_started=True, adapter_sha256=scoring.prep.shared.ADAPTER_FILES['adapter_model.safetensors'],
                primary_comparison_eligible=status in {'success', 'abstain'}))
        if kind == 'incomplete':
            predictions = predictions[:14]
        n = len(predictions)
        longest = max(self.inputs, key=lambda row: row['input_tokens'])
        run = dict(identity, identity_sha256=identity_sha, schedule=order, scheduled_outputs=30,
            attempted_outputs=n, recorded_outputs=n, model_calls_started=n, active_output_id=None,
            unattempted_output_ids=order[n:], status='incomplete' if n < 30 else 'completed_with_errors' if kind == 'failed_a' else 'completed',
            adapter_unchanged_after_inference=True, successful_outputs=sum(row['status'] in {'success','abstain'} for row in predictions),
            canary=dict(status='passed', id=longest['id'], input_tokens=longest['input_tokens'],
                rendered_input_ids_sha256=longest['input_ids_sha256'], output_generated=False, experimental_attempts=0))
        files = {'evaluation/run.json': scoring.encode(run), 'evaluation/predictions.jsonl': scoring.lines(predictions),
                 'model-inputs.jsonl': self.input_raw, 'contract.json': scoring.CONTRACT.read_bytes(), 'driver.log': b'synthetic driver log\n',
                 'snapshots/attempt-01/result.json': scoring.encode(predictions[0])}
        for name, raw in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        self.reclose(root)
        receipt = self.root / 'recovery-receipt.json'
        self.receipt(root, receipt, remote)
        return root, receipt

    def reclose(self, root):
        files = {path.relative_to(root).as_posix(): {'sha256': scoring.sha(path.read_bytes()), 'bytes': path.stat().st_size}
                 for path in root.rglob('*') if path.is_file() and path.name != 'manifest.json'}
        manifest = dict(self.settings, schema_version=1, files=files, training_performed=False,
            optimizer_updates=0, remote_inventory_verified=False, quality_validated=False)
        # Match the real exporter: output_prefix belongs to the recovery receipt.
        if getattr(self, 'manifest_prefix', False) is not True:
            manifest.pop('output_prefix')
        (root / 'manifest.json').write_bytes(scoring.encode(manifest))

    def receipt(self, root, path, remote=True):
        manifest_raw = (root / 'manifest.json').read_bytes()
        manifest = scoring.decode(manifest_raw)
        data = dict(schema='dictionary-faithfulness-recovery-v1', run_id=self.preview['run_id'], output_prefix=self.preview['output_prefix'],
            manifest_sha256=scoring.sha(manifest_raw), independent_remote_verified=remote,
            objects={'manifest.json': {'sha256': scoring.sha(manifest_raw), 'bytes': len(manifest_raw)}, **manifest['files']})
        path.write_bytes(scoring.encode(data))

    def packets(self, root, receipt):
        packet = self.root / 'packets'
        result = scoring.prepare(root, receipt, packet)
        return packet, result

    def ratings(self, packet, gains=(), losses=(), reviewer='AB', abstain=False, criticals=()):
        mapping = scoring.decode_lines((packet / 'lead-only/mapping.jsonl').read_bytes())
        for rater in reviewer:
            selected = {row['review_id']: row for row in mapping if row['reviewer'] == rater}
            ratings = []
            for output in scoring.decode_lines((packet / f'reviewer-{rater}/packet.jsonl').read_bytes()):
                item = selected[output['review_id']]
                judgment = 'meaning_error'
                if item['arm'] == 'B' and item['case_id'] in gains:
                    judgment = 'accepted'
                if item['case_id'] in losses:
                    judgment = 'accepted' if item['arm'] == 'A' else 'critical_error'
                if item['arm'] == 'B' and item['case_id'] in criticals:
                    judgment = 'critical_error'
                not_assessable = abstain or output['execution_status'] == 'abstain'
                if not_assessable:
                    judgment = 'not_assessable'
                categories = {cat: 'uncertain' if not_assessable else 'pass' for cat in scoring.prep.CATEGORIES}
                if judgment in {'meaning_error','critical_error'}:
                    categories['lexical_meaning'] = 'fail'
                ratings.append(dict(review_id=output['review_id'], output_sha256=output['output_sha256'], judgment=judgment,
                    categories=categories, supported_span_severity='uncertain' if not_assessable else 'none' if judgment == 'accepted' else judgment,
                    unknown_span_handling='uncertain' if not_assessable else 'no_unknown_span',
                    reason='Synthetic fixture finding for source ' + item['case_id'] + ' and its exact output.',
                    output_span='' if judgment in {'accepted','not_assessable'} else output['output_text']))
            (packet / f'reviewer-{rater}/reviews.jsonl').write_bytes(scoring.lines(ratings))

    def score(self, packet, root, receipt):
        return scoring.score(packet, root, receipt, self.root / ('score-' + uuid.uuid4().hex))

    def test_native_export_without_transport_prefix_preserves_receipt_binding(self):
        root, receipt = self.closed()
        self.assertNotIn('output_prefix', scoring.decode((root / 'manifest.json').read_bytes()))
        self.assertTrue(scoring.load_closed(root, receipt)['receipt']['independent_remote_verified'])
        changed = scoring.decode(receipt.read_bytes())
        changed['output_prefix'] += '-different'
        receipt.write_bytes(scoring.encode(changed))
        with self.assertRaisesRegex(ValueError, 'Recovery receipt byte pins or identity differ'):
            scoring.load_closed(root, receipt)

    def test_explicit_conflicting_manifest_prefix_is_rejected(self):
        root, receipt = self.closed()
        manifest = scoring.decode((root / 'manifest.json').read_bytes())
        manifest['output_prefix'] = self.preview['output_prefix'] + '-different'
        (root / 'manifest.json').write_bytes(scoring.encode(manifest))
        self.receipt(root, receipt)
        with self.assertRaisesRegex(ValueError, 'Manifest preview identity differs: output_prefix'):
            scoring.load_closed(root, receipt)

    def test_complete_two_work_gain_each_rater_and_reference_preservation(self):
        root, receipt = self.closed()
        packet, prepared = self.packets(root, receipt)
        self.assertTrue(prepared['primary_eligible'])
        outputs = scoring.decode_lines((packet / 'reviewer-A/packet.jsonl').read_bytes())
        self.assertEqual(len(outputs), 30)
        self.assertTrue(all(set(row) == scoring.prep.PACKET_FIELDS for row in outputs))
        self.assertEqual(outputs[0]['references'], {key: self.references[next(c['id'] for c in self.cases if c['source_text'] == outputs[0]['source_text'])][key]
            for key in ('translations','edition','notes','reference_screen','expert_adjudicated')})
        self.ratings(packet, gains=('QUALITYDEV1-002','QUALITYDEV1-007'))
        result = self.score(packet, root, receipt)
        self.assertTrue(result['semantic_continuation'])
        for rater in 'AB':
            self.assertEqual(result['reviewers'][rater]['net_accepted_change'], 2)
            self.assertEqual(result['reviewers'][rater]['works_with_newly_accepted'], ['parsig:103','parsig:112'])
        self.assertEqual(set(result['review_freeze']), {'A','B'})

    def test_immutable_fresh_and_cli_prepare(self):
        root, receipt = self.closed()
        output = self.root / 'cli-packets'
        command = [sys.executable, '-B', '-X', 'utf8', str(scoring.PREVIEW.with_name('score.py')), 'prepare', str(root), str(receipt), str(output)]
        # Fresh tokenizer/library startup exceeded the old 20-second fixture
        # limit locally; this is a test-process bound, not a cloud limit.
        result = subprocess.run(command, capture_output=True, text=True, timeout=180)
        self.assertEqual(result.returncode, 0, result.stderr)
        with self.assertRaisesRegex(ValueError, 'fresh'):
            scoring.prepare(root, receipt, output)

    def test_mutated_hash_unmanifested_file_and_receipt_pin(self):
        root, receipt = self.closed()
        log = root / 'driver.log'
        log.write_bytes(b'changed\n')
        with self.assertRaisesRegex(ValueError, 'hash/size'):
            scoring.load_closed(root, receipt)
        self.reclose(root)
        with self.assertRaisesRegex(ValueError, 'receipt'):
            scoring.load_closed(root, receipt)
        self.receipt(root, receipt)
        (root / 'unexpected.log').write_bytes(b'extra')
        with self.assertRaisesRegex(ValueError, 'inventory'):
            scoring.load_closed(root, receipt)

    def test_incomplete_and_failed_a_keep_30_technical_statuses_no_packets(self):
        for kind in ('incomplete','failed_a'):
            self.root = self.fixture_parent / ('fixture-' + uuid.uuid4().hex)
            self.root.mkdir(exist_ok=False)
            root, receipt = self.closed(kind)
            packet, result = self.packets(root, receipt)
            self.assertEqual(result['status'], 'HOLD')
            self.assertEqual(len(result['per_output_status']), 30)
            self.assertFalse((packet / 'reviewer-A/packet.jsonl').exists())
            scored = self.score(packet, root, receipt)
            self.assertFalse(scored['semantic_continuation'])
            self.assertNotIn('reviewers', scored)

    def test_one_critic_missing_and_remote_false_hold(self):
        root, receipt = self.closed()
        packet, _ = self.packets(root, receipt)
        self.ratings(packet, gains=('QUALITYDEV1-002','QUALITYDEV1-007'), reviewer='A')
        result = self.score(packet, root, receipt)
        self.assertEqual(result['missing_reviewers'], ['B'])
        self.assertEqual(result['screen_status'], 'inconclusive')
        # Mounted flags remain false even when a human observational receipt says true.
        self.receipt(root, receipt, remote=False)
        other = self.root / 'remote-false-packets'
        prepared = scoring.prepare(root, receipt, other)
        self.assertFalse(prepared['primary_eligible'])
        self.assertTrue((other / 'reviewer-A/packet.jsonl').is_file())
        result = self.score(other, root, receipt)
        self.assertFalse(result['semantic_continuation'])

    def test_swapped_arm_mapping_and_packet_mutation_even_with_repin(self):
        for name in ('lead-only/mapping.jsonl','reviewer-A/packet.jsonl'):
            self.root = self.fixture_parent / ('fixture-' + uuid.uuid4().hex)
            self.root.mkdir(exist_ok=False)
            root, receipt = self.closed()
            packet, _ = self.packets(root, receipt)
            rows = scoring.decode_lines((packet / name).read_bytes())
            if 'mapping' in name:
                rows[0]['arm'] = 'B' if rows[0]['arm'] == 'A' else 'A'
            else:
                rows[0]['output_text'] = 'tampered output'
                rows[0]['output_sha256'] = scoring.sha(b'tampered output')
            raw = scoring.lines(rows)
            (packet / name).write_bytes(raw)
            provenance = scoring.decode((packet / 'lead-only/provenance.json').read_bytes())
            provenance['files'][name] = {'sha256': scoring.sha(raw), 'bytes': len(raw)}
            (packet / 'lead-only/provenance.json').write_bytes(scoring.encode(provenance))
            with self.assertRaisesRegex(ValueError, 'differs from recovered raw'):
                self.score(packet, root, receipt)

    def test_all_abstain_no_gain(self):
        root, receipt = self.closed('abstain')
        packet, _ = self.packets(root, receipt)
        self.ratings(packet, abstain=True)
        result = self.score(packet, root, receipt)
        self.assertFalse(result['semantic_continuation'])
        self.assertEqual(result['reviewers']['A']['counts']['A'], {'not_assessable': 15})
        self.assertEqual(result['reviewers']['A']['net_accepted_change'], 0)

    def test_one_work_gain_and_critical_regression_hold(self):
        root, receipt = self.closed()
        packet, _ = self.packets(root, receipt)
        self.ratings(packet, gains=('QUALITYDEV1-002','QUALITYDEV1-003'))
        result = self.score(packet, root, receipt)
        self.assertFalse(result['semantic_continuation'])
        self.assertFalse(result['reviewers']['A']['screen_checks']['gains_in_multiple_named_works'])
        self.ratings(packet, gains=('QUALITYDEV1-002','QUALITYDEV1-007','QUALITYDEV1-012'), losses=('QUALITYDEV1-005',))
        result = self.score(packet, root, receipt)
        self.assertFalse(result['semantic_continuation'])
        self.assertEqual(result['reviewers']['A']['net_accepted_change'], 2)
        self.assertEqual(result['reviewers']['A']['accepted_to_critical'], ['QUALITYDEV1-005'])

    def test_closed_identity_mutation_rehashed_still_rejected(self):
        root, receipt = self.closed()
        path = root / 'evaluation/run.json'
        run = scoring.decode(path.read_bytes())
        run['max_generation_seconds'] = 1200
        run['identity_sha256'] = scoring.sha(scoring.canonical({key: run[key] for key in scoring.IDENTITY_FIELDS}))
        path.write_bytes(scoring.encode(run))
        self.reclose(root)
        self.receipt(root, receipt)
        with self.assertRaisesRegex(ValueError, 'closed controls'):
            scoring.load_closed(root, receipt)

    def test_valid_a_eos_abstain_can_gain_and_pure_critical_increase_holds(self):
        root, receipt = self.closed()
        path = root / 'evaluation/predictions.jsonl'
        rows = scoring.decode_lines(path.read_bytes())
        for row in rows:
            if row['id'] in {'QUALITYDEV1-002:A','QUALITYDEV1-007:A'}:
                row['status'] = 'abstain'
                row['text'] = '[UNRESOLVED]'
                row['output_sha256'] = scoring.sha(row['text'].encode())
                row['output_token_ids'] = self.tokenizer.encode(row['text'], add_special_tokens=False) + [1]
                row['output_tokens'] = len(row['output_token_ids'])
        path.write_bytes(scoring.lines(rows))
        self.reclose(root)
        self.receipt(root, receipt)
        packet, _ = self.packets(root, receipt)
        self.ratings(packet, gains=('QUALITYDEV1-002','QUALITYDEV1-007'))
        result = self.score(packet, root, receipt)
        self.assertTrue(result['semantic_continuation'])
        self.assertEqual(result['reviewers']['A']['net_accepted_change'], 2)
        self.assertEqual(result['reviewers']['A']['accepted_counts']['B'] - result['reviewers']['A']['accepted_counts']['A'], 2)
        self.ratings(packet, gains=('QUALITYDEV1-002','QUALITYDEV1-007'), criticals=('QUALITYDEV1-005',))
        result = self.score(packet, root, receipt)
        self.assertFalse(result['semantic_continuation'])
        self.assertEqual(result['reviewers']['A']['accepted_to_critical'], [])
        self.assertEqual(result['reviewers']['A']['critical_count_change'], 1)

    def test_manifest_escape_and_over_16mib_inventory_rejected(self):
        root, receipt = self.closed()
        manifest_path = root / 'manifest.json'
        manifest = scoring.decode(manifest_path.read_bytes())
        manifest['files']['../outside'] = {'sha256': '0' * 64, 'bytes': 0}
        manifest_path.write_bytes(scoring.encode(manifest))
        with self.assertRaises(ValueError):
            scoring.load_closed(root, receipt)
        (root / 'oversized.log').write_bytes(b'x' * scoring.MAX_BYTES)
        with self.assertRaisesRegex(ValueError, '16 MiB'):
            scoring.load_closed(root, receipt)

    def test_rehashed_out_of_vocabulary_output_rejected_before_packets(self):
        root, receipt = self.closed()
        path = root / 'evaluation/predictions.jsonl'
        rows = scoring.decode_lines(path.read_bytes())
        rows[0]['output_token_ids'] = [999999999, 1]
        rows[0]['output_tokens'] = 2
        path.write_bytes(scoring.lines(rows))
        self.reclose(root)
        self.receipt(root, receipt)
        with self.assertRaisesRegex(ValueError, 'outside frozen vocabulary'):
            self.packets(root, receipt)
        self.assertFalse((self.root / 'packets').exists())

    def test_rehashed_valid_ids_wrong_decoded_text_rejected_before_packets(self):
        root, receipt = self.closed()
        path = root / 'evaluation/predictions.jsonl'
        rows = scoring.decode_lines(path.read_bytes())
        rows[0]['output_token_ids'] = self.tokenizer.encode('different synthetic output', add_special_tokens=False) + [1]
        rows[0]['output_tokens'] = len(rows[0]['output_token_ids'])
        path.write_bytes(scoring.lines(rows))
        self.reclose(root)
        self.receipt(root, receipt)
        with self.assertRaisesRegex(ValueError, 'decode/text/hash differs'):
            self.packets(root, receipt)
        self.assertFalse((self.root / 'packets').exists())


    def test_jsonl_tail_duplicate_keys_canary_and_schedule_suffix_rejected(self):
        for mutation in ('tail', 'duplicate', 'canary', 'suffix'):
            self.root = self.fixture_parent / ('fixture-' + mutation)
            self.root.mkdir(exist_ok=False)
            root, receipt = self.closed()
            path = root / 'evaluation/predictions.jsonl'
            if mutation == 'tail':
                path.write_bytes(path.read_bytes().rstrip(b'\n'))
            elif mutation == 'duplicate':
                raw = path.read_bytes()
                path.write_bytes(raw.replace(b'{"id":', b'{"id": "duplicate", "id":', 1))
            else:
                run_path = root / 'evaluation/run.json'
                run = scoring.decode(run_path.read_bytes())
                if mutation == 'canary':
                    run['canary']['rendered_input_ids_sha256'] = '0' * 64
                else:
                    run['unattempted_output_ids'] = [run['schedule'][-1]]
                run_path.write_bytes(scoring.encode(run))
            self.reclose(root)
            self.receipt(root, receipt)
            with self.assertRaises(ValueError):
                self.packets(root, receipt)
            self.assertFalse((self.root / 'packets').exists())

    def test_reviewer_disagreement_preserved_and_not_pooled(self):
        root, receipt = self.closed()
        packet, _ = self.packets(root, receipt)
        self.ratings(packet, gains=('QUALITYDEV1-002', 'QUALITYDEV1-007'), reviewer='A')
        self.ratings(packet, gains=('QUALITYDEV1-002',), reviewer='B')
        result = self.score(packet, root, receipt)
        self.assertFalse(result['semantic_continuation'])
        self.assertTrue(result['reviewers']['A']['screen_pass'])
        self.assertFalse(result['reviewers']['B']['screen_pass'])
        self.assertEqual([d['case_id'] for d in result['reviewer_agreement']['B']['disagreements']], ['QUALITYDEV1-007'])
        self.assertFalse(result['expert_adjudicated'])
        self.assertIn('No significance, unseen generalization', result['limits'])
        a = scoring.decode_lines((packet / 'reviewer-A/packet.jsonl').read_bytes())
        b = scoring.decode_lines((packet / 'reviewer-B/packet.jsonl').read_bytes())
        self.assertFalse({r['review_id'] for r in a} & {r['review_id'] for r in b})
        self.assertNotEqual([r['output_sha256'] for r in a], [r['output_sha256'] for r in b])

    def test_token_count_message_and_receipt_identity_tampering_rejected(self):
        for mutation in ('count', 'message', 'run_id', 'object_bytes'):
            self.root = self.fixture_parent / ('fixture-' + mutation)
            self.root.mkdir(exist_ok=False)
            root, receipt = self.closed()
            if mutation in {'count', 'message'}:
                path = root / 'evaluation/predictions.jsonl'
                rows = scoring.decode_lines(path.read_bytes())
                if mutation == 'count':
                    rows[0]['output_tokens'] += 1
                else:
                    rows[0]['messages'][0]['content'] += ' Tampered.'
                    rows[0]['messages_sha256'] = scoring.sha(scoring.canonical(rows[0]['messages']))
                path.write_bytes(scoring.lines(rows))
                self.reclose(root)
                self.receipt(root, receipt)
            else:
                data = scoring.decode(receipt.read_bytes())
                if mutation == 'run_id':
                    data['run_id'] = '0' * 32
                else:
                    data['objects']['evaluation/predictions.jsonl']['bytes'] += 1
                receipt.write_bytes(scoring.encode(data))
            with self.assertRaises(ValueError):
                self.packets(root, receipt)

    def test_provenance_mutation_cannot_repin_semantic_packet(self):
        root, receipt = self.closed()
        packet, _ = self.packets(root, receipt)
        self.ratings(packet, gains=('QUALITYDEV1-002', 'QUALITYDEV1-007'))
        path = packet / 'lead-only/provenance.json'
        data = scoring.decode(path.read_bytes())
        data['protocol'] = 'dictionary-ab-v1'
        path.write_bytes(scoring.encode(data))
        with self.assertRaisesRegex(ValueError, 'differs from recovered raw'):
            self.score(packet, root, receipt)

if __name__ == '__main__':
    unittest.main()
