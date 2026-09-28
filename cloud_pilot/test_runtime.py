"""Offline runtime admission tests; no model imports or cloud operations."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import mock_open, patch

import runtime


class RuntimeChecks(unittest.TestCase):
    def setUp(self):
        self.bundle = Path(__file__).resolve().parent
        self.output = (self.bundle / "unused-test-run").resolve()
        self.checkpoint = self.output / "checkpoint-20"
        self.contract = runtime.read_json(self.bundle / "contract.json")
        self.contract["execution_policy"] = copy.deepcopy(runtime.CLOUD_FIRST_POLICY)
        self.args = SimpleNamespace(bundle=str(self.bundle), contract=str(self.bundle / "contract.json"),
            output=str(self.output), resume=str(self.checkpoint), full=True, max_steps=None,
            base="unused-base", deadline_utc="2099-01-01T00:00:00Z")

    def test_external_contract_rejected_by_train_and_eval_before_gpu(self):
        self.args.contract = str(self.bundle / "external-contract.json")
        for entry in (runtime.train, runtime.evaluate):
            with self.subTest(entry=entry.__name__), patch.object(runtime, "offline"), \
                    patch.object(runtime, "verified_bundle", return_value=self.bundle), \
                    patch.object(runtime, "contract_at") as contract_reader, \
                    patch.object(runtime, "gpu_admission") as gpu:
                with self.assertRaisesRegex(ValueError, "verified bundle's contract"):
                    entry(self.args)
                contract_reader.assert_not_called()
                gpu.assert_not_called()

    def test_matching_contract_is_read_only_after_bundle_verification(self):
        events = []
        with patch.object(runtime, "verified_bundle", side_effect=lambda _: events.append("verify") or self.bundle), \
                patch.object(runtime, "contract_at", side_effect=lambda _: events.append("read") or self.contract):
            self.assertEqual(runtime.bundled_contract(self.args), (self.bundle, self.contract))
        self.assertEqual(events, ["verify", "read"])

    def test_each_false_readiness_gate_rejected_before_gpu(self):
        for key in runtime.READINESS - {"local_model_verified"}:
            contract = copy.deepcopy(self.contract)
            contract["readiness"] = dict.fromkeys(runtime.READINESS, True)
            contract["readiness"][key] = False
            with self.subTest(gate=key), patch.object(runtime, "offline"), \
                    patch.object(runtime, "bundled_contract", return_value=(self.bundle, contract)), \
                    patch.object(runtime, "gpu_admission") as gpu:
                with self.assertRaisesRegex(ValueError, "every readiness gate"):
                    runtime.train(self.args)
                gpu.assert_not_called()

    def test_cloud_first_allows_false_local_fact_without_changing_it(self):
        self.contract["readiness"] = dict.fromkeys(runtime.READINESS, True)
        self.contract["readiness"]["local_model_verified"] = False
        with patch.object(runtime, "offline"), \
                patch.object(runtime, "bundled_contract", return_value=(self.bundle, self.contract)), \
                patch.object(runtime, "load_rows", side_effect=RuntimeError("past admission")), \
                patch.object(runtime, "gpu_admission") as gpu:
            with self.assertRaisesRegex(RuntimeError, "past admission"):
                runtime.train(self.args)
            gpu.assert_not_called()
        self.assertIs(self.contract["readiness"]["local_model_verified"], False)

    def test_cloud_first_policy_and_delivery_requirement_are_explicit(self):
        self.contract["readiness"] = dict.fromkeys(runtime.READINESS, True)
        for policy in (None, {}, {"mode": "cloud_first"},
                {"mode": "cloud_first", "local_validation_required_before_delivery": False},
                {"mode": "cloud_first", "local_validation_required_before_delivery": 1}):
            contract = copy.deepcopy(self.contract)
            contract["execution_policy"] = policy
            with self.subTest(policy=policy), patch.object(runtime, "offline"), \
                    patch.object(runtime, "bundled_contract", return_value=(self.bundle, contract)), \
                    patch.object(runtime, "gpu_admission") as gpu:
                with self.assertRaisesRegex(ValueError, "cloud-first policy"):
                    runtime.train(self.args)
                gpu.assert_not_called()

    def test_cloud_first_rejects_missing_or_nonboolean_local_fact(self):
        self.contract["readiness"] = dict.fromkeys(runtime.READINESS, True)
        for value in (None, "false", 0):
            self.contract["readiness"]["local_model_verified"] = value
            with self.subTest(value=value), patch.object(runtime, "offline"), \
                    patch.object(runtime, "bundled_contract", return_value=(self.bundle, self.contract)), \
                    patch.object(runtime, "gpu_admission") as gpu:
                with self.assertRaisesRegex(ValueError, "boolean fact"):
                    runtime.train(self.args)
                gpu.assert_not_called()

    def test_missing_or_empty_checkpoint_artifacts_rejected_before_gpu(self):
        required = ("trainer_state.json", "optimizer.pt", "scheduler.pt", "rng_state.pth",
                    "adapter_config.json", "adapter_model.safetensors")
        self.contract["readiness"] = dict.fromkeys(runtime.READINESS, True)
        for name in required:
            for missing in (True, False):
                with self.subTest(artifact=name, missing=missing), patch.object(runtime, "offline"), \
                        patch.object(runtime, "bundled_contract", return_value=(self.bundle, self.contract)), \
                        patch.object(runtime, "load_rows", return_value=[]), \
                        patch.object(Path, "exists", return_value=False), \
                        patch.object(Path, "is_file", autospec=True,
                            side_effect=lambda p: not (missing and p.name == name)), \
                        patch.object(Path, "stat", autospec=True,
                            side_effect=lambda p, **_: SimpleNamespace(st_size=0 if not missing and p.name == name else 1)), \
                        patch.object(runtime, "gpu_admission") as gpu:
                    with self.assertRaisesRegex(ValueError, "Missing or empty"):
                        runtime.train(self.args)
                    gpu.assert_not_called()

    def test_checkpoint_step_must_match_passing_canary(self):
        for status in ({"status": "canary_pass", "global_step": 19},
                       {"status": "failed", "global_step": 20}):
            with self.subTest(status=status), patch.object(Path, "exists", return_value=False), \
                    patch.object(Path, "is_file", return_value=True), \
                    patch.object(Path, "stat", return_value=SimpleNamespace(st_size=1)), \
                    patch.object(runtime, "read_json", side_effect=lambda p: status if p.name == "status.json" else {"global_step": 20}):
                with self.assertRaisesRegex(ValueError, "match the passing canary"):
                    runtime.resume_checkpoint(self.checkpoint, self.output)

    def test_resume_record_hashes_every_checkpoint_file(self):
        files = [self.checkpoint / name for name in ("optimizer.pt", "scheduler.pt", "rng_state.pth",
            "adapter_config.json", "adapter_model.safetensors", "trainer_state.json", "training_args.bin", "README.md")]
        with patch.object(Path, "exists", return_value=False), patch.object(Path, "is_file", return_value=True), \
                patch.object(Path, "stat", return_value=SimpleNamespace(st_size=1)), \
                patch.object(Path, "rglob", return_value=files), \
                patch.object(runtime, "read_json", side_effect=lambda p: {"status": "canary_pass", "global_step": 20}), \
                patch.object(runtime, "digest", side_effect=lambda p: "hash-" + p.name):
            checkpoint, record = runtime.resume_checkpoint(self.checkpoint, self.output)
        self.assertEqual(checkpoint, self.checkpoint)
        self.assertEqual(record, {"checkpoint": "checkpoint-20", "global_step": 20,
                                 "files": {p.name: "hash-" + p.name for p in files}})

    def test_existing_resume_record_is_rejected(self):
        with patch.object(Path, "exists", return_value=True):
            with self.assertRaisesRegex(ValueError, "record already exists"):
                runtime.resume_checkpoint(self.checkpoint, self.output)

    def test_resume_record_is_written_exclusively_before_model_loading(self):
        self.contract["readiness"] = dict.fromkeys(runtime.READINESS, True)
        record = {"checkpoint": "checkpoint-20", "global_step": 20, "files": {"optimizer.pt": "sha"}}
        expected_record = {**record, "contract": copy.deepcopy(self.contract),
                           "contract_sha256": "approved-contract-sha", "bundle_manifest_sha256": "approved-bundle-sha"}
        hashes = {"train.jsonl": "train-sha", "contract.json": "approved-contract-sha",
                  "manifest.json": "approved-bundle-sha"}
        identity = {"model": self.contract["model"], "training": self.contract["training"],
                    "train_sha256": "train-sha", "runtime": {}, "base_files": {"base": "sha"}}
        writer = mock_open()
        with patch.object(runtime, "offline"), \
                patch.object(runtime, "bundled_contract", return_value=(self.bundle, self.contract)), \
                patch.object(runtime, "load_rows", return_value=[]), \
                patch.object(runtime, "resume_checkpoint", return_value=(self.checkpoint, record)), \
                patch.object(runtime, "gpu_admission", return_value={}), \
                patch.object(runtime, "verify_base", return_value={"files": {"base": "sha"}}), \
                patch.object(runtime, "digest", side_effect=lambda p: hashes[p.name]), \
                patch.object(runtime, "read_json", return_value=identity), \
                patch.object(Path, "open", writer), \
                patch.object(runtime, "write_json", side_effect=RuntimeError("stop before model imports")) as json_writer:
            with self.assertRaisesRegex(RuntimeError, "stop before model imports"):
                runtime.train(self.args)
        writer.assert_called_once_with("x", encoding="utf-8")
        written = "".join(call.args[0] for call in writer().write.call_args_list)
        self.assertEqual(json.loads(written), expected_record)
        self.assertEqual(json_writer.call_args.args[0], self.output / "status.json")
        json_writer.assert_called_once()


if __name__ == "__main__":
    unittest.main()
