"""Archive and extract the public Cologne legacy CPD; never query Kosh."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from collect_public_texts import Archive, write_json

REVISION = '60bb06c897c4a7bec45a5f45d26695e745044b42'
BASE = f'https://raw.githubusercontent.com/sanskrit-lexicon/csl-santam/{REVISION}/'


def extract(raw):
    selected = []
    rows = raw.splitlines(keepends=True)
    for number, row in enumerate(rows, 1):
        fields = row.removesuffix(b'\n').removesuffix(b'\r').split(b'\t')
        if len(fields) != 3 or fields[0] not in (b'1', b'2', b'3', b'4'):
            raise ValueError(f'Unexpected source row {number}')
        if fields[0] == b'4':
            selected.append((number, row, fields))
    return len(rows), selected


def run():
    archive = Archive('cologne-legacy-cpd-20260928', limit=3)
    receipts = {}
    for path in ('LICENSE.md', 'dat/books', 'sqlite/ganz.txt'):
        raw, receipt = archive.get(BASE + path, max_bytes=27_000_000)
        receipts[path] = receipt
        if raw is None:
            write_json(archive.path / 'extraction.json', {'status': 'FETCH_FAILED', 'receipts': receipts})
            raise RuntimeError('Download failed; no automatic retry: ' + path)
    count, selected = extract(raw)
    if len(selected) != 4218:
        raise ValueError(f'Expected the published 4218 legacy CPD rows, got {len(selected)}')
    target = archive.path / 'cpd-original.tsv'
    target.write_bytes(b''.join(row for _, row, _ in selected))
    # Keep original bytes authoritative. No spelling, sense, or encoding repairs.
    records = [{'source_line': n, 'dictionary_id': int(f[0]),
                'headword': f[1].decode('cp1252'), 'entry': f[2].decode('cp1252')}
               for n, _, f in selected]
    readable = archive.path / 'cpd.jsonl'
    readable.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in records), encoding='utf-8')
    assert len(readable.read_text('utf-8').splitlines()) == len(selected)
    summary = {'status': 'EXTRACTED_LEGACY_SOURCE_ONLY', 'revision': REVISION,
               'receipts': receipts, 'source_rows': count, 'cpd_rows': len(selected),
               'unique_headwords': len({r['headword'] for r in records}),
               'all_source_fields': ['dictionary_id', 'headword', 'entry'],
               'outputs': [{'file': p.name, 'bytes': p.stat().st_size,
                            'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                           for p in (target, readable)],
               'rights': 'Repository declares data CC BY-NC-SA 3.0',
               'limits': 'Legacy Cologne data; equivalence to current MPCD/Kosh or print edition unverified; no training admission'}
    write_json(archive.path / 'extraction.json', summary)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-check', action='store_true')
    args = parser.parse_args()
    if args.self_check:
        total, selected = extract(b'1\tx\ty\r\n4\ta\tb\r\n4\ta\tc\r\n')
        assert total == 3 and [n for n, _, _ in selected] == [2, 3]
        assert [f[2] for _, _, f in selected] == [b'b', b'c']
        for original in (b'4\ta\tb\n', b'4\ta\tb\r\n', b'4\ta\tb'):
            _, sample = extract(original)
            assert sample[0][1] == original and sample[0][2] == [b'4', b'a', b'b']
        for invalid in (b'4\ta\r\n', b'4\ta\tb\textra\r\n', b'9\ta\tb\r\n'):
            try:
                extract(invalid)
            except ValueError:
                pass
            else:
                raise AssertionError('Invalid source accepted')
        print('PASS: extraction preserves duplicate headwords, source lines and fields; rejects malformed rows')
    else:
        run()
