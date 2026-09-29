"""Offline tiny-model numerical, order, admission, and exact transport checks."""
import ast
import base64
import copy
from datetime import datetime, timedelta, timezone
import gzip
import json
import os
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch
import uuid

ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / 'resources/local/mixed-supervision-20260929/server-tests'
SCRATCH.mkdir(parents=True, exist_ok=True)
os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_HUB_DISABLE_TELEMETRY='1',
                  HF_HOME=str(SCRATCH / 'hf-cache'), TEMP=str(SCRATCH), TMP=str(SCRATCH))
tempfile.tempdir = str(SCRATCH)
sys.path.extend([str(ROOT / 'resources/local/train-fit-deps'),
                 str(ROOT / 'resources/local/hf-client-venv/Lib/site-packages')])
import torch
from transformers import Gemma4Config, Gemma4TextConfig, Gemma4ForConditionalGeneration
from peft import LoraConfig, get_peft_model
from . import mixed_train as core, mixed_run, hf_mixed


def model():
    torch.set_num_threads(1)
    torch.manual_seed(42)
    config = Gemma4Config(text_config=Gemma4TextConfig(vocab_size=32, hidden_size=32, intermediate_size=48,
        num_hidden_layers=2, num_attention_heads=4, num_key_value_heads=2, head_dim=8, global_head_dim=8,
        max_position_embeddings=64, vocab_size_per_layer_input=32, hidden_size_per_layer_input=0,
        layer_types=['sliding_attention', 'full_attention'], sliding_window=16, final_logit_softcapping=30.0),
        vision_config=None, audio_config=None)
    config._attn_implementation = 'eager'
    result = get_peft_model(Gemma4ForConditionalGeneration(config), LoraConfig(r=2, lora_alpha=4,
        target_modules=['q_proj', 'v_proj'], lora_dropout=0.0, task_type='CAUSAL_LM', bias='none'))
    result.config.use_cache = result.config.text_config.use_cache = False
    with torch.no_grad():
        for name, p in result.named_parameters():
            if 'lora_B' in name: p.normal_(0.0, 0.2)
    return result


SETTINGS = dict(seed=3407, max_steps=2, gradient_accumulation_steps=16, learning_rate=1e-3,
                warmup_steps=0, bf16=False, gradient_checkpointing=False)
ROWS = [dict(id='a', task='historical-control-fa', input_ids=[2, 3, 4, 7, 1], attention_mask=[1]*5,
             labels=[-100]*3+[7, 1], prompt_tokens=3),
        dict(id='b', task='historical-control-fa', input_ids=[2, 11, 12, 13, 14, 15, 16, 1], attention_mask=[1]*8,
             labels=[-100]*3+[13, 14, 15, 16, 1], prompt_tokens=3)]*16


class MixedTest(unittest.TestCase):
    def setUp(self):
        self.out = SCRATCH / uuid.uuid4().hex
        self.deadline = (datetime.now(timezone.utc)+timedelta(minutes=4)).isoformat()

    def run_core(self, loaded=None, **kwargs):
        return core.train_one(loaded or model(), copy.deepcopy(ROWS), SETTINGS, self.out, self.deadline,
                              canary_steps=1, admission=kwargs.get('admission', lambda *a: {'admitted': True}))

    def test_numerical_per_example_mean_and_order(self):
        trained, manual = model(), model()
        result = self.run_core(trained)
        params = list(core.core.trainables(manual).values())
        optimizer = torch.optim.AdamW(params, lr=1e-3, weight_decay=0.0, betas=(0.9,0.999), eps=1e-8)
        manual.train()
        for step in range(2):
            optimizer.zero_grad(set_to_none=True)
            optimizer.param_groups[0]['lr'] = 1e-3 * (1-step/2)
            for row in ROWS[step*16:(step+1)*16]:
                inputs = {k:torch.tensor([row[k]]) for k in ('input_ids','labels','attention_mask')}
                response = manual(**inputs)
                loss = torch.nn.functional.cross_entropy(response.logits[:,:-1].float().reshape(-1,32),
                        inputs['labels'][:,1:].reshape(-1), ignore_index=-100, reduction='mean')
                (loss/16).backward()
            torch.nn.utils.clip_grad_norm_(params,1.0)
            optimizer.step()
        for key, p in core.core.trainables(trained).items():
            torch.testing.assert_close(p, core.core.trainables(manual)[key], atol=2e-7, rtol=2e-6)
        self.assertEqual(result['ordered_ids'], [r['id'] for r in ROWS])
        self.assertTrue(result['fresh_optimizer'])
        self.assertEqual(result['completed_steps'], 2)

    def test_order_mutation(self):
        from transformers import Trainer
        original=Trainer.get_train_dataloader
        def corrupt(t):
            t.train_dataset=list(reversed(t.train_dataset))
            return original(t)
        with patch.object(Trainer,'get_train_dataloader',corrupt), self.assertRaisesRegex(ValueError,'order/content'):
            self.run_core()

    def test_nonfinite(self):
        loaded=model()
        handle=next(iter(core.core.trainables(loaded).values())).register_hook(lambda g:g*float('nan'))
        try:
            with self.assertRaises(FloatingPointError): self.run_core(loaded)
        finally: handle.remove()
        self.assertEqual(json.loads((self.out/'run.json').read_text())['completed_steps'],0)

    def test_canary_denial_preserves_adapter(self):
        with self.assertRaises(TimeoutError): self.run_core(admission=lambda *a:{'admitted':False})
        run=json.loads((self.out/'run.json').read_text())
        self.assertEqual(run['completed_steps'],1)
        self.assertEqual(run['status'],'incomplete')
        self.assertTrue((self.out/'bounded-adapter-step20/adapter_model.safetensors').is_file())
        self.assertFalse((self.out/'adapter').exists())

    def test_expired_and_invalid(self):
        self.deadline='2000-01-01T00:00:00+00:00'
        with self.assertRaises(TimeoutError):self.run_core()
        self.assertFalse(self.out.exists())
        rows=copy.deepcopy(ROWS); rows[0]['labels'][0]=2
        with self.assertRaises(ValueError):core.validate_rows(rows,SETTINGS)

    def test_forecast_and_exact_artifact(self):
        train=ROOT/'resources/local/training-ready-v2-20260929/data/train.jsonl'
        manifest=ROOT/'experiments/training-ready-v2-20260929/data-manifest.json'
        spec, settings=hf_mixed.prepare(train,manifest,'1'*32)
        rows,_=mixed_run.read_data(train,manifest,settings)
        self.assertFalse(core.forecast(rows,20,1000,1200)['admitted'])
        self.assertTrue(core.forecast(rows,20,100,3500)['admitted'])
        with self.assertRaises(ValueError):core.forecast(rows,20,float('nan'),3000)
        transport=ast.parse(spec['command'][3])
        payload=ast.literal_eval(transport.body[1].value.args[0].args[0])
        code=gzip.decompress(base64.b64decode(payload)).decode()
        program=ast.parse(code)
        program.body.pop()
        namespace={}
        exec(compile(program,'exact-mixed-artifact','exec'),namespace)
        self.assertTrue(callable(namespace['execute_mixed']))
        self.assertEqual(namespace['settings'], {k: v for k,v in settings.items() if k not in {'output_prefix','prepared_not_submitted','decoded_command_sha256','command_sha256','command_arg_utf8_bytes','command_total_utf8_bytes_with_nul'}})
        self.assertEqual(spec['timeout'],'100m')
        self.assertEqual(settings['internal_seconds']-settings['compute_seconds'],600)
        for name,entry in namespace['scripts'].items():
            data=base64.b64decode(entry['content'])
            self.assertEqual(data,(ROOT/'cloud_pilot'/name).read_bytes())
            compile(data,name,'exec')
        self.assertEqual(settings['scheduled_outputs'],24)

    def test_corrected_data_rejects_bad_admission_before_model_load(self):
        train=ROOT/'resources/local/training-ready-v2-20260929/data/train.jsonl'
        manifest=ROOT/'experiments/training-ready-v2-20260929/data-manifest.json'
        original_rows=[json.loads(s) for s in train.read_text('utf-8').splitlines()]
        original_manifest=json.loads(manifest.read_text('utf-8'))
        self.out.mkdir()
        path, receipt=self.out/'train.jsonl', self.out/'manifest.json'
        for case in ('duplicate_id','failed_status','out_of_vocabulary','unknown_token',
                     'wrong_terminator','duplicate_prefix','wrong_tokenizer'):
            with self.subTest(case=case):
                rows, m=copy.deepcopy(original_rows), copy.deepcopy(original_manifest)
                if case=='duplicate_id': rows[1]['id']=rows[0]['id']
                elif case=='failed_status': m['status']='FAIL'
                elif case=='out_of_vocabulary': rows[0]['input_ids'][0]=262144
                elif case=='unknown_token': rows[0]['input_ids'][0]=3
                elif case=='wrong_terminator':
                    rows[0]['input_ids'][-1]=rows[0]['labels'][-1]=108
                elif case=='duplicate_prefix':
                    identifier=rows[1]['id']; rows[1]=copy.deepcopy(rows[0]); rows[1]['id']=identifier
                elif case=='wrong_tokenizer': m['tokenizer_sha256']={}
                path.write_text(''.join(json.dumps(r)+'\n' for r in rows),encoding='utf-8')
                m['outputs']['train.jsonl'].update(sha256=mixed_run.runtime.digest(path),bytes=path.stat().st_size)
                m['pilot']['selected_ids_in_order']=[r['id'] for r in rows]
                receipt.write_text(json.dumps(m),encoding='utf-8')
                settings=dict(train_sha256=mixed_run.runtime.digest(path),data_manifest_sha256=mixed_run.runtime.digest(receipt))
                with self.assertRaises(ValueError): mixed_run.read_data(path,receipt,settings)
        with self.assertRaisesRegex(ValueError,'Corrected and validated v2'):
            hf_mixed.prepare(ROOT/'resources/local/mixed-supervision-20260929/data/train.jsonl',
                             ROOT/'experiments/mixed-supervision-20260929/data-manifest.json','2'*32)

    def test_candidate_generation_and_failure_no_retry(self):
        class Stub(torch.nn.Module):
            def __init__(self, fail_at=None):
                super().__init__(); self.calls=0; self.active=None; self.fail_at=fail_at
            def set_adapter(self, name):self.active=name
            def get_model_status(self):
                return SimpleNamespace(enabled=True, active_adapters=[self.active], merged_adapters=[], available_adapters=['candidate'])
            def generate(self, **kwargs):
                self.calls+=1
                if self.calls==self.fail_at:raise RuntimeError('injected generation failure')
                assert kwargs['max_new_tokens']==4096 and kwargs['do_sample'] is False and kwargs['num_beams']==1
                return torch.cat([kwargs['input_ids'],torch.tensor([[8,1]])],dim=1)
        rows=mixed_run.frozen.read_inputs(ROOT/'experiments/dev-diagnostic-20260927/inputs.jsonl')
        identity={'adapters':{'candidate':{'files':{'adapter_model.safetensors':'1'*64}}}}
        prepared={r['id']:[2,3,4] for r in rows}
        tokenizer=SimpleNamespace(decode=lambda *a,**kw:'test translation')
        with patch.object(mixed_run.qualified,'prefill_canary',return_value={'status':'passed'}):
            loaded=Stub()
            result=mixed_run.generate_candidate(loaded,tokenizer,rows,prepared,self.out,identity,self.deadline,device='cpu')
            self.assertEqual((loaded.calls,result['completed_outputs'],result['completed_cases']),(24,24,24))
            failed=SCRATCH/uuid.uuid4().hex
            loaded=Stub(3)
            with self.assertRaisesRegex(RuntimeError,'injected generation'):
                mixed_run.generate_candidate(loaded,tokenizer,rows,prepared,failed,identity,self.deadline,device='cpu')
            run=json.loads((failed/'run.json').read_text())
            self.assertEqual((loaded.calls,run['attempted_outputs'],run['recorded_outputs']),(3,3,3))
            self.assertEqual(run['status'],'incomplete')


if __name__=='__main__': unittest.main()
