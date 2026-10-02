"""Copy exact admission evidence after tests; never approve, authorize, or submit."""
import json
from pathlib import Path
import shutil
import prepare
from cloud_pilot import training_admission as gate

HERE, ROOT = prepare.HERE, prepare.ROOT


def artifact(root, path):
    raw = path.read_bytes()
    return dict(path=path.relative_to(root).as_posix(), sha256=prepare.sha(raw), bytes=len(raw))


def write(folder, name, value):
    path = folder / name
    prepare.put(path, prepare.encode(value))
    return artifact(folder, path)


def main():
    proposal = HERE / 'execution-proposal'
    prep = json.loads((proposal / 'job-receipt.json').read_bytes())
    draft = prep['training_admission']
    folder = HERE / 'admission'
    folder.mkdir()
    nf4 = 'experiments/nf4-diagnostic-20260930/live-execution/'
    dose = 'experiments/dose-acquisition-20260930/'
    groups = {
        'data': ['resources/local/training-ready-v2-20260929/data/train.jsonl',
                 'experiments/training-ready-v2-20260929/data-manifest.json',
                 'experiments/training-ready-v2-20260929/READINESS.md',
                 'experiments/training-ready-v2-20260929/INDEPENDENT-REVIEW.md'],
        'checkpoint_model': ['cloud_pilot/contract.json', nf4+'recovered/reference-manifest.json',
                             nf4+'recovered/base-provenance.json'],
        'prompts': [dose+'inputs.jsonl',dose+'packet-contract.json',dose+'packet-validation.json'],
        'benchmark_qualification': ['experiments/dev-diagnostic-20260927/assessment-contract.json',
            'experiments/dev-diagnostic-20260927/reference-screen.json',
            'experiments/dev-diagnostic-20260927/references.jsonl',
            'experiments/corrected-review-20260930/lead-only/frozen/references.jsonl',
            'experiments/training-ready-v2-20260929/COMPARISON-PLAN.md'],
        'diagnostic_qualification': ['experiments/corrected-learning-diagnosis-20260930/inputs.jsonl',
            'experiments/corrected-learning-diagnosis-20260930/references.jsonl',
            nf4+'OUTCOME.md',nf4+'review-summary.json',nf4+'result-integrity.json',
            nf4+'recovered/evaluation/evaluation/predictions.jsonl',nf4+'RESULT-INTEGRITY-REVIEW.md',
            *[dose+'confirmation/'+name for name in ('inputs.jsonl','references.jsonl','selection.json','README.md','build.py')]],
        'actual_exposure': ['experiments/training-ready-v2-20260929/recovered/mixed/training/run.json',
                            'experiments/corrected-learning-diagnosis-20260930/census.json'],
        'objective_optimizer_sampling': [dose+'PLAN.md','cloud_pilot/dose_train.py','cloud_pilot/mixed_train.py'],
        'runtime_code': ['cloud_pilot/'+name for name in (*prep['script_hashes'], 'hf_dose.py','training_admission.py',
                                                        'runtime.py','bundle.py','requirements-linux.lock')
                         if name != 'bf16_learning_eval.py'] + [dose+'prepare.py',dose+'execute.py',dose+'freeze.py'],
        'limits': [dose+'PLAN.md',dose+'live-execution/funding.json',dose+'live-execution/initial-live-check.json'],
    }
    records = {}
    for group, paths in groups.items():
        records[group] = []
        for relative in paths:
            source, target = ROOT / relative, folder / 'artifacts' / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                shutil.copyfile(source, target)
            if target.read_bytes() != source.read_bytes():
                raise ValueError('Source changed while freezing: ' + relative)
            records[group].append(artifact(folder, target))
    job = draft['job']
    contract = dict(schema_version=1,job_sha256=draft['job_sha256'],experiment_id='dose-acquisition-20260930',
        execution_owner='/root',job=job,artifacts=records,
        acquisition=dict(packet_sha256='02c5ecc82e187847377d5891c31fcb9fc5fb0d3714ea4aa66e686c0a3fabce3c',expected_outputs=56))
    contract_record = write(folder,'contract.json',contract)
    result = folder / 'artifacts' / nf4 / 'recovered/evaluation/evaluation/predictions.jsonl'
    outputs = [json.loads(s) for s in result.read_text('utf-8').splitlines()]
    assert len(outputs) == 56 and len({r['id'] for r in outputs}) == 56
    assert all(r['status'] in {'success','abstain'} for r in outputs)
    acquisition_record = write(folder,'acquisition.json',dict(status='completed',**contract['acquisition'],
        completed_outputs=56,results=artifact(folder,result)))
    write(folder,'decision.json',dict(contract_sha256=contract_record['sha256'],
        acquisition_sha256=acquisition_record['sha256'],status='training_justified',
        rationale='Both fresh blinded reviewers retain0/6 lexical inventories in matched NF4; no module checkpoint-order reversal. Individual negation/event precision effects are preserved, not dismissed. One prespecified four-pass acquisition trajectory on the exact existing1536rows can discriminate insufficient acquisition from lack of passage transfer; matched full24retention and five qualified confirmation cases prevent acquisition-only promotion. No automatic full-pool training. This is not a causal comparison to the historical96-step learning-rate schedule.'))
    check = HERE / 'local-validation.json'
    if json.loads(check.read_bytes())['status'] != 'PASS':
        raise ValueError('Exact local validation must pass before freeze')
    target = folder / 'checks' / check.name
    target.parent.mkdir()
    shutil.copyfile(check,target)
    write(folder,'validation.json',dict(contract_sha256=contract_record['sha256'],status='PASS',checks=[artifact(folder,target)]))
    print(json.dumps(dict(status='FROZEN_REVIEW_AND_AUTHORIZATION_PENDING',contract_sha256=contract_record['sha256'],
                         job_sha256=draft['job_sha256'],artifacts=len(set(r['path'] for values in records.values() for r in values)))))


if __name__ == '__main__':
    main()
