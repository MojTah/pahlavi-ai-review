"""Offline spec and executed cloud-body contract checks; no credentials or GPU."""
import hashlib
import json
from pathlib import Path
import tempfile
import time
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from . import hf_dev_diagnostic as job, hf_convert


class DiagnosticJobTests(unittest.TestCase):
    def test_spec_reuses_pinned_bootstrap_and_restricts_writes(self):
        with patch("huggingface_hub.HfApi.run_job", autospec=True) as submit:
            spec, identity = job.specification("d" * 32)
        submit.assert_not_called()
        self.assertEqual(spec["timeout"], "55m")
        self.assertEqual(spec["flavor"], "a100-large")
        self.assertNotIn("secrets", spec)
        self.assertEqual([(v.mount_path, v.read_only) for v in spec["volumes"]],
                         [("/input", True), ("/trained", True), ("/output", False)])
        self.assertEqual(identity["trained_manifest_sha256"], job.TRAINED_MANIFEST_SHA256)
        compile(spec["command"][3], "prepared-job", "exec")
        with self.assertRaises(ValueError):
            job.specification("../bad")

    def test_body_copies_verified_adapter_and_rejects_incomplete_child(self):
        with tempfile.TemporaryDirectory() as td:
            stage = Path(td)
            trained, evidence = stage / "remote", stage / "evidence"
            evidence.mkdir()
            entries = {}
            for name in ("training/adapter/adapter_config.json", "training/adapter/adapter_model.safetensors",
                         "training/provenance.json", "training/status.json"):
                file = trained / name
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_bytes(b"verified-test-artifact")
                entries[name] = {"bytes": file.stat().st_size, "sha256": hf_convert.file_sha256(file)}
            manifest = trained / "manifest.json"
            manifest.write_text(json.dumps({"full_training_completed": True, "training_reached_step_312": True, "files": entries}))
            (stage / "bundle").mkdir()
            (stage / "bundle/manifest.json").write_text("{}")
            settings = {"trained_manifest_sha256": hf_convert.file_sha256(manifest), "inputs_name": job.INPUTS_NAME}
            calls = []

            def child(command, check, timeout):
                self.assertTrue(check)
                self.assertGreater(timeout, 0)
                calls.append(command)
                if "--download" in command:
                    (stage / "base").mkdir(exist_ok=True)
                    (stage / "base/provenance.json").write_text("{}")
                else:
                    out = evidence / "diagnostic"
                    out.mkdir(exist_ok=True)
                    (out / "run.json").write_text(json.dumps({"status": "incomplete", "completed_outputs": 4}))
                    (out / "predictions.jsonl").write_text('{}\n' * 4)

            def mapped_path(value):
                return trained if value == "/trained" else Path(value)

            mocks = {"bundle": SimpleNamespace(verify=lambda p: None),
                     "runtime": SimpleNamespace(gpu_admission=lambda: {"test": True}, offline=lambda: None)}
            with patch.dict("sys.modules", mocks), patch.dict(job.__dict__, {
                "Path": mapped_path, "file_sha256": hf_convert.file_sha256,
                "remaining": hf_convert.remaining, "emit": lambda *a, **k: None}, clear=False), \
                    patch("subprocess.run", side_effect=child), patch("sys.path", list(sys.path)):
                with self.assertRaisesRegex(ValueError, "did not complete"):
                    job.diagnostic_body(settings, stage, time.monotonic() + 2000, evidence)
            self.assertEqual(len(calls), 2)
            self.assertEqual((stage / "training/status.json").read_bytes(), b"verified-test-artifact")
            self.assertIn("--adapter", calls[1])
            self.assertIn(str(stage / "training/adapter"), calls[1])
            self.assertNotIn("--full", calls[1])


if __name__ == "__main__":
    unittest.main()
