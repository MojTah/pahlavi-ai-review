"""Offline generated-wrapper and closed-evidence checks; no model or API calls."""
import ast
import base64
import hashlib
import inspect
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid

from . import hf_contextual as job, hf_dev_assisted

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "experiments/dev-diagnostic-20260927/inputs.jsonl"
PACKAGE = ROOT / "experiments/contextual-supervision-20260927/contextual-pilot-bb3795d9a499.zip"


class ContextualJobTests(unittest.TestCase):
    def scratch(self):
        folder = ROOT / "resources/local/hf-contextual-check" / uuid.uuid4().hex
        folder.mkdir(parents=True)
        return folder

    def specification(self):
        return job.specification("c" * 32)

    def decoded(self, spec, settings):
        compiled = []
        namespace = {"exec": compiled.append}
        exec(spec["command"][3], namespace)
        self.assertEqual(len(compiled), 1)
        self.assertEqual(compiled[0].co_filename, "hf-contextual")
        data = namespace["_contextual_code"]
        self.assertEqual(hashlib.sha256(data).hexdigest(), settings["decoded_command_sha256"])
        return data.decode("utf-8")

    def rows(self):
        return [json.loads(s) for s in INPUT.read_text("utf-8").splitlines()]

    def settings(self):
        settings = self.specification()[1]
        settings["evaluation_schedule"] = [(row["id"], "control" if condition == "plain" else "candidate")
            for row, condition in hf_dev_assisted.dev_assisted.schedule(self.rows())]
        return settings

    def completed_files(self, folder, settings):
        (folder / "training").mkdir(parents=True)
        (folder / "evaluation").mkdir()
        (folder / "run.json").write_text(json.dumps(dict(status="completed",
            package_manifest_sha256=settings["package_manifest_sha256"],
            runner_sha256=settings["script_hashes"]["contextual_run.py"],
            original_adapter_manifest_sha256=settings["trained_manifest_sha256"])), encoding="utf-8")
        training = {"status": "completed", "arms": {arm: dict(status="completed", completed_steps=48,
            consumed_slots=768, parent_order_verified=True) for arm in ("control", "candidate")}}
        (folder / "training/run.json").write_text(json.dumps(training), encoding="utf-8")
        for arm in training["arms"]:
            adapter = folder / "training" / arm / "adapter"
            adapter.mkdir(parents=True)
            (adapter / "adapter_config.json").write_text("{}", encoding="utf-8")
            (adapter / "adapter_model.safetensors").write_bytes(b"closed adapter fixture")
        ids = [case + ":" + arm for case, arm in settings["evaluation_schedule"]]
        run = dict(status="completed", scheduled_outputs=48, attempted_outputs=48, recorded_outputs=48,
                   completed_outputs=48, completed_cases=24, active_output_id=None, unattempted_output_ids=[],
                   schedule=ids, inputs_sha256=settings["inputs_sha256"])
        indexed = {r["id"]: r for r in self.rows()}
        results = [dict(id=ids[i], case_id=case, arm=arm, sequence=i + 1, status="success",
                        record_id=indexed[case]["record_id"], work_id=indexed[case]["work_id"],
                        input_sha256=hashlib.sha256(indexed[case]["source_text"].encode()).hexdigest())
                   for i, (case, arm) in enumerate(settings["evaluation_schedule"])]
        (folder / "evaluation/run.json").write_text(json.dumps(run), encoding="utf-8")
        (folder / "evaluation/predictions.jsonl").write_text("".join(json.dumps(r) + "\n" for r in results), encoding="utf-8")
        return training, run, results

    def test_specification_is_fixed_native_bound_and_never_constructs_client(self):
        with patch("huggingface_hub.HfApi.__init__", side_effect=AssertionError("No client")), \
             patch("huggingface_hub.HfApi.run_job", autospec=True) as submit:
            spec, settings = self.specification()
            submit.assert_not_called()
        from huggingface_hub import HfApi
        inspect.signature(HfApi.run_job).bind(None, **spec)
        compile(spec["command"][3], "generated-contextual", "exec")
        self.assertEqual((spec["flavor"], spec["timeout"]), ("a100-large", "75m"))
        self.assertEqual([settings[k] for k in ("native_timeout_minutes", "compute_seconds", "internal_seconds",
                         "export_reserve_seconds", "maximum_wait_seconds")], [75, 3900, 4200, 300, 300])
        self.assertEqual(settings["max_export_bytes"], 2 * 1024**3)
        self.assertEqual(settings["command_sha256"], hashlib.sha256(spec["command"][3].encode()).hexdigest())
        self.assertEqual([(v.path, v.mount_path, v.read_only) for v in spec["volumes"]],
            [("inputs", "/input", True), (hf_dev_assisted.TRAINED_PREFIX, "/trained", True),
             ("contextual-pilot/" + "c" * 32, "/output", False)])
        self.assertNotIn("secrets", spec)
        self.assertNotIn("evidence", settings)
        self.assertNotIn("audit", settings)
        self.assertEqual((settings["inputs_name"], settings["inputs_sha256"]), hf_dev_assisted.INPUT_FILES["inputs"])
        self.assertEqual(settings["package_sha256"], job.file_sha256(PACKAGE))
        self.assertEqual(settings["package_manifest_sha256"], job.PACKAGE_MANIFEST_SHA256)
        tree = ast.parse(self.decoded(spec, settings))
        scripts = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                       and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "scripts")
        self.assertEqual(set(scripts), {"contextual_run.py", "contextual_train.py", "dev_assisted.py", "dev_diagnostic.py", "palref_eval.py"})
        for name, entry in scripts.items():
            self.assertEqual(base64.b64decode(entry["content"]), Path(job.__file__).with_name(name).read_bytes())
            self.assertEqual(entry["sha256"], settings["script_hashes"][name])

    def test_invalid_run_id_and_changed_package_rejected(self):
        with self.assertRaises(ValueError):
            job.specification("../bad")
        folder = self.scratch() / "package"
        job.safe_extract(PACKAGE, folder, job.PACKAGE_SHA256, 8 * 1024**2)
        job.verify_package(folder, job.PACKAGE_MANIFEST_SHA256)
        (folder / "extra.txt").write_text("drift")
        with self.assertRaisesRegex(ValueError, "inventory"):
            job.verify_package(folder, job.PACKAGE_MANIFEST_SHA256)

    def test_completion_rejects_partial_retry_duplicate_or_wrong_identity(self):
        folder, settings = self.scratch() / "contextual", self.settings()
        training, run, results = self.completed_files(folder, settings)
        job.completed_contextual(folder, self.rows(), settings)
        for change in ({"attempted_outputs": 49}, {"completed_outputs": 47}, {"active_output_id": results[0]["id"]},
                       {"inputs_sha256": "0" * 64}, {"unattempted_output_ids": [results[0]["id"]]}):
            (folder / "evaluation/run.json").write_text(json.dumps({**run, **change}))
            with self.assertRaises(ValueError): job.completed_contextual(folder, self.rows(), settings)
        (folder / "evaluation/run.json").write_text(json.dumps(run))
        for change in ({"completed_steps": 47}, {"completed_steps": True}, {"consumed_slots": 767}, {"parent_order_verified": False}):
            changed = json.loads(json.dumps(training))
            changed["arms"]["candidate"].update(change)
            (folder / "training/run.json").write_text(json.dumps(changed))
            with self.assertRaises(ValueError): job.completed_contextual(folder, self.rows(), settings)
        (folder / "training/run.json").write_text(json.dumps(training))
        for altered in (results[:-1], results + results[:1], [results[0]] * 48,
                        [{**results[0], "arm": "candidate" if results[0]["arm"] == "control" else "control"}, *results[1:]],
                        [{**results[0], "status": "error"}, *results[1:]]):
            (folder / "evaluation/predictions.jsonl").write_text("".join(json.dumps(r) + "\n" for r in altered))
            with self.assertRaises(ValueError): job.completed_contextual(folder, self.rows(), settings)

    def lifecycle(self, mode):
        spec, settings = self.specification()
        tree = ast.parse(self.decoded(spec, settings))
        namespace = {}
        exec(compile(ast.Module(body=tree.body[:-1], type_ignores=[]), "generated-definitions", "exec"), namespace)
        root = self.scratch()
        inputs, output, stage = root / "input", root / "output", root / "stage"
        inputs.mkdir(); stage.mkdir()
        shutil.copyfile(INPUT, inputs / settings["inputs_name"])
        shutil.copyfile(PACKAGE, inputs / settings["package_name"])
        shutil.copyfile(ROOT / "resources/local/cloud-pilot-qualified-20260927.zip", inputs / settings["bundle_name"])
        if mode == "package":
            with (inputs / settings["package_name"]).open("ab") as f: f.write(b"drift")
        calls, alarms = [], []
        def mapped_path(value):
            return {"/input": inputs, "/output": output}.get(str(value), Path(value))
        def bootstrap(source):
            calls.append("bootstrap")
            if mode == "bootstrap": raise RuntimeError("bootstrap fixture")
        def body(settings, stage, deadline, evidence):
            calls.append("body")
            if mode in {"driver", "driver_timeout", "driver_exit"}:
                folder = evidence / "contextual/training/control/adapter"
                folder.mkdir(parents=True)
                (folder / "adapter_model.safetensors").write_bytes(b"completed control retained")
                (evidence / "contextual/training/run.json").write_text('{"status":"incomplete","arms":{"control":{"status":"completed"}}}')
                (evidence / "unfinished.tmp").write_text("not closed")
                if mode != "driver":
                    code = ("import time; print('visible progress', flush=True); time.sleep(30)" if mode == "driver_timeout"
                            else "import sys; print('visible failure', flush=True); sys.exit(7)")
                    with patch("sys.stdout", SimpleNamespace(buffer=io.BytesIO())):
                        namespace["run_logged"]([sys.executable, "-u", "-c", code], evidence / "driver.log", 0.5)
                raise RuntimeError("candidate subprocess failed")
            settings.update(self.settings())
            self.completed_files(evidence / "contextual", settings)
            namespace["completed_contextual"](evidence / "contextual", self.rows(), settings)
        namespace.update(Path=mapped_path, exec=bootstrap, contextual_body=body,
            time=SimpleNamespace(monotonic=lambda: 100, sleep=lambda n: calls.append(("sleep", n))),
            signal=SimpleNamespace(SIGTERM=15, SIGALRM=14, signal=lambda *a: None, alarm=alarms.append),
            tempfile=SimpleNamespace(mkdtemp=lambda **kw: str(stage)), emit=lambda *a, **kw: None)
        with patch("shutil.disk_usage", return_value=SimpleNamespace(free=100 * 1024**3)):
            invoke = compile(ast.Module(body=[tree.body[-1]], type_ignores=[]), "generated-invocation", "exec")
            if mode == "success": exec(invoke, namespace)
            else:
                with self.assertRaises((ValueError, RuntimeError, subprocess.SubprocessError)): exec(invoke, namespace)
        manifest = json.loads((output / "manifest.json").read_text())
        self.assertEqual(manifest["contextual_status"], "complete" if mode == "success" else "incomplete")
        self.assertEqual(manifest["evaluation_complete"], mode == "success")
        self.assertFalse(manifest["quality_validated"])
        self.assertFalse(manifest["remote_inventory_verified"])
        self.assertIsNone(manifest["latest_optimizer_checkpoint"])
        self.assertNotIn("canary_compute_pass", manifest)
        self.assertEqual(alarms, [3900, 4200, 0])
        self.assertIn(("sleep", 300), calls)
        self.assertLessEqual(calls.count("body"), 1)
        for name, entry in manifest["files"].items():
            self.assertEqual(job.file_sha256(output / name), entry["sha256"])
            self.assertFalse(name.startswith("base/"))
            self.assertNotIn("checkpoint-", name)
        if mode in {"driver", "driver_timeout", "driver_exit"}:
            self.assertEqual((output / "contextual/training/control/adapter/adapter_model.safetensors").read_bytes(), b"completed control retained")
            self.assertNotIn("unfinished.tmp", manifest["files"])
            if mode != "driver":
                self.assertIn("visible", (output / "driver.log").read_text())
                self.assertIn(manifest["error_type"], {"TimeoutExpired", "CalledProcessError"})
        if mode == "package": self.assertNotIn("bootstrap", calls)
        with self.assertRaises(ValueError): namespace["fresh_output"](output)

    def test_generated_success_and_partial_failure_export(self):
        for mode in ("success", "driver", "driver_timeout", "driver_exit", "bootstrap", "package"):
            with self.subTest(mode=mode): self.lifecycle(mode)

    def test_child_progress_reaches_stdout_and_log_before_child_finishes(self):
        root = self.scratch()
        release = root / "release"
        class VisibleOutput(io.BytesIO):
            def write(self, data):
                if b"first progress" in data:
                    release.write_text("visible before exit")
                return super().write(data)
        visible = VisibleOutput()
        code = ("import pathlib,sys,time; print('first progress',flush=True); "
                "p=pathlib.Path(sys.argv[1]); deadline=time.monotonic()+10\n"
                "while not p.exists() and time.monotonic()<deadline: time.sleep(.01)\n"
                "assert p.exists(); print('last progress',flush=True)")
        with patch("sys.stdout", SimpleNamespace(buffer=visible)):
            job.run_logged([sys.executable, "-u", "-c", code, str(release)], root / "driver.log", 3)
        self.assertEqual((root / "driver.log").read_bytes(), visible.getvalue())
        self.assertIn(b"last progress", visible.getvalue())

    def test_child_timeout_and_interruption_kill_and_reap_without_retry(self):
        for interrupted in (False, True):
            with self.subTest(interrupted=interrupted):
                root, children = self.scratch(), []
                original = subprocess.Popen
                def spawn(*args, **kwargs):
                    child = original(*args, **kwargs)
                    children.append(child)
                    if interrupted:
                        original_wait = child.wait
                        calls = []
                        def wait(timeout=None):
                            calls.append(timeout)
                            if len(calls) == 1: raise KeyboardInterrupt("fixture interruption")
                            return original_wait(timeout=timeout)
                        child.wait = wait
                    return child
                started = time.monotonic()
                with patch("subprocess.Popen", side_effect=spawn), patch("sys.stdout", SimpleNamespace(buffer=io.BytesIO())):
                    with self.assertRaises(KeyboardInterrupt if interrupted else subprocess.TimeoutExpired):
                        job.run_logged([sys.executable, "-u", "-c", "import time; print('started',flush=True); time.sleep(30)"], root / "driver.log", .5)
                self.assertEqual(len(children), 1)
                self.assertIsNotNone(children[0].poll())
                self.assertTrue(children[0].stdout.closed)
                self.assertLess(time.monotonic() - started, 8)

    def test_export_bound_is_enforced_without_copying_base(self):
        root = self.scratch()
        source, output = root / "evidence", root / "output"
        source.mkdir(); output.mkdir()
        (source / "closed.json").write_bytes(b"12345")
        with self.assertRaisesRegex(ValueError, "export bound"):
            job.export_evidence(source, output, job.time.monotonic() + 30, {"max_export_bytes": 4})

    def test_compressed_transport_preserves_exact_prior_program_and_all_other_argv(self):
        spec, identity = self.specification()
        decoded = self.decoded(spec, identity)
        # Recorded from the unchanged c*32 specification before this transport repair.
        self.assertEqual(hashlib.sha256(decoded.encode("utf-8")).hexdigest(),
                         "ce2c38bb92f574f4065dc00ec91a19f9ceeb263814a284def9f92f83a33869af")
        self.assertEqual(len(decoded.encode("utf-8")), 133680)
        original, _ = job.hf_preflight.specification("cuda")
        self.assertEqual(spec["command"][:3], original["command"][:3])
        self.assertEqual(spec["command"][4:], original["command"][4:])
        lengths, total = job.command_lengths(spec["command"])
        self.assertEqual(lengths, identity["command_arg_utf8_bytes"])
        self.assertEqual(total, identity["command_total_utf8_bytes_with_nul"])
        self.assertLess(max(lengths), 100 * 1024)
        self.assertLess(total, 1024**2)
        self.assertEqual(job.compressed_command(decoded), spec["command"][3])
        with self.assertRaisesRegex(ValueError, "checksum"):
            exec(spec["command"][3].replace(identity["decoded_command_sha256"], "0" * 64), {})
        for command in (["x" * (100 * 1024)], ["x" * (99 * 1024)] * 11):
            with self.assertRaisesRegex(ValueError, "argument or 1 MiB"):
                job.command_lengths(command)

    def test_compressed_launcher_executes_in_real_python_with_unchanged_argv(self):
        source = "import sys,json; print(json.dumps({'argv':sys.argv,'marker':'unchanged program'}))\n"
        code = job.compressed_command(source)
        observed = subprocess.run([sys.executable, "-u", "-c", code, "original-bootstrap-argument", "cuda"],
                                  capture_output=True, check=True, text=True, timeout=5)
        self.assertEqual(json.loads(observed.stdout),
                         {"argv": ["-c", "original-bootstrap-argument", "cuda"], "marker": "unchanged program"})


if __name__ == "__main__":
    unittest.main()
