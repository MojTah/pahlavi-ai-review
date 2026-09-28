import importlib.util
from pathlib import Path
import unittest
import json
from hashlib import sha256
import shutil
import uuid

spec = importlib.util.spec_from_file_location("prepare_language_dev", Path(__file__).resolve().parents[1] / "scripts/prepare_language_dev.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
run_spec = importlib.util.spec_from_file_location("run_language_dev", Path(__file__).resolve().parents[1] / "scripts/run_language_dev_qwen.py")
runner = importlib.util.module_from_spec(run_spec)
run_spec.loader.exec_module(runner)


class SelectionTest(unittest.TestCase):
    def test_paired_selection_is_deterministic_bounded_and_excludes_known_exposure(self):
        rows = [{"id": f"r{i}", "work_id": "work", "status": "reviewed", "alignment": "verified",
                 "transcription": "x " * (i + 1), "translations": {
                     l: {"published": True, "role": "translation", "credit": "Fixture", "text": l}
                     for l in ("en", "fa")}} for i in range(18)]
        held = rows[0] | {"id": "held", "work_id": "parsig:104"}
        missing = rows[0] | {"id": "missing", "translations": {}}
        selected, candidates = module.select([*rows, held, missing], {"r3"})
        again, _ = module.select(list(reversed([*rows, held, missing])), {"r3"})
        self.assertEqual(selected, again)
        self.assertEqual(len(selected), 6)
        self.assertEqual(len(candidates), 17)
        self.assertFalse({"r3", "held", "missing"} & {r["id"] for r in selected})

    def test_runner_uses_paired_source_only_inputs_and_rejects_injected_answers(self):
        root = Path(__file__).resolve().parents[1]
        rows = runner.inputs(root / "experiments/language-choice-dev-v1")
        self.assertEqual(len(rows), 12)
        self.assertEqual([r["id"].split(":")[0] for r in rows[:4]], ["PALDEV1-001"] * 2 + ["PALDEV1-006"] * 2)
        parent = (root / "tmp").resolve()
        packet = parent / ("devtest-" + uuid.uuid4().hex)
        packet.mkdir(parents=True)
        try:
            rows[0]["target"] = "An answer must never be an input field"
            data = "".join(json.dumps(r) + "\n" for r in rows).encode()
            (packet / "inputs.jsonl").write_bytes(data)
            (packet / "audit.json").write_text(json.dumps({"files": {"inputs.jsonl": sha256(data).hexdigest()}}), "utf-8")
            with self.assertRaisesRegex(ValueError, "approved source fields"):
                runner.inputs(packet)
            rows[0].pop("target")
            rows[0]["text"] += " mismatch"
            data = "".join(json.dumps(r) + "\n" for r in rows).encode()
            (packet / "inputs.jsonl").write_bytes(data)
            with self.assertRaisesRegex(ValueError, "checksum"):
                runner.inputs(packet)
            (packet / "audit.json").write_text(json.dumps({"files": {"inputs.jsonl": sha256(data).hexdigest()}}), "utf-8")
            with self.assertRaisesRegex(ValueError, "identical six"):
                runner.inputs(packet)
        finally:
            if packet.resolve().parent != parent:
                raise ValueError("Unsafe temporary path")
            shutil.rmtree(packet)


if __name__ == "__main__":
    unittest.main()
