"""Prepare one cloud-only instruction diagnostic; never authenticate or submit."""
import base64
import hashlib
import inspect
import json
from pathlib import Path
import re
import uuid

from . import hf_baseline, hf_convert, hf_preflight, hf_train

BUNDLE_NAME = "cloud-pilot-20260926-hf-v5.zip"
BUNDLE_SHA256 = "6c686fa4a38ae2cf52b8c75de616f1717da02ae0a32206f8e7b541a3b4e27cbb"
INPUTS_SHA256 = "06ac58310bf67767fae4124d8e935c808d15debcd8daebce07b583937cd97182"
INPUTS_NAME = "qualitydev1-" + INPUTS_SHA256[:12] + ".jsonl"
TRAINED_PREFIX = "continuations/4c67a84cfc7e4e70a5f1e9e7b63072ac"
TRAINED_MANIFEST_SHA256 = "4e88826bf911ab22e85a6a0b4ecfae131591c6edecbc34fff687af9b57a57a01"
PALREF_RUNNER_SHA256 = "050a38880c68113ca5e5ebc4abd26945d05959eeda52f5df64f00292acfe4a49"


def diagnostic_body(settings, stage, deadline, evidence):
    import os
    import shutil
    import subprocess
    import sys
    from datetime import datetime, timedelta, timezone

    folder, base = stage / "bundle", stage / "base"
    sys.path.insert(0, str(folder))
    import bundle
    import runtime
    bundle.verify(folder)
    emit("gpu_admission", environment=runtime.gpu_admission())
    trained = Path("/trained")
    if file_sha256(trained / "manifest.json") != settings["trained_manifest_sha256"]:
        raise ValueError("Trained cloud manifest identity differs")
    manifest = json.loads((trained / "manifest.json").read_text("utf-8"))
    if manifest.get("full_training_completed") is not True or manifest.get("training_reached_step_312") is not True:
        raise ValueError("Completed step312 evidence required")
    for name in ("training/adapter/adapter_config.json", "training/adapter/adapter_model.safetensors", "training/provenance.json", "training/status.json"):
        source, target = trained / name, stage / name
        entry = manifest["files"][name]
        if source.stat().st_size != entry["bytes"] or file_sha256(source) != entry["sha256"]:
            raise ValueError("Trained cloud artifact checksum mismatch: " + name)
        remaining(deadline, 180)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if file_sha256(target) != entry["sha256"]:
            raise ValueError("Trained local cloud copy differs: " + name)
    shutil.copyfile(trained / "manifest.json", evidence / "trained-manifest.json")
    emit("trained_adapter_recovered")
    emit("base_download_started")
    subprocess.run([sys.executable, "-u", str(folder / "fetch_base.py"), "--out", str(base), "--download"],
                   check=True, timeout=remaining(deadline, 180))
    emit("base_download_verified")
    for source, name in ((base / "provenance.json", "base-provenance.json"),
                         (folder / "manifest.json", "bundle-manifest.json")):
        shutil.copyfile(source, evidence / name)
    runtime.offline()
    if remaining(deadline, 180) < 900:
        raise TimeoutError("Fewer than fifteen minutes remain for the complete diagnostic")
    os.environ["PYTHONPATH"] = str(folder)
    cutoff = (datetime.now(timezone.utc) + timedelta(seconds=remaining(deadline, 180))).isoformat()
    command = [sys.executable, "-u", str(stage / "dev_diagnostic.py"), "--bundle", str(folder),
               "--base", str(base), "--tokenizer", str(base), "--inputs", str(Path("/input") / settings["inputs_name"]),
               "--adapter", str(stage / "training/adapter"), "--output", str(evidence / "diagnostic"),
               "--deadline-utc", cutoff]
    emit("diagnostic_started", command=command)
    subprocess.run(command, check=True, timeout=remaining(deadline, 180))
    run = json.loads((evidence / "diagnostic/run.json").read_text("utf-8"))
    results = [json.loads(line) for line in (evidence / "diagnostic/predictions.jsonl").read_text("utf-8").splitlines()]
    if run.get("status") != "completed" or run.get("completed_outputs") != 96 or len(results) != 96:
        raise ValueError("Diagnostic child did not complete all 96 first attempts")
    emit("diagnostic_finished")


def specification(run_id=None):
    """Pure preparation; the execution owner must separately admit cost and references."""
    run_id = uuid.uuid4().hex if run_id is None else run_id
    if not isinstance(run_id, str) or not re.fullmatch(r"[a-f0-9]{32}", run_id):
        raise ValueError("Fresh hexadecimal run ID required")
    spec, hashes = hf_preflight.specification("cuda")
    prefix, marker, _ = hf_preflight.BOOTSTRAP.partition("device = sys.argv[2]\n")
    if not marker:
        raise ValueError("Bootstrap boundary changed")
    scripts = {}
    for name in ("dev_diagnostic.py", "palref_eval.py"):
        data = Path(__file__).with_name(name).read_bytes()
        scripts[name] = {"sha256": hashlib.sha256(data).hexdigest(), "content": base64.b64encode(data).decode("ascii")}
    if scripts["palref_eval.py"]["sha256"] != PALREF_RUNNER_SHA256:
        raise ValueError("Frozen PAL-REF helper changed")
    settings = dict(run_id=run_id, bundle_name=BUNDLE_NAME, bundle_sha256=BUNDLE_SHA256,
                    inputs_name=INPUTS_NAME, inputs_sha256=INPUTS_SHA256,
                    trained_manifest_sha256=TRAINED_MANIFEST_SHA256, bootstrap_hashes=hashes,
                    script_hashes={name: value["sha256"] for name, value in scripts.items()})
    header = "import base64,hashlib,json,os,re,signal,stat,sys,tempfile,time,zipfile\nfrom pathlib import Path,PurePosixPath\n"
    for function in (hf_convert.file_sha256, hf_convert.safe_extract, hf_convert.remaining,
                     hf_train.emit, hf_baseline.publish, diagnostic_body):
        header += inspect.getsource(function) + "\n"
    body = '''
settings = SETTINGS
deadline = time.monotonic() + 3000
def interrupted(signum, frame):
    raise TimeoutError('Diagnostic interrupted or computation deadline reached')
signal.signal(signal.SIGTERM, interrupted)
signal.signal(signal.SIGALRM, interrupted)
signal.alarm(2820)
output = Path('/output')
output.mkdir(parents=True, exist_ok=True)
if any(output.iterdir()):
    raise ValueError('Fresh output prefix required')
stage = Path(tempfile.mkdtemp(prefix='pahlavi-qualitydev-'))
evidence = stage / 'evidence'
evidence.mkdir()
identity = dict(settings, operation='dev_instruction_diagnostic', diagnostic_status='incomplete',
                training_performed=False, quality_validated=False, local_model_verified=False)
try:
    import shutil
    if shutil.disk_usage('/tmp').free < 90 * 1024**3:
        raise ValueError('Diagnostic requires 90 GiB ephemeral disk')
    if file_sha256(Path('/input') / settings['inputs_name']) != settings['inputs_sha256']:
        raise ValueError('Source-only input checksum mismatch')
    safe_extract(Path('/input') / settings['bundle_name'], stage / 'bundle', settings['bundle_sha256'], 128 * 1024**2)
    for name, expected in settings['bootstrap_hashes'].items():
        if file_sha256(stage / 'bundle' / name) != expected:
            raise ValueError('Frozen bootstrap/bundle mismatch: ' + name)
    for name, entry in SCRIPTS.items():
        data = base64.b64decode(entry['content'])
        if hashlib.sha256(data).hexdigest() != entry['sha256']:
            raise ValueError('Runner source mismatch')
        (stage / name).write_bytes(data)
    emit('bootstrap_started')
    exec(BOOTSTRAP_PREFIX)
    emit('bootstrap_complete')
    diagnostic_body(settings, stage, deadline, evidence)
    identity['diagnostic_status'] = 'complete'
except BaseException as error:
    identity.update(error_type=type(error).__name__, error=str(error))
    emit('diagnostic_incomplete', **identity)
finally:
    signal.alarm(max(1, int(max(0, deadline - time.monotonic()))))
    (evidence / 'diagnostic-status.json').write_text(json.dumps(identity, indent=2) + '\\n')
    result = publish(evidence, output, deadline, identity)
    emit('ready_to_persist', **result)
    time.sleep(max(0, min(300, deadline - time.monotonic())))
    emit('persistence_window_expired', remote_inventory_verified=False)
    signal.alarm(0)
'''.replace("SETTINGS", repr(settings)).replace("SCRIPTS", repr(scripts)).replace("BOOTSTRAP_PREFIX", repr(prefix))
    spec["command"][3] = header + body
    spec["flavor"], spec["timeout"] = "a100-large", "55m"
    spec["labels"].update(purpose="dev-instruction-diagnostic", trial_id=run_id)
    spec["env"].update(HF_XET_CACHE="/tmp/pahlavi-xet-cache", OMP_NUM_THREADS="8", MKL_NUM_THREADS="8")
    from huggingface_hub import HfApi, Volume
    spec["volumes"] = [Volume(type="bucket", source=hf_train.BUCKET, path="inputs", mount_path="/input", read_only=True),
        Volume(type="bucket", source=hf_train.BUCKET, path=TRAINED_PREFIX, mount_path="/trained", read_only=True),
        Volume(type="bucket", source=hf_train.BUCKET, path="diagnostics/" + run_id, mount_path="/output", read_only=False)]
    compile(spec["command"][3], "hf-dev-diagnostic", "exec")
    inspect.signature(HfApi.run_job).bind(None, **spec)
    return spec, dict(settings, output_prefix="diagnostics/" + run_id,
                      command_sha256=hashlib.sha256(spec["command"][3].encode()).hexdigest())
