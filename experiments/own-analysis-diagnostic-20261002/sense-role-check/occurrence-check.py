"""Replay two commentary joins and bounded source-only information checks.

This checks identity and search scope, not philological truth or unseen status.
"""
import argparse
import hashlib
import html
import json
import re
import unicodedata
import xml.etree.ElementTree as ET

from check import ROOT, PINS as BASE_PINS, encoded

OUT = ROOT / 'resources/local/own-analysis-diagnostic-20261002/sense-role-check/occurrence-difference.json'
CAPTURE = 'sources/local/occurrence-commentary-20261002/'
PINS = {
    **{p: h for p, h in BASE_PINS.items() if 'bounded-coverage-trace' not in p},
    'experiments/dev-assisted-qualified-20260927/evidence/evidence.jsonl':
        '1d5e02cfb91dad1da94db072e9f5fcd6be463746bbc951425cb6631b5ea2ce4a',
    'experiments/component-diagnostic-20261001/packet-manifest.json':
        '08589df191f9ebb2337a59638b30c38f26510f6a5c4394be492920b3cf8decd4',
    'sources/local/public-texts-2026-09-20/berkeley/documents.json':
        'abe347c57356666d6ebbb5984c792fef57c9c3ae7f9387fe972a1716054167dc',
    'sources/local/public-texts-2026-09-20/invisible-east/middle-persian.json':
        '522fd18e024ba30fde22e867b6c72b53ed3a9e549dbe2f09453044a73d445692',
    'resources/local/own-analysis-diagnostic-20261002/sense-role-check/primary-inspection.json':
        '37ba2af3e6e51ea51f1908d3c097ab4edf13469eec3732a26e06f02971617c6e',
    CAPTURE + 'weber-1739b0616dd54089b7ab833805c5f2587551b48d84362993838383214e19c272.pdf':
        '1739b0616dd54089b7ab833805c5f2587551b48d84362993838383214e19c272',
    CAPTURE + 'iedc1036-07707cd2ec78b4b612de314bd2af78b2dd87434c897a032a85ee88527749e87d.html':
        '07707cd2ec78b4b612de314bd2af78b2dd87434c897a032a85ee88527749e87d',
}


def read(path, pin=None):
    data = (ROOT / path).read_bytes()
    expected = pin or PINS[path]
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError('Changed pinned input: ' + path)
    return data


def norm(text):
    text = html.unescape(re.sub('<[^>]+>', ' ', text)).casefold()
    text = ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))
    return ' '.join(re.findall(r'\w+', text))


def hits(texts, terms):
    # Bounded spelling screen; other readings and uninspected historical prompts remain unknown.
    return [i for i, text in enumerate(texts) if any(norm(t) in norm(text) for t in terms)]


def build():
    data = {p: read(p) for p in PINS}
    aid = [json.loads(s) for s in data['experiments/dev-assisted-qualified-20260927/evidence/evidence.jsonl'].splitlines()]
    attached = [e['source_text'] for r in aid for e in r['examples']]
    queries = [r['source_text'] for r in aid]
    if (len(attached), len(set(attached)), len(queries)) != (58, 56, 24):
        raise ValueError('Prior assistance universe changed')
    manifest = json.loads(data['experiments/component-diagnostic-20261001/packet-manifest.json'])
    translator = '[USER_HOME]/Documents/Codex Projects/01-Software/Pahlavi Translator/config/experiments/'
    s04 = json.loads(read(translator + 'lexical-sense-diagnostic-plan.json', manifest['input_sha256'][translator + 'lexical-sense-diagnostic-plan.json']))
    s07 = json.loads(read(translator + 'grammar-agent-diagnostic-plan.json', manifest['input_sha256'][translator + 'grammar-agent-diagnostic-plan.json']))
    if (s04['added_senses'] != manifest['information_difference_audit']['s04_added_senses'] or
            s07['grammar_notes'] != manifest['information_difference_audit']['s07_notes']):
        raise ValueError('Prior aid payload binding changed')
    docs = json.loads(data['sources/local/public-texts-2026-09-20/berkeley/documents.json'])
    doc = docs[53]
    iedc = json.loads(data['sources/local/public-texts-2026-09-20/invisible-east/middle-persian.json'])[152]
    if doc['id'] != 'MP0035' or doc['title'] != 'MP0035 / Berk. 34' or iedc['uri'] != 'IEDC1036' or iedc['shelfmark'] != 'Berk. 34, recto':
        raise ValueError('Physical witness join changed')
    raw_path = 'sources/local/public-texts-2026-09-20/berkeley/' + doc['source']['file']
    read(raw_path, doc['source']['sha256'])
    ns = {'t': 'http://www.tei-c.org/ns/1.0'}
    title_raw = 'sources/local/public-texts-2026-09-20/berkeley/raw/540c9dc38685c22ff09afced019cef47a9451ee6f3eb4192f4697b47cf022875.source'
    title = ET.fromstring(read(title_raw, '1d177c79bf6e77a37707b94c30beae19ad8bc7235c2e130a09380acd9555a91d'))
    title_span = title.find(".//t:ab[@{http://www.w3.org/XML/1998/namespace}id='MP0439_trc-p1']", ns)
    if title_span is None or 'friyag i pad namewar darig' not in norm(' '.join(title_span.itertext())):
        raise ValueError('Titleholder source binding changed')
    source9 = re.findall(r'<li[^>]*>(.*?)</li>', iedc['folios'][0]['transcription'], re.S)[8]
    if norm(source9) != norm('ud wizārēm ud ēn nāmag man pad gugāy-muhrīhā ī Xwadāgerd āwišt'):
        raise ValueError('IEDC line9 changed')
    # Keep source editions separate. The first predicate continues the prior sentence;
    # the online line9 translation corresponds only to the closing sealing clause.
    source9_text = html.unescape(re.sub('<[^>]+>', '', source9)).strip()
    closing = source9_text.removeprefix('ud wizārēm ').strip()
    if closing == source9_text or norm(closing) != norm('ud ēn nāmag man pad gugāy-muhrīhā ī Xwadāgerd āwišt'):
        raise ValueError('Closing-clause boundary changed')
    online_target9 = re.findall(r'<li[^>]*>(.*?)</li>', iedc['folios'][0]['translation'], re.S)[8]
    online_target9 = html.unescape(re.sub('<[^>]+>', '', online_target9)).strip()
    live_html = data[CAPTURE + 'iedc1036-07707cd2ec78b4b612de314bd2af78b2dd87434c897a032a85ee88527749e87d.html'].decode('utf8')
    if norm(source9_text) not in norm(live_html) or norm(online_target9) not in norm(live_html):
        raise ValueError('Archived clause is not present in captured online edition')
    raw = ET.fromstring(read(raw_path, doc['source']['sha256']))
    english = raw.find(".//t:ab[@{http://www.w3.org/XML/1998/namespace}id='MP0035_trans-p1']", ns)
    if english is None:
        raise ValueError('Missing separately attributed OpenAMPD English layer')
    lb9 = english.find("t:lb[@n='9']", ns)
    if lb9 is None or not lb9.tail or 'I sealed' not in lb9.tail:
        raise ValueError('OpenAMPD sealing presentation changed')
    translit9 = raw.find(".//t:ab[@{http://www.w3.org/XML/1998/namespace}id='MP0035_trl-p1']/t:lb[@n='9']", ns)
    if translit9 is None or not translit9.tail:
        raise ValueError('Missing separately attributed OpenAMPD transliteration')
    inspection = json.loads(data['resources/local/own-analysis-diagnostic-20261002/sense-role-check/primary-inspection.json'])
    eligibility = {'id': 'BERK34_RECTO_CLOSING_SEALING_CLAUSE', 'family': 'QOM_CENTRAL_IRAN',
        'use': 'RESEARCH_ELIGIBILITY_ONLY_NOT_MODEL_INPUT_OR_TRAINING',
        'iedc_edition': {'identity': 'IEDC1036', 'source_layer': 'transcription', 'source_full_line9': source9_text,
            'selected_source_clause': closing, 'selected_source_locator': 'recto line9, after ud wizārēm',
            'selected_source_sha256': hashlib.sha256(closing.encode('utf8')).hexdigest(),
            'published_english_line9': online_target9, 'actor_presentation': 'UNSTATED_PASSIVE',
            'persian_reference_qualified': False},
        'openampd_edition': {'identity': 'MP0035', 'raw_path': raw_path, 'raw_sha256': doc['source']['sha256'],
            'layers': [v['type'] for v in doc['layers']], 'published_english_full_line9': lb9.tail.strip(),
            'published_transliteration_full_line9': translit9.tail.strip(),
            'actor_presentation': 'FIRST_PERSON_ACTIVE',
            'latin_phonetic_source_present': False, 'automatic_cross_edition_pairing_allowed': False},
        'benfey_analysis': {'doi': inspection['benfey']['doi'], 'locator': inspection['benfey']['locator'],
            'claims': inspection['benfey']['attributed_relations'], 'actor_disposition': 'TENTATIVE_NOT_ADJUDICATED',
            'raw_pdf_bytes_frozen': False, 'certain_corrective_target_allowed': False},
        'unresolved': ['Edition/year/page bibliography reconciliation', 'Source-qualified complete lexical inventories and lemma/category bindings',
            'Independent reference qualification; no certified Persian reference', 'Actor interpretation not adjudicated',
            'Full historical inference exposure unknown', 'No new work family'],
        'comparison_admitted': False, 'training_admitted': False}
    prior_hits = {name: {'attachments': hits(attached, terms), 'queries': hits(queries, terms)} for name, terms in {
        'berk34': ['MP0035', 'IEDC1036', 'Berk. 34', 'Xwadāgerd', 'Xwadāgird', 'ēn nāmag man pad gugāy'],
        'titleholder': ['Friyag', 'Namēwar', 'dārīg']}.items()}
    if any(v for group in prior_hits.values() for v in group.values()):
        raise ValueError('A candidate spelling now occurs in prior aid')
    membership = {}
    for path, payload in data.items():
        if not path.endswith('.jsonl') or 'evidence/evidence' in path:
            continue
        records = [json.loads(s) for s in payload.splitlines()]
        identifiers = [str(r.get('id', r.get('unit_id', ''))) + ' ' + ' '.join(r.get('parent_ids', [])) for r in records]
        membership[path] = {ident: sum(ident in s for s in identifiers) for ident in ('MP0035', 'IEDC1036', 'MP0439')}
    journal = json.loads(data['experiments/dose-acquisition-20260930/live-execution/recovered/dose/training/run.json'])
    dose = {ident: sum(ident in s for s in journal['ordered_ids']) for ident in ('MP0035', 'IEDC1036', 'MP0439')}
    if dose != {'MP0035': 0, 'IEDC1036': 0, 'MP0439': 4}:
        raise ValueError('Later selected witness exposure changed')
    return {'purpose': 'SOURCE_IDENTITY_AND_BOUNDED_NOVELTY_ONLY', 'input_sha256': PINS,
            'corrected_witness': {'OpenAMPD': 'MP0035', 'IEDC': 'IEDC1036', 'shelfmark': 'Berk. 34, recto', 'raw_path': raw_path, 'raw_sha256': doc['source']['sha256']},
            'prior_attachment_count': 58, 'prior_distinct_sources': 56, 'prior_query_count': 24,
            'prior_source_spelling_hits': prior_hits, 'membership_ids_only': membership, 'later_forwards_ids_only': dose,
            'scoped_eligibility_record': eligibility,
            'analysis_disposition': {'berk34': 'ATTRIBUTED_TENTATIVE_ANALYSIS_ACTOR_NOT_STATED_IN_PASSIVE_ONLINE_RENDERING', 'titleholder': 'TITLE_LOCATION_ONLY_NOT_TRANSFER_ROLE'},
            'reference_gold_claim_allowed': False, 'exhaustive_unseen_claim_allowed': False,
            'complete_cases_admitted': 0, 'training_allowed': False, 'paid_launch_allowed': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    result = build()
    payload = encoded(result)
    if parser.parse_args().write:
        OUT.write_bytes(payload)
    elif OUT.read_bytes() != payload:
        raise ValueError('Saved occurrence receipt differs from replay')
    print(json.dumps({'status': 'PASS_IDENTITY_BOUNDED_SCOPE_ONLY', 'ledger_sha256': hashlib.sha256(payload).hexdigest(), 'complete_cases_admitted': 0}))
