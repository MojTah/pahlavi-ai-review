"""Validate frozen blind reviews and call the unchanged PAL-REF scorer four times."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloud_pilot.score_palref_fa import score

PAIR = ROOT / "experiments/palref-paired-20260927"
CONDITIONS = {"previous": ROOT / "experiments/palref-v1/trained-20260927",
              "candidate": ROOT / "experiments/palref-v1/qualified-20260927"}
FIELDS = {"id", "output_sha256", "judgment", "meaning_checks", "categories", "reason", "output_span"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    return [json.loads(line) for line in path.read_text("utf-8").splitlines() if line.strip()]


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def validate_blind(packet, reviews):
    by_id = {p["id"]: p for p in packet}
    require(len(by_id) == len(packet), "duplicate packet ID")
    require(len({r["id"] for r in reviews}) == len(reviews) == len(packet), "review coverage/duplicates")
    require({r["id"] for r in reviews} == set(by_id), "review ID mismatch")
    for review in reviews:
        p = by_id[review["id"]]
        require(set(review) == FIELDS, "review schema")
        require(review["output_sha256"] == p["output_sha256"] == hashlib.sha256(p["text"].encode()).hexdigest(), "output identity")
        span = review["output_span"]
        require(isinstance(span, str), "span must be text")
        require(not span or span in p["text"], "span is not exact output substring")
        if p["status"] == "success" and review["judgment"] != "accepted":
            require(bool(span.strip()), "adverse span missing")
    # The unchanged scorer below validates category/check/judgment consistency.


def check():
    text = "actual output"
    p = {"id": "one", "text": text, "status": "success", "output_sha256": hashlib.sha256(text.encode()).hexdigest()}
    r = {"id": "one", "output_sha256": p["output_sha256"], "judgment": "meaning_error",
         "meaning_checks": ["fail", "pass"], "categories": {}, "reason": "synthetic", "output_span": "actual"}
    validate_blind([p], [r])
    for reviews in ([r, r], [], [{**r, "output_span": "invented"}], [{**r, "output_sha256": "wrong"}], [{**r, "status": "success"}]):
        try:
            validate_blind([p], reviews)
        except ValueError:
            continue
        raise AssertionError("Invalid blind evidence accepted")
    print("PASS: exact review identity, coverage, schema and adverse-span checks")


def main():
    provenance = json.loads((PAIR / "lead-only/provenance.json").read_text("utf-8"))
    for name, expected in provenance["packet_files"].items():
        require(sha(PAIR / name) == expected, "packet changed: " + name)
    mapping = rows(PAIR / "lead-only/mapping.jsonl")
    require(len(mapping) == len({r["id"] for r in mapping}) == 160, "mapping coverage")
    blind = {}
    frozen = {}
    for reviewer in ("A", "B"):
        path = PAIR / ("reviewer-" + reviewer) / "reviews.jsonl"
        packet = rows(path.with_name("packet.jsonl"))
        require(len(packet) == 80, "packet coverage")
        blind[reviewer] = rows(path)
        validate_blind(packet, blind[reviewer])
        frozen[reviewer] = {"sha256": sha(path), "rows": len(blind[reviewer])}
    for condition, source in CONDITIONS.items():
        for filename in ("run.json", "predictions.jsonl"):
            require(sha(source / filename) == provenance["conditions"][condition][filename.split('.')[0] + "_sha256"], "raw condition changed")
    out = PAIR / "scored"
    out.mkdir(exist_ok=False)
    write(out / "blind-review-freeze.json", frozen)
    scores, decoded = {}, {}
    for reviewer, reviews in blind.items():
        index = {m["id"]: m for m in mapping if m["reviewer"] == reviewer}
        require(set(index) == {r["id"] for r in reviews}, "mapping/review mismatch")
        scores[reviewer], decoded[reviewer] = {}, {}
        for condition, source in CONDITIONS.items():
            directory = out / reviewer / condition
            directory.mkdir(parents=True)
            selected = []
            for r in reviews:
                m = index[r["id"]]
                require(m["output_sha256"] == r["output_sha256"], "mapping output mismatch")
                if m["condition"] == condition:
                    selected.append({**r, "id": m["prediction_id"]})
            require(len(selected) == 40, "condition coverage")
            run = json.loads((source / "run.json").read_text("utf-8"))
            run.update(reviewer_id="/root/blind_pair_" + reviewer.lower(), reviewer_type="ai", review_status="provisional_single_review")
            write(directory / "run.json", run)
            (directory / "predictions.jsonl").write_bytes((source / "predictions.jsonl").read_bytes())
            (directory / "reviews.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in selected), encoding="utf-8", newline="\n")
            scores[reviewer][condition] = score(directory)
            decoded[reviewer][condition] = {r["id"]: r for r in selected}
            write(directory / "score.json", scores[reviewer][condition])
    paired = {}
    for reviewer, conditions in decoded.items():
        old, new = conditions["previous"], conditions["candidate"]
        cases = [{"id": cid, "previous": old[cid]["judgment"], "candidate": new[cid]["judgment"]} for cid in sorted(old)]
        previous, candidate = [scores[reviewer][c]["directions"]["pal>fa"] for c in CONDITIONS]
        paired[reviewer] = {"previous": previous, "candidate": candidate,
            "accepted_change_percentage_points": candidate["accepted_percent"] - previous["accepted_percent"],
            "critical_error_change_percentage_points": candidate["critical_error_percent"] - previous["critical_error_percent"],
            "newly_accepted": [c["id"] for c in cases if c["previous"] != "accepted" and c["candidate"] == "accepted"],
            "lost_acceptance": [c["id"] for c in cases if c["previous"] == "accepted" and c["candidate"] != "accepted"],
            "transitions": dict(Counter(c["previous"] + " -> " + c["candidate"] for c in cases)), "cases": cases}
    agreement = {}
    for condition in CONDITIONS:
        a, b = decoded["A"][condition], decoded["B"][condition]
        disagreement = [{"id": cid, "A": a[cid]["judgment"], "B": b[cid]["judgment"]} for cid in sorted(a) if a[cid]["judgment"] != b[cid]["judgment"]]
        agreement[condition] = {"total": 40, "exact_judgment_agreement": 40-len(disagreement),
            "acceptance_agreement": sum((a[c]["judgment"] == "accepted") == (b[c]["judgment"] == "accepted") for c in a), "disagreements": disagreement}
    summary = {"status": "four unchanged provisional scorings complete", "expert_adjudicated": False,
               "blind_review_hashes": frozen, "paired": paired, "reviewer_agreement": agreement}
    write(out / "comparison.json", summary)
    for reviewer, value in paired.items():
        print(reviewer, json.dumps({k: v for k, v in value.items() if k not in {"cases", "transitions"}}))
    print("Reviewer agreement:", json.dumps(agreement))


if __name__ == "__main__":
    check() if sys.argv[1:] == ["--check"] else main()
