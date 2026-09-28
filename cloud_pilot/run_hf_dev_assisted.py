"""Run one predeclared comparison family; one POST, bounded observation and shutdown."""
import argparse
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import time

import httpx
from huggingface_hub import HfApi, Volume, set_client_factory

from . import hf_dev_assisted

ROOT = Path(__file__).resolve().parents[1]
BUCKET = 'Mojionix/pahlavi-pilot'
TERMINAL = {'COMPLETED', 'ERROR', 'CANCELED', 'CANCELLED', 'DELETED'}
RATE_MICRO_USD = 41667
NATIVE_MINUTES = 55
TOTAL_RESERVED_USD = Decimal(RATE_MICRO_USD * NATIVE_MINUTES * 2) / 1000000
IDENTITY_KEYS = ('run_id', 'family', 'bundle_name', 'bundle_sha256', 'input_files',
                 'trained_manifest_sha256', 'bootstrap_hashes', 'script_hashes', 'runner')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), default=vars)


def checked_admission(admission, family, run_id, now):
    allowed = admission['allowed_trial_ids']
    if (not isinstance(allowed, dict) or set(allowed) != {'gemma', 'qwen'}
            or any(not isinstance(v, str) or not re.fullmatch('[a-f0-9]{32}', v) for v in allowed.values())
            or len(set(allowed.values())) != 2 or allowed.get(family) != run_id):
        raise ValueError('Admission must bind exactly two distinct family trial IDs')
    observed = datetime.fromisoformat(admission['observation_utc'].replace('Z', '+00:00'))
    if observed.utcoffset() != timezone.utc.utcoffset(observed) or not 0 <= (now - observed).total_seconds() <= 1800:
        raise ValueError('Credit observation must be UTC and at most thirty minutes old')
    try:
        credit, reserved, reserve = (Decimal(str(admission[key])) for key in
            ('observed_credit_usd', 'total_reserved_compute_usd', 'reserve_usd'))
    except InvalidOperation as error:
        raise ValueError('Invalid admission funding amounts') from error
    if (not all(v.is_finite() for v in (credit, reserved, reserve))
            or reserved != TOTAL_RESERVED_USD or reserve != Decimal('.75') or credit < reserved + reserve):
        raise ValueError('Observed credit must fund both fixed 55-minute jobs and the 0.75 USD reserve')
    return allowed


def checked_jobs(jobs, allowed, family):
    seen = set()
    for job in jobs:
        labels = job.labels or {}
        trial = labels.get('trial_id')
        if trial in allowed.values():
            expected_family = next(name for name, value in allowed.items() if value == trial)
            if (trial in seen or labels.get('family') != expected_family
                    or labels.get('purpose') != 'dev-plain-assisted'):
                raise ValueError('Duplicate trial or mismatched declared family')
            seen.add(trial)
            if trial == allowed[family]:
                raise ValueError('This trial already exists; never submit it again')
        elif job.status.stage not in TERMINAL:
            raise ValueError('An active job is outside the two declared trials')


def checked_preparation(family, spec_bytes, identity, admission_bytes, revision, controller_bytes):
    for data, key in ((spec_bytes, 'spec_sha256'), (controller_bytes, 'controller_sha256'),
                      (admission_bytes, 'admission_sha256')):
        if hashlib.sha256(data).hexdigest() != identity[key]:
            raise ValueError('Prepared identity changed: ' + key)
    if revision != identity['source_commit']:
        raise ValueError('Prepared source commit changed')
    spec = json.loads(spec_bytes)
    expected_spec, expected_identity = hf_dev_assisted.specification(family, identity['run_id'])
    if canonical(spec) != canonical(expected_spec):
        raise ValueError('Prepared specification differs from the current frozen sources')
    if any(canonical(identity[key]) != canonical(value) for key, value in expected_identity.items()):
        raise ValueError('Prepared source identity differs from the specification')
    if (spec['namespace'] != 'Mojionix' or spec['flavor'] != 'a100-large'
            or spec['timeout'] != '55m' or spec.get('secrets')
            or spec['labels']['family'] != family or spec['labels']['trial_id'] != identity['run_id']):
        raise ValueError('Only the declared account, hardware, duration and family are allowed')
    return spec


def checked_hardware(hardware):
    if hardware.name != 'a100-large' or hardware.unit_label != 'minute' or hardware.unit_cost_micro_usd != RATE_MICRO_USD:
        raise ValueError('Pinned A100 price or billing unit changed')


def incremental_compute_usd(seconds):
    return round(max(0, seconds) * RATE_MICRO_USD / 60 / 1000000, 6)


class ObservationUnavailable(RuntimeError):
    pass


def observe(call, sleep=time.sleep):
    # Retry only read-only requests; submission and cancellation never enter here.
    for attempt in range(3):
        try:
            return call()
        except httpx.TransportError as error:
            if attempt == 2:
                raise ObservationUnavailable(type(error).__name__) from error
            sleep(2)


class SubmissionFailed(RuntimeError):
    def __init__(self, jobs):
        super().__init__('Submission response failed; never repeat the POST')
        self.jobs = jobs


def submit_once(api, spec, run_id, emit, sleep=time.sleep):
    try:
        return api.run_job(**spec)
    except Exception as error:
        emit(event='submission_response_failed', error_type=type(error).__name__)
        recovered = []
        for attempt in range(3):
            try:
                recovered = [j for j in observe(lambda: api.list_jobs(namespace='Mojionix',
                    labels={'trial_id': run_id}, timeout=15), sleep=sleep)
                    if (j.labels or {}).get('trial_id') == run_id]
            except Exception as reconcile_error:
                emit(event='reconciliation_delayed', error_type=type(reconcile_error).__name__)
            if recovered:
                break
            if attempt < 2:
                sleep(10)
        if not recovered:
            emit(event='URGENT_submission_unconfirmed', run_id=run_id)
        raise SubmissionFailed(recovered) from error


def checked_inventory(manifest, entries, prefix, identity):
    if any(manifest[key] != identity[key] for key in IDENTITY_KEYS):
        raise ValueError('Manifest identity changed')
    if (prefix != 'comparisons/' + identity['run_id'] or manifest['operation'] != 'dev_plain_assisted'
            or manifest['training_performed'] is not False
            or manifest['comparison_status'] not in {'complete', 'incomplete'}):
        raise ValueError('Manifest operation or output prefix changed')
    files = manifest['files']
    allowed = {'comparison/run.json', 'comparison/predictions.jsonl', 'comparison-status.json', 'bundle-manifest.json'}
    allowed |= {'trained-manifest.json', 'base-provenance.json'} if identity['family'] == 'gemma' else {'qwen-source-identity.json'}
    if not 1 <= len(files) <= 30 or not set(files) <= allowed or 'comparison-status.json' not in files:
        raise ValueError('Only the declared small comparison evidence files are allowed')
    if manifest['comparison_status'] == 'complete' and not {'comparison/predictions.jsonl', 'comparison/run.json'} <= files.keys():
        raise ValueError('Complete comparison lacks predictions or run metadata')
    observed, total = [], 0
    for name, record in files.items():
        path = PurePosixPath(name)
        if (path.is_absolute() or '..' in path.parts or chr(92) in name or ':' in name or name != path.as_posix()
                or not isinstance(record['sha256'], str) or not re.fullmatch('[a-f0-9]{64}', record['sha256'])
                or type(record['bytes']) is not int or record['bytes'] < 0):
            raise ValueError('Invalid manifest file record')
        total += record['bytes']
        entry = entries.get(prefix + '/' + name)
        if entry is None or entry.size != record['bytes'] or not entry.xet_hash:
            return None
        observed.append({'path': entry.path, 'bytes': entry.size, 'xet_hash': entry.xet_hash})
    if total > 16 * 1024**2 or set(entries) - {prefix + '/manifest.json', *(prefix + '/' + name for name in files)}:
        raise ValueError('Remote evidence inventory exceeds its declared scope')
    return observed


def shutdown(api, jobs, emit, start, clock=time.monotonic, sleep=time.sleep):
    pending = {job.id: job for job in jobs}
    stop_deadline = min(start + 3600, clock() + 300)
    while pending and clock() < stop_deadline:
        for job_id in list(pending):
            try:
                stage = api.inspect_job(job_id=job_id, namespace='Mojionix').status.stage
                emit(event='shutdown_status', job_id=job_id, stage=stage)
                if stage in TERMINAL:
                    del pending[job_id]
                else:
                    api.cancel_job(job_id=job_id, namespace='Mojionix')
            except Exception as error:
                emit(event='shutdown_check_error', error_type=type(error).__name__, job_id=job_id)
        if pending:
            sleep(10)
    if pending:
        emit(event='URGENT_termination_unconfirmed', job_ids=list(pending))
        raise RuntimeError('Remote termination not confirmed')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--family', choices=('gemma', 'qwen'), required=True)
    family = parser.parse_args(argv).family
    local = ROOT / 'resources/local'
    out = local / f'hf-dev-assisted-{family}-run-20260927'
    out.mkdir(exist_ok=False)  # Exclusive owner directory persists even after uncertain submission.

    def emit(**event):
        event['utc'] = datetime.now(timezone.utc).isoformat()
        line = json.dumps(event)
        print(line, flush=True)
        with (out / 'events.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(line + '\n')

    identity = json.loads((local / f'hf-dev-assisted-{family}-20260927-provenance.json').read_text('utf-8'))
    admission_bytes = (local / 'hf-dev-assisted-20260927-admission.json').read_bytes()
    admission = json.loads(admission_bytes)
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    spec = checked_preparation(family, (local / f'hf-dev-assisted-{family}-20260927.json').read_bytes(),
        identity, admission_bytes, revision, Path(__file__).read_bytes())
    allowed = checked_admission(admission, family, identity['run_id'], datetime.now(timezone.utc))
    os.environ['HF_XET_CACHE'] = str(local / 'hf-xet-cache')
    set_client_factory(lambda: httpx.Client(timeout=15, follow_redirects=True))
    api = HfApi()
    if observe(api.whoami)['name'] != 'Mojionix':
        raise ValueError('Only account Mojionix is admitted')
    hardware = next(h for h in observe(api.list_jobs_hardware) if h.name == 'a100-large')
    checked_hardware(hardware)
    checked_jobs(observe(lambda: api.list_jobs(namespace='Mojionix', timeout=15)), allowed, family)
    prefix = identity['output_prefix']
    if observe(lambda: list(api.list_bucket_tree(BUCKET, prefix=prefix + '/', recursive=True))):
        raise ValueError('Fresh comparison output prefix required')
    # Refresh the time gate immediately before the sole submission attempt.
    checked_admission(admission, family, identity['run_id'], datetime.now(timezone.utc))
    spec['volumes'] = [Volume(**v) for v in spec['volumes']]
    emit(event='admitted', family=family, source_commit=revision, spec_sha256=identity['spec_sha256'],
         admission_sha256=identity['admission_sha256'], run_id=identity['run_id'])
    start = time.monotonic()
    deadline = start + NATIVE_MINUTES * 60
    active, uncertain, submission_unconfirmed = None, [], False
    inventory_verified, last_progress, last_contact, logs = False, None, start, ''
    try:
        try:
            submission_unconfirmed = True
            active = submit_once(api, spec, identity['run_id'], emit)
            submission_unconfirmed = False
        except SubmissionFailed as error:
            uncertain, submission_unconfirmed = error.jobs, not error.jobs
            raise
        emit(event='submitted', job_id=active.id, url=active.url)
        while time.monotonic() < deadline:
            try:
                info = observe(lambda: api.inspect_job(job_id=active.id, namespace='Mojionix'))
                last_contact = time.monotonic()
            except ObservationUnavailable as error:
                emit(event='observation_delayed', request='status', error_type=str(error))
                if time.monotonic() - last_contact > 180:
                    raise TimeoutError('Provider status unavailable for more than three minutes')
                time.sleep(5)
                continue
            try:
                logs = observe(lambda: '\n'.join(api.fetch_job_logs(job_id=active.id, namespace='Mojionix', follow=False)))
            except ObservationUnavailable as error:
                emit(event='observation_delayed', request='logs', error_type=str(error))
            (out / 'provider.log').write_text(logs, encoding='utf-8')
            emit(event='status', job_id=active.id, stage=info.status.stage,
                 elapsed_seconds=round(time.monotonic() - start),
                 conservative_compute_usd=incremental_compute_usd(time.monotonic() - start))
            lines = [s for s in logs.splitlines() if '"stage":' in s or '"status": "dev_attempt_recorded"' in s]
            if lines and lines[-1] != last_progress:
                last_progress = lines[-1]
                emit(event='progress', line=last_progress[:1800])
            ready = None
            for line in logs.splitlines():
                if '"stage": "ready_to_persist"' in line:
                    candidate = json.loads(line[line.index('{'):])
                    if candidate.get('stage') == 'ready_to_persist':
                        ready = candidate
            if ready is not None:
                if type(ready['manifest_bytes']) is not int or not 0 < ready['manifest_bytes'] <= 1024**2:
                    raise ValueError('Manifest exceeds the small-result limit')
                entries = {f.path: f for f in observe(lambda: list(api.list_bucket_tree(BUCKET,
                    prefix=prefix + '/', recursive=True))) if hasattr(f, 'size')}
                remote_manifest = entries.get(prefix + '/manifest.json')
                if remote_manifest and remote_manifest.size == ready['manifest_bytes'] and remote_manifest.xet_hash:
                    path = out / 'manifest.json'
                    if not path.exists():
                        observe(lambda: api.download_bucket_files(BUCKET, [(remote_manifest, path)], raise_on_missing_files=True))
                    if hashlib.sha256(path.read_bytes()).hexdigest() != ready['manifest_sha256']:
                        raise ValueError('Persisted manifest SHA256 differs')
                    manifest = json.loads(path.read_text('utf-8'))
                    if manifest != ready['manifest']:
                        raise ValueError('Persisted manifest differs from job evidence')
                    inventory = checked_inventory(manifest, entries, prefix, identity)
                    if inventory is not None:
                        proof = {'status': 'server_committed_inventory_verified', 'job_id': active.id,
                            'manifest_sha256': ready['manifest_sha256'], 'files': inventory,
                            'cross_job_sha256_verified': False, 'resume_requires_all_file_sha256': True}
                        (out / 'inventory-verification.json').write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
                        inventory_verified = True
                        emit(event='inventory_verified', file_count=len(inventory), full_sha_recovery_pending=True)
                        break
            if info.status.stage in TERMINAL:
                break
            time.sleep(min(20, max(0, deadline - time.monotonic())))
        if not inventory_verified:
            raise RuntimeError('Comparison inventory not verified; no automatic retry')
    finally:
        shutdown(api, uncertain + ([active] if active is not None else []), emit, start)
        emit(event='finished', inventory_verified=inventory_verified, cloud_terminal=not submission_unconfirmed,
             conservative_compute_usd=incremental_compute_usd(time.monotonic() - start),
             elapsed_seconds=round(time.monotonic() - start), automatic_continuation=False)


if __name__ == '__main__':
    main()
