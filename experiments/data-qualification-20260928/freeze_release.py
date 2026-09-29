"""Build the typed, source-qualified learning view; never launch training."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import unicodedata
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / 'resources/local/data-qualification-20260928/ready-v1'
MANIFEST = HERE / 'release-v1.json'
BASELINE = 'experiments/train-audit-20260927/qualified-v1/train.jsonl'
BASELINE_SHA = '15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc'
PAR = 'sources/local/parsig-2026-09-20/exports/text-units.jsonl'
PAR_SHA = 'c42e0a5a0d4d108218a0481ca073c07c6bb00cdcba0bffb462b67bb6d7a60789'
PROTECTED = {103,104,110,111,112,114,116,117,118,120,124,130,132,138,152,517}
S22 = [
    'experiments/composition-evidence-20260928/candidates.jsonl',
    'experiments/dataset-expansion-20260928/s22-candidates.jsonl',
    'experiments/dataset-expansion-20260928/s22-supplement.jsonl',
    'experiments/data-qualification-20260928/s22-grammar-remainder.jsonl',
]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf8')


def normalize(text):
    return ' '.join(unicodedata.normalize('NFC', text).casefold().split())


def archive_text(layer):
    # Selected text is narrower than its provenance context_lines; never serialize the latter.
    if 'text' in layer:
        return layer['text']
    return '\n\n'.join('\n'.join(line.get('text_with_uncertainty_markup', line['text'])
                                  for line in block['lines']) for block in layer['blocks'])


def build():
    bindings = {}

    def bind_file(name, expected):
        if name in bindings:
            assert bindings[name] == expected, name
        else:
            assert sha((ROOT / name).read_bytes()) == expected, name
            bindings[name] = expected

    def read(name, expected=None):
        raw = (ROOT / name).read_bytes()
        checksum = sha(raw)
        if expected:
            assert checksum == expected, name
        if name in bindings:
            assert bindings[name] == checksum, name
        bindings[name] = checksum
        if name.endswith('.jsonl'):
            return [json.loads(line) for line in raw.decode('utf8').splitlines()]
        return json.loads(raw)

    baseline = read(BASELINE, BASELINE_SHA)
    assert len(baseline) == 2237
    # Verify immutable benchmark bytes without parsing or displaying answer content.
    benchmark = read('benchmarks/pal-reference-v1/manifest.json', 'a3932f7510f101376cc91c47bb23f3c9872656c41f563701fa3dcb2b6c89a5e8')
    for name, expected in benchmark['files'].items():
        path = 'benchmarks/pal-reference-v1/' + name
        assert sha((ROOT / path).read_bytes()) == expected, path
        bindings[path] = expected
    outputs, exclusions = defaultdict(list), []
    old_s22_hashes = dict(zip(S22[:3], [
        'b0525e52490f7fc4f58d0e4cb9808be59fbdaae9aab4ba17845bf672bdfd06b9',
        'e24a63448805f5e99f54874e32d502af350febb57e3830f07ed51d069b061e11',
        'a328fe6b7075c58e3e27125f26d90d1ad5c3a17bb0c2aa8e9c17d412aa72ec78']))

    def add(file, r, row_id, task, src, tgt, context, restriction, origin_extra=None):
        assert src and tgt and row_id
        outputs[task].append({'id': row_id, 'task': task,
                             'learning': {'source': src, 'target': tgt, 'context': context},
                             'origin': {'file': file, 'sha256': bindings[file], 'row_id': row_id,
                                        **(origin_extra or {})},
                             'qualification': 'SOURCE_QUALIFIED_AI_REVIEWED_NOT_EXPERT_CERTIFIED',
                             'use_restriction': restriction, 'training_run_authorized': False})

    file = 'resources/local/data-qualification-20260928/persian-v1/qualified.jsonl'
    fa_manifest = read('experiments/data-qualification-20260928/persian-summary-v1.json')
    bind_file('resources/local/data-qualification-20260928/persian-v1/shared-form-bundles.jsonl',
              fa_manifest['outputs']['shared-form-bundles.jsonl']['sha256'])
    for r in read(file, fa_manifest['outputs']['qualified.jsonl']['sha256']):
        assert r['collection'] in {'da','dk8','dmx','gbd','raf','yz'}
        f = r['learning_fields']
        for evidence in r['source_pointers']:
            bind_file('sources/local/public-texts-2026-09-20/' + evidence['raw_file'], evidence['raw_sha256'])
        add(file, r, r['id'], 'lexical-fa', f['forms_as_published'],
            f['complete_meaning_inventory_as_published'],
            {'source_scope': f['source_scope'], 'source_language': 'pal', 'target_language': 'fas',
             'stratum': r['stratum']},
            'Full source-scoped sense inventory, not a sentence or one universal meaning. Keep alternatives together; no Cartesian expansion.')
    for r in read('resources/local/data-qualification-20260928/persian-v1/held.jsonl', fa_manifest['outputs']['held.jsonl']['sha256']):
        exclusions.append({'id': r['resource_id'], 'component': 'lexical-fa', 'reason': r['reasons']})
    file = 'resources/local/data-qualification-20260928/cpd/qualified.jsonl'
    cpd_manifest = read('resources/local/data-qualification-20260928/cpd/manifest.json')
    for r in read(file, cpd_manifest['outputs']['qualified.jsonl']['sha256']):
        assert r['evidence_type'] == 'generic_lexical_sense_inventory'
        bind_file('sources/local/public-texts-2026-09-20/' + r['source']['raw_file'], r['source']['raw_sha256'])
        add(file, r, r['id'], 'lexical-en', r['form_bundle'], r['senses'],
            {'scope_annotations': r['scope_annotations'], 'edition': r['edition'],
             'source_language': 'pal', 'target_language': 'eng'},
            'Complete direct senses for the declared block. English remains English. Excluded context paths/quotations are provenance only.',
            {'source_scope_paths': r['source']})
    for r in read('resources/local/data-qualification-20260928/cpd/held.jsonl', cpd_manifest['outputs']['held.jsonl']['sha256']):
        exclusions.append({'id': r['id'], 'component': 'lexical-en', 'reason': r.get('reasons', r.get('reason'))})
    mmp_file = 'experiments/data-qualification-20260928/mmp-review.json'
    mmp = read(mmp_file)
    resources = {r['id']: r for r in read(mmp['source_path'], mmp['source_sha256']) if r['collection'] == 'mmp'}
    assert len(resources) == mmp['reviewed_count'] == 1990
    assert set(mmp['qualified_resource_ids']).isdisjoint(mmp['holds'])
    assert set(mmp['qualified_resource_ids']) | set(mmp['holds']) == set(resources)
    bind_file(mmp['original_xml_observations_path'], mmp['original_xml_observations_sha256'])
    bind_file(mmp['raw_xml_response_path'], mmp['raw_xml_response_sha256'])
    xml_rows = {}
    mmp_ids = set(mmp['qualified_resource_ids'])
    with (ROOT / mmp['original_xml_observations_path']).open(encoding='utf8') as stream:
        for line in stream:
            r = json.loads(line)
            if 'recovered:' + r['id'] in mmp_ids:
                xml_rows[r['id']] = r['source_record']['xml']
    for scope in mmp['qualified_scopes']:
        r = resources[scope['resource_id']]
        meaning = r['meaning_as_published']
        assert sha(meaning.encode('utf8')) == scope['original_meaning_sha256']
        selected = [meaning[a:b] for a,b in scope['target_spans_unicode_codepoints_half_open']]
        target = ''.join(selected)
        assert target == scope['expected_complete_selected_text']
        xml = xml_rows[r['observation_ids'][0]]
        assert sha(xml.encode('utf8')) == scope['source_xml_sha256']
        tree = ET.fromstring(xml)
        assert [node.text.strip() for node in tree.findall('lang')] == ['MP']
        assert ' '.join((tree.findtext('gramm') or '').split()) == scope['pos_grammar_as_published']
        add(mmp['source_path'], r, r['id'], 'lexical-mmp-en', r['forms'], target,
            {'source_language': 'pal', 'target_language': 'eng', 'stratum': 'MANICHAEAN_MIDDLE_PERSIAN',
             'grammar_as_published': scope['pos_grammar_as_published'],
             'source_scope': r['catalogue_attribution']['title']},
            'Complete generic sense inventory; manuscript quotations and unresolved interpretations are held. Preserve all form variants and grammatical roles.',
            {'qualification_overlay': mmp_file, 'qualification_sha256': bindings[mmp_file],
             'target_spans': scope['target_spans_unicode_codepoints_half_open'],
             'observation_ids': r['observation_ids']})
    for rid, reason in mmp['holds'].items():
        exclusions.append({'id': rid, 'component': 'lexical-mmp-en', 'reason': reason})
    decisions = read('experiments/data-qualification-20260928/s22-derived-decisions.json')
    for file in S22:
        for r in read(file, decisions['raw_input_sha256'] if file == S22[-1] else old_s22_hashes[file]):
            bind_file(r['source_pdf'], r['source_pdf_sha256'])
            bind_file(r['image_path'], r['image_sha256'])
            if r['id'] in decisions['holds']:
                exclusions.append({'id': r['id'], 'reason': decisions['holds'][r['id']]})
                continue
            target = r['persian_translation']
            correction = decisions['corrections'].get(r['id'])
            if correction:
                assert target == correction['original']
                target = correction['derived']
            record_type = r.get('record_type', 'pedagogical_clause')
            context = {k: r[k] for k in ['page_location', 'phenomenon', 'context_family', 'published_literal_gloss', 'source_register'] if k in r}
            context.update(record_type=record_type, source_language='pal', target_language='fas')
            add(file, r, r['id'], 'pedagogy-fa', r['pahlavi_transcription'], target, context,
                'Printed grammar context or teaching example. Preserve all variants/editorial signs; not independent manuscript attestations.',
                {'pdf': r['source_pdf'], 'pdf_sha256': r['source_pdf_sha256'],
                 'pdf_page': r['pdf_page_1_based'], 'derivation': correction})
            note = r.get('semantic_qualification', r.get('phenomenon', 'Printed teaching example'))
            if r['id'] in {'S22GRAM-045','S22GRAM-046'}:
                note = 'Printed comparative/superlative adverb; derived target spelling corrected by two independent page readings. Source segmentation preserved.'
            if r['id'] == 'S22GRAM-043':
                note = 'Indefinite-pronoun inventory. List-ending و غیره remains evidence, not a lexical meaning of this form.'
            # Ambiguous printed forms require their row-specific grammatical context.
            # This is an auxiliary grammar task, not a source-only translation prompt.
            outputs['pedagogy-fa'][-1]['learning']['context']['grammatical_context'] = note
    for name in ['s22-glossary-a.jsonl','s22-glossary-b.jsonl']:
        for r in read((HERE / name).relative_to(ROOT).as_posix()):
            exclusions.append({'id': r.get('id', r.get('record_id')), 'component': 'textbook-glossary', 'reason': 'UNRESOLVED_READING_LINEAGE_IN_MIXED_PROTECTED_SOURCE_BOOK'})
    file = 'experiments/dataset-expansion-20260928/parsig-format-candidates.jsonl'
    for r in read(file, 'f4dbc011c80bc7616f9f31c9ff46db0cc938aadc7c47fd7ae1e94ceba45042aa'):
        exclusions.append({'id': r['id'], 'component': 'parsig-format-recovery', 'reason': 'REVERSIBLE_FORMAT_RECOVERY_DOES_NOT_RESOLVE_SEMANTIC_CONCERNS'})
    file = 'experiments/data-qualification-20260928/archive-alignment.jsonl'
    archive_decisions = read('experiments/data-qualification-20260928/archive-derived-decisions.json')
    for r in read(file, archive_decisions['source_packet_sha256']):
        provenance = r['provenance']
        bind_file(provenance['packet_path'], provenance['packet_sha256'])
        for key in ['raw_source','archive_record_pointer']:
            bind_file(provenance[key]['path'], provenance[key]['sha256'])
        if r['disposition'].startswith('HELD'):
            exclusions.append({'id': r['unit_id'], 'reason': r['disposition']})
            continue
        assert r['disposition'] in {'QUALIFIED_WHOLE_PASSAGE','QUALIFIED_FRAGMENT'}
        target = archive_text(r['target'])
        correction = archive_decisions['corrections'].get(r['unit_id'])
        if correction:
            assert target.count(correction['original_substring']) == correction['expected_occurrences']
            target = target.replace(correction['original_substring'], correction['derived_substring'])
        add(file, r, r['unit_id'], 'documentary-en', archive_text(r['source']), target,
            {'source_language': 'pal', 'target_language': 'eng', 'grain': r['grain'],
             'witness_group': r['split_and_overlap']['witness_group'],
             'evidence_class': r['disposition'], 'task_condition': 'Translate the preserved, possibly damaged edition span; retain uncertainty and editorial additions.'},
            'Annotated source-bound documentary evidence, including fragments. Never treat damaged/restored readings or editorial explanations as certain complete prose.',
            {'derivation': correction})

    file = 'experiments/data-qualification-20260928/kanheri-candidates.jsonl'
    for r in read(file):
        assert r['split']['work_id'] == 201 and 201 not in PROTECTED
        bind_file(r['source_pdf'], r['source_pdf_sha256'])
        for evidence in r['visual_evidence']:
            bind_file(evidence['path'], evidence['sha256'])
        for scope in r['qualified_scopes']:
            if scope['qualification'] != 'SOURCE_QUALIFIED_SCOPE_PENDING_INDEPENDENT_REVIEW':
                exclusions.append({'id': scope['scope_id'], 'reason': scope['qualification']})
                continue
            a, b = scope['source_char_span']
            c, d = scope['target_char_span']
            assert r['source_text'][a:b] == scope['source_text']
            assert r['target_text'][c:d] == scope['target_text']
            add(file, scope, scope['scope_id'], 'inscription-fa', scope['source_text'], scope['target_text'],
                {'source_language': 'pal', 'target_language': 'fas', 'grain': scope['grain'],
                 'witness_group': r['matched_existing_record'], 'edition': r['citation']['edition_identity']},
                'Earlier article edition, exact supported span only. Shared witness with existing Parsig201; not a new independent inscription.',
                {'parent_row_id': r['candidate_id'], 'source_span': [a,b], 'target_span': [c,d],
                 'pdf': r['source_pdf'], 'pdf_sha256': r['source_pdf_sha256']})

    file = 'experiments/data-qualification-20260928/s23-candidates.jsonl'
    for r in read(file):
        bind_file(r['source_pdf'], r['source_pdf_sha256'])
        for evidence in r['visual_evidence']:
            bind_file(evidence['path'], evidence['sha256'])
        for scope in r['qualified_scopes']:
            if scope['scope_id'] == 'S23-BERK25-SEAL':
                exclusions.append({'id': scope['scope_id'], 'component': 's23', 'reason': 'FORMULA_ALREADY_COVERED_BY_ARCHIVE_MP0408'})
                continue
            if scope['qualification'] != 'SOURCE_QUALIFIED_SCOPE_PENDING_INDEPENDENT_REVIEW':
                exclusions.append({'id': scope['scope_id'], 'component': 's23', 'reason': scope['qualification']})
                continue
            a,b = scope['source_char_span']
            c,d = scope['target_char_span']
            assert r['source_text'][a:b] == scope['source_text']
            assert r['target_text'][c:d] == scope['target_text']
            add(file, scope, scope['scope_id'], 'edition-spans-en', scope['source_text'], scope['target_text'],
                {'source_language': 'pal', 'target_language': 'eng', 'grain': scope['grain'],
                 'witness_group': r['witness_group'],
                 'task_condition': 'Translate exactly this published span without supplying missing agents, damaged material or neighboring clauses.'},
                'Exact unaffected printed span. Damaged/contradictory parent passages and repeated archive formula stay outside the learning view.',
                {'parent_row_id': r['candidate_id'], 'source_span': [a,b], 'target_span': [c,d],
                 'pdf': r['source_pdf'], 'pdf_sha256': r['source_pdf_sha256'],
                 'source_pdf_page': scope['source_page_pdf_1_based'], 'target_pdf_page': scope['target_page_pdf_1_based']})

    # Source-only copy screen from the independently archived source corpus, never test answers.
    protected_sources = []
    for r in read(PAR, PAR_SHA):
        if int(r['book_id']) in PROTECTED:
            for t in r['transcription']:
                text = t if isinstance(t, str) else t.get('text', '')
                if text:
                    protected_sources.append((r['book_id'], normalize(text)))
    assert protected_sources
    for task in ['pedagogy-fa', 'documentary-en', 'inscription-fa', 'edition-spans-en']:
        kept = []
        for r in outputs[task]:
            source = normalize(r['learning']['source'])
            # Short grammatical words are expected vocabulary overlap, not passage leakage.
            hits = sorted({book for book, text in protected_sources
                           if len(source.split()) >= 5 and source in text})
            if hits:
                exclusions.append({'id': r['id'], 'reason': 'PROTECTED_SOURCE_SPAN_CONTAINMENT', 'work_ids': hits})
            else:
                kept.append(r)
        outputs[task] = kept
    duplicates = []
    for task, rows in outputs.items():
        groups = defaultdict(list)
        for r in rows:
            groups[sha(encode([r['learning']['source'],r['learning']['target']]))].append(r['id'])
        duplicates.extend({'task': task, 'row_ids': ids, 'type': 'SURFACE_SOURCE_TARGET_REPETITION',
                           'policy': 'Not a merge instruction: different grammatical contexts remain distinct; shared witnesses are not independent attestations.'}
                          for ids in groups.values() if len(ids) > 1)
        assert len({r['id'] for r in rows}) == len(rows)
    # Freeze reports/checks which justify the per-component admission, without using their prose as learning text.
    reports = ['ADMISSION-REVIEW.md','PERSIAN-REVIEW.md','CPD-REVIEW.md','MMP-QA.md','S22-GRAMMAR-REVIEW.md','ARCHIVE-REVIEW.md','INSCRIPTION-REVIEW.md','S23-REVIEW.md']
    for name in reports:
        path = (HERE / name).relative_to(ROOT).as_posix()
        bindings[path] = sha((ROOT / path).read_bytes())
    return outputs, exclusions, duplicates, bindings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    assert not (args.write and args.check)
    if args.write and (OUT.exists() or MANIFEST.exists()):
        raise ValueError('Frozen release exists; refusing overwrite')
    # Scope regression: held continuations must not leak; damaged XML content must remain marked.
    assert archive_text({'text': 'allowed', 'context_lines': [{'text': 'held continuation'}]}) == 'allowed'
    assert archive_text({'blocks': [{'lines': [{'text': 'bare', 'text_with_uncertainty_markup': '⟦unclear⟧'}]}]}) == '⟦unclear⟧'
    outputs, exclusions, duplicates, bindings = build()
    counts = {task: len(rows) for task, rows in outputs.items()}
    outputs['excluded'] = exclusions
    outputs['duplicate-groups'] = duplicates
    payloads = {name + '.jsonl': b''.join(encode(r) + b'\n' for r in rows) for name, rows in outputs.items()}
    payloads['historical-control-fa.jsonl'] = (ROOT / BASELINE).read_bytes()
    assert sha(payloads['historical-control-fa.jsonl']) == BASELINE_SHA
    assert sum(map(len, payloads.values())) < 50_000_000
    manifest = {'release': 'source-qualified-v1', 'historical_control_pairs': 2237,
                'typed_additions': counts, 'counts_are_not_additive_translation_pairs': True,
                'input_sha256': bindings, 'script_sha256': sha(Path(__file__).read_bytes()),
                'outputs': {name: {'sha256': sha(raw), 'bytes': len(raw), 'rows': 2237 if name == 'historical-control-fa.jsonl' else len(outputs[name[:-6]])}
                            for name, raw in payloads.items()},
                'training_launched': False, 'model_tokenizer_census': 'Deferred until training design; no new model download.',
                'limits': ['Source qualification is not expert certification.',
                           'All 888 S22 glossary groups remain outside learning because reading lineage is unresolved.',
                           'Source-only containment is a bounded copy screen, not universal paraphrase exclusion.',
                           'Only learning fields are model-visible; never serialize provenance or held evidence.',
                           'Original control and fixed benchmark remain immutable; benchmark byte checks do not expose answers.']}
    for name, expected in bindings.items():
        assert sha((ROOT / name).read_bytes()) == expected, name
    if args.write:
        OUT.mkdir(parents=True)
        for name, raw in payloads.items():
            (OUT / name).write_bytes(raw)
        MANIFEST.write_bytes(encode(manifest) + b'\n')
    elif args.check:
        assert json.loads(MANIFEST.read_bytes()) == manifest
        for name, raw in payloads.items():
            assert (OUT / name).read_bytes() == raw, name
    print(json.dumps({'typed_additions': counts, 'excluded': len(exclusions), 'duplicate_groups': len(duplicates)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
