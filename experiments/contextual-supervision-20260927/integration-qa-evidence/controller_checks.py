from pathlib import Path
from types import SimpleNamespace
import importlib.util,sys,json,hashlib,copy,uuid
from datetime import datetime,timezone,timedelta
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
p=ROOT/'experiments/contextual-supervision-20260927/cloud_control.py'
sp=importlib.util.spec_from_file_location('contextual_qa_controller',p);c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
scratch=(ROOT/'resources/local/contextual-integration-qa')/('controller-'+uuid.uuid4().hex);scratch.mkdir()
instant=datetime.now(timezone.utc);valid={'utc':instant.isoformat(),'balance_usd':'15.82','automatic_recharge_set':False}
c.check_admission(valid,instant)
for changed in [{'utc':(instant-timedelta(seconds=601)).isoformat()},{'utc':(instant+timedelta(seconds=1)).isoformat()},{'balance_usd':'NaN'},{'balance_usd':'Infinity'},{'balance_usd':'3.6250'},{'automatic_recharge_set':True}]:
    try:c.check_admission(valid|changed,instant)
    except (ValueError,ArithmeticError):pass
    else:raise AssertionError('Unsafe admission accepted: '+str(changed))
prefix='contextual-pilot/fixture';weight='contextual/training/control/adapter/adapter_model.safetensors'
manifest={'files':{'contextual/run.json':{'bytes':5,'sha256':'a'*64},weight:{'bytes':100,'sha256':'b'*64}}}
def entries_for(m):
    return {prefix+'/manifest.json':SimpleNamespace(size=100,xet_hash='manifest'),**{prefix+'/'+n:SimpleNamespace(size=e['bytes'],xet_hash='committed') for n,e in m['files'].items()}}
assert c.checked_files(manifest,entries_for(manifest),prefix)==['contextual/run.json']
for unsafe in ['../outside.json','/abs.json','a\\b.json','a:b.json','x/../y.json','unexpected.bin']:
    m=copy.deepcopy(manifest);m['files'][unsafe]={'bytes':1,'sha256':'c'*64}
    try:c.checked_files(m,entries_for(m),prefix)
    except ValueError:pass
    else:raise AssertionError('Unsafe path/type accepted: '+unsafe)
for mode in ['missing','extra','uncommitted','size']:
    e=entries_for(manifest)
    if mode=='missing':del e[prefix+'/'+weight]
    if mode=='extra':e[prefix+'/extra.json']=SimpleNamespace(size=1,xet_hash='x')
    if mode=='uncommitted':e[prefix+'/'+weight].xet_hash=None
    if mode=='size':e[prefix+'/'+weight].size+=1
    try:c.checked_files(manifest,e,prefix)
    except ValueError:pass
    else:raise AssertionError('Unsafe inventory accepted: '+mode)

def fixture():
    root=scratch/uuid.uuid4().hex;root.mkdir();exp=root/'experiment';exp.mkdir()
    c.LOCAL=root/'local';c.EXP=exp
    for name in c.REVIEWS:(exp/name).write_text('offline fixture review',encoding='utf-8')
    c.prepare();identity=c.read(c.LOCAL/'preparation.json')
    c.write(c.LOCAL/'admission.json',valid);c.write(exp/'input-transfer.json',{'sha256':identity['package_sha256'],'roundtrip_verified':True})
    return identity
def git(command,**kw):return b'' if command[1]=='status' else 'qa-fixed-commit\n'
class API:
    def __init__(self,ambiguous=False):self.posts=0;self.ambiguous=ambiguous;self.runid=None;self.job=None
    def whoami(self):return {'name':'Mojionix'}
    def list_jobs_hardware(self):return [SimpleNamespace(name='a100-large',unit_label='minute',unit_cost_micro_usd=41667)]
    def list_jobs(self,**kw):return [self.job] if kw.get('labels') else []
    def list_bucket_tree(self,*a,**kw):return []
    def run_job(self,**spec):
        self.posts+=1;self.runid=spec['labels']['trial_id'];self.job=SimpleNamespace(id='qa-owned-job',status=SimpleNamespace(stage='RUNNING'),labels={'trial_id':self.runid})
        if self.ambiguous:raise RuntimeError('Response lost after remote acceptance')
        return self.job
with patch.object(c.subprocess,'check_output',side_effect=git):
    fixture();api=API();c.launch(api);assert api.posts==1 and c.read(c.EXP/'execution.json')['job_id']==api.job.id
    try:c.launch(api)
    except (FileExistsError,ValueError):pass
    else:raise AssertionError('Repeated submission did not fail closed')
    assert api.posts==1
    fixture();api=API()
    with patch.object(c,'now',side_effect=[instant,instant+timedelta(seconds=601)]):
        try:c.launch(api)
        except ValueError:pass
        else:raise AssertionError('Admission expired during provider reads but was submitted')
    assert api.posts==0 and not (c.LOCAL/'submission-started.json').exists()
    fixture();api=API(ambiguous=True);stopped=[]
    with patch.object(c,'shutdown',side_effect=lambda api,jobs,*a,**kw:stopped.extend(j.id for j in jobs)):
        try:c.launch(api)
        except c.SubmissionFailed:pass
        else:raise AssertionError('Ambiguous submission swallowed')
    assert api.posts==1
    ambiguity_cleanup=stopped==['qa-owned-job']
    fixture();api=API();stopped=[];write=c.write
    def failed_record(path,value):
        if Path(path).name=='execution.json':raise OSError('injected local record failure')
        return write(path,value)
    with patch.object(c,'write',side_effect=failed_record),patch.object(c,'shutdown',side_effect=lambda api,jobs,*a,**kw:stopped.extend(j.id for j in jobs)):
        try:c.launch(api)
        except OSError:pass
        else:raise AssertionError('Local record failure swallowed')
    assert api.posts==1
    record_failure_cleanup=stopped==['qa-owned-job']
    # No execution.json exists after the injected write failure: stop must use trial identity.
    assert not (c.EXP/'execution.json').exists()
    foreign=SimpleNamespace(id='foreign-job',labels={'trial_id':'other'})
    api.list_jobs=lambda **kw:[api.job,foreign]
    stopped=[]
    with patch('huggingface_hub.HfApi',return_value=api),patch('huggingface_hub.set_client_factory'),patch.object(sys,'argv',['cloud_control.py','stop']),patch.object(c,'shutdown',side_effect=lambda api,jobs,*a,**kw:stopped.extend(j.id for j in jobs)):
        c.main()
    stop_identity_filter=stopped==['qa-owned-job']
summary={'status':'PASS' if ambiguity_cleanup and record_failure_cleanup and stop_identity_filter else 'FAIL','controller_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'admission_cases':7,'expired_during_provider_reads_zero_post':'PASS','inventory_negative_cases':10,'small_only_selection':'PASS','one_post_and_relaunch_rejected':'PASS','ambiguous_known_job_cleanup':ambiguity_cleanup,'post_submit_record_failure_cleanup':record_failure_cleanup,'stop_without_execution_exact_trial_only':stop_identity_filter}
(ROOT/'resources/local/contextual-integration-qa/controller-result.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary))
raise SystemExit(0 if summary['status']=='PASS' else 1)
