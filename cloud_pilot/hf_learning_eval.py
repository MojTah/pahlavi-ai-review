"""Prepare one bounded two-checkpoint inference job; never authenticate or launch."""
import base64
import hashlib
import inspect
import json
from pathlib import Path, PurePosixPath
import re
import signal
import stat
import tempfile
import time
import uuid
import zipfile

from . import hf_contextual, hf_continue, hf_convert, hf_dev_assisted, hf_preflight, hf_train, hf_train_recall

file_sha256, safe_extract, remaining = hf_convert.file_sha256, hf_convert.safe_extract, hf_convert.remaining
emit, fresh_output = hf_train.emit, hf_train_recall.fresh_output
export_evidence, run_logged = hf_continue.export_evidence, hf_contextual.run_logged
MIXED_PREFIX = 'mixed-supervision/ad548e0f8b7b454682dc2fd6c3298966'
MIXED_MANIFEST = '795d337284175325eaf18f5878bd89642d0c3ea0bf9720c34b678a9211a6de13'
HELPERS = ('runtime.py', 'bundle.py', 'contextual_run.py', 'contextual_train.py',
           'dev_assisted.py', 'dev_diagnostic.py', 'palref_eval.py')


def copy_adapter(mount, prefix, target, expected_manifest, expected_files, evidence, arm):
    """Read-through verify existing cloud weights before using a server-local copy."""
    import shutil
    manifest_path = mount / 'manifest.json'
    if file_sha256(manifest_path) != expected_manifest:
        raise ValueError('Adapter manifest differs: ' + arm)
    manifest = json.loads(manifest_path.read_text('utf-8'))
    target.mkdir(parents=True, exist_ok=False)
    for name, expected in expected_files.items():
        if Path(name).name != name:
            raise ValueError('Adapter filename must be a basename')
        key = prefix + '/' + name
        entry, source = manifest['files'][key], mount / key
        if entry['sha256'] != expected or source.stat().st_size != entry['bytes']:
            raise ValueError('Adapter inventory mismatch: ' + arm)
        shutil.copyfile(source, target / name)
        if file_sha256(target / name) != expected:
            raise ValueError('Adapter server copy checksum mismatch: ' + arm)
    shutil.copyfile(manifest_path, evidence / (arm + '-manifest.json'))


def evaluation_body(settings, stage, deadline, evidence):
    import os
    import shutil
    import subprocess
    import sys
    from datetime import datetime, timedelta, timezone

    folder, base = stage / 'bundle', stage / 'base'
    sys.path.insert(0, str(stage))
    import bundle
    import runtime
    bundle.verify(folder)
    for arm, mount, prefix in [('reference', Path('/original'), 'training/adapter'),
                               ('candidate', Path('/mixed'), 'mixed/training/adapter')]:
        remaining(deadline, 300)
        copy_adapter(mount, prefix, stage / arm, settings[arm + '_manifest_sha256'],
                     settings[arm + '_adapter_files'], evidence, arm)
        emit('adapter_verified', arm=arm)
    shutil.copyfile(folder / 'manifest.json', evidence / 'bundle-manifest.json')
    emit('gpu_admission', environment=runtime.gpu_admission())
    emit('base_download_started')
    subprocess.run([sys.executable, '-u', str(folder / 'fetch_base.py'), '--out', str(base), '--download'],
                   check=True, timeout=remaining(deadline, 300))
    shutil.copyfile(base / 'provenance.json', evidence / 'base-provenance.json')
    runtime.offline()
    emit('base_download_verified')
    os.environ['PYTHONPATH'] = os.pathsep.join((str(stage), str(folder)))
    cutoff = (datetime.now(timezone.utc) + timedelta(seconds=remaining(deadline, 180))).isoformat()
    command = [sys.executable, '-u', str(stage / 'learning_eval.py'), '--base', str(base),
               '--tokenizer', str(base), '--reference-adapter', str(stage / 'reference'),
               '--candidate-adapter', str(stage / 'candidate'), '--inputs', str(Path('/input') / settings['inputs_name']),
               '--settings', str(stage / 'settings.json'), '--output', str(evidence / 'evaluation'),
               '--deadline-utc', cutoff]
    emit('learning_evaluation_started', scheduled_outputs=56, training=False)
    run_logged(command, evidence / 'driver.log', remaining(deadline, 180))


def execute_evaluation(settings, scripts, bootstrap_prefix):
    import shutil
    deadline = time.monotonic() + settings['internal_seconds']
    def interrupted(signum, frame):
        raise TimeoutError('Inference computation interrupted or deadline reached')
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGALRM, interrupted)
    signal.alarm(settings['compute_seconds'])
    output = Path('/output')
    fresh_output(output)
    stage = Path(tempfile.mkdtemp(prefix='pahlavi-learning-eval-'))
    evidence = stage / 'evidence'
    evidence.mkdir()
    identity = dict(settings, operation='learning_diagnosis_inference_only', evaluation_status='incomplete',
                    training_launched=False, optimizer_updates=0, max_export_bytes=16 * 1024**2)
    failure = None
    try:
        if shutil.disk_usage('/tmp').free < 90 * 1024**3:
            raise ValueError('Insufficient ephemeral space for verified server-only base')
        if file_sha256(Path('/input') / settings['inputs_name']) != settings['inputs_sha256']:
            raise ValueError('Diagnostic prompt file differs')
        safe_extract(Path('/input') / settings['bundle_name'], stage / 'bundle', settings['bundle_sha256'], 128 * 1024**2)
        for name, expected in settings['bootstrap_hashes'].items():
            if file_sha256(stage / 'bundle' / name) != expected:
                raise ValueError('Bootstrap differs from qualified bundle')
        for name, entry in scripts.items():
            data = base64.b64decode(entry['content'])
            if hashlib.sha256(data).hexdigest() != entry['sha256'] or Path(name).name != name:
                raise ValueError('Runner source identity differs')
            (stage / name).write_bytes(data)
        evaluator_fields = ('schema_version', 'inputs_sha256', 'runner_sha256', 'helper_sha256',
                            'reference_adapter_files', 'candidate_adapter_files', 'generation')
        evaluator_settings = {key: settings[key] for key in evaluator_fields}
        (stage / 'settings.json').write_text(json.dumps(evaluator_settings), encoding='utf-8')
        emit('bootstrap_started')
        exec(bootstrap_prefix)
        emit('bootstrap_complete')
        evaluation_body(settings, stage, deadline, evidence)
        identity['evaluation_status'] = 'finished_see_per_attempt_status'
    except BaseException as error:
        failure = error
        identity.update(error_type=type(error).__name__, error=str(error))
        emit('learning_evaluation_incomplete', error_type=type(error).__name__, error=str(error))
    finally:
        signal.alarm(max(1, int(max(0, deadline - time.monotonic()))))
        (evidence / 'diagnostic-status.json').write_text(json.dumps(identity, indent=2) + '\n', encoding='utf-8')
        result = export_evidence(evidence, output, deadline, identity)
        emit('ready_to_persist', manifest_sha256=result['manifest_sha256'],
             exported_files=len(result['manifest']['files']), evaluation_status=identity['evaluation_status'])
        time.sleep(max(0, min(settings['maximum_wait_seconds'], deadline - time.monotonic())))
        emit('persistence_window_expired', remote_inventory_verified=False)
        signal.alarm(0)
    if failure is not None:
        raise failure


def prepare(inputs_path, run_id=None):
    from huggingface_hub import HfApi, Volume
    run_id = uuid.uuid4().hex if run_id is None else run_id
    if not re.fullmatch(r'[a-f0-9]{32}', run_id):
        raise ValueError('Fresh hexadecimal run identity required')
    inputs_path = Path(inputs_path)
    rows = [json.loads(line) for line in inputs_path.read_bytes().splitlines()]
    if len(rows) != 28 or any(set(r) != {'case_id', 'prompt'} for r in rows):
        raise ValueError('Only the28 case IDs and prompts may be packaged')
    if [r['case_id'] for r in rows] != [f'LD-{i:03d}' for i in range(1, 29)]:
        raise ValueError('Diagnostic case order differs')
    census = json.loads(inputs_path.with_name('census.json').read_bytes())
    inputs_sha = file_sha256(inputs_path)
    if census['output_sha256']['inputs.jsonl'] != inputs_sha:
        raise ValueError('Frozen local diagnostic input differs')
    spec, bootstrap_hashes = hf_preflight.specification('cuda')
    bootstrap, marker, _ = hf_preflight.BOOTSTRAP.partition('device = sys.argv[2]\n')
    if not marker:
        raise ValueError('Reviewed bootstrap boundary differs')
    root = Path(__file__).resolve().parent
    scripts = {name: {'sha256': file_sha256(root / name), 'content': base64.b64encode((root / name).read_bytes()).decode('ascii')}
               for name in (*HELPERS, 'learning_eval.py')}
    settings = dict(schema_version=1, run_id=run_id, inputs_name='learning-diagnosis-' + inputs_sha[:16] + '.jsonl',
                    inputs_sha256=inputs_sha, runner_sha256=scripts['learning_eval.py']['sha256'],
                    helper_sha256={k: scripts[k]['sha256'] for k in HELPERS},
                    reference_adapter_files=hf_dev_assisted.dev_assisted.ADAPTER_FILES,
                    candidate_adapter_files={'adapter_config.json': '9e7f2895e1ab5fe3707e7e533653df2b64003b1b7823194e72e79b63372b20f4',
                        'adapter_model.safetensors': 'f01d10058f26c1fc6fc212820b183e42d033fed0b959d200a87befa3d142cbca'},
                    reference_manifest_sha256=hf_dev_assisted.dev_assisted.ADAPTER_MANIFEST_SHA256,
                    candidate_manifest_sha256=MIXED_MANIFEST,
                    generation={'max_new_tokens': 512, 'max_generation_seconds': 90, 'seed': 42},
                    bundle_name=hf_dev_assisted.BUNDLE_NAME, bundle_sha256=hf_dev_assisted.BUNDLE_SHA256,
                    bootstrap_hashes=bootstrap_hashes, compute_seconds=3000, internal_seconds=3300,
                    native_timeout_minutes=60, export_reserve_seconds=180, maximum_wait_seconds=60)
    code = 'import base64,hashlib,json,re,signal,stat,tempfile,time,zipfile\nfrom pathlib import Path,PurePosixPath\n'
    for function in (file_sha256, safe_extract, remaining, emit, fresh_output, export_evidence,
                     run_logged, copy_adapter, evaluation_body, execute_evaluation):
        code += inspect.getsource(function) + '\n'
    code += 'settings=' + repr(settings) + '\nscripts=' + repr(scripts) + '\n'
    code += 'execute_evaluation(settings,scripts,' + repr(bootstrap) + ')\n'
    spec['command'][3] = hf_contextual.compressed_command(code)
    lengths, total = hf_contextual.command_lengths(spec['command'])
    spec['flavor'], spec['timeout'] = 'a100-large', '60m'
    spec['labels'].update(purpose='learning-diagnosis', trial_id=run_id)
    spec['env'].update(HF_XET_CACHE='/tmp/pahlavi-xet-cache', OMP_NUM_THREADS='8', MKL_NUM_THREADS='8')
    prefix = 'learning-diagnosis/' + run_id
    spec['volumes'] = [Volume(type='bucket', source=hf_train.BUCKET, path=path, mount_path=mount, read_only=readonly)
                       for path, mount, readonly in [('inputs', '/input', True),
                           (hf_dev_assisted.TRAINED_PREFIX, '/original', True), (MIXED_PREFIX, '/mixed', True),
                           (prefix, '/output', False)]]
    compile(code, 'hf-learning-eval', 'exec')
    inspect.signature(HfApi.run_job).bind(None, **spec)
    return spec, dict(settings, output_prefix=prefix, prepared_not_submitted=True,
                     decoded_command_sha256=hashlib.sha256(code.encode()).hexdigest(),
                     command_sha256=hashlib.sha256(spec['command'][3].encode()).hexdigest(),
                     command_arg_utf8_bytes=lengths, command_total_utf8_bytes_with_nul=total)
