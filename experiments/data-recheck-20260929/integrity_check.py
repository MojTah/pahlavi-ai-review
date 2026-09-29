"""Read canonical data; write only this audit's metadata-only integrity.json."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import ast
import hashlib
import json
from pathlib import Path
import unicodedata

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
READY = ROOT / 'resources/local/data-qualification-20260928/ready-v1'
MIXED = ROOT / 'resources/local/mixed-supervision-20260929/data'
checks, files = [], []


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def js(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def read(path):
    return json.loads(Path(path).read_text('utf-8'))


def rows(path):
    return [json.loads(line) for line in Path(path).read_text('utf-8').splitlines() if line.strip()]


def check(name, condition, **details):
    checks.append(dict(check=name, status='PASS' if condition else 'FAIL', **details))


def ids(data):
    return [r['id'] for r in data]


def constants(path, name):
    tree = ast.parse(Path(path).read_text('utf-8'))
    return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == name for t in n.targets))


def norm(value):
    return ' '.join(unicodedata.normalize('NFC', value).casefold().split())


release_path = ROOT / 'experiments/data-qualification-20260928/release-v1.json'
mixed_manifest_path = ROOT / 'experiments/mixed-supervision-20260929/data-manifest.json'
release, manifest = read(release_path), read(mixed_manifest_path)
check('release_bound_by_mixed_manifest', sha(release_path.read_bytes()) == manifest['release_sha256'])
check('release_builder_identity', sha((ROOT / 'experiments/data-qualification-20260928/freeze_release.py').read_bytes()) == release['script_sha256'])
check('mixed_builder_identity', sha((ROOT / 'experiments/mixed-supervision-20260929/prepare.py').read_bytes()) == manifest['script_sha256'])
check('bundle_helper_identity', sha((ROOT / 'cloud_pilot/bundle.py').read_bytes()) == manifest['bundle_helper_sha256'])
check('canonical_file_sets', {p.name for p in READY.iterdir()} == set(release['outputs'])
      and {p.name for p in MIXED.iterdir()} == set(manifest['outputs']) | {'census.json'})
for directory, expected in ((READY, release['outputs']), (MIXED, manifest['outputs'])):
    for name, frozen in expected.items():
        raw = (directory / name).read_bytes()
        text_lines = raw.decode('utf-8').splitlines()
        count = len(text_lines)
        valid = sha(raw) == frozen['sha256'] and len(raw) == frozen['bytes'] and count == frozen['rows']
        check('file_identity:' + name + ':' + directory.name, valid,
              blank_lines=sum(not x.strip() for x in text_lines))
        files.append(dict(path=(directory / name).relative_to(ROOT).as_posix(), bytes=len(raw),
                          rows=count, sha256=sha(raw), frozen_identity_matches=valid))
census_raw = (MIXED / 'census.json').read_bytes()
check('census_exact_manifest_bytes', census_raw == mixed_manifest_path.read_bytes())
check('no_blank_canonical_jsonl_lines', all(c.get('blank_lines', 0) == 0 for c in checks))
files.append(dict(path=(MIXED / 'census.json').relative_to(ROOT).as_posix(), bytes=len(census_raw),
                  rows=1, sha256=sha(census_raw), frozen_identity_matches=census_raw == mixed_manifest_path.read_bytes()))

tasks = {p.stem: rows(p) for p in READY.glob('*.jsonl') if p.stem not in {'excluded', 'duplicate-groups'}}
released = {r['id']: (task, r) for task, data in tasks.items() for r in data}
check('release_global_unique_ids', len(released) == sum(map(len, tasks.values())) == 10152)
missing = []
for task, data in tasks.items():
    for r in data:
        if task == 'historical-control-fa':
            good = all(isinstance(r.get(k), str) and r[k].strip() for k in ('id', 'text', 'target', 'work_id'))
        else:
            learn = r.get('learning', {})
            good = (r.get('task') == task and set(learn) == {'source', 'target', 'context'}
                    and bool(learn['source']) and bool(learn['target']) and isinstance(learn['context'], dict)
                    and all(r.get(k) for k in ('id', 'origin', 'qualification', 'use_restriction')))
        if not good:
            missing.append(r['id'])
check('required_learning_fields_nonblank', not missing, count=len(missing), example_ids=missing[:5])

projections = rows(MIXED / 'learning-projections.jsonl')
pool, train, audits = (rows(MIXED / name) for name in ('pool.jsonl', 'train.jsonl', 'row-audit.jsonl'))
duplicate_rows, excluded = rows(MIXED / 'duplicates.jsonl'), rows(READY / 'excluded.jsonl')
projected = {r['id']: r for r in projections}
pool_map, train_map, audit_map = ({r['id']: r for r in data} for data in (pool, train, audits))
for name, data in [('projections', projections), ('pool', pool), ('train', train), ('row-audit', audits)]:
    check(name + '_unique_nonblank_ids', len(set(ids(data))) == len(data) and all(ids(data)), rows=len(data))
projection_bad = []
for identifier, (task, r) in released.items():
    expected = dict(source=r['text'], target=r['target'], context={}) if task == 'historical-control-fa' else r['learning']
    if projected.get(identifier) != dict(id=identifier, task=task, learning=expected):
        projection_bad.append(identifier)
check('verbatim_release_to_learning_projection', not projection_bad and set(projected) == set(released),
      mismatches=len(projection_bad), example_ids=projection_bad[:5])
exact_groups = defaultdict(list)
for r in projections:
    exact_groups[js(dict(task=r['task'], learning=r['learning']))].append(r['id'])
expected_collapses = {(g[i], g[0]) for g in exact_groups.values() for i in range(1, len(g))}
actual_collapses = {(r['id'], r['canonical_id']) for r in duplicate_rows}
check('exact_complete_context_duplicate_policy', expected_collapses == actual_collapses,
      collapsed_records=len(actual_collapses), duplicate_ids=[dict(removed=a, retained=b) for a, b in sorted(actual_collapses)])
check('released_pool_identity', set(pool_map) == set(released) - {a for a, b in actual_collapses}
      and set(pool_map) == set(audit_map) and not rows(MIXED / 'exclusions.jsonl'))
check('train_is_exact_pool_subset', all(pool_map.get(r['id']) == r for r in train))
consumed = read(ROOT / 'experiments/mixed-supervision-20260929/recovered/mixed/training/run.json')
check('saved_selection_and_consumed_order', ids(train) == manifest['pilot']['selected_ids_in_order']
      == consumed['ordered_ids'] and consumed['completed_steps'] == 96 and consumed['consumed_slots'] == 1536)
valid_blocks = 0
for start in range(0, len(train), 16):
    block = [r['task'] for r in train[start:start + 16]]
    valid_blocks += (block[:12] == ['historical-control-fa'] * 12
                     and all(t in {'lexical-fa', 'lexical-en', 'lexical-mmp-en'} for t in block[12:14])
                     and all(t in {'pedagogy-fa', 'documentary-en', 'inscription-fa', 'edition-spans-en'} for t in block[14:]))
check('per_update_12_2_2_order', valid_blocks == 96, valid_updates=valid_blocks)

from tokenizers import Tokenizer
tokenizer_dir = ROOT / 'resources/local/cloud-pilot-qualified-20260927/tokenizer'
for name, frozen in manifest['tokenizer_sha256'].items():
    check('tokenizer_identity:' + name, sha((tokenizer_dir / name).read_bytes()) == frozen)
tokenizer = Tokenizer.from_file(str(tokenizer_dir / 'tokenizer.json'))
vocab = tokenizer.get_vocab_size()
task_prompts = constants(ROOT / 'experiments/mixed-supervision-20260929/prepare.py', 'PROMPTS')
historical_prompt = constants(ROOT / 'cloud_pilot/bundle.py', 'PROMPT')
mask_bad, decode_bad, audit_bad = [], [], []
for r in pool:
    token, label, attention, boundary = (r[k] for k in ('input_ids', 'labels', 'attention_mask', 'prompt_tokens'))
    good = (type(boundary) is int and 0 < boundary < len(token) <= 2048 and len(token) == len(label) == len(attention)
            and all(type(x) is int and 0 <= x < vocab for x in token) and attention == [1] * len(token)
            and label == [-100] * boundary + token[boundary:])
    if not good:
        mask_bad.append(r['id']); continue
    source = projected[r['id']]
    answer = source['learning']['target']
    answer = js(answer) if r['task'] == 'lexical-en' else answer
    if r['task'] == 'historical-control-fa':
        answer = answer.strip()
        prompt = historical_prompt.format(text=source['learning']['source'].strip())
    else:
        form = source['learning']['source']
        prompt = task_prompts[r['task']] + '\nContext:\n' + js(source['learning']['context']) + '\nSource:\n' + (form if isinstance(form, str) else js(form))
    decoded = tokenizer.decode(token[boundary:], skip_special_tokens=False)
    if decoded != answer + '<turn|>\n':
        decode_bad.append(r['id'])
    a = audit_map[r['id']]
    if (a['answer_sha256'] != sha(answer.encode()) or a['prompt_sha256'] != sha(prompt.encode())
            or a['learning_sha256'] != sha((js(source['learning']) + '\n').encode())
            or a['prompt_tokens'] != boundary or a['sequence_tokens'] != len(token)):
        audit_bad.append(r['id'])
check('pool_token_masks_boundaries_and_lengths', not mask_bad, checked_rows=len(pool), bad_ids=mask_bad[:5])
check('pool_verbatim_target_and_terminator_decode', not decode_bad, checked_rows=len(pool), bad_ids=decode_bad[:5])
check('row_audit_independent_hashes', not audit_bad, checked_rows=len(pool), bad_ids=audit_bad[:5])
check('historical_token_arrays_unchanged', all(all(pool_map[r['id']][k] == r[k] for k in
      ('input_ids', 'labels', 'attention_mask', 'prompt_tokens')) for r in tasks['historical-control-fa']))

protected = constants(ROOT / 'data/unified-corpus/build.py', 'HOLDOUT')
check('protected_policy_agrees', protected == constants(ROOT / 'experiments/data-qualification-20260928/freeze_release.py', 'PROTECTED'),
      protected_work_ids=sorted(protected))
historical = tasks['historical-control-fa']
leaked = [r['id'] for r in historical if int(r['work_id'].split(':')[-1]) in protected]
check('historical_protected_work_exclusion', not leaked, bad_ids=leaked[:5])
ledger = rows(ROOT / 'experiments/train-audit-20260927/qualified-v1/final-ledger.jsonl')
check('historical_ledger_identity', sha((ROOT / 'experiments/train-audit-20260927/qualified-v1/final-ledger.jsonl').read_bytes())
      == constants(ROOT / 'data/unified-corpus/build.py', 'LEDGER_SHA'))
eligible = {r['id']: r for r in ledger if r['disposition'] in {'ELIGIBLE', 'ELIGIBLE_WITH_QUALIFICATIONS'}}
check('historical_exact_eligible_ledger_join', set(eligible) == set(ids(historical)) and all(
      r['text'] == eligible[r['id']]['source_text'] and r['target'] == eligible[r['id']]['target_text']
      and eligible[r['id']]['split_status'] == 'PASS_IDENTITY_AND_PINNED_HOLDOUT' for r in historical),
      ledger_rows=len(ledger), excluded_historical_rows=len(ledger) - len(eligible))
excluded_ids = {r['id'] for r in excluded}
check('excluded_ids_absent_from_learning', not (excluded_ids & set(released)),
      exact_overlap_ids=sorted(excluded_ids & set(released))[:5])
fa_qualified = rows(ROOT / 'resources/local/data-qualification-20260928/persian-v1/qualified.jsonl')
fa_held = {r['resource_id'] for r in rows(ROOT / 'resources/local/data-qualification-20260928/persian-v1/held.jsonl')}
check('persian_parent_resource_holds_excluded', not ({r['source_resource_id'] for r in fa_qualified} & fa_held)
      and set(ids(fa_qualified)) == set(ids(tasks['lexical-fa'])), held_parent_count=len(fa_held))
glossary = [r.get('id', r.get('record_id')) for name in ('s22-glossary-a.jsonl', 's22-glossary-b.jsonl')
            for r in rows(ROOT / 'experiments/data-qualification-20260928' / name)]
check('all_888_s22_glossary_groups_remain_excluded', len(glossary) == len(set(glossary)) == 888
      and set(glossary) <= excluded_ids and not (set(glossary) & set(released)),
      glossary_groups=len(glossary), released_overlap_count=len(set(glossary) & set(released)))

# Repeat only the existing source-side copy policy; never read benchmark reference answers.
source_path = ROOT / 'sources/local/parsig-2026-09-20/exports/text-units.jsonl'
check('source_archive_identity', sha(source_path.read_bytes()) == release['input_sha256'][source_path.relative_to(ROOT).as_posix()])
protected_sources = []
for r in rows(source_path):
    if int(r['book_id']) in protected:
        for transcription in r['transcription']:
            text = transcription if isinstance(transcription, str) else transcription.get('text', '')
            if text:
                protected_sources.append(norm(text))
screened, short, copy_hits = 0, 0, []
for task in ('pedagogy-fa', 'documentary-en', 'inscription-fa', 'edition-spans-en'):
    for r in tasks[task]:
        source = norm(r['learning']['source'])
        if len(source.split()) < 5:
            short += 1; continue
        screened += 1
        if any(source in text for text in protected_sources):
            copy_hits.append(r['id'])
check('existing_source_only_containment_screen', not copy_hits, screened_rows=screened,
      short_rows_outside_policy=short, protected_source_strings=len(protected_sources), bad_ids=copy_hits[:5])

surface_groups = defaultdict(list)
for r in projections:
    if r['task'] != 'historical-control-fa':
        surface_groups[(r['task'], js([r['learning']['source'], r['learning']['target']]))].append(r['id'])
repeated_surface = [g for g in surface_groups.values() if len(g) > 1]
frozen_groups = rows(READY / 'duplicate-groups.jsonl')
check('surface_repetition_register_preserved', {tuple(sorted(g)) for g in repeated_surface}
      == {tuple(sorted(r['row_ids'])) for r in frozen_groups}, surface_groups=len(repeated_surface))
lexical_forms = defaultdict(set)
for r in projections:
    if r['task'].startswith('lexical-'):
        for form in r['learning']['source']:
            lexical_forms[js(form)].add(r['id'])
ambiguous_form_groups = [v for v in lexical_forms.values() if len(v) > 1]
historical_work_counts = Counter(r['work_id'] for r in historical)
selected_work_counts = Counter(released[r['id']][1]['work_id'] for r in train if r['task'] == 'historical-control-fa')
case_id = 'S22GRAM-095'
case_pool = pool_map[case_id]
case_decoded = tokenizer.decode(case_pool['input_ids'][case_pool['prompt_tokens']:], skip_special_tokens=False)
case_target = projected[case_id]['learning']['target']
case_exposure = dict(id=case_id, released_count=sum(case_id in ids(v) for v in tasks.values()),
                     projection_count=ids(projections).count(case_id), pool_count=ids(pool).count(case_id),
                     train_count=ids(train).count(case_id), saved_consumed_count=consumed['ordered_ids'].count(case_id),
                     train_index_1_based=ids(train).index(case_id) + 1 if case_id in train_map else None,
                     decoded_target_matches_release=case_decoded == case_target + '<turn|>\n',
                     target_sha256=sha(case_target.encode()),
                     semantic_status='Initial omission claim withdrawn after independent source-page views: the extra gloss belongs to the following ka entry. Existing ku inventory and reported-speech context are retained correctly; no correction warranted. See SEMANTIC-SPOTCHECK.md; byte parity is not semantic certification.')
check('original_17_files_unchanged_after_read', all(sha((ROOT / f['path']).read_bytes()) == f['sha256'] for f in files))
result = dict(status='PASS' if all(c['status'] == 'PASS' for c in checks) else 'FAIL',
              checked_utc=datetime.now(timezone.utc).isoformat(), script_sha256=sha(Path(__file__).read_bytes()),
              scope='Structural integrity and existing exclusion policy; not complete semantic certification',
              canonical_files=files, checks=checks,
              targeted_exposure=case_exposure,
              counts=dict(released_by_task={k: len(v) for k, v in tasks.items()},
                          pool_by_task=dict(Counter(r['task'] for r in pool)), train_by_task=dict(Counter(r['task'] for r in train)),
                          exclusions_by_component=dict(Counter(r.get('component', 'unspecified') for r in excluded)),
                          surface_repetition_groups=len(repeated_surface), shared_lexical_form_groups=len(ambiguous_form_groups),
                          historical_work_count=len(historical_work_counts), historical_largest_work=historical_work_counts.most_common(1),
                          selected_historical_largest_work=selected_work_counts.most_common(1),
                          pool_supervised_tokens=sum(len(r['input_ids']) - r['prompt_tokens'] for r in pool),
                          train_supervised_tokens=sum(len(r['input_ids']) - r['prompt_tokens'] for r in train),
                          train_sequence_tokens=sum(len(r['input_ids']) for r in train),
                          maximum_pool_sequence=max(len(r['input_ids']) for r in pool)),
              limits=['No new linguistic adjudication or source acquisition.',
                      'No benchmark reference answers parsed; source-only archived transcriptions used for copy screen.',
                      'Exact held-ID and >=5-word normalized containment checks do not prove absence of paraphrases, alternate witnesses or shared formulas.',
                      'Short forms and shared lexical forms are expected overlap; homonyms and source-scoped alternatives are not collapsed.',
                      'Cloud weights, cloud state, training/inference and source-redistribution rights were not revalidated.'])
(HERE / 'integrity.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(status=result['status'], files=len(files), checks=len(checks),
                     failures=[c['check'] for c in checks if c['status'] != 'PASS'], counts=result['counts']), ensure_ascii=False))
raise SystemExit(0 if result['status'] == 'PASS' else 1)
