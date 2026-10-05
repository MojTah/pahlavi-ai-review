"""Frozen, source-only DEV15 dictionary lookup; no lemma or sense selection.

Classic Codex: one isolated standard-library selector, verified with synthetic
boundary checks and the frozen exposed DEV sources. Offsets are half-open Python
Unicode code-point offsets in the original source. Multiword forms require the
literal intervening text after NFC, including whitespace. Comma bundles are
reported separately and never promoted to aliases or selected inventories.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import tempfile
import unicodedata


ROOT = Path(__file__).resolve().parents[2]
DICTIONARY_PATH = ROOT / "resources/local/usable-resource-v3-20261001/dictionary.jsonl"
MANIFEST_PATH = DICTIONARY_PATH.with_name("manifest.json")
INPUT_PATH = ROOT / "experiments/dev-diagnostic-20260927/inputs.jsonl"
DICTIONARY_SHA256 = "bcf789f6658e93e8d8bf3f7ab8a9d6bf7f2f7e918833d0344604fac1b24bea2f"
INPUT_SHA256 = "06ac58310bf67767fae4124d8e935c808d15debcd8daebce07b583937cd97182"
DEV15_IDS = tuple(f"QUALITYDEV1-{i:03d}" for i in
                  (2, 3, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 17, 20, 21))
EDGE_PUNCTUATION = ".,:;!?،؛«»()[]{}"
POLICY = {
    "version": "NFC_LITERAL_PUBLISHED_FORMS_V1",
    "normalization": "NFC only; case, diacritics and hyphens preserved",
    "token_boundaries": "whitespace; trim only the listed edge punctuation",
    "edge_punctuation": EDGE_PUNCTUATION,
    "multiword": "literal contiguous source text after NFC; no whitespace collapse",
    "alternatives": "all matching groups, all inventory senses and scope labels",
    "bundles": "comma bundles unresolved; component mentions are not aliases",
    "abstentions": "unmatched surface tokens; not a claim of lexical OOV",
    "offset_unit": "original-source Unicode code points; half-open [start,end)",
    "no_inference": ["lemma", "clitic", "spelling alias", "preferred contextual sense"],
}


def nfc(text):
    return unicodedata.normalize("NFC", text)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def source_tokens(source):
    tokens = []
    for match in re.finditer(r"\S+", source):
        raw = match.group()
        left = len(raw) - len(raw.lstrip(EDGE_PUNCTUATION))
        end = match.end() - (len(raw) - len(raw.rstrip(EDGE_PUNCTUATION)))
        start = match.start() + left
        if start < end:
            text = source[start:end]
            tokens.append({"start": start, "end": end, "text": text,
                           "normalized_form": nfc(text)})
    return tokens


def select(source, dictionary):
    """Return deterministic exact-match receipts without mutating either input.

    ``dictionary`` is an iterable of qualified rows with id/forms and complete
    inventory fields. Returned inventories are whole matching rows, not chosen
    definitions. Unresolved bundle diagnostics do not supply their meanings.
    """
    if not isinstance(source, str):
        raise TypeError("source must be a string")
    tokens = source_tokens(source)
    positions = defaultdict(list)
    for index, token in enumerate(tokens):
        positions[token["normalized_form"]].append(index)

    def spans(form):
        parts = nfc(form).split()
        if not parts:
            return []
        result = []
        for first in positions.get(parts[0], ()):
            last = first + len(parts) - 1
            if last >= len(tokens):
                continue
            if [t["normalized_form"] for t in tokens[first:last + 1]] != parts:
                continue
            start, end = tokens[first]["start"], tokens[last]["end"]
            if nfc(source[start:end]) == nfc(form):
                result.append((start, end, first, last))
        return result

    matches = {}
    inventories = {}
    unresolved = []
    covered = set()
    seen_ids = set()
    for row in dictionary:
        entry_id, forms = row["id"], row["forms"]
        if entry_id in seen_ids:
            raise ValueError(f"Duplicate dictionary group: {entry_id}")
        seen_ids.add(entry_id)
        if not isinstance(forms, list) or any(not isinstance(f, str) for f in forms):
            raise ValueError(f"Invalid published forms: {entry_id}")
        for form_index, form in enumerate(forms):
            if "," in form or "،" in form:
                for fragment in dict.fromkeys(p.strip() for p in re.split("[,،]", form)):
                    for start, end, _, _ in spans(fragment):
                        unresolved.append({"entry_id": entry_id,
                            "published_form_index": form_index, "published_form": form,
                            "mentioned_fragment": fragment, "start": start, "end": end,
                            "source_text": source[start:end],
                            "binding": "UNRESOLVED_PUBLISHED_COMMA_BUNDLE_NOT_AN_ALIAS",
                            "scope": row.get("context", {}),
                            "parent_ids": row.get("parent_ids", [])})
                continue
            for start, end, first, last in spans(form):
                key = (start, end, nfc(form))
                if key not in matches:
                    matches[key] = {"start": start, "end": end,
                        "source_text": source[start:end], "normalized_form": nfc(form),
                        "binding": "EXACT_NFC_PUBLISHED_FORM_ALL_INVENTORY_ALTERNATIVES",
                        "candidates": []}
                matches[key]["candidates"].append({"entry_id": entry_id,
                    "published_form_index": form_index, "published_form": form})
                inventories[entry_id] = dict(row)
                covered.update(range(first, last + 1))
    ordered_matches = [matches[key] for key in sorted(matches)]
    for match in ordered_matches:
        match["candidates"].sort(key=lambda c: (c["entry_id"], c["published_form_index"]))
    unresolved.sort(key=lambda r: (r["start"], r["end"], r["entry_id"],
                                    r["published_form_index"], r["mentioned_fragment"]))
    return {"source_text": source, "source_sha256": sha256(source.encode("utf-8")),
            "policy": dict(POLICY), "matches": ordered_matches,
            "inventories": [inventories[key] for key in sorted(inventories)],
            "misses": [dict(token, binding="ABSTAIN_NO_EXACT_PUBLISHED_FORM")
                       for i, token in enumerate(tokens) if i not in covered],
            "bundles_left_unresolved": unresolved}


def synthetic_checks():
    def row(entry_id, forms, meaning, scope):
        return {"id": entry_id, "forms": forms, "meaning_text": meaning,
                "archival_target": {"entries": [{"senses": meaning}]},
                "context": scope, "parent_ids": [entry_id],
                "provenance": {"synthetic": True}, "expert_certified": False}

    dictionary = [row("snake", ["mār"], "snake", {"usage": "synthetic A"}),
                  row("homograph", ["mār"], "alternative", {"usage": "synthetic B"}),
                  row("account", ["mar"], "reckoning", {"grammar": "synthetic noun"}),
                  row("phrase", ["mār ī mar"], "unselected phrase inventory", {}),
                  row("lower", ["kār"], "lower-case only", {}),
                  row("bundle", ["x, y"], "must not be supplied for x alone", {})]

    def require(condition, message):
        if not condition:
            raise AssertionError(message)

    receipt = select("mār mar ma\u0304r mār-iz KĀR kār", dictionary)
    by_form = {m["normalized_form"]: m for m in receipt["matches"]}
    require({c["entry_id"] for c in by_form["mār"]["candidates"]} ==
            {"snake", "homograph"}, "mār homographs lost or confused with mar")
    require([c["entry_id"] for c in by_form["mar"]["candidates"]] == ["account"],
            "mar was conflated with mār")
    require({r["context"]["usage"] for r in receipt["inventories"] if r["id"] in
             {"snake", "homograph"}} == {"synthetic A", "synthetic B"},
            "qualifiers were discarded")
    require([t["text"] for t in receipt["misses"]] == ["mār-iz", "KĀR"],
            "hyphen/case abstention failed")
    require(any(m["source_text"] == "ma\u0304r" and m["normalized_form"] == "mār"
                for m in receipt["matches"]), "NFC match lost original offsets")
    for match in receipt["matches"]:
        require(receipt["source_text"][match["start"]:match["end"]] ==
                match["source_text"], "source offset is not original-source based")
    require(receipt == select(receipt["source_text"], reversed(dictionary)),
            "dictionary order changes the receipt")

    phrase = select("mār ī mar.", dictionary)
    require(any(m["source_text"] == "mār ī mar" and m["start"] == 0 and m["end"] == 9
                and any(c["entry_id"] == "phrase" for c in m["candidates"])
                for m in phrase["matches"]), "literal multiword span missing")
    for source in ("mār, ī mar", "mār  ī mar"):
        require("phrase" not in {r["id"] for r in select(source, dictionary)["inventories"]},
                "punctuation or whitespace silently created a phrase")
    bundle = select("x", dictionary)
    require(not bundle["inventories"] and bundle["misses"][0]["text"] == "x" and
            bundle["bundles_left_unresolved"][0]["entry_id"] == "bundle",
            "comma bundle was promoted to an alias")
    return ["mār_vs_mar", "all_homographs_and_qualifiers", "NFC_original_offsets",
            "case_and_hyphen_abstention", "literal_multiword_boundaries",
            "unresolved_bundle_not_alias", "dictionary_order_determinism"]


def frozen_receipts():
    dictionary_raw = DICTIONARY_PATH.read_bytes()
    input_raw = INPUT_PATH.read_bytes()
    manifest_raw = MANIFEST_PATH.read_bytes()
    if sha256(dictionary_raw) != DICTIONARY_SHA256 or sha256(input_raw) != INPUT_SHA256:
        raise ValueError("Frozen source or dictionary hash changed")
    manifest = json.loads(manifest_raw)
    declaration = manifest["output_files"]["dictionary.jsonl"]
    if declaration["sha256"] != DICTIONARY_SHA256 or declaration["rows"] != 7438:
        raise ValueError("Dictionary manifest does not match the frozen resource")
    dictionary = [json.loads(line) for line in dictionary_raw.decode("utf-8").splitlines()]
    if len(dictionary) != 7438:
        raise ValueError("Frozen dictionary row count changed")
    inputs = [json.loads(line) for line in input_raw.decode("utf-8").splitlines()]
    allowed = {"id", "record_id", "work_id", "source_language", "target_language", "source_text"}
    if any(set(row) != allowed for row in inputs):
        raise ValueError("DEV inputs are not the frozen source-only schema")
    indexed = {row["id"]: row for row in inputs}
    if len(indexed) != len(inputs) or any(case_id not in indexed for case_id in DEV15_IDS):
        raise ValueError("Missing or duplicated frozen DEV case")
    receipts = []
    for case_id in DEV15_IDS:
        row = indexed[case_id]
        receipt = select(row["source_text"], dictionary)
        receipt.update({key: row[key] for key in allowed - {"source_text"}})
        receipts.append(receipt)
    return {"schema": "DEV15_AUTOMATIC_DICTIONARY_LOOKUP_V1", "policy": POLICY,
        "frozen_dev15_ids": list(DEV15_IDS), "inputs_sha256": INPUT_SHA256,
        "dictionary_sha256": DICTIONARY_SHA256, "dictionary_rows": len(dictionary),
        "inputs_path": INPUT_PATH.relative_to(ROOT).as_posix(),
        "dictionary_path": DICTIONARY_PATH.relative_to(ROOT).as_posix(),
        "manifest_sha256": sha256(manifest_raw),
        "selector_sha256": sha256(Path(__file__).read_bytes()),
        "capacity_status": "NOT_MEASURED_WITH_RENDERED_GEMMA_PROMPT_OR_TOKENIZER",
        "receipts": receipts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="Check synthetic boundaries and frozen DEV15")
    mode.add_argument("--out", type=Path, help="Write source-only receipts to a new file beneath system TEMP")
    args = parser.parse_args()
    checks = synthetic_checks()
    payload = frozen_receipts()
    raw = (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    summary = {"result": "PASS", "synthetic_checks": checks,
        "case_count": len(payload["receipts"]), "receipt_sha256": sha256(raw),
        "dictionary_sha256": DICTIONARY_SHA256, "inputs_sha256": INPUT_SHA256,
        "capacity_status": payload["capacity_status"],
        "cases": [{"id": r["id"], "matched_groups": len(r["inventories"]),
                   "matched_spans": len(r["matches"]), "misses": len(r["misses"]),
                   "unresolved_bundle_mentions": len(r["bundles_left_unresolved"])}
                  for r in payload["receipts"]]}
    if args.out is not None:
        output = args.out.resolve()
        temp_root = Path(tempfile.gettempdir()).resolve()
        if not output.is_relative_to(temp_root) or output.is_relative_to(ROOT):
            raise ValueError("Receipt output must be beneath system TEMP and outside the project")
        with output.open("xb") as handle:
            handle.write(raw)
        summary["output_path"] = str(output)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
