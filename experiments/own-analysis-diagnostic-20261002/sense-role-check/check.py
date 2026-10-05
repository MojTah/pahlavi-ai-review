"""Reproduce the bounded six-group evidence inventory. No models or training.

Semantic dispositions are reviewed separately; this checks identity and scope.
Classic + Critic; the lead owns this file and the qualification report.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'resources/local/own-analysis-diagnostic-20261002/sense-role-check/inventory.json'
PINS = {
    'resources/local/own-analysis-diagnostic-20261002/authorized-execution/bounded-coverage-trace.json':
        '35641424d158cf5cf8ab5e695d8fda3964bc321ec22b73b1bd7a52278da5fb75',
    'resources/local/cloud-pilot-qualified-20260927/train.jsonl':
        '15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc',
    'resources/local/plain-target-preparation-20261001/data/learning-projections.jsonl':
        'b91a80ef92bc8f6adc3ae9ccae2f174ded02662b2d7445e7c29ac7350d6bfb17',
    'resources/local/training-ready-v2-20260929/data/train.jsonl':
        '22266b73d3a0f3c697aa4ced00f32d07e4d0198c11d36507778d4b6084a3ac59',
    'experiments/data-qualification-20260928/archive-alignment.jsonl':
        '051b4644ef0a4613f48232b9149398242a953f19726f36670919b10eb320019c',
    'experiments/dose-acquisition-20260930/live-execution/recovered/dose/training/run.json':
        '73013069580d48fe6a3b80291b7935c28889a7007aca594b05413d38ed8df71f',
}
PANEL = {'openampd:MP0602:full', 'openampd:MP0406:full'}


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')


def rows(path):
    values = [json.loads(s) for s in (ROOT / path).read_text(encoding='utf-8').splitlines()]
    key = 'unit_id' if values and 'unit_id' in values[0] else 'id'
    result = {r[key]: r for r in values}
    if len(result) != len(values):
        raise ValueError('Duplicate record identity: ' + path)
    return result


def build():
    for path, pin in PINS.items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != pin:
            raise ValueError('Changed pinned source: ' + path)
    trace = json.loads((ROOT / next(iter(PINS))).read_text(encoding='utf-8'))
    train, candidates, later, archives = [rows(p) for p in list(PINS)[1:5]]
    dose = json.loads((ROOT / list(PINS)[5]).read_text(encoding='utf-8'))
    exposures = Counter(dose['ordered_ids'])
    if (dose['status'] != 'completed' or dose['completed_steps'] != 384 or
            dose['consumed_slots'] != 6144 or len(dose['ordered_ids']) != 6144 or
            set(exposures) != set(later) or set(exposures.values()) != {4}):
        raise ValueError('Later execution no longer binds the four-pass selected stream')
    if len(trace['results']) != 6 or (len(train), len(candidates), len(later)) != (2237, 9971, 1536):
        raise ValueError('Changed bounded scope')
    groups, unique = {}, set()
    for name, group in trace['results'].items():
        ids = sorted(set(group['trained_record_ids'] + group['candidate_contextual_ids'] +
                         [r['id'] for r in group['lexical_entries']]))
        records = []
        for ident in ids:
            old, new = train.get(ident), candidates.get(ident)
            if old is None and new is None:
                raise ValueError('Missing traced record: ' + ident)
            record = {'id': ident, 'retained_file_membership': old is not None,
                      'later_selected_membership': ident in later,
                      'already_scored_panel_witness': ident in PANEL,
                      'later_logged_parent_forwards': exposures[ident],
                      'retained_optimizer_exposure_claim': 'MEMBERSHIP_ONLY_CHECK_RUN_RECEIPTS_SEPARATELY',
                      'current_projection_trained_claim_allowed': False}
            if old:
                record['retained_source'] = old['text']
                record['retained_target'] = old['target']
                record['retained_target_language'] = old['target_language']
                record['retained_work_id'] = old['work_id']
                record['retained_row_sha256'] = hashlib.sha256(encoded(old)).hexdigest()
            if new:
                record.update(task=new['task'], learning=new['learning'], parent_ids=new['parent_ids'])
                if 'lexical_provenance' in new:
                    record['lexical_provenance'] = new['lexical_provenance']
            if ident in archives:
                a = archives[ident]
                raw = a['provenance']['raw_source']
                if hashlib.sha256((ROOT / raw['path']).read_bytes()).hexdigest() != raw['sha256']:
                    raise ValueError('Changed documentary source: ' + ident)
                record['archive'] = {k: a[k] for k in ('disposition', 'provenance', 'split_and_overlap')}
            records.append(record)
            unique.add(ident)
        groups[name] = {'queried_forms': group['queried_forms'], 'records': records}
    return {'purpose': 'BOUNDED_QUALIFICATION_EVIDENCE_NOT_NEW_GOLD_OR_TRAINING',
            'input_sha256': PINS, 'groups': groups, 'unique_records': len(unique),
            'group_memberships': sum(len(g['records']) for g in groups.values()),
            'unique_candidate_tasks': dict(sorted(Counter(candidates[i]['task'] for i in unique
                                                         if i in candidates).items())),
            'unseen_claim_allowed': False, 'training_admitted': False, 'paid_run_admitted': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = build()
    payload = encoded(result)
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_bytes(payload)
    elif OUT.read_bytes() != payload:
        raise ValueError('Saved bounded inventory differs from pinned sources')
    print(json.dumps({'status': 'PASS_IDENTITY_SCOPE_ONLY', 'unique_records': result['unique_records'],
                      'group_memberships': result['group_memberships'],
                      'inventory_sha256': hashlib.sha256(payload).hexdigest()}))
