"""Exercise fit packaging offline with ordinary-directory fixtures; no cloud or model."""
import ast
import base64
import hashlib
import inspect
import json
from pathlib import Path
import shutil
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid

from . import hf_train_fit as job, hf_dev_assisted, hf_preflight

ROOT = Path(__file__).resolve().parents[1]
INPUT_NAME = "train-recall-5a2b29c878b6.jsonl"
CONTROL_NAME = "train-fit-source-control-3db2398a95b6.json"


class FitJobTests(unittest.TestCase):
    def scratch(self):
        # tempfile's 0700 mkdir has a Windows sandbox ACL issue. Retain bounded fixtures.
        folder = ROOT / "resources/local/train-fit-test-tmp" / uuid.uuid4().hex
        folder.mkdir(parents=True)
        return folder

    def specification(self):
        return job.specification(INPUT_NAME, job.INPUTS_SHA256, CONTROL_NAME, job.SOURCE_CONTROL_SHA256, "e" * 32)

    def rows(self):
        return [json.loads(line) for line in
            (ROOT / "experiments/train-recall-20260927/inputs.jsonl").read_text("utf-8").splitlines()]

    def control(self):
        return json.loads((ROOT / "experiments/train-fit-20260927/source-control.json").read_text("utf-8"))

    def completed_files(self, folder):
        from . import train_fit
        rows = self.rows()
        ordered = list(train_fit.schedule(rows))
        ids = [train_fit.output_id(row, enabled, source) for row, enabled, source in ordered]
        audit = json.loads((ROOT / "experiments/train-fit-20260927/token-audit.json").read_text("utf-8"))
        prepared = {row["id"] + ":" + row["source_condition"]:
            {field: row[field] for field in train_fit.TOKEN_MAP_FIELDS} for row in audit["rows"]}
        run = dict(status="completed", scheduled_outputs=80, attempted_outputs=80, recorded_outputs=80,
            completed_outputs=80, completed_cases=20, active_output_id=None, unattempted_output_ids=[],
            inputs_sha256=job.INPUTS_SHA256, source_control_sha256=job.SOURCE_CONTROL_SHA256,
            expected_token_map_sha256=job.EXPECTED_TOKEN_MAP_SHA256, actual_token_map_sha256=job.EXPECTED_TOKEN_MAP_SHA256,
            identity_sha256="d" * 64, prepared_inputs=prepared, schedule=ids,
            runner_sha256=job.file_sha256(Path(job.__file__).with_name("train_fit.py")),
            adapter_manifest_sha256=hf_dev_assisted.dev_assisted.ADAPTER_MANIFEST_SHA256,
            adapter_step=280, generation_performed=False, training_performed=False)
        results = [dict(id=ids[index], case_id=row["id"], record_id=row["record_id"], work_id=row["work_id"],
            adapter_enabled=enabled, source_condition=source, sequence=index + 1, status="success",
            input_sha256=prepared[row["id"] + ":" + source]["input_ids_sha256"],
            **{field: prepared[row["id"] + ":" + source][field] for field in
               ("labels_sha256", "target_ids_sha256", "supervised_tokens", "input_tokens", "prompt_tokens")},
            identity_sha256="d" * 64, sum_nll=float(prepared[row["id"] + ":" + source]["supervised_tokens"]),
            mean_nll=1.0, model_loss=1.0, numerical_loss_difference=0.0)
            for index, (row, enabled, source) in enumerate(ordered)]
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "run.json").write_text(json.dumps(run), encoding="utf-8")
        (folder / "results.jsonl").write_text("".join(json.dumps(row) + "\n" for row in results), encoding="utf-8")
        return run, results

    def test_native_spec_mounts_pins_and_real_sdk_signature_without_client(self):
        with patch("huggingface_hub.HfApi.__init__", side_effect=AssertionError("No authenticated client")), \
             patch("huggingface_hub.HfApi.run_job", autospec=True) as submit:
            spec, identity = self.specification()
            submit.assert_not_called()
        original, hashes = hf_preflight.specification("cuda")
        self.assertEqual(spec["image"], original["image"])
        self.assertEqual(spec["command"][4:], original["command"][4:])
        self.assertEqual(identity["bootstrap_hashes"], hashes)
        self.assertEqual((spec["flavor"], spec["timeout"]), ("a100-large", "29m"))
        self.assertEqual(identity["scheduled_outputs"], 80)
        self.assertEqual([identity[key] for key in ("compute_seconds", "internal_seconds", "export_reserve_seconds", "maximum_wait_seconds")],
                         [1440, 1620, 180, 180])
        self.assertEqual(identity["bundle_sha256"], hf_dev_assisted.BUNDLE_SHA256)
        self.assertEqual(identity["trained_manifest_sha256"], hf_dev_assisted.dev_assisted.ADAPTER_MANIFEST_SHA256)
        self.assertEqual([(v.path, v.mount_path, v.read_only) for v in spec["volumes"]],
            [("inputs", "/input", True), (hf_dev_assisted.TRAINED_PREFIX, "/trained", True),
             ("train-fit/" + "e" * 32, "/output", False)])
        self.assertNotIn("secrets", spec)
        self.assertEqual(identity["command_sha256"], hashlib.sha256(spec["command"][3].encode()).hexdigest())
        compile(spec["command"][3], "generated-fit", "exec")
        from huggingface_hub import HfApi
        inspect.signature(HfApi.run_job).bind(None, **spec)

    def test_frozen_inputs_control_and_source_snapshot(self):
        self.assertEqual(job.file_sha256(ROOT / "experiments/train-recall-20260927/inputs.jsonl"), job.INPUTS_SHA256)
        self.assertEqual(job.file_sha256(ROOT / "experiments/train-fit-20260927/source-control.json"), job.SOURCE_CONTROL_SHA256)
        spec, identity = self.specification()
        tree = ast.parse(spec["command"][3])
        scripts = next(ast.literal_eval(node.value) for node in tree.body
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "scripts")
        self.assertEqual(set(scripts), {"train_fit.py", "train_recall.py", "dev_assisted.py", "dev_diagnostic.py", "palref_eval.py"})
        for name, entry in scripts.items():
            data = base64.b64decode(entry["content"])
            self.assertEqual(data, Path(job.__file__).with_name(name).read_bytes())
            self.assertEqual(hashlib.sha256(data).hexdigest(), identity["script_hashes"][name])
        self.assertFalse(self.control()["contains_reference_answers"])
        self.assertTrue(self.control()["never_training_pairs"])
        self.assertTrue(all(set(row) == {"id", "record_id", "work_id", "source_text", "source_language", "target_language"}
                            for row in self.rows()))
        self.assertNotIn('"target_text":', spec["command"][3])

    def test_unsafe_names_or_unfrozen_hashes_are_rejected(self):
        options = dict(inputs_name=INPUT_NAME, inputs_sha256=job.INPUTS_SHA256,
            source_control_name=CONTROL_NAME, source_control_sha256=job.SOURCE_CONTROL_SHA256, run_id="e" * 32)
        for change in ({"inputs_name": "../bad.jsonl"}, {"source_control_name": "/bad.json"},
                       {"inputs_sha256": "f" * 64}, {"source_control_sha256": "f" * 64}, {"run_id": "pending"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                job.specification(**{**options, **change})

    def test_exact_eighty_first_forward_identity_gate(self):
        folder = self.scratch()
        run, results = self.completed_files(folder)
        _, settings = self.specification()
        job.completed_fit(folder, self.rows(), self.control(), settings)
        for change in ({"attempted_outputs": 79}, {"attempted_outputs": 81}, {"recorded_outputs": 79},
                       {"completed_outputs": 79}, {"completed_cases": 19}, {"active_output_id": results[0]["id"]},
                       {"inputs_sha256": "0" * 64}, {"source_control_sha256": "0" * 64},
                       {"runner_sha256": "0" * 64}, {"adapter_step": 20}, {"generation_performed": True},
                       {"actual_token_map_sha256": "0" * 64}, {"prepared_inputs": {}}):
            with self.subTest(change=change):
                (folder / "run.json").write_text(json.dumps({**run, **change}), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "80 frozen first-forward identities"):
                    job.completed_fit(folder, self.rows(), self.control(), settings)
        (folder / "run.json").write_text(json.dumps(run), encoding="utf-8")
        altered_run = json.loads(json.dumps(run))
        altered_run["prepared_inputs"][next(iter(altered_run["prepared_inputs"]))]["input_ids_sha256"] = "0" * 64
        (folder / "run.json").write_text(json.dumps(altered_run), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "prepared token map differs"):
            job.completed_fit(folder, self.rows(), self.control(), settings)
        (folder / "run.json").write_text(json.dumps(run), encoding="utf-8")
        for altered in (results[:-1], results + results[:1], [results[0]] * 80):
            (folder / "results.jsonl").write_text("".join(json.dumps(row) + "\n" for row in altered), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "80 frozen first-forward identities"):
                job.completed_fit(folder, self.rows(), self.control(), settings)
        for change in ({"status": "error"}, {"adapter_enabled": False}, {"source_condition": "mismatched"},
                       {"input_sha256": "0" * 64}, {"labels_sha256": "0" * 64}, {"supervised_tokens": 0},
                       {"sum_nll": float("nan")}, {"mean_nll": None}):
            with self.subTest(change=change):
                altered = [{**results[0], **change}, *results[1:]]
                (folder / "results.jsonl").write_text("".join(json.dumps(row) + "\n" for row in altered), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "identity/numerical status mismatch"):
                    job.completed_fit(folder, self.rows(), self.control(), settings)

    def lifecycle(self, mode):
        spec, _ = self.specification()
        tree = ast.parse(spec["command"][3])
        namespace = {}
        # Load the actual generated definitions/settings, then isolate external boundaries.
        exec(compile(ast.Module(body=tree.body[:-1], type_ignores=[]), "generated-fit-definitions", "exec"), namespace)
        root = self.scratch()
        inputs, output, stage = root / "inputs", root / "output", root / "stage"
        inputs.mkdir()
        stage.mkdir()
        shutil.copyfile(ROOT / "experiments/train-recall-20260927/inputs.jsonl", inputs / INPUT_NAME)
        shutil.copyfile(ROOT / "experiments/train-fit-20260927/source-control.json", inputs / CONTROL_NAME)
        shutil.copyfile(ROOT / "resources/local/cloud-pilot-qualified-20260927.zip", inputs / hf_dev_assisted.BUNDLE_NAME)
        if mode in {"input_hash", "control_hash"}:
            target = inputs / (INPUT_NAME if mode == "input_hash" else CONTROL_NAME)
            target.write_bytes(target.read_bytes() + b" ")
        calls, alarms = [], []
        def mapped_path(value):
            return {"/input": inputs, "/output": output}.get(str(value), Path(value))
        def bootstrap(source):
            calls.append("bootstrap")
            if mode == "bootstrap":
                raise RuntimeError("bootstrap fixture failure")
        def body(settings, stage, deadline, evidence):
            calls.append("fit")
            target = evidence / "fit"
            if mode == "forward":
                target.mkdir()
                (target / "results.jsonl").write_text('{"status":"error"}\n', encoding="utf-8")
                raise RuntimeError("first forward failed")
            self.completed_files(target)
            namespace["completed_fit"](target, self.rows(), self.control(), settings)
        namespace.update(Path=mapped_path, exec=bootstrap, fit_body=body,
            time=SimpleNamespace(monotonic=lambda: 100, sleep=lambda seconds: calls.append(("sleep", seconds))),
            signal=SimpleNamespace(SIGTERM=15, SIGALRM=14, signal=lambda *a: None, alarm=alarms.append),
            tempfile=SimpleNamespace(mkdtemp=lambda **kwargs: str(stage)), emit=lambda *a, **k: None)
        with patch("shutil.disk_usage", return_value=SimpleNamespace(free=100 * 1024**3)):
            invocation = compile(ast.Module(body=[tree.body[-1]], type_ignores=[]), "generated-fit-invocation", "exec")
            if mode == "success":
                exec(invocation, namespace)
            else:
                with self.assertRaises((RuntimeError, ValueError)):
                    exec(invocation, namespace)
        manifest = json.loads((output / "manifest.json").read_text("utf-8"))
        status = json.loads((output / "fit-status.json").read_text("utf-8"))
        self.assertEqual(manifest["fit_status"], "complete" if mode == "success" else "incomplete")
        self.assertEqual(status["evaluation_complete"], mode == "success")
        self.assertFalse(manifest["remote_inventory_verified"])
        self.assertEqual(alarms, [1440, 1620, 0])
        self.assertIn(("sleep", 180), calls)
        self.assertEqual(calls.count("fit"), int(mode in {"success", "forward"}))
        for name, entry in manifest["files"].items():
            self.assertEqual(job.file_sha256(output / name), entry["sha256"])
        if mode == "forward":
            self.assertEqual((output / "fit/results.jsonl").read_text("utf-8"), '{"status":"error"}\n')
        if mode in {"input_hash", "control_hash"}:
            self.assertNotIn("bootstrap", calls)
            self.assertFalse((stage / "bundle").exists())
        with self.assertRaisesRegex(ValueError, "never reuse"):
            namespace["fresh_output"](output)

    def test_generated_success_lifecycle_publishes_complete_records(self):
        self.lifecycle("success")

    def test_generated_first_forward_failure_preserves_partial_without_retry(self):
        self.lifecycle("forward")

    def test_generated_bootstrap_failure_still_publishes_status(self):
        self.lifecycle("bootstrap")

    def test_generated_input_hash_failures_precede_extraction_and_bootstrap(self):
        for mode in ("input_hash", "control_hash"):
            with self.subTest(mode=mode):
                self.lifecycle(mode)


if __name__ == "__main__":
    unittest.main()
