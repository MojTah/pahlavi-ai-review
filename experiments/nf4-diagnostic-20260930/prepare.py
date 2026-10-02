"""Build a versioned NF4 inference proposal; no authentication or launch."""
import ast
import base64
import inspect
import json
import lzma
from pathlib import Path
import re
import sys
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'experiments/readiness-repair-20260930'))
import prepare_execution as frozen

sha, encode = frozen.reviewed.sha, frozen.reviewed.encode
PACKET = frozen.reviewed.PACKET
BF16_OUTPUT = ROOT / 'experiments/readiness-repair-20260930/live-execution/recovered/evaluation/evaluation/predictions.jsonl'
BF16_SHA = 'f719d7e408d3db94afa2fb99cc77158aa732cd116e0970ae79229c91cfa24816'


def reconcile_evaluation(output):
    """Extend the frozen finalizer only for an interrupted NF4 model load."""
    import os
    import tempfile
    path = Path(output) / 'run.json'
    state = json.loads(path.read_text('utf-8'))
    if state['status'] == 'loading_nf4':
        predictions = Path(output) / 'predictions.jsonl'
        if (state['attempted_outputs'] != 0 or state['recorded_outputs'] != 0
                or state['active_output_id'] is not None
                or (predictions.exists() and predictions.stat().st_size)):
            raise ValueError('NF4 loading ledger contains generation attempts')
        state.update(status='incomplete', error_type='ChildInterrupted',
                     error='Evaluator stopped during NF4 loading before any generation')
        # Validate in an isolated scratch ledger first; preserve corrupt originals.
        with tempfile.TemporaryDirectory(dir=path.parent) as scratch:
            scratch_path = Path(scratch)
            (scratch_path / 'run.json').write_text(json.dumps(state), encoding='utf-8')
            state = baseline_reconcile_evaluation(scratch_path)
        temporary = path.with_suffix('.json.tmp')
        temporary.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')
        os.replace(temporary, path)
        return state
    return baseline_reconcile_evaluation(output)


def literals(program):
    return {node.targets[0].id: ast.literal_eval(node.value) for node in ast.parse(program).body
            if isinstance(node, ast.Assign) and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name) and node.targets[0].id in {'settings', 'scripts'}}


def decoded(command):
    constants = [n.value for n in ast.walk(ast.parse(command))
                 if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    return lzma.decompress(base64.b64decode(max(constants, key=len))).decode('utf-8')


def build(run_id):
    frozen.verify_reviewed()
    if not re.fullmatch('[a-f0-9]{32}', run_id):
        raise ValueError('Fresh hexadecimal run ID required')
    if sha(BF16_OUTPUT.read_bytes()) != BF16_SHA:
        raise ValueError('Cached BF16 comparison outputs changed')
    from cloud_pilot import hf_contextual, hf_learning_eval, training_admission
    spec, receipt = hf_learning_eval.prepare(PACKET / 'inputs.jsonl', run_id,
        corrected_binding=json.loads((PACKET / 'binding.json').read_bytes()),
        timing_budget=frozen.reviewed.BUDGET)
    original = frozen.decoded(spec['command'][3])
    values = literals(original)
    settings, scripts = values['settings'], values['scripts']
    scripts['bf16_learning_eval.py'] = scripts['learning_eval.py']
    raw = (ROOT / 'cloud_pilot/nf4_learning_eval.py').read_bytes()
    scripts['learning_eval.py'] = dict(sha256=sha(raw), content=base64.b64encode(raw).decode('ascii'))
    settings['runner_sha256'] = sha(raw)
    settings['helper_sha256']['bf16_learning_eval.py'] = scripts['bf16_learning_eval.py']['sha256']
    settings['numerical_condition'] = 'nf4_training_matched'
    # Only replace the two literal payloads; retain every frozen parent function byte.
    lines = original.splitlines(keepends=True)
    for node in reversed(ast.parse(original).body):
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            key = node.targets[0].id
            if key in values:
                lines[node.lineno - 1:node.end_lineno] = [key + '=' + repr(values[key]) + '\n']
    program = ''.join(lines)
    boundary = program.index('\nsettings=') + 1
    program = (program[:boundary] + 'baseline_reconcile_evaluation=reconcile_evaluation\n'
               + inspect.getsource(reconcile_evaluation) + '\n' + program[boundary:])
    compile(program, 'nf4-inference-parent', 'exec')
    # The second frozen runner exceeds the existing gzip/100KiB argument guard.
    # Stdlib LZMA preserves the exact program and stays under that same guard.
    compressed = base64.b64encode(lzma.compress(program.encode())).decode('ascii')
    spec['command'][3] = ('import base64,lzma,hashlib\n'
        '_code=lzma.decompress(base64.b64decode(' + repr(compressed) + '))\n'
        'if hashlib.sha256(_code).hexdigest() != ' + repr(sha(program.encode())) + ':\n'
        "    raise ValueError('Decoded NF4 source checksum mismatch')\n"
        "exec(compile(_code,'hf-nf4-diagnosis','exec'))\n")
    assert decoded(spec['command'][3]) == program
    spec['labels']['purpose'] = 'nf4-learning-diagnosis'
    prefix = 'nf4-learning-diagnosis/' + run_id
    spec['volumes'][-1].path = prefix
    lengths, total = hf_contextual.command_lengths(spec['command'])
    if max(lengths) + 1 >= 100 * 1024 or total >= 1024 ** 2:
        raise ValueError('Command exceeds reviewed transport envelope: ' + str(lengths))
    receipt.update(settings, output_prefix=prefix,
        decoded_command_sha256=sha(program.encode()), command_sha256=sha(spec['command'][3].encode()),
        command_arg_utf8_bytes=lengths, command_total_utf8_bytes_with_nul=total,
        cached_bf16_predictions_sha256=BF16_SHA, protocol_sha256=sha((HERE / 'PLAN.md').read_bytes()))
    native = training_admission.sdk_spec(spec)
    saved = training_admission.plain(native)
    assert training_admission.plain(training_admission.sdk_spec(saved)) == saved
    sources = dict(frozen.verify_reviewed()['source_sha256'])
    for path in [Path(__file__), HERE / 'PLAN.md', ROOT / 'cloud_pilot/nf4_learning_eval.py',
                 ROOT / 'cloud_pilot/test_nf4_learning_eval.py', HERE / 'test_prepare.py', HERE / 'execute.py', BF16_OUTPUT,
                 ROOT / 'experiments/readiness-repair-20260930/prepare_execution.py',
                 ROOT / 'experiments/readiness-repair-20260930/live-execution/submit_once.py',
                 ROOT / 'experiments/readiness-repair-20260930/live-execution/stage_inputs.py']:
        sources[path.relative_to(ROOT).as_posix()] = sha(path.read_bytes())
    payload = {'job-spec.json': encode(saved), 'job-receipt.json': encode(receipt)}
    payload['check.json'] = encode(dict(status='PREPARED_NOT_SUBMITTED', run_id=run_id,
        source_sha256=sources, files_sha256={k: sha(v) for k, v in payload.items()},
        sdk_roundtrip=True, cloud_runtime_verified=False, frozen_baseline_unchanged=True))
    return payload


def materialize(destination=None):
    run_id = uuid.uuid4().hex
    payload = build(run_id)
    destination = Path(destination) if destination else HERE / 'execution-proposal'
    destination.mkdir()  # Never overwrite or reuse a proposal.
    for name, raw in payload.items():
        with (destination / name).open('xb') as stream:
            stream.write(raw)
    return destination


def verify(destination):
    check = json.loads((destination / 'check.json').read_bytes())
    for relative, expected in check['source_sha256'].items():
        if sha((ROOT / relative).read_bytes()) != expected:
            raise ValueError('Reviewed source changed: ' + relative)
    for name, raw in build(check['run_id']).items():
        if (destination / name).read_bytes() != raw:
            raise ValueError('Exact proposal reconstruction failed: ' + name)
    return check


if __name__ == '__main__':
    print(materialize())
