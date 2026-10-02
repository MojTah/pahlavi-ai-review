"""Prepare/check an offline inference specimen; never authenticate or submit."""
import argparse
import ast
import base64
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import socket
import sys
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.extend([str(ROOT / 'resources/local/train-fit-deps'),
                 str(ROOT / 'resources/local/hf-client-venv/Lib/site-packages')])
PACKET = ROOT / 'experiments/corrected-learning-diagnosis-20260930'
# Reserved preparation identity, not an executed run. Fresh identity at launch.
RUN_ID = '20260930000000000000000000000002'
BUDGET = {'compute_seconds': 6600, 'internal_seconds': 6900, 'native_timeout_minutes': 120}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def build():
    from cloud_pilot import hf_learning_eval, training_admission
    from huggingface_hub import HfApi
    module_spec = importlib.util.spec_from_file_location('frozen_packet', PACKET / 'prepare.py')
    packet = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(packet)
    with patch.object(socket.socket, 'connect', side_effect=AssertionError('Offline only')), \
            patch.object(socket, 'create_connection', side_effect=AssertionError('Offline only')), \
            patch.object(HfApi, 'run_job', autospec=True, side_effect=AssertionError('No launch')):
        for name, raw in packet.build().items():
            assert (PACKET / name).read_bytes() == raw, name
        spec, receipt = hf_learning_eval.prepare(PACKET / 'inputs.jsonl', RUN_ID,
            corrected_binding=json.loads((PACKET / 'binding.json').read_bytes()), timing_budget=BUDGET)
        # Use the CLI/SDK's canonical camelCase representation, not dataclasses.asdict.
        saved = {**spec, 'volumes': [v.to_dict() for v in spec['volumes']]}
        native = training_admission.sdk_spec(saved)
        assert training_admission.plain(native) == training_admission.plain(spec)
    transport = ast.parse(spec['command'][3])
    compressed = max((n.value for n in ast.walk(transport)
                     if isinstance(n, ast.Constant) and isinstance(n.value, str)), key=len)
    program = gzip.decompress(base64.b64decode(compressed))
    assert sha(program) == receipt['decoded_command_sha256']
    tree = ast.parse(program)
    assignments = {n.targets[0].id: ast.literal_eval(n.value) for n in tree.body
                   if isinstance(n, ast.Assign) and len(n.targets) == 1
                   and isinstance(n.targets[0], ast.Name) and n.targets[0].id in {'settings', 'scripts'}}
    assert all(assignments['settings'][k] == v for k, v in BUDGET.items())
    assert spec['timeout'] == '120m'
    for name, entry in assignments['scripts'].items():
        raw = base64.b64decode(entry['content'])
        assert raw == (ROOT / 'cloud_pilot' / name).read_bytes() and sha(raw) == entry['sha256']
        compile(raw, name, 'exec')
    compile(program, 'reviewed-inference-specimen', 'exec')
    assert max(receipt['command_arg_utf8_bytes']) + 1 < 100 * 1024
    assert receipt['command_total_utf8_bytes_with_nul'] < 1024 ** 2
    assert all(set(json.loads(line)) == {'case_id', 'prompt'}
               for line in (PACKET / 'inputs.jsonl').read_bytes().splitlines())
    census = json.loads((PACKET / 'census.json').read_bytes())
    bound = dict(census['inputs_sha256'])
    bound.update({(PACKET / name).relative_to(ROOT).as_posix(): sha((PACKET / name).read_bytes())
                  for name in ('prepare.py', 'inputs.jsonl', 'references.jsonl', 'binding.json', 'census.json')})
    # Includes launch-time reconstruction/import dependencies, beyond embedded helpers.
    for name in ('hf_learning_eval.py', 'learning_eval.py', *hf_learning_eval.HELPERS,
                 'hf_contextual.py', 'hf_continue.py', 'hf_convert.py', 'hf_dev_assisted.py',
                 'hf_preflight.py', 'hf_train.py', 'hf_train_recall.py', 'training_admission.py'):
        path = ROOT / 'cloud_pilot' / name
        bound[path.relative_to(ROOT).as_posix()] = sha(path.read_bytes())
    for relative in ('experiments/mixed-supervision-20260929/prepare.py',
                     'cloud_pilot/requirements-linux.lock', 'cloud_pilot/contract.json'):
        path = ROOT / relative
        bound[relative] = sha(path.read_bytes())
    for name in ('job-spec.json', 'job-receipt.json'):
        path = PACKET / name
        bound[path.relative_to(ROOT).as_posix()] = sha(path.read_bytes())
    for module in tuple(sys.modules.values()):
        source = getattr(module, '__file__', None)
        if source:
            path = Path(source).resolve()
            if path.suffix == '.py' and path.is_relative_to(ROOT / 'cloud_pilot'):
                bound[path.relative_to(ROOT).as_posix()] = sha(path.read_bytes())
    bound[Path(__file__).relative_to(ROOT).as_posix()] = sha(Path(__file__).read_bytes())
    for path, expected in bound.items():
        assert sha((ROOT / path).read_bytes()) == expected, path
    spec_raw, receipt_raw = encode(saved), encode(receipt)
    return {'job-spec.json': spec_raw, 'job-receipt.json': receipt_raw,
            'runtime-check.json': encode(dict(status='LOCAL_PREPARED_NOT_SUBMITTED',
                source_sha256=bound, job_spec_sha256=sha(spec_raw), job_receipt_sha256=sha(receipt_raw),
                scientific_packet_unchanged=True, embedded_helpers_equal=True, sdk_serialization_passed=True,
                launch_authorized=False, gpu_runtime_exercised=False, remote_persistence_verified=False))}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for name, raw in build().items():
        path = HERE / name
        if args.check:
            assert path.read_bytes() == raw, name
        else:
            path.write_bytes(raw)
    print('PASS: exact frozen packet, current runtime specimen, SDK serialization and helper bytes; no launch')
