"""One offline Gemma4 adapter experiment. This program never provisions cloud resources."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import re
import sys
import time

MODEL_ID = "google/gemma-4-31B-it"
REVISION = "842da3794eaa0b77d5f08bae87a17459d91ff475"
TARGETS = r"^model\.language_model\.layers\.\d+\.(?:self_attn\.(?:q_proj|k_proj|v_proj|o_proj)|mlp\.(?:gate_proj|up_proj|down_proj))$"
PINS = {"torch": "2.11.0+cu128", "transformers": "5.13.1", "peft": "0.21.0",
        "bitsandbytes": "0.50.2", "accelerate": "1.14.0", "tokenizers": "0.22.2",
        "huggingface-hub": "1.23.0", "safetensors": "0.8.0"}
READINESS = {"full_training_authorized", "linux_container_verified", "stage_dev_ready",
             "local_model_verified", "cloud_controls_verified", "base_weights_verified",
             "transfer_roundtrip_verified", "adapter_export_roundtrip_verified"}
EXTRA_EVAL_SHA256 = "da52b3026596ce843bc015959bbc17a4b6ee8bfa3af4206506d152ea975de06e"
EXTRA_EVAL_IDS = {"STAGEDEV-PROP-S1-001", "STAGEDEV-PROP-S1-005", "STAGEDEV-PROP-S2-004",
                  "STAGEDEV-PROP-S2-006", "STAGEDEV-PROP-S3-003", "STAGEDEV-PROP-S3-007"}
CLOUD_FIRST_POLICY = {"mode": "cloud_first", "local_validation_required_before_delivery": True}


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text("utf-8"))


def write_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", "utf-8")
    os.replace(temporary, path)


def environment():
    packages = {}
    for name in PINS:
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    return {"system": platform.system(), "machine": platform.machine(),
            "python": platform.python_version(), "packages": packages,
            "runtime_sha256": digest(__file__)}


def check_deadline(value):
    if not value:
        raise ValueError("An explicit --deadline-utc is required")
    deadline = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if deadline.tzinfo is None:
        raise ValueError("Deadline must include its UTC offset")
    if datetime.now(timezone.utc) >= deadline:
        raise TimeoutError("Run deadline reached; the outer launcher must also bound execution")
    return deadline


def checked_files(root, files):
    root = Path(root).resolve()
    if not isinstance(files, dict) or not files:
        raise ValueError("Nonempty checksum mapping required")
    for name, expected in files.items():
        path = (root / name).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError("Invalid artifact path: " + name)
        expected = expected.get("sha256") if isinstance(expected, dict) else expected
        if not isinstance(expected, str) or not re.fullmatch(r"[a-f0-9]{64}", expected) or digest(path) != expected:
            raise ValueError("Artifact checksum mismatch: " + name)


def verified_bundle(folder):
    bundle = Path(folder).resolve()
    manifest = read_json(bundle / "manifest.json")
    checked_files(bundle, manifest["files"])
    if not {"train.jsonl", "dev-inputs.jsonl", "runtime.py", "bundle.py", "contract.json"} <= set(manifest["files"]):
        raise ValueError("Data, verifier or driver missing from bundle manifest")
    if digest(bundle / "runtime.py") != digest(__file__):
        raise ValueError("Executing driver differs from the verified bundle")
    spec = importlib.util.spec_from_file_location("_pilot_bundle_verifier", bundle / "bundle.py")
    verifier = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)
    verifier.verify(bundle)
    return bundle


def contract_at(path):
    contract = read_json(path)
    model = contract["model"]
    if contract.get("schema_version") != 1 or (model["id"], model["revision"], model["architecture"]) != (
            MODEL_ID, REVISION, "Gemma4ForConditionalGeneration"):
        raise ValueError("Unexpected model contract")
    generation = contract["generation"]
    if generation["do_sample"] is not False or generation["enable_thinking"] is not False or generation["pad_token_id"] != 0 or generation["eos_token_id"] != [1, 106, 50]:
        raise ValueError("Generation contract differs from frozen nonthinking policy")
    if not 1 <= generation["max_new_tokens"] <= 1024:
        raise ValueError("Invalid generation token cap")
    return contract


def bundled_contract(args):
    bundle = verified_bundle(args.bundle)
    if Path(args.contract).resolve() != bundle / "contract.json":
        raise ValueError("Execution requires this verified bundle's contract.json")
    return bundle, contract_at(bundle / "contract.json")


def resume_checkpoint(checkpoint, output):
    checkpoint = Path(checkpoint).resolve()
    if checkpoint == output or not checkpoint.is_relative_to(output):
        raise ValueError("Resume must name a checkpoint inside this run")
    if (output / "resume-checkpoint.json").exists():
        raise ValueError("Resume checkpoint record already exists; preserve this run")
    required = {"trainer_state.json", "optimizer.pt", "scheduler.pt", "rng_state.pth",
                "adapter_config.json", "adapter_model.safetensors"}
    for name in required:
        path = checkpoint / name
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError("Missing or empty resume checkpoint artifact: " + name)
    status = read_json(output / "status.json")
    step = read_json(checkpoint / "trainer_state.json")["global_step"]
    if status.get("status") != "canary_pass" or type(step) is not int or step < 1 or step != status.get("global_step"):
        raise ValueError("Checkpoint step must match the passing canary")
    files = {}
    for path in sorted(checkpoint.rglob("*")):
        if not path.resolve().is_relative_to(checkpoint):
            raise ValueError("Checkpoint artifact escapes its directory")
        if path.is_file():
            files[path.relative_to(checkpoint).as_posix()] = digest(path)
    return checkpoint, {"checkpoint": checkpoint.relative_to(output).as_posix(),
                        "global_step": step, "files": files}


def verify_base(folder):
    folder = Path(folder).resolve()
    provenance = read_json(folder / "provenance.json")
    if (provenance.get("model_id"), provenance.get("revision")) != (MODEL_ID, REVISION):
        raise ValueError("Base snapshot identity mismatch")
    checked_files(folder, provenance["files"])
    config = read_json(folder / "config.json")
    if config.get("architectures") != ["Gemma4ForConditionalGeneration"] or config.get("quantization_config"):
        raise ValueError("Original unquantized Google base required")
    if config["text_config"].get("num_kv_shared_layers") != 0:
        raise ValueError("Unexpected shared-KV architecture")
    index = read_json(folder / "model.safetensors.index.json")
    required = {"config.json", "generation_config.json", "model.safetensors.index.json",
                "tokenizer.json", "tokenizer_config.json", "chat_template.jinja", *index["weight_map"].values()}
    if not required <= set(provenance["files"]):
        raise ValueError("Base provenance does not cover every required shard")
    return provenance


def load_rows(path, max_length):
    rows = [json.loads(line) for line in Path(path).read_text("utf-8").splitlines() if line.strip()]
    if not rows or len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Training examples must be nonempty and have unique IDs")
    for row in rows:
        ids, mask, labels = row["input_ids"], row["attention_mask"], row["labels"]
        if not isinstance(ids, list) or not 1 <= len(ids) <= max_length or len(ids) != len(mask) or len(ids) != len(labels):
            raise ValueError("Invalid tokenized row: " + row["id"])
        if any(type(x) is not int or x < 0 or x >= 262144 for x in ids) or any(x != 1 for x in mask):
            raise ValueError("Invalid token IDs or unpadded mask")
        supervised = [i for i, label in enumerate(labels) if label != -100]
        if not supervised or supervised != list(range(supervised[0], len(ids))) or supervised[0] == 0:
            raise ValueError("Answer-only contiguous supervision required")
        if any(type(label) is not int or (label != -100 and label != ids[i]) for i, label in enumerate(labels)) or 106 not in labels:
            raise ValueError("Invalid answer labels or missing turn end")
    return rows


def offline():
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"


def gpu_admission():
    import torch
    info = environment()
    if info["system"] != "Linux" or info["machine"] not in {"x86_64", "AMD64"} or sys.version_info[:2] != (3, 12):
        raise RuntimeError("Real training requires the frozen Linux amd64 Python 3.12 runtime")
    if info["packages"] != PINS:
        raise RuntimeError("Installed dependency versions differ from the frozen requirements")
    if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
        raise RuntimeError("Exactly one visible CUDA GPU is required")
    device = torch.cuda.get_device_properties(0)
    if "A100" not in device.name or device.total_memory < 75 * 1024**3 or not torch.cuda.is_bf16_supported():
        raise RuntimeError("The paid recipe requires one A100 80 GB with BF16")
    info["gpu"] = {"name": device.name, "bytes": device.total_memory}
    return info


def assert_adapter(model):
    trainable = [(name, value) for name, value in model.named_parameters() if value.requires_grad]
    if not trainable or any(".language_model.layers." not in name or ".lora_" not in name for name, _ in trainable):
        raise RuntimeError("Only language-layer LoRA parameters may train")
    return sum(value.numel() for _, value in trainable)


def train(args):
    offline()
    check_deadline(args.deadline_utc)
    bundle, contract = bundled_contract(args)
    settings = contract["training"]
    if args.full:
        policy = contract.get("execution_policy")
        if policy != CLOUD_FIRST_POLICY or policy.get("local_validation_required_before_delivery") is not True:
            raise ValueError("Full training requires the explicit cloud-first policy with local validation before delivery")
        readiness = contract.get("readiness", {})
        if type(readiness.get("local_model_verified")) is not bool:
            raise ValueError("Local validation must remain an explicit boolean fact")
        cloud_gates = READINESS - {"local_model_verified"}
        if not all(readiness.get(key) is True for key in cloud_gates) or not all(
                value is True for key, value in readiness.items() if key != "local_model_verified") or not args.resume:
            raise ValueError("Full training requires every readiness gate and explicit canary resume")
    elif args.max_steps is None or not 1 <= args.max_steps <= min(20, settings["canary_max_steps"]):
        raise ValueError("Specify a bounded canary --max-steps between 1 and 20")
    elif args.resume:
        raise ValueError("This recipe permits one bounded canary, followed only by explicit --full resume")
    rows = load_rows(bundle / "train.jsonl", settings["max_length"])
    output = Path(args.output).resolve()
    if args.resume:
        checkpoint, resume_record = resume_checkpoint(args.resume, output)
    info = gpu_admission()
    base_provenance = verify_base(args.base)
    check_deadline(args.deadline_utc)
    identity = {"model": contract["model"], "training": settings,
                "train_sha256": digest(bundle / "train.jsonl"), "runtime": info,
                "base_files": base_provenance["files"]}
    if args.resume:
        if read_json(output / "provenance.json") != identity:
            raise ValueError("Resume identity differs from the original run")
        resume_record.update({"contract": contract,
            "contract_sha256": digest(bundle / "contract.json"),
            "bundle_manifest_sha256": digest(bundle / "manifest.json")})
        with (output / "resume-checkpoint.json").open("x", encoding="utf-8") as stream:
            json.dump(resume_record, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
    else:
        if output.exists():
            raise ValueError("Fresh training output must not exist; never overwrite a run")
        output.mkdir(parents=True)
        write_json(output / "environment.json", info)
        write_json(output / "provenance.json", identity)
        write_json(output / "contract.json", contract)
    args._owns_output = True
    write_json(output / "status.json", {"status": "starting", "paid_readiness_claim": False})
    import torch
    from transformers import Gemma4ForConditionalGeneration, BitsAndBytesConfig, Trainer, TrainingArguments, TrainerCallback, set_seed
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    set_seed(settings["seed"])
    model = Gemma4ForConditionalGeneration.from_pretrained(
        args.base, local_files_only=True, trust_remote_code=False, use_safetensors=True,
        device_map={"": 0}, dtype=torch.bfloat16, attn_implementation="eager",
        quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16))
    model = prepare_model_for_kbit_training(model, gradient_checkpointing_kwargs={"use_reentrant": False})
    model = get_peft_model(model, LoraConfig(r=settings["r"], lora_alpha=settings["lora_alpha"],
        lora_dropout=settings["lora_dropout"], bias="none", task_type="CAUSAL_LM", target_modules=TARGETS))
    model.config.use_cache = False
    model.config.text_config.use_cache = False
    count = assert_adapter(model)

    class Guard(TrainerCallback):
        def on_step_begin(self, args_, state, control, **kwargs):
            check_deadline(args.deadline_utc)

        def on_pre_optimizer_step(self, args_, state, control, **kwargs):
            nonzero = False
            for name, parameter in model.named_parameters():
                if parameter.requires_grad and parameter.grad is not None:
                    if not torch.isfinite(parameter.grad).all():
                        raise FloatingPointError("Nonfinite adapter gradient: " + name)
                    if not nonzero and parameter.grad.abs().sum() > 0:
                        nonzero = True
            if not nonzero:
                raise FloatingPointError("No nonzero adapter gradient at optimizer step")

        def on_log(self, args_, state, control, logs=None, **kwargs):
            if logs and "loss" in logs and not math.isfinite(logs["loss"]):
                raise FloatingPointError("Nonfinite training loss")

        def on_step_end(self, args_, state, control, **kwargs):
            check_deadline(args.deadline_utc)
            if not args.full and state.global_step >= args.max_steps:
                control.should_save = True
                control.should_training_stop = True
            return control

    def collate(batch):
        longest = max(len(row["input_ids"]) for row in batch)
        return {key: torch.tensor([row[key] + [pad] * (longest - len(row[key])) for row in batch], dtype=torch.long)
                for key, pad in (("input_ids", 0), ("attention_mask", 0), ("labels", -100))}

    arguments = TrainingArguments(output_dir=str(output), num_train_epochs=settings["num_train_epochs"],
        per_device_train_batch_size=settings["micro_batch_size"], gradient_accumulation_steps=settings["gradient_accumulation_steps"],
        learning_rate=settings["learning_rate"], warmup_ratio=settings["warmup_ratio"], lr_scheduler_type=settings["lr_scheduler_type"],
        seed=settings["seed"], data_seed=settings["seed"], bf16=True, fp16=False,
        gradient_checkpointing=True, gradient_checkpointing_kwargs={"use_reentrant": False},
        optim="adamw_torch", save_strategy="steps", save_steps=settings["save_steps"],
        logging_steps=settings["logging_steps"], logging_nan_inf_filter=False, report_to="none", push_to_hub=False,
        dataloader_num_workers=0, remove_unused_columns=False)
    trainer = Trainer(model=model, args=arguments, train_dataset=rows, data_collator=collate, callbacks=[Guard()])
    result = trainer.train(resume_from_checkpoint=str(checkpoint) if args.resume else None)
    adapter = output / ("adapter" if args.full else "canary-adapter")
    if adapter.exists():
        raise ValueError("Adapter output exists; preserve previous artifacts")
    model.save_pretrained(adapter, safe_serialization=True)
    if not math.isfinite(result.training_loss):
        raise FloatingPointError("Nonfinite final loss")
    write_json(output / "metrics.json", {**result.metrics, "global_step": trainer.state.global_step,
        "trainable_parameters": count, "peak_gpu_bytes": torch.cuda.max_memory_allocated()})
    write_json(output / "status.json", {"status": "training_complete" if args.full else "canary_pass",
        "global_step": trainer.state.global_step, "adapter": adapter.name,
        "quality_validated": False, "cloud_shutdown_performed": False})


def extra_eval_rows(path, adapter, original_rows, bundle):
    """Admit only the frozen after-training sentinels; bundle is already verified."""
    if not adapter:
        raise ValueError("Extra evaluation inputs require --adapter")
    data = Path(path).read_bytes()
    checksum = hashlib.sha256(data).hexdigest()
    if checksum != EXTRA_EVAL_SHA256:
        raise ValueError("Extra evaluation inputs differ from the frozen six sentinels")
    rows = [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]
    fields = {"id", "record_id", "work_id", "source_language", "target_language", "text", "prompt"}
    if len(rows) != 6 or any(not isinstance(row, dict) or set(row) != fields for row in rows):
        raise ValueError("Extra evaluation requires exactly six input-only records")
    if any(any(not isinstance(row[key], str) or not row[key].strip() for key in fields) or
           row["source_language"] != "pal" or row["target_language"] != "fa" for row in rows):
        raise ValueError("Invalid extra evaluation fields or translation direction")
    ids = {row["id"] for row in rows}
    if ids != EXTRA_EVAL_IDS or ids & {row["id"] for row in original_rows}:
        raise ValueError("Extra evaluation IDs must match the frozen set and be distinct")
    verifier = sys.modules["_pilot_bundle_verifier"]
    guard = {"__file__": str(bundle / "holdout.py")}
    exec(compile((bundle / "holdout.py").read_bytes(), "<verified-holdout>", "exec"), guard)
    rules = read_json(bundle / "benchmark-holdout.json")
    for row in rows:
        verifier.reject_controls(row["text"])
        verifier.reject_controls(row["prompt"])
        if guard["blocked_reason"](row, rules):
            raise ValueError("Extra evaluation intersects the held-out benchmark: " + row["id"])
    return rows, checksum


def evaluate(args):
    offline()
    check_deadline(args.deadline_utc)
    bundle, contract = bundled_contract(args)
    if Path(args.inputs).resolve() != bundle / "dev-inputs.jsonl":
        raise ValueError("Evaluation is restricted to this verified bundle's dev-inputs.jsonl")
    rows = [json.loads(line) for line in Path(args.inputs).read_text("utf-8").splitlines() if line.strip()]
    extra_inputs_sha256 = None
    if getattr(args, "extra_inputs", None):
        extra, extra_inputs_sha256 = extra_eval_rows(args.extra_inputs, args.adapter, rows, bundle)
        rows.extend(extra)
    if not rows or any(not isinstance(row.get("id"), str) or not row["id"] or
            not isinstance(row.get("prompt"), str) or not row["prompt"].strip() for row in rows):
        raise ValueError("Prediction IDs and prompts must be nonempty strings")
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Prediction IDs must be unique")
    output = Path(args.output)
    if output.exists():
        raise ValueError("Prediction output exists")
    inputs_sha256 = digest(args.inputs)
    base_provenance = verify_base(args.base)
    checked_files(args.tokenizer, {name: base_provenance["files"][name]
        for name in ("tokenizer.json", "tokenizer_config.json", "chat_template.jinja")})
    adapter_files = {}
    if args.adapter:
        adapter_path = Path(args.adapter).resolve()
        adapter_provenance = read_json(adapter_path.parent / "provenance.json")
        if adapter_provenance["model"] != contract["model"] or adapter_provenance["base_files"] != base_provenance["files"]:
            raise ValueError("Adapter provenance does not match the original base")
        adapter_files = {name: digest(adapter_path / name)
            for name in ("adapter_config.json", "adapter_model.safetensors")}
    import torch
    from transformers import Gemma4ForConditionalGeneration, AutoTokenizer, DynamicCache
    from peft import PeftModel
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, local_files_only=True, trust_remote_code=False)
    prepared = []
    for row in rows:
        ids = tokenizer.apply_chat_template([{"role": "user", "content": row["prompt"]}], tokenize=True,
            return_dict=False, add_generation_prompt=True, enable_thinking=False)
        if len(ids) > 4096:
            raise ValueError("Evaluation input exceeds 4096 tokens")
        prepared.append((row, ids))
    check_deadline(args.deadline_utc)
    gpu_admission()
    model = Gemma4ForConditionalGeneration.from_pretrained(args.base, local_files_only=True,
        trust_remote_code=False, use_safetensors=True, device_map={"": 0}, dtype=torch.bfloat16, attn_implementation="eager")
    if args.adapter:
        model = PeftModel.from_pretrained(model, args.adapter, local_files_only=True, is_trainable=False)
    model.eval()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        for row, ids in prepared:
            check_deadline(args.deadline_utc)
            start = time.monotonic()
            tokens = torch.tensor([ids], device="cuda")
            # 5.13.1 configured DynamicCache slices [:0] for Gemma4's zero shared layers.
            # A public unconfigured cache avoids that bug; it retains full-length KV.
            with torch.inference_mode():
                generated = model.generate(input_ids=tokens, attention_mask=torch.ones_like(tokens),
                    past_key_values=DynamicCache(), use_cache=True, do_sample=False,
                    max_new_tokens=contract["generation"]["max_new_tokens"], pad_token_id=0, eos_token_id=[1, 106, 50])
            result = {"id": row["id"], "text": tokenizer.decode(generated[0, len(ids):], skip_special_tokens=True),
                "input_tokens": len(ids), "output_tokens": generated.shape[-1] - len(ids),
                "seconds": time.monotonic() - start, "base_revision": REVISION,
                "inputs_sha256": inputs_sha256,
                "extra_inputs_sha256": extra_inputs_sha256,
                "adapter": str(Path(args.adapter).resolve()) if args.adapter else None,
                "adapter_files": adapter_files,
                "hit_output_cap": generated.shape[-1] - len(ids) >= contract["generation"]["max_new_tokens"],
                "condition": "bf16-original-plus-adapter" if args.adapter else "bf16-original"}
            stream.write(json.dumps(result, ensure_ascii=False) + "\n")
            stream.flush()
            check_deadline(args.deadline_utc)
    print(json.dumps({"status": "evaluation_complete", "count": len(rows)}))


def tiny_smoke(args):
    offline()
    import torch
    from transformers import Gemma4Config, Gemma4TextConfig, Gemma4ForConditionalGeneration, BitsAndBytesConfig, DynamicCache
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    torch.set_num_threads(2)
    torch.manual_seed(42)
    text = Gemma4TextConfig(vocab_size=128, hidden_size=64, intermediate_size=128, num_hidden_layers=2,
        num_attention_heads=4, num_key_value_heads=2, head_dim=16, global_head_dim=16, num_global_key_value_heads=2,
        hidden_size_per_layer_input=0, vocab_size_per_layer_input=128, num_kv_shared_layers=0, attention_k_eq_v=True,
        layer_types=["sliding_attention", "full_attention"], sliding_window=16, max_position_embeddings=128,
        attention_dropout=0.0, use_bidirectional_attention="vision", final_logit_softcapping=30.0)
    config = Gemma4Config(text_config=text, vision_config=None, audio_config=None)
    config._attn_implementation = "eager"
    model = Gemma4ForConditionalGeneration(config)
    if args.four_bit:
        model = Gemma4ForConditionalGeneration.from_pretrained(None, config=config, state_dict=model.state_dict(),
            local_files_only=True, device_map={"": args.device}, dtype=torch.bfloat16,
            quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16))
    else:
        model.to(args.device)
    model = prepare_model_for_kbit_training(model, gradient_checkpointing_kwargs={"use_reentrant": False})
    model = get_peft_model(model, LoraConfig(r=4, lora_alpha=8, lora_dropout=0.0, bias="none", task_type="CAUSAL_LM", target_modules=TARGETS))
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.config.use_cache = False
    count = assert_adapter(model)
    model.train()
    ids = torch.tensor([[2, 11, 12, 13, 14, 15, 16, 17]], device=args.device)
    labels = ids.clone()
    labels[:, :4] = -100
    result = model(input_ids=ids, attention_mask=torch.ones_like(ids), labels=labels, use_cache=False)
    if not torch.isfinite(result.loss):
        raise FloatingPointError("Tiny loss is nonfinite")
    result.loss.backward()
    parameters = [p for p in model.parameters() if p.requires_grad]
    if not any(p.grad is not None and p.grad.abs().sum() > 0 for p in parameters) or any(p.grad is not None and not torch.isfinite(p.grad).all() for p in parameters):
        raise FloatingPointError("Tiny gradients failed")
    model.eval()
    model.gradient_checkpointing_disable()
    with torch.inference_mode():
        common = {"input_ids": ids, "attention_mask": torch.ones_like(ids), "max_new_tokens": 3,
                  "do_sample": False, "eos_token_id": None, "pad_token_id": 0}
        cached = model.generate(**common, past_key_values=DynamicCache(), use_cache=True)
        uncached = model.generate(**common, use_cache=False)
    if not torch.equal(cached, uncached):
        raise AssertionError("Tiny cached/uncached greedy outputs differ")
    print(json.dumps({"status": "tiny_smoke_pass", "device": args.device, "four_bit": args.four_bit,
        "loss": result.loss.item(), "trainable_parameters": count, "cache_parity": True,
        "full_model_tested": False, "environment": environment()}))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("inspect-runtime")
    tiny = commands.add_parser("tiny-smoke")
    tiny.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    tiny.add_argument("--four-bit", action="store_true")
    training = commands.add_parser("train")
    for name in ("contract", "bundle", "base", "output", "deadline-utc"):
        training.add_argument("--" + name, required=True)
    stop = training.add_mutually_exclusive_group(required=True)
    stop.add_argument("--max-steps", type=int)
    stop.add_argument("--full", action="store_true")
    training.add_argument("--resume")
    evaluation = commands.add_parser("eval")
    for name in ("contract", "bundle", "base", "tokenizer", "inputs", "output", "deadline-utc"):
        evaluation.add_argument("--" + name, required=True)
    evaluation.add_argument("--adapter")
    evaluation.add_argument("--extra-inputs")
    args = parser.parse_args(argv)
    args._owns_output = False
    try:
        if args.command == "inspect-runtime":
            print(json.dumps(environment(), indent=2))
        elif args.command == "tiny-smoke":
            tiny_smoke(args)
        elif args.command == "train":
            train(args)
        else:
            evaluate(args)
    except Exception as error:
        if args.command == "train" and args._owns_output:
            write_json(Path(args.output) / "status.json", {"status": "failed", "error_type": type(error).__name__,
                "error": str(error), "cloud_shutdown_performed": False})
        raise


if __name__ == "__main__":
    main()
