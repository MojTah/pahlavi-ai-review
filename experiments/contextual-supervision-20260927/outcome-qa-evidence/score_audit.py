"""Reconstruct frozen DEV48 arithmetic independently; no semantic re-rating."""
from pathlib import Path
from collections import Counter
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
EXP=ROOT/'experiments/contextual-supervision-20260927'; PACK=EXP/'blind-dev48'
sha=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())
rows=lambda p:[json.loads(x) for x in Path(p).read_bytes().splitlines() if x.strip()]
receipt=read(EXP/'reviewer-receipts.json'); provenance=read(PACK/'lead-only/provenance.json')
mapping=rows(PACK/'lead-only/mapping.jsonl')
contract=read(ROOT/'experiments/dev-assisted-qualified-20260927/uniform-evaluation-contract.json')
references={r['id']:r for r in rows(ROOT/'experiments/dev-diagnostic-20260927/references.jsonl')}
assessments={r['id']:r for r in read(ROOT/'experiments/dev-diagnostic-20260927/assessment-contract.json')['cases']}
predictions={r['id']:r for r in rows(EXP/'attempt-2/recovered/contextual/evaluation/predictions.jsonl')}
assert receipt['fresh_context'] is True and receipt['identities_hidden_until_both_reviews_complete'] is True
assert len(mapping)==len({m['review_id'] for m in mapping})==96
assert provenance['completion']['complete'] is True
categories=set(contract['review']['categories']); decoded={}; validated=0
packet_fields={'review_id','source_text','references','assessment','constraint','execution_status','output_text','output_sha256'}
rating_fields={'review_id','output_sha256','judgment','categories','supported_span_severity','unknown_span_handling','reason','output_span'}
digests={}
for reviewer in ('A','B'):
    ppath=PACK/f'reviewer-{reviewer}/packet.jsonl'; rpath=PACK/f'reviewer-{reviewer}/reviews.jsonl'
    packet=rows(ppath); ratings=rows(rpath)
    assert sha(rpath.read_bytes())==receipt['reviewers'][reviewer]['sha256']
    assert len(packet)==len(ratings)==receipt['reviewers'][reviewer]['rows']==48
    bypacket={p['review_id']:p for p in packet}; byrating={r['review_id']:r for r in ratings}
    mine={m['review_id']:m for m in mapping if m['reviewer']==reviewer}
    assert len(bypacket)==len(byrating)==48 and bypacket.keys()==byrating.keys()==mine.keys()
    decoded[reviewer]={'control':{},'candidate':{}}
    for rid,p in bypacket.items():
        r,m=byrating[rid],mine[rid]; cid=m['case_id']; raw=predictions[m['prediction_id']]
        assert set(p)==packet_fields and set(r)==rating_fields
        assert r['output_sha256']==p['output_sha256']==m['output_sha256']==sha(p['output_text'].encode())==raw['output_sha256']
        assert p['output_text']==raw['text'] and p['execution_status']==m['execution_status']==raw['status']=='success'
        assert p['source_text']==references[cid]['source_text'] and sha(p['source_text'].encode())==m['source_sha256']
        assert p['references']=={k:references[cid][k] for k in ('translations','edition','notes','reference_screen','expert_adjudicated')}
        assert p['assessment']==m['assessment']==assessments[cid]['assessment'] and p['constraint']==assessments[cid]['constraint']
        assert m['work_id']==assessments[cid]['work_id']
        assert set(r['categories'])==categories and set(r['categories'].values())<={'pass','fail','uncertain','not_applicable'}
        assert isinstance(r['reason'],str) and r['reason'].strip()
        assert isinstance(r['output_span'],str) and (not r['output_span'] or r['output_span'] in p['output_text'])
        assert r['supported_span_severity'] in ('none','meaning_error','critical_error','uncertain')
        assert r['unknown_span_handling'] in ('appropriately_uncertain','overconfident','uncertain','no_unknown_span')
        if p['assessment']=='provisional_whole_translation':
            assert r['judgment'] in ('accepted','meaning_error','critical_error','uncertain')
            if r['judgment']=='accepted':
                assert set(r['categories'].values())<={'pass','not_applicable'}
                assert all(r['categories'][c]=='pass' for c in ('lexical_meaning','omissions','unsupported_additions','source_uncertainty'))
                assert r['supported_span_severity']=='none' and r['unknown_span_handling']!='overconfident'
            else:
                assert r['output_span'].strip() and ('uncertain' if r['judgment']=='uncertain' else 'fail') in r['categories'].values()
        else:
            assert p['assessment']=='constrained_meanings_only' and r['judgment']=='constrained_only'
            severity=r['supported_span_severity']
            if severity!='none':assert ('uncertain' if severity=='uncertain' else 'fail') in r['categories'].values()
            if severity!='none' or r['unknown_span_handling']=='overconfident':assert r['output_span'].strip()
            if r['unknown_span_handling']=='overconfident':assert r['categories']['source_uncertainty']=='fail'
        assert cid not in decoded[reviewer][m['condition']]
        decoded[reviewer][m['condition']][cid]={**r,**m}
        validated+=1
    digests[reviewer]={'packet':sha(ppath.read_bytes()),'review':sha(rpath.read_bytes())}

def condition(items):
    whole=[r for r in items if r['assessment']=='provisional_whole_translation']; constrained=[r for r in items if r['assessment']=='constrained_meanings_only']
    c=Counter(r['judgment'] for r in whole)
    return {'total_cases':len(items),'execution_counts':dict(Counter(r['execution_status'] for r in items)),
      'whole_denominator':len(whole),'whole_counts':{k:c[k] for k in ('accepted','meaning_error','critical_error','uncertain','abstain','timeout','error','unattempted')},
      'accepted_percent':100*c['accepted']/len(whole),'critical_error_percent':100*c['critical_error']/len(whole),
      'constrained_denominator':len(constrained),'constrained_severity':dict(Counter(r['supported_span_severity'] for r in constrained)),
      'constrained_execution':dict(Counter(r['execution_status'] for r in constrained)),
      'constrained_overconfidence':sum(r['unknown_span_handling']=='overconfident' for r in constrained),
      'failed_categories_whole':dict(Counter(k for r in whole for k,v in r['categories'].items() if v=='fail'))}
def pair(old,new):
    assert old.keys()==new.keys() and len(old)==24
    cases=[dict(case_id=cid,work_id=old[cid]['work_id'],assessment=old[cid]['assessment'],previous=old[cid]['judgment'],candidate=new[cid]['judgment'],
      previous_severity=old[cid]['supported_span_severity'],candidate_severity=new[cid]['supported_span_severity'],
      previous_unknown_handling=old[cid]['unknown_span_handling'],candidate_unknown_handling=new[cid]['unknown_span_handling']) for cid in sorted(old)]
    whole=[r for r in cases if r['assessment']=='provisional_whole_translation']; constrained=[r for r in cases if r['assessment']=='constrained_meanings_only']
    gain=[r['case_id'] for r in whole if r['previous']!='accepted' and r['candidate']=='accepted']
    lost=[r['case_id'] for r in whole if r['previous']=='accepted' and r['candidate']!='accepted']
    crit=sum(r['candidate']=='critical_error' for r in whole)-sum(r['previous']=='critical_error' for r in whole)
    atoc=[r['case_id'] for r in whole if r['previous']=='accepted' and r['candidate']=='critical_error']
    works=sorted({r['work_id'] for r in whole if r['case_id'] in gain})
    net={w:sum((r['candidate']=='accepted')-(r['previous']=='accepted') for r in whole if r['work_id']==w) for w in sorted({r['work_id'] for r in whole})}
    ccrit=sum(r['candidate_severity']=='critical_error' for r in constrained)-sum(r['previous_severity']=='critical_error' for r in constrained)
    over=[r['case_id'] for r in constrained if r['candidate_unknown_handling']=='overconfident' and r['previous_unknown_handling']!='overconfident']
    checks={'full_two_arm_comparison_complete':True,'all_pair_outputs_attempted':True,
      'net_accepted_gain':len(gain)-len(lost)>=contract['comparison']['screen']['both_reviewers_min_net_accepted_gain'],
      'gains_in_multiple_works':len(works)>=contract['comparison']['screen']['min_works_with_gains'],
      'no_whole_critical_increase':crit<=0,'no_accepted_to_critical':not atoc,
      'no_constrained_critical_increase':ccrit<=0,'no_new_overconfidence':not over}
    return dict(newly_accepted=gain,lost_acceptance=lost,net_accepted_change=len(gain)-len(lost),critical_count_change=crit,
      accepted_to_critical=atoc,work_net_accepted_changes=net,works_with_newly_accepted=works,
      constrained_critical_count_change=ccrit,new_constrained_overconfidence=over,
      whole_transitions=dict(Counter(r['previous']+' -> '+r['candidate'] for r in whole)),
      constrained_severity_transitions=dict(Counter(r['previous']+':'+r['previous_severity']+' -> '+r['candidate']+':'+r['candidate_severity'] for r in constrained)),
      cases=cases,screen_checks=checks,screen_pass=all(checks.values()),screen_status='pass' if all(checks.values()) else 'fail')
reports={}
for reviewer in ('A','B'):
    conditions={}
    for arm in ('control','candidate'):
        items=list(decoded[reviewer][arm].values()); c=condition(items)
        assert (c['whole_denominator'],c['constrained_denominator'])==(15,9)
        c['by_work']={w:condition([r for r in items if r['work_id']==w]) for w in sorted({r['work_id'] for r in items})}
        conditions[arm]=c
    reports[reviewer]={'conditions':conditions,'paired':{'control -> candidate':pair(decoded[reviewer]['control'],decoded[reviewer]['candidate'])}}
disagreements={arm:[{'case_id':cid,'A':{k:decoded['A'][arm][cid][k] for k in ('judgment','supported_span_severity','unknown_span_handling')},
  'B':{k:decoded['B'][arm][cid][k] for k in ('judgment','supported_span_severity','unknown_span_handling')}} for cid in sorted(decoded['A'][arm])
  if any(decoded['A'][arm][cid][k]!=decoded['B'][arm][cid][k] for k in ('judgment','supported_span_severity','unknown_span_handling'))] for arm in ('control','candidate')}
result=dict(status='PASS',validated_reviews=validated,review_sha256=digests,reviewers=reports,reviewer_disagreements=disagreements,
    both_reviewers_screen=all(reports[r]['paired']['control -> candidate']['screen_pass'] for r in reports),
    no_semantic_rerating=True,scoring_helper_imported=False)
(Path(__file__).parent/'score-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
short={r:{'conditions':{a:{k:v[k] for k in ('whole_counts','constrained_severity','constrained_overconfidence')} for a,v in reports[r]['conditions'].items()},
    'net_accepted_change':reports[r]['paired']['control -> candidate']['net_accepted_change'],
    'screen_checks':reports[r]['paired']['control -> candidate']['screen_checks'],
    'newly_accepted':reports[r]['paired']['control -> candidate']['newly_accepted'],
    'lost_acceptance':reports[r]['paired']['control -> candidate']['lost_acceptance']} for r in reports}
print(json.dumps({'status':'PASS','reviews':validated,'summary':short,'disagreement_counts':{a:len(v) for a,v in disagreements.items()}},ensure_ascii=False,indent=2))
scored=EXP/'scored-comparison/comparison.json'
if scored.exists():
    actual=read(scored)
    assert actual['reviewers']==reports and actual['reviewer_disagreements']==disagreements and actual['both_reviewers_screen']==result['both_reviewers_screen']
    freeze_path=scored.parent/'blind-review-freeze.json'; freeze=read(freeze_path)
    assert actual['blind_review_freeze']==freeze
    for reviewer in ('A','B'):
        data=(PACK/f'reviewer-{reviewer}/reviews.jsonl').read_bytes()
        assert data==(scored.parent/f'reviewer-{reviewer}/reviews.jsonl').read_bytes()
        assert sha(data)==freeze[reviewer]['sha256']==receipt['reviewers'][reviewer]['sha256']
    assert actual['packet_provenance_sha256']==sha((PACK/'lead-only/provenance.json').read_bytes())
    assert actual['scorer_sha256']==sha((ROOT/'scripts/review_contextual.py').read_bytes())
    assert actual['comparison_completion']['complete'] is True and actual['screen_status']=='assessed'
    parity=dict(status='PASS',full_reviewer_conditions_perwork_pairs_transitions_disagreements_exact=True,
        raw_frozen_reviews_unchanged=True,score_contract_provenance_bound=True,
        comparison_sha256=sha(scored.read_bytes()),blind_review_freeze_sha256=sha(freeze_path.read_bytes()),
        receipts_sha256=sha((EXP/'reviewer-receipts.json').read_bytes()),scorer_sha256=actual['scorer_sha256'])
    (Path(__file__).parent/'score-parity.json').write_text(json.dumps(parity,indent=2)+'\n',encoding='utf-8')
    print('Frozen converter summary exactly matches independent reconstruction.')
