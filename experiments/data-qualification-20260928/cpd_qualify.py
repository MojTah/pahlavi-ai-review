"""Qualify generic CPD sense inventories; no sentence examples or training launch.

No argument: run checks/profile only. --write: freeze component outputs once.
The root reviewer must integrate, review and clear the resulting component.
"""
from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'resources/local/data-qualification-20260928/cpd'
EXTRACTOR = ROOT / 'experiments/dataset-expansion-20260928/cpd_extract.py'
EXTRACTOR_SHA = '1d1c247109e7f45356b36bddcf62056c288a5275ac6b25209e6af4e4864a998f'
OBS = ROOT / 'resources/local/kosh-quality-20260928/complete-v4/observations.jsonl'
OBS_SHA = '3b0b14ce6e6520ad801839388d7362596c0cdfd1480f1a5b63d378071c0c1a65'
PDF = ROOT / 'sources/local/mackenzie-pdf-20260928/english-1986.pdf'
PDF_SHA = '594421d8c58e3f6b0ae169e383ae2917fe7572ac53fe568350b1b4ea62b1e091'
TRAIN = ROOT / 'experiments/train-audit-20260927/qualified-v1/train.jsonl'
TRAIN_SHA = '15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc'

# These are literal checks of the generic-sense changes read on PDF19--22.
# A phrase check applies to this exact complete transcription, never a fuzzy
# substring or a similarly spelled homograph. No replacement target is created.
CORRECTIONS = [
    ('abāz dādan ō', 19, ['attribute', 'appoint']),
    ('a-čār', 19, ['helpless']), ('agār', 19, ['useless']),
    ('āšnāg', 19, ['acquainted with']), ('āštīh', 19, ['concord']),
    ('bahr', 19, ['part', 'reason']), ('bahrag', 19, ['part', 'reason']),
    ('bahrwar', 19, ['partaking', 'partner']), ('bahragwar', 19, ['partaking', 'partner']),
    ('bahrwarīh', 19, ['participation', 'advantage']),
    ('baxtan, baxš-', 19, ['divide']), ('buland', 19, ['aloud']),
    ('čimīg', 19, ['caused', 'justified', 'reasonable']),
    ('did', 20, ['other']), ('drubušt', 20, ['protective']),
    ('duš-čihr', 20, ['ill-natured']), ('duš-nām', 20, ['ill-famed']),
    ('ēkānag', 20, ['loyal', 'faithful']), ('ēkānagīh', 20, ['loyalty', 'faithfulness']),
    ('guftār', 20, ['eloquence']), ('guftārīh', 20, ['eloquence']),
    ('hammōxtan, hammōz-', 20, ['learn']), ('hammōzišn', 20, ['learning']),
    ('hūg', 20, ['pig']), ('hūkar', 20, ['porcupine (not hedgehog)']),
    ('hūkarag', 20, ['porcupine (not hedgehog)']),
    ('karbūg', 20, ['lizard']), ('kardagān', 20, ['service (of the gods)']),
    ('mānīg', 20, ['house-owner']), ('mayānǰīg', 20, ['arbiter']),
    ('mizīdan, miz-', 21, ['suck']), ('mowmard', 21, ['magus']),
    ('nēk', 21, ['benefit']), ('nēkīh', 21, ['benefit']),
    ('niyāz', 21, ['necessity']), ('niyāzōmandīh', 21, ['necessity']),
    ('padist', 21, ['threat']), ('pad-nigerišn', 21, ['carefully']),
    ('parisp', 21, ['wall']), ('purnāy', 21, ['adult']),
    ('purr-marg', 21, ['deadly', 'baneful']), ('rēbās', 21, ['rhubarb']),
    ('rox', 21, ['rook', 'castle']), ('sārwār', 21, ['helmet']),
    ('sneh', 21, ['club', 'weapon']), ('šabyār', 21, ['grape syrup']),
    ('tahm', 22, ['strong', 'brave']), ('tāk', 22, ['branch']),
    ('wanīgar', 22, ['prodigal']), ('wanīgarīh', 22, ['prodigality', 'waste']),
    ('wēzag', 22, ['lot']), ('wiyābānīg', 22, ['confusing']),
    ('xīg', 22, ['leather bag']), ('xwarg', 22, ['live coal']),
]
# Explicitly deleted/superseded source headwords. Exact matches only.
DELETED = {'ā-distag', 'Ahrišwang', '*drēm', 'hammist', 'hammistān',
           'hammistagān', 'karbunag', 'karxōš', 'mādayār', 'mēzīdan',
           'nāyīzag', 'ōzārak', 'wizāštan', 'xūg', 'xūkar', 'xūkarag', 'yazd', 'yazdān'}
# Printed optional endings explicitly support these complete website bundles.
# This does NOT permit expansion into separate form/sense rows.
BUNDLE_EVIDENCE = {
    ('hūkar', 'hūkarag'): 20, ('bahr', 'bahrag'): 19,
    ('bahrwar', 'bahragwar'): 19,
}
UNRESOLVED_CORRECTION_FORMS = {'wiyābān', 'guftār', 'nēk', 'niyāz'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def walk(node):
    yield node
    for child in node['children']:
        yield from walk(child)


def text(node):
    """Exact text projection including mixed inline tails, not normalization."""
    return (node['text'] or '') + ''.join(text(c) + (c['tail'] or '') for c in node['children'])


def plain(node):
    """Permit only typographic inline emphasis; reject semantic markup."""
    if any(n['tag'] != 'hi' for n in list(walk(node))[1:]):
        raise ValueError('SEMANTIC_INLINE_MARKUP')
    return text(node)


def dubious(nodes):
    for node in nodes:
        for n in walk(node):
            value = text(n)
            if (n['attributes'].get('type', '') in {'doubtf', 'dobtf', 'concession'}
                    or re.search(r'[?？�*\[\]…]|\.{2,}|\b(?:perhaps|probably|uncertain)\b', value, re.I)
                    or any(unicodedata.category(c) in {'Co', 'Cn'} for c in value)):
                return True
    return False


def sense_view(node):
    """Keep a complete ordered sense's gloss/POS/usage; exclude quoted examples."""
    result = {'number_as_published': node['attributes'].get('n'), 'components': []}
    excluded = []
    if (node['text'] or '').strip():
        raise ValueError('UNSCOPED_SENSE_TEXT')
    for child in node['children']:
        if child['tag'] in {'eg', 'q'}:
            excluded.append(child['path'])
            continue
        if child['tag'] not in {'tr', 'def', 'gram', 'gramGrp', 'usg'}:
            raise ValueError('SENSE_REFERENCE_OR_NOTE_REQUIRES_REVIEW')
        if child['tag'] == 'gramGrp':
            # Preserve grammatical components individually; example sentences stay out.
            components = []
            for item in child['children']:
                if item['tag'] in {'eg', 'q'}:
                    excluded.append(item['path'])
                elif item['tag'] in {'gram', 'number', 'mood', 'itype', 'usg'}:
                    components.append({'kind': item['tag'], 'text': plain(item),
                                       'attributes': item['attributes'], 'tail': item['tail']})
                else:
                    raise ValueError('COMPLEX_GRAMMAR_SCOPE')
            value = {'kind': 'gramGrp', 'text': child['text'],
                     'attributes': child['attributes'], 'components': components}
        else:
            value = {'kind': child['tag'], 'text': plain(child), 'attributes': child['attributes']}
        if (child['tail'] or '').strip():
            raise ValueError('UNSCOPED_SENSE_TAIL')
        result['components'].append(value)
    if not any(c['kind'] in {'tr', 'def'} and any(ch.isalpha() for ch in c['text'])
               for c in result['components']):
        raise ValueError('NO_GENERIC_GLOSS_IN_SENSE')
    return result, excluded


def build():
    for path, expected in [(EXTRACTOR, EXTRACTOR_SHA), (OBS, OBS_SHA), (PDF, PDF_SHA), (TRAIN, TRAIN_SHA)]:
        assert sha(path) == expected, str(path)
    spec = importlib.util.spec_from_file_location('frozen_cpd_extract', EXTRACTOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = [r for r in map(json.loads, OBS.read_text(encoding='utf8').splitlines()) if r['collection'] == 'cpd']
    assert len(rows) == 3103
    extracted = [(r, module.extract(r['source_record']['xml'])) for r in rows]
    targets = set()
    for _, ex in extracted:
        if ex['tree']:
            identifier = ex['tree']['attributes'].get('{http://www.w3.org/XML/1998/namespace}id')
            if identifier:
                targets.add(identifier)
    qualified, held, correction_checks = [], [], []
    by_form = defaultdict(list)
    for row, ex in extracted:
        if ex['tree'] is None or ex['status'] != 'STRUCTURE_RECOVERED_REVIEW_REQUIRED':
            held.append({'id': row['id'], 'reason': ex['status'], 'source_xml_sha256': ex['source_xml_sha256']})
            continue
        top = ex['tree']['children']
        for block in ex['blocks']:
            forms = [top[i] for i in block['form_indices']]
            transcriptions = [n for f in forms for n in f['children'] if n['tag'] == 'trc']
            form_text = [text(n) for n in transcriptions]
            senses = [top[i] for i in block['sense_indices']]
            for form in form_text:
                by_form[form].append((row['id'], block['block_index'], '\n'.join(text(s) for s in senses)))
            locator = {'observation_id': row['id'], 'block_index': block['block_index'],
                       'raw_file': row['raw_file'], 'raw_sha256': row['raw_sha256'],
                       'source_url': row['source_url'], 'source_xml_sha256': ex['source_xml_sha256'],
                       'form_paths': [n['path'] for n in forms], 'sense_paths': [n['path'] for n in senses]}
            reasons = []
            if not form_text or not all(any(c.isalpha() for c in f) for f in form_text):
                reasons.append('MISSING_SOURCE_FORM')
            if not senses:
                reasons.append('NO_DIRECT_SENSE')
            multi = len(transcriptions) > 1 or 'MULTIPLE_FORM_ELEMENTS_ASSOCIATION_UNRESOLVED' in block['scope_flags']
            if multi and tuple(form_text) not in BUNDLE_EVIDENCE:
                reasons.append('FORM_SENSE_ASSOCIATION_UNRESOLVED')
            if dubious(forms):
                reasons.append('UNCERTAIN_OR_DAMAGED_FORM')
            if dubious(senses):
                reasons.append('UNCERTAIN_OR_DAMAGED_SENSE')
            if any(f in DELETED for f in form_text):
                reasons.append('SUPERSEDED_1986_FORM')
            if any(f in UNRESOLVED_CORRECTION_FORMS for f in form_text):
                reasons.append('1986_ADDED_SENSE_SCOPE_UNRESOLVED')
            # An explicit donor-language label is not silently treated as Middle Persian.
            relevant = [ex['tree']] + forms
            if any(any(k in n['attributes'] for k in ('lang', '{http://www.w3.org/XML/1998/namespace}lang'))
                   for item in relevant for n in ([item] if item is ex['tree'] else walk(item))):
                reasons.append('EXPLICIT_LANGUAGE_REQUIRES_SEPARATE_POOL')
            block_nodes = [top[i] for k in ('form_indices', 'sense_indices', 'cross_reference_indices', 'metadata_indices') for i in block[k]]
            refs = [n for item in block_nodes for n in walk(item) if n['tag'] == 'ref']
            if any(n['attributes'].get('target', '').removeprefix('#') not in targets for n in refs):
                reasons.append('DANGLING_XML_CROSS_REFERENCE')
            views, excluded = [], []
            for sense in senses:
                try:
                    value, omissions = sense_view(sense)
                    views.append(value)
                    excluded.extend(omissions)
                except ValueError as exc:
                    reasons.append(str(exc))
            annotations = []
            for index in block['metadata_indices']:
                item = top[index]
                if item['tag'] in {'gram', 'gramGrp', 'usg'}:
                    if any(n['tag'] in {'eg', 'q', 'xr', 'ref', 'note'} for n in walk(item)):
                        reasons.append('COMPLEX_BLOCK_GRAMMAR_OR_USAGE')
                    else:
                        annotations.append(item)
                elif item['tag'] == 'note':
                    reasons.append('ENTRY_NOTE_REQUIRES_SOURCE_REVIEW')
            # All metadata and illustrations are excluded from the supervision view.
            excluded += [top[i]['path'] for i in block['metadata_indices'] + block['cross_reference_indices']]
            target_text = '\n'.join(text(s) for s in senses)
            for form, page, expected in CORRECTIONS:
                if form in form_text and not all(term in target_text for term in expected):
                    reasons.append('1986_GENERIC_SENSE_CHECK_MISMATCH')
            record = {'id': row['id'] + ':block:' + str(block['block_index']), 'source': locator,
                      'form_bundle': form_text, 'sense_count': len(senses)}
            if reasons:
                held.append({**record, 'reasons': sorted(set(reasons))})
            else:
                qualified.append({**record, 'evidence_type': 'generic_lexical_sense_inventory',
                                  'source_language': 'pal', 'target_language': 'eng',
                                  'senses': views, 'scope_annotations': annotations,
                                  'excluded_context_paths': sorted(set(excluded) - {a['path'] for a in annotations}),
                                  'edition': 'MacKenzie 1971; Kosh structured CPD with checked 1986 corrections',
                                  'correction_bundle_page': BUNDLE_EVIDENCE.get(tuple(form_text)),
                                  'status': 'SOURCE_QUALIFIED_PENDING_INDEPENDENT_REVIEW',
                                  'training_admitted': False, 'expert_certified': False,
                                  'lexical_benchmark_unseen_vocabulary_claim_allowed': False})
    for form, page, expected in CORRECTIONS:
        matches = by_form.get(form, [])
        correction_checks.append({'form': form, 'pdf_page': page, 'required_generic_text': expected,
                                  'results': [{'observation_id': oid, 'block_index': idx,
                                               'pass': all(t in value for t in expected)} for oid, idx, value in matches],
                                  'status': 'MATCH' if matches and all(all(t in x[2] for t in expected) for x in matches)
                                  else 'MISSING_OR_SCOPE_MISMATCH'})
    deleted_checks = [{'form': f, 'present': f in by_form} for f in sorted(DELETED)]
    # No splitting of meanings, no inadvertent example payload, and real danger cases.
    assert all(len(q['senses']) == q['sense_count'] for q in qualified)
    assert len(qualified) + len(held) == 4226  # 4,224 scoped blocks + two malformed entries.
    assert len({q['id'] for q in qualified + held}) == 4226
    xrad = [q for q in qualified if q['form_bundle'] == ['xrad']]
    assert len(xrad) == 1 and xrad[0]['senses'][0]['components'][0]['text'] == 'wisdom, reason'
    assert any('FORM_SENSE_ASSOCIATION_UNRESOLVED' in q.get('reasons', []) and q['form_bundle'] == ['wihēz', 'wihēzag'] for q in held)
    assert sum(q.get('reason') == 'HELD_MALFORMED_XML' for q in held) == 2
    assert any(q['form_bundle'] == ['hūkar', 'hūkarag'] and q['correction_bundle_page'] == 20 for q in qualified)
    assert all(not any(n['tag'] in {'eg', 'q', 'xr', 'ref'} for n in walk(a))
               for q in qualified for a in q['scope_annotations'])
    assert not any(any(f in DELETED or f in UNRESOLVED_CORRECTION_FORMS for f in q['form_bundle']) for q in qualified)
    assert sha(TRAIN) == TRAIN_SHA
    counts = Counter(reason for q in held for reason in q.get('reasons', [q.get('reason')]))
    summary = {'source_observations': 3103, 'qualified_inventory_units': len(qualified),
               'held_units_including_malformed_entries': len(held), 'hold_reason_counts_overlap': dict(sorted(counts.items())),
               'correction_checks': len(correction_checks), 'correction_check_statuses': dict(Counter(c['status'] for c in correction_checks)),
               'deleted_headword_checks': deleted_checks, 'training_admitted': 0, 'expert_certified': False,
               'input_sha256': {str(p.relative_to(ROOT)): v for p, v in [(OBS, OBS_SHA), (PDF, PDF_SHA), (EXTRACTOR, EXTRACTOR_SHA), (TRAIN, TRAIN_SHA)]},
               'script_sha256': sha(Path(__file__)), 'status': 'COMPONENT_REVIEW_REQUIRED',
               'limits': ['Complete inventory means all direct senses in a scoped publisher block, not every homograph across editions.',
                          'No lexical unseen-vocabulary evaluation claim; root split/duplicate review required.',
                          'No original-page inspection of all dictionary entries; correction audit is explicitly bounded.',
                          'No training-use license or manuscript-quotation clearance inferred.']}
    return qualified, held, correction_checks, summary


def main():
    sys.stdout.reconfigure(encoding='utf8')
    assert sys.argv[1:] in ([], ['--write'])
    if sys.argv[1:] and OUT.exists():
        raise FileExistsError('Refusing existing component output directory')
    qualified, held, checks, summary = build()
    if sys.argv[1:]:
        OUT.mkdir(parents=True)
        receipts = {}
        for name, values in [('qualified.jsonl', qualified), ('held.jsonl', held), ('correction-checks.jsonl', checks)]:
            raw = ''.join(json.dumps(v, ensure_ascii=False) + '\n' for v in values).encode('utf8')
            (OUT / name).write_bytes(raw)
            receipts[name] = {'rows': len(values), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
        summary['outputs'] = receipts
        (OUT / 'manifest.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
