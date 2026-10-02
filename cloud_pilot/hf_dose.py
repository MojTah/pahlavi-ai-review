"""Prepare one gated, bounded acquisition trajectory. No authentication or launch."""
import base64
import hashlib
import inspect
import json
import lzma
from pathlib import Path, PurePosixPath
import re
import signal
import stat
import tempfile
import time
import uuid
import zipfile

from . import (dose_train, hf_contextual, hf_continue, hf_convert, hf_dev_assisted,
               hf_preflight, hf_train, hf_train_recall, mixed_run, training_admission)

file_sha256, safe_extract, remaining = hf_convert.file_sha256, hf_convert.safe_extract, hf_convert.remaining
emit, fresh_output, export_evidence = hf_train.emit, hf_train_recall.fresh_output, hf_continue.export_evidence
run_logged = hf_contextual.run_logged


def completed_training(output, settings):
    """Independent evidence check, including the actual forwarded stream and saves."""
    training = json.loads((output / 'training/run.json').read_text('utf-8'))
    manifest = json.loads((output.parent / 'data-manifest.json').read_text('utf-8'))
    ordered = manifest['pilot']['selected_ids_in_order']
    if (file_sha256(output.parent / 'data-manifest.json') != settings['data_manifest_sha256']
            or training.get('status') != 'completed' or training['completed_steps'] != 384
            or training['consumed_slots'] != 6144 or training['ordered_ids'] != ordered * 4
            or training['settings'] != settings['training_settings']
            or training['runner_sha256'] != settings['script_hashes']['dose_train.py']
            or training['fresh_optimizer'] is not True or training['canary_adapter_changed'] is not True
            or training['forwarded_stream_sha256'] != training['stream_sha256']
            or training['initial_adapter_sha256'] == training['final_adapter_sha256']
            or len(training['pass_exposures']) != 4
            or set(training['snapshots']) != {'96', '192', '384'}
            or [r['step'] for r in training['admission_observations']] != [20, 96, 192]
            or any(r['admitted'] is not True for r in training['admission_observations'])):
        raise ValueError('Dose training completion evidence differs')
    for index, record in enumerate(training['pass_exposures'], 1):
        if (record['pass_index'] != index or record['slots'] != 1536 or record['ids'] != ordered
                or record['stream_sha256'] != training['base_cycle_sha256']):
            raise ValueError('Actual dose exposure differs')
    for step, record in training['snapshots'].items():
        if (record['consumed_slots'] != int(step) * 16 or record['optimizer_steps'] != [int(step)]
                or record['scheduler_step'] != int(step)):
            raise ValueError('Dose snapshot step differs')
        folder, files = output / 'training' / ('adapter-step' + step), record['files']
        if (not {'adapter_config.json', 'adapter_model.safetensors'} <= set(files)
                or any(Path(n).name != n for n in files)
                or {p.name for p in folder.iterdir()} != set(files)):
            raise ValueError('Dose adapter inventory differs')
        for name, expected in files.items():
            path = folder / name
            if path.is_symlink() or not path.is_file() or not path.stat().st_size or file_sha256(path) != expected:
                raise ValueError('Dose snapshot checksum differs')
    return training


def dose_body(settings, stage, deadline, evidence):
    import os
    import shutil
    import subprocess
    import sys
    from datetime import datetime, timedelta, timezone

    folder, base, trained = stage / 'bundle', stage / 'base', Path('/trained')
    sys.path[:0] = [str(stage), str(folder)]
    import bundle
    import runtime
    import contextual_run
    bundle.verify(folder)
    for name, expected in contextual_run.HELPER_SHA256.items():
        if file_sha256(folder / name if name in {'bundle.py', 'runtime.py'} else stage / name) != expected:
            raise ValueError('Frozen helper differs: ' + name)
    if file_sha256(trained / 'manifest.json') != settings['trained_manifest_sha256']:
        raise ValueError('Qualified step280 manifest differs')
    manifest = json.loads((trained / 'manifest.json').read_text('utf-8'))
    if (manifest.get('full_training_completed') is not True or manifest.get('training_schedule_completed') is not True
            or manifest.get('completed_global_step') != 280):
        raise ValueError('Qualified completed step280 required')
    for name, expected in settings['adapter_files'].items():
        source, target, entry = trained / name, stage / name, manifest['files'][name]
        remaining(deadline, settings['export_reserve_seconds'])
        if source.stat().st_size != entry['bytes'] or entry['sha256'] != expected or file_sha256(source) != expected:
            raise ValueError('Qualified mounted artifact differs: ' + name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if file_sha256(target) != expected:
            raise ValueError('Qualified server copy differs: ' + name)
    for source, name in ((trained / 'manifest.json', 'trained-manifest.json'),
                         (folder / 'manifest.json', 'bundle-manifest.json'),
                         (Path('/input') / settings['data_manifest_name'], 'data-manifest.json')):
        shutil.copyfile(source, evidence / name)
    emit('gpu_admission', environment=runtime.gpu_admission())
    emit('base_download_started', destination='cloud_ephemeral_disk_only')
    subprocess.run([sys.executable, '-u', str(folder / 'fetch_base.py'), '--out', str(base), '--download'],
                   check=True, timeout=remaining(deadline, settings['export_reserve_seconds']))
    shutil.copyfile(base / 'provenance.json', evidence / 'base-provenance.json')
    runtime.offline()
    os.environ['PYTHONPATH'] = os.pathsep.join((str(stage), str(folder)))
    cutoff = (datetime.now(timezone.utc) + timedelta(seconds=remaining(deadline, settings['export_reserve_seconds']))).isoformat()
    command = [sys.executable, '-u', str(stage / 'dose_run.py'), '--bundle', str(folder), '--base', str(base),
        '--tokenizer', str(base), '--adapter', str(stage / 'training/adapter'),
        '--train', str(Path('/input') / settings['train_name']),
        '--data-manifest', str(Path('/input') / settings['data_manifest_name']),
        '--settings', str(stage / 'settings.json'), '--inputs', str(Path('/input') / settings['inputs_name']),
        '--output', str(evidence / 'dose'), '--deadline-utc', cutoff]
    emit('dose_started', planned_updates=384, scheduled_outputs=settings['expected_outputs'])
    run_logged(command, evidence / 'driver.log', remaining(deadline, settings['export_reserve_seconds']))
    completed_training(evidence / 'dose', settings)
    run = json.loads((evidence / 'dose/run.json').read_text('utf-8'))
    if (run.get('status') != 'completed' or run.get('recorded_outputs') != settings['expected_outputs']
            or run.get('successful_outputs') != settings['expected_outputs']
            or run.get('final_adapters_unchanged') is not True):
        raise ValueError('Dose child did not complete evaluation')


def execute_dose(settings, scripts, bootstrap_prefix):
    import shutil

    deadline = time.monotonic() + settings['internal_seconds']
    def interrupted(signum, frame):
        raise TimeoutError('Dose job computation deadline or termination')
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGALRM, interrupted)
    signal.alarm(settings['compute_seconds'])
    output = Path('/output')
    fresh_output(output)
    stage = Path(tempfile.mkdtemp(prefix='pahlavi-dose-'))
    evidence = stage / 'evidence'
    evidence.mkdir()
    identity = dict(settings, operation='dose_acquisition', status='incomplete',
                    training_schedule_completed=False, evaluation_complete=False,
                    quality_validated=False, resumable_optimizer_checkpoint=False)
    failure = None
    try:
        if shutil.disk_usage('/tmp').free < 90 * 1024**3:
            raise ValueError('Dose requires90GiB ephemeral disk')
        for name, expected in ((settings['inputs_name'], settings['inputs_sha256']),
                               (settings['train_name'], settings['train_sha256']),
                               (settings['data_manifest_name'], settings['data_manifest_sha256'])):
            if file_sha256(Path('/input') / name) != expected:
                raise ValueError('Frozen dose input differs: ' + name)
        safe_extract(Path('/input') / settings['bundle_name'], stage / 'bundle', settings['bundle_sha256'], 128 * 1024**2)
        for name, expected in settings['bootstrap_hashes'].items():
            if file_sha256(stage / 'bundle' / name) != expected:
                raise ValueError('Frozen bootstrap differs: ' + name)
        for name, entry in scripts.items():
            data = base64.b64decode(entry['content'])
            if hashlib.sha256(data).hexdigest() != entry['sha256']:
                raise ValueError('Dose source checksum differs')
            (stage / name).write_bytes(data)
        (stage / 'settings.json').write_text(json.dumps(settings), encoding='utf-8')
        emit('bootstrap_started')
        exec(bootstrap_prefix)
        emit('bootstrap_complete')
        dose_body(settings, stage, deadline, evidence)
        identity.update(status='completed', training_schedule_completed=True, evaluation_complete=True)
    except BaseException as error:
        failure = error
        identity.update(error_type=type(error).__name__, error=str(error))
        for phase in ('evaluation-baseline', 'evaluation'):
            path = evidence / 'dose' / phase
            if (path / 'run.json').is_file():
                try:
                    from dose_run import reconcile_evaluation
                    reconcile_evaluation(path)
                except Exception as ledger_error:
                    identity.setdefault('ledger_reconciliation_errors', {})[phase] = str(ledger_error)
                    emit('ledger_reconciliation_failed', phase=phase, error=str(ledger_error))
        try:
            completed_training(evidence / 'dose', settings)
        except Exception as validation_error:
            emit('training_completion_unverified', error_type=type(validation_error).__name__)
        else:
            identity['training_schedule_completed'] = True
        emit('dose_incomplete', **{k: identity[k] for k in ('error_type', 'error', 'training_schedule_completed')})
    finally:
        signal.alarm(max(1, int(max(0, deadline - time.monotonic()))))
        (evidence / 'dose-status.json').write_text(json.dumps(identity, indent=2) + '\n', encoding='utf-8')
        result = export_evidence(evidence, output, deadline, identity)
        emit('ready_to_persist', **result)
        time.sleep(max(0, min(settings['maximum_wait_seconds'], deadline - time.monotonic())))
        emit('persistence_window_expired', remote_inventory_verified=False)
        signal.alarm(0)
    if failure is not None:
        raise failure


@training_admission.draft
def prepare(train_path, manifest_path, inputs_path, packet_contract, run_id=None):
    run_id = run_id or uuid.uuid4().hex
    if not isinstance(run_id, str) or not re.fullmatch('[a-f0-9]{32}', run_id):
        raise ValueError('Fresh hexadecimal run ID required')
    spec, hashes = hf_preflight.specification('cuda')
    prefix, marker, _ = hf_preflight.BOOTSTRAP.partition('device = sys.argv[2]\n')
    if not marker:
        raise ValueError('Reviewed bootstrap boundary changed')
    root = Path(__file__).resolve().parent
    train_sha, manifest_sha, inputs_sha = map(file_sha256, (train_path, manifest_path, inputs_path))
    settings = dict(train_sha256=train_sha, data_manifest_sha256=manifest_sha)
    _, manifest = mixed_run.read_data(train_path, manifest_path, settings)
    if manifest.get('version') != 'corrected-v2' or manifest['unresolved_prompt_collisions'] != 0:
        raise ValueError('Qualified corrected-v2 source required')
    if packet_contract['inputs_sha256'] != inputs_sha or packet_contract['expected_outputs'] != 98:
        raise ValueError('Frozen98-output packet required')
    scripts = {}
    names = ('dose_run.py', 'dose_train.py', 'mixed_run.py', 'mixed_train.py', 'contextual_run.py',
             'contextual_train.py', 'dev_assisted.py', 'dev_diagnostic.py', 'palref_eval.py',
             'learning_eval.py', 'nf4_learning_eval.py')
    for name in names:
        raw = (root / name).read_bytes()
        scripts[name] = dict(sha256=hashlib.sha256(raw).hexdigest(), content=base64.b64encode(raw).decode())
    # The frozen NF4 module's standalone import uses this exact helper alias.
    scripts['bf16_learning_eval.py'] = scripts['learning_eval.py']
    qualified = hf_dev_assisted.dev_assisted
    adapter_files = {'training/adapter/' + n: v for n, v in qualified.ADAPTER_FILES.items()}
    adapter_files.update({'training/' + n: v for n, v in qualified.ADAPTER_METADATA.items()})
    settings.update(packet_contract, experiment_id='dose-acquisition-20260930', run_id=run_id,
        inputs_name='dose-inputs-' + inputs_sha[:12] + '.jsonl',
        train_name='mixed-train-' + train_sha[:12] + '.jsonl',
        data_manifest_name='mixed-data-manifest-' + manifest_sha[:12] + '.json',
        training_settings=dose_train.SETTINGS, bundle_name=hf_dev_assisted.BUNDLE_NAME,
        bundle_sha256=hf_dev_assisted.BUNDLE_SHA256, trained_prefix=hf_dev_assisted.TRAINED_PREFIX,
        trained_manifest_sha256=qualified.ADAPTER_MANIFEST_SHA256,
        reference_adapter_files=qualified.ADAPTER_FILES, adapter_files=adapter_files,
        bootstrap_hashes=hashes, script_hashes={n: e['sha256'] for n, e in scripts.items()},
        baseline_allocation_seconds=2400, remaining_evaluation_seconds=6600, reload_seconds=300,
        native_timeout_minutes=360, compute_seconds=20400, internal_seconds=21000,
        export_reserve_seconds=600, maximum_wait_seconds=300, max_export_bytes=3 * 1024**3)
    from . import dose_run
    dose_run.read_packet(inputs_path, settings)
    # In-memory construction and saved-JSON reconstruction must emit identical code.
    settings = json.loads(json.dumps(settings, sort_keys=True, ensure_ascii=False))
    scripts = json.loads(json.dumps(scripts, sort_keys=True, ensure_ascii=False))
    code = 'import base64,hashlib,json,os,re,signal,stat,sys,tempfile,time,zipfile\nfrom pathlib import Path,PurePosixPath\n'
    for function in (file_sha256, safe_extract, remaining, emit, fresh_output, export_evidence,
                     completed_training, run_logged, dose_body, execute_dose):
        code += inspect.getsource(function) + '\n'
    code += 'settings=' + repr(settings) + '\nscripts=' + repr(scripts) + '\n'
    code += 'execute_dose(settings,scripts,' + repr(prefix) + ')\n'
    packed = base64.b64encode(lzma.compress(code.encode())).decode()
    spec['command'][3] = ('import base64,lzma,hashlib\n_code=lzma.decompress(base64.b64decode(' + repr(packed) + '))\n'
        'if hashlib.sha256(_code).hexdigest() != ' + repr(hashlib.sha256(code.encode()).hexdigest()) + ':\n'
        "    raise ValueError('Dose transport checksum mismatch')\nexec(compile(_code,'hf-dose','exec'))\n")
    spec['flavor'], spec['timeout'] = 'a100-large', '360m'
    spec['labels'].update(purpose='dose-acquisition', trial_id=run_id)
    spec['env'].update(HF_XET_CACHE='/tmp/pahlavi-xet-cache', OMP_NUM_THREADS='8', MKL_NUM_THREADS='8')
    from huggingface_hub import Volume
    output_prefix = 'dose-acquisition/' + run_id
    spec['volumes'] = [Volume(type='bucket', source=hf_train.BUCKET, path='inputs', mount_path='/input', read_only=True),
        Volume(type='bucket', source=hf_train.BUCKET, path=settings['trained_prefix'], mount_path='/trained', read_only=True),
        Volume(type='bucket', source=hf_train.BUCKET, path=output_prefix, mount_path='/output', read_only=False)]
    lengths, total = hf_contextual.command_lengths(spec['command'])
    if max(lengths) + 16384 >= 100 * 1024 or total >= 1024**2:
        raise ValueError('Dose transport leaves insufficient admission-guard space')
    compile(code, 'hf-dose', 'exec')
    training_admission.sdk_spec(spec)
    return spec, dict(settings, output_prefix=output_prefix, prepared_not_submitted=True,
        decoded_command_sha256=hashlib.sha256(code.encode()).hexdigest(),
        command_sha256=hashlib.sha256(spec['command'][3].encode()).hexdigest(),
        command_arg_utf8_bytes=lengths, command_total_utf8_bytes_with_nul=total)
