"""Bounded offline replay and tiny random-model tests; no project training."""
import ast
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import socket
import sys
import time
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SCRATCH = ROOT / 'resources/local/full-pretraining-audit-20260929/runtime-tests'
SCRATCH.mkdir(parents=True, exist_ok=True)
os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_HUB_DISABLE_TELEMETRY='1',
                  HF_HOME=str(SCRATCH / 'hf-cache'), TEMP=str(SCRATCH), TMP=str(SCRATCH),
                  PYTHONDONTWRITEBYTECODE='1')
sys.path[:0] = [str(ROOT), str(ROOT / 'cloud_pilot')]
sys.path.extend([str(ROOT / 'resources/local/train-fit-deps'),
                 str(ROOT / 'resources/local/hf-client-venv/Lib/site-packages')])


def load_tests(name):
    """Change only test scratch roots in memory; leave repository tests intact."""
    path = ROOT / 'cloud_pilot' / (name + '.py')
    tree = ast.parse(path.read_text('utf-8'))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'SCRATCH' for t in node.targets):
            node.value = ast.Call(func=ast.Name(id='Path', ctx=ast.Load()),
                                  args=[ast.Constant(str(SCRATCH / name))], keywords=[])
    ast.fix_missing_locations(tree)
    module = types.ModuleType('cloud_pilot.audit_' + name)
    module.__file__, module.__package__ = str(path), 'cloud_pilot'
    sys.modules[module.__name__] = module
    exec(compile(tree, str(path), 'exec'), module.__dict__)
    return module


def main():
    # This fixture intentionally reconstructs the pre-repair failure. A newer
    # validator correctly rejects its minimal receipt; never reinterpret that
    # rejection as evidence that the repaired phase-accounting bug persists.
    historical_sha = '4fec5d53e300da55be2b297002e9ffe67397f335a2d30c7bca32c905b0eee23a'
    actual_sha = hashlib.sha256((ROOT / 'cloud_pilot/hf_mixed.py').read_bytes()).hexdigest()
    if actual_sha != historical_sha:
        raise SystemExit(
            'HISTORICAL-ONLY audit: hf_mixed.py differs from the pre-repair SHA256 ' + historical_sha +
            '. Refusing to rerun the historical fixture or overwrite its evidence. Current regression command: '
            '[USER_HOME]\\.venvs\\codex-science\\Scripts\\python.exe -B -X utf8 -m unittest '
            'cloud_pilot.test_hf_mixed_recovery '
            'cloud_pilot.test_mixed.MixedTest.test_forecast_and_exact_artifact -v')
    started = time.monotonic()
    result = {'status': 'running', 'network_used': False, 'pretrained_weights_used': False,
              'project_training_performed': False, 'scratch': str(SCRATCH), 'checks': {}}
    from huggingface_hub import HfApi
    from transformers import PreTrainedModel
    with contextlib.ExitStack() as stack:
        for obj, name in ((socket.socket, 'connect'), (socket, 'create_connection'),
                          (HfApi, 'run_job'), (HfApi, 'create_repo'), (HfApi, 'upload_file'),
                          (HfApi, 'upload_folder'), (PreTrainedModel, 'from_pretrained')):
            stack.enter_context(patch.object(obj, name, autospec=True,
                                             side_effect=AssertionError('Offline audit forbids ' + name)))
        modules = [load_tests(name) for name in ('test_mixed', 'test_contextual_train', 'test_runtime')]
        suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromModule(m) for m in modules)
        log = io.StringIO()
        with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
            tests = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
        (SCRATCH / 'existing-tests.log').write_text(log.getvalue(), encoding='utf-8')
        result['checks']['existing_tests'] = {'passed': tests.wasSuccessful(), 'count': tests.testsRun,
            'failures': [(str(t), s) for t, s in tests.failures], 'errors': [(str(t), s) for t, s in tests.errors],
            'log': str(SCRATCH / 'existing-tests.log'),
            'scope': 'Original tests, only SCRATCH assignments redirected in memory; tiny random CPU Gemma/LoRA only.'}
        import torch
        from transformers import Trainer, TrainingArguments
        tiny = modules[0].model()
        arguments = TrainingArguments(output_dir=str(SCRATCH / 'native-loss'), max_steps=1,
            per_device_train_batch_size=1, gradient_accumulation_steps=2, use_cpu=True,
            report_to='none', save_strategy='no', disable_tqdm=True)
        trainer = Trainer(model=tiny, args=arguments)
        batches = [{k: torch.tensor([row[k]]) for k in ('input_ids', 'labels', 'attention_mask')}
                   for row in modules[0].ROWS[:2]]
        count = trainer._get_num_items_in_batch(batches, torch.device('cpu'))
        supervised = sum(int(b['labels'][:, 1:].ne(-100).sum()) for b in batches)
        native, pooled, example = [], [], []
        for batch in batches:
            loss, response = trainer.compute_loss(tiny, batch.copy(), return_outputs=True, num_items_in_batch=count)
            logits, labels = response.logits[:, :-1].float().reshape(-1, 32), batch['labels'][:, 1:].reshape(-1)
            # Match native training_step's accumulation division when the model
            # declines num_items_in_batch; do not assume Gemma's default flag.
            native.append(loss / 2 if not trainer.model_accepts_loss_kwargs or count is None else loss)
            pooled.append(torch.nn.functional.cross_entropy(logits, labels, ignore_index=-100, reduction='sum') / supervised)
            example.append(torch.nn.functional.cross_entropy(logits, labels, ignore_index=-100, reduction='mean') / 2)
        parameters = list(modules[0].core.core.trainables(tiny).values())
        native_gradient = torch.autograd.grad(sum(native), parameters, retain_graph=True)
        pooled_gradient = torch.autograd.grad(sum(pooled), parameters)
        gradient_difference = max((a-b).abs().max().item() for a,b in zip(native_gradient, pooled_gradient))
        assert trainer.model_accepts_loss_kwargs is False and count is None
        assert torch.allclose(sum(native), sum(example), atol=1e-7, rtol=1e-6)
        assert gradient_difference > 1e-6
        result['checks']['original_native_loss_vs_mixed_override'] = {
            'model_accepts_loss_kwargs_default': trainer.model_accepts_loss_kwargs,
            'supervised_tokens': supervised, 'native_num_items_in_batch': None,
            'native_accumulated_loss': sum(native).item(),
            'manual_pooled_loss': sum(pooled).item(), 'manual_equal_example_loss': sum(example).item(),
            'max_gradient_difference_native_vs_pooled': gradient_difference,
            'scope': 'Pinned Transformers/PEFT tiny CPU native loss and backward, no optimizer; historical GPU execution not replayed.'}
        from cloud_pilot import mixed_run, hf_mixed, runtime, bundle
        train = ROOT / 'resources/local/mixed-supervision-20260929/data/train.jsonl'
        manifest = ROOT / 'experiments/mixed-supervision-20260929/data-manifest.json'
        spec, receipt = hf_mixed.prepare(train, manifest, '2' * 32)
        rows, data = mixed_run.read_data(train, manifest, receipt)
        result['checks']['actual_frozen_train'] = dict(rows=len(rows), unique_ids=len({r['id'] for r in rows}),
            sequence_tokens=sum(len(r['input_ids']) for r in rows),
            supervised_tokens=sum(sum(t != -100 for t in r['labels']) for r in rows),
            max_sequence=max(len(r['input_ids']) for r in rows), train_sha256=runtime.digest(train),
            tokenizer_sha256=data['tokenizer_sha256'],
            terminators_match=all(r['input_ids'][-2:] == [106, 107] for r in rows))
        result['checks']['transport'] = {k: receipt[k] for k in ('command_arg_utf8_bytes',
            'command_total_utf8_bytes_with_nul', 'decoded_command_sha256')}
        # Run the actual wrapper with inert setup and a failing evaluation after
        # a completed synthetic training receipt; only its export writes files.
        failure_root = SCRATCH / ('wrapper-failure-' + str(time.time_ns()))
        stage, exported = failure_root / 'stage', failure_root / 'exported'
        stage.mkdir(parents=True)
        frozen_settings = dict(receipt, bootstrap_hashes={}, maximum_wait_seconds=0)
        namespace = dict(hf_mixed.__dict__)
        namespace.update(Path=lambda p: exported if str(p) == '/output' else Path(p),
            tempfile=types.SimpleNamespace(mkdtemp=lambda **kw: str(stage)),
            signal=types.SimpleNamespace(SIGTERM=15, SIGALRM=14, signal=lambda *a: None, alarm=lambda *a: None),
            emit=lambda *a, **kw: None,
            file_sha256=lambda p: {frozen_settings['inputs_name']: frozen_settings['inputs_sha256'],
                frozen_settings['train_name']: frozen_settings['train_sha256'],
                frozen_settings['data_manifest_name']: frozen_settings['data_manifest_sha256']}[p.name],
            safe_extract=lambda *a: None)
        def failed_evaluation(settings, stage, deadline, evidence):
            folder = evidence / 'mixed/training'
            folder.mkdir(parents=True)
            runtime.write_json(folder / 'run.json', {'status': 'completed', 'completed_steps': 96, 'consumed_slots': 1536})
            raise RuntimeError('synthetic evaluation failure after training')
        namespace['mixed_body'] = failed_evaluation
        execute = types.FunctionType(hf_mixed.execute_mixed.__code__, namespace)
        with patch('shutil.disk_usage', return_value=types.SimpleNamespace(free=100 * 1024**3)):
            try:
                execute(frozen_settings, {}, '')
            except RuntimeError as error:
                assert str(error) == 'synthetic evaluation failure after training'
            else:
                raise AssertionError('Wrapper failed to propagate failure')
        exported_manifest = runtime.read_json(exported / 'manifest.json')
        result['checks']['evaluation_failure_status_reproduction'] = {
            'inner_training': runtime.read_json(exported / 'mixed/training/run.json'),
            'outer_training_schedule_completed': exported_manifest['training_schedule_completed'],
            'outer_evaluation_complete': exported_manifest['evaluation_complete'],
            'partial_receipt_exported': True, 'path': str(exported)}
        helper_hashes = mixed_run.old.HELPER_SHA256
        result['checks']['helper_pins'] = {name: runtime.digest(ROOT / 'cloud_pilot' / name) == digest
                                           for name, digest in helper_hashes.items()}
        prep_path = ROOT / 'experiments/mixed-supervision-20260929/prepare.py'
        loader = importlib.util.spec_from_file_location('audit_mixed_prepare', prep_path)
        prep = importlib.util.module_from_spec(loader)
        loader.loader.exec_module(prep)
        payloads, manifest_bytes = prep.build()
        result['checks']['full_data_replay'] = {'files': len(payloads),
            'all_bytes_equal': all((prep.OUT / name).read_bytes() == payload for name, payload in payloads.items()),
            'manifest_equal': prep.MANIFEST.read_bytes() == manifest_bytes,
            'script_sha256': runtime.digest(prep_path)}
        result['source_sha256'] = {name: runtime.digest(ROOT / 'cloud_pilot' / name) for name in
            ('hf_mixed.py', 'mixed_run.py', 'mixed_train.py', 'contextual_train.py', 'runtime.py', 'bundle.py')}
        result['local_environment'] = runtime.environment()
    result['elapsed_seconds'] = time.monotonic() - started
    result['check_status'] = 'PASS' if (tests.wasSuccessful() and all(result['checks']['helper_pins'].values())
        and result['checks']['full_data_replay']['all_bytes_equal']
        and result['checks']['full_data_replay']['manifest_equal']) else 'PARTIAL'
    phase = result['checks']['evaluation_failure_status_reproduction']
    result['findings'] = ([{'id': 'TRAIN-001', 'severity': 'P2',
        'location': 'cloud_pilot/hf_mixed.py:127-157',
        'summary': 'Evaluation failure leaves outer training completion false despite completed inner training.',
        'reproduced': True}] if phase['outer_training_schedule_completed'] is False else [])
    result['status'] = 'PARTIAL' if result['findings'] else result['check_status']
    (HERE / 'training-audit.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('status', 'elapsed_seconds')}, indent=2))
    print(json.dumps(result['checks'], indent=2))


if __name__ == '__main__':
    main()
