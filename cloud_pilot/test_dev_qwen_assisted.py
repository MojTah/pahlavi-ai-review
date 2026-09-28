"""Offline checks: exact Qwen identities, native-call wiring and attempt accounting."""
import copy
from contextlib import nullcontext
from datetime import datetime, timezone
import io
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from . import dev_qwen_assisted as runner


class QwenDevTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]
        cls.folder = cls.root / 'experiments/dev-assisted-qualified-20260927'
        cls.identity = cls.folder / 'qwen-source-identity.json'
        cls.source = json.loads(cls.identity.read_bytes())
        cls.rows = runner.shared.frozen.read_inputs(cls.root / 'experiments/dev-diagnostic-20260927/inputs.jsonl')
        cls.witnesses = runner.shared.read_evidence(cls.folder / 'evidence/evidence.jsonl', cls.folder / 'evidence/audit.json', cls.rows)
        cls.deadline = datetime(2999, 1, 1, tzinfo=timezone.utc)

    def test_frozen_inputs_helpers_and_same_shared_prompts(self):
        self.assertEqual(runner.runtime.digest(self.identity), runner.SOURCE_IDENTITY_SHA256)
        self.assertEqual(runner.runtime.digest(runner.shared.__file__), runner.SHARED_HELPER_SHA256)
        self.assertEqual(runner.runtime.digest(Path(runner.__file__).with_name('qwen_presence.py')), runner.PRESENCE_SHA256)
        self.assertEqual(len(runner.shared.schedule(self.rows)), 48)
        for row in self.rows:
            for condition in runner.shared.CONDITIONS:
                messages = runner.shared.messages(row, condition, self.witnesses[row['id']])
                self.assertEqual(messages[0]['content'], runner.protocol.SYSTEM)
                self.assertEqual(json.loads(messages[1]['content'].split('\n\n', 1)[1])['source_text'], row['source_text'])

    def test_snapshot_checks_every_publisher_file_and_missing_shards(self):
        source = self.source
        weights = {f'language-key-{i}': shard['rfilename'] for i, shard in enumerate(source['weight_shards_metadata_only'])}
        weights.update({f'language-key-{i}': source['weight_shards_metadata_only'][0]['rfilename']
                        for i in range(15, source['weight_parameter_mapping_keys'])})
        by_name = {'config.json': source['config'], 'generation_config.json': source['generation_config'],
                   'model.safetensors.index.json': {'weight_map': weights}}
        sizes = {entry['rfilename']: entry['size'] for entry in source['weight_shards_metadata_only']}
        with patch.object(runner.runtime, 'checked_files') as checked, \
                patch.object(runner.runtime, 'read_json', side_effect=lambda path: by_name[path.name]), \
                patch.object(Path, 'stat', autospec=True, side_effect=lambda path: SimpleNamespace(st_size=sizes[path.name])):
            identity, files, ignored = runner.verify_snapshot('unused', self.identity)
            self.assertEqual(len(files), 26)
            self.assertEqual(set(checked.call_args.args[1]), set(source['files']) | set(sizes))
            self.assertTrue(all(files[e['rfilename']] == e['lfs']['sha256'] for e in source['weight_shards_metadata_only']))
        with patch.object(runner.runtime, 'checked_files', side_effect=ValueError('missing or corrupt shard')):
            with self.assertRaisesRegex(ValueError, 'shard'):
                runner.verify_snapshot('unused', self.identity)
        with patch.object(Path, 'read_bytes', return_value=self.identity.read_bytes() + b' '):
            with self.assertRaisesRegex(ValueError, 'identity'):
                runner.verify_snapshot('unused', self.identity)

    def test_native_loading_rejects_all_language_defects(self):
        good = {'missing_keys': set(), 'mismatched_keys': set(), 'error_msgs': [],
                'unexpected_keys': {'model.visual.foo', 'mtp.foo'}}
        self.assertEqual(runner.check_loading(good)['unexpected_keys'], ['model.visual.foo', 'mtp.foo'])
        for key, value in [('missing_keys', {'model.layers.0.weight'}), ('mismatched_keys', {('lm_head.weight', (2,), (3,))}),
                           ('unexpected_keys', {'model.language_model.layers.0.weight'}), ('error_msgs', ['conversion failure']),
                           ('conversion_errors', {'layer': 'failure'})]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                runner.check_loading({**good, key: value})
        with self.assertRaises(ValueError): runner.check_loading({})

    def test_generate_uses_exact_native_settings_fresh_cache_and_penalty(self):
        caches, penalties, calls = [], [], []
        class Penalty:
            def __init__(self, length, value):
                self.prompt_length, self.penalty = length, value
                penalties.append(self)
        def cache(**kwargs):
            item = object(); caches.append((item, kwargs)); return item
        class Generated:
            def __getitem__(self, item): return SimpleNamespace(tolist=lambda: [17, 248046])
        def generate(**kwargs): calls.append(kwargs); return Generated()
        torch = SimpleNamespace(tensor=lambda value, **kw: value, ones_like=lambda value: value,
            inference_mode=nullcontext, cuda=SimpleNamespace(synchronize=lambda: None))
        transformers = SimpleNamespace(DynamicCache=cache, LogitsProcessorList=list, StoppingCriteriaList=list)
        model = SimpleNamespace(config=object(), generate=generate)
        with patch.dict('sys.modules', {'torch': torch, 'transformers': transformers,
                'cloud_pilot.qwen_presence': SimpleNamespace(GeneratedTokenPresencePenalty=Penalty)}):
            for _ in range(2):
                new_ids, elapsed, reason = runner.generate_ids(model, [1, 2, 3], self.deadline)
                self.assertEqual(new_ids, [17, 248046]); self.assertIsNone(reason)
        self.assertIsNot(caches[0][0], caches[1][0])
        self.assertTrue(all(kwargs == {'config': model.config} for _, kwargs in caches))
        self.assertTrue(all((p.prompt_length, p.penalty) == (3, 1.5) for p in penalties))
        for call in calls:
            self.assertTrue(all(call[key] == value for key, value in runner.SAMPLING.items()))
            self.assertNotIn('presence_penalty', call)
            self.assertEqual((call['max_new_tokens'], call['logits_to_keep'], call['pad_token_id'], call['eos_token_id']), (4096, 1, 248044, [248046, 248044]))

    def test_canary_two_synthetic_requests_and_longest_prefill_only(self):
        tokenizer = Mock()
        tokenizer.apply_chat_template.side_effect = [runner.NONTHINKING_SUFFIX, [1, 2]]
        tokenizer.encode.return_value = [1, 2]
        logits = SimpleNamespace(shape=(1, 1, 32))
        model = Mock(return_value=SimpleNamespace(logits=logits))
        model.config = SimpleNamespace(vocab_size=32)
        cuda = SimpleNamespace(reset_peak_memory_stats=lambda: None, synchronize=lambda: None,
            max_memory_allocated=lambda: 100, max_memory_reserved=lambda: 200, empty_cache=lambda: None)
        torch = SimpleNamespace(tensor=lambda value, **kw: value, ones_like=lambda value: value, inference_mode=nullcontext,
            cuda=cuda, isfinite=lambda value: SimpleNamespace(all=lambda: SimpleNamespace(item=lambda: True)))
        transformers = SimpleNamespace(DynamicCache=Mock(), set_seed=Mock())
        with patch.dict('sys.modules', {'torch': torch, 'transformers': transformers}), \
                patch.object(runner, 'generate_ids', return_value=([5, 6, 7], 0.2, None)) as generate:
            result = runner.canary(model, tokenizer, {('short', 'plain'): [1], ('long', 'assisted'): [1, 2, 3]}, self.deadline)
        self.assertEqual(generate.call_count, 2)
        self.assertEqual([call.args[1] for call in generate.call_args_list], [[1, 2], [1, 2]])
        self.assertEqual(transformers.set_seed.call_count, 2)
        model.assert_called_once()
        self.assertEqual(model.call_args.kwargs['input_ids'], [[1, 2, 3]])
        self.assertEqual(result['experimental_attempts'], 0)
        self.assertFalse(result['longest_prompt_prefill']['output_generated'])

    def mocked_run(self, failure=None):
        class Stream(io.StringIO):
            def __exit__(self, *args): return False
        stream, saved, generated = Stream(), [], []
        tokenizer = Mock(eos_token_id=248046, pad_token_id=248044)
        tokenizer.convert_tokens_to_ids.side_effect = lambda token: 248046 if token == '<|im_end|>' else 248044
        tokenizer.apply_chat_template.return_value = [2, 3]
        tokenizer.decode.return_value = 'translation'
        model = SimpleNamespace(dtype='bf16', config=SimpleNamespace(model_type='qwen3_5_text'), eval=lambda: None)
        loading = {'missing_keys': [], 'unexpected_keys': [], 'mismatched_keys': [], 'error_msgs': []}
        if failure == 'loading': loading['missing_keys'] = ['lm_head.weight']
        transformers = SimpleNamespace(__file__='mock-transformers/__init__.py',
            AutoTokenizer=SimpleNamespace(from_pretrained=Mock(return_value=tokenizer)),
            Qwen3_5ForCausalLM=SimpleNamespace(from_pretrained=Mock(return_value=(model, loading))), set_seed=Mock())
        torch = SimpleNamespace(bfloat16='bf16')
        def generate(*args):
            generated.append(args)
            if failure == 'exception' and len(generated) == 2: raise RuntimeError('generation error')
            return ([4] * 4096 if failure == 'cap' else [4, 248046], 0.1,
                    'case_timeout' if failure == 'timeout' else None)
        def digest(path):
            return {'dev_assisted.py': runner.SHARED_HELPER_SHA256, 'palref_eval.py': runner.shared.PROTOCOL_SHA256,
                    'qwen_presence.py': runner.PRESENCE_SHA256}.get(Path(path).name, 'a' * 64)
        def check_time(deadline):
            if failure == 'global' and generated: raise TimeoutError('global deadline')
        args = SimpleNamespace(inputs='unused', evidence='unused', audit='unused', base='unused-base', source_identity=self.identity,
            output='unused-output', deadline_utc='2999-01-01T00:00:00Z')
        with patch.dict('sys.modules', {'torch': torch, 'transformers': transformers}), \
                patch.object(runner.runtime, 'offline'), patch.object(runner.runtime, 'digest', side_effect=digest), \
                patch.object(runner.shared.frozen, 'read_inputs', return_value=self.rows), \
                patch.object(runner.shared, 'read_evidence', return_value=self.witnesses), \
                patch.object(runner, 'verify_snapshot', return_value=(self.source, {}, ['mtp.weight'])), \
                patch.object(runner.runtime, 'gpu_admission', return_value={}), patch.object(runner.runtime, 'checked_files'), \
                patch.object(runner.runtime, 'write_json', side_effect=lambda path, value: saved.append(copy.deepcopy(value))), \
                patch.object(runner, 'generate_ids', side_effect=generate), patch.object(runner, 'check_time', side_effect=check_time), \
                patch.object(runner, 'canary', side_effect=RuntimeError('canary failed') if failure == 'canary' else None,
                             return_value={'status': 'passed', 'experimental_attempts': 0}) as canary, \
                patch.object(Path, 'exists', return_value=False), patch.object(Path, 'mkdir'), \
                patch.object(Path, 'open', return_value=stream), patch('builtins.print'):
            if failure:
                with self.assertRaises((RuntimeError, ValueError, TimeoutError)): runner.evaluate(args)
            else: runner.evaluate(args)
        records = [json.loads(line) for line in stream.getvalue().splitlines()]
        if failure not in ('canary', 'loading'): transformers.set_seed.assert_called_once_with(42)
        if failure == 'loading': canary.assert_not_called()
        loader = transformers.Qwen3_5ForCausalLM.from_pretrained.call_args.kwargs
        self.assertTrue(loader['local_files_only']); self.assertFalse(loader['trust_remote_code'])
        self.assertEqual((loader['dtype'], loader['device_map'], loader['attn_implementation']), ('bf16', {'': 0}, 'eager'))
        return records, saved[-1], generated

    def test_complete_mocked_48_run_and_uniform_prompts(self):
        records, run, generated = self.mocked_run()
        self.assertEqual((len(records), len(generated)), (48, 48))
        self.assertEqual([record['id'] for record in records], run['schedule'])
        self.assertEqual((run['status'], run['completed_outputs'], run['completed_cases']), ('completed', 48, 24))
        self.assertEqual(run['unattempted_output_ids'], [])
        for entry, (row, arm) in zip(run['prompts'], runner.shared.schedule(self.rows)):
            self.assertEqual(entry['messages'], runner.shared.messages(row, arm, self.witnesses[row['id']]))

    def test_first_attempt_failures_and_preflight_failures_are_preserved(self):
        for mode, attempted, completed in [('exception', 2, 1), ('cap', 1, 0), ('timeout', 1, 0),
                                            ('global', 1, 1), ('loading', 0, 0), ('canary', 0, 0)]:
            with self.subTest(mode=mode):
                records, run, generated = self.mocked_run(mode)
                self.assertEqual((len(records), len(generated)), (attempted, attempted))
                self.assertEqual((run['status'], run['attempted_outputs'], run['completed_outputs']), ('incomplete', attempted, completed))
                self.assertEqual(len(run['unattempted_output_ids']), 48 - attempted)
                if mode == 'canary': self.assertEqual(run['canary']['status'], 'failed')


if __name__ == '__main__':
    unittest.main()
