"""Frozen Qwen DEV plain/assisted inference on already-local assets; no submission."""
import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import time

try:
    from . import dev_assisted as shared
except ImportError:
    import dev_assisted as shared

runtime, protocol = shared.runtime, shared.protocol
MODEL_ID = "Qwen/Qwen3.6-27B"
REVISION = "6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
SOURCE_IDENTITY_SHA256 = "b0d6d51fe7603d4a955be4dec41b551100a4ca401b5d1d8a1a5a4c8d5427f8ce"
SHARED_HELPER_SHA256 = "4334db8c1097c220dbcce75b3d30287a29c43c5482ab71313c3db9cf287fec4d"
PRESENCE_SHA256 = "299e25706752946ff86b60af71d77758b77acc932abd3adcae7946b4cae6279e"
EOS, PAD = [248046, 248044], 248044
SAMPLING = {"do_sample": True, "temperature": 0.7, "top_p": 0.8, "top_k": 20,
            "min_p": 0.0, "repetition_penalty": 1.0, "num_beams": 1}
CANARY_SECONDS, CANARY_TOKENS = 180, 8
NONTHINKING_SUFFIX = "<|im_start|>assistant\n<think>\n\n</think>\n\n"


def verify_snapshot(base, identity_path):
    """Hash every supplied publisher file, including all 15 weight shards."""
    data = Path(identity_path).read_bytes()
    if shared.sha(data) != SOURCE_IDENTITY_SHA256:
        raise ValueError("Frozen Qwen source identity differs")
    identity = json.loads(data)
    if (identity["model_id"], identity["revision"]) != (MODEL_ID, REVISION):
        raise ValueError("Qwen model/revision differs")
    files = {name: value["sha256"] for name, value in identity["files"].items()}
    shards = identity["weight_shards_metadata_only"]
    if len(shards) != 15 or len({entry["rfilename"] for entry in shards}) != 15:
        raise ValueError("Exactly 15 publisher shards required")
    files.update({entry["rfilename"]: entry["lfs"]["sha256"] for entry in shards})
    runtime.checked_files(base, files)
    base = Path(base)
    for entry in shards:
        if (base / entry["rfilename"]).stat().st_size != entry["size"]:
            raise ValueError("Publisher shard size differs")
    config = runtime.read_json(base / "config.json")
    generation = runtime.read_json(base / "generation_config.json")
    index = runtime.read_json(base / "model.safetensors.index.json")
    if config != identity["config"] or generation != identity["generation_config"] or "quantization_config" in config:
        raise ValueError("Original BF16 Qwen configuration required")
    if (generation["eos_token_id"], generation["pad_token_id"]) != (EOS, PAD):
        raise ValueError("Qwen generation token identity differs")
    if (set(index["weight_map"].values()) != {entry["rfilename"] for entry in shards}
            or len(index["weight_map"]) != identity["weight_parameter_mapping_keys"]):
        raise ValueError("Qwen shard/index coverage differs")
    ignored = sorted(name for name in index["weight_map"] if name.startswith(("model.visual.", "mtp.")))
    return identity, files, ignored


def check_loading(info):
    required = {"missing_keys", "unexpected_keys", "mismatched_keys", "error_msgs"}
    if not isinstance(info, dict) or not required <= set(info):
        raise ValueError("Native loading diagnostics required")
    if any(info[key] for key in ("missing_keys", "mismatched_keys", "error_msgs", "conversion_errors") if key in info):
        raise ValueError("Missing/mismatched Qwen language weights or loading errors")
    if any(not name.startswith(("model.visual.", "mtp.")) for name in info["unexpected_keys"]):
        raise ValueError("Unexpected non-vision/MTP checkpoint weights")
    return {key: sorted(info[key]) for key in required}


def check_time(deadline):
    if datetime.now(timezone.utc) >= deadline:
        raise TimeoutError("Global/canary deadline reached")


def generate_ids(model, ids, deadline, max_tokens=protocol.MAX_TOKENS, min_tokens=0):
    import torch
    from transformers import DynamicCache, LogitsProcessorList, StoppingCriteriaList
    try:
        from .qwen_presence import GeneratedTokenPresencePenalty
    except ImportError:
        from qwen_presence import GeneratedTokenPresencePenalty
    check_time(deadline)
    start = time.monotonic()
    stopper = protocol.GenerationDeadline(start, deadline)
    tokens = torch.tensor([ids], device="cuda")
    with torch.inference_mode():
        generated = model.generate(input_ids=tokens, attention_mask=torch.ones_like(tokens),
            past_key_values=DynamicCache(config=model.config), use_cache=True, logits_to_keep=1,
            max_new_tokens=max_tokens, min_new_tokens=min_tokens, pad_token_id=PAD, eos_token_id=EOS,
            logits_processor=LogitsProcessorList([GeneratedTokenPresencePenalty(len(ids), 1.5)]),
            stopping_criteria=StoppingCriteriaList([stopper]), **SAMPLING)
    new_ids = generated[0, len(ids):].tolist()
    torch.cuda.synchronize()
    stopper(None, None)
    return new_ids, time.monotonic() - start, stopper.reason


def canary(model, tokenizer, prepared, deadline):
    """Two synthetic requests plus longest real prompt prefill; zero DEV attempts."""
    import torch
    from transformers import DynamicCache, set_seed
    deadline = min(deadline, datetime.now(timezone.utc) + timedelta(seconds=CANARY_SECONDS))
    synthetic = [{"role": "system", "content": "This is a short API functionality check."},
                 {"role": "user", "content": "Write the numbers one through six in English."}]
    rendered = tokenizer.apply_chat_template(synthetic, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    ids = tokenizer.apply_chat_template(synthetic, tokenize=True, return_dict=False, add_generation_prompt=True, enable_thinking=False)
    if not rendered.endswith(NONTHINKING_SUFFIX) or tokenizer.encode(rendered, add_special_tokens=False) != ids:
        raise ValueError("Native nonthinking tokenizer/template canary differs")
    attempts = []
    for _ in range(2):
        check_time(deadline)
        set_seed(42)
        torch.cuda.reset_peak_memory_stats()
        new_ids, elapsed, reason = generate_ids(model, ids, deadline, max_tokens=CANARY_TOKENS, min_tokens=3)
        if reason is not None or len(new_ids) < 3:
            raise RuntimeError("Synthetic cached-decoding canary incomplete")
        attempts.append({"output_token_ids": new_ids, "elapsed_seconds": elapsed,
                         "seconds_per_output_token": elapsed / len(new_ids),
                         "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
                         "peak_reserved_bytes": torch.cuda.max_memory_reserved()})
    if attempts[0]["output_token_ids"] != attempts[1]["output_token_ids"]:
        raise RuntimeError("Same-seed fresh-request synthetic canary differs")
    key, longest = max(prepared.items(), key=lambda item: len(item[1]))
    check_time(deadline)
    torch.cuda.reset_peak_memory_stats()
    torch.cuda.synchronize()
    start = time.monotonic()
    tokens = torch.tensor([longest], device="cuda")
    with torch.inference_mode():
        prefill = model(input_ids=tokens, attention_mask=torch.ones_like(tokens),
            past_key_values=DynamicCache(config=model.config), use_cache=True, logits_to_keep=1, return_dict=True)
    torch.cuda.synchronize()
    if tuple(prefill.logits.shape) != (1, 1, model.config.vocab_size) or not torch.isfinite(prefill.logits).all().item():
        raise RuntimeError("Longest-prompt prefill returned invalid logits")
    elapsed = time.monotonic() - start
    check_time(deadline)
    result = {"status": "passed", "synthetic_only_generation": True, "experimental_attempts": 0,
        "same_seed_repeatability": True, "synthetic_messages": synthetic, "synthetic_input_tokens": len(ids),
        "synthetic_max_new_tokens": CANARY_TOKENS, "synthetic_min_new_tokens": 3, "attempts": attempts,
        "longest_prompt_prefill": {"id": key[0] + ":" + key[1], "input_tokens": len(longest),
            "elapsed_seconds": elapsed, "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
            "peak_reserved_bytes": torch.cuda.max_memory_reserved(), "output_generated": False},
        "maximum_seconds": CANARY_SECONDS, "deadline_utc": deadline.isoformat()}
    del prefill, tokens
    torch.cuda.empty_cache()
    return result


def evaluate(args):
    runtime.offline()
    deadline = runtime.check_deadline(args.deadline_utc)
    rows = shared.frozen.read_inputs(args.inputs)
    witnesses = shared.read_evidence(args.evidence, args.audit, rows)
    output = Path(args.output).resolve()
    if output.exists():
        raise ValueError("Qwen DEV output must be a fresh directory")
    if runtime.digest(shared.__file__) != SHARED_HELPER_SHA256 or runtime.digest(protocol.__file__) != shared.PROTOCOL_SHA256:
        raise ValueError("Frozen shared prompt/evaluation helper differs")
    presence_path = Path(__file__).with_name("qwen_presence.py")
    if runtime.digest(presence_path) != PRESENCE_SHA256:
        raise ValueError("Frozen presence-penalty helper differs")
    source, files, ignored = verify_snapshot(args.base, args.source_identity)
    environment = runtime.gpu_admission()
    import torch
    import transformers
    from transformers import AutoTokenizer, Qwen3_5ForCausalLM, set_seed
    runtime.checked_files(Path(transformers.__file__).parent,
        {name: entry["official_sha256"] for name, entry in source["runtime_source_verification"].items()})
    tokenizer = AutoTokenizer.from_pretrained(args.base, local_files_only=True, trust_remote_code=False)
    if (tokenizer.eos_token_id != EOS[0] or tokenizer.pad_token_id != PAD
            or tokenizer.convert_tokens_to_ids("<|im_end|>") != EOS[0]
            or tokenizer.convert_tokens_to_ids("<|endoftext|>") != PAD):
        raise ValueError("Native Qwen special-token identities differ")
    prompts = {(row["id"], condition): shared.messages(row, condition, witnesses[row["id"]])
               for row in rows for condition in shared.CONDITIONS}
    prepared = {key: tokenizer.apply_chat_template(value, tokenize=True, return_dict=False,
        add_generation_prompt=True, enable_thinking=False) for key, value in prompts.items()}
    limit = source["config"]["text_config"]["max_position_embeddings"]
    if any(not ids or len(ids) + protocol.MAX_TOKENS > limit for ids in prepared.values()):
        raise ValueError("Untruncated Qwen prompt plus output cap exceeds context")
    ordered = shared.schedule(rows)
    output_ids = [row["id"] + ":" + condition for row, condition in ordered]
    identity = {"experiment_id": "dev-assisted-qualified-20260927", "model_id": MODEL_ID, "model_revision": REVISION,
        "source_identity_sha256": SOURCE_IDENTITY_SHA256, "base_files": files, "adapter": None,
        "inputs_sha256": shared.frozen.INPUTS_SHA256, "evidence_sha256": shared.EVIDENCE_SHA256,
        "audit_sha256": shared.AUDIT_SHA256, "shared_helper_sha256": SHARED_HELPER_SHA256,
        "presence_helper_sha256": PRESENCE_SHA256, "protocol_helper_sha256": shared.PROTOCOL_SHA256,
        "local_evaluation_contract_sha256": shared.LOCAL_EVALUATION_CONTRACT_SHA256,
        "runner_sha256": runtime.digest(__file__), "runtime": environment, "system_instruction": protocol.SYSTEM,
        "common_caution": shared.CAUTION, "conditions": shared.CONDITIONS, "schedule": output_ids,
        "seed": 42, "seed_policy": "one reset after canary, continuous stream across experimental schedule",
        "sampling": SAMPLING, "presence_penalty": 1.5, "presence_scope": "distinct generated response tokens only",
        "max_new_tokens": protocol.MAX_TOKENS, "max_generation_seconds": protocol.CASE_SECONDS,
        "eos_token_ids": EOS, "pad_token_id": PAD, "enable_thinking": False, "logits_to_keep": 1,
        "fresh_context_each_case": True, "scoring_performed": False, "expert_adjudicated": False,
        "deadline_utc": args.deadline_utc, "ignored_checkpoint_vision_mtp_keys": ignored,
        "prompts": [{"id": row["id"] + ":" + condition, "messages": prompts[row["id"], condition],
            "input_tokens": len(prepared[row["id"], condition]),
            "rendered_input_ids_sha256": shared.sha(shared.canonical(prepared[row["id"], condition]))} for row, condition in ordered]}
    identity_sha = shared.sha(shared.canonical(identity))
    run = {**identity, "identity_sha256": identity_sha, "status": "running", "scheduled_outputs": 48,
        "attempted_outputs": 0, "completed_outputs": 0, "completed_cases": 0,
        "unattempted_output_ids": list(output_ids), "case_metadata": [], "canary": {"status": "not_started"}}
    output.mkdir(parents=True, exist_ok=False)
    runtime.write_json(output / "run.json", run)
    try:
        check_time(deadline)
        model, loading = Qwen3_5ForCausalLM.from_pretrained(args.base, local_files_only=True, trust_remote_code=False,
            use_safetensors=True, device_map={"": 0}, dtype=torch.bfloat16, attn_implementation="eager", output_loading_info=True)
        run["loading_info"] = check_loading(loading)
        if model.dtype != torch.bfloat16 or model.config.model_type != "qwen3_5_text":
            raise ValueError("Native unquantized BF16 text model required")
        model.eval()
        run["canary"] = {"status": "running"}
        runtime.write_json(output / "run.json", run)
        run["canary"] = canary(model, tokenizer, prepared, deadline)
        set_seed(42)
        runtime.write_json(output / "run.json", run)
        completed = Counter()
        with (output / "predictions.jsonl").open("x", encoding="utf-8") as stream:
            for index, (row, condition) in enumerate(ordered):
                check_time(deadline)
                ids = prepared[row["id"], condition]
                start, failure, new_ids, hit_cap, reason = time.monotonic(), None, [], False, None
                try:
                    new_ids, elapsed, reason = generate_ids(model, ids, deadline)
                    hit_cap = len(new_ids) >= protocol.MAX_TOKENS and new_ids[-1] not in EOS
                    result = protocol.prediction(row, tokenizer.decode(new_ids, skip_special_tokens=True), elapsed,
                        timed_out=reason is not None, hit_cap=hit_cap)
                except BaseException as error:
                    failure = error
                    result = protocol.prediction(row, "", time.monotonic() - start)
                    result.update(status="error", error_type=type(error).__name__, error=str(error))
                result.update(id=output_ids[index], case_id=row["id"], record_id=row["record_id"], work_id=row["work_id"],
                    condition=condition, sequence=index + 1, identity_sha256=identity_sha,
                    input_tokens=len(ids), output_tokens=len(new_ids), output_token_ids=new_ids,
                    hit_output_cap_without_eos=hit_cap, stop_reason=reason,
                    rendered_input_ids_sha256=shared.sha(shared.canonical(ids)))
                stream.write(json.dumps(result, ensure_ascii=False) + "\n")
                stream.flush()
                run["attempted_outputs"] += 1
                run["unattempted_output_ids"] = output_ids[index + 1:]
                if result["status"] in {"success", "abstain"}:
                    run["completed_outputs"] += 1
                    completed[row["id"]] += 1
                run["completed_cases"] = sum(count == 2 for count in completed.values())
                run["case_metadata"].append({key: result[key] for key in ("id", "condition", "status", "input_tokens", "output_tokens")})
                runtime.write_json(output / "run.json", run)
                print(json.dumps({"status": "dev_attempt_recorded", "id": result["id"], "outcome": result["status"]}), flush=True)
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
    for name in ("base", "source-identity", "inputs", "evidence", "audit", "output", "deadline-utc"):
        parser.add_argument("--" + name, required=True)
    evaluate(parser.parse_args(argv))


if __name__ == "__main__":
    main()
