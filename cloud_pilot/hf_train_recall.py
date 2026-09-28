"""Prepare one qualified Gemma TRAIN-recall job; never authenticate or submit."""
import argparse
import base64
import hashlib
import inspect
import json
from pathlib import Path
import re
import uuid

from . import hf_baseline, hf_convert, hf_dev_assisted, hf_preflight, hf_train

file_sha256, remaining, emit = hf_convert.file_sha256, hf_convert.remaining, hf_train.emit


def fresh_output(output):
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError("Fresh output prefix required; never reuse a previous recall run")


def completed_recall(output, rows, inputs_sha256):
    """Require forty distinct first attempts, preserving runner failures unchanged."""
    run = json.loads((output / "run.json").read_text("utf-8"))
    results = [json.loads(line) for line in (output / "predictions.jsonl").read_text("utf-8").splitlines()]
    ordered = [(row, condition) for index, row in enumerate(rows)
               for condition in (("training", "evaluation") if index % 2 == 0 else ("evaluation", "training"))]
    ids = [row["id"] + ":" + condition for row, condition in ordered]
    if (len(rows) != 20 or len(set(ids)) != 40 or len(results) != 40
            or run.get("status") != "completed" or run.get("scheduled_outputs") != 40
            or run.get("attempted_outputs") != 40 or run.get("completed_outputs") != 40
            or run.get("recorded_outputs") != 40 or "active_output_id" not in run or run["active_output_id"] is not None
            or run.get("completed_cases") != 20 or run.get("unattempted_output_ids") != []
            or run.get("inputs_sha256") != inputs_sha256 or run.get("schedule") != ids
            or [result.get("id") for result in results] != ids):
        raise ValueError("Recall did not complete all 40 distinct first attempts")
    for index, ((row, condition), result) in enumerate(zip(ordered, results)):
        if (result.get("status") not in {"success", "abstain"}
                or result.get("case_id") != row["id"] or result.get("record_id") != row["record_id"]
                or result.get("work_id") != row["work_id"] or result.get("condition") != condition
                or result.get("sequence") != index + 1
                or result.get("input_sha256") != hashlib.sha256(row["source_text"].encode("utf-8")).hexdigest()
                or result.get("identity_sha256") != run.get("identity_sha256")
                or not re.fullmatch(r"[a-f0-9]{64}", str(run.get("identity_sha256")))):
            raise ValueError("Recall first-attempt identity/status mismatch")


def recall_body(settings, stage, deadline, evidence):
    import os
    import shutil
    import subprocess
    import sys
    from datetime import datetime, timedelta, timezone

    folder, base, trained = stage / "bundle", stage / "base", Path("/trained")
    sys.path.insert(0, str(stage))
    sys.path.insert(0, str(folder))
    import bundle
    import runtime
    import train_recall
    bundle.verify(folder)
    rows = train_recall.read_inputs(Path("/input") / settings["inputs_name"],
                                    settings["inputs_sha256"], folder / "train.jsonl")
    if file_sha256(trained / "manifest.json") != settings["trained_manifest_sha256"]:
        raise ValueError("Qualified trained manifest differs")
    manifest = json.loads((trained / "manifest.json").read_text("utf-8"))
    if (manifest.get("full_training_completed") is not True
            or manifest.get("training_schedule_completed") is not True
            or manifest.get("completed_global_step") != 280):
        raise ValueError("Completed qualified step280 required")
    for name, expected in settings["adapter_files"].items():
        source, target, entry = trained / name, stage / name, manifest["files"][name]
        remaining(deadline, 180)
        if (entry["sha256"] != expected or source.stat().st_size != entry["bytes"]
                or file_sha256(source) != expected):
            raise ValueError("Qualified cloud artifact mismatch: " + name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if file_sha256(target) != expected:
            raise ValueError("Qualified server copy differs: " + name)
    shutil.copyfile(trained / "manifest.json", evidence / "trained-manifest.json")
    shutil.copyfile(folder / "manifest.json", evidence / "bundle-manifest.json")
    emit("gpu_admission", environment=runtime.gpu_admission())
    emit("base_download_started")
    subprocess.run([sys.executable, "-u", str(folder / "fetch_base.py"), "--out", str(base), "--download"],
                   check=True, timeout=remaining(deadline, 180))
    shutil.copyfile(base / "provenance.json", evidence / "base-provenance.json")
    runtime.offline()
    emit("base_download_verified")
    os.environ["PYTHONPATH"] = str(folder)
    cutoff = (datetime.now(timezone.utc) + timedelta(seconds=remaining(deadline, 180))).isoformat()
    command = [sys.executable, "-u", str(stage / "train_recall.py"), "--bundle", str(folder),
               "--base", str(base), "--tokenizer", str(base), "--adapter", str(stage / "training/adapter"),
               "--inputs", str(Path("/input") / settings["inputs_name"]),
               "--inputs-sha256", settings["inputs_sha256"], "--output", str(evidence / "recall"),
               "--deadline-utc", cutoff]
    emit("train_recall_started", scheduled_outputs=40)
    subprocess.run(command, check=True, timeout=remaining(deadline, 180))
    completed_recall(evidence / "recall", rows, settings["inputs_sha256"])
    emit("train_recall_finished", completed_outputs=40)


def specification(inputs_name, inputs_sha256, run_id=None):
    """Require an externally frozen source-only input identity; no default input."""
    if (not isinstance(inputs_name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*\.jsonl", inputs_name)
            or not isinstance(inputs_sha256, str) or not re.fullmatch(r"[a-f0-9]{64}", inputs_sha256)):
        raise ValueError("Frozen source-only JSONL basename and full lowercase SHA-256 required")
    run_id = uuid.uuid4().hex if run_id is None else run_id
    if not isinstance(run_id, str) or not re.fullmatch(r"[a-f0-9]{32}", run_id):
        raise ValueError("Fresh hexadecimal run ID required")
    spec, hashes = hf_preflight.specification("cuda")
    prefix, marker, _ = hf_preflight.BOOTSTRAP.partition("device = sys.argv[2]\n")
    if not marker:
        raise ValueError("Reviewed bootstrap boundary changed")
    from . import train_recall
    scripts = {}
    for name in ("train_recall.py", "dev_assisted.py", "dev_diagnostic.py", "palref_eval.py"):
        data = Path(__file__).with_name(name).read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if name in train_recall.HELPER_SHA256 and digest != train_recall.HELPER_SHA256[name]:
            raise ValueError("Frozen recall helper changed: " + name)
        scripts[name] = {"sha256": digest, "content": base64.b64encode(data).decode("ascii")}
    qualified = hf_dev_assisted.dev_assisted
    adapter_files = {"training/adapter/" + name: value for name, value in qualified.ADAPTER_FILES.items()}
    adapter_files.update({"training/" + name: value for name, value in qualified.ADAPTER_METADATA.items()})
    settings = dict(run_id=run_id, inputs_name=inputs_name, inputs_sha256=inputs_sha256,
        bundle_name=hf_dev_assisted.BUNDLE_NAME, bundle_sha256=hf_dev_assisted.BUNDLE_SHA256,
        trained_prefix=hf_dev_assisted.TRAINED_PREFIX, trained_manifest_sha256=qualified.ADAPTER_MANIFEST_SHA256,
        adapter_files=adapter_files, bootstrap_hashes=hashes,
        script_hashes={name: value["sha256"] for name, value in scripts.items()},
        scheduled_outputs=40, compute_seconds=1440, internal_seconds=1620,
        export_reserve_seconds=180, maximum_wait_seconds=180)
    header = "import base64,hashlib,json,os,re,signal,stat,sys,tempfile,time,zipfile\nfrom pathlib import Path,PurePosixPath\n"
    for function in (hf_convert.file_sha256, hf_convert.safe_extract, hf_convert.remaining,
                     hf_train.emit, hf_baseline.publish, fresh_output, completed_recall, recall_body):
        header += inspect.getsource(function) + "\n"
    body = '''
settings = SETTINGS
deadline = time.monotonic() + settings['internal_seconds']
def interrupted(signum, frame):
    raise TimeoutError('TRAIN recall interrupted or computation deadline reached')
signal.signal(signal.SIGTERM, interrupted)
signal.signal(signal.SIGALRM, interrupted)
signal.alarm(settings['compute_seconds'])
output = Path('/output')
fresh_output(output)
stage = Path(tempfile.mkdtemp(prefix='pahlavi-train-recall-'))
evidence = stage / 'evidence'
evidence.mkdir()
identity = dict(settings, operation='qualified_train_recall', recall_status='incomplete',
                evaluation_complete=False, training_performed=False, scoring_performed=False,
                quality_validated=False, local_model_verified=False)
failure = None
try:
    import shutil
    if shutil.disk_usage('/tmp').free < 90 * 1024**3:
        raise ValueError('Recall requires 90 GiB ephemeral disk')
    if file_sha256(Path('/input') / settings['inputs_name']) != settings['inputs_sha256']:
        raise ValueError('Frozen source-only input checksum mismatch')
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
    recall_body(settings, stage, deadline, evidence)
    identity.update(recall_status='complete', evaluation_complete=True)
except BaseException as error:
    failure = error
    identity.update(error_type=type(error).__name__, error=str(error))
    emit('train_recall_incomplete', **identity)
finally:
    signal.alarm(max(1, int(max(0, deadline - time.monotonic()))))
    (evidence / 'recall-status.json').write_text(json.dumps(identity, indent=2) + '\\n', encoding='utf-8')
    result = publish(evidence, output, deadline, identity)
    emit('ready_to_persist', **result)
    time.sleep(max(0, min(settings['maximum_wait_seconds'], deadline - time.monotonic())))
    emit('persistence_window_expired', remote_inventory_verified=False)
    signal.alarm(0)
if failure is not None:
    raise failure
'''.replace("SETTINGS", repr(settings)).replace("SCRIPTS", repr(scripts)).replace("BOOTSTRAP_PREFIX", repr(prefix))
    spec["command"][3] = header + body
    spec["flavor"], spec["timeout"] = "a100-large", "30m"
    spec["labels"].update(purpose="qualified-train-recall", trial_id=run_id)
    spec["env"].update(HF_XET_CACHE="/tmp/pahlavi-xet-cache", OMP_NUM_THREADS="8", MKL_NUM_THREADS="8")
    from huggingface_hub import HfApi, Volume
    spec["volumes"] = [
        Volume(type="bucket", source=hf_train.BUCKET, path="inputs", mount_path="/input", read_only=True),
        Volume(type="bucket", source=hf_train.BUCKET, path=settings["trained_prefix"], mount_path="/trained", read_only=True),
        Volume(type="bucket", source=hf_train.BUCKET, path="train-recall/" + run_id, mount_path="/output", read_only=False),
    ]
    compile(spec["command"][3], "hf-train-recall", "exec")
    inspect.signature(HfApi.run_job).bind(None, **spec)
    return spec, dict(settings, output_prefix="train-recall/" + run_id,
                      command_sha256=hashlib.sha256(spec["command"][3].encode()).hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs-name", required=True)
    parser.add_argument("--inputs-sha256", required=True)
    parser.add_argument("--run-id")
    spec, provenance = specification(**vars(parser.parse_args()))
    spec["volumes"] = [volume.to_dict() for volume in spec["volumes"]]
    print(json.dumps({"status": "prepared_not_submitted", "spec": spec, "provenance": provenance}))


if __name__ == "__main__":
    main()
