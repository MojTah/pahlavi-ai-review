"""Submit the exact authorized inference proposal once; never retry a claimed run."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
from decimal import Decimal
import json
from pathlib import Path
import uuid
from types import SimpleNamespace

from stage_inputs import HERE, handoff, sha
from cloud_pilot import training_admission
from huggingface_hub import HfApi
from huggingface_hub._jobs_api import TERMINAL_JOB_STAGES
from huggingface_hub.errors import EntryNotFoundError


def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, default=str)
        stream.write('\n')


def submit_once(api, native, folder, admission):
    save(folder / 'submission-claim.json', admission)
    # Keep this claim on every exception, including an unknown provider outcome.
    job = api.run_job(**native)
    result = dict(job_id=job.id, url=job.url, stage=job.status.stage,
                  created_at=job.created_at, observed_utc=datetime.now(timezone.utc).isoformat(),
                  run_id=admission['run_id'], job_spec_sha256=admission['job_spec_sha256'])
    save(folder / 'provider-receipt.json', result)
    return result


def main():
    if (HERE / 'submission-claim.json').exists():
        raise RuntimeError('Submission already claimed; inspect the provider, never resubmit automatically')
    handoff.verify_reviewed()
    proposal = HERE.parent / 'execution-proposal'
    pins = {'job-spec.json': '15ee39c4c7692b8f515a6412b64a39428410f8ce9fa9e23f113ba1311b7f23ff',
            'job-receipt.json': '1c11f4b12099475fccee19e59363f2f3ca9f21d9ad77ce26f0903dbcfba7177d',
            'handoff.json': '8ac3af55f4ab6dd9f6c7580b0d79d35a6884ab1c9cf5239f49ead361f19716b5'}
    for name, expected in pins.items():
        if sha(proposal / name) != expected:
            raise ValueError('Approved proposal changed: ' + name)
    spec = json.loads((proposal / 'job-spec.json').read_bytes())
    receipt = json.loads((proposal / 'job-receipt.json').read_bytes())
    inventory = json.loads((proposal / 'handoff.json').read_bytes())
    handoff.equivalent(spec, receipt, json.loads((HERE.parent / 'job-spec.json').read_bytes()),
                       json.loads((HERE.parent / 'job-receipt.json').read_bytes()))
    native = training_admission.sdk_spec(spec)
    staging = json.loads((HERE / 'staging.json').read_bytes())
    expected = [dict(path=e['remote_path'], bytes=e['bytes'], sha256=e['sha256'])
                for e in inventory['transfer_inventory']]
    if staging['run_id'] != receipt['run_id'] or staging['inputs_readback_verified'] != expected:
        raise ValueError('Staging does not bind the exact approved inputs')
    for arm in ('reference', 'candidate'):
        evidence = staging['adapter_evidence'][arm]
        if (evidence['manifest_sha256'] != receipt[arm + '_manifest_sha256']
                or evidence['config_sha256'] != receipt[arm + '_adapter_files']['adapter_config.json']
                or evidence['weight_size_matches_manifest'] is not True):
            raise ValueError('Adapter evidence differs')
    prior = json.loads((HERE / 'live-check.json').read_bytes())
    if (datetime.now(timezone.utc) - datetime.fromisoformat(prior['utc'])).total_seconds() > 1800:
        raise ValueError('Refresh the live funding observation before launch')
    api = HfApi()
    if api.whoami()['name'] != spec['namespace'] or not api.bucket_info('Mojionix/pahlavi-pilot').private:
        raise ValueError('Account/bucket identity differs')
    hardware = next(h for h in api.list_jobs_hardware() if h.name == spec['flavor'])
    if hardware.unit_label != 'minute':
        raise ValueError('Unexpected billing unit')
    rate = Decimal(str(hardware.unit_cost_usd))
    allowance = rate * receipt['native_timeout_minutes'] + Decimal('0.50')
    if allowance > Decimal('5.51') or Decimal(prior['browser_observed_credit_usd']) < allowance:
        raise ValueError('Price/funding exceeds approved envelope')
    jobs = api.list_jobs(namespace=spec['namespace'], timeout=30)
    if any(j.status.stage not in TERMINAL_JOB_STAGES or
           (j.labels or {}).get('trial_id') == receipt['run_id'] for j in jobs):
        raise ValueError('An active or matching job exists')
    try:
        if list(api.list_bucket_tree('Mojionix/pahlavi-pilot', prefix=receipt['output_prefix'], recursive=True)):
            raise ValueError('Output prefix is not empty')
    except EntryNotFoundError:
        pass
    admission = dict(utc=datetime.now(timezone.utc).isoformat(),
        status='SUBMISSION_CLAIMED_OUTCOME_UNKNOWN_UNTIL_PROVIDER_RECEIPT',
        authorization_question='Use existing HF credentials, stage/read back the two verified files, and launch one inference-only job within 120 minutes and USD5.51 from existing credit, without recharge?',
        user_reply='yes and we can increase the credit if needed',
        scope='One inference job only; no training, local weight download, recharge or automatic retry',
        owner='root', run_id=receipt['run_id'], source_commit='064526b',
        job_spec_sha256=pins['job-spec.json'], handoff_sha256=pins['handoff.json'],
        staging_sha256=sha(HERE / 'staging.json'), live_check_sha256=sha(HERE / 'live-check.json'),
        hardware=asdict(hardware), maximum_compute_usd=str(rate * receipt['native_timeout_minutes']),
        reserve_usd='0.50', maximum_allowance_usd=str(allowance), approved_cap_usd='5.51',
        observed_credit_usd=prior['browser_observed_credit_usd'], native_timeout_minutes=120,
        active_jobs=[], matching_trial_ids=[], output_prefix_empty=True,
        server_weight_rehash_gpu_canary_and_persistence='PENDING')
    print(json.dumps(submit_once(api, native, HERE, admission), default=str))


def self_check():
    calls = []
    def unknown(**kwargs):
        calls.append(kwargs)
        raise TimeoutError('Simulated ambiguous provider outcome')
    root = HERE.parents[2] / 'resources/local/claim-self-checks' / uuid.uuid4().hex
    root.mkdir(parents=True)
    for expected in (TimeoutError, FileExistsError):
        try:
            submit_once(SimpleNamespace(run_job=unknown), {'flavor': 'test-only'}, root,
                        {'run_id': 'test-only', 'job_spec_sha256': 'test-only'})
        except expected:
            pass
        else:
            raise AssertionError('Claim failed to prevent retry')
    assert len(calls) == 1 and (root / 'submission-claim.json').exists()
    print('PASS: ambiguous submission retains claim; a second submission makes no API call')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--submit', action='store_true', help='Execute the already-authorized single submission')
    args = parser.parse_args()
    main() if args.submit else self_check()
