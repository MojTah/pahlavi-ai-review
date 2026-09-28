"""Prepare one fixed plain/assisted comparison job; never authenticate or submit."""
import base64
import hashlib
import inspect
import json
from pathlib import Path
import re
import uuid

from . import dev_assisted, hf_baseline, hf_convert, hf_preflight, hf_train

BUNDLE_NAME = "cloud-pilot-qualified-20260927.zip"
BUNDLE_SHA256 = "41fbbe703b7eb3cfc471c83e344ede16c1e92cae8a604b91f638a57d856477b9"
TRAINED_PREFIX = "continuations/1ae0f16dae9c4dffa36d15a24345fded"
SOURCE_IDENTITY_SHA256 = "b0d6d51fe7603d4a955be4dec41b551100a4ca401b5d1d8a1a5a4c8d5427f8ce"
INPUT_FILES = {
    "inputs": ("qualitydev1-06ac58310bf6.jsonl", dev_assisted.frozen.INPUTS_SHA256),
    "evidence": ("qualitydev-qualified-1d5e02cfb91d.jsonl", dev_assisted.EVIDENCE_SHA256),
    "audit": ("qualitydev-qualified-audit-193f49f54dd1.json", dev_assisted.AUDIT_SHA256),
}


def fetch_qwen(identity_path, base, deadline):
    """Server-only download of publisher-pinned bytes, bounded by the job alarm."""
    from huggingface_hub import hf_hub_download
    identity = json.loads(identity_path.read_text("utf-8"))
    entries = dict(identity["files"])
    entries.update({item["rfilename"]: {"bytes": item["size"], "sha256": item["lfs"]["sha256"]}
                    for item in identity["weight_shards_metadata_only"]})
    base.mkdir(exist_ok=False)
    for name, entry in sorted(entries.items()):
        remaining(deadline, 180)
        if Path(name).name != name:
            raise ValueError("Flat pinned Qwen snapshot required")
        emit("base_file_download_started", name=name, bytes=entry["bytes"])
        path = Path(hf_hub_download(identity["model_id"], name, revision=identity["revision"],
                                   token=False, local_dir=base))
        if path.stat().st_size != entry["bytes"] or file_sha256(path) != entry["sha256"]:
            raise ValueError("Pinned Qwen artifact checksum mismatch: " + name)
        emit("base_file_verified", name=name)


def comparison_body(settings, stage, deadline, evidence):
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
    extra = []
    if settings["family"] == "gemma":
        trained = Path("/trained")
        if file_sha256(trained / "manifest.json") != settings["trained_manifest_sha256"]:
            raise ValueError("Qualified trained manifest differs")
        manifest = json.loads((trained / "manifest.json").read_text("utf-8"))
        if (manifest.get("full_training_completed") is not True
                or manifest.get("training_schedule_completed") is not True
                or manifest.get("completed_global_step") != 280):
            raise ValueError("Completed qualified step280 required")
        for name in ("training/adapter/adapter_config.json", "training/adapter/adapter_model.safetensors",
                     "training/provenance.json", "training/status.json"):
            source, target, entry = trained / name, stage / name, manifest["files"][name]
            remaining(deadline, 180)
            if source.stat().st_size != entry["bytes"] or file_sha256(source) != entry["sha256"]:
                raise ValueError("Qualified cloud artifact mismatch: " + name)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            if file_sha256(target) != entry["sha256"]:
                raise ValueError("Qualified server copy differs: " + name)
        shutil.copyfile(trained / "manifest.json", evidence / "trained-manifest.json")
        emit("base_download_started")
        subprocess.run([sys.executable, "-u", str(folder / "fetch_base.py"), "--out", str(base), "--download"],
                       check=True, timeout=remaining(deadline, 180))
        shutil.copyfile(base / "provenance.json", evidence / "base-provenance.json")
        extra = ["--bundle", str(folder), "--tokenizer", str(base), "--adapter", str(stage / "training/adapter")]
    else:
        emit("base_download_started")
        identity_path = stage / "qwen-source-identity.json"
        fetch_qwen(identity_path, base, deadline)
        shutil.copyfile(identity_path, evidence / "qwen-source-identity.json")
        extra = ["--source-identity", str(identity_path)]
    emit("base_download_verified")
    shutil.copyfile(folder / "manifest.json", evidence / "bundle-manifest.json")
    runtime.offline()
    if remaining(deadline, 180) < 900:
        raise TimeoutError("Fewer than fifteen minutes remain for the comparison")
    os.environ["PYTHONPATH"] = str(folder)
    cutoff = (datetime.now(timezone.utc) + timedelta(seconds=remaining(deadline, 180))).isoformat()
    command = [sys.executable, "-u", str(stage / settings["runner"]), "--base", str(base),
               "--output", str(evidence / "comparison"), "--deadline-utc", cutoff, *extra]
    for key, (name, _) in settings["input_files"].items():
        command.extend(["--" + key, str(Path("/input") / name)])
    emit("comparison_started", family=settings["family"])
    subprocess.run(command, check=True, timeout=remaining(deadline, 180))
    run = json.loads((evidence / "comparison/run.json").read_text("utf-8"))
    results = [json.loads(line) for line in (evidence / "comparison/predictions.jsonl").read_text("utf-8").splitlines()]
    if run.get("status") != "completed" or run.get("completed_outputs") != 48 or len(results) != 48:
        raise ValueError("Comparison did not complete all 48 first attempts")
    emit("comparison_finished", family=settings["family"])


def specification(family, run_id=None):
    if family not in {"gemma", "qwen"}:
        raise ValueError("Only the two predeclared model families are admitted")
    run_id = uuid.uuid4().hex if run_id is None else run_id
    if not isinstance(run_id, str) or not re.fullmatch(r"[a-f0-9]{32}", run_id):
        raise ValueError("Fresh hexadecimal run ID required")
    spec, hashes = hf_preflight.specification("cuda")
    prefix, marker, _ = hf_preflight.BOOTSTRAP.partition("device = sys.argv[2]\n")
    if not marker:
        raise ValueError("Bootstrap boundary changed")
    names = ["dev_assisted.py", "dev_diagnostic.py", "palref_eval.py"]
    if family == "qwen":
        names += ["dev_qwen_assisted.py", "qwen_presence.py"]
    scripts = {}
    for name in names:
        data = Path(__file__).with_name(name).read_bytes()
        scripts[name] = {"sha256": hashlib.sha256(data).hexdigest(), "content": base64.b64encode(data).decode("ascii")}
    if scripts["palref_eval.py"]["sha256"] != dev_assisted.PROTOCOL_SHA256:
        raise ValueError("Frozen PAL-REF helper changed")
    if family == "qwen":
        data = (Path(__file__).resolve().parents[1] / "experiments/dev-assisted-qualified-20260927/qwen-source-identity.json").read_bytes()
        if hashlib.sha256(data).hexdigest() != SOURCE_IDENTITY_SHA256:
            raise ValueError("Qwen publisher identity changed")
        scripts["qwen-source-identity.json"] = {"sha256": SOURCE_IDENTITY_SHA256, "content": base64.b64encode(data).decode("ascii")}
    settings = dict(run_id=run_id, family=family, bundle_name=BUNDLE_NAME, bundle_sha256=BUNDLE_SHA256,
        input_files=INPUT_FILES, trained_manifest_sha256=dev_assisted.ADAPTER_MANIFEST_SHA256 if family == "gemma" else None,
        bootstrap_hashes=hashes, script_hashes={name: value["sha256"] for name, value in scripts.items()},
        runner="dev_assisted.py" if family == "gemma" else "dev_qwen_assisted.py")
    header = "import base64,hashlib,json,os,re,signal,stat,sys,tempfile,time,zipfile\nfrom pathlib import Path,PurePosixPath\n"
    for function in (hf_convert.file_sha256, hf_convert.safe_extract, hf_convert.remaining,
                     hf_train.emit, hf_baseline.publish, fetch_qwen, comparison_body):
        header += inspect.getsource(function) + "\n"
    body = '''
settings = SETTINGS
deadline = time.monotonic() + 3000
def interrupted(signum, frame):
    raise TimeoutError('Comparison interrupted or computation deadline reached')
signal.signal(signal.SIGTERM, interrupted)
signal.signal(signal.SIGALRM, interrupted)
signal.alarm(2820)
output = Path('/output')
output.mkdir(parents=True, exist_ok=True)
if any(output.iterdir()):
    raise ValueError('Fresh output prefix required')
stage = Path(tempfile.mkdtemp(prefix='pahlavi-assisted-'))
evidence = stage / 'evidence'
evidence.mkdir()
identity = dict(settings, operation='dev_plain_assisted', comparison_status='incomplete',
                training_performed=False, quality_validated=False, local_model_verified=False)
try:
    import shutil
    if shutil.disk_usage('/tmp').free < 90 * 1024**3:
        raise ValueError('Comparison requires 90 GiB ephemeral disk')
    for name, expected in settings['input_files'].values():
        if file_sha256(Path('/input') / name) != expected:
            raise ValueError('Frozen source/TRAIN evidence mismatch: ' + name)
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
    comparison_body(settings, stage, deadline, evidence)
    identity['comparison_status'] = 'complete'
except BaseException as error:
    identity.update(error_type=type(error).__name__, error=str(error))
    emit('comparison_incomplete', **identity)
finally:
    signal.alarm(max(1, int(max(0, deadline - time.monotonic()))))
    (evidence / 'comparison-status.json').write_text(json.dumps(identity, indent=2) + '\\n')
    result = publish(evidence, output, deadline, identity)
    emit('ready_to_persist', **result)
    time.sleep(max(0, min(300, deadline - time.monotonic())))
    emit('persistence_window_expired', remote_inventory_verified=False)
    signal.alarm(0)
'''.replace("SETTINGS", repr(settings)).replace("SCRIPTS", repr(scripts)).replace("BOOTSTRAP_PREFIX", repr(prefix))
    spec["command"][3] = header + body
    spec["flavor"], spec["timeout"] = "a100-large", "55m"
    spec["labels"].update(purpose="dev-plain-assisted", family=family, trial_id=run_id)
    spec["env"].update(HF_XET_CACHE="/tmp/pahlavi-xet-cache", OMP_NUM_THREADS="8", MKL_NUM_THREADS="8")
    from huggingface_hub import HfApi, Volume
    spec["volumes"] = [Volume(type="bucket", source=hf_train.BUCKET, path="inputs", mount_path="/input", read_only=True)]
    if family == "gemma":
        spec["volumes"].append(Volume(type="bucket", source=hf_train.BUCKET, path=TRAINED_PREFIX, mount_path="/trained", read_only=True))
    spec["volumes"].append(Volume(type="bucket", source=hf_train.BUCKET, path="comparisons/" + run_id, mount_path="/output", read_only=False))
    compile(spec["command"][3], "hf-dev-assisted", "exec")
    inspect.signature(HfApi.run_job).bind(None, **spec)
    return spec, dict(settings, output_prefix="comparisons/" + run_id,
                      command_sha256=hashlib.sha256(spec["command"][3].encode()).hexdigest())
