"""Paired counts under frozen denominators; no pooled accuracy or automatic promotion."""
from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('rating_schema', ROOT / 'experiments/readiness-repair-20260930/live-execution/summarize_reviews.py')
schema = importlib.util.module_from_spec(spec)
spec.loader.exec_module(schema)
EXPECTED = {'lexical_task_recall':6, 'conditioned_grammar_recall':4, 'inscription_task_recall':2,
            'historical_context_retention':12, 'targeted_sense_applicability':4,
            'fixed_whole':15, 'fixed_constrained':9, 'confirmation':5}


def rows(name):
    return [json.loads(x) for x in (HERE / name).read_bytes().splitlines()]


def main():
    mapping = json.loads((HERE / 'blind-mapping.json').read_bytes())
    packet = {r['blind_id']:r for r in rows('blind-packet.jsonl')}
    assert len(mapping) == len(packet) == 126 and set(mapping) == set(packet)
    result = dict(provisional_ai_review=True, expert_adjudicated=False, pooled_accuracy=None,
                  reviewers={}, gates={}, paired_transitions=[], source_sha256={})
    all_ratings = {}
    whole = {r['id']:r for r in schema.read_lines(ROOT / 'experiments/dev-diagnostic-20260927/references.jsonl')}
    for reviewer in ('reviewer-a','reviewer-b'):
        ratings = rows(reviewer + '.jsonl')
        assert len(ratings) == 126 and {r['blind_id'] for r in ratings} == set(mapping)
        cells, duplicate_labels = defaultdict(list), {}
        keyed = {}
        work_cells = defaultdict(list)
        for r in ratings:
            assert set(r) == schema.FIELDS
            m, p = mapping[r['blind_id']], packet[r['blind_id']]
            labels = (schema.LABELS - {'accepted'}) | {'no_supported_error'} if p['module']=='fixed_constrained' else schema.LABELS
            assert r['label'] in labels
            assert isinstance(r['reason'],str) and r['reason'].strip() and isinstance(r['evidence_span'],str)
            assert all(isinstance(r[k],list) and all(isinstance(v,str) for v in r[k]) for k in ('supported','omitted','unsupported'))
            assert r['uncertainty_preserved'] is None or type(r['uncertainty_preserved']) is bool
            assert r['structure'] in {'valid_target_schema','valid_json_different_schema','invalid_json','not_applicable'}
            assert r['scope_preservation'] in {'preserved','contradicted','uncertain','not_applicable'}
            dup = json.dumps({k:p[k] for k in ('module','prompt','evidence','answer')},sort_keys=True,ensure_ascii=False)
            assert duplicate_labels.setdefault(dup,r['label']) == r['label'], (reviewer,'identical output inconsistent',r['blind_id'])
            module = m['review_module'] if m['module']=='fixed_merit' else m['module']
            cells[module,m['arm']].append(r)
            keyed[m['arm'],m['case_id']] = r
            if module == 'fixed_whole':
                work_cells[whole[m['case_id']]['work_id'],m['arm']].append(r)
        tables = {}
        for module,n in EXPECTED.items():
            arms = ('reference','dose96','dose192','dose384') if module=='lexical_task_recall' else ('reference','dose384')
            tables[module] = {}
            for arm in arms:
                cell = cells[module,arm]
                assert len(cell)==n,(module,arm,len(cell),n)
                tables[module][arm] = dict(n=n, labels=dict(Counter(r['label'] for r in cell)),
                    structure=dict(Counter(r['structure'] for r in cell)))
        transitions = []
        for case in sorted({m['case_id'] for m in mapping.values()}):
            a,b = keyed['reference',case],keyed['dose384',case]
            m = next(v for v in mapping.values() if v['case_id']==case)
            module = m['review_module'] if m['module']=='fixed_merit' else m['module']
            transitions.append(dict(reviewer=reviewer,case_id=case,module=module,before=a,after=b))
        result['paired_transitions'] += transitions
        count = lambda mod,arm,label: tables[mod][arm]['labels'].get(label,0)
        gain = count('lexical_task_recall','dose384','accepted')-count('lexical_task_recall','reference','accepted')
        lost = [t['case_id'] for t in transitions if t['module']=='fixed_whole' and t['before']['label']=='accepted' and t['after']['label']!='accepted']
        unsafe = [t['case_id'] for t in transitions if t['module'] in {'fixed_whole','fixed_constrained'} and t['before']['label'] in {'accepted','no_supported_error'} and t['after']['label']=='critical_error']
        critical_ok = all(count(mod,'dose384','critical_error')<=count(mod,'reference','critical_error') for mod in ('fixed_whole','fixed_constrained'))
        conf_gain = [t['case_id'] for t in transitions if t['module']=='confirmation' and t['before']['label']!='accepted' and t['after']['label']=='accepted']
        result['reviewers'][reviewer] = tables
        result['gates'][reviewer] = dict(lexical_net_gain=gain, acquisition_pass=gain>=2,
            lost_accepted_whole_cases=lost, new_accepted_to_critical_cases=unsafe,
            fixed_critical_counts_not_increased=critical_ok,
            retention_safety_pass=not lost and not unsafe and critical_ok,
            confirmation_newly_accepted_cases=conf_gain,
            confirmation_critical_not_increased=count('confirmation','dose384','critical_error')<=count('confirmation','reference','critical_error'))
        result.setdefault('fixed_whole_by_work',{})[reviewer] = {f'{w}:{a}':dict(Counter(r['label'] for r in rr)) for (w,a),rr in work_cells.items()}
        all_ratings[reviewer] = {r['blind_id']:r for r in ratings}
    gates = list(result['gates'].values())
    joint = set(gates[0]['confirmation_newly_accepted_cases']) & set(gates[1]['confirmation_newly_accepted_cases'])
    result['joint_new_confirmation_cases'] = sorted(joint)
    result['acquisition_pass_both'] = all(g['acquisition_pass'] for g in gates)
    result['retention_safety_pass_both'] = all(g['retention_safety_pass'] for g in gates)
    result['confirmation_pass_both'] = bool(joint) and all(g['confirmation_critical_not_increased'] for g in gates)
    result['full_pool_proposal_screen_pass'] = all(result[k] for k in ('acquisition_pass_both','retention_safety_pass_both','confirmation_pass_both'))
    result['label_disagreements'] = [dict(blind_id=k,**mapping[k],a=all_ratings['reviewer-a'][k]['label'],b=all_ratings['reviewer-b'][k]['label']) for k in mapping if all_ratings['reviewer-a'][k]['label'] != all_ratings['reviewer-b'][k]['label']]
    for name in ('BLIND-REVIEW.md','blind-packet.jsonl','blind-mapping.json','reviewer-a.jsonl','reviewer-b.jsonl'):
        result['source_sha256'][name] = hashlib.sha256((HERE/name).read_bytes()).hexdigest()
    transitions = result.pop('paired_transitions')
    (HERE/'case-transitions.jsonl').write_text(''.join(json.dumps(t,ensure_ascii=False)+'\n' for t in transitions),encoding='utf8')
    (HERE/'review-summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    for who,table in result['reviewers'].items():
        print(who)
        for mod,arms in table.items(): print(mod,{a:v['labels'] for a,v in arms.items()})
    print('GATES',json.dumps(result['gates']))
    print('joint_new_confirmation',result['joint_new_confirmation_cases'],'full_pool_screen',result['full_pool_proposal_screen_pass'])
    print('label_disagreements',len(result['label_disagreements']))


if __name__=='__main__':
    main()
