"""Offline all-record ambiguity/character/exposure audit; no corpus mutation."""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DATA = ROOT / 'resources/local/mixed-supervision-20260929/data'


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def leaves(value, path=''):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, list):
        for i, item in enumerate(value):
            yield from leaves(item, f'{path}[{i}]')
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from leaves(item, f'{path}.{key}' if path else key)


def ambiguous_groups(records):
    groups = defaultdict(list)
    for record in records:
        groups[record['prefix_token_sha256']].append(record)
    return [rows for rows in groups.values() if len({r['answer_token_sha256'] for r in rows}) > 1]


def main():
    from tokenizers import Tokenizer
    paths = {name: DATA / name for name in ('pool.jsonl', 'train.jsonl', 'learning-projections.jsonl', 'duplicates.jsonl')}
    rows = {name: [json.loads(s) for s in path.read_text('utf-8').splitlines()] for name, path in paths.items()}
    pool = {r['id']: r for r in rows['pool.jsonl']}
    selected = {r['id']: i + 1 for i, r in enumerate(rows['train.jsonl'])}
    duplicates = {r['id']: r['canonical_id'] for r in rows['duplicates.jsonl']}
    tokenizer_path = ROOT / 'resources/local/cloud-pilot-qualified-20260927/tokenizer/tokenizer.json'
    tokenizer = Tokenizer.from_file(str(tokenizer_path))
    unknown = tokenizer.token_to_id('<unk>')
    ledger, totals, task_counts = [], Counter(), defaultdict(Counter)
    for projection in rows['learning-projections.jsonl']:
        identifier, task, learning = (projection[k] for k in ('id', 'task', 'learning'))
        count, chars, units, nfc, controls, repeated_format = 0, 0, 0, [], [], []
        for field, text in leaves(learning):
            count += 1
            chars += len(text)
            units += len(text.split())
            if text != unicodedata.normalize('NFC', text):
                nfc.append(field)
            bad = Counter(f'U+{ord(c):04X}' for c in text
                          if (unicodedata.category(c) in ('Cc', 'Cf', 'Cs') and c not in '\n\r\t\u200c') or c == '\ufffd')
            if bad:
                controls.append({'field': field, 'codepoints': dict(bad)})
            if re.search(r'[\u200c\u200d]{2,}', text):
                repeated_format.append(field)
        totals.update(records=1, string_fields=count, unicode_codepoints=chars, whitespace_units=units)
        entry = {'id': identifier, 'task': task, 'string_fields_screened': count,
                 'unicode_codepoints_screened': chars, 'whitespace_units_screened': units,
                 'non_nfc_fields': nfc, 'control_character_flags': controls,
                 'repeated_joiner_fields': repeated_format,
                 'selected_position': selected.get(identifier),
                 'evidence_level': 'MECHANICAL_SCREEN_ONLY_NOT_SEMANTIC_APPROVAL'}
        task_counts[task].update(released=1, selected=int(identifier in selected),
                                unicode_flags=bool(controls), non_nfc=bool(nfc), repeated_joiners=bool(repeated_format))
        if identifier in duplicates:
            entry['duplicate_of'] = duplicates[identifier]
            ledger.append(entry)
            continue
        row = pool[identifier]
        boundary = row['prompt_tokens']
        prefix, answer = row['input_ids'][:boundary], row['input_ids'][boundary:]
        assert row['labels'] == [-100] * boundary + answer, identifier
        expected = canonical(learning['target']) if task == 'lexical-en' else learning['target']
        if task == 'historical-control-fa':
            expected = expected.strip()
        assert tokenizer.decode(answer, skip_special_tokens=False) == expected + '<turn|>\n', identifier
        entry.update(prefix_token_sha256=digest(canonical(prefix)), answer_token_sha256=digest(canonical(answer)),
                     source_sha256=digest(canonical(learning['source'])),
                     context_sha256=digest(canonical(learning['context'])),
                     target_sha256=digest(expected), prefix_tokens=len(prefix), answer_tokens=len(answer),
                     unknown_token_count=row['input_ids'].count(unknown) if unknown is not None else 0)
        context_texts = [text for _, text in leaves(learning['context'])]
        entry['exact_target_in_context'] = len(expected) >= 5 and any(expected in text for text in context_texts)
        task_counts[task].update(pool=1, answer_tokens=len(answer), prefix_tokens=len(prefix),
                                unknown_tokens=entry['unknown_token_count'],
                                target_in_context=entry['exact_target_in_context'])
        if identifier in selected:
            task_counts[task].update(selected_answer_tokens=len(answer), selected_prefix_tokens=len(prefix))
        ledger.append(entry)
    prepared = [r for r in ledger if 'prefix_token_sha256' in r]
    assert len(ledger) == 10152 and len(prepared) == 10151 and len(selected) == 1536
    conflicts = []
    for group in ambiguous_groups(prepared):
        # Confirm exact arrays too, rather than relying solely on equal digests.
        prefixes = [pool[r['id']]['input_ids'][:pool[r['id']]['prompt_tokens']] for r in group]
        assert all(prefix == prefixes[0] for prefix in prefixes)
        selected_group = [r for r in group if r['selected_position'] is not None]
        conflicts.append({'task': group[0]['task'], 'ids': [r['id'] for r in group],
                          'prefix_token_sha256': group[0]['prefix_token_sha256'],
                          'distinct_targets': len({r['answer_token_sha256'] for r in group}),
                          'selected_ids': [r['id'] for r in selected_group],
                          'selected_distinct_targets': len({r['answer_token_sha256'] for r in selected_group}),
                          'interpretation': 'IDENTICAL_MODEL_INPUT_DIFFERENT_EXPECTED_OUTPUT_REQUIRES_SOURCE_ADJUDICATION'})
    # Small negative/positive control: a homograph with different context is not this finding.
    assert len(ambiguous_groups([{'prefix_token_sha256': 'p', 'answer_token_sha256': 'a'},
                                {'prefix_token_sha256': 'p', 'answer_token_sha256': 'b'}])) == 1
    assert not ambiguous_groups([{'prefix_token_sha256': 'p', 'answer_token_sha256': 'a'},
                                 {'prefix_token_sha256': 'q', 'answer_token_sha256': 'b'}])
    assert not re.search(r'[\u200c\u200d]{2,}', 'می\u200cرود')
    assert re.search(r'[\u200c\u200d]{2,}', 'می\u200c\u200cرود')
    result = {'scope': 'Every released learning string and every prepared token prefix/answer; mechanical evidence only',
              'status': 'REVIEW_REQUIRED' if conflicts else 'NO_EXACT_PROMPT_AMBIGUITY_DETECTED',
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'input_sha256': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in [*paths.values(), tokenizer_path]},
              'coverage': dict(totals), 'task_counts': {k: dict(v) for k, v in task_counts.items()},
              'exact_prompt_ambiguity': {'groups': len(conflicts), 'rows': sum(len(g['ids']) for g in conflicts),
                  'groups_by_task': dict(Counter(g['task'] for g in conflicts)),
                  'selected_rows': sum(len(g['selected_ids']) for g in conflicts),
                  'groups_with_multiple_selected_targets': sum(g['selected_distinct_targets'] > 1 for g in conflicts),
                  'details': conflicts},
              'rows': ledger,
              'limits': ['Different answers may be legitimate alternatives; lexical/philological adjudication is separate.',
                         'This census cannot certify every word meaning or eliminate every possible runtime failure.',
                         'Whitespace units are not a linguistic word count. Unicode flags are not automatically errors.',
                         'No canonical data, model, cloud job, benchmark or training configuration changed.']}
    (HERE / 'cross-record-audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': result['status'], 'coverage': result['coverage'],
                      'ambiguity': {k: v for k, v in result['exact_prompt_ambiguity'].items() if k != 'details'},
                      'task_counts': result['task_counts']}))


if __name__ == '__main__':
    main()
