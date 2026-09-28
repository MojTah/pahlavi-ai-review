"""Filter frozen witness-audited DEV evidence by qualified TRAIN membership only."""
import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import unicodedata


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "experiments/dev-assisted-qualified-20260927/evidence"
FILES = {
    "previous_evidence": ("experiments/dev-assisted-20260927/admitted-evidence/evidence.jsonl", "6a22bd61461916199c0637fbab82f0a420b61f2abd4d8e88306a1bae3c434a7d"),
    "previous_audit": ("experiments/dev-assisted-20260927/admitted-evidence/audit.json", "18255dd781b83029a6a848cdb5a89928cbef2069c1d3eeaf9c9de994a4b91933"),
    "witness_review_receipt": ("experiments/dev-assisted-20260927/PREPARATION-REVIEW.md", "83cf37682badca84b427d47090c704d8771bc9d664aee2cfb2bea0ea97fc554e"),
    "legacy_generator": ("cloud_pilot/dev_evidence.py", "611d190d4075a9b4fc99c374c9bbbfa6068d9e48170246b4a4db33a2f5ce0a08"),
    "qualified_train": ("experiments/train-audit-20260927/qualified-v1/train.jsonl", "15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc"),
    "qualified_manifest": ("experiments/train-audit-20260927/qualified-v1/manifest.json", "a5031b6f2abe81b103fb0c863602a7441776efc5b4dccf11b2e1dc6a2050ec15"),
    "qualified_ledger": ("experiments/train-audit-20260927/qualified-v1/final-ledger.jsonl", "d79af2e64fbb92954c8b8d0ed9cb7a34e7e7d24d4c22ea9c22f1da6d569a8e77"),
    "inputs": ("experiments/dev-diagnostic-20260927/inputs.jsonl", "06ac58310bf67767fae4124d8e935c808d15debcd8daebce07b583937cd97182"),
}
QUERY_FIELDS = {"id", "record_id", "work_id", "source_language", "target_language", "source_text"}
ELIGIBLE = {"ELIGIBLE", "ELIGIBLE_WITH_QUALIFICATIONS"}
LEGACY_COVERAGE = "Original attested rare case-term universe; original selection/IDF metadata retained, not recomputed for qualified TRAIN"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def checked(data, expected, label):
    require(sha(data) == expected, "Frozen hash changed: " + label)
    return data


def rows(data):
    return [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]


def unique(items, label):
    mapped = {item["id"]: item for item in items}
    require(len(mapped) == len(items), "Duplicate IDs: " + label)
    return mapped


def tokens(text):
    # Exact normalization from the frozen legacy generator; no new retrieval/IDF.
    result = []
    for word in unicodedata.normalize("NFC", text).casefold().split():
        while word and unicodedata.category(word[0]).startswith("P"):
            word = word[1:]
        while word and unicodedata.category(word[-1]).startswith("P"):
            word = word[:-1]
        if word:
            result.append(word)
    return tuple(result)


def validate_example(example, ledger, train=None):
    require(example["id"] == ledger["id"], "Example/ledger ID differs")
    for key in ("record_id", "work_id", "credit", "revision", "source_text", "target_text", "source_sha256", "target_sha256"):
        require(example[key] == ledger[key], "Example/ledger payload changed: " + key)
    for side in ("source", "target"):
        require(sha(example[side + "_text"].encode("utf-8")) == example[side + "_sha256"], "Example text/hash mismatch: " + side)
    review = ledger["linguistic_review"]
    require(review["id"] == example["id"] and review["source_sha256"] == example["source_sha256"]
            and review["target_sha256"] == example["target_sha256"], "Linguistic review identity differs")
    require(review["expert_adjudicated"] is False and ledger["expert_status"] == "NOT_EXPERT_ADJUDICATED", "Unexpected expert status")
    if train is not None:
        require(ledger["disposition"] in ELIGIBLE and review["disposition"] in ELIGIBLE, "Surviving example is not qualified")
        require(ledger["row_sha256"] == sha(canonical(train)), "Qualified TRAIN row hash differs")
        for key in ("id", "record_id", "work_id", "credit", "revision"):
            require(example[key] == train[key], "Example/TRAIN identity changed: " + key)
        require(example["source_text"].encode("utf-8") == train["text"].encode("utf-8")
                and example["target_text"].encode("utf-8") == train["target"].encode("utf-8"), "Example/TRAIN text bytes changed")


def build():
    data = {name: checked((ROOT / path).read_bytes(), expected, name) for name, (path, expected) in FILES.items()}
    manifest = json.loads(data["qualified_manifest"])
    for key, name in (("train.jsonl", "qualified_train"), ("final-ledger.jsonl", "qualified_ledger")):
        require(manifest["files"][key] == {"sha256": sha(data[name]), "bytes": len(data[name])}, "Qualification manifest differs")
    require(manifest["status"] == "PROVISIONAL_AI_QUALIFIED_DATA_NOT_EXPERT_CERTIFIED", "Unexpected qualification status")
    previous = rows(data["previous_evidence"])
    queries = rows(data["inputs"])
    train = unique(rows(data["qualified_train"]), "TRAIN")
    ledger_rows = rows(data["qualified_ledger"])
    ledger = unique(ledger_rows, "ledger")
    ledger_lines = {row["id"]: index for index, row in enumerate(ledger_rows, 1)}
    require(len(train) == 2237 and len(ledger) == 2484, "Qualification counts changed")
    require(set(train) == {cid for cid, row in ledger.items() if row["disposition"] in ELIGIBLE}, "TRAIN and qualified ledger membership differ")
    expected_ids = [f"QUALITYDEV1-{i:03d}" for i in range(1, 25)]
    require([q["id"] for q in queries] == [q["id"] for q in previous] == expected_ids, "DEV case identity/order differs")
    require(all(set(query) == QUERY_FIELDS for query in queries), "Source-only input schema changed")
    require(sum(len(row["examples"]) for row in previous) == 68, "Original attachment count differs")
    require(not ({row["work_id"] for row in train.values()} & {q["work_id"] for q in queries}), "Qualified TRAIN/DEV works overlap")
    prior_audit = json.loads(data["previous_audit"])
    require(prior_audit["evidence_sha256"] == FILES["previous_evidence"][1]
            and prior_audit["status"] == "WITNESS_SCREEN_PASSED_NOT_CLOUD_ADMISSION"
            and prior_audit["attachments"] == 68, "Prior witness audit does not bind these examples")
    output, removed, retained = [], [], []
    for line, (original, query) in enumerate(zip(previous, queries), 1):
        require({key: original[key] for key in QUERY_FIELDS} == query, "DEV source-only payload changed")
        require(original["source_sha256"] == sha(query["source_text"].encode("utf-8")), "DEV source hash differs")
        record = copy.deepcopy(original)
        record["examples"] = []
        for index, example in enumerate(original["examples"]):
            entry = ledger[example["id"]]
            validate_example(example, entry, train.get(example["id"]))
            pointer = {"case_id": query["id"], "example_id": example["id"],
                       "prior_evidence_pointer": FILES["previous_evidence"][0] + f":{line}",
                       "original_example_index": index, "example_canonical_sha256": sha(canonical(example)),
                       "prior_witness_audit": FILES["previous_audit"][0],
                       "prior_witness_review_pointer": FILES["witness_review_receipt"][0] + ":20",
                       "qualified_ledger_pointer": FILES["qualified_ledger"][0] + f":{ledger_lines[example['id']]}",
                       "ledger_record_canonical_sha256": sha(canonical(entry)),
                       "disposition": entry["disposition"], "linguistic_review": entry["linguistic_review"],
                       "qualification_status": entry["qualification_status"], "expert_status": entry["expert_status"],
                       "edition": entry["edition"], "flags": entry["flags"],
                       "curation_alignment_scope": entry["curation_alignment_scope"]}
            if example["id"] in train:
                record["examples"].append(example)
                retained.append(pointer)
            else:
                require(entry["disposition"] == "QUARANTINED", "Excluded witness lacks quarantine disposition")
                removed.append({**pointer, "reason": entry["linguistic_review"]["reason"]})
        universe = set(original["support"]["attested_rare_terms"])
        covered = universe & {term for example in record["examples"] for term in tokens(example["source_text"])}
        record["support"].update(covered_rare_terms=sorted(covered), uncovered_rare_terms=sorted(universe - covered),
                                 supported=bool(record["examples"]), coverage_basis=LEGACY_COVERAGE)
        require(record["examples"] == [example for example in original["examples"] if example["id"] in train], "Example order/payload changed")
        output.append(record)
    require(len(retained) == 58 and len(removed) == 10 and len({row["example_id"] for row in removed}) == 9, "Unexpected evidence intersection")
    coverage = {"cases": len(output), "attachments": len(retained), "distinct_witnesses": len({r["example_id"] for r in retained}),
                "supported_cases": sum(bool(row["examples"]) for row in output),
                "attachment_histogram": dict(sorted(Counter(str(len(row["examples"])) for row in output).items())),
                **{key: sum(len(row["support"][key]) for row in output) for key in
                   ("attested_rare_terms", "covered_rare_terms", "uncovered_rare_terms", "unattested_terms", "common_terms")}}
    audit = {"status": "LOCAL_QUALIFIED_EVIDENCE_PREPARATION_ONLY", "source_files": {
                name: {"path": path, "sha256": sha(data[name]), "bytes": len(data[name])} for name, (path, _) in FILES.items()},
             "helper_sha256": sha(Path(__file__).read_bytes()), "qualified_train_rows": len(train),
             "coverage_basis": LEGACY_COVERAGE, "legacy_coverage": coverage,
             "removed_attachments": removed, "retained_qualifications": retained,
             "removed_distinct_witnesses": len({r["example_id"] for r in removed}),
             "derivation": "Ordered intersection only; no retrieval, reranking, repairs or replacements. Full surviving examples and legacy selection metadata preserved. Qualifications retained in this audit, tied to exact witness hashes.",
             "prior_witness_audit_limit": prior_audit["limits"], "new_archive_or_specialist_review_performed": False,
             "references_or_dev_answers_read": False, "model_outputs_used": False, "scoring_performed": False,
             "expert_adjudicated": False, "paid_run_admitted": False,
             "limits": "AI/archive-qualified examples are not expert-certified senses or a claim of complete semantic accuracy. Legacy term coverage is descriptive and does not measure translation quality or qualified-pool IDF."}
    return output, audit


def fresh(output):
    require(not output.exists(), "Evidence output must be a fresh directory")


def negative_checks(records):
    checks = []
    for label, action in (("wrong_hash", lambda: checked(b"changed", FILES["qualified_train"][1], "negative fixture")),
                          ("overwrite", lambda: fresh(ROOT))):
        try:
            action()
        except ValueError:
            checks.append(label)
        else:
            raise AssertionError("Negative check accepted: " + label)
    example = records[0]["examples"][0]
    ledger = unique(rows(checked((ROOT / FILES["qualified_ledger"][0]).read_bytes(), FILES["qualified_ledger"][1], "ledger")), "ledger")
    changed = copy.deepcopy(example)
    changed["target_text"] += " changed"
    try:
        validate_example(changed, ledger[example["id"]])
    except ValueError:
        checks.append("changed_payload")
    else:
        raise AssertionError("Changed example payload accepted")
    return checks


def prepare(check=False):
    if not check:
        fresh(OUTPUT)
    records, audit = build()
    audit["negative_checks_passed"] = negative_checks(records)
    evidence = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records).encode("utf-8")
    audit["evidence_sha256"] = sha(evidence)
    audit_bytes = (json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if check:
        require((OUTPUT / "evidence.jsonl").read_bytes() == evidence, "Derived evidence does not regenerate exactly")
        require((OUTPUT / "audit.json").read_bytes() == audit_bytes, "Derived audit does not regenerate exactly")
    else:
        OUTPUT.mkdir(parents=True, exist_ok=False)
        for name, payload in (("evidence.jsonl", evidence), ("audit.json", audit_bytes)):
            with (OUTPUT / name).open("xb") as stream:
                stream.write(payload)
    return {"status": "PASS_CHECK_ONLY" if check else "PREPARED_NOT_CLOUD_ADMITTED", "coverage": audit["legacy_coverage"],
            "removed_attachments": len(audit["removed_attachments"]), "removed_distinct_witnesses": audit["removed_distinct_witnesses"],
            "negative_checks_passed": audit["negative_checks_passed"], "helper_sha256": audit["helper_sha256"],
            "evidence_sha256": sha(evidence), "audit_sha256": sha(audit_bytes)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Regenerate in memory and verify existing output, without writes")
    print(json.dumps(prepare(parser.parse_args().check), indent=2))
