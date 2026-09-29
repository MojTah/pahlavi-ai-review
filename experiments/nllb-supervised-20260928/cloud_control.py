"""Attended single-owner HF lifecycle; one launch POST, only small result downloads."""
import argparse
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / 'resources/local/hf-client-venv/Lib/site-packages'))
from cloud_pilot import hf_nllb as pilot
from cloud_pilot.run_hf_dev_assisted import checked_hardware, submit_once, SubmissionFailed, TERMINAL, shutdown

EXP, BUCKET = pilot.EXP, pilot.BUCKET
PHASE='canary'
LOCAL,RESULTS=pilot.LOCAL/PHASE,EXP/PHASE
RESERVATION = Decimal('3.208353')
sha = pilot.file_sha256
read = lambda path: json.loads(Path(path).read_text('utf-8'))
now = lambda: datetime.now(timezone.utc)
SMALL = {'status.json', 'package-manifest.json', 'driver.log', 'nllb/run.json', 'nllb/schedule.json',
         'nllb/training.jsonl', 'nllb/canary.json', 'nllb/predictions.jsonl', 'nllb/model/training-state.json'}


def write(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def emit(**event):
    line = json.dumps(dict(utc=now().isoformat(), **event))
    print(line, flush=True)
    with (LOCAL / 'events.jsonl').open('a', encoding='utf-8') as stream:
        stream.write(line+'\n')


def check_admission(record, instant):
    age = (instant-datetime.fromisoformat(record['utc'])).total_seconds()
    values = {k: Decimal(str(record[k])) for k in ('balance_usd', 'period_usage_usd')}
    if (not 0 <= age <= 900 or not all(v.is_finite() and v >= 0 for v in values.values())
            or values['balance_usd'] < RESERVATION or values['period_usage_usd'] + RESERVATION > 25
            or record['automatic_recharge_set'] is not False or record['rate_micro_usd_per_minute'] != 41667):
        raise ValueError('Fresh balance, cumulative cap, rate and no recharge required')


def closed_minutes(terminal,execution,recovery):
    if (terminal['job_id']!=execution['job_id'] or terminal['run_id']!=execution['run_id']
            or terminal['run_id']!=recovery['run_id'] or terminal['submitted_utc']!=execution['submitted_utc']
            or terminal['terminal_stage'] not in TERMINAL or terminal['recovered_before_termination'] is not True):
        raise ValueError('Closed canary identity differs')
    finish=datetime.fromisoformat(terminal['terminal_utc'])
    elapsed=(finish-datetime.fromisoformat(execution['submitted_utc'])).total_seconds()
    minutes=math.ceil(elapsed/60)
    if (not math.isfinite(elapsed) or elapsed<=0 or finish<datetime.fromisoformat(recovery['utc'])
            or elapsed!=terminal['elapsed_seconds_upper'] or minutes!=terminal['rounded_minutes_upper']):
        raise ValueError('Closed canary time bound differs')
    return minutes


def continuation_source():
    recovery=read(EXP/'canary/recovery.json')
    prior=read(pilot.LOCAL/'canary/preparation.json')
    canary_record=read(EXP/'canary/recovered/nllb/canary.json')
    terminal_path=EXP/'canary/termination.json'
    minutes=closed_minutes(read(terminal_path),read(EXP/'canary/execution.json'),recovery)
    native=59-minutes
    if not 9<=native<=50:
        raise ValueError('Remaining allocation cannot admit continuation')
    if recovery['nllb_status']!='canary_complete' or recovery['provider_inventory_committed'] is not True:
        raise ValueError('Complete persisted canary required')
    if recovery['persistence_upper_seconds']*1.5>360:
        raise ValueError('Measured persistence does not fit continuation tail')
    forecast=canary_record['max_steady_update_seconds']*1.5*680+canary_record['baseline_seconds']*1.5+canary_record['save_reload_seconds']*2+120
    if not math.isfinite(forecast) or forecast<=0 or forecast>(native-8)*60-120:
        raise ValueError('Measured full training projection does not fit compute allocation with setup reserve')
    return dict(output_prefix=prior['output_prefix'],manifest_sha256=recovery['manifest_sha256'],
                native_minutes=native,closed_minutes=minutes,termination_sha256=sha(terminal_path))


def prepare():
    LOCAL.mkdir(parents=True,exist_ok=True)
    RESULTS.mkdir(parents=True,exist_ok=True)
    if (LOCAL / 'preparation.json').exists():
        raise ValueError('Prepared trial already exists; do not replace identity')
    review = (EXP / 'RUNNER-REVIEW.md').read_text('utf-8')
    if not re.search(r'^Critic verdict: pass(?: with notes)?\s*$', review, re.M):
        raise ValueError('Independent bounded-launch review must pass')
    canary=None
    if PHASE=='continue':
        if not re.search(r'^Continuation verdict: pass(?: with notes)?\s*$',review,re.M):
            raise ValueError('Measured continuation review must pass')
        canary=continuation_source()
    spec, identity = pilot.specification(phase=PHASE,canary=canary)
    write(LOCAL / 'spec.json', dict(spec, volumes=[v.to_dict() for v in spec['volumes']]))
    identity.update(spec_sha256=sha(LOCAL/'spec.json'), controller_sha256=sha(__file__),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        review_sha256=sha(EXP/'RUNNER-REVIEW.md'))
    write(LOCAL/'preparation.json',identity)
    emit(event='prepared_not_submitted',run_id=identity['run_id'],reservation_usd=str(RESERVATION),
         package_bytes=(pilot.LOCAL/'package.zip').stat().st_size)


def upload(api):
    identity=read(LOCAL/'preparation.json')
    package=pilot.LOCAL/'package.zip'
    if sha(package)!=identity['package_sha256']:
        raise ValueError('Package changed')
    name='inputs/'+identity['package_name']
    entries=list(api.get_bucket_paths_info(BUCKET,[name]))
    if not entries:
        api.batch_bucket_files(BUCKET,add=[(package,name)])
    roundtrip=LOCAL/'package-roundtrip.zip'
    api.download_bucket_files(BUCKET,[(name,roundtrip)],raise_on_missing_files=True)
    if sha(roundtrip)!=identity['package_sha256'] or roundtrip.stat().st_size!=package.stat().st_size:
        raise ValueError('Input cloud round trip failed')
    entry=list(api.get_bucket_paths_info(BUCKET,[name]))
    if len(entry)!=1 or not entry[0].xet_hash or entry[0].size!=package.stat().st_size:
        raise ValueError('Input not committed')
    write(LOCAL/'input-transfer.json',dict(path=name,sha256=sha(roundtrip),roundtrip_verified=True,
        bytes=package.stat().st_size,xet_hash=entry[0].xet_hash,utc=now().isoformat()))
    emit(event='package_transfer_verified',bytes=package.stat().st_size)


def launch(api):
    identity=read(LOCAL/'preparation.json')
    canary=continuation_source() if PHASE=='continue' else None
    spec,current=pilot.specification(identity['run_id'],phase=PHASE,canary=canary)
    if (sha(LOCAL/'spec.json')!=identity['spec_sha256'] or sha(__file__)!=identity['controller_sha256']
            or sha(EXP/'RUNNER-REVIEW.md')!=identity['review_sha256']
            or dict(spec,volumes=[v.to_dict() for v in spec['volumes']])!=read(LOCAL/'spec.json')
            or any(identity[k]!=v for k,v in current.items())):
        raise ValueError('Frozen source/specification changed')
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if revision!=identity['source_commit'] or subprocess.check_output(['git','status','--porcelain'],cwd=ROOT).strip():
        raise ValueError('Clean checkpoint required')
    check_admission(read(LOCAL/'admission.json'),now())
    transfer=read(LOCAL/'input-transfer.json')
    if transfer['sha256']!=identity['package_sha256'] or transfer['roundtrip_verified'] is not True:
        raise ValueError('Missing package cloud round trip')
    if api.whoami()['name']!='Mojionix':
        raise ValueError('Wrong account')
    checked_hardware(next(h for h in api.list_jobs_hardware() if h.name=='a100-large'))
    jobs=list(api.list_jobs(namespace='Mojionix',timeout=15))
    if any(j.status.stage not in TERMINAL or (j.labels or {}).get('trial_id')==identity['run_id'] for j in jobs):
        raise ValueError('Active or duplicate job')
    if list(api.list_bucket_tree(BUCKET,prefix=identity['output_prefix']+'/',recursive=True)):
        raise ValueError('Output prefix already used')
    check_admission(read(LOCAL/'admission.json'),now())
    record=dict(run_id=identity['run_id'],source_commit=revision,submitted_utc=now().isoformat(),
        spec_sha256=identity['spec_sha256'],command_sha256=identity['command_sha256'],
        native_timeout=spec['timeout'],phase=PHASE,reservation_usd=str(RESERVATION),execution_owner='/root',prelaunch_jobs=len(jobs))
    write(LOCAL/'submission-started.json',record)
    try:
        job=submit_once(api,spec,identity['run_id'],emit)
    except SubmissionFailed as error:
        try:
            write(LOCAL/'submission-unconfirmed.json',dict(record,known_job_ids=[j.id for j in error.jobs]))
        finally:
            if error.jobs: shutdown(api,error.jobs,emit,time.monotonic())
        raise
    record.update(job_id=job.id,job_url='https://huggingface.co/jobs/Mojionix/'+job.id)
    try:
        write(LOCAL/'execution.json',record)
        write(RESULTS/'execution.json',record)
    except BaseException:
        shutdown(api,[job],emit,time.monotonic())
        raise
    emit(event='submitted',**record)


def observe(api):
    execution=read(LOCAL/'execution.json')
    info=api.inspect_job(job_id=execution['job_id'],namespace='Mojionix')
    logs='\n'.join(api.fetch_job_logs(job_id=execution['job_id'],namespace='Mojionix',follow=False))
    (LOCAL/'provider.log').write_text(logs,encoding='utf-8')
    elapsed=(now()-datetime.fromisoformat(execution['submitted_utc'])).total_seconds()
    emit(event='observation',stage=info.status.stage,elapsed_seconds=round(elapsed),
         compute_estimate_usd=round(elapsed*41667/60/1e6,4),ready_to_persist='"stage": "ready_to_persist"' in logs)
    print('\n'.join(logs.splitlines()[-5:])[:4000])
    return logs


def checked_files(manifest,entries,prefix):
    files=manifest['files']
    if not files or len(files)>35 or sum(v['bytes'] for v in files.values())>24*1024**3:
        raise ValueError('Export inventory/size bound')
    if set(entries)!={prefix+'/manifest.json',*(prefix+'/'+n for n in files)}:
        raise ValueError('Provider inventory incomplete or extra files')
    for name,record in files.items():
        path=PurePosixPath(name)
        if (path.is_absolute() or '..' in path.parts or path.as_posix()!=name or '\\' in name or ':' in name
                or type(record['bytes']) is not int or record['bytes']<0 or not re.fullmatch('[a-f0-9]{64}',record['sha256'])):
            raise ValueError('Unsafe export record')
        if name not in SMALL and not (name.startswith('nllb/model/') and path.parent.as_posix()=='nllb/model'
                and (name.endswith(('.json','.safetensors')) or path.name in ('optimizer.pt','rng.pt'))):
            raise ValueError('Undeclared output file')
        entry=entries[prefix+'/'+name]
        if entry.size!=record['bytes'] or not entry.xet_hash:
            raise ValueError('Artifact not yet committed')
    selected=sorted(set(files)&SMALL)
    if sum(files[n]['bytes'] for n in selected)>16*1024**2 or 'status.json' not in selected:
        raise ValueError('Small-result recovery scope differs')
    return selected


def recover(api):
    logs=observe(api)
    ready=[json.loads(s[s.index('{'):]) for s in logs.splitlines() if '"stage": "ready_to_persist"' in s]
    if len(ready)!=1 or not 0<ready[0]['manifest_bytes']<=1024**2:
        raise ValueError('One closed manifest announcement required')
    ready=ready[0]
    identity=read(LOCAL/'preparation.json')
    prefix=identity['output_prefix']
    entries={f.path:f for f in api.list_bucket_tree(BUCKET,prefix=prefix+'/',recursive=True) if hasattr(f,'size')}
    remote=entries[prefix+'/manifest.json']
    if remote.size!=ready['manifest_bytes'] or not remote.xet_hash:
        raise ValueError('Manifest not committed')
    out=RESULTS/'recovered'
    out.mkdir(exist_ok=True)
    api.download_bucket_files(BUCKET,[(remote,out/'manifest.json')],raise_on_missing_files=True)
    manifest=read(out/'manifest.json')
    if sha(out/'manifest.json')!=ready['manifest_sha256'] or manifest!=ready['manifest']:
        raise ValueError('Persisted manifest differs')
    for key in ('run_id','package_sha256','package_manifest_sha256','train_sha256','dev_sha256','settings',
                'bootstrap_hashes','model','revision','phase','compute_seconds','internal_seconds','native_timeout_minutes','output_prefix'):
        if manifest[key]!=identity[key]: raise ValueError('Output identity differs: '+key)
    if manifest['operation']!='nllb_supervised' or manifest['quality_validated'] is not False:
        raise ValueError('Unexpected operation/quality claim')
    selected=checked_files(manifest,entries,prefix)
    for name in selected:
        target=out/name
        target.parent.mkdir(parents=True,exist_ok=True)
        api.download_bucket_files(BUCKET,[(entries[prefix+'/'+name],target)],raise_on_missing_files=True)
        if target.stat().st_size!=manifest['files'][name]['bytes'] or sha(target)!=manifest['files'][name]['sha256']:
            raise ValueError('Recovered small evidence differs')
    persistence_upper=ready['export_seconds']+max(0,(now()-datetime.fromisoformat(ready['ready_utc'])).total_seconds())
    proof=dict(utc=now().isoformat(),run_id=identity['run_id'],manifest_sha256=ready['manifest_sha256'],
        persistence_upper_seconds=persistence_upper,
        provider_inventory_committed=True,provider_inventory={n:dict(bytes=f.size,xet_hash=f.xet_hash) for n,f in entries.items()},
        local_sha_verified_files=selected,model_weights_downloaded=False,nllb_status=manifest['nllb_status'],
        weight_sha_evidence='Server manifest; provider committed size/Xet independently observed. No laptop weight download.')
    write(RESULTS/'recovery.json',proof)
    emit(event='small_results_recovered',status=manifest['nllb_status'],files=len(selected))


def main():
    global PHASE,LOCAL,RESULTS
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('prepare','upload','launch','observe','recover','stop'))
    parser.add_argument('--phase',choices=('canary','continue'),default='canary')
    args=parser.parse_args()
    action,PHASE=args.action,args.phase
    LOCAL,RESULTS=pilot.LOCAL/PHASE,EXP/PHASE
    if action=='prepare':
        prepare()
        return
    import httpx
    from huggingface_hub import HfApi,set_client_factory
    os.environ['HF_XET_CACHE']=str(ROOT/'resources/local/hf-xet-cache')
    set_client_factory(lambda:httpx.Client(timeout=20,follow_redirects=True))
    api=HfApi()
    if action=='stop':
        identity=read(LOCAL/'preparation.json')
        jobs=[j for j in api.list_jobs(namespace='Mojionix',labels={'trial_id':identity['run_id']})
              if (j.labels or {}).get('trial_id')==identity['run_id']]
        shutdown(api,jobs,emit,time.monotonic())
    else:
        globals()[action](api)


if __name__=='__main__': main()
