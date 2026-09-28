"""Prepare and verify the one-run Pahlavi package. No cloud access or installs."""
import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import zipfile

DATASET = "6f442563128d3a4c49dd5024af6882f6911b3f1b11eb5a2d4ef0d28a453acf0c"
TRAIN_HASH = "485d063523b9efb7692c0384cfc9a87aafb3c2a86aaf3e16848eaab3fdefd070"
ORIGINAL_TOKENIZED_TRAIN_HASH = "844a5b64d43a423b69d5989527a53273290a43be15c399056c979f5abb0678a1"
PARENT_MANIFEST_HASH = "496cd9af52b2167c1895ba00f942d0fbc2b6c8aa6bdb6c23dbcd661a5f9218c6"
QUALIFIED_TRAIN_HASH = "15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc"
QUALIFIED_MANIFEST_HASH = "a5031b6f2abe81b103fb0c863602a7441776efc5b4dccf11b2e1dc6a2050ec15"
QUALIFIED_SUMMARY_HASH = "fc7131ac6600b1acda4351220d5458bf60d5a866b8f17002231eb6797996ebba"
QUALIFICATION = {
    "status": "PROVISIONAL_AI_QUALIFIED_DATA_NOT_EXPERT_CERTIFIED",
    "parent_manifest_sha256": PARENT_MANIFEST_HASH,
    "parent_train_sha256": ORIGINAL_TOKENIZED_TRAIN_HASH,
    "parent_provenance_sha256": "556272526fe9563c98d7a950496ad537f651e0780702b914733f23fc3a15c47e",
    "audit_manifest_sha256": QUALIFIED_MANIFEST_HASH,
    "audit_summary_sha256": QUALIFIED_SUMMARY_HASH,
    "qualified_train_sha256": QUALIFIED_TRAIN_HASH,
    "original_rows": 2484, "retained_rows": 2237, "excluded_rows": 247,
    "source_target_token_mutations": 0, "expert_adjudicated": False, "paid_run_admitted": False,
}
HOLDOUT_HASH = "90d66c53c03870413d86b4ac2bd77d6e95010bd316ed0c01c3414ccc68ad67c9"
POLICY_HASH = "fead263bb73e4797c09595320aeeefb6cf7e553510e3fb08a932700ffaaa55cc"
TOKENIZER_HASHES = {
    "chat_template.jinja": "ae53464bf3be25802b3a5b37def7fd89667067d7577049b3b2d74c4d8de4c6d4",
    "tokenizer.json": "cc8d3a0ce36466ccc1278bf987df5f71db1719b9ca6b4118264f45cb627bfe0f",
    "tokenizer_config.json": "9f4fec4b1dc6ecddf8f4a92e9caea5971c0e67d81309f3f9066a2bee8c362633",
}
PROMPT = ("Translate the following Middle Persian text in scholarly Latin transcription into Farsi. "
          "Return only the translation. Preserve negation, participants, names, numbers, and uncertainty. "
          "Do not invent missing context.\nSource:\n{text}")
TERMINATOR = "<turn|>\n"
CONTROL_EXCLUSIONS = {
    "parsig:151015025:pal>fa": "Source contains one literal editorial <pad>, colliding with the reserved padding token",
    "parsig:151043031:pal>fa": "Source contains one literal editorial <pad>, colliding with the reserved padding token",
    "parsig:150000054:pal>fa": "Source contains one literal editorial <pad>, colliding with the reserved padding token",
}
BASE_FILES = {"bundle.py", "runtime.py", "contract.json", "holdout.py", "benchmark-holdout.json",
              "train.jsonl", "dev-inputs.jsonl", "provenance.json", "fetch_base.py", "requirements.in",
              "Dockerfile", ".dockerignore", "requirements-linux.lock"}
BUNDLE_FILES = BASE_FILES | {"tokenizer/" + name for name in TOKENIZER_HASHES}
SOURCE_KEYS = {"credit", "id", "record_id", "revision", "source_language", "target",
               "target_language", "text", "work_id"}
DEV_KEYS = {"id", "record_id", "work_id", "source_language", "target_language", "text"}
DEV_OUTPUT_KEYS = DEV_KEYS | {"prompt"}
TOKEN_KEYS = {"input_ids", "attention_mask", "labels", "prompt_tokens"}
RESULT_ROOT = {"status.json", "metrics.json", "predictions.jsonl", "baseline-predictions.jsonl",
               "trained-predictions.jsonl", "train.log", "environment.json", "contract.json",
               "provenance.json", "resume-checkpoint.json"}
ADAPTER_FILES = {"adapter_model.safetensors", "adapter_config.json", "README.md"} | set(TOKENIZER_HASHES)


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def digest(data):
    return sha256(data).hexdigest()


def file_hash(path):
    with Path(path).open("rb") as stream:
        value = sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def check_hash(path, expected):
    if file_hash(path) != expected:
        raise ValueError(f"Pinned checksum mismatch: {Path(path).name}")


def safe_name(name):
    if not isinstance(name, str) or not name or "\\" in name or ":" in name or "\x00" in name:
        raise ValueError(f"Unsafe member name: {name!r}")
    parts = name.split("/")
    if any(part in {"", ".", ".."} for part in parts) or PurePosixPath(name).is_absolute():
        raise ValueError(f"Unsafe member name: {name!r}")
    return name


def reject_controls(text, specials=()):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Empty or non-string source/target")
    if re.search(r"<[^<>\r\n]*\|[^<>\r\n]*>|<(?:bos|eos|pad|mask|unk)>", text):
        raise ValueError("Control token in source/target")
    if any(token and token in text for token in specials):
        raise ValueError("Tokenizer special token in source/target")


def validate_row(row):
    if set(row) - (SOURCE_KEYS | TOKEN_KEYS):
        raise ValueError("Unexpected training field")
    if row.get("source_language") != "pal" or row.get("target_language") != "fa":
        raise ValueError("Wrong translation direction")
    if any(not row.get(key) for key in ("id", "record_id", "work_id", "revision")):
        raise ValueError("Missing source provenance")
    if row["id"] in CONTROL_EXCLUSIONS:
        raise ValueError("Explicitly excluded editorial-control-token source")
    reject_controls(row["text"])
    reject_controls(row["target"])
    ids, labels, mask = row["input_ids"], row["labels"], row["attention_mask"]
    prefix = row["prompt_tokens"]
    if any(not isinstance(seq, list) for seq in (ids, labels, mask)):
        raise ValueError("Token arrays must be lists")
    if not isinstance(prefix, int) or isinstance(prefix, bool) or not 0 < prefix < len(ids) <= 2048:
        raise ValueError("Invalid prompt boundary or sequence length")
    if any(type(token) is not int or token < 0 for token in ids):
        raise ValueError("Invalid input token")
    if mask != [1] * len(ids) or len(labels) != len(ids):
        raise ValueError("Invalid attention/label length")
    if labels != [-100] * prefix + ids[prefix:]:
        raise ValueError("Prompt masking or answer labels are incorrect")


def tokenize_row(row, tokenizer):
    reject_controls(row["text"], tokenizer.all_special_tokens)
    reject_controls(row["target"], tokenizer.all_special_tokens)
    text, target = row["text"].strip(), row["target"].strip()
    prefix = tokenizer.apply_chat_template(
        [{"role": "user", "content": PROMPT.format(text=text)}], tokenize=False,
        add_generation_prompt=True, enable_thinking=False)
    prefix_ids = tokenizer(prefix, add_special_tokens=False)["input_ids"]
    ids = tokenizer(prefix + target + TERMINATOR, add_special_tokens=False)["input_ids"]
    if ids[:len(prefix_ids)] != prefix_ids:
        raise ValueError("Tokenizer changes tokens across the prompt/answer boundary")
    answer_ids = ids[len(prefix_ids):]
    if tokenizer.decode(answer_ids, skip_special_tokens=False, clean_up_tokenization_spaces=False) != target + TERMINATOR:
        raise ValueError("Supervised answer does not decode exactly to target and terminator")
    result = dict(row, text=text, target=target, input_ids=ids, attention_mask=[1] * len(ids),
                  labels=[-100] * len(prefix_ids) + answer_ids, prompt_tokens=len(prefix_ids))
    validate_row(result)
    return result


def jsonl(data):
    return [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]


def exclude_editorial_controls(rows, tokenizer):
    """Exclude only three pinned records, preserving their source data unchanged."""
    retained, exclusions, found = [], [], set()
    for row in rows:
        if row["id"] in CONTROL_EXCLUSIONS:
            if row["id"] in found or row["text"].count("<pad>") != 1:
                raise ValueError("Pinned editorial exclusion count/control mismatch")
            # Removal is only a check for additional controls, never a data rewrite.
            reject_controls(row["text"].replace("<pad>", ""), tokenizer.all_special_tokens)
            reject_controls(row["target"], tokenizer.all_special_tokens)
            found.add(row["id"])
            exclusions.append({
                **{key: row[key] for key in ("id", "record_id", "work_id", "revision", "credit")},
                "reason": CONTROL_EXCLUSIONS[row["id"]],
                "source_sha256": digest(row["text"].encode("utf-8")),
                "target_sha256": digest(row["target"].encode("utf-8")),
            })
        else:
            reject_controls(row["text"], tokenizer.all_special_tokens)
            reject_controls(row["target"], tokenizer.all_special_tokens)
            retained.append(row)
    if found != set(CONTROL_EXCLUSIONS):
        raise ValueError("Pinned editorial exclusion IDs are missing")
    return retained, exclusions


def bundle_checks(read):
    """Validate payloads, executing only the exact checksum-pinned upstream guard."""
    for name, expected in TOKENIZER_HASHES.items():
        if digest(read("tokenizer/" + name)) != expected:
            raise ValueError("Bundled tokenizer differs from pinned version")
    for name, expected in (("holdout.py", HOLDOUT_HASH), ("benchmark-holdout.json", POLICY_HASH)):
        if digest(read(name)) != expected:
            raise ValueError("Bundled holdout guard differs from pinned version")
    # The exact trusted module exports blocked_reason(row, rules), so verification
    # needs neither extraction nor the module's path-based policy() loader.
    guard = {"__file__": "checksum-verified-holdout.py"}
    exec(compile(read("holdout.py"), "<checksum-verified-holdout>", "exec"), guard)
    rules = json.loads(read("benchmark-holdout.json"))
    train_data = read("train.jsonl")
    provenance = json.loads(read("provenance.json"))
    qualification = provenance.get("qualification")
    if qualification is not None and qualification != QUALIFICATION:
        raise ValueError("Frozen qualification identity mismatch")
    expected_hash = QUALIFIED_TRAIN_HASH if qualification is not None else ORIGINAL_TOKENIZED_TRAIN_HASH
    expected_rows = QUALIFICATION["retained_rows"] if qualification is not None else 2484
    if digest(train_data) != expected_hash:
        raise ValueError("Frozen training payload checksum mismatch")
    rows = jsonl(train_data)
    if len(rows) != expected_rows or len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Training row count/identity mismatch")
    if qualification is not None and (provenance.get("training_rows") != len(rows)
            or provenance.get("token_count") != sum(len(row["input_ids"]) for row in rows)
            or provenance.get("max_tokens") != max(len(row["input_ids"]) for row in rows)):
        raise ValueError("Qualified training provenance counts mismatch")
    for row in rows:
        validate_row(row)
        reason = guard["blocked_reason"]({key: row[key] for key in SOURCE_KEYS}, rules)
        if reason:
            raise ValueError(f"Holdout exclusion: {row['id']}: {reason}")
    if len({(row["text"], row["target"]) for row in rows}) != len(rows):
        raise ValueError("Duplicate training pair")
    dev = jsonl(read("dev-inputs.jsonl"))
    validate_dev(dev)
    for row in dev:
        reason = guard["blocked_reason"](row, rules)
        if reason:
            raise ValueError(f"Holdout exclusion: {row['id']}: {reason}")
    return {"rows": len(rows), "dev_inputs": len(dev), "tokens": sum(len(r["input_ids"]) for r in rows)}


def validate_dev(dev):
    if len(dev) != 6 or len({row["id"] for row in dev}) != 6:
        raise ValueError("DEV input count/identity mismatch")
    for row in dev:
        if set(row) != DEV_OUTPUT_KEYS or row["source_language"] != "pal" or row["target_language"] != "fa":
            raise ValueError("DEV has unexpected fields, references or direction")
        reject_controls(row["text"])
        if row["prompt"] != PROMPT.format(text=row["text"]):
            raise ValueError("DEV prompt differs from the canonical translation prompt")


def result_allowed(name):
    parts = PurePosixPath(name).parts
    return (name in RESULT_ROOT or len(parts) == 2 and
            ((parts[0] in {"adapter", "canary-adapter"} and parts[1] in ADAPTER_FILES) or
             (parts[0] == "tokenizer" and parts[1] in TOKENIZER_HASHES)))


def verify_members(names, read):
    if len(names) != len(set(names)):
        raise ValueError("Duplicate archive members")
    for name in names:
        safe_name(name)
    manifest = json.loads(read("manifest.json"))
    entries = manifest.get("files", {})
    if manifest.get("schema") != 1 or not isinstance(entries, dict):
        raise ValueError("Unsupported manifest")
    if set(names) != set(entries) | {"manifest.json"}:
        raise ValueError("Unexpected or missing bundle members")
    kind = manifest.get("kind")
    if kind == "training-bundle":
        if set(entries) != BUNDLE_FILES:
            raise ValueError("Training bundle whitelist mismatch")
    elif kind == "run-results":
        if "status.json" not in entries or not all(result_allowed(name) for name in entries):
            raise ValueError("Result archive whitelist mismatch")
    else:
        raise ValueError("Unknown bundle kind")
    for name, entry in entries.items():
        safe_name(name)
        data = read(name)
        if len(data) != entry.get("bytes") or digest(data) != entry.get("sha256"):
            raise ValueError(f"File integrity mismatch: {name}")
    summary = bundle_checks(read) if kind == "training-bundle" else {"status": json.loads(read("status.json"))}
    return dict(summary, kind=kind, files=len(entries), integrity="PASS")


def directory_files(directory):
    files = {}
    for path in sorted(directory.rglob("*")):
        if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
            raise ValueError("Links are not allowed in bundles")
        if path.is_file():
            name = safe_name(path.relative_to(directory).as_posix())
            files[name] = path
    return files


def verify(path):
    path = Path(path)
    if path.is_dir():
        files = directory_files(path)
        return verify_members(list(files), lambda name: files[name].read_bytes())
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            if info.is_dir() or stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError("Directory/link archive members are not allowed")
        return verify_members(archive.namelist(), archive.read)


def manifest_for(files, kind):
    return encoded({"schema": 1, "kind": kind, "files": {
        name: {"sha256": file_hash(path), "bytes": path.stat().st_size}
        for name, path in sorted(files.items())}})


def write_archive(files, output, manifest):
    """Deterministic ZIP; exclusive create avoids replacing an earlier result."""
    output = Path(output)
    with output.open("xb") as stream, zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(set(files) | {"manifest.json"}):
            info = zipfile.ZipInfo(safe_name(name), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            if name == "manifest.json":
                archive.writestr(info, manifest)
            else:
                with files[name].open("rb") as source, archive.open(info, "w", force_zip64=True) as target:
                    for block in iter(lambda: source.read(1024 * 1024), b""):
                        target.write(block)


def prepare(translator, tokenizer_path, output):
    translator, tokenizer_path, output = map(Path, (translator, tokenizer_path, output))
    archive_path = output.with_suffix(output.suffix + ".zip")
    if output.exists() or archive_path.exists():
        raise ValueError("Output directory/archive already exists; use a new run directory")
    source = translator / "runs" / "datasets" / DATASET / "train.jsonl"
    holdout_path = translator / "pahlavi" / "holdout.py"
    policy_path = holdout_path.with_name("benchmark-holdout.json")
    check_hash(source, TRAIN_HASH)
    check_hash(holdout_path, HOLDOUT_HASH)
    check_hash(policy_path, POLICY_HASH)
    for name, expected in TOKENIZER_HASHES.items():
        check_hash(tokenizer_path / name, expected)
    own_dir = Path(__file__).resolve().parent
    payload = {name: (own_dir / name).read_bytes() for name in
               ("bundle.py", "runtime.py", "contract.json", "fetch_base.py", "requirements.in",
                "Dockerfile", ".dockerignore", "requirements-linux.lock")}
    payload.update({"holdout.py": holdout_path.read_bytes(), "benchmark-holdout.json": policy_path.read_bytes()})
    spec = importlib.util.spec_from_file_location("verified_pahlavi_holdout", holdout_path)
    holdout = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(holdout)
    rows = [r for r in jsonl(source.read_bytes()) if r.get("source_language") == "pal" and r.get("target_language") == "fa"]
    if len(rows) != 2609 or any(set(row) != SOURCE_KEYS for row in rows):
        raise ValueError("Unexpected forward dataset schema/count")
    holdout.require_allowed(rows)
    seen, unique, duplicates = {}, [], {}
    for row in rows:
        key = (row["text"].strip(), row["target"].strip())
        if key in seen:
            duplicates.setdefault(seen[key], []).append({k: row[k] for k in ("id", "record_id", "work_id", "revision", "credit")})
        else:
            seen[key] = row["id"]
            unique.append(row)
    if len(unique) != 2487:
        raise ValueError("Unexpected exact-pair deduplication count")
    # Heavy dependency is needed only here; verify and result packing are stdlib-only.
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_path), local_files_only=True, trust_remote_code=False)
    retained, exclusions = exclude_editorial_controls(unique, tokenizer)
    if len(retained) != 2484:
        raise ValueError("Unexpected row count after explicit editorial exclusions")
    tokenized = [tokenize_row(row, tokenizer) for row in retained]
    dev_source = own_dir.parent / "experiments" / "language-choice-dev-v1" / "inputs.jsonl"
    dev_rows = jsonl(dev_source.read_bytes())
    if any(set(row) != DEV_KEYS for row in dev_rows):
        raise ValueError("DEV input file contains unexpected fields or reference answers")
    dev = [r for r in dev_rows if r["source_language"] == "pal" and r["target_language"] == "fa"]
    holdout.require_allowed(dev)
    dev = [dict(row, text=row["text"].strip(), prompt=PROMPT.format(text=row["text"].strip())) for row in dev]
    payload["train.jsonl"] = b"".join(encoded(row) for row in tokenized)
    payload["dev-inputs.jsonl"] = b"".join(encoded(row) for row in dev)
    payload.update({"tokenizer/" + name: (tokenizer_path / name).read_bytes() for name in TOKENIZER_HASHES})
    payload["provenance.json"] = encoded({
        "dataset_sha256": TRAIN_HASH, "holdout_check": "PASS", "raw_forward_rows": len(rows),
        "deduplicated_rows": len(unique), "duplicates": duplicates, "prompt": PROMPT,
        "unique_before_exclusions": len(unique), "training_rows": len(tokenized),
        "explicit_exclusions": exclusions,
        "serialization": "user generation prefix (thinking disabled) + stripped target + <turn|>\\n",
        "loss": "assistant target and turn terminator only; entire prompt masked -100",
        "token_count": sum(len(row["input_ids"]) for row in tokenized),
        "max_tokens": max(len(row["input_ids"]) for row in tokenized),
        "dev_source_sha256": file_hash(dev_source), "dev_purpose": "historical exploratory inputs, no references",
        "training_or_inference_executed": False,
    })
    # Validate the completed payload before creating any destination files.
    bundle_checks(payload.__getitem__)
    output.mkdir(parents=True, exist_ok=False)
    for name, data in sorted(payload.items()):
        destination = output / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    files = directory_files(output)
    manifest = manifest_for(files, "training-bundle")
    (output / "manifest.json").write_bytes(manifest)
    verified = verify(output)
    write_archive(files, archive_path, manifest)
    verify(archive_path)
    return dict(verified, directory=str(output), archive=str(archive_path), archive_sha256=file_hash(archive_path))


def prepare_qualified(parent, qualified, output, contract_path=None):
    """Copy the frozen parent with the exact audited subset; no tokenization or launch."""
    parent, qualified, output = map(Path, (parent, qualified, output))
    archive_path = output.with_suffix(output.suffix + ".zip")
    if output.exists() or archive_path.exists():
        raise ValueError("Output directory/archive already exists; use a new run directory")
    check_hash(parent / "manifest.json", PARENT_MANIFEST_HASH)
    verify(parent)
    for name, expected in (("manifest.json", QUALIFIED_MANIFEST_HASH),
                           ("summary.json", QUALIFIED_SUMMARY_HASH), ("train.jsonl", QUALIFIED_TRAIN_HASH)):
        check_hash(qualified / name, expected)
    payload = {name: (parent / name).read_bytes() for name in BUNDLE_FILES}
    contract_data = Path(contract_path or Path(__file__).with_name("contract.json")).read_bytes()
    contract, original_contract = json.loads(contract_data), json.loads(payload["contract.json"])
    if set(contract) != set(original_contract) or any(
            contract[key] != original_contract[key] for key in original_contract if key not in {"budget", "cloud", "notes"}):
        raise ValueError("Qualified contract may change only budget, cloud timeout and notes")
    if set(contract["cloud"]) != set(original_contract["cloud"]) or any(
            contract["cloud"][key] != original_contract["cloud"][key]
            for key in original_contract["cloud"] if key != "native_timeout_minutes"):
        raise ValueError("Qualified contract must preserve cloud controls except timeout")
    train_data = (qualified / "train.jsonl").read_bytes()
    rows = jsonl(train_data)
    selected = {row["id"] for row in rows}
    original_subset = b"".join(line for line in payload["train.jsonl"].splitlines(keepends=True)
                               if json.loads(line)["id"] in selected)
    if original_subset != train_data:
        raise ValueError("Qualified rows must preserve exact parent bytes and order")
    provenance = json.loads(payload["provenance.json"])
    provenance.update(qualification=dict(QUALIFICATION), training_rows=len(rows),
                      token_count=sum(len(row["input_ids"]) for row in rows),
                      max_tokens=max(len(row["input_ids"]) for row in rows),
                      prepared_contract_sha256=digest(contract_data))
    payload.update({"train.jsonl": train_data, "provenance.json": encoded(provenance),
                    "bundle.py": Path(__file__).read_bytes(), "contract.json": contract_data})
    bundle_checks(payload.__getitem__)
    output.mkdir(parents=True, exist_ok=False)
    for name, data in sorted(payload.items()):
        destination = output / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    files = directory_files(output)
    manifest = manifest_for(files, "training-bundle")
    (output / "manifest.json").write_bytes(manifest)
    verified = verify(output)
    write_archive(files, archive_path, manifest)
    verify(archive_path)
    return dict(verified, directory=str(output), archive=str(archive_path), archive_sha256=file_hash(archive_path))


def pack_results(run_dir, output):
    run_dir, output = Path(run_dir).resolve(), Path(output).resolve()
    if output.is_relative_to(run_dir):
        raise ValueError("Result archive must be outside the run directory")
    files = {name: path for name, path in directory_files(run_dir).items() if result_allowed(name)}
    if "status.json" not in files:
        raise ValueError("Missing runtime status.json; do not infer success")
    status = json.loads(files["status.json"].read_bytes())
    if not isinstance(status, dict) or not status.get("status"):
        raise ValueError("Runtime status must identify the recorded run status")
    state = str(status["status"]).upper()
    if state in {"SUCCESS", "COMPLETE", "COMPLETED", "PASS", "TRAINING_COMPLETE", "CANARY_PASS"}:
        adapter = "canary-adapter" if state == "CANARY_PASS" else "adapter"
        if not {adapter + "/adapter_config.json", adapter + "/adapter_model.safetensors"} <= set(files):
            raise ValueError("Successful training status requires both final adapter files")
    # Deliberately omit optimizer checkpoints and full base weights. The runtime retains them locally.
    manifest = manifest_for(files, "run-results")
    write_archive(files, output, manifest)
    result = verify(output)
    return dict(result, archive=str(output), archive_sha256=file_hash(output))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prep = commands.add_parser("prepare")
    for name in ("translator", "tokenizer", "out"):
        prep.add_argument("--" + name, required=True)
    qualified = commands.add_parser("prepare-qualified")
    for name in ("parent", "qualified", "out"):
        qualified.add_argument("--" + name, required=True)
    qualified.add_argument("--contract", help="Reviewed contract; defaults to this helper's contract.json")
    commands.add_parser("verify").add_argument("bundle")
    results = commands.add_parser("pack-results")
    results.add_argument("run_dir")
    results.add_argument("out_zip")
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare(args.translator, args.tokenizer, args.out)
    elif args.command == "prepare-qualified":
        result = prepare_qualified(args.parent, args.qualified, args.out, args.contract)
    elif args.command == "verify":
        result = verify(args.bundle)
    else:
        result = pack_results(args.run_dir, args.out_zip)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
