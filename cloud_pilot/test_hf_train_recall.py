"""Offline recall preparation/lifecycle tests; no authentication, cloud or weights."""
import ast
import base64
import hashlib
import inspect
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from . import hf_train_recall as job, hf_dev_assisted, hf_preflight, train_recall

INPUT_NAME = "train-recall-5a2b29c878b6.jsonl"
INPUT_SHA256 = "5a2b29c878b67e05bb1051fab015feae33753e7c23568ab57517af0cf84c233a"


class RecallJobTests(unittest.TestCase):
    def specification(self):
        return job.specification(INPUT_NAME, INPUT_SHA256, "d" * 32)

    def rows(self):
        return [{"id": f"RECALL-{index:03d}", "record_id": f"parsig:107000{index:03d}",
                 "work_id": "parsig:107", "source_text": f"fixture {index}"} for index in range(20)]

    def completed_files(self, output):
        rows = self.rows()
        ordered = train_recall.schedule(rows)
        ids = [row["id"] + ":" + condition for row, condition in ordered]
        run = dict(status="completed", scheduled_outputs=40, attempted_outputs=40, completed_outputs=40,
                   recorded_outputs=40, active_output_id=None,
                   completed_cases=20, unattempted_output_ids=[], schedule=ids,
                   inputs_sha256=INPUT_SHA256, identity_sha256="c" * 64)
        results = [dict(id=ids[index], case_id=row["id"], record_id=row["record_id"], work_id=row["work_id"],
                        condition=condition, sequence=index + 1, status="success", identity_sha256="c" * 64,
                        input_sha256=hashlib.sha256(row["source_text"].encode()).hexdigest())
                   for index, (row, condition) in enumerate(ordered)]
        output.mkdir(parents=True, exist_ok=True)
        (output / "run.json").write_text(json.dumps(run))
        (output / "predictions.jsonl").write_text("".join(json.dumps(row) + "\n" for row in results))
        return rows, run, results

    def test_specification_has_pins_native_timeout_readonly_inputs_and_real_sdk_signature(self):
        with patch("huggingface_hub.HfApi.__init__", side_effect=AssertionError("No authenticated client")), \
             patch("huggingface_hub.HfApi.run_job", autospec=True) as submit:
            spec, identity = self.specification()
            submit.assert_not_called()
        original, hashes = hf_preflight.specification("cuda")
        self.assertEqual((spec["flavor"], spec["timeout"]), ("a100-large", "30m"))
        self.assertEqual(spec["image"], original["image"])
        self.assertEqual(spec["command"][4:], original["command"][4:])
        self.assertEqual(identity["bootstrap_hashes"], hashes)
        self.assertEqual(identity["bundle_sha256"], hf_dev_assisted.BUNDLE_SHA256)
        self.assertEqual(identity["trained_manifest_sha256"], hf_dev_assisted.dev_assisted.ADAPTER_MANIFEST_SHA256)
        self.assertEqual(identity["inputs_sha256"], INPUT_SHA256)
        self.assertEqual(identity["scheduled_outputs"], 40)
        self.assertEqual((identity["compute_seconds"], identity["internal_seconds"],
                          identity["export_reserve_seconds"], identity["maximum_wait_seconds"]), (1440, 1620, 180, 180))
        self.assertEqual([(v.path, v.mount_path, v.read_only) for v in spec["volumes"]],
                         [("inputs", "/input", True), (hf_dev_assisted.TRAINED_PREFIX, "/trained", True),
                          ("train-recall/" + "d" * 32, "/output", False)])
        self.assertNotIn("secrets", spec)
        self.assertEqual(identity["command_sha256"], hashlib.sha256(spec["command"][3].encode()).hexdigest())
        compile(spec["command"][3], "actual-generated-recall", "exec")
        from huggingface_hub import HfApi
        inspect.signature(HfApi.run_job).bind(None, **spec)

    def test_requires_explicit_frozen_inputs_and_rejects_unsafe_values(self):
        with self.assertRaises(TypeError):
            job.specification()
        for name, digest, run_id in [("../inputs.jsonl", INPUT_SHA256, "d" * 32),
                                     (INPUT_NAME, "pending", "d" * 32),
                                     (INPUT_NAME, INPUT_SHA256, "../run")]:
            with self.subTest(name=name, digest=digest, run_id=run_id), self.assertRaises(ValueError):
                job.specification(name, digest, run_id)

    def test_actual_source_projection_and_embedded_helpers_have_no_answer_payload(self):
        root = Path(job.__file__).resolve().parents[1]
        path = root / "experiments/train-recall-20260927/inputs.jsonl"
        self.assertEqual(job.file_sha256(path), INPUT_SHA256)
        rows = train_recall.read_inputs(path, INPUT_SHA256,
            root / "experiments/train-audit-20260927/qualified-v1/train.jsonl")
        self.assertEqual(len(rows), 20)
        self.assertTrue(all(set(row) == train_recall.frozen.FIELDS for row in rows))
        spec, identity = self.specification()
        tree = ast.parse(spec["command"][3])
        scripts = next(ast.literal_eval(node.iter.func.value) for node in ast.walk(tree)
                       if isinstance(node, ast.For) and isinstance(node.iter, ast.Call)
                       and isinstance(node.iter.func, ast.Attribute) and node.iter.func.attr == "items"
                       and isinstance(node.iter.func.value, ast.Dict)
                       and "train_recall.py" in ast.literal_eval(node.iter.func.value))
        self.assertEqual(set(scripts), {"train_recall.py", "dev_assisted.py", "dev_diagnostic.py", "palref_eval.py"})
        for name, entry in scripts.items():
            data = base64.b64decode(entry["content"])
            self.assertEqual(hashlib.sha256(data).hexdigest(), identity["script_hashes"][name])
            self.assertEqual(data, Path(job.__file__).with_name(name).read_bytes())
        self.assertNotIn(path.read_text("utf-8"), spec["command"][3])

    def test_all_40_attempts_and_exact_identity_are_required(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td)
            rows, run, results = self.completed_files(output)
            job.completed_recall(output, rows, INPUT_SHA256)
            for change in ({"attempted_outputs": 39}, {"attempted_outputs": 41}, {"completed_outputs": 39},
                           {"recorded_outputs": 39}, {"active_output_id": "RECALL-019:evaluation"},
                           {"status": "incomplete"}, {"completed_cases": 19}, {"inputs_sha256": "0" * 64}):
                with self.subTest(change=change):
                    (output / "run.json").write_text(json.dumps({**run, **change}))
                    with self.assertRaisesRegex(ValueError, "40 distinct first attempts"):
                        job.completed_recall(output, rows, INPUT_SHA256)
            (output / "run.json").write_text(json.dumps(run))
            for altered in (results[:-1], results + results[:1], [results[0]] * 40):
                (output / "predictions.jsonl").write_text("".join(json.dumps(row) + "\n" for row in altered))
                with self.assertRaisesRegex(ValueError, "40 distinct first attempts"):
                    job.completed_recall(output, rows, INPUT_SHA256)
            results[0]["status"] = "error"
            (output / "predictions.jsonl").write_text("".join(json.dumps(row) + "\n" for row in results))
            with self.assertRaisesRegex(ValueError, "identity/status mismatch"):
                job.completed_recall(output, rows, INPUT_SHA256)

    def test_server_rejects_nonempty_prefix_without_touching_prior_results(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "output"
            job.fresh_output(output)
            old = output / "manifest.json"
            old.write_bytes(b"previous result")
            with self.assertRaisesRegex(ValueError, "never reuse"):
                job.fresh_output(output)
            self.assertEqual(old.read_bytes(), b"previous result")

    def test_generated_failure_path_exports_partial_and_reraises_without_retry(self):
        spec, _ = self.specification()
        tree = ast.parse(spec["command"][3])
        # Execute the actual generated lifecycle in memory with inert server boundaries.
        body = ast.Module(body=[node for node in tree.body if not isinstance(node, (ast.Import, ast.ImportFrom))
            and (not isinstance(node, ast.FunctionDef) or node.name == "interrupted")], type_ignores=[])
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            stage = root / "stage"
            stage.mkdir()
            inputs = root / "inputs"
            inputs.mkdir()
            output = root / "output"
            calls, alarms = [], []
            def recall(settings, stage, deadline, evidence):
                calls.append("recall")
                target = evidence / "recall"
                target.mkdir()
                (target / "predictions.jsonl").write_text('{"status":"error"}\n')
                raise RuntimeError("first attempt failed")
            def extract(path, destination, expected, limit):
                calls.append("extract")
                destination.mkdir()
            def mapped_path(value):
                return {"/input": inputs, "/output": output}.get(str(value), Path(value))
            namespace = dict(base64=base64, hashlib=hashlib, json=json, Path=mapped_path,
                time=SimpleNamespace(monotonic=lambda: 100, sleep=lambda seconds: calls.append(("sleep", seconds))),
                signal=SimpleNamespace(SIGTERM=15, SIGALRM=14, signal=lambda *a: None, alarm=alarms.append),
                tempfile=SimpleNamespace(mkdtemp=lambda **kwargs: str(stage)), fresh_output=job.fresh_output,
                file_sha256=lambda path: INPUT_SHA256 if path.name == INPUT_NAME else hf_preflight.specification("cuda")[1][path.name],
                safe_extract=extract, recall_body=recall, emit=lambda *a, **k: None, exec=lambda *a: calls.append("bootstrap"))
            def publish(source, target, deadline, identity):
                self.assertEqual(identity["recall_status"], "incomplete")
                self.assertFalse(identity["evaluation_complete"])
                self.assertEqual((source / "recall/predictions.jsonl").read_text(), '{"status":"error"}\n')
                self.assertEqual(json.loads((source / "recall-status.json").read_text())["error_type"], "RuntimeError")
                calls.append("publish")
                return {}
            namespace["publish"] = publish
            with patch("shutil.disk_usage", return_value=SimpleNamespace(free=100 * 1024**3)):
                with self.assertRaisesRegex(RuntimeError, "first attempt failed"):
                    exec(compile(body, "generated-lifecycle", "exec"), namespace)
            self.assertEqual(calls.count("recall"), 1)
            self.assertEqual(calls.count("publish"), 1)
            self.assertIn(("sleep", 180), calls)
            self.assertEqual(alarms, [1440, 1620, 0])

    def test_bad_manifest_blocks_before_server_base_fetch(self):
        rows = self.rows()
        class Trained:
            def __truediv__(self, name):
                return SimpleNamespace(read_text=lambda encoding: "{}")
        modules = {"bundle": SimpleNamespace(verify=lambda path: None),
                   "runtime": SimpleNamespace(gpu_admission=lambda: {}, offline=lambda: None),
                   "train_recall": SimpleNamespace(read_inputs=lambda *args: rows)}
        _, identity = self.specification()
        with patch.dict("sys.modules", modules), patch("sys.path", []), \
             patch.object(job, "Path", side_effect=lambda value: Trained() if value == "/trained" else Path(value)), \
             patch.object(job, "file_sha256", return_value="0" * 64), patch("subprocess.run") as child:
            with self.assertRaisesRegex(ValueError, "manifest differs"):
                job.recall_body(identity, Path("fixture-stage"), 1000, Path("fixture-evidence"))
            child.assert_not_called()


if __name__ == "__main__":
    unittest.main()
