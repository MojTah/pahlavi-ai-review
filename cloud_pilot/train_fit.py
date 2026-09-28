"""Offline conditional fit on twenty seen TRAIN parents; no generation or training."""
import argparse
from collections import Counter
from contextlib import nullcontext
import json
import math
import os
from pathlib import Path
import time

try:
    from . import train_recall as recall
except ImportError:
    import train_recall as recall

qualified, frozen, runtime = recall.qualified, recall.frozen, recall.runtime
bundle = frozen.training_bundle
INPUTS_SHA256 = recall.INPUTS_SHA256
SOURCE_CONTROL_SHA256 = "3db2398a95b6480ad2522dc2fe30d2d38156564e3a4a72714b43bcc2a54393a0"
TOKEN_AUDIT_SHA256 = "a3dbbab31b5b893e032cc1fcac4d2b459f4231d3a367953e0191bb780ff3e7c8"
TOKEN_MAP_SHA256 = "de1388e6ae8e260ec1233cefbbcdcbc4130871715707898973de1696e9f168bf"
HELPER_SHA256 = {**recall.HELPER_SHA256,
    "train_recall.py": "8d2b56c2807c52d2f103faac252f8e90de4a2ca5ce9d1df6b9a2f05fdb9dc639"}
CONDITIONS = ((True, "correct"), (False, "correct"), (True, "mismatched"), (False, "mismatched"))
LOSS_ATOL, LOSS_RTOL = 1e-5, 1e-5
TOKEN_MAP_FIELDS = ("input_tokens", "prompt_tokens", "supervised_tokens", "input_ids_sha256",
                    "labels_sha256", "target_ids_sha256")


def read_inputs(path, expected_sha256, train_path):
    return recall.read_inputs(path, expected_sha256, train_path)


def validate_control(control, rows):
    if len(rows) != 20 or [row["id"] for row in rows] != recall.IDS:
        raise ValueError("Frozen twenty-parent order required")
    shift = next(index for index in range(1, len(rows)) if all(
        row["work_id"] != rows[(i + index) % len(rows)]["work_id"]
        and row["record_id"] != rows[(i + index) % len(rows)]["record_id"]
        for i, row in enumerate(rows)))
    pairs = []
    for index, row in enumerate(rows):
        other = rows[(index + shift) % len(rows)]
        pairs.append({"target_parent_id": row["id"], "target_record_id": row["record_id"],
            "correct_source_sha256": qualified.sha(row["source_text"].encode("utf-8")),
            "mismatched_source_parent_id": other["id"], "mismatched_source_record_id": other["record_id"],
            "mismatched_source_sha256": qualified.sha(other["source_text"].encode("utf-8"))})
    expected = {"status": "FROZEN_BEFORE_FIT_OUTPUTS", "source_input_sha256": INPUTS_SHA256,
        "method": "Smallest positive cyclic shift with no shared parent or work", "shift": shift,
        "count": 20, "contains_reference_answers": False, "never_training_pairs": True, "pairs": pairs}
    if shift != 5 or control != expected:
        raise ValueError("Source control differs from the frozen no-shared-work permutation")


def read_source_control(path, expected_sha256, rows):
    data = Path(path).read_bytes()
    if expected_sha256 != SOURCE_CONTROL_SHA256 or qualified.sha(data) != expected_sha256:
        raise ValueError("Source control checksum differs")
    control = json.loads(data)
    validate_control(control, rows)
    return control


def prepare_inputs(rows, train_path, control, tokenizer, max_length):
    """Tokenize forty inputs locally; verify saved TRAIN tokens and unchanged answer suffixes."""
    validate_control(control, rows)
    data = Path(train_path).read_bytes()
    if qualified.sha(data) != qualified.TRAIN_SHA256:
        raise ValueError("Exact qualified TRAIN required")
    train = {row["record_id"]: row for row in bundle.jsonl(data)}
    sources = {row["id"]: row for row in rows}
    prepared = {}
    for row, pair in zip(rows, control["pairs"]):
        saved = train[row["record_id"]]
        if any(saved[key] != row[key] for key in ("record_id", "work_id", "source_language", "target_language")) or saved["text"] != row["source_text"]:
            raise ValueError("Parent is not exact qualified TRAIN membership")
        bundle.validate_row(saved)
        target_ids = saved["input_ids"][saved["prompt_tokens"]:]
        for condition in ("correct", "mismatched"):
            source = row if condition == "correct" else sources[pair["mismatched_source_parent_id"]]
            raw = {key: saved[key] for key in bundle.SOURCE_KEYS}
            raw["text"] = source["source_text"]
            rendered = bundle.tokenize_row(raw, tokenizer)
            if condition == "correct" and rendered != saved:
                raise ValueError("Re-rendered correct row differs from saved TRAIN tokens/labels")
            ids, labels, prompt = rendered["input_ids"], rendered["labels"], rendered["prompt_tokens"]
            if ids[prompt:] != target_ids or len(ids) > max_length:
                raise ValueError("Changed answer/terminator tokens or context overflow")
            prepared[row["id"] + ":" + condition] = {
                **{key: rendered[key] for key in bundle.TOKEN_KEYS},
                "input_tokens": len(ids), "supervised_tokens": len(target_ids),
                "input_ids_sha256": qualified.sha(qualified.canonical(ids)),
                "labels_sha256": qualified.sha(qualified.canonical(labels)),
                "target_ids_sha256": qualified.sha(qualified.canonical(target_ids)),
                "source_parent_id": source["id"], "source_sha256": qualified.sha(source["source_text"].encode("utf-8")),
                "target_sha256": qualified.sha(saved["target"].encode("utf-8")),
                "training_row_sha256": qualified.sha(qualified.canonical(saved))}
    return prepared


def token_map(prepared):
    return {key: {field: value[field] for field in TOKEN_MAP_FIELDS} for key, value in prepared.items()}


def validate_token_map(prepared):
    actual = qualified.sha(qualified.canonical(token_map(prepared)))
    if actual != TOKEN_MAP_SHA256:
        raise ValueError("Prepared token map differs from frozen local tokenizer audit")
    return actual


def schedule(rows):
    return [(row, enabled, condition) for i, row in enumerate(rows)
            for enabled, condition in CONDITIONS[i % 4:] + CONDITIONS[:i % 4]]


def output_id(row, enabled, condition):
    return row["id"] + (":adapter_on:" if enabled else ":adapter_off:") + condition


def causal_nll(logits, labels, model_loss):
    """Independent causal shift; every nonmasked next-token label contributes once."""
    import torch
    if logits.ndim != 3 or labels.ndim != 2 or logits.shape[:2] != labels.shape or labels.shape[0] != 1:
        raise ValueError("Full single-sequence logits and labels required")
    if labels[0, 0].item() != -100 or not torch.isfinite(logits).all().item():
        raise ValueError("Nonfinite logits or invalid first-label mask")
    shifted = labels[:, 1:]
    count = int((shifted != -100).sum().item())
    if count < 1:
        raise ValueError("No supervised causal tokens")
    # float32 matches Transformers' causal loss upcast; reduce independently by sum/count.
    total = torch.nn.functional.cross_entropy(logits[:, :-1, :].float().reshape(-1, logits.shape[-1]),
        shifted.reshape(-1), ignore_index=-100, reduction="sum").item()
    mean = total / count
    reported = model_loss.float().item()
    if not all(math.isfinite(value) for value in (total, mean, reported)) or not math.isclose(
            mean, reported, rel_tol=LOSS_RTOL, abs_tol=LOSS_ATOL):
        raise ValueError("Independent shifted CE disagrees with model loss or is nonfinite")
    return {"sum_nll": total, "mean_nll": mean, "supervised_tokens": count,
        "model_loss": reported, "numerical_loss_difference": abs(mean - reported)}


def adapter_state(model, expected_enabled):
    state = model.get_model_status()
    if state.enabled is not expected_enabled or state.merged_adapters != [] or state.num_adapter_layers < 1:
        raise ValueError("Adapter enabled/merged state differs")
    if state.active_adapters != ["default"] or state.available_adapters != ["default"]:
        raise ValueError("Exactly the default qualified adapter required")
    if model.training or any(parameter.requires_grad for parameter in model.parameters()):
        raise ValueError("Evaluation requires frozen parameters and eval mode")
    return {"enabled": state.enabled, "active_adapters": state.active_adapters,
        "merged_adapters": state.merged_adapters, "num_adapter_layers": state.num_adapter_layers}


def forward_once(model, prepared, enabled, deadline_utc):
    import torch
    runtime.check_deadline(deadline_utc)
    proof = {"before": adapter_state(model, True)}
    device = next(model.parameters()).device
    tokens = {name: torch.tensor([prepared[name]], device=device) for name in ("input_ids", "labels", "attention_mask")}
    try:
        with (nullcontext() if enabled else model.disable_adapter()), torch.inference_mode():
            proof["during"] = adapter_state(model, enabled)
            output = model(**tokens, use_cache=False, logits_to_keep=0, return_dict=True)
            if output.past_key_values is not None:
                raise ValueError("Unexpected KV cache in fit forward")
            result = causal_nll(output.logits, tokens["labels"], output.loss)
            if result["supervised_tokens"] != prepared["supervised_tokens"]:
                raise ValueError("Causal supervised count differs from frozen answer suffix")
    finally:
        # PEFT's enable_adapters restores active adapters with requires_grad=True.
        # Re-freeze after its context; inference_mode prevents any gradient computation.
        model.requires_grad_(False)
        proof["restored"] = adapter_state(model, True)
    runtime.check_deadline(deadline_utc)
    return {**result, "adapter_state": proof}


def write_run(output, run):
    runtime.write_json(output / "run.json", run)
    with (output / "run.json").open("r+b") as stream:
        os.fsync(stream.fileno())


def run_forwards(model, rows, prepared, output, run, deadline_utc):
    """Stop at the first failure; persist the started attempt before calling the model."""
    completed = Counter()
    try:
        with (output / "results.jsonl").open("x", encoding="utf-8") as stream:
            for index, (row, enabled, condition) in enumerate(schedule(rows)):
                runtime.check_deadline(deadline_utc)
                key = output_id(row, enabled, condition)
                item = prepared[row["id"] + ":" + condition]
                run.update(attempted_outputs=index + 1, active_output_id=key,
                    unattempted_output_ids=run["schedule"][index + 1:])
                write_run(output, run)
                start, failure = time.monotonic(), None
                result = {"id": key, "case_id": row["id"], "record_id": row["record_id"], "work_id": row["work_id"],
                    "adapter_enabled": enabled, "source_condition": condition, "sequence": index + 1,
                    "input_sha256": item["input_ids_sha256"], "identity_sha256": run["identity_sha256"],
                    **{name: item[name] for name in ("labels_sha256", "target_ids_sha256", "input_tokens", "prompt_tokens")}}
                try:
                    result.update(forward_once(model, item, enabled, deadline_utc), status="success")
                except BaseException as error:
                    failure = error
                    result.update(status="error", error_type=type(error).__name__, error=str(error),
                        sum_nll=None, mean_nll=None, supervised_tokens=None)
                result["elapsed_seconds"] = time.monotonic() - start
                stream.write(json.dumps(result, ensure_ascii=False, allow_nan=False) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
                run["recorded_outputs"] += 1
                run["active_output_id"] = None
                if result["status"] == "success":
                    run["completed_outputs"] += 1
                    completed[row["id"]] += 1
                run["completed_cases"] = sum(value == 4 for value in completed.values())
                write_run(output, run)
                print(json.dumps({"status": "train_fit_attempt_recorded", "id": key, "outcome": result["status"]}), flush=True)
                if failure is not None:
                    raise failure
        run["status"] = "completed"
        write_run(output, run)
    except BaseException as error:
        run.update(status="incomplete", error_type=type(error).__name__, error=str(error))
        write_run(output, run)
        raise


def evaluate(args):
    runtime.offline()
    runtime.check_deadline(args.deadline_utc)
    output = Path(args.output).resolve()
    if output.exists():
        raise ValueError("Fit output must be a fresh directory")
    for module in (recall, qualified, frozen, bundle, recall.protocol):
        if runtime.digest(module.__file__) != HELPER_SHA256[Path(module.__file__).name]:
            raise ValueError("Frozen helper identity differs")
    folder = runtime.verified_bundle(args.bundle)
    rows = read_inputs(args.inputs, args.inputs_sha256, folder / "train.jsonl")
    control = read_source_control(args.source_control, args.source_control_sha256, rows)
    contract = runtime.contract_at(folder / "contract.json")
    base = runtime.verify_base(args.base)
    tokenizer_files = {name: base["files"][name] for name in bundle.TOKENIZER_HASHES}
    runtime.checked_files(args.tokenizer, tokenizer_files)
    qualified.verify_adapter(args.adapter, contract, base)
    environment = runtime.gpu_admission()
    output_ids = [output_id(*item) for item in schedule(rows)]
    identity = {"experiment_id": "qualified-train-fit", "diagnostic_scope": "seen TRAIN conditional fit, not translation merit/generalization",
        "inputs_sha256": args.inputs_sha256, "source_control_sha256": args.source_control_sha256,
        "source_control": control, "train_sha256": qualified.TRAIN_SHA256,
        "model_id": runtime.MODEL_ID, "model_revision": runtime.REVISION, "base_files": base["files"],
        "adapter_files": qualified.ADAPTER_FILES, "adapter_metadata": qualified.ADAPTER_METADATA,
        "adapter_step": 280, "adapter_manifest_sha256": qualified.ADAPTER_MANIFEST_SHA256,
        "tokenizer_files": tokenizer_files, "runtime": environment, "runner_sha256": runtime.digest(__file__),
        "helper_sha256": HELPER_SHA256, "bundle_manifest_sha256": runtime.digest(folder / "manifest.json"),
        "schedule": output_ids, "schedule_method": "frozen parent order; left-rotate four conditions by parent index modulo four",
        "seed": 42, "dtype": "bfloat16", "attention_backend": "eager", "use_cache": False,
        "enable_thinking": False, "prompt_template_sha256": qualified.sha(bundle.PROMPT.encode("utf-8")),
        "terminator": bundle.TERMINATOR, "loss_atol": LOSS_ATOL, "loss_rtol": LOSS_RTOL,
        "loss_reduction": "manual causal shift; answer and terminator only; float32 sum/count",
        "local_token_audit_sha256": TOKEN_AUDIT_SHA256, "expected_token_map_sha256": TOKEN_MAP_SHA256,
        "deadline_utc": args.deadline_utc, "generation_performed": False, "training_performed": False}
    run = {**identity, "identity_sha256": None, "status": "preparing", "scheduled_outputs": 80,
        "attempted_outputs": 0, "recorded_outputs": 0, "completed_outputs": 0, "completed_cases": 0,
        "active_output_id": None, "unattempted_output_ids": list(output_ids)}
    output.mkdir(parents=True, exist_ok=False)
    write_run(output, run)
    try:
        import torch
        from transformers import AutoTokenizer, Gemma4ForConditionalGeneration, set_seed
        from peft import PeftModel
        runtime.check_deadline(args.deadline_utc)
        tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, local_files_only=True, trust_remote_code=False)
        context_limit = runtime.read_json(Path(args.base) / "config.json")["text_config"]["max_position_embeddings"]
        prepared = prepare_inputs(rows, folder / "train.jsonl", control, tokenizer, context_limit)
        identity.update(prepared_inputs=token_map(prepared), actual_token_map_sha256=validate_token_map(prepared),
            parent_provenance={key: {field: value[field] for field in ("source_parent_id", "source_sha256", "target_sha256", "training_row_sha256")}
                for key, value in prepared.items()})
        run.update(identity, identity_sha256=qualified.sha(qualified.canonical(identity)), status="loading")
        write_run(output, run)
        runtime.check_deadline(args.deadline_utc)
        set_seed(42)
        base_model = Gemma4ForConditionalGeneration.from_pretrained(args.base, local_files_only=True,
            trust_remote_code=False, use_safetensors=True, device_map={"": 0}, dtype=torch.bfloat16, attn_implementation="eager")
        model = PeftModel.from_pretrained(base_model, args.adapter, local_files_only=True, is_trainable=False)
        model.eval()
        model.requires_grad_(False)
        run["initial_adapter_state"] = adapter_state(model, True)
        run["status"] = "running"
        write_run(output, run)
        run_forwards(model, rows, prepared, output, run, args.deadline_utc)
    except BaseException as error:
        run.update(status="incomplete", error_type=type(error).__name__, error=str(error))
        write_run(output, run)
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("bundle", "base", "tokenizer", "adapter", "inputs", "inputs-sha256",
                 "source-control", "source-control-sha256", "output", "deadline-utc"):
        parser.add_argument("--" + name, required=True)
    evaluate(parser.parse_args(argv))


if __name__ == "__main__":
    main()
