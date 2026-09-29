"""Build one inference-only TRAIN diagnostic; no authentication or paid submission."""
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

from . import hf_contextual, hf_nllb, hf_preflight, nllb_train

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / 'experiments/nllb-seen-20260928/precision-repair'
LOCAL = ROOT / 'resources/local/nllb-seen-20260928/precision-repair'
BUCKET = hf_nllb.BUCKET
MODEL_PREFIX = 'nllb-supervised/99231a67ac364af992565d15cb53a325'
MODEL_MANIFEST_SHA = 'c2ed23f93d72f5958f8a46d1c37b1d187c6eff2a0f9d354c565de3f505ad2349'
TOKEN_MAP_SHA = '5dac1a0c537ce8d7c410110b33bf30aaf3f95c2577f507d86eb228881953b255'
INFERENCE_NAMES = ('config.json', 'generation_config.json', 'model-00001-of-00002.safetensors',
    'model-00002-of-00002.safetensors', 'model.safetensors.index.json', 'tokenizer.json',
    'tokenizer_config.json', 'training-state.json')
file_sha256, safe_extract, remaining = hf_nllb.file_sha256, hf_nllb.safe_extract, hf_nllb.remaining
emit, fresh_output, export_evidence = hf_nllb.emit, hf_nllb.fresh_output, hf_nllb.export_evidence
run_logged, verify_package = hf_nllb.run_logged, hf_nllb.verify_package


def package():
    from . import nllb_seen
    paths = {
        'train.jsonl': ROOT / 'resources/local/cloud-pilot-qualified-20260927/train.jsonl',
        'inputs.jsonl': ROOT / 'experiments/train-recall-20260927/inputs.jsonl',
        'source-control.json': ROOT / 'experiments/train-fit-20260927/source-control.json',
        'model-manifest.json': ROOT / 'experiments/nllb-supervised-20260928/continue/recovered/manifest.json',
        'nllb_train.py': Path(nllb_train.__file__), 'nllb_seen.py': Path(nllb_seen.__file__)}
    if file_sha256(paths['model-manifest.json']) != MODEL_MANIFEST_SHA:
        raise ValueError('Completed model manifest changed')
    LOCAL.mkdir(parents=True, exist_ok=True)
    import shutil
    folder = LOCAL / 'package-staging'
    folder.mkdir(exist_ok=True)
    for name, source in paths.items():
        shutil.copyfile(source, folder / name)
    cached=LOCAL/'token-map.json'
    if cached.is_file() and file_sha256(cached)==TOKEN_MAP_SHA:
        token_bytes=cached.read_bytes()
    else:
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            ROOT / 'resources/local/nllb-tokenizer-20260928/adapted-language-token',
            local_files_only=True, token=False, trust_remote_code=False,
            src_lang='pal_Latn', tgt_lang='pes_Arab')
        token_map = nllb_seen.build_token_map(folder, tokenizer)
        token_bytes=(json.dumps(token_map, ensure_ascii=False, sort_keys=True, indent=2)+'\n').encode('utf-8')
    if (hashlib.sha256(token_bytes).hexdigest()!=TOKEN_MAP_SHA
            or json.loads(token_bytes)['source_files_sha256']!={n:file_sha256(paths[n]) for n in
                ('train.jsonl','inputs.jsonl','source-control.json','model-manifest.json')}):
        raise ValueError('Previously constructed and independently verified token map differs')
    token_path = folder / 'token-map.json'
    token_path.write_bytes(token_bytes)
    paths['token-map.json'] = token_path
    files = {name: {'bytes': path.stat().st_size, 'sha256': file_sha256(path)} for name,path in paths.items()}
    manifest = dict(files=files, operation='nllb_seen', training_performed=False,
        model_manifest_sha256=MODEL_MANIFEST_SHA, scored_forwards=40, generations=20,
        unscored_readiness_forwards=2, includes_dev_targets=False)
    payload = (json.dumps(manifest, sort_keys=True, indent=2)+'\n').encode()
    with zipfile.ZipFile(LOCAL/'package.zip', 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(paths):
            info = zipfile.ZipInfo(name, date_time=(2026,9,28,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, paths[name].read_bytes())
        info = zipfile.ZipInfo('manifest.json', date_time=(2026,9,28,0,0,0))
        info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(info,payload)
    (LOCAL/'token-map.json').write_bytes(token_path.read_bytes())
    (LOCAL/'package-manifest.json').write_bytes(payload)
    return LOCAL/'package.zip', manifest, hashlib.sha256(payload).hexdigest()


def copy_inference(source, target, settings, deadline):
    import shutil
    if file_sha256(source/'manifest.json') != settings['model_manifest_sha256']:
        raise ValueError('Cloud model manifest differs')
    manifest = json.loads((source/'manifest.json').read_bytes())
    if (manifest['run_id'] != settings['model_run_id'] or manifest['completed_steps'] != 700
            or manifest['nllb_status'] != 'complete' or manifest['model'] != settings['model']
            or manifest['revision'] != settings['revision']):
        raise ValueError('Completed trained checkpoint required')
    target.mkdir(exist_ok=False)
    for name in settings['inference_names']:
        remaining(deadline, 120)
        if Path(name).name != name:
            raise ValueError('Unsafe model filename')
        origin, destination = source/'nllb/model'/name, target/name
        entry = manifest['files']['nllb/model/'+name]
        if origin.is_symlink() or origin.stat().st_size != entry['bytes']:
            raise ValueError('Model file size/type differs')
        shutil.copyfile(origin, destination)
        if file_sha256(destination) != entry['sha256']:
            raise ValueError('Model inference bytes differ: '+name)
        emit('model_file_verified', name=name, bytes=entry['bytes'])
    return sum(manifest['files']['nllb/model/'+n]['bytes'] for n in settings['inference_names'])


def completed_seen(output, package, settings):
    run=json.loads((output/'run.json').read_bytes())
    token_map=json.loads((package/'token-map.json').read_bytes())
    rows=token_map['rows']
    by_id={r['id']:r for r in rows}
    calls=[]
    for i,row in enumerate(rows):
        for condition in (('correct','mismatched') if i%2==0 else ('mismatched','correct')):
            source=row if condition=='correct' else by_id[row['mismatched_source_parent_id']]
            calls.append((row['id']+':'+condition,row,source,'likelihood'))
    calls.extend((r['id']+':trained',r,r,'generation') for r in rows)
    expected=[c[0] for c in calls]
    if (len(rows)!=20 or len(set(expected))!=60 or run['status']!='completed'
            or run.get('training_performed') is not False or run.get('optimizer_updates')!=0
            or run.get('all_first_attempts_recorded') is not True
            or run.get('completed_call_ids')!=expected or run.get('unattempted_call_ids')!=[]
            or run.get('model_manifest_sha256')!=settings['model_manifest_sha256']
            or run.get('token_map_sha256')!=settings['token_map_sha256']
            or run.get('runner_sha256')!=file_sha256(package/'nllb_seen.py')):
        raise ValueError('Completed diagnostic identity or schedule differs')
    records=[]
    for name,count in (('likelihood.jsonl',40),('predictions.jsonl',20)):
        part=[json.loads(s) for s in (output/name).read_text('utf-8').splitlines()]
        if len(part)!=count:
            raise ValueError('Diagnostic record coverage differs')
        records.extend(part)
    for sequence,((call_id,target,source,kind),record) in enumerate(zip(calls,records),1):
        if (record.get('id')!=call_id or record.get('sequence')!=sequence or record.get('kind')!=kind
                or record.get('record_id')!=target['record_id'] or record.get('work_id')!=target['work_id']
                or record.get('input_sha256')!=source['source_sha256']
                or record.get('target_sha256')!=target['target_sha256']
                or record.get('status') not in ({'success'} if kind=='likelihood' else {'success','failed'})):
            raise ValueError('Diagnostic first-attempt record differs')
    return run


def execute_seen(settings, bootstrap):
    import shutil
    import sys
    start = time.monotonic()
    compute, deadline = start+settings['compute_seconds'], start+settings['internal_seconds']
    def interrupted(signum, frame):
        raise TimeoutError('NLLB diagnostic deadline/interruption')
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGALRM, interrupted)
    signal.alarm(settings['compute_seconds'])
    output = Path('/output')
    fresh_output(output)
    stage = Path(tempfile.mkdtemp(prefix='pahlavi-nllb-seen-'))
    evidence = stage/'evidence'
    evidence.mkdir()
    identity = dict(settings, operation='nllb_seen', diagnostic_status='incomplete',
        training_performed=False, quality_validated=False, max_export_bytes=16*1024**2)
    failure = None
    try:
        if shutil.disk_usage('/tmp').free < 12*1024**3:
            raise ValueError('12 GiB inference scratch required')
        folder = stage/'package'
        safe_extract(Path('/input')/settings['package_name'], folder, settings['package_sha256'],128*1024**2)
        verify_package(folder, settings)
        shutil.copyfile(folder/'manifest.json',evidence/'package-manifest.json')
        emit('bootstrap_started')
        exec(bootstrap)
        import runtime
        emit('gpu_admission', environment=runtime.gpu_admission())
        size = copy_inference(Path('/trained'),stage/'model',settings,compute)
        identity['verified_inference_bytes'] = size
        emit('model_readthrough_verified',bytes=size,remaining_seconds=remaining(compute))
        command=[sys.executable,'-u',str(folder/'nllb_seen.py'),'--package',str(folder),
            '--model',str(stage/'model'),'--output',str(evidence/'seen'),'--deadline',str(compute)]
        run_logged(command,evidence/'driver.log',remaining(compute))
        completed_seen(evidence/'seen',folder,settings)
        identity['diagnostic_status']='complete'
    except BaseException as error:
        failure=error
        identity.update(error_type=type(error).__name__,error=str(error))
        emit('diagnostic_incomplete',error_type=type(error).__name__,error=str(error))
    finally:
        signal.alarm(max(1,int(max(0,deadline-time.monotonic()))))
        (evidence/'status.json').write_text(json.dumps(identity,indent=2)+'\n',encoding='utf-8')
        before=time.monotonic()
        result=export_evidence(evidence,output,deadline,identity)
        from datetime import datetime, timezone
        emit('ready_to_persist',export_seconds=time.monotonic()-before,
            ready_utc=datetime.now(timezone.utc).isoformat(),**result)
        time.sleep(max(0,min(60,deadline-time.monotonic())))
        signal.alarm(0)
    if failure is not None:
        raise failure


def specification(run_id=None):
    run_id=uuid.uuid4().hex if run_id is None else run_id
    if not re.fullmatch('[a-f0-9]{32}',run_id):
        raise ValueError('Unique diagnostic run id required')
    path,manifest,manifest_sha=package()
    spec,hashes=hf_preflight.specification('cuda')
    prefix,marker,_=hf_preflight.BOOTSTRAP.partition('device = sys.argv[2]\n')
    if not marker:
        raise ValueError('Bootstrap boundary changed')
    settings=dict(run_id=run_id,package_name='nllb-seen-'+file_sha256(path)[:16]+'.zip',
        package_sha256=file_sha256(path),package_manifest_sha256=manifest_sha,bootstrap_hashes=hashes,
        model=nllb_train.MODEL,revision=nllb_train.REVISION,model_manifest_sha256=MODEL_MANIFEST_SHA,
        model_run_id='99231a67ac364af992565d15cb53a325',model_prefix=MODEL_PREFIX,
        inference_names=list(INFERENCE_NAMES),train_sha256=manifest['files']['train.jsonl']['sha256'],
        inputs_sha256=manifest['files']['inputs.jsonl']['sha256'],
        source_control_sha256=manifest['files']['source-control.json']['sha256'],
        token_map_sha256=manifest['files']['token-map.json']['sha256'],
        compute_seconds=600,internal_seconds=780,native_timeout_minutes=15,output_prefix='nllb-seen/'+run_id)
    code='import hashlib,json,os,re,signal,stat,sys,tempfile,time,zipfile\nfrom pathlib import Path,PurePosixPath\n'
    for function in (file_sha256,safe_extract,remaining,emit,fresh_output,export_evidence,
                     run_logged,verify_package,copy_inference,completed_seen,execute_seen):
        code+=inspect.getsource(function)+'\n'
    code+='execute_seen('+repr(settings)+','+repr(prefix)+')\n'
    compile(code,'hf-nllb-seen','exec')
    spec['command'][3]=hf_contextual.compressed_command(code)
    hf_contextual.command_lengths(spec['command'])
    spec['timeout']='15m'
    spec['labels'].update(purpose='nllb-seen',trial_id=run_id)
    spec['env'].update(OMP_NUM_THREADS='8',MKL_NUM_THREADS='8',HF_HUB_DISABLE_IMPLICIT_TOKEN='1')
    from huggingface_hub import Volume
    spec['volumes']=[Volume(type='bucket',source=BUCKET,path='inputs',mount_path='/input',read_only=True),
        Volume(type='bucket',source=BUCKET,path=MODEL_PREFIX,mount_path='/trained',read_only=True),
        Volume(type='bucket',source=BUCKET,path=settings['output_prefix'],mount_path='/output',read_only=False)]
    settings['command_sha256']=hashlib.sha256(spec['command'][3].encode()).hexdigest()
    return spec,settings
