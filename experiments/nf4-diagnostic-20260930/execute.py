"""Read back existing cloud inputs, then optionally submit this reviewed job ONCE."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
from decimal import Decimal
import json
import os
from pathlib import Path
import subprocess
import sys

import prepare
from cloud_pilot import training_admission
from huggingface_hub import HfApi
from huggingface_hub._jobs_api import TERMINAL_JOB_STAGES
from huggingface_hub.errors import EntryNotFoundError

sys.path.insert(0, str(prepare.ROOT / 'experiments/readiness-repair-20260930/live-execution'))
from submit_once import submit_once, save

HERE = prepare.HERE
LIVE = HERE / 'live-execution'
PROPOSAL = HERE / 'execution-proposal'
BUCKET = 'Mojionix/pahlavi-pilot'


def live_check(api, spec, receipt):
    funds = json.loads((LIVE / 'funding.json').read_bytes())
    age = (datetime.now(timezone.utc) - datetime.fromisoformat(funds['utc'])).total_seconds()
    if not 0 <= age <= 1800 or funds['automatic_recharge'] is not False:
        raise ValueError('Fresh no-auto-recharge browser funding observation required')
    if api.whoami()['name'] != spec['namespace'] or not api.bucket_info(BUCKET).private:
        raise ValueError('Account/private bucket differs')
    hardware = next(h for h in api.list_jobs_hardware() if h.name == spec['flavor'])
    if hardware.unit_label != 'minute':
        raise ValueError('Unexpected billing unit')
    compute = Decimal(str(hardware.unit_cost_usd)) * receipt['native_timeout_minutes']
    allowance = compute + Decimal('0.50')
    if allowance > Decimal('5.51') or Decimal(funds['credit_usd']) < allowance:
        raise ValueError('Current price/funds exceed the approved envelope')
    jobs = api.list_jobs(namespace=spec['namespace'], timeout=30)
    if any(j.status.stage not in TERMINAL_JOB_STAGES or (j.labels or {}).get('trial_id') == receipt['run_id'] for j in jobs):
        raise ValueError('Active or matching job exists; never resubmit')
    try:
        if list(api.list_bucket_tree(BUCKET, prefix=receipt['output_prefix'], recursive=True)):
            raise ValueError('Output prefix is not empty')
    except EntryNotFoundError:
        pass
    return dict(utc=datetime.now(timezone.utc).isoformat(), hardware=asdict(hardware),
        maximum_compute_usd=str(compute), maximum_allowance_usd=str(allowance),
        observed_credit_usd=funds['credit_usd'], private_bucket=True, active_jobs=[],
        matching_trial_ids=[], output_prefix_empty=True)


def stage(api, spec, receipt):
    local = prepare.ROOT / 'resources/local/nf4-readback' / receipt['run_id']
    local.mkdir(parents=True, exist_ok=True)
    mounts = {v['mountPath']: v['path'] for v in spec['volumes']}
    inputs = [(prepare.PACKET / 'inputs.jsonl', 'inputs/' + receipt['inputs_name'], receipt['inputs_sha256']),
              (prepare.ROOT / 'resources/local' / receipt['bundle_name'], 'inputs/' + receipt['bundle_name'], receipt['bundle_sha256'])]
    arms = {'reference': (mounts['/original'], 'training/adapter'),
            'candidate': (mounts['/mixed'], 'mixed/training/adapter')}
    paths = [key for _, key, _ in inputs]
    for prefix, relative in arms.values():
        paths.extend([prefix + '/manifest.json', prefix + '/' + relative + '/adapter_config.json',
                      prefix + '/' + relative + '/adapter_model.safetensors'])
    remote = {f.path: f for f in api.get_bucket_paths_info(BUCKET, paths)}
    verified_inputs, verified_arms = [], {}
    for source, key, expected in inputs:
        if prepare.sha(source.read_bytes()) != expected or remote[key].size != source.stat().st_size:
            raise ValueError('Input identity/size differs')
        target = local / Path(key).name
        api.download_bucket_files(BUCKET, [(remote[key], target)], raise_on_missing_files=True)
        if prepare.sha(target.read_bytes()) != expected:
            raise ValueError('Remote input readback differs')
        verified_inputs.append(dict(path=key, bytes=remote[key].size, sha256=expected))
    for arm, (prefix, relative) in arms.items():
        manifest_key, config_key = prefix + '/manifest.json', prefix + '/' + relative + '/adapter_config.json'
        if not 0 < remote[manifest_key].size < 2 * 1024**2 or not 0 < remote[config_key].size < 65536:
            raise ValueError('Unexpected metadata size')
        manifest_path, config_path = local / (arm + '-manifest.json'), local / (arm + '-config.json')
        api.download_bucket_files(BUCKET, [(remote[manifest_key], manifest_path), (remote[config_key], config_path)], raise_on_missing_files=True)
        if prepare.sha(manifest_path.read_bytes()) != receipt[arm + '_manifest_sha256'] or prepare.sha(config_path.read_bytes()) != receipt[arm + '_adapter_files']['adapter_config.json']:
            raise ValueError('Adapter metadata identity differs')
        manifest = json.loads(manifest_path.read_bytes())
        for name, expected in receipt[arm + '_adapter_files'].items():
            entry = manifest['files'][relative + '/' + name]
            if entry['sha256'] != expected or remote[prefix + '/' + relative + '/' + name].size != entry['bytes']:
                raise ValueError('Adapter inventory differs')
        verified_arms[arm] = dict(manifest_sha256=receipt[arm + '_manifest_sha256'],
            config_sha256=receipt[arm + '_adapter_files']['adapter_config.json'],
            weight_size_matches_manifest=True, weight_bytes_rehashed_locally=False)
    return dict(run_id=receipt['run_id'], utc=datetime.now(timezone.utc).isoformat(),
        inputs_readback_verified=verified_inputs, adapter_evidence=verified_arms,
        uploaded_files=[], weights_downloaded=False, server_weight_rehash_required=True)


def main(submit=False):
    if (LIVE / 'submission-claim.json').exists():
        raise ValueError('Already claimed; inspect provider instead of retrying')
    prepare.verify(PROPOSAL)
    spec = json.loads((PROPOSAL / 'job-spec.json').read_bytes())
    receipt = json.loads((PROPOSAL / 'job-receipt.json').read_bytes())
    native = training_admission.sdk_spec(spec)
    api = HfApi()
    os.environ['HF_XET_CACHE'] = str(prepare.ROOT / 'resources/local/learning-diagnosis-xet-cache')
    os.environ['HF_HUB_DISABLE_PROGRESS_BARS'] = '1'
    current = live_check(api, spec, receipt)
    staging = stage(api, spec, receipt)
    if not submit:
        (LIVE / 'staging.json').write_bytes(prepare.encode(staging))
        (LIVE / 'live-check.json').write_bytes(prepare.encode(current))
        print(json.dumps({'status': 'STAGED_NOT_SUBMITTED', **current, **staging}))
        return
    # The exact reviewed source/proposal remains byte-bound; enforce independent PASS.
    review = json.loads((HERE / 'review-gate.json').read_bytes())
    if review['verdict'] != 'PASS' or review['proposal_check_sha256'] != prepare.sha((PROPOSAL / 'check.json').read_bytes()):
        raise ValueError('Independent review does not bind this proposal')
    current = live_check(api, spec, receipt)
    admission = dict(current, scope='One NF4 inference-only job; no training/recharge/local weights/automatic retry',
        user_reply='do', authorized_cap_usd='5.51', native_timeout_minutes=120, owner='root',
        run_id=receipt['run_id'], output_prefix=receipt['output_prefix'],
        source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=prepare.ROOT, text=True).strip(),
        job_spec_sha256=prepare.sha((PROPOSAL / 'job-spec.json').read_bytes()),
        review_gate_sha256=prepare.sha((HERE / 'review-gate.json').read_bytes()), staging=staging,
        server_weight_rehash_gpu_canary_and_persistence='PENDING')
    print(json.dumps(submit_once(api, native, LIVE, admission), default=str))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--submit', action='store_true')
    main(parser.parse_args().submit)
