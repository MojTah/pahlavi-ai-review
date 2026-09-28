"""Offline safety checks: python -B -m unittest discover -s cloud_pilot -p test_bundle.py."""
import copy
from contextlib import contextmanager
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch
from uuid import uuid4
import zipfile

import bundle


@contextmanager
def scratch_directory():
    # tempfile's restrictive Windows ACL is incompatible with this local sandbox.
    parent = Path(__file__).resolve().parent
    path = parent / ("tmp-bundle-" + uuid4().hex)
    path.mkdir()
    try:
        yield path
    finally:
        if path.resolve().parent != parent or path.is_symlink():
            raise ValueError("Scratch cleanup escaped its test directory")
        shutil.rmtree(path)


class CharacterTokenizer:
    all_special_tokens = ["<turn|>", "<eos>"]

    def apply_chat_template(self, messages, **options):
        assert options == {"tokenize": False, "add_generation_prompt": True, "enable_thinking": False}
        return "<user>" + messages[0]["content"] + "\n<assistant>\n"

    def __call__(self, text, add_special_tokens):
        assert add_special_tokens is False
        return {"input_ids": [ord(char) for char in text]}

    def decode(self, ids, **options):
        return "".join(chr(value) for value in ids)


def source_row():
    return {"credit": "source citation", "id": "parsig:133000000:pal>fa",
            "record_id": "parsig:133000000", "revision": "fixture", "source_language": "pal",
            "target_language": "fa", "text": "  pad nām ī yazdān  ", "target": "  به نام یزدان  ",
            "work_id": "parsig:133"}


class BundleChecks(unittest.TestCase):
    def test_answer_only_labels_round_trip(self):
        row = bundle.tokenize_row(source_row(), CharacterTokenizer())
        n = row["prompt_tokens"]
        self.assertEqual(row["labels"][:n], [-100] * n)
        answer = CharacterTokenizer().decode(row["labels"][n:])
        self.assertEqual(answer, "به نام یزدان" + bundle.TERMINATOR)
        self.assertEqual(row["text"], "pad nām ī yazdān")
        broken = copy.deepcopy(row)
        broken["labels"][0] = broken["input_ids"][0]
        with self.assertRaisesRegex(ValueError, "masking"):
            bundle.validate_row(broken)
        broken = copy.deepcopy(row)
        broken["labels"][-1] = -100
        with self.assertRaisesRegex(ValueError, "masking"):
            bundle.validate_row(broken)

    def test_token_boundary_change_is_rejected(self):
        class BoundaryTokenizer(CharacterTokenizer):
            def __call__(self, text, add_special_tokens):
                result = super().__call__(text, add_special_tokens)
                if text.endswith(bundle.TERMINATOR):
                    result["input_ids"][0] += 1
                return result
        with self.assertRaisesRegex(ValueError, "boundary"):
            bundle.tokenize_row(source_row(), BoundaryTokenizer())

    def test_control_tokens_and_overlength_are_rejected(self):
        for field in ("text", "target"):
            for control in ("<turn|>", "<|channel>", "<bos>"):
                row = source_row()
                row[field] += control
                with self.assertRaisesRegex(ValueError, "token"):
                    bundle.tokenize_row(row, CharacterTokenizer())
        row = source_row()
        row["target"] = "x" * 2048
        with self.assertRaisesRegex(ValueError, "sequence length"):
            bundle.tokenize_row(row, CharacterTokenizer())

    def test_dev_references_cannot_be_shipped(self):
        dev = [{key: value for key, value in source_row().items() if key in bundle.DEV_KEYS} for _ in range(6)]
        for i, row in enumerate(dev):
            row["id"] = f"PALDEV1-{i}:pal>fa"
            row["prompt"] = bundle.PROMPT.format(text=row["text"])
        bundle.validate_dev(dev)
        changed_prompt = copy.deepcopy(dev)
        changed_prompt[0]["prompt"] += "invent missing words"
        with self.assertRaisesRegex(ValueError, "canonical"):
            bundle.validate_dev(changed_prompt)
        for key in ("target", "reference", "references", "answer"):
            leaked = copy.deepcopy(dev)
            leaked[0][key] = "answer"
            with self.assertRaisesRegex(ValueError, "references"):
                bundle.validate_dev(leaked)

    def test_only_pinned_editorial_controls_are_excluded(self):
        pinned = []
        for row_id in bundle.CONTROL_EXCLUSIONS:
            row = source_row()
            row.update(id=row_id, text="editorial <pad> source")
            pinned.append(row)
        rows = pinned + [source_row()]
        original = copy.deepcopy(rows)
        retained, exclusions = bundle.exclude_editorial_controls(rows, CharacterTokenizer())
        self.assertEqual(retained, [source_row()])
        self.assertEqual({row["id"] for row in exclusions}, set(bundle.CONTROL_EXCLUSIONS))
        self.assertEqual(rows, original)
        for bad in (rows[1:], rows + [pinned[0]]):
            with self.assertRaisesRegex(ValueError, "Pinned editorial"):
                bundle.exclude_editorial_controls(bad, CharacterTokenizer())
        for field in ("text", "target"):
            bad = copy.deepcopy(rows)
            bad[-1][field] += "<pad>"
            with self.assertRaisesRegex(ValueError, "token"):
                bundle.exclude_editorial_controls(bad, CharacterTokenizer())
        bad = copy.deepcopy(rows)
        bad[0]["text"] += "<turn|>"
        with self.assertRaisesRegex(ValueError, "token"):
            bundle.exclude_editorial_controls(bad, CharacterTokenizer())

    def test_result_pack_tamper_extra_members_and_determinism(self):
        with scratch_directory() as temporary:
            root = Path(temporary)
            run = root / "run"
            run.mkdir()
            (run / "status.json").write_bytes(bundle.encoded({"status": "PARTIAL", "reason": "fixture"}))
            (run / "metrics.json").write_bytes(bundle.encoded({"steps": 2}))
            (run / "resume-checkpoint.json").write_bytes(bundle.encoded({"checkpoint": "checkpoint-20", "global_step": 20, "files": {"optimizer.pt": "fixture"}}))
            (run / "secret.env").write_text("must not be included", encoding="utf-8")
            (run / "model.safetensors").write_bytes(b"base weights must not be included")
            one, two = root / "one.zip", root / "two.zip"
            first = bundle.pack_results(run, one)
            bundle.pack_results(run, two)
            self.assertEqual(one.read_bytes(), two.read_bytes())
            self.assertEqual(first["status"]["status"], "PARTIAL")
            with zipfile.ZipFile(one) as archive:
                self.assertEqual(set(archive.namelist()), {"status.json", "metrics.json", "resume-checkpoint.json", "manifest.json"})
                payload = {name: archive.read(name) for name in archive.namelist()}
            for mutation in ("tamper", "unexpected", "traversal", "duplicate"):
                bad = root / (mutation + ".zip")
                with zipfile.ZipFile(bad, "w") as archive:
                    for name, data in payload.items():
                        archive.writestr(name, data + b" " if mutation == "tamper" and name == "metrics.json" else data)
                    if mutation == "unexpected":
                        archive.writestr("unexpected.txt", b"no")
                    if mutation == "traversal":
                        archive.writestr("../outside", b"no")
                    if mutation == "duplicate":
                        with self.assertWarns(UserWarning):
                            archive.writestr("status.json", payload["status.json"])
                with self.assertRaises(ValueError):
                    bundle.verify(bad)
            with self.assertRaises(FileExistsError):
                bundle.pack_results(run, one)
            with self.assertRaisesRegex(ValueError, "outside"):
                bundle.pack_results(run, run / "inside.zip")

    def test_missing_status_and_false_success_fail(self):
        with scratch_directory() as temporary:
            root = Path(temporary)
            run = root / "run"
            run.mkdir()
            with self.assertRaisesRegex(ValueError, "Missing"):
                bundle.pack_results(run, root / "absent.zip")
            (run / "status.json").write_text(json.dumps({"status": "SUCCESS"}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "adapter"):
                bundle.pack_results(run, root / "false.zip")

    @unittest.skipUnless(os.environ.get("PAHLAVI_TRANSLATOR"), "real guard integration requires PAHLAVI_TRANSLATOR")
    def test_frozen_work_rejected_even_with_rehashed_manifest(self):
        translator = Path(os.environ["PAHLAVI_TRANSLATOR"])
        payload = {name: b"{}\n" for name in bundle.BASE_FILES}
        payload["holdout.py"] = (translator / "pahlavi" / "holdout.py").read_bytes()
        payload["benchmark-holdout.json"] = (translator / "pahlavi" / "benchmark-holdout.json").read_bytes()
        rows = []
        for index in range(2484):
            row = source_row()
            row.update(id=f"fixture-{index}", text=f"fixture source {index}", target=f"fixture meaning {index}")
            rows.append(bundle.tokenize_row(row, CharacterTokenizer()))
        dev = [{key: value for key, value in source_row().items() if key in bundle.DEV_KEYS} for _ in range(6)]
        for index, row in enumerate(dev):
            row["id"] = f"fixture-dev-{index}"
            row["prompt"] = bundle.PROMPT.format(text=row["text"])
        payload["dev-inputs.jsonl"] = b"".join(bundle.encoded(row) for row in dev)

        def rehash():
            payload["train.jsonl"] = b"".join(bundle.encoded(row) for row in rows)
            payload["manifest.json"] = bundle.encoded({"schema": 1, "kind": "training-bundle", "files": {
                name: {"sha256": bundle.digest(data), "bytes": len(data)}
                for name, data in payload.items() if name != "manifest.json"}})

        # Tokenizer identity is orthogonal here; the real holdout code and policy
        # remain pinned and run unmodified against current TRAIN and DEV content.
        with patch.object(bundle, "TOKENIZER_HASHES", {}), patch.object(bundle, "BUNDLE_FILES", bundle.BASE_FILES):
            rehash()
            with patch.object(bundle, "ORIGINAL_TOKENIZED_TRAIN_HASH", bundle.digest(payload["train.jsonl"])):
                self.assertEqual(bundle.verify_members(list(payload), payload.__getitem__)["integrity"], "PASS")
            rows[0]["work_id"] = "parsig:104"
            rehash()
            with patch.object(bundle, "ORIGINAL_TOKENIZED_TRAIN_HASH", bundle.digest(payload["train.jsonl"])), \
                    self.assertRaisesRegex(ValueError, "Holdout exclusion"):
                bundle.verify_members(list(payload), payload.__getitem__)
            rows[0]["work_id"] = "parsig:133"
            dev[0]["work_id"] = "parsig:104"
            payload["dev-inputs.jsonl"] = b"".join(bundle.encoded(row) for row in dev)
            rehash()
            with patch.object(bundle, "ORIGINAL_TOKENIZED_TRAIN_HASH", bundle.digest(payload["train.jsonl"])), \
                    self.assertRaisesRegex(ValueError, "Holdout exclusion"):
                bundle.verify_members(list(payload), payload.__getitem__)


ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "resources/local/cloud-pilot-20260926-hf-v5"
QUALIFIED = ROOT / "experiments/train-audit-20260927/qualified-v1"


@unittest.skipUnless(PARENT.is_dir() and QUALIFIED.is_dir(), "frozen local bundle/audit fixtures required")
class QualifiedBundleChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent_payload = {name: (PARENT / name).read_bytes() for name in bundle.BUNDLE_FILES}
        cls.qualified_train = (QUALIFIED / "train.jsonl").read_bytes()

    def test_real_original_bundle_remains_verifiable(self):
        self.assertEqual(bundle.verify(PARENT)["rows"], 2484)
        self.assertEqual(bundle.digest(self.parent_payload["train.jsonl"]), bundle.ORIGINAL_TOKENIZED_TRAIN_HASH)

    def test_cli_preserves_exact_rows_order_tokens_and_parent_files(self):
        with scratch_directory() as temporary:
            output = Path(temporary) / "qualified"
            command = [sys.executable, "-B", str(Path(bundle.__file__)), "prepare-qualified",
                       "--parent", str(PARENT), "--qualified", str(QUALIFIED), "--out", str(output)]
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            report = json.loads(result.stdout)
            self.assertEqual(report["rows"], 2237)
            self.assertEqual(bundle.verify(report["archive"])["rows"], 2237)
            self.assertEqual((output / "train.jsonl").read_bytes(), self.qualified_train)
            self.assertEqual(set(bundle.directory_files(output)), bundle.BUNDLE_FILES | {"manifest.json"})
            for name in bundle.BUNDLE_FILES - {"train.jsonl", "provenance.json", "bundle.py", "contract.json"}:
                self.assertEqual((output / name).read_bytes(), self.parent_payload[name], name)
            self.assertEqual((output / "bundle.py").read_bytes(), Path(bundle.__file__).read_bytes())
            contract_data = Path(bundle.__file__).with_name("contract.json").read_bytes()
            self.assertEqual((output / "contract.json").read_bytes(), contract_data)
            rows = bundle.jsonl(self.qualified_train)
            ids = {row["id"] for row in rows}
            exact_subset = b"".join(line for line in self.parent_payload["train.jsonl"].splitlines(keepends=True)
                                    if json.loads(line)["id"] in ids)
            self.assertEqual(exact_subset, self.qualified_train)
            parent_provenance = json.loads(self.parent_payload["provenance.json"])
            provenance = json.loads((output / "provenance.json").read_bytes())
            self.assertEqual(provenance.pop("qualification"), bundle.QUALIFICATION)
            self.assertEqual(provenance.pop("prepared_contract_sha256"), bundle.digest(contract_data))
            for name in ("training_rows", "token_count", "max_tokens"):
                provenance.pop(name)
                parent_provenance.pop(name)
            self.assertEqual(provenance, parent_provenance)
            before = (output / "manifest.json").read_bytes()
            with self.assertRaisesRegex(ValueError, "already exists"):
                bundle.prepare_qualified(PARENT, QUALIFIED, output)
            self.assertEqual((output / "manifest.json").read_bytes(), before)
            archive_only = Path(temporary) / "occupied"
            archive_only.with_suffix(".zip").write_bytes(b"preserve")
            with self.assertRaisesRegex(ValueError, "already exists"):
                bundle.prepare_qualified(PARENT, QUALIFIED, archive_only)
            self.assertEqual(archive_only.with_suffix(".zip").read_bytes(), b"preserve")

    def test_rehashed_tampering_and_unqualified_row_are_rejected(self):
        rows = bundle.jsonl(self.qualified_train)
        provenance = json.loads(self.parent_payload["provenance.json"])
        provenance.update(qualification=dict(bundle.QUALIFICATION), training_rows=len(rows),
                          token_count=sum(len(row["input_ids"]) for row in rows),
                          max_tokens=max(len(row["input_ids"]) for row in rows))
        good = dict(self.parent_payload, **{"train.jsonl": self.qualified_train,
                                         "provenance.json": bundle.encoded(provenance)})

        def verify_rehashed(payload):
            payload["manifest.json"] = bundle.encoded({"schema": 1, "kind": "training-bundle", "files": {
                name: {"bytes": len(data), "sha256": bundle.digest(data)}
                for name, data in payload.items() if name != "manifest.json"}})
            return bundle.verify_members(list(payload), payload.__getitem__)

        self.assertEqual(verify_rehashed(dict(good))["rows"], 2237)
        selected = {row["id"] for row in rows}
        excluded = next(line for line in self.parent_payload["train.jsonl"].splitlines(keepends=True)
                        if json.loads(line)["id"] not in selected)
        for bad_train in (self.qualified_train + b"\n", excluded + b"".join(self.qualified_train.splitlines(keepends=True)[1:]),
                          self.parent_payload["train.jsonl"]):
            with self.assertRaisesRegex(ValueError, "payload checksum"):
                verify_rehashed(dict(good, **{"train.jsonl": bad_train}))
        for field in ("audit_manifest_sha256", "audit_summary_sha256", "parent_manifest_sha256"):
            bad = copy.deepcopy(provenance)
            bad["qualification"][field] = "0" * 64
            with self.assertRaisesRegex(ValueError, "qualification identity"):
                verify_rehashed(dict(good, **{"provenance.json": bundle.encoded(bad)}))
        bad = copy.deepcopy(provenance)
        bad["training_rows"] -= 1
        with self.assertRaisesRegex(ValueError, "provenance counts"):
            verify_rehashed(dict(good, **{"provenance.json": bundle.encoded(bad)}))
        with self.assertRaisesRegex(ValueError, "payload checksum"):
            verify_rehashed(dict(self.parent_payload, **{"train.jsonl": self.qualified_train}))

    def test_wrong_frozen_audit_or_parent_manifest_creates_no_output(self):
        with scratch_directory() as temporary:
            root = Path(temporary)
            wrong = root / "wrong"
            wrong.mkdir()
            (wrong / "manifest.json").write_bytes(b"{}\n")
            for parent, audit in ((wrong, QUALIFIED), (PARENT, wrong)):
                with self.assertRaisesRegex(ValueError, "Pinned checksum"):
                    bundle.prepare_qualified(parent, audit, root / "output")
                self.assertFalse((root / "output").exists())
                self.assertFalse((root / "output.zip").exists())

    def test_contract_override_cannot_change_recipe_or_cloud_controls(self):
        with scratch_directory() as temporary:
            root = Path(temporary)
            for section, key, value in (("training", "num_train_epochs", 3),
                                        ("generation", "do_sample", True),
                                        ("readiness", "stage_dev_ready", True),
                                        ("cloud", "automatic_recharge", True)):
                contract = json.loads(self.parent_payload["contract.json"])
                contract[section][key] = value
                path = root / "contract.json"
                path.write_bytes(bundle.encoded(contract))
                with self.assertRaisesRegex(ValueError, "Qualified contract"):
                    bundle.prepare_qualified(PARENT, QUALIFIED, root / "output", path)
                self.assertFalse((root / "output").exists())


if __name__ == "__main__":
    unittest.main()
