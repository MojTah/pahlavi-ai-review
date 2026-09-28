"""One bounded, source-only Qwen DEV run. No training, retrieval or downloads.

Prepare the contract first, then execute it. Existing results are never replaced.
The same process/model serves fresh single-message contexts; no KV cache is reused.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time

FIELDS = {"id", "record_id", "work_id", "source_language", "target_language", "text"}
PROMPT = ("Translate the following Middle Persian text in scholarly Latin transcription into {language}. "
          "Return only the translation. Preserve negation, participants, names, numbers, and uncertainty. "
          "Do not invent missing context.\nSource:\n{text}")


def hashed(path):
    return sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def inputs(packet):
    audit = json.loads((packet / "audit.json").read_text("utf-8"))
    if hashed(packet / "inputs.jsonl") != audit["files"]["inputs.jsonl"]:
        raise ValueError("Input checksum changed")
    rows = [json.loads(x) for x in (packet / "inputs.jsonl").read_text("utf-8").splitlines()]
    if len(rows) != 12 or len({r["id"] for r in rows}) != 12:
        raise ValueError("Expected the twelve unique, preselected DEV cases")
    for r in rows:
        if set(r) != FIELDS or r["source_language"] != "pal" or r["target_language"] not in {"en", "fa"} or not r["text"].strip():
            raise ValueError("Input must contain only approved source fields")
    pairs = {}
    for r in rows:
        pairs.setdefault(r["record_id"], []).append(r)
    if len(pairs) != 6 or any(len(p) != 2 or {r["target_language"] for r in p} != {"en", "fa"}
                             or len({r["text"] for r in p}) != 1 for p in pairs.values()):
        raise ValueError("Both languages require the identical six source passages")
    order = ["001", "006", "002", "003", "004", "005"]
    return sorted(rows, key=lambda r: (order.index(r["id"].split(":")[0][-3:]), r["target_language"]))


def main(repo, packet, prepare):
    sys.path.insert(0, str(repo))
    from pahlavi.holdout import require_allowed
    from pahlavi.model import verify_model_artifacts, read_config, model_path
    from pahlavi.training import model_identity, runtime_identity
    from pahlavi.quality import QualityModel
    rows = inputs(packet)
    require_allowed(rows)
    config_path = repo / "models/candidate-real-full-20260921.json"
    config = read_config(config_path)
    artifacts = verify_model_artifacts(config_path, full_hashes=True)
    identity = {"model": model_identity(config_path), "config_sha256": hashed(config_path),
                "base_files": artifacts["files"], "runtime": runtime_identity(),
                "quality_code_sha256": hashed(repo / "pahlavi/quality.py"), "runner_sha256": hashed(Path(__file__)),
                "inputs_sha256": hashed(packet / "inputs.jsonl"), "audit_sha256": hashed(packet / "audit.json"),
                "reference_screen_sha256": hashed(packet / "REFERENCE_SCREEN_FA.md"),
                "prompt": PROMPT, "order": [r["id"] for r in rows], "max_new_tokens": 1024,
                "max_input_tokens": 4096, "case_seconds": 120, "run_seconds": 600, "decoding": "greedy",
                "retrieval": "none", "fresh_context_each_case": True, "first_attempt_only": True,
                "precision": "existing Qwen loader: 4-bit NF4", "purpose": "exploratory DEV, not PAL-REF or language qualification"}
    if prepare:
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_path(config_path, config), local_files_only=True, trust_remote_code=False)
        lengths = {}
        for r in rows:
            prompt = PROMPT.format(language={"en": "English", "fa": "modern Persian (Farsi)"}[r["target_language"]], text=r["text"])
            lengths[r["id"]] = len(tokenizer.apply_chat_template([{"role": "user", "content": prompt}], tokenize=True,
                add_generation_prompt=True, enable_thinking=False))
        if max(lengths.values()) > identity["max_input_tokens"]:
            raise ValueError("An input exceeds the complete-input limit")
        if (config_path.parent / "gpu.lock").exists():
            raise ValueError("GPU already leased; do not launch")
        save(packet / "qwen-contract.json", {"identity": identity, "preflight_tokens": lengths,
             "translator_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()})
        print(json.dumps({"preflight": "PASS", "cases": len(rows), "max_input_tokens": max(lengths.values())}))
        return
    contract = json.loads((packet / "qwen-contract.json").read_text("utf-8"))
    if contract["identity"] != identity:
        raise ValueError("Execution identity differs from the prepared contract")
    stop_file = packet / "STOP"
    started = time.monotonic()
    model = QualityModel(config_path, max_input_tokens=identity["max_input_tokens"])
    attempted, success, failure = [], 0, None
    try:
        with (packet / "qwen-predictions.jsonl").open("x", encoding="utf-8") as handle:
            for r in rows:
                if stop_file.exists() or time.monotonic() - started >= identity["run_seconds"]:
                    failure = "stopped at a case boundary"
                    break
                begin = time.monotonic()
                result = {"id": r["id"], "source_sha256": sha256(r["text"].encode()).hexdigest(), "output": ""}
                try:
                    model.prepare_generation(r["id"], "direct")
                    result["output"] = model.generate(
                        PROMPT.format(language={"en": "English", "fa": "modern Persian (Farsi)"}[r["target_language"]], text=r["text"]),
                        max_new_tokens=identity["max_new_tokens"],
                        max_time=min(identity["case_seconds"], identity["run_seconds"] - (time.monotonic() - started)),
                        should_stop=lambda: stop_file.exists() or time.monotonic() - started >= identity["run_seconds"])
                    result["status"] = "abstain" if "[unresolved]" in result["output"].lower() else "success"
                    success += result["status"] == "success"
                except Exception as exc:
                    result.update(status="error", error=str(exc), error_code=getattr(exc, "code", type(exc).__name__))
                    failure = result["error_code"]
                result.update(seconds=round(time.monotonic() - begin, 3), generation=model.last_generation)
                handle.write(json.dumps(result, ensure_ascii=False) + "\n")
                handle.flush()
                attempted.append(r["id"])
                print(json.dumps({"id": r["id"], "status": result["status"], "seconds": result["seconds"]}), flush=True)
                if failure:
                    break
    finally:
        model.close()
    save(packet / "qwen-run-summary.json", {"attempted": attempted, "successful_outputs": success,
         "not_run": [r["id"] for r in rows if r["id"] not in attempted], "failure": failure,
         "seconds": round(time.monotonic() - started, 3), "contract_sha256": hashed(packet / "qwen-contract.json"),
         "predictions_sha256": hashed(packet / "qwen-predictions.jsonl"), "meaning_quality": "NOT YET REVIEWED",
         "gpu_lock_released": not (config_path.parent / "gpu.lock").exists()})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path)
    parser.add_argument("packet", type=Path)
    parser.add_argument("--prepare", action="store_true")
    args = parser.parse_args()
    main(args.repo.resolve(), args.packet.resolve(), args.prepare)
