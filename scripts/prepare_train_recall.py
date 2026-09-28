"""Freeze source-only inputs for a seen-TRAIN recall diagnostic, never a benchmark."""
import argparse
import json

from prepare_lexical_feasibility import ROOT, FILES, canonical, require, sha, validate

OUT = ROOT / "experiments/train-recall-20260927"
PINS = {
    "experiments/grounded-supervision-20260927/qualification-decision.json": "e466aa2bc1b2129e802605ff60882b550b1517a6b2c9ffba84b1419a8bc8fdd6",
    "experiments/grounded-supervision-20260927/contrast-qualification.json": "ee7d06f3c3746c4dbe7c78c70ff5c9b5b8b68e10044563c68f9036292e68db68",
}


def build():
    raw = {}
    for name in ("train", "ledger", "inventory"):
        path, expected = FILES[name]
        raw[name] = (ROOT / path).read_bytes()
        require(sha(raw[name]) == expected, "Frozen input changed: " + path)
    train = {r["id"]: r for r in map(json.loads, raw["train"].decode().splitlines())}
    ledger = {r["id"]: r for r in map(json.loads, raw["ledger"].decode().splitlines())}
    heldout = set(json.loads(raw["inventory"])["heldout_work_ids"])
    annotations = {}
    for path, expected in PINS.items():
        data = (ROOT / path).read_bytes()
        require(sha(data) == expected, "Qualification decision changed")
        decision = json.loads(data)
        require(decision["expert_adjudicated"] is False and decision["training_admitted"] is False,
                "Qualification scope changed")
        for source, digest in decision["source_files_sha256"].items():
            require(sha((ROOT / source).read_bytes()) == digest, "Qualified source changed: " + source)
        for a in decision["accepted"]:
            annotations.setdefault(a["train_id"], []).append(a)
    require(len(annotations) == 20 and sum(map(len, annotations.values())) == 28, "Selection changed")
    inputs, references = [], []
    for index, key in enumerate(sorted(annotations), 1):
        row, entry = train[key], ledger[key]
        validate(row, entry, heldout)
        item = {"id": f"TRAINRECALL1-{index:03d}", "record_id": row["record_id"],
                "work_id": row["work_id"], "source_language": "pal", "target_language": "fa",
                "source_text": row["text"]}
        inputs.append(item)
        references.append({**item, "train_id": key, "reference_fa": row["target"],
                           "qualified_train_ledger": entry, "reviewed_annotation_scopes": annotations[key],
                           "expert_adjudicated": False, "use": "LOCAL_TRAIN_RECALL_DIAGNOSIS_ONLY"})
    require(len({r["source_text"] for r in inputs}) == 20, "Duplicate source")
    return inputs, references


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    inputs, references = build()
    payloads = {"inputs.jsonl": b"".join(canonical(r) + b"\n" for r in inputs),
                "references.local.jsonl": b"".join(canonical(r) + b"\n" for r in references)}
    audit = {"purpose": "SEEN_TRAIN_RECALL_NOT_GENERALIZATION_OR_STANDARD_BENCHMARK",
             "selection": "Sorted union of parents of all28 independently qualified auxiliary annotations",
             "input_sha256": sha(payloads["inputs.jsonl"]),
             "local_reference_sha256": sha(payloads["references.local.jsonl"]),
             "qualification_inputs": PINS, "qualified_train_sha256": FILES["train"][1],
             "count": len(inputs), "works": len({r["work_id"] for r in inputs}),
             "heldout_overlap": 0, "expert_adjudicated": False, "new_model_predictions_used": False,
             "input_fields": sorted(inputs[0]), "cloud_upload_allowed_files": ["inputs.jsonl"]}
    payloads["selection.json"] = canonical(audit) + b"\n"
    if not args.check:
        OUT.mkdir(parents=True, exist_ok=True)
    for name, data in payloads.items():
        path = OUT / name
        if args.check:
            require(path.read_bytes() == data, "Saved artifact differs: " + name)
        else:
            require(not path.exists() or path.read_bytes() == data, "Refusing changed artifact overwrite")
            path.write_bytes(data)
    require(all(set(r) == set(audit["input_fields"]) for r in inputs), "Input schema differs")
    require(not ({"target", "reference_fa", "reviewed_annotation_scopes"} & set(audit["input_fields"])),
            "Reference leaked into inference input")
    print(json.dumps(audit, ensure_ascii=False))


if __name__ == "__main__":
    main()
