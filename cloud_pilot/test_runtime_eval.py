"""Offline admission checks for the one frozen post-training evaluation sidecar."""
import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

try:
    from . import runtime, bundle as verifier
except ImportError:
    import runtime
    import bundle as verifier


class ExtraEvaluationTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parent.parent
        self.bundle = root / "resources/local/cloud-pilot-20260926-hf-v4"
        self.sidecar = root / "experiments/staged-dev-20260926/bf16-after-inputs-only.jsonl"
        self.data = self.sidecar.read_bytes()
        self.rows = [json.loads(line) for line in self.data.decode("utf-8").splitlines()]
        self.original = [json.loads(line) for line in (self.bundle / "dev-inputs.jsonl").read_text("utf-8").splitlines()]
        self.module = patch.dict(runtime.sys.modules, {"_pilot_bundle_verifier": verifier})
        self.module.start()
        self.addCleanup(self.module.stop)

    def admit(self, data, original=None):
        real_read = Path.read_bytes
        with patch.object(Path, "read_bytes", autospec=True,
                side_effect=lambda path: data if path == self.sidecar else real_read(path)):
            return runtime.extra_eval_rows(self.sidecar, "adapter", self.original if original is None else original, self.bundle)

    def test_exact_frozen_file_and_holdout_guard_pass(self):
        rows, checksum = runtime.extra_eval_rows(self.sidecar, "adapter", self.original, self.bundle)
        self.assertEqual(rows, self.rows)
        self.assertEqual(checksum, "da52b3026596ce843bc015959bbc17a4b6ee8bfa3af4206506d152ea975de06e")
        self.assertEqual({row["id"] for row in rows}, runtime.EXTRA_EVAL_IDS)
        self.assertEqual(len(self.original), 6)

    def test_adapter_required_before_sidecar_read(self):
        with patch.object(Path, "read_bytes") as read:
            with self.assertRaisesRegex(ValueError, "require --adapter"):
                runtime.extra_eval_rows(self.sidecar, None, self.original, self.bundle)
            read.assert_not_called()

    def test_even_whitespace_tampering_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "frozen six"):
            self.admit(self.data + b"\n")

    def test_collision_with_historical_ids_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "distinct"):
            self.admit(self.data, self.original + [self.rows[0]])

    def test_schema_direction_controls_and_id_validation(self):
        mutations = [
            lambda rows: rows[0].update(target="reference must never enter inference"),
            lambda rows: rows[0].update(prompt=""),
            lambda rows: rows[0].update(text="<pad>"),
            lambda rows: rows[0].update(prompt="<|channel>"),
            lambda rows: rows[0].update(source_language="en"),
            lambda rows: rows[0].update(id=rows[1]["id"]),
            lambda rows: rows.pop(),
        ]
        for mutate in mutations:
            rows = copy.deepcopy(self.rows)
            mutate(rows)
            data = ("\n".join(json.dumps(row) for row in rows) + "\n").encode()
            # Exercise the structural guards separately from the byte-level pin.
            with self.subTest(mutation=mutate), patch.object(runtime, "EXTRA_EVAL_SHA256", hashlib.sha256(data).hexdigest()):
                with self.assertRaises(ValueError):
                    self.admit(data)

    def test_benchmark_overlap_is_rejected_by_pinned_guard(self):
        rules = runtime.read_json(self.bundle / "benchmark-holdout.json")
        rules["excluded_work_ids"].append(self.rows[2]["work_id"].removeprefix("parsig:"))
        with patch.object(runtime, "read_json", return_value=rules):
            with self.assertRaisesRegex(ValueError, "held-out benchmark"):
                self.admit(self.data)

    def test_no_adapter_rejected_by_eval_before_base_or_gpu(self):
        args = SimpleNamespace(bundle=str(self.bundle), contract=str(self.bundle / "contract.json"),
            inputs=str(self.bundle / "dev-inputs.jsonl"), extra_inputs=str(self.sidecar), adapter=None,
            deadline_utc="2099-01-01T00:00:00Z")
        with patch.object(runtime, "offline"), \
                patch.object(runtime, "bundled_contract", return_value=(self.bundle, {})), \
                patch.object(runtime, "verify_base") as base, patch.object(runtime, "gpu_admission") as gpu:
            with self.assertRaisesRegex(ValueError, "require --adapter"):
                runtime.evaluate(args)
            base.assert_not_called()
            gpu.assert_not_called()

    def test_valid_sidecar_appends_six_before_model_loading(self):
        args = SimpleNamespace(bundle=str(self.bundle), contract=str(self.bundle / "contract.json"),
            inputs=str(self.bundle / "dev-inputs.jsonl"), extra_inputs=str(self.sidecar), adapter="adapter",
            output=str(self.bundle / "unused-eval-test-output.jsonl"), base="unused-base",
            deadline_utc="2099-01-01T00:00:00Z")
        with patch.object(runtime, "offline"), \
                patch.object(runtime, "bundled_contract", return_value=(self.bundle, {})), \
                patch.object(runtime, "extra_eval_rows", wraps=runtime.extra_eval_rows) as extra, \
                patch.object(runtime, "verify_base", side_effect=RuntimeError("stop before base load")), \
                patch.object(runtime, "gpu_admission") as gpu:
            with self.assertRaisesRegex(RuntimeError, "stop before base load"):
                runtime.evaluate(args)
            combined = extra.call_args.args[2]
            self.assertEqual(len(combined), 12)
            self.assertEqual(combined[:6], self.original)
            self.assertEqual(combined[6:], self.rows)
            gpu.assert_not_called()


if __name__ == "__main__":
    unittest.main()
