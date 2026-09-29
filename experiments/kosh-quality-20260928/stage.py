"""Local, lossless dictionary staging. Never modifies or admits training data."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'experiments/kosh-acquisition-20260928'))
from novelty import checked_bytes, digest, flatten, TrainingIndex, load_source_tokens

BASE = ROOT / 'sources/local/public-texts-2026-09-20'
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'resources/local/kosh-quality-20260928'
INTAKE = ROOT / 'experiments/kosh-download-method-20260928/intake-snapshot-5992.json'
INTAKE_SHA = '923a3c045ca8e1cbeaf96d64afdcab69874a990fce7343553038e480c41607f2'
EXPANSION = ROOT / 'experiments/kosh-download-method-20260928/size1000-pass-final.json'
EXPANSION_SHA = 'f7445e466c22ca315accdaadf494afd1f5953574c4a59ce822a5d674997768c0'
CHECKPOINT = ROOT / 'experiments/kosh-download-method-20260928/intake-checkpoint-34539.json'
CHECKPOINT_SHA = '857fc6951396d7e86d5e74a39416b3a6ab2c554125e8aea99fa6b0997421983f'
COMPLETE = ROOT / 'experiments/kosh-download-method-20260928/intake-complete-38686.json'
COMPLETE_SHA = '7aac772fd6f062b5a96d709a7b30c7d5a0c29ce885658e384935cf3a5f9aad31'
LEGACY = ROOT / 'experiments/kosh-download-method-20260928/legacy-extraction.json'
LEGACY_SHA = 'fdaffa5807e75cacebd8c8a3d9f39bbaea969abf50e98b23ff54218029f87412'
TRAIN = ROOT / 'experiments/train-audit-20260927/qualified-v1/train.jsonl'
TRAIN_SHA = '15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc'
HELDOUT = {'hkr', 'sns', 'wz', 'mz'}
LANGUAGE_REVIEW = {'mmp', 'wmiar'}
FLAT_METADATA = {'trl', 'attest', 'attest_with_avestan', 'attest_without_avestan',
                 'citation', 'comment', 'pos', 'gramm', 'definition', 'category', 'orig_trc'}
PLACEHOLDERS = {'', '_', '?', '(?)'}


def norm(text):
    return ' '.join(unicodedata.normalize('NFC', text).split())


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def checked_path(base, name):
    path = (base / name).resolve()
    if not path.is_relative_to(base.resolve()):
        raise ValueError('Input path escapes archive')
    return path


def load_receipt(base, receipt):
    return checked_bytes(checked_path(base, receipt['file']).read_bytes(), receipt['sha256'], receipt['bytes'])


def leaf(node):
    if len(node):
        raise ValueError('NESTED_TEXT_NEEDS_REVIEW')
    return node.text or ''


def element_only(node):
    if norm(node.text or '') or any(norm(child.tail or '') for child in node):
        raise ValueError('UNSCOPED_TEXT_NEEDS_REVIEW')


def extract(xml):
    """Accept only one structurally unambiguous form group and its own sense."""
    entry = ET.fromstring(xml)
    if entry.tag != 'entry':
        raise ValueError('UNKNOWN_ENTRY_ROOT')
    element_only(entry)
    children = list(entry)
    if len(children) == 1 and children[0].tag == 'form':
        scope = children[0]
        element_only(scope)
    elif [n.tag for n in children] == ['form', 'sense']:
        form = children[0]
        element_only(form)
        if any(n.tag not in {'trc', 'trl', 'orig_trc'} for n in form):
            raise ValueError('UNKNOWN_FORM_METADATA')
        if len(form.findall('trc')) != 1:
            raise ValueError('AMBIGUOUS_FORM_GROUP')
        forms = [leaf(form.find('trc'))]
        return forms, leaf(children[1])
    else:
        scope = entry
    if any(n.tag not in FLAT_METADATA | {'trc', 'sense'} for n in scope):
        raise ValueError('UNKNOWN_OR_COMPLEX_SCHEMA')
    if len(scope.findall('trc')) != 1 or len(scope.findall('sense')) > 1:
        raise ValueError('AMBIGUOUS_FORM_SENSE_BOUNDARY')
    trc = scope.find('trc')
    if len(trc):
        if any(n.tag != 'form' for n in trc) or norm(trc.text or '') or any(norm(n.tail or '') for n in trc):
            raise ValueError('AMBIGUOUS_ALTERNATIVE_STRUCTURE')
        forms = [leaf(n) for n in trc]
    else:
        forms = [leaf(trc)]
    sense = scope.find('sense')
    return forms, leaf(sense) if sense is not None else ''


def reason_for(name, entry):
    if name in HELDOUT:
        return 'HELDOUT_WORK_OR_RELATED_COLLECTION', None
    if name in LANGUAGE_REVIEW:
        return 'SOURCE_LANGUAGE_OR_LOANWORD_REVIEW', None
    if name == 'cpd':
        try:
            ET.fromstring(entry['xml'])
        except ET.ParseError:
            return 'MALFORMED_XML', None
        return 'COMPLEX_CPD_FORM_SENSE_MAPPING_REVIEW', None
    try:
        forms, sense = extract(entry['xml'])
    except (ValueError, ET.ParseError) as exc:
        return str(exc), None
    normalized_forms = [norm(f) for f in forms]
    if any(f in PLACEHOLDERS for f in normalized_forms):
        return 'MISSING_OR_PLACEHOLDER_FORM', None
    if [norm(f) for f in flatten(entry.get('trc'))] != normalized_forms:
        return 'JSON_XML_FORM_MISMATCH', None
    if norm(sense) in PLACEHOLDERS:
        return 'MISSING_OR_PLACEHOLDER_MEANING', None
    if any('\ufffd' in s or any(unicodedata.category(c) == 'Cs' for c in s) for s in forms + [sense]):
        return 'DAMAGED_UNICODE', None
    return None, (tuple(normalized_forms), norm(sense))


def write_jsonl(path, rows):
    raw = b''.join(canonical(row) + b'\n' for row in rows)
    path.write_bytes(raw)
    return {'file': str(path.relative_to(ROOT)).replace('\\', '/'), 'rows': len(rows),
            'bytes': len(raw), 'sha256': digest(raw)}


def verified_superset(old_entries, new_entries):
    old = {e['id']: e for e in old_entries}
    new = {e['id']: e for e in new_entries}
    if len(old) != len(old_entries) or len(new) != len(new_entries):
        raise ValueError('Duplicate IDs in expansion comparison')
    if any(key not in new or new[key] != value for key, value in old.items()):
        raise ValueError('Expansion drops or changes baseline evidence')
    return set(old)


def run(expanded=False, checkpoint=False, complete=False):
    # Validate all inputs before any output; later downloader changes fail closed.
    checkpoint = checkpoint or complete
    expanded = expanded or checkpoint
    version = 'v4' if complete else 'v3' if checkpoint else 'v2' if expanded else 'v1'
    out = OUT / 'complete-v4' if complete else OUT / 'checkpoint-v3' if checkpoint else OUT / 'expanded-v2' if expanded else OUT
    summary_path = HERE / ('summary.json' if version == 'v1' else f'summary-{version}.json')
    if summary_path.exists() or any((out / n).exists() for n in ['observations.jsonl', 'staged-groups.jsonl', 'quarantine.jsonl']):
        raise ValueError('Frozen output already exists; choose a new reviewed version, never overwrite it')
    snapshot = json.loads(checked_bytes(INTAKE.read_bytes(), INTAKE_SHA))
    prior_provenance = {}
    if expanded:
        supplement = json.loads(checked_bytes(EXPANSION.read_bytes(), EXPANSION_SHA))
        replaced = set()
        for name, item in supplement['collections'].items():
            if item['receipt'].get('status') != 'ok' or not item.get('entries'):
                continue
            previous = snapshot['collections'][name]
            old_rows = json.loads(load_receipt(checked_path(BASE, previous['archive']), previous['receipt']))['data']['entries']
            new_rows = json.loads(load_receipt(checked_path(BASE, item['archive']), item['receipt']))['data']['entries']
            for oid in verified_superset(old_rows, new_rows):
                prior_provenance[f'kosh:{name}:{oid}'] = {
                    'raw_file': f"{previous['archive']}/{previous['receipt']['file']}",
                    'raw_sha256': previous['receipt']['sha256'], 'source_url': previous['receipt']['url']}
            snapshot['collections'][name] = item
            replaced.add(name)
        if replaced != {'cpd', 'cpd_de', 'da', 'dd1', 'dk5', 'dk6', 'dk7', 'dk8'} or len(prior_provenance) != 800:
            raise ValueError('Unexpected expansion coverage')
    checkpoints = [(CHECKPOINT, CHECKPOINT_SHA, 9597)] if checkpoint else []
    if complete:
        checkpoints.append((COMPLETE, COMPLETE_SHA, 34539))
    for manifest_path, manifest_sha, expected_previous in checkpoints:
        latest = json.loads(checked_bytes(manifest_path.read_bytes(), manifest_sha))
        if set(latest['collections']) != set(snapshot['collections']):
            raise ValueError('Unexpected checkpoint collection set')
        prior_provenance = {}
        previous_captures = list(snapshot['collections'].items())
        previous_captures += [(item['collection'], item) for item in snapshot.get('additional_captures', [])]
        latest_extra = {(item['collection'], item['data_key']): item for item in latest.get('additional_captures', [])}
        for name, previous in previous_captures:
            if previous['receipt'].get('status') != 'ok' or not previous.get('entries'):
                continue
            key = previous.get('data_key', 'entries')
            current = latest['collections'][name] if key == 'entries' else latest_extra[(name, key)]
            old_rows = json.loads(load_receipt(checked_path(BASE, previous['archive']), previous['receipt']))['data'][key]
            new_rows = json.loads(load_receipt(checked_path(BASE, current['archive']), current['receipt']))['data'][key]
            for oid in verified_superset(old_rows, new_rows):
                prior_provenance[f'kosh:{name}:{oid}'] = {
                    'raw_file': f"{previous['archive']}/{previous['receipt']['file']}",
                    'raw_sha256': previous['receipt']['sha256'], 'source_url': previous['receipt']['url']}
        if len(prior_provenance) != expected_previous:
            raise ValueError('Previous version baseline coverage changed')
        catalogue = latest['catalogue']
        load_receipt(checked_path(BASE, catalogue['archive']), catalogue['receipt'])
        snapshot = latest
    expected_current = 38686 if complete else 34539 if checkpoint else 9597 if expanded else 5992
    legacy_receipt = json.loads(checked_bytes(LEGACY.read_bytes(), LEGACY_SHA))
    observations, quarantine, groups = [], [], {}
    collection_counts = defaultdict(Counter)
    input_ids, form_senses = set(), defaultdict(set)
    original_snapshot = json.loads(checked_bytes((ROOT / 'experiments/kosh-acquisition-20260928/acquisition-report.json').read_bytes(),
                                                '075d3c4d7043ce10ab08aaa2e638af67735c48cc621bd2659bef91c42607dea3'))
    old = {c['collection']: c for c in original_snapshot['collections'] if c['receipt'].get('status') == 'ok'}
    reused = 0
    captures = list(snapshot['collections'].items())
    captures += [(item['collection'], item) for item in snapshot.get('additional_captures', [])]
    for name, item in captures:
        if item['receipt'].get('status') != 'ok' or not item.get('entries'):
            continue
        receipt = item['receipt']
        raw = load_receipt(checked_path(BASE, item['archive']), receipt)
        data_key = item.get('data_key', 'entries')
        if data_key not in {'entries', 'ids'}:
            raise ValueError('Unknown capture data key')
        entries = json.loads(raw)['data'][data_key]
        if len(entries) != item['entries']:
            raise ValueError('Snapshot count mismatch')
        if name in old and data_key == 'entries':
            if receipt['sha256'] != old[name]['receipt']['sha256']:
                raise ValueError('Previously counted collection changed')
            reused += len(entries)
        for entry in entries:
            if not isinstance(entry.get('id'), str) or not entry['id']:
                raise ValueError('Missing entry ID')
            oid = f"kosh:{name}:{entry['id']}"
            if oid in input_ids:
                raise ValueError('Duplicate observation ID')
            input_ids.add(oid)
            reason, pair = reason_for(name, entry)
            observation = {'id': oid, 'collection': name, 'raw_file': f"{item['archive']}/{receipt['file']}",
                           'raw_sha256': receipt['sha256'], 'source_url': receipt['url'],
                           'source_record': entry, 'status': 'QUARANTINED' if reason else 'STAGED_NOT_TRAIN_ADMITTED',
                           'quarantine_reason': reason, 'lineage_status': 'UNRESOLVED', 'expert_certified': False}
            observations.append(observation)
            if oid in prior_provenance:
                observation['identical_record_in_baseline'] = prior_provenance[oid]
            collection_counts[name]['input_records'] += 1
            if reason:
                quarantine.append({'observation_id': oid, 'reason': reason})
                collection_counts[name]['quarantined_records'] += 1
                continue
            forms, sense = pair
            key = (name, forms, sense)
            if key not in groups:
                groups[key] = {'id': 'lex:' + digest(canonical(key)), 'collection': name,
                               'forms': forms, 'meaning_as_published': sense, 'observation_ids': [],
                               'language_status': 'NOT_VERIFIED', 'lineage_status': 'UNRESOLVED',
                               'expert_certified': False, 'status': 'STAGED_NOT_TRAIN_ADMITTED'}
            groups[key]['observation_ids'].append(oid)
            form_senses[(name, forms)].add(sense)
            collection_counts[name]['staged_input_records'] += 1
    if len(observations) != expected_current or reused != 3292:
        raise ValueError('Current input/reuse census differs from frozen handoff')
    if checkpoint and any(collection_counts[name]['input_records'] != count
                          for name, count in snapshot['effective_counts'].items()):
        raise ValueError('Effective collection census differs from frozen checkpoint')
    legacy_file = next(r for r in legacy_receipt['outputs'] if r['file'] == 'cpd.jsonl')
    legacy_raw = load_receipt(BASE / 'cologne-legacy-cpd-20260928', legacy_file)
    legacy_pairs = Counter()
    legacy_rows = [json.loads(line) for line in legacy_raw.splitlines()]
    if len(legacy_rows) != 4218:
        raise ValueError('Legacy count mismatch')
    for row in legacy_rows:
        if set(row) != {'source_line', 'dictionary_id', 'headword', 'entry'} or row['dictionary_id'] != 4:
            raise ValueError('Legacy schema mismatch')
        oid = f"legacy-cpd:{row['source_line']}"
        if oid in input_ids:
            raise ValueError('Duplicate legacy source line')
        input_ids.add(oid)
        legacy_pairs[(norm(row['headword']), norm(row['entry']))] += 1
        observations.append({'id': oid, 'collection': 'legacy-cpd', 'raw_file': 'cologne-legacy-cpd-20260928/cpd.jsonl',
                             'raw_sha256': legacy_file['sha256'], 'source_record': row,
                             'license': legacy_receipt['rights'], 'revision': legacy_receipt['revision'],
                             'status': 'QUARANTINED', 'quarantine_reason': 'LEGACY_ENCODING_AND_EDITION_REVIEW',
                             'lineage_status': 'UNRESOLVED', 'expert_certified': False})
        quarantine.append({'observation_id': oid, 'reason': 'LEGACY_ENCODING_AND_EDITION_REVIEW'})
    staged = list(groups.values())
    tokens, helper_sha = load_source_tokens()
    if helper_sha != '9c616eae976683ce16e5428af10b3e4425aa4d72e0f8ac4e33020f5238325abc':
        raise ValueError('Changed TRAIN token helper')
    train = [json.loads(line) for line in checked_bytes(TRAIN.read_bytes(), TRAIN_SHA).splitlines()]
    index = TrainingIndex([r['text'] for r in train], tokens)
    cross_collection = defaultdict(list)
    for group in staged:
        key = (group['collection'], group['forms'])
        group['multiple_published_meanings_for_form_group'] = len(form_senses[key]) > 1
        group['train_source_form_matches'] = [index.contains(tokens(f)) for f in group['forms']]
        group['meaning_has_arabic_script_letters'] = any('\u0600' <= c <= '\u06ff' and c.isalpha() for c in group['meaning_as_published'])
        cross_collection[(group['forms'], group['meaning_as_published'])].append(group['id'])
        collection_counts[group['collection']]['staged_groups'] += 1
    accounted = [q['observation_id'] for q in quarantine] + [i for g in staged for i in g['observation_ids']]
    if len(accounted) != len(set(accounted)) or set(accounted) != input_ids:
        raise ValueError('Every input must occur exactly once in staging/quarantine provenance')
    out.mkdir(parents=True, exist_ok=True)
    outputs = [write_jsonl(out / name, rows) for name, rows in
               [('observations.jsonl', observations), ('staged-groups.jsonl', staged), ('quarantine.jsonl', quarantine)]]
    summary = {'status': 'MECHANICAL_STAGING_COMPLETE_NOT_TRAINING_ADMISSION',
               'script_sha256': digest(Path(__file__).read_bytes()), 'input_manifest_sha256': INTAKE_SHA,
               'legacy_receipt_sha256': LEGACY_SHA, 'baseline_train_sha256': TRAIN_SHA,
               'source_token_helper_sha256': helper_sha, 'input_current_site_records': expected_current,
               'expansion_manifest_sha256': EXPANSION_SHA if expanded else None,
               'checkpoint_manifest_sha256': CHECKPOINT_SHA if checkpoint else None,
               'complete_manifest_sha256': COMPLETE_SHA if complete else None,
               'new_current_site_ids_since_v2': expected_current - 9597 if checkpoint else None,
               'new_current_site_ids_since_v3': expected_current - 34539 if complete else None,
               'catalogue_count_reconciliation_complete': snapshot.get('catalogue_count_reconciliation_complete', False),
               'catalogue_source': snapshot.get('catalogue'),
               'gaps_to_reported_counts': snapshot.get('gaps_to_reported_counts'),
               'expansion_baseline_records_verified_unchanged': len(prior_provenance),
               'expansion_new_record_ids': expected_current - 5992,
               'previously_counted_records_reused_once': reused, 'additional_current_site_records': expected_current - reused,
               'legacy_records_separate_edition': len(legacy_rows), 'total_observations': len(observations),
               'staged_groups': len(staged), 'staged_input_records': sum(len(g['observation_ids']) for g in staged),
               'duplicate_staged_rows_collapsed': sum(len(g['observation_ids']) - 1 for g in staged),
               'quarantine_counts': dict(Counter(q['reason'] for q in quarantine)),
               'quarantined_records': len(quarantine), 'per_collection': dict(collection_counts),
               'legacy_unique_raw_pairs': len(legacy_pairs), 'legacy_duplicate_raw_rows': sum(legacy_pairs.values()) - len(legacy_pairs),
               'cross_collection_exact_pair_candidate_groups': sum(len(ids) > 1 for ids in cross_collection.values()),
               'groups_with_multiple_published_meanings': sum(g['multiple_published_meanings_for_form_group'] for g in staged),
               'groups_with_arabic_script_meanings_not_verified_persian': sum(g['meaning_has_arabic_script_letters'] for g in staged),
               'outputs': outputs, 'input_id_coverage_exactly_once': True,
               'training_admission': {'historical_pairs_before': 2237, 'historical_pairs_after': 2237, 'new_pairs': 0},
               'limits': ['Reported Kosh catalogue counts reconcile; this is not an entire MPCorpus website export.' if complete else
                          'Capped/incomplete source snapshot; not a complete dictionary export.',
                          'Staging preserves published text, not proof of correct source reading or meaning.',
                          'Arabic-script letters are not a verified Persian-language label.',
                          'No splitting variants, synthetic translations, legacy decoding, or semantic duplicate inference.',
                          'All lineage unresolved; known held-out-related collections quarantined wholesale.',
                          'Legacy and current editions are not counted as independent novel meanings.',
                          'Only exact textual duplicates within each collection collapse; all evidence remains in observations.',
                          'No DEV/TEST answers read; original TRAIN and evaluation remain unchanged.']}
    summary_path.write_bytes(canonical(summary) + b'\n')
    print(json.dumps({k: summary[k] for k in ['status', 'total_observations', 'staged_groups', 'duplicate_staged_rows_collapsed', 'quarantined_records', 'quarantine_counts']}))


def self_check():
    assert norm(' a\u0304\n b ') == 'ā b'
    assert extract('<entry><trc>x, y</trc><sense>gloss</sense></entry>') == (['x, y'], 'gloss')
    assert extract('<entry><form><trc>x</trc><sense>noun</sense></form></entry>') == (['x'], 'noun')
    assert extract('<entry><trc><form>x</form><form>y</form></trc><sense>g</sense></entry>') == (['x', 'y'], 'g')
    for xml in ['<entry><form><trc>x</trc></form><sense>noun</sense><form><trc>y</trc></form><sense>adjective</sense></entry>',
                '<entry><trc>x</trc><sense>one</sense><sense>two</sense></entry>']:
        try: extract(xml)
        except ValueError: pass
        else: raise AssertionError('Ambiguous sense mapping accepted')
    e = {'trc': ['x'], 'xml': '<entry><trc>x</trc><sense>?</sense></entry>'}
    assert reason_for('acpv1_7', e)[0] == 'MISSING_OR_PLACEHOLDER_MEANING'
    assert reason_for('sns', e)[0] == 'HELDOUT_WORK_OR_RELATED_COLLECTION'
    e['xml'] = '<entry><trc>y</trc><sense>meaning</sense></entry>'
    assert reason_for('acpv1_7', e)[0] == 'JSON_XML_FORM_MISMATCH'
    assert reason_for('cpd', {'xml': '<entry>broken & data</entry>'})[0] == 'MALFORMED_XML'
    for xml in [
        '<entry><trc>x</trc><sense>good</sense>but not in this context</entry>',
        '<entry><form><trc>x</trc></form>not x<sense>good</sense></entry>',
        '<entry>uncertain<trc>x</trc><sense>good</sense></entry>',
        '<entry><form><trc>x</trc>or y<sense>good</sense></form></entry>',
        '<entry><form>uncertain<trc>x</trc></form><sense>good</sense></entry>',
    ]:
        assert reason_for('acpv1_7', {'trc': ['x'], 'xml': xml})[0] == 'UNSCOPED_TEXT_NEEDS_REVIEW'
    assert extract('<entry> \n<trc>x</trc>\n<sense>good</sense> </entry>') == (['x'], 'good')
    assert verified_superset([{'id': 'a', 'x': 1}], [{'id': 'a', 'x': 1}, {'id': 'b'}]) == {'a'}
    for incoming in [[{'id': 'a', 'x': 2}], [{'id': 'b'}], [{'id': 'a', 'x': 1}] * 2]:
        try: verified_superset([{'id': 'a', 'x': 1}], incoming)
        except ValueError: pass
        else: raise AssertionError('Changed, missing or duplicate baseline accepted')
    for operation in [lambda: checked_path(OUT, '../escape'), lambda: checked_bytes(b'wrong', digest(b'right'))]:
        try: operation()
        except ValueError: pass
        else: raise AssertionError('Invalid input accepted')
    print('PASS: schema boundaries, quarantine, NFC, input guards and immutable baseline reconciliation')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-check', action='store_true')
    version_flags = parser.add_mutually_exclusive_group()
    version_flags.add_argument('--expanded', action='store_true', help='Use frozen larger captures; preserve v1 outputs')
    version_flags.add_argument('--checkpoint', action='store_true', help='Use frozen 34539-record checkpoint; preserve v1/v2')
    version_flags.add_argument('--complete', action='store_true', help='Use final 38686-record capture; preserve v1/v2/v3')
    args = parser.parse_args()
    self_check() if args.self_check else run(args.expanded, args.checkpoint, args.complete)
