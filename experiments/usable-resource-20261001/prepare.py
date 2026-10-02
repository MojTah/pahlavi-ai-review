"""Offline readable resource derived from the frozen qualified pool; no training.

Classic + Critic: one local builder, independently reviewed after deterministic
replay. Keep source payloads, senses, scopes and uncertainty; never strip content
inside arbitrary parentheses. JSONL lookup needs no database at this scale.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from functools import cache
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'resources/local/usable-resource-v3-20261001'
PARENT = ROOT / 'resources/local/training-ready-v2-20260929/data'
MANIFEST = ROOT / 'experiments/training-ready-v2-20260929/data-manifest.json'
MANIFEST_PIN = '157531204582c50f2d8f73aaa76ce8aca0c83e2c6e624d60bbc8c8daa1515b54'
TOKENIZER = ROOT / 'resources/local/cloud-pilot-qualified-20260927/tokenizer'
LEXICAL = {'lexical-fa', 'lexical-en', 'lexical-mmp-en'}
STATUS = 'READABLE_RESOURCE_ONLY_NOT_TRAINING_OR_CLOUD_ADMITTED'
KINDS = {'tr': '', 'def': 'Definition: ', 'usg': 'Usage: ', 'gram': 'Grammar: ',
         'gramGrp': 'Grammar: ', 'mood': 'Transitivity: ', 'number': 'Number: ',
         'itype': 'Inflection: '}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def encoded(value):
    return (canonical(value) + '\n').encode('utf8')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def rows(raw):
    return [json.loads(x) for x in raw.decode('utf8').splitlines() if x.strip()]


def fields(value, allowed):
    if not isinstance(value, dict) or set(value) - set(allowed):
        raise ValueError('Unsupported lexical schema: ' + repr(value))


def leaves(value, path=''):
    if isinstance(value, dict):
        for k, v in value.items():
            yield from leaves(v, path + '/' + k)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from leaves(v, path + '/' + str(i))
    elif isinstance(value, str) and value:
        yield path, value
    elif value is not None:
        raise ValueError('Unsupported non-string lexical leaf')


@cache
def punctuation_decisions():
    values=json.loads((HERE/'punctuation-decisions.json').read_text('utf8'))['cpd_outer_parentheses']
    return {(v['id'],v['path']):v for v in values}


def render(target, task, record_id=None):
    """Render the known schema and account for every nonempty string leaf.

    Only whole-gloss MMP quotation delimiters are removed here. CPD parentheses
    require an exact, reviewed leaf whitelist in punctuation-decisions.json.
    All other punctuation remains verbatim. Offsets are Unicode code points.
    """
    parts, mappings, structural = [], [], []
    length = 0
    whitelist = punctuation_decisions()

    def add(text):
        nonlocal length
        parts.append(text)
        length += len(text)

    def emit(text, path, role):
        if not text:
            return
        before, after, op = 0, len(text), 'verbatim'
        if task == 'lexical-mmp-en' and re.fullmatch(r"`[^`']+'\.?", text):
            after = len(text) - (2 if text.endswith("'.") else 1)
            before, op = 1, 'whole_gloss_quote_delimiters_removed'
        elif task == 'lexical-en' and (record_id,path) in whitelist:
            decision=whitelist[(record_id,path)]
            if text!=decision['text'] or role!=decision['kind']:
                raise ValueError('Reviewed punctuation leaf changed')
            before, after, op = 1, text.rfind(')'), 'reviewed_whole_parenthesis_delimiters_removed'
        content = text[before:after]
        redundant_period = (op=='reviewed_whole_parenthesis_delimiters_removed'
                            and text.endswith('.') and content.endswith('.'))
        if redundant_period:
            op='reviewed_whole_parenthesis_and_redundant_terminal_period_removed'
        start = length
        add(content)
        mappings.append(dict(path=path, role=role, original_sha256=sha(text.encode('utf8')),
                             source_span=[before, after], output_span=[start, length], operation=op))
        if op != 'verbatim' and text.endswith('.') and not redundant_period:
            add('.')
            mappings.append(dict(path=path, role=role, original_sha256=sha(text.encode('utf8')),
                                 source_span=[len(text)-1, len(text)], output_span=[length-1, length],
                                 operation='terminal_period_preserved'))

    def metadata(path, value, disposition):
        if value:
            structural.append(dict(path=path, value=value, disposition=disposition))

    def component(v, p, typed_meaning=False):
        fields(v, {'kind', 'attributes', 'text', 'tail', 'components'})
        kind = v['kind']
        if kind not in KINDS:
            raise ValueError('Unknown component kind')
        metadata(p+'/kind', kind, 'group_of_qualified_components' if kind=='gramGrp' else
                 ('reader_role_label' if KINDS[kind] or typed_meaning else 'published_meaning'))
        fields(v.get('attributes', {}), {'type'})
        if v.get('attributes', {}).get('type'):
            add(v['attributes']['type'] + ': ')
            # Attributes are content qualifiers, not discarded JSON decoration.
            start = length-len(v['attributes']['type'])-2
            t = v['attributes']['type']
            mappings.append(dict(path=p+'/attributes/type', role='attribute', original_sha256=sha(t.encode('utf8')),
                                 source_span=[0,len(t)], output_span=[start,start+len(t)], operation='verbatim'))
        if kind=='tr' and typed_meaning:
            add('Meaning: ')
        elif kind!='gramGrp' or v.get('text'):
            add(KINDS[kind])
        emit(v.get('text'), p+'/text', kind)
        for i, child in enumerate(v.get('components', [])):
            if v.get('text') or i:
                add('; ')
            component(child, p+'/components/'+str(i), typed_meaning=len(v.get('components',[]))>1)
        if v.get('tail'):
            add(' ')
            emit(v['tail'], p+'/tail', 'tail')

    def senses(v, p):
        if isinstance(v, str):
            emit(v, p, 'meaning')
            return
        if not isinstance(v, list) or not v:
            raise ValueError('Missing published senses')
        for i, sense in enumerate(v):
            fields(sense, {'number_as_published', 'components', 'text'})
            if i:
                add('\n')
            if sense.get('number_as_published'):
                emit(sense['number_as_published'], p+'/'+str(i)+'/number_as_published', 'sense_number')
                add('. ')
            if sense.get('text'):
                emit(sense['text'], p+'/'+str(i)+'/text', 'meaning')
            for j, value in enumerate(sense.get('components', [])):
                if sense.get('text') or j:
                    add('; ')
                component(value, p+'/'+str(i)+'/components/'+str(j), typed_meaning=len(sense.get('components',[]))>1)

    def forms(v, p):
        if not isinstance(v, list) or not v:
            raise ValueError('Missing associated form')
        for i, form in enumerate(v):
            if i:
                add(' / ')
            emit(form, p+'/'+str(i), 'associated_form')

    fields(target, {'entries'})
    if not target['entries']:
        raise ValueError('Empty inventory')
    for i, entry in enumerate(target['entries']):
        fields(entry, {'senses', 'sense_type', 'components', 'related_forms'})
        p = '/entries/'+str(i)
        if i:
            add('\n\n')
        if len(target['entries']) > 1:
            add('Entry '+str(i+1)+':\n')
        if 'sense_type' in entry:
            if entry['sense_type'] != 'compound_components_as_published':
                raise ValueError('Unknown sense relationship')
            metadata(p+'/sense_type', entry['sense_type'], 'compound_components_with_separate_form_meanings')
            add('Compound components:\n')
            for j, item in enumerate(entry['components']):
                fields(item, {'forms', 'senses'})
                if j:
                    add('\n')
                forms(item['forms'], p+'/components/'+str(j)+'/forms')
                add(' — ')
                senses(item['senses'], p+'/components/'+str(j)+'/senses')
        else:
            if 'components' in entry:
                raise ValueError('Unscoped compound components')
            senses(entry['senses'], p+'/senses')
        for j, item in enumerate(entry.get('related_forms', [])):
            fields(item, {'forms', 'senses', 'headword_relation_to_this_form_as_published', 'qualification_as_published'})
            q = p+'/related_forms/'+str(j)
            add('\nRelated form: ')
            forms(item['forms'], q+'/forms')
            if 'senses' in item:
                add(' — ')
                senses(item['senses'], q+'/senses')
            if item.get('headword_relation_to_this_form_as_published'):
                add('; headword relation to this form: ')
                emit(item['headword_relation_to_this_form_as_published'], q+'/headword_relation_to_this_form_as_published', 'headword_relation')
            if item.get('qualification_as_published'):
                add('; qualification: ')
                emit(item['qualification_as_published'], q+'/qualification_as_published', 'qualification')
    text = ''.join(parts)
    source_leaves = dict(leaves(target))
    accounted = {m['path'] for m in mappings} | {m['path'] for m in structural}
    if set(source_leaves) != accounted:
        raise ValueError('Unaccounted lexical fields: ' + repr(set(source_leaves)^accounted))
    for m in mappings:
        a,b = m['source_span']; c,d = m['output_span']
        if text[c:d] != source_leaves[m['path']][a:b]:
            raise ValueError('Changed meaning text')
    if not text.strip():
        raise ValueError('Empty reader meaning')
    return text, mappings, structural


def markers(text):
    result = []
    for left,right,label in [('(',')','parentheses'),('[',']','square_brackets'),('{','}','braces'),('⟦','⟧','edition_tags')]:
        if left in text or right in text:
            result.append(label)
    if '?' in text or '؟' in text:
        result.append('question_mark')
    if '`' in text:
        result.append('backtick')
    return result


def build():
    inputs = {}

    def read(path, expected=None):
        raw = path.read_bytes()
        if expected and sha(raw) != expected:
            raise ValueError('Pinned input changed: '+str(path))
        inputs[path.relative_to(ROOT).as_posix()] = sha(raw)
        return raw

    manifest = json.loads(read(MANIFEST, MANIFEST_PIN))
    source = rows(read(PARENT/'learning-projections.jsonl', manifest['outputs']['learning-projections.jsonl']['sha256']))
    old_pool = rows(read(PARENT/'pool.jsonl', manifest['outputs']['pool.jsonl']['sha256']))
    old_selected = rows(read(PARENT/'train.jsonl', manifest['outputs']['train.jsonl']['sha256']))
    held = rows(read(PARENT/'holds.jsonl', manifest['outputs']['holds.jsonl']['sha256']))
    read(HERE/'punctuation-decisions.json')
    if len(source) != 9973 or len({r['id'] for r in source}) != len(source):
        raise ValueError('Unexpected qualified inventory')
    if {r['id'] for r in held} & {p for r in source for p in r['parent_ids']}:
        raise ValueError('Held parent reintroduced')
    # Recheck archived dictionary response/XML identity; qualification is inherited,
    # not a new assertion of semantic correctness or public redistribution rights.
    archives = {}
    for r in source:
        if r['task'] not in LEXICAL:
            continue
        for e in r['lexical_provenance']['entries']:
            for s in e['sources']:
                if s['raw_file'] not in archives:
                    raw = read(ROOT/s['raw_file'], s['raw_sha256'])
                    archives[s['raw_file']] = {str(e['id']):e for e in json.loads(raw)['data']['entries']}
                elif inputs[s['raw_file']] != s['raw_sha256']:
                    raise ValueError('Conflicting archive pin')
                if sha(archives[s['raw_file']][s['entry_id']]['xml'].encode('utf8')) != s['xml_sha256']:
                    raise ValueError('Changed source XML')
    for name,pin in manifest['tokenizer_sha256'].items():
        read(TOKENIZER/name, pin)
    from tokenizers import Tokenizer
    tokenizer = Tokenizer.from_file(str(TOKENIZER/'tokenizer.json'))
    terminator = tokenizer.encode('<turn|>\n', add_special_tokens=False).ids
    old_by_id = {r['id']:r for r in old_pool}
    selected_ids = {r['id'] for r in old_selected}
    if len(old_pool) != len(old_by_id) or set(old_by_id) != {r['id'] for r in source} or len(selected_ids) != 1536:
        raise ValueError('Old exposure identity changed')
    dictionary, proposed, audits = [], [], []
    census = {'by_task':defaultdict(Counter), 'by_language':defaultdict(Counter), 'by_scope':defaultdict(Counter)}
    operations, marker_counts = Counter(), defaultdict(Counter)
    for r in source:
        t = r['task']; original = r['learning']['target']
        if t in LEXICAL:
            text, mapping, structural = render(original, t, r['id'])
            dictionary.append(dict(id=r['id'], task=t, forms=r['learning']['source'],
                                   context=r['learning']['context'], meaning_text=text,
                                   archival_target=original, parent_ids=r['parent_ids'],
                                   provenance=r['lexical_provenance'], expert_certified=False))
        else:
            if not isinstance(original,str):
                raise ValueError('Unexpected nonlexical target')
            text, mapping, structural = original, [], []
        p = deepcopy(r)
        p['learning']['target'] = text
        p['projection_status'] = STATUS
        proposed.append(p)
        flags = markers(text)
        # Flags are a review queue, not proof a translation is wrong. Do not let
        # parentheses-based cleaning invent certainty or choose a sense.
        audits.append(dict(id=r['id'], task=t, archival_target_sha256=sha(canonical(original).encode('utf8')),
                           reader_target_sha256=sha(text.encode('utf8')), changed=original != text,
                           mappings=mapping, structural=structural, remaining_marker_review=flags,
                           nonlexical_policy='unchanged_pending_source_bound_apparatus_review' if t not in LEXICAL else None))
        operations.update(m['operation'] for m in mapping if m['operation'] != 'verbatim')
        marker_counts[t].update(flags)
        before = old_by_id[r['id']]
        n = before['prompt_tokens']
        if before['labels'][:n] != [-100]*n or before['labels'][n:] != before['input_ids'][n:] or before['labels'][-len(terminator):] != terminator:
            raise ValueError('Old token accounting failed')
        expected = canonical(original) if t in LEXICAL else (original.strip() if t=='historical-control-fa' else original)
        if tokenizer.decode(before['input_ids'][n:], skip_special_tokens=False) != expected+'<turn|>\n':
            raise ValueError('Old labels do not match the pinned learning projection')
        context=r['learning']['context']
        lang=context.get('target_language', 'fas' if t.endswith('fa') else 'eng')
        scope='parsig:'+r['id'].split(':')[1][:3] if r['id'].startswith('parsig:') else context.get('source_scope',context.get('edition',context.get('stratum',t)))
        counts=dict(available=1, previous_selected=int(r['id'] in selected_ids),
                    prior_full_sequence_tokens=len(before['input_ids']),
                    prior_content_label_tokens=len(before['input_ids'])-n-len(terminator),
                    prior_terminal_label_tokens=len(terminator),
                    reader_target_standalone_tokens=len(tokenizer.encode(text,add_special_tokens=False).ids))
        for dimension,key in [('by_task',t),('by_language',lang),('by_scope',scope)]:
            census[dimension][key].update(counts)
    if len(dictionary)!=7438 or len(proposed)!=9973:
        raise ValueError('Incomplete resource')
    output = {'dictionary.jsonl':b''.join(encoded(r) for r in dictionary),
              'learning-projections.jsonl':b''.join(encoded(r) for r in proposed),
              'target-audit.jsonl':b''.join(encoded(r) for r in audits)}
    for name,pin in inputs.items():
        if sha((ROOT/name).read_bytes())!=pin:
            raise ValueError('Input changed during build: '+name)
    result=dict(status=STATUS, expert_certified=False, source_inputs_sha256=inputs,
                builder_sha256=sha(Path(__file__).read_bytes()), qualified_inputs=len(source),
                dictionary_groups=len(dictionary), represented_parents=sum(len(r['parent_ids']) for r in source),
                previous_selected=1536, held_parents_preserved=len(held),
                all_lexical_nonempty_string_leaves_accounted=True,
                nonlexical_targets_unchanged=sum(r['task'] not in LEXICAL for r in source),
                output_files={name:dict(bytes=len(raw),rows=len(raw.splitlines()),sha256=sha(raw)) for name,raw in output.items()},
                delimiter_operations=dict(operations), remaining_marker_counts={k:dict(v) for k,v in marker_counts.items()},
                census={d:{k:dict(v) for k,v in sorted(data.items())} for d,data in census.items()},
                token_note='Prior counts are exact frozen full-pool labels including separate terminators. Reader counts are standalone targets, not retokenized chat examples; no new prompt, sampling, loss or training contract is admitted.',
                raw_source_files_rehashed=len(archives), cloud_or_weights_used=False)
    output['manifest.json']=encoded(result)
    return output,result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--lookup',help='Exact, case-sensitive published form; return ALL scopes/entries/languages')
    args=parser.parse_args()
    if args.lookup is not None:
        saved=json.loads((OUT/'manifest.json').read_text('utf8'))
        raw=(OUT/'dictionary.jsonl').read_bytes()
        if sha(raw)!=saved['output_files']['dictionary.jsonl']['sha256']:
            raise ValueError('Changed lookup resource')
        hits=[r for r in rows(raw) if args.lookup in r['forms']]
        for r in hits:
            print(canonical(r))
        print('Exact matches: '+str(len(hits)),file=sys.stderr)
        return
    outputs,summary=build()
    if args.check:
        for name,raw in outputs.items():
            if (OUT/name).read_bytes()!=raw:
                raise ValueError('Non-reproducible saved resource: '+name)
    else:
        # Never overwrite even a partial previous build. A failed build remains
        # visible for inspection; use a new version, not a silent repair.
        OUT.mkdir(parents=True,exist_ok=False)
        for name,raw in outputs.items():
            with (OUT/name).open('xb') as f:
                f.write(raw)
    print(canonical({k:summary[k] for k in ['status','qualified_inputs','dictionary_groups','nonlexical_targets_unchanged','raw_source_files_rehashed','delimiter_operations']}))


if __name__=='__main__':
    main()
