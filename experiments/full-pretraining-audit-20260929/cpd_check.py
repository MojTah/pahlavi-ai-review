"""Independent raw-XML CPD audit. No qualifier/extractor imports; writes one audit JSON."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import ast
import hashlib
import json
from pathlib import Path
import re
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CPD = ROOT / 'resources/local/data-qualification-20260928/cpd'
READY = ROOT / 'resources/local/data-qualification-20260928/ready-v1/lexical-en.jsonl'
OBS = ROOT / 'resources/local/kosh-quality-20260928/complete-v4/observations.jsonl'
PUBLIC = ROOT / 'sources/local/public-texts-2026-09-20'
MIXED = ROOT / 'resources/local/mixed-supervision-20260929/data'
inputs = {}
POLICY = ROOT / 'experiments/data-qualification-20260928/cpd_qualify.py'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def load(path, jsonl=False):
    raw = path.read_bytes()
    inputs[path.relative_to(ROOT).as_posix()] = dict(bytes=len(raw), sha256=digest(raw))
    return [json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()] if jsonl else json.loads(raw)


def txt(node):
    return ''.join(node.itertext())


def node_map(root):
    result = {}
    def visit(node, path):
        result[path] = node
        for i, child in enumerate(node):
            visit(child, f'{path}/{child.tag}[{i}]')
    visit(root, '/entry')
    return result


def tree(node, path):
    return dict(path=path, tag=node.tag, attributes=dict(node.attrib), text=node.text, tail=node.tail,
                children=[tree(c, f'{path}/{c.tag}[{i}]') for i, c in enumerate(node)])


def blocks(root):
    """Independent interval partition: form starts after an intervening direct sense/xr."""
    starts, saw_meaning = [0], False
    for i, child in enumerate(root):
        if child.tag == 'form' and saw_meaning:
            starts.append(i); saw_meaning = False
        saw_meaning |= child.tag in {'sense', 'xr'}
    return [list(range(a, b)) for a, b in zip(starts, starts[1:] + [len(root)])]


def text_strings(v, path=''):
    if isinstance(v, str):
        yield path, v
    elif isinstance(v, list):
        for i, child in enumerate(v):
            yield from text_strings(child, f'{path}[{i}]')
    elif isinstance(v, dict):
        for k, child in v.items():
            yield from text_strings(child, f'{path}.{k}')


def independent_senses(nodes, paths):
    projected, omitted, flags = [], [], []
    for node, path in zip(nodes, paths):
        item = dict(number_as_published=node.get('n'), components=[])
        if set(node.attrib) - {'n'}: flags.append('UNPROJECTED_SENSE_ATTRIBUTES')
        if (node.text or '').strip(): flags.append('UNPROJECTED_SENSE_TEXT')
        for i, child in enumerate(node):
            child_path = f'{path}/{child.tag}[{i}]'
            if child.tag in {'eg', 'q'}:
                omitted.append(child_path)
                if (child.tail or '').strip(): flags.append('EXCLUDED_EXAMPLE_HAS_NONEMPTY_TAIL')
                continue
            if child.tag not in {'tr', 'def', 'gram', 'gramGrp', 'usg'}:
                flags.append('UNSUPPORTED_DIRECT_SENSE_CHILD'); continue
            component = dict(kind=child.tag, text=child.text if child.tag == 'gramGrp' else txt(child), attributes=dict(child.attrib))
            if child.tag == 'gramGrp':
                component['components'] = []
                for j, sub in enumerate(child):
                    if sub.tag in {'eg', 'q'}:
                        omitted.append(f'{child_path}/{sub.tag}[{j}]')
                        if (sub.tail or '').strip(): flags.append('EXCLUDED_GRAMMAR_EXAMPLE_HAS_TAIL')
                        continue
                    if sub.tag not in {'gram', 'number', 'mood', 'itype', 'usg'}: flags.append('UNSUPPORTED_GRAMMAR_CHILD')
                    if any(n.tag != 'hi' for n in list(sub.iter())[1:]): flags.append('SEMANTIC_INLINE_NODE')
                    component['components'].append(dict(kind=sub.tag, text=txt(sub), attributes=dict(sub.attrib), tail=sub.tail))
            elif any(n.tag != 'hi' for n in list(child.iter())[1:]):
                flags.append('SEMANTIC_INLINE_NODE')
            if (child.tail or '').strip(): flags.append('UNPROJECTED_SENSE_TAIL')
            item['components'].append(component)
        projected.append(item)
    return projected, omitted, flags


def dubious(nodes):
    return any(n.get('type') in {'doubtf', 'dobtf', 'concession'}
               or re.search(r'[?？\ufffd*\[\]…]|\.{2,}|\b(?:perhaps|probably|uncertain)\b', txt(n), re.I)
               or any(unicodedata.category(c) in {'Co', 'Cn'} for c in txt(n))
               for node in nodes for n in node.iter())


# Read only the saved edition-policy literals, never import/execute its builder.
policy_raw = POLICY.read_bytes()
inputs[POLICY.relative_to(ROOT).as_posix()] = dict(bytes=len(policy_raw), sha256=digest(policy_raw))
policy = {}
for statement in ast.parse(policy_raw.decode('utf-8')).body:
    if isinstance(statement, ast.Assign):
        for name in statement.targets:
            if isinstance(name, ast.Name) and name.id in {'CORRECTIONS', 'DELETED', 'UNRESOLVED_CORRECTION_FORMS', 'BUNDLE_EVIDENCE'}:
                policy[name.id] = ast.literal_eval(statement.value)


def hold_evidence(root, form_nodes, forms, senses, metadata, sense_flags, dangling):
    all_sense_text = '\n'.join(txt(s) for s in senses)
    return {
        'MISSING_SOURCE_FORM': not forms or not all(any(c.isalpha() for c in f) for f in forms),
        'NO_DIRECT_SENSE': not senses,
        'FORM_SENSE_ASSOCIATION_UNRESOLVED': (len(forms) > 1 or sum(any(c.tag == 'trc' for c in f) for f in form_nodes) > 1)
            and tuple(forms) not in policy['BUNDLE_EVIDENCE'],
        'UNCERTAIN_OR_DAMAGED_FORM': dubious(form_nodes),
        'UNCERTAIN_OR_DAMAGED_SENSE': dubious(senses),
        'SUPERSEDED_1986_FORM': any(f in policy['DELETED'] for f in forms),
        '1986_ADDED_SENSE_SCOPE_UNRESOLVED': any(f in policy['UNRESOLVED_CORRECTION_FORMS'] for f in forms),
        'EXPLICIT_LANGUAGE_REQUIRES_SEPARATE_POOL': any('lang' in n.attrib or '{http://www.w3.org/XML/1998/namespace}lang' in n.attrib
            for n in [root] + [n for form in form_nodes for n in form.iter()]),
        'DANGLING_XML_CROSS_REFERENCE': bool(dangling),
        'UNSCOPED_SENSE_TEXT': 'UNPROJECTED_SENSE_TEXT' in sense_flags,
        'SEMANTIC_INLINE_MARKUP': 'SEMANTIC_INLINE_NODE' in sense_flags,
        'SENSE_REFERENCE_OR_NOTE_REQUIRES_REVIEW': 'UNSUPPORTED_DIRECT_SENSE_CHILD' in sense_flags,
        'COMPLEX_GRAMMAR_SCOPE': 'UNSUPPORTED_GRAMMAR_CHILD' in sense_flags,
        'UNSCOPED_SENSE_TAIL': 'UNPROJECTED_SENSE_TAIL' in sense_flags,
        'NO_GENERIC_GLOSS_IN_SENSE': any(not any(c.tag in {'tr', 'def'} and any(ch.isalpha() for ch in txt(c)) for c in s) for s in senses),
        'COMPLEX_BLOCK_GRAMMAR_OR_USAGE': any(n.tag in {'eg', 'q', 'xr', 'ref', 'note'}
            for p, node in metadata if node.tag in {'gram', 'gramGrp', 'usg'} for n in node.iter()),
        'ENTRY_NOTE_REQUIRES_SOURCE_REVIEW': any(n.tag == 'note' for p, n in metadata),
        '1986_GENERIC_SENSE_CHECK_MISMATCH': any(f in forms and not all(t in all_sense_text for t in terms)
            for f, page, terms in policy['CORRECTIONS']),
    }


manifest = load(CPD / 'manifest.json')
qualified, held, released = (load(p, True) for p in (CPD / 'qualified.jsonl', CPD / 'held.jsonl', READY))
observations = [r for r in load(OBS, True) if r['collection'] == 'cpd']
observation_by_id = {r['id']: r for r in observations}
qmap, hmap, rmap = ({r['id']: r for r in data} for data in (qualified, held, released))
pool_rows = [r for r in load(MIXED / 'pool.jsonl', True) if r['task'] == 'lexical-en']
selected_rows = [r for r in load(MIXED / 'train.jsonl', True) if r['task'] == 'lexical-en']
pool = {r['id']: r for r in pool_rows}
selected = {r['id'] for r in selected_rows}
assert len(pool_rows) == len(pool) == 3506 and set(pool) == set(rmap)
assert len(selected_rows) == len(selected) == 64 and selected <= set(pool)
raw_files, raw_entries = {}, {}
for observation in observations:
    path = observation['raw_file']
    if path not in raw_files:
        raw_files[path] = load(PUBLIC / path)['data']['entries']
        assert inputs[(PUBLIC / path).relative_to(ROOT).as_posix()]['sha256'] == observation['raw_sha256']
        raw_entries[path] = {r['id']: r for r in raw_files[path]}
    assert raw_entries[path][observation['source_record']['id']] == observation['source_record']
source = {r['id']: raw_entries[r['raw_file']][r['source_record']['id']] for r in observations}
assert len(observations) == len(source) == 3103
assert {r['source_record']['id'] for r in observations} == {r['id'] for rows in raw_files.values() for r in rows}
roots, maps, partitions, malformed = {}, {}, {}, []
for oid, record in source.items():
    assert '<!DOCTYPE' not in record['xml'].upper() and '<!ENTITY' not in record['xml'].upper()
    try:
        roots[oid] = ET.fromstring(record['xml'])
    except ET.ParseError:
        malformed.append(oid); continue
    maps[oid] = node_map(roots[oid]); partitions[oid] = blocks(roots[oid])
xml_ids = {r.get('{http://www.w3.org/XML/1998/namespace}id') for r in roots.values()} - {None}
expected_units = {oid + ':block:' + str(i) for oid, b in partitions.items() for i in range(len(b))} | set(malformed)
assert len(released) == len(rmap) == len(qmap) == 3506 and set(rmap) == set(qmap)
assert len(held) == len(hmap) == 720 and not (set(qmap) & set(hmap))
assert expected_units == set(qmap) | set(hmap)
for name in ('qualified.jsonl', 'held.jsonl'):
    assert inputs[(CPD / name).relative_to(ROOT).as_posix()]['sha256'] == manifest['outputs'][name]['sha256']

ledger, component_counts, omitted_tags, held_reason_counts = [], Counter(), Counter(), Counter()
form_child_tags, form_attribute_names, source_type_counts, excluded_sense_tags = Counter(), Counter(), Counter(), Counter()
input_groups, homonym_rows, findings = defaultdict(list), [], []
all_form_strings = all_target_strings = all_target_texts = 0
flag_groups = defaultdict(list)
resolved_flags = []
for rid, disposition in [(r['id'], 'released') for r in released] + [(r['id'], 'held') for r in held]:
    row = (qmap if disposition == 'released' else hmap)[rid]
    if rid in malformed:
        assert row['reason'] == 'HELD_MALFORMED_XML'
        assert row['source_xml_sha256'] == digest(source[rid]['xml'].encode())
        held_reason_counts[row['reason']] += 1
        ledger.append(dict(id=rid, disposition='held', status='MALFORMED_SOURCE_REMAINS_HELD',
                           source_xml_sha256=digest(source[rid]['xml'].encode()), checks=['raw_entry_identity', 'malformed_xml'],
                           declared_reason_evidence={'HELD_MALFORMED_XML': True}, flags=[]))
        continue
    loc = row['source']; oid = loc['observation_id']; root = roots[oid]; lookup = maps[oid]
    segment = partitions[oid][loc['block_index']]
    scope_nodes = [root[i] for i in segment]
    expected_forms = [f'/entry/form[{i}]' for i in segment if root[i].tag == 'form']
    expected_senses = [f'/entry/sense[{i}]' for i in segment if root[i].tag == 'sense']
    flags = []
    source_checks = dict(raw_xml_hash=digest(source[oid]['xml'].encode()) == loc['source_xml_sha256'],
                         raw_locator=all(loc[key] == observation_by_id[oid][key] for key in ('raw_file', 'raw_sha256', 'source_url')),
                         form_scope=loc['form_paths'] == expected_forms, sense_scope=loc['sense_paths'] == expected_senses)
    forms = [txt(c) for p in expected_forms for c in lookup[p] if c.tag == 'trc']
    source_checks['form_text'] = forms == row['form_bundle']
    sense_nodes = [lookup[p] for p in expected_senses]
    expected_target, omitted, sense_flags = independent_senses(sense_nodes, expected_senses)
    refs = [n for item in scope_nodes for n in item.iter() if n.tag == 'ref']
    dangling = [n for n in refs if n.get('target', '').removeprefix('#') not in xml_ids]
    metadata = [(f'/entry/{root[i].tag}[{i}]', root[i]) for i in segment if root[i].tag not in {'form', 'sense'}]
    if disposition == 'released':
        current = rmap[rid]
        expected_annotations = [tree(n, p) for p, n in metadata if n.tag in {'gram', 'gramGrp', 'usg'}]
        expected_exclusions = sorted(set(omitted + [p for p, n in metadata if n.tag not in {'gram', 'gramGrp', 'usg'}]))
        source_checks.update(sense_tree=expected_target == row['senses'] == current['learning']['target'],
                             sense_count=len(expected_senses) == row['sense_count'],
                             scope_annotations=expected_annotations == row['scope_annotations'] == current['learning']['context']['scope_annotations'],
                             excluded_paths=expected_exclusions == row['excluded_context_paths'],
                             release_forms=forms == current['learning']['source'],
                             released_origin_locator=current['origin']['source_scope_paths'] == loc)
        flags += sense_flags
        if dangling: flags.append('DANGLING_REFERENCE_IN_RELEASED_BLOCK')
        for p, node in metadata:
            if p in expected_exclusions:
                omitted_tags[node.tag] += 1
                if node.tag in {'note', 'lbl'} and txt(node).strip(): flags.append('OMITTED_NOTE_OR_LABEL')
                if (node.tail or '').strip() not in {'', '|', ',', ')'}: flags.append('UNEXPECTED_TOP_LEVEL_TAIL')
        for path in expected_forms:
            form_attribute_names.update(lookup[path].attrib.keys())
            for child in lookup[path]:
                form_child_tags[child.tag] += 1
                if child.tag == 'trc' and any(n.tag != 'hi' for n in list(child.iter())[1:]): flags.append('FORM_SEMANTIC_INLINE_NODE')
        source_type_counts[root.get('type', 'unmarked')] += 1
        excluded_sense_tags.update(lookup[p].tag for p in omitted)
        if root.get('n'):
            homonym_rows.append(rid)
        strings = list(text_strings(current['learning']['source'])) + list(text_strings(current['learning']['target']))
        for path, value in strings:
            if any(unicodedata.category(c) in {'Co', 'Cn', 'Cs'} or c == '\ufffd' for c in value): flags.append('UNICODE_DAMAGE_OR_PRIVATE_CHARACTER')
            if any(unicodedata.category(c) == 'Cc' and c not in '\n\r\t' for c in value): flags.append('UNICODE_CONTROL_CHARACTER')
        for item in expected_target:
            component_counts.update(c['kind'] for c in item['components'])
        target_strings = list(text_strings(current['learning']['target']))
        all_form_strings += len(forms); all_target_strings += len(target_strings)
        target_text_count = sum(p.endswith('.text') for p, v in target_strings)
        all_target_texts += target_text_count
        key = canonical([current['learning']['source'], current['learning']['context']])
        input_groups[key].append(rid)
        if rid == 'kosh:cpd:af7f6c8954361b77a45ab410745b6c6af181fdc9:block:0':
            assert txt(lookup['/entry/lbl[3]']) == '=' and '/entry/lbl[3]' in expected_exclusions
            assert 'OMITTED_NOTE_OR_LABEL' in flags
            flags.remove('OMITTED_NOTE_OR_LABEL')
            resolved_flags.append(dict(id=rid, flag='OMITTED_NOTE_OR_LABEL', path='/entry/lbl[3]',
                resolution='Reviewed raw XML: equality label between spelling and comparative transcription evidence; no omitted gloss or grammatical qualifier. Explicitly excluded already.'))
        entry = dict(id=rid, disposition='released', source_xml_sha256=loc['source_xml_sha256'],
                     block_index=loc['block_index'], form_paths=expected_forms, sense_paths=expected_senses,
                     raw_entry_homonym_number=root.get('n'), raw_entry_type=root.get('type'),
                     form_string_count=len(forms), target_string_count=len(target_strings), target_text_count=target_text_count,
                     forms_sha256=digest(canonical(forms).encode()), target_sha256=digest(canonical(expected_target).encode()),
                     scope_sha256=digest(canonical(expected_annotations).encode()), excluded_context_nodes=len(expected_exclusions),
                     selected_in_mixed=rid in selected, checks=source_checks, flags=sorted(set(flags)))
    else:
        reasons = row.get('reasons', [row.get('reason')])
        evidence = hold_evidence(root, [lookup[p] for p in expected_forms], forms, sense_nodes, metadata, sense_flags, dangling)
        reason_checks = {reason: bool(evidence.get(reason, False)) for reason in reasons}
        held_reason_counts.update(reasons)
        source_checks['declared_hold_reasons_supported'] = all(reason_checks.values())
        entry = dict(id=rid, disposition='held', source_xml_sha256=loc['source_xml_sha256'],
                     block_index=loc['block_index'], form_paths=expected_forms, sense_paths=expected_senses,
                     form_string_count=len(forms), sense_count=len(sense_nodes), checks=source_checks,
                     declared_reasons=reasons, declared_reason_evidence=reason_checks,
                     independent_structural_flags=sorted(set(sense_flags)), dangling_reference_count=len(dangling), flags=[])
    entry['status'] = 'SOURCE_SCOPE_PASS' if all(source_checks.values()) and not flags else 'REVIEW_REQUIRED'
    for flag in sorted(set(flags)):
        flag_groups[flag].append(rid)
    for check, passed in source_checks.items():
        if not passed: flag_groups['MISMATCH:' + check].append(rid)
    ledger.append(entry)

collisions = []
for group in input_groups.values():
    if len({canonical(rmap[r]['learning']['target']) for r in group}) < 2: continue
    prefix_hashes = {digest(canonical(pool[r]['input_ids'][:pool[r]['prompt_tokens']]).encode()) for r in group}
    assert len(prefix_hashes) == 1
    numbers = [roots[qmap[r]['source']['observation_id']].get('n') for r in group]
    labels = [roots[qmap[r]['source']['observation_id']].get('{http://www.w3.org/XML/1998/namespace}id') for r in group]
    collisions.append(dict(ids=group, distinct_targets=len({canonical(rmap[r]['learning']['target']) for r in group}),
                           entry_homonym_numbers=numbers, all_have_distinct_entry_numbers=all(numbers) and len(set(numbers)) == len(numbers),
                           all_have_distinct_xml_labels=bool(all(labels) and len(set(labels)) == len(labels)),
                           source_entry_ids_distinct=len({qmap[r]['source']['observation_id'] for r in group}) == len(group),
                           token_prefix_sha256=next(iter(prefix_hashes)), selected_ids=sorted(set(group) & selected)))
collision_ids = {i for group in collisions for i in group['ids']}
for entry in ledger:
    if entry['id'] in collision_ids:
        entry['model_input_status'] = 'IDENTICAL_INPUT_DIFFERENT_TARGET_IN_RELEASED_POOL'
    elif entry['disposition'] == 'released':
        entry['model_input_status'] = 'NO_EXACT_CPD_INPUT_COLLISION_FOUND'

result = dict(status='PARTIAL', completed_utc=datetime.now(timezone.utc).isoformat(),
              source_fidelity_status='PASS' if not flag_groups else 'REVIEW_REQUIRED',
              task_identifiability_status='REVIEW_REQUIRED' if collisions else 'PASS',
              script_sha256=digest(Path(__file__).read_bytes()), inputs=inputs,
              coverage=dict(raw_entries=len(source), well_formed_entries=len(roots), malformed_entries=len(malformed),
                            raw_scoped_blocks=sum(map(len, partitions.values())), released_records=len(released), held_units=len(held),
                            actual_pool_records=len(pool_rows), actual_selected_records=len(selected_rows),
                            ledger_records=len(ledger), released_form_strings=all_form_strings,
                            released_target_strings=all_target_strings, released_target_text_strings=all_target_texts,
                            target_component_kinds=dict(component_counts), excluded_top_level_tags=dict(omitted_tags),
                            released_form_child_tags=dict(form_child_tags), released_form_attribute_names=dict(form_attribute_names),
                            released_source_entry_types=dict(source_type_counts), excluded_sense_example_tags=dict(excluded_sense_tags),
                            source_entry_homonym_number_rows=len(homonym_rows), identical_input_conflict_groups=len(collisions),
                            identical_input_conflict_rows=len(collision_ids), selected_conflict_rows=len(collision_ids & selected),
                            selected_coexposure_groups=sum(len(x['selected_ids']) > 1 for x in collisions),
                            numbered_homonym_conflict_groups=sum(bool(x['all_have_distinct_entry_numbers']) for x in collisions),
                            unnumbered_distinct_xml_label_conflict_groups=sum(not x['all_have_distinct_entry_numbers'] and x['all_have_distinct_xml_labels'] for x in collisions),
                            unnumbered_unlabeled_conflict_groups=sum(not x['all_have_distinct_entry_numbers'] and not x['all_have_distinct_xml_labels'] for x in collisions),
                            held_reason_counts=dict(held_reason_counts)),
              flagged_discrepancies=dict(flag_groups), reviewed_resolutions=resolved_flags, identical_input_conflicts=collisions, row_ledger=ledger,
              limitations=['Exhaustive machine comparison against this archived XML, not visual reading of every printed page.',
                           'No new expert adjudication, translation correction, training admission or source-redistribution clearance.',
                           'Held records stay held; structural justification is not proof that every hold is necessary.',
                           'Entry homonym numbers distinguish source inventories; they do not by themselves identify a contextual passage meaning.'])
assert all(digest((ROOT / name).read_bytes()) == item['sha256'] for name, item in inputs.items())
result['input_bytes_unchanged_on_completion'] = True
(HERE / 'cpd-audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(status=result['status'], source_fidelity_status=result['source_fidelity_status'], coverage=result['coverage'],
                     flagged_discrepancies=result['flagged_discrepancies']), ensure_ascii=False))
