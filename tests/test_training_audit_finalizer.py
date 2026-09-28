import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("audit_finalizer", ROOT / "scripts/finalize_training_audit.py")
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)


def fixture(id="one", text="a b", target="الف ب"):
    original = dict(id=id, record_id="record:" + id, work_id="work", revision="revision", credit="edition", text=text, target=target,
                    input_ids=[2, 3, 106], labels=[-100, 3, 106], attention_mask=[1, 1, 1], prompt_tokens=1)
    packet = dict(id=id, source=text, target=target, locator="chapter:" + id,
                  source_sha256=f.digest(text.encode()), target_sha256=f.digest(target.encode()))
    review = dict(id=id, source_sha256=packet["source_sha256"], target_sha256=packet["target_sha256"], alignment="pass",
                  meaning="no_identified_issue", disposition="ELIGIBLE", reason="The stated actor and action are both retained.",
                  source_span="", target_span="", qualifications=[], evidence=[packet["locator"]],
                  reviewer_id="/root/test", reviewer_type="AI", expert_adjudicated=False)
    ledger = dict(id=id, record_id=original["record_id"], work_id="work", revision="revision", credit="edition", row_number=1,
                  row_sha256=f.digest(f.canonical(original)), source_text=text, target_text=target,
                  source_sha256=packet["source_sha256"], target_sha256=packet["target_sha256"],
                  mechanical_status="PASS", provenance_status="PASS", token_structure_status="PASS_STRUCTURE_ONLY",
                  token_reconstruction_status="PASS_HASH_BOUND_INDEPENDENT_PROOF", split_status="PASS_IDENTITY_AND_PINNED_HOLDOUT",
                  mechanical_errors=[], split_errors=[], flags=[], disposition="UNREVIEWED")
    return original, packet, review, ledger


def structural(ledger, decision):
    return dict(id=ledger["id"], source_sha256=ledger["source_sha256"], target_sha256=ledger["target_sha256"],
                flag_kinds=f.nonmarker_flags(ledger), decision=decision, reason="The neighboring clause was checked against its archived paragraph.",
                evidence=["record:" + ledger["id"]], reviewer_id="/root", reviewer_type="AI", expert_adjudicated=False)


class FinalizerTests(unittest.TestCase):
    def test_missing_duplicate_and_extra_review_fields_rejected(self):
        _, packet, review, _ = fixture()
        for reviews in ([], [review, review], [dict(review, invented="field")]):
            with self.subTest(reviews=reviews), self.assertRaises(ValueError):
                f.validate_reviews([packet], reviews, "/root/test")

    def test_hash_and_exact_span_mismatch_rejected(self):
        _, packet, review, _ = fixture()
        for changed in (dict(review, source_sha256="wrong"), dict(review, source_span="a  b"), dict(review, target_span="invented")):
            with self.assertRaises(ValueError):
                f.validate_reviews([packet], [changed], "/root/test")

    def test_disposition_qualification_and_actual_reviewer_invariants(self):
        _, packet, review, _ = fixture()
        changes = [dict(disposition="UNREVIEWED"), dict(disposition="ELIGIBLE_WITH_QUALIFICATIONS"), dict(meaning="uncertain"),
                   dict(disposition="QUARANTINED"), dict(reviewer_id="/root/impostor"), dict(expert_adjudicated=True),
                   dict(reason="PASS"), dict(evidence=[])]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(ValueError):
                f.validate_reviews([packet], [dict(review, **change)], "/root/test")

    def test_concern_needs_exact_span_and_cited_evidence(self):
        _, packet, review, _ = fixture()
        concern = dict(review, meaning="uncertain", disposition="QUARANTINED")
        with self.assertRaisesRegex(ValueError, "supporting span"):
            f.validate_reviews([packet], [concern], "/root/test")
        concern["source_span"] = "a"
        self.assertEqual(f.validate_reviews([packet], [concern], "/root/test")["one"]["disposition"], "QUARANTINED")

    def test_structural_exact_coverage_hash_and_kind_checks(self):
        _, _, _, ledger = fixture()
        ledger["flags"] = [{"kind": "adjacent_target_overlap"}, {"kind": "marker:ellipsis"}]
        good = structural(ledger, "CLEAR_FLAG")
        f.validate_structural([ledger], [good])
        for values in ([], [good, good], [dict(good, source_sha256="wrong")], [dict(good, flag_kinds=["marker:ellipsis"])],
                       [dict(good, invented=True)]):
            with self.assertRaises(ValueError):
                f.validate_structural([ledger], values)

    def test_filter_keeps_exact_original_bytes_order_and_quarantine_precedence(self):
        values = [fixture(id) for id in ("one", "two", "three")]
        originals, packets, reviews, ledgers = map(list, zip(*values))
        for n, ledger in enumerate(ledgers, 1):
            ledger["row_number"] = n
        reviews[0].update(disposition="QUARANTINED", meaning="uncertain", source_span="a")
        reviews[2].update(disposition="ELIGIBLE_WITH_QUALIFICATIONS", meaning="qualified", qualifications=["Editorial restoration retained."])
        all_reviews = f.validate_reviews(packets, reviews, "/root/test")
        ledgers[0]["flags"] = [{"kind": "adjacent_target_overlap"}]
        ledgers[1]["flags"] = [{"kind": "heldout_near_source"}]
        checks = [structural(ledgers[0], "CLEAR_FLAG"), structural(ledgers[1], "QUARANTINE")]
        # Deliberately use spaces and CRLF; filtering must not canonicalize them.
        lines = [(json.dumps(row, ensure_ascii=False, separators=(", ", ": ")) + "\r\n").encode() for row in originals]
        final, data = f.merge(b"".join(lines), ledgers, all_reviews, {r["id"]: r for r in checks})
        self.assertEqual(data, lines[2])
        self.assertEqual([r["id"] for r in final], ["one", "two", "three"])
        self.assertEqual([r["disposition"] for r in final], ["QUARANTINED", "QUARANTINED", "ELIGIBLE_WITH_QUALIFICATIONS"])
        self.assertFalse(any(r["paid_run_admitted"] for r in final))

    def test_original_row_hash_mutation_rejected(self):
        original, _, _, ledger = fixture()
        original["input_ids"][0] = 99
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            f.validate_ledger(f.canonical(original) + b"\n", [ledger])

    def test_current_file_hash_and_size_verified(self):
        with patch.object(Path, "read_bytes", return_value=b"real"):
            for expected, length in ((f.digest(b"different"), 4), (f.digest(b"real"), 5)):
                with self.assertRaises(ValueError):
                    f.read_verified(ROOT / "fixture", {}, expected, length)

    def test_validation_failure_creates_no_output(self):
        with (patch.object(Path, "exists", return_value=False), patch.object(Path, "mkdir") as mkdir,
              patch.object(f, "load_inputs", side_effect=ValueError("incomplete reviews"))):
            with self.assertRaisesRegex(ValueError, "incomplete"):
                f.finalize(ROOT, ROOT / "experiments/not-created-fixture")
            mkdir.assert_not_called()

    def test_available_complete_real_packets(self):
        path = ROOT / f.AUDIT_ROOT / "linguistic-review/manifest.json"
        if not path.exists():
            self.skipTest("Frozen review packets not installed")
        manifest = json.loads(f.read_verified(path, {}, f.PACKET_MANIFEST_SHA))
        completed = 0
        for item in manifest["packets"]:
            packet_path = ROOT / item["path"]
            review_path = packet_path.with_name("reviews.jsonl")
            if not review_path.exists():
                continue
            packet = f.rows(f.read_verified(packet_path, {}, item["sha256"]))
            review = f.rows(review_path.read_bytes())
            if len(review) != len(packet):
                continue  # Full CLI still refuses partial coverage; this is bounded integration.
            with self.subTest(packet=item["packet"]):
                self.assertEqual(len(f.validate_reviews(packet, review, f.REVIEWERS[item["packet"]])), item["rows"])
            completed += 1
        if not completed:
            self.skipTest("No complete real packet yet")


if __name__ == "__main__":
    unittest.main()
