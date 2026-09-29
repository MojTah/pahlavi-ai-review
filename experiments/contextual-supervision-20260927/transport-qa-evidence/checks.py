"""Independent offline transport/controller checks; no real API clients or model work."""
from pathlib import Path
import ast, hashlib, importlib.util, io, json, sys, time, unittest, uuid
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from cloud_pilot import hf_contextual as job, test_hf_contextual as tests
SCRATCH = ROOT / 'resources/local/contextual-integration-qa/transport'
SCRATCH.mkdir(parents=True, exist_ok=True)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
before = json.loads((SCRATCH / 'before.json').read_text('utf-8'))
spec, identity = job.specification('e' * 32)
compiled = []
namespace = {'exec': compiled.append}
exec(spec['command'][3], namespace)
decoded = namespace['_contextual_code']
assert len(compiled) == 1
assert decoded == (SCRATCH / 'previous-generated.py').read_bytes()
assert hashlib.sha256(decoded).hexdigest() == before['command_sha256'] == identity['decoded_command_sha256']
assert identity['decoded_command_utf8_bytes'] == len(decoded) == 133680
for name, expected in before['source_hashes'].items():
    assert sha(ROOT / 'cloud_pilot' / name) == expected == identity['script_hashes'][name]
original, _ = job.hf_preflight.specification('cuda')
assert spec['command'][:3] == original['command'][:3]
assert spec['command'][4:] == original['command'][4:]
lengths = [len(a.encode('utf-8')) + 1 for a in spec['command']]
assert all(n < 100 * 1024 < 131072 for n in lengths)
assert sum(lengths) == identity['command_total_utf8_bytes_with_nul'] < 1024**2
assert [n - 1 for n in lengths] == identity['command_arg_utf8_bytes']
assert sha(ROOT/'cloud_pilot/hf_contextual.py') == 'c5630b5765eca339e917e52241c0ee133e0243c70c3a3ae08cf5cd852cbea2c8'
for bad in (["é" * 51200], ['a' * (100 * 1024 - 1)], ['a' * 100000] * 11):
    try: job.command_lengths(bad)
    except ValueError: pass
    else: raise AssertionError('Byte boundary not rejected')
job.command_lengths(['a' * (100 * 1024 - 2)])
native_exec = exec
try:
    native_exec(spec['command'][3].replace(identity['decoded_command_sha256'], '0' * 64), {'exec': lambda *a: (_ for _ in ()).throw(AssertionError('executed'))})
except ValueError: pass
else: raise AssertionError('Tampered checksum accepted')

def scratch(self):
    out = SCRATCH / ('wrapper-' + uuid.uuid4().hex)
    out.mkdir()
    return out
stream = io.StringIO()
start = time.monotonic()
with patch.object(tests.ContextualJobTests, 'scratch', scratch):
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(tests.ContextualJobTests))
wrapper_seconds = round(time.monotonic() - start, 3)
(SCRATCH / 'wrapper-tests.txt').write_text(stream.getvalue(), encoding='utf-8')
assert result.wasSuccessful(), stream.getvalue()

controller_path = ROOT / 'experiments/contextual-supervision-20260927/cloud_control.py'
def controller():
    module_spec = importlib.util.spec_from_file_location('transport_controller_' + uuid.uuid4().hex, controller_path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    folder = SCRATCH / ('attempt-' + uuid.uuid4().hex)
    folder.mkdir()
    module.ROOT = folder
    module.EXP = folder / 'experiment'
    module.EXP.mkdir()
    module.RESULTS = module.EXP
    module.LOCAL = folder / 'original-local'
    return module

default = controller()
with patch.object(default, 'prepare') as prepared, patch.object(sys, 'argv', ['control', 'prepare']):
    default.main()
    prepared.assert_called_once()
assert default.RESULTS == default.EXP and default.LOCAL.name == 'original-local'
assert len(default.REVIEWS) == 3

allowed = {'status': 'ERROR', 'bootstrap_started': False, 'training_started': False}
rejected = 0
for changed in ({'status':'RUNNING'}, {'status':'COMPLETED'}, {'bootstrap_started':True}, {'training_started':True}, {'bootstrap_started':0}, {'training_started':None}):
    c = controller()
    (c.EXP / 'startup-failure.json').write_text(json.dumps(allowed | changed))
    with patch.object(c, 'prepare') as prepared, patch.object(sys, 'argv', ['control', 'prepare', '--attempt', '2']), patch('huggingface_hub.HfApi.__init__', side_effect=AssertionError('No API')):
        try: c.main()
        except ValueError: rejected += 1
        else: raise AssertionError('Ineligible attempt2 accepted')
        prepared.assert_not_called()

c = controller()
(c.EXP/'startup-failure.json').write_text(json.dumps(allowed))
(c.EXP/'execution.json').write_text('preserved original execution')
original_hash = sha(c.EXP/'execution.json')
with patch.object(c, 'prepare') as prepared, patch.object(sys, 'argv', ['control', 'prepare', '--attempt', '2']):
    c.main()
    prepared.assert_called_once()
assert c.RESULTS == c.EXP / 'attempt-2'
assert c.LOCAL == c.ROOT / 'resources/local/hf-contextual-run-20260927-attempt-2'
assert c.REVIEWS[-2:] == ('TRANSPORT-REPAIR-QA.md', 'TRANSPORT-REPAIR-JUDGE.md')
c.LOCAL.parent.mkdir(parents=True)
for name in c.REVIEWS: (c.EXP/name).write_text('offline review fixture')
with patch.object(c.subprocess, 'check_output', return_value='offline-commit\n'):
    c.prepare()
    prepared = c.read(c.LOCAL/'preparation.json')
    saved = c.read(c.LOCAL/'spec.json')
    regenerated, current = job.specification(prepared['run_id'])
    assert saved == dict(regenerated, volumes=[v.to_dict() for v in regenerated['volumes']])
    assert all(prepared[k] == v for k, v in current.items())
    assert prepared['controller_sha256'] == sha(controller_path)
    assert set(prepared['review_sha256']) == set(c.REVIEWS)
    try: c.prepare()
    except FileExistsError: pass
    else: raise AssertionError('Existing attempt2 preparation overwritten')
c.write(c.RESULTS/'execution.json', {'fixture': 'attempt2'})
try: c.write(c.RESULTS/'execution.json', {'fixture': 'overwrite'})
except FileExistsError: pass
else: raise AssertionError('Existing execution overwritten')
assert sha(c.EXP/'execution.json') == original_hash

summary = dict(status='PASS', wrapper_tests=result.testsRun, wrapper_seconds=wrapper_seconds,
    wrapper_sha256=sha(ROOT/'cloud_pilot/hf_contextual.py'), test_sha256=sha(ROOT/'cloud_pilot/test_hf_contextual.py'),
    controller_sha256=sha(controller_path), decoded_equals_preserved_original=True,
    decoded_sha256=identity['decoded_command_sha256'], transport_sha256=identity['command_sha256'],
    decoded_bytes=len(decoded), argument_bytes_including_nul=lengths, total_argument_bytes_including_nul=sum(lengths),
    utf8_and_nul_boundary_rejections=True, checksum_tamper_rejected_before_exec=True,
    unchanged_scientific_sources=before['source_hashes'], default_attempt1_preserved=True,
    rejected_attempt2_conditions=rejected, attempt2_paths_and_review_bindings=True,
    attempt2_exact_spec_regeneration=True, attempt2_exclusive_prepare_and_execution=True,
    original_execution_unchanged=True, network_cloud_credentials_models=False)
(SCRATCH/'result.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
print(json.dumps(summary, indent=2))
