"""Prepare the frozen eighty-forward TRAIN-fit diagnostic; never authenticate or submit."""
import argparse
import base64
import hashlib
import inspect
import json
import math
from pathlib import Path
import re
import uuid

from . import hf_baseline, hf_convert, hf_dev_assisted, hf_preflight, hf_train, hf_train_recall

INPUTS_SHA256 = "5a2b29c878b67e05bb1051fab015feae33753e7c23568ab57517af0cf84c233a"
SOURCE_CONTROL_SHA256 = "3db2398a95b6480ad2522dc2fe30d2d38156564e3a4a72714b43bcc2a54393a0"
EXPECTED_TOKEN_MAP_SHA256 = "de1388e6ae8e260ec1233cefbbcdcbc4130871715707898973de1696e9f168bf"
file_sha256, remaining, emit = hf_convert.file_sha256, hf_convert.remaining, hf_train.emit


def completed_fit(output, rows, control, settings):
    """Require eighty successful first forwards with the frozen parent/token identities."""
    run = json.loads((output / "run.json").read_text("utf-8"))
    results = [json.loads(line) for line in (output / "results.jsonl").read_text("utf-8").splitlines()]
    conditions = ((True, "correct"), (False, "correct"), (True, "mismatched"), (False, "mismatched"))
    ordered = [(row, enabled, source) for index, row in enumerate(rows)
               for enabled, source in conditions[index % 4:] + conditions[:index % 4]]
    ids = [row["id"] + (":adapter_on:" if enabled else ":adapter_off:") + source
           for row, enabled, source in ordered]
    prepared_keys = {row["id"] + ":" + source for row in rows for source in ("correct", "mismatched")}
    if (len(rows) != 20 or len(set(ids)) != 80 or len(results) != 80
            or run.get("status") != "completed" or run.get("scheduled_outputs") != 80
            or run.get("attempted_outputs") != 80 or run.get("recorded_outputs") != 80
            or run.get("completed_outputs") != 80 or run.get("completed_cases") != 20
            or "active_output_id" not in run or run["active_output_id"] is not None
            or run.get("unattempted_output_ids") != [] or run.get("schedule") != ids
            or [result.get("id") for result in results] != ids
            or run.get("inputs_sha256") != settings["inputs_sha256"]
            or run.get("source_control_sha256") != settings["source_control_sha256"]
            or run.get("runner_sha256") != settings["script_hashes"]["train_fit.py"]
            or run.get("adapter_manifest_sha256") != settings["trained_manifest_sha256"] or run.get("adapter_step") != 280
            or run.get("generation_performed") is not False or run.get("training_performed") is not False
            or run.get("expected_token_map_sha256") != settings["expected_token_map_sha256"]
            or run.get("actual_token_map_sha256") != settings["expected_token_map_sha256"]
            or not isinstance(run.get("prepared_inputs"), dict) or set(run["prepared_inputs"]) != prepared_keys
            or [pair["target_parent_id"] for pair in control["pairs"]] != [row["id"] for row in rows]
            or not re.fullmatch(r"[a-f0-9]{64}", str(run.get("identity_sha256")))):
        raise ValueError("Fit did not complete all 80 frozen first-forward identities")
    token_map_bytes = json.dumps(run["prepared_inputs"], ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if hashlib.sha256(token_map_bytes).hexdigest() != settings["expected_token_map_sha256"]:
        raise ValueError("Fit prepared token map differs from frozen identity")
    for index, ((row, enabled, source), result) in enumerate(zip(ordered, results)):
        prepared = run["prepared_inputs"][row["id"] + ":" + source]
        if (result.get("status") != "success" or result.get("case_id") != row["id"]
                or result.get("record_id") != row["record_id"] or result.get("work_id") != row["work_id"]
                or result.get("adapter_enabled") is not enabled or result.get("source_condition") != source
                or result.get("sequence") != index + 1 or result.get("identity_sha256") != run["identity_sha256"]
                or result.get("input_sha256") != prepared.get("input_ids_sha256")
                or result.get("labels_sha256") != prepared.get("labels_sha256")
                or result.get("target_ids_sha256") != prepared.get("target_ids_sha256")
                or result.get("input_tokens") != prepared.get("input_tokens")
                or result.get("prompt_tokens") != prepared.get("prompt_tokens")
                or result.get("supervised_tokens") != prepared.get("supervised_tokens")
                or type(result.get("supervised_tokens")) is not int or result["supervised_tokens"] <= 0
                or any(not re.fullmatch(r"[a-f0-9]{64}", str(result.get(key)))
                       for key in ("input_sha256", "labels_sha256", "target_ids_sha256"))
                or any(type(result.get(key)) not in (int, float) or not math.isfinite(result[key])
                       for key in ("sum_nll", "mean_nll", "model_loss", "numerical_loss_difference"))):
            raise ValueError("Fit first-forward identity/numerical status mismatch")


def fit_body(settings, stage, deadline, evidence):
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
    import train_fit
    bundle.verify(folder)
    rows = train_fit.read_inputs(Path("/input") / settings["inputs_name"],
                                    settings["inputs_sha256"], folder / "train.jsonl")
    control = train_fit.read_source_control(Path("/input") / settings["source_control_name"],
                                            settings["source_control_sha256"], rows)
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
    shutil.copyfile(Path("/input") / settings["source_control_name"], evidence / "source-control.json")
    emit("gpu_admission", environment=runtime.gpu_admission())
    emit("base_download_started")
    subprocess.run([sys.executable, "-u", str(folder / "fetch_base.py"), "--out", str(base), "--download"],
                   check=True, timeout=remaining(deadline, 180))
    shutil.copyfile(base / "provenance.json", evidence / "base-provenance.json")
    runtime.offline()
    emit("base_download_verified")
    os.environ["PYTHONPATH"] = str(folder)
    cutoff = (datetime.now(timezone.utc) + timedelta(seconds=remaining(deadline, 180))).isoformat()
    command = [sys.executable, "-u", str(stage / "train_fit.py"), "--bundle", str(folder),
               "--base", str(base), "--tokenizer", str(base), "--adapter", str(stage / "training/adapter"),
               "--inputs", str(Path("/input") / settings["inputs_name"]),
               "--inputs-sha256", settings["inputs_sha256"],
               "--source-control", str(Path("/input") / settings["source_control_name"]),
               "--source-control-sha256", settings["source_control_sha256"],
               "--output", str(evidence / "fit"), "--deadline-utc", cutoff]
    emit("train_fit_started", scheduled_outputs=80)
    subprocess.run(command, check=True, timeout=remaining(deadline, 180))
    completed_fit(evidence / "fit", rows, control, settings)
    emit("train_fit_finished", completed_outputs=80)


def execute_fit(settings, scripts, bootstrap_prefix):
    """Server lifecycle: verify, run once, publish closed partials, preserve failure."""
    import shutil

    deadline = time.monotonic() + settings["internal_seconds"]
    def interrupted(signum, frame):
        raise TimeoutError("TRAIN fit interrupted or computation deadline reached")
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGALRM, interrupted)
    signal.alarm(settings["compute_seconds"])
    output = Path("/output")
    fresh_output(output)
    stage = Path(tempfile.mkdtemp(prefix="pahlavi-train-fit-"))
    evidence = stage / "evidence"
    evidence.mkdir()
    identity = dict(settings, operation="qualified_train_fit", fit_status="incomplete",
                    evaluation_complete=False, training_performed=False, generation_performed=False,
                    optimizer_updates=0, quality_validated=False, local_model_verified=False)
    failure = None
    try:
        if shutil.disk_usage("/tmp").free < 90 * 1024**3:
            raise ValueError("Fit requires 90 GiB ephemeral disk")
        for key in ("inputs", "source_control"):
            if file_sha256(Path("/input") / settings[key + "_name"]) != settings[key + "_sha256"]:
                raise ValueError("Frozen source-only input/control checksum mismatch: " + key)
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
        fit_body(settings, stage, deadline, evidence)
        identity.update(fit_status="complete", evaluation_complete=True)
    except BaseException as error:
        failure = error
        identity.update(error_type=type(error).__name__, error=str(error))
        emit("train_fit_incomplete", **identity)
    finally:
        signal.alarm(max(1, int(max(0, deadline - time.monotonic()))))
        (evidence / "fit-status.json").write_text(json.dumps(identity, indent=2) + "\n", encoding="utf-8")
        result = publish(evidence, output, deadline, identity)
        emit("ready_to_persist", **result)
        time.sleep(max(0, min(settings["maximum_wait_seconds"], deadline - time.monotonic())))
        emit("persistence_window_expired", remote_inventory_verified=False)
        signal.alarm(0)
    if failure is not None:
        raise failure


def specification(inputs_name, inputs_sha256, source_control_name, source_control_sha256, run_id=None):
    if (not isinstance(inputs_name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*\.jsonl", inputs_name)
            or not isinstance(source_control_name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*\.json", source_control_name)
            or inputs_sha256 != INPUTS_SHA256 or source_control_sha256 != SOURCE_CONTROL_SHA256):
        raise ValueError("Exact frozen source-only input/control hashes and safe basenames required")
    run_id = uuid.uuid4().hex if run_id is None else run_id
    if not isinstance(run_id, str) or not re.fullmatch(r"[a-f0-9]{32}", run_id):
        raise ValueError("Fresh hexadecimal run ID required")
    spec, hashes = hf_preflight.specification("cuda")
    prefix, marker, _ = hf_preflight.BOOTSTRAP.partition("device = sys.argv[2]\n")
    if not marker:
        raise ValueError("Reviewed bootstrap boundary changed")
    from . import train_fit
    if train_fit.TOKEN_MAP_SHA256 != EXPECTED_TOKEN_MAP_SHA256:
        raise ValueError("Frozen fit token identity changed")
    scripts = {}
    for name in ("train_fit.py", "train_recall.py", "dev_assisted.py", "dev_diagnostic.py", "palref_eval.py"):
        data = Path(__file__).with_name(name).read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if name in train_fit.HELPER_SHA256 and digest != train_fit.HELPER_SHA256[name]:
            raise ValueError("Frozen fit helper changed: " + name)
        scripts[name] = {"sha256": digest, "content": base64.b64encode(data).decode("ascii")}
    qualified = hf_dev_assisted.dev_assisted
    adapter_files = {"training/adapter/" + name: value for name, value in qualified.ADAPTER_FILES.items()}
    adapter_files.update({"training/" + name: value for name, value in qualified.ADAPTER_METADATA.items()})
    settings = dict(run_id=run_id, inputs_name=inputs_name, inputs_sha256=inputs_sha256,
        source_control_name=source_control_name, source_control_sha256=source_control_sha256,
        expected_token_map_sha256=EXPECTED_TOKEN_MAP_SHA256,
        bundle_name=hf_dev_assisted.BUNDLE_NAME, bundle_sha256=hf_dev_assisted.BUNDLE_SHA256,
        trained_prefix=hf_dev_assisted.TRAINED_PREFIX, trained_manifest_sha256=qualified.ADAPTER_MANIFEST_SHA256,
        adapter_files=adapter_files, bootstrap_hashes=hashes,
        script_hashes={name: value["sha256"] for name, value in scripts.items()},
        scheduled_outputs=80, compute_seconds=1440, internal_seconds=1620,
        export_reserve_seconds=180, maximum_wait_seconds=180)
    code = "import base64,hashlib,json,math,os,re,signal,stat,sys,tempfile,time,zipfile\nfrom pathlib import Path,PurePosixPath\n"
    for function in (hf_convert.file_sha256, hf_convert.safe_extract, hf_convert.remaining,
                     hf_train.emit, hf_baseline.publish, hf_train_recall.fresh_output,
                     completed_fit, fit_body, execute_fit):
        code += inspect.getsource(function) + "\n"
    code += "settings = " + repr(settings) + "\nscripts = " + repr(scripts) + "\n"
    code += "execute_fit(settings, scripts, " + repr(prefix) + ")\n"
    spec["command"][3] = code
    spec["flavor"], spec["timeout"] = "a100-large", "29m"
    spec["labels"].update(purpose="qualified-train-fit", trial_id=run_id)
    spec["env"].update(HF_XET_CACHE="/tmp/pahlavi-xet-cache", OMP_NUM_THREADS="8", MKL_NUM_THREADS="8")
    from huggingface_hub import HfApi, Volume
    spec["volumes"] = [
        Volume(type="bucket", source=hf_train.BUCKET, path="inputs", mount_path="/input", read_only=True),
        Volume(type="bucket", source=hf_train.BUCKET, path=settings["trained_prefix"], mount_path="/trained", read_only=True),
        Volume(type="bucket", source=hf_train.BUCKET, path="train-fit/" + run_id, mount_path="/output", read_only=False),
    ]
    compile(code, "hf-train-fit", "exec")
    inspect.signature(HfApi.run_job).bind(None, **spec)
    return spec, dict(settings, output_prefix="train-fit/" + run_id,
                      command_sha256=hashlib.sha256(code.encode()).hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("inputs-name", "inputs-sha256", "source-control-name", "source-control-sha256"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--run-id")
    spec, provenance = specification(**vars(parser.parse_args()))
    spec["volumes"] = [volume.to_dict() for volume in spec["volumes"]]
    print(json.dumps({"status": "prepared_not_submitted", "spec": spec, "provenance": provenance}))


if __name__ == "__main__":
    main()
