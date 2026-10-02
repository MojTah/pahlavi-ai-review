"""Freeze twelve exploratory stage prompts; no model weights or cloud calls.

Classic + Critic: sole root writer. Reuse the qualified four-case packet and
publisher tokenizer. Supplied semantic constraints are deliberate interventions,
not independent discoveries or new training labels.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'resources/local/semantic-stage-diagnostic-20261001'
CASES = ('KANHERI06', 'BERK25', 'TB3', 'ZAND301')


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))+'\n').encode('utf8')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


# Scope deliberately excludes unsolved titles, readings, and other clause roles.
# Zand is a conditional published-translator reading, not a certified gold label.
MEANINGS = {
    'KANHERI06': 'Directed relation: son_of. Child: Ābāngušnasp, a person. Parent: Farroxān, a person. Express this direction only; do not invent other events or name etymologies.',
    'BERK25': 'Event: giving. Giver: an unidentified person. Recipient: Wahman-Ohrmazd, a person. What was given is outside the requested scope. Express this event and these roles only; do not invent a giver name or another event.',
    'TB3': 'Event: sealing. Agent: Māh, a person. Object: unspecified. Express this event and agent only; do not interpret the name as moon/month or expand any titles.',
    'ZAND301': 'Conditional reading to realize: two distinct coordinated list elements, places (plural) and villages/districts (plural), with demonstrative reference. This reading has no possessive owner and no event. Express both plural referents only; do not add another referent or action.'}

QUESTIONS = {
    'KANHERI06': 'Identify whether there is a directed kinship relation, its type, and which person occupies each role. Mark unsupported relations unresolved.',
    'BERK25': 'Identify the dād event, the giver and recipient. Mark an unknown giver unidentified; do not assign actors from a different clause. Do not analyze other events.',
    'TB3': 'Identify the muhr abar nihād event and its agent; distinguish personal-name use from common-noun interpretation. Mark unqualified titles or objects unresolved.',
    'ZAND301': 'Identify the number and function of ōyšān in relation to gyāg and rōstāg. Distinguish plural demonstrative reference from a possessive owner and distinguish coordination from a single noun phrase. If the supplied evidence cannot decide, report unresolved.'}


def build():
    old = json.loads((ROOT/'experiments/component-diagnostic-20261001/packet-manifest.json').read_bytes())
    previous = ROOT/'resources/local/component-diagnostic-20261001'
    inputs = {}
    note_path = 'sources/local/parsig-2026-09-20/responses/7b0f3a98957fdcc44f4b4a2ea27d9f7d3604bde30f69adc748b107dafc08a0bd.json'
    note_raw = (ROOT/note_path).read_bytes()
    if sha(note_raw) != '9fdc68e17e8daef45fe0e2a1293920a3e29e2e46f419959b438d0920d3fdf866':
        raise ValueError('Original occurrence Note changed')
    note = next(r for r in json.loads(note_raw) if str(r['Code'])=='301001016')['Note']
    if (sha(note[147:191].encode()) != '1dbc42c9c6aa6351824a283292f13d3b4d2efb895c1acdeffc3669182ce778cd'
            or note[105:145] != 'ōyšān صورت جمع است و موصوف‌های آن مفردند'):
        raise ValueError('Scoped plural observation changed')
    inputs[note_path] = sha(note_raw)
    for name, entry in old['local_outputs'].items():
        raw = (previous/name).read_bytes()
        if len(raw) != entry['bytes'] or sha(raw) != entry['sha256']:
            raise ValueError('Qualified prior packet changed: '+name)
        inputs[str((previous/name).relative_to(ROOT))] = sha(raw)
    cases = [json.loads(x) for x in (previous/'cases.jsonl').read_bytes().splitlines()]
    previous_prompts = {r['id']:r for r in
        (json.loads(x) for x in (previous/'model-inputs.jsonl').read_bytes().splitlines())}
    if tuple(c['id'] for c in cases) != CASES:
        raise ValueError('Qualified identities/order changed')
    from tokenizers import Tokenizer
    from jinja2.sandbox import ImmutableSandboxedEnvironment
    sys.path.insert(0,str(ROOT))
    from cloud_pilot.bundle import TOKENIZER_HASHES
    tokroot = ROOT/'resources/local/cloud-pilot-qualified-20260927/tokenizer'
    for name, pin in TOKENIZER_HASHES.items():
        raw = (tokroot/name).read_bytes()
        if sha(raw) != pin: raise ValueError('Publisher tokenizer changed')
        inputs[str((tokroot/name).relative_to(ROOT))] = pin
    tokenizer = Tokenizer.from_file(str(tokroot/'tokenizer.json'))
    template = ImmutableSandboxedEnvironment().from_string((tokroot/'chat_template.jinja').read_text('utf8'))
    config = json.loads((tokroot/'tokenizer_config.json').read_bytes())
    prompts, private = [], []
    for c in cases:
        key = c['id']
        if (c['training_admitted'] or c['expert_certified'] or c['unseen_claim_allowed']
                or c['context'][slice(*c['source_span'])] != c['source']):
            raise ValueError('Source qualification/admission changed')
        lexical = previous_prompts[key+'-B']['prompt'].split('\n\nLexical/category evidence:\n',1)[1]
        if key=='ZAND301':
            old_scope='General use beside a noun: demonstrative adjectives.'
            if old_scope not in lexical: raise ValueError('Prior grammatical reader changed')
            lexical=lexical.replace(old_scope,
                'The adjacent published grammar explains demonstrative adjectives beside nouns, '
                'but its paragraph refers to the preceding demonstrative table. This is not an '
                'occurrence annotation or a categorical demonstrative rule for ōyšān here.')
        source = ('Pahlavi context:\n'+c['context']+'\nSelected source span '
                  +str(c['source_span'])+' (half-open Unicode code points):\n'+c['source'])
        arms = {
            'I': ('Analyze only the selected source, using the supplied lexical/category evidence. '
                  'Return one compact JSON object with keys relation_or_event, participants, '
                  'number_and_scope, unresolved. Do not translate or invent missing information.\n'
                  +QUESTIONS[key]+'\n\n'+source+'\n\nLexical/category evidence:\n'+lexical),
            'R': ('Write a short natural Persian realization of only the following supplied semantic constraints. '
                  'Treat these constraints as authoritative for this task. Preserve every specified role, '
                  'direction and number; include no commentary, analysis, or unspecified content.\n'
                  'Supplied semantic constraints:\n'+MEANINGS[key])}
        # S differs from R only by the same source block, never generated I output.
        arms['S'] = arms['R']+'\n\nSource context (do not expand the requested semantic scope):\n'+source
        for condition, prompt in arms.items():
            rendered = template.render(messages=[{'role':'user','content':prompt}],add_generation_prompt=True,
                enable_thinking=False,bos_token=config['bos_token'],tools=None)
            ids = tokenizer.encode(rendered,add_special_tokens=False).ids
            if len(ids)+256 > 2048 or tokenizer.token_to_id('<unk>') in ids:
                raise ValueError('Actual publisher template capacity failure')
            prompts.append(dict(id=key+'-'+condition,case_id=key,condition=condition,prompt=prompt,
                prompt_tokens=len(ids),rendered_sha256=sha(rendered.encode()),has_unknown_token=False))
        private.append(dict(case_id=key,family=c['family'],work_id=c['work_id'],evidence=c['evidence'],
            source_sha256=sha(c['source'].encode()),previous_exposure=c['exposure'],
            supplied_constraints=MEANINGS[key],primary_constraint=c['primary_constraint'],
            interpretation_task='TASK_CUED_SOURCE_RELATION_PROBE',
            interpretation_secondary_constraint='Recipient is Wahman-Ohrmazd; score separately from the existing giving/unnamed-giver primary constraint.' if key=='BERK25' else None,
            unscored=c['unscored'],reference=c['reference'],expert_certified=False,training_admitted=False,
            interpretation_scoring='UNRESOLVED_OR_CONDITIONAL_ONLY' if key=='ZAND301' else 'SOURCE_QUALIFIED_SCOPED_RELATION',
            realization_scoring='PRESERVE_SUPPLIED_CONSTRAINTS_NOT_SOURCE_TRUTH',
            number_scoring='Semantic plurality; do not require a particular Persian suffix.',
            no_new_unseen_claim=True))
    outputs = {'model-inputs.jsonl':b''.join(encoded(p) for p in prompts),
               'review-constraints.jsonl':b''.join(encoded(c) for c in private)}
    manifest = dict(protocol='stages-v1',cases=list(CASES),planned_outputs=12,
        primary_source_interpretation_cases=list(CASES[:3]),conditional_case='ZAND301',
        previous_manifest_sha256=sha((ROOT/'experiments/component-diagnostic-20261001/packet-manifest.json').read_bytes()),
        inputs_sha256=inputs,local_outputs={n:dict(bytes=len(b),sha256=sha(b)) for n,b in outputs.items()},
        max_prompt_tokens=max(r['prompt_tokens'] for r in prompts),max_new_tokens=256,
        training=False,independent_confirmation=False,expert_certified=False,
        merit='Existing semantic preservation categories; task-specific denominators never pooled.',
        schedule=[c+'-'+a for c,o in zip(CASES,('IRS','RSI','SIR','SRI')) for a in o])
    return outputs,manifest


def main():
    outputs,manifest = build()
    if sys.argv[1:] == ['--write']:
        if OUT.exists():
            old=json.loads((HERE/'packet-manifest.json').read_bytes())
            if set(old['local_outputs']) != set(outputs): raise ValueError('Unknown preparation ownership')
            for name,entry in old['local_outputs'].items():
                if sha((OUT/name).read_bytes()) != entry['sha256']:
                    raise ValueError('Refuse to overwrite changed private preparation')
        OUT.mkdir(parents=True,exist_ok=True)
        for name,raw in outputs.items(): (OUT/name).write_bytes(raw)
        (HERE/'packet-manifest.json').write_bytes(encoded(manifest))
    elif sys.argv[1:] == ['--check']:
        if json.loads((HERE/'packet-manifest.json').read_bytes()) != manifest:
            raise ValueError('Prepared manifest changed')
        for name,raw in outputs.items():
            if (OUT/name).read_bytes() != raw: raise ValueError('Prepared output changed')
    else: raise ValueError('Use --write once or --check')
    print(json.dumps(dict(status='pass',outputs=12,maximum_prompt_tokens=manifest['max_prompt_tokens'],
                         cloud_performed=False,weights_downloaded=False)))


if __name__ == '__main__': main()
