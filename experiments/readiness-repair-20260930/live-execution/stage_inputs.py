"""One user-authorized input staging/readback; no job submission or weight download."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
import prepare_execution as handoff
from cloud_pilot import training_admission
from huggingface_hub import HfApi
from huggingface_hub.errors import EntryNotFoundError


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    handoff.verify_reviewed()
    proposal = HERE.parent / 'execution-proposal'
    inventory = json.loads((proposal / 'handoff.json').read_bytes())
    spec = json.loads((proposal / 'job-spec.json').read_bytes())
    receipt = json.loads((proposal / 'job-receipt.json').read_bytes())
    handoff.equivalent(spec, receipt,
        json.loads((HERE.parent / 'job-spec.json').read_bytes()),
        json.loads((HERE.parent / 'job-receipt.json').read_bytes()))
    for name, entry in inventory['local_files'].items():
        path = proposal / name
        assert path.stat().st_size == entry['bytes'] and sha(path) == entry['sha256']
    api = HfApi()
    assert api.whoami()['name'] == spec['namespace'] == 'Mojionix'
    bucket = 'Mojionix/pahlavi-pilot'
    assert api.bucket_info(bucket).private is True
    try:
        assert not list(api.list_bucket_tree(bucket, prefix=receipt['output_prefix'], recursive=True)), 'Output prefix already exists'
    except EntryNotFoundError:
        pass
    mounts = {v['mountPath']: v['path'] for v in spec['volumes']}
    arms = {'reference': (mounts['/original'], 'training/adapter'),
            'candidate': (mounts['/mixed'], 'mixed/training/adapter')}
    paths = [entry['remote_path'] for entry in inventory['transfer_inventory']]
    for prefix, relative in arms.values():
        paths.extend([prefix + '/manifest.json', prefix + '/' + relative + '/adapter_config.json',
                      prefix + '/' + relative + '/adapter_model.safetensors'])
    remote = {f.path: f for f in api.get_bucket_paths_info(bucket, paths)}
    local = PROJECT / 'resources/local/learning-diagnosis-live' / receipt['run_id']
    local.mkdir(parents=True, exist_ok=True)
    verified_arms = {}
    for arm, (prefix, relative) in arms.items():
        manifest_key, config_key = prefix + '/manifest.json', prefix + '/' + relative + '/adapter_config.json'
        assert 0 < remote[manifest_key].size < 2 * 1024**2
        assert 0 < remote[config_key].size < 64 * 1024
        manifest_file, config_file = local / (arm + '-manifest.json'), local / (arm + '-adapter-config.json')
        api.download_bucket_files(bucket, [(remote[manifest_key], manifest_file), (remote[config_key], config_file)], raise_on_missing_files=True)
        assert sha(manifest_file) == receipt[arm + '_manifest_sha256']
        assert sha(config_file) == receipt[arm + '_adapter_files']['adapter_config.json']
        manifest = json.loads(manifest_file.read_bytes())
        for name, expected in receipt[arm + '_adapter_files'].items():
            key = relative + '/' + name
            assert manifest['files'][key]['sha256'] == expected
            assert remote[prefix + '/' + key].size == manifest['files'][key]['bytes']
        verified_arms[arm] = dict(manifest_sha256=sha(manifest_file), config_sha256=sha(config_file),
                                 weight_size_matches_manifest=True, weight_bytes_rehashed_locally=False)
    added, verified_inputs = [], []
    for entry in inventory['transfer_inventory']:
        source = Path(entry['local_path'])
        if not source.is_absolute(): source = PROJECT / source
        assert source.stat().st_size == entry['bytes'] and sha(source) == entry['sha256']
        key = entry['remote_path']
        target = local / Path(key).name
        if key in remote:
            assert remote[key].size == entry['bytes'], 'Existing input size differs; refusing overwrite'
            api.download_bucket_files(bucket, [(remote[key], target)], raise_on_missing_files=True)
            assert sha(target) == entry['sha256'], 'Existing input hash differs; refusing overwrite'
        else:
            api.batch_bucket_files(bucket, add=[(source, key)])
            added.append(key)
            api.download_bucket_files(bucket, [(key, target)], raise_on_missing_files=True)
        assert target.stat().st_size == entry['bytes'] and sha(target) == entry['sha256']
        verified_inputs.append(dict(path=key, bytes=entry['bytes'], sha256=sha(target)))
    result = dict(utc=datetime.now(timezone.utc).isoformat(), run_id=receipt['run_id'],
        private_bucket=True, output_prefix_empty_at_check=True, uploaded_paths=added,
        inputs_readback_verified=verified_inputs, adapter_evidence=verified_arms,
        weights_downloaded=False, server_weight_rehash_required=True, job_submitted=False)
    (HERE / 'staging.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
