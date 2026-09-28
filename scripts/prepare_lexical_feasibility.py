"""Reproduce a TRAIN-only review packet; never create accepted lexical labels."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/lexical-feasibility-20260927"
FILES = {
    "train": ("experiments/train-audit-20260927/qualified-v1/train.jsonl", "15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc"),
    "ledger": ("experiments/train-audit-20260927/qualified-v1/final-ledger.jsonl", "d79af2e64fbb92954c8b8d0ed9cb7a34e7e7d24d4c22ea9c22f1da6d569a8e77"),
    "drafts": ("dictionary/entries.json", "e962acaca1714e361a0ff06269816c19f21cd9a470033d9d68c2c462346f9074"),
    "inventory": ("experiments/dev-assisted-qualified-20260927/UNLABELED-DATA-INVENTORY.json", "7eba461256dfcf44e324dde31d2b119cac1b4fae866ca0a53e705217389ba060"),
}
# Existing draft attestations, not selection from evaluation predictions/answers.
CONTEXTS = {
    "mp-xrad-n": "parsig:107000001:pal>fa",
    "mp-frazand-n": "parsig:107000003:pal>fa",
    "mp-xwastag-n": "parsig:107000004:pal>fa",
    "mp-ruwan-n": "parsig:107000006:pal>fa",
    "mp-hunsandih-n": "parsig:119000002:pal>fa",
}
ELIGIBLE = {"ELIGIBLE", "ELIGIBLE_WITH_QUALIFICATIONS"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def validate(row, entry, heldout):
    require(row["id"] == entry["id"], "Identity mismatch")
    require(entry["disposition"] in ELIGIBLE, "Quarantined witness")
    require(row["work_id"] not in heldout, "Held-out work")
    require(sha(canonical(row)) == entry["row_sha256"], "TRAIN row changed")
    for field, ledger_field in (("text", "source"), ("target", "target")):
        require(row[field] == entry[ledger_field + "_text"], "Payload differs")
        require(sha(row[field].encode("utf-8")) == entry[ledger_field + "_sha256"], "Text hash differs")
    require(entry["expert_status"] == "NOT_EXPERT_ADJUDICATED", "Unexpected expert status")


def build():
    raw = {}
    for name, (path, expected) in FILES.items():
        raw[name] = (ROOT / path).read_bytes()
        require(sha(raw[name]) == expected, "Input hash changed: " + path)
    train = {r["id"]: r for r in map(json.loads, raw["train"].decode().splitlines())}
    ledger = {r["id"]: r for r in map(json.loads, raw["ledger"].decode().splitlines())}
    drafts = json.loads(raw["drafts"])
    heldout = set(json.loads(raw["inventory"])["heldout_work_ids"])
    require(len(train) == 2237 and len(ledger) == 2484, "Input membership changed")
    require(drafts["status"] == "draft_source_assisted_analysis", "Draft status changed")
    entries = {e["id"]: e for e in drafts["entries"]}
    singles = [r["id"] for r in train.values() if len(r["text"].split()) == 1]
    require(len(singles) == 9, "Single-item selection changed")
    selected = [(key, None) for key in singles] + [(value, key) for key, value in CONTEXTS.items()]
    records = []
    for index, (key, draft_id) in enumerate(selected, 1):
        r, entry = train[key], ledger[key]
        validate(r, entry, heldout)
        record = {
            "id": f"LEXFEAS1-{index:03d}",
            "purpose": "CONTEXTUAL_ANNOTATION_REVIEW" if draft_id else "EXISTING_TRAIN_RECALL_REVIEW",
            "training_admitted": False,
            "accepted_lexical_label": None,
            "accepted_grammar_label": None,
            "expert_adjudicated": False,
            "train_id": key, "record_id": r["record_id"], "work_id": r["work_id"],
            "source_text": r["text"], "parallel_translation_fa": r["target"],
            "provenance": {k: entry[k] for k in (
                "row_sha256", "source_sha256", "target_sha256", "edition", "credit", "revision",
                "raw_pointer", "raw_unit_sha256", "disposition", "split_status", "linguistic_review")},
            "draft_proposal": None,
        }
        if draft_id:
            draft = entries[draft_id]
            form = draft["headword"]
            starts = [m.start() for m in re.finditer(re.escape(form), r["text"])]
            require(len(starts) == 1, "Expected one exact contextual form")
            start = starts[0]
            record["source_span"] = {"start": start, "end": start + len(form), "text": form,
                                     "offset_unit": "Unicode code points, end exclusive"}
            record["draft_proposal"] = {
                "status": "CODEX_DRAFT_NOT_ACCEPTED_SUPERVISION",
                "id": draft_id,
                "origin": FILES["drafts"][0],
                "authorship": drafts["authorship"],
                **{k: draft[k] for k in ("headword", "part_of_speech", "sense_fa", "sense_en", "uncertainty")},
                "independent_lexical_support": None,
            }
        else:
            record["source_span"] = {"start": 0, "end": len(r["text"]), "text": r["text"],
                                     "offset_unit": "Unicode code points, end exclusive"}
            record["recall_group"] = unicodedata.normalize("NFC", r["text"]).casefold().rstrip(".")
        records.append(record)
    require(len({r["train_id"] for r in records}) == 14, "Duplicate selected TRAIN row")
    require("parsig:119000001:pal>fa" not in train, "Previously quarantined source was admitted")
    payload = b"".join(canonical(record) + b"\n" for record in records)
    audit = {
        "status": "FEASIBILITY_REVIEW_ONLY_NOT_TRAINING_OR_NEW_BENCHMARK",
        "selection": "All nine one-whitespace-item qualified TRAIN units, plus five existing TRAIN-only draft headwords in qualified cited contexts; no model outputs or benchmark answers read.",
        "records": len(records), "works": sorted({r["work_id"] for r in records}),
        "existing_single_item_rows": 9,
        "single_item_groups": len({r["recall_group"] for r in records if "recall_group" in r}),
        "contextual_draft_candidates": 5, "accepted_new_lexical_labels": 0,
        "accepted_new_grammar_labels": 0, "heldout_work_overlap": [],
        "excluded_annotation": {"occurrence_id": "119000001003", "train_id": "parsig:119000001:pal>fa",
                                "reason": "QUARANTINED source; occurrence-specific annotation cannot transfer to119000002."},
        "limits": ["Existing translation pairs are not new independent word-level gold.",
                   "Draft senses/POS are Codex analyses, not reviewed lexical labels.",
                   "Repeated frazaft units form one recall group; recall is not generalization.",
                   "Source/translation bytes unchanged; recall grouping alone uses NFC, casefold and final-period removal.",
                   "No new text, model inference, training admission or expert judgment."],
        "sources": {name: {"path": path, "sha256": digest, "bytes": len(raw[name])}
                    for name, (path, digest) in FILES.items()},
        "packet": {"sha256": sha(payload), "bytes": len(payload)},
    }
    return payload, canonical(audit) + b"\n", train, ledger, heldout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Regenerate in memory, compare frozen files, and check rejection paths.")
    args = parser.parse_args()
    payload, audit, train, ledger, heldout = build()
    artifacts = {"packet.jsonl": payload, "packet-audit.json": audit}
    if args.check:
        for name, data in artifacts.items():
            require((OUT / name).read_bytes() == data, "Frozen output changed: " + name)
        row = train[CONTEXTS["mp-xrad-n"]]
        entry = ledger[row["id"]]
        changed = copy.deepcopy(row)
        changed["text"] += " changed"
        quarantined = copy.deepcopy(entry)
        quarantined["disposition"] = "QUARANTINED"
        for a, b, c in ((changed, entry, heldout), (row, quarantined, heldout), (row, entry, heldout | {row["work_id"]})):
            try:
                validate(a, b, c)
            except ValueError:
                continue
            raise AssertionError("Invalid witness accepted")
        print("PASS: exact rebuild; changed-text, quarantine and held-out-work rejection")
    else:
        OUT.mkdir(parents=True, exist_ok=True)
        require(not any((OUT / name).exists() for name in artifacts), "Refusing to overwrite existing packet")
        for name, data in artifacts.items():
            with (OUT / name).open("xb") as handle:
                handle.write(data)
        print("Prepared14 TRAIN review records; zero new accepted lexical/grammar labels.")


if __name__ == "__main__":
    main()
