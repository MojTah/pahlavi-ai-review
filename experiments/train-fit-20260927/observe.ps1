@'
import json,os
from pathlib import Path
from datetime import datetime,timezone
import httpx
from huggingface_hub import HfApi,set_client_factory
os.environ['HF_XET_CACHE']=str(Path('resources/local/hf-xet-cache').resolve());set_client_factory(lambda:httpx.Client(timeout=15,follow_redirects=True))
x=json.loads(Path('experiments/train-fit-20260927/execution.json').read_text()); api=HfApi()
info=api.inspect_job(job_id=x['job_id'],namespace='Mojionix')
logs='\n'.join(api.fetch_job_logs(job_id=x['job_id'],namespace='Mojionix',follow=False)); Path('resources/local/hf-train-fit-20260927/provider.log').write_text(logs,encoding='utf-8')
elapsed=(datetime.now(timezone.utc)-datetime.fromisoformat(x['submitted_utc'])).total_seconds()
lines=logs.splitlines()
progress=[l for l in lines if '"stage":' in l or '"status": "train_fit_attempt_recorded"' in l]
summary={'utc':datetime.now(timezone.utc).isoformat(),'status':info.status.stage,'elapsed_seconds':round(elapsed),'elapsed_compute_estimate_usd':round(elapsed*41667/60/1e6,4),'recorded_outputs':sum('"status": "train_fit_attempt_recorded"' in l for l in lines),'ready_to_persist':any('"stage": "ready_to_persist"' in l for l in lines)}
with Path('resources/local/hf-train-fit-20260927/events.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(summary)+'\n')
print(json.dumps(summary));print('\n'.join(progress[-2:])[:1400]);print('\n'.join(lines[-4:])[:2000])
'@ | & resources/local/hf-client-venv/Scripts/python.exe -B -X utf8 -
