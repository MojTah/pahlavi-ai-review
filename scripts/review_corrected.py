"""Offline frozen DEV72 comparison; no inference, cloud access or semantic judging."""
import argparse
import json
from pathlib import Path
import sys
from types import FunctionType

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import review_mixed as mixed, review_nllb as three

prep, scoring = mixed.prep, mixed.scoring
require, sha = prep.require, prep.sha
EXP = ROOT / 'experiments/training-ready-v2-20260929'
PRIOR = ROOT / 'experiments/mixed-review-20260929'
TRAIN = ROOT / 'resources/local/training-ready-v2-20260929/data/train.jsonl'
JOB_SPEC = ROOT / 'resources/local/training-ready-v2-20260929/job-spec.json'
RUN_ID = '157531204582c50f2d8f73aaa76ce8ac'
JOB_ID = '6abc15b8031314b696342162'
SOURCE_COMMIT = '28aeab6ae944ae1200fca33a5577ad359647e94e'
PREPARATION_SHA = 'bae4f02f8183e8b6a3a48e14d5920852839cc5fc2cb8e11417002bb367b55389'
SPEC_SHA = '4a373c2a4241693dbbdaba6343205a0405516ced43d67086261b6eea63add4db'
PRIOR_PROVENANCE_SHA = 'fc5fb3df9ac345ae08bee6a08fd3ddbb4cd8726a86a3706a772f3abdd16b473c'
CONDITIONS = ('gemma280_plain', 'mixed96_plain', 'corrected96_plain')
PAIRS = ((CONDITIONS[0], CONDITIONS[2]), (CONDITIONS[1], CONDITIONS[2]),
         (CONDITIONS[0], CONDITIONS[1]))
SEEDS = {'A': 2026093001, 'B': 2026093002}
HELPERS = {
    'scripts/review_mixed.py': '3df24a1b32c59f18060b186ba1eb1c3218c7b0155606ea8b38e9363f45bccb76',
    'scripts/review_nllb.py': '2467ad0b84b757d964e643c97a224fabe536711e30a80acffdd1a474f5a7e6b9',
    'scripts/prepare_blind_dev_assisted.py': 'dbb601e9ec806b4c4fe69c0fb39f2261d8e978441cf0fbf0975918ed4197153e',
    'scripts/score_blind_dev_assisted.py': '7dfa3ac29b038fb370f27a6afbfab6d6d2c733644a62c40fa26cac7e5bbeb5b5',
}


def bound(function, **constants):
    """Reuse frozen code with explicit constants, without changing module globals."""
    return FunctionType(function.__code__, function.__globals__ | constants,
                        function.__name__, function.__defaults__, function.__closure__)


def load_sources(experiment, prior, contract, rows, witnesses):
    from tokenizers import Tokenizer
    experiment, prior = Path(experiment), Path(prior)
    for name, digest in HELPERS.items():
        require(sha((ROOT / name).read_bytes()) == digest, 'Frozen review helper changed: ' + name)
    prior_provenance = (prior / 'lead-only/provenance.json').read_bytes()
    require(sha(prior_provenance) == PRIOR_PROVENANCE_SHA, 'Prior evidence freeze changed')
    prior_raw = prior / 'lead-only/raw'
    for name, digest in json.loads(prior_provenance)['files'].items():
        if name.startswith('lead-only/raw/'):
            require(sha((prior / name).read_bytes()) == digest, 'Prior raw evidence changed: ' + name)
    gemma_run, gemma_predictions, gemma_raw = prep.load_run(prior_raw / 'gemma280', 'gemma280', rows, witnesses)
    mixed.driver.runtime.checked_files(mixed.TOKENIZER, mixed.driver.bundle.TOKENIZER_HASHES)
    tokenizer = Tokenizer.from_file(str(mixed.TOKENIZER / 'tokenizer.json'))
    files = {'lead-only/raw/prior-review-provenance.json': prior_provenance}
    files.update({'lead-only/raw/gemma280/' + n: data for n, data in gemma_raw.items()})
    candidates, runs = {}, {}
    for condition, folder, train, expected_sha, run_id in (
        ('mixed96_plain', prior_raw, mixed.TRAIN, mixed.PREPARATION_SHA, mixed.RUN_ID),
        ('corrected96_plain', experiment / 'recovered', TRAIN, PREPARATION_SHA, RUN_ID),
    ):
        control = prior_raw if condition == 'mixed96_plain' else experiment
        preparation_bytes = (control / 'execution-preparation.json').read_bytes()
        require(sha(preparation_bytes) == expected_sha, 'Frozen preparation changed: ' + condition)
        preparation = json.loads(preparation_bytes)
        manifest_bytes = (folder / ('export-manifest.json' if condition == 'mixed96_plain' else 'manifest.json')).read_bytes()
        export = json.loads(manifest_bytes)
        recovery_bytes = (control / 'recovery.json').read_bytes()
        raw = bound(mixed.validate_recovery, RUN_ID=run_id)(folder, manifest_bytes, export,
                    json.loads(recovery_bytes), preparation)
        if condition == 'corrected96_plain':
            launch_bytes = (experiment / 'launch.json').read_bytes()
            intent_bytes = (experiment / 'submission-intent.json').read_bytes()
            spec_bytes = JOB_SPEC.read_bytes()
            launch, intent = json.loads(launch_bytes), json.loads(intent_bytes)
            require(launch.get('id') == JOB_ID and launch.get('run_id') == intent.get('run_id') == RUN_ID
                    and launch.get('source_commit') == intent.get('source_commit') == SOURCE_COMMIT
                    and intent.get('spec_sha256') == sha(spec_bytes) == SPEC_SHA
                    and preparation['output_prefix'] == 'mixed-supervision/' + RUN_ID,
                    'Corrected launch binding differs')
            for name, digest in {**preparation['script_hashes'], **preparation['bootstrap_hashes']}.items():
                require(sha((ROOT / 'cloud_pilot' / name).read_bytes()) == digest, 'Current launch helper changed: ' + name)
            raw.update({'launch.json': launch_bytes, 'submission-intent.json': intent_bytes, 'job-spec.json': spec_bytes})
        else:
            raw['execution.json'] = (control / 'execution.json').read_bytes()
            execution = json.loads(raw['execution.json'])
            require(execution.get('run_id') == mixed.RUN_ID and execution.get('job_id') == '6abb82b6e2f3c356be0389a3'
                    and execution.get('source_commit') == 'e0ba397629b4e9d9c4962600080ae0d751e829f9'
                    and execution.get('spec_sha256') == preparation['spec_sha256']
                    and execution.get('output_prefix') == preparation['output_prefix'], 'Prior launch differs')
        for key in ('run_id', 'inputs_sha256', 'train_sha256', 'data_manifest_sha256', 'bundle_sha256',
                    'trained_manifest_sha256', 'adapter_files', 'script_hashes', 'training_settings', 'prompt_identities', 'steps'):
            require(export.get(key) == preparation.get(key), 'Export/launch identity differs: ' + key)
        require(export.get('operation') == 'mixed_supervision' and export.get('quality_validated') is False,
                'Export operation differs')
        status = json.loads(raw['mixed-status.json'])
        require(all(export.get(k) == v for k, v in status.items()), 'Export/status contradiction')
        train_rows, manifest = mixed.driver.read_data(train, folder / 'data-manifest.json', preparation)
        top, training, evaluation = (json.loads(raw[n]) for n in ('mixed/run.json', 'mixed/training/run.json', 'mixed/evaluation/run.json'))
        for adapter, field in (('adapter', 'adapter_files'), ('bounded-adapter-step20', 'canary_adapter_files')):
            prefix = 'mixed/training/' + adapter + '/'
            require({n[len(prefix):] for n in export['files'] if n.startswith(prefix)} == set(training[field]),
                    'Adapter export inventory differs')
            for name, digest in training[field].items():
                require(export['files'][prefix + name]['sha256'] == digest
                        and export['files'][prefix + name]['bytes'] > 0, 'Adapter export hash differs')
        predictions = prep.decode_lines(raw['mixed/evaluation/predictions.jsonl'])
        completion = mixed.validate_artifacts(top, training, evaluation, predictions, rows, preparation,
                                             train_rows, manifest, gemma_run, tokenizer)
        completion['complete'] &= export.get('mixed_status') == 'complete'
        require(completion['complete'], 'Complete source-only first attempts required: ' + condition)
        candidates[condition] = prep.unique(predictions, 'case_id')
        runs[condition] = completion
        raw.update({'execution-preparation.json': preparation_bytes, 'recovery.json': recovery_bytes})
        files.update({'lead-only/raw/' + condition + '/' + name: data for name, data in raw.items()})
    candidates['gemma280_plain'] = {p['case_id']: p for p in gemma_predictions if p['condition'] == 'plain'}
    records = {(condition, row['id']): dict(candidates[condition][row['id']],
               execution_status=candidates[condition][row['id']]['status']) for condition in CONDITIONS for row in rows}
    completion = dict(training_completed=all(r['complete'] for r in runs.values()), runs=runs,
        gemma_original_run_completed=gemma_run['status'] == 'completed' and gemma_run['completed_outputs'] == 48,
        conditions={c: dict(attempted=24, scheduled=24, usable_execution=all(records[c, r['id']]['status']
                    in {'success', 'abstain'} for r in rows)) for c in CONDITIONS})
    require(completion['gemma_original_run_completed'], 'Complete retained Gemma run required')
    for name in ('references.jsonl', 'assessment-contract.json', 'reviewer-clarification.json'):
        files['lead-only/frozen/' + name] = (prep.DEV / name).read_bytes()
    files['lead-only/frozen/reused-helpers.json'] = prep.json_bytes(HELPERS)
    return records, completion, files


def build_files(experiment=EXP, prior=PRIOR):
    files, contract, completion = bound(three.build_files, load_sources=load_sources,
            CONDITIONS=CONDITIONS, SEEDS=SEEDS, __file__=__file__)(experiment, prior)
    for reviewer in SEEDS:
        name = f'reviewer-{reviewer}/INSTRUCTIONS.md'
        files[name] += (b'\nIf source, references, assessment, constraint, execution status and output are identical '
                       b'across opaque records, keep semantic ratings consistent. Retain every record; repeated '
                       b'outputs are not independent evidence. Reconsider any conflict before freezing your file.\n')
    provenance = json.loads(files['lead-only/provenance.json'])
    provenance.update(status='LOCAL_BLIND_CORRECTED_DEV72_PREPARED', pairs=PAIRS,
        files={name: sha(data) for name, data in files.items() if name != 'lead-only/provenance.json'})
    files['lead-only/provenance.json'] = prep.json_bytes(provenance)
    return files, contract, completion


def duplicate_consistency(packet, reviews):
    """Check blind semantic consistency; never change a rating or expose an arm."""
    ratings = scoring.validate_reviews(packet, reviews, expected_count=72)
    seen = {}
    for row in packet:
        key = prep.shared.canonical({k: v for k, v in row.items() if k != 'review_id'})
        rating = ratings[row['review_id']]
        semantic = {k: rating[k] for k in ('judgment', 'categories', 'supported_span_severity', 'unknown_span_handling')}
        if key in seen:
            previous_id, previous = seen[key]
            require(semantic == previous, 'Blind duplicate ratings conflict; reconsider opaque records '
                    + previous_id + ' and ' + row['review_id'])
        else:
            seen[key] = (row['review_id'], semantic)


def summarize(mapping, packets, reviews, contract, completion):
    for reviewer in SEEDS:
        duplicate_consistency(packets[reviewer], reviews[reviewer])
    result = bound(three.summarize, CONDITIONS=CONDITIONS, PAIRS=PAIRS)(mapping, packets, reviews, contract, completion)
    result.pop('descriptive_pair')
    result.update(primary_pair=' -> '.join(PAIRS[0]), repair_pair=' -> '.join(PAIRS[1]),
        historical_pair=' -> '.join(PAIRS[2]),
        limits='Fixed exposed DEV; separate AI raters and paired cases, no reviewer pooling, significance, '
               'specialist certification, PALREF score or automatic promotion. Identical outputs are repeated '
               'paired observations, not independent evidence. Repair comparison does not isolate each data change.')
    return result


def prepare(output_dir, experiment=EXP, prior=PRIOR):
    files, _, completion = build_files(experiment, prior)
    prep.write_fresh(output_dir, files)
    return dict(status='LOCAL_BLIND_CORRECTED_DEV72_PREPARED', completion=completion,
                provenance_sha256=sha(files['lead-only/provenance.json']))


def score(packet_dir, output_dir, experiment=EXP, prior=PRIOR, review_a=None, review_b=None):
    files, contract, completion = build_files(experiment, prior)
    for name, data in files.items():
        require((Path(packet_dir) / name).read_bytes() == data, 'Frozen packet/evidence changed: ' + name)
    paths = {r: Path(explicit) if explicit else Path(packet_dir) / f'reviewer-{r}/reviews.jsonl'
             for r, explicit in (('A', review_a), ('B', review_b))}
    require(paths['A'].resolve() != paths['B'].resolve(), 'Separate reviewer files required')
    raw = {r: path.read_bytes() for r, path in paths.items()}
    packets = {r: prep.decode_lines(files[f'reviewer-{r}/packet.jsonl']) for r in SEEDS}
    reviews = {r: prep.decode_lines(data) for r, data in raw.items()}
    result = summarize(prep.decode_lines(files['lead-only/mapping.jsonl']), packets, reviews, contract, completion)
    freeze = {r: dict(sha256=sha(data), rows=len(reviews[r]), reviewer_type='AI', expert_adjudicated=False)
              for r, data in raw.items()}
    result.update(blind_review_freeze=freeze, packet_provenance_sha256=sha(files['lead-only/provenance.json']),
                  scorer_sha256=HELPERS['scripts/score_blind_dev_assisted.py'])
    prep.write_fresh(output_dir, {'comparison.json': prep.json_bytes(result),
        'blind-review-freeze.json': prep.json_bytes(freeze),
        **{f'reviewer-{r}/reviews.jsonl': data for r, data in raw.items()}})
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('prepare', 'score'):
        sub = commands.add_parser(name)
        if name == 'score':
            sub.add_argument('packet_dir', type=Path)
            sub.add_argument('--review-a', type=Path)
            sub.add_argument('--review-b', type=Path)
        sub.add_argument('output_dir', type=Path)
        sub.add_argument('--experiment', type=Path, default=EXP)
        sub.add_argument('--prior', type=Path, default=PRIOR)
    args = vars(parser.parse_args())
    command = args.pop('command')
    result = prepare(**args) if command == 'prepare' else score(**args)
    print(json.dumps({k: result[k] for k in ('status', 'completion', 'both_reviewers_screen') if k in result}, indent=2))
