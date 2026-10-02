"""CPU checks for packet identity, exact rendering and deadline admission."""
import json
from pathlib import Path
from unittest.mock import patch
import unittest
from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import MagicMock
from . import dose_run as runner


class PacketChecks(unittest.TestCase):
    def test_packet_and_rendering(self):
        row = {'case_id': 'x', 'module': 'learning', 'messages': [{'role': 'user', 'content': 'fixed'}], 'arms': ['reference','dose384']}
        with patch.object(runner.runtime, 'digest', return_value='abc'), patch.object(Path, 'read_text', return_value=json.dumps(row)):
            path = Path('inputs.jsonl')
            settings = {'inputs_sha256': runner.runtime.digest(path), 'expected_outputs': 2,
                'evaluation_schedule': ['x:reference','x:dose384'],
                'generation_by_module': {'learning': runner.learning.GENERATION},
                'prompt_identities': {'x': {'input_tokens':2,'rendered_input_ids_sha256':runner.qualified.sha(runner.qualified.canonical([2,3]))}}}
            rows, schedule = runner.read_packet(path, settings)
            class Tokenizer:
                def apply_chat_template(self, messages, **kwargs):
                    self.messages, self.kwargs = messages, kwargs
                    return [2,3]
            tokenizer = Tokenizer()
            self.assertEqual(runner.prepare_prompts(rows, tokenizer, 1024, settings), {'x': [2,3]})
            self.assertEqual(tokenizer.messages, row['messages'])
            self.assertFalse(tokenizer.kwargs['enable_thinking'])
            settings['evaluation_schedule'].reverse()
            with self.assertRaises(ValueError):
                runner.read_packet(path, settings)

    def test_reserve(self):
        with self.assertRaises(TimeoutError):
            runner.reserve_guard('2999-01-01T00:00:00Z', 10**15)

    def test_first_attempt_failure_is_durable_and_never_retried(self):
        import sys
        states, records = [], []
        stream = MagicMock()
        stream.__enter__.return_value = stream
        stream.write.side_effect = records.append
        tokens = SimpleNamespace(shape=(1, 2))
        torch = SimpleNamespace(tensor=lambda *a, **k: tokens, ones_like=lambda t: t,
            bfloat16='bf16', autocast=lambda **k: nullcontext(), inference_mode=nullcontext)
        transformers = SimpleNamespace(DynamicCache=lambda: None, StoppingCriteriaList=list, set_seed=lambda s: None)
        model = SimpleNamespace(generate=MagicMock(side_effect=RuntimeError('first attempt failed')))
        row = {'case_id':'x','module':'learning','prompt':'fixed','arms':['reference']}
        settings = {'generation_by_module': {'learning':runner.learning.GENERATION},
            'canary_seconds':60,'finalization_seconds':60}
        identity = {'adapters': {'reference': {'adapter_model.safetensors':'abc'}}}
        def save(path, state):
            states.append(json.loads(json.dumps(state)))
        with patch.dict(sys.modules, {'torch':torch,'transformers':transformers}), \
                patch.object(Path,'mkdir'), patch.object(Path,'open',return_value=stream), \
                patch.object(runner.runtime,'write_json',side_effect=save), patch.object(runner.os,'fsync'), \
                patch.object(runner,'select_adapter'), patch.object(runner.old,'emit'), \
                patch.object(runner.qualified,'prefill_canary',return_value={'status':'passed','elapsed_seconds':1}):
            with self.assertRaisesRegex(RuntimeError,'first attempt failed'):
                runner.generate(model,None,[(row,'reference')],{'x':[2,3]},'unused',identity,
                    '2999-01-01T00:00:00Z',settings,available=('reference',),allocation_seconds=2400)
        self.assertEqual(model.generate.call_count,1)
        self.assertEqual(json.loads(records[0])['status'],'error')
        self.assertTrue(any(s['active_output_id']=='x:reference' and s['attempted_outputs']==1 for s in states))
        self.assertEqual(states[-1]['status'],'incomplete')
        self.assertEqual(states[-1]['recorded_outputs'],1)
        self.assertEqual(states[-1]['unattempted_output_ids'],[])

    def test_real_peft_unload_and_four_named_adapter_reload(self):
        from .test_contextual_train import model, SCRATCH
        from peft import PeftModel
        import uuid
        output = SCRATCH / ('dose-runtime-' + uuid.uuid4().hex)
        trained = model()
        trained.save_pretrained(output, safe_serialization=True)
        base = trained.unload()
        self.assertFalse(any('lora_' in name for name, _ in base.named_parameters()))
        loaded = PeftModel.from_pretrained(base, output, adapter_name='reference', local_files_only=True, is_trainable=False)
        for arm in runner.ARMS[1:]:
            loaded.load_adapter(output, adapter_name=arm, local_files_only=True, is_trainable=False)
        for arm in runner.ARMS:
            runner.select_adapter(loaded, arm)
            runner.old.verify_loaded_adapter(loaded, output, arm)

        reloaded_base = loaded.unload()
        self.assertFalse(any('lora_' in name for name, _ in reloaded_base.named_parameters()))
        loaded = PeftModel.from_pretrained(reloaded_base, output, adapter_name='reference', local_files_only=True, is_trainable=False)
        for arm in runner.ARMS[1:]:
            loaded.load_adapter(output, adapter_name=arm, local_files_only=True, is_trainable=False)
        for arm in runner.ARMS:
            runner.select_adapter(loaded, arm)
            runner.old.verify_loaded_adapter(loaded, output, arm)

    def test_assembled_packet_exact_local_tokenizer_rendering(self):
        from .test_contextual_train import ROOT
        from transformers import AutoTokenizer
        folder = ROOT / 'experiments/dose-acquisition-20260930'
        settings = runner.runtime.read_json(folder / 'packet-contract.json')
        rows, schedule = runner.read_packet(folder / 'inputs.jsonl', settings)
        tokenizer = AutoTokenizer.from_pretrained(ROOT / 'resources/local/cloud-pilot-qualified-20260927/tokenizer',
            local_files_only=True, trust_remote_code=False)
        result = runner.prepare_prompts(rows, tokenizer, 131072, settings)
        self.assertEqual(len(result),57)
        self.assertEqual(len(schedule),98)

    def test_real_killed_child_reconciles_active_attempt_without_fake_output(self):
        from .test_contextual_train import SCRATCH
        import subprocess
        import sys
        import uuid
        output = SCRATCH / ('dose-killed-' + uuid.uuid4().hex)
        output.mkdir()
        script = '''import json, os, pathlib, sys, time
p = pathlib.Path(sys.argv[1])
state = dict(status='running',schedule=['x:reference','y:reference','z:reference'],attempted_outputs=2,recorded_outputs=0,active_output_id='y:reference',unattempted_output_ids=['z:reference'],canaries={})
(p/'run.json').write_text(json.dumps(state))
with (p/'predictions.jsonl').open('w') as f:
 f.write(json.dumps(dict(id='x:reference',status='success'))+'\\n'); f.flush(); os.fsync(f.fileno())
print('ready',flush=True)
time.sleep(30)
'''
        child = subprocess.Popen([sys.executable,'-c',script,str(output)],stdout=subprocess.PIPE,text=True)
        try:
            self.assertEqual(child.stdout.readline().strip(),'ready')
            child.kill()
            child.wait(timeout=10)
        finally:
            if child.poll() is None:
                child.kill()
                child.wait(timeout=10)
            child.stdout.close()
        result = runner.reconcile_evaluation(output)
        self.assertEqual(result['status'],'incomplete')
        self.assertEqual(result['attempted_outputs'],2)
        self.assertEqual(result['recorded_outputs'],1)
        self.assertEqual(result['active_incomplete_output_id'],'y:reference')
        self.assertEqual(result['unattempted_output_ids'],['z:reference'])
        self.assertEqual(len((output/'predictions.jsonl').read_text().splitlines()),1)


if __name__ == '__main__':
    unittest.main()
