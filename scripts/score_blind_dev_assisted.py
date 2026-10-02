"""Validate two frozen DEV96 reviews and summarize each separately; no semantic judge."""
import argparse
from collections import Counter
import json
from pathlib import Path

try:
    from scripts import prepare_blind_dev_assisted as prep
except ImportError:
    import prepare_blind_dev_assisted as prep

FIELDS = {"review_id", "output_sha256", "judgment", "categories", "supported_span_severity", "unknown_span_handling", "reason", "output_span"}
JUDGMENTS = {"accepted", "meaning_error", "critical_error", "uncertain"}
SEVERITIES = {"none", "meaning_error", "critical_error", "uncertain"}
HANDLING = {"appropriately_uncertain", "overconfident", "uncertain", "no_unknown_span"}
PAIRS = (("gemma280_plain", "gemma280_assisted"), ("qwen36_27b_plain", "qwen36_27b_assisted"),
         ("gemma280_plain", "qwen36_27b_plain"), ("gemma280_assisted", "qwen36_27b_assisted"))
require = prep.require


def validate_reviews(packet, reviews, expected_count=96):
    packets, ratings = prep.unique(packet, "review_id"), prep.unique(reviews, "review_id")
    require(len(packet) == len(reviews) == expected_count and packets.keys() == ratings.keys(), "Review coverage differs")
    for rid, review in ratings.items():
        row = packets[rid]
        require(set(row) == prep.PACKET_FIELDS and set(review) == FIELDS, "Packet/review schema differs")
        require(review["output_sha256"] == row["output_sha256"] == prep.sha(row["output_text"].encode("utf-8")), "Review output hash differs")
        cats, judgment = review["categories"], review["judgment"]
        require(isinstance(cats, dict) and set(cats) == set(prep.CATEGORIES)
                and all(v in {"pass", "fail", "uncertain", "not_applicable"} for v in cats.values()), "Invalid meaning categories")
        require(review["supported_span_severity"] in SEVERITIES and review["unknown_span_handling"] in HANDLING, "Invalid constrained findings")
        require(isinstance(review["reason"], str) and bool(review["reason"].strip()), "Missing review rationale")
        span = review["output_span"]
        require(isinstance(span, str) and (not span or span in row["output_text"]), "Output span is not an exact substring")
        if row["execution_status"] != "success":
            require(row["execution_status"] in {"abstain", "timeout", "error", "unattempted"}, "Unknown execution outcome")
            require(judgment == "not_assessable" and all(v in {"uncertain", "not_applicable"} for v in cats.values())
                    and review["supported_span_severity"] == review["unknown_span_handling"] == "uncertain", "Execution failure received a meaning judgment")
        elif row["assessment"] == "provisional_whole_translation":
            require(judgment in JUDGMENTS, "Whole judgment missing")
            require(review["supported_span_severity"] != "critical_error" or judgment == "critical_error",
                    "Supported critical error contradicts whole judgment; obtain corrected review")
            if judgment == "accepted":
                require(all(v in {"pass", "not_applicable"} for v in cats.values())
                        and all(cats[k] == "pass" for k in ("lexical_meaning", "omissions", "unsupported_additions", "source_uncertainty"))
                        and review["supported_span_severity"] == "none" and review["unknown_span_handling"] != "overconfident", "Acceptance lacks positive meaning assessment")
            else:
                require(bool(span.strip()), "Adverse whole judgment needs an exact output span")
                require(("uncertain" if judgment == "uncertain" else "fail") in cats.values(), "Judgment/category inconsistency")
        else:
            require(row["assessment"] == "constrained_meanings_only" and judgment == "constrained_only", "Constrained case received whole acceptance")
            severity = review["supported_span_severity"]
            if severity != "none":
                require(("uncertain" if severity == "uncertain" else "fail") in cats.values(), "Supported severity/category inconsistency")
            if severity != "none" or review["unknown_span_handling"] == "overconfident":
                require(bool(span.strip()), "Constrained adverse finding needs an exact output span")
            if review["unknown_span_handling"] == "overconfident":
                require(cats["source_uncertainty"] == "fail", "Overconfidence must identify failed uncertainty handling")
    return ratings


def outcome(item):
    return item["judgment"] if item["execution_status"] == "success" else item["execution_status"]


def condition_report(items):
    whole = [x for x in items if x["assessment"] == "provisional_whole_translation"]
    constrained = [x for x in items if x["assessment"] == "constrained_meanings_only"]
    counts = Counter(outcome(x) for x in whole)
    labels = ("accepted", "meaning_error", "critical_error", "uncertain", "abstain", "timeout", "error", "unattempted")
    result = {"total_cases": len(items), "execution_counts": dict(Counter(x["execution_status"] for x in items)),
        "whole_denominator": len(whole), "whole_counts": {label: counts[label] for label in labels},
        "accepted_percent": 100 * counts["accepted"] / len(whole),
        "critical_error_percent": 100 * counts["critical_error"] / len(whole),
        "constrained_denominator": len(constrained),
        "constrained_severity": dict(Counter(x["supported_span_severity"] for x in constrained if x["execution_status"] == "success")),
        "constrained_execution": dict(Counter(x["execution_status"] for x in constrained)),
        "constrained_overconfidence": sum(x["execution_status"] == "success" and x["unknown_span_handling"] == "overconfident" for x in constrained),
        "failed_categories_whole": dict(Counter(k for x in whole if x["execution_status"] == "success" for k, value in x["categories"].items() if value == "fail"))}
    return result


def comparison_completion(loaded, rows):
    """Screen admission requires both validated full runs, not just a complete pair."""
    expected = [row["id"] + ":" + arm for row, arm in prep.shared.schedule(rows)]
    families = {}
    for family in prep.RUNNERS:
        if family not in loaded:
            families[family] = {"complete": False, "reason": "missing family run"}
            continue
        run, predictions, _ = loaded[family]
        checks = {"terminal_completed": run.get("status") == "completed",
            "48_completed_outputs": run.get("completed_outputs") == 48,
            "48_attempted_outputs": run.get("attempted_outputs") == 48,
            "full_fixed_schedule": run.get("schedule") == expected and [p["id"] for p in predictions] == expected,
            "success_or_abstain_first_attempts": len(predictions) == 48
                and all(p.get("status") in {"success", "abstain"} and p.get("sequence") == i
                        for i, p in enumerate(predictions, 1))}
        families[family] = {"complete": all(checks.values()), "declared_status": run.get("status"),
            "completed_outputs": run.get("completed_outputs"), "checks": checks}
    return {"complete": set(loaded) == set(prep.RUNNERS) and all(value["complete"] for value in families.values()),
            "families": families}


def paired_report(old, new, screen, comparison_complete):
    require(old.keys() == new.keys() and len(old) == 24, "Paired case coverage differs")
    cases = [{"case_id": cid, "work_id": old[cid]["work_id"], "assessment": old[cid]["assessment"],
              "previous": outcome(old[cid]), "candidate": outcome(new[cid]),
              "previous_severity": old[cid]["supported_span_severity"], "candidate_severity": new[cid]["supported_span_severity"],
              "previous_unknown_handling": old[cid]["unknown_span_handling"], "candidate_unknown_handling": new[cid]["unknown_span_handling"]}
             for cid in sorted(old)]
    whole = [x for x in cases if x["assessment"] == "provisional_whole_translation"]
    constrained = [x for x in cases if x["assessment"] == "constrained_meanings_only"]
    gained = [x["case_id"] for x in whole if x["previous"] != "accepted" and x["candidate"] == "accepted"]
    lost = [x["case_id"] for x in whole if x["previous"] == "accepted" and x["candidate"] != "accepted"]
    critical_change = sum(x["candidate"] == "critical_error" for x in whole) - sum(x["previous"] == "critical_error" for x in whole)
    accepted_to_critical = [x["case_id"] for x in whole if x["previous"] == "accepted" and x["candidate"] == "critical_error"]
    work_net = {work: sum((x["candidate"] == "accepted") - (x["previous"] == "accepted") for x in whole if x["work_id"] == work)
                for work in sorted({x["work_id"] for x in whole})}
    works_with_gains = sorted({x["work_id"] for x in whole if x["case_id"] in gained})
    constrained_critical_change = sum(x["candidate"] == "constrained_only" and x["candidate_severity"] == "critical_error" for x in constrained) - sum(x["previous"] == "constrained_only" and x["previous_severity"] == "critical_error" for x in constrained)
    new_overconfidence = [x["case_id"] for x in constrained if x["candidate"] == "constrained_only" and x["candidate_unknown_handling"] == "overconfident"
                          and not (x["previous"] == "constrained_only" and x["previous_unknown_handling"] == "overconfident")]
    checks = {"full_four_condition_comparison_complete": comparison_complete,
        "all_pair_outputs_attempted": all(x["previous"] != "unattempted" and x["candidate"] != "unattempted" for x in cases),
        "net_accepted_gain": len(gained) - len(lost) >= screen["both_reviewers_min_net_accepted_gain"],
        "gains_in_multiple_works": len(works_with_gains) >= screen["min_works_with_gains"],
        "no_whole_critical_increase": critical_change <= 0, "no_accepted_to_critical": not accepted_to_critical,
        "no_constrained_critical_increase": constrained_critical_change <= 0, "no_new_overconfidence": not new_overconfidence}
    return {"newly_accepted": gained, "lost_acceptance": lost, "net_accepted_change": len(gained) - len(lost),
        "critical_count_change": critical_change, "accepted_to_critical": accepted_to_critical,
        "work_net_accepted_changes": work_net, "works_with_newly_accepted": works_with_gains,
        "constrained_critical_count_change": constrained_critical_change,
        "new_constrained_overconfidence": new_overconfidence,
        "whole_transitions": dict(Counter(x["previous"] + " -> " + x["candidate"] for x in whole)),
        "constrained_severity_transitions": dict(Counter(x["previous"] + ":" + x["previous_severity"] + " -> " + x["candidate"] + ":" + x["candidate_severity"] for x in constrained)),
        "cases": cases, "screen_checks": checks,
        "screen_pass": all(checks.values()) if comparison_complete else None,
        "screen_status": ("pass" if all(checks.values()) else "fail") if comparison_complete else "inconclusive"}


def summarize(mapping, packets, reviews, contract, completion=None):
    completion = completion or {"complete": False, "reason": "actual run completion evidence not supplied"}
    comparison_complete = completion.get("complete") is True
    require(len(mapping) == 192 and len(prep.unique(mapping, "review_id")) == 192, "Mapping coverage differs")
    decoded, summaries = {}, {}
    for reviewer in ("A", "B"):
        ratings = validate_reviews(packets[reviewer], reviews[reviewer])
        selected = [m for m in mapping if m["reviewer"] == reviewer]
        require({m["review_id"] for m in selected} == set(ratings), "Mapping/review identity differs")
        by_packet = prep.unique(packets[reviewer], "review_id")
        decoded[reviewer] = {condition: {} for condition in prep.CONDITIONS}
        for item in selected:
            packet, rating = by_packet[item["review_id"]], ratings[item["review_id"]]
            require(item["output_sha256"] == packet["output_sha256"] and item["source_sha256"] == prep.sha(packet["source_text"].encode("utf-8"))
                    and item["assessment"] == packet["assessment"] and item["execution_status"] == packet["execution_status"], "Private mapping differs")
            target = decoded[reviewer][item["condition"]]
            require(item["case_id"] not in target, "Duplicate mapped case/condition")
            target[item["case_id"]] = {**rating, **item}
        conditions = {}
        for condition, records in decoded[reviewer].items():
            require(len(records) == 24, "Condition coverage differs")
            report = condition_report(list(records.values()))
            require((report["whole_denominator"], report["constrained_denominator"]) == (15, 9), "Fixed denominators differ")
            report["by_work"] = {work: condition_report([r for r in records.values() if r["work_id"] == work]) for work in sorted({r["work_id"] for r in records.values()})}
            conditions[condition] = report
        pairs = {old + " -> " + new: paired_report(decoded[reviewer][old], decoded[reviewer][new], contract["comparison"]["screen"], comparison_complete) for old, new in PAIRS}
        summaries[reviewer] = {"conditions": conditions, "paired": pairs}
    agreement = {}
    for condition in prep.CONDITIONS:
        a, b = decoded["A"][condition], decoded["B"][condition]
        disagreement = [{"case_id": cid, "A": outcome(a[cid]), "B": outcome(b[cid]),
                         "A_severity": a[cid]["supported_span_severity"], "B_severity": b[cid]["supported_span_severity"],
                         "A_unknown_handling": a[cid]["unknown_span_handling"], "B_unknown_handling": b[cid]["unknown_span_handling"]}
                        for cid in sorted(a) if any(a[cid][k] != b[cid][k] for k in ("judgment", "supported_span_severity", "unknown_span_handling"))]
        agreement[condition] = {"total": 24, "disagreements": disagreement,
            "whole_acceptance_agreement": sum((outcome(a[c]) == "accepted") == (outcome(b[c]) == "accepted") for c in a if a[c]["assessment"] == "provisional_whole_translation")}
    return {"status": "TWO_SEPARATE_PROVISIONAL_DEV96_REVIEWS", "not_palref_score": True, "expert_adjudicated": False,
        "contract_sha256": prep.CONTRACT_SHA, "reviewers": summaries, "reviewer_agreement": agreement,
        "comparison_completion": completion,
        "both_reviewers_screen": {old + " -> " + new: (all(summaries[r]["paired"][old + " -> " + new]["screen_pass"] for r in ("A", "B"))
            if comparison_complete else None) for old, new in PAIRS},
        "screen_status": "assessed" if comparison_complete else "inconclusive",
        "limits": "Descriptive fixed-DEV results; no pooled rater score, significance claim, expert certification or automatic promotion. Native decoding and adaptation differ. A work has a gain if at least one case is newly accepted; global net gain is checked separately. All screens are inconclusive until both full runs complete."}


def score(packet_dir, gemma_dir, qwen_dir, output_dir, review_a=None, review_b=None):
    packet_dir = Path(packet_dir)
    require(not Path(output_dir).exists(), "Output directory must be fresh")
    contract, rows, references, assessments, witnesses = prep.load_contract()
    provenance_data = (packet_dir / "lead-only/provenance.json").read_bytes()
    provenance = json.loads(provenance_data)
    require(provenance["contract_sha256"] == prep.CONTRACT_SHA and provenance["preparer_sha256"] == prep.sha(Path(prep.__file__).read_bytes()), "Packet preparation identity differs")
    for name, expected in provenance["files"].items():
        path = (packet_dir / name).resolve()
        require(path.is_relative_to(packet_dir.resolve()) and prep.sha(path.read_bytes()) == expected, "Packet/archive changed: " + name)
    loaded = {family: prep.load_run(directory, family, rows, witnesses) for family, directory in zip(prep.RUNNERS, (gemma_dir, qwen_dir))}
    rebuilt = prep.build_files(loaded, contract, rows, references, assessments)
    for name, data in rebuilt.items():
        require((packet_dir / name).read_bytes() == data, "Packet/private mapping is not the frozen deterministic conversion: " + name)
    mapping = prep.decode_lines((packet_dir / "lead-only/mapping.jsonl").read_bytes())
    packets, reviews, freeze, files = {}, {}, {}, {}
    for reviewer, explicit in (("A", review_a), ("B", review_b)):
        path = Path(explicit) if explicit is not None else packet_dir / f"reviewer-{reviewer}/reviews.jsonl"
        data = path.read_bytes()
        packets[reviewer] = prep.decode_lines((packet_dir / f"reviewer-{reviewer}/packet.jsonl").read_bytes())
        reviews[reviewer] = prep.decode_lines(data)
        freeze[reviewer] = {"sha256": prep.sha(data), "rows": len(reviews[reviewer]), "reviewer_type": "AI", "expert_adjudicated": False}
        files[f"reviewer-{reviewer}/reviews.jsonl"] = data
    summary = summarize(mapping, packets, reviews, contract, comparison_completion(loaded, rows))
    summary["blind_review_freeze"] = freeze
    summary["packet_provenance_sha256"] = prep.sha(provenance_data)
    summary["scorer_sha256"] = prep.sha(Path(__file__).read_bytes())
    files["comparison.json"] = prep.json_bytes(summary)
    files["blind-review-freeze.json"] = prep.json_bytes(freeze)
    prep.write_fresh(output_dir, files)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("packet_dir", "gemma_dir", "qwen_dir", "output_dir"):
        parser.add_argument(name, type=Path)
    parser.add_argument("--review-a", type=Path)
    parser.add_argument("--review-b", type=Path)
    args = parser.parse_args()
    result = score(args.packet_dir, args.gemma_dir, args.qwen_dir, args.output_dir, args.review_a, args.review_b)
    print(json.dumps({"status": result["status"], "screen_status": result["screen_status"], "both_reviewers_screen": result["both_reviewers_screen"]}, indent=2))
