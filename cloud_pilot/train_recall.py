"""Offline step-280 seen-TRAIN recall diagnostic; no scoring or cloud submission."""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import re
import time

try:
    from . import dev_assisted as qualified, dev_diagnostic as frozen, palref_eval as protocol, runtime
except ImportError:
    import dev_assisted as qualified
    import dev_diagnostic as frozen
    import palref_eval as protocol
    import runtime

CONDITIONS = ("training", "evaluation")
INPUTS_SHA256 = "5a2b29c878b67e05bb1051fab015feae33753e7c23568ab57517af0cf84c233a"
TOKEN_AUDIT_SHA256 = "2b1632e86f504ddea2a44f736d00997fb14b67c7710b5a874b9abf42766d6b16"
TOKEN_MAP_SHA256 = "0909c12c316960cad702823b895555e0539ffb4e196b1bbcd5f10de8a1baeead"
IDS = [f"TRAINRECALL1-{index:03d}" for index in range(1, 21)]
HELPER_SHA256 = {
    "dev_assisted.py": "4334db8c1097c220dbcce75b3d30287a29c43c5482ab71313c3db9cf287fec4d",
    "dev_diagnostic.py": "9d459482f3b7189cc2109bd68e36d14e77693df64f41574ff952d71bc6725d11",
    "bundle.py": "60094706124ee58b78a2b73b6a43c30eb9310a2a1d3786f83749e95b597b1a2d",
    "palref_eval.py": qualified.PROTOCOL_SHA256,
}


def read_inputs(path, expected_sha256, train_path):
    """Bind the six-field projection to exact qualified TRAIN, returning no targets."""
    data = Path(path).read_bytes()
    if expected_sha256 != INPUTS_SHA256 or qualified.sha(data) != expected_sha256:
        raise ValueError("Frozen source-only input checksum differs")
    train_data = Path(train_path).read_bytes()
    if qualified.sha(train_data) != qualified.TRAIN_SHA256:
        raise ValueError("Exact qualified TRAIN required")
    rows = [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]
    if len(rows) != 20 or any(not isinstance(row, dict) or set(row) != frozen.FIELDS for row in rows):
        raise ValueError("Exactly twenty six-field source-only rows required")
    membership = {}
    for line in train_data.decode("utf-8").splitlines():
        entry = json.loads(line)
        if entry["record_id"] in membership:
            raise ValueError("Ambiguous TRAIN parent identity")
        membership[entry["record_id"]] = {key: entry[key] for key in
            ("record_id", "work_id", "source_language", "target_language", "text")}
    for row in rows:
        if (any(not isinstance(row[key], str) or not row[key].strip() for key in frozen.FIELDS)
                or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9:_>.\-]*", row["id"])
                or not re.fullmatch(r"parsig:\d{9}", row["record_id"])
                or row["work_id"] != row["record_id"][:10]
                or (row["source_language"], row["target_language"]) != ("pal", "fa")):
            raise ValueError("Invalid source identity or direction")
        frozen.training_bundle.reject_controls(row["source_text"])
        expected = {key: row[key] for key in ("record_id", "work_id", "source_language", "target_language")}
        expected["text"] = row["source_text"]
        if membership.get(row["record_id"]) != expected:
            raise ValueError("Source/record/work is not exact qualified TRAIN membership")
    if [row["id"] for row in rows] != IDS or len({row["record_id"] for row in rows}) != 20:
        raise ValueError("Frozen case order and twenty unique parent identities required")
    return rows


def schedule(rows):
    """Preserve frozen input order; alternate the two prompt orders by parent index."""
    return [(row, condition) for index, row in enumerate(rows)
            for condition in (CONDITIONS if index % 2 == 0 else CONDITIONS[::-1])]


def evaluate(args):
    runtime.offline()
    deadline = runtime.check_deadline(args.deadline_utc)
    output = Path(args.output).resolve()
    if output.exists():
        raise ValueError("Recall output must be a fresh directory")
    for module in (qualified, frozen, frozen.training_bundle, protocol):
        if runtime.digest(module.__file__) != HELPER_SHA256[Path(module.__file__).name]:
            raise ValueError("Frozen helper identity differs")
    folder = runtime.verified_bundle(args.bundle)
    rows = read_inputs(args.inputs, args.inputs_sha256, folder / "train.jsonl")
    contract = runtime.contract_at(folder / "contract.json")
    base = runtime.verify_base(args.base)
    tokenizer_files = {name: base["files"][name] for name in
        ("tokenizer.json", "tokenizer_config.json", "chat_template.jinja")}
    runtime.checked_files(args.tokenizer, tokenizer_files)
    qualified.verify_adapter(args.adapter, contract, base)
    environment = runtime.gpu_admission()
    ordered = schedule(rows)
    output_ids = [row["id"] + ":" + condition for row, condition in ordered]
    prompts = {(row["id"], condition): frozen.messages(row, condition) for row, condition in ordered}
    identity = {"experiment_id": "qualified-train-recall", "diagnostic_scope": "seen TRAIN recall; not generalization",
        "inputs_sha256": args.inputs_sha256, "train_sha256": qualified.TRAIN_SHA256,
        "model_id": runtime.MODEL_ID, "model_revision": runtime.REVISION, "base_files": base["files"],
        "adapter_files": qualified.ADAPTER_FILES, "adapter_metadata": qualified.ADAPTER_METADATA,
        "adapter_step": 280, "adapter_manifest_sha256": qualified.ADAPTER_MANIFEST_SHA256,
        "tokenizer_files": tokenizer_files, "runtime": environment, "runner_sha256": runtime.digest(__file__),
        "local_token_audit_sha256": TOKEN_AUDIT_SHA256, "expected_token_map_sha256": TOKEN_MAP_SHA256,
        "actual_token_map_sha256": None,
        "helper_sha256": HELPER_SHA256, "bundle_manifest_sha256": runtime.digest(folder / "manifest.json"),
        "schedule": output_ids, "schedule_method": "frozen parent order; alternate prompt order by zero-based parent index",
        "seed": 42, "seed_policy": "set once before the schedule; greedy generation",
        "conditions": CONDITIONS, "max_new_tokens": protocol.MAX_TOKENS, "max_generation_seconds": protocol.CASE_SECONDS,
        "eos_token_ids": protocol.EOS, "pad_token_id": 0, "num_beams": 1, "decoding": "greedy",
        "enable_thinking": False, "fresh_context_each_case": True, "deadline_utc": args.deadline_utc,
        "scoring_performed": False, "training_performed": False,
        "prompts": [{"id": row["id"] + ":" + condition, "record_id": row["record_id"], "work_id": row["work_id"],
            "source_sha256": qualified.sha(row["source_text"].encode("utf-8")),
            "messages": prompts[row["id"], condition],
            "messages_sha256": qualified.sha(qualified.canonical(prompts[row["id"], condition]))}
            for row, condition in ordered]}
    run = {**identity, "identity_sha256": None, "status": "preparing", "scheduled_outputs": 40,
        "attempted_outputs": 0, "recorded_outputs": 0, "active_output_id": None,
        "completed_outputs": 0, "completed_cases": 0,
        "unattempted_output_ids": list(output_ids), "case_metadata": [],
        "canary": {"status": "not_started", "experimental_attempts": 0}}
    output.mkdir(parents=True, exist_ok=False)
    runtime.write_json(output / "run.json", run)
    try:
        import torch
        from transformers import AutoTokenizer, DynamicCache, Gemma4ForConditionalGeneration, StoppingCriteriaList, set_seed
        from peft import PeftModel
        runtime.check_deadline(args.deadline_utc)
        tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, local_files_only=True, trust_remote_code=False)
        prepared = {key: tokenizer.apply_chat_template(value, tokenize=True, return_dict=False,
            add_generation_prompt=True, enable_thinking=False) for key, value in prompts.items()}
        context_limit = runtime.read_json(Path(args.base) / "config.json")["text_config"]["max_position_embeddings"]
        for note, (row, condition) in zip(identity["prompts"], ordered):
            ids = prepared[row["id"], condition]
            if not ids or any(type(token) is not int or token < 0 for token in ids) or len(ids) + protocol.MAX_TOKENS > context_limit:
                raise ValueError("Invalid/untruncated prompt plus output ceiling exceeds context")
            note.update(input_tokens=len(ids), input_token_ids=ids, rendered_input_ids_sha256=qualified.sha(qualified.canonical(ids)))
        token_map = {case_id + ":" + condition: {"input_tokens": len(ids),
            "input_ids_sha256": qualified.sha(qualified.canonical(ids))}
            for (case_id, condition), ids in prepared.items()}
        actual_token_map_sha = qualified.sha(qualified.canonical(token_map))
        identity["actual_token_map_sha256"] = actual_token_map_sha
        run["actual_token_map_sha256"] = actual_token_map_sha
        identity_sha = qualified.sha(qualified.canonical(identity))
        run["identity_sha256"] = identity_sha
        if actual_token_map_sha != TOKEN_MAP_SHA256:
            raise ValueError("Rendered prompt token map differs from the frozen local audit")
        run["status"] = "running"
        runtime.write_json(output / "run.json", run)
        runtime.check_deadline(args.deadline_utc)
        base_model = Gemma4ForConditionalGeneration.from_pretrained(args.base, local_files_only=True,
            trust_remote_code=False, use_safetensors=True, device_map={"": 0}, dtype=torch.bfloat16, attn_implementation="eager")
        model = PeftModel.from_pretrained(base_model, args.adapter, local_files_only=True, is_trainable=False)
        model.eval()
        run["canary"] = {"status": "running", "experimental_attempts": 0}
        runtime.write_json(output / "run.json", run)
        run["canary"] = qualified.prefill_canary(model, prepared, args.deadline_utc)
        runtime.write_json(output / "run.json", run)
        set_seed(42)
        completed = Counter()
        with (output / "predictions.jsonl").open("x", encoding="utf-8") as stream:
            for index, (row, condition) in enumerate(ordered):
                runtime.check_deadline(args.deadline_utc)
                ids = prepared[row["id"], condition]
                # A killed process must leave this attempt marked as started, not unattempted.
                run["attempted_outputs"] += 1
                run["active_output_id"] = output_ids[index]
                run["unattempted_output_ids"] = output_ids[index + 1:]
                runtime.write_json(output / "run.json", run)
                start, failure, new_ids, hit_cap = time.monotonic(), None, [], False
                stopper = protocol.GenerationDeadline(start, deadline)
                try:
                    tokens = torch.tensor([ids], device="cuda")
                    with torch.inference_mode():
                        generated = model.generate(input_ids=tokens, attention_mask=torch.ones_like(tokens),
                            past_key_values=DynamicCache(), use_cache=True, do_sample=False, num_beams=1,
                            max_new_tokens=protocol.MAX_TOKENS, pad_token_id=0, eos_token_id=protocol.EOS,
                            stopping_criteria=StoppingCriteriaList([stopper]))
                    new_ids = generated[0, len(ids):].tolist()
                    stopper(None, None)
                    hit_cap = len(new_ids) >= protocol.MAX_TOKENS and new_ids[-1] not in protocol.EOS
                    result = protocol.prediction(row, tokenizer.decode(new_ids, skip_special_tokens=True),
                        time.monotonic() - start, timed_out=stopper.reason is not None, hit_cap=hit_cap)
                except BaseException as error:
                    failure = error
                    result = protocol.prediction(row, "", time.monotonic() - start)
                    result.update(status="error", error_type=type(error).__name__, error=str(error))
                result.update(id=output_ids[index], case_id=row["id"], record_id=row["record_id"], work_id=row["work_id"],
                    condition=condition, sequence=index + 1, identity_sha256=identity_sha,
                    input_tokens=len(ids), output_tokens=len(new_ids), output_token_ids=new_ids,
                    output_token_ids_sha256=qualified.sha(qualified.canonical(new_ids)),
                    hit_output_cap_without_eos=hit_cap, stop_reason=stopper.reason,
                    rendered_input_ids_sha256=qualified.sha(qualified.canonical(ids)))
                stream.write(json.dumps(result, ensure_ascii=False) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
                run["recorded_outputs"] += 1
                run["active_output_id"] = None
                if result["status"] in {"success", "abstain"}:
                    run["completed_outputs"] += 1
                    completed[row["id"]] += 1
                run["completed_cases"] = sum(count == 2 for count in completed.values())
                run["case_metadata"].append({key: result[key] for key in ("id", "condition", "status", "input_tokens", "output_tokens")})
                runtime.write_json(output / "run.json", run)
                print(json.dumps({"status": "train_recall_attempt_recorded", "id": result["id"], "outcome": result["status"]}), flush=True)
                if failure is not None:
                    raise failure
                if result["status"] not in {"success", "abstain"}:
                    raise RuntimeError("First-attempt generation incomplete: " + result["status"])
        run["status"] = "completed"
        runtime.write_json(output / "run.json", run)
    except BaseException as error:
        if run["canary"]["status"] == "running":
            run["canary"].update(status="failed", error_type=type(error).__name__, error=str(error))
        run.update(status="incomplete", error_type=type(error).__name__, error=str(error))
        runtime.write_json(output / "run.json", run)
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("bundle", "base", "tokenizer", "inputs", "inputs-sha256", "adapter", "output", "deadline-utc"):
        parser.add_argument("--" + name, required=True)
    evaluate(parser.parse_args(argv))


if __name__ == "__main__":
    main()
