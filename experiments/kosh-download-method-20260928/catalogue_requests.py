"""Download incomplete collections to their published catalogue counts, sequentially."""
import argparse
import hashlib
import json
from pathlib import Path
import time
import urllib.parse

from small_requests import Archive, BASE, COLLECTIONS, canonical, inspect, write_json

WORK = Path(__file__).resolve().parent


def verified(item):
    receipt = item['receipt']
    folder = BASE / item['archive']
    path = (folder / receipt['file']).resolve()
    if not path.is_relative_to(folder.resolve()):
        raise ValueError('Raw path escaped archive')
    raw = path.read_bytes()
    if len(raw) != receipt['bytes'] or hashlib.sha256(raw).hexdigest() != receipt['sha256']:
        raise ValueError('Raw identity mismatch')
    return raw


def inputs():
    raw = (WORK / 'intake-snapshot-10497.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != '5b35021cb0471e5d2324e2278b6b3e8a4728675c1f51242ad7a496fadf28f869':
        raise ValueError('Frozen intake identity mismatch')
    baseline = json.loads(raw)
    catalogue = json.loads(verified(baseline['catalogue']))['dicts']
    if set(catalogue) != set(COLLECTIONS):
        raise ValueError('Catalogue identity changed')
    for name, item in baseline['collections'].items():
        verified(item)
        if not isinstance(catalogue[name]['size'], int) or not 0 <= catalogue[name]['size'] < 10000:
            raise ValueError('Unexpected catalogue size')
    gap = json.loads((WORK / 'awn-gap-retry-result.json').read_text('utf-8'))
    rows = json.loads(verified(gap))['data']['ids']
    assert len(rows) == 1 and rows[0]['id'] == '190'
    old_awn = json.loads(verified(baseline['collections']['awn']))['data']['entries']
    assert '190' not in {r['id'] for r in old_awn}
    assert len(old_awn) + 1 == catalogue['awn']['size']
    candidates = [name for name in COLLECTIONS if name != 'awn'
                  and baseline['collections'][name]['entries'] < catalogue[name]['size']]
    return baseline, catalogue, gap, candidates


def run(limit):
    baseline, catalogue, gap, candidates = inputs()
    archive = Archive('kosh-catalogue-sized-20260928', limit=limit)
    report = {'scope': 'RAW DOWNLOADS; NOT TRAINING ADMITTED',
              'baseline_snapshot': 'intake-snapshot-10497.json',
              'catalogue': baseline['catalogue'], 'awn_gap': gap,
              'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'collections': {}, 'stop_reason': None}
    started = last_request = time.monotonic()
    for name in candidates:
        if archive.requests >= limit or time.monotonic() - started >= 1200:
            report['stop_reason'] = 'Request or 20-minute admission limit reached'
            break
        expected = catalogue[name]['size']
        query = urllib.parse.urlencode({'field': 'trc', 'query': '*', 'query_type': 'wildcard', 'size': expected + 1})
        url = f'https://kosh.uni-koeln.de/mpcd/{name}/restful/entries?{query}'
        if canonical(url) not in archive.manifest:
            time.sleep(max(0, 30 - (time.monotonic() - last_request)))
            if time.monotonic() - started >= 1200:
                report['stop_reason'] = '20-minute admission limit reached'
                break
            last_request = time.monotonic()
        raw, receipt = archive.get(url, max_bytes=16_000_000)
        item = {'archive': archive.path.name, 'receipt': receipt, 'catalogue_entries': expected}
        if raw is None:
            item['status'] = 'FETCH_FAILED'
            report['stop_reason'] = receipt.get('error', 'Request failed')
        else:
            try:
                item.update(inspect(raw, expected + 1, strict_xml=False))
                old = {e['id']: e for e in json.loads(verified(baseline['collections'][name]))['data']['entries']}
                new = {e['id']: e for e in json.loads(raw)['data']['entries']}
                item['missing_baseline_ids'] = sorted(set(old) - set(new))
                item['changed_baseline_ids'] = sorted(k for k in old.keys() & new.keys() if old[k] != new[k])
                item['matches_catalogue_count'] = len(new) == expected
                if item['missing_baseline_ids'] or item['changed_baseline_ids']:
                    report['stop_reason'] = 'Capture overlap changed; inspect retained raw versions'
            except (ValueError, KeyError, TypeError) as exc:
                item.update(status='SCHEMA_ERROR', error=str(exc))
                report['stop_reason'] = 'Raw response saved; schema requires review'
        report['collections'][name] = item
        write_json(archive.path / 'coverage.json', report)
        print(json.dumps({'collection': name, 'entries': item.get('entries'), 'catalogue_entries': expected,
                          'xml_errors': len(item.get('xml_errors_for_quarantine', [])),
                          'stop_reason': report['stop_reason']}), flush=True)
        if report['stop_reason']:
            break
    write_json(archive.path / 'coverage.json', report)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-check', action='store_true')
    parser.add_argument('--max-new-requests', type=int, choices=range(1, 22), default=21)
    args = parser.parse_args()
    if args.self_check:
        baseline, catalogue, gap, candidates = inputs()
        assert len(candidates) == 21 and 'cpd' in candidates and 'awn' not in candidates
        assert sum(d['size'] for d in catalogue.values()) == 38686
        item = baseline['collections']['cpd']
        try:
            verified({**item, 'receipt': {**item['receipt'], 'sha256': '0' * 64}})
        except ValueError:
            pass
        else:
            raise AssertionError('Hash mismatch accepted')
        print('PASS: frozen inputs, all archive hashes, count-based queue, recovered AWN ID and mismatch rejection')
    else:
        run(args.max_new_requests)
