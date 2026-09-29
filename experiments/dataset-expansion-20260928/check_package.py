"""Check frozen expansion evidence and compute an explicit-grain local manifest."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / 'package-manifest.json'
RESOURCE = ROOT / 'resources/local/dataset-expansion-20260928/lexicon-v1'
TRAIN = ROOT / 'experiments/train-audit-20260927/qualified-v1/train.jsonl'
TRAIN_SHA = '15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc'
PRIOR_S22 = 'experiments/composition-evidence-20260928/candidates.jsonl'
PRIOR_S22_SHA = 'b0525e52490f7fc4f58d0e4cb9808be59fbdaae9aab4ba17845bf672bdfd06b9'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def lines(path):
    return [json.loads(x) for x in path.read_text(encoding='utf8').splitlines()]


def verify():
    receipt = json.loads((HERE / 'lexicon-summary-v1.json').read_bytes())
    for name, expected in receipt['input_sha256'].items():
        assert sha((ROOT / name).read_bytes()) == expected, name
    for name, item in receipt['output_receipts'].items():
        raw = (RESOURCE / name).read_bytes()
        assert sha(raw) == item['sha256'] and len(raw) == item['bytes'], name
    for name, expected in receipt['code_sha256'].items():
        assert sha((HERE / name).read_bytes()) == expected
    assert sha(TRAIN.read_bytes()) == TRAIN_SHA
    train = lines(TRAIN)
    assert len(train) == 2237

    # Reuse the project's tested normalization/matching helper, without network.
    helper = ROOT / 'experiments/kosh-acquisition-20260928/novelty.py'
    assert sha(helper.read_bytes()) == 'bc3ccdaf1e76d831400fbc9b1f60ebf023ed1f5ac3437f39e01d36c3e8984f29'
    spec = importlib.util.spec_from_file_location('prior_novelty', helper)
    novelty = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(novelty)
    tokenize, helper_sha = novelty.load_source_tokens()
    assert helper_sha == '9c616eae976683ce16e5428af10b3e4425aa4d72e0f8ac4e33020f5238325abc'
    index = novelty.TrainingIndex([r['text'] for r in train], tokenize)
    lexical = lines(RESOURCE / 'lexical-resources.jsonl')
    plain = [r for r in lexical if r['resource_status'] == 'SOURCE_BACKED_LEXICON_CANDIDATE']
    old = {novelty.normal(f) for r in plain if r['origin'] == 'EXISTING_V4_GROUP' for f in r['forms']}
    new = {novelty.normal(f) for r in plain if r['origin'] == 'RECOVERED_V4_QUARANTINE' for f in r['forms']}

    packets = {}
    hash_cache = {}

    def bound(path, expected):
        path = (ROOT / path).resolve()
        assert path.is_relative_to(ROOT.resolve())
        if path not in hash_cache:
            hash_cache[path] = sha(path.read_bytes())
        assert hash_cache[path] == expected, path

    s22 = []
    for name in ['s22-candidates.jsonl', 's22-supplement.jsonl',
                 'parsig-format-candidates.jsonl', 'archive-candidates.jsonl']:
        path = HERE / name
        rows = lines(path)
        ids = [r.get('id', r.get('candidate_id')) for r in rows]
        assert None not in ids and len(set(ids)) == len(ids)
        for r in rows:
            if name.startswith('s22-'):
                assert r['admission_allowed'] is False and r['expert_certified'] is False
                bound(r['source_pdf'], r['source_pdf_sha256'])
                bound(r['image_path'], r['image_sha256'])
                assert r['pahlavi_transcription'].strip() and r['persian_translation'].strip()
                s22.append(r)
            elif name.startswith('parsig-'):
                assert r['admission'] is False
                p = r['provenance']
                bound(p['export_path'], p['export_sha256'])
                bound(p['publisher_response_path'], p['publisher_response_sha256'])
                assert sha(r['source_text'].encode()) == p['source_body_sha256']
                assert sha(r['target_text'].encode()) == p['target_body_sha256']
                c = r['citation_metadata']
                assert r['source_text'] + c['source_separator'] + c['source_edition'] + c['source_trailer'] == r['raw_source_field']
                assert r['target_text'] + c['target_separator'] + c['target_attribution'] == r['raw_target_field']
            else:
                assert r['train_admitted'] is False and r['target_language'] == 'en'
                for key in ['raw_source', 'archive_record_pointer']:
                    bound(r[key]['path'], r[key]['sha256'])
        packets[name] = {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes()), 'records': len(rows)}
    assert len(s22) == len({r['id'] for r in s22})
    bound(PRIOR_S22, PRIOR_S22_SHA)
    historical_s22 = lines(ROOT / PRIOR_S22)
    assert len(historical_s22) == 7
    exact_seen = {novelty.normal(r['pahlavi_transcription']) for r in historical_s22}
    exact_prior = [r['id'] for r in s22 if novelty.normal(r['pahlavi_transcription']) in exact_seen]
    forms = Counter(novelty.normal(r['pahlavi_transcription']) for r in s22)
    census = {
        'flat_lexical_candidate_records': len(plain),
        'full_form_coverage': novelty.form_counts(old | new, index, tokenize),
        'recovered_mmp_form_coverage': novelty.form_counts(new, index, tokenize),
        'recovered_mmp_forms_not_in_old_flat_candidates': len(new - old),
        'new_s22_records_by_type': dict(Counter(r.get('record_type', 'pedagogical_clause') for r in s22)),
        'new_s22_distinct_source_strings': len(forms),
        'new_s22_exact_source_repeats_of_prior_seven': exact_prior,
        'new_s22_repeated_source_strings_with_different_contexts': {k: v for k, v in forms.items() if v > 1},
        'new_s22_whitespace_terms': {'source': sum(len(r['pahlavi_transcription'].split()) for r in s22),
                                    'target': sum(len(r['persian_translation'].split()) for r in s22)},
        'limits': 'Different grains are not summed into training pairs. Lexical coverage is orthographic, not semantic novelty. S22 counts preserve variants and polysemy; no independent-attestation or tokenizer count claim.'}
    return {'status': 'SOURCE_RESOURCE_CHECKPOINT_NOT_TRAINING_RELEASE', 'historical_training_pairs': 2237,
            'historical_training_sha256': TRAIN_SHA, 'new_training_admissions': 0,
            'prior_s22_packet': {'path': PRIOR_S22, 'sha256': PRIOR_S22_SHA},
            'lexical_manifest': {'path': 'experiments/dataset-expansion-20260928/lexicon-summary-v1.json',
                                 'sha256': sha((HERE / 'lexicon-summary-v1.json').read_bytes())},
            'parallel_and_pedagogical_packets': packets, 'census': census,
            'code_sha256': sha(Path(__file__).read_bytes()), 'bound_evidence_files_checked': len(hash_cache)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if args.write and OUT.exists():
        raise ValueError('Frozen package manifest exists; do not overwrite')
    report = verify()
    if args.write:
        OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    elif OUT.exists():
        assert json.loads(OUT.read_bytes()) == report
    print(json.dumps(report, ensure_ascii=False))
