"""Offline provenance, prompt, adapter and first-attempt execution checks."""
import copy
from collections import Counter
from contextlib import nullcontext
from datetime import datetime, timezone
import io
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from . import dev_assisted as runner


class QualifiedDevTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]
        cls.inputs = cls.root / 'experiments/dev-diagnostic-20260927/inputs.jsonl'
        cls.folder = cls.root / 'experiments/dev-assisted-qualified-20260927/evidence'
        cls.rows = runner.frozen.read_inputs(cls.inputs)
        cls.evidence = (cls.folder / 'evidence.jsonl').read_bytes()
        cls.audit = (cls.folder / 'audit.json').read_bytes()
        cls.witnesses = runner.read_evidence(cls.folder / 'evidence.jsonl', cls.folder / 'audit.json', cls.rows)

    def test_exact_evidence_qualification_and_prompt(self):
        originals = [json.loads(line) for line in self.evidence.splitlines()]
        notes = json.loads(self.audit)['retained_qualifications']
        self.assertEqual(sum(map(len, self.witnesses.values())), 58)
        self.assertEqual(len({w['example']['id'] for ws in self.witnesses.values() for w in ws}), 56)
        for row, original in zip(self.rows, originals):
            witnesses = self.witnesses[row['id']]
            self.assertEqual([w['example'] for w in witnesses], original['examples'])
            self.assertEqual([w['qualification'] for w in witnesses], [n for n in notes if n['case_id'] == row['id']])
            for condition in runner.CONDITIONS:
                messages = runner.messages(row, condition, witnesses)
                self.assertEqual(messages[0], {'role': 'system', 'content': runner.protocol.SYSTEM})
                caution, payload = messages[1]['content'].split('\n\n', 1)
                self.assertEqual(caution, runner.CAUTION)
                self.assertEqual(json.loads(payload), {'source_text': row['source_text'], 'examples': witnesses if condition == 'assisted' else []})
        self.assertEqual(runner.runtime.digest(runner.protocol.__file__), runner.PROTOCOL_SHA256)
        contract = self.root / 'experiments/dev-assisted-qualified-20260927/uniform-evaluation-contract.json'
        self.assertEqual(runner.runtime.digest(contract), runner.LOCAL_EVALUATION_CONTRACT_SHA256)

    def test_contamination_and_changed_bytes_fail(self):
        with patch.object(Path, 'read_bytes', side_effect=[self.evidence + b' ', self.audit]):
            with self.assertRaisesRegex(ValueError, 'bytes differ'):
                runner.read_evidence('evidence', 'audit', self.rows)
        for location in ('query', 'example'):
            rows = [json.loads(line) for line in self.evidence.splitlines()]
            target = rows[0] if location == 'query' else rows[0]['examples'][0]
            target['reference_text'] = 'forbidden DEV reference'
            modified = b'\n'.join(runner.canonical(row) for row in rows)
            audit = json.loads(self.audit)
            audit['evidence_sha256'] = runner.sha(modified)
            audit_data = runner.canonical(audit)
            with patch.object(Path, 'read_bytes', side_effect=[modified, audit_data]), \
                    patch.object(runner, 'EVIDENCE_SHA256', runner.sha(modified)), \
                    patch.object(runner, 'AUDIT_SHA256', runner.sha(audit_data)):
                with self.assertRaisesRegex(ValueError, 'schema'):
                    runner.read_evidence('evidence', 'audit', self.rows)
        altered = copy.deepcopy(self.rows)
        altered[0]['target_text'] = 'forbidden'
        with self.assertRaisesRegex(ValueError, 'identity'):
            runner.read_evidence(self.folder / 'evidence.jsonl', self.folder / 'audit.json', altered)

    def test_qualification_tamper_rejected_even_with_rebound_file_hash(self):
        audit = json.loads(self.audit)
        audit['retained_qualifications'][0]['linguistic_review']['source_sha256'] = 'a' * 64
        data = runner.canonical(audit)
        with patch.object(Path, 'read_bytes', side_effect=[self.evidence, data]), patch.object(runner, 'AUDIT_SHA256', runner.sha(data)):
            with self.assertRaisesRegex(ValueError, 'review hash'):
                runner.read_evidence('evidence', 'audit', self.rows)

    def test_schedule_is_24_by_2_balanced(self):
        ordered = runner.schedule(self.rows)
        self.assertEqual(len(ordered), 48)
        self.assertEqual(Counter((row['id'], arm) for row, arm in ordered), Counter((row['id'], arm) for row in self.rows for arm in runner.CONDITIONS))
        self.assertEqual(Counter(arm for _, arm in ordered[::2]), Counter(plain=12, assisted=12))
        for work in runner.frozen.WORKS:
            self.assertEqual(Counter(arm for row, arm in ordered[::2] if row['work_id'] == work), Counter(plain=3, assisted=3))

    def test_existing_output_rejected_before_runtime_admission(self):
        args = SimpleNamespace(deadline_utc='2999-01-01T00:00:00Z', inputs=self.inputs,
            evidence=self.folder / 'evidence.jsonl', audit=self.folder / 'audit.json', output=self.folder)
        with patch.object(runner.runtime, 'offline'), patch.object(runner.runtime, 'gpu_admission') as gpu:
            with self.assertRaisesRegex(ValueError, 'fresh directory'):
                runner.evaluate(args)
            gpu.assert_not_called()

    def test_qualified_adapter_identity_and_old_adapter_rejection(self):
        path = self.root / 'experiments/retrain-qualified-20260927/continuation/training'
        provenance = runner.runtime.read_json(path / 'provenance.json')
        status = runner.runtime.read_json(path / 'status.json')
        manifest = runner.runtime.read_json(path.parent / 'manifest.json')
        prior = runner.runtime.read_json(path.parent / 'after/run.json')
        self.assertEqual(runner.runtime.digest(path.parent / 'manifest.json'), runner.ADAPTER_MANIFEST_SHA256)
        self.assertEqual(runner.runtime.digest(path.parent / 'after/run.json'), runner.ADAPTER_EVALUATION_SHA256)
        self.assertEqual(prior['adapter_files'], runner.ADAPTER_FILES)
        for name, digest in runner.ADAPTER_FILES.items():
            self.assertEqual(manifest['files']['training/adapter/' + name]['sha256'], digest)
        for name, digest in runner.ADAPTER_METADATA.items():
            self.assertEqual(runner.runtime.digest(path / name), digest)
        contract = {key: provenance[key] for key in ('model', 'training')}
        base = {'files': provenance['base_files']}
        with patch.object(runner.runtime, 'checked_files') as check:
            runner.verify_adapter(path / 'adapter', contract, base)
            self.assertEqual(check.call_args_list[0].args[1], runner.ADAPTER_FILES)
            self.assertEqual(check.call_args_list[1].args[1], runner.ADAPTER_METADATA)
            for step in (20, 312):
                with patch.object(runner.runtime, 'read_json', side_effect=[provenance, {**status, 'global_step': step}]):
                    with self.assertRaisesRegex(ValueError, 'step-280'):
                        runner.verify_adapter(path / 'adapter', contract, base)
            with patch.object(runner.runtime, 'read_json', side_effect=[{**provenance, 'train_sha256': 'a' * 64}, status]):
                with self.assertRaises(ValueError):
                    runner.verify_adapter(path / 'adapter', contract, base)
        with patch.object(runner.runtime, 'checked_files', side_effect=ValueError('hash differs')):
            with self.assertRaisesRegex(ValueError, 'hash differs'):
                runner.verify_adapter(path / 'adapter', contract, base)

    def mocked_run(self, failure=None):
        class Stream(io.StringIO):
            def __exit__(self, *args): return False
        class Generated:
            def __init__(self, ids): self.ids = ids
            def __getitem__(self, index): return SimpleNamespace(tolist=lambda: self.ids)
        calls, caches, saved, stream = [], [], [], Stream()
        def generate(**kwargs):
            calls.append(kwargs)
            if failure == 'exception' and len(calls) == 2: raise RuntimeError('simulated failure')
            if failure == 'timeout': kwargs['stopping_criteria'][0].reason = 'case_timeout'
            return Generated([42] * 4096 if failure == 'cap' else [42, 106])
        prefill_logits = SimpleNamespace(shape=(1, 1, 32))
        model = Mock(generate=generate, eval=lambda: None,
            config=SimpleNamespace(get_text_config=lambda: SimpleNamespace(vocab_size=32)),
            return_value=SimpleNamespace(logits=prefill_logits))
        if failure == 'prefill_exception': model.side_effect = RuntimeError('prefill failure')
        if failure == 'prefill_shape': prefill_logits.shape = (1, 2, 32)
        tokenizer = Mock()
        tokenizer.apply_chat_template.side_effect = lambda messages, **kwargs: ([2, 4, 6]
            if json.loads(messages[1]['content'].split('\n\n', 1)[1])['examples'] else [2, 4])
        tokenizer.decode.return_value = 'translation'
        def cache():
            value = object(); caches.append(value); return value
        transformers = SimpleNamespace(AutoTokenizer=SimpleNamespace(from_pretrained=Mock(return_value=tokenizer)), DynamicCache=cache,
            Gemma4ForConditionalGeneration=SimpleNamespace(from_pretrained=Mock(return_value='base')),
            StoppingCriteriaList=list, set_seed=Mock())
        peft = SimpleNamespace(PeftModel=SimpleNamespace(from_pretrained=Mock(return_value=model)))
        torch = SimpleNamespace(tensor=lambda values, **kwargs: values, ones_like=lambda values: values,
            bfloat16='bf16', inference_mode=nullcontext,
            isfinite=lambda value: SimpleNamespace(all=lambda: SimpleNamespace(item=lambda: failure != 'prefill_nonfinite')),
            cuda=SimpleNamespace(reset_peak_memory_stats=Mock(), synchronize=Mock(), empty_cache=Mock(),
                max_memory_allocated=lambda: 100, max_memory_reserved=lambda: 200))
        files = {name: 'a' * 64 for name in ('tokenizer.json', 'tokenizer_config.json', 'chat_template.jinja')}
        def deadline(value):
            if failure == 'global' and calls: raise TimeoutError('global deadline')
            if failure == 'prefill_deadline' and model.called: raise TimeoutError('prefill deadline')
            if failure == 'late_global': return datetime(2000, 1, 1, tzinfo=timezone.utc)
            return datetime(2999, 1, 1, tzinfo=timezone.utc)
        def digest(path):
            return runner.PROTOCOL_SHA256 if Path(path).name == 'palref_eval.py' else runner.TRAIN_SHA256
        args = SimpleNamespace(inputs=self.inputs, evidence='unused-evidence', audit='unused-audit', bundle=self.root / 'mock-bundle',
            base='mock-base', tokenizer='mock-tokenizer', adapter='mock-adapter', output='unused-output', deadline_utc='2999-01-01T00:00:00Z')
        with patch.dict('sys.modules', {'torch': torch, 'transformers': transformers, 'peft': peft}), \
                patch.object(runner.runtime, 'offline'), patch.object(runner.runtime, 'check_deadline', side_effect=deadline), \
                patch.object(runner, 'read_evidence', return_value=self.witnesses), patch.object(runner, 'verify_adapter'), \
                patch.object(runner.runtime, 'verified_bundle', return_value=args.bundle), patch.object(runner.runtime, 'contract_at', return_value={}), \
                patch.object(runner.runtime, 'verify_base', return_value={'files': files}), patch.object(runner.runtime, 'checked_files'), \
                patch.object(runner.runtime, 'gpu_admission', return_value={}), \
                patch.object(runner.runtime, 'read_json', return_value={'text_config': {'max_position_embeddings': 8192}}), \
                patch.object(runner.runtime, 'write_json', side_effect=lambda path, value: saved.append(copy.deepcopy(value))), \
                patch.object(runner.runtime, 'digest', side_effect=digest), patch.object(Path, 'exists', return_value=False), \
                patch.object(Path, 'mkdir'), patch.object(Path, 'open', return_value=stream), \
                patch.object(runner.frozen, 'read_inputs', return_value=self.rows), patch('builtins.print'):
            if failure:
                with self.assertRaises((RuntimeError, TimeoutError)): runner.evaluate(args)
            else:
                runner.evaluate(args)
        transformers.Gemma4ForConditionalGeneration.from_pretrained.assert_called_once()
        peft.PeftModel.from_pretrained.assert_called_once_with('base', args.adapter, local_files_only=True, is_trainable=False)
        self.assertEqual(len(caches), len({id(cache) for cache in caches}))
        model.assert_called_once()
        self.assertEqual(model.call_args.kwargs['input_ids'], [[2, 4, 6]])
        self.assertEqual(model.call_args.kwargs['logits_to_keep'], 1)
        self.assertTrue(model.call_args.kwargs['use_cache'])
        torch.cuda.empty_cache.assert_called_once()
        for call in calls:
            self.assertFalse(call['do_sample'])
            self.assertEqual((call['num_beams'], call['max_new_tokens'], call['pad_token_id'], call['eos_token_id']), (1, 4096, 0, [1, 106, 50]))
        for call in tokenizer.apply_chat_template.call_args_list:
            self.assertIs(call.kwargs['enable_thinking'], False)
        return [json.loads(line) for line in stream.getvalue().splitlines()], saved[-1], calls

    def test_complete_mocked_run_and_protocol_settings(self):
        records, run, calls = self.mocked_run()
        self.assertEqual(len(calls), 48)
        self.assertEqual([record['id'] for record in records], run['schedule'])
        self.assertEqual((run['status'], run['attempted_outputs'], run['completed_outputs'], run['completed_cases']), ('completed', 48, 48, 24))
        self.assertEqual(run['unattempted_output_ids'], [])
        self.assertTrue(all(record['identity_sha256'] == run['identity_sha256'] for record in records))
        self.assertEqual(run['canary']['status'], 'passed')
        self.assertEqual(run['canary']['id'], 'QUALITYDEV1-001:assisted')
        self.assertEqual(run['canary']['input_tokens'], 3)
        self.assertEqual(run['canary']['experimental_attempts'], 0)
        self.assertFalse(run['canary']['output_generated'])

    def test_prefill_failures_preserve_zero_experimental_attempts(self):
        for failure in ('prefill_exception', 'prefill_shape', 'prefill_nonfinite', 'prefill_deadline'):
            with self.subTest(failure=failure):
                records, run, calls = self.mocked_run(failure)
                self.assertEqual((records, calls), ([], []))
                self.assertEqual((run['status'], run['canary']['status'], run['attempted_outputs']), ('incomplete', 'failed', 0))
                self.assertEqual(len(run['unattempted_output_ids']), 48)

    def test_failure_deadline_timeout_and_cap_preserve_attempts(self):
        for failure, attempted, completed in [('exception', 2, 1), ('timeout', 1, 0), ('cap', 1, 0), ('global', 1, 1), ('late_global', 1, 0)]:
            with self.subTest(failure=failure):
                records, run, calls = self.mocked_run(failure)
                self.assertEqual((len(records), len(calls)), (attempted, attempted))
                self.assertEqual((run['status'], run['attempted_outputs'], run['completed_outputs']), ('incomplete', attempted, completed))
                self.assertEqual(len(run['unattempted_output_ids']), 48 - attempted)
                self.assertEqual(len({record['id'] for record in records}), attempted)


if __name__ == '__main__':
    unittest.main()
