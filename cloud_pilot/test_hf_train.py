"""Offline spec/interface checks; these do not claim A100 or bucket execution."""
import base64
import gzip
import hashlib
import inspect
import json
from pathlib import Path
import unittest
from unittest.mock import patch

try:
    from . import hf_train as train, hf_preflight
except ImportError:
    import hf_train as train
    import hf_preflight


class CanaryPreparationTests(unittest.TestCase):
    def options(self):
        return dict(bundle_name="cloud-pilot-v5.zip", bundle_sha256="a" * 64, run_id="b" * 32)

    def test_native_spec_keeps_verified_stack_and_is_prepare_only(self):
        with patch("huggingface_hub.HfApi.whoami", side_effect=AssertionError("No auth")), \
             patch("huggingface_hub.HfApi.run_job", autospec=True) as submit:
            spec, evidence = train.specification(**self.options())
            submit.assert_not_called()
        original, hashes = hf_preflight.specification("cuda")
        self.assertEqual(spec["image"], original["image"])
        self.assertEqual(spec["command"][4:], original["command"][4:])
        self.assertEqual(evidence["bootstrap_hashes"], hashes)
        payload = json.loads(gzip.decompress(base64.b64decode(spec["command"][4])))
        for name, item in payload.items():
            self.assertEqual(base64.b64decode(item["content"]), Path(train.__file__).with_name(name).read_bytes())
        self.assertEqual((spec["flavor"], spec["timeout"]), ("a100-large", "30m"))
        self.assertNotIn("secrets", spec)
        self.assertEqual(spec["volumes"][0].to_dict(), {"type": "bucket", "source": train.BUCKET,
            "path": "inputs", "mountPath": "/input", "readOnly": True})
        self.assertEqual(spec["volumes"][1].to_dict(), {"type": "bucket", "source": train.BUCKET,
            "path": "trials/" + "b" * 32, "mountPath": "/output", "readOnly": False})
        compile(spec["command"][3], "generated-canary", "exec")
        self.assertEqual(evidence["command_sha256"], hashlib.sha256(spec["command"][3].encode()).hexdigest())

    def test_scope_and_bundle_identity_are_required(self):
        for change in ({"bundle_name": "../v5.zip"}, {"bundle_name": "/v5.zip"},
                       {"bundle_sha256": "x" * 64}, {"run_id": "../prior"}):
            options = self.options()
            options.update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                train.specification(**options)

    def test_generated_contract_has_ordered_admission_and_bounded_export(self):
        spec, evidence = train.specification(**self.options())
        source = spec["command"][3]
        body = inspect.getsource(train.canary_body)
        self.assertLess(body.index("runtime.gpu_admission()"), body.index('child("base_download"'))
        self.assertLess(body.index('child("base_download"'), body.index('child("canary"'))
        self.assertNotIn('"eval"', body)
        self.assertNotIn("evaluation-inputs", source)
        self.assertNotIn("stdout=", body)
        self.assertNotIn("stderr=", body)
        self.assertNotIn('phase + ".log"', body)
        self.assertIn('"--max-steps", "20"', body)
        self.assertNotIn('"--full"', body)
        self.assertNotIn('"--resume"', body)
        self.assertIn("signal.alarm(1500)", source)
        self.assertIn("deadline = time.monotonic() + 1500", source)
        self.assertEqual(evidence["internal_seconds"], 1500)
        self.assertIn("min(300, deadline - time.monotonic())", source)
        self.assertEqual(evidence["export_reserve_seconds"], 180)
        bootstrap = hf_preflight.BOOTSTRAP.partition("device = sys.argv[2]\n")[0]
        self.assertIn(repr(bootstrap), source)
        self.assertNotIn("tiny-smoke", source)
        publishing = inspect.getsource(train.publish)
        self.assertNotIn("os.replace", publishing)
        self.assertNotIn("fsync", publishing)
        self.assertIn('target.open("xb")', publishing)
        self.assertIn('"cross_job_sha256_verified": False', publishing)


if __name__ == "__main__":
    unittest.main()
