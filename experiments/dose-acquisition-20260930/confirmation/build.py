"""Offline deterministic pilot-heldout panel; no prediction-dependent selection."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DATA = ROOT / 'resources/local/training-ready-v2-20260929/data'
LEXICAL = {'lexical-fa', 'lexical-en', 'lexical-mmp-en'}
def rows(path):
    return [json.loads(line) for line in path.read_text('utf-8').splitlines()]
def js(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
def sha(data):
    return hashlib.sha256(data).hexdigest()
def norm(text):
    text = unicodedata.normalize('NFKD', text.casefold())
    return ''.join(c for c in text if not unicodedata.combining(c) and c.isalpha())
def forms(row):
    source = row['learning']['source']
    if isinstance(source, list):
        return {norm(part) for form in source for part in [form] + form.split() if norm(part)}
    return {norm(word) for word in re.findall(r'[^\s]+', source) if norm(word)}
def families(row):
    return {source.get('observation_id', '') for entry in row.get('lexical_provenance', {}).get('entries', [])
            for source in entry.get('sources', [])} - {''}
def write(name, value):
    (OUT / name).write_text(value, encoding='utf-8')
def build():
    spec = importlib.util.spec_from_file_location('corrected_prepare', ROOT / 'experiments/training-ready-v2-20260929/prepare.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    pool = {r['id']: r for r in rows(DATA / 'pool.jsonl')}
    train = rows(DATA / 'train.jsonl')
    projections = {r['id']: r for r in rows(DATA / 'learning-projections.jsonl')}
    audit = {r['id']: r for r in rows(DATA / 'row-audit.jsonl')}
    parent_map = rows(DATA / 'parent-map.jsonl')
    train_ids = {r['id'] for r in train}
    train_parents = {r['id'] for r in parent_map if r['output_id'] in train_ids}
    train_groups = {audit[i]['group'] for i in train_ids}
    blocked_forms = set().union(*(forms(projections[i]) for i in train_ids))
    blocked_families = set().union(*(families(projections[i]) for i in train_ids))
    fixed_paths = [ROOT / 'resources/local/qualitydev1-inputs.roundtrip.jsonl', ROOT / 'experiments/corrected-learning-diagnosis-20260930/inputs.jsonl']
    fixed = [r for path in fixed_paths for r in rows(path)]
    for row in fixed:
        if 'prompt' not in row:
            row['prompt'] = module.bundle.PROMPT.format(text=row['source_text'].strip())
    # Exclude every lexical-looking word in fixed evaluation prompts, not just case IDs.
    for row in fixed:
        blocked_forms.update(norm(word) for word in re.findall(r"[^\s\[\]\"{},:]+", row['prompt']) if norm(word))
    fixed_prompts = {r['prompt'] for r in fixed}
    excluded_forms, excluded_families = set(blocked_forms), set(blocked_families)
    train_prefixes = {tuple(r['input_ids'][:r['prompt_tokens']]) for r in train}
    selected, counts = [], {}
    for task, number in [('lexical-fa', 2), ('lexical-en', 1), ('lexical-mmp-en', 1), ('inscription-fa', 1)]:
        candidates = []
        for identifier, row in projections.items():
            if row['task'] != task or identifier not in pool or identifier in train_ids or set(row['parent_ids']) & train_parents:
                continue
            prompt, answer = module.prompt_answer(row)
            prefix = pool[identifier]['input_ids'][:pool[identifier]['prompt_tokens']]
            if prompt in fixed_prompts or tuple(prefix) in train_prefixes:
                continue
            if task in LEXICAL:
                if forms(row) & blocked_forms or families(row) & blocked_families:
                    continue
            elif audit[identifier]['group'] in train_groups:
                continue
            candidates.append(identifier)
        candidates.sort(key=lambda identifier: sha(('dose-confirmation-v1:' + identifier).encode()))
        counts[task] = len(candidates)
        picked = []
        for identifier in candidates:
            row = projections[identifier]
            if task in LEXICAL and (forms(row) & blocked_forms or families(row) & blocked_families):
                continue
            picked.append(identifier)
            blocked_forms.update(forms(row)); blocked_families.update(families(row))
            if len(picked) == number:
                break
        assert len(picked) == number, (task, counts, picked)
        selected.extend(picked)
    inputs, refs = [], []
    for index, identifier in enumerate(selected, 1):
        row = projections[identifier]; prompt, answer = module.prompt_answer(row)
        tokens = pool[identifier]['input_ids'][:pool[identifier]['prompt_tokens']]
        assert sha(prompt.encode()) == audit[identifier]['prompt_sha256']
        assert tuple(tokens) not in train_prefixes
        assert identifier not in train_ids and not set(row['parent_ids']) & train_parents
        assert prompt not in fixed_prompts
        if row['task'] in LEXICAL:
            assert not forms(row) & excluded_forms and not families(row) & excluded_families
        else:
            assert audit[identifier]['group'] not in train_groups
        case = f'CONF-{index:03d}'
        inputs.append({'case_id': case, 'prompt': prompt})
        refs.append({'case_id': case, 'record_id': identifier, 'task': row['task'], 'learning': row['learning'],
                     'expected_training_answer': answer, 'parent_ids': row['parent_ids'],
                     'source_group': audit[identifier]['group'], 'lexical_entry_families': sorted(families(row)),
                     'normalized_forms': sorted(forms(row)), 'prompt_token_ids': tokens,
                     'row_audit': audit[identifier], 'pretraining_exposure': 'UNKNOWN',
                     'pilot_exact_record_exposed': False, 'expert_certified': False})
    assert len(inputs) == 5 and len({r['prompt'] for r in inputs}) == 5
    lexical = [projections[i] for i in selected if projections[i]['task'] in LEXICAL]
    for index, row in enumerate(lexical):
        for other in lexical[index + 1:]:
            assert not forms(row) & forms(other) and not families(row) & families(other)
    write('inputs.jsonl', ''.join(js(r) + '\n' for r in inputs))
    write('references.jsonl', ''.join(js(r) + '\n' for r in refs))
    evidence = {'selected_ids': selected, 'candidate_counts_before_panel_mutual_exclusion': counts,
                'selection_rule': 'SHA256(dose-confirmation-v1:ID), task quota; no model output read',
                'train_rows_excluded': len(train), 'fixed_evaluation_rows_excluded': len(fixed),
                'checks': {'exact_train_id_overlap': 0, 'exact_train_prompt_token_prefix_overlap': 0,
                           'exact_fixed_prompt_overlap': 0, 'lexical_normalized_forms_overlap_with_train': 0,
                           'lexical_observation_entry_family_overlap_with_train': 0,
                           'inscription_work_group_overlap_with_train': 0},
                'input_sha256': {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p.read_bytes()) for p in
                                 [DATA / name for name in ['pool.jsonl','train.jsonl','learning-projections.jsonl','parent-map.jsonl','row-audit.jsonl']] + fixed_paths},
                'output_sha256': {name: sha((OUT / name).read_bytes()) for name in ['inputs.jsonl','references.jsonl']},
                'limitations': ['Pilot-heldout only; step280/base pretraining exposure unknown.',
                                'Lexical source editions overlap training; exclusion is normalized form and observation entry identity, not edition independence.',
                                'Normalization is a conservative string check, not expert lemmatization; related derivational families cannot be exhaustively certified.',
                                'No unused documentary/edition spans; unused historical and pedagogy rows share training work/context families. Only one unused inscription is group-disjoint.',
                                'Five-case diagnostic is not broad translation/generalization validation.']}
    write('selection.json', json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    print(js({'selected': selected, 'candidate_counts': counts, 'checks': evidence['checks']}))
if __name__ == '__main__':
    build()
