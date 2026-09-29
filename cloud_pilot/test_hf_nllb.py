"""Exact package and failure-boundary checks; fake service, no account access."""
import ast
from datetime import datetime,timezone,timedelta
import importlib.util
import contextlib
import inspect
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
import uuid

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.append(str(ROOT/'resources/local/hf-client-venv/Lib/site-packages'))
from cloud_pilot import hf_nllb as p


class HfNllbChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=ROOT/'experiments/nllb-supervised-20260928/cloud_control.py'
        spec=importlib.util.spec_from_file_location('nllb_control_check',path)
        cls.control=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.control)

    def fresh(self):
        path=ROOT/'resources/local/nllb-hf-tests'/uuid.uuid4().hex
        path.mkdir(parents=True)
        return path

    def test_exact_package_and_host_arguments(self):
        spec,identity=p.specification('b'*32)
        stage=self.fresh()
        p.safe_extract(p.LOCAL/'package.zip',stage/'package',identity['package_sha256'],128*1024**2)
        manifest=p.verify_package(stage/'package',identity)
        self.assertEqual(manifest['training_rows'],2237)
        self.assertEqual(spec['timeout'],'20m')
        self.assertLess(max(map(lambda s:len(s.encode()),spec['command'])),100*1024)
        from transformers import AutoTokenizer
        from cloud_pilot.nllb_train import token_rows
        tokenizer=AutoTokenizer.from_pretrained(stage/'package/tokenizer',local_files_only=True,token=False,
            trust_remote_code=False,src_lang='pal_Latn',tgt_lang='pes_Arab')
        train,tokens,dev=token_rows(stage/'package',tokenizer)
        self.assertEqual((len(train),len(tokens),len(dev)),(2237,2237,24))
        (stage/'package/config.json').write_text('{}')
        with self.assertRaises(ValueError): p.verify_package(stage/'package',identity)

    def test_valid_canary_survives_partial_final(self):
        stage=self.fresh()
        evidence=stage/'evidence'
        evidence.mkdir()
        (stage/'final-state').mkdir()
        (stage/'final-state/half-written.safetensors').write_bytes(b'partial')
        folder=stage/'canary-state'
        folder.mkdir()
        (folder/'model.safetensors').write_bytes(b'closed fake weights')
        (folder/'training-state.json').write_text('{"step":20}')
        record={'step':20,'reload_and_generation_verified':True,'files':{
            f.name:{'bytes':f.stat().st_size,'sha256':p.file_sha256(f)} for f in folder.iterdir()}}
        (folder/'checkpoint-verified.json').write_text(json.dumps(record))
        self.assertEqual(p.retain_verified_checkpoint(stage,evidence),20)
        self.assertTrue((evidence/'nllb/model/model.safetensors').exists())
        self.assertTrue((stage/'final-state/half-written.safetensors').exists())
        stage=self.fresh()
        (stage/'canary-state').mkdir()
        (stage/'canary-state/partial').write_bytes(b'partial')
        self.assertIsNone(p.retain_verified_checkpoint(stage,stage/'evidence'))
        self.assertFalse((stage/'evidence/nllb/model').exists())

    def test_budget_age_and_finite_values(self):
        now=datetime.now(timezone.utc)
        record=dict(utc=now.isoformat(),balance_usd=13.70,period_usage_usd=16.61,
                    automatic_recharge_set=False,rate_micro_usd_per_minute=41667)
        self.control.check_admission(record,now)
        for key,value in [('balance_usd',2),('balance_usd','NaN'),('period_usage_usd',23),
                          ('automatic_recharge_set',True),('utc',(now-timedelta(minutes=16)).isoformat())]:
            with self.assertRaises(ValueError): self.control.check_admission(dict(record,**{key:value}),now)

    def test_actual_wrapper_start_event(self):
        tree=ast.parse(inspect.getsource(p.execute_nllb))
        call=next(n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)
                  and n.func.id=='emit' and n.args and isinstance(n.args[0],ast.Constant)
                  and n.args[0].value=='nllb_started')
        stream=io.StringIO()
        with contextlib.redirect_stdout(stream):
            eval(compile(ast.Expression(call),'actual-start-event','eval'),
                 {'emit':p.emit,'settings':{'phase':'canary'}})
        self.assertEqual(json.loads(stream.getvalue())['run_phase'],'canary')

    def test_closed_canary_continuation_bound(self):
        source=self.control.continuation_source()
        self.assertEqual((source['closed_minutes'],source['native_minutes']),(9,50))
        spec,identity=p.specification('d'*32,phase='continue',canary=source)
        self.assertEqual((spec['timeout'],identity['compute_seconds'],identity['internal_seconds']),('50m',2520,2880))
        first=json.loads((p.LOCAL/'canary/preparation.json').read_bytes())
        self.assertEqual(identity['package_sha256'],first['package_sha256'])
        path=p.EXP/'canary'
        terminal=json.loads((path/'termination.json').read_bytes())
        execution=json.loads((path/'execution.json').read_bytes())
        recovery=json.loads((path/'recovery.json').read_bytes())
        for key,value in [('job_id','wrong'),('terminal_stage','RUNNING'),('rounded_minutes_upper',8),
                          ('elapsed_seconds_upper',0),('terminal_utc',execution['submitted_utc'])]:
            with self.assertRaises(ValueError): self.control.closed_minutes(dict(terminal,**{key:value}),execution,recovery)
        with self.assertRaises(ValueError): p.specification('d'*32,phase='continue',canary=dict(source,native_minutes=51))

    def test_ambiguous_submit_still_stops_when_record_write_fails(self):
        tree=ast.parse(Path(self.control.__file__).read_text())
        function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='launch')
        identity=dict(run_id='c'*32,spec_sha256='hash',controller_sha256='hash',review_sha256='hash',
                      source_commit='commit',package_sha256='package',output_prefix='prefix',command_sha256='command')
        spec={'volumes':[],'timeout':'20m'}
        stopped=[]
        class Ambiguous(Exception):
            jobs=[SimpleNamespace(id='known-owned-job')]
        def submit(*args): raise Ambiguous()
        def write(path,record):
            if path.name=='submission-unconfirmed.json': raise OSError('injected record write failure')
        def read(path):
            return {'preparation.json':identity,'spec.json':spec,'input-transfer.json':
                    {'sha256':'package','roundtrip_verified':True},'admission.json':{}}[path.name]
        scope=dict(pilot=SimpleNamespace(specification=lambda *a,**k:(spec,{})),PHASE='canary',
            LOCAL=Path('local'),EXP=Path('exp'),ROOT=Path('root'),RESULTS=Path('results'),__file__='control.py',
            read=read,sha=lambda p:'hash',subprocess=SimpleNamespace(check_output=lambda args,**kw:'commit' if 'rev-parse' in args else b''),
            check_admission=lambda *args:None,now=lambda:datetime.now(timezone.utc),checked_hardware=lambda x:None,
            TERMINAL={'COMPLETED'},BUCKET='bucket',RESERVATION='2.958351',write=write,submit_once=submit,
            emit=lambda **kw:None,SubmissionFailed=Ambiguous,shutdown=lambda *args:stopped.append(True),
            time=SimpleNamespace(monotonic=lambda:0))
        exec(compile(ast.Module(body=[function],type_ignores=[]),'actual-launch','exec'),scope)
        api=SimpleNamespace(whoami=lambda:{'name':'Mojionix'},list_jobs_hardware=lambda:[SimpleNamespace(name='a100-large')],
                            list_jobs=lambda **kw:[],list_bucket_tree=lambda *a,**kw:[])
        with self.assertRaises(OSError): scope['launch'](api)
        self.assertEqual(stopped,[True])


if __name__=='__main__': unittest.main()
