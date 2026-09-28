"""Run unchanged PAL-REF inputs on one owned local llama.cpp server; no scoring."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import time
import urllib.error
import urllib.request

try:
    from . import palref_eval as protocol, local_eval as local
    from .bundle import TOKENIZER_HASHES
except ImportError:
    import palref_eval as protocol
    import local_eval as local
    from bundle import TOKENIZER_HASHES

MODEL_SHA256 = "4c294a4d67542654525b6de3c1f15a1e6d37e31e5043a9438ec3e8b8177f128f"
CONVERTER_COMMIT = "95887577ab5fead779581a7030a83c7752ff3234"
BUILD = "build 11205, commit 95887577a"


def prepare_inputs(tokenizer, rows):
    prepared = []
    for row in rows:
        kwargs = {"add_generation_prompt": True, "enable_thinking": False}
        rendered = tokenizer.apply_chat_template(protocol.messages(row), tokenize=False, **kwargs)
        ids = tokenizer.apply_chat_template(protocol.messages(row), tokenize=True, return_dict=False, **kwargs)
        if not ids or ids[0] != tokenizer.bos_token_id or tokenizer.encode(rendered, add_special_tokens=False) != ids:
            raise ValueError("Official chat-template/tokenizer parity failed: " + row["id"])
        prepared.append((row, rendered, ids))
    return prepared


def verify_server_tokens(request, prepared):
    for row, rendered, ids in prepared:
        response = request("/tokenize", {"content": rendered, "add_special": False, "parse_special": True})
        if response.get("tokens") != ids:
            raise ValueError("llama.cpp tokenizer parity failed: " + row["id"])


def completion_payload(ids):
    return {"prompt": ids, "n_predict": protocol.MAX_TOKENS, "temperature": 0, "dynatemp_range": 0,
            "samplers": ["temperature"], "seed": 42, "repeat_penalty": 1, "presence_penalty": 0,
            "frequency_penalty": 0, "cache_prompt": False, "ignore_eos": False, "stop": [],
            "stream": False, "return_tokens": True, "id_slot": 0}


def generate_cases(process, request, tokenizer, prepared, predictions, events, metadata):
    for row, _, ids in prepared:
        start = time.monotonic()
        record = protocol.prediction(row, "", 0)
        try:
            response = local.bounded(process, protocol.CASE_SECONDS,
                                     lambda: request("/completion", completion_payload(ids)))
            local.write_record(events, {"event": "case_response", "id": row["id"], "raw_response": response})
            local.validate_response(response, protocol.MAX_TOKENS)
            text = tokenizer.decode(response["tokens"], skip_special_tokens=True)
            record = protocol.prediction(row, text, time.monotonic() - start, hit_cap=response["stop_type"] == "limit")
        except BaseException as error:
            record = protocol.prediction(row, "", time.monotonic() - start, timed_out=isinstance(error, TimeoutError))
            local.write_record(events, {"event": "case_failed", "id": row["id"],
                                        "error_type": type(error).__name__, "error": str(error)})
            raise
        finally:
            local.write_record(predictions, record)
            metadata["completed_cases"] += 1
        print(json.dumps({"status": "palref_case_complete", "id": row["id"], "outcome": record["status"],
                          "completed_cases": metadata["completed_cases"], "total_cases": 40}), flush=True)


def run(args):
    protocol.runtime.offline()
    rows = protocol.read_inputs(args.inputs)
    output = Path(args.output).resolve()
    if output.exists():
        raise ValueError("Evaluation output must be a fresh directory")
    paths = {name: Path(getattr(args, name)).resolve(strict=True)
             for name in ("server", "model", "adapter", "adapter_source", "inputs", "tokenizer")}
    if args.model_sha256.lower() != MODEL_SHA256 or not re.fullmatch(r"[a-fA-F0-9]{64}", args.adapter_sha256):
        raise ValueError("Require the frozen Q8 base and an expected converted-adapter SHA256")
    source_provenance_path = paths["adapter_source"].parent / "provenance.json"
    source_provenance = protocol.runtime.read_json(source_provenance_path)
    model_identity = source_provenance["model"]
    if (model_identity.get("id"), model_identity.get("revision")) != (protocol.runtime.MODEL_ID, protocol.runtime.REVISION):
        raise ValueError("Source PEFT adapter belongs to a different model/revision")
    source_config = protocol.runtime.read_json(paths["adapter_source"] / "adapter_config.json")
    if (source_config.get("peft_type"), source_config.get("r"), source_config.get("lora_alpha")) != ("LORA", 16, 32) or source_config.get("use_dora") or source_config.get("use_rslora"):
        raise ValueError("Source adapter differs from the frozen LoRA representation")
    protocol.runtime.checked_files(paths["tokenizer"], TOKENIZER_HASHES)
    hashes = {name: local.file_hash(paths[name]) for name in ("server", "model", "adapter", "inputs")}
    if hashes["model"] != MODEL_SHA256 or hashes["adapter"] != args.adapter_sha256.lower():
        raise ValueError("Model or converted-adapter checksum mismatch")
    hashes["source_peft"] = {name: local.file_hash(paths["adapter_source"] / name)
                             for name in ("adapter_config.json", "adapter_model.safetensors")}
    hashes["source_provenance"] = local.file_hash(source_provenance_path)
    hashes["runtime_dlls"] = {path.name: local.file_hash(path) for path in sorted(paths["server"].parent.glob("*.dll"))}
    hashes["runner"] = local.file_hash(__file__)
    hashes["helpers"] = {name: local.file_hash(module.__file__) for name, module in
                          (("palref_eval.py", protocol), ("local_eval.py", local), ("runtime.py", protocol.runtime))}
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(paths["tokenizer"], local_files_only=True, trust_remote_code=False, token=False)
    prepared = prepare_inputs(tokenizer, rows)
    context_size = max(5120, max(len(ids) for _, _, ids in prepared) + protocol.MAX_TOKENS)
    environment = {key: value for key, value in os.environ.items() if not key.startswith("LLAMA_ARG_")}
    version = subprocess.run([str(paths["server"]), "--version"], capture_output=True, text=True,
        timeout=30, check=True, env=environment, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    version_text = version.stdout + version.stderr
    if BUILD not in version_text:
        raise ValueError("Local server differs from the pinned llama.cpp build")
    command = [str(paths["server"]), "--model", str(paths["model"]), "--lora", str(paths["adapter"]),
        "--host", "127.0.0.1", "--port", str(args.port), "--parallel", "1", "--ctx-size", str(context_size),
        "--fit-ctx", str(context_size), "--gpu-layers", "auto", "--fit", "on", "--fit-target", "2048",
        "--batch-size", "512", "--ubatch-size", "128", "--cache-type-k", "f16", "--cache-type-v", "f16",
        "--cache-ram", "0", "--no-cache-prompt", "--no-context-shift", "--offline", "--no-webui", "--seed", "42",
        "--n-predict", str(protocol.MAX_TOKENS)]
    with socket.socket() as check:
        check.bind(("127.0.0.1", args.port))
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    def request(endpoint, payload=None):
        data = None if payload is None else json.dumps(payload, allow_nan=False).encode("utf-8")
        req = urllib.request.Request(f"http://127.0.0.1:{args.port}{endpoint}", data=data,
                                     headers={"Content-Type": "application/json"})
        with opener.open(req, timeout=protocol.CASE_SECONDS if endpoint == "/completion" else 5) as response:
            return json.load(response)
    metadata = {"benchmark_id": "pal-reference-v1", "benchmark_manifest_sha256": protocol.BENCHMARK_SHA256,
        "original_inputs_sha256": protocol.ORIGINAL_INPUTS_SHA256, "source_only_inputs_sha256": protocol.INPUTS_SHA256,
        "model_id": protocol.runtime.MODEL_ID, "model_revision": protocol.runtime.REVISION,
        "adapter_sha256_or_none": hashes["adapter"], "runtime": version_text.strip(), "hashes": hashes,
        "tokenizer_files": TOKENIZER_HASHES, "chat_template_sha256": TOKENIZER_HASHES["chat_template.jinja"],
        "decoding": "greedy", "seed": 42, "max_new_tokens": protocol.MAX_TOKENS,
        "max_generation_seconds": protocol.CASE_SECONDS, "retrieval": "none", "fresh_context_each_case": True,
        "system_prompt": protocol.PROMPT, "rendered_system_instruction": protocol.SYSTEM, "enable_thinking": False,
        "reviewer_id": "", "reviewer_type": "unassigned", "review_status": "provisional_single_review",
        "direction": "pal>fa", "condition": "q8_0-original-plus-f32-lora", "expected_converter_commit": CONVERTER_COMMIT,
        "converted_tensor_parity_verified": False, "server_tokenizer_parity_verified": False,
        "full_model_runtime_verified": False, "quality_verified": False, "command": command,
        "status": "starting", "completed_cases": 0}
    output.mkdir(parents=True, exist_ok=False)
    protocol.runtime.write_json(output / "run.json", metadata)
    process = None
    with (output / "predictions.jsonl").open("x", encoding="utf-8") as predictions, \
            (output / "events.jsonl").open("x", encoding="utf-8") as events, \
            (output / "server.log").open("x", encoding="utf-8") as log:
        try:
            process = subprocess.Popen(command, cwd=paths["server"].parent, env=environment,
                stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            def ready():
                while process.poll() is None:
                    try:
                        if request("/health").get("status") == "ok":
                            return request("/props")
                    except (OSError, urllib.error.URLError):
                        pass
                    time.sleep(0.25)
                raise RuntimeError("Owned server exited before readiness")
            props = local.bounded(process, local.STARTUP_SECONDS, ready)
            eog = {int(value) for value in re.findall(r"EOG token\s*=\s*(\d+)",
                    (output / "server.log").read_text("utf-8", errors="replace"))}
            if eog != local.EOS:
                raise ValueError("Server EOS IDs differ from the frozen tokenizer")
            verify_server_tokens(request, prepared)
            metadata.update(status="running", server_tokenizer_parity_verified=True)
            metadata["rendered_input_tokens_sha256"] = hashlib.sha256(json.dumps(
                [{"id": row["id"], "token_ids": ids} for row, _, ids in prepared], separators=(",", ":")).encode()).hexdigest()
            protocol.runtime.write_json(output / "run.json", metadata)
            local.write_record(events, {"event": "ready", "props": props, "eog_ids": sorted(eog)})
            generate_cases(process, request, tokenizer, prepared, predictions, events, metadata)
            metadata.update(status="completed", full_model_runtime_verified=True)
        except BaseException as error:
            metadata.update(status="incomplete", error_type=type(error).__name__, error=str(error))
            raise
        finally:
            try:
                if process is not None:
                    local.stop_server(process)
                    local.write_record(events, {"event": "server_exit_confirmed", "exit_code": process.returncode})
            except BaseException as error:
                metadata.update(status="incomplete", error_type=type(error).__name__, error=str(error))
                raise
            finally:
                protocol.runtime.write_json(output / "run.json", metadata)
    print(json.dumps({"status": "palref_local_evaluation_complete", "count": metadata["completed_cases"]}), flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("server", "model", "model-sha256", "adapter", "adapter-sha256", "adapter-source", "inputs", "tokenizer", "output"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--port", type=int, default=8765, choices=range(1024, 65536), metavar="PORT")
    run(parser.parse_args(argv))


if __name__ == "__main__":
    main()
