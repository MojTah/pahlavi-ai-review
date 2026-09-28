"""Offline protocol, identity and mocked generation checks; no model or cloud access."""
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

try:
    from . import palref_eval as runner
except ImportError:
    import palref_eval as runner


class PalrefTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent
        self.inputs = self.root / "resources/local/palref-v1-pal-fa-inputs.jsonl"
        self.data = self.inputs.read_bytes()
        self.rows = runner.read_inputs(self.inputs)

    def test_exact_existing_protocol_and_projection(self):
        path = self.root / "benchmarks/pal-reference-v1/benchmark.py"
        spec = importlib.util.spec_from_file_location("frozen_palref", path)
        benchmark = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(benchmark)
        frozen, cases = benchmark.verify()
        self.assertEqual(frozen, runner.BENCHMARK_SHA256)
        self.assertEqual(benchmark.digest((path.parent / "inputs.jsonl").read_bytes()), runner.ORIGINAL_INPUTS_SHA256)
        self.assertEqual(self.rows, [row for row in cases.values() if (row["source_language"], row["target_language"]) == ("pal", "fa")])
        self.assertEqual(runner.PROMPT, benchmark.PROMPT)
        self.assertEqual(runner.SYSTEM, benchmark.PROMPT.format(source_language=benchmark.LANGS["pal"], target_language=benchmark.LANGS["fa"]))
        self.assertEqual((runner.MAX_TOKENS, runner.CASE_SECONDS), (4096, 1200))
        self.assertEqual(len(self.rows), 40)

    def test_model_messages_contain_only_instruction_and_one_original_source(self):
        for row in self.rows:
            self.assertEqual(set(row), runner.FIELDS)
            self.assertEqual(runner.messages(row), [
                {"role": "system", "content": runner.SYSTEM}, {"role": "user", "content": row["source_text"]}])

    def test_byte_tampering_rejected_before_bundle_or_gpu(self):
        with patch.object(Path, "read_bytes", return_value=self.data + b"\n"), \
                patch.object(runner.runtime, "verified_bundle") as bundle, \
                patch.object(runner.runtime, "gpu_admission") as gpu:
            with self.assertRaisesRegex(ValueError, "Input bytes differ"):
                runner.evaluate(SimpleNamespace(inputs=self.inputs, deadline_utc="2999-01-01T00:00:00Z"))
            bundle.assert_not_called()
            gpu.assert_not_called()

    def test_schema_ids_and_direction_are_independently_checked(self):
        altered = []
        rows = copy.deepcopy(self.rows); rows[0]["reference"] = "answer"; altered.append(rows)
        rows = copy.deepcopy(self.rows); rows[0]["id"] = rows[1]["id"]; altered.append(rows)
        rows = copy.deepcopy(self.rows); rows[0]["target_language"] = "en"; altered.append(rows)
        rows = copy.deepcopy(self.rows); rows[0]["source_text"] = ""; altered.append(rows)
        altered.append(self.rows[:-1])
        for rows in altered:
            data = ("\n".join(json.dumps(row) for row in rows) + "\n").encode()
            with self.subTest(rows=len(rows)), patch.object(Path, "read_bytes", return_value=data), \
                    patch.object(runner, "INPUTS_SHA256", hashlib.sha256(data).hexdigest()):
                with self.assertRaises(ValueError):
                    runner.read_inputs(self.inputs)

    def test_prediction_schema_status_and_original_source_hash(self):
        for text, elapsed, timeout, cap, expected in [
                ("translation", 1, False, False, "success"), ("[UNRESOLVED]", 1, False, False, "abstain"),
                ("partial", 1201, False, False, "timeout"), ("partial", 1, True, False, "timeout"),
                ("partial", 1, False, True, "error"), ("", 1, False, False, "error")]:
            pred = runner.prediction(self.rows[0], text, elapsed, timeout, cap)
            self.assertEqual(set(pred), {"id", "input_sha256", "status", "text", "elapsed_seconds"})
            self.assertEqual(pred["status"], expected)
            self.assertEqual(pred["input_sha256"], hashlib.sha256(self.rows[0]["source_text"].encode()).hexdigest())

    def test_deadline_stopper_is_case_local_and_honors_global_deadline(self):
        future = datetime(2999, 1, 1, tzinfo=timezone.utc)
        stop = runner.GenerationDeadline(100, future)
        with patch.object(runner.time, "monotonic", return_value=1299):
            self.assertFalse(stop(None, None))
        with patch.object(runner.time, "monotonic", return_value=1300):
            self.assertTrue(stop(None, None))
        self.assertEqual(stop.reason, "case_timeout")
        other = runner.GenerationDeadline(100, datetime(2000, 1, 1, tzinfo=timezone.utc))
        self.assertTrue(other(None, None))
        self.assertEqual(other.reason, "global_deadline")

    def test_mocked_whole_run_preserves_standard_generation_and_fresh_cache(self):
        class Stream(io.StringIO):
            def __exit__(self, *args):
                self.flush()
        class Generated:
            def __getitem__(self, index):
                return SimpleNamespace(tolist=lambda: [42, 106])
        stream = Stream()
        model = Mock()
        model.generate.return_value = Generated()
        tokenizer = Mock()
        tokenizer.apply_chat_template.return_value = [2, 3]
        tokenizer.decode.return_value = "translation"
        caches = []
        def cache():
            value = object(); caches.append(value); return value
        transformer = SimpleNamespace(AutoTokenizer=SimpleNamespace(from_pretrained=Mock(return_value=tokenizer)),
            DynamicCache=cache, Gemma4ForConditionalGeneration=SimpleNamespace(from_pretrained=Mock(return_value=model)),
            StoppingCriteriaList=list, set_seed=Mock())
        torch = SimpleNamespace(tensor=lambda values, **kw: values, ones_like=lambda values: values,
                                bfloat16="bf16", inference_mode=lambda: patch.dict({}, {}))
        files = {name: "a" * 64 for name in ("tokenizer.json", "tokenizer_config.json", "chat_template.jinja")}
        bundle = self.root / "mock-bundle"
        saved = []
        real_open = Path.open
        args = SimpleNamespace(inputs=self.inputs, bundle=bundle, base="mock-base", tokenizer="mock-tokenizer",
                               output=self.root / "unused-palref-output", adapter=None, deadline_utc="2999-01-01T00:00:00Z")
        with patch.dict("sys.modules", {"torch": torch, "transformers": transformer, "peft": SimpleNamespace(PeftModel=Mock())}), \
                patch.object(runner.runtime, "verified_bundle", return_value=bundle), \
                patch.object(runner.runtime, "contract_at", return_value={"model": {}}), \
                patch.object(runner.runtime, "verify_base", return_value={"files": files}), \
                patch.object(runner.runtime, "checked_files"), patch.object(runner.runtime, "gpu_admission", return_value={}), \
                patch.object(runner.runtime, "read_json", return_value={"text_config": {"max_position_embeddings": 8192}}), \
                patch.object(runner.runtime, "write_json", side_effect=lambda path, value: saved.append(copy.deepcopy(value))), \
                patch.object(runner.runtime, "digest", return_value="b" * 64), \
                patch.object(Path, "exists", return_value=False), patch.object(Path, "mkdir"), \
                patch.object(Path, "open", autospec=True, side_effect=lambda path, *a, **kw: stream if a and a[0] == "x" else real_open(path, *a, **kw)), patch("builtins.print"):
            runner.evaluate(args)
        predictions = [json.loads(line) for line in stream.getvalue().splitlines()]
        self.assertEqual([row["id"] for row in predictions], runner.IDS)
        self.assertTrue(all(row["status"] == "success" for row in predictions))
        self.assertEqual(len({id(value) for value in caches}), 40)
        transformer.set_seed.assert_called_once_with(42)
        self.assertEqual(saved[-1]["status"], "completed")
        self.assertEqual(saved[-1]["completed_cases"], 40)
        for call, row in zip(tokenizer.apply_chat_template.call_args_list, self.rows):
            self.assertEqual(call.args[0], runner.messages(row))
            self.assertFalse(call.kwargs["enable_thinking"])
        for call in model.generate.call_args_list:
            self.assertFalse(call.kwargs["do_sample"])
            self.assertEqual(call.kwargs["max_new_tokens"], 4096)
            self.assertEqual(call.kwargs["num_beams"], 1)
            self.assertEqual(call.kwargs["eos_token_id"], [1, 106, 50])
            self.assertEqual(len(call.kwargs["stopping_criteria"]), 1)


if __name__ == "__main__":
    unittest.main()
