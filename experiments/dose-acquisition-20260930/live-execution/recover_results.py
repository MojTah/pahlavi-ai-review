"""Read back this completed job's small evidence; never download model weights."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
JOB = '6abd57e0fbc85ba68235c601'
BUCKET = 'Mojionix/pahlavi-pilot'
PREFIX = 'dose-acquisition/8385384aa7eb46e3955af8cfe8706447'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == raw, f'Existing evidence differs: {path}'
    else:
        path.write_bytes(raw)


def main():
    sys.path.append(str(ROOT / 'resources/local/hf-client-venv/Lib/site-packages'))
    from huggingface_hub import HfApi
    api = HfApi()
    job = api.inspect_job(job_id=JOB, namespace='Mojionix')
    assert str(job.status.stage) == 'COMPLETED'
    assert api.bucket_info(BUCKET).private is True
    logs = list(api.fetch_job_logs(job_id=JOB, namespace='Mojionix', follow=False))
    # HF splits large log records at 16 KiB, including in the middle of strings.
    start = next(i for i, x in enumerate(logs) if str(x).startswith('{"stage": "ready_to_persist"'))
    record = ''
    final = None
    for chunk in logs[start:]:
        record += str(chunk)
        try:
            final = json.loads(record)
            break
        except json.JSONDecodeError:
            assert len(record) < 200_000
    assert final is not None and final['stage'] == 'ready_to_persist'
    save(HERE / 'terminal-log.txt', ('\n'.join(map(str, logs)) + '\n').encode())
    tree = {f.path: f for f in api.list_bucket_tree(BUCKET, prefix=PREFIX, recursive=True)
            if hasattr(f, 'size')}
    recovered = HERE / 'recovered'
    recovered.mkdir(exist_ok=True)
    key = PREFIX + '/manifest.json'
    assert key in tree and tree[key].size == final['manifest_bytes'] < 2_000_000
    target = recovered / 'manifest.json'
    if not target.exists():
        api.download_bucket_files(BUCKET, [(tree[key], target)], raise_on_missing_files=True)
    raw = target.read_bytes()
    assert digest(raw) == final['manifest_sha256']
    manifest = json.loads(raw)
    assert manifest == final['manifest']
    assert manifest['run_id'] == PREFIX.split('/')[-1]
    downloads, verified, weights = [], [], []
    for name, info in manifest['files'].items():
        rel = PurePosixPath(name)
        assert not rel.is_absolute() and '..' not in rel.parts and '\\' not in name and ':' not in name
        remote = PREFIX + '/' + name
        assert remote in tree and tree[remote].size == info['bytes'], name
        if rel.suffix == '.safetensors':
            weights.append(dict(path=name, bytes=info['bytes'], runner_sha256=info['sha256'],
                                remote_size_verified=True, remote_sha256_independently_verified=False))
            continue
        assert rel.suffix in {'.json', '.jsonl', '.md', '.log'} and info['bytes'] < 2_000_000, name
        path = recovered.joinpath(*rel.parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            downloads.append((tree[remote], path))
        verified.append(dict(path=name, **info))
    assert sum(x['bytes'] for x in verified) < 10_000_000
    if downloads:
        api.download_bucket_files(BUCKET, downloads, raise_on_missing_files=True)
    for item in verified:
        raw = (recovered / item['path']).read_bytes()
        assert len(raw) == item['bytes'] and digest(raw) == item['sha256'], item['path']
    result = dict(job_id=JOB, stage=str(job.status.stage), created_at=str(job.created_at),
                  started_at=str(job.started_at), finished_at=str(job.finished_at),
                  manifest_sha256=final['manifest_sha256'], files=verified,
                  model_weights_not_downloaded=weights,
                  small_file_sha256_readback_verified=True,
                  downloaded_evidence_bytes=len((recovered / 'manifest.json').read_bytes()) + sum(x['bytes'] for x in verified))
    save(HERE / 'terminal.json', (json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode())
    print(json.dumps({k: v for k, v in result.items() if k not in ('files', 'model_weights_not_downloaded')}))
    print(json.dumps({'small_files':len(verified), 'cloud_only_adapters':len(weights),
                      'checked_utc':datetime.now(timezone.utc).isoformat()}))


if __name__ == '__main__':
    main()
