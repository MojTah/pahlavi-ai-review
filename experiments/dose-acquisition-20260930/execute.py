"""Stage exact approved evidence; submit at most once through the existing gate."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
from decimal import Decimal
import json
import os
from pathlib import Path
import sys

import prepare
from cloud_pilot import hf_dose, training_admission as gate

os.environ['HF_XET_CACHE'] = str(prepare.ROOT / 'resources/local/learning-diagnosis-xet-cache')
os.environ['HF_HUB_DISABLE_PROGRESS_BARS'] = '1'
from huggingface_hub import HfApi
from huggingface_hub._jobs_api import TERMINAL_JOB_STAGES
from huggingface_hub.errors import EntryNotFoundError

HERE, ROOT = prepare.HERE, prepare.ROOT
LIVE, PROPOSAL, EVIDENCE = HERE / 'live-execution', HERE / 'execution-proposal', HERE / 'admission'
BUCKET = 'Mojionix/pahlavi-pilot'


def verify_proposal():
    check = json.loads((PROPOSAL / 'check.json').read_bytes())
    for relative, expected in check['source_sha256'].items():
        if prepare.sha((ROOT / relative).read_bytes()) != expected:
            raise ValueError('Reviewed source changed: ' + relative)
    for name, expected in check['files_sha256'].items():
        if prepare.sha((PROPOSAL / name).read_bytes()) != expected:
            raise ValueError('Prepared proposal changed: ' + name)
    spec, prep = hf_dose.prepare(ROOT / 'resources/local/training-ready-v2-20260929/data/train.jsonl',
        ROOT / 'experiments/training-ready-v2-20260929/data-manifest.json', HERE / 'inputs.jsonl',
        json.loads((HERE / 'packet-contract.json').read_bytes()), check['run_id'])
    if (prepare.encode(gate.plain(spec)) != (PROPOSAL / 'job-spec.json').read_bytes()
            or prepare.encode(prep) != (PROPOSAL / 'job-receipt.json').read_bytes()):
        raise ValueError('Exact current proposal replay failed')
    gate.validate(EVIDENCE, prep['training_admission']['job_sha256'])
    return gate.plain(spec), prep


def live_check(api, spec, prep):
    funds = json.loads((LIVE / 'funding.json').read_bytes())
    age = (datetime.now(timezone.utc) - datetime.fromisoformat(funds['utc'])).total_seconds()
    if not 0 <= age <= 1800 or funds['automatic_recharge'] is not False:
        raise ValueError('Fresh funding observation with recharge disabled required')
    if api.whoami()['name'] != 'Mojionix' or not api.bucket_info(BUCKET).private:
        raise ValueError('Expected private project bucket/account')
    hardware = next(h for h in api.list_jobs_hardware() if h.name == spec['flavor'])
    if hardware.unit_label != 'minute' or prep['native_timeout_minutes'] != 360:
        raise ValueError('Billing unit or timeout differs')
    compute = Decimal(str(hardware.unit_cost_usd)) * 360
    allowance = compute + Decimal('0.50')
    if allowance > Decimal('15.51') or Decimal(funds['credit_usd']) < allowance:
        raise ValueError('Insufficient existing funds or rate exceeds pilot allowance')
    jobs = api.list_jobs(namespace='Mojionix', timeout=30)
    if any(j.status.stage not in TERMINAL_JOB_STAGES or (j.labels or {}).get('trial_id') == prep['run_id'] for j in jobs):
        raise ValueError('Active/matching job exists; inspect instead of retrying')
    try:
        if list(api.list_bucket_tree(BUCKET, prefix=prep['output_prefix'], recursive=True)):
            raise ValueError('Output prefix exists')
    except EntryNotFoundError:
        pass
    return dict(utc=datetime.now(timezone.utc).isoformat(),hardware=asdict(hardware),
        compute_ceiling_usd=str(compute),allowance_usd=str(allowance),credit_usd=funds['credit_usd'],
        private_bucket=True,active_jobs=[],output_prefix_empty=True)


def stage(api, prep):
    claim = EVIDENCE / ('submission-' + prep['training_admission']['job_sha256'] + '.json')
    if claim.exists():
        raise ValueError('Existing submission claim; inspect provider instead of restaging')
    inventory = [(HERE / 'inputs.jsonl','inputs/' + prep['inputs_name']),
        (ROOT / 'resources/local/training-ready-v2-20260929/data/train.jsonl','inputs/' + prep['train_name']),
        (ROOT / 'experiments/training-ready-v2-20260929/data-manifest.json','inputs/' + prep['data_manifest_name']),
        (ROOT / 'resources/local' / prep['bundle_name'],'inputs/' + prep['bundle_name'])]
    admission_prefix = 'inputs/training-admission/' + prep['training_admission']['job_sha256'] + '/'
    inventory += [(p,admission_prefix + p.relative_to(EVIDENCE).as_posix()) for p in sorted(EVIDENCE.rglob('*')) if p.is_file()]
    if any(p.is_symlink() for p,_ in inventory):
        raise ValueError('No symlink uploads')
    paths = [remote for _,remote in inventory]
    reference_prefix = prep['trained_prefix']
    manifest_key = reference_prefix + '/manifest.json'
    paths += [manifest_key] + [reference_prefix+'/'+n for n in prep['adapter_files']]
    remote = {f.path:f for f in api.get_bucket_paths_info(BUCKET,paths)}
    scratch = ROOT / 'resources/local/dose-readback' / prep['run_id']
    scratch.mkdir(parents=True,exist_ok=True)
    # Metadata only: never download the ~490MB reference weights to this computer.
    config_name = 'training/adapter/adapter_config.json'
    meta = [(manifest_key,scratch/'reference-manifest.json'),
            (reference_prefix+'/'+config_name,scratch/'reference-config.json')]
    for key,_ in meta:
        if key not in remote or not 0 < remote[key].size < 2*1024**2:
            raise ValueError('Reference metadata missing/unexpected size')
    api.download_bucket_files(BUCKET,[(remote[k],p) for k,p in meta],raise_on_missing_files=True)
    if (prepare.sha(meta[0][1].read_bytes()) != prep['trained_manifest_sha256']
            or prepare.sha(meta[1][1].read_bytes()) != prep['reference_adapter_files']['adapter_config.json']):
        raise ValueError('Reference metadata hash differs')
    manifest = json.loads(meta[0][1].read_bytes())
    for name,expected in prep['adapter_files'].items():
        entry = manifest['files'][name]
        if entry['sha256'] != expected or remote[reference_prefix+'/'+name].size != entry['bytes']:
            raise ValueError('Reference artifact manifest/size differs')
    downloads, missing = [], []
    for i,(source,key) in enumerate(inventory):
        target = scratch/'inputs'/str(i)
        target.parent.mkdir(exist_ok=True)
        if key in remote:
            if remote[key].size != source.stat().st_size:
                raise ValueError('Existing remote size differs; refusing overwrite: ' + key)
            downloads.append((remote[key],target))
        else:
            missing.append((source,key))
    # Verify existing paths before changing anything; never overwrite a conflict.
    api.download_bucket_files(BUCKET,downloads,raise_on_missing_files=True)
    for i,(source,key) in enumerate(inventory):
        if key in remote and prepare.sha((scratch/'inputs'/str(i)).read_bytes()) != prepare.sha(source.read_bytes()):
            raise ValueError('Existing remote hash differs; refusing overwrite: ' + key)
    if missing:
        api.batch_bucket_files(BUCKET,add=missing)
        api.download_bucket_files(BUCKET,[(key,scratch/'inputs'/str(i)) for i,(_,key) in enumerate(inventory)
                                        if key not in remote],raise_on_missing_files=True)
    evidence = []
    for i,(source,key) in enumerate(inventory):
        target = scratch/'inputs'/str(i)
        if target.stat().st_size != source.stat().st_size or prepare.sha(target.read_bytes()) != prepare.sha(source.read_bytes()):
            raise ValueError('Remote readback differs: ' + key)
        evidence.append(dict(path=key,sha256=prepare.sha(target.read_bytes()),bytes=target.stat().st_size))
    return dict(utc=datetime.now(timezone.utc).isoformat(),run_id=prep['run_id'],uploaded_files=[k for _,k in missing],
        readback=evidence,weights_downloaded=False,reference_metadata_verified=True,
        reference_weights_size_matches_manifest=True,server_weight_rehash_required=True)


def main(submit=False):
    spec, prep = verify_proposal()
    api = HfApi()
    current = live_check(api,spec,prep)
    staging = stage(api,prep)
    (LIVE/'staging.json').write_bytes(prepare.encode(staging))
    (LIVE/'live-check.json').write_bytes(prepare.encode(current))
    if not submit:
        print(json.dumps(dict(status='STAGED_NOT_SUBMITTED',files=len(staging['readback']),**current)))
        return
    verify_proposal()
    current = live_check(api,spec,prep)
    (LIVE/'live-check.json').write_bytes(prepare.encode(current))
    job = gate.submit(api,spec,prep,EVIDENCE)
    record = dict(id=job.id,status=job.status.stage,run_id=prep['run_id'],output_prefix=prep['output_prefix'],
        url='https://huggingface.co/jobs/Mojionix/'+job.id,utc=datetime.now(timezone.utc).isoformat(),
        job_sha256=prep['training_admission']['job_sha256'])
    with (LIVE/'provider-receipt.json').open('xb') as stream:
        stream.write(prepare.encode(record))
    print(json.dumps(record))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--submit',action='store_true')
    main(parser.parse_args().submit)
