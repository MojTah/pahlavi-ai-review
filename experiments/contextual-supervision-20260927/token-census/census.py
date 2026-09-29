"""Offline tokenizer census of the proposed contextual pilot; never launch or train."""
import collections
import difflib
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import unicodedata

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BUNDLE = ROOT / "resources/local/cloud-pilot-qualified-20260927"
PROPOSALS = ROOT / "experiments/contextual-supervision-20260927"
AUX_PROMPT = ("Translate the selected expression from this Middle Persian passage into Farsi, "
              "using the passage as context. Return only its contextual meaning. Preserve negation "
              "and uncertainty. Do not invent missing context.\nSource:\n{source}\nSelected expression:\n{focus}")
PINS = {
    "proposals.jsonl": "f465bfac2d3f818c1960386dc0ef1edbc6b2a87561ede3b0e6c657ed2860923e",
    "extension-proposals.jsonl": "17cc66d7a880ef6ad64d79493ac447602465f2f62356d448800c523d87d0c5a4",
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def fingerprint(path):
    return {"path": str(path), "sha256": digest(path.read_bytes())}


def stats(rows):
    return {k: {"sum": sum(r[k] for r in rows), "min": min(r[k] for r in rows),
                "max": max(r[k] for r in rows), "mean": sum(r[k] for r in rows) / len(rows)}
            for k in ("prompt_tokens", "target_tokens", "supervised_tokens", "sequence_tokens")}


def main():
    # Existing installed packages only, with the science interpreter retaining priority.
    for key in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE", "HF_HUB_DISABLE_TELEMETRY"):
        os.environ[key] = "1"
    sys.path.append(str(ROOT / "resources/local/hf-client-venv/Lib/site-packages"))
    import transformers
    from transformers import AutoTokenizer
    environment = {}
    for name in ("transformers", "tokenizers", "huggingface_hub", "jinja2"):
        module = importlib.import_module(name)
        environment[name] = {"version": module.__version__, "path": module.__file__}
    assert transformers.__version__ == "5.13.1"
    manifest = json.loads((BUNDLE / "manifest.json").read_bytes())
    inputs = {}
    for name in ("bundle.py", "train.jsonl", "tokenizer/tokenizer.json",
                 "tokenizer/tokenizer_config.json", "tokenizer/chat_template.jinja"):
        path = BUNDLE / name
        assert digest(path.read_bytes()) == manifest["files"][name]["sha256"], name
        inputs[name] = fingerprint(path)
    spec = importlib.util.spec_from_file_location("pinned_census_bundle", BUNDLE / "bundle.py")
    bundle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bundle)
    tokenizer = AutoTokenizer.from_pretrained(str(BUNDLE / "tokenizer"), local_files_only=True,
                                             trust_remote_code=False)
    assert tokenizer.chat_template == (BUNDLE / "tokenizer/chat_template.jinja").read_text(encoding="utf-8")
    assert tokenizer.encode(bundle.TERMINATOR, add_special_tokens=False) == [106, 107]
    proposals = []
    for name, pin in PINS.items():
        path = PROPOSALS / name
        assert digest(path.read_bytes()) == pin, name
        inputs[name] = fingerprint(path)
        proposals.extend(bundle.jsonl(path.read_bytes()))
    assert len(proposals) == len({p["record_id"] for p in proposals}) == 12
    train = bundle.jsonl((BUNDLE / "train.jsonl").read_bytes())
    assert len(train) == 2237
    by_parent = {r["record_id"]: r for r in train}
    parents = {p["record_id"] for p in proposals}
    regular = sorted((r for r in train if r["record_id"] not in parents),
                     key=lambda r: digest(("contextual-pilot-v1|3407|" + r["id"]).encode("utf-8")))[:720]
    assert len(regular) == len({r["id"] for r in regular}) == 720

    def token_summary(row):
        bundle.validate_row(row)
        n = row["prompt_tokens"]
        answer = row["input_ids"][n:]
        assert answer[-2:] == [106, 107]
        assert tokenizer.decode(answer, skip_special_tokens=False, clean_up_tokenization_spaces=False) == row["target"] + bundle.TERMINATOR
        return {"prompt_tokens": n, "target_tokens": len(answer) - 2,
                "supervised_tokens": len(answer), "sequence_tokens": len(row["input_ids"]),
                "loss_first_label_index": n, "loss_last_label_index": len(row["labels"]) - 1,
                "causal_logit_first_index": n - 1,
                "input_ids_sha256": digest(canonical(row["input_ids"])),
                "labels_sha256": digest(canonical(row["labels"]))}

    def checked_ordinary(saved):
        actual = bundle.tokenize_row({k: saved[k] for k in bundle.SOURCE_KEYS}, tokenizer)
        assert actual == saved, saved["id"]
        return token_summary(actual)

    regular_data = [{"id": r["id"], "work_id": r["work_id"], **checked_ordinary(r)} for r in regular]
    anchors, auxiliary_rows = [], []
    for proposal in proposals:
        parent = by_parent[proposal["record_id"]]
        source, focus, target = proposal["source_text"], proposal["source_focus"], proposal["proposed_target"]
        assert source == parent["text"] and proposal["reference_fa"] == parent["target"]
        assert digest(source.encode("utf-8")) == proposal["source_sha256"]
        assert digest(target.encode("utf-8")) == proposal["target_sha256"]
        for value in (source, focus, target):
            bundle.reject_controls(value, tokenizer.all_special_tokens)
            assert value == value.strip(), "Do not silently change proposed strings"
        starts = [m.start() for m in re.finditer("(?=" + re.escape(focus) + ")", source)]
        spans = [[s, s + len(focus)] for s in starts]
        byte_spans = [[len(source[:s].encode("utf-8")), len(source[:e].encode("utf-8"))] for s, e in spans]
        assert proposal["source_span"] in spans and proposal["source_utf8_span"] in byte_spans
        content = AUX_PROMPT.format(source=source, focus=focus)
        prefix = tokenizer.apply_chat_template([{"role": "user", "content": content}], tokenize=False,
                                               add_generation_prompt=True, enable_thinking=False)
        prefix_ids = tokenizer(prefix, add_special_tokens=False)["input_ids"]
        ids = tokenizer(prefix + target + bundle.TERMINATOR, add_special_tokens=False)["input_ids"]
        assert ids[:len(prefix_ids)] == prefix_ids
        row = {k: parent[k] for k in bundle.SOURCE_KEYS}
        row.update(target=target, input_ids=ids, attention_mask=[1] * len(ids),
                   labels=[-100] * len(prefix_ids) + ids[len(prefix_ids):], prompt_tokens=len(prefix_ids))
        auxiliary_rows.append(dict(row, train_id=parent["id"], annotation_id=proposal["id"],
                                   task="contextual_expression"))
        rid = proposal["record_id"]
        family = ("affliction" if rid in {"parsig:107000001", "parsig:151026026", "parsig:518000014"}
                  else "equal_temporal_spatial_contrast" if rid in {"parsig:108000001", "parsig:151001162", "parsig:136005007", "parsig:137001027"}
                  else "theft")
        anchors.append({"proposal_id": proposal["id"], "record_id": rid, "train_id": parent["id"],
                        "work_id": parent["work_id"], "family": family, "source_focus": focus,
                        "proposed_target": target, "focus_unique": len(starts) == 1,
                        "source_codepoint_spans": spans, "source_utf8_spans": byte_spans,
                        "focus_utf8_hex": focus.encode("utf-8").hex(),
                        "reference_target_span": proposal.get("reference_target_span"),
                        "target_kind": proposal["target_kind"], "candidate": token_summary(row),
                        "control": checked_ordinary(parent), "exposures_per_arm": 4})

    base_order = list(range(12))
    rotated_order = base_order[6:] + base_order[:6]
    cycle_orders = [base_order, list(reversed(base_order)), rotated_order, list(reversed(rotated_order))]
    position_balance = {a["record_id"]: [order.index(index) for order in cycle_orders]
                        for index, a in enumerate(anchors)}
    assert all(sum(positions) == 22 for positions in position_balance.values())
    anchor_order = [index for cycle in cycle_orders for index in cycle]
    updates = []
    slots = []
    for i in range(48):
        group, anchor = regular_data[i * 15:(i + 1) * 15], anchors[anchor_order[i]]
        denominators = {arm: sum(r["supervised_tokens"] for r in group) + anchor[arm]["supervised_tokens"]
                        for arm in ("candidate", "control")}
        updates.append({"update": i + 1, "cycle_index": i // 12, "within_cycle_position": i % 12,
                        "packet_anchor_index": anchor_order[i], "regular_ids_in_order": [r["id"] for r in group],
                        "designated_slot": 16, "designated_parent": anchor["record_id"],
                        "equal_example_weight": 1 / 16,
                        "supervised_tokens": denominators,
                        "designated_per_token_weight_under_example_mean": {
                            arm: 1 / (16 * anchor[arm]["supervised_tokens"]) for arm in denominators},
                        "designated_weight_if_token_normalized_instead": {
                            arm: anchor[arm]["supervised_tokens"] / denominators[arm] for arm in denominators}})
        for slot, regular_row in enumerate(group, 1):
            slots.append({"update": i + 1, "microstep": slot, "record_id": regular_row["id"].split(":pal>")[0],
                          "control_id": regular_row["id"], "candidate_id": regular_row["id"],
                          "kind": "ordinary_translation"})
        slots.append({"update": i + 1, "microstep": 16, "record_id": anchor["record_id"],
                      "control_id": anchor["train_id"], "candidate_id": anchor["train_id"],
                      "candidate_annotation_id": anchor["proposal_id"],
                      "kind": "designated_parent"})
    assert len(slots) == 768
    for name, rows in (("auxiliary-tokenized.jsonl", auxiliary_rows),
                       ("regular-id-order.jsonl", [{"id": r["id"], "record_id": r["record_id"]} for r in regular]),
                       ("ordered-slots.jsonl", slots)):
        (OUT / name).write_bytes(b"".join(canonical(row) for row in rows))
    pairs = []
    for i, left in enumerate(proposals):
        for right in proposals[i + 1:]:
            pair = {"left": left["id"], "right": right["id"], "fields": {}}
            for field in ("source_text", "reference_fa", "proposed_target"):
                a, b = left[field], right[field]
                norm = lambda s: " ".join(unicodedata.normalize("NFC", s).casefold().split())
                ratio = difflib.SequenceMatcher(None, norm(a), norm(b), autojunk=False).ratio()
                pair["fields"][field] = {"exact": a == b, "normalized_exact": norm(a) == norm(b),
                                        "character_similarity": ratio, "near_flag": ratio >= 0.8}
            pairs.append(pair)
    trainer_file = Path(transformers.__file__).parent / "trainer.py"
    model_file = Path(transformers.__file__).parent / "models/gemma4/modeling_gemma4.py"
    model_source = model_file.read_text(encoding="utf-8")
    assert re.search(r"class Gemma4ForConditionalGeneration.*?accepts_loss_kwargs = False", model_source, re.S)
    result = {"status": "TOKENIZER_CENSUS_ONLY_PROVISIONAL_NOT_LAUNCH_ADMITTED", "training_admitted": False,
              "mode": "Classic Codex; one bounded offline script, no model execution",
              "script": fingerprint(Path(__file__)), "environment": environment, "inputs": inputs,
              "source_qualification_decision": fingerprint(PROPOSALS / "qualification-decision-v2.json"),
              "runner_inputs": {name: fingerprint(OUT / name) for name in
                                ("auxiliary-tokenized.jsonl", "regular-id-order.jsonl", "ordered-slots.jsonl")},
              "auxiliary_prompt_template": AUX_PROMPT, "enable_thinking": False,
              "terminator": bundle.TERMINATOR, "terminator_ids": [106, 107], "max_length": 2048,
              "checks": {"all_732_ordinary_rows_exact_token_label_parity": True,
                         "all_12_candidate_boundaries_and_exact_answer_decodes": True,
                         "all_focus_unique": all(a["focus_unique"] for a in anchors),
                         "all_sequences_le_2048": True, "tokenizer_manifest_and_template": True,
                         "source_target_control_tokens_rejected": True},
              "design": {"updates_per_arm": 48, "microbatch": 1, "accumulation": 16,
                         "examples_per_arm": 768, "regular_distinct_parents": 720,
                         "regular_selection": "sha256('contextual-pilot-v1|3407|' + train_row['id']) ascending; exclude 12 parent IDs; first 720",
                         "regular_work_counts": dict(collections.Counter(r["work_id"] for r in regular)),
                         "anchor_work_counts": dict(collections.Counter(a["work_id"] for a in anchors)),
                         "anchor_family_counts": dict(collections.Counter(a["family"] for a in anchors)),
                         "regular_exposures_per_parent": 1, "designated_exposures_per_parent": 4,
                         "cycle_orders_zero_based_packet_indices": cycle_orders,
                         "anchor_positions_zero_based_by_cycle": position_balance,
                         "mean_within_cycle_position_each_anchor": 5.5,
                         "balance_limit": "Position balance across four cycles, not perfect learning-rate-dose equality; warmup remains unchanged.",
                         "designated_slots_per_arm": 48, "designated_example_fraction": 1 / 16},
              "anchors_in_packet_order": anchors, "regular_rows_in_order": regular_data, "updates": updates,
              "token_statistics": {"regular_720": stats(regular_data),
                                   **{arm: stats(regular_data + [a[arm] for a in anchors] * 4)
                                      for arm in ("candidate", "control")}},
              "duplicate_screen": {"method": "Exact strings plus NFC/casefold/whitespace normalized character SequenceMatcher; near threshold 0.8; report only, no removals or semantic claim",
                                   "all_66_pairs": pairs},
              "loss_weighting": {"expected": "Gemma4ForConditionalGeneration accepts_loss_kwargs=False; native Trainer uses each microbatch's mean answer-token loss, divided by 16. Each example nominally weighs 1/16, including answer terminator. This is source inspection, not executed training or gradient evidence; verify the eventual PEFT wrapper retains the flag and no custom reduction overrides it.",
                                 "per_token_formula": "1 / (16 * supervised_tokens_in_this_example)",
                                 "regular_per_token_weight_min": min(1 / (16 * r["supervised_tokens"]) for r in regular_data),
                                 "regular_per_token_weight_max": max(1 / (16 * r["supervised_tokens"]) for r in regular_data),
                                 "sources": [fingerprint(trainer_file), fingerprint(model_file)]}}
    (OUT / "result.json").write_bytes(canonical(result))
    report = ["# Provisional contextual pilot tokenizer census", "", result["status"], "",
              "No model, network, cloud, package installation, held-out reference or model-output access. Source qualification is recorded separately in qualification-decision-v2.json (fingerprinted in result.json); this census remains not launch-admitted.", "",
              "48 updates per arm, microbatch 1, accumulation 16: 720 distinct ordinary TRAIN parents, then one designated parent in slot 16 of each update. Candidate and control share the same four fixed balanced cycle orders; designated candidate targets use the exact contextual proposals, controls use complete frozen translations.", "",
              "Cycle orders use zero-based original packet indices: " + json.dumps(cycle_orders) + ". Every anchor has mean within-cycle position 5.5 across the four cycles. This balances position; it does not establish perfect learning-rate-dose equality because warmup is unchanged. Regular IDs and their order are unchanged.", "",
              f"All 732 ordinary parent token/label reconstructions match saved TRAIN exactly. All 12 candidate answer boundaries, exact answer-plus-terminator decodes and <=2048 checks pass. Focus uniqueness: {result['checks']['all_focus_unique']}.", "",
              f"Regular works: {len(result['design']['regular_work_counts'])}; anchor works: {len(result['design']['anchor_work_counts'])}; family counts: {result['design']['anchor_family_counts']}.", "",
              "| Arm | Total prompt tokens | Total target tokens | Total supervised tokens | Total sequence tokens | Maximum sequence |",
              "|---|---:|---:|---:|---:|---:|"]
    for arm in ("candidate", "control"):
        s = result["token_statistics"][arm]
        report.append(f"| {arm} | {s['prompt_tokens']['sum']} | {s['target_tokens']['sum']} | {s['supervised_tokens']['sum']} | {s['sequence_tokens']['sum']} | {s['sequence_tokens']['max']} |")
    report += ["", "Target counts exclude the two terminator tokens; supervised counts include them. Prompt labels are -100; the first answer label is at prompt_tokens, predicted by the previous token's logit. No truncation or padding is introduced.", "",
               "| Parent | Family | Candidate prompt / target / supervised / total | Control prompt / target / supervised / total | Unique focus |",
               "|---|---|---|---|---|" ]
    for a in anchors:
        values = lambda arm: " / ".join(str(a[arm][k]) for k in ("prompt_tokens", "target_tokens", "supervised_tokens", "sequence_tokens"))
        report.append(f"| {a['record_id']} | {a['family']} | {values('candidate')} | {values('control')} | {a['focus_unique']} |")
    report += ["", "Expected weighting: " + result["loss_weighting"]["expected"], "",
               "Consequently short contextual answers receive the same example-level weight as long translations; each answer token has weight 1/(16*N). Equal token mass across arms is not implied. Result JSON records each update's token denominators and the different weights that a token-normalized implementation would produce.", "",
               "Duplicate screening (report-only; full 66-pair values are in result.json):"]
    flagged = [(p, k, v) for p in pairs for k, v in p["fields"].items() if v["exact"] or v["near_flag"]]
    if not flagged:
        report.append("- No exact or >=0.8 normalized character-similarity pair in full sources, full translations or proposed targets.")
    for p, k, v in flagged:
        report.append(f"- {p['left']} / {p['right']}, {k}: exact={v['exact']}, normalized similarity={v['character_similarity']:.6f}.")
    report += ["", "Reproduce from the project root:", "", "```powershell",
               "& '[USER_HOME]/.venvs/codex-science/Scripts/python.exe' -B resources/local/contextual-token-census/census.py", "```", "",
               f"Script SHA-256: `{digest(Path(__file__).read_bytes())}`", f"Result SHA-256: `{digest((OUT / 'result.json').read_bytes())}`", "",
               "Actual loaded package paths/versions, pinned input hashes, all 720 regular IDs, 48 update orders, exact source focus spans in code points and UTF-8 bytes, answer boundaries and token-array hashes are in result.json.", "",
               "Runner preparation files (still not launch admission): `auxiliary-tokenized.jsonl` has 12 masked tokenized auxiliary rows; `regular-id-order.jsonl` has 720 frozen ordinary IDs; `ordered-slots.jsonl` has 768 ordered parent slots with candidate/control row IDs. Ordinary and control tokens come unchanged from pinned TRAIN. Hashes are recorded in result.json."]
    (OUT / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps({"checks": result["checks"], "statistics": result["token_statistics"],
                      "files": [fingerprint(OUT / name) for name in ("census.py", "result.json", "REPORT.md",
                                "auxiliary-tokenized.jsonl", "regular-id-order.jsonl", "ordered-slots.jsonl")]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
