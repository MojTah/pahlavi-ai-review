from pathlib import Path
import os, sys, json, uuid, types, unittest, hashlib, ast, copy, shutil
ROOT=Path(__file__).resolve().parents[3]
SCRATCH=ROOT/'resources/local/contextual-integration-qa'
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1',HF_HOME=str(SCRATCH/'hf-cache'))
sys.path.insert(0,str(ROOT));sys.path.extend([str(ROOT/'resources/local/train-fit-deps'),str(ROOT/'resources/local/hf-client-venv/Lib/site-packages')])

def load_test(name):
    path=ROOT/'cloud_pilot'/f'{name}.py';source=path.read_text(encoding='utf-8')
    # Only relocate tests' scratch; production sources remain unmodified.
    source=source.replace("SCRATCH = ROOT / 'resources/local/contextual-run-check'",f'SCRATCH = Path({str(SCRATCH)!r})')
    module=types.ModuleType('cloud_pilot.'+name);module.__file__=str(path);module.__package__='cloud_pilot'
    sys.modules[module.__name__]=module;exec(compile(source,str(path),'exec'),module.__dict__)
    return module

driver=load_test('test_contextual_run');wrapper=load_test('test_hf_contextual')
def scratch(self):
    p=SCRATCH/uuid.uuid4().hex;p.mkdir();return p
wrapper.ContextualJobTests.scratch=scratch
suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(driver),unittest.defaultTestLoader.loadTestsFromModule(wrapper)])
result=unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful(): raise SystemExit(1)

import torch
from transformers import Gemma4Config,Gemma4TextConfig,Gemma4ForConditionalGeneration
from peft import LoraConfig,get_peft_model,PeftModel
from cloud_pilot import contextual_run as run
torch.set_num_threads(1);torch.manual_seed(73)
cfg=Gemma4Config(text_config=Gemma4TextConfig(vocab_size=32,hidden_size=32,intermediate_size=48,num_hidden_layers=2,num_attention_heads=4,num_key_value_heads=2,head_dim=8,global_head_dim=8,max_position_embeddings=64,vocab_size_per_layer_input=32,hidden_size_per_layer_input=0,layer_types=['sliding_attention','full_attention'],sliding_window=16,final_logit_softcapping=30.0),vision_config=None,audio_config=None)
cfg._attn_implementation='eager'
base=Gemma4ForConditionalGeneration(cfg);base.config.use_cache=base.config.text_config.use_cache=False
initial=copy.deepcopy(base.state_dict())
model=get_peft_model(base,LoraConfig(r=2,lora_alpha=4,target_modules=['q_proj','v_proj'],lora_dropout=0,task_type='CAUSAL_LM',bias='none'))
native=SCRATCH/('native-'+uuid.uuid4().hex);native.mkdir()
with torch.no_grad():
    for n,p in model.named_parameters():
        if 'lora_B' in n:p.normal_(0,.2)
model.save_pretrained(native/'control',safe_serialization=True)
with torch.no_grad():
    for n,p in model.named_parameters():
        if 'lora_B' in n:p.add_(.3)
model.save_pretrained(native/'candidate',safe_serialization=True)
del model
base=Gemma4ForConditionalGeneration(copy.deepcopy(cfg));base.load_state_dict(initial)
model=PeftModel.from_pretrained(base,native/'control',adapter_name='control',local_files_only=True,is_trainable=False)
model.load_adapter(native/'candidate',adapter_name='candidate',local_files_only=True,is_trainable=False)
outputs={}
for arm in ['control','candidate','control']:
    run.verify_loaded_adapter(model,native/arm,arm)
    model.set_adapter(arm);model.requires_grad_(False);model.eval();state=model.get_model_status()
    assert state.enabled is True and state.active_adapters==[arm] and state.merged_adapters==[] and set(state.available_adapters)=={'control','candidate'} and not any(p.requires_grad for p in model.parameters())
    with torch.inference_mode():out=model(input_ids=torch.tensor([[2,3,4]]),use_cache=False).logits.clone()
    if arm in outputs:assert torch.equal(outputs[arm],out)
    outputs[arm]=out
assert not torch.equal(outputs['control'],outputs['candidate'])
run.verify_adapter_architecture(json.loads((native/'candidate/adapter_config.json').read_bytes()),json.loads((native/'control/adapter_config.json').read_bytes()))
with torch.no_grad():
    next(p for n,p in model.named_parameters() if '.candidate.' in n).add_(.125)
try:run.verify_loaded_adapter(model,native/'candidate','candidate')
except ValueError:pass
else:raise AssertionError('Changed loaded adapter was accepted')
print('REAL_TINY_PEFT_SAVED_IDENTITY_NAMED_SWITCH_AND_TAMPER_PASS')

# Execute the exact generated top-level wrapper with a timeout after partial output.
case=wrapper.ContextualJobTests();spec,settings=case.specification();tree=ast.parse(spec['command'][3]);ns={}
exec(compile(ast.Module(body=tree.body[:-1],type_ignores=[]),'generated-definitions','exec'),ns)
root=scratch(case);inputs=root/'input';stage=root/'stage';out=root/'output';inputs.mkdir();stage.mkdir()
shutil.copyfile(wrapper.INPUT,inputs/settings['inputs_name']);shutil.copyfile(wrapper.PACKAGE,inputs/settings['package_name']);shutil.copyfile(ROOT/'resources/local/cloud-pilot-qualified-20260927.zip',inputs/settings['bundle_name'])
calls=[];alarms=[]
def body(settings,stage,deadline,evidence):
    calls.append('body');p=evidence/'contextual/training/control/adapter';p.mkdir(parents=True);(p/'adapter_model.safetensors').write_bytes(b'closed timeout fixture')
    raise TimeoutError('injected bounded compute timeout')
ns.update(Path=lambda v:{'/input':inputs,'/output':out}.get(str(v),Path(v)),exec=lambda s:calls.append('bootstrap'),contextual_body=body,time=types.SimpleNamespace(monotonic=lambda:100,sleep=lambda n:calls.append(('sleep',n))),signal=types.SimpleNamespace(SIGTERM=15,SIGALRM=14,signal=lambda *a:None,alarm=alarms.append),tempfile=types.SimpleNamespace(mkdtemp=lambda **k:str(stage)),emit=lambda *a,**k:None)
from unittest.mock import patch
with patch('shutil.disk_usage',return_value=types.SimpleNamespace(free=100*1024**3)):
    try:exec(compile(ast.Module(body=[tree.body[-1]],type_ignores=[]),'generated-invocation','exec'),ns)
    except TimeoutError:pass
    else:raise AssertionError('Timeout swallowed')
manifest=json.loads((out/'manifest.json').read_bytes());assert manifest['contextual_status']=='incomplete' and manifest['error_type']=='TimeoutError' and not manifest['evaluation_complete']
assert calls.count('body')==1 and alarms==[3900,4200,0] and ('sleep',300) in calls
for name,e in manifest['files'].items():assert hashlib.sha256((out/name).read_bytes()).hexdigest()==e['sha256']
assert (out/'contextual/training/control/adapter/adapter_model.safetensors').read_bytes()==b'closed timeout fixture'
summary={'status':'PASS','tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'windows_permission_retries':driver.FS_RETRY_COUNT,'native_tiny_peft':'PASS','generated_timeout_partial_export':'PASS','source_hashes':{n:hashlib.sha256((ROOT/'cloud_pilot'/n).read_bytes()).hexdigest() for n in ['contextual_run.py','test_contextual_run.py','contextual_train.py','hf_contextual.py','test_hf_contextual.py']}}
(SCRATCH/'result.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary))
