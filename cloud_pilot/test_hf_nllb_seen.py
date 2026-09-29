"""Local exact-package and lifecycle failure checks; no service or credentials."""
import ast
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid

ROOT=Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT/'resources/local/hf-client-venv/Lib/site-packages'))
from cloud_pilot import hf_nllb_seen as p


class SeenLifecycleChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=ROOT/'experiments/nllb-seen-20260928/control.py'
        spec=importlib.util.spec_from_file_location('seen_control_checks',path)
        cls.control=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.control)

    def fresh(self):
        path=ROOT/'resources/local/nllb-seen-hf-tests'/uuid.uuid4().hex
        path.mkdir(parents=True)
        return path

    def test_exact_prepared_package_and_spec(self):
        archive=p.LOCAL/'package.zip'
        manifest=json.loads((p.LOCAL/'package-manifest.json').read_bytes())
        digest=p.file_sha256(p.LOCAL/'package-manifest.json')
        stage=self.fresh()
        p.safe_extract(archive,stage/'package',p.file_sha256(archive),128*1024**2)
        checked=p.verify_package(stage/'package',{'package_manifest_sha256':digest})
        self.assertEqual(checked,manifest)
        self.assertEqual((manifest['scored_forwards'],manifest['generations']),(40,20))
        for name in ('nllb_seen.py','nllb_train.py'):
            self.assertEqual(p.file_sha256(ROOT/'cloud_pilot'/name),manifest['files'][name]['sha256'])
        token_map=json.loads((stage/'package/token-map.json').read_bytes())
        self.assertEqual(len(token_map['rows']),20)
        self.assertEqual(len({r['work_id'] for r in token_map['rows']}),16)
        # Exact prepared bytes already underwent real token-map construction; do not retokenize them here.
        with patch.object(p,'package',return_value=(archive,manifest,digest)):
            spec,identity=p.specification('f'*32)
        self.assertEqual(spec['timeout'],'15m')
        self.assertEqual((identity['compute_seconds'],identity['internal_seconds']),(600,780))
        self.assertEqual([(v.mount_path,v.read_only) for v in spec['volumes']],
                         [('/input',True),('/trained',True),('/output',False)])
        self.assertLess(max(len(c.encode()) for c in spec['command']),100*1024)
        (stage/'package/inputs.jsonl').write_text('changed',encoding='utf-8')
        with self.assertRaises(ValueError): p.verify_package(stage/'package',identity)

    def test_small_only_recovery_and_exact_copy(self):
        prefix='nllb-seen/test'
        manifest={'files':{'status.json':{'bytes':2,'sha256':'a'*64}}}
        entries={prefix+'/manifest.json':SimpleNamespace(size=100,xet_hash='ready'),
                 prefix+'/status.json':SimpleNamespace(size=2,xet_hash='ready')}
        self.assertEqual(self.control.checked_files(manifest,entries,prefix),['status.json'])
        bad={'files':{'seen/model.safetensors':{'bytes':2,'sha256':'a'*64}}}
        with self.assertRaises(ValueError): self.control.checked_files(bad,entries,prefix)
        entries[prefix+'/status.json'].xet_hash=None
        with self.assertRaises(ValueError): self.control.checked_files(manifest,entries,prefix)
        stage=self.fresh();source=stage/'cloud';(source/'nllb/model').mkdir(parents=True)
        model=dict(run_id='model',completed_steps=700,nllb_status='complete',model='model-name',revision='rev',files={})
        for name in p.INFERENCE_NAMES:
            file=source/'nllb/model'/name;file.write_bytes(name.encode())
            model['files']['nllb/model/'+name]={'bytes':file.stat().st_size,'sha256':p.file_sha256(file)}
        (source/'nllb/model/optimizer.pt').write_bytes(b'must not be copied')
        (source/'manifest.json').write_text(json.dumps(model),encoding='utf-8')
        settings=dict(model_manifest_sha256=p.file_sha256(source/'manifest.json'),model_run_id='model',
            model='model-name',revision='rev',inference_names=list(p.INFERENCE_NAMES))
        import time
        p.copy_inference(source,stage/'inference',settings,time.monotonic()+300)
        self.assertEqual({f.name for f in (stage/'inference').iterdir()},set(p.INFERENCE_NAMES))
        (source/'nllb/model/tokenizer.json').write_bytes(b'wrong bytes')
        with self.assertRaises(ValueError): p.copy_inference(source,stage/'invalid',settings,time.monotonic()+300)

    def test_completed_schedule_keeps_caps_and_rejects_wrong_source(self):
        import contextlib
        import io
        import time
        from cloud_pilot import nllb_seen
        package=p.LOCAL/'package-staging'
        rows=json.loads((package/'token-map.json').read_bytes())['rows']
        output=self.fresh()
        state=dict(training_performed=False,optimizer_updates=0,model_manifest_sha256=p.MODEL_MANIFEST_SHA,
            token_map_sha256=p.TOKEN_MAP_SHA,runner_sha256=p.file_sha256(package/'nllb_seen.py'))
        with contextlib.redirect_stdout(io.StringIO()):
            nllb_seen.execute(rows,output,state,time.monotonic()+300,
                lambda target,source:{'mean_nll':1.0},
                lambda source:nllb_seen.generation_result([2,256053]+[9]*511,'retained capped text'))
        settings=dict(model_manifest_sha256=p.MODEL_MANIFEST_SHA,token_map_sha256=p.TOKEN_MAP_SHA)
        result=p.completed_seen(output,package,settings)
        self.assertEqual(result['status'],'completed')
        self.assertEqual(result['generation_failures'],20)
        path=output/'likelihood.jsonl'
        records=[json.loads(x) for x in path.read_text(encoding='utf-8').splitlines()]
        records[0]['input_sha256']='b'*64
        path.write_text('\n'.join(json.dumps(x) for x in records)+'\n',encoding='utf-8')
        with self.assertRaises(ValueError): p.completed_seen(output,package,settings)

    def test_ambiguous_launch_record_failure_still_shuts_down(self):
        tree=ast.parse(Path(self.control.__file__).read_text(encoding='utf-8'))
        function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='launch')
        identity=dict(run_id='c'*32,spec_sha256='hash',controller_sha256='hash',review_sha256='hash',
            source_commit='commit',package_sha256='package',output_prefix='prefix',command_sha256='command')
        spec={'volumes':[],'timeout':'15m'};stopped=[]
        class Ambiguous(Exception):
            jobs=[SimpleNamespace(id='owned-job')]
        def submit(*args): raise Ambiguous()
        def write(path,record):
            if path.name=='submission-unconfirmed.json': raise OSError('injected record failure')
        def read(path):
            return {'preparation.json':identity,'spec.json':spec,'input-transfer.json':
                {'sha256':'package','roundtrip_verified':True},'admission.json':{}}[path.name]
        scope=dict(pilot=SimpleNamespace(specification=lambda *a,**k:(spec,{})),PHASE='seen',
            LOCAL=Path('local'),EXP=Path('exp'),ROOT=Path('root'),RESULTS=Path('results'),__file__='control.py',
            read=read,sha=lambda p:'hash',subprocess=SimpleNamespace(check_output=lambda args,**kw:'commit' if 'rev-parse' in args else b''),
            check_admission=lambda *a:None,now=lambda:datetime.now(timezone.utc),checked_hardware=lambda h:None,
            TERMINAL={'COMPLETED'},BUCKET='bucket',RESERVATION='3.208353',write=write,submit_once=submit,
            emit=lambda **kw:None,SubmissionFailed=Ambiguous,shutdown=lambda *a:stopped.append(True),
            time=SimpleNamespace(monotonic=lambda:0))
        api=SimpleNamespace(whoami=lambda:{'name':'Mojionix'},list_jobs_hardware=lambda:[SimpleNamespace(name='a100-large')],
            list_jobs=lambda **kw:[],list_bucket_tree=lambda *a,**kw:[])
        exec(compile(ast.Module(body=[function],type_ignores=[]),'actual-launch','exec'),scope)
        with self.assertRaises(OSError):scope['launch'](api)
        self.assertEqual(stopped,[True])


if __name__=='__main__': unittest.main()
