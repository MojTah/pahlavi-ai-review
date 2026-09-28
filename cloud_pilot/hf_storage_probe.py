"""Prepare, but never submit, a tiny CPU adapter roundtrip on one HF bucket."""
import argparse
import hashlib
import inspect
import json
from pathlib import Path
import re
import uuid

try:
    from . import hf_preflight
except ImportError:
    import hf_preflight


BUCKET = "Mojionix/pahlavi-pilot"
FIXTURE_NAME = "storage-probe-fixture.txt"
FIXTURE_BYTES = b"pahlavi-hf-storage-probe-v1\n"
FIXTURE_SHA256 = hashlib.sha256(FIXTURE_BYTES).hexdigest()


def verify_fixture(path):
    if Path(path).read_bytes() != FIXTURE_BYTES:
        raise ValueError("Mounted storage probe fixture differs from expected bytes")


PROBE = r'''
import copy, json
from pathlib import Path
import torch
from transformers import Gemma4Config, Gemma4TextConfig, Gemma4ForConditionalGeneration, BitsAndBytesConfig
from peft import LoraConfig, PeftModel, get_peft_model, prepare_model_for_kbit_training
import runtime

runtime.offline()
torch.set_num_threads(2)
torch.manual_seed(42)
output = Path("/output/new-run")
output.mkdir(exist_ok=False)
runtime.write_json(output / "checkpoint.json", {"global_step": 0, "status": "started"})
text = Gemma4TextConfig(vocab_size=128, hidden_size=64, intermediate_size=128, num_hidden_layers=2,
    num_attention_heads=4, num_key_value_heads=2, head_dim=16, global_head_dim=16, num_global_key_value_heads=2,
    hidden_size_per_layer_input=0, vocab_size_per_layer_input=128, num_kv_shared_layers=0, attention_k_eq_v=True,
    layer_types=["sliding_attention", "full_attention"], sliding_window=16, max_position_embeddings=128,
    attention_dropout=0.0, use_bidirectional_attention="vision", final_logit_softcapping=30.0)
config = Gemma4Config(text_config=text, vision_config=None, audio_config=None)
config._attn_implementation = "eager"
original = Gemma4ForConditionalGeneration(config)
base_state = {name: tensor.detach().clone() for name, tensor in original.state_dict().items()}
del original

def tiny_base():
    base = Gemma4ForConditionalGeneration.from_pretrained(None, config=copy.deepcopy(config),
        state_dict={name: tensor.clone() for name, tensor in base_state.items()},
        local_files_only=True, device_map={"": "cpu"}, dtype=torch.bfloat16,
        quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16))
    return prepare_model_for_kbit_training(base, gradient_checkpointing_kwargs={"use_reentrant": False})

model = get_peft_model(tiny_base(), LoraConfig(r=4, lora_alpha=8, lora_dropout=0.0,
    bias="none", task_type="CAUSAL_LM", target_modules=runtime.TARGETS))
count = runtime.assert_adapter(model)
model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
model.config.use_cache = False
model.train()
parameters = [p for p in model.parameters() if p.requires_grad]
before = [p.detach().clone() for p in parameters]
optimizer = torch.optim.AdamW(parameters, lr=1e-3)
ids = torch.tensor([[2, 11, 12, 13, 14, 15, 16, 17]])
labels = ids.clone()
labels[:, :4] = -100
result = model(input_ids=ids, attention_mask=torch.ones_like(ids), labels=labels, use_cache=False)
if not torch.isfinite(result.loss):
    raise FloatingPointError("Storage probe loss is nonfinite")
result.loss.backward()
if not any(p.grad is not None and p.grad.abs().sum() > 0 for p in parameters) or any(
        p.grad is not None and not torch.isfinite(p.grad).all() for p in parameters):
    raise FloatingPointError("Storage probe gradients failed")
optimizer.step()
if not any(not torch.equal(old, p) for old, p in zip(before, parameters)):
    raise AssertionError("Optimizer step did not change any adapter parameter")
optimizer.zero_grad(set_to_none=True)
model.eval()
model.gradient_checkpointing_disable()
with torch.inference_mode():
    expected_logits = model(input_ids=ids, attention_mask=torch.ones_like(ids), use_cache=False).logits.clone()
model.save_pretrained(output / "adapter", safe_serialization=True, save_embedding_layers=False)
torch.save({"global_step": 1, "optimizer": optimizer.state_dict()}, output / "optimizer.pt")
# Replacing an existing JSON also exercises the production temporary-file/os.replace path.
runtime.write_json(output / "checkpoint.json", {"global_step": 1, "status": "saved"})
if runtime.read_json(output / "checkpoint.json") != {"global_step": 1, "status": "saved"}:
    raise AssertionError("Atomic checkpoint JSON did not roundtrip")
files = {str(p.relative_to(output)).replace("\\", "/"): runtime.digest(p)
         for p in output.rglob("*") if p.is_file()}
required = {"adapter/adapter_config.json", "adapter/adapter_model.safetensors", "optimizer.pt", "checkpoint.json"}
if not required <= files.keys():
    raise AssertionError("Required adapter/optimizer/checkpoint files were not saved")
runtime.checked_files(output, files)
restored = PeftModel.from_pretrained(tiny_base(), output / "adapter", is_trainable=True,
    local_files_only=True)
if runtime.assert_adapter(restored) != count:
    raise AssertionError("Reloaded adapter trainable parameter count differs")
restored.eval()
restored.gradient_checkpointing_disable()
saved = torch.load(output / "optimizer.pt", map_location="cpu", weights_only=True)
if saved["global_step"] != 1 or not saved["optimizer"]["state"] or any(
        float(state["step"]) != 1 for state in saved["optimizer"]["state"].values()):
    raise AssertionError("Expected exactly one saved optimizer step")
restored_optimizer = torch.optim.AdamW([p for p in restored.parameters() if p.requires_grad], lr=1e-3)
restored_optimizer.load_state_dict(saved["optimizer"])
if restored_optimizer.state_dict()["param_groups"] != optimizer.state_dict()["param_groups"]:
    raise AssertionError("Reloaded optimizer parameter groups differ")
for key, state in optimizer.state_dict()["state"].items():
    for name, value in state.items():
        loaded = restored_optimizer.state_dict()["state"][key][name]
        if torch.is_tensor(value) and not torch.equal(value, loaded):
            raise AssertionError("Reloaded optimizer tensor differs")
with torch.inference_mode():
    actual_logits = restored(input_ids=ids, attention_mask=torch.ones_like(ids), use_cache=False).logits
torch.testing.assert_close(actual_logits, expected_logits, rtol=0, atol=0)
runtime.checked_files(output, files)
record = {"stage": "storage_probe_complete", "device": "cpu", "four_bit": True,
    "global_step": 1, "trainable_parameters": count, "loss": result.loss.item(),
    "logits_exact_match": True, "optimizer_reloaded": True, "atomic_json_replaced": True,
    "cross_job_durability_verified": False,
    "full_model_tested": False, "training_data_uploaded": False, "files": files,
    "environment": runtime.environment()}
runtime.write_json(output / "result.json", record)
if runtime.read_json(output / "result.json") != record:
    raise AssertionError("Final result did not roundtrip")
print(json.dumps(record), flush=True)
'''


def specification(run_id=None):
    """Return SDK arguments and provenance; no filesystem writes or remote actions."""
    run_id = uuid.uuid4().hex if run_id is None else run_id
    if not isinstance(run_id, str) or not re.fullmatch(r"[a-f0-9]{32}", run_id):
        raise ValueError("run_id must be 32 lowercase hexadecimal characters")
    spec, hashes = hf_preflight.specification("cpu")
    fixture_check = ("from pathlib import Path\nFIXTURE_BYTES = " + repr(FIXTURE_BYTES) + "\n"
                     + inspect.getsource(verify_fixture)
                     + f"\nverify_fixture('/input/{FIXTURE_NAME}')\n")
    spec["command"][3] = (fixture_check + spec["command"][3]
        + "\nsubprocess.run([sys.executable, '-u', '-c', " + repr(PROBE)
        + "], check=True, timeout=90)\n")
    from huggingface_hub import HfApi, Volume
    spec["volumes"] = [
        Volume(type="bucket", source=BUCKET, path="inputs", mount_path="/input", read_only=True),
        Volume(type="bucket", source=BUCKET, path="probes/" + run_id, mount_path="/output", read_only=False),
    ]
    spec["labels"]["purpose"] = "storage-probe"
    spec["labels"]["probe_id"] = run_id
    compile(spec["command"][3], "storage-probe-bootstrap", "exec")
    compile(PROBE, "storage-probe-body", "exec")
    inspect.signature(HfApi.run_job).bind(None, **spec)
    return spec, {"run_id": run_id, "input_path": f"inputs/{FIXTURE_NAME}",
        "input_sha256": FIXTURE_SHA256, "output_prefix": "probes/" + run_id,
        "files": hashes, "probe_sha256": hashlib.sha256(PROBE.encode()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id")
    args = parser.parse_args()
    spec, provenance = specification(args.run_id)
    # A JSON-loading controller must reconstruct these entries with Volume(**entry).
    spec["volumes"] = [volume.to_dict() for volume in spec["volumes"]]
    print(json.dumps({"status": "prepared_not_submitted", "spec": spec, "provenance": provenance}))


if __name__ == "__main__":
    main()
