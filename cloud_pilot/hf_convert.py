"""Prepare one bounded CPU Q8 conversion Job; never authenticate or submit."""
import argparse
import hashlib
import inspect
import json
from pathlib import Path, PurePosixPath
import re
import stat
import time
import uuid
import zipfile

try:
    from . import hf_preflight
except ImportError:
    import hf_preflight

BUCKET = "Mojionix/pahlavi-pilot"
BUNDLE_SHA256 = "715daf3893ea7287089d904923925c32a214349f60e735dd0a0739f4f93c2b36"
SOURCE_MANIFEST_SHA256 = "d8f13d1868ad4ee6643a39355c009d3a3eb5ff5248aaf59c6ad519ffbf524e90"
SOURCE_COMMIT = "95887577ab5fead779581a7030a83c7752ff3234"
REVISION = "842da3794eaa0b77d5f08bae87a17459d91ff475"


def file_sha256(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024**2), b""):
            value.update(block)
    return value.hexdigest()


def safe_extract(path, destination, expected, maximum_bytes):
    """Validate the complete archive before creating any extracted member."""
    if file_sha256(path) != expected:
        raise ValueError("Archive checksum mismatch")
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        names = [item.filename for item in members]
        if len(names) != len(set(names)) or sum(item.file_size for item in members) > maximum_bytes:
            raise ValueError("Duplicate or oversized archive")
        for item in members:
            name = item.orig_filename
            if (not name or "\\" in name or ":" in name or "\x00" in name
                    or PurePosixPath(name).is_absolute()
                    or any(part in {"", ".", ".."} for part in name.split("/"))
                    or item.is_dir() or stat.S_ISLNK(item.external_attr >> 16)):
                raise ValueError("Unsafe archive member")
        destination = Path(destination)
        destination.mkdir(parents=True, exist_ok=False)
        for item in members:
            target = destination / item.filename
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(archive.read(item))


def verify_source(directory):
    directory = Path(directory)
    manifest = directory / "source-manifest.json"
    if file_sha256(manifest) != SOURCE_MANIFEST_SHA256:
        raise ValueError("Source manifest differs from reviewed source")
    record = json.loads(manifest.read_text("utf-8"))
    if record["source_commit"] != SOURCE_COMMIT or len(record["files"]) != 17:
        raise ValueError("Unexpected source revision or closure")
    expected = {item["path"] for item in record["files"]} | {"source-manifest.json"}
    if {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()} != expected:
        raise ValueError("Unexpected conversion source files")
    for item in record["files"]:
        path = directory / item["path"]
        if path.stat().st_size != item["size"] or file_sha256(path) != item["sha256"]:
            raise ValueError("Conversion source checksum mismatch")
    return record


def remaining(deadline, reserve=0):
    seconds = deadline - time.monotonic() - reserve
    if seconds <= 0:
        raise TimeoutError("Conversion job deadline reached")
    return seconds


def conversion_body(settings, stage, deadline, output):
    """Executed only inside the prepared Job, after the unchanged install bootstrap."""
    import os
    import shutil
    import subprocess
    import sys

    bundle_dir, source = stage / "bundle", stage / "source"
    sys.path.insert(0, str(bundle_dir))
    import bundle
    bundle.verify(bundle_dir)
    verify_source(source)
    base = stage / "base"
    print(json.dumps({"stage": "base_download_started"}), flush=True)
    subprocess.run([sys.executable, "-u", str(bundle_dir / "fetch_base.py"), "--out", str(base),
                    "--download"], check=True, timeout=remaining(deadline, 600))
    provenance = json.loads((base / "provenance.json").read_text("utf-8"))
    if provenance["model_id"] != "google/gemma-4-31B-it" or provenance["revision"] != REVISION:
        raise ValueError("Original base identity mismatch")
    print(json.dumps({"stage": "base_download_verified"}), flush=True)
    os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")
    os.environ.pop("NO_LOCAL_GGUF", None)
    local_gguf = stage / "gemma-4-31B-it-Q8_0.gguf"
    command = [sys.executable, "-u", str(source / "convert_hf_to_gguf.py"), str(base),
               "--outtype", "q8_0", "--outfile", str(local_gguf)]
    print(json.dumps({"stage": "conversion_started"}), flush=True)
    with (output / "conversion.log").open("x", encoding="utf-8") as log:
        subprocess.run(command, check=True, timeout=remaining(deadline, 300), stdout=log,
                       stderr=subprocess.STDOUT)
    sys.path.insert(0, str(source / "gguf-py"))
    from gguf import GGUFReader, LlamaFileType
    reader = GGUFReader(local_gguf)
    if (reader.get_field("general.architecture").contents() != "gemma4"
            or reader.get_field("gemma4.block_count").contents() != 60
            or reader.get_field("general.file_type").contents() != int(LlamaFileType.MOSTLY_Q8_0)
            or not reader.tensors):
        raise ValueError("Exported GGUF architecture mismatch")
    del reader
    checksum = file_sha256(local_gguf)
    print(json.dumps({"stage": "conversion_verified", "bytes": local_gguf.stat().st_size,
                      "sha256": checksum}), flush=True)
    partial = output / (local_gguf.name + ".partial")
    transfer = ("import hashlib,shutil,sys;shutil.copyfile(sys.argv[1],sys.argv[2]);"
                "h=hashlib.sha256();f=open(sys.argv[2],'rb');"
                "[h.update(b) for b in iter(lambda:f.read(8*1024**2),b'')];f.close();"
                "assert h.hexdigest()==sys.argv[3], 'Durable GGUF checksum mismatch'")
    print(json.dumps({"stage": "durable_copy_started"}), flush=True)
    subprocess.run([sys.executable, "-c", transfer, str(local_gguf), str(partial), checksum],
                   check=True, timeout=remaining(deadline))
    os.replace(partial, output / local_gguf.name)
    for name in ("config.json", "generation_config.json", "tokenizer_config.json", "chat_template.jinja"):
        shutil.copyfile(base / name, output / name)
    shutil.copyfile(base / "provenance.json", output / "base-provenance.json")
    shutil.copyfile(source / "source-manifest.json", output / "source-manifest.json")
    result = {"status": "conversion_complete", "model_id": provenance["model_id"],
        "revision": REVISION, "source_commit": SOURCE_COMMIT, "source_manifest_sha256": SOURCE_MANIFEST_SHA256,
        "bundle_sha256": BUNDLE_SHA256, "source_zip_sha256": settings["source_sha256"],
        "runtime_input_sha256": settings["bootstrap_hashes"],
        "artifact": local_gguf.name, "bytes": local_gguf.stat().st_size, "sha256": checksum,
        "command": command, "quality_verified": False, "local_fit_verified": False,
        "cross_job_durability_verified": False}
    (output / "provenance.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (output / "SHA256SUMS").write_text(checksum + "  " + local_gguf.name + "\n", encoding="ascii")
    with (output / "environment.txt").open("x", encoding="utf-8") as environment_log:
        subprocess.run([sys.executable, "-m", "pip", "freeze", "--all"], check=True,
                       stdout=environment_log, timeout=remaining(deadline))
    return result


def specification(bundle_name, source_name, source_sha256, run_id=None):
    """Return native SDK arguments and provenance without any remote calls."""
    run_id = uuid.uuid4().hex if run_id is None else run_id
    if not isinstance(run_id, str) or not re.fullmatch(r"[a-f0-9]{32}", run_id):
        raise ValueError("run_id must be 32 lowercase hexadecimal characters")
    for name in (bundle_name, source_name):
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*\.zip", name):
            raise ValueError("Expected a ZIP basename within inputs")
    if bundle_name == source_name or not re.fullmatch(r"[a-f0-9]{64}", source_sha256):
        raise ValueError("Distinct inputs and exact source ZIP checksum required")
    spec, hashes = hf_preflight.specification("cpu")
    prefix, marker, _ = hf_preflight.BOOTSTRAP.partition("device = sys.argv[2]\n")
    if not marker:
        raise ValueError("Preflight bootstrap boundary changed")
    settings = dict(bundle_name=bundle_name, source_name=source_name, source_sha256=source_sha256,
                    run_id=run_id, bootstrap_hashes=hashes)
    header = "import hashlib,json,os,signal,stat,sys,tempfile,time,zipfile\nfrom pathlib import Path,PurePosixPath\n"
    for name in ("BUNDLE_SHA256", "SOURCE_MANIFEST_SHA256", "SOURCE_COMMIT", "REVISION"):
        header += name + " = " + repr(globals()[name]) + "\n"
    for function in (file_sha256, safe_extract, verify_source, remaining, conversion_body):
        header += inspect.getsource(function) + "\n"
    body = '''
settings = SETTINGS
deadline = time.monotonic() + 3300
output = Path('/output')
output.mkdir(parents=True, exist_ok=True)
if any(output.iterdir()):
    raise ValueError('Output prefix already contains files; never overwrite an export')
status = {'status': 'started', 'run_id': settings['run_id'], 'quality_verified': False, 'local_fit_verified': False}
def save_status():
    pending = output / 'status.json.tmp'
    pending.write_text(json.dumps(status, indent=2) + '\\n', encoding='utf-8')
    os.replace(pending, output / 'status.json')
save_status()
def interrupted(signum, frame):
    raise TimeoutError('Job received termination signal')
signal.signal(signal.SIGTERM, interrupted)
try:
    import shutil
    if shutil.disk_usage('/tmp').free < 110 * 1024**3:
        raise ValueError('CPU conversion requires at least 110 GiB free ephemeral disk')
    stage = Path(tempfile.mkdtemp(prefix='pahlavi-conversion-'))
    safe_extract(Path('/input') / settings['bundle_name'], stage / 'bundle', BUNDLE_SHA256, 128 * 1024**2)
    safe_extract(Path('/input') / settings['source_name'], stage / 'source', settings['source_sha256'], 5 * 1024**2)
    verify_source(stage / 'source')
    for name, expected in settings['bootstrap_hashes'].items():
        if file_sha256(stage / 'bundle' / name) != expected:
            raise ValueError('Bootstrap differs from immutable bundle: ' + name)
    exec(BOOTSTRAP_PREFIX)
    remaining(deadline)
    status = conversion_body(settings, stage, deadline, output)
    status['run_id'] = settings['run_id']
    save_status()
    print(json.dumps(status), flush=True)
except BaseException as error:
    status.update(status='failed', error_type=type(error).__name__, error=str(error))
    save_status()
    print(json.dumps(status), flush=True)
    raise
'''.replace("SETTINGS", repr(settings)).replace("BOOTSTRAP_PREFIX", repr(prefix))
    spec["command"][3] = header + body
    spec["flavor"], spec["timeout"] = "cpu-xl", "60m"
    spec["env"].update(HF_XET_CACHE="/tmp/pahlavi-xet-cache", CUDA_VISIBLE_DEVICES="",
                       OMP_NUM_THREADS="8", MKL_NUM_THREADS="8", OPENBLAS_NUM_THREADS="8")
    spec["labels"].update(purpose="q8-conversion", export_id=run_id)
    from huggingface_hub import HfApi, Volume
    spec["volumes"] = [
        Volume(type="bucket", source=BUCKET, path="inputs", mount_path="/input", read_only=True),
        Volume(type="bucket", source=BUCKET, path="exports/" + run_id, mount_path="/output", read_only=False)]
    compile(spec["command"][3], "hf-convert-bootstrap", "exec")
    inspect.signature(HfApi.run_job).bind(None, **spec)
    return spec, dict(settings, bundle_sha256=BUNDLE_SHA256,
        source_manifest_sha256=SOURCE_MANIFEST_SHA256, output_prefix="exports/" + run_id,
        command_sha256=hashlib.sha256(spec["command"][3].encode()).hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-name", required=True)
    parser.add_argument("--source-name", required=True)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--run-id")
    args = parser.parse_args()
    spec, provenance = specification(args.bundle_name, args.source_name, args.source_sha256, args.run_id)
    spec["volumes"] = [volume.to_dict() for volume in spec["volumes"]]
    print(json.dumps({"status": "prepared_not_submitted", "spec": spec, "provenance": provenance}))


if __name__ == "__main__":
    main()
