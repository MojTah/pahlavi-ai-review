"""Freeze source-scoped Persian lexical inventories, never sentence translations."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'experiments/dataset-expansion-20260928'))
from expand import canonical, forms_from, norm

RESOURCES = 'resources/local/dataset-expansion-20260928/lexicon-v1/lexical-resources.jsonl'
OBSERVATIONS = 'resources/local/kosh-quality-20260928/complete-v4/observations.jsonl'
PINS = {
    RESOURCES: '3f963c94c00f79cf8c04421fcd55a539649c1b2a62eb4ac029ae195c1d73871c',
    OBSERVATIONS: '3b0b14ce6e6520ad801839388d7362596c0cdfd1480f1a5b63d378071c0c1a65',
    'experiments/dataset-expansion-20260928/expand.py': 'e05b9733b680c1e5378ceb7d7106c7ae978b7f3fbb5566a47bda49ec5edede7b',
    'experiments/dataset-expansion-20260928/cpd_extract.py': '1d1c247109e7f45356b36bddcf62056c288a5275ac6b25209e6af4e4864a998f',
}
COLLECTIONS = {'da': 102, 'dk8': 480, 'dmx': 1030, 'gbd': 773, 'raf': 285, 'yz': 129}
REVIEWS = ['persian-root-review.json', 'dmx-review.json', 'gbd-review.json']
OUT = ROOT / 'resources/local/data-qualification-20260928/persian-v1'
RECEIPT = HERE / 'persian-summary-v1.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def automatic_holds(r):
    reasons = []
    if r['resource_status'] != 'SOURCE_BACKED_LEXICON_CANDIDATE':
        reasons.append(r['resource_status'])
    if any(flag in r['flags'] for flag in ['PUBLISHED_UNCERTAINTY', 'DAMAGED_UNICODE', 'SOURCE_GLYPH_PLACEHOLDER']):
        reasons.append('Published uncertainty or damaged extraction')
    if any(any(mark in f for mark in ['[', ']', '*', '?', '؟']) for f in r['forms']):
        reasons.append('Form reconstruction or uncertain annotation requires source review')
    if r['meaning_as_published'].endswith(('*', '>', '=')):
        reasons.append('Dangling reference or unresolved note marker')
    return reasons


def assemble():
    bindings = dict(PINS)
    for name, expected in PINS.items():
        assert sha((ROOT / name).read_bytes()) == expected, name
    resources = [json.loads(x) for x in (ROOT / RESOURCES).read_text(encoding='utf8').splitlines()]
    observations = {r['id']: r for r in map(json.loads, (ROOT / OBSERVATIONS).read_text(encoding='utf8').splitlines())}
    reviews, holds, reviewed = [], defaultdict(list), {}
    for name in REVIEWS:
        raw = (HERE / name).read_bytes()
        bindings[(HERE / name).relative_to(ROOT).as_posix()] = sha(raw)
        review = json.loads(raw)
        reviews.append({'path': name, 'reviewer': review['reviewer']})
        reviewed.update(review['reviewed_collections'])
        for oid, reason in review['holds'].items():
            assert oid in observations, oid
            holds[oid].append(reason)
    assert reviewed == COLLECTIONS, reviewed
    candidates = [r for r in resources if r['collection'] in COLLECTIONS]
    assert dict(Counter(r['collection'] for r in candidates)) == COLLECTIONS
    qualified, held = [], []
    for r in candidates:
        assert r['catalogue_attribution']['target_languages'] == ['fas']
        assert r['source_language_scope'] == ['pal']
        lineage = r['source_qualification']['work_lineage']
        assert lineage['resource_identity_resolved'] and not lineage['verified_heldout_work_id']
        assert not lineage['potential_heldout_constituent_to_check']
        reasons = automatic_holds(r)
        contexts = []
        for oid in r['observation_ids']:
            o = observations[oid]
            assert o['collection'] == r['collection']
            tree = ET.fromstring(o['source_record']['xml'])
            assert len(tree.findall('trc')) == len(tree.findall('sense')) == 1
            assert forms_from(tree.find('trc')) == r['forms'], oid
            assert not len(tree.find('sense'))
            assert norm(tree.findtext('sense')) == r['meaning_as_published'], oid
            reasons.extend(holds.get(oid, []))
            contexts.append({'observation_id': oid,
                             'grammar_as_published': [norm(x.text or '') for x in tree.findall('gramm')],
                             'attestation_as_published': [norm(x.text or '') for x in tree.findall('attest')]})
        if reasons:
            held.append({'resource_id': r['id'], 'collection': r['collection'],
                         'observation_ids': r['observation_ids'], 'reasons': list(dict.fromkeys(reasons))})
            continue
        qualified.append({
            'id': 'FAINV:' + r['id'], 'kind': 'SOURCE_SCOPED_LEXICAL_INVENTORY',
            'qualification': 'PUBLISHED_SOURCE_QUALIFIED_NOT_EXPERT_CERTIFIED',
            'learning_fields': {'forms_as_published': r['forms'],
                                'complete_meaning_inventory_as_published': r['meaning_as_published'],
                                'source_scope': r['catalogue_attribution']['title']},
            'source_language': 'pal', 'target_language': 'fas',
            'stratum': 'MIDDLE_PERSIAN_TRANSMISSION_WITH_PARTHIAN_LAYER' if r['collection'] in {'da', 'yz'} else 'BOOK_MIDDLE_PERSIAN',
            'collection': r['collection'], 'source_resource_id': r['id'],
            'observation_ids': r['observation_ids'], 'source_pointers': r['source_pointers'],
            'source_attribution': r['catalogue_attribution'],
            'non_learning_provenance': contexts, 'prior_content_review': r['content_review'],
            'inventory_policy': 'Keep all senses and form/stem bundles. A source-scoped inventory is not an exhaustive dictionary or a single context-free translation. Do not explode variants into independent examples.',
            'split_clearance': 'These six source works are outside the16 protected work families. Contextual attestations remain provenance only; do not export them into learning fields.',
            'expert_certified': False, 'training_run_authorized': False,
        })
    # A form shared by several sources is a review bundle, never a majority-vote label.
    groups = defaultdict(list)
    for r in qualified:
        for form in r['learning_fields']['forms_as_published']:
            groups[norm(form)].append(r['id'])
    bundles = [{'form_as_published': form, 'inventory_ids': ids,
                'policy': 'Preserve source-specific senses; do not choose one gloss or count witnesses as independent.'}
               for form, ids in sorted(groups.items()) if len(ids) > 1]
    assert len(qualified) + len(held) == 2799
    assert len({r['id'] for r in qualified}) == len(qualified)
    return {'qualified.jsonl': qualified, 'held.jsonl': held, 'shared-form-bundles.jsonl': bundles}, bindings, reviews


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--write', action='store_true')
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    assert not (args.write and args.check)
    if args.write and (OUT.exists() or RECEIPT.exists()):
        raise ValueError('Frozen output exists; refusing overwrite')
    # Real dangerous cases: uncertain dictionary labels and absent meaning must never pass.
    rows = [json.loads(x) for x in (ROOT / RESOURCES).read_text(encoding='utf8').splitlines()]
    for oid in ['kosh:gbd:361', 'kosh:gbd:11', 'kosh:da:24']:
        assert automatic_holds(next(r for r in rows if oid in r['observation_ids']))
    data, bindings, reviews = assemble()
    payloads = {name: b''.join(canonical(r) + b'\n' for r in values) for name, values in data.items()}
    assert sum(map(len, payloads.values())) < 50_000_000
    summary = {'status': 'SOURCE_QUALIFIED_LEXICAL_POOL_NO_TRAINING_RUN', 'total_reviewed_groups': 2799,
               'qualified_inventories': len(data['qualified.jsonl']), 'held_groups': len(data['held.jsonl']),
               'qualified_by_collection': dict(Counter(r['collection'] for r in data['qualified.jsonl'])),
               'shared_form_bundles': len(data['shared-form-bundles.jsonl']),
               'input_sha256': bindings, 'reviewers': reviews, 'code_sha256': sha(Path(__file__).read_bytes()),
               'outputs': {name: {'sha256': sha(raw), 'bytes': len(raw), 'rows': len(data[name])}
                           for name, raw in payloads.items()}}
    for name, expected in bindings.items():
        assert sha((ROOT / name).read_bytes()) == expected, name
    if args.write:
        OUT.mkdir(parents=True)
        for name, raw in payloads.items():
            (OUT / name).write_bytes(raw)
        RECEIPT.write_bytes(canonical(summary) + b'\n')
    elif args.check:
        assert json.loads(RECEIPT.read_bytes()) == summary
        for name, raw in payloads.items():
            assert (OUT / name).read_bytes() == raw, name
    print(json.dumps({k: v for k, v in summary.items() if k not in ['input_sha256', 'outputs']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
