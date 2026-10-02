"""Verify staged byte-bound files through a real Windows-style Git checkout."""
import hashlib
import json
from pathlib import Path
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    evidence = json.loads((HERE / 'runtime-check.json').read_bytes())
    paths = dict(evidence['source_sha256'])
    for name in ('job-spec.json', 'job-receipt.json', 'runtime-check.json'):
        path = HERE / name
        paths[path.relative_to(ROOT).as_posix()] = sha(path.read_bytes())
    tracked, local = {}, {}
    for path, expected in paths.items():
        assert sha((ROOT / path).read_bytes()) == expected, ('Working bytes differ', path)
        if path.startswith('resources/local/'):
            local[path] = expected
        else:
            tracked[path] = expected
    attrs = subprocess.check_output(['git', 'check-attr', '-z', 'text', '--', *tracked], cwd=ROOT).split(b'\0')
    assert all(attrs[i + 2] == b'unset' for i in range(0, len(attrs) - 1, 3)), 'Missing -text rule'
    destination = ROOT / 'resources/local/readiness-checkout' / uuid.uuid4().hex
    destination.mkdir(parents=True)
    # No index/worktree replacement or deletion. Export only to a fresh ignored directory.
    subprocess.run(['git', '-c', 'core.autocrlf=true', 'checkout-index',
                    '--prefix=' + destination.as_posix() + '/', '--', *tracked], cwd=ROOT, check=True)
    for path, expected in tracked.items():
        assert sha((destination / path).read_bytes()) == expected, ('Staged checkout bytes differ', path)
    result = dict(status='PASS', operation='git -c core.autocrlf=true checkout-index to fresh ignored directory',
        checkout=str(destination), byte_identical_tracked_files=len(tracked),
        hash_verified_local_only_files=len(local), tracked_sha256=tracked, local_only_sha256=local,
        caveat='Local private data/tokenizer stay outside Git; this export is not a standalone full-project install.')
    (HERE / 'checkout-check.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f'PASS: {len(tracked)} actual checkout files byte-identical; {len(local)} local-only files hash-verified')


if __name__ == '__main__':
    main()
