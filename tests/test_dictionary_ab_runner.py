"""Offline fixed-panel checks using cached tokenizer and CPU mock generation only."""
import copy
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import sys
import types
import unittest
import uuid
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
# The pinned project client is used without installing into the shared runtime.
sys.path.insert(0, str(ROOT / 'resources/local/hf-client-venv/Lib/site-packages'))
from cloud_pilot import hf_component, runtime

helper = types.ModuleType('component_helpers')
with patch.dict(sys.modules, {'runtime': runtime}):
    exec(hf_component.helper_source()[0], helper.__dict__)
    spec = importlib.util.spec_from_file_location('_dictionary_ab_test_runner', ROOT / 'cloud_pilot/component_eval.py')
    runner = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {'component_helpers': helper}):
        spec.loader.exec_module(runner)

import torch
from transformers import AutoTokenizer


@contextmanager
def test_directory():
    # Python's mode-0700 Temp directories exclude the Windows sandbox token.
    # Use an exclusive random directory with inherited permissions and preserve
    # its mock journal for inspection. It is outside all frozen source artifacts.
    path = ROOT / 'resources/local' / ('dictionary-runner-check-' + uuid.uuid4().hex)
    path.mkdir(exist_ok=False)
    yield str(path)


class Model:
    """Real CPU token tensors, no parameters, model weights, network or GPU calls."""
    training = False

    def __init__(self, kind='success', clock=None):
        self.kind, self.clock = kind, clock
        self.calls, self.caches = [], []

    def set_adapter(self, arm):
        assert arm == 'reference'

    def requires_grad_(self, value):
        assert value is False

    def eval(self):
        self.training = False

    def zero_grad(self, **kwargs):
        pass

    def parameters(self):
        return []

    def get_model_status(self):
        return types.SimpleNamespace(enabled=True, active_adapters=['reference'], merged_adapters=[], available_adapters=['reference'])

    def generate(self, **kwargs):
        self.calls.append(kwargs)
        self.caches.append(kwargs['past_key_values'])
        if self.kind == 'fatal' and len(self.calls) == 3:
            raise RuntimeError('Mock first-attempt model failure')
        if self.kind == 'timeout':
            kwargs['stopping_criteria'][0].start -= 91
        if self.kind == 'reserve':
            self.clock[0] += 87
        if self.kind == 'remaining' and len(self.calls) == 1:
            self.clock[0] += 112
        tail = [7] * kwargs['max_new_tokens'] if self.kind == 'cap' else [7] if self.kind == 'missing_eos' else [7, 1]
        return torch.cat((kwargs['input_ids'], torch.tensor([tail])), dim=1)


class DictionaryRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = ROOT / 'resources/local/dev-comparability-20261003/ab-inputs.jsonl'
        cls.rows = runner.read_inputs(cls.inputs, runner.DICTIONARY_INPUTS_SHA256, 'dictionary-ab-v1')
        cls.tokenizer = AutoTokenizer.from_pretrained(
            ROOT / 'resources/local/cloud-pilot-qualified-20260927/tokenizer',
            local_files_only=True, trust_remote_code=False)
        cls.prepared = runner.prepare_prompts(cls.rows, cls.tokenizer, 'dictionary-ab-v1')

    def settings(self):
        return dict(protocol='dictionary-ab-v1', run_id='0123456789abcdef0123456789abcdef',
            script_hashes={'component_eval.py': '0' * 64, 'component_helpers.py': '0' * 64},
            decode_controls=runner.dictionary_controls(),
            timing_contract=runner.DICTIONARY_TIMING_CONTRACT, compute_seconds=6600,
            internal_seconds=7020, native_timeout_minutes=120, planned_outputs=30,
            inputs_sha256=runner.DICTIONARY_INPUTS_SHA256, schedule=runner.schedule('dictionary-ab-v1'),
            reviewed_specimen_sha256=runner.DICTIONARY_HISTORICAL_CONTRACT_SHA256,
            precision='bf16_base_fp32_retained_lora', training=False, automatic_retry=False)

    def state(self, protocol='dictionary-ab-v1'):
        order = runner.schedule(protocol)
        settings = self.settings() if protocol == 'dictionary-ab-v1' else {}
        return dict(settings, protocol=protocol, decode_controls=runner.dictionary_controls(),
            identity_sha256='0' * 64, status='running', schedule=order, scheduled_outputs=len(order),
            attempted_outputs=0, recorded_outputs=0, successful_outputs=0, model_calls_started=0,
            active_output_id=None, unattempted_output_ids=order, last_result=None)

    def test_fixed_rows_and_schedule_with_legacy_defaults_unchanged(self):
        expected = [case + ':' + arm for case in runner.DICTIONARY_CASES for arm in 'AB']
        self.assertEqual([r['id'] for r in self.rows], expected)
        order = runner.schedule('dictionary-ab-v1')
        self.assertEqual(len(set(order)), 30)
        self.assertEqual(set(order), set(expected))
        self.assertEqual(order[::2], [c + ':' + ('A' if i % 2 == 0 else 'B') for i, c in enumerate(runner.DICTIONARY_CASES)])
        self.assertEqual([r['work_id'] for r in self.rows[::2]], list(runner.DICTIONARY_WORKS.values()))
        self.assertEqual(runner.schedule(), [c + '-' + a for c, o in zip(runner.CASES, runner.ORDERS) for a in o])
        self.assertEqual([len(runner.schedule(p)) for p in ('components-v1', 'stages-v1', 'own-analysis-v1')], [12, 12, 9])

    def test_frozen_file_cannot_be_rebound_to_new_hash(self):
        raw = self.inputs.read_bytes() + b' '
        with test_directory() as directory:
            changed = Path(directory) / 'inputs.jsonl'
            changed.write_bytes(raw)
            with self.assertRaisesRegex(ValueError, 'not caller-selectable'):
                runner.read_inputs(changed, runner.sha(raw), 'dictionary-ab-v1')
            with self.assertRaisesRegex(ValueError, 'checksum differs'):
                runner.read_inputs(changed, runner.DICTIONARY_INPUTS_SHA256, 'dictionary-ab-v1')

    def test_schema_role_source_and_work_binding_failures(self):
        for kind in ('field', 'role', 'missing_system', 'empty_system', 'work', 'source', 'eligibility', 'boolean_tokens', 'arm', 'group_count'):
            row = copy.deepcopy(self.rows[0])
            if kind == 'field': row['reference_text'] = 'forbidden'
            elif kind == 'role': row['messages'][0]['role'] = 'user'
            elif kind == 'missing_system': row['messages'].pop(0)
            elif kind == 'empty_system': row['messages'][0]['content'] = ''
            elif kind == 'work': row['work_id'] = 'parsig:517'
            elif kind == 'source': row['source_sha256'] = '0' * 64
            elif kind == 'eligibility': row['eligible_without_truncation'] = False
            elif kind == 'boolean_tokens': row['input_tokens'] = True
            elif kind == 'arm': row['arm'] = 'C'
            else: row['dictionary_group_count'] = 1
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                runner.validate_dictionary_row(row)

    def test_real_longest_prompt_replays_all_messages_ids_and_hashes(self):
        self.assertEqual(max(map(len, self.prepared.values())), 5135)
        calls = []
        def render(messages, **kwargs):
            calls.append(copy.deepcopy(messages))
            return self.tokenizer.apply_chat_template(messages, **kwargs)
        tokenizer = types.SimpleNamespace(unk_token_id=self.tokenizer.unk_token_id, apply_chat_template=render)
        result = runner.prepare_prompts(self.rows, tokenizer, 'dictionary-ab-v1')
        self.assertEqual(result, self.prepared)
        self.assertEqual(calls, [r['messages'] for r in self.rows for _ in range(2)])
        for row in self.rows:
            self.assertEqual(len(result[row['id']]), row['input_tokens'])
            self.assertEqual(runner.sha(runner.canonical(result[row['id']])), row['input_ids_sha256'])
            self.assertLessEqual(row['input_tokens'] + 4096, 12288)

    def test_tokenizer_hash_unknown_token_and_capacity_fail_without_truncation(self):
        for key in ('input_ids_sha256', 'rendered_text_sha256', 'input_tokens'):
            row = copy.deepcopy(self.rows[0])
            row[key] = row[key] + 1 if key == 'input_tokens' else '0' * 64
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'never truncate'):
                runner.prepare_prompts([row], self.tokenizer, 'dictionary-ab-v1')
        row = copy.deepcopy(self.rows[0])
        text, ids = 'mock capacity rendering', [7] * 8192
        row.update(input_tokens=len(ids), rendered_text_sha256=runner.sha(text.encode()),
            input_ids_sha256=runner.sha(runner.canonical(ids)))
        tokenizer = types.SimpleNamespace(unk_token_id=3,
            apply_chat_template=lambda messages, **kwargs: ids if kwargs['tokenize'] else text)
        self.assertEqual(len(runner.prepare_prompts([row], tokenizer, 'dictionary-ab-v1')[row['id']]) + 4096, 12288)
        overflow = dict(row, input_tokens=8193)
        with self.assertRaises(ValueError): runner.prepare_prompts([overflow], tokenizer, 'dictionary-ab-v1')
        ids[0] = tokenizer.unk_token_id
        with self.assertRaisesRegex(ValueError, 'never truncate'):
            runner.prepare_prompts([row], tokenizer, 'dictionary-ab-v1')

    def test_closed_settings_do_not_allow_historical_or_arbitrary_relaxation(self):
        runner.dictionary_settings(self.settings())
        for key, value in (('compute_seconds', 6601), ('internal_seconds', 7200),
                ('native_timeout_minutes', 121), ('planned_outputs', 29),
                ('timing_contract', 'historical-1200s'), ('training', True), ('automatic_retry', True)):
            settings = self.settings(); settings[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): runner.dictionary_settings(settings)
        for key, value in (('max_generation_seconds', 1200), ('input_cap_tokens', 9000),
                ('max_new_tokens', 256), ('context_limit', 12289), ('max_generation_seconds', 90.0),
                ('no_truncation', False), ('first_attempt_only', False)):
            settings = self.settings(); settings['decode_controls'][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError): runner.dictionary_settings(settings)
        runner.dictionary_settings({'protocol': 'components-v1'})
        runner.dictionary_settings({'protocol': 'own-analysis-v1'})
        controls = runner.dictionary_controls()
        self.assertEqual(30 * controls['max_generation_seconds'] + controls['export_overhead_seconds'] + controls['tail_reserve_seconds'], 3420)

    def generation(self, root, kind='success', seconds=3600, clock=None, publish=None):
        output = root / kind; output.mkdir()
        (root / 'model-inputs.jsonl').write_bytes(self.inputs.read_bytes())
        state, model = self.state(), Model(kind, clock)
        deadline = (datetime.now(timezone.utc) + timedelta(seconds=seconds)).isoformat()
        patches = [patch.object(runner, 'emit'), patch.object(runner.os, 'fsync', wraps=runner.os.fsync),
            patch.object(helper, 'emit')]
        if clock is not None: patches.append(patch.object(runner.time, 'monotonic', side_effect=lambda: clock[0]))
        if publish is not None: patches.append(patch.object(runner, 'publish', side_effect=publish))
        from contextlib import ExitStack
        with ExitStack() as stack:
            mocks = [stack.enter_context(p) for p in patches]
            error = None
            try:
                runner.generate(model, self.tokenizer, self.rows, self.prepared, output, root / (kind + '-mount'), state, deadline, device='cpu')
            except (RuntimeError, TimeoutError, FileExistsError) as failure:
                error = failure
        predictions = output / 'predictions.jsonl'
        rows = [json.loads(line) for line in predictions.read_bytes().splitlines()] if predictions.exists() else []
        return state, model, rows, error, mocks[1].call_count, output

    def test_thirty_first_attempts_greedy_fresh_cache_journal_and_no_retry(self):
        with test_directory() as directory:
            root = Path(directory)
            state, model, rows, error, syncs, output = self.generation(root)
            self.assertIsNone(error)
            self.assertEqual(syncs, 30)
            self.assertEqual(state['recorded_outputs'], 30)
            self.assertEqual(state['model_calls_started'], 30)
            self.assertEqual([r['id'] for r in rows], runner.schedule('dictionary-ab-v1'))
            self.assertEqual(len({id(cache) for cache in model.caches}), 30)
            self.assertEqual(len(list((root / 'success-mount').glob('*/manifest.json'))), 60)
            self.assertFalse(state['primary_comparison_inconclusive'])
            for call, record in zip(model.calls, rows):
                frozen = next(r for r in self.rows if r['id'] == record['id'])
                self.assertEqual(call['max_new_tokens'], 4096)
                self.assertEqual((call['do_sample'], call['num_beams'], call['pad_token_id'], call['eos_token_id']), (False, 1, 0, [1, 106, 50]))
                self.assertEqual(call['input_ids'].shape[1], frozen['input_tokens'])
                self.assertEqual(record['messages'], frozen['messages'])
                for key in ('work_id', 'source_sha256', 'input_tokens', 'rendered_text_sha256', 'input_ids_sha256'):
                    self.assertEqual(record[key], frozen[key])
            state['adapter_unchanged_after_inference'] = True  # Mock-only receipt, no GPU proof.
            runtime.write_json(output / 'run.json', state)
            accounting = hf_component.reconcile(output, state['schedule'])
            self.assertEqual(accounting['status'], 'complete')
            self.assertTrue(accounting['pipeline_complete'])
            self.assertEqual(accounting['committed_model_calls'], 30)
            with patch.object(runner, 'emit'), self.assertRaises(FileExistsError):
                runner.generate(model, self.tokenizer, self.rows, self.prepared, output,
                    root / 'success-mount', state, (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(), device='cpu')
            self.assertEqual(len(model.calls), 30)

    def test_timeout_and_cap_keep_fixed_denominator_and_make_primary_inconclusive(self):
        with test_directory() as directory:
            for kind, status in (('timeout', 'timeout'), ('cap', 'error')):
                state, model, rows, error, syncs, output = self.generation(Path(directory), kind)
                self.assertIsNone(error)
                self.assertEqual((len(rows), len(model.calls), syncs), (30, 30, 30))
                self.assertTrue(state['primary_comparison_inconclusive'])
                self.assertTrue(all(r['status'] == status and not r['primary_comparison_eligible'] for r in rows))
                if kind == 'cap': self.assertTrue(all(r['hit_output_cap_without_eos'] for r in rows))
                state['adapter_unchanged_after_inference'] = True  # Mock-only receipt.
                runtime.write_json(output / 'run.json', state)
                self.assertFalse(hf_component.reconcile(output, state['schedule'])['pipeline_complete'])

    def test_fatal_model_error_is_saved_once_without_replacement(self):
        with test_directory() as directory:
            state, model, rows, error, syncs, _ = self.generation(Path(directory), 'fatal')
            self.assertIsInstance(error, RuntimeError)
            self.assertEqual((len(rows), len(model.calls), syncs), (3, 3, 3))
            self.assertEqual(state['unattempted_output_ids'], runner.schedule('dictionary-ab-v1')[3:])
            self.assertIsNone(state['active_output_id'])
            self.assertEqual(rows[-1]['error_type'], 'RuntimeError')

    def test_full_time_admission_before_first_output(self):
        with test_directory() as directory:
            state, model, rows, error, syncs, output = self.generation(Path(directory), seconds=3419)
            self.assertIsInstance(error, TimeoutError)
            self.assertFalse((output / 'predictions.jsonl').exists())
            self.assertEqual((len(rows), len(model.calls), syncs, state['attempted_outputs']), (0, 0, 0, 0))

    def test_each_slot_admission_and_safe_reserve_preserve_remaining_slots(self):
        with test_directory() as directory:
            state, model, rows, error, syncs, _ = self.generation(Path(directory), 'remaining', seconds=3421, clock=[0.0])
            self.assertIsInstance(error, TimeoutError)
            self.assertEqual((len(rows), len(model.calls), syncs), (1, 1, 1))
            self.assertEqual(state['unattempted_output_ids'], runner.schedule('dictionary-ab-v1')[1:])
        # Deliberate slow export mock bypasses publication enforcement to exercise
        # generation's independent reserve guard rather than waiting in real time.
        with test_directory() as directory:
            clock, published = [0.0], []
            def slow_export(source, target, deadline, identity):
                published.append(deadline)
                if len(published) == 1: clock[0] += 15
                if len(published) == 2: clock[0] += 10
                return {'manifest_sha256': '0' * 64}
            state, model, rows, error, syncs, _ = self.generation(Path(directory), 'reserve', seconds=3421, clock=clock, publish=slow_export)
            self.assertIsInstance(error, TimeoutError)
            self.assertEqual((len(rows), len(model.calls), syncs), (1, 1, 1))
            self.assertEqual(rows[0]['stop_reason'], 'safe_reserve')
            self.assertTrue(state['primary_comparison_inconclusive'])
            self.assertEqual(state['unattempted_output_ids'], runner.schedule('dictionary-ab-v1')[1:])
            self.assertEqual(published[0], 10.0)

    def test_export_failure_keeps_interrupted_or_committed_slot_without_retry(self):
        with test_directory() as directory:
            for fail_at in (1, 2):
                count = [0]
                def publish(source, target, deadline, identity):
                    count[0] += 1
                    if count[0] == fail_at: raise TimeoutError('Mock export timeout')
                    return {'manifest_sha256': '0' * 64}
                state, model, rows, error, syncs, output = self.generation(Path(directory), 'export' + str(fail_at), publish=publish)
                self.assertIsInstance(error, TimeoutError)
                committed = fail_at - 1
                saved = json.loads((output / 'run.json').read_bytes())
                self.assertEqual((state['attempted_outputs'], state['recorded_outputs'], len(rows), len(model.calls), syncs), (1, committed, committed, committed, committed))
                self.assertEqual(saved['active_output_id'], runner.schedule('dictionary-ab-v1')[0] if fail_at == 1 else None)
                self.assertEqual(saved['unattempted_output_ids'], runner.schedule('dictionary-ab-v1')[1:])
                accounting = hf_component.reconcile(output, state['schedule'])
                self.assertEqual(accounting['status'], 'incomplete')
                self.assertEqual(accounting['per_output_status'][state['schedule'][0]],
                    'interrupted_output_unknown' if fail_at == 1 else 'success')
                self.assertEqual(sum(value == 'unattempted' for value in accounting['per_output_status'].values()), 29)

    def test_non_eos_below_cap_is_error_and_primary_inconclusive(self):
        with test_directory() as directory:
            state, model, rows, error, syncs, _ = self.generation(Path(directory), 'missing_eos')
            self.assertIsNone(error)
            self.assertEqual((len(rows), len(model.calls), syncs), (30, 30, 30))
            self.assertTrue(state['primary_comparison_inconclusive'])
            self.assertTrue(all(r['status'] == 'error' and r['error_type'] == 'MissingEOS'
                and not r['hit_output_cap_without_eos'] for r in rows))

    def test_loaded_precision_guard_rejects_quantization_wrong_dtype_and_cpu_before_canary(self):
        from contextlib import ExitStack
        from unittest.mock import Mock
        with test_directory() as directory:
            root = Path(directory)
            for kind in ('quantized', 'base_fp32', 'lora_bf16', 'cpu', 'valid'):
                model = Model()
                model.config = types.SimpleNamespace(quantization_config={'bits': 4} if kind == 'quantized' else None)
                def parameter(dtype, device='cuda'):
                    return types.SimpleNamespace(dtype=dtype, device=types.SimpleNamespace(type=device),
                        is_floating_point=lambda: True)
                model.named_parameters = lambda: iter((
                    ('model.base.weight', parameter(torch.float32 if kind == 'base_fp32' else torch.bfloat16,
                        'cpu' if kind == 'cpu' else 'cuda')),
                    ('model.layer.lora_A.reference.weight', parameter(torch.bfloat16 if kind == 'lora_bf16' else torch.float32))))
                base_loader, adapter_loader, seed = Mock(return_value='mock_base'), Mock(return_value=model), Mock()
                transformers = types.SimpleNamespace(AutoTokenizer=types.SimpleNamespace(from_pretrained=Mock(return_value=self.tokenizer)),
                    Gemma4ForConditionalGeneration=types.SimpleNamespace(from_pretrained=base_loader), set_seed=seed)
                peft = types.SimpleNamespace(PeftModel=types.SimpleNamespace(from_pretrained=adapter_loader))
                args = types.SimpleNamespace(settings='mock_settings', deadline_utc=(datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
                    base='mock_base', bundle='mock_bundle', adapter='mock_adapter', inputs=self.inputs,
                    output=root / kind, incremental=root / (kind + '-mount'))
                with ExitStack() as stack:
                    stack.enter_context(patch.dict(sys.modules, {'transformers': transformers, 'peft': peft}))
                    for name, value in (('offline', None), ('checked_files', None), ('verified_bundle', Path('mock_bundle')),
                            ('contract_at', {}), ('verify_base', {'files': {}}), ('gpu_admission', {}), ('read_json', self.settings())):
                        stack.enter_context(patch.object(runner.runtime, name, return_value=value))
                    stack.enter_context(patch.object(runner, 'verify_adapter'))
                    verified = stack.enter_context(patch.object(runner, 'verify_loaded_adapter'))
                    prefill = stack.enter_context(patch.object(runner, 'prefill_canary', return_value={'status': 'passed'}))
                    generate = stack.enter_context(patch.object(runner, 'generate'))
                    stack.enter_context(patch.object(runner, 'emit'))
                    stack.enter_context(patch.object(runner, 'snapshot', side_effect=lambda output, remote, state, name, deadline:
                        runner.runtime.write_json(output / 'run.json', state)))
                    if kind == 'valid':
                        runner.run(args)
                        prefill.assert_called_once()
                        self.assertEqual(max(map(len, prefill.call_args.args[1].values())), 5135)
                        generate.assert_called_once()
                        self.assertEqual(verified.call_count, 2)
                    else:
                        with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, 'numerical path differs'):
                            runner.run(args)
                        prefill.assert_not_called(); generate.assert_not_called()
                state = json.loads((args.output / 'run.json').read_bytes())
                self.assertEqual(state['adapter_step'], 280)
                self.assertEqual(state['precision'], 'bf16_base_fp32_retained_lora')
                self.assertEqual(state['decode_controls'], runner.dictionary_controls())
                self.assertEqual(state['reviewed_specimen_sha256'], runner.DICTIONARY_HISTORICAL_CONTRACT_SHA256)
                self.assertEqual(state['timing_contract'], runner.DICTIONARY_TIMING_CONTRACT)
                self.assertEqual(base_loader.call_args.kwargs['torch_dtype'], torch.bfloat16)
                self.assertFalse(adapter_loader.call_args.kwargs['is_trainable'])
                if kind != 'valid': self.assertTrue(state['primary_comparison_inconclusive'])

    def test_slow_input_setup_stops_before_model_dispatch_and_saves_first_slot(self):
        clock, actual_tensor = [0.0], torch.tensor
        def slow_tensor(*args, **kwargs):
            clock[0] += 100
            return actual_tensor(*args, **kwargs)
        with test_directory() as directory, patch.object(torch, 'tensor', side_effect=slow_tensor):
            state, model, rows, error, syncs, _ = self.generation(Path(directory), seconds=3421, clock=clock)
            self.assertIsInstance(error, TimeoutError)
            self.assertEqual((state['attempted_outputs'], state['recorded_outputs'], len(rows), len(model.calls), syncs), (1, 1, 1, 0, 1))
            self.assertFalse(rows[0]['model_call_started'])
            self.assertEqual(rows[0]['error_type'], 'TimeoutError')
            self.assertTrue(state['primary_comparison_inconclusive'])
            self.assertEqual(state['unattempted_output_ids'], runner.schedule('dictionary-ab-v1')[1:])


if __name__ == '__main__':
    unittest.main()
