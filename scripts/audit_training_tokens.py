"""Reconstruct every frozen training token from pinned Jinja/tokenizer bytes, offline."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloud_pilot import bundle

TRAIN_SHA = "844a5b64d43a423b69d5989527a53273290a43be15c399056c979f5abb0678a1"


def check_row(row, tokenizer, template, bos_token):
    bundle.validate_row(row)
    prefix = template.render(messages=[{"role": "user", "content": bundle.PROMPT.format(text=row["text"].strip())}],
                             add_generation_prompt=True, enable_thinking=False, bos_token=bos_token, tools=None)
    prefix_ids = tokenizer.encode(prefix, add_special_tokens=False).ids
    target = row["target"].strip() + bundle.TERMINATOR
    ids = tokenizer.encode(prefix + target, add_special_tokens=False).ids
    return {"id": row["id"], "prompt_matches": prefix_ids == row["input_ids"][:row["prompt_tokens"]],
            "prompt_count_matches": len(prefix_ids) == row["prompt_tokens"], "all_tokens_match": ids == row["input_ids"],
            "labels_match": row["labels"] == [-100] * len(prefix_ids) + ids[len(prefix_ids):],
            "decoded_answer_matches": tokenizer.decode(row["input_ids"][row["prompt_tokens"]:], skip_special_tokens=False) == target,
            "sequence_tokens": len(ids), "prompt_tokens": len(prefix_ids)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Preserve existing audit: output must be fresh")
    folder = ROOT / "resources/local/cloud-pilot-20260926-hf-v5"
    train = folder / "train.jsonl"
    bundle.check_hash(train, TRAIN_SHA)
    for name, digest in bundle.TOKENIZER_HASHES.items():
        bundle.check_hash(folder / "tokenizer" / name, digest)
    from tokenizers import Tokenizer
    from jinja2.sandbox import ImmutableSandboxedEnvironment
    config = json.loads((folder / "tokenizer/tokenizer_config.json").read_text("utf-8"))
    tokenizer = Tokenizer.from_file(str(folder / "tokenizer/tokenizer.json"))
    env = ImmutableSandboxedEnvironment(trim_blocks=True, lstrip_blocks=True, extensions=["jinja2.ext.loopcontrols"])
    def reject(message):
        raise ValueError(message)
    env.globals["raise_exception"] = reject
    template = env.from_string((folder / "tokenizer/chat_template.jinja").read_text("utf-8"))
    rows = bundle.jsonl(train.read_bytes())
    if len(rows) != 2484 or len({r["id"] for r in rows}) != 2484:
        raise ValueError("Frozen row coverage differs")
    checks = [check_row(row, tokenizer, template, config["bos_token"]) for row in rows]
    fields = ("prompt_matches", "prompt_count_matches", "all_tokens_match", "labels_match", "decoded_answer_matches")
    # A changed target must fail exact reconstruction even when token-array shapes remain valid.
    changed = dict(rows[0], target=rows[0]["target"] + "؟")
    assert not check_row(changed, tokenizer, template, config["bos_token"])["all_tokens_match"]
    failures = [row for row in checks if not all(row[key] for key in fields)]
    summary = {"status": "PASS" if not failures else "FAIL", "rows": len(checks), "failures": failures,
               "train_sha256": TRAIN_SHA, "tokenizer_files": bundle.TOKENIZER_HASHES,
               "script_sha256": bundle.file_hash(Path(__file__)), "bundle_helper_sha256": bundle.file_hash(Path(bundle.__file__)),
               "packages": {name: importlib.metadata.version(name) for name in ("tokenizers", "jinja2")},
               "method": "Independent pinned Jinja rendering plus tokenizers encode/decode; no Transformers import, inference or network",
               "maximum_sequence_tokens": max(row["sequence_tokens"] for row in checks), "negative_control_passed": True,
               "semantic_correctness_verified": False}
    args.output.mkdir(parents=True, exist_ok=False)
    data = b"".join(bundle.encoded(row) for row in checks)
    (args.output / "rows.jsonl").write_bytes(data)
    summary["rows_sha256"] = hashlib.sha256(data).hexdigest()
    (args.output / "summary.json").write_bytes(bundle.encoded(summary))
    print(json.dumps({k: summary[k] for k in ("status", "rows", "maximum_sequence_tokens", "negative_control_passed")}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
