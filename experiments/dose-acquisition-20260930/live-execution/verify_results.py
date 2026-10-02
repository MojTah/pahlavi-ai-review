"""Local receipt/stream verification; no network or model weights required."""
import ast
import hashlib
import json
import math
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from cloud_pilot import dose_train


def read(path):
    return json.loads(path.read_bytes())


def rows(path):
    return [json.loads(line) for line in path.read_bytes().splitlines()]


def main():
    recovered = HERE / 'recovered'
    receipt = read(HERE / 'terminal.json')
    assert receipt['stage'] == 'COMPLETED'
    assert hashlib.sha256((recovered / 'manifest.json').read_bytes()).hexdigest() == receipt['manifest_sha256']
    for item in receipt['files']:
        raw = (recovered / item['path']).read_bytes()
        assert len(raw) == item['bytes'] and hashlib.sha256(raw).hexdigest() == item['sha256']
    assert not list(recovered.rglob('*.safetensors'))
    run = read(recovered / 'dose/training/run.json')
    base = rows(ROOT / 'resources/local/training-ready-v2-20260929/data/train.jsonl')
    assert len(base) == 1536
    stream = base * 4
    ids = dose_train.validate_rows(stream, run['settings'], passes=4)
    assert ids == run['ordered_ids'] and len(ids) == 6144
    digest = lambda value: hashlib.sha256(dose_train.core.canonical(value)).hexdigest()
    assert digest(base) == run['base_cycle_sha256']
    assert digest(stream) == run['stream_sha256'] == run['forwarded_stream_sha256']
    assert len(run['pass_exposures']) == 4
    for number, cycle in enumerate(run['pass_exposures'], 1):
        assert cycle == dict(pass_index=number, slots=1536, ids=ids[:1536], stream_sha256=digest(base))
    assert run['status'] == 'completed' and run['fresh_optimizer'] and run['parent_order_verified']
    assert run['completed_steps'] == 384 and run['consumed_slots'] == 6144
    progress = rows(recovered / 'dose/training/progress.jsonl')
    assert len(progress) == 384
    for step, event in enumerate(progress, 1):
        assert event['step'] == step and event['consumed_slots'] == 16 * step
        assert math.isfinite(event['seconds']) and event['seconds'] > 0
    assert all(a['seconds'] <= b['seconds'] for a, b in zip(progress, progress[1:]))
    for step in (96, 192, 384):
        snapshot = run['snapshots'][str(step)]
        assert snapshot['optimizer_steps'] == [step] and snapshot['scheduler_step'] == step
        assert snapshot['consumed_slots'] == 16 * step
    identities = [run['initial_adapter_sha256']] + [run['snapshots'][str(s)]['adapter_sha256'] for s in (96, 192, 384)]
    assert len(set(identities)) == 4 and identities[-1] == run['final_adapter_sha256']
    log = (recovered / 'driver.log').read_text(encoding='utf8')
    loss_rows = [ast.literal_eval(s) for s in re.findall(r"\{'loss':[^\r\n]*?\}", log)]
    assert len(loss_rows) == 384
    assert all(math.isfinite(float(row[key])) for row in loss_rows for key in ('loss', 'grad_norm', 'learning_rate'))
    means = [sum(float(r['loss']) for r in loss_rows[i:i+96]) / 96 for i in range(0, 384, 96)]
    report = dict(status='PASS_FOR_LISTED_LOCAL_CHECKS', owner='root', recovered_file_hashes=len(receipt['files']),
        original_rows=1536, identical_passes=4, forwarded_slots=6144, optimizer_updates=384,
        finite_training_log_rows=384, mean_logged_loss_by_pass=means,
        scope='Recovered small-file integrity, exact source token/mask/stream reconstruction, recorded update progression and snapshot identities.',
        limits=['Server adapter tensor digests are recorded evidence; model bytes were not independently reread.',
                'This is lead verification, not a completed independent technical audit or a semantic quality certification.'])
    (HERE / 'root-verification.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
