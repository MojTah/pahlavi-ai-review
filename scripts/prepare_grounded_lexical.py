"""Bind five observed publisher annotations to unchanged qualified TRAIN contexts."""
import argparse
import copy
import json
import re

from prepare_lexical_feasibility import ROOT, FILES, CONTEXTS, canonical, require, sha, validate

OUT = ROOT / "experiments/grounded-supervision-20260927"
OBSERVED_SHA = "dcd0c41b66cc17623426b0d49da7cbad6a9efa576479bdaf4afd244eacc93301"


def bind(observed, row, entry, heldout):
    validate(row, entry, heldout)
    require(observed["occurrence_id"][:-3] == row["record_id"].split(":", 1)[1], "Wrong parent")
    # The UI inserts highlight spacing; normalize only for context comparison.
    for display, original, citation in (
        (observed["displayed_source"], row["text"], entry["edition"]),
        (observed["displayed_translation"], row["target"], row["credit"]),
    ):
        require(display.endswith(citation), "Different citation")
        require(" ".join(display[:-len(citation)].split()) == " ".join(original.split()), "Different context")
    form = observed["transcription"]
    spans = list(re.finditer(r"(?<!\w)" + re.escape(form) + r"(?!\w)", row["text"]))
    require(len(spans) == 1, "Ambiguous or absent exact form")
    require(observed["category"] == "اسم" and bool(observed["translation1"].strip()), "Incomplete annotation")
    span = spans[0]
    return {
        "id": "GROUNDEDLEX1-" + observed["occurrence_id"],
        "train_id": row["id"], "work_id": row["work_id"],
        "source_text": row["text"], "parallel_translation_fa": row["target"],
        "source_span": {"start": span.start(), "end": span.end(), "text": span.group(),
                        "offset_unit": "Unicode code points, end exclusive"},
        "published_annotation": observed,
        "publisher_capture_sha256": OBSERVED_SHA,
        "qualified_train_ledger": entry,
        "candidate_task": "Contextual lexical gloss using the published translation1 verbatim",
        "qualification": "Occurrence-specific publisher evidence; no exhaustive dictionary sense, lemma, full-clause or expert-certification claim",
        "expert_adjudicated": False,
        "training_admitted": False,
        "review_status": "PENDING_INDEPENDENT_REVIEW",
    }


def build():
    raw = {}
    for key in ("train", "ledger", "inventory"):
        path, expected = FILES[key]
        raw[key] = (ROOT / path).read_bytes()
        require(sha(raw[key]) == expected, "Changed frozen input: " + path)
    train = {r["id"]: r for r in map(json.loads, raw["train"].decode().splitlines())}
    ledger = {r["id"]: r for r in map(json.loads, raw["ledger"].decode().splitlines())}
    heldout = set(json.loads(raw["inventory"])["heldout_work_ids"])
    observed_raw = (OUT / "published-occurrences.json").read_bytes()
    require(sha(observed_raw) == OBSERVED_SHA, "Publisher capture changed")
    observations = json.loads(observed_raw)["entries"]
    ids = ["parsig:" + r["occurrence_id"][:-3] + ":pal>fa" for r in observations]
    require(len(ids) == 5 and set(ids) == set(CONTEXTS.values()), "Unexpected occurrence selection")
    records = [bind(o, train[key], ledger[key], heldout) for o, key in zip(observations, ids)]
    return records, train, ledger, heldout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify saved packet without writing")
    args = parser.parse_args()
    records, train, ledger, heldout = build()
    first = records[0]
    for field, value in (("displayed_source", "wrong context"), ("occurrence_id", "119000001003"),
                         ("transcription", "absent_form"), ("displayed_translation", "wrong translation")):
        bad = copy.deepcopy(first["published_annotation"])
        bad[field] = value
        try:
            bind(bad, train[first["train_id"]], ledger[first["train_id"]], heldout)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid observation accepted: " + field)
    payload = b"".join(canonical(r) + b"\n" for r in records)
    dest = OUT / "lexical-packet.jsonl"
    if args.check:
        require(dest.read_bytes() == payload, "Saved packet does not reproduce")
    else:
        require(not dest.exists() or dest.read_bytes() == payload, "Refusing to overwrite different evidence")
        dest.write_bytes(payload)
    print(json.dumps({"records": len(records), "works": len({r['work_id'] for r in records}),
                      "sha256": sha(payload), "negative_checks": 4, "training_admitted": 0}))


if __name__ == "__main__":
    main()
