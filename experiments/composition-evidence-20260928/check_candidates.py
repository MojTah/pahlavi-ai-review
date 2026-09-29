"""Reproducible source-copy screen for staged examples; never training admission."""
import hashlib
import json
from pathlib import Path
import sys
from difflib import SequenceMatcher

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from audit_training_corpus import checked, jsonl, source_tokens, DATASET_ID, DATASET_PINS, TRANSLATOR


def relation(candidate, existing):
    if not candidate or not existing:
        raise ValueError('Empty source cannot establish novelty')
    contained = any(existing[i:i + len(candidate)] == candidate
                    for i in range(len(existing) - len(candidate) + 1))
    return candidate == existing, contained, SequenceMatcher(None, candidate, existing, autojunk=False).ratio()


def main():
    # Small runnable controls: exact, embedded and unrelated sources differ.
    assert relation(('a', 'b'), ('a', 'b'))[:2] == (True, True)
    assert relation(('a', 'b'), ('x', 'a', 'b', 'y'))[:2] == (False, True)
    assert relation(('a', 'b'), ('x', 'y')) == (False, False, 0.0)
    folder = Path(__file__).resolve().parent
    inputs = {}
    for implementation in [Path(__file__).resolve(), ROOT / 'scripts/audit_training_corpus.py']:
        data = implementation.read_bytes()
        inputs[str(implementation)] = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
    candidate_bytes = (folder / 'candidates.jsonl').read_bytes()
    candidates = jsonl(candidate_bytes)
    assert len(candidates) == len({c['id'] for c in candidates}) == 7
    pools = {}
    for name in ['train-records.jsonl', 'dev-records.jsonl', 'test-records.jsonl']:
        data = checked(TRANSLATOR / 'runs/datasets' / DATASET_ID / name, DATASET_PINS[name], inputs)
        # Only IDs, work identities and sources enter this check; no answers emitted.
        pools[name] = [(r['id'], r['work_id'], source_tokens(r['transcription'])) for r in jsonl(data)]
    train = ROOT / 'experiments/train-audit-20260927/qualified-v1/train.jsonl'
    data = checked(train, '15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc', inputs)
    pools['qualified_train'] = [(r['id'], r['work_id'], source_tokens(r['text'])) for r in jsonl(data)]
    results = []
    for c in candidates:
        assert c['status'] == 'STAGED_NOT_TRAIN_ADMITTED' and c['expert_certified'] is False
        checked(ROOT / c['source_pdf'], c['source_pdf_sha256'], inputs)
        checked(ROOT / c['image_path'], c['image_sha256'], inputs)
        a = source_tokens(c['pahlavi_transcription'])
        matches = {}
        for label, pool in pools.items():
            hits = []
            best = (0.0, None, None)
            for identifier, work, b in pool:
                if not b:
                    continue
                exact, contained, similarity = relation(a, b)
                if similarity > best[0]:
                    best = (similarity, identifier, work)
                if exact or contained or similarity >= 0.8:
                    hits.append({'id': identifier, 'work_id': work, 'exact': exact,
                                 'contained': contained, 'token_ratio': similarity})
            matches[label] = {'flagged': hits, 'nearest': best}
        results.append({'id': c['id'], 'source_copy_screen': matches,
                        'admission': False, 'work_lineage_review_complete': False})
    report = {'status': 'MECHANICAL_SCREEN_ONLY_NOT_TRAIN_ADMISSION',
              'candidate_sha256': hashlib.sha256(candidate_bytes).hexdigest(),
              'inputs': inputs, 'counts': {k: len(v) for k, v in pools.items()},
              'normalization': 'Existing audit source_tokens: NFC/casefold, boundary punctuation removed; internal characters retained.',
              'limits': 'Exact/contiguous/token-ratio screens cannot identify every alternate spelling, paraphrase, witness or work lineage. No new split or expert certification.',
              'rows': results}
    (folder / 'source-copy-screen.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'candidates': len(results),
                      'flagged_counts': {k: sum(len(r['source_copy_screen'][k]['flagged']) for r in results) for k in pools}}))


if __name__ == '__main__':
    main()
