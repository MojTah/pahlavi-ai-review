"""Validate two blinded rating files; report each module/rater without pooling."""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LABELS = {'accepted', 'meaning_error', 'critical_error', 'uncertain'}
FIELDS = {'blind_id', 'label', 'reason', 'evidence_span', 'supported', 'omitted',
          'unsupported', 'uncertainty_preserved', 'structure', 'scope_preservation'}


def read_lines(path):
    return [json.loads(line) for line in path.read_bytes().splitlines()]


def main():
    mapping = json.loads((HERE / 'blind-mapping.json').read_bytes())
    packet = read_lines(HERE / 'blind-packet.jsonl')
    assert len(mapping) == len(packet) == 56 and set(mapping) == {r['blind_id'] for r in packet}
    output = dict(provisional_ai_review=True, expert_adjudicated=False, pooled_accuracy=None,
                  reviewers={}, source_sha256={})
    syntax = {a: dict(n=0, raw_json=0, json_after_optional_fence_removal=0)
              for a in ('reference', 'candidate')}
    for item in packet:
        m = mapping[item['blind_id']]
        if m['module'] != 'lexical_task_recall':
            continue
        stats = syntax[m['arm']]
        stats['n'] += 1
        raw = item['answer'].strip()
        lines = raw.splitlines()
        unfenced = '\n'.join(lines[1:-1]) if len(lines) >= 3 and lines[0] in ('```json', '```') and lines[-1] == '```' else raw
        for key, text in [('raw_json', raw), ('json_after_optional_fence_removal', unfenced)]:
            try:
                json.loads(text)
                stats[key] += 1
            except json.JSONDecodeError:
                pass
    output['mechanical_lexical_json_syntax'] = syntax
    transitions = []
    for name in ('reviewer-a', 'reviewer-b'):
        path = HERE / (name + '.jsonl')
        ratings = read_lines(path)
        assert len(ratings) == 56 and {r['blind_id'] for r in ratings} == set(mapping)
        pairs, modules = defaultdict(dict), defaultdict(lambda: defaultdict(list))
        for r in ratings:
            assert set(r) == FIELDS and r['label'] in LABELS
            assert isinstance(r['reason'], str) and r['reason'].strip()
            assert isinstance(r['evidence_span'], str)
            assert all(isinstance(r[k], list) and all(isinstance(v, str) for v in r[k])
                       for k in ('supported', 'omitted', 'unsupported'))
            assert r['uncertainty_preserved'] is None or type(r['uncertainty_preserved']) is bool
            assert r['structure'] in {'valid_target_schema', 'valid_json_different_schema', 'invalid_json', 'not_applicable'}
            assert r['scope_preservation'] in {'preserved', 'contradicted', 'uncertain', 'not_applicable'}
            m = mapping[r['blind_id']]
            pairs[m['case_id']][m['arm']] = r
            modules[m['module']][m['arm']].append(r)
        result = {}
        for module, arms in modules.items():
            assert len(arms['reference']) == len(arms['candidate'])
            result[module] = {arm: dict(n=len(rows), labels=dict(Counter(r['label'] for r in rows)),
                structure=dict(Counter(r['structure'] for r in rows)),
                scopes=dict(Counter(r['scope_preservation'] for r in rows))) for arm, rows in arms.items()}
        for case, arms in sorted(pairs.items()):
            assert set(arms) == {'reference', 'candidate'}
            module = mapping[arms['reference']['blind_id']]['module']
            transitions.append(dict(reviewer=name, case_id=case, module=module,
                reference=arms['reference'], candidate=arms['candidate']))
        output['reviewers'][name] = result
    for name in ('blind-packet.jsonl', 'blind-mapping.json', 'reviewer-a.jsonl', 'reviewer-b.jsonl', 'BLIND-REVIEW.md'):
        output['source_sha256'][name] = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
    (HERE / 'review-summary.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (HERE / 'case-transitions.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in transitions), encoding='utf-8')
    for reviewer, modules in output['reviewers'].items():
        print(reviewer)
        for module, arms in sorted(modules.items()):
            print(module, json.dumps({a: dict(n=v['n'], labels=v['labels'], scopes=v['scopes']) for a, v in arms.items()}))


if __name__ == '__main__':
    main()
