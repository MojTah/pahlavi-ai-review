"""Local two-arm DEV48 packet preparation and review aggregation; never a semantic judge."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path, PurePosixPath
import random
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import prepare_blind_dev_assisted as prep, score_blind_dev_assisted as scoring
from cloud_pilot import contextual_run as driver

require, sha, canonical = prep.require, prep.sha, prep.shared.canonical
ARMS = ("control", "candidate")
SEEDS = {"A": 2026092711, "B": 2026092712}
LAUNCH = {
    "run_id": "555064e068b54aacafee67e37375ec78",
    "source_commit": "0c2b869c0e0c0bd08fd0014a9130c14b4366e934",
    "spec_sha256": "8fbd1d6b422e9d084757090932b11c367c3087714867281fbada06e40e23af70",
    "command_sha256": "596595227e88c575d411a898b8bcb5350f65e8cf0fb5932c0b247686e7f1bab4",
}
JOB_ID = "6ab9237d52d0dbd7f1d9c66b"
MUTABLE = {"identity_sha256", "status", "schedule", "scheduled_outputs", "attempted_outputs",
           "recorded_outputs", "completed_outputs", "completed_cases", "active_output_id",
           "unattempted_output_ids", "canary", "error_type", "error"}


def ordered(rows):
    return [(row, {"plain": "control", "assisted": "candidate"}[arm])
            for row, arm in prep.shared.schedule(rows)]


def validate_launch(execution, preparation):
    for key, value in LAUNCH.items():
        require(execution.get(key) == preparation.get(key) == value, "Frozen launch differs: " + key)
    require(execution.get("job_id") == JOB_ID, "Job identity differs")
    for name, digest in preparation["script_hashes"].items():
        require(name in {"contextual_run.py", "contextual_train.py", "dev_assisted.py", "dev_diagnostic.py", "palref_eval.py"}
                and sha((ROOT / "cloud_pilot" / name).read_bytes()) == digest, "Launch helper changed")
    require(set(preparation["script_hashes"]) == {"contextual_run.py", "contextual_train.py", "dev_assisted.py", "dev_diagnostic.py", "palref_eval.py"}, "Launch helper inventory differs")
    for name, digest in driver.HELPER_SHA256.items():
        require(sha((ROOT / "cloud_pilot" / name).read_bytes()) == digest, "Frozen helper changed: " + name)
    require(preparation.get("package_manifest_sha256") == driver.PACKAGE_SHA256
            and preparation.get("inputs_sha256") == driver.frozen.INPUTS_SHA256
            and preparation.get("trained_manifest_sha256") == prep.shared.ADAPTER_MANIFEST_SHA256,
            "Preparation data/adapter identity differs")


def validate_artifacts(top, training, evaluation, predictions, rows, preparation, payload, tokenizer):
    """Check metadata and exact tokens only. Adapter tensors remain on the server."""
    expected = {
        "experiment_id": "contextual-supervision-20260927", "package_manifest_sha256": driver.PACKAGE_SHA256,
        "qualified_train_sha256": prep.shared.TRAIN_SHA256, "evaluation_inputs_sha256": driver.frozen.INPUTS_SHA256,
        "inputs_sha256": driver.frozen.INPUTS_SHA256, "original_adapter_files": prep.shared.ADAPTER_FILES,
        "original_adapter_manifest_sha256": prep.shared.ADAPTER_MANIFEST_SHA256,
        "model_id": driver.runtime.MODEL_ID, "model_revision": driver.runtime.REVISION,
        "tokenizer_files": driver.bundle.TOKENIZER_HASHES,
        "runner_sha256": preparation["script_hashes"]["contextual_run.py"], "helper_sha256": driver.HELPER_SHA256,
        "settings": driver.SETTINGS, "seed": 42, "decoding": "greedy", "enable_thinking": False,
        "max_new_tokens": 4096, "max_generation_seconds": 1200, "eos_token_ids": driver.protocol.EOS,
        "evaluation_prompt": "dev_assisted.messages(row, plain, [])",
        "uniform_evaluation_contract_sha256": prep.CONTRACT_SHA,
        "prompts": payload["dev-prompt-identities.json"], "expert_adjudicated": False,
        "quality_validated": False, "scoring_performed": False,
    }
    for key, value in expected.items():
        require(top.get(key) == value, "Top-level identity differs: " + key)
    require(top.get("status") in {"completed", "incomplete"}, "Only closed run evidence can be reviewed")
    prep.first_attempt(top, "top")
    prepared = driver.prepare_prompts(rows, payload["dev-prompt-identities.json"], tokenizer, 262144)
    slots = [s["control_id"] for s in payload["ordered-slots.jsonl"]]
    training_complete = training is not None and training.get("status") == "completed"
    if training is not None:
        require(training.get("settings") == driver.SETTINGS and training.get("runner_sha256") == driver.HELPER_SHA256["contextual_train.py"]
                and training.get("runtime_sha256") == driver.HELPER_SHA256["runtime.py"]
                and training.get("scheduled_parent_ids") == slots and training.get("scheduled_slots_per_arm") == 768,
                "Training recipe/order identity differs")
    if training_complete:
        require(set(training.get("arms", {})) == set(ARMS), "Training arm coverage differs")
        for arm in ARMS:
            info = training["arms"][arm]
            require(info.get("status") == "completed" and info.get("completed_steps") == 48
                    and info.get("consumed_slots") == 768 and info.get("consumed_parent_ids") == slots
                    and info.get("parent_order_verified") is True and info.get("optimizer_initially_empty") is True
                    and info.get("optimizer_initial_state_entries") == 0 and info.get("initial_scheduler_step") == 0
                    and info.get("model_accepts_loss_kwargs") is False
                    and info.get("initial_adapter_sha256") == training.get("initial_adapter_sha256"), "Training arm incomplete or mismatched")
            if evaluation is not None:
                a = top.get("adapters", {}).get(arm, {})
                require(a == {"files": info.get("adapter_files"), "final_tensor_sha256": info.get("final_adapter_sha256"),
                              "new_phase_steps": 48, "original_adapter_step": 280}, "New adapter provenance differs")
                require(all(isinstance(v, str) and len(v) == 64 for v in a["files"].values())
                        and {"adapter_config.json", "adapter_model.safetensors"} <= set(a["files"]), "Invalid adapter hashes")
        for key in ("initial_rng_sha256", "train_begin_rng_sha256"):
            require(training["arms"]["control"].get(key) == training["arms"]["candidate"].get(key)
                    and isinstance(training["arms"]["control"].get(key), str), "Paired initial RNG differs")
    if evaluation is None:
        require(not predictions and top["status"] != "completed", "Missing evaluation evidence")
        return {"complete": False, "reason": "Evaluation never produced a run record", "training_complete": training_complete}
    require(training_complete and top.get("training_canary", {}).get("status") == "passed", "Evaluation lacks completed training/canary")
    for key in (*expected, "base_files", "environment", "deadline_utc", "adapters"):
        require(evaluation.get(key) == top.get(key), "Evaluation/top identity differs: " + key)
    identity = {key: value for key, value in evaluation.items() if key not in MUTABLE}
    require(sha(canonical(identity)) == evaluation.get("identity_sha256"), "Evaluation identity hash differs")
    schedule = ordered(rows)
    ids = [r["id"] + ":" + arm for r, arm in schedule]
    require(evaluation.get("status") in {"completed", "incomplete"} and evaluation.get("schedule") == ids
            and evaluation.get("scheduled_outputs") == 48, "Evaluation schedule/state differs")
    require(all(type(evaluation.get(k)) is int for k in ("scheduled_outputs", "attempted_outputs", "recorded_outputs", "completed_outputs", "completed_cases")), "Counter types differ")
    prep.first_attempt(evaluation, "evaluation")
    prep.unique(predictions)
    require([p["id"] for p in predictions] == ids[:len(predictions)] and len(predictions) <= 48, "First-attempt prefix differs")
    require(evaluation.get("attempted_outputs") == evaluation.get("recorded_outputs") == len(predictions)
            and evaluation.get("active_output_id") is None
            and evaluation.get("unattempted_output_ids") == ids[len(predictions):], "Counters/active attempt require recovery")
    completed = Counter()
    for i, (p, (row, arm)) in enumerate(zip(predictions, schedule), 1):
        prep.first_attempt(p, p["id"])
        require(type(p.get("sequence")) is int and (p.get("case_id"), p.get("record_id"), p.get("work_id"), p.get("arm"), p.get("condition"), p.get("sequence"))
                == (row["id"], row["record_id"], row["work_id"], arm, arm, i), "Prediction identity differs")
        require(p.get("input_sha256") == sha(row["source_text"].encode()) and p.get("identity_sha256") == evaluation["identity_sha256"]
                and p.get("adapter_sha256") == top["adapters"][arm]["files"]["adapter_model.safetensors"], "Source/run/adapter hash differs")
        require(p.get("input_tokens") == len(prepared[row["id"]])
                and p.get("rendered_input_ids_sha256") == sha(canonical(prepared[row["id"]])), "Rendered input tokens differ")
        tokens, text, elapsed, status = p.get("output_token_ids"), p.get("text"), p.get("elapsed_seconds"), p.get("status")
        require(isinstance(tokens, list) and all(type(t) is int and 0 <= t < len(tokenizer) for t in tokens)
                and p.get("output_tokens") == len(tokens) <= 4096, "Output token IDs/count differ")
        require(isinstance(text, str) and text == tokenizer.decode(tokens, skip_special_tokens=True)
                and p.get("output_sha256") == sha(text.encode()), "Output text/token/hash differs")
        require(type(elapsed) in (int, float) and math.isfinite(elapsed) and elapsed >= 0
                and status in {"success", "abstain", "timeout", "error"}, "Invalid execution outcome")
        cap = len(tokens) == 4096 and tokens[-1] not in driver.protocol.EOS
        require(p.get("hit_output_cap_without_eos") is cap, "Output cap evidence differs")
        if status in {"success", "abstain"}:
            require(elapsed <= 1200 and not cap and p.get("stop_reason") is None
                    and text.strip() and (status == "abstain") == (text.strip() == "[UNRESOLVED]"), "Invalid completed output")
            require(tokens[-1] in driver.protocol.EOS, "Successful generation lacks EOS")
            completed[row["id"]] += 1
        require(i == len(predictions) or status in {"success", "abstain"}, "Output after first failure")
    require(evaluation.get("completed_outputs") == sum(completed.values())
            and evaluation.get("completed_cases") == sum(n == 2 for n in completed.values()), "Completion counters differ")
    if predictions:
        require(evaluation.get("canary", {}).get("status") == "passed", "Missing prefill canary")
    all_outputs = len(predictions) == sum(completed.values()) == 48
    if evaluation["status"] == "completed":
        require(all_outputs, "False evaluation completion")
    if top["status"] == "completed":
        require(all_outputs and evaluation["status"] == "completed" and top.get("training_steps_per_arm") == 48
                and top.get("evaluation_completed_outputs") == 48 and top.get("evaluation_completed_cases") == 24, "False top-level completion")
    return {"complete": top["status"] == evaluation["status"] == "completed" and all_outputs,
            "training_complete": training_complete, "recorded_outputs": len(predictions),
            "completed_outputs": sum(completed.values()), "adapter_tensor_validation": "Server provenance only; no local weights opened"}


def validate_recovery(root, manifest_bytes, export, proof, preparation):
    """Bind the controller's closed recovery proof; never open weight files."""
    require(proof.get("run_id") == preparation["run_id"] == LAUNCH["run_id"]
            and proof.get("manifest_sha256") == sha(manifest_bytes)
            and proof.get("provider_inventory_committed") is True
            and proof.get("model_weights_downloaded") is False
            and proof.get("contextual_status") == export.get("contextual_status"), "Recovery proof/manifest binding differs")
    files, inventory = export["files"], proof.get("provider_inventory", {})
    prefix = preparation["output_prefix"]
    require(prefix == "contextual-pilot/" + LAUNCH["run_id"]
            and set(inventory) == {prefix + "/manifest.json", *(prefix + "/" + n for n in files)}, "Recovery provider inventory is not exact")
    manifest_entry = inventory[prefix + "/manifest.json"]
    require(manifest_entry.get("bytes") == len(manifest_bytes) and isinstance(manifest_entry.get("xet_hash"), str)
            and bool(manifest_entry["xet_hash"]), "Recovery manifest is not provider committed")
    small = []
    for name, record in files.items():
        path = PurePosixPath(name)
        require(not path.is_absolute() and ".." not in path.parts and path.as_posix() == name and "\\" not in name and ":" not in name
                and type(record.get("bytes")) is int and record["bytes"] >= 0
                and isinstance(record.get("sha256"), str) and re.fullmatch(r"[a-f0-9]{64}", record["sha256"]), "Unsafe export record")
        entry = inventory[prefix + "/" + name]
        require(entry.get("bytes") == record["bytes"] and isinstance(entry.get("xet_hash"), str) and bool(entry["xet_hash"]), "Recovery artifact is not provider committed")
        if name.endswith((".json", ".jsonl", ".md", ".log")):
            small.append(name)
            local = Path(root) / name
            require(local.is_file() and not local.is_symlink() and local.resolve().is_relative_to(Path(root).resolve()), "Recovered small record missing/unsafe")
            data = local.read_bytes()
            require(len(data) == record["bytes"] and sha(data) == record["sha256"], "Recovered small record hash/size differs")
        else:
            require(name in {"contextual/training/" + arm + "/adapter/adapter_model.safetensors" for arm in ARMS}, "Unexpected binary export")
    verified = proof.get("local_sha_verified_files")
    require(isinstance(verified, list) and len(verified) == len(set(verified)) and set(verified) == set(small), "Recovery small-file verified set differs")


def validate_adapter_exports(training, export):
    if training is None:
        return
    for arm, info in training.get("arms", {}).items():
        if info.get("status") != "completed":
            continue
        require(arm in ARMS, "Unknown exported training arm")
        prefix = "contextual/training/" + arm + "/adapter/"
        expected = info.get("adapter_files", {})
        require({"adapter_config.json", "adapter_model.safetensors"} <= set(expected)
                and {n[len(prefix):] for n in export["files"] if n.startswith(prefix)} == set(expected), "Completed adapter export inventory differs")
        for name, digest in expected.items():
            entry = export["files"][prefix + name]
            require(entry["sha256"] == digest and entry["bytes"] > 0, "Completed adapter export hash differs")


def load_artifacts(run_dir, execution, preparation, package, tokenizer_path, rows):
    from transformers import AutoTokenizer
    run_dir = Path(run_dir)
    raw = {"execution.json": Path(execution).read_bytes(), "execution-preparation.json": Path(preparation).read_bytes()}
    launch, prepared_launch = json.loads(raw["execution.json"]), json.loads(raw["execution-preparation.json"])
    validate_launch(launch, prepared_launch)
    manifest_bytes = (run_dir.parent / "manifest.json").read_bytes()
    export = json.loads(manifest_bytes)
    raw["recovery.json"] = (run_dir.parent.parent / "recovery.json").read_bytes()
    validate_recovery(run_dir.parent, manifest_bytes, export, json.loads(raw["recovery.json"]), prepared_launch)
    for key in ("run_id", "package_manifest_sha256", "inputs_sha256", "bundle_sha256", "trained_manifest_sha256", "script_hashes"):
        require(export.get(key) == prepared_launch.get(key), "Export/launch identity differs: " + key)
    require(export.get("operation") == "contextual_pilot" and export.get("quality_validated") is False, "Export operation differs")
    _, payload = driver.read_package(package, driver.PACKAGE_SHA256)
    driver.runtime.checked_files(tokenizer_path, driver.bundle.TOKENIZER_HASHES)
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, local_files_only=True, trust_remote_code=False)
    for name in ("run.json", "training/run.json", "evaluation/run.json", "evaluation/predictions.jsonl"):
        path = run_dir / name
        require(path.is_file() or "contextual/" + name not in export["files"], "Declared export record is missing locally: " + name)
        if path.is_file():
            raw[name] = path.read_bytes()
            entry = export["files"].get("contextual/" + name, {})
            require(entry.get("sha256") == sha(raw[name]) and entry.get("bytes") == len(raw[name]), "Exported record hash/size differs: " + name)
    require("run.json" in raw, "Recovered runner metadata is required")
    top = json.loads(raw["run.json"])
    training = json.loads(raw["training/run.json"]) if "training/run.json" in raw else None
    validate_adapter_exports(training, export)
    evaluation = json.loads(raw["evaluation/run.json"]) if "evaluation/run.json" in raw else None
    predictions = prep.decode_lines(raw.get("evaluation/predictions.jsonl", b""))
    completion = validate_artifacts(top, training, evaluation, predictions, rows, prepared_launch, payload, tokenizer)
    completion["complete"] = completion["complete"] and export.get("contextual_status") == "complete"
    raw["export-manifest.json"] = manifest_bytes
    return predictions, raw, completion


def build_files(predictions, raw, completion, contract, rows, references, assessments):
    files = {"lead-only/raw/" + name: data for name, data in raw.items()}
    # Retain the original bytes in addition to the unchanged reference projection in each packet.
    for name in ("references.jsonl", "assessment-contract.json", "reviewer-clarification.json"):
        files["lead-only/frozen/" + name] = (prep.DEV / name).read_bytes()
    observed, mapping, used = prep.unique(predictions), [], set()
    source = prep.unique(rows)
    instructions = prep.instructions()
    require(instructions.count(b"Review all 96 opaque records") == 1, "Instruction count phrase changed")
    instructions = instructions.replace(b"Review all 96 opaque records", b"Review all 48 opaque records")
    for reviewer, seed in SEEDS.items():
        rng = random.Random(seed)
        order = [(row["id"], arm) for row in rows for arm in ARMS]
        rng.shuffle(order)
        packet = []
        for cid, arm in order:
            rid = "r" + format(rng.getrandbits(128), "032x")
            require(rid not in used, "Opaque ID collision")
            used.add(rid)
            p = observed.get(cid + ":" + arm)
            text, status = (p["text"], p["status"]) if p is not None else ("", "unattempted")
            ref, assessment, row = references[cid], assessments[cid], source[cid]
            packet.append({"review_id": rid, "source_text": row["source_text"],
                "references": {k: ref[k] for k in ("translations", "edition", "notes", "reference_screen", "expert_adjudicated")},
                "assessment": assessment["assessment"], "constraint": assessment["constraint"],
                "execution_status": status, "output_text": text, "output_sha256": sha(text.encode())})
            mapping.append({"reviewer": reviewer, "review_id": rid, "condition": arm, "case_id": cid,
                "work_id": row["work_id"], "assessment": assessment["assessment"], "prediction_id": cid + ":" + arm,
                "source_sha256": sha(row["source_text"].encode()), "output_sha256": sha(text.encode()),
                "output_present": p is not None, "execution_status": status})
        require(len(packet) == 48, "DEV48 coverage differs")
        files[f"reviewer-{reviewer}/packet.jsonl"] = prep.lines(packet)
        files[f"reviewer-{reviewer}/INSTRUCTIONS.md"] = instructions
    files["lead-only/mapping.jsonl"] = prep.lines(mapping)
    files["lead-only/provenance.json"] = prep.json_bytes({"status": "LOCAL_BLIND_CONTEXTUAL_DEV48_PREPARED",
        "contract_sha256": prep.CONTRACT_SHA, "launch": LAUNCH, "completion": completion,
        "source_files_sha256": contract["source_files_sha256"], "reviewers": 2, "outputs_per_reviewer": 48,
        "expert_adjudicated": False, "seeds": SEEDS, "preparer_sha256": sha(Path(__file__).read_bytes()),
        "files": {name: sha(data) for name, data in files.items()}})
    return files


def summarize(mapping, packets, reviews, contract, completion):
    require(len(mapping) == 96 and len(prep.unique(mapping, "review_id")) == 96, "Private mapping coverage differs")
    decoded, reports = {}, {}
    for reviewer in SEEDS:
        ratings = scoring.validate_reviews(packets[reviewer], reviews[reviewer], expected_count=48)
        selected = [m for m in mapping if m["reviewer"] == reviewer]
        require({m["review_id"] for m in selected} == set(ratings), "Mapping/review identity differs")
        by_packet = prep.unique(packets[reviewer], "review_id")
        decoded[reviewer] = {arm: {} for arm in ARMS}
        for m in selected:
            p = by_packet[m["review_id"]]
            require(m["output_sha256"] == p["output_sha256"] and m["source_sha256"] == sha(p["source_text"].encode())
                    and m["assessment"] == p["assessment"] and m["execution_status"] == p["execution_status"], "Private mapping differs")
            require(m["condition"] in ARMS and m["case_id"] not in decoded[reviewer][m["condition"]], "Mapped arm/case differs")
            decoded[reviewer][m["condition"]][m["case_id"]] = {**ratings[m["review_id"]], **m}
        conditions = {arm: scoring.condition_report(list(decoded[reviewer][arm].values())) for arm in ARMS}
        require(all((v["whole_denominator"], v["constrained_denominator"]) == (15, 9) for v in conditions.values()), "Fixed denominators differ")
        for arm in ARMS:
            records = list(decoded[reviewer][arm].values())
            conditions[arm]["by_work"] = {work: scoring.condition_report([r for r in records if r["work_id"] == work])
                                           for work in sorted({r["work_id"] for r in records})}
        pair = scoring.paired_report(decoded[reviewer]["control"], decoded[reviewer]["candidate"], contract["comparison"]["screen"], completion["complete"])
        pair["screen_checks"]["full_two_arm_comparison_complete"] = pair["screen_checks"].pop("full_four_condition_comparison_complete")
        reports[reviewer] = {"conditions": conditions, "paired": {"control -> candidate": pair}}
    disagreements = {arm: [{"case_id": cid, "A": {k: decoded["A"][arm][cid][k] for k in ("judgment", "supported_span_severity", "unknown_span_handling")},
                            "B": {k: decoded["B"][arm][cid][k] for k in ("judgment", "supported_span_severity", "unknown_span_handling")}}
                          for cid in sorted(decoded["A"][arm])
                          if any(decoded["A"][arm][cid][k] != decoded["B"][arm][cid][k] for k in ("judgment", "supported_span_severity", "unknown_span_handling"))] for arm in ARMS}
    return {"status": "TWO_SEPARATE_PROVISIONAL_CONTEXTUAL_DEV48_REVIEWS", "contract_sha256": prep.CONTRACT_SHA,
        "expert_adjudicated": False, "not_palref_score": True, "reviewers": reports, "reviewer_disagreements": disagreements,
        "comparison_completion": completion, "screen_status": "assessed" if completion["complete"] else "inconclusive",
        "both_reviewers_screen": all(reports[r]["paired"]["control -> candidate"]["screen_pass"] for r in SEEDS) if completion["complete"] else None,
        "limits": "Fixed development-exposed DEV, two separate provisional AI reviews; no pooled score, significance, expert certification or automatic promotion. Control versus candidate is primary. Historical step280 is descriptive only and is not part of these packets or this screen."}


def operate(args):
    require(not Path(args.output).exists(), "Output directory must be fresh")
    contract, rows, references, assessments, _ = prep.load_contract()
    predictions, raw, completion = load_artifacts(args.run_dir, args.execution, args.preparation, args.package, args.tokenizer, rows)
    files = build_files(predictions, raw, completion, contract, rows, references, assessments)
    if args.command == "prepare":
        prep.write_fresh(args.output, files)
        return {"status": "LOCAL_BLIND_CONTEXTUAL_DEV48_PREPARED", "completion": completion}
    require(args.packet_dir is not None, "Scoring requires frozen packet directory")
    packet_dir = Path(args.packet_dir)
    for name, data in files.items():
        require((packet_dir / name).read_bytes() == data, "Packet/archive is not the exact frozen conversion: " + name)
    packets, reviews, freeze, output = {}, {}, {}, {}
    for reviewer in SEEDS:
        packets[reviewer] = prep.decode_lines(files[f"reviewer-{reviewer}/packet.jsonl"])
        data = (packet_dir / f"reviewer-{reviewer}/reviews.jsonl").read_bytes()
        reviews[reviewer] = prep.decode_lines(data)
        freeze[reviewer] = {"sha256": sha(data), "rows": len(reviews[reviewer]), "reviewer_type": "AI", "expert_adjudicated": False}
        output[f"reviewer-{reviewer}/reviews.jsonl"] = data
    result = summarize(prep.decode_lines(files["lead-only/mapping.jsonl"]), packets, reviews, contract, completion)
    result.update(blind_review_freeze=freeze, packet_provenance_sha256=sha(files["lead-only/provenance.json"]), scorer_sha256=sha(Path(__file__).read_bytes()))
    output["comparison.json"], output["blind-review-freeze.json"] = prep.json_bytes(result), prep.json_bytes(freeze)
    prep.write_fresh(args.output, output)
    return {"status": result["status"], "screen_status": result["screen_status"], "both_reviewers_screen": result["both_reviewers_screen"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "score"))
    for name in ("run-dir", "execution", "preparation", "package", "tokenizer", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--packet-dir", type=Path)
    print(json.dumps(operate(parser.parse_args()), indent=2))


if __name__ == "__main__":
    main()
