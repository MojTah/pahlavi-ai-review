"""Prepare an exploratory paired-language DEV packet from the existing split.

Never repurpose TRAIN or TEST. This selects candidates, not certified gold.
Run once with the translator repository and a new output directory.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re

DATASET = "6f442563128d3a4c49dd5024af6882f6911b3f1b11eb5a2d4ef0d28a453acf0c"
WORKS = {"parsig:" + x for x in ("104", "110", "116", "130", "132")}


def read_rows(path):
    return [json.loads(x) for x in path.read_text("utf-8").splitlines()]


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", "utf-8")


def select(rows, seen):
    candidates = [r for r in rows if r["id"] not in seen and r["work_id"] not in WORKS
                  and r["alignment"] == "verified" and r["status"] == "reviewed"
                  and r.get("transcription", "").strip()
                  and all(r.get("translations", {}).get(l, {}).get("published")
                          and r["translations"][l].get("role") == "translation"
                          and r["translations"][l].get("credit", "").strip()
                          and r["translations"][l].get("text", "").strip() for l in ("en", "fa"))]
    selected = []
    for work in sorted({r["work_id"] for r in candidates}):
        values = sorted((r for r in candidates if r["work_id"] == work),
                        key=lambda r: (len(r["transcription"].encode()), r["id"]))
        # Six length strata, one deterministic seed-42 choice per nonempty stratum.
        bins = [[] for _ in range(min(6, len(values)))]
        for i, row in enumerate(values):
            bins[min(len(bins) - 1, i * len(bins) // len(values))].append(row)
        selected.extend(min(b, key=lambda r: sha256(("42|" + r["id"]).encode()).hexdigest()) for b in bins if b)
    return selected, candidates


def main(repo, output):
    dataset = repo / "runs/datasets" / DATASET
    manifest = json.loads((dataset / "manifest.json").read_text("utf-8"))
    for name, expected in manifest["files"].items():
        if sha256((dataset / name).read_bytes()).hexdigest() != expected:
            raise ValueError("Dataset checksum mismatch: " + name)
    train, dev = (read_rows(dataset / (s + "-records.jsonl")) for s in ("train", "dev"))
    if {r["work_id"] for r in train} & {r["work_id"] for r in dev}:
        raise ValueError("TRAIN/DEV work overlap")
    seen, scanned = set(), {}
    for path in sorted((repo / "runs").rglob("*")):
        if path.is_file() and path.suffix in {".json", ".jsonl"} and any(s in path.name.lower() for s in ("prediction", "comparison", "response")):
            data = path.read_bytes()
            seen.update(re.findall(r"parsig:\d{9}", data.decode("utf-8")))
            scanned[str(path.relative_to(repo))] = sha256(data).hexdigest()
    selected, candidates = select(dev, seen)
    if not selected:
        raise ValueError("No eligible unreported DEV candidates; do not borrow TRAIN/TEST")
    output.mkdir(parents=True, exist_ok=False)
    refs, inputs = [], []
    for i, row in enumerate(selected, 1):
        case_id = f"PALDEV1-{i:03}"
        refs.append({"id": case_id, "record_id": row["id"], "work_id": row["work_id"],
                     "text": row["transcription"], "translations": row["translations"],
                     "edition": row["edition"], "source_url": row["source_url"],
                     "source_sha256": row["source_sha256"], "notes": row["notes"],
                     "reference_screen": "pending", "expert_adjudicated": False})
        for language in ("en", "fa"):
            inputs.append({"id": case_id + ":pal>" + language, "record_id": row["id"],
                           "work_id": row["work_id"], "source_language": "pal", "target_language": language,
                           "text": row["transcription"]})
    for name, rows in (("references.jsonl", refs), ("inputs.jsonl", inputs)):
        (output / name).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), "utf-8")
    write(output / "audit.json", {
        "dataset_id": DATASET, "dataset_files": manifest["files"], "selection_script_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "train_work_overlap": [], "benchmark_work_overlap": [], "previous_prediction_files": scanned,
        "previously_reported_record_ids": sorted(seen), "eligible_unreported_trilingual_dev": len(candidates),
        "available_trilingual_dev_works": dict(Counter(r["work_id"] for r in dev if all(l in r["translations"] for l in ("en", "fa")))),
        "selected_work_counts": dict(Counter(r["work_id"] for r in selected)),
        "selection": "up to six per work; UTF-8 source-length strata; minimum SHA256(42|record_id) in each stratum",
        "passages": len(refs), "forward_cases": len(inputs), "requested_work_count": 5,
        "status": "EXPLORATORY_REFERENCE_SCREEN_PENDING", "expert_adjudicated": False,
        "checkpoint_selection_exposure": "Entire historical DEV was used for Qwen/ByT5 checkpoint loss; selected inputs are not pristine qualification data.",
        "limits": "Prediction filename scan is bounded evidence, not proof against unrecorded exposure. One-work outcomes cannot settle a general language winner.",
        "files": {n: sha256((output / n).read_bytes()).hexdigest() for n in ("references.jsonl", "inputs.jsonl")}})
    print(json.dumps({"output": str(output), "passages": len(refs), "cases": len(inputs),
                      "work_counts": dict(Counter(r["work_id"] for r in selected))}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    main(args.repo, args.output)
