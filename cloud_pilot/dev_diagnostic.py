"""Frozen 24-case, four-condition DEV inference; no scoring or cloud provisioning."""
import argparse
from collections import Counter
from contextlib import nullcontext
import hashlib
import json
from pathlib import Path
import re
import time

try:
    from . import bundle as training_bundle, palref_eval as protocol, runtime
except ImportError:
    import bundle as training_bundle
    import palref_eval as protocol
    import runtime

INPUTS_SHA256 = "06ac58310bf67767fae4124d8e935c808d15debcd8daebce07b583937cd97182"
FIELDS = {"id", "record_id", "work_id", "source_language", "target_language", "source_text"}
IDS = [f"QUALITYDEV1-{i:03d}" for i in range(1, 25)]
WORKS = {"parsig:103", "parsig:112", "parsig:138", "parsig:517"}
ADAPTER_FILES = {"adapter_config.json": "e481bc2a4d4031ca070c3099133a85b22aa5406cb11b4503e3c1873fa0f1bbb5",
                 "adapter_model.safetensors": "e329333a79a30e82dfad7a751939afa71529800570fb6f8b0cfac78427ec2827"}
ADAPTER_CLOUD_MANIFEST = "4e88826bf911ab22e85a6a0b4ecfae131591c6edecbc34fff687af9b57a57a01"
CONDITIONS = {"D0": ("base", "training"), "D1": ("base", "evaluation"),
              "D2": ("adapter", "training"), "D3": ("adapter", "evaluation")}
# Balanced positions and immediate preceding conditions across each four cases.
ORDERS = ((0, 1, 3, 2), (1, 2, 0, 3), (2, 3, 1, 0), (3, 0, 2, 1))


def read_inputs(path):
    data = Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest() != INPUTS_SHA256:
        raise ValueError("DEV input bytes differ from the frozen source-only projection")
    rows = [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]
    if len(rows) != 24 or any(not isinstance(row, dict) or set(row) != FIELDS for row in rows):
        raise ValueError("Exactly 24 six-field source-only records required")
    if [row["id"] for row in rows] != IDS or len({row["record_id"] for row in rows}) != 24:
        raise ValueError("DEV identity or order differs")
    for row in rows:
        if (any(not isinstance(row[key], str) or not row[key].strip() for key in FIELDS)
                or (row["source_language"], row["target_language"]) != ("pal", "fa")
                or not re.fullmatch(r"parsig:\d{9}", row["record_id"])
                or row["work_id"] != row["record_id"][:10]):
            raise ValueError("Invalid source identity or direction")
        training_bundle.reject_controls(row["source_text"])
    if Counter(row["work_id"] for row in rows) != Counter({work: 6 for work in WORKS}):
        raise ValueError("DEV work coverage differs")
    return rows


def messages(row, instruction):
    if instruction == "training":
        return [{"role": "user", "content": training_bundle.PROMPT.format(text=row["source_text"])}]
    if instruction == "evaluation":
        return protocol.messages(row)
    raise ValueError("Unknown instruction condition")


def schedule(rows):
    """Visit four sorted works per length stratum; rotate condition order within work."""
    groups = {work: [row for row in rows if row["work_id"] == work] for work in sorted(WORKS)}
    return [(groups[work][stratum], f"D{condition}") for stratum in range(6)
            for work_index, work in enumerate(groups) for condition in ORDERS[(stratum + work_index) % 4]]


def verify_adapter(adapter, contract, base):
    adapter = Path(adapter).resolve()
    runtime.checked_files(adapter, ADAPTER_FILES)
    provenance = runtime.read_json(adapter.parent / "provenance.json")
    status = runtime.read_json(adapter.parent / "status.json")
    if provenance["model"] != contract["model"] or provenance["base_files"] != base["files"]:
        raise ValueError("Adapter provenance differs from the original frozen base")
    if status.get("status") != "training_complete" or status.get("global_step") != 312:
        raise ValueError("The frozen completed step-312 adapter is required")


def evaluate(args):
    runtime.offline()
    deadline = runtime.check_deadline(args.deadline_utc)
    rows = read_inputs(args.inputs)
    output = Path(args.output).resolve()
    if output.exists():
        raise ValueError("DEV output must be a fresh directory")
    folder = runtime.verified_bundle(args.bundle)
    contract = runtime.contract_at(folder / "contract.json")
    if runtime.digest(training_bundle.__file__) != runtime.digest(folder / "bundle.py"):
        raise ValueError("Executing training-prompt helper differs from the frozen bundle")
    base = runtime.verify_base(args.base)
    tokenizer_files = {name: base["files"][name] for name in ("tokenizer.json", "tokenizer_config.json", "chat_template.jinja")}
    runtime.checked_files(args.tokenizer, tokenizer_files)
    verify_adapter(args.adapter, contract, base)
    environment = runtime.gpu_admission()
    import torch
    from transformers import AutoTokenizer, DynamicCache, Gemma4ForConditionalGeneration, StoppingCriteriaList, set_seed
    from peft import PeftModel
    set_seed(42)
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, local_files_only=True, trust_remote_code=False)
    prepared = {(row["id"], instruction): tokenizer.apply_chat_template(messages(row, instruction), tokenize=True,
        return_dict=False, add_generation_prompt=True, enable_thinking=False) for row in rows for instruction in ("training", "evaluation")}
    context_limit = runtime.read_json(Path(args.base) / "config.json")["text_config"]["max_position_embeddings"]
    if any(not ids or len(ids) + protocol.MAX_TOKENS > context_limit for ids in prepared.values()):
        raise ValueError("Untruncated input plus output ceiling exceeds model context")
    ordered = schedule(rows)
    output_ids = [row["id"] + ":" + condition for row, condition in ordered]
    identity = {"diagnostic_id": "dev-diagnostic-20260927", "inputs_sha256": INPUTS_SHA256,
        "model_id": runtime.MODEL_ID, "model_revision": runtime.REVISION, "base_files": base["files"],
        "adapter_files": ADAPTER_FILES, "adapter_step": 312, "adapter_source_manifest_sha256": ADAPTER_CLOUD_MANIFEST,
        "tokenizer_files": tokenizer_files, "runtime": environment, "runner_sha256": runtime.digest(__file__),
        "protocol_helper_sha256": runtime.digest(protocol.__file__), "bundle_manifest_sha256": runtime.digest(folder / "manifest.json"),
        "training_prompt": training_bundle.PROMPT, "evaluation_system": protocol.SYSTEM, "conditions": CONDITIONS,
        "schedule": output_ids, "schedule_method": "stratum 0..5, sorted works 103/112/138/517, ORDERS[(stratum+work_index)%4]",
        "seed": 42, "max_new_tokens": protocol.MAX_TOKENS, "max_generation_seconds": protocol.CASE_SECONDS,
        "eos_token_ids": protocol.EOS, "decoding": "greedy", "enable_thinking": False, "fresh_context_each_case": True,
        "retrieval": "none", "scoring_performed": False, "deadline_utc": args.deadline_utc}
    identity_sha = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    run = {**identity, "identity_sha256": identity_sha, "status": "running", "scheduled_outputs": 96,
        "attempted_outputs": 0, "completed_outputs": 0, "completed_cases": 0,
        "unattempted_output_ids": list(output_ids), "case_metadata": []}
    output.mkdir(parents=True, exist_ok=False)
    runtime.write_json(output / "run.json", run)
    try:
        runtime.check_deadline(args.deadline_utc)
        base_model = Gemma4ForConditionalGeneration.from_pretrained(args.base, local_files_only=True,
            trust_remote_code=False, use_safetensors=True, device_map={"": 0}, dtype=torch.bfloat16, attn_implementation="eager")
        model = PeftModel.from_pretrained(base_model, args.adapter, local_files_only=True, is_trainable=False)
        model.eval()
        completed = Counter()
        with (output / "predictions.jsonl").open("x", encoding="utf-8") as stream:
            for index, (row, condition) in enumerate(ordered):
                runtime.check_deadline(args.deadline_utc)
                model_condition, instruction = CONDITIONS[condition]
                ids = prepared[row["id"], instruction]
                tokens = torch.tensor([ids], device="cuda")
                start, failure, new_ids = time.monotonic(), None, []
                stopper = protocol.GenerationDeadline(start, deadline)
                try:
                    with (model.disable_adapter() if model_condition == "base" else nullcontext()), torch.inference_mode():
                        generated = model.generate(input_ids=tokens, attention_mask=torch.ones_like(tokens),
                            past_key_values=DynamicCache(), use_cache=True, do_sample=False, num_beams=1,
                            max_new_tokens=protocol.MAX_TOKENS, pad_token_id=0, eos_token_id=protocol.EOS,
                            stopping_criteria=StoppingCriteriaList([stopper]))
                    new_ids = generated[0, len(ids):].tolist()
                    elapsed = time.monotonic() - start
                    hit_cap = len(new_ids) >= protocol.MAX_TOKENS and new_ids[-1] not in protocol.EOS
                    result = protocol.prediction(row, tokenizer.decode(new_ids, skip_special_tokens=True), elapsed,
                        timed_out=stopper.reason is not None, hit_cap=hit_cap)
                except BaseException as error:
                    failure = error
                    result = protocol.prediction(row, "", time.monotonic() - start)
                    result.update(status="error", error_type=type(error).__name__, error=str(error))
                    hit_cap = False
                result.update(id=output_ids[index], case_id=row["id"], record_id=row["record_id"], work_id=row["work_id"],
                    condition=condition, model_condition=model_condition, instruction=instruction, sequence=index + 1,
                    identity_sha256=identity_sha, input_tokens=len(ids), output_tokens=len(new_ids), output_token_ids=new_ids,
                    hit_output_cap_without_eos=hit_cap, stop_reason=stopper.reason,
                    rendered_input_ids_sha256=hashlib.sha256(json.dumps(ids).encode()).hexdigest())
                stream.write(json.dumps(result, ensure_ascii=False) + "\n")
                stream.flush()
                run["attempted_outputs"] += 1
                run["unattempted_output_ids"] = output_ids[index + 1:]
                if result["status"] in {"success", "abstain"}:
                    run["completed_outputs"] += 1
                    completed[row["id"]] += 1
                run["completed_cases"] = sum(count == 4 for count in completed.values())
                run["case_metadata"].append({key: result[key] for key in ("id", "case_id", "condition", "status", "input_tokens", "output_tokens")})
                runtime.write_json(output / "run.json", run)
                print(json.dumps({"status": "dev_attempt_recorded", "id": result["id"], "outcome": result["status"],
                                  "attempted_outputs": run["attempted_outputs"], "scheduled_outputs": 96}), flush=True)
                if failure is not None:
                    raise failure
                if result["status"] not in {"success", "abstain"}:
                    raise RuntimeError("First-attempt generation incomplete: " + result["status"])
        run["status"] = "completed"
        runtime.write_json(output / "run.json", run)
    except BaseException as error:
        run.update(status="incomplete", error_type=type(error).__name__, error=str(error))
        runtime.write_json(output / "run.json", run)
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("bundle", "base", "tokenizer", "inputs", "adapter", "output", "deadline-utc"):
        parser.add_argument("--" + name, required=True)
    evaluate(parser.parse_args(argv))


if __name__ == "__main__":
    main()
