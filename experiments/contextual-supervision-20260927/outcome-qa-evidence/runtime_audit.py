"""Independent metadata/bytes audit. Never print generated text or open reviewer ratings."""
from pathlib import Path
from collections import Counter
from datetime import datetime
from decimal import Decimal
import hashlib,json,sys,zipfile
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
EXP=ROOT/'experiments/contextual-supervision-20260927'
RUN=EXP/'attempt-2'
REC=RUN/'recovered'
LOCAL=ROOT/'resources/local/hf-contextual-run-20260927-attempt-2'
sha=lambda data:hashlib.sha256(data).hexdigest()
read=lambda path:json.loads(Path(path).read_bytes())
lines=lambda path:[json.loads(x) for x in Path(path).read_bytes().splitlines() if x.strip()]
canonical=lambda value:json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
manifest=read(REC/'manifest.json'); recovery=read(RUN/'recovery.json')
execution=read(RUN/'execution.json'); preparation=read(RUN/'execution-preparation.json')
assert sha((REC/'manifest.json').read_bytes())==recovery['manifest_sha256']
assert manifest['run_id']==recovery['run_id']==execution['run_id']==preparation['run_id']=='555064e068b54aacafee67e37375ec78'
assert execution['job_id']=='6ab9237d52d0dbd7f1d9c66b'
assert recovery['provider_inventory_committed'] is True and recovery['model_weights_downloaded'] is False
prefix=preparation['output_prefix']; inventory=recovery['provider_inventory']
assert set(inventory)=={prefix+'/manifest.json',*(prefix+'/'+n for n in manifest['files'])}
assert inventory[prefix+'/manifest.json']['bytes']==(REC/'manifest.json').stat().st_size
for n,e in manifest['files'].items():
    assert inventory[prefix+'/'+n]['bytes']==e['bytes'] and inventory[prefix+'/'+n]['xet_hash']
small=recovery['local_sha_verified_files']
assert len(small)==len(set(small))==18
assert set(small)=={n for n in manifest['files'] if n.endswith(('.json','.jsonl','.md','.log'))}
for n in small:
    b=(REC/n).read_bytes(); assert sha(b)==manifest['files'][n]['sha256'] and len(b)==manifest['files'][n]['bytes']
assert sum(manifest['files'][n]['bytes'] for n in small)==278467
assert not list(REC.rglob('*.safetensors'))
for k in ('package_manifest_sha256','package_sha256','inputs_sha256','bundle_sha256','trained_manifest_sha256','script_hashes','adapter_files','bootstrap_hashes','steps_per_arm','scheduled_outputs'):
    assert manifest[k]==preparation[k]
assert manifest['contextual_status']=='complete' and manifest['evaluation_complete'] is True and manifest['quality_validated'] is False
assert (RUN/'execution-preparation.json').read_bytes()==(LOCAL/'preparation.json').read_bytes()
assert sha((LOCAL/'spec.json').read_bytes())==preparation['spec_sha256']==execution['spec_sha256']
spec=read(LOCAL/'spec.json')
assert spec['labels']['trial_id']==execution['run_id'] and spec['timeout']=='75m'
assert sha(spec['command'][3].encode())==preparation['command_sha256']==execution['command_sha256']
captured=[]; namespace={'exec':captured.append}; exec(spec['command'][3],namespace)
assert len(captured)==1 and sha(namespace['_contextual_code'])==preparation['decoded_command_sha256']
for n,h in preparation['script_hashes'].items():assert sha((ROOT/'cloud_pilot'/n).read_bytes())==h
for n,h in preparation['review_sha256'].items():assert sha((EXP/n).read_bytes())==h
assert sha((EXP/'cloud_control.py').read_bytes())==preparation['controller_sha256']

with zipfile.ZipFile(EXP/preparation['package_name']) as z:
    package_manifest=z.read('manifest.json')
    assert sha(package_manifest)==preparation['package_manifest_sha256']
    slots=[json.loads(l) for l in z.read('ordered-slots.jsonl').splitlines()]
    prompts=json.loads(z.read('dev-prompt-identities.json'))
slotids=[s['control_id'] for s in slots]
top=read(REC/'contextual/run.json'); training=read(REC/'contextual/training/run.json'); evaluation=read(REC/'contextual/evaluation/run.json')
assert top['status']==training['status']==evaluation['status']=='completed'
assert training['scheduled_parent_ids']==slotids and len(slotids)==training['scheduled_slots_per_arm']==768
assert top['training_canary']['status']=='passed' and top['training_canary']['optimizer_updates']==0
assert top['training_canary']['adapter_sha256']==training['initial_adapter_sha256']
assert top['training_canary']['native_loss']==top['training_canary']['manual_loss']
arms={}
for arm,a in training['arms'].items():
    assert arm in ('control','candidate') and a['status']=='completed' and a['completed_steps']==48 and a['consumed_slots']==768
    assert a['consumed_parent_ids']==slotids and a['parent_order_verified'] is True
    assert a['initial_adapter_sha256']==training['initial_adapter_sha256']
    assert a['optimizer_initially_empty'] is True and a['optimizer_initial_state_entries']==a['initial_scheduler_step']==0
    assert a['model_accepts_loss_kwargs'] is False
    assert top['adapters'][arm]['files']==a['adapter_files'] and top['adapters'][arm]['final_tensor_sha256']==a['final_adapter_sha256']
    for n,h in a['adapter_files'].items():assert manifest['files'][f'contextual/training/{arm}/adapter/{n}']['sha256']==h
    progress=lines(REC/f'contextual/training/{arm}/progress.jsonl')
    assert [r['step'] for r in progress]==list(range(1,49)) and progress[-1]['consumed_slots']==768
    arms[arm]={k:a[k] for k in ('completed_steps','consumed_slots','initial_adapter_sha256','initial_rng_sha256','train_begin_rng_sha256','final_adapter_sha256','adapter_files','training_loss')}
for key in ('initial_rng_sha256','train_begin_rng_sha256'):
    assert arms['control'][key]==arms['candidate'][key]
assert arms['control']['final_adapter_sha256']!=arms['candidate']['final_adapter_sha256']
assert top['prompts']==evaluation['prompts']==prompts
for k,v in dict(seed=42,decoding='greedy',enable_thinking=False,max_new_tokens=4096,max_generation_seconds=1200,evaluation_prompt='dev_assisted.messages(row, plain, [])').items():
    assert top[k]==evaluation[k]==v
assert evaluation['canary']['status']=='passed' and evaluation['canary']['experimental_attempts']==0
for k,v in dict(scheduled_outputs=48,attempted_outputs=48,recorded_outputs=48,completed_outputs=48,completed_cases=24,active_output_id=None,unattempted_output_ids=[]).items():assert evaluation[k]==v
pred=lines(REC/'contextual/evaluation/predictions.jsonl')
assert len(pred)==48 and [p['id'] for p in pred]==evaluation['schedule']
assert len(set(p['id'] for p in pred))==48 and Counter(p['arm'] for p in pred)=={'control':24,'candidate':24}
assert Counter(p['status'] for p in pred)=={'success':48}
promptmap={p['id'].removesuffix(':plain'):p for p in prompts}
source={p['id']:p for p in lines(ROOT/'experiments/dev-diagnostic-20260927/inputs.jsonl')}
for i,p in enumerate(pred,1):
    assert p['sequence']==i and p['identity_sha256']==evaluation['identity_sha256']
    assert p['input_sha256']==sha(source[p['case_id']]['source_text'].encode())
    assert p['input_tokens']==promptmap[p['case_id']]['input_tokens'] and p['rendered_input_ids_sha256']==promptmap[p['case_id']]['rendered_input_ids_sha256']
    assert p['adapter_sha256']==top['adapters'][p['arm']]['files']['adapter_model.safetensors']
    assert p['output_sha256']==sha(p['text'].encode()) and p['output_tokens']==len(p['output_token_ids'])<=4096
    assert p['hit_output_cap_without_eos'] is False and p['stop_reason'] is None and p['elapsed_seconds']<=1200
    assert p['output_token_ids'][-1] in evaluation['eos_token_ids']

contract_path=ROOT/'experiments/dev-assisted-qualified-20260927/uniform-evaluation-contract.json'
contract=read(contract_path); contract_sha=sha(contract_path.read_bytes())
assert contract_sha=='4165e8150f291c2cd6077d2daee86513ad08e1851acbfc3e83169bc40263f8c2'
assert top['uniform_evaluation_contract_sha256']==evaluation['uniform_evaluation_contract_sha256']==contract_sha
for n,h in contract['source_files_sha256'].items():assert sha((ROOT/n).read_bytes())==h
packet_provenance=read(EXP/'blind-dev48/lead-only/provenance.json')
assert packet_provenance['completion']['complete'] is True and packet_provenance['contract_sha256']==contract_sha
for n,h in packet_provenance['files'].items():assert sha((EXP/'blind-dev48'/n).read_bytes())==h
mapping=lines(EXP/'blind-dev48/lead-only/mapping.jsonl')
assert len(mapping)==len(set(m['review_id'] for m in mapping))==96
for reviewer in ('A','B'):
    m=[m for m in mapping if m['reviewer']==reviewer]
    assert Counter(x['condition'] for x in m)=={'control':24,'candidate':24}
    assert all(x['execution_status']=='success' for x in m)
    for arm in ('control','candidate'):
        assert Counter(x['assessment'] for x in m if x['condition']==arm)=={'provisional_whole_translation':15,'constrained_meanings_only':9}
    assert {x['prediction_id'] for x in m}==set(evaluation['schedule'])

events=lines(LOCAL/'events.jsonl')
assert len([e for e in events if e['event']=='submitted'])==1
shutdown=[e for e in events if e['event']=='shutdown_status' and e['stage']=='CANCELED']
assert len(shutdown)==1 and shutdown[0]['job_id']==execution['job_id']
assert datetime.fromisoformat(recovery['utc'])<datetime.fromisoformat(shutdown[0]['utc'])
jobs=read(RUN/'post-stop-inventory.json')
assert len(jobs['jobs'])==18 and len({j['job_id'] for j in jobs['jobs']})==18 and jobs['active']==[]
assert all(j['stage'] in ('CANCELED','COMPLETED','ERROR') for j in jobs['jobs'])
assert any(j['job_id']==execution['job_id'] and j['stage']=='CANCELED' for j in jobs['jobs'])
billing=read(RUN/'post-stop-billing.json'); admission=read(RUN/'admission.json')
D=lambda x:Decimal(str(x))
credit_change=D(billing['balance_usd'])-D(admission['balance_usd'])
usage_change=D(billing['period_usage_usd'])-D(admission['period_usage_usd'])
assert credit_change==D(billing['displayed_balance_change_usd'])==Decimal('-2.08')
assert usage_change==D(billing['displayed_usage_change_usd'])==Decimal('2.08')
assert billing['automatic_recharge_set'] is False and billing['exact_per_job_invoice'] is False
assert D(admission['reservation_usd'])==Decimal('3.625025')>usage_change
observations=lines(RUN/'provider-observations.jsonl')
start=datetime.fromisoformat(observations[0]['started_at']); stop=datetime.fromisoformat(shutdown[0]['utc'])
wall=(stop-start).total_seconds(); arithmetic=D(wall)*Decimal('41667')/Decimal(60)/Decimal(1e6)

evidence=[RUN/'execution.json',RUN/'execution-preparation.json',RUN/'recovery.json',REC/'manifest.json',REC/'contextual/training/run.json',REC/'contextual/run.json',REC/'contextual/evaluation/run.json',REC/'contextual/evaluation/predictions.jsonl',RUN/'post-stop-inventory.json',RUN/'post-stop-billing.json',EXP/'blind-dev48/lead-only/provenance.json',LOCAL/'events.jsonl',LOCAL/'spec.json']
summary=dict(status='PASS',job_id=execution['job_id'],run_id=execution['run_id'],small_files=18,small_bytes=278467,
    provider_inventory_objects=len(inventory),training=arms,successful_first_attempts=48,total_output_tokens=sum(p['output_tokens'] for p in pred),
    prompt_identities=24,uniform_contract_sha256=contract_sha,all_eight_source_bindings_unchanged=True,
    training_canary=top['training_canary'],evaluation_canary=evaluation['canary'],terminal_confirmation=shutdown[0],
    all18_jobs_terminal=True,credit_change=str(credit_change),period_usage_change=str(usage_change),
    observed_running_start_to_terminal_seconds=wall,elapsed_rate_arithmetic_usd=str(arithmetic),
    arithmetic_is_not_invoice_or_upper_bound=True,no_local_weights=True,no_reviewer_ratings_read=True,
    evidence_sha256={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in evidence})
(Path(__file__).parent/'runtime-result.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k not in ('training','training_canary','evaluation_canary','evidence_sha256')},indent=2))
