"""Prepare one bounded A100 20-step canary; never authenticate or submit."""
import argparse
import hashlib
import inspect
import json
from pathlib import Path
import re
import uuid

try:
    from . import hf_convert, hf_preflight
except ImportError:
    import hf_convert
    import hf_preflight

BUCKET = "Mojionix/pahlavi-pilot"
REVISION = "842da3794eaa0b77d5f08bae87a17459d91ff475"
EXPORT_RESERVE_SECONDS = 180
MAX_EXPORT_BYTES = 2 * 1024**3
file_sha256, remaining = hf_convert.file_sha256, hf_convert.remaining


def emit(phase, **details):
    from datetime import datetime, timezone
    print(json.dumps({"stage": phase, "utc": datetime.now(timezone.utc).isoformat(), **details}), flush=True)


def publish(source, output, deadline, identity):
    """Close immutable final files, then publish a manifest; remote durability remains unverified."""
    import shutil
    files = {}
    paths = sorted(source.rglob("*"))
    if any(path.is_symlink() or not path.resolve().is_relative_to(source.resolve()) for path in paths):
        raise ValueError("Export path escapes its owned directory")
    paths = [path for path in paths if path.is_file()]
    if not paths or sum(path.stat().st_size for path in paths) > MAX_EXPORT_BYTES:
        raise ValueError("Empty export or export exceeds the 2 GiB canary bound")
    for path in paths:
        remaining(deadline)
        name = path.relative_to(source).as_posix()
        files[name] = {"bytes": path.stat().st_size, "sha256": file_sha256(path)}
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with path.open("rb") as incoming, target.open("xb") as outgoing:
            shutil.copyfileobj(incoming, outgoing, 8 * 1024**2)
        emit("artifact_closed", path=name, **files[name])
    manifest = {"schema_version": 1, **identity, "files": files, "canary_compute_pass": True,
                "remote_inventory_verified": False, "cross_job_sha256_verified": False}
    payload = (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    remaining(deadline)
    with (output / "manifest.json").open("xb") as stream:
        stream.write(payload)
    return {"manifest": manifest, "manifest_file": "manifest.json", "manifest_bytes": len(payload),
            "manifest_sha256": hashlib.sha256(payload).hexdigest()}


def canary_body(settings, stage, deadline, output):
    import shutil
    import subprocess
    import sys
    from datetime import datetime, timezone, timedelta
    bundle_dir, artifacts, base = stage / "bundle", stage / "artifacts", stage / "base"
    artifacts.mkdir()
    sys.path.insert(0, str(bundle_dir))
    import bundle
    import runtime
    bundle.verify(bundle_dir)
    emit("gpu_admission", environment=runtime.gpu_admission())  # Before any model download.
    driver = str(bundle_dir / "runtime.py")
    commands = []

    def child(phase, command):
        commands.append(command)
        emit(phase + "_started", command=command)
        # Provider logs remain live; the controller preserves them independently.
        subprocess.run(command, check=True, timeout=remaining(deadline, EXPORT_RESERVE_SECONDS))
        emit(phase + "_complete")

    child("base_download", [sys.executable, "-u", str(bundle_dir / "fetch_base.py"), "--out", str(base), "--download"])
    provenance = json.loads((base / "provenance.json").read_text("utf-8"))
    if provenance["model_id"] != "google/gemma-4-31B-it" or provenance["revision"] != REVISION:
        raise ValueError("Original base identity mismatch")
    runtime.offline()
    compute_deadline = (datetime.now(timezone.utc) + timedelta(seconds=remaining(deadline, EXPORT_RESERVE_SECONDS))).isoformat()
    common = ["--bundle", str(bundle_dir), "--contract", str(bundle_dir / "contract.json"),
              "--base", str(base), "--deadline-utc", compute_deadline]
    if remaining(deadline, EXPORT_RESERVE_SECONDS) < 600:
        raise TimeoutError("Do not start training with less than ten minutes before the export reserve")
    training = artifacts / "training"
    child("canary", [sys.executable, "-u", driver, "train", *common, "--output", str(training), "--max-steps", "20"])
    checkpoint, checkpoint_record = runtime.resume_checkpoint(training / "checkpoint-20", training)
    if checkpoint_record["global_step"] != 20:
        raise ValueError("Canary checkpoint must contain exactly 20 optimizer steps")
    for name in ("adapter_config.json", "adapter_model.safetensors"):
        if not (training / "canary-adapter" / name).is_file() or (training / "canary-adapter" / name).stat().st_size == 0:
            raise ValueError("Missing final canary adapter artifact: " + name)
    for source, name in ((base / "provenance.json", "base-provenance.json"),
                         (bundle_dir / "manifest.json", "bundle-manifest.json"), (bundle_dir / "contract.json", "contract.json")):
        shutil.copyfile(source, artifacts / name)
    identity = {"run_id": settings["run_id"], "bundle_name": settings["bundle_name"], "bundle_sha256": settings["bundle_sha256"],
                "global_step": 20, "model_id": provenance["model_id"], "revision": REVISION,
                "bootstrap_hashes": settings["bootstrap_hashes"], "commands": commands,
                "checkpoint": checkpoint.relative_to(artifacts).as_posix(), "full_training_resumed": False}
    (artifacts / "job-provenance.json").write_text(json.dumps(identity, indent=2) + "\n", encoding="utf-8")
    emit("export_started")
    return publish(artifacts, output, deadline, identity)


try:
    from .training_admission import draft
except ImportError:
    from training_admission import draft


@draft
def specification(bundle_name, bundle_sha256, run_id=None):
    run_id = uuid.uuid4().hex if run_id is None else run_id
    if not isinstance(run_id, str) or not re.fullmatch(r"[a-f0-9]{32}", run_id):
        raise ValueError("run_id must be 32 lowercase hexadecimal characters")
    if not isinstance(bundle_name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*\.zip", bundle_name):
        raise ValueError("Bundle must be a simple ZIP basename within inputs")
    if not isinstance(bundle_sha256, str) or not re.fullmatch(r"[a-f0-9]{64}", bundle_sha256):
        raise ValueError("Require immutable bundle SHA-256")
    spec, hashes = hf_preflight.specification("cuda")
    prefix, marker, _ = hf_preflight.BOOTSTRAP.partition("device = sys.argv[2]\n")
    if not marker:
        raise ValueError("Reviewed bootstrap boundary changed")
    settings = dict(bundle_name=bundle_name, bundle_sha256=bundle_sha256, run_id=run_id, bootstrap_hashes=hashes)
    header = "import hashlib,json,os,signal,stat,sys,tempfile,time,zipfile\nfrom pathlib import Path,PurePosixPath\n"
    for name in ("REVISION", "EXPORT_RESERVE_SECONDS", "MAX_EXPORT_BYTES"):
        header += name + " = " + repr(globals()[name]) + "\n"
    for function in (hf_convert.file_sha256, hf_convert.safe_extract, hf_convert.remaining, emit, publish, canary_body):
        header += inspect.getsource(function) + "\n"
    body = '''
settings = SETTINGS
deadline = time.monotonic() + 1500
ready_to_persist = False
def interrupted(signum, frame):
    raise TimeoutError('Canary received termination signal or reached its 25-minute deadline')
signal.signal(signal.SIGTERM, interrupted)
signal.signal(signal.SIGALRM, interrupted)
signal.alarm(1500)
try:
    output = Path('/output')
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError('Output prefix is not empty; never overwrite a prior trial')
    import shutil
    if shutil.disk_usage('/tmp').free < 80 * 1024**3:
        raise ValueError('Original safetensors and canary require 80 GiB free ephemeral disk')
    stage = Path(tempfile.mkdtemp(prefix='pahlavi-canary-'))
    safe_extract(Path('/input') / settings['bundle_name'], stage / 'bundle', settings['bundle_sha256'], 128 * 1024**2)
    for name, expected in settings['bootstrap_hashes'].items():
        if file_sha256(stage / 'bundle' / name) != expected:
            raise ValueError('Bootstrap differs from immutable bundle: ' + name)
    emit('bootstrap_started', run_id=settings['run_id'])
    exec(BOOTSTRAP_PREFIX)
    emit('bootstrap_complete')
    result = canary_body(settings, stage, deadline, output)
    ready_to_persist = True
    emit('ready_to_persist', **result)
    wait_seconds = max(0, min(300, deadline - time.monotonic()))
    emit('awaiting_controller_durability_check', maximum_wait_seconds=wait_seconds)
    time.sleep(wait_seconds)
    emit('persistence_window_expired', remote_inventory_verified=False, cross_job_sha256_verified=False)
except BaseException as error:
    emit('stopped_after_ready' if ready_to_persist else 'failed', error_type=type(error).__name__, error=str(error),
         ready_to_persist=ready_to_persist)
    raise
finally:
    signal.alarm(0)
'''.replace("SETTINGS", repr(settings)).replace("BOOTSTRAP_PREFIX", repr(prefix))
    spec["command"][3] = header + body
    spec["flavor"], spec["timeout"] = "a100-large", "30m"
    spec["env"].update(HF_XET_CACHE="/tmp/pahlavi-xet-cache", OMP_NUM_THREADS="8", MKL_NUM_THREADS="8")
    spec["labels"].update(purpose="training-canary20", trial_id=run_id)
    from huggingface_hub import HfApi, Volume
    spec["volumes"] = [Volume(type="bucket", source=BUCKET, path="inputs", mount_path="/input", read_only=True),
                       Volume(type="bucket", source=BUCKET, path="trials/" + run_id, mount_path="/output", read_only=False)]
    compile(spec["command"][3], "hf-canary-bootstrap", "exec")
    inspect.signature(HfApi.run_job).bind(None, **spec)
    return spec, dict(settings, output_prefix="trials/" + run_id, internal_seconds=1500, export_reserve_seconds=180,
        maximum_wait_seconds=300, command_sha256=hashlib.sha256(spec["command"][3].encode()).hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("bundle-name", "bundle-sha256"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--run-id")
    args = parser.parse_args()
    spec, provenance = specification(args.bundle_name, args.bundle_sha256, args.run_id)
    spec["volumes"] = [volume.to_dict() for volume in spec["volumes"]]
    print(json.dumps({"status": "prepared_not_submitted", "spec": spec, "provenance": provenance}))


if __name__ == "__main__":
    main()
