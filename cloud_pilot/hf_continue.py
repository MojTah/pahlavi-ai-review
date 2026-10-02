"""Prepare one evidenced checkpoint-20 continuation and final PAL-REF run; never launch."""
import argparse

import hashlib

import inspect

import json

import math

from pathlib import Path, PurePosixPath

import re

import uuid

import zipfile

try:
    from . import hf_train, hf_preflight, hf_convert
except ImportError:
    import hf_train
    import hf_preflight
    import hf_convert

INPUTS_SHA256 = "0616b50838339e9b520f06fe8b2ed9c0fd9b399b67c8f68cd680a62115a12f37"

BASELINE_RUN_SHA256 = "0dfd30cdafe60572555683300dc6676b51cdf7d9bf2ef0635e05adebcb6a0e1e"
BASELINE_PREDICTIONS_SHA256 = "38b7e8a85895a2cf68571358eef9685fe559b9aab2042d5dc33572ce309e5999"
EVALUATOR_SHA256 = "050a38880c68113ca5e5ebc4abd26945d05959eeda52f5df64f00292acfe4a49"
BASELINE_SECONDS = 170.8188028060831
FINAL_EVALUATION_SECONDS = 420
MODEL_LOAD_SECONDS = 180
EXPORT_RESERVE_SECONDS = 300
TRAINING_TAIL_SECONDS = EXPORT_RESERVE_SECONDS + FINAL_EVALUATION_SECONDS

file_sha256, remaining, emit = hf_convert.file_sha256, hf_convert.remaining, hf_train.emit

def admit(record, minutes):
    """The controller supplies external facts only after their evidence exists."""
    fields = {"schema_version", "full_training_authorized", "cloud_controls_verified", "evidence", "max_minutes",
              "prior_cumulative_compute_usd", "canary_elapsed_minutes", "remaining_aggregate_a100_minutes", "budget_ceiling_usd"}
    if set(record) != fields or record["schema_version"] != 1:
        raise ValueError("Unexpected controller admission schema")
    if record["full_training_authorized"] is not True or record["cloud_controls_verified"] is not True:
        raise ValueError("Controller authorization/control evidence is missing")
    evidence = record["evidence"]
    if not isinstance(evidence, dict) or set(evidence) != {"authorization", "cloud_controls", "canary_terminal", "baseline_reported"} or any(
            not isinstance(value, str) or not value.strip() for value in evidence.values()):
        raise ValueError("Explicit evidence references are required")
    for name in ("prior_cumulative_compute_usd", "canary_elapsed_minutes", "remaining_aggregate_a100_minutes", "budget_ceiling_usd"):
        if type(record[name]) not in (int, float) or not math.isfinite(record[name]) or record[name] < 0:
            raise ValueError("Invalid controller resource measurement")
    if (type(minutes) is not int or not 11 <= minutes <= 150 or type(record["max_minutes"]) is not int
            or record["max_minutes"] != minutes or record["budget_ceiling_usd"] not in (10, 25)
            or minutes > record["remaining_aggregate_a100_minutes"]
            or record["prior_cumulative_compute_usd"] + minutes * 2.5 / 60 > record["budget_ceiling_usd"]):
        raise ValueError("Continuation exceeds the controller's aggregate time or explicitly authorized USD 10/25 envelope")
    if record["prior_cumulative_compute_usd"] + minutes * 2.5 / 60 + 0.75 > record["budget_ceiling_usd"]:
        raise ValueError("Native timeout would consume the USD 0.75 cash reserve")

def canary_steps(state, expected_total_steps=312):
    if type(expected_total_steps) is not int or expected_total_steps <= 20:
        raise ValueError("An integer full schedule greater than the 20-step canary is required")
    if (type(state.get("global_step")) is not int or state["global_step"] != 20
            or type(state.get("max_steps")) is not int or state["max_steps"] != expected_total_steps):
        raise ValueError("Expected fresh checkpoint step 20 of the declared full schedule")
    return expected_total_steps - state["global_step"]

def training_schedule(row_count, training, state, expected_total_steps=312):
    """Single-GPU Trainer keeps the final partial accumulation in each epoch."""
    recipe = {"micro_batch_size": 1, "gradient_accumulation_steps": 16, "num_train_epochs": 2}
    if type(row_count) is not int or row_count <= 0 or any(
            type(training.get(key)) is not int or training[key] != value for key, value in recipe.items()):
        raise ValueError("Positive TRAIN row count and frozen batch1/accumulation16/two-epoch recipe required")
    derived = ((row_count + 15) // 16) * 2
    remaining_steps = canary_steps(state, expected_total_steps)
    if derived != expected_total_steps:
        raise ValueError("Declared/checkpoint schedule differs from the verified TRAIN row count")
    return {"train_rows": row_count, "expected_total_steps": derived, "remaining_steps": remaining_steps}

def projection(metrics, state, available_seconds, expected_total_steps=312):
    remaining_steps = canary_steps(state, expected_total_steps)
    measured = metrics.get("train_runtime")
    if (type(measured) not in (int, float) or not math.isfinite(measured) or measured <= 0
            or type(available_seconds) not in (int, float) or not math.isfinite(available_seconds) or available_seconds <= 0):
        raise ValueError("Measured canary and baseline durations are required")
    forecast = measured / 20 * 1.3 * remaining_steps + FINAL_EVALUATION_SECONDS + EXPORT_RESERVE_SECONDS + MODEL_LOAD_SECONDS
    if forecast > available_seconds:
        raise TimeoutError("Measured continuation projection exceeds the remaining deadline")
    return {"expected_total_steps": expected_total_steps, "remaining_steps": remaining_steps,
            "canary_train_seconds": measured, "baseline_generation_seconds": BASELINE_SECONDS,
            "final_evaluation_allowance_seconds": FINAL_EVALUATION_SECONDS,
            "model_reload_reserve_seconds": MODEL_LOAD_SECONDS, "model_reload_reserve_is_estimate": True,
            "safety_multiplier": 1.3, "export_reserve_seconds": EXPORT_RESERVE_SECONDS, "projected_seconds": forecast,
            "available_seconds": available_seconds}

def pre_submission_check(metrics, state, admission, setup_reserve_seconds, expected_total_steps=312):
    """Pure local check of recovered evidence before any upload or paid launch."""
    minutes = admission["max_minutes"]
    admit(admission, minutes)
    if type(setup_reserve_seconds) not in (int, float) or not math.isfinite(setup_reserve_seconds) or setup_reserve_seconds < 0:
        raise ValueError("A finite nonnegative setup reserve is required")
    # Keep USD 0.75 outside the worst-case compute envelope for other charges.
    worst_compute = admission["prior_cumulative_compute_usd"] + minutes * 2.5 / 60
    forecast = projection(metrics, state, (minutes - 5) * 60 - setup_reserve_seconds, expected_total_steps)
    return {"status": "locally_admitted_not_submitted", **forecast,
            "native_timeout_minutes": minutes, "internal_timeout_minutes": minutes - 5,
            "setup_reserve_seconds": setup_reserve_seconds, "worst_cumulative_compute_usd": worst_compute,
            "cash_reserve_usd": 0.75, "budget_ceiling_usd": admission["budget_ceiling_usd"]}

def verify_canary(root, expected, run_id):
    if file_sha256(root / "manifest.json") != expected:
        raise ValueError("Canary manifest checksum mismatch")
    manifest = json.loads((root / "manifest.json").read_text("utf-8"))
    files = manifest.get("files", {})
    if manifest.get("run_id") != run_id or manifest.get("canary_compute_pass") is not True or manifest.get("global_step") != 20 or not files:
        raise ValueError("Passing canary manifest at step 20 required")
    if {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()} != set(files) | {"manifest.json"}:
        raise ValueError("Canary remote inventory differs from frozen manifest")
    for name, entry in files.items():
        path = root / name
        if (not path.resolve().is_relative_to(root.resolve()) or path.is_symlink() or "\\" in name
                or PurePosixPath(name).is_absolute() or any(part in {"", ".", ".."} for part in name.split("/"))
                or path.stat().st_size != entry["bytes"] or file_sha256(path) != entry["sha256"]):
            raise ValueError("Canary full roundtrip verification failed: " + name)
    return manifest

def verify_adapter(training):
    import torch
    from safetensors import safe_open
    adapter, checkpoint = training / "canary-adapter", training / "checkpoint-20"
    if json.loads((adapter / "adapter_config.json").read_text("utf-8")) != json.loads((checkpoint / "adapter_config.json").read_text("utf-8")):
        raise ValueError("Canary adapter/checkpoint configurations differ")
    with safe_open(adapter / "adapter_model.safetensors", framework="pt", device="cpu") as left, safe_open(
            checkpoint / "adapter_model.safetensors", framework="pt", device="cpu") as right:
        if not left.keys() or set(left.keys()) != set(right.keys()):
            raise ValueError("Canary adapter/checkpoint tensor keys differ")
        for key in left.keys():
            a, b = left.get_tensor(key), right.get_tensor(key)
            if a.dtype != b.dtype or a.shape != b.shape or not torch.isfinite(a).all() or not torch.equal(a, b):
                raise ValueError("Canary adapter/checkpoint tensors differ or are nonfinite: " + key)

def export_evidence(source, output, deadline, identity):
    """Select one complete checkpoint; write final names once, then freeze the manifest."""
    import shutil
    required = {"trainer_state.json", "optimizer.pt", "scheduler.pt", "rng_state.pth", "adapter_config.json", "adapter_model.safetensors"}
    checkpoints = []
    for path in (source / "training").glob("checkpoint-*"):
        if re.fullmatch(r"checkpoint-\d+", path.name) and all((path / name).is_file() and (path / name).stat().st_size for name in required):
            try:
                step = json.loads((path / "trainer_state.json").read_text("utf-8"))["global_step"]
                if step == int(path.name.split("-")[1]):
                    for name in ("optimizer.pt", "scheduler.pt", "rng_state.pth"):
                        with zipfile.ZipFile(path / name) as archive:
                            if archive.testzip() is not None:
                                raise ValueError("Incomplete checkpoint archive")
                    checkpoints.append((step, path.name))
            except (ValueError, KeyError, OSError, zipfile.BadZipFile):
                pass
    latest = max(checkpoints)[1] if checkpoints else None
    files = {}
    for path in sorted(source.rglob("*")):
        if path.is_symlink() or not path.resolve().is_relative_to(source.resolve()):
            raise ValueError("Unsafe evidence path")
        if not path.is_file() or path.name.endswith(".tmp"):
            continue
        relative = path.relative_to(source)
        if "canary-adapter" in relative.parts or any(part.startswith("checkpoint-") and part != latest for part in relative.parts):
            continue
        if sum(entry["bytes"] for entry in files.values()) + path.stat().st_size > identity.get("max_export_bytes", 16 * 1024**2):
            raise ValueError("Continuation evidence exceeds the observed-canary-derived export bound")
        remaining(deadline)
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        entry = {"bytes": path.stat().st_size, "sha256": file_sha256(path)}
        with path.open("rb") as incoming, target.open("xb") as outgoing:
            shutil.copyfileobj(incoming, outgoing, 8 * 1024**2)
        files[relative.as_posix()] = entry
        emit("artifact_closed", path=relative.as_posix(), **entry)
    manifest = {"schema_version": 1, **identity, "files": files, "latest_optimizer_checkpoint": latest,
                "automatic_full_resume_supported": False,
                "remote_inventory_verified": False, "cross_job_sha256_verified": False, "quality_validated": False}
    payload = (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode()
    with (output / "manifest.json").open("xb") as stream:
        stream.write(payload)
    return {"manifest": manifest, "manifest_file": "manifest.json", "manifest_bytes": len(payload),
            "manifest_sha256": hashlib.sha256(payload).hexdigest()}

def readiness_for(checks, controls):
    required = {"linux_container_verified", "stage_dev_ready", "base_weights_verified", "transfer_roundtrip_verified", "adapter_export_roundtrip_verified"}
    if set(checks) != required or any(not isinstance(checks[key], dict) or checks[key].get("verified") is not True for key in required):
        raise ValueError("Every technical readiness flag requires its own completed evidence check")
    if controls["full_training_authorized"] is not True or controls["cloud_controls_verified"] is not True:
        raise ValueError("Missing external authorization or controller verification")
    return {"full_training_authorized": controls["full_training_authorized"],
            "cloud_controls_verified": controls["cloud_controls_verified"], "local_model_verified": False,
            "linux_container_verified": checks["linux_container_verified"]["verified"],
            "stage_dev_ready": checks["stage_dev_ready"]["verified"],
            "base_weights_verified": checks["base_weights_verified"]["verified"],
            "transfer_roundtrip_verified": checks["transfer_roundtrip_verified"]["verified"],
            "adapter_export_roundtrip_verified": checks["adapter_export_roundtrip_verified"]["verified"]}


def continuation(settings, stage, deadline, evidence, identity):
    import importlib.util
    import os
    import signal
    import shutil
    import subprocess
    import sys
    import time
    from datetime import datetime, timezone, timedelta
    signal.alarm(min(180, max(1, int(remaining(deadline, EXPORT_RESERVE_SECONDS)))))
    folder, base, canary = stage / "bundle", stage / "base", Path("/canary")
    sys.path.insert(0, str(folder))
    import runtime
    import bundle
    bundle.verify(folder)
    controls = json.loads((Path("/input") / settings["admission_name"]).read_text("utf-8"))
    admit(controls, settings["max_minutes"])
    checks = {}
    manifest = verify_canary(canary, settings["canary_manifest_sha256"], settings["canary_run_id"])
    if manifest["bundle_sha256"] != settings["bundle_sha256"] or manifest["bootstrap_hashes"] != settings["bootstrap_hashes"]:
        raise ValueError("Canary used a different immutable bundle/runtime")
    total_canary_bytes = sum(entry["bytes"] for entry in manifest["files"].values())
    identity["max_export_bytes"] = min(4 * 1024**3, total_canary_bytes + 64 * 1024**2)
    checks["transfer_roundtrip_verified"] = {"verified": True, "manifest_sha256": settings["canary_manifest_sha256"], "files": len(manifest["files"])}
    current = runtime.gpu_admission()
    saved = json.loads((canary / "training/environment.json").read_text("utf-8"))
    if current != saved:
        raise ValueError("GPU/runtime identity differs from the saved canary environment")
    emit("gpu_and_roundtrip_verified", environment=current)
    checks["linux_container_verified"] = {"verified": True, "environment": current}
    training = evidence / "training"
    shutil.copytree(canary / "training", training)
    runtime.checked_files(training, {name[len("training/"):]: entry for name, entry in manifest["files"].items() if name.startswith("training/")})
    runtime.resume_checkpoint(training / "checkpoint-20", training)
    verify_adapter(training)
    checks["adapter_export_roundtrip_verified"] = {"verified": True, "check": "Remote SHA-verified config and all finite adapter tensors equal checkpoint20"}
    state = json.loads((training / "checkpoint-20/trainer_state.json").read_text("utf-8"))
    metrics = json.loads((training / "metrics.json").read_text("utf-8"))
    contract = runtime.contract_at(folder / "contract.json")
    train_rows = [json.loads(line) for line in (folder / "train.jsonl").read_text("utf-8").splitlines()]
    schedule = training_schedule(len(train_rows), contract["training"], state, settings["expected_total_steps"])
    provenance = json.loads((training / "provenance.json").read_text("utf-8"))
    if provenance["train_sha256"] != file_sha256(folder / "train.jsonl") or provenance["training"] != contract["training"]:
        raise ValueError("Canary TRAIN identity or recipe differs from the verified continuation bundle")
    identity.update(expected_total_steps=schedule["expected_total_steps"], completed_global_step=state["global_step"])
    emit("training_schedule_verified", **schedule)
    for path, name in ((canary / "manifest.json", "canary-manifest.json"), (training / "provenance.json", "canary-provenance.json"),
                       (folder / "contract.json", "original-contract.json"), (folder / "manifest.json", "original-bundle-manifest.json")):
        shutil.copyfile(path, evidence / name)
    evaluator = stage / "palref_eval.py"
    shutil.copyfile(Path("/input") / settings["evaluator_name"], evaluator)
    os.environ["PYTHONPATH"] = str(folder)
    spec = importlib.util.spec_from_file_location("frozen_palref_evaluator", evaluator)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    panel = Path("/input") / settings["inputs_name"]
    panel_rows = module.read_inputs(panel)
    overlap = {row["work_id"] for row in train_rows} & {row["work_id"] for row in panel_rows}
    if overlap:
        raise ValueError("Training work intersects frozen PAL-REF work: " + repr(sorted(overlap)))
    checks["stage_dev_ready"] = {"verified": True, "meaning": "Frozen evaluation protocol ready, not a score threshold",
        "source_inputs_sha256": settings["inputs_sha256"], "evaluator_sha256": settings["evaluator_sha256"],
        "baseline_run_sha256": BASELINE_RUN_SHA256, "baseline_predictions_sha256": BASELINE_PREDICTIONS_SHA256,
        "training_work_overlap": [], "holdout_bundle_verification": "passed"}

    def child(phase, command, reserve=300):
        emit(phase + "_started", command=command)
        subprocess.run(command, check=True, timeout=remaining(deadline, reserve))
        emit(phase + "_complete")

    def utc(reserve=300):
        return (datetime.now(timezone.utc) + timedelta(seconds=remaining(deadline, reserve))).isoformat()

    signal.alarm(max(1, int(remaining(deadline, EXPORT_RESERVE_SECONDS))))
    child("base_download", [sys.executable, "-u", str(folder / "fetch_base.py"), "--out", str(base), "--download"])
    # The downloader has just checked every upstream file; the frozen training driver checks again at use.
    original_base = json.loads((base / "provenance.json").read_text("utf-8"))
    if original_base["files"] != json.loads((training / "provenance.json").read_text("utf-8"))["base_files"]:
        raise ValueError("Original model files differ from the saved canary")
    runtime.offline()
    checks["base_weights_verified"] = {"verified": True, "check": "Original pinned download completed upstream checksum checks and matches canary base_files"}
    common = ["--bundle", str(folder), "--base", str(base), "--tokenizer", str(base), "--inputs", str(panel)]
    forecast = projection(metrics, state, remaining(deadline), settings["expected_total_steps"])
    emit("continuation_projection_admitted", **forecast)
    (evidence / "projection.json").write_text(json.dumps(forecast, indent=2) + "\n")
    if contract.get("execution_policy") != runtime.CLOUD_FIRST_POLICY or set(contract["readiness"]) != runtime.READINESS:
        raise ValueError("Unexpected cloud-first readiness contract")
    contract["readiness"] = readiness_for(checks, controls)
    (evidence / "readiness-evidence.json").write_text(json.dumps(checks, indent=2) + "\n")
    (folder / "contract.json").write_text(json.dumps(contract, indent=2) + "\n")
    names = json.loads((folder / "manifest.json").read_text("utf-8"))["files"]
    (folder / "manifest.json").write_bytes(bundle.manifest_for({name: folder / name for name in names}, "training-bundle"))
    bundle.verify(folder)
    shutil.copyfile(folder / "contract.json", evidence / "resumed-contract.json")
    shutil.copyfile(folder / "manifest.json", evidence / "resumed-bundle-manifest.json")
    shutil.copyfile(Path("/input") / settings["admission_name"], evidence / "controller-admission.json")
    child("full_resume", [sys.executable, "-u", str(folder / "runtime.py"), "train", "--bundle", str(folder),
          "--contract", str(folder / "contract.json"), "--base", str(base), "--output", str(training),
          "--full", "--resume", str(training / "checkpoint-20"), "--deadline-utc", utc(TRAINING_TAIL_SECONDS)], TRAINING_TAIL_SECONDS)
    status = json.loads((training / "status.json").read_text("utf-8"))
    if type(status.get("global_step")) is int:
        identity["completed_global_step"] = status["global_step"]
    if (status.get("status") != "training_complete" or type(status.get("global_step")) is not int
            or status["global_step"] != settings["expected_total_steps"]):
        raise ValueError("Full unchanged schedule did not complete the expected total steps")
    identity["training_schedule_completed"] = True
    identity["training_reached_step_312"] = settings["expected_total_steps"] == 312
    child("palref_final", [sys.executable, "-u", str(evaluator), *common, "--adapter", str(training / "adapter"),
          "--output", str(evidence / "after"), "--deadline-utc", utc()])
    after = json.loads((evidence / "after/run.json").read_text("utf-8"))
    output_ids = [json.loads(line)["id"] for line in (evidence / "after/predictions.jsonl").read_text("utf-8").splitlines()]
    if (after.get("status") != "completed" or after.get("completed_cases") != 40 or after.get("condition") != "bf16-original-plus-adapter"
            or output_ids != module.IDS):
        raise ValueError("Final PAL-REF inference did not complete forty cases")

try:
    from .training_admission import draft
except ImportError:
    from training_admission import draft


@draft
def specification(bundle_name, bundle_sha256, evaluator_name, evaluator_sha256, inputs_name, inputs_sha256,
                  canary_run_id, canary_manifest_sha256, admission_name, admission_sha256, max_minutes, run_id=None,
                  expected_total_steps=312):
    if type(expected_total_steps) is not int or expected_total_steps <= 20:
        raise ValueError("An integer full schedule greater than the 20-step canary is required")
    run_id = uuid.uuid4().hex if run_id is None else run_id
    for value in (run_id, canary_run_id):
        if not isinstance(value, str) or not re.fullmatch(r"[a-f0-9]{32}", value):
            raise ValueError("Expected 32 lowercase hexadecimal run IDs")
    if run_id == canary_run_id or type(max_minutes) is not int or not 11 <= max_minutes <= 150:
        raise ValueError("Distinct run and a bounded 11..150 minute native timeout required")
    names = (bundle_name, evaluator_name, inputs_name, admission_name)
    if len(set(names)) != 4 or any(not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name) for name in names):
        raise ValueError("Four distinct immutable input basenames required")
    for checksum in (bundle_sha256, evaluator_sha256, inputs_sha256, canary_manifest_sha256, admission_sha256):
        if not isinstance(checksum, str) or not re.fullmatch(r"[a-f0-9]{64}", checksum):
            raise ValueError("Full lowercase SHA-256 values required")
    if inputs_sha256 != INPUTS_SHA256 or evaluator_sha256 != EVALUATOR_SHA256 or evaluator_sha256 != file_sha256(Path(__file__).with_name("palref_eval.py")):
        raise ValueError("Only the frozen source-only PAL-REF evaluator and forty inputs are allowed")
    spec, hashes = hf_preflight.specification("cuda")
    prefix, marker, _ = hf_preflight.BOOTSTRAP.partition("device = sys.argv[2]\n")
    if not marker:
        raise ValueError("Reviewed bootstrap boundary changed")
    settings = dict(zip(("bundle_name", "bundle_sha256", "evaluator_name", "evaluator_sha256", "inputs_name", "inputs_sha256",
                         "canary_run_id", "canary_manifest_sha256", "admission_name", "admission_sha256", "max_minutes", "run_id"),
                        (bundle_name, bundle_sha256, evaluator_name, evaluator_sha256, inputs_name, inputs_sha256,
                         canary_run_id, canary_manifest_sha256, admission_name, admission_sha256, max_minutes, run_id)))
    settings["bootstrap_hashes"] = hashes
    settings["expected_total_steps"] = expected_total_steps
    header = "import hashlib,json,math,os,re,signal,stat,sys,tempfile,time,zipfile\nfrom pathlib import Path,PurePosixPath\n"
    for name in ("BASELINE_SECONDS", "FINAL_EVALUATION_SECONDS", "MODEL_LOAD_SECONDS", "EXPORT_RESERVE_SECONDS", "TRAINING_TAIL_SECONDS",
                 "BASELINE_RUN_SHA256", "BASELINE_PREDICTIONS_SHA256"):
        header += name + " = " + repr(globals()[name]) + "\n"
    for function in (hf_convert.file_sha256, hf_convert.safe_extract, hf_convert.remaining, hf_train.emit,
                     admit, canary_steps, training_schedule, projection, verify_canary, verify_adapter, export_evidence, readiness_for, continuation):
        header += inspect.getsource(function) + "\n"
    body = '''
settings = SETTINGS
deadline = time.monotonic() + (settings['max_minutes'] - 5) * 60
def interrupted(signum, frame):
    raise TimeoutError('Continuation interrupted or computation deadline reached')
signal.signal(signal.SIGTERM, interrupted)
signal.signal(signal.SIGALRM, interrupted)
signal.alarm((settings['max_minutes'] - 10) * 60)
output = Path('/output')
output.mkdir(parents=True, exist_ok=True)
if any(output.iterdir()):
    raise ValueError('Fresh output prefix required')
stage = Path(tempfile.mkdtemp(prefix='pahlavi-continuation-'))
evidence = stage / 'evidence'
evidence.mkdir()
identity = dict(settings, operation='full_resume_and_palref', continuation_status='incomplete', full_training_completed=False,
                completed_global_step=None, training_schedule_completed=False,
                training_reached_step_312=False, local_model_verified=False, max_export_bytes=16*1024**2)
try:
    import shutil
    if shutil.disk_usage('/tmp').free < 90 * 1024**3:
        raise ValueError('Continuation requires 90 GiB ephemeral disk')
    for key in ('evaluator', 'inputs', 'admission'):
        if file_sha256(Path('/input') / settings[key + '_name']) != settings[key + '_sha256']:
            raise ValueError('Frozen input checksum mismatch: ' + key)
    safe_extract(Path('/input') / settings['bundle_name'], stage / 'bundle', settings['bundle_sha256'], 128 * 1024**2)
    for name, expected in settings['bootstrap_hashes'].items():
        if file_sha256(stage / 'bundle' / name) != expected:
            raise ValueError('Frozen bootstrap and bundle differ: ' + name)
    emit('bootstrap_started')
    exec(BOOTSTRAP_PREFIX)
    emit('bootstrap_complete')
    continuation(settings, stage, deadline, evidence, identity)
    identity.update(continuation_status='complete', full_training_completed=True)
except BaseException as error:
    identity.update(error_type=type(error).__name__, error=str(error))
    emit('continuation_incomplete', **identity)
finally:
    signal.alarm(max(1, int(max(0, deadline - time.monotonic()))))
    (evidence / 'continuation-status.json').write_text(json.dumps(identity, indent=2) + '\\n')
    result = export_evidence(evidence, output, deadline, identity)
    emit('ready_to_persist', **result)
    time.sleep(max(0, min(300, deadline - time.monotonic())))
    emit('persistence_window_expired', remote_inventory_verified=False)
    signal.alarm(0)
'''.replace("SETTINGS", repr(settings)).replace("BOOTSTRAP_PREFIX", repr(prefix))
    spec["command"][3] = header + body
    spec["flavor"], spec["timeout"] = "a100-large", str(max_minutes) + "m"
    spec["labels"].update(purpose="full-resume-palref", trial_id=run_id)
    spec["env"].update(HF_XET_CACHE="/tmp/pahlavi-xet-cache", OMP_NUM_THREADS="8", MKL_NUM_THREADS="8")
    from huggingface_hub import HfApi, Volume
    spec["volumes"] = [Volume(type="bucket", source=hf_train.BUCKET, path="inputs", mount_path="/input", read_only=True),
        Volume(type="bucket", source=hf_train.BUCKET, path="trials/" + canary_run_id, mount_path="/canary", read_only=True),
        Volume(type="bucket", source=hf_train.BUCKET, path="continuations/" + run_id, mount_path="/output", read_only=False)]
    compile(spec["command"][3], "hf-continuation", "exec")
    inspect.signature(HfApi.run_job).bind(None, **spec)
    return spec, dict(settings, output_prefix="continuations/" + run_id,
        command_sha256=hashlib.sha256(spec["command"][3].encode()).hexdigest())

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("bundle-name", "bundle-sha256", "evaluator-name", "evaluator-sha256", "inputs-name", "inputs-sha256",
                 "canary-run-id", "canary-manifest-sha256", "admission-name", "admission-sha256"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--max-minutes", type=int, required=True)
    parser.add_argument("--expected-total-steps", type=int, default=312)
    parser.add_argument("--run-id")
    spec, provenance = specification(**vars(parser.parse_args()))
    spec["volumes"] = [volume.to_dict() for volume in spec["volumes"]]
    print(json.dumps({"status": "prepared_not_submitted", "spec": spec, "provenance": provenance}))

if __name__ == "__main__":
    main()
