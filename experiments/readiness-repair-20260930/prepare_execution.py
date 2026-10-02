"""Materialize a fresh LOCAL ONLY handoff. No launch or authorization."""
import argparse
import ast
import base64
import copy
import gzip
import json
from pathlib import Path
import re
import uuid

import prepare_runtime as reviewed

CHECK_SHA256 = '474b947a0325dcd7b2f6161cc2099f0d234a71b1f859899d7bba50935448c1dc'


def verify_reviewed():
    raw = (reviewed.HERE / 'runtime-check.json').read_bytes()
    if reviewed.sha(raw) != CHECK_SHA256:
        raise ValueError('Reviewed runtime check changed')
    check = json.loads(raw)
    for relative, expected in check['source_sha256'].items():
        if reviewed.sha((reviewed.ROOT / relative).read_bytes()) != expected:
            raise ValueError('Reviewed source changed: ' + relative)
    for name in ('job-spec', 'job-receipt'):
        if reviewed.sha((reviewed.HERE / (name + '.json')).read_bytes()) != check[name.replace('-', '_') + '_sha256']:
            raise ValueError('Reviewed specimen changed: ' + name)
    for name, rebuilt in reviewed.build().items():
        if (reviewed.HERE / name).read_bytes() != rebuilt:
            raise ValueError('Reviewed reconstruction differs: ' + name)
    return check


def decoded(command):
    constants = [node.value for node in ast.walk(ast.parse(command))
                 if isinstance(node, ast.Constant) and isinstance(node.value, str)]
    return gzip.decompress(base64.b64decode(max(constants, key=len))).decode('utf-8')


def equivalent(spec, receipt, original_spec, original_receipt):
    """Permit identity/output changes only; verify all derived values separately."""
    from cloud_pilot import hf_contextual, training_admission
    fresh, old = receipt['run_id'], original_receipt['run_id']
    if not re.fullmatch('[a-f0-9]{32}', fresh) or fresh == old:
        raise ValueError('Fresh hexadecimal run identity required')
    program = decoded(spec['command'][3])
    old_program = decoded(original_spec['command'][3])
    if program.count(repr(fresh)) != 1 or program.replace(repr(fresh), repr(old)) != old_program:
        raise ValueError('Runtime differs beyond run identity')
    if spec['command'][3] != hf_contextual.compressed_command(program):
        raise ValueError('Runtime transport differs')
    lengths, total = hf_contextual.command_lengths(spec['command'])
    expected_derived = dict(decoded_command_sha256=reviewed.sha(program.encode()),
        command_sha256=reviewed.sha(spec['command'][3].encode()),
        command_arg_utf8_bytes=lengths, command_total_utf8_bytes_with_nul=total)
    if any(receipt[name] != value for name, value in expected_derived.items()):
        raise ValueError('Derived command identity differs')
    if max(lengths) + 1 >= 100 * 1024 or total >= 1024 ** 2:
        raise ValueError('Command exceeds reviewed transport limits')
    expected_receipt = copy.deepcopy(original_receipt)
    expected_receipt.update(run_id=fresh, output_prefix='learning-diagnosis/' + fresh, **expected_derived)
    if receipt != expected_receipt:
        raise ValueError('Scientific/runtime receipt differs')
    expected_spec = copy.deepcopy(original_spec)
    expected_spec['command'][3] = spec['command'][3]
    expected_spec['labels']['trial_id'] = fresh
    expected_spec['volumes'][-1]['path'] = receipt['output_prefix']
    if training_admission.plain(spec) != expected_spec:
        raise ValueError('SDK specification differs beyond permitted identity changes')
    training_admission.sdk_spec(spec)


def prepare(run_id=None, *, out=None):
    check = verify_reviewed()  # Verify source bytes before rebuilding/importing runtime helpers.
    from cloud_pilot import hf_learning_eval, training_admission
    run_id = uuid.uuid4().hex if run_id is None else run_id
    if not re.fullmatch('[a-f0-9]{32}', run_id) or run_id == reviewed.RUN_ID:
        raise ValueError('Fresh hexadecimal run identity required')
    parent = reviewed.ROOT / 'resources/local/prepared-executions'
    destination = Path(out) if out is not None else parent / run_id
    parent = destination.parent
    if destination.exists():
        raise FileExistsError('Local handoff already exists: ' + str(destination))
    spec, receipt = hf_learning_eval.prepare(reviewed.PACKET / 'inputs.jsonl', run_id,
        corrected_binding=json.loads((reviewed.PACKET / 'binding.json').read_bytes()), timing_budget=reviewed.BUDGET)
    original_spec = json.loads((reviewed.HERE / 'job-spec.json').read_bytes())
    original_receipt = json.loads((reviewed.HERE / 'job-receipt.json').read_bytes())
    equivalent(spec, receipt, original_spec, original_receipt)
    prompts = (reviewed.PACKET / 'inputs.jsonl').read_bytes()
    bundle = reviewed.ROOT / 'resources/local' / receipt['bundle_name']
    bundle_raw = bundle.read_bytes()
    if reviewed.sha(prompts) != receipt['inputs_sha256'] or reviewed.sha(bundle_raw) != receipt['bundle_sha256']:
        raise ValueError('Transfer input/bundle differs')
    saved = training_admission.plain(spec)
    files = {'job-spec.json': reviewed.encode(saved), 'job-receipt.json': reviewed.encode(receipt),
             receipt['inputs_name']: prompts}
    inventory = dict(status='NOT_SUBMITTED', authorization_status='NOT_AUTHORIZED', run_id=run_id,
        output_prefix=receipt['output_prefix'], reviewed_runtime_check_sha256=CHECK_SHA256,
        reviewed_spec_sha256=check['job_spec_sha256'], reviewed_receipt_sha256=check['job_receipt_sha256'],
        sdk_serialization_passed=True, permitted_changes=['run_id', 'output_prefix', 'labels.trial_id',
            'decoded_command_sha256', 'command_sha256', 'command_arg_utf8_bytes', 'command_total_utf8_bytes_with_nul'],
        local_files={name: dict(sha256=reviewed.sha(raw), bytes=len(raw)) for name, raw in files.items()},
        transfer_inventory=[dict(local_path=str(destination / receipt['inputs_name']), remote_path='inputs/' + receipt['inputs_name'],
            sha256=receipt['inputs_sha256'], bytes=len(prompts), content='case_id and prompt only'),
            dict(local_path=str(bundle), remote_path='inputs/' + receipt['bundle_name'],
            sha256=receipt['bundle_sha256'], bytes=len(bundle_raw), content='existing qualified bundle; not copied')],
        excluded_from_transfer=['references.jsonl', 'binding.json', 'census.json', 'local model/adapter weights',
                                'job-spec.json', 'job-receipt.json', 'handoff.json'],
        remote_staging_verified=False, provider_submitted=False)
    files['handoff.json'] = reviewed.encode(inventory)
    parent.mkdir(parents=True, exist_ok=True)
    destination.mkdir()  # Exclusive creation: never reuse or overwrite a handoff.
    for name, raw in files.items():
        with (destination / name).open('xb') as stream:
            stream.write(raw)
    return destination


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='Exact fresh local handoff directory')
    args = parser.parse_args()
    print(prepare(out=args.out))
    print('NOT_SUBMITTED / NOT_AUTHORIZED: local preparation only')
