"""Offline, immutable mixed-task census and fixed 96-update Gemma pilot."""
import argparse
from collections import Counter, defaultdict, deque
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from cloud_pilot import bundle

RELEASE = ROOT / "experiments/data-qualification-20260928/release-v1.json"
READY = ROOT / "resources/local/data-qualification-20260928/ready-v1"
TOKENIZER = ROOT / "resources/local/cloud-pilot-qualified-20260927/tokenizer"
OUT = ROOT / "resources/local/mixed-supervision-20260929/data"
MANIFEST = Path(__file__).with_name("data-manifest.json")
SEED = 3407
COUNTS = {"historical-control-fa": 2237, "lexical-fa": 2676, "lexical-en": 3506,
          "lexical-mmp-en": 1426, "pedagogy-fa": 240, "documentary-en": 57,
          "inscription-fa": 6, "edition-spans-en": 4}
PROMPTS = {
    "lexical-fa": "Give the complete published Persian meaning inventory for these Middle Persian forms in the stated source scope. Preserve all senses and alternatives; do not expand them into sentences.",
    "lexical-en": "Give the complete English dictionary sense structure for these Middle Persian forms in the stated edition and scope. Return JSON preserving all published sense numbers, component kinds, attributes, text, nested components and tails. Do not translate English into Persian or omit senses.",
    "lexical-mmp-en": "Give the complete published English meaning inventory for these Manichaean Middle Persian forms in the stated grammatical role and source scope. Preserve alternatives; do not expand them into sentences or translate English into Persian.",
    "pedagogy-fa": "Give the published Persian meaning for this Middle Persian teaching form or example under the supplied grammatical context. Preserve person, number, alternatives and editorial signs. This is a conditioned grammar task; do not supply missing context.",
    "documentary-en": "Translate this preserved Middle Persian documentary edition span into English under the supplied context. Preserve damage, uncertainty, editorial additions, names and quantities. Do not reconstruct missing prose.",
    "inscription-fa": "Translate exactly this supported Middle Persian inscription span into Persian under the supplied edition and scope. Preserve names, quantities and uncertainty; do not add neighboring text.",
    "edition-spans-en": "Translate exactly this published Middle Persian edition span into English under the supplied scope. Preserve uncertainty and quantities; do not supply missing agents, damaged material or neighboring clauses.",
}


def js(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def encoded(value):
    return (js(value) + "\n").encode("utf-8")


def sha(value):
    return hashlib.sha256(value).hexdigest()


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)


def rank(value):
    return sha(f"{SEED}:{value}".encode("utf-8"))


def balanced(rows, n):
    """Seeded within-group ordering and source/witness round robin, no replacement."""
    groups = defaultdict(list)
    for row in rows:
        groups[row["group"]].append(row)
    queues = [deque(sorted(groups[g], key=lambda r: rank(r["id"])))
              for g in sorted(groups, key=rank)]
    result = []
    while queues and len(result) < n:
        for queue in queues:
            if queue and len(result) < n:
                result.append(queue.popleft())
        queues = [q for q in queues if q]
    assert len(result) == n, (n, len(result))
    return result


def stats(rows):
    result = {}
    for task in COUNTS:
        values = [r for r in rows if r["task"] == task]
        lengths = sorted(len(r["input_ids"]) for r in values)
        result[task] = {"rows": len(values), "sequence_tokens": sum(lengths),
                        "prompt_tokens": sum(r["prompt_tokens"] for r in values),
                        "supervised_tokens": sum(len(r["input_ids"]) - r["prompt_tokens"] for r in values),
                        "min_sequence": min(lengths, default=0), "max_sequence": max(lengths, default=0),
                        "median_sequence": lengths[len(lengths) // 2] if lengths else 0}
    return result


def build():
    from tokenizers import Tokenizer
    from jinja2.sandbox import ImmutableSandboxedEnvironment
    release = json.loads(RELEASE.read_text("utf-8"))
    for name, digest in bundle.TOKENIZER_HASHES.items():
        bundle.check_hash(TOKENIZER / name, digest)
    config = json.loads((TOKENIZER / "tokenizer_config.json").read_text("utf-8"))
    tok_json = json.loads((TOKENIZER / "tokenizer.json").read_text("utf-8"))
    specials = [r["content"] for r in tok_json["added_tokens"] if r["special"]]
    tokenizer = Tokenizer.from_file(str(TOKENIZER / "tokenizer.json"))
    env = ImmutableSandboxedEnvironment(trim_blocks=True, lstrip_blocks=True, extensions=["jinja2.ext.loopcontrols"])
    def reject(message):
        raise ValueError(message)
    env.globals["raise_exception"] = reject
    template = env.from_string((TOKENIZER / "chat_template.jinja").read_text("utf-8"))

    def tokenize(identifier, task, prompt, answer):
        prefix = template.render(messages=[{"role": "user", "content": prompt}],
                                 add_generation_prompt=True, enable_thinking=False,
                                 bos_token=config["bos_token"], tools=None)
        prefix_ids = tokenizer.encode(prefix, add_special_tokens=False).ids
        ids = tokenizer.encode(prefix + answer + bundle.TERMINATOR, add_special_tokens=False).ids
        if ids[:len(prefix_ids)] != prefix_ids:
            raise ValueError("prompt_answer_boundary")
        if tokenizer.decode(ids[len(prefix_ids):], skip_special_tokens=False) != answer + bundle.TERMINATOR:
            raise ValueError("answer_decode_not_exact")
        if not 0 < len(prefix_ids) < len(ids) <= 2048:
            raise ValueError(f"sequence_length:{len(ids)}")
        return {"id": identifier, "task": task, "input_ids": ids, "attention_mask": [1] * len(ids),
                "labels": [-100] * len(prefix_ids) + ids[len(prefix_ids):], "prompt_tokens": len(prefix_ids)}

    pool, projections, audits, excluded, duplicates = [], [], [], [], []
    seen, input_hashes, parity_count, cpd_checks = {}, {}, 0, 0
    for task, count in COUNTS.items():
        path = READY / (task + ".jsonl")
        digest = release["outputs"][path.name]["sha256"]
        bundle.check_hash(path, digest)
        input_hashes[path.relative_to(ROOT).as_posix()] = digest
        rows = bundle.jsonl(path.read_bytes())
        assert len(rows) == count and len({r["id"] for r in rows}) == count
        for raw in rows:
            identifier = raw["id"]
            if task == "historical-control-fa":
                learning = {"source": raw["text"], "target": raw["target"], "context": {}}
                prompt = bundle.PROMPT.format(text=raw["text"].strip())
                answer = raw["target"].strip()
                group = raw["work_id"]
            else:
                assert raw["task"] == task and set(raw["learning"]) == {"source", "target", "context"}
                learning = raw["learning"]
                context = learning["context"]
                source = learning["source"] if isinstance(learning["source"], str) else js(learning["source"])
                prompt = PROMPTS[task] + "\nContext:\n" + js(context) + "\nSource:\n" + source
                answer = learning["target"]
                if task == "lexical-en":
                    answer = js(answer)
                    assert json.loads(answer) == learning["target"]
                    cpd_checks += 1
                assert isinstance(answer, str)
                group = next((js(context[k]) for k in ("witness_group", "source_scope", "context_family", "phenomenon", "grammar_as_published", "edition") if context.get(k)), task)
            projections.append({"id": identifier, "task": task, "learning": learning})
            key = js({"task": task, "learning": learning})
            if key in seen:
                duplicates.append({"id": identifier, "canonical_id": seen[key], "task": task,
                                   "reason": "exact_task_source_target_and_complete_context_identity"})
                continue
            seen[key] = identifier
            try:
                for value in strings(learning):
                    if value.strip():
                        bundle.reject_controls(value, specials)
                result = tokenize(identifier, task, prompt, answer)
            except ValueError as error:
                excluded.append({"id": identifier, "task": task, "reason": str(error)})
                if task == "historical-control-fa":
                    raise
                continue
            if task == "historical-control-fa":
                assert all(result[k] == raw[k] for k in bundle.TOKEN_KEYS), identifier
                parity_count += 1
            audits.append({"id": identifier, "task": task, "group": group,
                           "learning_sha256": sha(encoded(learning)), "prompt_sha256": sha(prompt.encode("utf-8")),
                           "answer_sha256": sha(answer.encode("utf-8")), "prompt_tokens": result["prompt_tokens"],
                           "sequence_tokens": len(result["input_ids"]), "exact_answer_decode": True,
                           "historical_parity": task == "historical-control-fa"})
            pool.append(dict(result, group=group, pair_key=js([learning["source"], learning["target"]])))
    assert parity_count == 2237 and cpd_checks == 3506
    by_task = {task: [r for r in pool if r["task"] == task] for task in COUNTS}
    historical = balanced(by_task["historical-control-fa"], 1152)
    lexical = []
    for task, n in (("lexical-fa", 96), ("lexical-en", 64), ("lexical-mmp-en", 32)):
        lexical.extend(balanced(by_task[task], n))
    lexical.sort(key=lambda r: rank("lexical:" + r["id"]))
    other = balanced(by_task["documentary-en"], 57) + balanced(by_task["edition-spans-en"], 4)
    kanheri, pairs = [], set()
    for row in balanced(by_task["inscription-fa"], len(by_task["inscription-fa"])):
        if row["pair_key"] not in pairs:
            kanheri.append(row)
            pairs.add(row["pair_key"])
    assert len(kanheri) == 4
    other += kanheri + balanced(by_task["pedagogy-fa"], 127)
    other.sort(key=lambda r: rank("other:" + r["id"]))
    train = []
    for step in range(96):
        block = historical[step * 12:(step + 1) * 12] + lexical[step * 2:(step + 1) * 2] + other[step * 2:(step + 1) * 2]
        assert len(block) == 16 and sum(r["task"] == "historical-control-fa" for r in block) == 12
        train.extend(block)
    assert len(train) == len({r["id"] for r in train}) == 1536
    # Negative checks guard control rejection and exact historical reconstruction.
    for bad in ("x<pad>", "x<turn|>", "x" + specials[0]):
        try:
            bundle.reject_controls(bad, specials)
        except ValueError:
            pass
        else:
            raise AssertionError("Reserved-token negative control failed")
    first = projections[0]
    changed = tokenize(first["id"], first["task"], bundle.PROMPT.format(text=first["learning"]["source"].strip()), first["learning"]["target"].strip() + "؟")
    assert changed["input_ids"] != pool[0]["input_ids"]
    def clean(row):
        return {k: v for k, v in row.items() if k not in ("group", "pair_key")}
    payloads = {"train.jsonl": b"".join(encoded(clean(r)) for r in train),
                "pool.jsonl": b"".join(encoded(clean(r)) for r in pool),
                "learning-projections.jsonl": b"".join(encoded(r) for r in projections),
                "row-audit.jsonl": b"".join(encoded(r) for r in audits),
                "exclusions.jsonl": b"".join(encoded(r) for r in excluded),
                "duplicates.jsonl": b"".join(encoded(r) for r in duplicates)}
    manifest = {"status": "PASS", "seed": SEED, "release_sha256": bundle.file_hash(RELEASE),
                "input_sha256": input_hashes, "tokenizer_sha256": bundle.TOKENIZER_HASHES,
                "script_sha256": bundle.file_hash(Path(__file__)), "bundle_helper_sha256": bundle.file_hash(Path(bundle.__file__)),
                "packages": {name: importlib.metadata.version(name) for name in ("tokenizers", "jinja2")},
                "raw_counts": COUNTS, "pool_counts": dict(Counter(r["task"] for r in pool)),
                "exact_duplicate_collapses": duplicates, "exclusions": excluded,
                "historical_all_array_parity": parity_count, "cpd_exact_structure_reconstruction": cpd_checks,
                "reserved_token_negative_checks": 3, "changed_answer_negative_check": True,
                "max_sequence_tokens": 2048, "truncated_rows": 0,
                "pilot": {"updates": 96, "microbatch": 1, "gradient_accumulation": 16,
                          "per_update": {"historical": 12, "lexical": 2, "other": 2},
                          "selected_ids_in_order": [r["id"] for r in train], "task_statistics": stats(train)},
                "pool_task_statistics": stats(pool), "sampling": "SHA256(seed:id), source/witness group round robin without replacement; task quotas frozen before any model output",
                "model_visible": "Historical text/target only with original prompt; new learning fields only. No origin, notes, credits or raw evidence.",
                "cpd_serialization": "Deterministic compact JSON target, exact recursive reconstruction including nested text/tail, roles, attributes and published numbering; all source variants together.",
                "scope": "Complete released corpus census and eligible pool; pilot is a bounded subset, not full-pool exposure. English targets remain English.",
                "benchmark_content_read": False, "network_or_weights_used": False,
                "outputs": {name: {"sha256": sha(data), "bytes": len(data), "rows": data.count(b'\n')} for name, data in payloads.items()}}
    payloads["census.json"] = encoded(manifest)
    return payloads, encoded(manifest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check and (OUT.exists() or MANIFEST.exists()):
        raise SystemExit("Refusing overwrite: immutable output already exists")
    payloads, manifest = build()
    if args.check:
        assert set(p.name for p in OUT.iterdir()) == set(payloads), "Output file set changed"
        for name, data in payloads.items():
            assert (OUT / name).read_bytes() == data, name
        assert MANIFEST.read_bytes() == manifest, "manifest changed"
    else:
        OUT.mkdir(parents=True, exist_ok=False)
        for name, data in payloads.items():
            with (OUT / name).open("xb") as stream:
                stream.write(data)
        with MANIFEST.open("xb") as stream:
            stream.write(manifest)
    value = json.loads(manifest)
    print(json.dumps({"status": "PASS", "replay": args.check, "pool_counts": value["pool_counts"],
                      "exclusions": value["exclusions"], "duplicates": len(value["exact_duplicate_collapses"]),
                      "train_sha256": value["outputs"]["train.jsonl"]["sha256"],
                      "manifest_sha256": sha(manifest)}, indent=2))


if __name__ == "__main__":
    main()
