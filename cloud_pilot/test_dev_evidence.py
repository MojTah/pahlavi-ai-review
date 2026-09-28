"""Offline evidence-selection tests; no references, weights, network, or artifacts."""
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

try:
    from . import dev_evidence as evidence
except ImportError:
    import dev_evidence as evidence


def row(number, text, target="meaning", work=None, length=10):
    record = f"parsig:{number:09d}"
    return {"id": record + ":pal>fa", "record_id": record, "work_id": work or record[:10],
        "text": text, "target": target, "credit": "original credit", "revision": "a" * 64,
        "input_ids": [1] * length, "source_language": "pal", "target_language": "fa"}


def fillers(count=60):
    return [row(900000000 + index, f"f{index} g{index} h{index}") for index in range(count)]


class DevEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parent.parent
        cls.train = cls.root / "resources/local/cloud-pilot-20260926-hf-v5/train.jsonl"
        cls.inputs = cls.root / "experiments/dev-diagnostic-20260927/inputs.jsonl"

    def test_normalization_conflicts_deduplication_and_bounds(self):
        self.assertEqual(evidence.tokens("‘A\u0304Z!’   foo-bar (šāh) ... +x+"), ("āz", "foo-bar", "šāh", "+x+"))
        rows = [row(200000001, "word one two!", " DIFFERENT "),
                row(100000001, "word one two", "meaning"),
                row(200000002, "same three words!", "  SAME\n meaning "),
                row(100000002, "same three words", "same meaning"),
                row(100000003, "too short"), row(100000004, "long token sequence", length=321),
                row(100000005, "allowed token sequence", length=320)]
        pool, df, excluded = evidence.prepare_pool(rows)
        self.assertEqual([item[0]["id"] for item in pool], [rows[3]["id"], rows[6]["id"]])
        self.assertEqual(excluded["ambiguous"], [[rows[1]["id"], rows[0]["id"]]])
        self.assertEqual(excluded["duplicate"], [rows[2]["id"]])
        self.assertCountEqual(excluded["length"], [rows[4]["id"], rows[5]["id"]])
        self.assertEqual(df["same"], 1)
        repeated_pool, repeated_df, _ = evidence.prepare_pool([row(100000006, "word word word")])
        self.assertEqual(repeated_df["word"], 1)
        self.assertEqual(len(repeated_pool), 1)

    def test_zero_support_and_deterministic_full_id_tie(self):
        rows = [row(200000001, "a red blue"), row(100000001, "a green black")] + fillers()
        pool, df, _ = evidence.prepare_pool(rows)
        selected, support = evidence.retrieve("a unknown extra query", pool, df)
        self.assertEqual([item["id"] for item in selected], [rows[1]["id"]])
        self.assertEqual(selected[0]["selection"]["new_rare_terms"], ["a"])
        self.assertEqual(support["unattested_terms"], ["extra", "query", "unknown"])
        reversed_pool, reversed_df, _ = evidence.prepare_pool(list(reversed(rows)))
        self.assertEqual(evidence.retrieve("a unknown extra query", pool, df),
                         evidence.retrieve("a unknown extra query", reversed_pool, reversed_df))
        for query in ("unseen terms only", "... !!!", ""):
            selected, support = evidence.retrieve(query, pool, df)
            self.assertEqual(selected, [])
            self.assertFalse(support["supported"])

    def test_greedy_new_terms_and_maximum_one_per_work(self):
        rows = [row(100000001, "a b p q r"), row(200000001, "a b u v w"),
                row(300000001, "c s t u v"), row(400000001, "d j k l m"),
                row(100000002, "d n o p q")] + fillers(100)
        pool, df, _ = evidence.prepare_pool(rows)
        selected, support = evidence.retrieve("a b c d unknown", pool, df)
        self.assertEqual(selected[0]["id"], rows[0]["id"])
        self.assertEqual({item["id"] for item in selected}, {rows[index]["id"] for index in (0, 2, 3)})
        self.assertEqual(len({item["work_id"] for item in selected}), 3)
        covered = set()
        for item in selected:
            new = set(item["selection"]["new_rare_terms"])
            self.assertTrue(new)
            self.assertFalse(new & covered)
            covered |= new
        self.assertEqual(support["covered_rare_terms"], ["a", "b", "c", "d"])

    def test_all_three_near_copy_rules(self):
        rows = [row(100000001, "a b c d e extra more tail"),
                row(200000001, "e d c b a"), row(300000001, "a b c d z")] + fillers(100)
        pool, df, _ = evidence.prepare_pool(rows)
        selected, support = evidence.retrieve("a b c d e", pool, df)
        reasons = {item["id"]: item["reasons"] for item in support["near_copy_exclusions"]}
        self.assertIn("query_contained", reasons[rows[0]["id"]])
        self.assertIn("set_jaccard", reasons[rows[1]["id"]])
        self.assertEqual(reasons[rows[2]["id"]], ["sequence_similarity"])
        self.assertEqual(selected, [])

    def test_actual_frozen_build_complete_provenance_and_expected_coverage(self):
        records, audit = evidence.build(self.train, self.inputs)
        source = {item["id"]: item for item in map(json.loads, self.train.read_text(encoding="utf-8").splitlines())}
        queries = evidence.dev_diagnostic.read_inputs(self.inputs)
        self.assertEqual(audit["coverage"], {"cases": 24, "supported_cases": 24, "attachments": 69,
            "attachment_histogram": {"1": 1, "2": 1, "3": 22}, "attested_rare_terms": 291,
            "covered_rare_terms": 165, "uncovered_rare_terms": 126, "unattested_terms": 145, "common_terms": 141})
        self.assertEqual((audit["eligible_rows"], audit["eligible_works"]), (2251, 74))
        self.assertEqual((len(audit["excluded"]["ambiguous"]), sum(map(len, audit["excluded"]["ambiguous"]))), (6, 13))
        self.assertEqual(audit["train_sha256"], hashlib.sha256(self.train.read_bytes()).hexdigest())
        self.assertEqual(audit["inputs_sha256"], hashlib.sha256(self.inputs.read_bytes()).hexdigest())
        for actual, query in zip(records, queries):
            self.assertEqual({key: actual[key] for key in query}, query)
            self.assertEqual(actual["source_sha256"], evidence.sha(query["source_text"].encode()))
            self.assertEqual(len({item["work_id"] for item in actual["examples"]}), len(actual["examples"]))
            for rank, example in enumerate(actual["examples"], 1):
                original = source[example["id"]]
                self.assertEqual(example["selection"]["rank"], rank)
                self.assertNotIn(example["work_id"], evidence.dev_diagnostic.WORKS)
                for key in ("record_id", "work_id", "credit", "revision"):
                    self.assertEqual(example[key], original[key])
                for key, original_key in (("source", "text"), ("target", "target")):
                    self.assertEqual(example[key + "_text"], original[original_key])
                    self.assertEqual(example[key + "_sha256"], evidence.sha(original[original_key].encode()))

    def test_hash_tampering_rejected_before_selection(self):
        read = Path.read_bytes
        for target in (self.train, self.inputs, self.root / "cloud_pilot/dev_diagnostic.py"):
            def tamper(path):
                data = read(path)
                return data + b"\n" if path.resolve() == target.resolve() else data
            with self.subTest(path=target.name), patch.object(Path, "read_bytes", tamper), patch.object(evidence, "prepare_pool") as selection:
                with self.assertRaises(ValueError):
                    evidence.build(self.train, self.inputs)
                selection.assert_not_called()

    def test_exclusive_output_and_exact_serialized_checksum(self):
        with patch.object(Path, "exists", return_value=True), patch.object(evidence, "build") as build:
            with self.assertRaisesRegex(ValueError, "fresh directory"):
                evidence.prepare(self.train, self.inputs, "existing")
            build.assert_not_called()
        class Bytes(io.BytesIO):
            def __exit__(self, *args): pass
        class Text(io.StringIO):
            def __exit__(self, *args): pass
        payload, report = Bytes(), Text()
        records, audit = [{"id": "test", "source_text": "šāh", "examples": []}], {"coverage": {"attachments": 0}}
        with patch.object(Path, "exists", return_value=False), patch.object(evidence, "build", return_value=(records, audit)), \
                patch.object(Path, "mkdir") as mkdir, patch.object(Path, "open", side_effect=[payload, report]) as opened:
            evidence.prepare(self.train, self.inputs, "fresh")
        mkdir.assert_called_once_with(parents=True, exist_ok=False)
        self.assertEqual([call.args[0] for call in opened.call_args_list], ["xb", "x"])
        self.assertEqual(json.loads(payload.getvalue()), records[0])
        self.assertEqual(json.loads(report.getvalue())["evidence_sha256"], evidence.sha(payload.getvalue()))


if __name__ == "__main__":
    unittest.main()
