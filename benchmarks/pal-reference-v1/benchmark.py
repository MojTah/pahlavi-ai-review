"""Integrity and judgment aggregation only: no inference and no automatic semantic judge."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
LANGS = {"pal": "Middle Persian (Pahlavi), scholarly Latin transcription", "en": "English", "fa": "Persian (Farsi)"}
PROMPT = "Translate the supplied text from {source_language} into {target_language}. Preserve its meaning, participants, negation, names, quantities, and uncertainty. Do not add explanations, citations, or facts. Return only the translation. For Middle Persian output, use scholarly Latin transcription. If you cannot translate it, return exactly [UNRESOLVED]."
DIRECTIONS = ("pal>en", "pal>fa", "en>pal", "fa>pal")
JUDGMENTS = {"accepted", "meaning_error", "critical_error", "uncertain"}
OUTCOMES = {"success", "abstain", "timeout", "error"}
CATEGORIES = ("lexical_meaning", "grammatical_roles", "negation_modality", "names", "numbers_quantities", "omissions", "unsupported_additions", "source_uncertainty")

def digest(data):
    return hashlib.sha256(data).hexdigest()

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def read_lines(path):
    return [json.loads(s) for s in path.read_text(encoding="utf-8").splitlines() if s.strip()]

def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def write_lines(path, values):
    path.write_text("".join(json.dumps(v, ensure_ascii=False) + "\n" for v in values), encoding="utf-8")

def require(condition, message):
    if not condition:
        raise ValueError(message)

def unique(rows, name):
    require(all(isinstance(r, dict) and isinstance(r.get("id"), str) for r in rows), name + ": invalid rows")
    mapped = {r["id"]: r for r in rows}
    require(len(mapped) == len(rows), name + ": duplicate IDs")
    return mapped

def verify():
    manifest_path = ROOT / "manifest.json"
    frozen = (ROOT.parent / (ROOT.name + ".sha256")).read_text("utf-8").strip()
    require(digest(manifest_path.read_bytes()) == frozen, "Frozen manifest changed")
    manifest = read_json(manifest_path)
    require(manifest["benchmark_id"] == "pal-reference-v1", "Wrong benchmark")
    for name, expected in manifest["files"].items():
        path = (ROOT / name).resolve()
        require(path.is_relative_to(ROOT), "Invalid manifest path")
        require(path.is_file() and digest(path.read_bytes()) == expected, "Frozen artifact changed: " + name)
    items = unique(read_lines(ROOT / "references.jsonl"), "references")
    cases = unique(read_lines(ROOT / "inputs.jsonl"), "inputs")
    require(len(items) == 40 and len(cases) == 160, "Incorrect benchmark counts")
    require(len({r for item in items.values() for r in item["record_ids"]}) == 42, "Incorrect source record count")
    require(len({item["work_id"] for item in items.values()}) == 5, "Incorrect work count")
    require(all(len(item["meaning_checks"]) == 2 for item in items.values()), "Incorrect meaning checklist")
    require(Counter(i["source_language"] + ">" + i["target_language"] for i in cases.values()) == Counter({d: 40 for d in DIRECTIONS}), "Directional coverage changed")
    require({(c["passage_id"], c["source_language"] + ">" + c["target_language"]) for c in cases.values()} == {(pid, d) for pid in items for d in DIRECTIONS}, "Missing passage/direction combination")
    for case in cases.values():
        item = items[case["passage_id"]]
        require(case["source_text"] == item["texts"][case["source_language"]], "Input/reference mismatch")
        require(case["work_id"] == item["work_id"], "Input/work mismatch")
    return frozen, cases

def templates(directory, frozen, cases):
    directory.mkdir(parents=True, exist_ok=False)
    write_json(directory / "run.json", {"benchmark_id": "pal-reference-v1", "benchmark_manifest_sha256": frozen, "model_id": "", "model_revision": "", "adapter_sha256_or_none": "", "runtime": "", "decoding": "greedy", "seed": 42, "max_new_tokens": 4096, "max_generation_seconds": 1200, "retrieval": "none", "reviewer_id": "", "reviewer_type": "unassigned", "review_status": "provisional_single_review", "fresh_context_each_case": True, "system_prompt": PROMPT})
    write_lines(directory / "predictions.jsonl", ({"id": c["id"], "input_sha256": digest(c["source_text"].encode("utf-8")), "status": "unrun", "text": "", "elapsed_seconds": None} for c in cases.values()))
    write_lines(directory / "reviews.jsonl", ({"id": c["id"], "output_sha256": "", "judgment": "unreviewed", "meaning_checks": ["unreviewed", "unreviewed"], "categories": {k: "unreviewed" for k in CATEGORIES}, "reason": "", "output_span": ""} for c in cases.values()))
    return {"status": "templates_created", "cases": len(cases), "directory": str(directory)}

def score(directory, frozen, cases):
    run = read_json(directory / "run.json")
    require(run["benchmark_manifest_sha256"] == frozen and run["benchmark_id"] == "pal-reference-v1", "Wrong run/benchmark identity")
    for key in ("model_id", "model_revision", "adapter_sha256_or_none", "runtime", "reviewer_id"):
        require(isinstance(run.get(key), str) and run[key].strip(), "Missing " + key)
    for key, value in {"decoding": "greedy", "seed": 42, "max_new_tokens": 4096, "max_generation_seconds": 1200, "retrieval": "none", "fresh_context_each_case": True, "system_prompt": PROMPT}.items():
        require(run.get(key) == value, "Not the standard v1 condition: " + key)
    require(run.get("reviewer_type") in {"ai", "human_specialist", "human_other"}, "Declare actual reviewer type")
    require(run.get("review_status") == "provisional_single_review", "This aggregator supports provisional single-review reports only")
    predictions = unique(read_lines(directory / "predictions.jsonl"), "predictions")
    reviews = unique(read_lines(directory / "reviews.jsonl"), "reviews")
    require(predictions.keys() == cases.keys() == reviews.keys(), "Missing or extra case IDs")
    counts, works = defaultdict(Counter), defaultdict(lambda: defaultdict(Counter))
    for cid, case in cases.items():
        pred, review = predictions[cid], reviews[cid]
        require(pred["input_sha256"] == digest(case["source_text"].encode("utf-8")), cid + ": input changed")
        status, text = pred.get("status"), pred.get("text")
        require(status in OUTCOMES and isinstance(text, str), cid + ": invalid/unrun prediction")
        elapsed = pred.get("elapsed_seconds")
        require(type(elapsed) in (int, float) and 0 <= elapsed < float("inf"), cid + ": invalid elapsed time")
        require(status != "success" or (bool(text.strip()) and text.strip() != "[UNRESOLVED]" and elapsed <= 1200), cid + ": invalid success")
        require(review["output_sha256"] == digest(text.encode("utf-8")), cid + ": review does not bind this output")
        direction = case["source_language"] + ">" + case["target_language"]
        if status == "success":
            judgment = review.get("judgment")
            require(judgment in JUDGMENTS, cid + ": meaning review missing")
            categories = review.get("categories", {})
            require(set(categories) == set(CATEGORIES) and all(v in {"pass", "fail", "uncertain", "not_applicable"} for v in categories.values()), cid + ": incomplete categories")
            checks = review.get("meaning_checks", [])
            require(len(checks) == 2 and all(v in {"pass", "fail", "uncertain"} for v in checks), cid + ": incomplete case-specific meaning checks")
            require(bool(review.get("reason", "").strip()), cid + ": review rationale missing")
            require(judgment != "accepted" or all(v in {"pass", "not_applicable"} for v in categories.values()), cid + ": accepted despite failed/uncertain category")
            require(judgment != "accepted" or (checks == ["pass", "pass"] and all(categories[k] == "pass" for k in ("lexical_meaning", "omissions", "unsupported_additions", "source_uncertainty"))), cid + ": accepted without positive meaning assessment")
            require(judgment not in {"meaning_error", "critical_error"} or "fail" in checks + list(categories.values()), cid + ": error judgment without identified failed check")
            require(judgment != "uncertain" or "uncertain" in checks + list(categories.values()), cid + ": uncertain judgment without identified uncertainty")
            require(judgment == "accepted" or bool(review.get("output_span", "").strip()), cid + ": adverse review needs output span")
        else:
            judgment = status
            require(review.get("judgment") == "not_assessable", cid + ": failed/abstained output must not receive a meaning pass")
        for counter in (counts[direction], works[direction][case["work_id"]]):
            counter["total"] += 1
            counter["complete_outputs"] += status == "success"
            counter[judgment] += 1
    def report(c):
        return {**{k: c[k] for k in ("total", "complete_outputs", "accepted", "meaning_error", "critical_error", "uncertain", "abstain", "timeout", "error")}, "accepted_percent": 100*c["accepted"]/c["total"], "critical_error_percent": 100*c["critical_error"]/c["total"], "complete_output_percent": 100*c["complete_outputs"]/c["total"]}
    return {"benchmark_manifest_sha256": frozen, "assessment": "provisional recorded judgments; not automatic semantic validation or model qualification", "reviewer_type": run["reviewer_type"], "reviewer_id": run["reviewer_id"], "model_id": run["model_id"], "model_revision": run["model_revision"], "artifact_hashes": {n: digest((directory/n).read_bytes()) for n in ("run.json", "predictions.jsonl", "reviews.jsonl")}, "directions": {d: report(counts[d]) for d in DIRECTIONS}, "by_work": {d: {w: report(c) for w, c in works[d].items()} for d in DIRECTIONS}}

def audit_training(path):
    policy = read_json(ROOT / "holdout-policy.json")
    banned_works, banned_records = set(policy["excluded_work_ids_canonical"]), set(policy["record_ids"])
    rows = read_lines(path)
    require(all(r.get("work_id") and (r.get("record_id") or r.get("id")) for r in rows), "Missing work/record identity; cannot audit")
    hits = [r.get("record_id", r.get("id")) for r in rows if r["work_id"] in banned_works or r.get("record_id", r.get("id")) in banned_records]
    require(not hits, "Benchmark holdout appears in training: " + str(hits[:5]))
    return {"status": "ID/work isolation passed", "rows": len(rows), "limit": "Does not detect unnamed witnesses, paraphrases or foundation pretraining exposure"}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("verify", "templates", "score", "audit-training"))
    parser.add_argument("path", nargs="?", type=Path)
    args = parser.parse_args()
    frozen, cases = verify()
    if args.command == "verify":
        result = {"status": "PASS", "benchmark": "pal-reference-v1", "passages": 40, "cases": 160, "manifest_sha256": frozen, "expert_adjudicated": False}
    else:
        require(args.path is not None, "Output directory/data file required")
        require(not args.path.resolve().is_relative_to(ROOT), "Results cannot be written inside the frozen benchmark")
        result = templates(args.path, frozen, cases) if args.command == "templates" else score(args.path, frozen, cases) if args.command == "score" else audit_training(args.path)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, TypeError, json.JSONDecodeError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        sys.exit(1)
