"""Source-only inference for the unchanged PAL-REF v1 Pahlavi-to-Persian cases.

This adapter performs no semantic scoring and never provisions cloud resources.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

try:
    from . import runtime
except ImportError:
    import runtime

BENCHMARK_SHA256 = "a3932f7510f101376cc91c47bb23f3c9872656c41f563701fa3dcb2b6c89a5e8"
ORIGINAL_INPUTS_SHA256 = "13124e8683099a1b3cf1bda56071de1a004eed83c895ce65e26ffd939f2bd759"
INPUTS_SHA256 = "0616b50838339e9b520f06fe8b2ed9c0fd9b399b67c8f68cd680a62115a12f37"
PROMPT = "Translate the supplied text from {source_language} into {target_language}. Preserve its meaning, participants, negation, names, quantities, and uncertainty. Do not add explanations, citations, or facts. Return only the translation. For Middle Persian output, use scholarly Latin transcription. If you cannot translate it, return exactly [UNRESOLVED]."
SYSTEM = PROMPT.format(source_language="Middle Persian (Pahlavi), scholarly Latin transcription", target_language="Persian (Farsi)")
FIELDS = {"id", "passage_id", "work_id", "source_language", "target_language", "source_text", "track"}
IDS = [f"PALREF1-{i:03d}:pal>fa" for i in range(1, 41)]
MAX_TOKENS = 4096
CASE_SECONDS = 1200
EOS = [1, 106, 50]


def read_inputs(path):
    data = Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest() != INPUTS_SHA256:
        raise ValueError("Input bytes differ from the frozen forty-case source-only projection")
    rows = [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]
    if len(rows) != 40 or any(not isinstance(row, dict) or set(row) != FIELDS for row in rows):
        raise ValueError("Exactly forty original seven-field input records are required")
    if [row["id"] for row in rows] != IDS:
        raise ValueError("Frozen case coverage or ordering differs")
    for row in rows:
        if any(not isinstance(row[key], str) or not row[key].strip() for key in FIELDS):
            raise ValueError("Every original input field must be a nonempty string")
        if (row["source_language"], row["target_language"], row["track"]) != ("pal", "fa", "forward_translation") or row["passage_id"] != row["id"].split(":")[0]:
            raise ValueError("Wrong original passage identity or translation direction")
    return rows


def messages(row):
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": row["source_text"]}]


class GenerationDeadline:
    """Transformers stopping callable; native job timeout remains the outer bound."""
    def __init__(self, start, deadline):
        self.start, self.deadline = start, deadline
        self.reason = None

    def __call__(self, input_ids, scores, **kwargs):
        if datetime.now(timezone.utc) >= self.deadline:
            self.reason = "global_deadline"
        elif time.monotonic() - self.start >= CASE_SECONDS:
            self.reason = "case_timeout"
        return self.reason is not None


def prediction(row, text, elapsed, timed_out=False, hit_cap=False):
    status = "timeout" if timed_out or elapsed > CASE_SECONDS else (
        "error" if hit_cap or not text.strip() else "abstain" if text.strip() == "[UNRESOLVED]" else "success")
    return {"id": row["id"], "input_sha256": hashlib.sha256(row["source_text"].encode("utf-8")).hexdigest(),
            "status": status, "text": text, "elapsed_seconds": elapsed}


def evaluate(args):
    runtime.offline()
    deadline = runtime.check_deadline(args.deadline_utc)
    rows = read_inputs(args.inputs)
    output = Path(args.output).resolve()
    if output.exists():
        raise ValueError("Evaluation output must be a fresh directory")
    bundle = runtime.verified_bundle(args.bundle)
    contract = runtime.contract_at(bundle / "contract.json")
    base = runtime.verify_base(args.base)
    tokenizer_files = {name: base["files"][name] for name in ("tokenizer.json", "tokenizer_config.json", "chat_template.jinja")}
    runtime.checked_files(args.tokenizer, tokenizer_files)
    adapter_files = {}
    if args.adapter:
        adapter = Path(args.adapter).resolve()
        provenance = runtime.read_json(adapter.parent / "provenance.json")
        if provenance["model"] != contract["model"] or provenance["base_files"] != base["files"]:
            raise ValueError("Adapter provenance differs from the original frozen base")
        adapter_files = {name: runtime.digest(adapter / name) for name in ("adapter_config.json", "adapter_model.safetensors")}
    environment = runtime.gpu_admission()
    import torch
    from transformers import AutoTokenizer, DynamicCache, Gemma4ForConditionalGeneration, StoppingCriteriaList, set_seed
    from peft import PeftModel
    set_seed(42)
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, local_files_only=True, trust_remote_code=False)
    prepared = [(row, tokenizer.apply_chat_template(messages(row), tokenize=True, return_dict=False,
                 add_generation_prompt=True, enable_thinking=False)) for row in rows]
    context_limit = runtime.read_json(Path(args.base) / "config.json")["text_config"]["max_position_embeddings"]
    if any(not ids or len(ids) + MAX_TOKENS > context_limit for _, ids in prepared):
        raise ValueError("An untruncated input plus the fixed output ceiling exceeds model context")
    runtime.check_deadline(args.deadline_utc)
    output.mkdir(parents=True, exist_ok=False)
    run = {"benchmark_id": "pal-reference-v1", "benchmark_manifest_sha256": BENCHMARK_SHA256,
        "original_inputs_sha256": ORIGINAL_INPUTS_SHA256, "source_only_inputs_sha256": INPUTS_SHA256,
        "model_id": runtime.MODEL_ID, "model_revision": runtime.REVISION,
        "adapter_sha256_or_none": adapter_files.get("adapter_model.safetensors", "none"), "adapter_files": adapter_files,
        "runtime": json.dumps(environment, sort_keys=True), "runner_sha256": runtime.digest(__file__),
        "bundle_manifest_sha256": runtime.digest(bundle / "manifest.json"), "base_files": base["files"],
        "tokenizer_files": tokenizer_files, "chat_template_sha256": tokenizer_files["chat_template.jinja"],
        "decoding": "greedy", "seed": 42, "max_new_tokens": MAX_TOKENS, "max_generation_seconds": CASE_SECONDS,
        "retrieval": "none", "reviewer_id": "", "reviewer_type": "unassigned", "review_status": "provisional_single_review",
        "fresh_context_each_case": True, "system_prompt": PROMPT, "rendered_system_instruction": SYSTEM,
        "enable_thinking": False, "direction": "pal>fa", "deadline_utc": args.deadline_utc,
        "condition": "bf16-original-plus-adapter" if args.adapter else "bf16-original",
        "status": "running", "completed_cases": 0, "case_metadata": []}
    runtime.write_json(output / "run.json", run)
    try:
        model = Gemma4ForConditionalGeneration.from_pretrained(args.base, local_files_only=True,
            trust_remote_code=False, use_safetensors=True, device_map={"": 0}, dtype=torch.bfloat16, attn_implementation="eager")
        if args.adapter:
            model = PeftModel.from_pretrained(model, args.adapter, local_files_only=True, is_trainable=False)
        model.eval()
        with (output / "predictions.jsonl").open("x", encoding="utf-8") as stream:
            for row, ids in prepared:
                runtime.check_deadline(args.deadline_utc)
                tokens = torch.tensor([ids], device="cuda")
                start = time.monotonic()
                stopper = GenerationDeadline(start, deadline)
                try:
                    with torch.inference_mode():
                        generated = model.generate(input_ids=tokens, attention_mask=torch.ones_like(tokens),
                            past_key_values=DynamicCache(), use_cache=True, do_sample=False, num_beams=1,
                            max_new_tokens=MAX_TOKENS, pad_token_id=0, eos_token_id=EOS,
                            stopping_criteria=StoppingCriteriaList([stopper]))
                    new_ids = generated[0, len(ids):].tolist()
                    elapsed = time.monotonic() - start
                    hit_cap = len(new_ids) >= MAX_TOKENS and new_ids[-1] not in EOS
                    result = prediction(row, tokenizer.decode(new_ids, skip_special_tokens=True), elapsed,
                                        timed_out=stopper.reason is not None, hit_cap=hit_cap)
                except Exception:
                    result = prediction(row, "", time.monotonic() - start)
                    result["status"] = "error"
                    stream.write(json.dumps(result, ensure_ascii=False) + "\n")
                    stream.flush()
                    run["completed_cases"] += 1
                    raise
                stream.write(json.dumps(result, ensure_ascii=False) + "\n")
                stream.flush()
                run["completed_cases"] += 1
                run["case_metadata"].append({"id": row["id"], "input_tokens": len(ids), "output_tokens": len(new_ids),
                                             "hit_output_cap_without_eos": hit_cap, "stop_reason": stopper.reason})
                runtime.write_json(output / "run.json", run)
                print(json.dumps({"status": "palref_case_complete", "completed_cases": run["completed_cases"],
                                  "total_cases": 40, "id": row["id"], "outcome": result["status"]}), flush=True)
                runtime.check_deadline(args.deadline_utc)
        run["status"] = "completed"
        runtime.write_json(output / "run.json", run)
        print(json.dumps({"status": "palref_evaluation_complete", "count": 40}), flush=True)
    except BaseException as error:
        run.update(status="incomplete", error_type=type(error).__name__, error=str(error))
        runtime.write_json(output / "run.json", run)
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("bundle", "base", "tokenizer", "inputs", "output", "deadline-utc"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--adapter")
    evaluate(parser.parse_args(argv))


if __name__ == "__main__":
    main()
