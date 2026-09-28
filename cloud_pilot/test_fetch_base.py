"""Offline checks for download integrity; no model download or Hub access."""
import hashlib
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import fetch_base


class DownloadChecks(unittest.TestCase):
    def test_revision_and_complete_file_list(self):
        item = lambda name: SimpleNamespace(rfilename=name, size=4, lfs=None, blob_id="a" * 40)
        info = SimpleNamespace(sha=fetch_base.REVISION,
            siblings=[item(name) for name in fetch_base.SMALL | {"model-00001-of-00001.safetensors"}])
        self.assertEqual(len(fetch_base.metadata_plan(info)), 7)
        info.sha = "wrong"
        with self.assertRaisesRegex(ValueError, "revision"):
            fetch_base.metadata_plan(info)
        info.sha = fetch_base.REVISION
        info.siblings = [item("config.json")]
        with self.assertRaisesRegex(ValueError, "required"):
            fetch_base.metadata_plan(info)

    def test_corruption_rejected_for_lfs_and_git(self):
        from io import BytesIO
        data = b"verified bytes"
        checks = [("sha256", hashlib.sha256(data).hexdigest()),
                  ("git-sha1", hashlib.sha1(b"blob 14\0" + data).hexdigest())]
        for algorithm, expected in checks:
            entry = {"bytes": len(data), "algorithm": algorithm, "expected": expected}
            with patch.object(Path, "stat", return_value=SimpleNamespace(st_size=len(data))), \
                 patch.object(Path, "open", side_effect=lambda *_: BytesIO(data)):
                self.assertEqual(fetch_base.verify_download(Path("model"), entry), hashlib.sha256(data).hexdigest())
                entry["expected"] = "0" * len(expected)
                with self.assertRaisesRegex(ValueError, "checksum"):
                    fetch_base.verify_download(Path("model"), entry)


if __name__ == "__main__":
    unittest.main()
