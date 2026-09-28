"""Prepare a code-only HF Job specification; never authenticate, upload or launch."""
import argparse
import base64
import gzip
import hashlib
import inspect
import json
from pathlib import Path


BOOTSTRAP = r'''
import base64, gzip, hashlib, importlib.metadata, json, os, platform
from pathlib import Path
import shutil, subprocess, sys, tempfile

assert sys.version_info[:2] == (3, 12), sys.version
assert platform.system() == "Linux" and platform.machine() == "x86_64"
assert importlib.metadata.version("torch") == "2.11.0+cu128"
assert shutil.disk_usage("/tmp").free >= 4 * 1024**3, "Insufficient setup disk space"
files = json.loads(gzip.decompress(base64.b64decode(sys.argv[1])))
assert set(files) == {"runtime.py", "requirements-linux.lock"}
work = Path(tempfile.mkdtemp(prefix="pahlavi-preflight-"))
for name, record in files.items():
    data = base64.b64decode(record["content"])
    assert hashlib.sha256(data).hexdigest() == record["sha256"], name
    (work / name).write_bytes(data)
os.chdir(work)
print(json.dumps({"stage": "input_verified", "files": {
    name: record["sha256"] for name, record in files.items()}}), flush=True)
# The base image's unused build CLI pins click<8.4; HF Hub 1.23 requires >=8.4.2.
# Remove only that build helper from this disposable container; keep all runtime pins.
subprocess.run([sys.executable, "-m", "pip", "uninstall", "--break-system-packages",
    "--yes", "spin"], check=True, timeout=30)
subprocess.run([sys.executable, "-m", "pip", "install", "--break-system-packages",
    "--no-cache-dir", "--only-binary=:all:", "--require-hashes",
    "--extra-index-url", "https://download.pytorch.org/whl/cu128",
    "-r", "requirements-linux.lock"], check=True, timeout=300)
subprocess.run([sys.executable, "-m", "pip", "check"], check=True, timeout=30)
sys.path.insert(0, str(work))
import runtime
observed = runtime.environment()
assert observed["packages"] == runtime.PINS, observed
device = sys.argv[2]
assert device in {"cpu", "cuda"}
if device == "cuda":
    print(json.dumps({"stage": "gpu_admission", "environment": runtime.gpu_admission()}), flush=True)
subprocess.run([sys.executable, "runtime.py", "tiny-smoke", "--device", device,
    "--four-bit"], check=True, timeout=90)
print(json.dumps({"stage": "preflight_complete", "device": device,
    "full_model_tested": False, "training_data_uploaded": False}), flush=True)
'''


def specification(device):
    if device not in {"cpu", "cuda"}:
        raise ValueError("Expected cpu or cuda")
    root = Path(__file__).resolve().parent
    contract = json.loads((root / "contract.json").read_text("utf-8"))
    files = {}
    for name in ("runtime.py", "requirements-linux.lock"):
        data = (root / name).read_bytes()
        files[name] = {"sha256": hashlib.sha256(data).hexdigest(),
                       "content": base64.b64encode(data).decode("ascii")}
    payload = base64.b64encode(gzip.compress(json.dumps(files).encode(), mtime=0)).decode("ascii")
    spec = {"image": contract["runtime"]["container_base"],
            "command": ["python", "-u", "-c", BOOTSTRAP, payload, device],
            "env": {"HF_HUB_DISABLE_TELEMETRY": "1", "PYTHONDONTWRITEBYTECODE": "1",
                    "PIP_DISABLE_PIP_VERSION_CHECK": "1"},
            "flavor": "cpu-basic" if device == "cpu" else "a100-large",
            "timeout": "8m" if device == "cpu" else "12m",
            "namespace": "Mojionix",
            "labels": {"project": "pahlavi", "purpose": "runtime-preflight", "device": device}}
    compile(BOOTSTRAP, "hf-preflight-bootstrap", "exec")
    assert json.loads(gzip.decompress(base64.b64decode(payload))) == files
    assert "@sha256:" in spec["image"]
    # Validate the real installed SDK interface without reading credentials or making a request.
    from huggingface_hub import HfApi
    inspect.signature(HfApi.run_job).bind(None, **spec)
    return spec, {name: record["sha256"] for name, record in files.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", choices=("cpu", "cuda"), required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    spec, hashes = specification(args.device)
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(spec, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"status": "prepared_not_submitted", "flavor": spec["flavor"],
        "timeout": spec["timeout"], "files": hashes, "specification": str(args.out.resolve())}))


if __name__ == "__main__":
    main()
