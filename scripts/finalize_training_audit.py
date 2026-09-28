"""Finalize complete provisional AI reviews; retain original TRAIN row bytes only.

This command never approves a paid run or certifies expert/semantic correctness.
All validation completes before the fresh output directory is created.
"""
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
AUDIT_ROOT = "experiments/train-audit-20260927"
TRAIN_PATH = "resources/local/cloud-pilot-20260926-hf-v5/train.jsonl"
TRAIN_SHA = "844a5b64d43a423b69d5989527a53273290a43be15c399056c979f5abb0678a1"
MECHANICAL_SHA = "b46d06e510f8299c4188585fe2f6966edb17b52a28dbebdf998b1822def86b29"
PACKET_MANIFEST_SHA = "cc1e8e86d735b1380ffefe565c31f3ad2455978b581e334b86923cf7d8605795"
PROTOCOL_SHA = "18302266c1f65001b7a215eff8069953eefd0c316fcdeccedf4a3ac8f468afc8"
REVIEWERS = {1: "/root/train_review_01", 2: "/root/train_review_02", 3: "/root/train_review_03",
             4: "/root/train_review_04", 5: "/root/train_review_04", 6: "/root/train_review_03",
             7: "/root/train_review_07", 8: "/root/train_review_08"}
REVIEW_FIELDS = {"id", "source_sha256", "target_sha256", "alignment", "meaning", "disposition",
                 "reason", "source_span", "target_span", "qualifications", "evidence",
                 "reviewer_id", "reviewer_type", "expert_adjudicated"}
STRUCTURAL_FIELDS = {"id", "source_sha256", "target_sha256", "flag_kinds", "decision", "reason",
                     "evidence", "reviewer_id", "reviewer_type", "expert_adjudicated"}
ELIGIBLE = {"ELIGIBLE", "ELIGIBLE_WITH_QUALIFICATIONS"}
STATUS = "PROVISIONAL_AI_QUALIFIED_DATA_NOT_EXPERT_CERTIFIED"


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(data):
    return sha256(data).hexdigest()


def rows(data):
    return [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]


def unique(values, label):
    result = {}
    for row in values:
        id = row.get("id")
        if not isinstance(id, str) or not id or id in result:
            raise ValueError(f"Missing or duplicate ID in {label}: {id!r}")
        result[id] = row
    return result


def read_verified(path, inputs, expected_sha=None, expected_bytes=None):
    path = Path(path).resolve()
    data = path.read_bytes()
    value = {"sha256": digest(data), "bytes": len(data)}
    if expected_sha is not None and value["sha256"] != expected_sha:
        raise ValueError("Hash mismatch: " + str(path))
    if expected_bytes is not None and value["bytes"] != expected_bytes:
        raise ValueError("Byte-size mismatch: " + str(path))
    if str(path) in inputs and inputs[str(path)] != value:
        raise ValueError("Input changed during validation: " + str(path))
    inputs[str(path)] = value
    return data


def nonempty_strings(value, name, required=False):
    if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() for x in value):
        raise ValueError(name + " must contain only nonempty strings")
    if required and not value:
        raise ValueError(name + " must not be empty")


def reason_and_evidence(review, locator=None):
    reason = review["reason"]
    if not isinstance(reason, str) or not reason.strip() or re.fullmatch(
            r"(?:pass|ok|eligible|checked|looks good|no (?:identified )?issues?|translation (?:is )?correct)[.! ]*",
            reason.strip(), re.IGNORECASE):
        raise ValueError("A source-specific reason is required: " + review["id"])
    nonempty_strings(review["evidence"], "evidence", required=True)
    if locator is not None and locator not in review["evidence"]:
        raise ValueError("Evidence must include the exact packet locator: " + review["id"])


def validate_reviews(packet, review_rows, expected_reviewer):
    packet_by_id = unique(packet, "packet")
    reviews = unique(review_rows, "reviews")
    if set(reviews) != set(packet_by_id):
        raise ValueError("Review coverage differs from assigned packet")
    for id, review in reviews.items():
        item = packet_by_id[id]
        if set(review) != REVIEW_FIELDS:
            raise ValueError("Unexpected or missing review fields: " + id)
        if (review["reviewer_id"] != expected_reviewer or review["reviewer_type"] != "AI"
                or review["expert_adjudicated"] is not False):
            raise ValueError("Reviewer identity or expert claim invalid: " + id)
        for field in ("source_sha256", "target_sha256"):
            if review[field] != item[field]:
                raise ValueError("Review text hash mismatch: " + id)
        alignment, meaning, disposition = (review[x] for x in ("alignment", "meaning", "disposition"))
        if alignment not in {"pass", "qualified", "uncertain", "error"} or meaning not in {"no_identified_issue", "qualified", "uncertain", "error"}:
            raise ValueError("Unsupported alignment/meaning status: " + id)
        if disposition not in ELIGIBLE | {"QUARANTINED"}:
            raise ValueError("Incomplete or invalid disposition: " + id)
        nonempty_strings(review["qualifications"], "qualifications")
        concern = alignment in {"uncertain", "error"} or meaning in {"uncertain", "error"}
        if concern != (disposition == "QUARANTINED"):
            raise ValueError("Concern/disposition contradiction: " + id)
        if disposition == "ELIGIBLE" and (alignment != "pass" or meaning != "no_identified_issue" or review["qualifications"]):
            raise ValueError("Unqualified eligibility contradicts review: " + id)
        if disposition == "ELIGIBLE_WITH_QUALIFICATIONS" and not review["qualifications"]:
            raise ValueError("Qualified eligibility needs explicit qualifications: " + id)
        for span, text in (("source_span", "source"), ("target_span", "target")):
            if not isinstance(review[span], str) or review[span] not in item[text]:
                raise ValueError("Review span is not an exact substring: " + id)
        if concern and not (review["source_span"].strip() or review["target_span"].strip()):
            raise ValueError("Concern requires an exact supporting span: " + id)
        reason_and_evidence(review, item["locator"])
    return reviews


def nonmarker_flags(row):
    return sorted({flag["kind"] for flag in row["flags"] if not flag["kind"].startswith("marker:")})


def validate_structural(ledger, reviews):
    expected = {row["id"]: row for row in ledger if nonmarker_flags(row)}
    actual = unique(reviews, "structural reviews")
    if set(actual) != set(expected):
        raise ValueError("Structural review coverage differs from non-marker flags")
    for id, review in actual.items():
        item = expected[id]
        if set(review) != STRUCTURAL_FIELDS:
            raise ValueError("Unexpected or missing structural fields: " + id)
        if (review["reviewer_id"] != "/root" or review["reviewer_type"] != "AI"
                or review["expert_adjudicated"] is not False):
            raise ValueError("Structural reviewer identity or expert claim invalid: " + id)
        if review["decision"] not in {"CLEAR_FLAG", "QUARANTINE"}:
            raise ValueError("Invalid structural decision: " + id)
        if review["flag_kinds"] != nonmarker_flags(item):
            raise ValueError("Structural flag kinds differ: " + id)
        if any(review[key] != item[key] for key in ("source_sha256", "target_sha256")):
            raise ValueError("Structural text hash mismatch: " + id)
        reason_and_evidence(review)
    return actual


def validate_ledger(original_data, ledger):
    original_lines = original_data.splitlines(keepends=True)
    if any(not line.strip() for line in original_lines):
        raise ValueError("Blank original TRAIN line is not an auditable row")
    original_rows = [json.loads(line) for line in original_lines]
    originals = unique(original_rows, "original TRAIN")
    checked = unique(ledger, "mechanical ledger")
    if list(originals) != list(checked):
        raise ValueError("Mechanical ledger must match every original ID and its order")
    for number, row in enumerate(original_rows, 1):
        item = checked[row["id"]]
        if item["row_number"] != number or item["row_sha256"] != digest(canonical(row)):
            raise ValueError("Original TRAIN row identity/hash mismatch: " + row["id"])
        for key, value in (("source_text", row["text"]), ("target_text", row["target"]),
                           ("source_sha256", digest(row["text"].encode("utf-8"))),
                           ("target_sha256", digest(row["target"].encode("utf-8"))),
                           ("record_id", row["record_id"]), ("work_id", row["work_id"]),
                           ("revision", row["revision"]), ("credit", row["credit"])):
            if item[key] != value:
                raise ValueError("Mechanical ledger projection mismatch: " + row["id"] + ":" + key)
        expected = {"mechanical_status": "PASS", "provenance_status": "PASS", "token_structure_status": "PASS_STRUCTURE_ONLY",
                    "token_reconstruction_status": "PASS_HASH_BOUND_INDEPENDENT_PROOF", "split_status": "PASS_IDENTITY_AND_PINNED_HOLDOUT"}
        if any(item[key] != value for key, value in expected.items()) or item["mechanical_errors"] or item["split_errors"]:
            raise ValueError("Mechanical/token/split checks are not clear: " + row["id"])
    return original_rows, original_lines


def merge(original_data, ledger, reviews, structural):
    original_rows, lines = validate_ledger(original_data, ledger)
    if set(reviews) != {row["id"] for row in original_rows}:
        raise ValueError("Final linguistic review coverage mismatch")
    structural = validate_structural(ledger, list(structural.values()))
    final, retained = [], []
    for original, line, mechanical in zip(original_rows, lines, ledger):
        review = reviews[original["id"]]
        structural_review = structural.get(original["id"])
        quarantine = structural_review and structural_review["decision"] == "QUARANTINE"
        disposition = "QUARANTINED" if quarantine else review["disposition"]
        if disposition not in ELIGIBLE | {"QUARANTINED"}:
            raise ValueError("Unreviewed final disposition: " + original["id"])
        final.append({**mechanical, "alignment_status": "PROVISIONAL_AI_" + review["alignment"].upper(),
                      "semantic_status": "PROVISIONAL_AI_" + review["meaning"].upper(),
                      "expert_status": "NOT_EXPERT_ADJUDICATED", "disposition": disposition,
                      "linguistic_review": review, "structural_review": structural_review,
                      "qualification_status": STATUS, "paid_run_admitted": False})
        if disposition in ELIGIBLE:
            retained.append(line)
    return final, b"".join(retained)


def load_inputs(root):
    root = Path(root).resolve()
    inputs = {}
    audit_root = root / AUDIT_ROOT
    mechanical_dir = audit_root / "corpus-audit-v2"
    summary = json.loads(read_verified(mechanical_dir / "summary.json", inputs, MECHANICAL_SHA))
    expected_outputs = {"inputs.json", "ledger.jsonl", "near-source-pairs.jsonl", "review-candidates.jsonl"}
    if set(summary["output_sha256"]) != expected_outputs:
        raise ValueError("Mechanical output inventory differs")
    mechanical = {name: read_verified(mechanical_dir / name, inputs, value) for name, value in summary["output_sha256"].items()}
    if (summary["rows"] != 2484 or summary["ledger_rows"] != 2484 or summary["mechanical_failed_rows"] != 0
            or summary["mechanical_error_counts"] or summary["selection_reconstruction"]["errors"]
            or summary["near_source_scan"]["completed"] is not True
            or summary["near_source_scan"]["pairs_enumerated"] != 3529764):
        raise ValueError("Mechanical audit is incomplete or failed")
    upstream = json.loads(mechanical["inputs.json"])
    if upstream["train_sha256"] != TRAIN_SHA or len(upstream["files"]) != 192:
        raise ValueError("Mechanical input identity/count differs")
    for path, metadata in upstream["files"].items():
        read_verified(path, inputs, metadata["sha256"], metadata["bytes"])
    original_data = read_verified(root / TRAIN_PATH, inputs, TRAIN_SHA)
    ledger = rows(mechanical["ledger.jsonl"])
    original_rows, _ = validate_ledger(original_data, ledger)
    if len(original_rows) != 2484:
        raise ValueError("Expected exactly 2,484 original TRAIN rows")
    original_by_id = unique(original_rows, "TRAIN")
    review_dir = audit_root / "linguistic-review"
    manifest = json.loads(read_verified(review_dir / "manifest.json", inputs, PACKET_MANIFEST_SHA))
    read_verified(review_dir / "PROTOCOL.md", inputs, PROTOCOL_SHA)
    if manifest["scope_rows"] != 2484 or manifest["train_sha256"] != TRAIN_SHA or len(manifest["packets"]) != 8:
        raise ValueError("Packet manifest scope differs")
    all_packet_ids, reviews = [], {}
    sorted_ids = sorted(original_by_id)
    for number, packet_info in enumerate(manifest["packets"], 1):
        expected_path = f"{AUDIT_ROOT}/linguistic-review/packet-{number:02d}/packet.jsonl"
        if packet_info["packet"] != number or packet_info["path"] != expected_path:
            raise ValueError("Packet identity/path mismatch")
        packet_path = root / expected_path
        packet = rows(read_verified(packet_path, inputs, packet_info["sha256"]))
        expected_ids = sorted_ids[(number - 1) * len(sorted_ids) // 8:number * len(sorted_ids) // 8]
        if ([row["id"] for row in packet] != expected_ids or len(packet) != packet_info["rows"]
                or packet[0]["id"] != packet_info["first_id"] or packet[-1]["id"] != packet_info["last_id"]):
            raise ValueError("Packet boundaries/order/coverage differ")
        for item in packet:
            original = original_by_id[item["id"]]
            for key, value in (("source", original["text"]), ("target", original["target"]),
                               ("source_sha256", digest(original["text"].encode("utf-8"))),
                               ("target_sha256", digest(original["target"].encode("utf-8"))),
                               ("record_id", original["record_id"]), ("revision", original["revision"]),
                               ("credit", original["credit"]), ("work_id", original["work_id"])):
                if item[key] != value:
                    raise ValueError("Packet differs from original TRAIN: " + item["id"] + ":" + key)
        packet_reviews = validate_reviews(packet, rows(read_verified(packet_path.with_name("reviews.jsonl"), inputs)), REVIEWERS[number])
        if set(packet_reviews) & set(reviews):
            raise ValueError("Review ID repeated across packets")
        reviews.update(packet_reviews)
        all_packet_ids.extend(expected_ids)
    if all_packet_ids != sorted_ids:
        raise ValueError("Packet union differs from complete TRAIN")
    structural = validate_structural(ledger, rows(read_verified(audit_root / "structural-review.jsonl", inputs)))
    return original_data, ledger, reviews, structural, inputs


def finalize(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    if output.exists():
        raise ValueError("Preserve existing artifacts: output must be fresh")
    if any(output.is_relative_to(root / name) for name in ("sources", "resources", "scripts", "tests")):
        raise ValueError("Output must not be inside authoritative source/code directories")
    original_data, ledger, reviews, structural, inputs = load_inputs(root)
    final, payload = merge(original_data, ledger, reviews, structural)
    # Up to here no directory or file has been created.
    script = Path(__file__).resolve()
    read_verified(script, inputs)
    by_work = defaultdict(Counter)
    for row in final:
        by_work[row["work_id"]][row["disposition"]] += 1
    artifacts = {"final-ledger.jsonl": b"".join(canonical(row) + b"\n" for row in final), "train.jsonl": payload}
    output_info = {name: {"sha256": digest(data), "bytes": len(data)} for name, data in artifacts.items()}
    summary = {"status": STATUS, "original_train_sha256": TRAIN_SHA, "original_rows": len(final),
               "qualified_rows": sum(row["disposition"] in ELIGIBLE for row in final),
               "disposition_counts": dict(Counter(row["disposition"] for row in final)),
               "by_work": {work: dict(counts) for work, counts in sorted(by_work.items())},
               "structural_decisions": dict(Counter(row["decision"] for row in structural.values())),
               "structural_quarantine_overrides": sum(row["decision"] == "QUARANTINE" and reviews[id]["disposition"] in ELIGIBLE for id, row in structural.items()),
               "reviewer_type": "AI", "expert_adjudicated": False, "paid_run_admitted": False,
               "source_target_token_mutations": 0, "payload_filter": "Exact original complete row bytes, original order; no reserialization",
               "inputs": inputs, "outputs": output_info, "script_sha256": inputs[str(script)]["sha256"],
               "limits": ["Complete AI review and integrity checks are not specialist certification or proof of perfect meaning.",
                          "Reason specificity is supported by reviewer attribution, exact spans and cited evidence; code cannot judge linguistic reasoning.",
                          "Structural CLEAR_FLAG never overrides linguistic quarantine; structural QUARANTINE always excludes the row."]}
    artifacts["summary.json"] = canonical(summary) + b"\n"
    manifest = {"status": STATUS, "files": {name: {"sha256": digest(data), "bytes": len(data)} for name, data in artifacts.items()},
                "paid_run_admitted": False}
    output.mkdir(parents=True, exist_ok=False)
    for name, data in artifacts.items():
        with (output / name).open("xb") as stream:
            stream.write(data)
    with (output / "manifest.json").open("xb") as stream:
        stream.write(canonical(manifest) + b"\n")
    print(json.dumps({"status": STATUS, "output": str(output), "qualified_rows": summary["qualified_rows"],
                      "manifest_sha256": digest(canonical(manifest) + b"\n"), "paid_run_admitted": False}), flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    finalize(args.root, args.output)


if __name__ == "__main__":
    main()
