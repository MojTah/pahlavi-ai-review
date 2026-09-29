"""Prepare one 100-minute mixed-supervision job. No authentication or submission."""
import base64
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
from . import hf_contextual as old, hf_continue, hf_convert, hf_dev_assisted, hf_preflight, hf_train, hf_train_recall, mixed_run
file_sha256, safe_extract, remaining = hf_convert.file_sha256, hf_convert.safe_extract, hf_convert.remaining
emit, fresh_output, export_evidence = hf_train.emit, hf_train_recall.fresh_output, hf_continue.export_evidence
run_logged = old.run_logged


def completed_mixed(output, rows, settings):
    run = json.loads((output / 'run.json').read_text('utf-8'))
    training = json.loads((output / 'training/run.json').read_text('utf-8'))
    evaluation = json.loads((output / 'evaluation/run.json').read_text('utf-8'))
    results = [json.loads(s) for s in (output / 'evaluation/predictions.jsonl').read_text('utf-8').splitlines()]
    expected = settings['evaluation_schedule']
    if (run.get('status') != 'completed' or training.get('status') != 'completed'
            or training['completed_steps'] != 96 or training['consumed_slots'] != 1536
            or training['settings'] != settings['training_settings'] or training['fresh_optimizer'] is not True
            or training['parent_order_verified'] is not True or training['admission']['admitted'] is not True
            or run['train_sha256'] != settings['train_sha256'] or run['runner_sha256'] != settings['script_hashes']['mixed_run.py']
            or evaluation.get('status') != 'completed' or evaluation['completed_outputs'] != 24
            or evaluation['completed_cases'] != 24 or evaluation['attempted_outputs'] != 24
            or evaluation['recorded_outputs'] != 24 or evaluation['unattempted_output_ids']
            or evaluation['active_output_id'] is not None or evaluation['schedule'] != expected
            or [r['id'] for r in results] != expected):
        raise ValueError('Incomplete mixed training or candidate-only DEV24')
    indexed = {r['id']: r for r in rows}
    for result in results:
        row = indexed[result['case_id']]
        if (result['status'] not in {'success', 'abstain'} or result['arm'] != 'candidate'
                or result['input_sha256'] != hashlib.sha256(row['source_text'].encode()).hexdigest()):
            raise ValueError('Mixed evaluation source/first attempt differs')
    for name, expected_hash in training['adapter_files'].items():
        if file_sha256(output / 'training/adapter' / name) != expected_hash:
            raise ValueError('Final adapter checksum differs')


def mixed_body(settings, stage, deadline, evidence):
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
    import mixed_run
    bundle.verify(folder)
    for name, expected in contextual_run.HELPER_SHA256.items():
        path = folder / name if name in {"runtime.py", "bundle.py"} else stage / name
        if file_sha256(path) != expected:
            raise ValueError("Frozen contextual helper differs before base download: " + name)
    rows = dev_diagnostic.read_inputs(Path("/input") / settings["inputs_name"])
    settings["evaluation_schedule"] = [row["id"] + ":candidate"
                                       for row, condition in dev_assisted.schedule(rows) if condition == "plain"]
    if file_sha256(trained / "manifest.json") != settings["trained_manifest_sha256"]:
        raise ValueError("Qualified trained manifest differs")
    manifest = json.loads((trained / "manifest.json").read_text("utf-8"))
    if (manifest.get("full_training_completed") is not True or manifest.get("training_schedule_completed") is not True
            or manifest.get("completed_global_step") != 280):
        raise ValueError("Completed qualified step280 required")
    for name, expected in settings["adapter_files"].items():
        source, target, entry = trained / name, stage / name, manifest["files"][name]
        remaining(deadline, 600)
        if entry["sha256"] != expected or source.stat().st_size != entry["bytes"] or file_sha256(source) != expected:
            raise ValueError("Qualified cloud artifact mismatch: " + name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if file_sha256(target) != expected:
            raise ValueError("Qualified server copy differs: " + name)
    for source, name in ((trained / "manifest.json", "trained-manifest.json"),
                         (folder / "manifest.json", "bundle-manifest.json"),
                         (Path("/input") / settings["data_manifest_name"], "data-manifest.json")):
        shutil.copyfile(source, evidence / name)
    emit("gpu_admission", environment=runtime.gpu_admission())
    emit("base_download_started")
    subprocess.run([sys.executable, "-u", str(folder / "fetch_base.py"), "--out", str(base), "--download"],
                   check=True, timeout=remaining(deadline, 600))
    shutil.copyfile(base / "provenance.json", evidence / "base-provenance.json")
    runtime.offline()
    emit("base_download_verified")
    os.environ["PYTHONPATH"] = os.pathsep.join((str(stage), str(folder)))
    cutoff = (datetime.now(timezone.utc) + timedelta(seconds=remaining(deadline, 600))).isoformat()
    command = [sys.executable, "-u", str(stage / "mixed_run.py"), "--bundle", str(folder),
               "--base", str(base), "--tokenizer", str(base), "--adapter", str(stage / "training/adapter"),
               "--train", str(Path("/input") / settings["train_name"]),
               "--data-manifest", str(Path("/input") / settings["data_manifest_name"]),
               "--settings", str(stage / "settings.json"),
               "--inputs", str(Path("/input") / settings["inputs_name"]),
               "--output", str(evidence / "mixed"), "--deadline-utc", cutoff]
    emit("mixed_started", steps=96, scheduled_outputs=24)
    run_logged(command, evidence / "driver.log", remaining(deadline, 600))
    completed_mixed(evidence / "mixed", rows, settings)
    emit("mixed_finished", completed_outputs=24)


def execute_mixed(settings, scripts, bootstrap_prefix):
    import shutil

    deadline = time.monotonic() + settings["internal_seconds"]
    def interrupted(signum, frame):
        raise TimeoutError("Contextual pilot interrupted or computation deadline reached")
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGALRM, interrupted)
    signal.alarm(settings["compute_seconds"])
    output = Path("/output")
    fresh_output(output)
    stage = Path(tempfile.mkdtemp(prefix="pahlavi-mixed-"))
    evidence = stage / "evidence"
    evidence.mkdir()
    identity = dict(settings, operation="mixed_supervision", mixed_status="incomplete",
                    training_schedule_completed=False, evaluation_complete=False,
                    quality_validated=False, local_model_verified=False, max_export_bytes=2 * 1024**3)
    failure = None
    try:
        if shutil.disk_usage("/tmp").free < 90 * 1024**3:
            raise ValueError("Contextual pilot requires 90 GiB ephemeral disk")
        if file_sha256(Path("/input") / settings["inputs_name"]) != settings["inputs_sha256"]:
            raise ValueError("Frozen source-only input checksum mismatch")
        for name, expected in ((settings['train_name'], settings['train_sha256']),
                               (settings['data_manifest_name'], settings['data_manifest_sha256'])):
            if file_sha256(Path('/input') / name) != expected:
                raise ValueError('Mixed frozen input differs: ' + name)
        safe_extract(Path("/input") / settings["bundle_name"], stage / "bundle", settings["bundle_sha256"], 128 * 1024**2)
        for name, expected in settings["bootstrap_hashes"].items():
            if file_sha256(stage / "bundle" / name) != expected:
                raise ValueError("Frozen bootstrap/bundle mismatch: " + name)
        for name, entry in scripts.items():
            data = base64.b64decode(entry["content"])
            if hashlib.sha256(data).hexdigest() != entry["sha256"]:
                raise ValueError("Runner source mismatch")
            (stage / name).write_bytes(data)
        (stage / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
        emit("bootstrap_started")
        exec(bootstrap_prefix)
        emit("bootstrap_complete")
        mixed_body(settings, stage, deadline, evidence)
        identity.update(mixed_status="complete", training_schedule_completed=True, evaluation_complete=True)
    except BaseException as error:
        failure = error
        identity.update(error_type=type(error).__name__, error=str(error))
        emit("mixed_incomplete", **identity)
    finally:
        signal.alarm(max(1, int(max(0, deadline - time.monotonic()))))
        (evidence / "mixed-status.json").write_text(json.dumps(identity, indent=2) + "\n", encoding="utf-8")
        result = export_evidence(evidence, output, deadline, identity)
        emit("ready_to_persist", **result)
        time.sleep(max(0, min(settings["maximum_wait_seconds"], deadline - time.monotonic())))
        emit("persistence_window_expired", remote_inventory_verified=False)
        signal.alarm(0)
    if failure is not None:
        raise failure


def prepare(train_path, manifest_path, run_id=None):
    run_id = uuid.uuid4().hex if run_id is None else run_id
    if not isinstance(run_id, str) or not re.fullmatch(r'[a-f0-9]{32}', run_id):
        raise ValueError('Fresh hexadecimal run ID required')
    spec, hashes = hf_preflight.specification('cuda')
    prefix, marker, _ = hf_preflight.BOOTSTRAP.partition('device = sys.argv[2]\n')
    if not marker:
        raise ValueError('Reviewed bootstrap boundary changed')
    root = Path(__file__).resolve().parent
    train_sha, manifest_sha = file_sha256(train_path), file_sha256(manifest_path)
    settings = dict(train_sha256=train_sha, data_manifest_sha256=manifest_sha)
    mixed_run.read_data(train_path, manifest_path, settings)
    prompts_path = root.parent / 'resources/local/contextual-run-package/dev-prompt-identities.json'
    prompt_manifest = json.loads(prompts_path.with_name('manifest.json').read_text('utf-8'))
    if (file_sha256(prompts_path.with_name('manifest.json')) != old.PACKAGE_MANIFEST_SHA256
            or file_sha256(prompts_path) != prompt_manifest['files'][prompts_path.name]['sha256']):
        raise ValueError('Frozen plain DEV prompt identity differs')
    scripts = {}
    for name in ('mixed_run.py', 'mixed_train.py', 'contextual_run.py', 'contextual_train.py',
                 'dev_assisted.py', 'dev_diagnostic.py', 'palref_eval.py'):
        data = (root / name).read_bytes()
        scripts[name] = dict(sha256=hashlib.sha256(data).hexdigest(), content=base64.b64encode(data).decode('ascii'))
        expected = mixed_run.old.HELPER_SHA256.get(name)
        if expected and scripts[name]['sha256'] != expected:
            raise ValueError('Frozen helper changed: ' + name)
    qualified = hf_dev_assisted.dev_assisted
    adapter_files = {'training/adapter/' + name: value for name, value in qualified.ADAPTER_FILES.items()}
    adapter_files.update({'training/' + name: value for name, value in qualified.ADAPTER_METADATA.items()})
    inputs_name, inputs_sha = hf_dev_assisted.INPUT_FILES['inputs']
    settings.update(run_id=run_id, inputs_name=inputs_name, inputs_sha256=inputs_sha,
        train_name='mixed-train-' + train_sha[:12] + '.jsonl',
        data_manifest_name='mixed-data-manifest-' + manifest_sha[:12] + '.json',
        prompt_identities=json.loads(prompts_path.read_text('utf-8')),
        training_settings=mixed_run.SETTINGS,
        bundle_name=hf_dev_assisted.BUNDLE_NAME, bundle_sha256=hf_dev_assisted.BUNDLE_SHA256,
        trained_prefix=hf_dev_assisted.TRAINED_PREFIX, trained_manifest_sha256=qualified.ADAPTER_MANIFEST_SHA256,
        adapter_files=adapter_files, bootstrap_hashes=hashes,
        script_hashes={name: entry['sha256'] for name, entry in scripts.items()},
        scheduled_outputs=24, steps=96, native_timeout_minutes=100, compute_seconds=5100, internal_seconds=5700,
        export_reserve_seconds=600, maximum_wait_seconds=300, max_export_bytes=2 * 1024**3)
    code = 'import base64,hashlib,json,os,re,signal,stat,sys,tempfile,time,zipfile\nfrom pathlib import Path,PurePosixPath\n'
    for function in (file_sha256, safe_extract, remaining, emit, fresh_output, export_evidence,
                     completed_mixed, run_logged, mixed_body, execute_mixed):
        code += inspect.getsource(function) + '\n'
    code += 'settings = ' + repr(settings) + '\nscripts = ' + repr(scripts) + '\n'
    code += 'execute_mixed(settings, scripts, ' + repr(prefix) + ')\n'
    spec['command'][3] = old.compressed_command(code)
    lengths, total = old.command_lengths(spec['command'])
    spec['flavor'], spec['timeout'] = 'a100-large', '100m'
    spec['labels'].update(purpose='mixed-supervision', trial_id=run_id)
    spec['env'].update(HF_XET_CACHE='/tmp/pahlavi-xet-cache', OMP_NUM_THREADS='8', MKL_NUM_THREADS='8')
    from huggingface_hub import HfApi, Volume
    output_prefix = 'mixed-supervision/' + run_id
    spec['volumes'] = [
        Volume(type='bucket', source=hf_train.BUCKET, path='inputs', mount_path='/input', read_only=True),
        Volume(type='bucket', source=hf_train.BUCKET, path=settings['trained_prefix'], mount_path='/trained', read_only=True),
        Volume(type='bucket', source=hf_train.BUCKET, path=output_prefix, mount_path='/output', read_only=False)]
    compile(code, 'hf-mixed', 'exec')
    compile(spec['command'][3], 'hf-mixed-transport', 'exec')
    inspect.signature(HfApi.run_job).bind(None, **spec)
    return spec, dict(settings, output_prefix=output_prefix, prepared_not_submitted=True,
        decoded_command_sha256=hashlib.sha256(code.encode()).hexdigest(),
        command_sha256=hashlib.sha256(spec['command'][3].encode()).hexdigest(),
        command_arg_utf8_bytes=lengths, command_total_utf8_bytes_with_nul=total)

