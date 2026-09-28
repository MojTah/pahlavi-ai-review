"""Execute preparation and transfer boundaries offline; never call HF or load weights."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from . import hf_dev_assisted as job, hf_convert


class ComparisonJobTests(unittest.TestCase):
    def test_specs_pin_shared_inputs_and_have_only_one_writable_mount(self):
        for family in ("gemma", "qwen"):
            with self.subTest(family=family), patch("huggingface_hub.HfApi.run_job", autospec=True) as submit:
                spec, identity = job.specification(family, "c" * 32)
                submit.assert_not_called()
                self.assertEqual(spec["timeout"], "55m")
                self.assertEqual(spec["flavor"], "a100-large")
                self.assertEqual(identity["input_files"], job.INPUT_FILES)
                self.assertEqual([v.mount_path for v in spec["volumes"] if not v.read_only], ["/output"])
                self.assertEqual(any(v.mount_path == "/trained" for v in spec["volumes"]), family == "gemma")
                self.assertNotIn("secrets", spec)
                compile(spec["command"][3], "cloud-comparison", "exec")
        with self.assertRaises(ValueError):
            job.specification("third-model")
        with self.assertRaises(ValueError):
            job.specification("gemma", "../bad")

    def test_pinned_qwen_fetch_executes_metadata_shard_schema_and_rejects_bad_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            digest = hashlib.sha256(b"fixture").hexdigest()
            identity = {"model_id": "test/model", "revision": "a" * 40,
                "files": {"config.json": {"bytes": 7, "sha256": digest}},
                "weight_shards_metadata_only": [{"rfilename": "model-00001-of-00001.safetensors",
                    "size": 7, "lfs": {"sha256": digest}}]}
            ip = root / "identity.json"
            ip.write_text(json.dumps(identity))
            def download(model, name, revision, token, local_dir):
                self.assertEqual((model, revision, token), ("test/model", "a" * 40, False))
                file = Path(local_dir) / name
                file.write_bytes(b"fixture")
                return str(file)
            with patch.dict(job.__dict__, {"remaining": hf_convert.remaining, "file_sha256": hf_convert.file_sha256,
                                          "emit": lambda *a, **k: None}), \
                    patch("huggingface_hub.hf_hub_download", side_effect=download) as fetch:
                job.fetch_qwen(ip, root / "base", time.monotonic() + 300)
                self.assertEqual(fetch.call_count, 2)
                identity["files"]["config.json"]["sha256"] = "0" * 64
                ip.write_text(json.dumps(identity))
                with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                    job.fetch_qwen(ip, root / "bad-base", time.monotonic() + 300)

    def test_both_cloud_bodies_require_all_first_attempts_and_correct_adapter(self):
        for family in ("gemma", "qwen"):
            with self.subTest(family=family), tempfile.TemporaryDirectory() as td:
                stage = Path(td)
                evidence, trained = stage / "evidence", stage / "remote"
                evidence.mkdir()
                (stage / "bundle").mkdir()
                (stage / "bundle/manifest.json").write_text("{}")
                (stage / "qwen-source-identity.json").write_text("{}")
                entries = {}
                for name in ("training/adapter/adapter_config.json", "training/adapter/adapter_model.safetensors",
                             "training/provenance.json", "training/status.json"):
                    path = trained / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(b"fixture")
                    entries[name] = {"bytes": 7, "sha256": hf_convert.file_sha256(path)}
                manifest = trained / "manifest.json"
                manifest.write_text(json.dumps({"full_training_completed": True, "training_schedule_completed": True,
                                                 "completed_global_step": 280, "files": entries}))
                settings = {"family": family, "trained_manifest_sha256": hf_convert.file_sha256(manifest),
                    "input_files": job.INPUT_FILES,
                    "runner": "dev_assisted.py" if family == "gemma" else "dev_qwen_assisted.py"}
                calls = []
                def child(command, check, timeout):
                    self.assertTrue(check)
                    self.assertGreater(timeout, 0)
                    calls.append(command)
                    if "--download" in command:
                        (stage / "base").mkdir()
                        (stage / "base/provenance.json").write_text("{}")
                    else:
                        out = evidence / "comparison"
                        out.mkdir()
                        (out / "run.json").write_text(json.dumps({"status": "incomplete", "completed_outputs": 4}))
                        (out / "predictions.jsonl").write_text('{}\n' * 4)
                modules = {"bundle": SimpleNamespace(verify=lambda p: None),
                           "runtime": SimpleNamespace(gpu_admission=lambda: {}, offline=lambda: None)}
                with patch.dict("sys.modules", modules), patch("sys.path", list(sys.path)), \
                        patch.dict(job.__dict__, {"Path": lambda v: trained if v == "/trained" else Path(v),
                            "remaining": hf_convert.remaining, "file_sha256": hf_convert.file_sha256,
                            "emit": lambda *a, **k: None}), \
                        patch.object(job, "fetch_qwen") as fetch, patch("subprocess.run", side_effect=child):
                    with self.assertRaisesRegex(ValueError, "all 48 first attempts"):
                        job.comparison_body(settings, stage, time.monotonic() + 2500, evidence)
                    self.assertEqual(fetch.call_count, int(family == "qwen"))
                self.assertEqual("--adapter" in calls[-1], family == "gemma")
                self.assertIn("--evidence", calls[-1])
                self.assertNotIn("--full", calls[-1])
                self.assertEqual(len((evidence / "comparison/predictions.jsonl").read_text().splitlines()), 4)


if __name__ == "__main__":
    unittest.main()
