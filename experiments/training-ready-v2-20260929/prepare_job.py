"""Prepare/check the exact corrected job locally. Never uploads or submits."""
import argparse
import ast
import base64
import dataclasses
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT), str(ROOT / 'resources/local/hf-client-venv/Lib/site-packages')]
from cloud_pilot import hf_mixed


def build():
    manifest = HERE / 'data-manifest.json'
    train = ROOT / 'resources/local/training-ready-v2-20260929/data/train.jsonl'
    identity = hashlib.sha256(manifest.read_bytes()).hexdigest()
    # Preparation identity is deterministic; no job has been submitted with it.
    spec, receipt = hf_mixed.prepare(train, manifest, identity[:32])
    transport = ast.parse(spec['command'][3])
    payload = ast.literal_eval(transport.body[1].value.args[0].args[0])
    decoded = gzip.decompress(base64.b64decode(payload)).decode()
    tree = ast.parse(decoded)
    assert isinstance(tree.body[-1], ast.Expr) and tree.body[-1].value.func.id == 'execute_mixed'
    tree.body.pop()  # Compile definitions/identities only; never execute the cloud job.
    namespace = {}
    exec(compile(tree, 'prepared-corrected-v2-artifact', 'exec'), namespace)
    for name, entry in namespace['scripts'].items():
        content = base64.b64decode(entry['content'])
        assert content == (ROOT / 'cloud_pilot' / name).read_bytes(), name
        compile(content, name, 'exec')
    assert callable(namespace['execute_mixed'])
    spec['volumes'] = [dataclasses.asdict(v) for v in spec['volumes']]
    receipt.update(status='PREPARED_NOT_SUBMITTED', exact_embedded_scripts_match=True,
                   dataset_version='corrected-v2', controller_sha256=hf_mixed.file_sha256(hf_mixed.__file__),
                   cloud_submitted=False, launch_authorized=False,
                   pending_launch_gates=['fresh user launch instruction', 'fresh cumulative budget/rate/idle-job check',
                                         'server GPU/runtime and persistence canaries'])
    dump = lambda value: (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode()
    return dump(spec), dump(receipt)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    spec, receipt = build()
    destinations = {ROOT / 'resources/local/training-ready-v2-20260929/job-spec.json': spec,
                    HERE / 'execution-preparation.json': receipt}
    if args.check:
        for path, data in destinations.items():
            assert path.read_bytes() == data, path
    else:
        assert not any(path.exists() for path in destinations), 'Refusing frozen package overwrite'
        for path, data in destinations.items():
            with path.open('xb') as stream:
                stream.write(data)
    value = json.loads(receipt)
    print(json.dumps({k: value[k] for k in ('status', 'data_manifest_sha256', 'train_sha256',
                                            'command_arg_utf8_bytes', 'command_total_utf8_bytes_with_nul')}))


if __name__ == '__main__':
    main()
