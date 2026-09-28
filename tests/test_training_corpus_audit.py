"""Focused audit contracts; never create or approve replacement training data."""
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("training_audit", ROOT / "scripts/audit_training_corpus.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def raw(id, chapter, sequence):
    return {"id": id, "raw_source_unit": {"ChapterCode": chapter, "Sequence": sequence}}


def train(id, source, target="الف"):
    return {"id": id + ":pal>fa", "record_id": id, "work_id": "train-work", "text": source, "target": target}


class AuditTests(unittest.TestCase):
    def historical_helpers(self):
        if not (audit.TRANSLATOR / "pahlavi/curation.py").exists():
            self.skipTest("Pinned historical source helpers not present")
        data = {name: audit.checked(audit.TRANSLATOR / name, value, {}) for name, value in audit.HELPER_PINS.items()}
        return audit.source_helpers(data["pahlavi/importers.py"], data["pahlavi/curation.py"])

    def test_hash_mismatch_refuses(self):
        with patch.object(Path, "read_bytes", return_value=b"tampered"):
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                audit.checked(ROOT / "dummy-input", audit.digest(b"expected"), {})

    def test_duplicate_identifiers_refused(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            audit.unique([{"id": "same"}, {"id": "same"}])

    def test_true_adjacency_uses_chapter_sequence_not_numeric_id(self):
        rows = [raw("009", "a", 8), raw("999", "a", 3), raw("010", "b", 4)]
        result = audit.adjacency(rows)
        self.assertEqual(result["999"]["next"]["id"], "009")
        self.assertIsNone(result["009"]["next"])
        self.assertIsNone(result["010"]["previous"])

    def test_ambiguous_sequence_flagged(self):
        result = audit.adjacency([raw("one", "a", 1), raw("two", "a", 1)])
        self.assertTrue(result["one"]["sequence_ambiguous"])

    def test_known_spillover_is_a_flag_not_a_repair(self):
        text = "بر مردار رود؛ یا اگر [خود را]"
        flags = audit.boundary_flags("nasā rawēd.", text, next_target="یا اگر [خود را] به برشنوم شوید")
        overlap = next(x for x in flags if x["kind"] == "adjacent_target_overlap")
        self.assertEqual(overlap["tokens"], 4)
        self.assertEqual(text, "بر مردار رود؛ یا اگر [خود را]")
        self.assertNotIn("disposition", overlap)

    def test_ordinary_question_is_not_uncertainty(self):
        m = audit.marker_inventory("کدام مرد؟")
        self.assertEqual(m["ordinary_question_punctuation_count"], 1)
        self.assertFalse(any(m["editorial_or_damage_markers"].values()))
        self.assertEqual(audit.marker_inventory("[?]")["editorial_or_damage_markers"]["explicit_question_annotation"], 1)

    def test_target_variants_flag_whole_source_group(self):
        rows = [train("one", "pursīd dānāg.", "پرسید دانا"), train("two", "pursīd dānāg", "پرسید")]
        result = audit.duplicate_groups(rows)
        self.assertEqual(set(result), {r["id"] for r in rows})
        self.assertTrue(all(result[r["id"]][0]["kind"] == "normalized_source_target_variants" for r in rows))

    def test_all_near_pairs_enumerated_including_exact_threshold(self):
        training = [train("one", "a b c d e"), train("two", "z")]
        held = [dict(id="dev-one", work_id="dev", transcription="a b c d x", split="dev"),
                dict(id="test-two", work_id="test", transcription="q r s", split="test")]
        matches = []
        counts = audit.near_sources(training, held, matches.append)
        self.assertEqual(counts["total_pairs"], 4)
        self.assertEqual(counts["pairs_enumerated"], 4)
        self.assertTrue(counts["completed"])
        self.assertEqual([(x["heldout_id"], x["ratio"]) for x in matches], [("dev-one", .8)])
        self.assertEqual(sum(counts[k] for k in ("empty_rejected", "length_bound_rejected", "multiset_bound_rejected", "sequence_comparisons")), 4)

    def test_multiset_filter_preserves_repeated_token_matches(self):
        rows = [train("one", "a a a b b")]
        held = [dict(id="dev", work_id="dev", transcription="a a a b x", split="dev")]
        matches = []; counts = audit.near_sources(rows, held, matches.append)
        self.assertEqual(counts["matches"], 1)
        self.assertEqual(matches[0]["ratio"], .8)

    def test_record_projection_detects_target_and_credit_changes(self):
        record = {"id": "r", "work_id": "w", "transcription": "a b", "translations": {"fa": {"text": "الف", "credit": "edition"}}}
        row = dict(id="r:pal>fa", record_id="r", work_id="w", revision=audit.digest(audit.canonical(record)),
                   source_language="pal", target_language="fa", text="a b", target="wrong", credit="wrong")
        self.assertEqual(audit.projection_errors(row, record), ["record_projection_mismatch:target", "record_projection_mismatch:credit"])

    def test_raw_projection_applies_only_historical_outer_strip(self):
        joined, citation_parts = self.historical_helpers()
        unit = {"transcription": ["  a b (Author, 2000)"], "farsi_translation": ["  الف (Author, 1398)"],
                "raw_source_unit": {"Transcription": [{"Section": "  a b (Author, 2000)"}],
                                    "Translation": [{"Section": "  الف (Author, 1398)"}]}}
        before = audit.canonical(unit)
        row = {"text": "a b", "target": "الف", "credit": "(Author, 1398)"}
        self.assertEqual(audit.raw_projection_errors(row, {"edition": "(Author, 2000)"}, unit, joined, citation_parts), [])
        self.assertEqual(audit.canonical(unit), before)

    def test_empty_raw_sections_follow_pinned_nonblank_line_comparison(self):
        joined, citation_parts = self.historical_helpers()
        unit = {"transcription": ["a b (Author, 2000)"], "farsi_translation": ["الف", "دوم (Author, 1398)"],
                "raw_source_unit": {"Transcription": [{"Section": "a b (Author, 2000)"}],
                                    "Translation": [{"Section": "الف"}, {"Section": ""}, {"Section": "  "}, {"Section": "دوم (Author, 1398)"}]}}
        row = {"text": "a b", "target": "الف\nدوم", "credit": "(Author, 1398)"}
        record = {"edition": "(Author, 2000)"}
        self.assertEqual(audit.raw_projection_errors(row, record, unit, joined, citation_parts), [])
        unit["raw_source_unit"]["Translation"][0]["Section"] = "changed nonblank text"
        self.assertEqual(audit.raw_projection_errors(row, record, unit, joined, citation_parts), ["export_raw_fields_mismatch"])

    def test_real_all2484_record_projections(self):
        tp = ROOT / "resources/local/cloud-pilot-20260926-hf-v5/train.jsonl"
        rp = audit.TRANSLATOR / "runs/datasets" / audit.DATASET_ID / "train-records.jsonl"
        if not tp.exists() or not rp.exists():
            self.skipTest("Frozen local corpus not present")
        records = audit.unique(audit.jsonl(audit.checked(rp, audit.DATASET_PINS["train-records.jsonl"], {})))
        rows = audit.jsonl(audit.checked(tp, audit.TRAIN_SHA, {}))
        self.assertEqual(len(rows), 2484)
        errors = [(r["id"], audit.projection_errors(r, records.get(r["record_id"]))) for r in rows]
        self.assertFalse([(id, e) for id, e in errors if e])
        raw_path = ROOT / "sources/local/parsig-2026-09-20/exports/text-units.jsonl"
        if raw_path.exists():
            raw_rows = audit.unique(audit.jsonl(audit.checked(raw_path, audit.EXPORT_SHA, {})))
            joined, citation_parts = self.historical_helpers()
            raw_errors = [(r["id"], audit.raw_projection_errors(r, records[r["record_id"]], raw_rows[r["record_id"]], joined, citation_parts)) for r in rows]
            self.assertFalse([(id, e) for id, e in raw_errors if e])
        spill = records["parsig:134004028"]
        next_target = records["parsig:134004029"]["translations"]["fa"]["text"]
        flags = audit.boundary_flags(spill["transcription"], spill["translations"]["fa"]["text"], next_target=next_target)
        self.assertTrue(any(f["kind"] == "adjacent_target_overlap" and f["tokens"] == 4 for f in flags))

    def test_real_token_proof_complete_and_missing_row_refused(self):
        tp = ROOT / "resources/local/cloud-pilot-20260926-hf-v5/train.jsonl"
        summary_path = ROOT / "experiments/train-audit-20260927/token-reconstruction/summary.json"
        if not tp.exists() or not summary_path.exists():
            self.skipTest("Frozen local token proof not present")
        files = {name: audit.checked(ROOT / name, value, {}) for name, value in audit.TOKEN_PROOF_PINS.items()}
        summary = json.loads(files["experiments/train-audit-20260927/token-reconstruction/summary.json"])
        proof = audit.jsonl(files["experiments/train-audit-20260927/token-reconstruction/rows.jsonl"])
        rows = audit.jsonl(audit.checked(tp, audit.TRAIN_SHA, {}))
        result = audit.validate_token_proof(summary, proof, rows, summary["tokenizer_files"])
        self.assertEqual(len(result), 2484)
        with self.assertRaisesRegex(ValueError, "cover every"):
            audit.validate_token_proof(summary, proof[:-1], rows, summary["tokenizer_files"])


if __name__ == "__main__":
    unittest.main()
