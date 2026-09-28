"""Inspect or explicitly download the one pinned, original Google model snapshot."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

from runtime import MODEL_ID, REVISION, digest, write_json

SMALL = {"config.json", "generation_config.json", "model.safetensors.index.json",
         "tokenizer.json", "tokenizer_config.json", "chat_template.jinja"}


def metadata_plan(info):
    if info.sha != REVISION:
        raise ValueError("Hub returned a different revision")
    files = {}
    for item in info.siblings:
        name = item.rfilename
        if name not in SMALL and not re.fullmatch(r"model-\d+-of-\d+\.safetensors", name):
            continue
        if type(item.size) is not int or item.size <= 0:
            raise ValueError("Missing file size: " + name)
        if item.lfs:
            algorithm, expected = "sha256", item.lfs.sha256
        else:
            algorithm, expected = "git-sha1", item.blob_id
        if not isinstance(expected, str) or not re.fullmatch("[a-f0-9]{%d}" % (64 if algorithm == "sha256" else 40), expected):
            raise ValueError("Missing upstream checksum: " + name)
        files[name] = {"bytes": item.size, "algorithm": algorithm, "expected": expected}
    if not SMALL <= set(files) or not any(name.endswith(".safetensors") for name in files):
        raise ValueError("Snapshot lacks required original model files")
    return files


def verify_download(path, entry):
    if path.stat().st_size != entry["bytes"]:
        raise ValueError("Download size mismatch: " + path.name)
    sha = hashlib.sha256()
    blob = hashlib.sha1(b"blob " + str(entry["bytes"]).encode("ascii") + b"\0")
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            sha.update(block)
            blob.update(block)
    actual = sha.hexdigest() if entry["algorithm"] == "sha256" else blob.hexdigest()
    if actual != entry["expected"]:
        raise ValueError("Upstream checksum mismatch: " + path.name)
    return sha.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    parser.add_argument("--download", action="store_true", help="Explicitly authorize the large weight download")
    args = parser.parse_args()
    from huggingface_hub import HfApi, hf_hub_download
    info = HfApi(token=False).model_info(MODEL_ID, revision=REVISION, files_metadata=True)
    files = metadata_plan(info)
    total = sum(entry["bytes"] for entry in files.values())
    output = Path(args.out).resolve()
    parent = output
    while not parent.exists():
        parent = parent.parent
    free = shutil.disk_usage(parent).free
    print(json.dumps({"model_id": MODEL_ID, "revision": REVISION, "files": len(files),
                      "download_bytes": total, "free_bytes": free, "download_requested": args.download}))
    if not args.download:
        return
    if (output / "provenance.json").exists():
        raise ValueError("Verified snapshot already exists; do not overwrite it")
    # Resuming an interrupted transfer is explicit; partial bytes already present count toward space.
    present = sum((output / name).stat().st_size for name in files if (output / name).is_file())
    if free < max(0, total - present) + 5 * 1024**3:
        raise ValueError("Insufficient disk space; leave at least 5 GiB beyond remaining snapshot size")
    output.mkdir(parents=True, exist_ok=True)
    checksums = {}
    for name, entry in sorted(files.items()):
        path = Path(hf_hub_download(MODEL_ID, name, revision=REVISION, token=False, local_dir=output))
        checksums[name] = verify_download(path, entry)
    index = json.loads((output / "model.safetensors.index.json").read_text("utf-8"))
    if not set(index["weight_map"].values()) <= set(checksums):
        raise ValueError("A weight shard referenced by the index was not verified")
    write_json(output / "provenance.json", {"model_id": MODEL_ID, "revision": REVISION,
        "files": checksums, "upstream": files, "fetch_script_sha256": digest(__file__)})
    print(json.dumps({"status": "verified", "directory": str(output), "bytes": total}))


if __name__ == "__main__":
    main()
