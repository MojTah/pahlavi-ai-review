"""Offline input, response and real subprocess deadline checks; no model weights."""
import json
from pathlib import Path
import subprocess
import sys
import time
import unittest
from unittest.mock import patch
import urllib.request

try:
    from . import local_eval as runner
except ImportError:
    import local_eval as runner


class LocalEvaluationTests(unittest.TestCase):
    def test_inputs_require_unique_ids_valid_tokens_and_explicit_probe(self):
        row = {"id": "a", "prompt": "source", "rendered_prompt": "<bos>source", "token_ids": [2, 17],
               "text": "source", "record_id": "technical:1", "work_id": "technical", "source_language": "pal", "target_language": "fa"}
        with patch.object(runner.Path, "read_text", return_value=json.dumps(row) + "\n") as read:
            self.assertEqual(runner.read_inputs("unused", 32), [row])
            with self.assertRaises(ValueError):
                runner.read_inputs("unused", 1024)
            for invalid in ([2, True], [], [2] * 4097, [2, -1]):
                read.return_value = json.dumps(dict(row, token_ids=invalid)) + "\n"
                with self.assertRaises(ValueError):
                    runner.read_inputs("unused", 32)
            read.return_value = "\n".join(json.dumps(dict(row, id=str(i))) for i in range(30))
            self.assertEqual(len(runner.read_inputs("unused", 1024)), 30)
            read.return_value = "\n".join(json.dumps(row) for _ in range(30))
            with self.assertRaises(ValueError):
                runner.read_inputs("unused", 1024)

    def test_exact_frozen_export_and_rejected_reference_or_source_changes(self):
        path = Path(__file__).resolve().parents[1] / "experiments/staged-dev-20260926/inputs-only.jsonl"
        exported = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        actual = runner.read_inputs(path, 1024)
        self.assertEqual(len(actual), 30)
        self.assertEqual(actual, exported)  # Preserve every source identity and provenance field.
        for change in ({"reference": "answer"}, {"metadata": {}}, {"source_language": "en"},
                       {"target_language": "en"}, {"record_id": ""}, {"work_id": ""}, {"text": "not in the frozen prompt"}):
            with self.subTest(change=change), patch.object(runner.Path, "read_text", return_value=json.dumps(dict(exported[0], **change))), self.assertRaises(ValueError):
                runner.read_inputs("unused", 32)

    def test_response_cap_eos_and_incomplete_fail_closed(self):
        good = {"tokens": [17, 106], "truncated": False, "stop_type": "eos"}
        runner.validate_response(good, 32)
        runner.validate_response(dict(good, tokens=[17] * 32, stop_type="limit"), 32)
        for update in ({"tokens": [17] * 33}, {"tokens": []}, {"tokens": [17, True]},
                       {"tokens": [106, 17, 106]}, {"tokens": [17, 7]}, {"stop_type": "none"},
                       {"truncated": True}, {"stop_type": "limit"}):
            with self.subTest(update=update), self.assertRaises(ValueError):
                runner.validate_response(dict(good, **update), 32)

    def test_watchdog_terminates_only_owned_child_and_confirms_exit(self):
        script = ("from http.server import HTTPServer, BaseHTTPRequestHandler\nimport time\n"
                  "class Handler(BaseHTTPRequestHandler):\n def do_GET(self): time.sleep(20)\n"
                  "server = HTTPServer(('127.0.0.1', 0), Handler)\n"
                  "print(server.server_port, flush=True)\nserver.serve_forever()\n")
        child = subprocess.Popen([sys.executable, "-u", "-c", script], stdout=subprocess.PIPE,
                                 creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        try:
            port = int(child.stdout.readline())
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            def stalled_request():
                with opener.open(f"http://127.0.0.1:{port}/", timeout=2) as response:
                    return response.read()
            with self.assertRaisesRegex(TimeoutError, "exit confirmed"):
                runner.bounded(child, 0.1, stalled_request)
            self.assertIsNotNone(child.poll())
            runner.stop_server(child)  # Already terminated cleanup is safe.
        finally:
            runner.stop_server(child)
            child.stdout.close()

    def test_success_cancels_watchdog_and_exceptions_propagate(self):
        child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(20)"],
                                 creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        try:
            self.assertEqual(runner.bounded(child, 0.08, lambda: 7), 7)
            time.sleep(0.12)
            self.assertIsNone(child.poll())
            with self.assertRaisesRegex(ValueError, "failed response"):
                runner.bounded(child, 1, lambda: (_ for _ in ()).throw(ValueError("failed response")))
        finally:
            runner.stop_server(child)


if __name__ == "__main__":
    unittest.main()
