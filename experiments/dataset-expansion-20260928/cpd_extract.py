"""Read-only CPD structure recovery. No pair expansion or training admission.

Run this file with Python -B for the pinned-corpus profile and self-check.
Importing the module does not read files or write outputs.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

OBSERVATIONS = 'resources/local/kosh-quality-20260928/complete-v4/observations.jsonl'
OBSERVATIONS_SHA256 = '3b0b14ce6e6520ad801839388d7362596c0cdfd1480f1a5b63d378071c0c1a65'
TOP_LEVEL = {'form', 'sense', 'trcEvid', 'etym', 'xr', 'eg', 'usg',
             'note', 'gram', 'gramGrp', 'lbl'}
KNOWN_TAGS = TOP_LEVEL | {'entry', 'trc', 'trl', 'idg', 'lang', 'mentioned', 'tr',
                         'def', 'hi', 'ref', 'q', 'number', 'mood', 'itype'}


def _node(element, path):
    """Preserve mixed text, tails, attributes and ordered children separately."""
    return {'path': path, 'tag': element.tag, 'attributes': dict(element.attrib),
            'text': element.text, 'tail': element.tail,
            'children': [_node(child, f'{path}/{child.tag}[{i}]')
                         for i, child in enumerate(element)]}


def _walk(node):
    yield node
    for child in node['children']:
        yield from _walk(child)


def extract(xml):
    """Return original XML, typed ordered nodes and provisional scope blocks.

    Block indices reference tree.children. A form after a sense/cross-reference
    opens a new block; forms preceding any meaning stay grouped. Blocks are a
    structural aid, never a claim that every form takes every sense. In
    particular, multiple transcription-bearing form elements are unresolved.
    """
    result = {'source_xml': xml,
              'source_xml_sha256': hashlib.sha256(xml.encode('utf8')).hexdigest(),
              'status': 'STRUCTURE_RECOVERED_REVIEW_REQUIRED',
              'training_admitted': False, 'source_correctness_certified': False,
              'tree': None, 'blocks': [], 'unresolved_paths': []}
    # Do not interpret declarations or attempt repairs of defective source XML.
    if '<!DOCTYPE' in xml.upper() or '<!ENTITY' in xml.upper():
        result.update(status='HELD_XML_DECLARATION', error='Declarations not supported')
        return result
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        result.update(status='HELD_MALFORMED_XML', error=str(exc))
        return result
    result['tree'] = tree = _node(root, '/entry')
    if root.tag != 'entry':
        result.update(status='HELD_UNSUPPORTED_ROOT', error='Expected unnamespaced entry')
        return result
    result['unresolved_paths'] = [n['path'] for n in _walk(tree) if n['tag'] not in KNOWN_TAGS]
    result['unresolved_paths'] += [n['path'] for n in tree['children'] if n['tag'] not in TOP_LEVEL]
    result['entry_type_as_published'] = root.get('type')
    result['explicit_language_nodes'] = [n['path'] for n in _walk(tree)
                                        if any(k in n['attributes'] for k in
                                               ('lang', '{http://www.w3.org/XML/1998/namespace}lang'))]
    blocks = []
    block = None
    for index, child in enumerate(root):
        # A cross-reference-only form must not inherit the next form's meaning.
        if block is None or (child.tag == 'form' and
                             (block['sense_indices'] or block['cross_reference_indices'])):
            block = {'block_index': len(blocks), 'form_indices': [], 'sense_indices': [],
                     'cross_reference_indices': [], 'metadata_indices': []}
            blocks.append(block)
        kind = {'form': 'form_indices', 'sense': 'sense_indices',
                'xr': 'cross_reference_indices'}.get(child.tag, 'metadata_indices')
        block[kind].append(index)
    for block in blocks:
        # Keep complete published strings: commas, parentheses and stems are not split.
        form_nodes = [tree['children'][i] for i in block['form_indices']]
        bearing = [n for n in form_nodes if any(c['tag'] == 'trc' for c in n['children'])]
        flags = []
        if len(bearing) > 1:
            flags.append('MULTIPLE_FORM_ELEMENTS_ASSOCIATION_UNRESOLVED')
        if not bearing:
            flags.append('NO_DIRECT_TRANSCRIPTION')
        if not block['sense_indices']:
            flags.append('NO_DIRECT_SENSE')
        if any(c['tag'] not in {'trc', 'trl', 'idg', 'xr'} for n in form_nodes for c in n['children']):
            flags.append('COMPLEX_FORM_CHILDREN_UNRESOLVED')
        # Inline references, examples, grammar and uncertainty stay in their own
        # nodes; downstream consumers must not use concatenated itertext as gold.
        block['scope_flags'] = flags
        block['association_status'] = 'UNRESOLVED' if flags else 'SINGLE_FORM_SEQUENCE_REVIEW_REQUIRED'
    result['blocks'] = blocks
    result['main_block_index'] = next((b['block_index'] for b in blocks if b['form_indices']), None)
    if result['unresolved_paths']:
        result['status'] = 'HELD_UNSUPPORTED_STRUCTURE'
    return result


def self_check(root=None):
    """Hash-checked whole-corpus structural census; returns JSON-safe counts."""
    root = Path(root) if root is not None else Path(__file__).resolve().parents[2]
    raw = (root / OBSERVATIONS).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == OBSERVATIONS_SHA256
    rows = [r for r in map(json.loads, raw.decode('utf8').splitlines()) if r['collection'] == 'cpd']
    assert len(rows) == 3103 and len({r['id'] for r in rows}) == 3103
    results = {r['id']: extract(r['source_record']['xml']) for r in rows}
    statuses, shapes, paths, flags = Counter(), Counter(), Counter(), Counter()
    total_blocks = total_senses = total_forms = 0
    for row in rows:
        value = results[row['id']]
        assert value['source_xml'] == row['source_record']['xml']
        assert not value['training_admitted'] and not value['source_correctness_certified']
        statuses[value['status']] += 1
        if value['tree'] is None:
            continue
        children = value['tree']['children']
        shapes[tuple(n['tag'] for n in children)] += 1
        for n in _walk(value['tree']):
            path = '/'.join(part.split('[')[0] for part in n['path'].split('/'))
            paths[path] += 1
        indices = [i for b in value['blocks'] for key in
                   ('form_indices', 'sense_indices', 'cross_reference_indices', 'metadata_indices') for i in b[key]]
        assert sorted(indices) == list(range(len(children)))
        total_blocks += len(value['blocks'])
        total_senses += sum(n['tag'] == 'sense' for n in children)
        total_forms += sum(n['tag'] == 'form' for n in children)
        flags.update(f for b in value['blocks'] for f in b['scope_flags'])
    xrad = results['kosh:cpd:04922df1d3095c85d144db82f2322eab708cfa34']
    assert len(xrad['blocks']) == 2
    assert [xrad['tree']['children'][b['sense_indices'][0]]['children'][0]['text']
            for b in xrad['blocks']] == ['wisdom, reason', 'wise']
    assert xrad['tree']['children'][xrad['blocks'][1]['form_indices'][0]]['children'][0]['text'] == 'xradīg, xradōmand'
    ambiguous = results['kosh:cpd:20194fd2eed4636d5ceb9bed2f27f1bb2375e952']
    assert len(ambiguous['blocks']) == 1 and ambiguous['blocks'][0]['association_status'] == 'UNRESOLVED'
    assert len(ambiguous['blocks'][0]['form_indices']) == 2 and len(ambiguous['blocks'][0]['sense_indices']) == 3
    example = results['kosh:cpd:4cdd1efd4cd2ad48e400cf5c6d48965422ce271a']
    assert sum(len(b['sense_indices']) for b in example['blocks']) == 2  # Nested example translation is separate.
    assert sum(n['tag'] == 'sense' for n in _walk(example['tree'])) == 3
    assert len(example['blocks'][0]['form_indices']) == 2  # trl-only supplementary spelling retained.
    malformed = {k for k, v in results.items() if v['status'] == 'HELD_MALFORMED_XML'}
    assert statuses == {'STRUCTURE_RECOVERED_REVIEW_REQUIRED': 3101, 'HELD_MALFORMED_XML': 2}
    assert malformed == {'kosh:cpd:8a25cd9aab91d28e0ee26362420a038d79c28d90',
                         'kosh:cpd:18e5fce7abcc6ac96b157109ffd59b462a3a1e65'}
    assert extract('<entry><form>')['status'] == 'HELD_MALFORMED_XML'
    assert extract('<entry><unknown/></entry>')['status'] == 'HELD_UNSUPPORTED_STRUCTURE'
    nested = extract('<entry><form><form><trc>x</trc></form></form><sense><tr>y</tr></sense></entry>')
    assert 'COMPLEX_FORM_CHILDREN_UNRESOLVED' in nested['blocks'][0]['scope_flags']
    return {'input_sha256': OBSERVATIONS_SHA256, 'observations': len(rows), 'statuses': dict(statuses),
            'top_level_shape_count': len(shapes), 'node_path_counts': dict(sorted(paths.items())),
            'blocks': total_blocks, 'direct_forms': total_forms, 'direct_senses': total_senses,
            'scope_flag_counts': dict(flags), 'malformed_ids': sorted(malformed),
            'self_check': 'PASS', 'training_admitted': 0}


if __name__ == '__main__':
    print(json.dumps(self_check(), ensure_ascii=False, indent=2))
