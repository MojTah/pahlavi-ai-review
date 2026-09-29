"""Exhaustive local mechanical screening; flagged meanings require recorded AI review.

No source writes, network, model inference, or old-label semantic endorsement.
"""
import ast
from collections import Counter, defaultdict
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import unicodedata as ud

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).with_name('historical-audit.json')
ARCHIVE = ROOT / 'sources/local/parsig-2026-09-20'
HIST = ROOT / 'resources/local/data-qualification-20260928/ready-v1/historical-control-fa.jsonl'
LEDGER = ROOT / 'experiments/train-audit-20260927/qualified-v1/final-ledger.jsonl'
EXPORT = ARCHIVE / 'exports/text-units.jsonl'
TRAIN = ROOT / 'resources/local/mixed-supervision-20260929/data/train.jsonl'


def digest(data):
    return sha256(data).hexdigest()


def rows(path):
    return [json.loads(line) for line in path.read_text('utf-8-sig').splitlines() if line.strip()]


def joined(value):
    if isinstance(value, str):
        return value
    return '\n'.join(x['Section'] if isinstance(x, dict) else x for x in (value or []))


def normalized(text):
    return ' '.join(ud.normalize('NFC', text).casefold().split())


NUMBERS = {'dō': (2, 'دو'), 'se': (3, 'سه'), 'čahār': (4, 'چهار'),
           'panǰ': (5, 'پنج'), 'panj': (5, 'پنج'), 'šaš': (6, 'شش'),
           'haft': (7, 'هفت'), 'hašt': (8, 'هشت'), 'nōh': (9, 'نه'),
           'dah': (10, 'ده'), 'wīst': (20, 'بیست'), 'sad': (100, 'صد'),
           'hazār': (1000, 'هزار')}
PERSIAN_NEG = re.compile(r'(?:\b(?:نه|هرگز|نیست\S*|نب\S*|نش\S*|نمی\S*|نخواهد\S*|نکرد\S*|نکن\S*|مکن\S*|مدار\S*|مباد\S*|نباید\S*|ناید\S*|مگوی\S*|بدون)\b|بی[\u200c -]|ن[‌ ]?می|نیام|ندار|ندهد|ندید|نرف|نزد|نافر|نپذ|نمان|نرس|نزی|نترس|ندان|نبود|نخواهد|دروغ)')


def main():
    prior = json.loads(OUT.read_text('utf-8')) if OUT.exists() else {}
    adjudications = prior.get('adjudications', [])
    historic = rows(HIST)
    ledger = {r['id']: r for r in rows(LEDGER)}
    export = {r['id']: (i + 1, r) for i, r in enumerate(rows(EXPORT))}
    manifest = json.loads((ARCHIVE / 'manifest.json').read_text('utf-8'))
    tree = ast.parse((ROOT / 'data/unified-corpus/build.py').read_text('utf-8'))
    protected = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                     and any(isinstance(t, ast.Name) and t.id == 'HOLDOUT' for t in n.targets))
    exposed = Counter(r['id'] for r in rows(TRAIN))
    raw_cache, raw_inputs = {}, {}
    result, source_groups, target_groups = [], defaultdict(list), defaultdict(list)
    characters = Counter()
    for line, row in enumerate(historic, 1):
        rid = row['id']
        export_line, unit = export[row['record_id']]
        endpoint = f"surf/paragraph/{unit['book_id']}/{unit['chapter_id']}/All"
        pointer = manifest[endpoint]
        if endpoint not in raw_cache:
            data = (ARCHIVE / pointer['file']).read_bytes()
            raw_inputs[pointer['file']] = {'sha256': digest(data), 'bytes': len(data),
                                        'archive_hash_matches': digest(data) == pointer['sha256'] and len(data) == pointer['bytes']}
            raw_cache[endpoint] = {str(r['Code']): (i, r) for i, r in enumerate(json.loads(data))}
        raw_index, raw = raw_cache[endpoint][row['record_id'].split(':')[1]]
        old = ledger[rid]
        raw_source, raw_target = joined(raw.get('Transcription')), joined(raw.get('Translation'))
        source = raw_source.strip()
        target = raw_target.strip()
        source_suffix, target_suffix = old['edition'], row['credit']
        source = source[:-len(source_suffix)].strip() if source_suffix and source.endswith(source_suffix) else source
        target = target[:-len(target_suffix)].strip() if target_suffix and target.endswith(target_suffix) else target
        checks = {
            'raw_archive_sha256_and_size': raw_inputs[pointer['file']]['archive_hash_matches'],
            'raw_export_unit_exact': raw == unit['raw_source_unit'],
            'source_field_exact_after_recorded_citation_removal': source == row['text'],
            'target_field_exact_after_recorded_citation_removal': target == row['target'],
            'raw_source_pointer_matches_export_and_ledger': pointer == unit['source'] == old['raw_pointer'],
            'parent_work_matches_raw_endpoint': row['work_id'] == 'parsig:' + str(unit['book_id']),
            'raw_chapter_matches_parent': str(raw['ChapterCode']) == str(unit['chapter_id']),
            'raw_sequence_matches_export': raw['Sequence'] == unit['sequence'],
            'publisher_code_matches_record_id': 'parsig:' + str(raw['Code']) == row['record_id'],
            'record_direction_and_id': rid == row['record_id'] + ':pal>fa' and row['source_language'] == 'pal' and row['target_language'] == 'fa',
            'excluded_work_absent': int(unit['book_id']) not in protected,
            'ledger_retained_identity': old['source_text'] == row['text'] and old['target_text'] == row['target'],
        }
        flags = ['mapping:' + k for k, good in checks.items() if not good]
        profiles = {}
        for field in ('text', 'target'):
            text = row[field]
            characters[field] += len(text)
            letters = [c for c in text if c.isalpha()]
            fa = sum('ARABIC' in ud.name(c, '') for c in letters)
            invisibles = sorted({f'U+{ord(c):04X}' for c in text if ud.category(c) in {'Cc', 'Cf'} and c not in '\n\r\t\u200c'})
            if invisibles:
                flags.append(field + ':invisible:' + ','.join(invisibles))
            if '\ufffd' in text or any(ud.category(c) == 'Cs' for c in text):
                flags.append(field + ':replacement_or_surrogate')
            if re.search(r'<(?:/?[A-Za-z][^>]*|/?\w+\s[^>]*)>', text):
                flags.append(field + ':possible_markup')
            if re.search('[\u200c\u200d]{2,}', text):
                flags.append(field + ':repeated_join_controls')
            profiles[field] = {'characters': len(text), 'whitespace_tokens': len(text.split()),
                               'letters': len(letters), 'arabic_script_letters': fa,
                               'sha256': digest(text.encode()), 'invisible_codepoints': invisibles}
        if profiles['target']['letters'] and profiles['target']['arabic_script_letters'] / profiles['target']['letters'] < .80:
            flags.append('target:non_persian_script_risk')
        if not row['text'].strip() or not row['target'].strip():
            flags.append('empty_source_or_target')
        tokens = re.findall(r'[^\W\d_]+', ud.normalize('NFC', row['text'].casefold()))
        digits_source = re.findall(r'\d+', row['text'])
        digits_target = [''.join(str(ud.digit(c)) for c in token) for token in re.findall(r'\d+', row['target'])]
        missing_digits = [n for n in digits_source if n not in digits_target and not any(str(v) == n and fa in row['target'] for v, fa in NUMBERS.values())]
        missing_words = [t for t in sorted(set(tokens) & set(NUMBERS)) if NUMBERS[t][1] not in row['target'] and str(NUMBERS[t][0]) not in digits_target]
        if missing_digits or missing_words:
            flags.append('numbers:possible_unrepresented_source_quantity')
        neg = [t for t in tokens if t in {'nē', 'ma'}]
        if neg and not PERSIAN_NEG.search(row['target']):
            flags.append('negation:source_negative_without_simple_target_marker')
        kin = [t for t in tokens if t in {'pid', 'pidar', 'mād', 'mādar', 'brād', 'pus', 'pusar', 'duxt'}]
        if kin and not re.search('پدر|مادر|برادر|پسر|دختر|فرزند|زاد|باب', row['target']):
            flags.append('roles:kinship_lexeme_without_simple_target_marker')
        if profiles['text']['whitespace_tokens'] >= 20 and profiles['target']['whitespace_tokens'] / profiles['text']['whitespace_tokens'] < .45:
            flags.append('scope:target_short_relative_to_source')
        if profiles['target']['whitespace_tokens'] >= 30 and profiles['target']['whitespace_tokens'] / max(1, profiles['text']['whitespace_tokens']) > 4:
            flags.append('scope:target_long_relative_to_source')
        source_groups[normalized(row['text'])].append(rid)
        target_groups[normalized(row['target'])].append(rid)
        result.append({'id': rid, 'canonical_line': line, 'work_id': row['work_id'], 'book_title': unit['book_title'],
                       'source_scope': 'publisher paragraph; not certified sentence alignment',
                       'raw_file': pointer['file'], 'raw_json_pointer': '/' + str(raw_index),
                       'raw_endpoint': endpoint, 'raw_sequence': raw['Sequence'], 'raw_code': raw['Code'],
                       'export_line': export_line, 'checks': checks, 'profiles': profiles, 'flags': flags,
                       'scope_cues_not_error_labels': {'source_at_most_three_whitespace_tokens': len(row['text'].split()) <= 3,
                                                      'source_ends_comma_colon_semicolon': row['text'].rstrip().endswith((',', ':', ';')),
                                                      'source_starts_connective': bool(re.match(r'^(ud|u-\S+|kū|čē)\b', row['text'])),
                                                      'source_contains_editorial_or_gap_marker': any(x in row['text'] for x in ('[', ']', '<', '>', '*', '...'))},
                       'source_number_tokens': [t for t in tokens if t in NUMBERS],
                       'source_digits': digits_source, 'target_digits': digits_target,
                       'unmatched_number_candidates': missing_digits + missing_words,
                       'source_negation_tokens': neg, 'source_kinship_tokens': kin,
                       'actual_mixed_train_occurrences': exposed[rid],
                       'semantic_status': 'NOT_INDIVIDUALLY_LINGUISTICALLY_READ_IN_THIS_AUDIT'})
    lookup = {r['id']: r for r in historic}
    groups = []
    for ids in source_groups.values():
        if len(ids) > 1:
            groups.append({'kind': 'same_normalized_source', 'ids': ids,
                           'distinct_normalized_targets': len({normalized(lookup[i]['target']) for i in ids})})
    for ids in target_groups.values():
        if len(ids) > 1 and len({normalized(lookup[i]['text']) for i in ids}) > 1:
            groups.append({'kind': 'same_normalized_target_different_sources', 'ids': ids})
    reviewed = {a['id']: a for a in adjudications}
    for record in result:
        if record['id'] in reviewed:
            judgment = reviewed[record['id']]
            assert judgment['source_sha256'] == record['profiles']['text']['sha256']
            assert judgment['target_sha256'] == record['profiles']['target']['sha256']
            record['semantic_status'] = 'TARGETED_AI_FLAG_REVIEW_NOT_FULL_PHILOLOGICAL_CERTIFICATION'
    old_ids = set(ledger)
    admitted = {r['id'] for r in historic}
    payload = {'schema_version': 1, 'generated_utc': datetime.now(timezone.utc).isoformat(),
               'scope': 'All 2237 historical pairs; exhaustive raw alignment and string screening, targeted AI adjudication only',
               'script_sha256': digest(Path(__file__).read_bytes()),
               'inputs': {str(p.relative_to(ROOT)): {'sha256': digest(p.read_bytes()), 'bytes': p.stat().st_size} for p in (HIST, LEDGER, EXPORT, TRAIN, ARCHIVE / 'manifest.json')},
               'coverage': {'rows': len(result), 'unique_ids': len(admitted), 'characters_scanned': dict(characters),
                            'raw_endpoint_files': len(raw_inputs), 'works': len({r['work_id'] for r in result}),
                            'mapping_failed_rows': sum(not all(r['checks'].values()) for r in result),
                            'flagged_rows': sum(bool(r['flags']) for r in result),
                            'mechanical_reviewed_ids': len(result), 'targeted_pair_review_ids': len(reviewed),
                            'flagged_ids_without_adjudication': [r['id'] for r in result if r['flags'] and r['id'] not in reviewed],
                            'all_rows_linguistically_read': False},
               'excluded_ledger_ids': sorted(old_ids - admitted), 'protected_work_ids': sorted(protected),
               'administrative_ledger_membership_matches': admitted == {i for i, r in ledger.items() if r['disposition'] in {'ELIGIBLE', 'ELIGIBLE_WITH_QUALIFICATIONS'}},
               'flags_by_kind': dict(Counter(f for r in result for f in r['flags'])),
               'scope_cue_counts_not_error_counts': dict(Counter(k for r in result for k, v in r['scope_cues_not_error_labels'].items() if v)),
               'raw_inputs': raw_inputs, 'duplicate_groups': groups, 'records': result,
               'adjudications': adjudications,
               'limitations': ['Old ELIGIBLE labels are not semantic evidence.', 'Unicode/script, quantity, negation, kinship and length rules are triage, not translation judges.', 'No sentence-level realignment or source correction was performed.', 'No new model training, inference, download, network or cloud action.']}
    assert len(result) == len(admitted) == 2237
    assert len(old_ids - admitted) == 247
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'coverage': payload['coverage'], 'flags': payload['flags_by_kind'], 'duplicate_groups': len(groups)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
