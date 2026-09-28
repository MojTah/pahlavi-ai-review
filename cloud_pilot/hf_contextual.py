"""Prepare one bounded contextual pilot job; never authenticate or submit."""
import argparse
import base64
import gzip
import hashlib
import inspect
import json
from pathlib import Path, PurePosixPath
import re
import signal
import stat
import tempfile
import time
import uuid
import zipfile

from . import hf_continue, hf_convert, hf_dev_assisted, hf_preflight, hf_train, hf_train_recall

PACKAGE_NAME = "contextual-pilot-bb3795d9a499.zip"
PACKAGE_SHA256 = "bb3795d9a49927f333e8f565fc1b961c35d7069d9848a9649421ddf233243563"
PACKAGE_MANIFEST_SHA256 = "7920e92e73bb1fee9d606b67c2055c0e114d225252d72bddcfb0071abbe7a7c1"
FROZEN_HELPERS = {"dev_assisted.py": "4334db8c1097c220dbcce75b3d30287a29c43c5482ab71313c3db9cf287fec4d",
                  "dev_diagnostic.py": "9d459482f3b7189cc2109bd68e36d14e77693df64f41574ff952d71bc6725d11"}
file_sha256, safe_extract, remaining = hf_convert.file_sha256, hf_convert.safe_extract, hf_convert.remaining
emit, fresh_output, export_evidence = hf_train.emit, hf_train_recall.fresh_output, hf_continue.export_evidence


def verify_package(folder, expected):
    if file_sha256(folder / "manifest.json") != expected:
        raise ValueError("Contextual package manifest mismatch")
    manifest = json.loads((folder / "manifest.json").read_text("utf-8"))
    files = manifest["files"]
    if {p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file()} != set(files) | {"manifest.json"}:
        raise ValueError("Contextual package inventory mismatch")
    for name, entry in files.items():
        path = folder / name
        if (Path(name).name != name or path.is_symlink() or path.stat().st_size != entry["bytes"]
                or file_sha256(path) != entry["sha256"]):
            raise ValueError("Contextual package file mismatch: " + name)
    return manifest


def completed_contextual(output, rows, settings):
    """Validate closed training/evaluation evidence, never translation quality."""
    run = json.loads((output / "run.json").read_text("utf-8"))
    training = json.loads((output / "training/run.json").read_text("utf-8"))
    evaluation = json.loads((output / "evaluation/run.json").read_text("utf-8"))
    results = [json.loads(s) for s in (output / "evaluation/predictions.jsonl").read_text("utf-8").splitlines()]
    # Caller supplies the exact driver schedule, pinned source-only input rows and arm labels.
    expected = settings["evaluation_schedule"]
    ids = [case + ":" + arm for case, arm in expected]
    if (run.get("status") != "completed" or training.get("status") != "completed"
            or run.get("package_manifest_sha256") != settings["package_manifest_sha256"]
            or run.get("runner_sha256") != settings["script_hashes"]["contextual_run.py"]
            or run.get("original_adapter_manifest_sha256") != settings["trained_manifest_sha256"]
            or set(training.get("arms", {})) != {"control", "candidate"}
            or len(rows) != 24 or len(ids) != 48 or len(set(ids)) != 48
            or evaluation.get("status") != "completed" or evaluation.get("scheduled_outputs") != 48
            or evaluation.get("attempted_outputs") != 48 or evaluation.get("recorded_outputs") != 48
            or evaluation.get("completed_outputs") != 48 or evaluation.get("completed_cases") != 24
            or "active_output_id" not in evaluation or evaluation["active_output_id"] is not None
            or evaluation.get("unattempted_output_ids") != [] or evaluation.get("schedule") != ids
            or evaluation.get("inputs_sha256") != settings["inputs_sha256"]
            or [r.get("id") for r in results] != ids):
        raise ValueError("Pilot requires both completed arms and 48 distinct first attempts")
    for arm in ("control", "candidate"):
        info = training["arms"][arm]
        if (type(info.get("completed_steps")) is not int or info["completed_steps"] != 48
                or info.get("status") != "completed" or info.get("consumed_slots") != 768
                or info.get("parent_order_verified") is not True):
            raise ValueError("Pilot training arm did not complete the exact 48-step schedule")
        for name in ("adapter_config.json", "adapter_model.safetensors"):
            path = output / "training" / arm / "adapter" / name
            if path.is_symlink() or not path.is_file() or path.stat().st_size <= 0:
                raise ValueError("Completed arm lacks its final adapter")
    indexed = {row["id"]: row for row in rows}
    for index, ((case, arm), result) in enumerate(zip(expected, results)):
        row = indexed[case]
        if (result.get("status") not in {"success", "abstain"} or result.get("case_id") != case
                or result.get("arm") != arm or result.get("sequence") != index + 1
                or result.get("record_id") != row["record_id"] or result.get("work_id") != row["work_id"]
                or result.get("input_sha256") != hashlib.sha256(row["source_text"].encode("utf-8")).hexdigest()):
            raise ValueError("Pilot evaluation first-attempt source/arm identity mismatch")


def run_logged(command, log_path, timeout):
    """Stream a child to the durable log and inherited stdout; reap it on failure."""
    import subprocess
    import sys
    import threading

    with log_path.open("xb") as log:
        child = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        errors = []
        def copy_output():
            try:
                for chunk in iter(child.stdout.readline, b""):
                    log.write(chunk)
                    log.flush()
                    stream = getattr(sys.stdout, "buffer", None)
                    if stream is not None:
                        stream.write(chunk)
                        stream.flush()
                    else:
                        sys.stdout.write(chunk.decode("utf-8", errors="replace"))
                        sys.stdout.flush()
            except BaseException as error:
                errors.append(error)
                child.kill()
        reader = threading.Thread(target=copy_output, daemon=True)
        reader.start()
        try:
            returncode = child.wait(timeout=timeout)
        except BaseException:
            child.kill()
            child.wait(timeout=5)
            raise
        finally:
            reader.join(timeout=5)
            if not reader.is_alive():
                child.stdout.close()
        if reader.is_alive():
            raise TimeoutError("Child output stream did not close within five seconds")
        if errors:
            raise errors[0]
        if returncode:
            raise subprocess.CalledProcessError(returncode, command)


def contextual_body(settings, stage, deadline, evidence):
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
    import dev_diagnostic
    import dev_assisted
    import contextual_run
    bundle.verify(folder)
    verify_package(stage / "package", settings["package_manifest_sha256"])
    for name, expected in contextual_run.HELPER_SHA256.items():
        path = folder / name if name in {"runtime.py", "bundle.py"} else stage / name
        if file_sha256(path) != expected:
            raise ValueError("Frozen contextual helper differs before base download: " + name)
    rows = dev_diagnostic.read_inputs(Path("/input") / settings["inputs_name"])
    settings["evaluation_schedule"] = [(row["id"], "control" if condition == "plain" else "candidate")
                                       for row, condition in dev_assisted.schedule(rows)]
    if file_sha256(trained / "manifest.json") != settings["trained_manifest_sha256"]:
        raise ValueError("Qualified trained manifest differs")
    manifest = json.loads((trained / "manifest.json").read_text("utf-8"))
    if (manifest.get("full_training_completed") is not True or manifest.get("training_schedule_completed") is not True
            or manifest.get("completed_global_step") != 280):
        raise ValueError("Completed qualified step280 required")
    for name, expected in settings["adapter_files"].items():
        source, target, entry = trained / name, stage / name, manifest["files"][name]
        remaining(deadline, 300)
        if entry["sha256"] != expected or source.stat().st_size != entry["bytes"] or file_sha256(source) != expected:
            raise ValueError("Qualified cloud artifact mismatch: " + name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if file_sha256(target) != expected:
            raise ValueError("Qualified server copy differs: " + name)
    for source, name in ((trained / "manifest.json", "trained-manifest.json"),
                         (folder / "manifest.json", "bundle-manifest.json"),
                         (stage / "package/manifest.json", "package-manifest.json")):
        shutil.copyfile(source, evidence / name)
    emit("gpu_admission", environment=runtime.gpu_admission())
    emit("base_download_started")
    subprocess.run([sys.executable, "-u", str(folder / "fetch_base.py"), "--out", str(base), "--download"],
                   check=True, timeout=remaining(deadline, 300))
    shutil.copyfile(base / "provenance.json", evidence / "base-provenance.json")
    runtime.offline()
    emit("base_download_verified")
    os.environ["PYTHONPATH"] = os.pathsep.join((str(stage), str(folder)))
    cutoff = (datetime.now(timezone.utc) + timedelta(seconds=remaining(deadline, 300))).isoformat()
    command = [sys.executable, "-u", str(stage / "contextual_run.py"), "--bundle", str(folder),
               "--base", str(base), "--tokenizer", str(base), "--adapter", str(stage / "training/adapter"),
               "--package", str(stage / "package"), "--package-manifest-sha256", settings["package_manifest_sha256"],
               "--inputs", str(Path("/input") / settings["inputs_name"]),
               "--output", str(evidence / "contextual"), "--deadline-utc", cutoff]
    emit("contextual_started", steps_per_arm=48, scheduled_outputs=48)
    run_logged(command, evidence / "driver.log", remaining(deadline, 300))
    completed_contextual(evidence / "contextual", rows, settings)
    emit("contextual_finished", completed_outputs=48)


def execute_contextual(settings, scripts, bootstrap_prefix):
    import shutil

    deadline = time.monotonic() + settings["internal_seconds"]
    def interrupted(signum, frame):
        raise TimeoutError("Contextual pilot interrupted or computation deadline reached")
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGALRM, interrupted)
    signal.alarm(settings["compute_seconds"])
    output = Path("/output")
    fresh_output(output)
    stage = Path(tempfile.mkdtemp(prefix="pahlavi-contextual-"))
    evidence = stage / "evidence"
    evidence.mkdir()
    identity = dict(settings, operation="contextual_pilot", contextual_status="incomplete",
                    training_schedule_completed=False, evaluation_complete=False,
                    quality_validated=False, local_model_verified=False, max_export_bytes=2 * 1024**3)
    failure = None
    try:
        if shutil.disk_usage("/tmp").free < 90 * 1024**3:
            raise ValueError("Contextual pilot requires 90 GiB ephemeral disk")
        if file_sha256(Path("/input") / settings["inputs_name"]) != settings["inputs_sha256"]:
            raise ValueError("Frozen source-only input checksum mismatch")
        safe_extract(Path("/input") / settings["package_name"], stage / "package", settings["package_sha256"], 8 * 1024**2)
        verify_package(stage / "package", settings["package_manifest_sha256"])
        safe_extract(Path("/input") / settings["bundle_name"], stage / "bundle", settings["bundle_sha256"], 128 * 1024**2)
        for name, expected in settings["bootstrap_hashes"].items():
            if file_sha256(stage / "bundle" / name) != expected:
                raise ValueError("Frozen bootstrap/bundle mismatch: " + name)
        for name, entry in scripts.items():
            data = base64.b64decode(entry["content"])
            if hashlib.sha256(data).hexdigest() != entry["sha256"]:
                raise ValueError("Runner source mismatch")
            (stage / name).write_bytes(data)
        emit("bootstrap_started")
        exec(bootstrap_prefix)
        emit("bootstrap_complete")
        contextual_body(settings, stage, deadline, evidence)
        identity.update(contextual_status="complete", training_schedule_completed=True, evaluation_complete=True)
    except BaseException as error:
        failure = error
        identity.update(error_type=type(error).__name__, error=str(error))
        emit("contextual_incomplete", **identity)
    finally:
        signal.alarm(max(1, int(max(0, deadline - time.monotonic()))))
        (evidence / "contextual-status.json").write_text(json.dumps(identity, indent=2) + "\n", encoding="utf-8")
        result = export_evidence(evidence, output, deadline, identity)
        emit("ready_to_persist", **result)
        time.sleep(max(0, min(settings["maximum_wait_seconds"], deadline - time.monotonic())))
        emit("persistence_window_expired", remote_inventory_verified=False)
        signal.alarm(0)
    if failure is not None:
        raise failure


def compressed_command(code):
    """Transport the unchanged scientific program below Linux's per-argument limit."""
    data = code.encode("utf-8")
    payload = base64.b64encode(gzip.compress(data, mtime=0)).decode("ascii")
    return ("import base64,gzip,hashlib\n"
            "_contextual_code=gzip.decompress(base64.b64decode(" + repr(payload) + "))\n"
            "if hashlib.sha256(_contextual_code).hexdigest() != " + repr(hashlib.sha256(data).hexdigest()) + ":\n"
            "    raise ValueError('Decoded contextual source checksum mismatch')\n"
            "exec(compile(_contextual_code,'hf-contextual','exec'))\n")


def command_lengths(command):
    lengths = [len(argument.encode("utf-8")) for argument in command]
    total = sum(length + 1 for length in lengths)
    if any(length + 1 >= 100 * 1024 for length in lengths) or total >= 1024**2:
        raise ValueError("Job command exceeds the 100 KiB argument or 1 MiB total guard")
    return lengths, total


def specification(run_id=None):
    run_id = uuid.uuid4().hex if run_id is None else run_id
    if not isinstance(run_id, str) or not re.fullmatch(r"[a-f0-9]{32}", run_id):
        raise ValueError("Fresh hexadecimal run ID required")
    spec, hashes = hf_preflight.specification("cuda")
    prefix, marker, _ = hf_preflight.BOOTSTRAP.partition("device = sys.argv[2]\n")
    if not marker:
        raise ValueError("Reviewed bootstrap boundary changed")
    scripts = {}
    from . import contextual_run
    if contextual_run.PACKAGE_SHA256 != PACKAGE_MANIFEST_SHA256:
        raise ValueError("Driver package pin differs")
    for name in ("contextual_run.py", "contextual_train.py", "dev_assisted.py", "dev_diagnostic.py", "palref_eval.py"):
        data = Path(__file__).with_name(name).read_bytes()
        scripts[name] = {"sha256": hashlib.sha256(data).hexdigest(), "content": base64.b64encode(data).decode("ascii")}
        if name in FROZEN_HELPERS and scripts[name]["sha256"] != FROZEN_HELPERS[name]:
            raise ValueError("Frozen helper changed: " + name)
        if name in contextual_run.HELPER_SHA256 and scripts[name]["sha256"] != contextual_run.HELPER_SHA256[name]:
            raise ValueError("Driver helper pin differs: " + name)
    qualified = hf_dev_assisted.dev_assisted
    if scripts["palref_eval.py"]["sha256"] != qualified.PROTOCOL_SHA256:
        raise ValueError("Frozen PAL-REF helper changed")
    adapter_files = {"training/adapter/" + name: value for name, value in qualified.ADAPTER_FILES.items()}
    adapter_files.update({"training/" + name: value for name, value in qualified.ADAPTER_METADATA.items()})
    inputs_name, inputs_sha256 = hf_dev_assisted.INPUT_FILES["inputs"]
    settings = dict(run_id=run_id, inputs_name=inputs_name, inputs_sha256=inputs_sha256,
        package_name=PACKAGE_NAME, package_sha256=PACKAGE_SHA256, package_manifest_sha256=PACKAGE_MANIFEST_SHA256,
        bundle_name=hf_dev_assisted.BUNDLE_NAME, bundle_sha256=hf_dev_assisted.BUNDLE_SHA256,
        trained_prefix=hf_dev_assisted.TRAINED_PREFIX, trained_manifest_sha256=qualified.ADAPTER_MANIFEST_SHA256,
        adapter_files=adapter_files, bootstrap_hashes=hashes,
        script_hashes={name: entry["sha256"] for name, entry in scripts.items()},
        scheduled_outputs=48, steps_per_arm=48, native_timeout_minutes=75, compute_seconds=3900, internal_seconds=4200,
        export_reserve_seconds=300, maximum_wait_seconds=300, max_export_bytes=2 * 1024**3)
    code = "import base64,hashlib,json,os,re,signal,stat,sys,tempfile,time,zipfile\nfrom pathlib import Path,PurePosixPath\n"
    for function in (file_sha256, safe_extract, remaining, emit, fresh_output, export_evidence,
                     verify_package, completed_contextual, run_logged, contextual_body, execute_contextual):
        code += inspect.getsource(function) + "\n"
    code += "settings = " + repr(settings) + "\nscripts = " + repr(scripts) + "\n"
    code += "execute_contextual(settings, scripts, " + repr(prefix) + ")\n"
    spec["command"][3] = compressed_command(code)
    argument_lengths, total_argument_bytes = command_lengths(spec["command"])
    spec["flavor"], spec["timeout"] = "a100-large", "75m"
    spec["labels"].update(purpose="contextual-pilot", trial_id=run_id)
    spec["env"].update(HF_XET_CACHE="/tmp/pahlavi-xet-cache", OMP_NUM_THREADS="8", MKL_NUM_THREADS="8")
    from huggingface_hub import HfApi, Volume
    spec["volumes"] = [
        Volume(type="bucket", source=hf_train.BUCKET, path="inputs", mount_path="/input", read_only=True),
        Volume(type="bucket", source=hf_train.BUCKET, path=settings["trained_prefix"], mount_path="/trained", read_only=True),
        Volume(type="bucket", source=hf_train.BUCKET, path="contextual-pilot/" + run_id, mount_path="/output", read_only=False)]
    compile(code, "hf-contextual", "exec")
    compile(spec["command"][3], "hf-contextual-transport", "exec")
    inspect.signature(HfApi.run_job).bind(None, **spec)
    return spec, dict(settings, output_prefix="contextual-pilot/" + run_id,
                      command_transport="gzip-base64-stdlib",
                      decoded_command_sha256=hashlib.sha256(code.encode("utf-8")).hexdigest(),
                      decoded_command_utf8_bytes=len(code.encode("utf-8")),
                      command_arg_utf8_bytes=argument_lengths, command_total_utf8_bytes_with_nul=total_argument_bytes,
                      command_sha256=hashlib.sha256(spec["command"][3].encode("utf-8")).hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id")
    spec, provenance = specification(**vars(parser.parse_args()))
    print(json.dumps({"status": "prepared_not_submitted", "spec": spec, "provenance": provenance}, default=vars))


if __name__ == "__main__":
    main()
