"""Single-owner pilot launch, observation and small-evidence recovery; no retries of launch."""
import argparse
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from cloud_pilot import hf_contextual as pilot
from cloud_pilot.run_hf_dev_assisted import checked_hardware, submit_once, SubmissionFailed, TERMINAL, shutdown

EXP = Path(__file__).parent
RESULTS = EXP
LOCAL = ROOT / 'resources/local/hf-contextual-run-20260927'
BUCKET = 'Mojionix/pahlavi-pilot'
RESERVATION = Decimal('3.625025')
REVIEWS = ('INTEGRATION-QA.md', 'INTEGRATION-JUDGE.md', 'COMPANY-GATE.md')
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
read = lambda path: json.loads(Path(path).read_text('utf-8'))
now = lambda: datetime.now(timezone.utc)


def write(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def emit(**event):
    event['utc'] = now().isoformat()
    line = json.dumps(event)
    print(line, flush=True)
    with (LOCAL / 'events.jsonl').open('a', encoding='utf-8') as stream:
        stream.write(line + '\n')


def check_admission(admission, instant):
    age = (instant - datetime.fromisoformat(admission['utc'])).total_seconds()
    credit = Decimal(str(admission['balance_usd']))
    if (not 0 <= age <= 600 or not credit.is_finite() or credit < RESERVATION
            or admission['automatic_recharge_set'] is not False):
        raise ValueError('Fresh funded credit and no automatic recharge required')


def prepare():
    RESULTS.mkdir(exist_ok=True)
    LOCAL.mkdir(exist_ok=False)
    spec, identity = pilot.specification()
    wire = dict(spec, volumes=[v.to_dict() for v in spec['volumes']])
    write(LOCAL / 'spec.json', wire)
    identity.update(spec_sha256=sha(LOCAL / 'spec.json'), controller_sha256=sha(__file__),
        source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        review_sha256={name: sha(EXP / name) for name in REVIEWS})
    write(LOCAL / 'preparation.json', identity)
    emit(event='prepared_not_submitted', run_id=identity['run_id'], reservation_usd=str(RESERVATION))


def launch(api):
    identity = read(LOCAL / 'preparation.json')
    spec, current = pilot.specification(identity['run_id'])
    if (sha(LOCAL / 'spec.json') != identity['spec_sha256'] or sha(__file__) != identity['controller_sha256']
            or dict(spec, volumes=[v.to_dict() for v in spec['volumes']]) != read(LOCAL / 'spec.json')
            or any(identity[k] != v for k, v in current.items())
            or any(sha(EXP / n) != identity['review_sha256'][n] for n in REVIEWS)):
        raise ValueError('Frozen preparation changed')
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if revision != identity['source_commit'] or subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT).strip():
        raise ValueError('Clean checkpointed source required')
    check_admission(read(LOCAL / 'admission.json'), now())
    transfer = read(EXP / 'input-transfer.json')
    if transfer['sha256'] != identity['package_sha256'] or transfer['roundtrip_verified'] is not True:
        raise ValueError('Verified package transfer required')
    if api.whoami()['name'] != 'Mojionix':
        raise ValueError('Wrong HF account')
    checked_hardware(next(h for h in api.list_jobs_hardware() if h.name == 'a100-large'))
    jobs = list(api.list_jobs(namespace='Mojionix'))
    if any(j.status.stage not in TERMINAL or (j.labels or {}).get('trial_id') == identity['run_id'] for j in jobs):
        raise ValueError('Active or duplicate job prevents submission')
    if list(api.list_bucket_tree(BUCKET, prefix=identity['output_prefix'] + '/', recursive=True)):
        raise ValueError('Output prefix already used')
    check_admission(read(LOCAL / 'admission.json'), now())
    record = dict(run_id=identity['run_id'], source_commit=revision, submitted_utc=now().isoformat(),
        spec_sha256=identity['spec_sha256'], command_sha256=identity['command_sha256'],
        native_timeout='75m', reservation_usd=str(RESERVATION), execution_owner='/root', prelaunch_jobs=len(jobs))
    write(LOCAL / 'submission-started.json', record)
    try:
        job = submit_once(api, spec, identity['run_id'], emit)
    except SubmissionFailed as error:
        try:
            write(RESULTS / 'submission-unconfirmed.json', dict(record, known_job_ids=[j.id for j in error.jobs]))
        finally:
            if error.jobs:
                shutdown(api, error.jobs, emit, time.monotonic())
        raise
    record.update(job_id=job.id, stage=job.status.stage, job_url='https://huggingface.co/jobs/Mojionix/' + job.id)
    try:
        write(LOCAL / 'known-job.json', record)
        write(RESULTS / 'execution.json', record)
    except BaseException:
        shutdown(api, [job], emit, time.monotonic())
        raise
    emit(event='submitted', **record)


def observe(api):
    execution = read(RESULTS / 'execution.json')
    info = api.inspect_job(job_id=execution['job_id'], namespace='Mojionix')
    logs = '\n'.join(api.fetch_job_logs(job_id=execution['job_id'], namespace='Mojionix', follow=False))
    (LOCAL / 'provider.log').write_text(logs, encoding='utf-8')
    elapsed = (now() - datetime.fromisoformat(execution['submitted_utc'])).total_seconds()
    lines = logs.splitlines()
    emit(event='observation', stage=info.status.stage, elapsed_seconds=round(elapsed),
        elapsed_compute_estimate_usd=round(elapsed * 41667 / 60 / 1e6, 4),
        recorded_outputs=sum('"phase": "generation_case_recorded"' in s for s in lines),
        ready_to_persist=any('"stage": "ready_to_persist"' in s for s in lines))
    print('\n'.join(lines[-6:])[:5000])
    return logs


def checked_files(manifest, entries, prefix):
    files = manifest['files']
    if not files or len(files) > 60 or sum(v['bytes'] for v in files.values()) > 2 * 1024**3:
        raise ValueError('Unexpected export size')
    if set(entries) != {prefix + '/manifest.json', *(prefix + '/' + n for n in files)}:
        raise ValueError('Provider inventory not complete/exact')
    selected = []
    for name, record in files.items():
        path = PurePosixPath(name)
        if (path.is_absolute() or '..' in path.parts or path.as_posix() != name or '\\' in name or ':' in name
                or type(record['bytes']) is not int or record['bytes'] < 0 or not re.fullmatch('[a-f0-9]{64}', record['sha256'])):
            raise ValueError('Unsafe export record')
        entry = entries[prefix + '/' + name]
        if entry.size != record['bytes'] or not entry.xet_hash:
            raise ValueError('Artifact not committed')
        if name.endswith(('.json', '.jsonl', '.md', '.log')):
            selected.append(name)
        elif name not in {'contextual/training/' + arm + '/adapter/adapter_model.safetensors' for arm in ('control', 'candidate')}:
            raise ValueError('Unexpected binary artifact')
    if sum(files[n]['bytes'] for n in selected) > 32 * 1024**2:
        raise ValueError('Small evidence exceeds local transfer bound')
    return selected


def recover(api):
    logs = observe(api)
    ready = [json.loads(s[s.index('{'):]) for s in logs.splitlines() if '"stage": "ready_to_persist"' in s]
    if len(ready) != 1 or not 0 < ready[0]['manifest_bytes'] <= 1024**2:
        raise ValueError('Single closed export required')
    ready = ready[0]
    identity = read(LOCAL / 'preparation.json')
    prefix = identity['output_prefix']
    entries = {f.path: f for f in api.list_bucket_tree(BUCKET, prefix=prefix + '/', recursive=True) if hasattr(f, 'size')}
    remote = entries[prefix + '/manifest.json']
    if remote.size != ready['manifest_bytes'] or not remote.xet_hash:
        raise ValueError('Manifest not committed')
    out = RESULTS / 'recovered'
    out.mkdir(exist_ok=True)
    api.download_bucket_files(BUCKET, [(remote, out / 'manifest.json')], raise_on_missing_files=True)
    manifest = read(out / 'manifest.json')
    if sha(out / 'manifest.json') != ready['manifest_sha256'] or manifest != ready['manifest']:
        raise ValueError('Manifest identity mismatch')
    for key in ('run_id', 'package_sha256', 'package_manifest_sha256', 'inputs_sha256', 'bundle_sha256',
                'trained_manifest_sha256', 'script_hashes', 'bootstrap_hashes', 'adapter_files',
                'compute_seconds', 'internal_seconds', 'native_timeout_minutes', 'scheduled_outputs', 'steps_per_arm'):
        if manifest[key] != identity[key]:
            raise ValueError('Export identity mismatch: ' + key)
    if manifest['operation'] != 'contextual_pilot' or manifest['quality_validated'] is not False:
        raise ValueError('Unexpected operation/quality claim')
    selected = checked_files(manifest, entries, prefix)
    pairs = []
    for name in selected:
        target = out / name
        target.parent.mkdir(parents=True, exist_ok=True)
        pairs.append((entries[prefix + '/' + name], target))
    api.download_bucket_files(BUCKET, pairs, raise_on_missing_files=True)
    for name in selected:
        if (out / name).stat().st_size != manifest['files'][name]['bytes'] or sha(out / name) != manifest['files'][name]['sha256']:
            raise ValueError('Recovered evidence differs: ' + name)
    proof = dict(utc=now().isoformat(), run_id=identity['run_id'], manifest_sha256=ready['manifest_sha256'],
        provider_inventory_committed=True, provider_inventory={n: dict(bytes=f.size, xet_hash=f.xet_hash) for n, f in entries.items()},
        local_sha_verified_files=selected, model_weights_downloaded=False,
        weight_sha_evidence='Server manifest only; committed provider size/xet inventory independently checked',
        contextual_status=manifest['contextual_status'])
    write(RESULTS / 'recovery.json', proof)
    emit(event='recovered', contextual_status=manifest['contextual_status'], small_files=len(selected))


def main():
    global LOCAL, RESULTS, REVIEWS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'launch', 'observe', 'recover', 'stop'))
    parser.add_argument('--attempt', choices=('1', '2'), default='1')
    args = parser.parse_args()
    action = args.action
    if args.attempt == '2':
        failure = read(EXP / 'startup-failure.json')
        if failure['status'] != 'ERROR' or failure['bootstrap_started'] is not False or failure['training_started'] is not False:
            raise ValueError('Attempt2 is only for the recorded pre-start transport failure')
        RESULTS = EXP / 'attempt-2'
        LOCAL = ROOT / 'resources/local/hf-contextual-run-20260927-attempt-2'
        REVIEWS = (*REVIEWS, 'TRANSPORT-REPAIR-QA.md', 'TRANSPORT-REPAIR-JUDGE.md')
    if action == 'prepare':
        prepare()
        return
    import httpx
    from huggingface_hub import HfApi, set_client_factory
    os.environ['HF_XET_CACHE'] = str(ROOT / 'resources/local/hf-xet-cache')
    set_client_factory(lambda: httpx.Client(timeout=15, follow_redirects=True))
    api = HfApi()
    if action == 'stop':
        identity = read(LOCAL / 'preparation.json')
        jobs = [j for j in api.list_jobs(namespace='Mojionix', labels={'trial_id': identity['run_id']})
                if (j.labels or {}).get('trial_id') == identity['run_id']]
        shutdown(api, jobs, emit, time.monotonic())
    else:
        globals()[action](api)


if __name__ == '__main__':
    main()
