"""Prepare one original-model PAL-REF baseline Job; never authenticate or submit."""
import argparse
import hashlib
import inspect
import json
from pathlib import Path
import re
import uuid

try:
    from . import hf_train, hf_preflight, hf_convert
except ImportError:
    import hf_train
    import hf_preflight
    import hf_convert

INPUTS_SHA256 = "0616b50838339e9b520f06fe8b2ed9c0fd9b399b67c8f68cd680a62115a12f37"
file_sha256, remaining, emit = hf_convert.file_sha256, hf_convert.remaining, hf_train.emit


def publish(source, output, deadline, identity):
    """Publish closed, immutable baseline artifacts; never claim remote durability."""
    import shutil
    paths = sorted(source.rglob("*"))
    if any(path.is_symlink() or not path.resolve().is_relative_to(source.resolve()) for path in paths):
        raise ValueError("Unsafe baseline artifact path")
    paths = [path for path in paths if path.is_file() and not path.name.endswith(".tmp")]
    if not paths or sum(path.stat().st_size for path in paths) > 16 * 1024**2:
        raise ValueError("Empty baseline export or export exceeds 16 MiB")
    files = {}
    for path in paths:
        remaining(deadline)
        name = path.relative_to(source).as_posix()
        entry = {"bytes": path.stat().st_size, "sha256": file_sha256(path)}
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with path.open("rb") as incoming, target.open("xb") as outgoing:
            shutil.copyfileobj(incoming, outgoing, 1024**2)
        files[name] = entry
        emit("artifact_closed", path=name, **entry)
    manifest = {"schema_version": 1, **identity, "files": files, "remote_inventory_verified": False,
                "cross_job_sha256_verified": False, "quality_validated": False}
    payload = (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode()
    remaining(deadline)
    with (output / "manifest.json").open("xb") as stream:
        stream.write(payload)
    return {"manifest": manifest, "manifest_file": "manifest.json", "manifest_bytes": len(payload),
            "manifest_sha256": hashlib.sha256(payload).hexdigest()}


def baseline_body(settings, stage, deadline, evidence):
    """One original-model PAL-REF attempt; no training, checkpoints or scoring."""
    import os
    import shutil
    import subprocess
    import sys
    from datetime import datetime, timezone, timedelta
    folder, base = stage / "bundle", stage / "base"
    sys.path.insert(0, str(folder))
    import runtime
    import bundle
    bundle.verify(folder)
    emit("gpu_admission", environment=runtime.gpu_admission())
    emit("base_download_started")
    subprocess.run([sys.executable, "-u", str(folder / "fetch_base.py"), "--out", str(base), "--download"],
                   check=True, timeout=remaining(deadline, 180))
    runtime.offline()
    emit("base_download_verified")
    for source, name in ((base / "provenance.json", "base-provenance.json"),
                         (folder / "manifest.json", "bundle-manifest.json"), (folder / "contract.json", "contract.json")):
        shutil.copyfile(source, evidence / name)
    evaluator = stage / "palref_eval.py"
    shutil.copyfile(Path("/input") / settings["evaluator_name"], evaluator)
    os.environ["PYTHONPATH"] = str(folder)
    cutoff = (datetime.now(timezone.utc) + timedelta(seconds=remaining(deadline, 180))).isoformat()
    command = [sys.executable, "-u", str(evaluator), "--bundle", str(folder), "--base", str(base),
               "--tokenizer", str(base), "--inputs", str(Path("/input") / settings["inputs_name"]),
               "--output", str(evidence / "baseline"), "--deadline-utc", cutoff]
    emit("palref_original_started", command=command)
    subprocess.run(command, check=True, timeout=remaining(deadline, 180))
    run = json.loads((evidence / "baseline/run.json").read_text("utf-8"))
    ids = [json.loads(line)["id"] for line in (evidence / "baseline/predictions.jsonl").read_text("utf-8").splitlines()]
    if (run.get("status") != "completed" or run.get("completed_cases") != 40 or run.get("condition") != "bf16-original"
            or ids != [f"PALREF1-{index:03d}:pal>fa" for index in range(1, 41)]):
        raise ValueError("Original PAL-REF attempt did not complete all forty cases")
    emit("palref_original_complete", completed_cases=40)

def baseline_specification(bundle_name, bundle_sha256, evaluator_name, evaluator_sha256, inputs_name, inputs_sha256, run_id=None):
    """Independent baseline only: 30m native, 25m internal, partial evidence on failure."""
    run_id = uuid.uuid4().hex if run_id is None else run_id
    if not isinstance(run_id, str) or not re.fullmatch(r"[a-f0-9]{32}", run_id):
        raise ValueError("Expected a fresh 32-character lowercase hexadecimal run ID")
    names = (bundle_name, evaluator_name, inputs_name)
    if len(set(names)) != 3 or any(not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name) for name in names):
        raise ValueError("Distinct immutable input basenames required")
    for checksum in (bundle_sha256, evaluator_sha256, inputs_sha256):
        if not isinstance(checksum, str) or not re.fullmatch(r"[a-f0-9]{64}", checksum):
            raise ValueError("Full lowercase SHA-256 values required")
    if inputs_sha256 != INPUTS_SHA256 or evaluator_sha256 != file_sha256(Path(__file__).with_name("palref_eval.py")):
        raise ValueError("Only the unchanged PAL-REF evaluator and source-only forty inputs are allowed")
    spec, hashes = hf_preflight.specification("cuda")
    prefix, marker, _ = hf_preflight.BOOTSTRAP.partition("device = sys.argv[2]\n")
    if not marker:
        raise ValueError("Reviewed bootstrap boundary changed")
    settings = dict(bundle_name=bundle_name, bundle_sha256=bundle_sha256, evaluator_name=evaluator_name,
                    evaluator_sha256=evaluator_sha256, inputs_name=inputs_name, inputs_sha256=inputs_sha256,
                    run_id=run_id, bootstrap_hashes=hashes)
    header = "import hashlib,json,os,re,signal,stat,sys,tempfile,time,zipfile\nfrom pathlib import Path,PurePosixPath\n"
    for function in (hf_convert.file_sha256, hf_convert.safe_extract, hf_convert.remaining, hf_train.emit, publish, baseline_body):
        header += inspect.getsource(function) + "\n"
    body = '''
settings = SETTINGS
deadline = time.monotonic() + 1500
def interrupted(signum, frame):
    raise TimeoutError('Baseline interrupted or reached its computation deadline')
signal.signal(signal.SIGTERM, interrupted)
signal.signal(signal.SIGALRM, interrupted)
signal.alarm(1320)
output = Path('/output')
output.mkdir(parents=True, exist_ok=True)
if any(output.iterdir()):
    raise ValueError('Fresh output prefix required')
stage = Path(tempfile.mkdtemp(prefix='pahlavi-baseline-'))
evidence = stage / 'evidence'
evidence.mkdir()
identity = dict(settings, operation='palref_baseline', baseline_status='incomplete', evaluation_complete=False, training_performed=False,
                local_model_verified=False, quality_validated=False)
try:
    import shutil
    if shutil.disk_usage('/tmp').free < 80 * 1024**3:
        raise ValueError('Original baseline requires 80 GiB ephemeral disk')
    for key in ('evaluator', 'inputs'):
        if file_sha256(Path('/input') / settings[key + '_name']) != settings[key + '_sha256']:
            raise ValueError('Frozen input checksum mismatch: ' + key)
    safe_extract(Path('/input') / settings['bundle_name'], stage / 'bundle', settings['bundle_sha256'], 128 * 1024**2)
    for name, expected in settings['bootstrap_hashes'].items():
        if file_sha256(stage / 'bundle' / name) != expected:
            raise ValueError('Frozen bootstrap and bundle differ: ' + name)
    emit('bootstrap_started')
    exec(BOOTSTRAP_PREFIX)
    emit('bootstrap_complete')
    baseline_body(settings, stage, deadline, evidence)
    identity.update(baseline_status='complete', evaluation_complete=True)
except BaseException as error:
    identity.update(error_type=type(error).__name__, error=str(error))
    emit('baseline_incomplete', **identity)
finally:
    signal.alarm(max(1, int(max(0, deadline - time.monotonic()))))
    (evidence / 'baseline-status.json').write_text(json.dumps(identity, indent=2) + '\\n')
    result = publish(evidence, output, deadline, identity)
    emit('ready_to_persist', **result)
    time.sleep(max(0, min(300, deadline - time.monotonic())))
    emit('persistence_window_expired', remote_inventory_verified=False)
    signal.alarm(0)
'''.replace("SETTINGS", repr(settings)).replace("BOOTSTRAP_PREFIX", repr(prefix))
    spec["command"][3] = header + body
    spec["flavor"], spec["timeout"] = "a100-large", "30m"
    spec["labels"].update(purpose="palref-original-only", trial_id=run_id)
    spec["env"].update(HF_XET_CACHE="/tmp/pahlavi-xet-cache", OMP_NUM_THREADS="8", MKL_NUM_THREADS="8")
    from huggingface_hub import HfApi, Volume
    spec["volumes"] = [Volume(type="bucket", source=hf_train.BUCKET, path="inputs", mount_path="/input", read_only=True),
        Volume(type="bucket", source=hf_train.BUCKET, path="baselines/" + run_id, mount_path="/output", read_only=False)]
    compile(spec["command"][3], "hf-baseline", "exec")
    inspect.signature(HfApi.run_job).bind(None, **spec)
    return spec, dict(settings, output_prefix="baselines/" + run_id,
        command_sha256=hashlib.sha256(spec["command"][3].encode()).hexdigest())

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("bundle-name", "bundle-sha256", "evaluator-name", "evaluator-sha256", "inputs-name", "inputs-sha256"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--run-id")
    spec, provenance = baseline_specification(**vars(parser.parse_args()))
    spec["volumes"] = [volume.to_dict() for volume in spec["volumes"]]
    print(json.dumps({"status": "prepared_not_submitted", "spec": spec, "provenance": provenance}))


if __name__ == "__main__":
    main()

