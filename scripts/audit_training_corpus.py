"""Read-only, exhaustive mechanical audit of the frozen 2,484-row TRAIN.

Reports are new artifacts. No source, target, split or review decision is changed.
Mechanical agreement with an archive is not a semantic or expert endorsement.
"""
import argparse
import ast
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
import time
import unicodedata


STUDY_ROOT = Path(__file__).resolve().parents[1]
TRANSLATOR = Path(r"[USER_HOME]\Documents\Codex Projects\01-Software\Pahlavi Translator")
DATASET_ID = "6f442563128d3a4c49dd5024af6882f6911b3f1b11eb5a2d4ef0d28a453acf0c"
REVIEW_ID = "560dcebcf0c20771e7759d45192a3b9555ad4876a272682fb734652a1128e6dc"
TRAIN_SHA = "844a5b64d43a423b69d5989527a53273290a43be15c399056c979f5abb0678a1"
EXPORT_SHA = "c42e0a5a0d4d108218a0481ca073c07c6bb00cdcba0bffb462b67bb6d7a60789"
BUNDLE_PINS = {
    "manifest.json": "496cd9af52b2167c1895ba00f942d0fbc2b6c8aa6bdb6c23dbcd661a5f9218c6",
    "bundle.py": "9721bcb2152b9f5e2fe1670b5ca280950dcfa2a81eefb13e132ac11dd2bbb1ce",
    "holdout.py": "90d66c53c03870413d86b4ac2bd77d6e95010bd316ed0c01c3414ccc68ad67c9",
    "benchmark-holdout.json": "fead263bb73e4797c09595320aeeefb6cf7e553510e3fb08a932700ffaaa55cc",
    "train.jsonl": TRAIN_SHA,
    "provenance.json": "556272526fe9563c98d7a950496ad537f651e0780702b914733f23fc3a15c47e",
}
DATASET_PINS = {
    "manifest.json": "190bc7906fa10396dc07b8e92b7bfcfe25694f6295e0f9592306b1ef7410186a",
    "train-records.jsonl": "3b3edf5550e95b13baaf9842ecaeaf53a50a0aa130d9a5dfe17d366ee62d7d43",
    "dev-records.jsonl": "6f341a94518405d5569b0d0cb806e38b92f0326c3ef9e1840dbc3b01e2f863e2",
    "test-records.jsonl": "ea510178112a75369f152bb3891cdc123702f06dc7b5b6ecbab105dead5195c7",
    "train.jsonl": "485d063523b9efb7692c0384cfc9a87aafb3c2a86aaf3e16848eaab3fdefd070",
}
REVIEW_PINS = {
    "manifest.json": "77bff33395813be63cb64acabd2ca0b70908ebf0918cda4e0031b03d8635be25",
    "policy.json": "2c545aafaa5e64a16e4dfde45f10339676ade81b60ac774bff1bf8d33a1b9f1c",
    "records.jsonl": "bde1f730f046de9c4f448f35c56d68bc903761603b0cc1704b80764b4d341051",
    "source.jsonl": EXPORT_SHA,
    "exceptions.json": "4228ca306c2675ca779a2f1c166729d293d4cd3220345e9d16c2f2f39e69bbce",
}
HELPER_PINS = {
    "pahlavi/importers.py": "d3ca1662f4906087469c64d8150f7bf8f328a5e415fa4363750686e5c02ee4ea",
    "pahlavi/curation.py": "716094cfa3b50cd1f1701b714f099f6db0e94ea399fc504194f92cd484584be7",
}
TOKEN_PROOF_PINS = {
    "experiments/train-audit-20260927/token-reconstruction/summary.json": "ed7253282527259b599f3ef25c691352736b5b616952e6cb59fb0eb3cdfb65b2",
    "experiments/train-audit-20260927/token-reconstruction/rows.jsonl": "3964e97059d1511b13c48a86cbff1a004f0efdf773739beed7c67a836c3609b4",
    "scripts/audit_training_tokens.py": "199009cba490f4c39a6da288fc70b3abbf2a2bfef243ac8dec0d765423a5c2fd",
}
NEAR_THRESHOLD = 0.8


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value):
    return sha256(value).hexdigest()


def jsonl(data):
    return [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]


def unique(rows, key="id"):
    result = {}
    for row in rows:
        value = str(row[key])
        if value in result:
            raise ValueError(f"Duplicate {key}: {value}")
        result[value] = row
    return result


def checked(path, expected, inputs):
    path = Path(path).resolve()
    data = path.read_bytes()
    actual = digest(data)
    inputs[str(path)] = {"sha256": actual, "bytes": len(data)}
    if actual != expected:
        raise ValueError(f"Pinned input hash mismatch: {path}")
    return data


def source_tokens(text):
    """NFC then casefold, whitespace tokens, boundary Unicode P* removal only."""
    result = []
    for token in unicodedata.normalize("NFC", text).casefold().split():
        while token and unicodedata.category(token[0]).startswith("P"):
            token = token[1:]
        while token and unicodedata.category(token[-1]).startswith("P"):
            token = token[:-1]
        if token:
            result.append(token)
    return tuple(result)


def target_tokens(text):
    text = unicodedata.normalize("NFC", text).casefold().replace("ي", "ی").replace("ك", "ک")
    return tuple(re.findall(r"[^\W_]+", text))


def normalized_target(text):
    return " ".join(unicodedata.normalize("NFC", text).casefold().split())


def source_helpers(importer_data, curation_data):
    # Only these checksum-pinned pure helpers execute; importing their parent
    # modules would load application/store code and unnecessary dependencies.
    nodes = []
    for data, functions, assignments in ((importer_data, {"joined"}, set()),
                                          (curation_data, {"citation_parts"}, {"CITATION"})):
        for node in ast.parse(data).body:
            if isinstance(node, ast.FunctionDef) and node.name in functions:
                nodes.append(node)
            elif isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in assignments for t in node.targets):
                nodes.append(node)
    namespace = {"re": re}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "<pinned-source-helpers>", "exec"), namespace)
    return namespace["joined"], namespace["citation_parts"]


def projection_errors(row, record):
    if record is None:
        return ["missing_original_train_record"]
    expected = {
        "id": record["id"] + ":pal>fa", "record_id": record["id"],
        "revision": digest(canonical(record)), "work_id": record["work_id"],
        "text": record["transcription"].strip(),
        "target": record["translations"]["fa"]["text"].strip(),
        "credit": record["translations"]["fa"]["credit"],
        "source_language": "pal", "target_language": "fa",
    }
    return ["record_projection_mismatch:" + key for key, value in expected.items() if row.get(key) != value]


def raw_projection_errors(row, record, unit, joined, citation_parts):
    """Reproduce pinned curation and final TRAIN stripping, without changing input.

    Curation extracts the target from the collected field. Its raw/collected
    translation comparison omits blank lines but preserves nonblank line text.
    The frozen bundle subsequently strips outer source/target whitespace.
    """
    raw = unit["raw_source_unit"]
    source, edition = citation_parts(joined(raw.get("Transcription")))
    target, credit = citation_parts(joined(unit["farsi_translation"]))
    errors = []
    if (source.strip(), target.strip(), credit, edition) != (row["text"], row["target"], row["credit"], record["edition"]):
        errors.append("raw_citation_projection_mismatch")
    raw_translation = "\n".join(line for line in joined(raw.get("Translation")).splitlines() if line.strip())
    collected_translation = "\n".join(line for line in joined(unit["farsi_translation"]).splitlines() if line.strip())
    if joined(unit["transcription"]) != joined(raw.get("Transcription")) or raw_translation != collected_translation:
        errors.append("export_raw_fields_mismatch")
    return errors


def validate_token_proof(summary, proof_rows, train, tokenizer_hashes):
    """Consume existing independent evidence, never infer it from prose or flags."""
    if (summary.get("status") != "PASS" or summary.get("failures") != []
            or summary.get("train_sha256") != TRAIN_SHA or summary.get("rows") != len(train)
            or summary.get("tokenizer_files") != tokenizer_hashes
            or summary.get("bundle_helper_sha256") != BUNDLE_PINS["bundle.py"]
            or summary.get("script_sha256") != TOKEN_PROOF_PINS["scripts/audit_training_tokens.py"]
            or summary.get("rows_sha256") != TOKEN_PROOF_PINS["experiments/train-audit-20260927/token-reconstruction/rows.jsonl"]
            or summary.get("negative_control_passed") is not True):
        raise ValueError("Token proof identity/status mismatch")
    proof = unique(proof_rows)
    if set(proof) != {row["id"] for row in train}:
        raise ValueError("Token proof does not cover every TRAIN ID exactly once")
    checks = ("prompt_matches", "prompt_count_matches", "all_tokens_match", "labels_match", "decoded_answer_matches")
    for row in train:
        item = proof[row["id"]]
        if (any(item.get(key) is not True for key in checks)
                or item.get("prompt_tokens") != row["prompt_tokens"]
                or item.get("sequence_tokens") != len(row["input_ids"])):
            raise ValueError("Token proof row mismatch: " + row["id"])
    return proof


def adjacency(raw_rows):
    """Neighbors are observed raw ChapterCode/Sequence order, never ID arithmetic."""
    chapters = defaultdict(list)
    for row in raw_rows:
        unit = row["raw_source_unit"]
        chapters[str(unit["ChapterCode"])].append(row)
    result = {}
    for chapter, rows in chapters.items():
        rows.sort(key=lambda row: (int(row["raw_source_unit"]["Sequence"]), row["id"]))
        sequences = Counter(int(row["raw_source_unit"]["Sequence"]) for row in rows)
        for index, row in enumerate(rows):
            result[row["id"]] = {
                "chapter": chapter, "sequence": int(row["raw_source_unit"]["Sequence"]),
                "sequence_ambiguous": any(count > 1 for count in sequences.values()),
                "previous": rows[index - 1] if index else None,
                "next": rows[index + 1] if index + 1 < len(rows) else None,
            }
    return result


def suffix_prefix(left, right, minimum=3):
    a, b = target_tokens(left), target_tokens(right)
    for count in range(min(len(a), len(b)), minimum - 1, -1):
        if a[-count:] == b[:count]:
            return {"tokens": count, "normalized_overlap": " ".join(a[-count:])}
    return None


def marker_inventory(text):
    # Ordinary sentence questions are counted separately, not called uncertainty.
    patterns = {
        "ellipsis": r"…|\.{3,}", "square_brackets": r"\[|\]",
        "angle_brackets": r"[<>]", "editorial_asterisk": r"\*",
        "explicit_question_annotation": r"[\[(]\s*[?؟]+\s*[\])]",
        "replacement_character": r"\ufffd",
    }
    return {"editorial_or_damage_markers": {name: len(re.findall(pattern, text)) for name, pattern in patterns.items()},
            "ordinary_question_punctuation_count": len(re.findall(r"[?؟]", text))}


def boundary_flags(source, target, previous_target=None, next_target=None):
    flags = []
    for direction, left, right in (("previous_to_current", previous_target, target),
                                    ("current_to_next", target, next_target)):
        if left is not None and right is not None:
            overlap = suffix_prefix(left, right)
            if overlap:
                flags.append({"kind": "adjacent_target_overlap", "direction": direction, **overlap})
    tokens = target_tokens(target)
    if tokens and (tokens[-1] in {"و", "یا", "اگر", "که", "تا", "زیرا", "چون"}
                   or tokens[-2:] == ("خود", "را")):
        flags.append({"kind": "possibly_unfinished_target_ending", "tail": " ".join(tokens[-5:])})
    a, b = len(source_tokens(source)), len(tokens)
    if a >= 8 and b >= 8 and (b / a > 4 or b / a < 0.25):
        flags.append({"kind": "source_target_length_outlier", "source_tokens": a, "target_tokens": b})
    return flags


def duplicate_groups(rows):
    sources, targets, pairs = defaultdict(list), defaultdict(list), defaultdict(list)
    for row in rows:
        sources[source_tokens(row["text"])].append(row)
        targets[target_tokens(row["target"])].append(row)
        pairs[(row["text"], row["target"])].append(row)
    findings = defaultdict(list)
    for key, members in sources.items():
        if len(members) > 1:
            kind = ("normalized_source_target_variants" if len({normalized_target(r["target"]) for r in members}) > 1
                    else "normalized_source_duplicate")
            for row in members:
                findings[row["id"]].append({"kind": kind, "record_ids": [r["record_id"] for r in members]})
    for key, members in targets.items():
        if len({source_tokens(r["text"]) for r in members}) > 1:
            for row in members:
                findings[row["id"]].append({"kind": "shared_target_distinct_sources", "record_ids": [r["record_id"] for r in members]})
    for members in pairs.values():
        if len(members) > 1:
            for row in members:
                findings[row["id"]].append({"kind": "exact_pair_duplicate", "record_ids": [r["record_id"] for r in members]})
    return findings


def near_sources(train, heldout, emit, progress=None, threshold=NEAR_THRESHOLD):
    """Enumerate EVERY directed TRAIN/heldout pair, with safe upper-bound rejects.

    SequenceMatcher is deliberately TRAIN as a, heldout as b; no sampling,
    shingle caps, common-bucket omission, or approximate candidate generation.
    """
    prepared = [(row, source_tokens(row["transcription"])) for row in heldout]
    prepared = [(row, tokens, Counter(tokens)) for row, tokens in prepared]
    counts = Counter(total_pairs=len(train) * len(heldout), pairs_enumerated=0,
                     empty_rejected=0, length_bound_rejected=0, multiset_bound_rejected=0,
                     sequence_comparisons=0, matches=0)
    for index, left in enumerate(train, 1):
        a = source_tokens(left["text"])
        ac = Counter(a)
        for right, b, bc in prepared:
            counts["pairs_enumerated"] += 1
            total = len(a) + len(b)
            if not a or not b:
                counts["empty_rejected"] += 1
                continue
            if 2 * min(len(a), len(b)) / total < threshold:
                counts["length_bound_rejected"] += 1
                continue
            small, large = (ac, bc) if len(ac) < len(bc) else (bc, ac)
            overlap = sum(min(count, large.get(token, 0)) for token, count in small.items())
            if 2 * overlap / total < threshold:
                counts["multiset_bound_rejected"] += 1
                continue
            counts["sequence_comparisons"] += 1
            ratio = SequenceMatcher(None, a, b, autojunk=False).ratio()
            if ratio >= threshold:
                counts["matches"] += 1
                emit({"train_id": left["id"], "train_record_id": left["record_id"],
                      "heldout_id": right["id"], "heldout_work_id": right["work_id"],
                      "heldout_split": right["split"], "ratio": ratio,
                      "train_source_sha256": digest(left["text"].encode()),
                      "heldout_source_sha256": digest(right["transcription"].encode())})
        if progress and (index % 128 == 0 or index == len(train)):
            progress(index, dict(counts))
    if counts["pairs_enumerated"] != counts["total_pairs"]:
        raise ValueError("Incomplete near-source scan")
    return dict(counts, completed=True)


def write_json(path, value):
    with Path(path).open("xb") as stream:
        stream.write(canonical(value) + b"\n")


def write_line(stream, value):
    stream.write(canonical(value) + b"\n")


def audit(study_root, translator, output):
    started = time.monotonic()
    study_root, translator, output = (Path(x).resolve() for x in (study_root, translator, output))
    bundle_path = study_root / "resources/local/cloud-pilot-20260926-hf-v5"
    source_root = study_root / "sources/local/parsig-2026-09-20"
    dataset = translator / "runs/datasets" / DATASET_ID
    review = translator / "data/research-reviews" / REVIEW_ID
    if any(output.is_relative_to(folder) for folder in (bundle_path, source_root, translator)):
        raise ValueError("Audit output must be outside authoritative input directories")
    output.mkdir(parents=True, exist_ok=False)
    inputs = {}
    try:
        bundles = {name: checked(bundle_path / name, value, inputs) for name, value in BUNDLE_PINS.items()}
        datasets = {name: checked(dataset / name, value, inputs) for name, value in DATASET_PINS.items()}
        reviews = {name: checked(review / name, value, inputs) for name, value in REVIEW_PINS.items()}
        helpers = {name: checked(translator / name, value, inputs) for name, value in HELPER_PINS.items()}
        raw_data = checked(source_root / "exports/text-units.jsonl", EXPORT_SHA, inputs)
        joined, citation_parts = source_helpers(helpers["pahlavi/importers.py"], helpers["pahlavi/curation.py"])
        bundle = {"__file__": str(bundle_path / "bundle.py"), "__name__": "verified_audit_bundle"}
        exec(compile(bundles["bundle.py"], bundle["__file__"], "exec"), bundle)
        guard = {"__file__": str(bundle_path / "holdout.py"), "__name__": "verified_audit_holdout"}
        exec(compile(bundles["holdout.py"], guard["__file__"], "exec"), guard)
        rules = json.loads(bundles["benchmark-holdout.json"])
        for name, expected in bundle["TOKENIZER_HASHES"].items():
            checked(bundle_path / "tokenizer" / name, expected, inputs)
        train = jsonl(bundles["train.jsonl"])
        if len(train) != 2484:
            raise ValueError("Expected exactly 2,484 frozen TRAIN rows")
        unique(train)
        unique(train, "record_id")
        token_files = {name: checked(study_root / name, value, inputs) for name, value in TOKEN_PROOF_PINS.items()}
        token_proof = validate_token_proof(
            json.loads(token_files["experiments/train-audit-20260927/token-reconstruction/summary.json"]),
            jsonl(token_files["experiments/train-audit-20260927/token-reconstruction/rows.jsonl"]),
            train, bundle["TOKENIZER_HASHES"])
        records = unique(jsonl(datasets["train-records.jsonl"]))
        curated = unique(jsonl(reviews["records.jsonl"]))
        raw = unique(jsonl(raw_data))
        neighbors = adjacency(list(raw.values()))
        heldout = [dict(row, split=split) for split in ("dev", "test")
                   for row in jsonl(datasets[split + "-records.jsonl"])]
        unique(heldout)
        by_held_id = {r["id"]: r for r in heldout}
        held_works = {r["work_id"] for r in heldout}
        held_sources, held_targets = defaultdict(list), defaultdict(list)
        for row in heldout:
            held_sources[source_tokens(row["transcription"])].append(row["id"])
            if "fa" in row["translations"]:
                held_targets[target_tokens(row["translations"]["fa"]["text"])].append(row["id"])
        # Reconstruct only the frozen Gemma selection; never rebuild/reassign splits.
        forward = [r for r in jsonl(datasets["train.jsonl"]) if r["source_language"] == "pal" and r["target_language"] == "fa"]
        seen, retained, duplicates, duplicate_count = {}, [], {}, 0
        for row in forward:
            pair = (row["text"].strip(), row["target"].strip())
            if pair in seen:
                duplicate_count += 1
                duplicates.setdefault(seen[pair], []).append({key: row[key] for key in ("id", "record_id", "work_id", "revision", "credit")})
                continue
            seen[pair] = row["id"]
            if row["id"] not in bundle["CONTROL_EXCLUSIONS"]:
                retained.append(dict(row, text=row["text"].strip(), target=row["target"].strip()))
        selection_errors = []
        if (len(forward), len(seen), len(retained)) != (2609, 2487, 2484):
            selection_errors.append("selection_count_mismatch")
        if duplicates != json.loads(bundles["provenance.json"])["duplicates"]:
            selection_errors.append("duplicate_provenance_mismatch")
        for actual, original in zip(train, retained):
            if {key: actual[key] for key in bundle["SOURCE_KEYS"]} != original:
                selection_errors.append("selection_projection_mismatch:" + actual["id"])
        # Read and hash every required original response once.
        response_units = {}
        for row in train:
            metadata = raw[row["record_id"]]["source"]
            name = metadata["file"]
            if name in response_units:
                continue
            path = (source_root / name).resolve()
            if not path.is_relative_to(source_root):
                raise ValueError("Raw response path escapes source archive")
            data = checked(path, metadata["sha256"], inputs)
            if len(data) != metadata["bytes"]:
                raise ValueError("Raw response byte length mismatch")
            response_units[name] = unique(json.loads(data), "Code")
        print(json.dumps({"phase": "archive_identity_checked", "rows": len(train), "responses": len(response_units)}), flush=True)
        duplicate_flags = duplicate_groups(train)
        near_by_train = defaultdict(list)
        with (output / "near-source-pairs.jsonl").open("xb") as stream:
            def emit(pair):
                near_by_train[pair["train_id"]].append({"kind": "heldout_near_source", **pair})
                write_line(stream, pair)
            scan = near_sources(train, heldout, emit, lambda index, counts: print(
                json.dumps({"phase": "near_source_scan", "rows_completed": index, **counts}), flush=True))
        flags_count, errors_count, inventory_count = Counter(), Counter(), Counter()
        flagged_rows = mechanical_failed = known_spill = 0
        def excerpt(unit):
            if unit is None:
                return None
            source, edition = citation_parts(joined(unit["transcription"]))
            target, credit = citation_parts(joined(unit["farsi_translation"]))
            return {"record_id": unit["id"], "chapter_id": unit["chapter_id"], "sequence": unit["sequence"],
                    "source_text": source, "target_text": target, "edition": edition, "credit": credit,
                    "notes": unit.get("notes", []), "additional_layers": unit.get("additional_layers", []),
                    "raw_pointer": unit["source"]}
        with (output / "ledger.jsonl").open("xb") as ledger, (output / "review-candidates.jsonl").open("xb") as candidates:
            for index, row in enumerate(train, 1):
                record = records.get(row["record_id"])
                unit = raw[row["record_id"]]
                errors = projection_errors(row, record)
                if record != curated.get(row["record_id"]):
                    errors.append("curation_snapshot_record_mismatch")
                raw_unit = unit["raw_source_unit"]
                if response_units[unit["source"]["file"]].get(row["record_id"].removeprefix("parsig:")) != raw_unit:
                    errors.append("original_response_unit_mismatch")
                if str(raw_unit["Code"]) != row["record_id"].removeprefix("parsig:") or str(raw_unit["ChapterCode"]) != str(unit["chapter_id"]):
                    errors.append("raw_identity_mismatch")
                if (str(unit["book_id"]) != row["work_id"].removeprefix("parsig:")
                        or int(raw_unit["Sequence"]) != int(unit["sequence"])
                        or record["source_sha256"] != EXPORT_SHA
                        or record["provenance"]["source"] != unit["source"]):
                    errors.append("raw_provenance_metadata_mismatch")
                verified_response = inputs[str((source_root / unit["source"]["file"]).resolve())]
                if any(verified_response[key] != unit["source"][key] for key in ("sha256", "bytes")):
                    errors.append("row_response_hash_or_size_mismatch")
                errors.extend(raw_projection_errors(row, record, unit, joined, citation_parts))
                try:
                    bundle["validate_row"](row)
                    token_status = "PASS_STRUCTURE_ONLY"
                except (ValueError, KeyError, TypeError) as error:
                    token_status = "FAIL"
                    errors.append("token_structure:" + str(error))
                split_errors = []
                if row["record_id"] in by_held_id or row["work_id"] in held_works:
                    split_errors.append("heldout_record_or_work_overlap")
                reason = guard["blocked_reason"](record, rules)
                if reason:
                    split_errors.append(reason)
                flags = list(duplicate_flags.get(row["id"], [])) + near_by_train.get(row["id"], [])
                for label, matches in (("heldout_exact_source", held_sources.get(source_tokens(row["text"]), [])),
                                        ("heldout_exact_target", held_targets.get(target_tokens(row["target"]), []))):
                    if matches:
                        flags.append({"kind": label, "heldout_ids": matches})
                adjacent = neighbors[row["record_id"]]
                prev, nxt = excerpt(adjacent["previous"]), excerpt(adjacent["next"])
                flags.extend(boundary_flags(row["text"], row["target"], prev["target_text"] if prev else None,
                                            nxt["target_text"] if nxt else None))
                if adjacent["sequence_ambiguous"]:
                    flags.append({"kind": "ambiguous_raw_sequence_order"})
                markers = {key: marker_inventory(row[key]) for key in ("text", "target")}
                for field, value in markers.items():
                    for name, count in value["editorial_or_damage_markers"].items():
                        if count:
                            flags.append({"kind": "marker:" + name, "field": field, "count": count})
                            inventory_count[field + ":" + name] += 1
                    if value["ordinary_question_punctuation_count"]:
                        inventory_count[field + ":question_punctuation"] += 1
                flags_count.update(flag["kind"] for flag in flags)
                errors_count.update(errors + split_errors)
                mechanical_failed += bool(errors or split_errors)
                flagged_rows += bool(flags)
                if row["record_id"] == "parsig:134004028":
                    known_spill = int(any(flag["kind"] == "adjacent_target_overlap" and flag["direction"] == "current_to_next" for flag in flags))
                item = {
                    "row_number": index, **{key: row[key] for key in ("id", "record_id", "work_id", "revision", "credit")},
                    "source_text": row["text"], "target_text": row["target"], "edition": record["edition"],
                    "row_sha256": digest(canonical(row)), "source_sha256": digest(row["text"].encode()),
                    "target_sha256": digest(row["target"].encode()), "raw_unit_sha256": digest(canonical(raw_unit)),
                    "raw_pointer": unit["source"], "raw_export_sha256": EXPORT_SHA,
                    "curation_alignment_scope": record["provenance"]["research_review"]["alignment_scope"],
                    "mechanical_status": "FAIL" if errors or split_errors else "PASS",
                    "provenance_status": "FAIL" if errors else "PASS",
                    "token_structure_status": token_status,
                    "token_reconstruction_status": "PASS_HASH_BOUND_INDEPENDENT_PROOF",
                    "token_proof_row_sha256": digest(canonical(token_proof[row["id"]])),
                    "split_status": "FAIL" if split_errors else "PASS_IDENTITY_AND_PINNED_HOLDOUT",
                    "split_similarity_status": "REVIEW_REQUIRED" if any(flag["kind"].startswith("heldout_") for flag in flags) else "NO_MATCH_AT_DECLARED_NORMALIZATIONS_AND_THRESHOLD",
                    "mechanical_errors": errors, "split_errors": split_errors,
                    "alignment_status": "UNREVIEWED", "semantic_status": "UNREVIEWED", "expert_status": "UNREVIEWED",
                    "disposition": "UNREVIEWED", "flags_are_not_exclusions": True,
                    "neighbors": {"chapter": adjacent["chapter"], "sequence": adjacent["sequence"],
                                  "previous_id": prev["record_id"] if prev else None, "next_id": nxt["record_id"] if nxt else None},
                    "marker_inventory": markers, "flags": flags,
                }
                write_line(ledger, item)
                if flags or errors or split_errors:
                    write_line(candidates, {"row_number": index, "id": row["id"], "disposition": "UNREVIEWED",
                                            "flags": flags, "mechanical_errors": errors, "split_errors": split_errors,
                                            "previous": prev, "current": excerpt(unit), "next": nxt})
        inputs[str(Path(__file__).resolve())] = {"sha256": digest(Path(__file__).read_bytes()), "bytes": Path(__file__).stat().st_size}
        write_json(output / "inputs.json", {
            "files": inputs, "python": sys.version, "unicode_version": unicodedata.unidata_version,
            "train_sha256": TRAIN_SHA, "source_normalization": "NFC then casefold; split whitespace; strip boundary Unicode P*; preserve internal characters",
            "target_overlap_normalization": "NFC then casefold; Arabic yeh/kaf mapped to Persian; Unicode alphanumeric tokens excluding underscore",
            "near_source": {"threshold": NEAR_THRESHOLD, "orientation": "TRAIN as a, heldout as b", "autojunk": False,
                            "safe_rejects": ["token_length_upper_bound", "token_multiset_upper_bound"], "sampling_or_caps": False},
            "boundary_overlap_minimum_tokens": 3,
            "no_semantic_or_expert_certification": True,
        })
        output_hashes = {p.name: digest(p.read_bytes()) for p in sorted(output.iterdir()) if p.is_file()}
        result = {
            "status": "AUDIT_COMPLETE_NOT_SEMANTICALLY_CLEARED", "rows": len(train),
            "ledger_rows": len(train), "raw_responses_verified": len(response_units),
            "mechanical_failed_rows": mechanical_failed, "mechanical_error_counts": dict(errors_count),
            "selection_reconstruction": {"forward_rows": len(forward), "unique_pairs": len(seen), "exact_duplicates_removed": duplicate_count,
                                         "final_rows": len(retained), "errors": selection_errors},
            "near_source_scan": scan, "flagged_rows": flagged_rows, "flag_counts": dict(flags_count),
            "marker_row_counts_overlapping": dict(inventory_count), "known_134004028_spill_flagged": bool(known_spill),
            "semantic_unreviewed_rows": len(train), "expert_unreviewed_rows": len(train),
            "dispositions": {"UNREVIEWED": len(train)}, "training_or_assisted_inference_admitted": False,
            "token_reconstruction_status": "PASS_HASH_BOUND_INDEPENDENT_PROOF",
            "output_sha256": output_hashes, "elapsed_seconds": round(time.monotonic() - started, 3),
            "limits": ["Archive identity does not establish faithful meaning or paragraph boundaries.",
                       "Defined-threshold source comparisons are exhaustive; semantic paraphrases and unknown witnesses remain unverified.",
                       "Marker/boundary flags require review and never cause automatic text repair or exclusion.",
                       "No automatic semantic disposition or expert approval is inferred from absence of flags."],
        }
        write_json(output / "summary.json", result)
        print(json.dumps({"phase": "audit_complete", "status": result["status"], "rows": len(train),
                          "mechanical_failed_rows": mechanical_failed, "flagged_rows": flagged_rows,
                          "output": str(output)}, ensure_ascii=False), flush=True)
        return result
    except Exception as error:
        if not (output / "summary.json").exists():
            write_json(output / "summary.json", {"status": "FAILED_INCOMPLETE_AUDIT", "error": str(error),
                                                 "training_or_assisted_inference_admitted": False})
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study-root", type=Path, default=STUDY_ROOT)
    parser.add_argument("--translator", type=Path, default=TRANSLATOR)
    parser.add_argument("--output", type=Path, required=True, help="New report directory; must not already exist")
    args = parser.parse_args()
    result = audit(args.study_root, args.translator, args.output)
    return int(bool(result["mechanical_failed_rows"] or result["selection_reconstruction"]["errors"]))


if __name__ == "__main__":
    raise SystemExit(main())
