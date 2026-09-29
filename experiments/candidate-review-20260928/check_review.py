"""Check and optionally freeze review overlays; never writes a training/source file."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LOCAL = ROOT / 'resources/local/candidate-review-20260928'
TRAIN = ROOT / 'experiments/train-audit-20260927/qualified-v1/train.jsonl'
TRAIN_SHA = '15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc'
RELATIONS = {'P': 'PARAPHRASE_CANDIDATE', 'D': 'DIFFERENT_PUBLISHED_SENSES_OR_ROLES',
             'C': 'CONTEXT_REQUIRED', 'F': 'FORM_SCOPE_REVIEW'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    manifest = json.loads((HERE / 'packet-manifest.json').read_text(encoding='utf8'))
    assert sha(HERE / 'prepare.py') == manifest['script_sha256']
    for name, expected in manifest['input_sha256'].items():
        assert sha(ROOT / name) == expected, name
    for receipt in manifest['files'].values():
        path = ROOT / receipt['path']
        assert sha(path) == receipt['sha256'] and path.stat().st_size == receipt['bytes'], path
    assert sha(TRAIN) == TRAIN_SHA
    cases = {x['case_id']: x for x in map(json.loads, (LOCAL / 'polysemy-cases.jsonl').read_text(encoding='utf8').splitlines())}
    with (HERE / 'decisions-v2.tsv').open(encoding='utf8', newline='') as stream:
        decisions = list(csv.DictReader(stream, delimiter='\t'))
    ids = [r['case_id'] for r in decisions]
    assert len(ids) == len(set(ids)) == len(cases) == 200
    assert set(ids) == set(cases)
    overlays = []
    for row in decisions:
        assert set(row) == {'case_id', 'relation', 'flags', 'reason'} and None not in row.values()
        assert row['relation'] in RELATIONS and row['reason'].strip()
        case = cases[row['case_id']]
        overlays.append({**row, 'relation_label': RELATIONS[row['relation']],
                         'comparison_form': case['comparison_form'],
                         'group_ids': [e['group_id'] for e in case['entries']],
                         'observation_ids': sorted({s['observation_id'] for e in case['entries'] for s in e['sources']}),
                         'reviewer': '/root', 'method': 'published-gloss comparison with original XML scope inspection',
                         'status': 'PROVISIONAL_REVIEW_ONLY', 'training_admitted': False,
                         'source_correctness_certified': False, 'merge_authorized': False})
    lookup = {r['case_id']: r for r in overlays}
    assert lookup['POLY015']['relation'] == lookup['POLY016']['relation'] == 'F'
    assert lookup['POLY002']['relation'] == 'D' and lookup['POLY001']['relation'] == 'P'
    assert lookup['POLY096']['flags'] == 'UNVOWELLED_PERSIAN'
    assert lookup['POLY192']['relation'] == 'C'
    placeholders = [json.loads(x) for x in (LOCAL / 'placeholder-holds.jsonl').read_text(encoding='utf8').splitlines()]
    assert len(placeholders) == 6 and all(not r['training_admitted'] for r in placeholders)
    summary = {'status': 'TRIAGE_COMPLETE_NOT_TRAIN_ADMITTED', 'reviewer': '/root',
               'case_count': len(overlays), 'group_count': len({g for r in overlays for g in r['group_ids']}),
               'observation_count': len({g for r in overlays for g in r['observation_ids']}),
               'relations': dict(sorted(Counter(r['relation_label'] for r in overlays).items())),
               'placeholder_group_holds': 6, 'compound_scope_observation_holds': ['kosh:gbd:11', 'kosh:gbd:15', 'kosh:gbd:16'],
               'numeral_mismatch_passage_hold': '201001001',
               'input_decisions_sha256': sha(HERE / 'decisions-v2.tsv'),
               'previous_decisions_sha256': sha(HERE / 'decisions.tsv'),
               'previous_summary_sha256': sha(HERE / 'review-summary.json'),
               'previous_verification_source_sha256': sha(LOCAL / 'check-review-v1-source.py'),
               'packet_manifest_sha256': sha(HERE / 'packet-manifest.json'),
               'verification_script_sha256': sha(Path(__file__)),
               'historical_train_sha256': sha(TRAIN), 'new_training_rows': 0,
               'scope': '200 same-form gloss comparisons, not full corpus linguistic certification',
               'limitations': ['AI review', 'No original book-page verification for dictionary suspects',
                               'No new source-family split clearance', 'No automated translation correction or merging']}
    raw = ''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in overlays).encode('utf8')
    summary['overlay_sha256'] = hashlib.sha256(raw).hexdigest()
    return raw, summary


if __name__ == '__main__':
    assert sys.argv[1:] in ([], ['--write']), 'Use no argument to verify, or --write once to freeze.'
    raw, summary = build()
    overlay = LOCAL / 'root-review-v2.jsonl'
    receipt = HERE / 'review-summary-v2.json'
    if sys.argv[1:] == ['--write']:
        assert not overlay.exists() and not receipt.exists(), 'Frozen review already exists'
        overlay.write_bytes(raw)
        receipt.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    else:
        assert overlay.read_bytes() == raw
        assert json.loads(receipt.read_text(encoding='utf8')) == summary
    print(json.dumps(summary, ensure_ascii=False))
