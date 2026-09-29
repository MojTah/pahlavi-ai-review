"""Local mechanical dictionary census; no training admission or network access."""
import argparse
import ast
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / 'sources/local/public-texts-2026-09-20/kosh-all-dictionaries-20260928'
REPORT = ARCHIVE / 'acquisition-report.json'
TRAIN = ROOT / 'experiments/train-audit-20260927/qualified-v1/train.jsonl'
TRAIN_SHA = '15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc'
OUTPUT = Path(__file__).with_name('novelty-summary.json')
HELPER = ROOT / 'scripts/audit_training_corpus.py'
# Collection-name flags only, not validated work/witness mapping.
HELDOUT_FLAGS = {'hkr': 'Possible work117: Husraw and a Page',
                 'sns': 'Possible work138: Shayast nashayast',
                 'wz': 'Possible work152: Zadspram',
                 'mz': 'Medicine of Zadspram: possible work152 relationship, not exact identity'}


def digest(raw):
    return sha256(raw).hexdigest()


def checked_bytes(raw, expected, size=None):
    if digest(raw) != expected or (size is not None and len(raw) != size):
        raise ValueError('Input hash/size mismatch')
    return raw


def normal(value):
    """Full form only: NFC, casefold, whitespace collapse; punctuation retained."""
    return ' '.join(unicodedata.normalize('NFC', value).casefold().split())


def flatten(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from flatten(item)
    elif value is not None:
        raise ValueError('Unexpected non-string/non-list trc value')


def load_source_tokens():
    raw = HELPER.read_bytes()
    nodes = [n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name == 'source_tokens']
    if len(nodes) != 1:
        raise ValueError('Expected one existing source_tokens helper')
    namespace = {'unicodedata': unicodedata}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(HELPER), 'exec'), namespace)
    return namespace['source_tokens'], digest(raw)


class TrainingIndex:
    def __init__(self, sources, tokenize):
        self.full = {normal(s) for s in sources}
        self.rows = [tokenize(s) for s in sources]
        self.whole_tokens = set(self.rows)
        self.positions = defaultdict(list)
        for row_id, row in enumerate(self.rows):
            for pos, token in enumerate(row):
                self.positions[token].append((row_id, pos))

    def contains(self, sequence):
        if not sequence:
            return False
        # Anchor on the rarest token, then verify the exact contiguous sequence.
        offset = min(range(len(sequence)), key=lambda i: len(self.positions.get(sequence[i], ())))
        for row_id, position in self.positions.get(sequence[offset], ()):
            start = position - offset
            if start >= 0 and self.rows[row_id][start:start + len(sequence)] == sequence:
                return True
        return False


def form_counts(forms, index, tokenize):
    full = sum(f in index.full for f in forms)
    whole_tokens = sum(tokenize(f) in index.whole_tokens for f in forms if tokenize(f))
    present = sum(index.contains(tokenize(f)) for f in forms)
    empty = sum(not tokenize(f) for f in forms)
    return {'unique_normalized_full_trc': len(forms),
            'matches_normalized_training_whole_source': full,
            'matches_training_whole_source_token_sequence': whole_tokens,
            'occurs_as_exact_contiguous_training_token_sequence': present,
            'not_found_as_training_token_sequence': len(forms) - present - empty,
            'empty_after_source_token_normalization': empty}


def duplicate_counts(xml_counts):
    collections = defaultdict(set)
    total = Counter()
    for name, counts in xml_counts.items():
        total.update(counts)
        for key in counts:
            collections[key].add(name)
    shared = {key for key, names in collections.items() if len(names) > 1}
    return total, shared


def run():
    report_raw = REPORT.read_bytes()
    report = json.loads(report_raw)
    train_raw = checked_bytes(TRAIN.read_bytes(), TRAIN_SHA)
    rows = [json.loads(line) for line in train_raw.splitlines() if line.strip()]
    if len(rows) != 2237 or len({r['id'] for r in rows}) != 2237:
        raise ValueError('Historical TRAIN membership changed')
    tokenize, helper_sha = load_source_tokens()
    index = TrainingIndex([r['text'] for r in rows], tokenize)
    per_collection, xml_counts, form_sets, raw_inputs = [], {}, {}, []
    names = [item['collection'] for item in report['collections']]
    if len(names) != len(set(names)):
        raise ValueError('Duplicate collection in acquisition report')
    for item in report['collections']:
        name, receipt = item['collection'], item['receipt']
        summary = {'collection': name, 'acquisition_status': item['status'],
                   'heldout_collection_name_flag': HELDOUT_FLAGS.get(name),
                   'lineage_status': 'UNRESOLVED_NO_COLLECTION_IS_CLEARED',
                   'admitted_training_pairs': 0}
        per_collection.append(summary)
        if receipt.get('status') != 'ok':
            summary['census_status'] = 'NO_SUCCESSFUL_RAW_RESPONSE'
            continue
        path = (ARCHIVE / receipt['file']).resolve()
        if not path.is_relative_to(ARCHIVE.resolve()):
            raise ValueError('Receipt path escapes acquisition archive')
        raw = checked_bytes(path.read_bytes(), receipt['sha256'], receipt['bytes'])
        raw_inputs.append({'collection': name, 'file': receipt['file'], 'sha256': digest(raw), 'bytes': len(raw)})
        if item['status'] == 'SCHEMA_ERROR':
            summary['census_status'] = 'ACQUISITION_SCHEMA_ERROR_NOT_COUNTED'
            continue
        entries = json.loads(raw)['data']['entries']
        if not isinstance(entries, list) or any(not isinstance(e, dict) for e in entries):
            raise ValueError('Unexpected entries schema')
        ids = [e.get('id') for e in entries]
        if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
            raise ValueError('Missing or duplicate entry IDs')
        if len(entries) != item['entries']:
            raise ValueError('Receipt report entry-count mismatch')
        counts, forms, stats = Counter(), set(), Counter()
        for entry in entries:
            xml = entry.get('xml')
            if isinstance(xml, str) and xml.strip():
                stats['xml_present'] += 1
                counts[digest(xml.encode('utf-8'))] += 1
                try:
                    ET.fromstring(xml)
                except ET.ParseError:
                    stats['xml_parse_failures'] += 1
            else:
                stats['xml_missing_or_invalid_type'] += 1
            values = list(flatten(entry.get('trc')))
            stats['raw_full_trc_values'] += len(values)
            if not values:
                stats['entries_without_trc_values'] += 1
            for value in values:
                norm = normal(value)
                if norm:
                    forms.add(norm)
                else:
                    stats['empty_full_trc_values'] += 1
        xml_counts[name], form_sets[name] = counts, forms
        summary.update(census_status='COUNTED_RAW_DICTIONARY_ROWS', entries=len(entries),
                       xml_present=stats['xml_present'], xml_parse_failures=stats['xml_parse_failures'],
                       xml_missing_or_invalid_type=stats['xml_missing_or_invalid_type'],
                       raw_full_trc_values=stats['raw_full_trc_values'],
                       entries_without_trc_values=stats['entries_without_trc_values'],
                       empty_full_trc_values=stats['empty_full_trc_values'],
                       unique_exact_xml_strings=len(counts),
                       duplicate_xml_rows_within_collection=sum(counts.values()) - len(counts),
                       **form_counts(forms, index, tokenize))
    xml_total, shared = duplicate_counts(xml_counts)
    for item in per_collection:
        counts = xml_counts.get(item['collection'], {})
        item['xml_rows_with_identical_xml_in_other_collections'] = sum(n for key, n in counts.items() if key in shared)
    all_forms = set().union(*form_sets.values()) if form_sets else set()
    flagged_forms = set().union(*(v for k, v in form_sets.items() if k in HELDOUT_FLAGS))
    unflagged_forms = set().union(*(v for k, v in form_sets.items() if k not in HELDOUT_FLAGS))
    result = {'status': 'MECHANICAL_CENSUS_ONLY_NOT_TRAINING_QUALIFICATION',
              'script_sha256': digest(Path(__file__).read_bytes()),
              'acquisition_report_sha256': digest(report_raw),
              'acquisition_snapshot': {'collections_reported': len(names),
                                       'stop_reason': report.get('stop_reason'),
                                       'requested_cap_per_collection': report.get('requested_cap_per_collection')},
              'source_tokens_helper_sha256': helper_sha,
              'baseline': {'rows': 2237, 'sha256': TRAIN_SHA, 'compared_field': 'text', 'heldout_answers_read': False},
              'raw_inputs': raw_inputs, 'collections': per_collection,
              'totals': {'downloaded_dictionary_rows_counted': sum(c.get('entries', 0) for c in per_collection),
                         'unique_exact_xml_strings': len(xml_total),
                         'duplicate_xml_row_excess_global': sum(xml_total.values()) - len(xml_total),
                         'xml_strings_shared_across_collections': len(shared),
                         **form_counts(all_forms, index, tokenize)},
              'forms_present_in_potentially_heldout_collections': form_counts(flagged_forms, index, tokenize),
              'forms_only_in_unflagged_but_lineage_unresolved_collections': form_counts(unflagged_forms - flagged_forms, index, tokenize),
              'training_admission': {'historical_pairs_before': 2237, 'historical_pairs_after': 2237,
                                     'new_lexical_pairs': 0, 'new_attested_sentence_pairs': 0},
              'limits': ['Not a completeness proof; capped, failed and missing collections remain unresolved.',
                         'Dictionary rows/forms are not sentence pairs or independent attestations.',
                         'Unseen orthography does not establish new meaning, usable translation, or scholarly correctness.',
                         'Exact XML uses the entire unmodified XML string including IDs/whitespace; differently serialized duplicates and shared edition lineage are not detected.',
                         'Full trc values are flattened from lists only; no parenthesis, slash, inflection or variant expansion.',
                         'Full forms: NFC/casefold/whitespace collapse, punctuation retained. Token matching additionally strips boundary Unicode punctuation using the existing audit helper.',
                         'Collection-name held-out flags are heuristic; absence of a flag is not clearance. Every collection has unresolved lineage.',
                         'No DEV/TEST answers, semantic alignment, sense validation, expert review, target creation or training admission.']}
    if REPORT.read_bytes() != report_raw:
        raise ValueError('Acquisition report changed during census; no output written')
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(OUTPUT), 'totals': result['totals'], 'admitted': 0}))


def self_check():
    tokenize, _ = load_source_tokens()
    assert normal('  A\u0304B\tC  ') == 'āb c'
    assert list(flatten(['a(b)', ['x/y']])) == ['a(b)', 'x/y']
    index = TrainingIndex(['āb, c d', 'x y'], tokenize)
    assert index.contains(tokenize('c d')) and not index.contains(tokenize('d x'))
    assert not index.contains(()) and not index.contains(tokenize('a b'))
    counts = form_counts({'āb, c d', 'c d', 'new', '...'}, index, tokenize)
    assert counts['matches_normalized_training_whole_source'] == 1
    assert counts['occurs_as_exact_contiguous_training_token_sequence'] == 2
    assert counts['not_found_as_training_token_sequence'] == 1
    total, shared = duplicate_counts({'a': Counter({'same': 2, 'x': 1}), 'b': Counter({'same': 1})})
    assert len(total) == 2 and sum(total.values()) - len(total) == 2 and shared == {'same'}
    assert checked_bytes(b'good', digest(b'good'), 4) == b'good'
    for sha, size in ((digest(b'bad'), 4), (digest(b'good'), 5)):
        try:
            checked_bytes(b'good', sha, size)
        except ValueError:
            pass
        else:
            raise AssertionError('Hash/size mismatch accepted')
    print('PASS: normalization, full-form preservation, contiguous matching, deduplication, hash/size rejection')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-check', action='store_true')
    parser.add_argument('--confirmed-acquisition-finished', action='store_true')
    args = parser.parse_args()
    if args.self_check:
        self_check()
    elif args.confirmed_acquisition_finished:
        run()
    else:
        parser.error('Root must confirm acquisition is finished before running the census')
