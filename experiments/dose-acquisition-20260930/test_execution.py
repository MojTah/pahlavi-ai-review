"""No-network funding/idle-job and immutable staging checks."""
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid
import execute as launch


@dataclass
class Hardware:
    name: str = 'a100-large'
    unit_label: str = 'minute'
    unit_cost_usd: float = 0.041667


class Checks(unittest.TestCase):
    def setUp(self):
        self.root = launch.ROOT/'resources/local/dose-execution-tests'/uuid.uuid4().hex
        self.root.mkdir(parents=True)
        (self.root/'funding.json').write_text(json.dumps(dict(utc=datetime.now(timezone.utc).isoformat(),
            credit_usd='26.28',automatic_recharge=False)))

    def test_funding_price_private_idle_guards(self):
        api = SimpleNamespace(whoami=lambda:{'name':'Mojionix'},bucket_info=lambda b:SimpleNamespace(private=True),
            list_jobs_hardware=lambda:[Hardware()],list_jobs=lambda **k:[],list_bucket_tree=lambda *a,**k:[])
        prep = dict(native_timeout_minutes=360,run_id='x',output_prefix='dose/x')
        with patch.object(launch,'LIVE',self.root):
            result = launch.live_check(api,{'flavor':'a100-large'},prep)
            self.assertEqual(result['compute_ceiling_usd'],'15.000120')
            api.list_jobs_hardware=lambda:[Hardware(unit_cost_usd=0.1)]
            with self.assertRaises(ValueError): launch.live_check(api,{'flavor':'a100-large'},prep)
            api.list_jobs_hardware=lambda:[Hardware()]
            api.list_jobs=lambda **k:[SimpleNamespace(status=SimpleNamespace(stage='RUNNING'),labels={})]
            with self.assertRaises(ValueError): launch.live_check(api,{'flavor':'a100-large'},prep)
            api.list_jobs=lambda **k:[]
            api.bucket_info=lambda b:SimpleNamespace(private=False)
            with self.assertRaises(ValueError): launch.live_check(api,{'flavor':'a100-large'},prep)

    def test_existing_remote_conflict_stops_before_upload(self):
        here, admission = self.root/'experiment',self.root/'admission'
        here.mkdir(); admission.mkdir()
        sources = [(here/'inputs.jsonl', 'inputs/i'),
            (self.root/'resources/local/training-ready-v2-20260929/data/train.jsonl','inputs/t'),
            (self.root/'experiments/training-ready-v2-20260929/data-manifest.json','inputs/m'),
            (self.root/'resources/local/b.zip','inputs/b.zip')]
        contents = {}
        for p,key in sources:
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes(b'correct')
            contents[key]=b'correct'
        config=b'{}'; weight=b'never-download-weights'
        sha=launch.prepare.sha
        metadata={'files':{'training/adapter/adapter_config.json':{'bytes':len(config),'sha256':sha(config)},
                           'training/adapter/adapter_model.safetensors':{'bytes':len(weight),'sha256':sha(weight)}}}
        manifest=json.dumps(metadata).encode()
        contents.update({'ref/manifest.json':manifest,'ref/training/adapter/adapter_config.json':config,
                         'ref/training/adapter/adapter_model.safetensors':weight})
        contents['inputs/i']=b'corrupt'  # Same size as local: hash readback must catch it.
        remote={key:SimpleNamespace(path=key,size=len(raw)) for key,raw in contents.items()}
        downloads=[]; uploads=[]
        def download(bucket,pairs,**kwargs):
            for item,path in pairs:
                key=item.path if hasattr(item,'path') else item
                downloads.append(key)
                Path(path).write_bytes(contents[key])
        api=SimpleNamespace(get_bucket_paths_info=lambda b,p:[remote[k] for k in p if k in remote],
            download_bucket_files=download,batch_bucket_files=lambda *a,**k:uploads.append(k))
        prep=dict(training_admission={'job_sha256':'x'},run_id='y',trained_prefix='ref',
            inputs_name='i',train_name='t',data_manifest_name='m',bundle_name='b.zip',
            trained_manifest_sha256=sha(manifest),reference_adapter_files={'adapter_config.json':sha(config)},
            adapter_files={k:v['sha256'] for k,v in metadata['files'].items()})
        with patch.object(launch,'ROOT',self.root),patch.object(launch,'HERE',here),patch.object(launch,'EVIDENCE',admission):
            with self.assertRaisesRegex(ValueError,'Existing remote hash differs'):
                launch.stage(api,prep)
        self.assertEqual(uploads,[])
        self.assertFalse(any(k.endswith('.safetensors') for k in downloads))


if __name__ == '__main__': unittest.main()
