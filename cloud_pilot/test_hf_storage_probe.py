"""Offline preparation checks; heavy model/storage execution belongs to the CPU Job."""
import base64
import gzip
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

try:
    from . import hf_preflight, hf_storage_probe as probe
except ImportError:
    import hf_preflight
    import hf_storage_probe as probe


class StorageProbePreparationTests(unittest.TestCase):
    def test_spec_preserves_pins_payload_and_scopes_volumes(self):
        run_id = "a" * 32
        with patch("huggingface_hub.HfApi.whoami", side_effect=AssertionError("Unexpected auth")), \
             patch("huggingface_hub.HfApi.run_job", autospec=True) as submit:
            spec, evidence = probe.specification(run_id)
            submit.assert_not_called()
        original, hashes = hf_preflight.specification("cpu")
        for key in ("image", "env", "flavor", "timeout", "namespace"):
            self.assertEqual(spec[key], original[key])
        self.assertEqual(spec["timeout"], "8m")
        self.assertEqual(spec["command"][4:], original["command"][4:])
        self.assertIn(hf_preflight.BOOTSTRAP, spec["command"][3])
        self.assertEqual(spec["volumes"][0].to_dict(), {"type": "bucket", "source": probe.BUCKET,
            "path": "inputs", "mountPath": "/input", "readOnly": True})
        self.assertEqual(spec["volumes"][1].to_dict(), {"type": "bucket", "source": probe.BUCKET,
            "path": "probes/" + run_id, "mountPath": "/output", "readOnly": False})
        decoded = json.loads(gzip.decompress(base64.b64decode(spec["command"][4])))
        self.assertEqual(set(decoded), {"runtime.py", "requirements-linux.lock"})
        for name, item in decoded.items():
            content = base64.b64decode(item["content"])
            self.assertEqual(hashlib.sha256(content).hexdigest(), hashes[name])
            self.assertEqual(content, Path(probe.__file__).with_name(name).read_bytes())
        self.assertEqual(evidence["files"], hashes)
        compile(spec["command"][3], "bootstrap-test", "exec")
        compile(probe.PROBE, "probe-test", "exec")

    def test_invalid_output_scope_is_rejected(self):
        for value in ("../escape", "", "A" * 32, "a" * 33, 17):
            with self.subTest(value=value), self.assertRaises(ValueError):
                probe.specification(value)

    def test_fixture_match_and_failure_propagation(self):
        with patch.object(Path, "read_bytes", return_value=probe.FIXTURE_BYTES):
            probe.verify_fixture("unused")
        with patch.object(Path, "read_bytes", return_value=b"wrong"), self.assertRaises(ValueError):
            probe.verify_fixture("unused")
        with patch.object(Path, "read_bytes", side_effect=FileNotFoundError), self.assertRaises(FileNotFoundError):
            probe.verify_fixture("unused")


if __name__ == "__main__":
    unittest.main()
