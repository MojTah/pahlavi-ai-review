"""Offline v2 lexical projection: exact-source spans, inclusive entry inventories.

No training or network. Original released files remain immutable. The callable
returns (projections, changes, holds); the CLI writes only versioned local output
and a metadata-only decision ledger beside this file.
"""
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
READY = 'resources/local/data-qualification-20260928/ready-v1/'
OUT = ROOT / 'resources/local/training-ready-v2-20260929/lexical'
TASKS = {'lexical-fa', 'lexical-en', 'lexical-mmp-en'}
PINS = {
    READY+'lexical-fa.jsonl': '7979a688dc73a67f646920a668fbdeed6d1e21eb3f10f3810a59de9c427290fe',
    READY+'lexical-en.jsonl': '4d8c2489eca369d0d11a3364f5844cb5440d32eb53777c4ad138f5aff16c0f48',
    READY+'lexical-mmp-en.jsonl': '8411819339113f16ba45dab1c67ce8a044cb6ec5df3d589e912772ba207ff2aa',
    'resources/local/data-qualification-20260928/persian-v1/qualified.jsonl': '57e01d50cba13053a4401d1a64b6ab93c650b32c6aaed94123630bea85415cde',
}

# Each split was read against the exact archived XML. No generic punctuation
# heuristic is allowed to turn a definition into an etymology or vice versa.
SPLITS = {
    'kosh:da:3': ('نهادن', ' > dā√ + پیشوند ni', 'etymology'),
    'kosh:da:42': ('ناهم جنس', ' = -jud، جدا (جد) + sardag', 'etymology'),
    'kosh:da:56': ('گناهیدن، گناه کردن', ' > winās = گناه', 'etymology'),
    'kosh:da:58': ('برهنه پایان', ' = wrahn، برهنه + pāy، پای، پا', 'etymology'),
    'kosh:da:59': ('پاک کنند، پیرایند، ویرایند', ' > rād√، آماده شدن، آماده کردن، آراستن', 'etymology'),
    'kosh:da:68': ('بدستی، یک وجبی', ' = watist (نک. واژه بالا) + īg- پسوند نسبت', 'resolved_etymology_cross_reference'),
    'kosh:da:69': ('زین افزار، جنگ افزار', '، -zēn', 'related_form'),
    'kosh:da:76': ('افکندن', ' > kan√ + پیشوند -apa', 'etymology'),
    'kosh:da:83': ('موزه، پای افزار', ' > maoc√', 'etymology'),
    'kosh:da:84': ('پیش بند چرمین', ': -mašk مشک، پوست', 'etymology'),
    'kosh:da:85': ('رفتن', ' > -rap√', 'etymology'),
    'kosh:da:96': ('پیوند', ': band + paiti√', 'etymology'),
    'kosh:da:101': ('نیرومند', ': -tag، نیرو، زور + īg- (نسبت)', 'etymology'),
    'kosh:yz:70': ('یاد داد، تعلیم دادن', '= √kaš < češt + نام', 'etymology'),
}
SPECIAL = {
    'kosh:dmx:107': ('این واژه ترکیبی است از u: "و" + š- : "ش"', {
        'sense_type': 'compound_components_as_published',
        'components': [{'forms': ['u'], 'senses': 'و'}, {'forms': ['š-'], 'senses': 'ش'}],
    }, 'composition_scoped_in_target'),
    'kosh:dmx:550': ('1- آفریدن brēhēnīd:آفرید brēhēnīhist:آفریده شد 2- مقدر کردن', {
        'senses': [{'number_as_published': '1', 'text': 'آفریدن'},
                   {'number_as_published': '2', 'text': 'مقدر کردن'}],
        'related_forms': [{'forms': ['brēhēnīd'], 'senses': 'آفرید'},
                          {'forms': ['brēhēnīhist'], 'senses': 'آفریده شد'}],
    }, 'inflectional_subentries_scoped_in_target'),
    'kosh:yz:13': ('اُفتاد. بن ماضی از ōpastan شیرازی کُهن', {
        'senses': 'اُفتاد.',
        'related_forms': [{'forms': ['ōpastan'],
                           'headword_relation_to_this_form_as_published': 'بن ماضی از',
                           'qualification_as_published': 'شیرازی کُهن'}],
    }, 'derivation_with_source_qualification_preserved'),
}
MMP_NOTES = {
    'kosh:mmp:3127': (' [Boyce]', 'attribution'),
    'kosh:mmp:4217': (' [Boyce]', 'attribution'),
    'kosh:mmp:4856': (" Cf. t'.", 'cross_reference'),
}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def value_hash(value):
    return digest(canonical(value).encode('utf8'))


def read(name, expected=None):
    raw = (ROOT / name).read_bytes()
    expected = expected or PINS.get(name)
    if expected and digest(raw) != expected:
        raise ValueError('Source pin changed: ' + name)
    return [json.loads(x) for x in raw.decode('utf8').splitlines() if x.strip()] if name.endswith('.jsonl') else json.loads(raw)


def norm(text):
    return ' '.join(unicodedata.normalize('NFC', text).split())


def input_key(row):
    return canonical([row['task'], row['learning']['source'], row['learning']['context']])


def build_lexical(projections):
    """Retain source entries, merge identical inputs, separate reviewed apparatus.

    Exact original released inputs are required; invoking on an already rewritten
    or silently modified corpus fails. Top-level provenance is never model input.
    """
    release = {r['id']: r for task in sorted(TASKS) for r in read(READY+task+'.jsonl')}
    parents = [r for r in projections if r['task'] in TASKS]
    if len(parents) != len(release) or {r['id'] for r in parents} != set(release):
        raise ValueError('All 7608 original lexical parents must be supplied exactly once')
    for r in parents:
        if r['learning'] != release[r['id']]['learning'] or r['task'] != release[r['id']]['task']:
            raise ValueError('Original learning projection changed: ' + r['id'])
    fa = {r['id']: r for r in read('resources/local/data-qualification-20260928/persian-v1/qualified.jsonl')}
    review = read('experiments/data-qualification-20260928/mmp-review.json')
    mscopes = {r['resource_id']: r for r in review['qualified_scopes']}
    raw_cache = {}

    def source_xml(name, expected, sid):
        if name not in raw_cache:
            records = read(name, expected)['data']['entries']
            raw_cache[name] = {str(x['id']): x for x in records}
            if len(raw_cache[name]) != len(records):
                raise ValueError('Duplicate source entry id: ' + name)
        xml = raw_cache[name][sid]['xml']
        if '<!DOCTYPE' in xml.upper() or '<!ENTITY' in xml.upper():
            raise ValueError('Unexpected XML declaration')
        return ET.fromstring(xml), {'raw_file': name, 'raw_sha256': expected,
                                   'entry_id': sid, 'xml_sha256': digest(xml.encode('utf8'))}

    def form_values(tree):
        node = tree.find('trc')
        return [norm(x.text or '') for x in node] if len(node) else [norm(node.text or '')]

    def source_evidence(row):
        rid, learning = row['id'], row['learning']
        if row['task'] == 'lexical-fa':
            evidence = []
            for pointer in fa[rid]['source_pointers']:
                oid = pointer['id']
                tree, pin = source_xml('sources/local/public-texts-2026-09-20/'+pointer['raw_file'],
                                       pointer['raw_sha256'], oid.rsplit(':', 1)[1])
                assert form_values(tree) == learning['source']
                assert norm(tree.findtext('sense')) == learning['target']
                pin['observation_id'] = oid
                evidence.append(pin)
            return evidence
        if row['task'] == 'lexical-mmp-en':
            tree, pin = source_xml(review['raw_xml_response_path'], review['raw_xml_response_sha256'], rid.rsplit(':', 1)[1])
            assert form_values(tree) == learning['source']
            assert tree.findtext('lang') == 'MP'
            assert ' '.join(tree.findtext('gramm').split()) == learning['context']['grammar_as_published']
            meaning, scope = norm(tree.findtext('sense')), mscopes[rid]
            assert digest(meaning.encode('utf8')) == scope['original_meaning_sha256']
            assert ''.join(meaning[a:b] for a, b in scope['target_spans_unicode_codepoints_half_open']) == learning['target']
            pin.update(observation_id=rid.removeprefix('recovered:'),
                       selected_source_spans=scope['target_spans_unicode_codepoints_half_open'])
            return [pin]
        loc = release[rid]['origin']['source_scope_paths']
        oid = loc['observation_id']
        tree, pin = source_xml('sources/local/public-texts-2026-09-20/'+loc['raw_file'], loc['raw_sha256'], oid.rsplit(':', 1)[1])
        assert pin['xml_sha256'] == loc['source_xml_sha256']
        lookup = {}
        def visit(node, path):
            lookup[path] = node
            for i, child in enumerate(node):
                visit(child, f'{path}/{child.tag}[{i}]')
        visit(tree, '/entry')
        assert [''.join(c.itertext()) for p in loc['form_paths'] for c in lookup[p] if c.tag == 'trc'] == learning['source']
        senses = []
        for path in loc['sense_paths']:
            node, components = lookup[path], []
            for child in node:
                if child.tag in {'eg', 'q'}:
                    continue
                assert child.tag in {'tr', 'def', 'gram', 'gramGrp', 'usg'}
                item = {'kind': child.tag, 'text': child.text if child.tag == 'gramGrp' else ''.join(child.itertext()), 'attributes': dict(child.attrib)}
                if child.tag == 'gramGrp':
                    item['components'] = [{'kind': c.tag, 'text': ''.join(c.itertext()), 'attributes': dict(c.attrib), 'tail': c.tail} for c in child if c.tag not in {'eg', 'q'}]
                components.append(item)
            senses.append({'number_as_published': node.get('n'), 'components': components})
        assert senses == learning['target']
        pin.update(observation_id=oid, form_paths=loc['form_paths'], sense_paths=loc['sense_paths'],
                   entry_number_as_published=tree.get('n'), entry_label_as_published=tree.get('{http://www.w3.org/XML/1998/namespace}id'))
        return [pin]

    groups, individual = {}, {}
    for row in parents:
        rid, old = row['id'], row['learning']['target']
        evidence = source_evidence(row)
        oids = [p['observation_id'] for p in evidence]
        entry, notes = {'senses': deepcopy(old)}, []
        hits = [oid for oid in oids if oid in SPLITS or oid in SPECIAL or oid in MMP_NOTES]
        assert len(hits) <= 1
        if hits:
            oid = hits[0]
            if oid in SPLITS:
                gloss, suffix, kind = SPLITS[oid]
                assert old == gloss+suffix, oid
                entry = {'senses': gloss}
                notes = [{'kind': kind, 'text_as_published': suffix, 'original_target_span': [len(gloss), len(old)]}]
                if oid == 'kosh:da:68':
                    pointer = fa[rid]['source_pointers'][0]
                    tree, pin = source_xml('sources/local/public-texts-2026-09-20/'+pointer['raw_file'], pointer['raw_sha256'], '67')
                    assert form_values(tree) == ['watist'] and norm(tree.findtext('sense')) == 'بدست، وجب'
                    pin['observation_id'] = 'kosh:da:67'
                    notes[0]['resolved_reference'] = {**pin, 'forms': ['watist'], 'senses': 'بدست، وجب',
                        'basis': 'Exact explicitly named form in same collection entry 67 preceding entry 68; not numeric adjacency alone'}
            elif oid in SPECIAL:
                expected, entry, kind = SPECIAL[oid]
                assert old == expected, oid
                entry = deepcopy(entry)
                notes = [{'kind': kind, 'text_as_published': old, 'original_target_span': [0, len(old)],
                          'policy': 'Meaning components and grammatical qualifiers stay in their explicit model-visible scopes'}]
            else:
                marker, kind = MMP_NOTES[oid]
                assert old.count(marker) == 1
                pos = old.index(marker)
                entry = {'senses': old[:pos]+old[pos+len(marker):]}
                notes = [{'kind': kind, 'text_as_published': marker, 'original_target_span': [pos, pos+len(marker)]}]
        individual[rid] = {'entry': entry, 'notes': notes, 'sources': evidence}
        groups.setdefault(input_key(row), []).append(row)

    replacements, changes = {}, []
    for key, members in groups.items():
        output = deepcopy(members[0])
        output['parent_ids'] = [r['id'] for r in members]
        entries, seen_entries, provenance = [], {}, []
        for parent in members:
            rid, item = parent['id'], individual[parent['id']]
            entry_key = canonical(item['entry'])
            if entry_key not in seen_entries:
                seen_entries[entry_key] = len(entries)
                entries.append(item['entry'])
            entry_index = seen_entries[entry_key]
            provenance.append({'parent_id': rid, 'target_entry_index': entry_index,
                'original_source_sha256': value_hash(parent['learning']['source']),
                'original_target_sha256': value_hash(parent['learning']['target']),
                'original_learning_sha256': value_hash(parent['learning']),
                'original_target': deepcopy(parent['learning']['target']),
                'sources': item['sources'], 'notes': item['notes']})
            changes.append({'id': rid, 'task': parent['task'], 'output_id': output['id'],
                'target_entry_index': entry_index,
                'reason': 'MERGE_EXACT_INPUT_PRESERVE_ENTRY_INVENTORIES' if len(members)>1 else 'STRUCTURED_SOURCE_ENTRY_INVENTORY',
                'original_learning_sha256': value_hash(parent['learning']),
                'original_target_sha256': value_hash(parent['learning']['target']),
                'new_entry_sha256': value_hash(item['entry']),
                'apparatus_reviewed': bool(item['notes']),
                'sources': item['sources'],
                'note_dispositions': [{k: v for k, v in n.items() if k not in {'text_as_published', 'resolved_reference'}} |
                    ({'resolved_reference_observation_id': n['resolved_reference']['observation_id'],
                      'resolved_reference_xml_sha256': n['resolved_reference']['xml_sha256']} if 'resolved_reference' in n else {}) for n in item['notes']]})
        output['learning']['target'] = {'entries': entries}
        output['lexical_provenance'] = {'policy': 'Source-scoped, inclusive qualified release; all different source entry inventories remain separate; exact equal entry inventories share one target index.',
                                        'entries': provenance, 'expert_certified': False}
        replacements[members[0]['id']] = output
    result = [deepcopy(row) if row['task'] not in TASKS else replacements[row['id']]
              for row in projections if row['task'] not in TASKS or row['id'] in replacements]
    assert len({input_key(r) for r in result if r['task'] in TASKS}) == len(replacements)
    assert Counter(p for r in replacements.values() for p in r['parent_ids']) == Counter(r['id'] for r in parents)
    assert sum(bool(v['notes']) for v in individual.values()) == 20
    assert len(replacements) == 7438
    return result, changes, []


def main():
    projections = read('resources/local/mixed-supervision-20260929/data/learning-projections.jsonl')
    original_hash = value_hash(projections)
    outputs, changes, holds = build_lexical(projections)
    assert value_hash(projections) == original_hash, 'Input object was mutated'
    assert build_lexical(projections) == (outputs, changes, holds), 'Replay differs'
    for corrupt in ('missing_parent', 'modified_target'):
        fixture = deepcopy(projections)
        index = next(i for i, row in enumerate(fixture) if row['task'] in TASKS)
        if corrupt == 'missing_parent':
            del fixture[index]
        else:
            fixture[index]['learning']['target'] = 'UNSUPPORTED TEST MUTATION'
        try:
            build_lexical(fixture)
        except ValueError:
            pass
        else:
            raise AssertionError('Admission failed to reject '+corrupt)
    originals = {r['id']: r for r in projections}
    for row in outputs:
        if row['task'] not in TASKS:
            assert row == originals[row['id']]
        else:
            assert row['id'] == row['parent_ids'][0]
            for p in row['lexical_provenance']['entries']:
                rid, index = p['parent_id'], p['target_entry_index']
                if not p['notes']:
                    assert row['learning']['target']['entries'][index] == {'senses': originals[rid]['learning']['target']}
    lexical = [r for r in outputs if r['task'] in TASKS]
    by_oid = {source['observation_id']: (row, entry)
              for row in lexical for entry in row['lexical_provenance']['entries']
              for source in entry['sources']}
    for oid in SPLITS.keys() | SPECIAL.keys() | MMP_NOTES.keys():
        row, provenance = by_oid[oid]
        assert provenance['notes'], oid
        target = row['learning']['target']['entries'][provenance['target_entry_index']]
        if oid in SPLITS:
            assert target == {'senses': SPLITS[oid][0]}, oid
        if oid in MMP_NOTES:
            assert MMP_NOTES[oid][0].strip() not in canonical(target), oid
    _, da68 = by_oid['kosh:da:68']
    assert da68['notes'][0]['resolved_reference']['observation_id'] == 'kosh:da:67'
    dmx550, source550 = by_oid['kosh:dmx:550']
    target550 = dmx550['learning']['target']['entries'][source550['target_entry_index']]
    assert [r['senses'] for r in target550['related_forms']] == ['آفرید', 'آفریده شد']
    assert [r['text'] for r in target550['senses']] == ['آفریدن', 'مقدر کردن']
    yz13, source13 = by_oid['kosh:yz:13']
    related13 = yz13['learning']['target']['entries'][source13['target_entry_index']]['related_forms'][0]
    assert yz13['learning']['source'] == ['ōpast']
    assert related13['forms'] == ['ōpastan']
    assert related13['headword_relation_to_this_form_as_published'] == 'بن ماضی از'
    assert 'relation_to_headword_as_published' not in related13
    merged = [r for r in lexical if len(r['parent_ids'])>1]
    summary = {'status': 'PASS_SOURCE_PROJECTION_AND_INPUT_IDENTIFIABILITY', 'training_run_authorized': False,
        'lexical_parent_rows': len(changes), 'lexical_output_rows': len(lexical),
        'merged_groups': len(merged), 'collapsed_row_count': len(changes)-len(lexical),
        'unequal_inventory_groups_resolved': sum(len({value_hash(originals[p]['learning']['target']) for p in r['parent_ids']})>1 for r in merged),
        'reviewed_apparatus_rows': sum(c['apparatus_reviewed'] for c in changes), 'holds': len(holds),
        'output_by_task': dict(Counter(r['task'] for r in lexical)),
        'all_source_targets_verified': True, 'deterministic_replay': True, 'nonlexical_unchanged': True,
        'missing_parent_rejected': True, 'modified_target_rejected': True,
        'note_scope_and_related_form_checks': True,
        'expert_semantic_certification': False}
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT/'projections.jsonl'
    path.write_text(''.join(canonical(r)+'\n' for r in outputs), encoding='utf8')
    (OUT/'changes.jsonl').write_text(''.join(canonical(r)+'\n' for r in changes), encoding='utf8')
    (OUT/'holds.jsonl').write_text('', encoding='utf8')
    decisions = {'summary': summary, 'script_sha256': digest(Path(__file__).read_bytes()), 'release_pins': PINS,
                 'projection_sha256': digest(path.read_bytes()), 'projection_path': path.relative_to(ROOT).as_posix(),
                 'parent_dispositions': changes,
                 'merged_groups': [{'id': r['id'], 'parent_ids': r['parent_ids'],
                    'target_entry_count': len(r['learning']['target']['entries']),
                    'input_sha256': digest(input_key(r).encode('utf8')),
                    'target_sha256': value_hash(r['learning']['target'])} for r in merged]}
    (HERE/'lexical-decisions.json').write_text(json.dumps(decisions, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
