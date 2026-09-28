"""Protocol and first-attempt checks with mocks, never local model inference."""
import importlib.util
import io
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

try:
    from . import palref_local_eval as runner
except ImportError:
    import palref_local_eval as runner


class LocalPalrefTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent
        self.inputs = self.root / "resources/local/palref-v1-pal-fa-inputs.jsonl"
        self.rows = runner.protocol.read_inputs(self.inputs)
        self.tokenizer = Mock(bos_token_id=2)
        self.tokenizer.apply_chat_template.side_effect = lambda messages, tokenize, **kw: [2, 12, 13] if tokenize else "rendered"
        self.tokenizer.encode.return_value = [2, 12, 13]
        self.tokenizer.decode.return_value = "mock translation, not a model output"

    def test_official_messages_used_and_all_server_token_ids_checked(self):
        prepared = runner.prepare_inputs(self.tokenizer, self.rows)
        calls = self.tokenizer.apply_chat_template.call_args_list
        self.assertEqual(len(calls), 80)
        for pair, row in zip(zip(calls[::2], calls[1::2]), self.rows):
            for call in pair:
                self.assertEqual(call.args[0], runner.protocol.messages(row))
                self.assertFalse(call.kwargs["enable_thinking"])
                self.assertTrue(call.kwargs["add_generation_prompt"])
        request = Mock(return_value={"tokens": [2, 12, 13]})
        runner.verify_server_tokens(request, prepared)
        self.assertEqual(request.call_count, 40)
        for call in request.call_args_list:
            self.assertEqual(call.args, ("/tokenize", {"content": "rendered", "add_special": False, "parse_special": True}))

    def test_tokenizer_or_server_parity_failure_rejected(self):
        self.tokenizer.encode.return_value = [2, 99]
        with self.assertRaisesRegex(ValueError, "Official chat-template"):
            runner.prepare_inputs(self.tokenizer, self.rows)
        self.tokenizer.encode.return_value = [2, 12, 13]
        prepared = runner.prepare_inputs(self.tokenizer, self.rows)
        request = Mock(return_value={"tokens": [2, 99]})
        with self.assertRaisesRegex(ValueError, "llama.cpp tokenizer"):
            runner.verify_server_tokens(request, prepared)
        request.assert_called_once()

    def test_tampered_inputs_rejected_before_process_or_file_hash(self):
        with patch.object(Path, "read_bytes", return_value=self.inputs.read_bytes() + b"\n"), \
                patch.object(runner.subprocess, "Popen") as launch, patch.object(runner.local, "file_hash") as hashing:
            with self.assertRaisesRegex(ValueError, "Input bytes differ"):
                runner.run(SimpleNamespace(inputs=self.inputs))
            launch.assert_not_called()
            hashing.assert_not_called()

    def test_source_identity_tokenizer_and_artifact_gates_precede_server_launch(self):
        args = SimpleNamespace(**{name: self.inputs for name in
            ("inputs", "server", "model", "adapter", "adapter_source", "tokenizer")},
            output=self.root / "unused-local-palref-output", model_sha256=runner.MODEL_SHA256, adapter_sha256="a" * 64)
        good_model = {"model": {"id": runner.protocol.runtime.MODEL_ID, "revision": runner.protocol.runtime.REVISION}}
        good_config = {"peft_type": "LORA", "r": 16, "lora_alpha": 32}
        for failure in ("identity", "config", "tokenizer", "artifact"):
            with self.subTest(failure=failure), patch.object(runner.subprocess, "Popen") as launch, \
                    patch.object(runner.subprocess, "run") as version, \
                    patch.object(runner.protocol.runtime, "read_json", side_effect=[
                        {"model": {}} if failure == "identity" else good_model,
                        {} if failure == "config" else good_config]), \
                    patch.object(runner.protocol.runtime, "checked_files", side_effect=ValueError("tokenizer mismatch") if failure == "tokenizer" else None), \
                    patch.object(runner.local, "file_hash", return_value="b" * 64):
                with self.assertRaises(ValueError):
                    runner.run(args)
                launch.assert_not_called()
                version.assert_not_called()

    def generate(self, responses, rows=None, bound=None):
        rows = self.rows if rows is None else rows
        prepared = runner.prepare_inputs(self.tokenizer, rows)
        predictions, events = io.StringIO(), io.StringIO()
        request = Mock(side_effect=responses)
        metadata = {"completed_cases": 0}
        def write(stream, value):
            stream.write(json.dumps(value) + "\n")
            stream.flush()
        def bounded(process, seconds, action):
            self.assertEqual(seconds, 1200)
            return action()
        with patch.object(runner.local, "write_record", side_effect=write), \
                patch.object(runner.local, "bounded", side_effect=bound or bounded), patch("builtins.print"):
            try:
                runner.generate_cases(Mock(), request, self.tokenizer, prepared, predictions, events, metadata)
                failure = None
            except BaseException as error:
                failure = error
        return [json.loads(s) for s in predictions.getvalue().splitlines()], [json.loads(s) for s in events.getvalue().splitlines()], request, metadata, failure

    def test_mocked_forty_cases_match_standard_prediction_and_decoding_contract(self):
        response = {"tokens": [42, 106], "truncated": False, "stop_type": "eos"}
        predictions, events, request, metadata, error = self.generate([response] * 40)
        self.assertIsNone(error)
        self.assertEqual([p["id"] for p in predictions], runner.protocol.IDS)
        self.assertEqual(metadata["completed_cases"], 40)
        self.assertEqual(request.call_count, 40)
        self.assertEqual(len(events), 40)
        for pred, row, call in zip(predictions, self.rows, request.call_args_list):
            self.assertEqual(pred, runner.protocol.prediction(row, self.tokenizer.decode.return_value, pred["elapsed_seconds"]))
            self.assertEqual(call.args[0], "/completion")
            payload = call.args[1]
            self.assertEqual((payload["seed"], payload["n_predict"], payload["temperature"]), (42, 4096, 0))
            self.assertEqual(payload["prompt"], [2, 12, 13])
            self.assertFalse(payload["cache_prompt"])
            self.assertEqual(payload["stop"], [])
        # The unchanged scorer consumes these predictions with its direction-only
        # wrapper. Mock reviews are test fixtures, never scientific judgments.
        path = self.root / "benchmarks/pal-reference-v1/benchmark.py"
        spec = importlib.util.spec_from_file_location("frozen_palref_local_test", path)
        benchmark = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(benchmark)
        frozen, _ = benchmark.verify()
        run = {"benchmark_manifest_sha256": frozen, "benchmark_id": "pal-reference-v1", "model_id": "fixture",
               "model_revision": "fixture", "adapter_sha256_or_none": "fixture", "runtime": "mocked", "reviewer_id": "test-fixture",
               "reviewer_type": "ai", "review_status": "provisional_single_review", "decoding": "greedy", "seed": 42,
               "max_new_tokens": 4096, "max_generation_seconds": 1200, "retrieval": "none", "fresh_context_each_case": True,
               "system_prompt": runner.protocol.PROMPT}
        reviews = [{"id": p["id"], "output_sha256": benchmark.digest(p["text"].encode()), "judgment": "uncertain",
                    "categories": {name: "uncertain" for name in benchmark.CATEGORIES}, "meaning_checks": ["uncertain", "uncertain"],
                    "reason": "Mock fixture only", "output_span": p["text"]} for p in predictions]
        with patch.object(benchmark, "read_json", return_value=run), \
                patch.object(benchmark, "read_lines", side_effect=lambda p: predictions if p.name == "predictions.jsonl" else reviews), \
                patch.object(benchmark, "DIRECTIONS", ("pal>fa",)), patch.object(Path, "read_bytes", return_value=b"fixture"):
            result = benchmark.score(Path("unused"), frozen, {row["id"]: row for row in self.rows})
        self.assertEqual(result["directions"]["pal>fa"]["total"], 40)
        self.assertEqual(result["directions"]["pal>fa"]["uncertain"], 40)

    def test_first_malformed_response_is_preserved_and_never_retried(self):
        malformed = {"tokens": [42], "truncated": True, "stop_type": "limit"}
        predictions, events, request, metadata, error = self.generate([malformed])
        self.assertIsInstance(error, ValueError)
        self.assertEqual(request.call_count, 1)
        self.assertEqual(len(predictions), 1)
        self.assertEqual(predictions[0]["status"], "error")
        self.assertEqual(events[0]["raw_response"], malformed)
        self.assertEqual(metadata["completed_cases"], 1)

    def test_timeout_is_preserved_and_run_stops_without_retry(self):
        predictions, events, request, _, error = self.generate([], bound=Mock(side_effect=TimeoutError("owned server stopped")))
        self.assertIsInstance(error, TimeoutError)
        request.assert_not_called()
        self.assertEqual(len(predictions), 1)
        self.assertEqual(predictions[0]["status"], "timeout")
        self.assertEqual(events[0]["error_type"], "TimeoutError")


if __name__ == "__main__":
    unittest.main()
