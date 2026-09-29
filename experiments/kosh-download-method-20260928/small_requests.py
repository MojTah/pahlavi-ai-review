"""One sequential 100-entry request per missing Kosh collection; never retry failures."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from collect_public_texts import Archive, canonical, write_json

COLLECTIONS = 'acpv1_7 afnan awn cpd cpd_de da dd1 dk5 dk6 dk7 dk8 dmx gbd gpv hkr hn lfv mmp mpcd_term_tech mz nmp pahlrivdd ps pyv raf sgw sns wdpw wmiar wz yz'.split()
BASE = ROOT / 'sources/local/public-texts-2026-09-20'


def inspect(raw, cap, strict_xml=True):
    entries = json.loads(raw)['data']['entries']
    if not isinstance(entries, list) or len(entries) > cap:
        raise ValueError('Invalid or over-cap entry list')
    ids = [entry['id'] for entry in entries]
    if any(not isinstance(i, str) or not i for i in ids) or len(ids) != len(set(ids)):
        raise ValueError('Missing or duplicate IDs')
    xml_errors = []
    for entry in entries:
        if entry.get('xml'):
            try:
                ET.fromstring(entry['xml'])
            except ET.ParseError as exc:
                if strict_xml:
                    raise
                xml_errors.append({'id': entry['id'], 'error': str(exc)})
    result = {'entries': len(entries), 'unique_ids': len(ids),
            'with_xml': sum(bool(e.get('xml')) for e in entries),
            'fields': sorted({k for e in entries for k in e}),
            'status': 'CAPPED' if len(entries) == cap else 'BELOW_CAP_UNVERIFIED' if entries else 'EMPTY_UNCONFIRMED'}
    if not strict_xml:
        result['xml_errors_for_quarantine'] = xml_errors
    return result


def previous():
    results = {}
    for folder, filename in [('kosh-all-dictionaries-20260928', 'acquisition-report.json'),
                              ('kosh-size100-check-20260928', 'check.json')]:
        data = json.loads((BASE / folder / filename).read_text('utf-8'))
        items = data.get('collections', [dict(data, collection='cpd')])
        for item in items:
            receipt = item['receipt']
            if receipt['status'] != 'ok':
                continue
            path = (BASE / folder / receipt['file']).resolve()
            if not path.is_relative_to((BASE / folder).resolve()):
                raise ValueError('Archive path escaped its source')
            raw = path.read_bytes()
            if len(raw) != receipt['bytes'] or hashlib.sha256(raw).hexdigest() != receipt['sha256']:
                raise ValueError('Previous capture identity mismatch')
            cap = int(urllib.parse.parse_qs(urllib.parse.urlsplit(receipt['url']).query)['size'][0])
            results[item['collection']] = {'archive': folder, 'receipt': receipt, **inspect(raw, cap)}
    return results


def run(limit, size=100):
    archive = Archive('kosh-small-requests-20260928' if size == 100 else 'kosh-size1000-20260928', limit=limit)
    candidates = COLLECTIONS
    if size == 1000:
        intake_path = Path(__file__).with_name('intake-snapshot-5992.json')
        intake_raw = intake_path.read_bytes()
        if hashlib.sha256(intake_raw).hexdigest() != '923a3c045ca8e1cbeaf96d64afdcab69874a990fce7343553038e480c41607f2':
            raise ValueError('Frozen intake identity mismatch')
        intake = json.loads(intake_raw)
        candidates = [k for k in COLLECTIONS if intake['collections'][k]['status'] == 'CAPPED']
    report = {'scope': 'RAW SEARCH CAPTURES; NOT A COMPLETE EXPORT OR TRAINING DATA',
              'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'collections': previous() if size == 100 else {}, 'stop_reason': None, 'complete_site_export': False}
    report_path = archive.path / 'coverage.json'
    started, last_request = time.monotonic(), time.monotonic()
    for collection in candidates:
        if collection in report['collections']:
            continue
        if archive.requests >= limit:
            report['stop_reason'] = 'Configured new-request limit reached'
            break
        if time.monotonic() - started >= 1200:
            report['stop_reason'] = '20-minute request-admission limit'
            break
        query = urllib.parse.urlencode({'field': 'trc', 'query': '*', 'query_type': 'wildcard', 'size': size})
        url = f'https://kosh.uni-koeln.de/mpcd/{collection}/restful/entries?{query}'
        if canonical(url) not in archive.manifest:
            time.sleep(max(0, 30 - (time.monotonic() - last_request)))
            if time.monotonic() - started >= 1200:
                report['stop_reason'] = '20-minute request-admission limit'
                break
            last_request = time.monotonic()
        raw, receipt = archive.get(url, max_bytes=2_000_000 if size == 100 else 4_000_000)
        item = {'archive': archive.path.name, 'receipt': receipt}
        if raw is None:
            item['status'] = 'FETCH_FAILED'
            report['stop_reason'] = receipt.get('error', 'Request failed')
        else:
            try:
                item.update(inspect(raw, size, strict_xml=size == 100))
            except (ValueError, KeyError, TypeError, ET.ParseError) as exc:
                item.update(status='SCHEMA_ERROR', error=str(exc))
                report['stop_reason'] = 'Raw response saved; schema requires review'
        report['collections'][collection] = item
        write_json(report_path, report)
        print(json.dumps({'collection': collection, **{k: v for k, v in item.items() if k not in ('archive', 'receipt')},
                          'stop_reason': report['stop_reason']}), flush=True)
        if report['stop_reason']:
            break
    write_json(report_path, report)
    print(json.dumps({'nonempty_collections': sum(x.get('entries', 0) > 0 for x in report['collections'].values()),
                      'empty_unconfirmed': [k for k, v in report['collections'].items() if v['status'] == 'EMPTY_UNCONFIRMED'],
                      'raw_entries': sum(x.get('entries', 0) for x in report['collections'].values()),
                      'stop_reason': report['stop_reason'], 'complete_site_export': False}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-check', action='store_true')
    parser.add_argument('--max-new-requests', type=int, choices=range(1, 28), default=27)
    parser.add_argument('--size', type=int, choices=[100, 1000], default=100)
    args = parser.parse_args()
    if args.self_check:
        assert len(COLLECTIONS) == len(set(COLLECTIONS)) == 31
        sample = b'{"data":{"entries":[{"id":"a","xml":"<entry/>","extra":["x", "y"]}]}}'
        assert inspect(sample, 1)['fields'] == ['extra', 'id', 'xml']
        assert inspect(sample, 1)['status'] == 'CAPPED'
        assert inspect(sample, 2)['status'] == 'BELOW_CAP_UNVERIFIED'
        assert inspect(b'{"data":{"entries":[]}}', 100)['status'] == 'EMPTY_UNCONFIRMED'
        malformed = b'{"data":{"entries":[{"id":"a","xml":"<broken>"}]}}'
        assert inspect(malformed, 1000, strict_xml=False)['xml_errors_for_quarantine'][0]['id'] == 'a'
        for raw in (b'{"data":{"entries":[{"id":"a"},{"id":"a"}]}}',
                    b'{"data":{"entries":[{"id":""}]}}',
                    b'{"data":{"entries":[{"id":"a","xml":"<broken>"}]}}'):
            try:
                inspect(raw, 100)
            except (ValueError, ET.ParseError):
                pass
            else:
                raise AssertionError('Invalid payload accepted')
        assert len(previous()) == 4
        print('PASS: catalogue, payload validation, extra fields, cap flags and four previous archive hashes')
    else:
        run(args.max_new_requests, args.size)
