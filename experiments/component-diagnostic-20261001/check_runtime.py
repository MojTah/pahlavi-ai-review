"""Offline renderer, SDK serialization, persistence and interrupted-attempt checks."""
import importlib.util
import json
from pathlib import Path
import sys
import time
import types
import uuid
from contextlib import nullcontext
from datetime import datetime, timedelta, timezone

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'resources/local/hf-client-venv/Lib/site-packages'))
from cloud_pilot import hf_component
from cloud_pilot.training_admission import sdk_spec
import cloud_pilot.runtime as runtime
sys.modules['runtime']=runtime
helper=types.ModuleType('component_helpers')
exec(hf_component.helper_source()[0],helper.__dict__)
helper.emit=lambda *a,**k:None
sys.modules['component_helpers']=helper
spec=importlib.util.spec_from_file_location('component_eval',ROOT/'cloud_pilot/component_eval.py')
runner=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
import torch
from transformers import AutoTokenizer


class Model:
    training=False
    def __init__(self,kind='success'): self.kind,self.calls=kind,0
    def set_adapter(self,arm): assert arm=='reference'
    def requires_grad_(self,value): assert value is False
    def eval(self): self.training=False
    def zero_grad(self,**kwargs): pass
    def parameters(self): return []
    def get_model_status(self):
        return types.SimpleNamespace(enabled=True,active_adapters=['reference'],merged_adapters=[],available_adapters=['reference'])
    def generate(self,**kw):
        self.calls+=1
        assert kw['max_new_tokens']==256 and kw['do_sample'] is False and kw['num_beams']==1
        if self.kind=='exception' and self.calls==3: raise RuntimeError('deliberate interrupted attempt')
        if self.kind=='timeout': kw['stopping_criteria'][0].start-=91
        tail=[7]*256 if self.kind=='cap' else [7,1]
        return torch.cat((kw['input_ids'],torch.tensor([tail])),dim=1)


def main():
    protocol='stages-v1' if sys.argv[1:]==['--stages'] else 'components-v1'
    if sys.argv[1:] not in ([],['--stages']): raise ValueError('Use optional --stages')
    experiment='semantic-stage-diagnostic' if protocol=='stages-v1' else 'component-diagnostic'
    inputs=ROOT/('resources/local/'+experiment+'-20261001/model-inputs.jsonl')
    job,receipt=hf_component.prepare(inputs,run_id='0123456789abcdef0123456789abcdef',protocol=protocol)
    serialized=json.loads(json.dumps(job,default=lambda x:x.to_dict()))
    restored=sdk_spec(serialized)
    assert restored['timeout']=='60m' and len(restored['volumes'])==3
    assert [v.read_only for v in restored['volumes']]==[True,True,False]
    rows=runner.read_inputs(inputs,receipt['inputs_sha256'],protocol)
    order=runner.schedule(protocol)
    assert receipt['schedule']==order and len(set(order))==12
    try: runner.read_inputs(inputs,receipt['inputs_sha256'],'components-v1' if protocol=='stages-v1' else 'stages-v1')
    except ValueError: pass
    else: raise AssertionError('Protocol mismatch admitted')
    tokenizer=AutoTokenizer.from_pretrained(ROOT/'resources/local/cloud-pilot-qualified-20260927/tokenizer',local_files_only=True,trust_remote_code=False)
    prepared=runner.prepare_prompts(rows,tokenizer)
    maximum=json.loads((ROOT/('experiments/'+experiment+'-20261001/packet-manifest.json')).read_bytes())['max_prompt_tokens']
    assert max(map(len,prepared.values()))==maximum
    output_tokenizer=types.SimpleNamespace(decode=lambda *a,**kw:'mock output')
    # Keep owned evidence; Python's private Temp ACL excludes this Windows sandbox.
    with nullcontext(ROOT/'resources/local'/('component-check-'+uuid.uuid4().hex)) as directory:
        root=Path(directory)
        root.mkdir(exist_ok=False)
        for kind in ('success','cap','timeout','exception'):
            output,remote=root/kind,root/(kind+'-mount')
            output.mkdir()
            state=dict(identity_sha256='0'*64,status='running',schedule=order,scheduled_outputs=12,
                attempted_outputs=0,recorded_outputs=0,successful_outputs=0,active_output_id=None,
                unattempted_output_ids=order,last_result=None)
            model=Model(kind)
            deadline=(datetime.now(timezone.utc)+timedelta(minutes=30)).isoformat()
            try: runner.generate(model,output_tokenizer,rows,prepared,output,remote,state,deadline,device='cpu')
            except RuntimeError:
                assert kind=='exception'
                state['status']='incomplete'
                runtime.write_json(output/'run.json',state)
            n=3 if kind=='exception' else 12
            assert model.calls==state['attempted_outputs']==state['recorded_outputs']==n
            records=[json.loads(x) for x in (output/'predictions.jsonl').read_bytes().splitlines()]
            assert len(records)==n and [r['id'] for r in records]==order[:n]
            expected='success' if kind=='success' else 'timeout' if kind=='timeout' else 'error'
            assert records[-1]['status']==expected
            assert len(list(remote.glob('*/manifest.json')))==2*n
            if kind=='exception': assert len(hf_component.reconcile(output,order)['per_output_status'])==12
            try: runner.generate(model,output_tokenizer,rows,prepared,output,remote,state,deadline,device='cpu')
            except FileExistsError: pass
            else: raise AssertionError('Repeated generation must refuse overwrite')
        # Simulate a killed child with a durable start and no committed output.
        state.update(status='running',attempted_outputs=4,recorded_outputs=3,
            active_output_id=order[3],unattempted_output_ids=order[4:])
        runtime.write_json(output/'run.json',state)
        account=hf_component.reconcile(output,order)
        assert account['per_output_status'][order[3]]=='interrupted_output_unknown'
        assert sum(v=='unattempted' for v in account['per_output_status'].values())==8
        # Admission before generation requires the entire remaining 12-output budget.
        short=root/'short'; short.mkdir()
        try: runner.generate(Model(),output_tokenizer,rows,prepared,short,root/'short-mount',state,
            (datetime.now(timezone.utc)+timedelta(seconds=30)).isoformat(),device='cpu')
        except TimeoutError: pass
        else: raise AssertionError('Insufficient complete-panel time was admitted')
        assert not (short/'predictions.jsonl').exists()
    print(json.dumps(dict(status='pass',protocol=protocol,real_tokenizer_receipts=12,maximum_prompt_tokens=maximum,
        mock_generation_scenarios=4,immutable_snapshots=True,interrupted_denominator=12,
        sdk_serialization=True,cloud_gpu_exercised=False)))


if __name__=='__main__': main()
