"""Independent synthetic converter QA; no actual predictions, ratings or cloud access."""
from pathlib import Path
import copy, hashlib, io, json, os, sys, time, unittest

ROOT = Path(__file__).resolve().parents[3]
SCRATCH = ROOT / 'resources/local/contextual-review-qa'
SCRATCH.mkdir(parents=True, exist_ok=True)
os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_HUB_DISABLE_TELEMETRY='1', HF_HOME=str(SCRATCH/'hf-cache'))
sys.path[:0] = [str(ROOT), str(ROOT/'resources/local/train-fit-deps'), str(ROOT/'resources/local/hf-client-venv/Lib/site-packages')]
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
SOURCES = ['scripts/review_contextual.py', 'scripts/test_review_contextual.py', 'scripts/score_blind_dev_assisted.py']
before = {n: sha(ROOT/n) for n in SOURCES}
from scripts import test_review_contextual as test
test.SCRATCH = SCRATCH
os.environ['HF_HOME'] = str(SCRATCH/'hf-cache')
mod = test.mod
stream = io.StringIO()
started = time.monotonic()
suite = unittest.defaultTestLoader.loadTestsFromTestCase(test.ContextualReviewTest)
result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
elapsed = round(time.monotonic()-started, 3)
(SCRATCH/'tests.txt').write_text(stream.getvalue(), encoding='utf-8')
assert result.wasSuccessful(), stream.getvalue()

cls = test.ContextualReviewTest
base = {}
for row in cls.rows:
    assessment = cls.assessments[row['id']]['assessment']
    base[row['id']] = dict(case_id=row['id'], work_id=row['work_id'], assessment=assessment,
        execution_status='success', judgment='accepted' if assessment=='provisional_whole_translation' else 'constrained_only',
        supported_span_severity='none', unknown_span_handling='no_unknown_span')
whole = [cid for cid in base if base[cid]['assessment']=='provisional_whole_translation']
works = sorted({base[cid]['work_id'] for cid in whole})
first = [cid for cid in whole if base[cid]['work_id']==works[0]]
second = [cid for cid in whole if base[cid]['work_id']==works[1]]
old, new = copy.deepcopy(base), copy.deepcopy(base)
for cid in [*first[:2], second[0]]: old[cid]['judgment']='meaning_error'
new[second[1]]['judgment']='meaning_error'
screen = cls.contract['comparison']['screen']
pair = mod.scoring.paired_report(old,new,screen,True)
assert pair['screen_pass'] and pair['net_accepted_change']==2
assert len(pair['works_with_newly_accepted'])==2 and pair['work_net_accepted_changes'][works[1]]==0
incomplete = mod.scoring.paired_report(old,new,screen,False)
assert incomplete['screen_pass'] is None and incomplete['screen_status']=='inconclusive'
constrained = next(cid for cid in base if base[cid]['assessment']=='constrained_meanings_only')
for field, value, check in [('supported_span_severity','critical_error','no_constrained_critical_increase'),
                           ('unknown_span_handling','overconfident','no_new_overconfidence')]:
    adverse = copy.deepcopy(new)
    adverse[constrained][field]=value
    p = mod.scoring.paired_report(old,adverse,screen,True)
    assert p['screen_pass'] is False and p['screen_checks'][check] is False
adverse = copy.deepcopy(new)
adverse[second[1]]['judgment']='critical_error'
p = mod.scoring.paired_report(old,adverse,screen,True)
assert p['screen_pass'] is False and not p['screen_checks']['no_accepted_to_critical']
assert not p['screen_checks']['no_whole_critical_increase']

contract_path = ROOT/'experiments/dev-assisted-qualified-20260927/uniform-evaluation-contract.json'
contract = json.loads(contract_path.read_bytes())
assert sha(contract_path)==mod.prep.CONTRACT_SHA
assert all(sha(ROOT/n)==expected for n,expected in contract['source_files_sha256'].items())
assert before=={n:sha(ROOT/n) for n in SOURCES}, 'Sources changed while executing QA'
summary = dict(status='PASS', tests=result.testsRun, seconds=elapsed, source_sha256=before,
    screen_gain_in_two_works_even_one_net_zero=True, global_net_gain_two=True,
    incomplete_inconclusive=True, constrained_critical_and_overconfidence_vetoes=True,
    accepted_to_critical_and_whole_critical_vetoes=True, uniform_contract_sha256=sha(contract_path),
    all_eight_frozen_merit_bindings_unchanged=True, actual_model_outputs_or_reviews_read=False,
    cloud_network_credentials_model_weights=False)
(SCRATCH/'result.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,indent=2))
