"""Offline exposure audit and fixed diagnostic packet; never runs a model."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DATA = ROOT / 'resources/local/mixed-supervision-20260929/data'
MANIFEST = ROOT / 'experiments/mixed-supervision-20260929/data-manifest.json'
PREPARE = ROOT / 'experiments/mixed-supervision-20260929/prepare.py'
QUALIFICATION = ROOT / 'experiments/contextual-supervision-20260927/qualification-decision-v2.json'
LEDGER = ROOT / 'experiments/train-audit-20260927/qualified-v1/final-ledger.jsonl'
LEXICAL = [
    'FAINV:lex:99f6033945f96433c70ea61566f8481b6a80783656bb62ba3cad22488d62d591',
    'FAINV:lex:7ba14ce5c6b2066e60c1a2d66e51e51e0d537f4348b64ffe903473231f6c5fe1',
    'kosh:cpd:9049ab850e04a9f20ec390e683ee173714318a93:block:0',
    'kosh:cpd:9049ab850e04a9f20ec390e683ee173714318a93:block:1',
    'recovered:kosh:mmp:1030', 'recovered:kosh:mmp:5418',
]
TEACHING = ['S22CLAUSE-002', 'S22CLAUSE-003', 'S22CLAUSE-006', 'S22CLAUSE-007']
INSCRIPTIONS = ['KANHERI-ARTICLE-01-ARRIVAL', 'KANHERI-ARTICLE-02-DATED-ARRIVAL']
CONTRASTS = ['parsig:134004021:pal>fa', 'parsig:509000009:pal>fa',
             'parsig:137001031:pal>fa', 'parsig:151031008:pal>fa']


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode('utf-8')


def forms(row):
    value = row['learning']['source']
    return value if isinstance(value, list) else [value]


def normalize(value):
    return ' '.join(unicodedata.normalize('NFC', value).casefold().split())


def overlaps(form, text):
    return re.search(r'(?<!\w)' + re.escape(normalize(form)) + r'(?!\w)', normalize(text)) is not None


def build():
    manifest = json.loads(MANIFEST.read_bytes())
    loaded, bindings = {}, {}
    for name in ['learning-projections.jsonl', 'pool.jsonl', 'train.jsonl', 'row-audit.jsonl']:
        path = DATA / name
        raw = path.read_bytes()
        expected = manifest['outputs'][name]
        assert len(raw) == expected['bytes'] and digest(raw) == expected['sha256'], name
        loaded[name] = [json.loads(line) for line in raw.splitlines()]
        bindings[path.relative_to(ROOT).as_posix()] = digest(raw)
    assert digest(PREPARE.read_bytes()) == manifest['script_sha256']
    spec = importlib.util.spec_from_file_location('frozen_prepare', PREPARE)
    prep = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prep)
    assert digest(Path(prep.bundle.__file__).read_bytes()) == manifest['bundle_helper_sha256']
    for path in [MANIFEST, PREPARE, QUALIFICATION, Path(prep.bundle.__file__)]:
        bindings[path.relative_to(ROOT).as_posix()] = digest(path.read_bytes())
    ledger_manifest_path = LEDGER.with_name('manifest.json')
    assert digest(ledger_manifest_path.read_bytes()) == prep.bundle.QUALIFIED_MANIFEST_HASH
    ledger_manifest = json.loads(ledger_manifest_path.read_bytes())
    ledger_raw = LEDGER.read_bytes()
    assert digest(ledger_raw) == ledger_manifest['files'][LEDGER.name]['sha256']
    ledger = {r['id']: r for r in map(json.loads, ledger_raw.splitlines())}
    for path in [LEDGER, ledger_manifest_path]:
        bindings[path.relative_to(ROOT).as_posix()] = digest(path.read_bytes())

    pool = {r['id']: r for r in loaded['pool.jsonl']}
    rows = {r['id']: r for r in loaded['learning-projections.jsonl'] if r['id'] in pool}
    train = {r['id']: r for r in loaded['train.jsonl']}
    audit = {r['id']: r for r in loaded['row-audit.jsonl']}
    assert len(rows) == len(pool) == len(audit) == 10151 and len(train) == 1536
    assert all(pool[k] == v for k, v in train.items())
    historical = [r for r in rows.values() if r['task'] == 'historical-control-fa']
    lexical = [rows[k] for k in train if rows[k]['task'].startswith('lexical-')]
    links, form_hits = [], Counter()
    for h in historical:
        matches = [{'lexical_id': r['id'], 'form': f} for r in lexical for f in forms(r)
                   if overlaps(f, h['learning']['source'])]
        if matches:
            links.append({'parent_id': h['id'], 'surface_matches_only': matches})
            form_hits.update({normalize(m['form']) for m in matches})
    stats = {}
    for task in manifest['pool_counts']:
        all_rows = [r for r in pool.values() if r['task'] == task]
        selected = [r for r in train.values() if r['task'] == task]
        stats[task] = {'pool_records': len(all_rows), 'selected_records': len(selected),
                       'selected_supervised_tokens': sum(sum(x != -100 for x in r['labels']) for r in selected)}
        assert stats[task]['selected_supervised_tokens'] == manifest['pilot']['task_statistics'][task]['supervised_tokens']
    auxiliary = sum(v['selected_supervised_tokens'] for k, v in stats.items() if k != 'historical-control-fa')
    english = sum(v['selected_supervised_tokens'] for k, v in stats.items() if k.endswith('-en'))

    qualified = json.loads(QUALIFICATION.read_bytes())['decisions']
    anchors = {'parsig:' + q['id'].split('-')[1] + ':pal>fa': q for q in qualified}
    assert len(anchors) == 12
    selections = [(k, 'lexical_task_recall') for k in LEXICAL]
    selections += [(k, 'conditioned_grammar_recall') for k in TEACHING]
    selections += [(k, 'inscription_task_recall') for k in INSCRIPTIONS]
    selections += [(k, 'historical_context_retention') for k in sorted(anchors)]
    selections += [(k, 'targeted_sense_applicability') for k in CONTRASTS]
    assert len(selections) == len(set(k for k, _ in selections)) == 28
    inputs, references = [], []
    for i, (key, module) in enumerate(selections, 1):
        row, learning = rows[key], rows[key]['learning']
        task, source = row['task'], learning['source']
        if task == 'historical-control-fa':
            prompt = prep.bundle.PROMPT.format(text=source.strip())
            answer = learning['target'].strip()
        else:
            assert key in train, ('Auxiliary probe was not actually trained', key)
            rendered_source = source if isinstance(source, str) else prep.js(source)
            prompt = prep.PROMPTS[task] + '\nContext:\n' + prep.js(learning['context']) + '\nSource:\n' + rendered_source
            answer = prep.js(learning['target']) if task == 'lexical-en' else learning['target']
        assert digest(prompt.encode('utf-8')) == audit[key]['prompt_sha256'], key
        assert digest(answer.encode('utf-8')) == audit[key]['answer_sha256'], key
        case_id = f'LD-{i:03d}'
        inputs.append({'case_id': case_id, 'prompt': prompt})
        reference = {'case_id': case_id, 'record_id': key, 'task': task, 'module': module,
                     'learning': learning, 'expected_training_answer': answer,
                     'step280_historical_pair_exposed': task == 'historical-control-fa',
                     'mixed96_exact_record_exposed': key in train,
                     'pretraining_exposure': 'UNKNOWN', 'expert_certified': False,
                     'source_group': audit[key]['group'],
                     'upstream_learning_sha256': audit[key]['learning_sha256']}
        if task == 'historical-control-fa':
            original = ledger[key]
            assert original['source_sha256'] == digest(source.encode('utf-8'))
            assert original['target_sha256'] == digest(learning['target'].encode('utf-8'))
            reference['qualified_train_ledger'] = original
        if key in anchors:
            reference['existing_scoped_qualification'] = anchors[key]
        if module == 'targeted_sense_applicability':
            reference['scope_gold'] = 'No new isolated-word gold; use complete original published target and preserve unresolved scope.'
        references.append(reference)
    summary = {'status': 'LOCAL_PACKET_PREPARED_NOT_RUN', 'claim': 'Exposure and task-compatibility diagnosis, not model mastery or novel-context generalization',
               'input_sha256': bindings, 'script_sha256': digest(Path(__file__).read_bytes()),
               'statistics': stats, 'auxiliary_supervised_tokens': auxiliary,
               'english_auxiliary_supervised_tokens': english, 'english_auxiliary_token_fraction': english / auxiliary,
               'selected_lexical_records': len(lexical),
               'historical_records_with_surface_overlap': len(links),
               'surface_overlap_is_sense_coverage': False, 'top_surface_matches': form_hits.most_common(10),
               'packet_records': len(inputs), 'modules': dict(Counter(r['module'] for r in references)),
               'new_predictions': 0, 'training_launched': False, 'model_weights_downloaded': False,
               'benchmark_content_read': False, 'selection': 'Purposive risk/contrast selection plus all12 previously qualified contextual parents; not random or representative.'}
    outputs = {'inputs.jsonl': b''.join(encode(r) for r in inputs),
               'references.jsonl': b''.join(encode(r) for r in references),
               'surface-links.jsonl': b''.join(encode(r) for r in links)}
    summary['output_sha256'] = {k: digest(v) for k, v in outputs.items()}
    outputs['census.json'] = encode(summary)
    return outputs


def check(outputs):
    inputs = [json.loads(x) for x in outputs['inputs.jsonl'].splitlines()]
    refs = [json.loads(x) for x in outputs['references.jsonl'].splitlines()]
    assert len(inputs) == len(refs) == 28
    assert all(set(r) == {'case_id', 'prompt'} for r in inputs)
    assert [r['case_id'] for r in inputs] == [r['case_id'] for r in refs]
    assert sum(r['step280_historical_pair_exposed'] for r in refs) == 16
    assert all('qualified_train_ledger' in r for r in refs if r['step280_historical_pair_exposed'])
    assert not overlaps('ēr', 'ērān') and overlaps('ēr', 'kōf ēr kaft')
    assert overlaps('ī', 'a i\u0304 b') and not overlaps('i', 'a ī b')
    assert not overlaps('²kardan', 'kardan')
    print('PASS: upstream identities, exact prompt/answer reconstruction, exposure joins, 28-case separation, and surface-match edge checks')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Rebuild in memory and compare saved outputs without writing')
    args = parser.parse_args()
    outputs = build()
    check(outputs)
    for name, raw in outputs.items():
        path = HERE / name
        if args.check:
            assert path.read_bytes() == raw, name
        else:
            if path.exists() and path.read_bytes() != raw:
                raise FileExistsError(f'Refusing to replace a changed frozen output: {path}')
            path.write_bytes(raw)
    print('CHECKED' if args.check else 'PREPARED', '28 prompts; no inference or training')
