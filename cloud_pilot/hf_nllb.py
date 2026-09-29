"""Prepare the single NLLB HF job and exact passive package; no auth, upload or launch."""
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

from . import hf_preflight, hf_contextual, hf_continue, hf_convert, hf_train, hf_train_recall, nllb_train

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / 'experiments/nllb-supervised-20260928'
LOCAL = ROOT / 'resources/local/nllb-supervised-20260928'
BUCKET = 'Mojionix/pahlavi-pilot'
file_sha256, safe_extract, remaining = hf_convert.file_sha256, hf_convert.safe_extract, hf_convert.remaining
emit, fresh_output, export_evidence = hf_train.emit, hf_train_recall.fresh_output, hf_continue.export_evidence
run_logged = hf_contextual.run_logged


def package():
    cache = ROOT / 'resources/local/nllb-tokenizer-20260928'
    previous = ROOT / 'experiments/nllb-feasibility-20260928'
    receipt = json.loads((previous / 'prepared-tokenizer-manifest.json').read_bytes())
    if file_sha256(previous / 'result.json') != receipt['result_sha256']:
        raise ValueError('Stale tokenizer/census manifest dependency')
    paths = {'train.jsonl': ROOT / 'resources/local/cloud-pilot-qualified-20260927/train.jsonl',
             'dev-inputs.jsonl': ROOT / 'experiments/dev-diagnostic-20260927/inputs.jsonl',
             'tokenizer-evidence.json': previous / 'result.json',
             'prepared-tokenizer-manifest.json': previous / 'prepared-tokenizer-manifest.json',
             'nllb_train.py': Path(nllb_train.__file__),
             'evaluation-contract.json': ROOT / 'experiments/dev-assisted-qualified-20260927/uniform-evaluation-contract.json'}
    for name in ('config.json', 'generation_config.json', 'special_tokens_map.json'):
        paths[name] = cache / name
    for name, record in receipt['files'].items():
        path = cache / 'adapted-language-token' / name
        if file_sha256(path) != record['sha256'] or path.stat().st_size != record['bytes']:
            raise ValueError('Prepared tokenizer differs')
        paths['tokenizer/' + name] = path
    assets = json.loads((previous / 'asset-receipt.json').read_bytes())
    for name in ('config.json', 'generation_config.json', 'special_tokens_map.json'):
        if file_sha256(paths[name]) != assets['files'][name]['sha256'] or paths[name].stat().st_size != assets['files'][name]['bytes']:
            raise ValueError('Original pinned model metadata differs')
    if file_sha256(paths['train.jsonl']) != nllb_train.TRAIN_SHA or file_sha256(paths['dev-inputs.jsonl']) != nllb_train.DEV_SHA:
        raise ValueError('Input data changed')
    files = {name: {'bytes': path.stat().st_size, 'sha256': file_sha256(path)} for name, path in paths.items()}
    manifest = dict(model=nllb_train.MODEL, revision=nllb_train.REVISION, files=files,
        settings=nllb_train.SETTINGS, tokenizer_receipt=receipt, original_asset_receipt=assets,
        training_rows=2237, dev_rows=24, scheduled_outputs=48, includes_dev_targets=False)
    payload = (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode()
    LOCAL.mkdir(exist_ok=True, parents=True)
    target = LOCAL / 'package.zip'
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(paths):
            info = zipfile.ZipInfo(name, date_time=(2026, 9, 28, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, paths[name].read_bytes())
        info = zipfile.ZipInfo('manifest.json', date_time=(2026, 9, 28, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(info, payload)
    (LOCAL / 'package-manifest.json').write_bytes(payload)
    return target, manifest, hashlib.sha256(payload).hexdigest()


def verify_package(folder, settings):
    if file_sha256(folder / 'manifest.json') != settings['package_manifest_sha256']:
        raise ValueError('Package manifest differs')
    manifest = json.loads((folder / 'manifest.json').read_bytes())
    if {p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()} != set(manifest['files']) | {'manifest.json'}:
        raise ValueError('Package inventory differs')
    for name, entry in manifest['files'].items():
        path = folder / name
        if path.is_symlink() or path.stat().st_size != entry['bytes'] or file_sha256(path) != entry['sha256']:
            raise ValueError('Package member differs: ' + name)
    return manifest


def verify_canary(folder, settings):
    if file_sha256(folder/'manifest.json')!=settings['canary_manifest_sha256']:
        raise ValueError('Committed canary manifest differs')
    manifest=json.loads((folder/'manifest.json').read_bytes())
    if manifest.get('nllb_status')!='canary_complete' or manifest.get('completed_steps')!=20:
        raise ValueError('Passing closed canary required')
    for key in ('package_sha256','package_manifest_sha256','settings','train_sha256','dev_sha256','model','revision'):
        if manifest[key]!=settings[key]: raise ValueError('Canary experiment identity differs')
    for name,entry in manifest['files'].items():
        if (PurePosixPath(name).is_absolute() or '..' in PurePosixPath(name).parts or '\\' in name or ':' in name
                or (folder/name).is_symlink() or (folder/name).stat().st_size!=entry['bytes']
                or file_sha256(folder/name)!=entry['sha256']):
            raise ValueError('Cloud checkpoint read-through integrity failed: '+name)
    return manifest


def retain_verified_checkpoint(stage,evidence):
    """Publish only a fully reload-verified directory; incomplete saves remain outside export."""
    target=evidence/'nllb/model'
    if target.exists(): return
    for name,step in (('final-state',700),('canary-state',20)):
        folder=stage/name
        marker=folder/'checkpoint-verified.json'
        if not marker.is_file(): continue
        record=json.loads(marker.read_bytes())
        if record['step']!=step or record['reload_and_generation_verified'] is not True:
            raise ValueError('Checkpoint completion marker differs')
        if {p.name for p in folder.iterdir()}!=set(record['files'])|{'checkpoint-verified.json'}:
            raise ValueError('Verified checkpoint inventory differs')
        for file,entry in record['files'].items():
            if Path(file).name!=file or (folder/file).stat().st_size!=entry['bytes'] or file_sha256(folder/file)!=entry['sha256']:
                raise ValueError('Verified checkpoint bytes differ')
        target.parent.mkdir(parents=True,exist_ok=True)
        folder.rename(target)
        return step


def execute_nllb(settings, bootstrap):
    import shutil
    import subprocess
    import sys
    start = time.monotonic()
    deadline = start + settings['internal_seconds']
    computation = start + settings['compute_seconds']
    def interrupted(signum, frame):
        raise TimeoutError('NLLB job deadline/interruption')
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGALRM, interrupted)
    signal.alarm(settings['compute_seconds'])
    output = Path('/output')
    fresh_output(output)
    stage = Path(tempfile.mkdtemp(prefix='pahlavi-nllb-'))
    evidence = stage / 'evidence'
    evidence.mkdir()
    identity = dict(settings, operation='nllb_supervised', nllb_status='incomplete',
        quality_validated=False, local_model_verified=False, max_export_bytes=24*1024**3)
    failure = None
    try:
        if shutil.disk_usage('/tmp').free < 70*1024**3:
            raise ValueError('NLLB needs 70 GiB available scratch')
        safe_extract(Path('/input') / settings['package_name'], stage / 'package', settings['package_sha256'], 128*1024**2)
        verify_package(stage / 'package', settings)
        shutil.copyfile(stage / 'package/manifest.json', evidence / 'package-manifest.json')
        emit('bootstrap_started')
        exec(bootstrap)
        # exec defines runtime via the already exercised bootstrap; import it from its prepared path.
        import runtime
        emit('gpu_admission', environment=runtime.gpu_admission())
        if settings['phase']=='continue':
            emit('canary_readthrough_started')
            verify_canary(Path('/canary'),settings)
            emit('canary_readthrough_verified')
        emit('nllb_started', run_phase=settings['phase'], initialized_outputs=24, trained_outputs=24, updates=700)
        command = [sys.executable, '-u', str(stage / 'package/nllb_train.py'), '--package', str(stage / 'package'),
            '--output', str(evidence / 'nllb'), '--deadline', str(computation), '--program-start', str(start)]
        if settings['phase']=='continue': command.extend(['--resume','/canary'])
        run_logged(command, evidence / 'driver.log', remaining(computation))
        run = json.loads((evidence / 'nllb/run.json').read_bytes())
        rows = [json.loads(s) for s in (evidence / 'nllb/predictions.jsonl').read_text('utf-8').splitlines()]
        inputs = [json.loads(s) for s in (stage / 'package/dev-inputs.jsonl').read_text('utf-8').splitlines()]
        arms=('initialized',) if settings['phase']=='canary' else ('initialized','trained')
        status,steps=('canary_complete',20) if settings['phase']=='canary' else ('completed',700)
        expected = [r['id'] + ':' + arm for arm in arms for r in inputs]
        if run['status'] != status or run['step'] != steps or [r['id'] for r in rows] != expected:
            raise ValueError('Scientific schedule incomplete')
        identity.update(nllb_status='canary_complete' if steps==20 else 'complete',completed_steps=steps)
    except BaseException as error:
        failure = error
        identity.update(error_type=type(error).__name__, error=str(error))
        emit('nllb_incomplete', error_type=type(error).__name__, error=str(error))
    finally:
        signal.alarm(max(1, int(max(0, deadline-time.monotonic()))))
        try:
            retained=retain_verified_checkpoint(stage,evidence)
            if retained: identity['recovered_checkpoint_step']=retained
        except Exception as recovery_error:
            identity['checkpoint_recovery_error']=type(recovery_error).__name__+': '+str(recovery_error)
        (evidence / 'status.json').write_text(json.dumps(identity, indent=2)+'\n', encoding='utf-8')
        export_start=time.monotonic()
        emit('export_started')
        result = export_evidence(evidence, output, deadline, identity)
        from datetime import datetime, timezone
        emit('ready_to_persist',export_seconds=time.monotonic()-export_start,
             ready_utc=datetime.now(timezone.utc).isoformat(),**result)
        time.sleep(max(0, min(420, deadline-time.monotonic())))
        signal.alarm(0)
    if failure is not None:
        raise failure


def specification(run_id=None,phase='canary',canary=None):
    run_id = uuid.uuid4().hex if run_id is None else run_id
    if not re.fullmatch('[a-f0-9]{32}', run_id):
        raise ValueError('Invalid unique trial ID')
    if phase not in {'canary','continue'} or (phase=='continue' and not canary):
        raise ValueError('Explicit phase and verified canary identity required')
    native_minutes=20
    if phase=='continue':
        native_minutes=canary['native_minutes']
        if (type(native_minutes) is not int or not 9<=native_minutes<=50
                or type(canary['closed_minutes']) is not int or canary['closed_minutes']+native_minutes!=59):
            raise ValueError('Closed canary plus continuation exceed frozen compute allocation')
    package_path, manifest, manifest_sha = package()
    spec, bootstrap_hashes = hf_preflight.specification('cuda')
    prefix, marker, _ = hf_preflight.BOOTSTRAP.partition('device = sys.argv[2]\n')
    if not marker:
        raise ValueError('Bootstrap boundary changed')
    settings = dict(run_id=run_id, package_name='nllb-' + file_sha256(package_path)[:16] + '.zip',
        package_sha256=file_sha256(package_path), package_manifest_sha256=manifest_sha,
        bootstrap_hashes=bootstrap_hashes, settings=nllb_train.SETTINGS,
        train_sha256=nllb_train.TRAIN_SHA, dev_sha256=nllb_train.DEV_SHA,
        model=nllb_train.MODEL, revision=nllb_train.REVISION,
        phase=phase,compute_seconds=720 if phase=='canary' else (native_minutes-8)*60,
        internal_seconds=(native_minutes-2)*60,native_timeout_minutes=native_minutes,
        output_prefix='nllb-supervised/' + run_id)
    if phase=='continue':
        settings.update(canary_prefix=canary['output_prefix'],canary_manifest_sha256=canary['manifest_sha256'],
            canary_closed_minutes=canary['closed_minutes'],canary_termination_sha256=canary['termination_sha256'])
    code = 'import base64,hashlib,json,os,re,signal,stat,sys,tempfile,time,zipfile\nfrom pathlib import Path,PurePosixPath\n'
    for function in (file_sha256, safe_extract, remaining, emit, fresh_output, export_evidence,
                     run_logged, verify_package,verify_canary,retain_verified_checkpoint,execute_nllb):
        code += inspect.getsource(function) + '\n'
    code += 'execute_nllb(' + repr(settings) + ', ' + repr(prefix) + ')\n'
    spec['command'][3] = hf_contextual.compressed_command(code)
    hf_contextual.command_lengths(spec['command'])
    compile(code, 'hf-nllb', 'exec')
    spec['timeout'] = str(settings['native_timeout_minutes'])+'m'
    spec['labels'].update(purpose='nllb-supervised',trial_id=run_id,phase=phase)
    spec['env'].update(OMP_NUM_THREADS='8', MKL_NUM_THREADS='8', HF_XET_CACHE='/tmp/pahlavi-xet-cache', HF_HUB_DISABLE_IMPLICIT_TOKEN='1')
    from huggingface_hub import Volume
    spec['volumes'] = [Volume(type='bucket', source=BUCKET, path='inputs', mount_path='/input', read_only=True),
        Volume(type='bucket', source=BUCKET, path=settings['output_prefix'], mount_path='/output', read_only=False)]
    if phase=='continue':
        spec['volumes'].append(Volume(type='bucket',source=BUCKET,path=settings['canary_prefix'],mount_path='/canary',read_only=True))
    settings.update(command_sha256=hashlib.sha256(spec['command'][3].encode()).hexdigest())
    return spec, settings
