"""Prepare a separate closed faithfulness Job; historical runtime/scorer pins stay unchanged."""
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

from . import hf_baseline, hf_component, hf_contextual, hf_convert, hf_dev_assisted, hf_preflight, hf_train

file_sha256, remaining, safe_extract = hf_convert.file_sha256, hf_convert.remaining, hf_convert.safe_extract
emit, publish, run_logged = hf_train.emit, hf_baseline.publish, hf_contextual.run_logged

DICTIONARY_INPUT_SHA256 = 'c53a78920b50598a17ac36cbbf4e50550d609c8838419162902fa7536764eeac'
DICTIONARY_CONTRACT_SHA256 = '6aebdcea208c3c4d84bb541a55bb71eac76cb8529e0a18dadce79b4e963972db'
DICTIONARY_CASES = tuple('QUALITYDEV1-'+n for n in
    ('002','003','005','006','007','008','009','010','012','013','014','015','017','020','021'))


HISTORICAL_CONTROL_MESSAGES_SHA256 = {'QUALITYDEV1-002': '48cb3e1e8080780de9c9b4143bcd00fcc1a632a8775ee215f574a1f6c44ef7fb', 'QUALITYDEV1-003': 'f19cc7f357edb6e845f2f9a8709ec3ec72a1261290d0b403c31c258ce2a82e42', 'QUALITYDEV1-005': '8de3a7c3dc25bbdf8f0fce7be9f6d7c3e11508624f98b9b8aab793e65627922b', 'QUALITYDEV1-006': 'ed975434af6d903ccee3aabb42d7e491ab416c16d874c662d109da9e4ec11edc', 'QUALITYDEV1-007': '8f41f04f419d1be63707b77c5274b16b404dc3fa5463682e932a5959b9af4c3a', 'QUALITYDEV1-008': '27d33e5a3601e24dc68af192f4f7f7c391c5931516d4a08e099bdbba1de59850', 'QUALITYDEV1-009': '90f97821663b037b7fe64fbc81d4c6f2957f5d3239ad4454075a822cd0b600a3', 'QUALITYDEV1-010': 'f9b92b1f1eb256fffc3c732763c8dcb385de2d8131d60e6f95bb8a8a43b1b57a', 'QUALITYDEV1-012': '9882e0d627d768cc4423dd4e7de2400855dbd7b1f2f31b030365a47461cd5363', 'QUALITYDEV1-013': 'b8e72089598fe0d6949d82a45149e778de78604dc376b91a3382d0bea0534f5c', 'QUALITYDEV1-014': '2a1ef7095bfcf66e4858521ff48f801b5b78bb552b27f214a8f07f93b4bd9361', 'QUALITYDEV1-015': 'fb59af3222aeae852eed4143326db856834aa6cd8808d0d7c96fa41950cd0dd6', 'QUALITYDEV1-017': '3ce118e0abb16381b0a85b1c1836686c605bfa2c2a0b5f1f47f51765e67a1abd', 'QUALITYDEV1-020': '5f72d115f485b3925b179614e2f1f2c2758db269e9982b2237a8a76f666f0297', 'QUALITYDEV1-021': 'be65662013517e8af709ae25293ec6e83f104304908458216b319892ff30907b'}
FAITHFULNESS_SENTENCE = 'Do not add explanatory glosses or equate alternative dictionary meanings unless the source context supports the added meaning.'

def dictionary_schedule():
    return [case+':'+arm for i,case in enumerate(DICTIONARY_CASES)
            for arm in (('A','B') if i % 2 == 0 else ('B','A'))]


def dictionary_controls():
    return dict(input_cap_tokens=8192,max_new_tokens=4096,context_limit=12288,
        max_generation_seconds=90,slot_export_reserve_seconds=20,export_overhead_seconds=600,
        tail_reserve_seconds=120,first_attempt_admission_seconds=3420,no_truncation=True,
        first_attempt_only=True,timeout_or_output_cap_primary_inconclusive=True)


def validate_frozen_inputs(raw, contract_raw):
    """Bind the new closed pair to historical B without loading answers or reviews."""
    if (hashlib.sha256(raw).hexdigest() != DICTIONARY_INPUT_SHA256
            or hashlib.sha256(contract_raw).hexdigest() != DICTIONARY_CONTRACT_SHA256):
        raise ValueError('Frozen faithfulness inputs/contract differ')
    contract = json.loads(contract_raw)
    if (contract.get('protocol') != 'dictionary-faithfulness-v1'
            or contract.get('model_inputs_sha256') != DICTIONARY_INPUT_SHA256):
        raise ValueError('Faithfulness contract/input identity differs')
    rows = [json.loads(line) for line in raw.splitlines()]
    fields = {'id','case_id','work_id','arm','source_sha256','messages','input_tokens',
              'rendered_text_sha256','input_ids_sha256','eligible_without_truncation','dictionary_group_count'}
    works = dict(zip(DICTIONARY_CASES,
        ('parsig:103',)*4 + ('parsig:112',)*5 + ('parsig:138',)*4 + ('parsig:517',)*2))
    if len(rows) != 30 or [r.get('id') for r in rows] != [c+':'+a for c in DICTIONARY_CASES for a in 'AB']:
        raise ValueError('Exactly the closed 30 faithfulness inputs required')
    for row in rows:
        messages = row.get('messages')
        if (set(row) != fields or row['arm'] not in ('A','B')
                or row['case_id'] not in works or row['id'] != row['case_id']+':'+row['arm']
                or row['work_id'] != works[row['case_id']]
                or row['eligible_without_truncation'] is not True
                or type(row['input_tokens']) is not int or not 0 < row['input_tokens'] <= 8192
                or type(row['dictionary_group_count']) is not int or row['dictionary_group_count'] <= 0
                or any(not isinstance(row[k],str) or not re.fullmatch('[a-f0-9]{64}',row[k])
                    for k in ('source_sha256','rendered_text_sha256','input_ids_sha256'))
                or not isinstance(messages,list) or len(messages) != 2
                or any(not isinstance(m,dict) or set(m) != {'role','content'}
                    or not isinstance(m['content'],str) or not m['content'].strip() for m in messages)
                or [m['role'] for m in messages] != ['system','user']):
            raise ValueError('Faithfulness model-visible schema differs')
        try:
            caution, payload = messages[1]['content'].split('\n\n',1)
            payload = json.loads(payload)
            if (not caution.strip() or set(payload) != {'source_text','dictionary_evidence'}
                    or not isinstance(payload['source_text'],str) or not payload['source_text'].strip()
                    or hashlib.sha256(payload['source_text'].encode()).hexdigest() != row['source_sha256']
                    or not isinstance(payload['dictionary_evidence'],list)
                    or len(payload['dictionary_evidence']) != row['dictionary_group_count']):
                raise ValueError('Faithfulness source/evidence binding differs')
        except (TypeError,AttributeError,json.JSONDecodeError) as error:
            raise ValueError('Faithfulness source/evidence binding differs') from error
    for a,b in zip(rows[::2],rows[1::2]):
        control_hash = hashlib.sha256(json.dumps(a['messages'],ensure_ascii=False,
            sort_keys=True,separators=(',',':')).encode()).hexdigest()
        if (control_hash != HISTORICAL_CONTROL_MESSAGES_SHA256[a['case_id']]
                or a['messages'][1]['content'].encode() != b['messages'][1]['content'].encode()
                or b['messages'][0]['content'] != a['messages'][0]['content']+'\n'+FAITHFULNESS_SENTENCE
                or a['source_sha256'] != b['source_sha256']
                or a['dictionary_group_count'] != b['dictionary_group_count']):
            raise ValueError('Faithfulness historical control or exact paired intervention differs')
    return rows


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
    dictionary = count == 30 and expected_schedule == dictionary_schedule()
    if not dictionary:
        raise ValueError('Unknown closed schedule')
    if dictionary and (state.get('protocol') != 'dictionary-faithfulness-v1'
            or state.get('inputs_sha256') != DICTIONARY_INPUT_SHA256
            or state.get('decode_controls') != dictionary_controls()
            or state.get('timing_contract') != 'dictionary-faithfulness-90s-v1'
            or state.get('contract_sha256') != DICTIONARY_CONTRACT_SHA256):
        raise ValueError('Closed dictionary recovery identity differs')
    source_rows = None
    if dictionary:
        source_file = output.parent / 'model-inputs.jsonl'
        if file_sha256(source_file) != DICTIONARY_INPUT_SHA256:
            raise ValueError('Frozen dictionary recovery inputs differ')
        source_rows = {r['id']:r for r in validate_frozen_inputs(source_file.read_bytes(),
            (output.parent / 'contract.json').read_bytes())}
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
                or row['id'] != row['case_id']+(':' if dictionary else '-')+row['condition']
                or row['identity_sha256'] != state['identity_sha256']
                or row['status'] not in ({'success','abstain','timeout','error','skipped_dependency'}
                                        if own_analysis else {'success','abstain','timeout','error'})):
            raise ValueError('First-attempt journal identity/status differs')
        if dictionary:
            messages = row.get('messages')
            original = source_rows[key]
            if (row.get('arm') != row['condition'] or row.get('hit_output_cap_without_eos') is not False
                    and row['status'] in {'success','abstain'}
                    or not isinstance(messages,list) or len(messages) != 2
                    or [m.get('role') for m in messages] != ['system','user']
                    or row.get('messages_sha256') != hashlib.sha256(
                        json.dumps(messages,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
                    or row.get('output_sha256') != hashlib.sha256(row['text'].encode()).hexdigest()
                    or type(row.get('output_tokens')) is not int
                    or row.get('output_tokens') != len(row.get('output_token_ids',[]))
                    or not 0 <= row['output_tokens'] <= 4096
                    or type(row.get('input_tokens')) is not int or not 0 < row['input_tokens'] <= 8192
                    or messages != original['messages'] or row.get('work_id') != original['work_id']
                    or row.get('source_sha256') != original['source_sha256']
                    or row['input_tokens'] != original['input_tokens']
                    or row.get('rendered_input_ids_sha256') != original['input_ids_sha256']
                    or row.get('rendered_sha256') != original['rendered_text_sha256']
                    or any(type(token) is not int or token < 0 for token in row.get('output_token_ids',[]))
                    or row['status'] in {'success','abstain'} and
                        (not row['text'].strip() or not row.get('output_token_ids') or row['output_token_ids'][-1] not in [1,106,50]
                         or row.get('stop_reason') is not None)):
                raise ValueError('Dictionary first-attempt output/message evidence differs')
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
    if dictionary or own_analysis or 'model_calls_started' in state or any('model_call_started' in r for r in rows):
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
        pipeline_complete=complete and all(r['status'] in
            ({'success','abstain'} if dictionary else {'success'}) for r in rows),
        unavailable_dependencies_for_unattempted_slots=unavailable,
        original_run_status=state['status'], original_evidence_unchanged=True,
        primary_comparison_inconclusive=not (complete and all(r['status'] in {'success','abstain'} for r in rows)),
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
    command = [sys.executable, '-u', str(stage / 'faithfulness_eval.py'), '--base', str(base),
               '--bundle', str(folder), '--adapter', str(stage / 'training/adapter'),
               '--inputs', str(Path('/input') / settings['inputs_name']),
               '--contract', str(Path('/input') / settings['contract_name']), '--settings', str(stage / 'settings.json'),
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
    dictionary = settings.get('protocol') == 'dictionary-faithfulness-v1'
    if not dictionary: raise ValueError('Only the separate dictionary-faithfulness-v1 runtime is allowed')
    if dictionary and (settings.get('decode_controls') != dictionary_controls()
            or settings.get('timing_contract') != 'dictionary-faithfulness-90s-v1'
            or settings.get('compute_seconds') != 6600 or settings.get('internal_seconds') != 7020
            or settings.get('native_timeout_minutes') != 120
            or settings.get('schedule') != dictionary_schedule()
            or settings.get('inputs_sha256') != DICTIONARY_INPUT_SHA256
            or settings.get('contract_sha256') != DICTIONARY_CONTRACT_SHA256
            or settings.get('precision') != 'bf16_base_fp32_retained_lora'
            or settings.get('training') is not False or settings.get('automatic_retry') is not False
            or type(settings.get('planned_outputs')) is not int or settings.get('planned_outputs') != 30
            or any(type(settings.get(k)) is not int for k in
                   ('compute_seconds','internal_seconds','native_timeout_minutes'))
            or any(type(settings['decode_controls'].get(k)) is not int for k,v in dictionary_controls().items()
                   if type(v) is int)
            or any(type(settings['decode_controls'].get(k)) is not bool for k,v in dictionary_controls().items()
                   if type(v) is bool)):
        raise ValueError('Closed dictionary deadline/settings contract differs')
    compute_seconds, internal_seconds = (6600,7020) if dictionary else (3000,3300)
    started = time.monotonic()
    deadline = started + internal_seconds
    compute_deadline = started + compute_seconds
    def interrupted(signum, frame):
        raise TimeoutError('Component job computation interrupted or deadline reached')
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGALRM, interrupted)
    signal.alarm(compute_seconds)
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
        contract_source = Path('/input') / settings['contract_name']
        validate_frozen_inputs(source.read_bytes(), contract_source.read_bytes())
        shutil.copyfile(source, evidence / 'model-inputs.jsonl')
        shutil.copyfile(contract_source, evidence / 'contract.json')
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
        try:
            export_deadline = deadline - 60 if dictionary else deadline
            result = publish_checked(evidence, output / 'final', export_deadline, identity)
            emit('ready_to_persist', manifest_sha256=result['manifest_sha256'], remote_inventory_verified=False)
            if dictionary:
                remaining(deadline,60)
                time.sleep(60)
            else:
                time.sleep(max(0,min(60,deadline-time.monotonic())))
            emit('persistence_window_expired', remote_inventory_verified=False)
        finally:
            signal.alarm(0)
    if failure is not None: raise failure


def helper_source():
    """Retain reviewed helpers, then add only this version's frozen input validator."""
    code, origins = hf_component.helper_source()
    code = code.decode() + 'import re\n'
    for name in ('DICTIONARY_INPUT_SHA256','DICTIONARY_CONTRACT_SHA256','DICTIONARY_CASES',
                 'HISTORICAL_CONTROL_MESSAGES_SHA256','FAITHFULNESS_SENTENCE'):
        code += name + '=' + repr(globals()[name]) + '\n'
    code += inspect.getsource(validate_frozen_inputs) + '\n'
    compile(code,'component_helpers.py','exec')
    return code.encode(), origins


def prepare(inputs_path, run_id=None, protocol='dictionary-faithfulness-v1', contract_path=None):
    """Build an actual SDK spec locally; do not authenticate, call providers or submit."""
    from huggingface_hub import HfApi, Volume
    if protocol != 'dictionary-faithfulness-v1': raise ValueError('Only dictionary-faithfulness-v1 is allowed')
    run_id = uuid.uuid4().hex if run_id is None else run_id
    if not re.fullmatch('[a-f0-9]{32}',run_id): raise ValueError('Fresh hexadecimal identity required')
    inputs_path = Path(inputs_path)
    contract_path = Path(contract_path) if contract_path is not None else inputs_path.with_name('contract.json')
    raw, contract_raw = inputs_path.read_bytes(), contract_path.read_bytes()
    validate_frozen_inputs(raw,contract_raw)
    spec, hashes = hf_preflight.specification('cuda')
    bootstrap, marker, _ = hf_preflight.BOOTSTRAP.partition('device = sys.argv[2]\n')
    if not marker: raise ValueError('Reviewed bootstrap boundary differs')
    helper, origins = helper_source()
    contents = {'faithfulness_eval.py':Path(__file__).with_name('faithfulness_eval.py').read_bytes(),
                'component_helpers.py':helper}
    scripts = {n:dict(sha256=hashlib.sha256(b).hexdigest(),content=base64.b64encode(b).decode()) for n,b in contents.items()}
    retained = {'training/adapter/'+n:s for n,s in hf_dev_assisted.dev_assisted.ADAPTER_FILES.items()}
    retained.update({'training/'+n:s for n,s in hf_dev_assisted.dev_assisted.ADAPTER_METADATA.items()})
    settings = dict(protocol=protocol,run_id=run_id,
        inputs_name='dictionary-faithfulness-'+DICTIONARY_INPUT_SHA256[:16]+'.jsonl',
        contract_name='dictionary-faithfulness-contract-'+DICTIONARY_CONTRACT_SHA256[:16]+'.json',
        inputs_sha256=DICTIONARY_INPUT_SHA256,contract_sha256=DICTIONARY_CONTRACT_SHA256,
        script_hashes={n:v['sha256'] for n,v in scripts.items()},helper_origins=origins,
        trained_manifest_sha256=hf_dev_assisted.dev_assisted.ADAPTER_MANIFEST_SHA256,retained_files=retained,
        bundle_name=hf_dev_assisted.BUNDLE_NAME,bundle_sha256=hf_dev_assisted.BUNDLE_SHA256,bootstrap_hashes=hashes,
        precision='bf16_base_fp32_retained_lora',compute_seconds=6600,internal_seconds=7020,native_timeout_minutes=120,
        planned_outputs=30,training=False,automatic_retry=False,schedule=dictionary_schedule(),
        decode_controls=dictionary_controls(),timing_contract='dictionary-faithfulness-90s-v1',generation_admitted=False)
    code = 'import base64,hashlib,json,re,signal,stat,tempfile,time,zipfile\nfrom pathlib import Path,PurePosixPath\n'
    for name in ('DICTIONARY_INPUT_SHA256','DICTIONARY_CONTRACT_SHA256','DICTIONARY_CASES',
                 'HISTORICAL_CONTROL_MESSAGES_SHA256','FAITHFULNESS_SENTENCE'):
        code += name+'='+repr(globals()[name])+'\n'
    for function in (dictionary_schedule,dictionary_controls,validate_frozen_inputs,file_sha256,remaining,
            safe_extract,emit,publish,publish_checked,run_logged,reconcile,component_body,execute):
        code += inspect.getsource(function)+'\n'
    code += 'execute('+repr(settings)+','+repr(scripts)+','+repr(bootstrap)+')\n'
    compile(code,'hf-dictionary-faithfulness','exec')
    spec['command'][3] = hf_contextual.compressed_command(code)
    lengths,total = hf_contextual.command_lengths(spec['command'])
    spec.update(flavor='a100-large',timeout='120m')
    spec['labels'].update(purpose='dictionary-faithfulness-inference',trial_id=run_id)
    spec['env'].update(HF_XET_CACHE='/tmp/pahlavi-xet-cache',OMP_NUM_THREADS='8',MKL_NUM_THREADS='8')
    output_prefix = 'dictionary-faithfulness/'+run_id
    spec['volumes'] = [Volume(type='bucket',source=hf_train.BUCKET,path=p,mount_path=m,read_only=r)
        for p,m,r in [('inputs','/input',True),(hf_dev_assisted.TRAINED_PREFIX,'/trained',True),(output_prefix,'/output',False)]]
    inspect.signature(HfApi.run_job).bind(None,**spec)
    return spec,dict(settings,output_prefix=output_prefix,prepared_not_submitted=True,
        training_performed=False,optimizer_updates=0,credentials_accessed=False,provider_called=False,
        model_visible_scope='frozen_system_user_messages_only',contract_scope='source_only_no_references',
        submitted=False,decoded_command_sha256=hashlib.sha256(code.encode()).hexdigest(),
        command_arg_utf8_bytes=lengths,command_total_utf8_bytes_with_nul=total)
