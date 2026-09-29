"""Independent raw-response fidelity and lexical prompt-scope audit. Offline; no training."""
import collections
import hashlib
import json
from pathlib import Path
import re
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PINS = {}

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def read(name):
    raw = (ROOT / name).read_bytes()
    PINS[name] = digest(raw)
    return [json.loads(x) for x in raw.decode('utf8').splitlines()] if name.endswith('.jsonl') else json.loads(raw)

def norm(text):
    return ' '.join(unicodedata.normalize('NFC', text).split())

def forms(tree):
    nodes = tree.findall('trc')
    assert len(nodes) == 1
    node = nodes[0]
    if len(node):
        assert all(x.tag == 'form' and not len(x) for x in node)
        assert not norm(node.text or '') and not any(norm(x.tail or '') for x in node)
        return [norm(x.text or '') for x in node]
    return [norm(node.text or '')]

def canon(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf8')

def main():
    fa = read('resources/local/data-qualification-20260928/persian-v1/qualified.jsonl')
    review = read('experiments/data-qualification-20260928/mmp-review.json')
    resources = {r['id']: r for r in read(review['source_path'])}
    observations = {r['id']: r for r in read(review['original_xml_observations_path'])}
    assert PINS[review['source_path']] == review['source_sha256']
    assert PINS[review['original_xml_observations_path']] == review['original_xml_observations_sha256']
    release_fa = read('resources/local/data-qualification-20260928/ready-v1/lexical-fa.jsonl')
    release_mmp = read('resources/local/data-qualification-20260928/ready-v1/lexical-mmp-en.jsonl')
    release = {r['id']: r for r in release_fa + release_mmp}
    assert len(fa) == len(release_fa) == 2676 and len(release_mmp) == 1426
    audits = {r['id']: r for r in read('resources/local/mixed-supervision-20260929/data/row-audit.jsonl')}
    selected = {r['id']: i for i, r in enumerate(read('resources/local/mixed-supervision-20260929/data/train.jsonl'), 1)}
    raw_cache = {}
    def raw_entries(name, expected):
        if name not in raw_cache:
            entries = read(name)['data']['entries']
            raw_cache[name] = {str(x['id']): x for x in entries}
            assert len(raw_cache[name]) == len(entries), name
        assert PINS[name] == expected, name
        return raw_cache[name]
    ledger, flags = [], collections.defaultdict(list)
    for r in fa:
        rid = r['id']
        original = resources[r['source_resource_id']]
        f = r['learning_fields']
        target = f['complete_meaning_inventory_as_published']
        assert original['forms'] == f['forms_as_published']
        assert original['catalogue_attribution'] == r['source_attribution']
        assert f['source_scope'] == r['source_attribution']['title']
        assert r['source_attribution']['source_languages'] == ['pal']
        assert r['source_attribution']['target_languages'] == ['fas']
        context = {'source_scope': f['source_scope'], 'source_language': 'pal', 'target_language': 'fas', 'stratum': r['stratum']}
        assert r['stratum'] == ('MIDDLE_PERSIAN_TRANSMISSION_WITH_PARTHIAN_LAYER' if r['collection'] in {'da','yz'} else 'BOOK_MIDDLE_PERSIAN')
        assert release[rid]['learning'] == {'source': f['forms_as_published'], 'target': target, 'context': context}
        assert {x['id'] for x in r['source_pointers']} == set(r['observation_ids'])
        evidence = []
        for pointer in r['source_pointers']:
            oid = pointer['id']
            assert oid.split(':')[1] == r['collection']
            assert '/'+r['collection']+'/restful/' in pointer['source_url']
            name = 'sources/local/public-texts-2026-09-20/' + pointer['raw_file']
            entry = raw_entries(name, pointer['raw_sha256'])[oid.rsplit(':',1)[1]]
            xml = entry['xml']
            tree = ET.fromstring(xml)
            assert tree.attrib['id'] == oid.rsplit(':',1)[1]
            assert xml == observations[oid]['source_record']['xml']
            assert forms(tree) == f['forms_as_published'], oid
            senses = tree.findall('sense')
            assert len(senses) == 1 and not len(senses[0])
            assert norm(senses[0].text or '') == target, oid
            assert not tree.findall('gramm'), oid
            evidence.append({'observation_id': oid, 'raw_file': name, 'xml_sha256': digest(xml.encode('utf8'))})
        if re.search('[a-zA-Z]', target): flags['fa_target_embedded_latin_etymology_or_forms'].append(rid)
        if re.search(r'نک\.|واژه بالا', target): flags['fa_target_unresolved_relative_cross_reference'].append(rid)
        assert re.search('[\u0600-\u06ff]', target), rid
        assert target.count('(') == target.count(')') and target.count('[') == target.count(']'), rid
        if len(target)>80 or re.search(r'\d|[؟?]|[<>=:؛]|نک\.|در ترکیب|مخفف|ضمیر|حرف|فعل|مصدر|صفت|ماضی|مضارع|مجهول',target):
            flags['fa_annotated_or_long_target_reviewed'].append(rid)
        ledger.append({'id': rid, 'task': 'lexical-fa', 'source_fidelity': 'PASS', 'target_sha256': digest(target.encode('utf8')), 'evidence': evidence})
    mraw = raw_entries(review['raw_xml_response_path'], review['raw_xml_response_sha256'])
    mscope = {x['resource_id']: x for x in review['qualified_scopes']}
    assert set(mscope) == {r['id'] for r in release_mmp} == set(review['qualified_resource_ids'])
    for r in release_mmp:
        rid = r['id']; s = mscope[rid]; original = resources[rid]
        entry = mraw[rid.rsplit(':',1)[1]]; xml = entry['xml']; tree = ET.fromstring(xml)
        assert xml == observations[original['observation_ids'][0]]['source_record']['xml']
        assert digest(xml.encode('utf8')) == s['source_xml_sha256']
        assert [norm(x.text or '') for x in tree.findall('lang')] == ['MP']
        assert forms(tree) == r['learning']['source'] == original['forms']
        senses = tree.findall('sense'); assert len(senses) == 1 and not len(senses[0])
        meaning = norm(senses[0].text or '')
        assert meaning == original['meaning_as_published']
        assert digest(meaning.encode('utf8')) == s['original_meaning_sha256']
        selected_text = ''.join(meaning[a:b] for a,b in s['target_spans_unicode_codepoints_half_open'])
        assert selected_text == r['learning']['target'] == s['expected_complete_selected_text']
        assert ' '.join((tree.findtext('gramm') or '').split()) == s['pos_grammar_as_published'] == r['learning']['context']['grammar_as_published']
        assert len(tree.findall('gramm')) == 1 and not len(tree.find('gramm'))
        assert len(original['observation_ids']) == 1
        assert r['learning']['context'] == {'grammar_as_published': s['pos_grammar_as_published'], 'source_scope': original['catalogue_attribution']['title'], 'source_language': 'pal', 'target_language': 'eng', 'stratum': 'MANICHAEAN_MIDDLE_PERSIAN'}
        all_spans = sorted(s['target_spans_unicode_codepoints_half_open'] + s['evidence_only_excluded_paratext_spans'])
        assert all_spans[0][0] == 0 and all_spans[-1][1] == len(meaning)
        assert all(a[1] == b[0] for a,b in zip(all_spans,all_spans[1:]))
        if s['evidence_only_excluded_paratext_spans']: flags['mmp_excluded_tails_reviewed'].append(rid)
        if re.search(r'\b(?:Cf\.|Boyce)', selected_text): flags['mmp_target_contains_bibliographic_or_cross_reference_label'].append(rid)
        ledger.append({'id': rid, 'task': 'lexical-mmp-en', 'source_fidelity': 'PASS', 'target_sha256': digest(selected_text.encode('utf8')), 'evidence': [{'observation_id': original['observation_ids'][0], 'raw_file': review['raw_xml_response_path'], 'xml_sha256': digest(xml.encode('utf8'))}]})
    groups = collections.defaultdict(list)
    for r in release.values():
        rid = r['id']; text = canon(r['learning']).decode('utf8')
        if '\ufffd' in text or any(unicodedata.category(c) in {'Cs','Co'} for c in text): flags['damaged_or_private_use_unicode'].append(rid)
        if any(unicodedata.category(c) == 'Cf' and c not in {'\u200c','\u200d'} for c in text): flags['format_controls'].append(rid)
        key = canon({'task':r['task'], 'source':r['learning']['source'], 'context':r['learning']['context']})
        groups[key].append(rid)
    collisions = []
    for ids in groups.values():
        if len(ids) < 2: continue
        targets = {release[x]['learning']['target'] for x in ids}
        kept = [x for x in ids if x in audits]
        assert len({audits[x]['prompt_sha256'] for x in kept}) <= 1
        collisions.append({'ids': ids, 'task': release[ids[0]]['task'], 'different_targets': len(targets)>1,
            'observation_ids': {x: [e['observation_id'] for e in next(y for y in ledger if y['id']==x)['evidence']] for x in ids},
            'selected_positions': {x:selected[x] for x in ids if x in selected},
            'prepared_prompt_sha256': audits[kept[0]]['prompt_sha256'] if kept else None,
            'disposition': 'HOLD_COMPLETE_INVENTORY_PROMPT_SCOPE' if len(targets)>1 else 'EXACT_DUPLICATE_EXPECTED_DEDUP'})
    distinct_fa = set('dk8:197 dmx:182 dmx:196 dmx:395 dmx:582 dmx:678 dmx:695 dmx:928 dmx:975 dmx:1032 gbd:18 gbd:264 gbd:285 gbd:338 gbd:417 gbd:510 gbd:551 gbd:567 gbd:625 gbd:647 gbd:653 gbd:655 gbd:674 gbd:754 raf:144'.split())
    for collision in collisions:
        oids = {oid.removeprefix('kosh:') for values in collision['observation_ids'].values() for oid in values}
        collision['manual_adjudication'] = ('EXACT_DUPLICATE' if not collision['different_targets'] else
            'PUBLISHED_DISTINCT_SENSE_OR_GRAMMATICAL_ROLE_NO_INPUT_DISCRIMINATOR' if collision['task']=='lexical-mmp-en' or oids & distinct_fa else
            'PUBLISHED_OVERLAPPING_WORDING_OR_EXPANDED_INVENTORY_NOT_ONE_UNIQUE_COMPLETE_TARGET')
    for row in ledger:
        row['selected_position'] = selected.get(row['id'])
        row['prepared_pool_present'] = row['id'] in audits
        row['semantic_certification'] = 'NOT_EXPERT_CERTIFIED'
    summary = {'release_rows':len(ledger), 'fa':len(fa), 'mmp':len(release_mmp), 'source_fidelity_pass':len(ledger),
        'raw_response_files':len(raw_cache), 'raw_xml_observations_compared':sum(len(x['evidence']) for x in ledger),
        'prepared_pool_rows':sum(x['prepared_pool_present'] for x in ledger),
        'selected_rows':sum(x['selected_position'] is not None for x in ledger),
        'collision_groups_by_task':dict(collections.Counter(x['task'] for x in collisions if x['different_targets'])),
        'collision_rows_by_task':dict(collections.Counter(task for x in collisions if x['different_targets'] for task in [x['task']]*len(x['ids']))),
        'collision_rows_selected':sum(len(x['selected_positions']) for x in collisions if x['different_targets']),
        'collision_groups_multiple_targets_selected':sum(len(x['selected_positions'])>1 for x in collisions if x['different_targets']),
        'flag_counts':{k:len(v) for k,v in flags.items()}}
    result = {'scope':'ALL_RELEASED_FA_AND_MMP_SOURCE_FIDELITY_PLUS_CROSS_RECORD_SCOPE', 'training_allowed':False,
        'status':'HOLD_PENDING_PROMPT_SCOPE_REPAIR', 'summary':summary, 'input_sha256':dict(sorted(PINS.items())),
        'flags':dict(flags), 'collisions':collisions, 'coverage':ledger,
        'flag_dispositions': {
            'fa_target_embedded_latin_etymology_or_forms':'SOURCE_FAITHFUL_MIXED_GLOSS_AND_NOTE_SCOPE; preserve semantic information but separate typed notes before any translation-style target use',
            'fa_target_unresolved_relative_cross_reference':'HOLD_OR_RESOLVE_SOURCE_NOTE; da68 contains an out-of-record previous-word reference, not a proven wrong definition',
            'fa_annotated_or_long_target_reviewed':'READ_ALL_MATCHES; valid alternatives, grammatical/contextual senses retained; annotation is not automatically an error',
            'mmp_excluded_tails_reviewed':'READ_ALL_544; no demonstrated missing generic sense; bibliographic, cross-reference, orthographic, etymological and attestation details remain provenance',
            'mmp_target_contains_bibliographic_or_cross_reference_label':'MMP3127_AND4217_BOYCE_ATTRIBUTION; MMP4856_CF_CROSS_REFERENCE: typed separation advised, no invented target',
            'damaged_or_private_use_unicode':'REQUIRES_MANUAL_HOLD_IF_PRESENT', 'format_controls':'REQUIRES_MANUAL_HOLD_IF_PRESENT'},
        'limits':['Every declared form and target was compared to archived XML; this does not prove the source dictionary is correct.',
            'All 544 discarded MMP tails and all 71 unequal-target collision groups were read; no claim of expert retranslation of all 4102 entries.',
            'No training, model inference, cloud use, network, installs, credentials, or source edits.']}
    destination = HERE/'lexical-fa-mmp-audit.json'
    destination.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()
