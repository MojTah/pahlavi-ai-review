"""Offline preparation checks; no model inference, cloud calls or credentials."""
import base64
import gzip
import inspect
import json
from pathlib import Path
import unittest
from unittest.mock import patch

try:
    from . import hf_baseline as baseline, hf_preflight
except ImportError:
    import hf_baseline as baseline
    import hf_preflight


class BaselinePreparationTests(unittest.TestCase):
    def options(self):
        return dict(bundle_name="v5.zip", bundle_sha256="a" * 64, evaluator_name="palref_eval.py",
            evaluator_sha256=baseline.file_sha256(Path(baseline.__file__).with_name("palref_eval.py")),
            inputs_name="palref40.jsonl", inputs_sha256=baseline.INPUTS_SHA256, run_id="e" * 32)

    def test_native_spec_keeps_frozen_stack_and_exact_two_mounts(self):
        with patch("huggingface_hub.HfApi.whoami", side_effect=AssertionError("No auth")), \
             patch("huggingface_hub.HfApi.run_job", autospec=True) as submit:
            spec, evidence = baseline.baseline_specification(**self.options())
            submit.assert_not_called()
        original, hashes = hf_preflight.specification("cuda")
        self.assertEqual(spec["image"], original["image"])
        self.assertEqual(spec["command"][4:], original["command"][4:])
        self.assertEqual(evidence["bootstrap_hashes"], hashes)
        payload = json.loads(gzip.decompress(base64.b64decode(spec["command"][4])))
        self.assertEqual(base64.b64decode(payload["runtime.py"]["content"]), Path(baseline.__file__).with_name("runtime.py").read_bytes())
        self.assertEqual((spec["flavor"], spec["timeout"]), ("a100-large", "30m"))
        self.assertEqual([(v.to_dict()["mountPath"], v.to_dict()["readOnly"]) for v in spec["volumes"]], [("/input", True), ("/output", False)])
        self.assertEqual(evidence["output_prefix"], "baselines/" + "e" * 32)
        self.assertNotIn("secrets", spec)
        compile(spec["command"][3], "baseline", "exec")

    def test_frozen_inputs_and_safe_scope_required(self):
        for change in ({"inputs_sha256": "a" * 64}, {"evaluator_sha256": "a" * 64},
                       {"bundle_name": "../bad.zip"}, {"run_id": "../bad"}, {"bundle_sha256": "bad"}):
            options = self.options()
            options.update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                baseline.baseline_specification(**options)

    def test_only_baseline_and_truthful_partial_export_contract(self):
        spec, _ = baseline.baseline_specification(**self.options())
        source = spec["command"][3]
        for forbidden in ('"--full"', '"--max-steps"', "/canary", "admission_name", "canary_compute_pass", "checkpoint-"):
            self.assertNotIn(forbidden, source)
        self.assertIn('os.environ["PYTHONPATH"] = str(folder)', source)
        self.assertNotIn("runtime.verify_base(base)", inspect.getsource(baseline.baseline_body))
        self.assertIn("signal.alarm(1320)", source)
        self.assertIn("baseline_status='incomplete'", source)
        self.assertIn("operation='palref_baseline'", source)
        self.assertIn("evaluation_complete=False", source)
        self.assertIn("16 * 1024**2", source)
        self.assertIn('target.open("xb")', source)
        self.assertNotIn("os.replace", source)
        self.assertNotIn("fsync", source)


if __name__ == "__main__":
    unittest.main()
