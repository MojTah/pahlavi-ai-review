"""Offline fixed-panel checks using cached tokenizer and CPU mock generation only."""
import copy
import ast
import hashlib
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
from cloud_pilot import hf_dictionary_faithfulness, runtime

helper = types.ModuleType('component_helpers')
with patch.dict(sys.modules, {'runtime': runtime}):
    exec(hf_dictionary_faithfulness.helper_source()[0], helper.__dict__)
    spec = importlib.util.spec_from_file_location('_dictionary_faithfulness_test_runner', ROOT / 'cloud_pilot/faithfulness_eval.py')
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
    path = ROOT / 'resources/local' / ('dictionary-faithfulness-check-' + uuid.uuid4().hex)
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


class DictionaryFaithfulnessRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = ROOT / 'resources/local/dictionary-faithfulness-20261005/model-inputs.jsonl'
        cls.rows = runner.read_inputs(cls.inputs, runner.DICTIONARY_INPUTS_SHA256, 'dictionary-faithfulness-v1')
        cls.tokenizer = AutoTokenizer.from_pretrained(
            ROOT / 'resources/local/cloud-pilot-qualified-20260927/tokenizer',
            local_files_only=True, trust_remote_code=False)
        cls.prepared = runner.prepare_prompts(cls.rows, cls.tokenizer, 'dictionary-faithfulness-v1')

    def settings(self):
        return dict(protocol='dictionary-faithfulness-v1', run_id='0123456789abcdef0123456789abcdef',
            script_hashes={'faithfulness_eval.py': '0' * 64, 'component_helpers.py': '0' * 64},
            decode_controls=runner.dictionary_controls(),
            timing_contract=runner.DICTIONARY_TIMING_CONTRACT, compute_seconds=6600,
            internal_seconds=7020, native_timeout_minutes=120, planned_outputs=30,
            inputs_sha256=runner.DICTIONARY_INPUTS_SHA256, schedule=runner.schedule('dictionary-faithfulness-v1'),
            contract_sha256=runner.DICTIONARY_CONTRACT_SHA256,
            precision='bf16_base_fp32_retained_lora', training=False, automatic_retry=False)

    def state(self, protocol='dictionary-faithfulness-v1'):
        order = runner.schedule(protocol)
        settings = self.settings() if protocol == 'dictionary-faithfulness-v1' else {}
        return dict(settings, protocol=protocol, decode_controls=runner.dictionary_controls(),
            identity_sha256='0' * 64, status='running', schedule=order, scheduled_outputs=len(order),
            attempted_outputs=0, recorded_outputs=0, successful_outputs=0, model_calls_started=0,
            active_output_id=None, unattempted_output_ids=order, last_result=None)

    def test_fixed_rows_and_schedule(self):
        expected = [case + ':' + arm for case in runner.DICTIONARY_CASES for arm in 'AB']
        self.assertEqual([r['id'] for r in self.rows], expected)
        order = runner.schedule('dictionary-faithfulness-v1')
        self.assertEqual(len(set(order)), 30)
        self.assertEqual(set(order), set(expected))
        self.assertEqual(order[::2], [c + ':' + ('A' if i % 2 == 0 else 'B') for i, c in enumerate(runner.DICTIONARY_CASES)])
        self.assertEqual([r['work_id'] for r in self.rows[::2]], list(runner.DICTIONARY_WORKS.values()))

    def test_exact_historical_controls_user_bytes_and_one_system_sentence(self):
        historical = {r['case_id']:r for r in map(json.loads,
            (ROOT / 'resources/local/dev-comparability-20261003/ab-inputs.jsonl').read_bytes().splitlines())
            if r['arm'] == 'B'}
        for a,b in zip(self.rows[::2],self.rows[1::2]):
            self.assertEqual(a['messages'],historical[a['case_id']]['messages'])
            self.assertEqual(a['source_sha256'],historical[a['case_id']]['source_sha256'])
            self.assertEqual(a['messages'][1]['content'].encode(),b['messages'][1]['content'].encode())
            self.assertEqual(b['messages'][0]['content'],
                a['messages'][0]['content']+'\n'+hf_dictionary_faithfulness.FAITHFULNESS_SENTENCE)
            self.assertGreater(a['dictionary_group_count'],0)

    def test_fake_pairs_wrong_identity_and_source_rejected_even_with_synthetic_rebinding(self):
        # Rebind only the test namespace so deeper schema/pair guards are exercised;
        # production's fixed input/contract hashes reject these bytes before this point.
        contract = json.loads(self.inputs.with_name('contract.json').read_bytes())
        for kind in ('user','system','double_suffix','control','id','source','work','count','arm'):
            rows = copy.deepcopy(self.rows)
            if kind == 'user': rows[1]['messages'][1]['content'] += ' '
            elif kind == 'system': rows[1]['messages'][0]['content'] += ' '
            elif kind == 'double_suffix': rows[1]['messages'][0]['content'] += '\n'+hf_dictionary_faithfulness.FAITHFULNESS_SENTENCE
            elif kind == 'control':
                rows[0]['messages'][0]['content'] += ' altered'
                rows[1]['messages'][0]['content'] = rows[0]['messages'][0]['content']+'\n'+hf_dictionary_faithfulness.FAITHFULNESS_SENTENCE
            elif kind == 'id': rows[0]['id'] = rows[2]['id']
            elif kind == 'source': rows[0]['source_sha256'] = 'f'*64
            elif kind == 'work': rows[0]['work_id'] = 'parsig:517'
            elif kind == 'count': rows[0]['dictionary_group_count'] = True
            else: rows[0]['arm'] = 'C'
            raw = b''.join(runner.canonical(r)+b'\n' for r in rows)
            digest = runner.sha(raw)
            changed_contract = dict(contract,model_inputs_sha256=digest)
            contract_raw = runner.canonical(changed_contract)
            with self.subTest(kind=kind), patch.object(hf_dictionary_faithfulness,'DICTIONARY_INPUT_SHA256',digest),\
                    patch.object(hf_dictionary_faithfulness,'DICTIONARY_CONTRACT_SHA256',runner.sha(contract_raw)),\
                    self.assertRaises(ValueError):
                hf_dictionary_faithfulness.validate_frozen_inputs(raw,contract_raw)

    def test_sdk_preview_is_self_contained_and_has_no_submission(self):
        from cloud_pilot.training_admission import sdk_spec
        import gzip,base64
        spec,receipt = hf_dictionary_faithfulness.prepare(self.inputs,run_id='e'*32)
        restored = sdk_spec(json.loads(json.dumps(spec,default=lambda x:x.to_dict())))
        self.assertEqual(restored['timeout'],'120m')
        self.assertEqual([v.read_only for v in restored['volumes']],[True,True,False])
        self.assertEqual(receipt['output_prefix'],'dictionary-faithfulness/'+'e'*32)
        self.assertEqual(set(receipt['script_hashes']),{'faithfulness_eval.py','component_helpers.py'})
        self.assertEqual(receipt['optimizer_updates'],0)
        self.assertFalse(receipt['credentials_accessed'])
        self.assertFalse(receipt['provider_called'])
        self.assertFalse(receipt['submitted'])
        command = ast.parse(restored['command'][3])
        payload = ast.literal_eval(command.body[1].value.args[0].args[0])
        code = gzip.decompress(base64.b64decode(payload)).decode()
        self.assertEqual(hashlib.sha256(code.encode()).hexdigest(),receipt['decoded_command_sha256'])
        tree = ast.parse(code)
        namespace = {}
        exec(compile(ast.Module(body=tree.body[:-1],type_ignores=[]),'prepared','exec'),namespace)
        self.assertEqual(namespace['dictionary_schedule'](),hf_dictionary_faithfulness.dictionary_schedule())
        self.assertEqual(namespace['dictionary_controls'](),hf_dictionary_faithfulness.dictionary_controls())
        self.assertEqual(namespace['validate_frozen_inputs'](self.inputs.read_bytes(),
            self.inputs.with_name('contract.json').read_bytes()),self.rows)

    def test_frozen_file_cannot_be_rebound_to_new_hash(self):
        raw = self.inputs.read_bytes() + b' '
        with test_directory() as directory:
            changed = Path(directory) / 'inputs.jsonl'
            changed.write_bytes(raw)
            with self.assertRaisesRegex(ValueError, 'not caller-selectable'):
                runner.read_inputs(changed, runner.sha(raw), 'dictionary-faithfulness-v1')
            with self.assertRaisesRegex(ValueError, 'checksum differs'):
                runner.read_inputs(changed, runner.DICTIONARY_INPUTS_SHA256, 'dictionary-faithfulness-v1')

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
            else: row['dictionary_group_count'] = 0
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                runner.validate_dictionary_row(row)

    def test_real_longest_prompt_replays_all_messages_ids_and_hashes(self):
        self.assertLessEqual(max(map(len, self.prepared.values())), 8192)
        calls = []
        def render(messages, **kwargs):
            calls.append(copy.deepcopy(messages))
            return self.tokenizer.apply_chat_template(messages, **kwargs)
        tokenizer = types.SimpleNamespace(unk_token_id=self.tokenizer.unk_token_id, apply_chat_template=render)
        result = runner.prepare_prompts(self.rows, tokenizer, 'dictionary-faithfulness-v1')
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
                runner.prepare_prompts([row], self.tokenizer, 'dictionary-faithfulness-v1')
        row = copy.deepcopy(self.rows[0])
        text, ids = 'mock capacity rendering', [7] * 8192
        row.update(input_tokens=len(ids), rendered_text_sha256=runner.sha(text.encode()),
            input_ids_sha256=runner.sha(runner.canonical(ids)))
        tokenizer = types.SimpleNamespace(unk_token_id=3,
            apply_chat_template=lambda messages, **kwargs: ids if kwargs['tokenize'] else text)
        self.assertEqual(len(runner.prepare_prompts([row], tokenizer, 'dictionary-faithfulness-v1')[row['id']]) + 4096, 12288)
        overflow = dict(row, input_tokens=8193)
        with self.assertRaises(ValueError): runner.prepare_prompts([overflow], tokenizer, 'dictionary-faithfulness-v1')
        ids[0] = tokenizer.unk_token_id
        with self.assertRaisesRegex(ValueError, 'never truncate'):
            runner.prepare_prompts([row], tokenizer, 'dictionary-faithfulness-v1')

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
        for protocol in ('components-v1','own-analysis-v1','dictionary-ab-v1'):
            with self.assertRaises(ValueError): runner.dictionary_settings({'protocol':protocol})
        controls = runner.dictionary_controls()
        self.assertEqual(30 * controls['max_generation_seconds'] + controls['export_overhead_seconds'] + controls['tail_reserve_seconds'], 3420)

    def generation(self, root, kind='success', seconds=3600, clock=None, publish=None):
        output = root / kind; output.mkdir()
        (root / 'model-inputs.jsonl').write_bytes(self.inputs.read_bytes())
        (root / 'contract.json').write_bytes(self.inputs.with_name('contract.json').read_bytes())
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
            self.assertEqual([r['id'] for r in rows], runner.schedule('dictionary-faithfulness-v1'))
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
            accounting = hf_dictionary_faithfulness.reconcile(output, state['schedule'])
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
                self.assertFalse(hf_dictionary_faithfulness.reconcile(output, state['schedule'])['pipeline_complete'])

    def test_fatal_model_error_is_saved_once_without_replacement(self):
        with test_directory() as directory:
            state, model, rows, error, syncs, _ = self.generation(Path(directory), 'fatal')
            self.assertIsInstance(error, RuntimeError)
            self.assertEqual((len(rows), len(model.calls), syncs), (3, 3, 3))
            self.assertEqual(state['unattempted_output_ids'], runner.schedule('dictionary-faithfulness-v1')[3:])
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
            self.assertEqual(state['unattempted_output_ids'], runner.schedule('dictionary-faithfulness-v1')[1:])
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
            self.assertEqual(state['unattempted_output_ids'], runner.schedule('dictionary-faithfulness-v1')[1:])
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
                self.assertEqual(saved['active_output_id'], runner.schedule('dictionary-faithfulness-v1')[0] if fail_at == 1 else None)
                self.assertEqual(saved['unattempted_output_ids'], runner.schedule('dictionary-faithfulness-v1')[1:])
                accounting = hf_dictionary_faithfulness.reconcile(output, state['schedule'])
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
                    base='mock_base', bundle='mock_bundle', adapter='mock_adapter', inputs=self.inputs, contract=self.inputs.with_name('contract.json'),
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
                        self.assertLessEqual(max(map(len, prefill.call_args.args[1].values())), 8192)
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
                self.assertEqual(state['contract_sha256'], runner.DICTIONARY_CONTRACT_SHA256)
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
            self.assertEqual(state['unattempted_output_ids'], runner.schedule('dictionary-faithfulness-v1')[1:])


hf = hf_dictionary_faithfulness
INPUTS = ROOT / 'resources/local/dictionary-faithfulness-20261005/model-inputs.jsonl'
owned_directory = test_directory
from cloud_pilot.training_admission import sdk_spec

class FaithfulnessWrapperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec,cls.receipt = hf.prepare(INPUTS,run_id='e'*32,protocol='dictionary-faithfulness-v1')

    def test_actual_sdk_and_self_contained_command(self):
        restored=sdk_spec(json.loads(json.dumps(self.spec,default=lambda x:x.to_dict())))
        self.assertEqual(restored['timeout'],'120m')
        self.assertEqual([v.read_only for v in restored['volumes']],[True,True,False])
        command=ast.parse(restored['command'][3])
        payload=ast.literal_eval(command.body[1].value.args[0].args[0])
        import gzip,base64
        code=gzip.decompress(base64.b64decode(payload)).decode()
        self.assertEqual(hashlib.sha256(code.encode()).hexdigest(),self.receipt['decoded_command_sha256'])
        tree=ast.parse(code)
        # Definitions, embedded settings and scripts execute; intercept only the
        # final execute call. No cloud action is present in the decoded program.
        namespace={}
        exec(compile(ast.Module(body=tree.body[:-1],type_ignores=[]),'prepared','exec'),namespace)
        self.assertEqual(namespace['dictionary_schedule'](),hf.dictionary_schedule())
        self.assertEqual(namespace['dictionary_controls'](),hf.dictionary_controls())
        self.assertEqual(ast.literal_eval(tree.body[-1].value.args[0])['native_timeout_minutes'],120)

    def test_pin_refuses_any_input_change(self):
        with owned_directory() as directory:
            path=Path(directory)/'inputs.jsonl';path.write_bytes(INPUTS.read_bytes()+b'\n')
            with self.assertRaises(ValueError):
                hf.prepare(path,run_id='e'*32,protocol='dictionary-faithfulness-v1',
                    contract_path=INPUTS.with_name('contract.json'))

    def test_pin_refuses_any_contract_change(self):
        with owned_directory() as directory:
            path=Path(directory)/'contract.json'
            path.write_bytes(INPUTS.with_name('contract.json').read_bytes()+b'\n')
            with self.assertRaises(ValueError):
                hf.prepare(INPUTS,run_id='e'*32,contract_path=path)

    def lifecycle(self,kind):
        with owned_directory() as directory:
            root=Path(directory);mount=root/'mount';incoming=root/'input';stage=root/'stage'
            incoming.mkdir();stage.mkdir()
            (incoming/self.receipt['inputs_name']).write_bytes(INPUTS.read_bytes())
            (incoming/self.receipt['contract_name']).write_bytes(INPUTS.with_name('contract.json').read_bytes())
            settings=copy.deepcopy(self.receipt)
            settings['bootstrap_hashes']={'runtime.py':hashlib.sha256(b'bootstrap').hexdigest()}
            clock=[1000.0];sleeps=[];alarms=[]
            def mapped(value):
                return mount if value=='/output' else incoming if value=='/input' else Path(value)
            def extract(source,dest,*args):
                dest.mkdir();(dest/'runtime.py').write_bytes(b'bootstrap')
            def body(settings,stage,deadline,evidence):
                self.assertEqual(deadline,7600.0)
                if kind=='bootstrap':raise RuntimeError('bootstrap failure')
                (evidence/'observed.txt').write_text('small recovered evidence')
                clock[0] += 6500 if kind=='late' else 100
                if kind=='child':raise TimeoutError('child safely stopped')
            actual_publish=hf.publish_checked
            def publish(source,dest,deadline,identity):
                self.assertEqual(deadline,7960.0)
                if kind=='export':raise TimeoutError('export deadline')
                result=actual_publish(source,dest,deadline,identity)
                if kind=='corrupt':
                    raise AssertionError('Corruption must be injected before actual readback')
                return result
            def sleep(seconds):sleeps.append(seconds);clock[0]+=seconds
            with patch.object(hf,'Path',side_effect=mapped),patch.object(hf.tempfile,'mkdtemp',return_value=str(stage)),\
                 patch.object(hf,'safe_extract',side_effect=extract),patch.object(hf,'component_body',side_effect=body),\
                 patch.object(hf,'publish_checked',side_effect=publish),patch.object(hf.shutil if hasattr(hf,'shutil') else __import__('shutil'),'disk_usage',return_value=types.SimpleNamespace(free=100*1024**3)),\
                 patch.object(hf.time,'monotonic',side_effect=lambda:clock[0]),patch.object(hf.time,'sleep',side_effect=sleep),\
                 patch.object(hf.signal,'SIGALRM',14,create=True),patch.object(hf.signal,'signal'),\
                 patch.object(hf.signal,'alarm',side_effect=lambda n:alarms.append(n),create=True),patch.object(hf,'emit'),\
                 patch.object(hf.hf_baseline,'emit'):
                try:
                    if kind=='corrupt':
                        original_hash=hf.file_sha256
                        def changed_hash(path):
                            return 'f'*64 if Path(path).is_relative_to(mount/'final') else original_hash(path)
                        # First publication uses the original helper's hashes;
                        # wrapper readback observes mismatched mounted bytes.
                        with patch.object(hf,'file_sha256',side_effect=changed_hash):
                            hf.execute(settings,{},'')
                    else:
                        hf.execute(settings,{},"raise RuntimeError('bootstrap failure')" if kind=='bootstrap' else '')
                except (RuntimeError,TimeoutError,ValueError) as error:
                    caught=error
                else:caught=None
            if kind in ('normal','late'):self.assertIsNone(caught)
            else:self.assertIsNotNone(caught)
            self.assertEqual(alarms[-1],0)
            if kind in ('normal','bootstrap','child','late'):
                self.assertEqual(sleeps,[60])
                self.assertEqual(alarms[-1],0)
                closed=json.loads((mount/'final/manifest.json').read_bytes())
                self.assertFalse(closed['remote_inventory_verified'])
                self.assertFalse(closed['training_performed'])
                self.assertEqual(closed['optimizer_updates'],0)
            return caught,alarms

    def test_normal_and_failure_full_export_lifecycle(self):
        for kind in ('normal','bootstrap','child','late','export','corrupt'):
            with self.subTest(kind=kind):self.lifecycle(kind)

    def test_invalid_timing_rejected_before_any_signal_or_mount(self):
        for field,value in (('compute_seconds',6601),('internal_seconds',7200),('native_timeout_minutes',60),
                ('compute_seconds',6600.0),('inputs_sha256','f'*64),('contract_sha256','f'*64),
                ('precision','nf4'),('training',True),('automatic_retry',True),('planned_outputs',True),
                ('schedule',hf.dictionary_schedule()[::-1])):
            bad=copy.deepcopy(self.receipt);bad[field]=value
            with patch.object(hf.signal,'signal') as signal:
                with self.assertRaises(ValueError):hf.execute(bad,{},'')
                signal.assert_not_called()

    def test_complete_interrupted_and_corrupted_fixed_denominator_recovery(self):
        original={r['id']:r for r in map(json.loads,INPUTS.read_bytes().splitlines())}
        order=hf.dictionary_schedule()
        rows=[]
        for i,key in enumerate(order):
            r=original[key]
            rows.append(dict(id=key,case_id=r['case_id'],condition=r['arm'],arm=r['arm'],
                work_id=r['work_id'],source_sha256=r['source_sha256'],sequence=i+1,status='success',
                identity_sha256='0'*64,model_call_started=True,text='mock output',
                output_sha256=hashlib.sha256(b'mock output').hexdigest(),output_tokens=2,output_token_ids=[7,1],
                hit_output_cap_without_eos=False,stop_reason=None,messages=r['messages'],
                messages_sha256=hashlib.sha256(json.dumps(r['messages'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
                input_tokens=r['input_tokens'],rendered_input_ids_sha256=r['input_ids_sha256'],rendered_sha256=r['rendered_text_sha256']))
        state=dict(self.receipt,identity_sha256='0'*64,status='completed',scheduled_outputs=30,
            attempted_outputs=30,recorded_outputs=30,model_calls_started=30,active_output_id=None,
            unattempted_output_ids=[],adapter_unchanged_after_inference=True)
        with owned_directory() as directory:
            root=Path(directory);output=root/'evaluation';output.mkdir()
            (root/'model-inputs.jsonl').write_bytes(INPUTS.read_bytes())
            (root/'contract.json').write_bytes(INPUTS.with_name('contract.json').read_bytes())
            def save(current,records):
                (output/'run.json').write_text(json.dumps(current),encoding='utf8')
                (output/'predictions.jsonl').write_bytes(b''.join((json.dumps(r,ensure_ascii=False)+'\n').encode() for r in records))
            save(state,rows)
            self.assertTrue(hf.reconcile(output,order)['pipeline_complete'])
            for mutation in ('empty','output_bool','dispatch','inputhash','work','message','stop','cap','tail'):
                bad=copy.deepcopy(rows)
                if mutation=='empty':bad[0].update(text='',output_sha256=hashlib.sha256(b'').hexdigest())
                if mutation=='output_bool':bad[0].update(output_tokens=True,output_token_ids=[1])
                if mutation=='dispatch':bad[0]['model_call_started']=False
                if mutation=='inputhash':bad[0]['rendered_input_ids_sha256']='f'*64
                if mutation=='work':bad[0]['work_id']='parsig:517'
                if mutation=='message':bad[0]['messages'][0]['content']+='changed'
                if mutation=='stop':bad[0]['stop_reason']='case_timeout'
                if mutation=='cap':bad[0]['hit_output_cap_without_eos']=True
                save(state,bad)
                if mutation=='tail':
                    with (output/'predictions.jsonl').open('ab') as stream:stream.write(b'{partial')
                with self.subTest(mutation=mutation),self.assertRaises(ValueError):hf.reconcile(output,order)
            interrupted=dict(state,status='running',attempted_outputs=4,recorded_outputs=3,
                model_calls_started=4,active_output_id=order[3],unattempted_output_ids=order[4:])
            save(interrupted,rows[:3])
            accounted=hf.reconcile(output,order)
            self.assertEqual(len(accounted['per_output_status']),30)
            self.assertEqual(accounted['per_output_status'][order[3]],'interrupted_output_unknown')
            self.assertEqual(sum(s=='unattempted' for s in accounted['per_output_status'].values()),26)
            self.assertFalse(accounted['pipeline_complete'])
            # Durable JSONL may be ahead of run.json by one commit; never retry.
            save(interrupted,rows[:4])
            self.assertFalse(hf.reconcile(output,order)['pipeline_complete'])

if __name__ == '__main__':
    unittest.main()
