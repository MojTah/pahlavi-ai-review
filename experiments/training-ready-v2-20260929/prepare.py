"""Build/check an immutable corrected pool and a matched, NOT SUBMITTED pilot."""
import argparse
from collections import Counter, defaultdict
import copy
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'resources/local/training-ready-v2-20260929/data'
OLD_DATA = ROOT / 'resources/local/mixed-supervision-20260929/data'
MANIFEST = HERE / 'data-manifest.json'
sys.path.insert(0, str(ROOT))
from cloud_pilot import bundle, mixed_run


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


old = module(ROOT / 'experiments/mixed-supervision-20260929/prepare.py', 'previous_prepare')
js, encoded, sha = old.js, old.encoded, old.sha
LEXICAL = {'lexical-fa', 'lexical-en', 'lexical-mmp-en'}
LEXICAL_PROMPT = (
    'Give the complete published meaning inventories for these Middle Persian forms in the stated source scope. '
    'Return JSON with an entries list, preserving each distinct source entry and all its senses and alternatives. '
    'Keep related_forms and compound components with their own meanings when supplied by the source; '
    'do not distribute a compound meaning across isolated forms. Preserve published sense structure, '
    'grammatical and semantic qualifiers, uncertainty and numbering. Dictionary editorial notes are not senses. '
    'This is a source-scoped dictionary inventory, not a contextual sentence translation. '
)
FORMAT_IDS = {
    'parsig:' + code + ':pal>fa' for code in
    ('133000037', '133000089', '133000265', '151006015', '151042005', '134007039',
     '559000003', '540000003', '531000003', '539000003', '557000001', '557000002',
     '557000003', '541000001', '151001160', '109000003', '109000011')
}
HISTORICAL_EQUIVALENTS = (
    ('parsig:151001010:pal>fa', 'parsig:151014005:pal>fa'),
    ('parsig:107000007:pal>fa', 'parsig:113000007:pal>fa'),
)


def read_rows(path):
    return bundle.jsonl(path.read_bytes())


def prompt_answer(projection):
    task, learning = projection['task'], projection['learning']
    if task == 'historical-control-fa':
        return bundle.PROMPT.format(text=learning['source'].strip()), learning['target'].strip()
    if task in LEXICAL:
        language = 'Persian' if task == 'lexical-fa' else 'English'
        instruction = LEXICAL_PROMPT + 'Keep the published meanings in ' + language + '; do not translate them into another language.'
        answer = js(learning['target'])
    else:
        instruction, answer = old.PROMPTS[task], learning['target']
    source = learning['source'] if isinstance(learning['source'], str) else js(learning['source'])
    return instruction + '\nContext:\n' + js(learning['context']) + '\nSource:\n' + source, answer


def tokenize(projection, tokenizer, template, config, specials):
    prompt, answer = prompt_answer(projection)
    for value in old.strings(projection['learning']):
        if value.strip():
            bundle.reject_controls(value, specials)
    prefix = template.render(messages=[{'role': 'user', 'content': prompt}], add_generation_prompt=True,
                             enable_thinking=False, bos_token=config['bos_token'], tools=None)
    prefix_ids = tokenizer.encode(prefix, add_special_tokens=False).ids
    ids = tokenizer.encode(prefix + answer + bundle.TERMINATOR, add_special_tokens=False).ids
    if ids[:len(prefix_ids)] != prefix_ids:
        raise ValueError('Prompt/answer token boundary changed')
    if tokenizer.decode(ids[len(prefix_ids):], skip_special_tokens=False) != answer + bundle.TERMINATOR:
        raise ValueError('Non-reversible target encoding')
    if not 0 < len(prefix_ids) < len(ids) <= 2048:
        raise ValueError('Sequence exceeds untruncated 2048-token contract')
    unknown = tokenizer.token_to_id('<unk>')
    if unknown is not None and unknown in ids:
        raise ValueError('Unknown model token')
    return dict(id=projection['id'], task=projection['task'], input_ids=ids, attention_mask=[1] * len(ids),
                labels=[-100] * len(prefix_ids) + ids[len(prefix_ids):], prompt_tokens=len(prefix_ids))


def select_pilot(pool, parent_map, previous):
    """Retain prior order/parents where possible; replace only unavailable/duplicate rows."""
    indexed = {r['id']: r for r in pool}
    family = lambda task: 'lexical' if task in LEXICAL else ('historical' if task == 'historical-control-fa' else 'other')
    reserved = {parent_map[r['id']] for r in previous if r['id'] in parent_map}
    reserved_inscriptions = {indexed[i]['pair_key'] for i in reserved if indexed[i]['task'] == 'inscription-fa'}
    available = [r for r in old.balanced(pool, len(pool)) if r['id'] not in reserved
                 and not (r['task'] == 'inscription-fa' and r['pair_key'] in reserved_inscriptions)]
    train, changes, used = [], [], set()
    for position, before in enumerate(previous, 1):
        mapped = parent_map.get(before['id'])
        if mapped in indexed and mapped not in used:
            row = indexed[mapped]
            reason = 'same_parent' if mapped == before['id'] else 'merged_source_inventory'
        else:
            options = [r for r in available if r['task'] == before['task'] and r['id'] not in used]
            if not options:
                options = [r for r in available if family(r['task']) == family(before['task']) and r['id'] not in used]
            if not options:
                raise ValueError('Insufficient unique reviewed replacement rows')
            row = options[0]
            reason = 'held_or_duplicate_parent_replaced'
        assert family(row['task']) == family(before['task'])
        used.add(row['id'])
        train.append(row)
        if row['id'] != before['id']:
            changes.append(dict(position=position, old_id=before['id'], new_id=row['id'],
                                old_task=before['task'], new_task=row['task'], reason=reason))
    assert len(train) == len(used) == 1536
    return train, changes


def build():
    from tokenizers import Tokenizer
    from jinja2.sandbox import ImmutableSandboxedEnvironment
    lexical = module(HERE / 'lexical.py', 'lexical_v2')
    previous_manifest_path = ROOT / 'experiments/mixed-supervision-20260929/data-manifest.json'
    previous_manifest = json.loads(previous_manifest_path.read_text('utf-8'))
    bundle.check_hash(Path(old.__file__), previous_manifest['script_sha256'])
    bundle.check_hash(Path(bundle.__file__), previous_manifest['bundle_helper_sha256'])
    inputs = {previous_manifest_path.relative_to(ROOT).as_posix(): bundle.file_hash(previous_manifest_path)}
    for name, entry in previous_manifest['outputs'].items():
        path = OLD_DATA / name
        bundle.check_hash(path, entry['sha256'])
        inputs[path.relative_to(ROOT).as_posix()] = entry['sha256']
    for name, digest in previous_manifest['input_sha256'].items():
        bundle.check_hash(ROOT / name, digest)
        inputs[name] = digest
    bundle.check_hash(old.RELEASE, previous_manifest['release_sha256'])
    inputs[old.RELEASE.relative_to(ROOT).as_posix()] = previous_manifest['release_sha256']
    release = json.loads(old.RELEASE.read_text('utf-8'))
    for name, entry in release['outputs'].items():
        bundle.check_hash(old.READY / name, entry['sha256'])
        inputs[(old.READY / name).relative_to(ROOT).as_posix()] = entry['sha256']
    assert (OLD_DATA / 'census.json').read_bytes() == previous_manifest_path.read_bytes()
    inputs[(OLD_DATA / 'census.json').relative_to(ROOT).as_posix()] = bundle.file_hash(OLD_DATA / 'census.json')
    for name, digest in bundle.TOKENIZER_HASHES.items():
        bundle.check_hash(old.TOKENIZER / name, digest)
    original = read_rows(OLD_DATA / 'learning-projections.jsonl')
    assert len(original) == len({r['id'] for r in original}) == 10152
    originals = {r['id']: r for r in original}
    projections, changes, holds = lexical.build_lexical(copy.deepcopy(original))
    decisions_path = HERE / 'nonlexical-decisions.json'
    decisions = json.loads(decisions_path.read_text('utf-8'))
    for name, digest in decisions['inputs'].items():
        bundle.check_hash(ROOT / name, digest)
        inputs[name] = digest
    for decision in decisions['decisions'] + decisions['typography']:
        original_learning = originals[decision['id']]['learning']
        assert sha(original_learning['source'].encode()) == decision['source_sha256']
        if 'target_sha256' in decision:
            assert sha(original_learning['target'].encode()) == decision['target_sha256']
        bundle.check_hash(ROOT / decision['raw_path'], decision['raw_sha256'])
        inputs[decision['raw_path']] = decision['raw_sha256']
    # Explicit decisions are reviewed against raw sources, never inferred from DEV answers.
    held = {r['id']: r for r in decisions['decisions'] if r['action'] == 'hold'}
    assert set(held) <= set(originals)
    for identifier, decision in held.items():
        holds.append(dict(id=identifier, task=originals[identifier]['task'], reason=decision['reason']))
    projections = [r for r in projections if r['id'] not in held]
    typography = {r['id']: r for r in decisions['typography']}
    assert set(typography) == FORMAT_IDS
    for row in projections:
        row.setdefault('parent_ids', [row['id']])
        if row['id'] in FORMAT_IDS:
            before = row['learning']['target']
            decision = typography[row['id']]
            assert sha(before.encode()) == decision['before_sha256']
            after = before
            for operation in decision['operations']:
                assert after.count(operation['old']) == operation['expected_occurrences']
                after = after.replace(operation['old'], operation['new'])
            assert sha(after.encode()) == decision['after_sha256']
            assert before != after
            row['learning']['target'] = after
            changes.append(dict(id=row['id'], field='target', reason='reviewed_typographic_controls_only',
                                before=before, after=after, before_sha256=sha(before.encode()), after_sha256=sha(after.encode())))
    assert FORMAT_IDS <= {r['id'] for r in projections}
    by_id = {r['id']: r for r in projections}
    for first, second in HISTORICAL_EQUIVALENTS:
        a, b = by_id[first], by_id[second]
        assert a['learning']['source'] == b['learning']['source'] and a['learning']['context'] == b['learning']['context'] == {}
        a['parent_ids'].extend(b['parent_ids'])
        a['alternative_targets'] = [{'id': second, 'target': b['learning']['target']}]
        changes.append(dict(id=first, parent_ids=[first, second], reason='reviewed_compatible_published_translation_variants',
                            retained_target_sha256=sha(a['learning']['target'].encode()), alternate_target_sha256=sha(b['learning']['target'].encode())))
        projections.remove(b)
    historical = {r['id']: r for r in read_rows(old.READY / 'historical-control-fa.jsonl')}
    old_pool = {r['id']: r for r in read_rows(OLD_DATA / 'pool.jsonl')}
    config = json.loads((old.TOKENIZER / 'tokenizer_config.json').read_text('utf-8'))
    tokenizer_json = json.loads((old.TOKENIZER / 'tokenizer.json').read_text('utf-8'))
    specials = [r['content'] for r in tokenizer_json['added_tokens'] if r['special']]
    tokenizer = Tokenizer.from_file(str(old.TOKENIZER / 'tokenizer.json'))
    env = ImmutableSandboxedEnvironment(trim_blocks=True, lstrip_blocks=True, extensions=['jinja2.ext.loopcontrols'])
    def reject(message):
        raise ValueError(message)
    env.globals['raise_exception'] = reject
    template = env.from_string((old.TOKENIZER / 'chat_template.jinja').read_text('utf-8'))
    pool, audit, parent_map, seen_prefix = [], [], {}, {}
    for row in projections:
        value = tokenize(row, tokenizer, template, config, specials)
        prefix = js(value['input_ids'][:value['prompt_tokens']])
        if prefix in seen_prefix:
            raise ValueError('Duplicate complete model-visible prompt: ' + row['id'] + ' / ' + seen_prefix[prefix])
        seen_prefix[prefix] = row['id']
        for parent in row['parent_ids']:
            assert parent not in parent_map and parent in originals
            assert row['task'] == originals[parent]['task']
            assert row['learning']['source'] == originals[parent]['learning']['source']
            assert row['learning']['context'] == originals[parent]['learning']['context']
            parent_map[parent] = row['id']
        context = row['learning']['context']
        group = historical[row['id']]['work_id'] if row['task'] == 'historical-control-fa' else next(
            (js(context[k]) for k in ('witness_group', 'source_scope', 'context_family', 'phenomenon', 'grammar_as_published', 'edition') if context.get(k)), row['task'])
        parity = None
        if row['task'] not in LEXICAL and row['id'] not in FORMAT_IDS:
            parity = all(value[k] == old_pool[row['id']][k] for k in bundle.TOKEN_KEYS)
            assert parity, row['id']
        prompt, answer = prompt_answer(row)
        audit.append(dict(id=row['id'], task=row['task'], parent_ids=row['parent_ids'], group=group,
                          learning_sha256=sha(encoded(row['learning'])), prefix_sha256=sha(prefix.encode()),
                          prompt_sha256=sha(prompt.encode()), answer_sha256=sha(answer.encode()),
                          sequence_tokens=len(value['input_ids']), prompt_tokens=value['prompt_tokens'],
                          exact_answer_decode=True, unchanged_nonlexical_array_parity=parity))
        pool.append(dict(value, group=group, pair_key=js([row['learning']['source'], row['learning']['target']])))
    hold_ids = {r['id'] for r in holds}
    assert len(hold_ids) == len(holds) and not hold_ids.intersection(parent_map)
    assert set(originals) == set(parent_map) | hold_ids
    train, substitutions = select_pilot(pool, parent_map, read_rows(OLD_DATA / 'train.jsonl'))
    inscriptions = [r['pair_key'] for r in train if r['task'] == 'inscription-fa']
    assert len(inscriptions) == len(set(inscriptions)) == 4
    clean = lambda row: {k: v for k, v in row.items() if k not in {'group', 'pair_key'}}
    train = [clean(r) for r in train]
    mixed_run.core.validate_rows(train)
    payloads = {name: b''.join(encoded(row) for row in rows) for name, rows in {
        'pool.jsonl': [clean(r) for r in pool], 'train.jsonl': train, 'learning-projections.jsonl': projections,
        'row-audit.jsonl': audit, 'changes.jsonl': changes, 'holds.jsonl': holds,
        'parent-map.jsonl': [dict(id=k, output_id=v) for k, v in parent_map.items()],
        'selection-changes.jsonl': substitutions}.items()}
    code_files = [Path(__file__), HERE / 'lexical.py', decisions_path, Path(bundle.__file__), Path(old.__file__)]
    manifest = dict(status='LOCAL_DATA_CHECKS_PASS_NOT_LAUNCH_AUTHORIZATION', version='corrected-v2',
        previous_manifest_sha256=bundle.file_hash(previous_manifest_path), input_sha256=inputs,
        source_code_sha256={p.relative_to(ROOT).as_posix(): bundle.file_hash(p) for p in code_files},
        tokenizer_sha256=bundle.TOKENIZER_HASHES, raw_counts=old.COUNTS,
        pool_counts=dict(Counter(r['task'] for r in pool)), original_records=10152,
        represented_parent_records=len(parent_map), held_records=len(holds), holds=holds,
        unique_complete_prompts=len(seen_prefix), unresolved_prompt_collisions=0,
        historical_typographic_repairs=len(FORMAT_IDS), truncated_rows=0, unknown_tokens=0,
        max_sequence_tokens=2048, pilot=dict(updates=96, microbatch=1, gradient_accumulation=16,
            per_update=dict(historical=12, lexical=2, other=2), selected_ids_in_order=[r['id'] for r in train],
            task_statistics=old.stats(train), substitutions=substitutions), pool_task_statistics=old.stats(pool),
        sampling='Previous ordered parent schedule where available; reviewed merged parent identity; deterministic same-task then same-family replacement without duplicates',
        model_visible='Only learning fields; lineage, editorial notes, alternatives and review evidence never serialized',
        scope='Full corrected pool available; prepared96 is a repair comparison, not full-pool training or an optimized recipe',
        benchmark_content_read=False, network_or_weights_used=False, cloud_submitted=False,
        outputs={name: dict(sha256=sha(data), bytes=len(data), rows=data.count(b'\n')) for name, data in payloads.items()})
    return payloads, encoded(manifest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if not args.check and (OUT.exists() or MANIFEST.exists()):
        raise SystemExit('Refusing overwrite of a frozen derived version')
    payloads, manifest = build()
    if args.check:
        assert {p.name for p in OUT.iterdir()} == set(payloads)
        for name, data in payloads.items():
            assert (OUT / name).read_bytes() == data, name
        assert MANIFEST.read_bytes() == manifest
    else:
        OUT.mkdir(parents=True, exist_ok=False)
        for name, data in payloads.items():
            with (OUT / name).open('xb') as stream:
                stream.write(data)
        with MANIFEST.open('xb') as stream:
            stream.write(manifest)
    m = json.loads(manifest)
    settings = dict(data_manifest_sha256=sha(manifest), train_sha256=m['outputs']['train.jsonl']['sha256'])
    mixed_run.read_data(OUT / 'train.jsonl', MANIFEST, settings)
    print(js(dict(status='PASS', replay=args.check, pool_counts=m['pool_counts'], holds=m['held_records'],
                  substitutions=len(m['pilot']['substitutions']), manifest_sha256=sha(manifest))))


if __name__ == '__main__':
    main()
