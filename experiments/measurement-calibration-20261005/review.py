"""One local post-hoc common assessment; archived primary evidence stays immutable."""
import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts import prepare_blind_dev_assisted as prep
from scripts.score_blind_dev_assisted import validate_reviews

HERE = Path(__file__).parent
OUT = ROOT / 'resources/local/measurement-calibration-20261005/packets'
IDS = tuple('QUALITYDEV1-' + n for n in ('002','003','005','006','007','008','009','010','012','013','014','015','017','020','021'))
SPEC = (
    ('dictionary', 'dictionary-ab-results-20261005/d68800b3b35c44a4a97adc0c5129a3de', 'dictionary-ab-runtime-20261003'),
    ('faithfulness', 'dictionary-faithfulness-results-20261005/6b54f5bc4e984dbe9a4b53e89e4bf5d8', 'dictionary-faithfulness-20261005'),
)
ARMS = ('dictionary:A', 'dictionary:B', 'faithfulness:A', 'faithfulness:B')
REF_KEYS = ('translations','edition','notes','reference_screen','expert_adjudicated')


def read(path):
    return json.loads(Path(path).read_bytes())


def rows(path):
    return prep.decode_lines(Path(path).read_bytes())


def digest(value):
    return prep.sha(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8'))


def group_key(case_id, item):
    return digest({'case_id': case_id, 'item': item})


def validate_members(members, groups):
    expected = {(arm, cid) for arm in ARMS for cid in IDS}
    prep.require(len(members) == 60 and {(m['arm'], m['case_id']) for m in members} == expected, 'Four-arm fixed coverage differs')
    prep.require(len(groups) == 42 and {m['group'] for m in members} == set(groups), 'Closed unique-context inventory differs')
    by = {(m['arm'], m['case_id']): m for m in members}
    for m in members:
        prep.require(m['group'] == group_key(m['case_id'], groups[m['group']]), 'Case/context grouping differs')
    for cid in IDS:
        prep.require(by['dictionary:B', cid]['group'] == by['faithfulness:A', cid]['group'], 'Repeated control differs')


def collect():
    contract_raw = prep.CONTRACT.read_bytes()
    prep.require(prep.sha(contract_raw) == prep.CONTRACT_SHA, 'Original merit contract changed')
    contract = json.loads(contract_raw)
    pins = {prep.CONTRACT.relative_to(ROOT).as_posix(): prep.sha(contract_raw)}
    for name, expected in contract['source_files_sha256'].items():
        prep.require(prep.sha((ROOT/name).read_bytes()) == expected, 'Frozen source changed: ' + name)
        pins[name] = expected
    refs = prep.unique(rows(prep.DEV/'references.jsonl'))
    assessments = prep.unique(read(prep.DEV/'assessment-contract.json')['cases'])
    prep.require(set(IDS) == {cid for cid, a in assessments.items() if a['assessment'] == 'provisional_whole_translation'}, 'Exposed case inventory changed')
    groups, members = {}, []
    for study, local, experiment in SPEC:
        base = ROOT/'resources/local'/local
        scored = base/'scored'
        provenance = read(scored/'lead-only/provenance.json')
        # Reuse the previously verified closed snapshot; verify every saved byte.
        for name, entry in provenance['files'].items():
            path = scored/name
            raw = path.read_bytes()
            prep.require(len(raw) == entry['bytes'] and prep.sha(raw) == entry['sha256'], 'Archived provenance differs: ' + name)
        tracked = ROOT/'experiments'/experiment/'live-execution/comparison.json'
        prep.require((scored/'comparison.json').read_bytes() == tracked.read_bytes(), 'Archived primary comparison differs')
        primary = read(tracked)
        prep.require(prep.sha((scored/'lead-only/provenance.json').read_bytes()) == primary['packet_provenance_sha256'], 'Primary packet provenance binding differs')
        for path in (tracked, scored/'lead-only/provenance.json', scored/'lead-only/mapping.jsonl', scored/'reviewer-A/packet.jsonl'):
            pins[path.relative_to(ROOT).as_posix()] = prep.sha(path.read_bytes())
        packet = prep.unique(rows(scored/'reviewer-A/packet.jsonl'), 'review_id')
        mapping = [m for m in rows(scored/'lead-only/mapping.jsonl') if m['reviewer'] == 'A']
        prep.require(len(mapping) == len(packet) == 30 and {m['review_id'] for m in mapping} == set(packet), 'Archived mapping coverage differs')
        raw_predictions = prep.unique(rows(base/'final/evaluation/predictions.jsonl'))
        manifest = read(base/'final/manifest.json')
        prediction_bytes = (base/'final/evaluation/predictions.jsonl').read_bytes()
        prep.require(prep.sha(prediction_bytes) == manifest['files']['evaluation/predictions.jsonl']['sha256']
                     and prep.sha((base/'final/manifest.json').read_bytes()) == provenance['manifest_sha256']
                     == primary['recovered_manifest_sha256'], 'Closed original prediction binding differs')
        for path in (base/'final/manifest.json', base/'final/evaluation/predictions.jsonl'):
            pins[path.relative_to(ROOT).as_posix()] = prep.sha(path.read_bytes())
        for m in mapping:
            cid = m['case_id']
            prep.require(cid in IDS and m['arm'] in 'AB', 'Unexpected case or arm')
            item = {k: v for k, v in packet[m['review_id']].items() if k != 'review_id'}
            ref, assessment = refs[cid], assessments[cid]
            prep.require(set(item) == prep.PACKET_FIELDS - {'review_id'} and item['source_text'] == ref['source_text']
                         and item['references'] == {k: ref[k] for k in REF_KEYS}
                         and item['constraint'] == assessment['constraint'] and item['assessment'] == assessment['assessment'], 'Frozen reference/qualification differs')
            output = raw_predictions[m['prediction_id']]
            prep.require(item['output_text'] == output['text'] and item['output_sha256'] == output['output_sha256']
                         == prep.sha(item['output_text'].encode()) and item['execution_status'] == output['status'] == 'success', 'Closed output identity/status differs')
            key = group_key(cid, item)
            prep.require(key not in groups or groups[key] == item, 'Context digest collision')
            groups[key] = item
            members.append(dict(arm=study+':'+m['arm'], case_id=cid, work_id=m['work_id'], group=key,
                                output_sha256=item['output_sha256'], prediction_id=m['prediction_id']))
    validate_members(members, groups)
    prep.require(Counter(assessments[c]['work_id'] for c in IDS) == {'parsig:103':4,'parsig:112':5,'parsig:138':4,'parsig:517':2}, 'Work bindings differ')
    for m in members:
        prep.require(m['work_id'] == assessments[m['case_id']]['work_id'], 'Membership work differs')
    return contract, pins, groups, members


def build():
    contract, pins, groups, members = collect()
    criteria = (HERE/'CRITERIA-v1.md').read_bytes()
    for path in (HERE/'PLAN.md', HERE/'SOURCE-AUDIT.md', HERE/'CRITERIA-v1.md', Path(__file__), Path(prep.__file__), ROOT/'scripts/score_blind_dev_assisted.py'):
        pins[path.relative_to(ROOT).as_posix()] = prep.sha(path.read_bytes())
    prep.require(pins['scripts/score_blind_dev_assisted.py'] == 'b21d70d8e1a92bd7fc1fbb2de73a9eaf7d856aeba0c396c18f9272c5369f1732', 'Original validator changed')
    files = {'lead-only/members.jsonl': prep.lines(members)}
    mapping = []
    for reviewer, seed in (('A',2026100503), ('B',2026100504)):
        rng = random.Random(seed)
        keys = sorted(groups)
        rng.shuffle(keys)
        packet = []
        for key in keys:
            rid = 'r' + format(rng.getrandbits(128), '032x')
            packet.append(dict(review_id=rid, **groups[key]))
            mapping.append(dict(reviewer=reviewer, review_id=rid, group=key))
        prep.require(len(prep.unique(packet, 'review_id')) == 42, 'Opaque identity collision')
        files[f'reviewer-{reviewer}/packet.jsonl'] = prep.lines(packet)
        instructions = prep.instructions().replace(b'all 96 opaque records', b'all 42 opaque records')
        instructions += b'\nApply the separately versioned CRITERIA-v1.md candidate in this folder. This is provisional assessment; do not follow its source links outside this folder. Describe evidence for required relations, defensible alternatives and unresolved recoverability. Do not infer a missing proposition solely from the expected reference.\n'
        files[f'reviewer-{reviewer}/INSTRUCTIONS.md'] = instructions
        files[f'reviewer-{reviewer}/CRITERIA-v1.md'] = criteria
    files['lead-only/mapping.jsonl'] = prep.lines(mapping)
    freeze = dict(status='FROZEN_BEFORE_COMMON_REVIEW', protocol='posthoc-common-dev15-v1', post_hoc=True,
                  candidate_sha256=prep.sha(criteria), original_merit_contract_sha256=prep.CONTRACT_SHA,
                  case_ids=list(IDS), memberships=60, unique_case_output_contexts=42, duplicate_memberships=18,
                  arms=list(ARMS), denominator_per_arm=15, source_pins=pins,
                  screen=contract['comparison']['screen'], seeds={'A':2026100503,'B':2026100504},
                  expert_adjudicated=False, primary_results_replaced=False, independent_confirmation=False,
                  files={name:prep.sha(data) for name,data in files.items()})
    files['freeze.json'] = prep.json_bytes(freeze)
    return files


def check(directory):
    expected = build()
    for name, raw in expected.items():
        prep.require((Path(directory)/name).read_bytes() == raw, 'Frozen assessment artifact differs: ' + name)
    return json.loads(expected['freeze.json'])


def paired(members, lookup, a, b, screen):
    arms = {arm:{m['case_id']:m for m in members if m['arm'] == arm} for arm in (a,b)}
    prep.require(all(set(x) == set(IDS) for x in arms.values()), 'Paired denominator differs')
    before = {c:lookup[arms[a][c]['group']]['judgment'] for c in IDS}
    after = {c:lookup[arms[b][c]['group']]['judgment'] for c in IDS}
    gain = [c for c in IDS if before[c] != 'accepted' and after[c] == 'accepted']
    loss = [c for c in IDS if before[c] == 'accepted' and after[c] != 'accepted']
    works = sorted({arms[a][c]['work_id'] for c in gain})
    critical_change = sum(x == 'critical_error' for x in after.values()) - sum(x == 'critical_error' for x in before.values())
    regressions = [c for c in IDS if before[c] == 'accepted' and after[c] == 'critical_error']
    checks = dict(net_accepted_gain=len(gain)-len(loss) >= screen['both_reviewers_min_net_accepted_gain'],
                  gains_in_multiple_named_works=len(works) >= screen['min_works_with_gains'],
                  no_critical_increase=critical_change <= 0, no_accepted_to_critical=not regressions)
    return dict(denominator=15, accepted_counts=[sum(x == 'accepted' for x in before.values()),sum(x == 'accepted' for x in after.values())],
                critical_counts=[sum(x == 'critical_error' for x in before.values()),sum(x == 'critical_error' for x in after.values())],
                newly_accepted=gain,lost_acceptance=loss,net_accepted_change=len(gain)-len(loss),
                works_with_gains=works,critical_count_change=critical_change,accepted_to_critical=regressions,
                transitions=[dict(case_id=c,work_id=arms[a][c]['work_id'],before=before[c],after=after[c]) for c in IDS],
                screen_checks=checks,screen_pass=all(checks.values()))


def score(directory):
    directory = Path(directory)
    freeze = check(directory)
    members = rows(directory/'lead-only/members.jsonl')
    mapping = rows(directory/'lead-only/mapping.jsonl')
    result = dict(protocol=freeze['protocol'],post_hoc=True,candidate_sha256=freeze['candidate_sha256'],
                  freeze_sha256=prep.sha((directory/'freeze.json').read_bytes()),memberships=60,unique_contexts=42,
                  expert_adjudicated=False,primary_results_replaced=False,independent_confirmation=False,reviewers={})
    all_ratings = {}
    for reviewer in 'AB':
        packet = rows(directory/f'reviewer-{reviewer}/packet.jsonl')
        review_raw = (directory/f'reviewer-{reviewer}/reviews.jsonl').read_bytes()
        ratings = validate_reviews(packet, prep.decode_lines(review_raw), expected_count=42)
        selected = [m for m in mapping if m['reviewer'] == reviewer]
        prep.require(len(selected) == 42 and {m['review_id'] for m in selected} == set(ratings), 'Review mapping differs')
        lookup = {m['group']:ratings[m['review_id']] for m in selected}
        prep.require(len(lookup) == 42, 'Each unique context must have exactly one judgment')
        all_ratings[reviewer] = lookup
        result['reviewers'][reviewer] = dict(review_sha256=prep.sha(review_raw),rows=42,
            counts={arm:dict(Counter(lookup[m['group']]['judgment'] for m in members if m['arm'] == arm)) for arm in ARMS},
            dictionary=paired(members,lookup,'dictionary:A','dictionary:B',freeze['screen']),
            faithfulness=paired(members,lookup,'faithfulness:A','faithfulness:B',freeze['screen']))
    result['disagreements'] = [dict(group=g,reviewer_A=all_ratings['A'][g],reviewer_B=all_ratings['B'][g])
                              for g in all_ratings['A'] if any(all_ratings['A'][g][k] != all_ratings['B'][g][k]
                              for k in ('judgment','categories','supported_span_severity','unknown_span_handling'))]
    result['both_reviewers_diagnostic_screen'] = {pair:all(result['reviewers'][r][pair]['screen_pass'] for r in 'AB') for pair in ('dictionary','faithfulness')}
    result['limits'] = 'Post-hoc candidate-rule reassessment of familiar archived text, with duplicate propagation by construction. Not replacement primary results, linguistic gold, independent confirmation, unseen accuracy, or training/promotion authority.'
    return result


def self_test():
    _, _, groups, members = collect()
    validate_members(members, groups)
    for broken in (members[:-1], members[:-1]+[members[0]]):
        try: validate_members(broken, groups)
        except ValueError: pass
        else: raise AssertionError('Invalid fixed coverage admitted')
    item = next(iter(groups.values()))
    altered = deepcopy(item)
    altered['constraint'] += ' changed'
    assert group_key(IDS[0],item) != group_key(IDS[1],item) != group_key(IDS[0],altered)
    screen = read(prep.CONTRACT)['comparison']['screen']
    synthetic = {m['group']:{'judgment':'meaning_error'} for m in members}
    by = {(m['arm'],m['case_id']):m for m in members}
    # Two real case/work memberships test the gate without judging their text.
    chosen = (IDS[0],IDS[4])
    for cid in chosen:
        synthetic[by['faithfulness:B',cid]['group']]['judgment'] = 'accepted'
    observed = paired(members,synthetic,'faithfulness:A','faithfulness:B',screen)
    assert observed['denominator'] == 15
    # At least one chosen output is a duplicate, so it cannot become a false gain.
    assert observed['net_accepted_change'] == sum(by['faithfulness:A',c]['group'] != by['faithfulness:B',c]['group'] for c in chosen)
    assert not observed['screen_pass']
    different = [c for c in IDS if by['faithfulness:A',c]['group'] != by['faithfulness:B',c]['group']]
    synthetic = {m['group']:{'judgment':'meaning_error'} for m in members}
    for cid in different[:3]:
        synthetic[by['faithfulness:B',cid]['group']]['judgment'] = 'accepted'
    good = paired(members,synthetic,'faithfulness:A','faithfulness:B',screen)
    assert good['screen_pass'] and good['net_accepted_change'] == 3
    cid = different[3]
    synthetic[by['faithfulness:A',cid]['group']]['judgment'] = 'accepted'
    synthetic[by['faithfulness:B',cid]['group']]['judgment'] = 'critical_error'
    unsafe = paired(members,synthetic,'faithfulness:A','faithfulness:B',screen)
    assert unsafe['net_accepted_change'] == 2 and unsafe['screen_checks']['net_accepted_gain']
    assert not unsafe['screen_pass'] and unsafe['accepted_to_critical'] == [cid]
    print('PASS: closed coverage, cross-case/qualification separation and duplicate-neutral gate checks')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare','check','score','self-test'))
    parser.add_argument('--directory', type=Path, default=OUT)
    args = parser.parse_args()
    if args.action == 'prepare':
        files = build()
        prep.write_fresh(args.directory, files)
        print('Prepared 60 memberships / 42 unique contexts per reviewer; post-hoc candidate v1')
    elif args.action == 'check':
        checked = check(args.directory)
        print(json.dumps({k:checked[k] for k in ('status','memberships','unique_case_output_contexts','candidate_sha256')}))
    elif args.action == 'self-test':
        self_test()
    else:
        result = score(args.directory)
        prep.write_fresh(args.directory.parent/'scored', {'comparison.json':prep.json_bytes(result)})
        print(json.dumps({'post_hoc':True,'both_reviewers_diagnostic_screen':result['both_reviewers_diagnostic_screen']}))
