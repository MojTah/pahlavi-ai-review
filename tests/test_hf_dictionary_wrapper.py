"""Local SDK and lifecycle checks; no provider calls, GPU, weights or secrets."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
from contextlib import contextmanager
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'resources/local/hf-client-venv/Lib/site-packages'))
from cloud_pilot import hf_component as hf
from cloud_pilot.training_admission import sdk_spec

INPUTS = ROOT/'resources/local/dev-comparability-20261003/ab-inputs.jsonl'

@contextmanager
def owned_directory():
    # Normal inherited workspace ACLs. Keep test evidence; no recursive cleanup.
    folder=ROOT/'resources/local'/('dictionary-wrapper-check-'+uuid.uuid4().hex)
    folder.mkdir()
    yield folder


class WrapperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec,cls.receipt = hf.prepare(INPUTS,run_id='e'*32,protocol='dictionary-ab-v1')

    def test_actual_sdk_and_self_contained_command(self):
        restored=sdk_spec(json.loads(json.dumps(self.spec,default=lambda x:x.to_dict())))
        self.assertEqual(restored['timeout'],'120m')
        self.assertEqual([v.read_only for v in restored['volumes']],[True,True,False])
        command=ast.parse(restored['command'][3])
        payload=ast.literal_eval(command.body[1].value.args[0].args[0])
        import gzip,base64
        code=gzip.decompress(base64.b64decode(payload)).decode()
        self.assertEqual(hashlib.sha256(code.encode()).hexdigest(),self.receipt['decoded_command_sha256'])
        tree=ast.parse(code)
        # Definitions, embedded settings and scripts execute; intercept only the
        # final execute call. No cloud action is present in the decoded program.
        namespace={}
        exec(compile(ast.Module(body=tree.body[:-1],type_ignores=[]),'prepared','exec'),namespace)
        self.assertEqual(namespace['dictionary_schedule'](),hf.dictionary_schedule())
        self.assertEqual(namespace['dictionary_controls'](),hf.dictionary_controls())
        self.assertEqual(ast.literal_eval(tree.body[-1].value.args[0])['native_timeout_minutes'],120)

    def test_pin_refuses_any_input_change(self):
        with owned_directory() as directory:
            path=Path(directory)/'inputs.jsonl';path.write_bytes(INPUTS.read_bytes()+b'\n')
            with self.assertRaises(ValueError):
                hf.prepare(path,run_id='e'*32,protocol='dictionary-ab-v1')

    def lifecycle(self,kind):
        with owned_directory() as directory:
            root=Path(directory);mount=root/'mount';incoming=root/'input';stage=root/'stage'
            incoming.mkdir();stage.mkdir()
            (incoming/self.receipt['inputs_name']).write_bytes(INPUTS.read_bytes())
            settings=copy.deepcopy(self.receipt)
            settings['bootstrap_hashes']={'runtime.py':hashlib.sha256(b'bootstrap').hexdigest()}
            clock=[1000.0];sleeps=[];alarms=[]
            def mapped(value):
                return mount if value=='/output' else incoming if value=='/input' else Path(value)
            def extract(source,dest,*args):
                dest.mkdir();(dest/'runtime.py').write_bytes(b'bootstrap')
            def body(settings,stage,deadline,evidence):
                self.assertEqual(deadline,7600.0)
                if kind=='bootstrap':raise RuntimeError('bootstrap failure')
                (evidence/'observed.txt').write_text('small recovered evidence')
                clock[0] += 6500 if kind=='late' else 100
                if kind=='child':raise TimeoutError('child safely stopped')
            actual_publish=hf.publish_checked
            def publish(source,dest,deadline,identity):
                self.assertEqual(deadline,7960.0)
                if kind=='export':raise TimeoutError('export deadline')
                result=actual_publish(source,dest,deadline,identity)
                if kind=='corrupt':
                    raise AssertionError('Corruption must be injected before actual readback')
                return result
            def sleep(seconds):sleeps.append(seconds);clock[0]+=seconds
            with patch.object(hf,'Path',side_effect=mapped),patch.object(hf.tempfile,'mkdtemp',return_value=str(stage)),\
                 patch.object(hf,'safe_extract',side_effect=extract),patch.object(hf,'component_body',side_effect=body),\
                 patch.object(hf,'publish_checked',side_effect=publish),patch.object(hf.shutil if hasattr(hf,'shutil') else __import__('shutil'),'disk_usage',return_value=types.SimpleNamespace(free=100*1024**3)),\
                 patch.object(hf.time,'monotonic',side_effect=lambda:clock[0]),patch.object(hf.time,'sleep',side_effect=sleep),\
                 patch.object(hf.signal,'SIGALRM',14,create=True),patch.object(hf.signal,'signal'),\
                 patch.object(hf.signal,'alarm',side_effect=lambda n:alarms.append(n),create=True),patch.object(hf,'emit'),\
                 patch.object(hf.hf_baseline,'emit'):
                try:
                    if kind=='corrupt':
                        original_hash=hf.file_sha256
                        def changed_hash(path):
                            return 'f'*64 if Path(path).is_relative_to(mount/'final') else original_hash(path)
                        # First publication uses the original helper's hashes;
                        # wrapper readback observes mismatched mounted bytes.
                        with patch.object(hf,'file_sha256',side_effect=changed_hash):
                            hf.execute(settings,{},'')
                    else:
                        hf.execute(settings,{},"raise RuntimeError('bootstrap failure')" if kind=='bootstrap' else '')
                except (RuntimeError,TimeoutError,ValueError) as error:
                    caught=error
                else:caught=None
            if kind in ('normal','late'):self.assertIsNone(caught)
            else:self.assertIsNotNone(caught)
            self.assertEqual(alarms[-1],0)
            if kind in ('normal','bootstrap','child','late'):
                self.assertEqual(sleeps,[60])
                self.assertEqual(alarms[-1],0)
                closed=json.loads((mount/'final/manifest.json').read_bytes())
                self.assertFalse(closed['remote_inventory_verified'])
                self.assertFalse(closed['training_performed'])
                self.assertEqual(closed['optimizer_updates'],0)
            return caught,alarms

    def test_normal_and_failure_full_export_lifecycle(self):
        for kind in ('normal','bootstrap','child','late','export','corrupt'):
            with self.subTest(kind=kind):self.lifecycle(kind)

    def test_invalid_timing_rejected_before_any_signal_or_mount(self):
        for field,value in (('compute_seconds',6601),('internal_seconds',7200),('native_timeout_minutes',60),
                ('compute_seconds',6600.0),('inputs_sha256','f'*64),('reviewed_specimen_sha256','f'*64),
                ('precision','nf4'),('training',True),('automatic_retry',True),('planned_outputs',True),
                ('schedule',hf.dictionary_schedule()[::-1])):
            bad=copy.deepcopy(self.receipt);bad[field]=value
            with patch.object(hf.signal,'signal') as signal:
                with self.assertRaises(ValueError):hf.execute(bad,{},'')
                signal.assert_not_called()

    def test_complete_interrupted_and_corrupted_fixed_denominator_recovery(self):
        original={r['id']:r for r in map(json.loads,INPUTS.read_bytes().splitlines())}
        order=hf.dictionary_schedule()
        rows=[]
        for i,key in enumerate(order):
            r=original[key]
            rows.append(dict(id=key,case_id=r['case_id'],condition=r['arm'],arm=r['arm'],
                work_id=r['work_id'],source_sha256=r['source_sha256'],sequence=i+1,status='success',
                identity_sha256='0'*64,model_call_started=True,text='mock output',
                output_sha256=hashlib.sha256(b'mock output').hexdigest(),output_tokens=2,output_token_ids=[7,1],
                hit_output_cap_without_eos=False,stop_reason=None,messages=r['messages'],
                messages_sha256=hashlib.sha256(json.dumps(r['messages'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
                input_tokens=r['input_tokens'],rendered_input_ids_sha256=r['input_ids_sha256'],rendered_sha256=r['rendered_text_sha256']))
        state=dict(self.receipt,identity_sha256='0'*64,status='completed',scheduled_outputs=30,
            attempted_outputs=30,recorded_outputs=30,model_calls_started=30,active_output_id=None,
            unattempted_output_ids=[],adapter_unchanged_after_inference=True)
        with owned_directory() as directory:
            root=Path(directory);output=root/'evaluation';output.mkdir()
            (root/'model-inputs.jsonl').write_bytes(INPUTS.read_bytes())
            def save(current,records):
                (output/'run.json').write_text(json.dumps(current),encoding='utf8')
                (output/'predictions.jsonl').write_bytes(b''.join((json.dumps(r,ensure_ascii=False)+'\n').encode() for r in records))
            save(state,rows)
            self.assertTrue(hf.reconcile(output,order)['pipeline_complete'])
            for mutation in ('empty','output_bool','dispatch','inputhash','work','message','stop','cap','tail'):
                bad=copy.deepcopy(rows)
                if mutation=='empty':bad[0].update(text='',output_sha256=hashlib.sha256(b'').hexdigest())
                if mutation=='output_bool':bad[0].update(output_tokens=True,output_token_ids=[1])
                if mutation=='dispatch':bad[0]['model_call_started']=False
                if mutation=='inputhash':bad[0]['rendered_input_ids_sha256']='f'*64
                if mutation=='work':bad[0]['work_id']='parsig:517'
                if mutation=='message':bad[0]['messages'][0]['content']+='changed'
                if mutation=='stop':bad[0]['stop_reason']='case_timeout'
                if mutation=='cap':bad[0]['hit_output_cap_without_eos']=True
                save(state,bad)
                if mutation=='tail':
                    with (output/'predictions.jsonl').open('ab') as stream:stream.write(b'{partial')
                with self.subTest(mutation=mutation),self.assertRaises(ValueError):hf.reconcile(output,order)
            interrupted=dict(state,status='running',attempted_outputs=4,recorded_outputs=3,
                model_calls_started=4,active_output_id=order[3],unattempted_output_ids=order[4:])
            save(interrupted,rows[:3])
            accounted=hf.reconcile(output,order)
            self.assertEqual(len(accounted['per_output_status']),30)
            self.assertEqual(accounted['per_output_status'][order[3]],'interrupted_output_unknown')
            self.assertEqual(sum(s=='unattempted' for s in accounted['per_output_status'].values()),26)
            self.assertFalse(accounted['pipeline_complete'])
            # Durable JSONL may be ahead of run.json by one commit; never retry.
            save(interrupted,rows[:4])
            self.assertFalse(hf.reconcile(output,order)['pipeline_complete'])


if __name__=='__main__':unittest.main()
