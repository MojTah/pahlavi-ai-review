"""Local plain-target/prompt alignment and source-review overlay. No model/job.

Classic + Critic. Reuse frozen nonlexical instructions and tokenizer contracts;
produce the full candidate inventory, not a sampled/authorized training stream.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unicodedata

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'resources/local/plain-target-preparation-20261001/data'
RESOURCE=ROOT/'experiments/usable-resource-20261001/resource-manifest.json'
RESOURCE_PIN='0c9779c4c1829944d422d053b983d1ef67dc41ac4f583e5dae6495b55d8028bd'
READER=ROOT/'resources/local/usable-resource-v3-20261001/learning-projections.jsonl'
PARENT=ROOT/'resources/local/training-ready-v2-20260929/data'
TOKENIZER=ROOT/'resources/local/cloud-pilot-qualified-20260927/tokenizer'
STATUS='TOKENIZED_CANDIDATES_ONLY_NOT_TRAINING_OR_CLOUD_ADMITTED'
sys.path.insert(0,str(ROOT))
from cloud_pilot import bundle


def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


old=module(ROOT/'experiments/mixed-supervision-20260929/prepare.py','plain_parent_helpers')
js,encoded,sha=old.js,old.encoded,old.sha
LEXICAL={'lexical-fa','lexical-en','lexical-mmp-en'}
LEXICAL_INSTRUCTION=(
    'Give the complete published meaning inventories for these Middle Persian forms in the stated source scope. '
    'Use plain text, not a JSON object or a quoted JSON string. '
    'Preserve every distinct entry, all senses and alternatives, published sense numbering, '
    'grammatical and usage qualifications, and uncertainty. Use separate entry/sense lines when needed. '
    'Keep compound components and related forms with their own meanings and explicit relationships; '
    'do not assign a compound meaning to an isolated form or reverse a headword relationship. '
    'Editorial notes are not additional senses. This is a source-scoped dictionary inventory, '
    'not a contextual sentence translation. '
)


def prompt_answer(row):
    task,learning=row['task'],row['learning']
    answer=learning['target']
    if not isinstance(answer,str) or not answer.strip():
        raise ValueError('Plain target required')
    if task=='historical-control-fa':
        return bundle.PROMPT.format(text=learning['source'].strip()),answer.strip()
    if task in LEXICAL:
        language='Persian' if task=='lexical-fa' else 'English'
        instruction=LEXICAL_INSTRUCTION+'Keep the published meanings in '+language+'; do not translate them into another language.'
    else:
        instruction=old.PROMPTS[task]
    source=learning['source'] if isinstance(learning['source'],str) else js(learning['source'])
    return instruction+'\nContext:\n'+js(learning['context'])+'\nSource:\n'+source,answer


def apply_decision(row,decision):
    if sha(row['learning']['target'].encode('utf8'))!=decision['reader_before_sha256']:
        raise ValueError('Reviewed target changed: '+row['id'])
    if sha(js(row['learning']['source']).encode('utf8'))!=decision['source_sha256']:
        raise ValueError('Reviewed source changed')
    disposition=decision['disposition']
    if disposition=='HOLD_STANDALONE_CROSS_RECORD_EDITORIAL_SCOPE':
        return None
    result=deepcopy(row)
    if disposition=='RETAIN_UNCHANGED_ANNOTATED_FRAGMENT_TASK_ONLY':
        c=result['learning']['context']
        if result['task']!='documentary-en' or c.get('evidence_class')!='QUALIFIED_FRAGMENT' or 'retain uncertainty and editorial additions' not in c.get('task_condition',''):
            raise ValueError('Annotated fragment lost its task context')
    elif disposition in {'APPLY_EXACT_TYPOGRAPHY_REPAIR','APPLY_EXACT_SOURCE_PRINT_SPACING_REPAIR'}:
        before=after=result['learning']['target']
        for operation in decision['operations']:
            if after.count(operation['old'])!=operation['count']:
                raise ValueError('Reviewed operation occurrence changed')
            after=after.replace(operation['old'],operation['new'])
        # All repairs are boundary/punctuation only; meaning characters stay.
        meaning=lambda s:''.join(c for c in s if c.isalnum() or unicodedata.category(c).startswith('M'))
        if meaning(before)!=meaning(after) or sha(after.encode('utf8'))!=decision['reader_after_sha256']:
            raise ValueError('Repair changed meaning characters/hash')
        result['learning']['target']=after
    else:
        raise ValueError('Unknown review disposition')
    if sha(result['learning']['target'].encode('utf8'))!=decision['reader_after_sha256']:
        raise ValueError('Review result changed')
    result['target_review']=dict(disposition=disposition,reader_before_sha256=decision['reader_before_sha256'],
                                 reader_after_sha256=decision['reader_after_sha256'],expert_certified=False)
    return result


def tokenize(row,tokenizer,template,config,specials):
    prompt,answer=prompt_answer(row)
    for value in old.strings(row['learning']):
        if value.strip():
            bundle.reject_controls(value,specials)
    prefix=template.render(messages=[{'role':'user','content':prompt}],add_generation_prompt=True,
                           enable_thinking=False,bos_token=config['bos_token'],tools=None)
    prefix_ids=tokenizer.encode(prefix,add_special_tokens=False).ids
    ids=tokenizer.encode(prefix+answer+bundle.TERMINATOR,add_special_tokens=False).ids
    if ids[:len(prefix_ids)]!=prefix_ids or tokenizer.decode(ids[len(prefix_ids):],skip_special_tokens=False)!=answer+bundle.TERMINATOR:
        raise ValueError('Prompt/answer boundary or target round trip failed')
    if not 0<len(prefix_ids)<len(ids)<=2048:
        raise ValueError('Untruncated sequence exceeds 2048-token contract')
    if tokenizer.token_to_id('<unk>') in ids:
        raise ValueError('Unknown token')
    return dict(id=row['id'],task=row['task'],input_ids=ids,attention_mask=[1]*len(ids),
                labels=[-100]*len(prefix_ids)+ids[len(prefix_ids):],prompt_tokens=len(prefix_ids))


def build():
    from tokenizers import Tokenizer
    from jinja2.sandbox import ImmutableSandboxedEnvironment
    inputs={}

    def read(path,pin=None):
        raw=path.read_bytes()
        if pin and sha(raw)!=pin:
            raise ValueError('Pinned input changed: '+str(path))
        inputs[path.relative_to(ROOT).as_posix()]=sha(raw)
        return raw

    resource=json.loads(read(RESOURCE,RESOURCE_PIN))
    for name,pin in resource['source_inputs_sha256'].items():
        read(ROOT/name,pin)
    read(ROOT/'experiments/usable-resource-20261001/prepare.py',resource['builder_sha256'])
    reviewed=json.loads(read(HERE/'target-decisions.json'))
    for name,pin in reviewed['source_inputs_sha256'].items():
        read(ROOT/name,pin)
    source=bundle.jsonl(read(READER,resource['output_files']['learning-projections.jsonl']['sha256']))
    parent_manifest=json.loads(read(ROOT/'experiments/training-ready-v2-20260929/data-manifest.json'))
    for name,pin in parent_manifest['source_code_sha256'].items():
        read(ROOT/name,pin)
    archives={r['id']:r for r in bundle.jsonl(read(PARENT/'learning-projections.jsonl',parent_manifest['outputs']['learning-projections.jsonl']['sha256']))}
    prior_tokens={r['id']:r for r in bundle.jsonl(read(PARENT/'pool.jsonl',parent_manifest['outputs']['pool.jsonl']['sha256']))}
    old_holds=bundle.jsonl(read(PARENT/'holds.jsonl',parent_manifest['outputs']['holds.jsonl']['sha256']))
    decisions={d['id']:d for d in reviewed['decisions']}
    if len(source)!=9973 or len({r['id'] for r in source})!=9973 or len(decisions)!=11:
        raise ValueError('Incomplete source/review inventory')
    if not set(decisions)<=set(archives):
        raise ValueError('Unknown review record')
    config=json.loads((TOKENIZER/'tokenizer_config.json').read_text('utf8'))
    tok_json=json.loads((TOKENIZER/'tokenizer.json').read_text('utf8'))
    specials=[t['content'] for t in tok_json['added_tokens'] if t['special']]
    tokenizer=Tokenizer.from_file(str(TOKENIZER/'tokenizer.json'))
    env=ImmutableSandboxedEnvironment(trim_blocks=True,lstrip_blocks=True,extensions=['jinja2.ext.loopcontrols'])
    def reject(message):
        raise ValueError(message)
    env.globals['raise_exception']=reject
    template=env.from_string((TOKENIZER/'chat_template.jinja').read_text('utf8'))
    terminal_ids=tokenizer.encode(bundle.TERMINATOR,add_special_tokens=False).ids
    projections,tokens,holds,audit=[],[],[],[]
    seen={};counts=defaultdict(Counter)
    for before in source:
        row=deepcopy(before)
        decision=decisions.get(row['id'])
        if decision:
            if sha(js(archives[row['id']]['learning']['target']).encode('utf8'))!=decision['archival_target_sha256']:
                raise ValueError('Archival target changed')
            row=apply_decision(row,decision)
            if row is None:
                holds.append(dict(id=before['id'],task=before['task'],reason=decision['reason'],disposition=decision['disposition']))
                continue
        row['projection_status']=STATUS
        if row['learning']['source']!=before['learning']['source'] or row['learning']['context']!=before['learning']['context'] or row['parent_ids']!=before['parent_ids']:
            raise ValueError('Unexpected source/scope/parent change')
        value=tokenize(row,tokenizer,template,config,specials)
        prompt,answer=prompt_answer(row)
        if prompt in seen:
            raise ValueError('Duplicate complete prompt: '+row['id']+' / '+seen[prompt])
        seen[prompt]=row['id']
        if row['task'] not in LEXICAL and row['id'] not in decisions and value!=prior_tokens[row['id']]:
            raise ValueError('Unchanged nonlexical tokenization drifted')
        projections.append(row);tokens.append(value)
        n=value['prompt_tokens'];m=len(value['input_ids'])
        audit.append(dict(id=row['id'],task=row['task'],prompt_sha256=sha(prompt.encode('utf8')),target_sha256=sha(answer.encode('utf8')),
                          sequence_tokens=m,prompt_tokens=n,content_label_tokens=m-n-len(terminal_ids),
                          terminal_label_tokens=len(terminal_ids),target_changed=row['learning']['target']!=before['learning']['target'],
                          instruction_changed=row['task'] in LEXICAL))
        counts[row['task']].update(dict(rows=1,sequence_tokens=m,prompt_tokens=n,content_label_tokens=m-n-len(terminal_ids),terminal_label_tokens=len(terminal_ids)))
    if len(projections)!=9971 or len(holds)!=2 or len({r['id'] for r in tokens})!=9971:
        raise ValueError('Unexpected overlay accounting')
    if {h['id'] for h in old_holds} & {p for r in projections for p in r['parent_ids']}:
        raise ValueError('Original hold reintroduced')
    for name,pin in inputs.items():
        if sha((ROOT/name).read_bytes())!=pin:
            raise ValueError('Input changed during build')
    outputs={name:b''.join(encoded(r) for r in values) for name,values in
             [('learning-projections.jsonl',projections),('all-candidates.jsonl',tokens),('holds.jsonl',holds),('row-audit.jsonl',audit)]}
    manifest=dict(status=STATUS,mode='Classic + Critic',script_sha256=sha(Path(__file__).read_bytes()),
                  input_sha256=inputs,source_groups=9973,candidate_groups=9971,original_release_holds_excluded=7,new_standalone_holds=2,
                  exact_target_repairs=sum(r['target_changed'] for r in audit),retained_named_annotated_fragments=3,
                  counts={k:dict(v) for k,v in sorted(counts.items())},max_sequence_tokens=max(r['sequence_tokens'] for r in audit),
                  template_sha256=bundle.file_hash(TOKENIZER/'chat_template.jinja'),lexical_instruction=LEXICAL_INSTRUCTION,
                  round_trip_checked_rows=len(tokens),unknown_tokens=0,truncated_rows=0,duplicate_complete_prompts=0,
                  outputs={name:dict(bytes=len(raw),rows=len(raw.splitlines()),sha256=sha(raw)) for name,raw in outputs.items()},
                  chosen_training_stream=False,selected_exposure_schedule=None,model_used=False,cloud_used=False,expert_certified=False,
                  limitation='Local token/identity/presentation validation; no semantic recertification, independent multi-work panel, new optimization or launch admission. Annotation signs remain under appropriate tasks.')
    outputs['manifest.json']=encoded(manifest)
    return outputs,manifest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    outputs,m=build()
    if args.check:
        for name,raw in outputs.items():
            if (OUT/name).read_bytes()!=raw:
                raise ValueError('Saved candidate package drifted: '+name)
    else:
        OUT.mkdir(parents=True,exist_ok=False)
        for name,raw in outputs.items():
            with (OUT/name).open('xb') as f:
                f.write(raw)
    print(js({k:m[k] for k in ['status','candidate_groups','exact_target_repairs','new_standalone_holds','max_sequence_tokens','unknown_tokens','truncated_rows']}))


if __name__=='__main__':
    main()
