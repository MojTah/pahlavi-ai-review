"""Four fixed local component cases; no model, training or cloud calls.

Classic + Critic. Reuse complete dictionary projections and the actual Gemma
template. The source editions/references stay in ignored local resources.
"""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'resources/local/component-diagnostic-20261001'


def sha(value):
    return hashlib.sha256(value).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))+'\n').encode('utf8')


def rows(raw):
    return [json.loads(line) for line in raw.decode('utf8').splitlines() if line.strip()]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Reader overlays preserve all grammatical senses, not a preferred gloss.
I_READER = ('Form: ī; ideogram: Y. Etymology: ^, Aramaic zy. '
            'Attestations: Manichaean y(g), New Persian i.\n'
            '1. Grammar: relative pronoun; Meaning: who, which.\n'
            '2. Grammar: connective particle.')
PRONOUN_READER = ('Forms: ōyšān, awēšān; Persian gloss: ایشان. '
    'Category: third-person plural independent personal pronouns. '
    'General use beside a noun: demonstrative adjectives. '
    'Historical case cross-reference: early Pahlavi ōy direct, awē oblique; '
    'this does not assign case to the current occurrence. '
    'Older Manichaean Middle Persian awēn instead of awēšān is a separate '
    'register-specific variant, not an unrestricted additional form here.')


def validate(cases, prompts):
    if len(cases) != 4 or len({c['family'] for c in cases}) != 4 or len(prompts) != 12:
        raise ValueError('Fixed four-case/twelve-output panel changed')
    for c in cases:
        a, b = c['source_span']
        if c['context'][a:b] != c['source'] or not c['source']:
            raise ValueError('Source/context span mismatch')
        if c['work_id'] in {103,104,110,111,112,114,116,117,118,120,124,130,132,138,152,517}:
            raise ValueError('Protected work')
        if (c['family'],c['work_id']) != {'KANHERI06':('KANHERI',201),'BERK25':('HASTIJAN',None),
                                        'TB3':('TANG_I_BOLAGHI',None),'ZAND301':('ZAND',301)}.get(c['id']):
            raise ValueError('Canonical witness identity changed or unresolved')
        if c['training_admitted'] or c['unseen_claim_allowed'] or c['expert_certified']:
            raise ValueError('Unsupported admission/certification')
        p = [x for x in prompts if x['case_id'] == c['id']]
        if {x['condition'] for x in p} != {'A','B','C'}:
            raise ValueError('Condition missing or duplicated')
        by = {x['condition']: x for x in p}
        if not by['B']['prompt'].startswith(by['A']['prompt']+'\n\nLexical/category evidence:\n'):
            raise ValueError('B changed common input')
        if by['C']['prompt'] != by['B']['prompt']+'\n\nPublished occurrence analysis:\n'+c['analysis']:
            raise ValueError('C changed dictionary or added undeclared information')
        for x in p:
            if c['reference'] in x['prompt'] or any(k in x for k in ('reference','rubric','primary_constraint')):
                raise ValueError('Reference/scoring information entered model input')
            if x['prompt_tokens']+256 > 2048 or x['has_unknown_token']:
                raise ValueError('Actual template capacity/unknown-token failure')


def build():
    old = load_module('occurrence_sources', 'experiments/occurrence-evidence-20261001/prepare.py')
    reader = load_module('complete_dictionary_reader', 'experiments/usable-resource-20261001/prepare.py')
    bundle = load_module('common_translation_prompt', 'cloud_pilot/bundle.py')
    prior = json.loads((ROOT/'experiments/occurrence-evidence-20261001/claim-ledger.json').read_text('utf8'))
    inputs = {}

    def read(path, pin=None):
        raw = (ROOT/path).read_bytes()
        digest = sha(raw)
        if pin is not None and digest != pin:
            raise ValueError('Changed frozen input: '+path)
        inputs[path] = digest
        return raw

    def original(key):
        return read(old.PATHS[key], prior['inputs_sha256'][key])

    qualified = {r['id']: r for r in rows(original('qualified'))}
    selected = {r['id'] for r in rows(original('selected'))}
    historic = {r['id']: r for r in rows(original('train2237'))}
    dictionary = rows(original('dictionary'))
    read('data/unified-corpus/build.py', '4ecdabac48e76f9e3c01b54397a086de32168741ac21dfdac1e64c87b9e26d28')
    original('pal_policy')
    read('sources/parsig-live-inventory.json',
         '68473251ce1206f0b1beb721ae52599c82c2bfaf1a3013ef40a461eba5b08e4e')
    run = json.loads(read('experiments/dose-acquisition-20260930/live-execution/recovered/dose/training/run.json',
                         '73013069580d48fe6a3b80291b7935c28889a7007aca594b05413d38ed8df71f'))
    if run['status'] != 'completed' or run['ordered_ids'] != [r['id'] for r in rows(original('selected'))]*4:
        raise ValueError('Consumed exposure receipt differs from selected stream')
    recovered = rows(read('resources/local/occurrence-evidence-20261001/recovered-grammar-inventories.jsonl',
                          '906de3d5529a65b752929ff1578330617c527835ab5e56dcdc3f6e6ab67b718e'))
    i_entry = next(r for r in recovered if r['form']=='ī')
    if sha(i_entry['source_xml'].encode('utf8')) != '22cd51d095578ea228c3921ede0ae49e784655e6a0d47b6ccc6329c0d553003b':
        raise ValueError('Recovered complete grammatical inventory changed')

    s23 = next(r for r in rows(original('s23')) if r['candidate_id']=='S23-BERK25')
    scope = next(r for r in s23['qualified_scopes'] if r['scope_id']=='S23-BERK25-TRANSACTION-RECEIPT')
    kan = next(r for r in rows(original('kanheri')) if r['candidate_id']=='KANHERI-ARTICLE-06')
    from pypdf import PdfReader
    original('s25_pdf')
    page = PdfReader(ROOT/old.PATHS['s25_pdf']).pages[18].extract_text()
    if sha(page.encode('utf8')) != '3baf463046a04e2ad3bfe570010264ca4e2c094cd4de4bbac513a033853ae5c3':
        raise ValueError('TB3 extraction changed')
    original('s23_pdf'); original('kanheri_pdf'); original('kanheri_image')
    raw_note = json.loads(read('sources/local/parsig-2026-09-20/responses/7b0f3a98957fdcc44f4b4a2ea27d9f7d3604bde30f69adc748b107dafc08a0bd.json',
                              '9fdc68e17e8daef45fe0e2a1293920a3e29e2e46f419959b438d0920d3fdf866'))
    note = next(r for r in raw_note if str(r['Code'])=='301001016')['Note']
    if note[105:145] != 'ōyšān صورت جمع است و موصوف‌های آن مفردند':
        raise ValueError('Occurrence-number claim changed')
    read('sources/@RastarLib_زبان_پهلوی،_ادبیات_و_دستور_آن.pdf',
         '207aeda5eae48227902f0f208f9b24fd5623627dd4ca589b217268e69596df92')
    for path, pin in [
        ('resources/local/data-qualification-20260928/s23/page08.png','0534539d20cf29fff26811a17a2eaf61e928f7b5b8507ce854f369d40c8ee83f'),
        ('resources/local/dataset-expansion-20260928/s22/pdf-071.png','827489f2b572c9f7ce00a458727817af78bafca8f4f75b6da9e882e82b7a64cf'),
        ('resources/local/dataset-expansion-20260928/s22/pdf-072.png','b174753d276df1914afd2e63be70c68448821ee4989f765707eac2d3bf6275ce')]:
        read(path, pin)
    z = qualified['parsig:301001016:pal>fa']['learning']
    cases = [
        dict(id='KANHERI06', family='KANHERI', work_id=201, context=kan['source_text'], source_span=[0,22],
             reference=kan['target_text'][1:19], reference_language='fas', exposure_ids=['KANHERI-ARTICLE-06-NAME','parsig:201006001:pal>fa'],
             analysis='Published relation: source span[0,11) is the child/son; span[14,22) is the parent. This is a directed patronymic relation, not a full sentence analysis.',
             evidence='Nasrollahzadeh2017, PDF14/printed120 descriptive prose before transcription; relation read before the target by composition_packet_audit.',
             primary_constraint='Preserve the directed patronymic: Ābāngušnasp is son of the person written Farroxān; do not reverse the relation.',
             unscored=['name etymologies','Farroxān-to-Farrox spelling analysis'],
             lexical_forms=[], names=['Ābāngušnasp','Farroxān'], include_i=True),
        dict(id='BERK25', family='HASTIJAN', work_id=None, context=s23['source_text'], source_span=scope['source_char_span'],
             reference=scope['target_text'], reference_language='eng', exposure_ids=[scope['scope_id']],
             analysis='Published subject link: dād at selected-scope span[30,33) has its subject in the damaged opening personal-name slot, full-context span[0,1), line1. Identity unresolved. No occurrence-specific subject analysis of stad is supplied.',
             evidence='Asefi2025 DOI10.46991/jil/2025.01.01 PDF8/printed9, Comments Line1; read before the target by documentary_target_review.',
             primary_constraint='Express the dād giving event with an unidentified actor. An unnamed/omitted subject is allowed; omission of the event is not. Never assign Wahman-Ohrmazd or Dēnabzūd as giver.',
             unscored=['damaged opening titles/places','full stad argument structure','final separate sealing clause'],
             lexical_forms=['may','ō','ud','az'], names=['Wahman-Ohrmazd'], include_i=True),
        dict(id='TB3', family='TANG_I_BOLAGHI', work_id=None, context=page[774:828], source_span=[0,54],
             reference=page[830:888], reference_language='eng', exposure_ids=[],
             analysis='Published participant link: personal-name occurrence māh at span[16,19) is the agent of predicate span[39,54). No expanded title, overt object or exhaustive attachment analysis is supplied.',
             evidence='Asefi/Farridnejad2026, Berkeley Working Papers4(6), PDF19/printed17 independent prose at page-text[509,655), https://escholarship.org/uc/item/2kq5107p.',
             primary_constraint='The person Māh is the sealer in the muhr abar nihād predicate; do not turn this name into moon/month or change the actor.',
             unscored=['mow title expansion','uncertain ārānān reading/role','supplied object (it)','exhaustive causal scope'],
             lexical_forms=['wābarīgānīh','rāy','muhr','abar'], names=['māh'], include_i=True),
        dict(id='ZAND301', family='ZAND', work_id=301, context=z['source'], source_span=[22,39],
             reference=z['target'][34:55], reference_language='fas', exposure_ids=['parsig:301001016:pal>fa'],
             analysis='Archived occurrence Note: plural ōyšān at full-context span[22,27) accompanies singular-form nominals gyāg[28,32) and rōstāg[33,39) in this list. This does not assign case or license additional nouns/actions.',
             evidence='Parsig301001016 Note[105,145), citing Cantera2004p272 (cited page not reread); complete paragraph Dhabhar1949p10 with published Persian translator credit. historical_target_review derived Note relation before reading target.',
             primary_constraint='Both gyāg and rōstāg retain plural reference under this ōyšān. Preserve the two distinct list elements.',
             unscored=['remaining list elements','whole-paragraph translation','case/register of this occurrence'],
             lexical_forms=['gyāg','rōstāg'], names=[], include_i=False)
    ]
    # Scope changes require explicit requalification; these are reviewed UTF-8 pins.
    source_pins = ['8333e73f8c150f5115c6899c69b785a3bcd80ebfb0a35bb671f99db0ca7fcab7',
                   '5d1491f61fede1994774f06437d5a4e0404b8e82676eda3515c1039ff954ad33',
                   '4fcb62b86db72178c58af7cc640f0aeab7ea90c4d4782755a82a8478e384dafb',
                   'a9feb8a92b714e5971d717a4e9a8cbb0780d94b35ef48f184682b074961f5fde']
    ref_pins = ['14236d3dd0a3f2b8cc8a121bc32b7ac140588a82b568b5afad63c15f40b2f4ce',
                'd68afcc811ab5233e98c3aa80da40d18c68b971ce9f9dc7cdc53dc5ffb49935c',
                '5b42784d08988d5f89beccaf5232568fb784dca3629a04324d52f557a09b5e35',
                '5d916dfd6de907192ee09da180d32fe9276f4d3d738cdc9c74d79c671ba2859d']
    prior_aid = rows(read('experiments/dev-assisted-qualified-20260927/evidence/evidence.jsonl'))
    aid_sources = [e['source_text'] for r in prior_aid for e in r['examples']]
    if len(aid_sources)!=58:
        raise ValueError('Earlier attachment universe changed')
    translator='[USER_HOME]/Documents/Codex Projects/01-Software/Pahlavi Translator/'
    s04=json.loads(read(translator+'config/experiments/lexical-sense-diagnostic-plan.json',
        'de2a6fc17d4df48da6c08fa0a1e21a8157971e00e95d2b0793877ffe37e17692'))
    s07=json.loads(read(translator+'config/experiments/grammar-agent-diagnostic-plan.json',
        '478276c9cf9bf5e01f0f5117f4c78f5a796588c078c363d181c46c129f1f94af'))
    information_audit=dict(s04_added_senses=s04['added_senses'],s07_notes=s07['grammar_notes'],
        previous_attachment_count=len(aid_sources),previous_distinct_source_count=len(set(aid_sources)),
        scope='Exact saved S04 added-sense payload, S07 note payload and source fields of all58 prior attachments; no prior targets/outputs read.',
        limits='Does not prove no earlier inference exposure or compare every historical prompt artifact.')
    for path in ['experiments/occurrence-evidence-20261001/prepare.py',
                 'experiments/usable-resource-20261001/prepare.py',
                 'experiments/usable-resource-20261001/punctuation-decisions.json',
                 'cloud_pilot/bundle.py']:
        read(path)
    from tokenizers import Tokenizer
    from jinja2.sandbox import ImmutableSandboxedEnvironment
    tokroot = ROOT/'resources/local/cloud-pilot-qualified-20260927/tokenizer'
    for filename, pin in bundle.TOKENIZER_HASHES.items():
        read(str((tokroot/filename).relative_to(ROOT)), pin)
    tok = Tokenizer.from_file(str(tokroot/'tokenizer.json'))
    template = ImmutableSandboxedEnvironment().from_string((tokroot/'chat_template.jinja').read_text('utf8'))
    config = json.loads((tokroot/'tokenizer_config.json').read_text('utf8'))
    prompts = []
    for c, sp, rp in zip(cases, source_pins, ref_pins):
        a,b = c['source_span']; c['source'] = c['context'][a:b]
        if sha(c['source'].encode('utf8'))!=sp or sha(c['reference'].encode('utf8'))!=rp:
            raise ValueError('Qualified source/reference span changed: '+c['id'])
        inventories=[]
        for form in c['lexical_forms']:
            hits=[r for r in dictionary if form in r['forms']]
            if not hits:
                raise ValueError('Missing declared complete inventory: '+form)
            for r in hits:
                text,_,_=reader.render(r['archival_target'], r['task'], r['id'])
                if text!=r['meaning_text']:
                    raise ValueError('Incomplete dictionary reader')
                inventories.append(dict(id=r['id'], forms=r['forms'], scope=r['context'], text=text,
                                        binding='EXACT_SURFACE_CANDIDATES_ALL_SCOPED_HOMOGRAPHS_NOT_SELECTED_SENSE'))
        if c['include_i']:
            inventories.append(dict(id=i_entry['id'], forms=['ī'], text=I_READER,
                                    scope={'source_scope':'MacKenzie CPD printed45'}, binding='EXACT_CONNECTIVE_RELATIVE_CANDIDATES',
                                    source_xml_sha256=i_entry['source_xml_sha256'], original_hold_unchanged=True))
        if c['id']=='ZAND301':
            inventories.append(dict(id='S22GRAM-021',forms=['ōyšān','awēšān'],text=PRONOUN_READER,
                                    scope={'source_scope':'Amouzgar/Tafazzoli1382SH printed68–69'},binding='PUBLISHED_SCOPED_PRONOUN_BUNDLE'))
        c['inventories']=inventories
        covered=set(c['lexical_forms']) | ({'ī'} if c['include_i'] else set()) | ({'ōyšān'} if c['id']=='ZAND301' else set())
        c['lexical_gaps']=[{'form':word,'span':[m.start(),m.end()],'status':'NO_VERIFIED_OCCURRENCE_TO_COMPLETE_INVENTORY_BINDING'}
            for m in re.finditer(r'\S+',c['source']) if (word:=m.group()) not in covered and word not in c['names'] and not word.isdecimal()]
        c['name_category_evidence']='Published source prose; preserve names without inferred etymology or lemma aliases.'
        c['exposure']={'qualified_ids':[i for i in c['exposure_ids'] if i in qualified],
            'selected1536_ids':[i for i in c['exposure_ids'] if i in selected],
            'train2237_ids':[i for i in c['exposure_ids'] if i in historic],
            'dose_consumptions':sum(run['ordered_ids'].count(i) for i in c['exposure_ids']),
            'prior58_exact_source_matches':sum(c['source']==s for s in aid_sources),
            'prior58_source_contains_component':sum(' '.join(c['source'].split()) in ' '.join(s.split()) for s in aid_sources),
            'earlier_inference_exposure':'NOT_FULLY_AUDITED',
            'no_match_does_not_prove_unseen':True}
        c.update(training_admitted=False, unseen_claim_allowed=False, expert_certified=False)
        c['inventory_policy']='Complete scoped candidates supplied; contextual sense not selected and token coverage not scored.'
        common=bundle.PROMPT.format(text=c['context'])
        common+='\nTranslate only the selected source span '+str(c['source_span'])+' (half-open Unicode code points):\n'+c['source']
        lexical='\n\n'.join('Forms: '+', '.join(r['forms'])+'\nScope: '+json.dumps(r['scope'],ensure_ascii=False)+'\n'+r['text'] for r in inventories)
        lexical+='\nPublished personal-name occurrences: '+(', '.join(c['names']) or 'none declared')
        lexical+='\nUnbound surface forms (no guessed lemma/gloss): '+', '.join(x['form'] for x in c['lexical_gaps'])
        arms={'A':common,'B':common+'\n\nLexical/category evidence:\n'+lexical}
        arms['C']=arms['B']+'\n\nPublished occurrence analysis:\n'+c['analysis']
        for condition,prompt in arms.items():
            rendered=template.render(messages=[{'role':'user','content':prompt}],add_generation_prompt=True,
                enable_thinking=False,bos_token=config['bos_token'],tools=None)
            ids=tok.encode(rendered,add_special_tokens=False).ids
            prompts.append(dict(id=c['id']+'-'+condition,case_id=c['id'],condition=condition,prompt=prompt,
                                prompt_tokens=len(ids),rendered_sha256=sha(rendered.encode('utf8')),
                                has_unknown_token=tok.token_to_id('<unk>') in ids))
    validate(cases,prompts)
    outputs={'cases.jsonl':b''.join(encoded(c) for c in cases),'model-inputs.jsonl':b''.join(encoded(p) for p in prompts)}
    manifest=dict(schema_version=1,status='LOCAL_COMPONENT_PACKET_NOT_PAID_OR_TRAINING_ADMITTED',
        intended_checkpoint='retained Gemma4-31B step280; no execution performed',
        case_count=4,family_count=4,planned_first_outputs=12,max_new_tokens=256,context_limit=2048,
        max_prompt_tokens=max(p['prompt_tokens'] for p in prompts),training_allowed=False,paid_launch_allowed=False,
        fixed_merit_changed=False,input_sha256=inputs,information_difference_audit=information_audit,
        protected_acquisition_screen={'AŌD-K20':{'canonical_work_id':150,'status':'IDENTITY_CLEAR_REFERENCE_UNQUALIFIED'},
            'WZ-K35':{'canonical_work_id':152,'status':'PROTECTED_EXCLUDE_BEFORE_ANSWER_ACQUISITION'},
            'PVr-K7a':{'canonical_work_id':None,'status':'HOLD_IDENTITY_UNRESOLVED'},
            'RĀF-TD2':{'canonical_work_id':None,'status':'HOLD_IDENTITY_UNRESOLVED'}},
        local_outputs={name:dict(path=str((OUT/name).relative_to(ROOT)),bytes=len(raw),sha256=sha(raw)) for name,raw in outputs.items()},
        remaining_gates=['independent exact-packet/Astra review',
                         'pinned cloud numerical/decoding/runtime/cost contract and exact launch authorization'])
    return cases,prompts,outputs,manifest


def main():
    cases,prompts,outputs,manifest=build()
    if sys.argv[1:]==['--write']:
        # Update only this builder's intact preparation outputs; preserve edits.
        if OUT.exists() or (HERE/'packet-manifest.json').exists():
            previous=json.loads((HERE/'packet-manifest.json').read_text('utf8'))
            if set(previous['local_outputs'])!=set(outputs):
                raise ValueError('Unknown preparation output ownership')
            for name,item in previous['local_outputs'].items():
                if sha((OUT/name).read_bytes())!=item['sha256']:
                    raise ValueError('Refusing to overwrite changed preparation output')
        OUT.mkdir(parents=True,exist_ok=True)
        for name,raw in outputs.items(): (OUT/name).write_bytes(raw)
        (HERE/'packet-manifest.json').write_bytes(encoded(manifest))
    elif sys.argv[1:]==['--check']:
        if json.loads((HERE/'packet-manifest.json').read_text('utf8'))!=manifest:
            raise ValueError('Manifest/input identity changed')
        for name,raw in outputs.items():
            if (OUT/name).read_bytes()!=raw: raise ValueError('Frozen output changed: '+name)
        for kind in ('context','protected','admission','dictionary','reference','capacity'):
            cc,pp=deepcopy(cases),deepcopy(prompts)
            if kind=='context': cc[0]['source_span']=[1,22]
            elif kind=='protected': cc[0]['work_id']=152
            elif kind=='admission': cc[0]['training_admitted']=True
            elif kind=='dictionary': pp[2]['prompt']+=' undeclared gloss'
            elif kind=='reference': pp[0]['reference']=cc[0]['reference']
            else: pp[0]['prompt_tokens']=2048
            try: validate(cc,pp)
            except ValueError: pass
            else: raise ValueError('Mutation accepted: '+kind)
    else: raise ValueError('Use --write or --check')
    print(json.dumps(dict(cases=4,prompts=12,max_prompt_tokens=manifest['max_prompt_tokens'],
        actual_dose_exposures={c['id']:c['exposure']['dose_consumptions'] for c in cases},
        tests=6 if '--check' in sys.argv else 0,paid_launch_allowed=False),sort_keys=True))


if __name__=='__main__': main()
