"""Deterministic TRAIN-only evidence for the frozen 24 source-only DEV queries."""
import argparse
from collections import Counter, defaultdict
from difflib import SequenceMatcher
import hashlib
import json
import math
from pathlib import Path
import re
import unicodedata

try:
    from . import dev_diagnostic
except ImportError:
    import dev_diagnostic

TRAIN_SHA256 = "844a5b64d43a423b69d5989527a53273290a43be15c399056c979f5abb0678a1"
SOURCE_HASHES = {
    "dev_diagnostic.py": "9d459482f3b7189cc2109bd68e36d14e77693df64f41574ff952d71bc6725d11",
    "bundle.py": "9721bcb2152b9f5e2fe1670b5ca280950dcfa2a81eefb13e132ac11dd2bbb1ce",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def tokens(text):
    result = []
    for word in unicodedata.normalize("NFC", text).casefold().split():
        while word and unicodedata.category(word[0]).startswith("P"):
            word = word[1:]
        while word and unicodedata.category(word[-1]).startswith("P"):
            word = word[:-1]
        if word:
            result.append(word)
    return tuple(result)


def target_key(text):
    return " ".join(unicodedata.normalize("NFC", text).casefold().split())


def prepare_pool(rows):
    """Resolve whole normalized-source groups before length eligibility checks."""
    grouped = defaultdict(list)
    for row in rows:
        grouped[tokens(row["text"])].append(row)
    pool, excluded = [], {"ambiguous": [], "duplicate": [], "length": []}
    for source, group in sorted(grouped.items()):
        group = sorted(group, key=lambda row: row["id"])
        if len({target_key(row["target"]) for row in group}) > 1:
            excluded["ambiguous"].append([row["id"] for row in group])
            continue
        row = group[0]
        excluded["duplicate"].extend(item["id"] for item in group[1:])
        if not 3 <= len(source) <= 60 or len(row["input_ids"]) > 320:
            excluded["length"].append(row["id"])
            continue
        pool.append((row, source, set(source)))
    pool.sort(key=lambda item: item[0]["id"])
    df = Counter(term for _, _, terms in pool for term in terms)
    return pool, df, excluded


def retrieve(query, pool, df):
    query_tokens = tokens(query)
    terms = set(query_tokens)
    count = len(pool)
    rare = {term for term in terms if 0 < df[term] <= .05 * count}
    idf = lambda term: 1 + math.log((count + 1) / (df[term] + 1))
    weighted_sum = lambda words: sum(idf(term) for term in sorted(words))
    candidates, excluded = [], []
    for row, source, source_terms in pool:
        overlap, union = terms & source_terms, terms | source_terms
        jaccard = len(overlap) / len(union) if union else 0
        sequence_ratio = SequenceMatcher(None, query_tokens, source, autojunk=False).ratio()
        contained = bool(query_tokens) and any(source[i:i + len(query_tokens)] == query_tokens
            for i in range(len(source) - len(query_tokens) + 1))
        reasons = (["query_contained"] if contained else []) + (["set_jaccard"] if jaccard >= .8 else []) + (["sequence_similarity"] if sequence_ratio >= .8 else [])
        if reasons:
            excluded.append({"id": row["id"], "reasons": reasons})
            continue
        candidates.append((row, source_terms, round(weighted_sum(overlap) / weighted_sum(union), 12) if union else 0,
                           round(jaccard, 12), round(sequence_ratio, 12)))
    selected, covered, works = [], set(), set()
    while len(selected) < 3:
        ranked = []
        for row, source_terms, weighted, jaccard, similarity in candidates:
            new = (rare & source_terms) - covered
            if new and row["work_id"] not in works:
                gain = round(weighted_sum(new), 12)
                ranked.append((-gain, -weighted, row["id"], row, new, jaccard, similarity))
        if not ranked:
            break
        negative_gain, negative_weight, _, row, new, jaccard, similarity = min(ranked, key=lambda item: item[:3])
        source_terms = set(tokens(row["text"]))
        selected.append({"id": row["id"], **{key: row[key] for key in ("record_id", "work_id", "credit", "revision")},
            "source_text": row["text"], "target_text": row["target"],
            "source_sha256": sha(row["text"].encode("utf-8")), "target_sha256": sha(row["target"].encode("utf-8")),
            "selection": {"rank": len(selected) + 1, "new_rare_terms": sorted(new), "idf_gain": -negative_gain,
                "weighted_jaccard": -negative_weight, "set_jaccard": jaccard, "sequence_similarity": similarity,
                "overlap_terms": sorted(terms & source_terms)}})
        covered.update(new)
        works.add(row["work_id"])
    support = {"query_terms": sorted(terms), "attested_rare_terms": sorted(rare),
        "unattested_terms": sorted(term for term in terms if not df[term]),
        "common_terms": sorted(term for term in terms if df[term] > .05 * count),
        "covered_rare_terms": sorted(covered), "uncovered_rare_terms": sorted(rare - covered),
        "near_copy_exclusions": excluded, "supported": bool(selected)}
    return selected, support


def build(train, inputs):
    for name, expected in SOURCE_HASHES.items():
        if sha(Path(__file__).with_name(name).read_bytes()) != expected:
            raise ValueError("Frozen source helper differs: " + name)
    queries = dev_diagnostic.read_inputs(inputs)
    data = Path(train).read_bytes()
    if sha(data) != TRAIN_SHA256:
        raise ValueError("TRAIN bytes differ from the frozen v5 dataset")
    rows = [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]
    identities = set()
    for row in rows:
        if (not isinstance(row, dict) or not re.fullmatch(r"parsig:\d{9}", row.get("record_id", ""))
                or row.get("work_id") != row["record_id"][:10]
                or row.get("id") != row["record_id"] + ":pal>fa"
                or (row.get("source_language"), row.get("target_language")) != ("pal", "fa")
                or any(not isinstance(row.get(key), str) or not row[key].strip() for key in ("text", "target", "credit"))
                or not re.fullmatch(r"[a-f0-9]{64}", row.get("revision", ""))
                or not isinstance(row.get("input_ids"), list) or not row["input_ids"]
                or any(type(token) is not int or token < 0 for token in row["input_ids"])
                or row["id"] in identities):
            raise ValueError("Invalid or duplicate TRAIN source identity")
        identities.add(row["id"])
    if {row["work_id"] for row in rows} & {row["work_id"] for row in queries}:
        raise ValueError("TRAIN and DEV works overlap")
    pool, df, excluded = prepare_pool(rows)
    if (len(pool), len({row["work_id"] for row, _, _ in pool}), len(excluded["ambiguous"]),
            sum(map(len, excluded["ambiguous"]))) != (2251, 74, 6, 13):
        raise ValueError("Frozen eligible TRAIN inventory differs")
    records = []
    for query in queries:
        examples, support = retrieve(query["source_text"], pool, df)
        records.append({**query, "source_sha256": sha(query["source_text"].encode("utf-8")), "examples": examples, "support": support})
    coverage = {"cases": len(records), "supported_cases": sum(bool(row["examples"]) for row in records),
        "attachments": sum(len(row["examples"]) for row in records),
        "attachment_histogram": dict(sorted(Counter(str(len(row["examples"])) for row in records).items())),
        **{key: sum(len(row["support"][key]) for row in records) for key in
           ("attested_rare_terms", "covered_rare_terms", "uncovered_rare_terms", "unattested_terms", "common_terms")}}
    audit = {"operation": "source_only_train_evidence", "train_sha256": TRAIN_SHA256,
        "inputs_sha256": dev_diagnostic.INPUTS_SHA256, "source_helpers_sha256": SOURCE_HASHES,
        "generator_sha256": sha(Path(__file__).read_bytes()), "train_rows": len(rows), "eligible_rows": len(pool),
        "eligible_works": len({row["work_id"] for row, _, _ in pool}), "excluded": excluded,
        "coverage": coverage, "query_ids": [row["id"] for row in records],
        "train_dev_work_disjoint": True, "references_read": False, "scoring_performed": False,
        "algorithm": {"normalization": "NFC then casefold then whitespace split; strip Unicode P at edges only",
            "target_normalization": "NFC then casefold then collapsed whitespace", "source_length": [3, 60],
            "maximum_input_ids": 320, "df_unit": "eligible unique normalized source", "rare_df_max": .05 * len(pool),
            "idf": "1 + ln((N+1)/(df+1))", "near_copy": "query token subsequence OR set Jaccard >= .8 OR token SequenceMatcher(autojunk=False) >= .8",
            "rank": "uncovered rare IDF gain descending, weighted Jaccard descending, full TRAIN id ascending",
            "weighted_jaccard": "sum IDF(intersection) / sum IDF(union); unseen df=0", "sum_order": "sorted terms",
            "round_decimals": 12, "maximum_examples": 3, "maximum_per_work": 1, "fallback": "none",
            "coverage_unit": "sum of distinct terms within each query; repeated terms across queries count separately"}}
    return records, audit


def prepare(train, inputs, output):
    output = Path(output)
    if output.exists():
        raise ValueError("Evidence output must be a fresh directory")
    records, audit = build(train, inputs)
    evidence = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records).encode("utf-8")
    audit["evidence_sha256"] = sha(evidence)
    output.mkdir(parents=True, exist_ok=False)
    with (output / "evidence.jsonl").open("xb") as stream:
        stream.write(evidence)
    with (output / "audit.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(audit, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")
    return audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("train", "inputs", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.train, args.inputs, args.output)["coverage"], sort_keys=True))


if __name__ == "__main__":
    main()
