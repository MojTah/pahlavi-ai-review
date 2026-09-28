"""Offline checks for the bounded conversion specification and input admission."""
import hashlib
from contextlib import contextmanager
import json
from pathlib import Path
import shutil
import stat
import unittest
import uuid
from unittest.mock import patch
import zipfile

try:
    from . import hf_convert as convert, hf_preflight
except ImportError:
    import hf_convert as convert
    import hf_preflight


class ConversionPreparationTests(unittest.TestCase):
    @contextmanager
    def temp(self):
        # Windows sandbox denies the explicit mode=0700 used by tempfile.mkdtemp.
        parent = (Path(__file__).resolve().parent.parent / "resources" / "local").resolve()
        directory = parent / ("convert-test-" + uuid.uuid4().hex)
        directory.mkdir()
        try:
            yield directory
        finally:
            assert directory.resolve().parent == parent
            shutil.rmtree(directory)

    def test_native_spec_is_scoped_bounded_and_never_submits(self):
        with patch("huggingface_hub.HfApi.whoami", side_effect=AssertionError("Authentication")), \
             patch("huggingface_hub.HfApi.run_job", autospec=True) as submit:
            spec, provenance = convert.specification("bundle.zip", "source.zip", "e" * 64, "a" * 32)
            submit.assert_not_called()
        self.assertEqual((spec["flavor"], spec["timeout"]), ("cpu-xl", "60m"))
        self.assertNotIn("secrets", spec)
        self.assertEqual(spec["volumes"][0].to_dict(), {"type": "bucket", "source": convert.BUCKET,
            "path": "inputs", "mountPath": "/input", "readOnly": True})
        self.assertEqual(spec["volumes"][1].to_dict(), {"type": "bucket", "source": convert.BUCKET,
            "path": "exports/" + "a" * 32, "mountPath": "/output", "readOnly": False})
        original, hashes = hf_preflight.specification("cpu")
        self.assertEqual(spec["image"], original["image"])
        self.assertEqual(spec["command"][4:], original["command"][4:])
        self.assertEqual(provenance["bootstrap_hashes"], hashes)
        prefix = hf_preflight.BOOTSTRAP.partition("device = sys.argv[2]\n")[0]
        self.assertIn(repr(prefix), spec["command"][3])
        compile(spec["command"][3], "job", "exec")
        self.assertEqual(provenance["command_sha256"], hashlib.sha256(spec["command"][3].encode()).hexdigest())

    def test_invalid_scope_rejected_before_sdk(self):
        for changes in ({"bundle_name": "../b.zip"}, {"source_name": "/s.zip"},
                        {"source_name": "bundle.zip"}, {"source_sha256": "x" * 64},
                        {"run_id": "../overwrite"}):
            options = dict(bundle_name="bundle.zip", source_name="source.zip", source_sha256="e" * 64,
                           run_id="a" * 32)
            options.update(changes)
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                convert.specification(**options)

    def archive(self, root, names):
        path = root / "input.zip"
        with zipfile.ZipFile(path, "w") as archive:
            for name in names:
                info = zipfile.ZipInfo("placeholder")
                info.filename = name
                archive.writestr(info, b"payload")
        return path, convert.file_sha256(path)

    def test_exact_archive_and_fresh_destination(self):
        with self.temp() as temp:
            root = Path(temp)
            archive, checksum = self.archive(root, ["dir/file.txt"])
            destination = root / "out"
            convert.safe_extract(archive, destination, checksum, 100)
            self.assertEqual((destination / "dir/file.txt").read_bytes(), b"payload")
            with self.assertRaises(FileExistsError):
                convert.safe_extract(archive, destination, checksum, 100)

    def test_archive_failures_leave_no_extraction(self):
        for names, limit, wrong_hash in [(["../escape"], 100, False), (["a\\b"], 100, False),
                (["/absolute"], 100, False), (["same", "same"], 100, False),
                (["large"], 1, False), (["okay"], 100, True)]:
            with self.subTest(names=names, limit=limit), self.temp() as temp:
                root = Path(temp)
                archive, checksum = self.archive(root, names)
                with self.assertRaises(ValueError):
                    convert.safe_extract(archive, root / "out", "0" * 64 if wrong_hash else checksum, limit)
                self.assertFalse((root / "out").exists())

    def test_symlink_archive_is_rejected(self):
        with self.temp() as temp:
            root = Path(temp)
            archive = root / "link.zip"
            info = zipfile.ZipInfo("link")
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            with zipfile.ZipFile(archive, "w") as stream:
                stream.writestr(info, "outside")
            with self.assertRaises(ValueError):
                convert.safe_extract(archive, root / "out", convert.file_sha256(archive), 100)

    def test_reviewed_source_manifest_and_member_tamper(self):
        with self.temp() as temp:
            root = Path(temp)
            members = []
            for index in range(17):
                name = str(index) + ".py"
                (root / name).write_bytes(b"valid")
                members.append({"path": name, "size": 5, "sha256": hashlib.sha256(b"valid").hexdigest()})
            manifest = root / "source-manifest.json"
            manifest.write_text(json.dumps({"source_commit": convert.SOURCE_COMMIT, "files": members}))
            with patch.object(convert, "SOURCE_MANIFEST_SHA256", convert.file_sha256(manifest)):
                self.assertEqual(len(convert.verify_source(root)["files"]), 17)
                (root / "0.py").write_bytes(b"wrong")
                with self.assertRaisesRegex(ValueError, "checksum"):
                    convert.verify_source(root)

    def test_deadline_reserves_time_and_stops_expired_phase(self):
        with patch.object(convert.time, "monotonic", return_value=100):
            self.assertEqual(convert.remaining(1000, 300), 600)
            for deadline, reserve in ((100, 0), (99, 0), (200, 100)):
                with self.assertRaises(TimeoutError):
                    convert.remaining(deadline, reserve)

    def test_job_records_admission_failure_before_install(self):
        spec, _ = convert.specification("bundle.zip", "source.zip", "e" * 64, "a" * 32)
        with self.temp() as root:
            output = root / "output"
            code = spec["command"][3].replace("Path('/output')", "Path(" + repr(str(output)) + ")")
            with patch("shutil.disk_usage") as disk, patch("signal.signal"), \
                    patch("subprocess.run", side_effect=AssertionError("No process before admission")):
                disk.return_value.free = 0
                with self.assertRaisesRegex(ValueError, "ephemeral disk"):
                    exec(compile(code, "failed-job-test", "exec"), {})
            status = json.loads((output / "status.json").read_text())
            self.assertEqual(status["status"], "failed")
            self.assertFalse(status["quality_verified"])
            self.assertFalse(status["local_fit_verified"])


if __name__ == "__main__":
    unittest.main()
