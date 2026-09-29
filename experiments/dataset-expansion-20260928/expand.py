"""Recover source-backed lexical resources locally; never creates training labels."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import time
import unicodedata
import xml.etree.ElementTree as ET

from cpd_extract import extract as extract_cpd

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'resources/local/dataset-expansion-20260928/lexicon-v1'
RECEIPT = HERE / 'lexicon-summary-v1.json'
BASE = 'resources/local/kosh-quality-20260928/complete-v4/'
CATALOGUE = 'sources/local/public-texts-2026-09-20/kosh-catalogue-20260928/raw/9c02a929451b66a27a5f385a02ba6fc6fabf8b3b12946a98d629c9b48613ce97.source'
REVIEW = 'resources/local/candidate-review-20260928/root-review-v2.jsonl'
TRAIN = 'experiments/train-audit-20260927/qualified-v1/train.jsonl'
DECISIONS = 'experiments/dataset-expansion-20260928/collection-decisions.json'
PINS = {
    BASE + 'observations.jsonl': '3b0b14ce6e6520ad801839388d7362596c0cdfd1480f1a5b63d378071c0c1a65',
    BASE + 'staged-groups.jsonl': '37f6740ca7066251a66395767f8b7049b5833522cd85a6b353ab6472e79755ee',
    BASE + 'quarantine.jsonl': '3c50ee513be84ce842e68342a7bfe09394fff42fb8188e9e4246eeab195c8d27',
    CATALOGUE: 'c57a017039bbee01dd55f8617c0302a99e012c471468c1bcfe259f140874bf8d',
    REVIEW: '22e6011478b3dedd9bd3ce5818a677d56d1f879ea0891335202acdd763475f6a',
    TRAIN: '15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc',
    DECISIONS: 'ce1b1c348678e5f6e5592d120f9b2c604bd64630cac0fd0166ce59e283f90c3f',
}
PROTECTED = {'hkr', 'sns', 'wz', 'mz'}
COMPOUND_HOLDS = {'kosh:gbd:11', 'kosh:gbd:15', 'kosh:gbd:16'}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf8')


def norm(value):
    return ' '.join(unicodedata.normalize('NFC', value).split())


def informative(value):
    return any(unicodedata.category(c)[0] in {'L', 'N'} for c in value)


def read(name):
    raw = (ROOT / name).read_bytes()
    assert digest(raw) == PINS[name], name
    return [json.loads(x) for x in raw.decode('utf8').splitlines()] if name.endswith('.jsonl') else json.loads(raw)


def forms_from(node):
    if node is None:
        return None
    if len(node) and (any(n.tag != 'form' or len(n) for n in node) or norm(node.text or '') or
                      any(norm(n.tail or '') for n in node)):
        return None
    forms = [norm(n.text or '') for n in node] if len(node) else [norm(node.text or '')]
    return forms if forms and all(informative(x) for x in forms) else None


def source_flags(forms, meaning):
    text = ' '.join(forms) + ' ' + meaning
    flags = []
    if '?' in text or '؟' in text:
        flags.append('PUBLISHED_UNCERTAINTY')
    if '\ufffd' in text or any(unicodedata.category(c) == 'Cs' for c in text):
        flags.append('DAMAGED_UNICODE')
    if 'EQUIVALENT' in text:
        flags.append('SOURCE_GLYPH_PLACEHOLDER')
    if len(forms) > 1:
        flags.append('KEEP_COMPLETE_FORM_GROUP')
    return flags


def recover(row):
    """Return a typed resource from known structures, or retain its original hold."""
    collection = row['collection']
    if collection not in {'cpd', 'mmp', 'nmp', 'pyv', 'mpcd_term_tech'}:
        return None
    xml = row['source_record']['xml']
    if collection == 'cpd':
        result = extract_cpd(xml)
        if result['status'] != 'STRUCTURE_RECOVERED_REVIEW_REQUIRED':
            return None
        return {'kind': 'SCOPED_CPD_ENTRY', 'structured_entry': result,
                'resource_status': 'STRUCTURED_REFERENCE_SCOPE_REVIEW',
                'flags': ['PROVISIONAL_BLOCK_ASSOCIATION', 'KEEP_NESTED_SENSES_AND_EXAMPLES_SEPARATE']}
    if '<!DOCTYPE' in xml.upper() or '<!ENTITY' in xml.upper():
        return None
    try:
        tree = ET.fromstring(xml)
    except ET.ParseError:
        return None
    if tree.tag != 'entry' or norm(tree.text or '') or any(norm(n.tail or '') for n in tree):
        return None
    if collection == 'mmp':
        if [norm(n.text or '') for n in tree.findall('lang')] != ['MP']:
            return None
        if len(tree.findall('trc')) != 1 or len(tree.findall('sense')) != 1:
            return None
        if any(n.tag not in {'trl', 'lang', 'trc', 'gramm', 'sense', 'attest', 'see'} for n in tree):
            return None
        forms = forms_from(tree.find('trc'))
        sense = tree.find('sense')
        if not forms or len(sense) or not informative(sense.text or ''):
            return None
        meaning = norm(sense.text)
        return {'kind': 'SOURCE_LABELED_MP_LEXICAL_ENTRY', 'forms': forms,
                'meaning_as_published': meaning, 'source_language_evidence': 'Exactly one explicit XML lang=MP',
                'resource_status': 'SOURCE_BACKED_LEXICON_CANDIDATE',
                'flags': source_flags(forms, meaning) + ['MANICHAEAN_CONTEXT', 'MANUSCRIPT_LINEAGE_NOT_CLEARED']}
    if collection == 'mpcd_term_tech':
        if len(tree.findall('trc')) != 1 or len(tree.findall('definition')) != 1:
            return None
        forms = forms_from(tree.find('trc'))
        definition = tree.find('definition')
        if not forms or len(definition) or not informative(definition.text or ''):
            return None
        return {'kind': 'DEFINITION_OR_CROSS_REFERENCE', 'forms': forms,
                'definition_as_published': norm(definition.text),
                'category_as_published': tree.findtext('category'),
                'resource_status': 'REFERENCE_ONLY_NOT_TRANSLATION_GLOSS',
                'flags': ['NO_MAIN_TRANSLATION_GLOSS', 'DO_NOT_RESOLVE_REFERENCES_AUTOMATICALLY']}
    # NMP/PYV: markup is readable evidence, but missing glyphs/page markers are
    # retained in XML, never flattened into an invented plain-text gold target.
    if [n.tag for n in tree] != ['form', 'sense']:
        return None
    form, sense = list(tree)
    if len(form.findall('trc')) != 1 or any(n.tag not in {'trc', 'trl', 'orig_trc'} for n in form):
        return None
    forms = forms_from(form.find('trc'))
    allowed = {'gr', 'br', 'em'} if collection == 'nmp' else {'pb', 'p', 'h2'}
    inline = set(n.tag for n in sense.iter()) - {'sense'}
    if not forms or not inline or not inline <= allowed or not informative(''.join(sense.itertext())):
        return None
    return {'kind': 'MARKUP_LEXICAL_ENTRY', 'forms': forms,
            'published_sense_xml': ET.tostring(sense, encoding='unicode'),
            'inline_tags': sorted(inline), 'resource_status': 'STRUCTURED_REFERENCE_WITH_MARKUP',
            'flags': ['KEEP_INLINE_MARKUP', 'NOT_PLAIN_TRANSLATION_TARGET'] +
                     (['SOURCE_GLYPH_PLACEHOLDER'] if 'gr' in inline or 'EQUIVALENT' in xml else [])}


def assemble():
    rows, groups, quarantine, catalogue, review, train, decisions = [read(n) for n in PINS]
    assert len(rows) == 42904 and len(groups) == 26377 and len(train) == 2237
    obs = {r['id']: r for r in rows}
    assert len(obs) == len(rows)
    by_group = defaultdict(list)
    for item in review:
        for gid in item['group_ids']:
            by_group[gid].append({k: item[k] for k in ['case_id', 'relation_label', 'flags', 'reason']})
    resources, dispositions = [], {}
    originals = catalogue['dicts']
    qualifications = {r['collection']: r for r in decisions['collections']}
    assert len(qualifications) == 31 and set(qualifications) == set(originals)
    for name, item in qualifications.items():
        assert item['catalogue_declared'] == {k: originals[name].get(k) for k in item['catalogue_declared']}

    def add(resource, oid_list, origin):
        assert len(set(oid_list)) == len(oid_list) and not any(o in dispositions for o in oid_list)
        names = {obs[o]['collection'] for o in oid_list}
        assert len(names) == 1 and not names & PROTECTED
        name = names.pop()
        md = originals[name]
        qualification = qualifications[name]
        resource.update(collection=name, origin=origin, observation_ids=oid_list,
                        catalogue_attribution={k: md.get(k) for k in ['title', 'authors', 'source_languages', 'target_languages', 'zotero-key']},
                        language_label_status='CATALOGUE_DECLARED' if name != 'mmp' else 'SOURCE_RECORD_EXPLICIT_MP',
                        source_language_scope=['pal'] if name == 'mmp' else md['source_languages'],
                        source_qualification={k: qualification[k] for k in
                                              ['proposed_role', 'required_next_check', 'work_lineage']},
                        target_language_status='CATALOGUE_CONFLICT_OBSERVED_GERMAN' if name == 'acpv1_7'
                                               else 'CATALOGUE_DECLARED_NOT_EVERY_ENTRY_VERIFIED',
                        source_pointers=[{k: obs[o][k] for k in ['id', 'raw_file', 'raw_sha256', 'source_url']} for o in oid_list],
                        training_admitted=False, expert_certified=False,
                        original_observations_path=BASE + 'observations.jsonl',
                        sentence_alignment_status='NOT_A_SENTENCE_PAIR',
                        whole_work_split_clearance=False)
        resources.append(resource)
        for oid in oid_list:
            dispositions[oid] = {'observation_id': oid, 'collection': name, 'resource_id': resource['id'],
                                 'disposition': resource['resource_status'], 'prior_status': obs[oid]['status'],
                                 'prior_reason': obs[oid]['quarantine_reason'], 'training_admitted': False}

    for group in groups:
        forms, meaning = group['forms'], group['meaning_as_published']
        flags = source_flags(forms, meaning)
        status = 'SOURCE_BACKED_LEXICON_CANDIDATE'
        if not informative(meaning):
            status = 'HELD_NO_USABLE_PRIMARY_GLOSS'
        elif set(group['observation_ids']) & COMPOUND_HOLDS:
            status = 'HELD_COMPOUND_SCOPE'
        elif 'DAMAGED_UNICODE' in flags:
            status = 'HELD_DAMAGED_UNICODE'
        elif 'SOURCE_GLYPH_PLACEHOLDER' in flags:
            status = 'REFERENCE_WITH_SOURCE_GAPS'
        add({'id': group['id'], 'kind': 'PUBLISHED_FORM_SENSE_GROUP', 'forms': forms,
             'meaning_as_published': meaning, 'resource_status': status, 'flags': flags,
             'content_review': by_group[group['id']], 'prior_source_form_matches': group['train_source_form_matches']},
            group['observation_ids'], 'EXISTING_V4_GROUP')
    assert len(dispositions) == 27280
    qids = {q['observation_id'] for q in quarantine}
    assert qids == set(obs) - set(dispositions)
    for row in rows:
        if row['id'] in dispositions:
            continue
        resource = recover(row)
        if resource:
            resource['id'] = 'recovered:' + row['id']
            add(resource, [row['id']], 'RECOVERED_V4_QUARANTINE')
        else:
            dispositions[row['id']] = {'observation_id': row['id'], 'collection': row['collection'],
                                      'disposition': 'RETAIN_ORIGINAL_HOLD', 'prior_reason': row['quarantine_reason'],
                                      'resource_id': None, 'training_admitted': False}
    assert set(dispositions) == set(obs)
    pairs = defaultdict(list)
    for r in resources:
        if r.get('meaning_as_published') and not r['resource_status'].startswith('HELD'):
            key = canonical([sorted(norm(f) for f in r['forms']), norm(r['meaning_as_published']),
                             sorted(r['source_language_scope']),
                             sorted(r['catalogue_attribution']['target_languages']), r['target_language_status']])
            pairs[digest(key)].append(r['id'])
    duplicates = [{'pair_hash': key, 'resource_ids': value, 'action': 'RETAIN_SOURCE_LINEAGE_NOT_INDEPENDENT_EXAMPLES'}
                  for key, value in sorted(pairs.items()) if len(value) > 1]
    recovered = [r for r in resources if r['origin'] == 'RECOVERED_V4_QUARANTINE']
    summary = {'status': 'EXPANDED_SOURCE_RESOURCE_NOT_TRAINING_RELEASE',
               'observations_accounted_for': len(dispositions), 'old_staged_groups': len(groups),
               'resource_records': len(resources), 'recovered_quarantine_observations': len(recovered),
               'recovered_by_kind': dict(Counter(r['kind'] for r in recovered)),
               'by_resource_status': dict(Counter(r['resource_status'] for r in resources)),
               'by_collection': dict(Counter(r['collection'] for r in resources)),
               'retained_hold_observations': sum(d['resource_id'] is None for d in dispositions.values()),
               'exact_pair_duplicate_clusters': len(duplicates),
               'duplicate_member_resources': sum(len(d['resource_ids']) for d in duplicates),
               'new_training_pairs': 0, 'historical_training_pairs': 2237,
               'counts_warning': 'Flat lexical groups, complex dictionary entries and references have different grains; not summed into training pairs.'}
    return resources, list(dispositions.values()), duplicates, decisions['collections'], summary


def self_check():
    def row(collection, xml):
        return {'collection': collection, 'source_record': {'xml': xml}}
    good = '<entry><lang>MP</lang><trc><form>x</form></trc><sense>word</sense></entry>'
    assert recover(row('mmp', good))['source_language_evidence'].endswith('lang=MP')
    assert recover(row('mmp', good.replace('>MP<', '>Pa/MP<'))) is None
    assert recover(row('mmp', good.replace('word', '?'))) is None
    assert recover(row('mmp', good.replace('</sense>', '</sense><sense>other</sense>'))) is None
    assert recover(row('sns', good)) is None
    nmp = '<entry><form><trc>x</trc></form><sense>word <gr/> evidence</sense></entry>'
    r = recover(row('nmp', nmp))
    assert '<gr' in r['published_sense_xml'] and 'SOURCE_GLYPH_PLACEHOLDER' in r['flags']
    assert 'meaning_as_published' not in r
    assert recover(row('nmp', nmp.replace('</entry>', 'stray</entry>'))) is None
    assert not informative('(؟)') and informative('word (?)')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    assert not (args.write and args.check)
    if args.write and (OUT.exists() or RECEIPT.exists()):
        raise ValueError('Frozen output exists; never overwrite it')
    started = time.monotonic()
    self_check()
    resources, dispositions, duplicates, collections, summary = assemble()
    bodies = {'lexical-resources.jsonl': resources, 'observation-dispositions.jsonl': dispositions,
              'exact-pair-duplicates.jsonl': duplicates, 'collection-decisions.jsonl': collections}
    payloads = {name: b''.join(canonical(r) + b'\n' for r in values) for name, values in bodies.items()}
    assert sum(len(raw) for raw in payloads.values()) < 250_000_000
    summary.update(input_sha256=PINS, code_sha256={p.name: digest(p.read_bytes()) for p in [Path(__file__), HERE / 'cpd_extract.py']},
                   output_receipts={name: {'sha256': digest(raw), 'bytes': len(raw), 'rows': len(bodies[name])} for name, raw in payloads.items()})
    for name, expected in PINS.items():
        assert digest((ROOT / name).read_bytes()) == expected
    if args.write:
        OUT.mkdir(parents=True)
        for name, raw in payloads.items():
            (OUT / name).write_bytes(raw)
        RECEIPT.write_bytes(canonical(summary) + b'\n')  # Completion receipt is written last.
    if args.check:
        assert json.loads(RECEIPT.read_bytes()) == summary
        for name, raw in payloads.items():
            assert (OUT / name).read_bytes() == raw, name
    print(json.dumps({**summary, 'elapsed_seconds': round(time.monotonic() - started, 2)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
