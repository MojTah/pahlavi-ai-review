"""Synthetic guard/arithmetic checks. No model execution or semantic validation."""
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import unittest
from uuid import uuid4

sys.dont_write_bytecode = True
BENCH = Path(__file__).resolve().parents[1] / "benchmarks" / "pal-reference-v1"
spec = importlib.util.spec_from_file_location("pal_benchmark", BENCH / "benchmark.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


class BenchmarkGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen, cls.cases = b.verify()
        cls.references = b.unique(b.read_lines(BENCH / "references.jsonl"), "references")

    def setUp(self):
        scratch = BENCH.parents[1] / "tmp" / "benchmark-tests"
        scratch.mkdir(parents=True, exist_ok=True)
        # tempfile's restrictive Windows ACL is incompatible with the local sandbox.
        self.scratch = scratch / uuid4().hex
        self.scratch.mkdir()
        self.addCleanup(self.clean_scratch)
        self.directory = self.scratch / "synthetic-only"
        b.templates(self.directory, self.frozen, self.cases)
        self.run = b.read_json(self.directory / "run.json")
        self.run.update(model_id="SYNTHETIC_NO_MODEL", model_revision="fixture", adapter_sha256_or_none="none", runtime="no inference", reviewer_id="synthetic test only", reviewer_type="ai")
        self.predictions = b.read_lines(self.directory / "predictions.jsonl")
        self.reviews = b.read_lines(self.directory / "reviews.jsonl")
        for pred, review in zip(self.predictions, self.reviews):
            case = self.cases[pred["id"]]
            text = self.references[case["passage_id"]]["texts"][case["target_language"]]
            pred.update(status="success", text=text, elapsed_seconds=1)
            review.update(output_sha256=b.digest(text.encode("utf-8")), judgment="accepted", meaning_checks=["pass", "pass"], categories={k: "pass" for k in b.CATEGORIES}, reason="Synthetic arithmetic fixture, not a real review.")

    def save(self):
        b.write_json(self.directory / "run.json", self.run)
        b.write_lines(self.directory / "predictions.jsonl", self.predictions)
        b.write_lines(self.directory / "reviews.jsonl", self.reviews)

    def clean_scratch(self):
        allowed = (BENCH.parents[1] / "tmp" / "benchmark-tests").resolve()
        assert self.scratch.resolve().parent == allowed
        shutil.rmtree(self.scratch)

    def score(self):
        self.save()
        return b.score(self.directory, self.frozen, self.cases)

    def test_blank_templates_cannot_score(self):
        with self.assertRaisesRegex(ValueError, "Missing model_id"):
            b.score(self.directory, self.frozen, self.cases)

    def test_aggregate_fixture_and_failure_denominators(self):
        # In ONE direction, seven cases exercise every non-pass outcome.
        indices = [i for i, p in enumerate(self.predictions) if p["id"].endswith(":pal>en")]
        for ix, judgment in zip(indices[:4], ["meaning_error", "critical_error", "uncertain", "critical_error"]):
            self.reviews[ix].update(judgment=judgment, output_span="synthetic diagnostic", reason="Synthetic non-pass rating to test arithmetic.")
            self.reviews[ix]["categories"]["lexical_meaning"] = "uncertain" if judgment == "uncertain" else "fail"
        for ix, status in zip(indices[4:7], ["abstain", "timeout", "error"]):
            text = "[UNRESOLVED]" if status == "abstain" else ""
            self.predictions[ix].update(status=status, text=text)
            self.reviews[ix].update(judgment="not_assessable", output_sha256=b.digest(text.encode("utf-8")))
        result = self.score()
        english = result["directions"]["pal>en"]
        self.assertEqual((english["total"], english["accepted"], english["complete_outputs"]), (40, 33, 37))
        self.assertEqual((english["accepted_percent"], english["critical_error_percent"], english["complete_output_percent"]), (82.5, 5.0, 92.5))
        self.assertEqual(result["directions"]["pal>fa"]["accepted"], 40)
        self.assertEqual(sum(x["total"] for x in result["by_work"]["pal>en"].values()), 40)
        self.assertIn("not automatic semantic validation", result["assessment"])

    def test_missing_and_duplicate_cases_rejected(self):
        saved = list(self.predictions)
        self.predictions.pop()
        with self.assertRaisesRegex(ValueError, "Missing or extra"):
            self.score()
        self.predictions = saved + [saved[0]]
        with self.assertRaisesRegex(ValueError, "duplicate IDs"):
            self.score()

    def test_changed_input_or_review_output_rejected(self):
        original = self.predictions[0]["input_sha256"]
        self.predictions[0]["input_sha256"] = "wrong"
        with self.assertRaisesRegex(ValueError, "input changed"):
            self.score()
        self.predictions[0]["input_sha256"] = original
        self.reviews[0]["output_sha256"] = "wrong"
        with self.assertRaisesRegex(ValueError, "does not bind this output"):
            self.score()

    def test_pass_requires_positive_meaning_assessment(self):
        self.reviews[0]["categories"]["names"] = "fail"
        with self.assertRaisesRegex(ValueError, "accepted despite"):
            self.score()
        self.reviews[0]["categories"] = {k: "not_applicable" for k in b.CATEGORIES}
        with self.assertRaisesRegex(ValueError, "without positive meaning"):
            self.score()

    def test_uncertainty_and_errors_need_evidence(self):
        for judgment in ["meaning_error", "critical_error", "uncertain"]:
            with self.subTest(judgment=judgment):
                self.reviews[0]["judgment"] = judgment
                with self.assertRaisesRegex(ValueError, "without identified"):
                    self.score()

    def test_abstention_empty_output_and_late_success_rejected(self):
        for text, elapsed in [("[UNRESOLVED]", 1), ("", 1), ("answer", 1201)]:
            with self.subTest(text=text, elapsed=elapsed):
                self.predictions[0].update(text=text, elapsed_seconds=elapsed)
                with self.assertRaisesRegex(ValueError, "invalid success"):
                    self.score()

    def test_retrieval_and_context_contamination_rejected(self):
        self.run["retrieval"] = "gold answers"
        with self.assertRaisesRegex(ValueError, "standard v1 condition: retrieval"):
            self.score()
        self.run["retrieval"] = "none"
        self.run["fresh_context_each_case"] = False
        with self.assertRaisesRegex(ValueError, "standard v1 condition: fresh_context"):
            self.score()

    def test_holdout_guard_rejects_entire_work_and_missing_identity(self):
        path = self.scratch / "training.jsonl"
        b.write_lines(path, [{"id": "unselected", "work_id": "parsig:104"}])
        with self.assertRaisesRegex(ValueError, "holdout appears"):
            b.audit_training(path)
        b.write_lines(path, [{"id": "unknown"}])
        with self.assertRaisesRegex(ValueError, "Missing work/record"):
            b.audit_training(path)
        b.write_lines(path, [{"id": "synthetic", "work_id": "unrelated-work"}])
        self.assertEqual(b.audit_training(path)["rows"], 1)

    def test_reference_and_manifest_tampering_rejected(self):
        root = self.scratch / "pal-reference-v1"
        shutil.copytree(BENCH, root)
        shutil.copyfile(BENCH.parent / "pal-reference-v1.sha256", root.parent / "pal-reference-v1.sha256")
        original_root = b.ROOT
        b.ROOT = root
        try:
            self.assertEqual(b.verify()[0], self.frozen)
            reference = root / "references.jsonl"
            reference.write_bytes(reference.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "Frozen artifact changed"):
                b.verify()
            manifest = root / "manifest.json"
            manifest.write_bytes(manifest.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "Frozen manifest changed"):
                b.verify()
        finally:
            b.ROOT = original_root


if __name__ == "__main__":
    unittest.main()
