"""Offline TRAIN binding, literal prompts and first-attempt lifecycle checks."""
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

from . import train_recall as runner


class TrainRecallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]
        cls.train = cls.root / 'experiments/train-audit-20260927/qualified-v1/train.jsonl'
        cls.train_bytes = cls.train.read_bytes()
        cls.inputs = cls.root / 'experiments/train-recall-20260927/inputs.jsonl'
        cls.rows = [json.loads(line) for line in cls.inputs.read_bytes().splitlines()]

    def bound_read(self, rows=None, expected=None, train_bytes=None):
        data = b'\n'.join(runner.qualified.canonical(row) for row in (self.rows if rows is None else rows)) + b'\n'
        # Synthetic corruption tests replace only this runner's input pin, never frozen helpers.
        # This exercises schema/membership gates independently of the earlier byte-hash gate.
        with patch.object(runner, 'INPUTS_SHA256', runner.qualified.sha(data)), \
                patch.object(Path, 'read_bytes', side_effect=[data, self.train_bytes if train_bytes is None else train_bytes]):
            return runner.read_inputs('source-inputs', expected or runner.qualified.sha(data), self.train)

    def test_direct_qualified_membership_and_source_only_schema(self):
        self.assertEqual(runner.read_inputs(self.inputs, runner.INPUTS_SHA256, self.train), self.rows)
        with self.assertRaisesRegex(ValueError, 'checksum'):
            runner.read_inputs(self.inputs, '0' * 64, self.train)
        self.assertEqual(self.bound_read(), self.rows)
        self.assertTrue(all(set(row) == runner.frozen.FIELDS for row in self.bound_read()))
        for mutate in (lambda rows: rows[0].update(target='FORBIDDEN_REFERENCE'),
                       lambda rows: rows[0].update(reference='FORBIDDEN_REFERENCE'),
                       lambda rows: rows[0].update(source_text=rows[0]['source_text'] + ' changed'),
                       lambda rows: rows[0].update(record_id='parsig:999999999', work_id='parsig:999'),
                       lambda rows: rows[0].update(work_id='parsig:999'),
                       lambda rows: rows[0].update(source_language='fa'),
                       lambda rows: rows[0].update(id=rows[1]['id']),
                       lambda rows: rows.__setitem__(0, copy.deepcopy(rows[1])),
                       lambda rows: rows.pop()):
            rows = copy.deepcopy(self.rows)
            mutate(rows)
            with self.subTest(rows=rows[0]['id']), self.assertRaises(ValueError):
                self.bound_read(rows)
        with self.assertRaisesRegex(ValueError, 'checksum'):
            self.bound_read(expected='0' * 64)
        with self.assertRaisesRegex(ValueError, 'qualified TRAIN'):
            self.bound_read(train_bytes=self.train_bytes + b' ')

    def test_exact_existing_prompts_and_balanced_schedule(self):
        order = runner.schedule(self.rows)
        self.assertEqual(len(order), 40)
        self.assertEqual(Counter(condition for row, condition in order), {'training': 20, 'evaluation': 20})
        self.assertEqual(len({(row['record_id'], condition) for row, condition in order}), 40)
        for index, row in enumerate(self.rows):
            pair = order[2 * index:2 * index + 2]
            self.assertEqual([item[0] for item in pair], [row, row])
            self.assertEqual([item[1] for item in pair], list(runner.CONDITIONS if index % 2 == 0 else runner.CONDITIONS[::-1]))
            self.assertEqual(runner.frozen.messages(row, 'training'), [{'role': 'user',
                'content': runner.frozen.training_bundle.PROMPT.format(text=row['source_text'])}])
            self.assertEqual(runner.frozen.messages(row, 'evaluation'), runner.protocol.messages(row))
        for module in (runner.qualified, runner.frozen, runner.frozen.training_bundle, runner.protocol):
            self.assertEqual(runner.runtime.digest(module.__file__), runner.HELPER_SHA256[Path(module.__file__).name])

    def test_actual_local_token_audit_matches_pinned_aggregate(self):
        path = self.root / 'experiments/train-recall-20260927/token-audit.json'
        self.assertEqual(runner.runtime.digest(path), runner.TOKEN_AUDIT_SHA256)
        audit = json.loads(path.read_text(encoding='utf-8'))
        self.assertEqual(audit['inputs_sha256'], runner.INPUTS_SHA256)
        mapping = {row['id'] + ':' + row['condition']: {'input_tokens': row['input_tokens'],
            'input_ids_sha256': row['input_ids_sha256']} for row in audit['rows']}
        self.assertEqual(len(mapping), 40)
        self.assertEqual(set(mapping), {row['id'] + ':' + condition for row, condition in runner.schedule(self.rows)})
        self.assertEqual(runner.qualified.sha(runner.qualified.canonical(mapping)), runner.TOKEN_MAP_SHA256)

    def mocked_run(self, failure=None):
        class Stream(io.StringIO):
            def __exit__(self, *args): return False
            def fileno(self): return 42
        class Generated:
            def __init__(self, ids, prefix): self.ids, self.prefix = ids, prefix
            def __getitem__(self, index):
                assert index[0] == 0 and index[1].start == self.prefix
                return SimpleNamespace(tolist=lambda: self.ids)
        saved, calls, caches, stream = [], [], [], Stream()
        def generate(**kwargs):
            calls.append(kwargs)
            if failure == 'exception' and len(calls) == 2: raise RuntimeError('synthetic generation failure')
            if failure == 'timeout': kwargs['stopping_criteria'][0].reason = 'case_timeout'
            return Generated([42] * 4096 if failure == 'cap' else [42, 106], len(kwargs['input_ids'][0]))
        logits = SimpleNamespace(shape=(1, 1, 32))
        model = Mock(generate=generate, eval=lambda: None,
            config=SimpleNamespace(get_text_config=lambda: SimpleNamespace(vocab_size=32)),
            return_value=SimpleNamespace(logits=logits))
        if failure == 'prefill': model.side_effect = RuntimeError('prefill failed')
        tokenizer = Mock()
        def render(messages, **kwargs):
            ids = [2, 4, 6] if len(messages) == 2 else [2, 4]
            if failure == 'token_id': ids[-1] = 99
            if failure == 'token_count': ids.append(8)
            return ids
        tokenizer.apply_chat_template.side_effect = render
        tokenizer.decode.return_value = '[UNRESOLVED]' if failure == 'abstain' else 'synthetic translation'
        def cache():
            value = object(); caches.append(value); return value
        transformers = SimpleNamespace(AutoTokenizer=SimpleNamespace(from_pretrained=Mock(return_value=tokenizer)),
            DynamicCache=cache, Gemma4ForConditionalGeneration=SimpleNamespace(from_pretrained=Mock(return_value='base')),
            StoppingCriteriaList=list, set_seed=Mock())
        if failure == 'load': transformers.Gemma4ForConditionalGeneration.from_pretrained.side_effect = RuntimeError('model load failed')
        peft = SimpleNamespace(PeftModel=SimpleNamespace(from_pretrained=Mock(return_value=model)))
        torch = SimpleNamespace(tensor=lambda values, **kwargs: values, ones_like=lambda values: values,
            bfloat16='bf16', inference_mode=nullcontext,
            isfinite=lambda value: SimpleNamespace(all=lambda: SimpleNamespace(item=lambda: True)),
            cuda=SimpleNamespace(reset_peak_memory_stats=Mock(), synchronize=Mock(), empty_cache=Mock(),
                max_memory_allocated=lambda: 100, max_memory_reserved=lambda: 200))
        files = {name: 'a' * 64 for name in ('tokenizer.json', 'tokenizer_config.json', 'chat_template.jinja')}
        def deadline(value):
            if failure == 'global' and calls: raise TimeoutError('global deadline')
            if failure == 'late_global': return datetime(2000, 1, 1, tzinfo=timezone.utc)
            return datetime(2999, 1, 1, tzinfo=timezone.utc)
        def digest(path):
            return runner.HELPER_SHA256.get(Path(path).name, 'd' * 64)
        args = SimpleNamespace(inputs='inputs', inputs_sha256='b' * 64, bundle=Path('mock-bundle'), base='base',
            tokenizer='tokenizer', adapter='adapter', output='out', deadline_utc='2999-01-01T00:00:00Z')
        expected_tokens = {row['id'] + ':' + condition: {'input_tokens': len(ids),
            'input_ids_sha256': runner.qualified.sha(runner.qualified.canonical(ids))}
            for row, condition in runner.schedule(self.rows)
            for ids in [[2, 4] if condition == 'training' else [2, 4, 6]]}
        with patch.dict('sys.modules', {'torch': torch, 'transformers': transformers, 'peft': peft}), \
                patch.object(runner, 'TOKEN_MAP_SHA256', runner.qualified.sha(runner.qualified.canonical(expected_tokens))), \
                patch.object(runner.runtime, 'offline'), patch.object(runner.runtime, 'check_deadline', side_effect=deadline), \
                patch.object(runner, 'read_inputs', return_value=self.rows) as reader, \
                patch.object(runner.qualified, 'verify_adapter') as verify_adapter, \
                patch.object(runner.runtime, 'verified_bundle', return_value=args.bundle), \
                patch.object(runner.runtime, 'contract_at', return_value={'qualified': True}), \
                patch.object(runner.runtime, 'verify_base', return_value={'files': files}), \
                patch.object(runner.runtime, 'checked_files'), patch.object(runner.runtime, 'gpu_admission', return_value={}), \
                patch.object(runner.runtime, 'read_json', return_value={'text_config': {'max_position_embeddings': 4096 if failure == 'context' else 8192}}), \
                patch.object(runner.runtime, 'write_json', side_effect=lambda path, value: saved.append(copy.deepcopy(value))), \
                patch.object(runner.runtime, 'digest', side_effect=digest), patch.object(Path, 'exists', return_value=False), \
                patch.object(Path, 'mkdir'), patch.object(Path, 'open', return_value=stream), \
                patch.object(runner.os, 'fsync') as fsync, patch('builtins.print'):
            if failure not in (None, 'abstain'):
                with self.assertRaises((ValueError, RuntimeError, TimeoutError)): runner.evaluate(args)
            else: runner.evaluate(args)
        reader.assert_called_once_with(args.inputs, args.inputs_sha256, args.bundle / 'train.jsonl')
        verify_adapter.assert_called_once_with(args.adapter, {'qualified': True}, {'files': files})
        records = [json.loads(line) for line in stream.getvalue().splitlines()]
        self.assertEqual(fsync.call_count, len(records))
        self.assertEqual(len(caches), len({id(cache) for cache in caches}))
        self.assertTrue(all(call.kwargs['enable_thinking'] is False for call in tokenizer.apply_chat_template.call_args_list))
        for call in calls:
            self.assertIs(call['do_sample'], False)
            self.assertEqual((call['num_beams'], call['max_new_tokens'], call['pad_token_id'], call['eos_token_id']), (1, 4096, 0, [1, 106, 50]))
            self.assertTrue(call['use_cache'])
        if failure not in ('load', 'context', 'token_id', 'token_count'):
            model.assert_called_once()
            self.assertEqual(model.call_args.kwargs['input_ids'], [[2, 4, 6]])
            self.assertEqual(model.call_args.kwargs['logits_to_keep'], 1)
        if failure in ('token_id', 'token_count'):
            transformers.Gemma4ForConditionalGeneration.from_pretrained.assert_not_called()
            peft.PeftModel.from_pretrained.assert_not_called()
            self.assertNotEqual(saved[-1]['expected_token_map_sha256'], saved[-1]['actual_token_map_sha256'])
        if calls:
            transformers.set_seed.assert_called_once_with(42)
            load = transformers.Gemma4ForConditionalGeneration.from_pretrained.call_args.kwargs
            self.assertEqual((load['dtype'], load['device_map'], load['local_files_only'], load['trust_remote_code']), ('bf16', {'': 0}, True, False))
        return records, saved, calls

    def test_complete_run_preserves_exact_prompts_tokens_and_identity(self):
        records, saved, calls = self.mocked_run()
        run = saved[-1]
        self.assertEqual(len(calls), 40)
        self.assertEqual([r['id'] for r in records], run['schedule'])
        self.assertEqual((run['status'], run['attempted_outputs'], run['completed_outputs'], run['completed_cases']), ('completed', 40, 40, 20))
        self.assertEqual(run['unattempted_output_ids'], [])
        self.assertEqual(run['recorded_outputs'], 40)
        self.assertEqual(run['actual_token_map_sha256'], run['expected_token_map_sha256'])
        self.assertIsNone(run['active_output_id'])
        started = [value for value in saved if value['active_output_id'] is not None]
        self.assertEqual([value['active_output_id'] for value in started], run['schedule'])
        self.assertEqual(run['canary']['id'], self.rows[0]['id'] + ':evaluation')
        self.assertEqual(run['canary']['experimental_attempts'], 0)
        for note, (row, condition) in zip(run['prompts'], runner.schedule(self.rows)):
            self.assertEqual(note['messages'], runner.frozen.messages(row, condition))
            self.assertEqual(note['messages_sha256'], runner.qualified.sha(runner.qualified.canonical(note['messages'])))
            self.assertEqual(note['rendered_input_ids_sha256'], runner.qualified.sha(runner.qualified.canonical(note['input_token_ids'])))
        self.assertTrue(all(r['identity_sha256'] == run['identity_sha256'] and r['output_token_ids'] == [42, 106] for r in records))
        self.assertTrue(all(r['output_token_ids_sha256'] == runner.qualified.sha(runner.qualified.canonical(r['output_token_ids'])) for r in records))
        self.assertNotIn('FORBIDDEN_REFERENCE', json.dumps(saved))

    def test_abstentions_are_completed_attempts(self):
        records, saved, calls = self.mocked_run('abstain')
        self.assertEqual({r['status'] for r in records}, {'abstain'})
        self.assertEqual(saved[-1]['completed_outputs'], 40)

    def test_partial_first_attempts_and_zero_attempt_preflight_failures(self):
        for failure, attempted, completed in [('exception', 2, 1), ('timeout', 1, 0), ('cap', 1, 0),
                ('global', 1, 1), ('late_global', 1, 0), ('prefill', 0, 0), ('load', 0, 0), ('context', 0, 0),
                ('token_id', 0, 0), ('token_count', 0, 0)]:
            with self.subTest(failure=failure):
                records, saved, calls = self.mocked_run(failure)
                run = saved[-1]
                self.assertEqual((len(records), len(calls)), (attempted, attempted))
                self.assertEqual((run['status'], run['attempted_outputs'], run['completed_outputs']), ('incomplete', attempted, completed))
                self.assertEqual(run['unattempted_output_ids'], run['schedule'][attempted:])
                self.assertEqual(len({r['id'] for r in records}), attempted)
                if failure == 'exception': self.assertEqual(records[-1]['error_type'], 'RuntimeError')
                if failure in ('timeout', 'late_global'): self.assertEqual(records[-1]['status'], 'timeout')
                if failure == 'prefill': self.assertEqual(run['canary']['status'], 'failed')

    def test_existing_output_and_missing_cli_hash_fail_closed(self):
        with patch.object(runner.runtime, 'offline'), patch.object(Path, 'exists', return_value=True):
            with self.assertRaisesRegex(ValueError, 'fresh'):
                runner.evaluate(SimpleNamespace(deadline_utc='2999-01-01T00:00:00Z', output='existing'))
        with patch('sys.stderr', io.StringIO()), self.assertRaises(SystemExit):
            runner.main([item for name in ('bundle', 'base', 'tokenizer', 'inputs', 'adapter', 'output', 'deadline-utc')
                         for item in ('--' + name, 'unused')])
        with patch.object(runner.runtime, 'offline'), patch.object(Path, 'exists', return_value=False), \
                patch.object(runner.runtime, 'digest', return_value='0' * 64):
            with self.assertRaisesRegex(ValueError, 'helper identity'):
                runner.evaluate(SimpleNamespace(deadline_utc='2999-01-01T00:00:00Z', output='fresh'))


if __name__ == '__main__':
    unittest.main()
