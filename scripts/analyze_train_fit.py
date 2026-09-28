"""Verify recovered fit evidence and report paired NLL contrasts, never translation merit."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloud_pilot import train_fit as fit, hf_train_fit as package


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def contrasts(records):
    """Four paired contrasts in nats per supervised token; equal-parent summaries."""
    grouped = defaultdict(dict)
    for row in records:
        key = (row['adapter_enabled'], row['source_condition'])
        require(key not in grouped[row['case_id']], 'Duplicate condition')
        grouped[row['case_id']][key] = row
    cases = []
    for cid, values in sorted(grouped.items()):
        require(set(values) == set(fit.CONDITIONS), 'Four conditions required per parent')
        require(len({r['work_id'] for r in values.values()}) == 1, 'Parent work differs')
        require(len({r['supervised_tokens'] for r in values.values()}) == 1, 'Target-token count differs')
        loss = {key: row['mean_nll'] for key, row in values.items()}
        cases.append({'case_id': cid, 'work_id': next(iter(values.values()))['work_id'],
            'supervised_tokens': next(iter(values.values()))['supervised_tokens'],
            'adapter_gain_correct': loss[False, 'correct'] - loss[True, 'correct'],
            'adapter_gain_mismatched': loss[False, 'mismatched'] - loss[True, 'mismatched'],
            'mismatch_penalty_adapter_on': loss[True, 'mismatched'] - loss[True, 'correct'],
            'mismatch_penalty_adapter_off': loss[False, 'mismatched'] - loss[False, 'correct']})
    fields = ('adapter_gain_correct', 'adapter_gain_mismatched',
              'mismatch_penalty_adapter_on', 'mismatch_penalty_adapter_off')
    def describe(rows):
        return {'parents': len(rows), 'contrasts': {name: {
            'mean': statistics.mean(r[name] for r in rows),
            'median': statistics.median(r[name] for r in rows),
            'min': min(r[name] for r in rows), 'max': max(r[name] for r in rows),
            'positive_count': sum(r[name] > 0 for r in rows),
            'negative_count': sum(r[name] < 0 for r in rows),
            'zero_count': sum(r[name] == 0 for r in rows)} for name in fields}}
    return {'units': 'natural-log NLL per supervised target/terminator token',
        'weighting': 'equal parent; no pooling of eighty forwards as independent units',
        'per_parent': cases, 'all_parents': describe(cases),
        'by_work': {work: describe([r for r in cases if r['work_id'] == work])
                    for work in sorted({r['work_id'] for r in cases})}}


def analyze(folder):
    folder = Path(folder)
    recovery = json.loads((folder / 'recovery.json').read_text())
    require(recovery['full_sha_recovery_verified'] and recovery['provider_inventory_committed'], 'Recovery not verified')
    recovered = folder / 'recovered'
    manifest_data = (recovered / 'manifest.json').read_bytes()
    require(sha(manifest_data) == recovery['manifest_sha256'], 'Manifest changed')
    manifest = json.loads(manifest_data)
    require(manifest['operation'] == 'qualified_train_fit' and manifest['training_performed'] is False,
            'Unexpected recovered operation')
    require(manifest['files'] == recovery['files'], 'Recovery inventory differs')
    require(manifest['script_hashes']['train_fit.py'] == sha(Path(fit.__file__).read_bytes()), 'Runner source changed')
    for name, entry in manifest['files'].items():
        path = (recovered / name).resolve()
        require(path.is_relative_to(recovered.resolve()), 'Unsafe manifest path')
        data = path.read_bytes()
        require(len(data) == entry['bytes'] and sha(data) == entry['sha256'], 'Recovered artifact changed: ' + name)
    run = json.loads((recovered / 'fit/run.json').read_text())
    result_path = recovered / 'fit/results.jsonl'
    records = [json.loads(line) for line in result_path.read_text().splitlines()] if result_path.exists() else []
    mutable = {'identity_sha256', 'status', 'scheduled_outputs', 'attempted_outputs', 'recorded_outputs',
               'completed_outputs', 'completed_cases', 'active_output_id', 'unattempted_output_ids',
               'initial_adapter_state', 'error_type', 'error'}
    identity = {k: v for k, v in run.items() if k not in mutable}
    require(sha(fit.qualified.canonical(identity)) == run['identity_sha256'], 'Run identity differs or preparation unfinished')
    require(run['runner_sha256'] == manifest['script_hashes']['train_fit.py'], 'Executed runner differs')
    require(run['model_id'] == fit.runtime.MODEL_ID and run['model_revision'] == fit.runtime.REVISION
            and run['adapter_files'] == fit.qualified.ADAPTER_FILES and run['adapter_step'] == 280
            and run['generation_performed'] is False and run['training_performed'] is False,
            'Model or operation differs')
    inputs = ROOT / 'experiments/train-recall-20260927/inputs.jsonl'
    require(sha(inputs.read_bytes()) == fit.INPUTS_SHA256, 'Frozen input changed')
    train_path = ROOT / 'experiments/train-audit-20260927/qualified-v1/train.jsonl'
    rows = fit.read_inputs(inputs, fit.INPUTS_SHA256, train_path)
    control = fit.read_source_control(folder / 'source-control.json', fit.SOURCE_CONTROL_SHA256, rows)
    require(run['source_control'] == control and run['inputs_sha256'] == fit.INPUTS_SHA256
            and run['source_control_sha256'] == fit.SOURCE_CONTROL_SHA256, 'Source control differs')
    require(run['expected_token_map_sha256'] == run['actual_token_map_sha256'] == fit.TOKEN_MAP_SHA256
            and sha(fit.qualified.canonical(run['prepared_inputs'])) == fit.TOKEN_MAP_SHA256, 'Token map differs')
    train = {row['record_id']: row for row in fit.bundle.jsonl(train_path.read_bytes())}
    sources = {row['id']: row for row in rows}
    provenance = {}
    for row, pair in zip(rows, control['pairs']):
        saved = train[row['record_id']]
        for condition in ('correct', 'mismatched'):
            source = row if condition == 'correct' else sources[pair['mismatched_source_parent_id']]
            provenance[row['id'] + ':' + condition] = {
                'source_parent_id': source['id'], 'source_sha256': sha(source['source_text'].encode('utf-8')),
                'target_sha256': sha(saved['target'].encode('utf-8')),
                'training_row_sha256': sha(fit.qualified.canonical(saved))}
    require(run['train_sha256'] == fit.qualified.TRAIN_SHA256
            and run['parent_provenance'] == provenance, 'TRAIN parent provenance differs')
    expected = [fit.output_id(*item) for item in fit.schedule(rows)]
    require(run['schedule'] == expected and [r['id'] for r in records] == expected[:len(records)], 'First-attempt order differs')
    require(len(records) <= 80 and run['scheduled_outputs'] == 80, 'Invalid scheduled coverage')
    recorded, attempted = run['recorded_outputs'], run['attempted_outputs']
    # A durable result can precede its run.json counter by one write.
    require(type(recorded) is int and type(attempted) is int
            and recorded in (len(records), len(records) - 1) and recorded >= 0
            and attempted in (recorded, recorded + 1) and len(records) <= attempted <= 80,
            'Incoherent first-attempt counters')
    require(run['unattempted_output_ids'] == expected[attempted:]
            and run['active_output_id'] == (expected[attempted - 1] if attempted > recorded else None),
            'Incoherent active/unattempted state')
    success = Counter(r['case_id'] for r in records[:recorded] if r['status'] == 'success')
    require(run['completed_outputs'] == sum(success.values())
            and run['completed_cases'] == sum(n == 4 for n in success.values()), 'Incoherent completed counters')
    coverage = {'scheduled_outputs': 80, 'recovered_outputs': len(records),
                'execution_counts': dict(Counter(r['status'] for r in records)),
                'missing_output_ids': expected[len(records):], 'declared_run_status': run['status']}
    answer = {'diagnostic_only_not_translation_merit': True, 'expert_adjudicated': False,
              'manifest_sha256': recovery['manifest_sha256'], 'coverage': coverage,
              'limits': 'Selected familiar TRAIN parents; paired computational contrasts, not independent replication, causal proof, significance or generalization.'}
    require(run['loss_atol'] == fit.LOSS_ATOL and run['loss_rtol'] == fit.LOSS_RTOL, 'Loss tolerance differs')
    for index, ((parent, enabled, source), row) in enumerate(zip(fit.schedule(rows), records)):
        prepared = run['prepared_inputs'][parent['id'] + ':' + source]
        require(row['case_id'] == parent['id'] and row['record_id'] == parent['record_id']
                and row['work_id'] == parent['work_id'] and row['adapter_enabled'] is enabled
                and row['source_condition'] == source and row['sequence'] == index + 1
                and row['identity_sha256'] == run['identity_sha256']
                and row['input_sha256'] == prepared['input_ids_sha256']
                and all(row[key] == prepared[key] for key in
                        ('labels_sha256', 'target_ids_sha256', 'input_tokens', 'prompt_tokens')),
                'Recovered first-forward identity differs')
        require(row['status'] in ('success', 'error'), 'Unknown attempt status')
        if row['status'] == 'error':
            require(index == len(records) - 1 and run['status'] != 'completed'
                    and all(row[key] is None for key in ('sum_nll', 'mean_nll', 'supervised_tokens')),
                    'Failure must terminate the first-attempt prefix')
            continue
        require(row['supervised_tokens'] == prepared['supervised_tokens']
                and all(type(row[key]) in (int, float) and math.isfinite(row[key]) for key in
                        ('sum_nll', 'mean_nll', 'model_loss', 'numerical_loss_difference')), 'Invalid numerical evidence')
        require(row['sum_nll'] >= 0 and row['mean_nll'] >= 0
                and math.isclose(row['sum_nll'] / row['supervised_tokens'], row['mean_nll'], rel_tol=1e-12, abs_tol=1e-12)
                and math.isclose(row['mean_nll'], row['model_loss'], rel_tol=fit.LOSS_RTOL, abs_tol=fit.LOSS_ATOL)
                and math.isclose(abs(row['mean_nll'] - row['model_loss']), row['numerical_loss_difference'], rel_tol=1e-12, abs_tol=1e-12),
                'Loss arithmetic differs')
        proof = row['adapter_state']
        for name, enabled in (('before', True), ('during', row['adapter_enabled']), ('restored', True)):
            require(proof[name]['enabled'] is enabled and proof[name]['active_adapters'] == ['default']
                    and proof[name]['merged_adapters'] == [] and proof[name]['num_adapter_layers'] > 0,
                    'Adapter toggle evidence differs')
    if run['status'] != 'completed':
        return {**answer, 'status': 'INCOMPLETE_NO_AGGREGATE_COMPARISON', 'contrasts': None}
    package.completed_fit(recovered / 'fit', rows, control, manifest)
    return {**answer, 'status': 'COMPLETE_FIT_DIAGNOSTIC', 'contrasts': contrasts(records),
        'max_manual_model_loss_difference': max(r['numerical_loss_difference'] for r in records),
        'analysis_source_sha256': sha(Path(__file__).read_bytes())}


def self_test():
    records = [{'case_id': f'c{i}', 'work_id': f'w{i % 2}', 'adapter_enabled': enabled,
        'source_condition': source, 'supervised_tokens': i + 1,
        'mean_nll': i + (0 if enabled else 1) + (0 if source == 'correct' else 2)}
        for i in range(20) for enabled, source in fit.CONDITIONS]
    result = contrasts(records)
    assert result['all_parents']['parents'] == 20
    assert sum(x['parents'] for x in result['by_work'].values()) == 20
    for name, value in result['all_parents']['contrasts'].items():
        assert value['mean'] == (1 if name.startswith('adapter_gain') else 2)
        assert value['positive_count'] == 20
    for bad in (records[:-1], records + records[:1]):
        try:
            contrasts(bad)
        except ValueError:
            continue
        raise AssertionError('Missing/duplicate contrast accepted')
    print('Paired-contrast arithmetic and missing/duplicate rejection PASS')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--experiment', type=Path)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
    elif args.experiment:
        result = analyze(args.experiment)
        with (args.experiment / 'analysis.json').open('x', encoding='utf-8') as stream:
            json.dump(result, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write('\n')
        print(result['status'])
    else:
        parser.error('--experiment or --self-test required')
