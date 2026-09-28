"""Offline checks with faithful adapter-context/cache mocks; no weights or cloud."""
import copy
from collections import Counter
from contextlib import contextmanager, nullcontext
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

try:
    from . import dev_diagnostic as runner
except ImportError:
    import dev_diagnostic as runner


class DevDiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent
        self.inputs = self.root / "experiments/dev-diagnostic-20260927/inputs.jsonl"
        self.data = self.inputs.read_bytes()
        self.rows = runner.read_inputs(self.inputs)

    def test_frozen_source_schema_and_all_four_counterbalanced_conditions(self):
        scheduled = runner.schedule(self.rows)
        self.assertEqual(len(scheduled), 96)
        self.assertEqual(len({(row['id'], condition) for row, condition in scheduled}), 96)
        cases = [row for row, _ in scheduled[::4]]
        self.assertEqual([row['work_id'] for row in cases], sorted(runner.WORKS) * 6)
        for work in runner.WORKS:
            self.assertEqual([row['id'] for row in cases if row['work_id'] == work],
                             [row['id'] for row in self.rows if row['work_id'] == work])
        for position in range(4):
            self.assertEqual(Counter(condition for _, condition in scheduled[position::4]), Counter({key: 6 for key in runner.CONDITIONS}))
        transitions = Counter((f'D{order[i]}', f'D{order[i+1]}') for order in runner.ORDERS for i in range(3))
        self.assertEqual(len(transitions), 12)
        self.assertEqual(set(transitions.values()), {1})
        self.assertEqual(scheduled, runner.schedule(self.rows))

    def test_exact_training_and_evaluation_messages(self):
        for row in self.rows:
            self.assertEqual(runner.messages(row, 'training'), [{'role': 'user', 'content': runner.training_bundle.PROMPT.format(text=row['source_text'])}])
            self.assertEqual(runner.messages(row, 'evaluation'), runner.protocol.messages(row))
        with self.assertRaises(ValueError):
            runner.messages(self.rows[0], 'unknown')

    def test_tampered_bytes_and_independent_schema_fail_closed(self):
        with patch.object(Path, 'read_bytes', return_value=self.data + b'\n'), patch.object(runner.runtime, 'verified_bundle') as bundle:
            with self.assertRaises(ValueError):
                runner.evaluate(SimpleNamespace(inputs=self.inputs, deadline_utc='2999-01-01T00:00:00Z'))
            bundle.assert_not_called()
        for field, value in [('reference', 'forbidden'), ('source_language', 'en'), ('record_id', 'parsig:151001001'), ('id', 'OTHER')]:
            rows = copy.deepcopy(self.rows); rows[0][field] = value
            data = '\n'.join(json.dumps(row) for row in rows).encode()
            with self.subTest(field=field), patch.object(Path, 'read_bytes', return_value=data), patch.object(runner, 'INPUTS_SHA256', hashlib.sha256(data).hexdigest()):
                with self.assertRaises(ValueError):
                    runner.read_inputs(self.inputs)

    def test_pinned_adapter_tampering_and_wrong_step_rejected(self):
        adapter = self.root / 'mock-adapter'
        for filename in runner.ADAPTER_FILES:
            def digest(path):
                return '0' * 64 if path.name == filename else runner.ADAPTER_FILES[path.name]
            with self.subTest(filename=filename), patch.object(Path, 'is_file', return_value=True), \
                    patch.object(runner.runtime, 'digest', side_effect=digest), patch.object(runner.runtime, 'read_json') as read:
                with self.assertRaisesRegex(ValueError, 'checksum'):
                    runner.verify_adapter(adapter, {'model': {}}, {'files': {}})
                read.assert_not_called()
        with patch.object(runner.runtime, 'checked_files'), patch.object(runner.runtime, 'read_json', side_effect=[{'model': {}, 'base_files': {}}, {'status': 'training_complete', 'global_step': 20}]):
            with self.assertRaisesRegex(ValueError, 'step-312'):
                runner.verify_adapter(adapter, {'model': {}}, {'files': {}})

    def mocked_run(self, failure=None):
        class Stream(io.StringIO):
            def __exit__(self, *args):
                self.flush()
        class Generated:
            def __init__(self, ids): self.ids = ids
            def __getitem__(self, index): return SimpleNamespace(tolist=lambda: self.ids)
        class Model:
            enabled = True
            def __init__(self): self.calls = []; self.contexts = 0
            def eval(self): pass
            @contextmanager
            def disable_adapter(self):
                old = self.enabled; self.enabled = False; self.contexts += 1
                try: yield
                finally: self.enabled = old
            def generate(self, **kwargs):
                self.calls.append((self.enabled, kwargs))
                if failure == 'exception' and len(self.calls) == 2:
                    raise RuntimeError('simulated generation failure')
                if failure == 'timeout': kwargs['stopping_criteria'][0].reason = 'case_timeout'
                return Generated([42] * runner.protocol.MAX_TOKENS if failure == 'cap' else [42, 106])
        model, stream, saved, caches = Model(), Stream(), [], []
        tokenizer = Mock()
        tokenizer.apply_chat_template.side_effect = lambda msgs, **kwargs: [2, 3] if len(msgs) == 1 else [2, 4]
        tokenizer.decode.return_value = 'translation'
        def cache():
            value = object(); caches.append(value); return value
        transformer = SimpleNamespace(AutoTokenizer=SimpleNamespace(from_pretrained=Mock(return_value=tokenizer)),
            DynamicCache=cache, Gemma4ForConditionalGeneration=SimpleNamespace(from_pretrained=Mock(return_value='original-base')),
            StoppingCriteriaList=list, set_seed=Mock())
        peft = SimpleNamespace(PeftModel=SimpleNamespace(from_pretrained=Mock(return_value=model)))
        torch = SimpleNamespace(tensor=lambda values, **kwargs: values, ones_like=lambda values: values,
                                bfloat16='bf16', inference_mode=nullcontext)
        files = {name: 'a' * 64 for name in ('tokenizer.json', 'tokenizer_config.json', 'chat_template.jinja')}
        def read(path):
            if path.name == 'provenance.json': return {'model': {}, 'base_files': files}
            if path.name == 'status.json': return {'status': 'training_complete', 'global_step': 312}
            return {'text_config': {'max_position_embeddings': 8192}}
        def deadline(value):
            if failure == 'global' and model.calls: raise TimeoutError('global deadline')
            return datetime(2999, 1, 1, tzinfo=timezone.utc)
        args = SimpleNamespace(inputs=self.inputs, bundle=self.root / 'mock-bundle', base='mock-base', tokenizer='mock-tokenizer',
            adapter=self.root / 'mock-training/adapter', output=self.root / 'unused-dev-output', deadline_utc='2999-01-01T00:00:00Z')
        with patch.dict('sys.modules', {'torch': torch, 'transformers': transformer, 'peft': peft}), \
                patch.object(runner.runtime, 'offline'), patch.object(runner.runtime, 'check_deadline', side_effect=deadline), \
                patch.object(runner.runtime, 'verified_bundle', return_value=args.bundle), \
                patch.object(runner.runtime, 'contract_at', return_value={'model': {}}), \
                patch.object(runner.runtime, 'verify_base', return_value={'files': files}), \
                patch.object(runner.runtime, 'checked_files'), patch.object(runner.runtime, 'gpu_admission', return_value={}), \
                patch.object(runner.runtime, 'read_json', side_effect=read), \
                patch.object(runner.runtime, 'write_json', side_effect=lambda path, value: saved.append(copy.deepcopy(value))), \
                patch.object(runner.runtime, 'digest', return_value='b' * 64), patch.object(Path, 'exists', return_value=False), \
                patch.object(Path, 'mkdir'), patch.object(Path, 'read_bytes', return_value=self.data), \
                patch.object(Path, 'open', return_value=stream), patch('builtins.print'):
            if failure:
                with self.assertRaises((RuntimeError, TimeoutError)):
                    runner.evaluate(args)
            else:
                runner.evaluate(args)
        records = [json.loads(line) for line in stream.getvalue().splitlines()]
        transformer.Gemma4ForConditionalGeneration.from_pretrained.assert_called_once()
        peft.PeftModel.from_pretrained.assert_called_once_with('original-base', args.adapter, local_files_only=True, is_trainable=False)
        transformer.set_seed.assert_called_once_with(42)
        self.assertTrue(model.enabled, 'disable_adapter must restore original state after success or exception')
        self.assertEqual(len({id(value) for value in caches}), len(model.calls))
        for record, (enabled, kwargs) in zip(records, model.calls):
            self.assertEqual(enabled, record['model_condition'] == 'adapter')
            self.assertFalse(kwargs['do_sample']); self.assertEqual(kwargs['num_beams'], 1)
            self.assertEqual(kwargs['max_new_tokens'], 4096); self.assertEqual(kwargs['eos_token_id'], [1, 106, 50])
            self.assertEqual(kwargs['input_ids'], [[2, 3] if record['instruction'] == 'training' else [2, 4]])
            self.assertEqual(len(kwargs['stopping_criteria']), 1)
        return records, saved[-1], model

    def test_complete_run_uses_one_model_and_adapter_with_fresh_cache(self):
        records, run, model = self.mocked_run()
        self.assertEqual(len(records), 96)
        self.assertEqual([record['id'] for record in records], run['schedule'])
        self.assertEqual(model.contexts, 48)
        self.assertEqual((run['status'], run['attempted_outputs'], run['completed_outputs'], run['completed_cases']), ('completed', 96, 96, 24))
        self.assertEqual(run['unattempted_output_ids'], [])
        self.assertTrue(all(record['identity_sha256'] == run['identity_sha256'] for record in records))

    def test_failure_cap_timeout_and_global_deadline_preserve_first_attempts(self):
        for failure, attempted, completed in [('exception', 2, 1), ('timeout', 1, 0), ('cap', 1, 0), ('global', 1, 1)]:
            with self.subTest(failure=failure):
                records, run, model = self.mocked_run(failure)
                self.assertEqual(len(records), attempted)
                self.assertEqual(len(model.calls), attempted)
                self.assertEqual((run['status'], run['attempted_outputs'], run['completed_outputs'], run['completed_cases']), ('incomplete', attempted, completed, 0))
                self.assertEqual(len(run['unattempted_output_ids']), 96-attempted)
                self.assertEqual(len({r['id'] for r in records}), attempted)


if __name__ == '__main__':
    unittest.main()
