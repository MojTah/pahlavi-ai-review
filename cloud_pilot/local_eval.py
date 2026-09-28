"""Sequential, offline llama.cpp evaluation; owns one server, never retries or resumes."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import threading
import time
import urllib.error
import urllib.request

EOS = {1, 50, 106}
STARTUP_SECONDS = 180
REQUEST_SECONDS = 1200
INPUT_FIELDS = {"id", "prompt", "text", "record_id", "work_id", "source_language",
                "target_language", "rendered_prompt", "token_ids"}


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_record(stream, value):
    stream.write(json.dumps(value, ensure_ascii=False, allow_nan=False) + "\n")
    stream.flush()
    os.fsync(stream.fileno())


def read_inputs(path, maximum):
    rows = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines()]
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != INPUT_FIELDS:
            raise ValueError("Require exactly the nine source-only input fields; references are forbidden")
        for key in ("id", "prompt", "rendered_prompt", "text", "record_id", "work_id"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError(f"Missing or empty {key}")
        if row["source_language"] != "pal" or row["target_language"] != "fa" or row["text"] not in row["prompt"]:
            raise ValueError("Require pal-to-fa input with the identified source text in its prompt")
        ids = row.get("token_ids")
        if not isinstance(ids, list) or not 1 <= len(ids) <= 4096 or any(type(x) is not int or x < 0 for x in ids):
            raise ValueError("Invalid token_ids or input exceeds 4096 tokens")
        if row["id"] in seen:
            raise ValueError("Duplicate ID")
        seen.add(row["id"])
    if not 1 <= maximum <= 1024 or len(rows) != (30 if maximum == 1024 else 1):
        raise ValueError("Require 30 evaluation rows, or one explicit technical probe with a smaller token cap")
    return rows


def stop_server(process):
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
    if process.poll() is None:
        raise RuntimeError("URGENT: owned server termination was not confirmed")


def bounded(process, seconds, action):
    expired, cleanup_errors = threading.Event(), []

    def expire():
        expired.set()
        try:
            stop_server(process)
        except Exception as exc:
            cleanup_errors.append(str(exc))

    timer = threading.Timer(seconds, expire)
    timer.daemon = True
    timer.start()
    try:
        return action()
    finally:
        timer.cancel()
        timer.join()
        if expired.is_set():
            if cleanup_errors:
                raise RuntimeError("URGENT: deadline cleanup failed: " + "; ".join(cleanup_errors))
            raise TimeoutError(f"Whole-operation deadline {seconds}s exceeded; owned server exit confirmed")


def validate_response(response, maximum):
    tokens = response.get("tokens")
    if not isinstance(tokens, list) or not 1 <= len(tokens) <= maximum or any(type(t) is not int or t < 0 for t in tokens):
        raise ValueError("Missing/invalid output token IDs or output exceeds token cap")
    if response.get("truncated") is not False or response.get("stop_type") not in {"eos", "limit"}:
        raise ValueError("Truncated or unfinished server response")
    if any(t in EOS for t in tokens[:-1]):
        raise ValueError("Server generated tokens after EOS")
    if response["stop_type"] == "eos" and tokens[-1] not in EOS:
        raise ValueError("Unexpected EOS token")
    if response["stop_type"] == "limit" and (len(tokens) != maximum or tokens[-1] in EOS):
        raise ValueError("Unexpected early limit or EOS/limit disagreement")


def run(args):
    paths = {name: Path(getattr(args, name)).resolve(strict=True) for name in ("server", "model", "inputs", "tokenizer")}
    rows = read_inputs(paths["inputs"], args.max_new_tokens)
    hashes = {name: file_hash(paths[name]) for name in ("server", "model", "inputs")}
    if hashes["model"] != args.model_sha256.lower():
        raise ValueError("Model SHA-256 does not match the verified model")
    if bool(args.adapter) != bool(args.adapter_sha256):
        raise ValueError("Adapter and its expected SHA-256 must be supplied together")
    adapter = Path(args.adapter).resolve(strict=True) if args.adapter else None
    if adapter:
        hashes["adapter"] = file_hash(adapter)
        if hashes["adapter"] != args.adapter_sha256.lower():
            raise ValueError("Adapter SHA-256 mismatch")
    try:
        from .bundle import TOKENIZER_HASHES
    except ImportError:
        from bundle import TOKENIZER_HASHES
    hashes["tokenizer"] = {name: file_hash(paths["tokenizer"] / name) for name in TOKENIZER_HASHES}
    if hashes["tokenizer"] != TOKENIZER_HASHES:
        raise ValueError("Tokenizer does not match the frozen project tokenizer")
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(str(paths["tokenizer"]), local_files_only=True, trust_remote_code=False, token=False)
    for row in rows:
        if tokenizer.encode(row["rendered_prompt"], add_special_tokens=False) != row["token_ids"] or row["token_ids"][0] != tokenizer.bos_token_id:
            raise ValueError(f"Frozen tokenizer/BOS mismatch: {row['id']}")
    command = [str(paths["server"]), "--model", str(paths["model"]), "--host", "127.0.0.1", "--port", str(args.port),
               "--parallel", "1", "--ctx-size", "5120", "--gpu-layers", "auto", "--fit", "on", "--fit-target", "2048",
               "--fit-ctx", "5120", "--batch-size", "512", "--ubatch-size", "128", "--cache-ram", "0", "--no-cache-prompt",
               "--no-context-shift", "--offline", "--no-webui", "--seed", "3407", "--n-predict", str(args.max_new_tokens)]
    if adapter:
        command += ["--lora", str(adapter)]
    hashes["runtime_dlls"] = {p.name: file_hash(p) for p in sorted(paths["server"].parent.glob("*.dll"))}
    hashes["runner"] = file_hash(__file__)
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", args.port))  # Refuse an already occupied port before starting our process.
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def request(endpoint, payload=None):
        data = None if payload is None else json.dumps(payload, allow_nan=False).encode("utf-8")
        req = urllib.request.Request(f"http://127.0.0.1:{args.port}{endpoint}", data=data, headers={"Content-Type": "application/json"})
        with opener.open(req, timeout=REQUEST_SECONDS if endpoint == "/completion" else 5) as response:
            return json.load(response)

    process, completed = None, 0
    with (output / "events.jsonl").open("x", encoding="utf-8") as events, (output / "predictions.jsonl").open("x", encoding="utf-8") as predictions, (output / "server.log").open("x", encoding="utf-8") as log:
        write_record(events, {"event": "started", "utc": datetime.now(timezone.utc).isoformat(), "hashes": hashes,
                             "command": command, "paths": {k: str(v) for k, v in paths.items()}, "adapter": str(adapter) if adapter else None,
                             "mode": "evaluation" if args.max_new_tokens == 1024 else "technical_probe", "rows": len(rows),
                             "request_deadline_seconds": REQUEST_SECONDS, "startup_deadline_seconds": STARTUP_SECONDS})
        try:
            env = {k: v for k, v in os.environ.items() if not k.startswith("LLAMA_ARG_")}
            process = subprocess.Popen(command, cwd=paths["server"].parent, env=env, stdin=subprocess.DEVNULL,
                                       stdout=log, stderr=subprocess.STDOUT, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))

            def ready():
                while process.poll() is None:
                    try:
                        if request("/health").get("status") == "ok":
                            return request("/props")
                    except (OSError, urllib.error.URLError):
                        pass  # Readiness polling only; inference requests are never retried.
                    time.sleep(0.25)
                raise RuntimeError("Server exited before readiness; inspect server.log")

            props = bounded(process, STARTUP_SECONDS, ready)
            if process.poll() is not None:
                raise RuntimeError("Owned server exited during startup")
            eog = {int(x) for x in re.findall(r"EOG token\s*=\s*(\d+)", (output / "server.log").read_text(encoding="utf-8", errors="replace"))}
            if eog != EOS:
                raise ValueError(f"Server EOG IDs unconfirmed or changed: {sorted(eog)}")
            write_record(events, {"event": "ready", "pid": process.pid, "props": props, "eog_ids": sorted(eog)})
            for row in rows:
                record = {"id": row["id"], "input": row, "status": "incomplete", "raw_response": None}
                started = time.monotonic()
                try:
                    def generate():
                        if process.poll() is not None:
                            raise RuntimeError("Owned server exited")
                        parity = request("/tokenize", {"content": row["rendered_prompt"], "add_special": False, "parse_special": True})
                        if parity.get("tokens") != row["token_ids"]:
                            raise ValueError("llama.cpp tokenizer parity mismatch")
                        return request("/completion", {"prompt": row["token_ids"], "n_predict": args.max_new_tokens,
                            "temperature": 0, "dynatemp_range": 0, "samplers": ["temperature"], "seed": 3407,
                            "repeat_penalty": 1, "presence_penalty": 0, "frequency_penalty": 0, "cache_prompt": False,
                            "ignore_eos": False, "stop": [], "stream": False, "return_tokens": True, "id_slot": 0})
                    result = bounded(process, REQUEST_SECONDS, generate)
                    record["raw_response"] = result
                    validate_response(result, args.max_new_tokens)
                    record.update(status="completed", prediction=tokenizer.decode(result["tokens"], skip_special_tokens=True),
                                  output_token_ids=result["tokens"], output_cap_reached=result["stop_type"] == "limit")
                    completed += 1
                except BaseException as exc:
                    record["error"] = f"{type(exc).__name__}: {exc}"
                    raise
                finally:
                    record["elapsed_seconds"] = time.monotonic() - started
                    write_record(predictions, record)
        except BaseException as exc:
            write_record(events, {"event": "incomplete", "completed": completed, "error": f"{type(exc).__name__}: {exc}"})
            raise
        finally:
            if process is not None:
                stop_server(process)
                write_record(events, {"event": "server_exit_confirmed", "pid": process.pid, "exit_code": process.returncode})
        write_record(events, {"event": "completed", "completed": completed, "utc": datetime.now(timezone.utc).isoformat()})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("server", "model", "model-sha256", "inputs", "tokenizer", "output"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--adapter")
    parser.add_argument("--adapter-sha256")
    parser.add_argument("--port", type=int, default=8765, choices=range(1024, 65536), metavar="PORT")
    parser.add_argument("--max-new-tokens", type=int, default=1024)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
