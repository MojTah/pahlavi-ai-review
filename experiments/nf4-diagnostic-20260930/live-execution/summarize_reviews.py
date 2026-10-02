"""Joint blinded precision/checkpoint comparison; preserve each reviewer and module."""
from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('original_review_schema',
    ROOT / 'experiments/readiness-repair-20260930/live-execution/summarize_reviews.py')
schema = importlib.util.module_from_spec(spec)
spec.loader.exec_module(schema)
DENOMINATORS = {'lexical_task_recall': 6, 'conditioned_grammar_recall': 4,
                'inscription_task_recall': 2, 'historical_context_retention': 12,
                'targeted_sense_applicability': 4}


def main():
    mapping = json.loads((HERE / 'blind-mapping.json').read_bytes())
    packet = schema.read_lines(HERE / 'blind-packet.jsonl')
    assert len(mapping) == len(packet) == 112 and set(mapping) == {r['blind_id'] for r in packet}
    assert len({(m['precision'], m['arm'], m['case_id']) for m in mapping.values()}) == 112
    output = dict(provisional_ai_review=True, expert_adjudicated=False, pooled_accuracy=None,
                  reviewers={}, primary_lexical_signal={}, identical_answer_label_disagreements={}, source_sha256={})
    transitions = []
    for reviewer in ('reviewer-a', 'reviewer-b'):
        ratings = schema.read_lines(HERE / (reviewer + '.jsonl'))
        assert len(ratings) == 112 and {r['blind_id'] for r in ratings} == set(mapping)
        cells = defaultdict(list)
        keyed = {}
        for r in ratings:
            assert set(r) == schema.FIELDS and r['label'] in schema.LABELS
            assert isinstance(r['reason'], str) and r['reason'].strip() and isinstance(r['evidence_span'], str)
            assert all(isinstance(r[k], list) and all(isinstance(v, str) for v in r[k]) for k in ('supported','omitted','unsupported'))
            assert r['uncertainty_preserved'] is None or type(r['uncertainty_preserved']) is bool
            assert r['structure'] in {'valid_target_schema','valid_json_different_schema','invalid_json','not_applicable'}
            assert r['scope_preservation'] in {'preserved','contradicted','uncertain','not_applicable'}
            m = mapping[r['blind_id']]
            cells[m['precision'], m['module'], m['arm']].append(r)
            keyed[m['precision'], m['arm'], m['case_id']] = r
        result = {}
        for precision in ('bf16','nf4'):
            result[precision] = {}
            for module, n in DENOMINATORS.items():
                result[precision][module] = {}
                for arm in ('reference','candidate'):
                    rows = cells[precision,module,arm]
                    assert len(rows) == n, (precision,module,arm,len(rows),n)
                    result[precision][module][arm] = dict(n=n, labels=dict(Counter(r['label'] for r in rows)),
                        structure=dict(Counter(r['structure'] for r in rows)), scopes=dict(Counter(r['scope_preservation'] for r in rows)))
        output['reviewers'][reviewer] = result
        lexical = {p: result[p]['lexical_task_recall']['candidate']['labels'].get('accepted',0) for p in ('bf16','nf4')}
        output['primary_lexical_signal'][reviewer] = dict(lexical, net_gain=lexical['nf4']-lexical['bf16'],
            meets_predeclared_rule=lexical['nf4']-lexical['bf16'] >= 2)
        for case in sorted({m['case_id'] for m in mapping.values()}):
            module = next(m['module'] for m in mapping.values() if m['case_id'] == case)
            for kind, fixed, left, right in [('precision','reference',('bf16','reference'),('nf4','reference')),
                ('precision','candidate',('bf16','candidate'),('nf4','candidate')),
                ('checkpoint','bf16',('bf16','reference'),('bf16','candidate')),
                ('checkpoint','nf4',('nf4','reference'),('nf4','candidate'))]:
                a,b = keyed[*left,case],keyed[*right,case]
                transitions.append(dict(reviewer=reviewer,case_id=case,module=module,comparison=kind,fixed=fixed,
                    before=a,after=b,accepted_to_critical=a['label']=='accepted' and b['label']=='critical_error'))
        lookup = {r['blind_id']:r for r in ratings}
        duplicates = defaultdict(list)
        for row in packet:
            key = json.dumps({k:row[k] for k in ('module','prompt','evidence','answer')},sort_keys=True,ensure_ascii=False)
            duplicates[key].append(row['blind_id'])
        output['identical_answer_label_disagreements'][reviewer] = [
            dict(blind_ids=ids,labels=[lookup[i]['label'] for i in ids]) for ids in duplicates.values()
            if len({lookup[i]['label'] for i in ids}) > 1]
    output['primary_rule_met_by_both'] = all(x['meets_predeclared_rule'] for x in output['primary_lexical_signal'].values())
    output['accepted_to_critical_transitions'] = [t for t in transitions if t['accepted_to_critical']]
    for name in ('blind-packet.jsonl','blind-mapping.json','reviewer-a.jsonl','reviewer-b.jsonl','BLIND-REVIEW.md'):
        output['source_sha256'][name] = hashlib.sha256((HERE/name).read_bytes()).hexdigest()
    (HERE/'review-summary.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (HERE/'case-transitions.jsonl').write_text(''.join(json.dumps(t,ensure_ascii=False)+'\n' for t in transitions),encoding='utf-8')
    for reviewer, result in output['reviewers'].items():
        print(reviewer)
        for module in DENOMINATORS:
            print(module, {p:{a:result[p][module][a]['labels'] for a in ('reference','candidate')} for p in ('bf16','nf4')})
    print('Primary signal:',output['primary_lexical_signal'])
    print('Accepted-to-critical:',[(t['reviewer'],t['case_id'],t['comparison'],t['fixed']) for t in output['accepted_to_critical_transitions']])
    print('Duplicate rating inconsistencies:',output['identical_answer_label_disagreements'])


if __name__ == '__main__':
    main()
