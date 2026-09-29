@'
import json,os,hashlib,re
from pathlib import Path,PurePosixPath
from datetime import datetime,timezone
import httpx
from huggingface_hub import HfApi,set_client_factory
os.environ['HF_XET_CACHE']=str(Path('resources/local/hf-xet-cache').resolve());set_client_factory(lambda:httpx.Client(timeout=15,follow_redirects=True))
exp=Path('experiments/train-fit-20260927'); local=Path('resources/local/hf-train-fit-20260927'); ex=json.loads((exp/'execution.json').read_text()); ident=json.loads((local/'preparation.json').read_text());prefix=ident['output_prefix'];api=HfApi();bucket='Mojionix/pahlavi-pilot'
logs='\n'.join(api.fetch_job_logs(job_id=ex['job_id'],namespace='Mojionix',follow=False));(local/'provider.log').write_text(logs,encoding='utf-8')
ready=[json.loads(l[l.index('{'):]) for l in logs.splitlines() if '"stage": "ready_to_persist"' in l]
assert len(ready)==1,'Exact single publication log required';ready=ready[0]
assert type(ready['manifest_bytes']) is int and 0<ready['manifest_bytes']<=1024**2
entries={f.path:f for f in api.list_bucket_tree(bucket,prefix=prefix+'/',recursive=True) if hasattr(f,'size')}
remote=entries.get(prefix+'/manifest.json');assert remote and remote.size==ready['manifest_bytes'] and remote.xet_hash,'Manifest not yet committed'
out=exp/'recovered';out.mkdir(exist_ok=True)
api.download_bucket_files(bucket,[(remote,out/'manifest.json')],raise_on_missing_files=True)
data=(out/'manifest.json').read_bytes();assert hashlib.sha256(data).hexdigest()==ready['manifest_sha256'];m=json.loads(data);assert m==ready['manifest']
for k in ['run_id','inputs_name','inputs_sha256','bundle_name','bundle_sha256','trained_prefix','trained_manifest_sha256','adapter_files','bootstrap_hashes','script_hashes','scheduled_outputs','compute_seconds','internal_seconds','export_reserve_seconds','maximum_wait_seconds','source_control_name','source_control_sha256','expected_token_map_sha256']:
 assert m[k]==ident[k],k
assert m['operation']=='qualified_train_fit' and m['training_performed'] is False and m['fit_status'] in ('complete','incomplete')
allowed={'base-provenance.json','bundle-manifest.json','trained-manifest.json','fit-status.json','fit/run.json','fit/results.jsonl','source-control.json'}
assert 1<=len(m['files'])<=7 and set(m['files'])<=allowed and 'fit-status.json' in m['files']
assert sum(v['bytes'] for v in m['files'].values())<=16*1024**2
assert set(entries)=={prefix+'/manifest.json',*(prefix+'/'+n for n in m['files'])}
files=[]
for n,v in m['files'].items():
 p=PurePosixPath(n);assert not p.is_absolute() and '..' not in p.parts and p.as_posix()==n and '\\' not in n and ':' not in n
 assert type(v['bytes']) is int and v['bytes']>=0 and re.fullmatch('[a-f0-9]{64}',v['sha256'])
 entry=entries[prefix+'/'+n];assert entry.size==v['bytes'] and entry.xet_hash,'Artifact not yet committed'
 target=out/n;target.parent.mkdir(parents=True,exist_ok=True);files.append((entry,target))
api.download_bucket_files(bucket,files,raise_on_missing_files=True)
for n,v in m['files'].items():
 data=(out/n).read_bytes();assert len(data)==v['bytes'] and hashlib.sha256(data).hexdigest()==v['sha256'],n
proof={'utc':datetime.now(timezone.utc).isoformat(),'job_id':ex['job_id'],'run_id':ex['run_id'],'manifest_sha256':ready['manifest_sha256'],'files':m['files'],'full_sha_recovery_verified':True,'file_count':len(m['files']),'total_bytes':sum(v['bytes'] for v in m['files'].values()),'fit_status':m['fit_status'],'provider_inventory_committed':True,'model_weights_downloaded':False}
(exp/'recovery.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
print(json.dumps(proof))
'@ | & resources/local/hf-client-venv/Scripts/python.exe -B -X utf8 -
