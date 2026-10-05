"""Freeze a local prospective SDK package; never access credentials or submit."""
import hashlib
import json
from pathlib import Path
import sys
import uuid

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'resources/local/hf-client-venv/Lib/site-packages'))
from cloud_pilot import hf_dictionary_faithfulness
from cloud_pilot.training_admission import sdk_spec

def main():
    destination=Path(__file__).with_name('preview.json')
    if destination.exists():raise ValueError('Refusing replacement of an existing preview; keep its identity')
    inputs=ROOT/'resources/local/dictionary-faithfulness-20261005/model-inputs.jsonl'
    run_id=uuid.uuid4().hex
    spec,receipt=hf_dictionary_faithfulness.prepare(inputs,run_id=run_id,protocol='dictionary-faithfulness-v1')
    serialized=json.loads(json.dumps(spec,default=lambda x:x.to_dict()))
    restored=sdk_spec(serialized)
    assert restored['timeout']=='120m'
    assert [v.read_only for v in restored['volumes']]==[True,True,False]
    folder=ROOT/'resources/local/dictionary-faithfulness-20261005'/run_id
    folder.mkdir(parents=True,exist_ok=False)
    for name,data in {'job-spec.json':serialized,'prepared-receipt.json':receipt}.items():
        (folder/name).write_bytes((json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode())
    evidence={'status':'LOCAL_PREVIEW_ONLY_PAID_HOLD','run_id':run_id,'output_prefix':receipt['output_prefix'],
        'frozen_messages_sha256':receipt['inputs_sha256'],'contract_sha256':receipt['contract_sha256'],
        'timing_contract':receipt['timing_contract'],'decode_controls':receipt['decode_controls'],
        'compute_seconds':6600,'internal_seconds':7020,'native_timeout_minutes':120,
        'script_hashes':receipt['script_hashes'],'helper_origins':receipt['helper_origins'],
        'decoded_command_sha256':receipt['decoded_command_sha256'],
        'command_arg_utf8_bytes':receipt['command_arg_utf8_bytes'],
        'sdk_version':__import__('huggingface_hub').__version__,'sdk_roundtrip':True,
        'files':{name:{'path':(folder/name).relative_to(ROOT).as_posix(),
            'sha256':hashlib.sha256((folder/name).read_bytes()).hexdigest(),'bytes':(folder/name).stat().st_size}
            for name in ('job-spec.json','prepared-receipt.json')},
        'credentials_accessed':False,'provider_called':False,'GPU_exercised':False,
        'submitted':False,'training_performed':False,'optimizer_updates':0,
        'training_admitted':False,'paid_run_admitted':False}
    destination.write_bytes((json.dumps(evidence,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode())
    print(json.dumps({'status':evidence['status'],'run_id':run_id,'preview':str(destination)},ensure_ascii=False))

if __name__=='__main__':main()
