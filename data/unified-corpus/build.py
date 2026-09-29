"""Offline, typed corpus index and audited historical training export; stdlib only."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import time
import unicodedata
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[2]
RESOLVED_ROOT = ROOT.resolve()
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'resources/local/unified-corpus-20260928/v2'
MANIFEST = HERE / 'manifest-v2.json'
REPORT = HERE / 'quality-report-v2.json'
TRAIN_DIR = 'experiments/train-audit-20260927/qualified-v1'
TRAIN_SHA = '15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc'
LEDGER_SHA = 'd79af2e64fbb92954c8b8d0ed9cb7a34e7e7d24d4c22ea9c22f1da6d569a8e77'
KOSH_SUMMARY = 'experiments/kosh-quality-20260928/summary-v4.json'
KOSH_SHA = '66d073cb95a2adbc6d983ccdd1a3fda39eed535289fec65ea7d820a808e035fd'
PAR = 'sources/local/parsig-2026-09-20'
PUBLIC = 'sources/local/public-texts-2026-09-20'
HOLDOUT = {103, 112, 138, 517, 104, 110, 111, 114, 116, 117, 118, 120, 124, 130, 132, 152}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def norm(text):
    return ' '.join(unicodedata.normalize('NFC', text).split())


def safe_path(name):
    path = (ROOT / name).resolve()
    if not path.is_relative_to(RESOLVED_ROOT):
        raise ValueError('Input escapes project')
    return path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def checked_text(raw, expected):
    require(digest(raw) == expected, 'Input changed before parsing')
    return raw.decode('utf-8-sig')


def document_holdout(doc):
    """Only verified work mappings; unmatched documents remain uncleared reference material."""
    family = doc['collection']
    if family == 'parsig' and int(doc['id']) in HOLDOUT:
        return int(doc['id'])
    path = unicodedata.normalize('NFC', unquote(urlparse(doc.get('source_url', '')).path)).lower()
    if family == 'titus':
        for segment, work in [('/snstrl/', 138), ('/snstrs/', 138), ('/zadspram/', 152)]:
            if segment in path:
                return work
    if family == 'avesta' and path in {'/mp/zadspram.html', '/mp/zadspram.pdf'}:
        return 152
    if family == 'persoaryan':
        if path == '/hkr.html' or path.endswith('/hkr.pdf'):
            return 117
        if path.endswith('/sūr.pdf'):
            return 112
    return None


def pair_checks(row, ledger):
    require(int(row['work_id'].split(':')[-1]) not in HOLDOUT, 'Held-out training work')
    require(ledger['disposition'] in {'ELIGIBLE', 'ELIGIBLE_WITH_QUALIFICATIONS'}, 'Unqualified pair')
    require(ledger['mechanical_status'] == ledger['provenance_status'] == 'PASS', 'Failed evidence')
    require(ledger['split_status'] == 'PASS_IDENTITY_AND_PINNED_HOLDOUT', 'Split not cleared')
    require(row['id'] == ledger['id'] and row['record_id'] == ledger['record_id']
            and row['work_id'] == ledger['work_id'], 'Identity mismatch')
    for field, source in [('text', 'source'), ('target', 'target')]:
        value = row[field]
        require(isinstance(value, str) and norm(value), 'Empty training text')
        require(value == ledger[source + '_text'], 'Training text changed')
        require(digest(value.encode('utf-8')) == ledger[source + '_sha256'], 'Pair hash changed')
    require(row['source_language'] == 'pal' and row['target_language'] == 'fa', 'Wrong task language')


def build():
    start = time.monotonic()
    inputs, catalogue, identifiers = {}, [], set()

    def pin(name, expected=None, size=None):
        # Repeated row locators share already-checked files; avoid 40k Windows path resolutions.
        if name not in inputs:
            path = safe_path(name)
            name = path.relative_to(RESOLVED_ROOT).as_posix()
        if name not in inputs:
            raw = path.read_bytes()
            inputs[name] = {'sha256': digest(raw), 'bytes': len(raw)}
        receipt = inputs[name]
        require(expected is None or receipt['sha256'] == expected, 'SHA mismatch: ' + name)
        require(size is None or receipt['bytes'] == size, 'Size mismatch: ' + name)
        require(time.monotonic() - start < 300, 'Five-minute import limit reached')
        return name

    def read(name, expected=None):
        name = pin(name, expected)
        raw = safe_path(name).read_bytes()
        text = checked_text(raw, inputs[name]['sha256'])
        return [json.loads(x) for x in text.splitlines() if x.strip()] if name.endswith('.jsonl') else json.loads(text)

    def add(ident, family, kind, path, selector, status='REVIEW_REQUIRED', reason=None, **extra):
        require(ident not in identifiers, 'Duplicate catalogue ID: ' + ident)
        identifiers.add(ident)
        catalogue.append({'id': ident, 'family': family, 'kind': kind, 'status': status,
                          'locator': {'path': pin(path), **selector}, 'reason': reason,
                          'training_admitted': False, **extra})

    previous = read('data/unified-corpus/manifest.json',
                    '99ef11068e763cf2b8ac9e7a9430e849db8f43a8a1a688d136d60d5922fecfae')
    pin('resources/local/unified-corpus-20260928/v1/build-source.py', previous['script_sha256'])
    pin('data/unified-corpus/quality-report.json', previous['quality_report_sha256'])
    for receipt in previous['outputs'].values():
        pin(receipt['path'], receipt['sha256'], receipt['bytes'])

    # Frozen reviewed data, not a fresh semantic approval or retokenization.
    train = read(TRAIN_DIR + '/train.jsonl', TRAIN_SHA)
    ledger_rows = read(TRAIN_DIR + '/final-ledger.jsonl', LEDGER_SHA)
    ledger = {x['id']: (i, x) for i, x in enumerate(ledger_rows, 1)}
    require(len(ledger) == len(ledger_rows), 'Duplicate audit ID')
    train_ids, pairs, variants, core = {}, set(), defaultdict(list), []
    for row in train:
        number, review = ledger[row['id']]
        pair_checks(row, review)
        require(row['record_id'] not in train_ids, 'Duplicate training parent')
        train_ids[row['record_id']] = row['id']
        key = (norm(row['text']), norm(row['target']))
        require(key not in pairs, 'Exact duplicate training pair')
        pairs.add(key)
        variants[key[0]].append(row['id'])
        core.append({k: row[k] for k in ['id', 'record_id', 'work_id', 'text', 'target',
                    'source_language', 'target_language', 'credit', 'revision']} |
                    {'status': 'HISTORICAL_PROVISIONAL_AI_QUALIFIED_CONTROL', 'expert_certified': False,
                     'training_launch_admitted': False, 'qualification': review['linguistic_review'],
                     'audit_locator': {'path': TRAIN_DIR + '/final-ledger.jsonl', 'line_1_based': number}})
    require(len(core) == 2237, 'Historical TRAIN count changed')
    print('Validated 2237 historical pairs and their audit bindings', flush=True)

    # One paragraph index. Protected targets are not copied into this catalogue.
    par_path = PAR + '/exports/text-units.jsonl'
    parsig = read(par_path)
    require(len(parsig) == 4507, 'Parsig coverage changed')
    ledger_by_parent = {x['record_id']: x for x in ledger_rows}
    for i, row in enumerate(parsig, 1):
        work = int(row['book_id'])
        prior = ledger_by_parent.get(row['id'])
        if work in HOLDOUT:
            status, reason = 'PROTECTED_HOLDOUT', 'Known held-out work family'
        elif row['id'] in train_ids:
            status, reason = 'HISTORICAL_CONTROL', 'Existing AI-qualified pair; qualifications retained'
        elif prior and prior['disposition'] not in {'ELIGIBLE', 'ELIGIBLE_WITH_QUALIFICATIONS'}:
            status, reason = 'QUARANTINED', 'Prior audit: ' + prior['disposition']
        else:
            status, reason = 'REVIEW_REQUIRED', 'Source language, alignment, lineage and meaning unresolved'
        add(row['id'], 'parsig', 'publisher_paragraph', par_path, {'line_1_based': i}, status, reason,
            work_id='parsig:' + str(work), training_pair_id=train_ids.get(row['id']))
        source = row['source']
        pin(PAR + '/' + source['file'], source['sha256'], source['bytes'])
    read(PAR + '/exports/book-metadata.json')
    require(set(train_ids) <= {r['id'] for r in parsig}, 'Training parent absent from source catalogue')

    # Earlier document catalogue stays at document grain; all original fields remain accessible.
    docs = read('data/document-index.jsonl')
    require(len(docs) == 2916, 'Historical catalogue changed')
    for i, doc in enumerate(docs, 1):
        family = doc['collection']
        protected_work = document_holdout(doc)
        add('archive:' + str(i), family, 'archive_document', 'data/document-index.jsonl',
            {'line_1_based': i}, 'PROTECTED_HOLDOUT' if protected_work else 'REFERENCE_ONLY',
            'Known held-out work or alternate witness' if protected_work else
            'Document may contain multiple works/layers; not aligned supervision',
            protected_work_id='parsig:' + str(protected_work) if protected_work else None)
        pin(doc.get('file', doc.get('source_file')), doc.get('sha256'))
        for key in ['text_file', 'pdf_text_file']:
            if doc.get(key):
                pin(doc[key])
    # Keep structured layers and metadata reachable, without inventing sentence alignment.
    for family in ['avesta', 'berkeley', 'invisible-east', 'persoaryan', 'titus']:
        path = PUBLIC + '/' + family
        manifest = read(path + '/manifest.json')
        for receipt in manifest.values():
            if receipt.get('status') == 'ok' and receipt.get('file'):
                pin(path + '/' + receipt['file'], receipt['sha256'], receipt.get('bytes'))
        read(path + ('/middle-persian.json' if family == 'invisible-east' else '/documents.json'))
        for leaf in ['coverage.json', 'pdf-text-coverage.json']:
            if safe_path(path + '/' + leaf).exists():
                pin(path + '/' + leaf)
        for extracted in sorted(safe_path(path).glob('pdf-text/*.jsonl')):
            pin(extracted.relative_to(ROOT).as_posix())
    print('Validated older corpus documents and archive receipts', flush=True)

    # Only final Kosh v4 is counted; prior snapshots are receipts, not extra observations.
    kosh = read(KOSH_SUMMARY, KOSH_SHA)
    kout = {Path(x['file']).name: x for x in kosh['outputs']}
    for receipt in kout.values():
        pin(receipt['file'], receipt['sha256'], receipt['bytes'])
    observations = read(kout['observations.jsonl']['file'])
    groups = read(kout['staged-groups.jsonl']['file'])
    quarantine = read(kout['quarantine.jsonl']['file'])
    obs = {r['id']: r for r in observations}
    require(len(obs) == len(observations) == 42904, 'Kosh observation identity mismatch')
    partition = []
    for i, group in enumerate(groups, 1):
        require(group['status'] == 'STAGED_NOT_TRAIN_ADMITTED', 'Unexpected lexical admission')
        partition.extend(group['observation_ids'])
        add(group['id'], 'kosh:' + group['collection'], 'lexical_form_sense_group',
            kout['staged-groups.jsonl']['file'], {'line_1_based': i},
            reason='Per-entry language, sense, edition/quotation lineage and use qualification required',
            observation_ids=group['observation_ids'])
    for i, row in enumerate(quarantine, 1):
        oid = row['observation_id']
        partition.append(oid)
        reason = row['reason']
        status = 'PROTECTED_HOLDOUT' if reason == 'HELDOUT_WORK_OR_RELATED_COLLECTION' else 'QUARANTINED'
        add(oid, 'kosh:' + obs[oid]['collection'], 'lexical_observation',
            kout['quarantine.jsonl']['file'], {'line_1_based': i}, status, reason)
    require(Counter(partition) == Counter({k: 1 for k in obs}), 'Kosh partition loses or repeats an ID')
    for row in observations:
        pin(PUBLIC + '/' + row['raw_file'], row['raw_sha256'])
    pin('experiments/kosh-download-method-20260928/intake-complete-38686.json',
        '7aac772fd6f062b5a96d709a7b30c7d5a0c29ce885658e384935cf3a5f9aad31')
    pin('experiments/kosh-download-method-20260928/field-coverage.json')
    print('Validated final Kosh observation partition and source hashes', flush=True)

    # Books/tool artifacts retain their own grain and rights; PDFs are not lexical rows.
    pdfs = read('sources/manifest.json')
    pdfs = [dict(x, local_path='sources/' + x['file']) for x in pdfs]
    pdfs += read('experiments/mackenzie-access-20260928/pdf-access.json')['files']
    for row in pdfs:
        name = pin(row['local_path'], row['sha256'], row['bytes'])
        add('pdf:' + name, 'reference_books', 'pdf_artifact', name, {}, 'REFERENCE_ONLY',
            'Page extraction/OCR, source relationship and intended use require separate review')
    resources = read('resources/manifest.json')
    for entry in resources['entries']:
        for row in entry['files']:
            name = pin(row['local_path'], row['sha256'], row['bytes'])
            add('resource:' + name, 'support:' + entry['repo'], 'tool_or_lexical_artifact', name, {},
                'REFERENCE_ONLY', 'Tool tables/code are not contextual translation gold')
    for family in ['ezafe-modeling-mp', 'UD_Middle_Persian-MPCD']:
        base = PUBLIC + '/' + family
        manifest = read(base + '/manifest.json')
        for row in manifest.values():
            if row.get('status') == 'ok' and row.get('file'):
                name = pin(base + '/' + row['file'], row['sha256'], row.get('bytes'))
                add('support:' + name, family, 'grammar_or_metadata_artifact', name, {}, 'REFERENCE_ONLY',
                    'Overlapping feature views; no automatic sentence alignment or CoNLL-U claim')

    # Later small, provenance-rich packets remain auxiliary until an explicit admission.
    s22 = 'experiments/composition-evidence-20260928/candidates.jsonl'
    for i, row in enumerate(read(s22), 1):
        require(row['status'] == 'STAGED_NOT_TRAIN_ADMITTED', 'Unexpected pedagogical admission')
        add(row['id'], 'supplied_S22', 'pedagogical_translation_pair', s22, {'line_1_based': i},
            reason='Printed teaching example; manuscript lineage, semantic and use review pending')
        pin(row['source_pdf'], row['source_pdf_sha256'])
        pin(row['image_path'], row['image_sha256'])
    grounded = 'experiments/grounded-supervision-20260927/'
    for leaf in ['qualification-decision.json', 'contrast-qualification.json']:
        path = grounded + leaf
        decision = read(path)
        require(decision['training_admitted'] is False, 'Unexpected annotation admission')
        for i, row in enumerate(decision['accepted']):
            add('annotation:' + row['annotation_id'], 'grounded_annotations', 'auxiliary_annotation', path,
                {'json_pointer': '/accepted/' + str(i)}, reason='Auxiliary development approval only; not training admission',
                parent_train_id=row['train_id'])
        for filename, sha in decision['source_files_sha256'].items():
            pin(filename, sha)
    for leaf in ['published-occurrences.json', 'lexical-packet.jsonl', 'DIRECTIVE-PILOT.json', 'CONTRAST-PILOT.json']:
        pin(grounded + leaf)
    for name, family, kind, reason in [
        (PAR + '/vocabulary-group-2.json', 'parsig_index', 'vocabulary_index', 'Forms/occurrences, not senses'),
        ('dictionary/entries.json', 'authored', 'draft_dictionary', 'Unreviewed and research-exposed; includes held-out work120'),
        ('experiments/published-annotation-access-20260927/authorized-detail.json', 'parsig_annotation', 'verification_capture', 'Same occurrence as published packet, not a sixth example'),
        ('experiments/composition-evidence-20260928/provenance-recovery.json', 'parsig_audit', 'rejected_candidate_ledger', '277 existing source rows, not extra data'),
        ('kb/study-status.md', 'authored', 'knowledge_base_index', 'Research-exposed narrative support, never wholesale gold')]:
        add('reference:' + name, family, kind, name, {}, 'REFERENCE_ONLY', reason)

    # Cross-source byte identity is diagnostic, not a claim of independent witness identity.
    same_bytes = defaultdict(list)
    for path, receipt in inputs.items():
        same_bytes[receipt['sha256']].append(path)
    report = {
        'status': 'CONSOLIDATED_NOT_NEW_TRAINING_ADMISSION',
        'counts_by_grain': dict(Counter(x['kind'] for x in catalogue)),
        'counts_by_status': dict(Counter(x['status'] for x in catalogue)),
        'counts_by_family': dict(Counter(x['family'] for x in catalogue)),
        'historical_control_pairs': len(core), 'newly_admitted_pairs': 0,
        'historical_train_sha256': TRAIN_SHA, 'expert_certified': False, 'paid_launch_admitted': False,
        'known_protected_archive_documents': sum(x['kind'] == 'archive_document' and
                                                x['status'] == 'PROTECTED_HOLDOUT' for x in catalogue),
        'exact_duplicate_control_pairs': 0,
        'control_same_source_target_variants': [v for v in variants.values() if len(v) > 1],
        'kosh': {'observations': len(obs), 'groups': len(groups), 'quarantined': len(quarantine),
                 'duplicate_provenance_rows': len(partition) - len(quarantine) - len(groups),
                 'cross_collection_pair_candidates': kosh['cross_collection_exact_pair_candidate_groups']},
        'byte_identical_input_groups': [v for v in same_bytes.values() if len(v) > 1],
        'limits': ['Counts have different grains and overlap; never sum into training pairs.',
                   'Historical core inherits prior AI qualifications and contamination audit; not specialist certification.',
                   'No new cross-corpus lineage or semantic clearance was inferred.',
                   'Reference-only documents may contain held-out quotations; none enter the training export.',
                   'PahGen317 and S27 are not verified local acquisitions.'],
    }
    require(sum(x['status'] == 'HISTORICAL_CONTROL' for x in catalogue) == len(core), 'Core parent mismatch')
    require(report['known_protected_archive_documents'] == 121, 'Known alternate-witness coverage changed')
    require(all(not x['training_admitted'] for x in catalogue), 'Catalogue admits unreviewed training')
    files = {'catalogue.jsonl': catalogue, 'train-core.jsonl': core,
             'review-queue.jsonl': [x for x in catalogue if x['status'] == 'REVIEW_REQUIRED'],
             'quarantine-index.jsonl': [x for x in catalogue if x['status'] in {'PROTECTED_HOLDOUT', 'QUARANTINED'}]}
    return inputs, files, report


def self_check():
    require(norm('a\u0304  x') == 'ā x' and norm('ā') != norm('a'), 'Normalization changes meaning')
    try:
        safe_path('../outside')
    except ValueError:
        pass
    else:
        raise AssertionError('Path escape accepted')
    require(checked_text(b'{"v":1}', digest(b'{"v":1}')) == '{"v":1}', 'Valid receipt rejected')
    try:
        checked_text(b'{"v":2}', digest(b'{"v":1}'))
    except ValueError:
        pass
    else:
        raise AssertionError('Changed input parsed under old receipt')
    for doc, work in [({'collection': 'parsig', 'id': '120'}, 120),
                      ({'collection': 'titus', 'source_url': 'https://titus.uni-frankfurt.de/a/snstrl/x.htm'}, 138),
                      ({'collection': 'titus', 'source_url': 'https://titus.uni-frankfurt.de/a/snstrs/x.htm'}, 138),
                      ({'collection': 'titus', 'source_url': 'https://titus.uni-frankfurt.de/a/zadspram/x.htm'}, 152),
                      ({'collection': 'avesta', 'source_url': 'https://www.avesta.org/mp/zadspram.pdf'}, 152),
                      ({'collection': 'persoaryan', 'source_url': 'https://www.persoaryanstudies.org/hkr.html'}, 117),
                      ({'collection': 'persoaryan', 'source_url': 'https://www.persoaryanstudies.org/uploads/s%c5%abr.pdf'}, 112),
                      ({'collection': 'titus', 'source_url': 'https://titus.uni-frankfurt.de/a/unknown/x.htm'}, None)]:
        require(document_holdout(doc) == work, 'Incorrect document protection mapping')
    source, target = 'ā', 'معنی'
    row = {'id': 'a', 'record_id': 'a', 'work_id': 'parsig:101', 'text': source, 'target': target,
           'source_language': 'pal', 'target_language': 'fa'}
    ledger = {'id': 'a', 'record_id': 'a', 'work_id': 'parsig:101', 'disposition': 'ELIGIBLE',
              'mechanical_status': 'PASS', 'provenance_status': 'PASS', 'split_status': 'PASS_IDENTITY_AND_PINNED_HOLDOUT',
              'source_text': source, 'target_text': target,
              'source_sha256': digest(source.encode()), 'target_sha256': digest(target.encode())}
    pair_checks(row, ledger)
    for bad in [dict(row, work_id='parsig:120'), dict(row, target='wrong'), dict(row, source_language='ave')]:
        try:
            pair_checks(bad, ledger)
        except ValueError:
            continue
        raise AssertionError('Unsafe pair accepted')
    print('PASS: normalization, path containment, held-out, text/hash and language gates')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--self-check', action='store_true')
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if args.self_check:
        self_check()
    else:
        if args.write:
            require(not OUT.exists() and not MANIFEST.exists(), 'Frozen output exists; do not overwrite')
        inputs, files, report = build()
        serialized = {name: b''.join(canonical(row) + b'\n' for row in rows) for name, rows in files.items()}
        require(sum(map(len, serialized.values())) < 200_000_000, 'Output size limit exceeded')
        if args.write:
            OUT.mkdir(parents=True, exist_ok=False)
            outputs = {}
            for name, raw in serialized.items():
                path = OUT / name
                path.write_bytes(raw)
                outputs[name] = {'path': path.relative_to(ROOT).as_posix(), 'sha256': digest(raw),
                                 'bytes': len(raw), 'rows': len(files[name])}
            report_raw = canonical(report) + b'\n'
            REPORT.write_bytes(report_raw)
            manifest = {'schema_version': 1, 'data_version': 2, 'date': '2026-09-28', 'status': report['status'],
                        'script_sha256': digest(Path(__file__).read_bytes()), 'inputs': inputs, 'outputs': outputs,
                        'quality_report_sha256': digest(report_raw), 'training_launch_admitted': False}
            # Manifest last is the completion marker; no partial output is a valid frozen resource.
            MANIFEST.write_bytes(canonical(manifest) + b'\n')
        print(json.dumps({'mode': 'write' if args.write else 'check', 'input_files': len(inputs),
                          'output_rows': {k: len(v) for k, v in files.items()},
                          'historical_control_pairs': len(files['train-core.jsonl']), 'new_training_pairs': 0}))
