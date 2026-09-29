"""Bounded archive of 31 observed Kosh collections; no training mutation."""
import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from collect_public_texts import Archive, write_json

COLLECTIONS = 'acpv1_7 afnan awn cpd cpd_de da dd1 dk5 dk6 dk7 dk8 dmx gbd gpv hkr hn lfv mmp mpcd_term_tech mz nmp pahlrivdd ps pyv raf sgw sns wdpw wmiar wz yz'.split()
CAP = 10000


def entries_from(raw):
    entries = json.loads(raw)['data']['entries']
    if not isinstance(entries, list) or len(entries) > CAP or any(not isinstance(e, dict) for e in entries):
        raise ValueError('Unexpected entries schema')
    ids = [e.get('id') for e in entries]
    if any(not isinstance(i, str) or not i for i in ids) or len(ids) != len(set(ids)):
        raise ValueError('Missing or duplicate entry IDs')
    return entries


def run():
    archive = Archive('kosh-all-dictionaries-20260928', limit=len(COLLECTIONS))
    report = {'scope': 'Raw source archive, NOT training data', 'requested_cap_per_collection': CAP,
              'collections': [], 'stop_reason': None}
    started, total_bytes, failures = time.monotonic(), 0, 0
    for name in COLLECTIONS:
        if time.monotonic() - started >= 600 or total_bytes >= 100_000_000:
            report['stop_reason'] = 'Time or cumulative byte admission limit'; break
        url = f'https://kosh.uni-koeln.de/mpcd/{name}/restful/entries?field=trc&query=*&query_type=wildcard&size={CAP}'
        raw, receipt = archive.get(url, max_bytes=10_000_000)
        item = {'collection': name, 'receipt': receipt}
        if raw is not None:
            total_bytes += len(raw)
            try:
                entries = entries_from(raw)
                item.update(entries=len(entries), unique_ids=len(entries),
                            with_xml=sum(bool(e.get('xml')) for e in entries),
                            status='AT_CAP' if len(entries) == CAP else 'BELOW_CAP_NOT_COMPLETENESS_PROOF' if entries else 'EMPTY_UNCONFIRMED')
                failures = 0 if entries else failures + 1
            except (ValueError, KeyError, TypeError) as exc:
                item.update(status='SCHEMA_ERROR', error=str(exc)); failures += 1
        else:
            item['status'] = 'FETCH_FAILED'; failures += 1
        report['collections'].append(item)
        error = receipt.get('error', '')
        if any(code in error for code in ('HTTP Error 401', 'HTTP Error 403', 'HTTP Error 429')):
            report['stop_reason'] = 'Access or rate-limit response; no automatic retry'
        elif failures >= 3:
            report['stop_reason'] = 'Three consecutive failed/empty collections'
        report['download_bytes'] = total_bytes
        write_json(archive.path / 'acquisition-report.json', report)
        print(json.dumps({k: v for k, v in item.items() if k != 'receipt'}), flush=True)
        if report['stop_reason']: break
    write_json(archive.path / 'acquisition-report.json', report)
    print(json.dumps({'collections_processed': len(report['collections']), 'bytes': total_bytes,
                      'stop_reason': report['stop_reason']}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-check', action='store_true')
    args = parser.parse_args()
    if args.self_check:
        assert len(COLLECTIONS) == len(set(COLLECTIONS)) == 31
        assert entries_from(b'{"data":{"entries":[{"id":"a","xml":"<entry/>"}]}}')[0]['id'] == 'a'
        for raw in (b'{"data":{"entries":[{},{}]}}', b'{"data":{"entries":[{"id":"a"},{"id":"a"}]}}', b'{"data":{"entries":{}}}'):
            try: entries_from(raw)
            except ValueError: pass
            else: raise AssertionError('Invalid record set accepted')
        try: entries_from(json.dumps({'data': {'entries': [{'id': str(i)} for i in range(CAP + 1)]}}))
        except ValueError: pass
        else: raise AssertionError('Over-cap response accepted')
        print('PASS: collection scope, schema and identity checks')
    else:
        run()
