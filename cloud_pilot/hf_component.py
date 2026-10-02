"""Prepare one 60-minute component inference Job; never authenticate or submit."""
import ast
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

from . import hf_baseline, hf_contextual, hf_convert, hf_dev_assisted, hf_preflight, hf_train

file_sha256, remaining, safe_extract = hf_convert.file_sha256, hf_convert.remaining, hf_convert.safe_extract
emit, publish, run_logged = hf_train.emit, hf_baseline.publish, hf_contextual.run_logged


def publish_checked(source, output, deadline, identity):
    result = publish(source, output, deadline, identity)
    for name, entry in result['manifest']['files'].items():
        remaining(deadline)
        target = output / name
        if target.stat().st_size != entry['bytes'] or file_sha256(target) != entry['sha256']:
            raise ValueError('Mounted export readback differs: ' + name)
    if file_sha256(output / 'manifest.json') != result['manifest_sha256']:
        raise ValueError('Mounted manifest readback differs')
    return result


def reconcile(output, expected_schedule):
    """Account for stopped first attempts without altering raw evidence or retrying."""
    state = json.loads((output / 'run.json').read_bytes())
    count = len(expected_schedule)
    own_analysis = count == 9 and expected_schedule == [c+'-'+a for c,o in
        zip(('KANHERI01','AMOL1','BERLIN6'),('DAP','APD','DAP')) for a in o]
    if count not in (9,12) or (count == 9 and not own_analysis):
        raise ValueError('Unknown closed schedule')
    if state['schedule'] != expected_schedule or state['scheduled_outputs'] != count:
        raise ValueError('Fixed denominator schedule differs')
    path = output / 'predictions.jsonl'
    raw = path.read_bytes() if path.exists() else b''
    if raw and not raw.endswith(b'\n'):
        raise ValueError('Partial prediction tail preserved; cannot safely interpret it')
    rows = [json.loads(x) for x in raw.splitlines()]
    attempted, recorded = state['attempted_outputs'], state['recorded_outputs']
    if (type(attempted) is not int or type(recorded) is not int
            or not 0 <= recorded <= len(rows) <= attempted <= count
            or attempted-recorded not in (0,1)
            or state['active_output_id'] != (expected_schedule[recorded] if attempted > recorded else None)
            or state['unattempted_output_ids'] != expected_schedule[attempted:]):
        raise ValueError('First-attempt journal counters differ')
    for index, row in enumerate(rows):
        key = expected_schedule[index]
        if (row['id'] != key or row['sequence'] != index+1
                or row['id'] != row['case_id']+'-'+row['condition']
                or row['identity_sha256'] != state['identity_sha256']
                or row['status'] not in ({'success','abstain','timeout','error','skipped_dependency'}
                                        if own_analysis else {'success','abstain','timeout','error'})):
            raise ValueError('First-attempt journal identity/status differs')
        if own_analysis and row['status'] == 'skipped_dependency':
            analysis = next((r for r in rows[:index] if r['id'] == row['analysis_output_id']), None)
            if (row['condition'] != 'P' or row['model_call_started'] or row['output_tokens'] != 0
                    or row['analysis_output_id'] != row['case_id']+'-A'
                    or analysis is None or analysis['status'] == 'success'
                    or row['analysis_output_sha256'] != analysis['output_sha256']):
                raise ValueError('Dependency skip evidence differs')
        if own_analysis and row['condition'] == 'P' and row['model_call_started']:
            analysis = next((r for r in rows[:index] if r['id'] == row['case_id']+'-A'), None)
            if (analysis is None or analysis['status'] != 'success'
                    or row['analysis_output_id'] != analysis['id']
                    or row['analysis_output_sha256'] != analysis['output_sha256']):
                raise ValueError('Resolved P analysis provenance differs')
    committed_calls = sum(r.get('model_call_started', True) for r in rows)
    # Legacy archived journals predate dispatch flags. New flagged journals in
    # every protocol must prove generated statuses were actually dispatched.
    if own_analysis or 'model_calls_started' in state or any('model_call_started' in r for r in rows):
        started_calls = state.get('model_calls_started')
        if (any(type(r.get('model_call_started')) is not bool for r in rows)
                or any(r['status'] in {'success','abstain','timeout'}
                       and r['model_call_started'] is not True for r in rows)
                or type(started_calls) is not int
                or not committed_calls <= started_calls <= committed_calls + attempted-len(rows)):
            raise ValueError('Dispatched model-call accounting differs')
    known = {r['id']:r['status'] for r in rows}
    outcomes = {key:known.get(key,'interrupted_output_unknown' if i < attempted else 'unattempted')
                for i,key in enumerate(expected_schedule)}
    complete = (len(rows) == attempted == recorded == count
                and state['status'] in {'completed','completed_with_errors'}
                and state.get('adapter_unchanged_after_inference') is True)
    unavailable = {key:key[:-1]+'A' for key in expected_schedule if key.endswith('-P')
        and known.get(key[:-1]+'A') in {'error','timeout','abstain'} and key not in known} if own_analysis else {}
    return dict(status='complete' if complete else 'incomplete', scheduled_outputs=count,
        attempted_outputs=attempted, committed_jsonl_outputs=len(rows), per_output_status=outcomes,
        model_calls_started=state.get('model_calls_started'),
        committed_model_calls=committed_calls,
        pipeline_complete=complete and all(r['status'] == 'success' for r in rows),
        unavailable_dependencies_for_unattempted_slots=unavailable,
        original_run_status=state['status'], original_evidence_unchanged=True,
        replacements_generated=False, raw_predictions_sha256=hashlib.sha256(raw).hexdigest())


def component_body(settings, stage, deadline, evidence):
    import os
    import shutil
    import subprocess
    import sys
    from datetime import datetime, timedelta, timezone
    folder, base = stage / 'bundle', stage / 'base'
    sys.path.insert(0, str(folder))
    import bundle
    import runtime
    bundle.verify(folder)
    runtime.gpu_admission()
    trained = Path('/trained')
    if file_sha256(trained / 'manifest.json') != settings['trained_manifest_sha256']:
        raise ValueError('Retained step280 manifest differs')
    manifest = json.loads((trained / 'manifest.json').read_text('utf-8'))
    if (manifest.get('full_training_completed') is not True
            or manifest.get('training_schedule_completed') is not True or manifest.get('completed_global_step') != 280):
        raise ValueError('Completed retained step280 required')
    for name, checksum in settings['retained_files'].items():
        source, target, entry = trained / name, stage / name, manifest['files'][name]
        remaining(deadline, 180)
        if entry['sha256'] != checksum or source.stat().st_size != entry['bytes']:
            raise ValueError('Retained artifact inventory differs: ' + name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if file_sha256(target) != checksum:
            raise ValueError('Retained server copy checksum differs: ' + name)
    shutil.copyfile(trained / 'manifest.json', evidence / 'trained-manifest.json')
    shutil.copyfile(folder / 'manifest.json', evidence / 'bundle-manifest.json')
    emit('base_download_started', server_only=True)
    run_logged([sys.executable, '-u', str(folder / 'fetch_base.py'), '--out', str(base), '--download'],
               evidence / 'base-download.log', remaining(deadline, 180))
    shutil.copyfile(base / 'provenance.json', evidence / 'base-provenance.json')
    runtime.offline()
    emit('base_download_verified', server_only=True)
    os.environ['PYTHONPATH'] = os.pathsep.join((str(stage), str(folder)))
    child_seconds = remaining(deadline, 180)
    cutoff = (datetime.now(timezone.utc) + timedelta(seconds=child_seconds)).isoformat()
    command = [sys.executable, '-u', str(stage / 'component_eval.py'), '--base', str(base),
               '--bundle', str(folder), '--adapter', str(stage / 'training/adapter'),
               '--inputs', str(Path('/input') / settings['inputs_name']), '--settings', str(stage / 'settings.json'),
               '--output', str(evidence / 'evaluation'), '--incremental', '/output/incremental', '--deadline-utc', cutoff]
    count = len(settings['schedule'])
    emit('component_inference_started', scheduled_outputs=count, training=False)
    run_logged(command, evidence / 'driver.log', remaining(deadline, 180))
    run = json.loads((evidence / 'evaluation/run.json').read_text('utf-8'))
    results = [json.loads(x) for x in (evidence / 'evaluation/predictions.jsonl').read_bytes().splitlines()]
    if (run['status'] not in {'completed','completed_with_errors'} or run['recorded_outputs'] != count
            or run['attempted_outputs'] != count or run['active_output_id'] is not None
            or run['unattempted_output_ids'] != [] or len(results) != count
            or [r['id'] for r in results] != run['schedule']
            or [r['sequence'] for r in results] != list(range(1,count+1))
            or any(r['identity_sha256'] != run['identity_sha256'] for r in results)
            or run.get('adapter_unchanged_after_inference') is not True):
        raise ValueError('Fixed first-attempt ledger or post-inference adapter identity failed')


def execute(settings, scripts, bootstrap):
    import shutil
    deadline = time.monotonic() + 3300
    compute_deadline = time.monotonic() + 3000
    def interrupted(signum, frame):
        raise TimeoutError('Component job computation interrupted or deadline reached')
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGALRM, interrupted)
    signal.alarm(3000)
    output = Path('/output')
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()): raise ValueError('Fresh output prefix required; no retries')
    stage = Path(tempfile.mkdtemp(prefix='pahlavi-component-'))
    evidence = stage / 'evidence'
    evidence.mkdir()
    identity = dict(settings, operation='closed_protocol_inference_only', status='incomplete',
                    training_performed=False, optimizer_updates=0, quality_validated=False)
    failure = None
    try:
        if shutil.disk_usage('/tmp').free < 90 * 1024**3:
            raise ValueError('Requires 90 GiB ephemeral disk for server-only base')
        source = Path('/input') / settings['inputs_name']
        if file_sha256(source) != settings['inputs_sha256']: raise ValueError('Frozen protocol inputs differ')
        shutil.copyfile(source, evidence / 'model-inputs.jsonl')
        safe_extract(Path('/input') / settings['bundle_name'], stage / 'bundle', settings['bundle_sha256'], 128 * 1024**2)
        for name, expected in settings['bootstrap_hashes'].items():
            if file_sha256(stage / 'bundle' / name) != expected: raise ValueError('Qualified bootstrap differs')
        for name, entry in scripts.items():
            data = base64.b64decode(entry['content'])
            if Path(name).name != name or hashlib.sha256(data).hexdigest() != entry['sha256']:
                raise ValueError('Runner source identity differs')
            (stage / name).write_bytes(data)
        (stage / 'settings.json').write_text(json.dumps(settings), encoding='utf-8')
        emit('bootstrap_started', training=False)
        exec(bootstrap)
        emit('bootstrap_complete', training=False)
        component_body(settings, stage, compute_deadline, evidence)
        identity['status'] = 'finished_see_per_attempt_status'
    except BaseException as error:
        failure = error
        identity.update(error_type=type(error).__name__, error=str(error))
        emit('component_incomplete', error_type=type(error).__name__, error=str(error))
    finally:
        signal.alarm(max(1, int(max(0,deadline-time.monotonic()))))
        evaluation = evidence / 'evaluation'
        if (evaluation / 'run.json').exists():
            try:
                accounting = reconcile(evaluation,settings['schedule'])
                (evidence / 'reconciliation.json').write_text(json.dumps(accounting,indent=2)+'\n',encoding='utf-8')
                if accounting['status'] != 'complete': identity['status'] = 'incomplete'
            except BaseException as error:
                identity.update(status='incomplete',reconciliation_error_type=type(error).__name__,reconciliation_error=str(error))
                if failure is None: failure=error
        (evidence / 'job-status.json').write_text(json.dumps(identity,indent=2)+'\n',encoding='utf-8')
        result = publish_checked(evidence, output / 'final', deadline, identity)
        emit('ready_to_persist', manifest_sha256=result['manifest_sha256'], remote_inventory_verified=False)
        time.sleep(max(0,min(60,deadline-time.monotonic())))
        emit('persistence_window_expired', remote_inventory_verified=False)
        signal.alarm(0)
    if failure is not None: raise failure


def helper_source():
    """Reuse exact existing reviewed primitives without their unrelated training imports."""
    root = Path(__file__).parent
    code = 'import hashlib,json,time\nfrom pathlib import Path\nimport runtime\nARMS=("reference",)\n'
    origins = {}
    for name, functions in (
        ('hf_convert.py', ('file_sha256','remaining')),
        ('hf_train.py', ('emit',)), ('hf_baseline.py', ('publish',)),
        ('dev_assisted.py', ('sha','canonical','verify_adapter','prefill_canary')),
        ('dose_run.py', ('select_adapter',)), ('contextual_run.py', ('verify_loaded_adapter',))):
        source = (root / name).read_text('utf-8')
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name in functions:
                code += ast.get_source_segment(source,node) + '\n\n'
            if (name == 'dev_assisted.py' and isinstance(node,ast.Assign)
                    and any(isinstance(t,ast.Name) and t.id in {'ADAPTER_FILES','ADAPTER_METADATA','TRAIN_SHA256'} for t in node.targets)):
                code += ast.get_source_segment(source,node) + '\n'
        origins[name] = file_sha256(root / name)
    code += inspect.getsource(publish_checked)+'\n'
    compile(code,'component_helpers.py','exec')
    return code.encode(), origins


def prepare(inputs_path, run_id=None, protocol='components-v1'):
    from huggingface_hub import HfApi, Volume
    run_id = uuid.uuid4().hex if run_id is None else run_id
    if not re.fullmatch(r'[a-f0-9]{32}',run_id): raise ValueError('Fresh hexadecimal identity required')
    inputs_path = Path(inputs_path)
    raw = inputs_path.read_bytes()
    rows = [json.loads(x) for x in raw.splitlines()]
    old_cases = ('KANHERI06','BERK25','TB3','ZAND301')
    protocols = {'components-v1': (old_cases, 'ABC', ('ABC','BCA','CAB','CBA'), 'component-diagnostic', '20261001'),
                 'stages-v1': (old_cases, 'IRS', ('IRS','RSI','SIR','SRI'), 'semantic-stage-diagnostic', '20261001'),
                 'own-analysis-v1': (('KANHERI01','AMOL1','BERLIN6'), 'DAP', ('DAP','APD','DAP'), 'own-analysis-diagnostic', '20261002')}
    cases, conditions, orders, experiment, date = protocols[protocol]
    fields = {'id','case_id','condition','prompt','prompt_tokens','rendered_sha256','has_unknown_token'}
    if protocol == 'own-analysis-v1': fields.add('dependency_id')
    count = len(cases)*len(conditions)
    if (len(rows) != count or [r['id'] for r in rows] != [c+'-'+a for c in cases for a in conditions]
            or any(set(r) != fields for r in rows)):
        raise ValueError('Only closed frozen model-visible inputs may be staged')
    manifest = json.loads((Path(__file__).parents[1] / ('experiments/'+experiment+'-'+date+'/packet-manifest.json')).read_bytes())
    digest = hashlib.sha256(raw).hexdigest()
    if digest != manifest['local_outputs']['model-inputs.jsonl']['sha256']: raise ValueError('Local reviewed packet differs')
    spec, hashes = hf_preflight.specification('cuda')
    bootstrap, marker, _ = hf_preflight.BOOTSTRAP.partition('device = sys.argv[2]\n')
    if not marker: raise ValueError('Reviewed bootstrap boundary differs')
    helper, origins = helper_source()
    contents = {'component_eval.py':Path(__file__).with_name('component_eval.py').read_bytes(),'component_helpers.py':helper}
    scripts = {n:dict(sha256=hashlib.sha256(b).hexdigest(),content=base64.b64encode(b).decode()) for n,b in contents.items()}
    retained = {'training/adapter/'+n:s for n,s in hf_dev_assisted.dev_assisted.ADAPTER_FILES.items()}
    retained.update({'training/'+n:s for n,s in hf_dev_assisted.dev_assisted.ADAPTER_METADATA.items()})
    settings = dict(protocol=protocol, run_id=run_id, inputs_name=experiment+'-'+digest[:16]+'.jsonl', inputs_sha256=digest,
        script_hashes={n:v['sha256'] for n,v in scripts.items()},helper_origins=origins,
        trained_manifest_sha256=hf_dev_assisted.dev_assisted.ADAPTER_MANIFEST_SHA256, retained_files=retained,
        bundle_name=hf_dev_assisted.BUNDLE_NAME,bundle_sha256=hf_dev_assisted.BUNDLE_SHA256,bootstrap_hashes=hashes,
        precision='bf16_base_fp32_retained_lora',compute_seconds=3000,internal_seconds=3300,native_timeout_minutes=60,
        planned_outputs=count,training=False,automatic_retry=False,
        schedule=[c+'-'+a for c,o in zip(cases,orders) for a in o])
    code = 'import base64,hashlib,json,re,signal,stat,tempfile,time,zipfile\nfrom pathlib import Path,PurePosixPath\n'
    for f in (file_sha256,remaining,safe_extract,emit,publish,publish_checked,run_logged,reconcile,component_body,execute):
        code += inspect.getsource(f)+'\n'
    code += 'execute('+repr(settings)+','+repr(scripts)+','+repr(bootstrap)+')\n'
    compile(code,'hf-component','exec')
    spec['command'][3] = hf_contextual.compressed_command(code)
    lengths,total = hf_contextual.command_lengths(spec['command'])
    spec.update(flavor='a100-large',timeout='60m')
    spec['labels'].update(purpose=experiment+'-inference',trial_id=run_id)
    spec['env'].update(HF_XET_CACHE='/tmp/pahlavi-xet-cache',OMP_NUM_THREADS='8',MKL_NUM_THREADS='8')
    output_prefix = experiment+'/'+run_id
    spec['volumes'] = [Volume(type='bucket',source=hf_train.BUCKET,path=p,mount_path=m,read_only=r)
        for p,m,r in [('inputs','/input',True),(hf_dev_assisted.TRAINED_PREFIX,'/trained',True),(output_prefix,'/output',False)]]
    inspect.signature(HfApi.run_job).bind(None,**spec)
    return spec,dict(settings,output_prefix=output_prefix,prepared_not_submitted=True,
        decoded_command_sha256=hashlib.sha256(code.encode()).hexdigest(),
        command_arg_utf8_bytes=lengths,command_total_utf8_bytes_with_nul=total)
