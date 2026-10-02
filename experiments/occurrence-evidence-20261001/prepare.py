"""Build/check a source-only qualification ledger; never admit training or jobs.

Classic + Critic. Reuse the frozen CPD extractor and stdlib JSONL; no retrieval
service, scoring framework, aliases, model calls or automatic gold generation.
"""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'resources/local/occurrence-evidence-20261001'
PATHS = {
    'qualified': 'resources/local/training-ready-v2-20260929/data/learning-projections.jsonl',
    'selected': 'resources/local/training-ready-v2-20260929/data/train.jsonl',
    'train2237': 'experiments/train-audit-20260927/qualified-v1/train.jsonl',
    's23': 'experiments/data-qualification-20260928/s23-candidates.jsonl',
    'kanheri': 'experiments/data-qualification-20260928/kanheri-candidates.jsonl',
    's23_pdf': 'sources/01+-+Nima+Asefi.pdf',
    's25_pdf': 'sources/qt2kq5107p.pdf',
    'kanheri_pdf': 'sources/local/public-texts-2026-09-20/qualification-source-search-20260928/raw/b385981ef422d96884dc19c958c274bf2e9efb0aefd923d83dbb71a2ae9fca1f.pdf',
    'kanheri_image': 'sources/local/public-texts-2026-09-20/qualification-source-search-20260928/inspection/kanheri/page14.png',
    'observations': 'resources/local/kosh-quality-20260928/complete-v4/observations.jsonl',
    'cpd_held': 'resources/local/data-qualification-20260928/cpd/held.jsonl',
    'cpd_qualified': 'resources/local/data-qualification-20260928/cpd/qualified.jsonl',
    'cpd_extractor': 'experiments/dataset-expansion-20260928/cpd_extract.py',
    'cpd_rules': 'experiments/data-qualification-20260928/cpd_qualify.py',
    'dictionary': 'resources/local/usable-resource-v3-20261001/dictionary.jsonl',
    'cpd_pdf': 'sources/local/mackenzie-pdf-20260928/english-1986.pdf',
    'kosh_raw': 'sources/local/public-texts-2026-09-20/kosh-catalogue-sized-20260928/raw/4b77cb976e9af1d4842f40bed847ea51ee00a5177e28e8fee6239184d49220c3.source',
    'pal_policy': 'benchmarks/pal-reference-v1/holdout-policy.json',
}

# Half-open Unicode offsets; citations are leads, not reread printed editions.
NOTES = [
    ('134001000', 'parsig:134', '1dbdea24e3025c4b74daf9033c500e978707a8930e61bc7552883ac87c04092f', [(191,200,'nibēsīhēm')], [(9,32)], 'CONFLICTED',
     'The note identifies a passive verb, but spells it differently from the transcription; preserve both readings and its alternative forms.',
     'Rashid-Mohassel1370,p21; Anklesaria1957,p1', 'Passive morphology only; source ē versus note ī remains unresolved.'),
    ('136002025', 'parsig:136', '7bbaa670530e9f88fcd6dbbed4db798716148f6866e314a9364d4e1e1ff649cb', [(42,61,'tō nē dānāgīhā kard'),(126,130,'burd'),(160,164,'guft')], [(169,243)], 'PROVISIONAL',
     'The note conditionally analyzes burd/guft as past transitive/ergative with tō as agent, alongside adverbial versus verbal-negation alternatives.',
     'Faravashi1378,pp19,21; Anklesaria1935,pp13-14', 'Translator-assisted conditional argument; neither agent nor negation scope is certain.'),
    ('301001016', 'ZAND_TRADITION', '7b0f3a98957fdcc44f4b4a2ea27d9f7d3604bde30f69adc748b107dafc08a0bd', [(22,93,'ōyšān gyāg rōstāg ud gāwyōd ud mēhan ud āb-xwar ud āb ud zamīg ud urwar')], [(105,145)], 'PROVISIONAL',
     'The note observes plural ōyšān with singular following nouns and compares the Avestan number.',
     'Cantera2004,p272; Dhabhar1949,p10', 'Number/agreement observation, not exhaustive attachments; parallel text not reread.'),
    ('301002003', 'ZAND_TRADITION', '5d6079af005377db7bd1693ac1d823908be87501131f074549a20300cc651223', [(716,768,'ān mēnōg [kē] ka mizag ī xwarišn dānēnd pad\u00a0rāh\u00a0ī ōy')], [(115,155),(207,232)], 'PROVISIONAL',
     'The note tentatively changes manuscript kū to relative kē and identifies ān mēnōg as antecedent.',
     'Brunner1977,p82,manuscriptK; Dhabhar1949,pp13-14', 'The source already contains editorial[kē]; novel information must be its attributed function, not spelling duplication.'),
    ('301002006', 'ZAND_TRADITION', '5d6079af005377db7bd1693ac1d823908be87501131f074549a20300cc651223', [(281,320,'ahlawān wehān abzārān abzōnīgān frawahr')], [(260,336)], 'PROVISIONAL',
     'The note argues that wehān/abzārān/abzōnīgān qualify frawahr using Yasna2.11/17 and Avestan parallels, proposing deletion of intervening ud.',
     'Dhabhar1949,p15; intratextual and Avestan parallels', 'Current source already adopts no-ud; parallel passages/manuscript were not reread.'),
    ('302001001', 'ZAND_TRADITION', '1551d5c357285e337bec0a100f7d1ab9c8befed23f7356b650bbfbc0f95c0f93', [(57,68,'ahlāyēnīdār')], [(9,61)], 'PROVISIONAL',
     'The note analyzes ahlāy plus ēn as a causative base.',
     'Dhabhar1927,p1; Hajipour1400', 'Morphology only; do not inherit the preferred translation or infer agent/patient roles.'),
]
DOCUMENTS = [
    ('BERK25-AGENT','S23-BERK25',[(258,261,'dād'),(0,37,'… ī pad... [dārīg] az ān ī [az mar ī]')],[8],
     'Asefi attributes the giver role to the missing opening personal name, not the final sealer.', 'Missing/restored agent remains unknown; whole parent stays held.'),
    ('BERK11-LOCATIVE','S23-BERK11',[(93,98,'xar 4'),(126,139,'Yazdānābestān'),(140,146,'estēnd')],[21],
     'Asefi reads estēnd as the predicate stating that four donkeys are in Yazdānābestān.', 'Preserve competing Gignoux ān nāmag reading; isolate from the ration-target contradiction.'),
    ('BERK11-CLITIC','S23-BERK11',[(45,48,'ī-š')],[20,21],
     'Asefi attributes <ZYš> to ī-š rather than the older kas reading.', 'No referent supplied; same witness as the locative lead, not an independent case.'),
    ('BERLIN26-NAME','S23-BERLIN26',[(66,83,'Kard-ābād-yazdbād')],[17],
     'Asefi treats Kard as part of the garden name rather than a repeated independent verb.', 'Preserve earlier Weber verb/marriage interpretation; attributed analysis is not consensus gold.'),
]
LEXICAL = [
    ('ī','11e0df6d1643dee73a27af9c4cfdb5d008caf2e8','22cd51d095578ea228c3921ede0ae49e784655e6a0d47b6ccc6329c0d553003b','NO_GENERIC_GLOSS_IN_SENSE',67,45,'Preserve grammar-only connective sense as grammar, not invented translation.'),
    ('pad','5952ae18b854496d99b3a760f2ce6598404301fc','eb8ab05f6ec67ab45390ccd6c6039cca2f07353e5060b9c03c2e17a496ca5499','UNCERTAIN_OR_DAMAGED_FORM',84,62,'Keep doubtful qualifier on ideogramPWN; do not propagate it to all transcription/gloss fields.'),
    ('ōy','b4a2e880e72be512d273496200436804a0d9fc1b','cac2d4ab451c5785bcfe5bde11b3a6e3755e684b4c4b74423ad15b952a943b31','COMPLEX_GRAMMAR_SCOPE',84,62,'Retain plural awēšān as a typed relationship and the MMP adverb homograph separately.'),
    ('guft','c24e8b77df60f790e4b4f18480cdf1c0e65aca8c','2c454533f5a1fc8c3e6b9ad5e3f28cdcc5b4bd9de976338505c6fd58e45d7e46','FORM_SENSE_ASSOCIATION_UNRESOLVED',None,None,'No exactguft headword: bundled verb inventory and occurrence-to-lemma mapping unresolved.'),
    ('kard','1c3c87465c0b89c8a3e1d2865cda449302ffbdb5','11b237dab3af8a1dc414ae523158883dcde3e5a9b5aa0f4d61213fb6150dd6dd',None,None,None,'The qualified noun inventory does not automatically apply to an occurrence of the past verb.'),
    ('kardan','f1293e5d4093b37a1dc0d405bfc29d62a81b3715','59286a0d05dc59b53c5bd8612efe3e4deec782858206bb819466e349308b6b8d','FORM_SENSE_ASSOCIATION_UNRESOLVED',None,None,'Published bundled verb forms need morphology/association evidence; no generated aliases.'),
]
MPCD = [
    ('AŌD-K20','Andarz_i_osnar_danag','Andarz',1726,'5428e141-0d76-4793-82bf-5c4e973c89df'),
    ('PVr-K7a','Pahlavi_Wisperad','Zand',4386,'1bb4294f-d261-494c-ab3a-bf0f172a648c'),
    ('RĀF-TD2','Rivayat_of_Adurfarnbay','Juridical',12413,'084aedd7-181e-4a52-8d84-aff3b5be7ef8'),
    ('WZ-K35','Wizidagihai_zadspram','Theological',9715,'56385fdd-7da4-435b-8df2-b5f0c55ffe45'),
]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf8')


def rows(raw):
    return [json.loads(x) for x in raw.decode('utf8').splitlines() if x.strip()]


def build():
    paths=dict(PATHS)
    for _,_,name,*_ in NOTES:
        paths['raw_'+name]='sources/local/parsig-2026-09-20/responses/'+name+'.json'
    raw={k:(ROOT/v).read_bytes() for k,v in paths.items()}
    qualified={r['id']:r for r in rows(raw['qualified'])}
    selected={r['id'] for r in rows(raw['selected'])}
    old={r['id'] for r in rows(raw['train2237'])}
    claims=[]
    views=[]

    def add(cid,family,origin,source,spans,claim,evidence,disposition,limitation):
        anchors=[]
        for a,b,text in spans:
            if source[a:b]!=text:
                raise ValueError('Source anchor changed: '+cid)
            anchors.append({'span':[a,b],'text_sha256':sha(text.encode('utf8'))})
        item={'id':cid,'work_family':family,'origin':origin,'source_sha256':sha(source.encode('utf8')),
              'full_source_span':[0,len(source)],'anchors':anchors,'claim':claim,'evidence':evidence,
              'disposition':disposition,'limitations':[limitation],
              'reference_status':'NOT_QUALIFIED_FOR_THIS_DIAGNOSTIC','earlier_inference_exposure':'NOT_AUDITED',
              'unseen_generalization_claim_allowed':False,'complete_pilot_case':False,'training_admitted':False,
              'target_used_to_derive_analysis':False,'candidate_outputs_used':False}
        claims.append(item)
        views.append({'id':cid,'source':source})

    for code,family,name,spans,note_spans,disp,claim,citation,limit in NOTES:
        rid='parsig:'+code+':pal>fa'
        original=next(r for r in json.loads(raw['raw_'+name]) if str(r['Code'])==code)
        source=qualified[rid]['learning']['source']
        if not original['Transcription'][0]['Section'].startswith(source):
            raise ValueError('Source differs from archived occurrence')
        note=original['Note']
        add('NOTE-'+code,family,{'kind':'qualified','record_id':rid,'work_id':int(code[:3])},source,spans,claim,
            {'kind':'archived-note','input':'raw_'+name,'field':'Note','note_sha256':sha(note.encode('utf8')),
             'note_anchors':[{'span':[a,b],'text_sha256':sha(note[a:b].encode('utf8'))} for a,b in note_spans],
             'citation':citation,'printed_primary_page_reread':False},disp,limit+' Cited editions not reread.')
        claims[-1]['exposure']={'in_qualified_pool':True,'in_selected1536':rid in selected,'in_train2237':rid in old}
    s23={r['candidate_id']:r for r in rows(raw['s23'])}
    for cid,parent,spans,pages,claim,limit in DOCUMENTS:
        add('S23-'+cid,'HASTIJAN',{'kind':'candidate-jsonl','input':'s23','record_id':parent},s23[parent]['source_text'],spans,claim,
            {'kind':'printed-commentary','input':'s23_pdf','pdf_pages_1_based':pages,'printed_pages':[p+1 for p in pages],
             'citation':'Asefi2025,DOI10.46991/jil/2025.01.01','visual_check_agent':'/root/composition_packet_audit'},'PROVISIONAL',limit)
    kan=next(r for r in rows(raw['kanheri']) if r['candidate_id']=='KANHERI-ARTICLE-06')
    add('KANHERI06-PATRONYMIC','parsig:201',{'kind':'candidate-jsonl','input':'kanheri','record_id':kan['candidate_id'],'work_id':201},
        kan['source_text'],[(0,22,'Ābāngušnasp ī Farroxān'),(0,11,'Ābāngušnasp'),(14,22,'Farroxān')],
        'Article descriptive prose identifies Ābāngušnasp as son of Farrox.',
        {'kind':'printed-descriptive-prose','input':'kanheri_pdf','pdf_pages_1_based':[14],'printed_pages':[120],
         'image_input':'kanheri_image','citation':'Nasrollahzadeh2017,Kanheri article','visual_check_agent':'/root/composition_packet_audit'},
        'PROVISIONAL','Name phrase, not a sentence. Two physical occurrences count as one type; same existing Parsig201006001 witness.')
    rid='parsig:201006001:pal>fa'
    claims[-1]['exposure']={'same_witness_record':rid,'in_qualified_pool':rid in qualified,'in_selected1536':rid in selected,'in_train2237':rid in old}
    from pypdf import PdfReader
    page=PdfReader(ROOT/paths['s25_pdf']).pages[18].extract_text()
    source='wābarīgānīh rāy māh ī mow ī (?) ārānān muhr abar nihād'
    a=page.index(source)
    add('S25-TB3-SEALER','TANG_I_BOLAGHI',{'kind':'pdf-transcription','input':'s25_pdf','pdf_page_1_based':19,
        'page_text_span':[a,a+len(source)],'page_text_sha256':sha(page.encode('utf8')),'extractor':'pypdf'},source,
        [(16,19,'māh'),(39,43,'muhr'),(44,54,'abar nihād')],
        'Adjacent primary prose identifies the lower-section clause as witness sealing and connects the name/title to bullae.',
        {'kind':'printed-commentary','input':'s25_pdf','pdf_pages_1_based':[19],'printed_pages':[17],
         'citation':'Asefi and Farridnejad2026,Three Middle Persian documents from Fars dating to the reigns of XusroII and OhrmazdIV,PDF19/printed17',
         'publication_url':'https://escholarship.org/uc/item/2kq5107p','visual_check_agent':'/root/composition_packet_audit'},
        'PROVISIONAL','Title remains uncertain. TB4 restoration/TB9 ellipsis are not independent families; reference/exposure unqualified.')
    obs={r['id']:r for r in rows(raw['observations'])}
    archived_cpd=json.loads(raw['kosh_raw'])['data']['entries']
    held={r['id']:r for r in rows(raw['cpd_held'])}
    released={r['id']:r for r in rows(raw['cpd_qualified'])}
    spec=importlib.util.spec_from_file_location('frozen_cpd_extract',ROOT/paths['cpd_extractor'])
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    import pypdfium2 as pdfium
    document=pdfium.PdfDocument(ROOT/paths['cpd_pdf'])
    page_pins={67:'a1085646c1cc2da73d1d72caec6773a307acfa43a745c14f6cfbfae9db1f647a',
               84:'7b28cf51c8ca9be436880ca0ceb688bc32b905f5d73c5b71f25fd8fdd4913977'}
    try:
        for number,pin in page_pins.items():
            page=document[number-1]
            textpage=page.get_textpage()
            try:
                if sha(textpage.get_text_range().encode('utf8'))!=pin:
                    raise ValueError('Changed printed entry page extraction')
            finally:
                textpage.close()
                page.close()
    finally:
        document.close()
    lexical=[]
    recovery=[]
    for i,(form,key,pin,reason,pdfpage,printed,limit) in enumerate(LEXICAL):
        oid='kosh:cpd:'+key
        rid=oid+':block:0'
        observation=obs[oid]
        if sha(raw['kosh_raw'])!=observation['raw_sha256']:
            raise ValueError('Changed archived dictionary response')
        if observation['source_record'] not in archived_cpd:
            raise ValueError('CPD observation not backed by archived response')
        xml=observation['source_record']['xml']
        if sha(xml.encode('utf8'))!=pin:
            raise ValueError('Changed CPD entry')
        if reason is not None and held[rid]['reasons']!=[reason]:
            raise ValueError('Changed hold disposition')
        if reason is None and rid not in released:
            raise ValueError('Changed released noun inventory')
        lexical.append({'id':rid,'observation_id':oid,'lookup_form_under_review':form,'source_xml_sha256':pin,
            'original_hold_reason':reason,'printed_pdf_page_1_based':pdfpage,'printed_page':printed,
            'disposition':'READABLE_REVIEW_ONLY_RECOVERY' if i<3 else 'OCCURRENCE_OR_BUNDLE_UNRESOLVED',
            'limitation':limit,'remove_original_hold':False,'training_admitted':False,'occurrence_mapping_admitted':False})
        if i<3:
            ex=module.extract(xml)
            if ex['status']!='STRUCTURE_RECOVERED_REVIEW_REQUIRED' or len(ex['blocks'])!=1:
                raise ValueError('Unexpected recovered structure')
            # Keep the whole typed tree, XML, attributes and inline tails. A field
            # view serves review, never a newly fabricated single translation.
            recovery.append({'id':rid,'form':form,'status':'READABLE_SOURCE_QUALIFIED_REVIEW_ONLY',
                'training_admitted':False,'occurrence_mapping_admitted':False,'expert_certified':False,
                'source_xml':xml,'source_xml_sha256':pin,'typed_tree':ex['tree'],
                'printed_evidence':{'pdf_input':'cpd_pdf','pdf_page_1_based':pdfpage,'printed_page':printed,
                    'page_text_sha256':page_pins[pdfpage],'page_text_extractor':'pypdfium2.get_text_range',
                    'visual_review_agent':'/root/target_cleanup_review','scope':'main-entry lines only'},
                'original_hold_reason':reason,'source_observation_id':oid,
                'raw_receipt':{'relative_path':observation['raw_file'],'sha256':observation['raw_sha256']}})
    outputs={'source-claims.jsonl':b''.join(encoded(v) for v in views),
             'recovered-grammar-inventories.jsonl':b''.join(encoded(v) for v in recovery)}
    ledger={'schema_version':1,'date':'2026-10-01','status':'PARTIAL_EVIDENCE_NOT_DIAGNOSTIC_OR_TRAINING_ADMITTED',
        'complete_pilot_cases':0,'paid_launch_allowed':False,'training_allowed':False,
        'input_paths':paths,'inputs_sha256':{k:sha(v) for k,v in raw.items()},'claims':claims,'dictionary_review':lexical,
        'local_outputs':{name:{'path':str((OUT/name).relative_to(ROOT)).replace('\\','/'),'sha256':sha(v),'bytes':len(v)} for name,v in outputs.items()},
        'mpcd_options':[{'witness':w,'work_family':f,'status_observed':'Annotated','genre_observed':g,'tokens_observed':n,
            'url':'https://www.mpcorpus.org/corpus/sections/'+u,'qualified_case_count':0,
            'exposure_and_protected_work_identity':'UNRESOLVED','reference_status':'UNQUALIFIED_WORKING_TRANSLATIONS'} for w,f,g,n,u in MPCD],
        'mpcd_observation':{'date':'2026-10-01','catalog_url':'https://www.mpcorpus.org/corpus/texts/',
            'publications_url':'https://www.mpcorpus.org/publications/','methodology_url':'https://www.mpcorpus.org/methodology/',
            'method':'normal signed-out public browser; manually recorded UI, not raw API export',
            'witness_rows':110,'statuses':{'Preannotated':47,'Inprogress':19,'Annotated':44,'Reviewed':0},
            'counts_are_independent_works':False,'raw_catalog_export_saved':False,
            'limits':['Working translations are lexicographic drafts, not final gold; consult responsible philologist before quoting.',
                'Some comments are not displayed; dictionary includes automatic/incomplete material.',
                'DD-K35 Inprogress graph demonstrated access only; no graph or translation admitted.']}}
    return ledger,outputs


def validate(ledger,outputs):
    expected,expected_outputs=build()
    if ledger!=expected or outputs!=expected_outputs:
        raise ValueError('Evidence, projection or admission contract changed')
    assert len(ledger['claims'])==12 and len(ledger['dictionary_review'])==6 and len(ledger['mpcd_options'])==4
    assert len({c['id'] for c in ledger['claims']})==12
    assert sum(c.get('exposure',{}).get('in_selected1536',False) for c in ledger['claims'][:6])==6
    assert len(rows(outputs['recovered-grammar-inventories.jsonl']))==3


def check():
    ledger=json.loads((HERE/'claim-ledger.json').read_text('utf8'))
    outputs={n:(OUT/n).read_bytes() for n in ledger['local_outputs']}
    validate(ledger,outputs)
    # Corruption/nonadmission checks change only in-memory copies.
    mutations=[lambda r:r.update(paid_launch_allowed=True),
               lambda r:r['claims'][0]['anchors'][0].update(span=[190,200]),
               lambda r:r['claims'][0]['exposure'].update(in_selected1536=False),
               lambda r:r['dictionary_review'][1].update(remove_original_hold=True),
               lambda r:r['mpcd_options'][0].update(status_observed='Reviewed')]
    for mutate in mutations:
        changed=deepcopy(ledger)
        mutate(changed)
        try:
            validate(changed,outputs)
        except ValueError:
            pass
        else:
            raise AssertionError('Mutation not rejected')
    changed=dict(outputs)
    entries=rows(changed['recovered-grammar-inventories.jsonl'])
    entries[1]['typed_tree']['children'][0]['children'][1]['attributes']={}
    changed['recovered-grammar-inventories.jsonl']=b''.join(encoded(e) for e in entries)
    try:
        validate(ledger,changed)
    except ValueError:
        pass
    else:
        raise AssertionError('Lost ideogram uncertainty not rejected')
    print('PASS:12partialclaims;6historicalparents selected;3typedreview-only recoveries;4publicoptions;6mutationsrejected;0completecases/noadmission.')


if __name__=='__main__':
    if sys.argv[1:]==['--write']:
        if (HERE/'claim-ledger.json').exists() or OUT.exists():
            raise SystemExit('Refuse overwriting existing evidence')
        ledger,outputs=build()
        OUT.mkdir()
        for name,raw in outputs.items():
            (OUT/name).write_bytes(raw)
        (HERE/'claim-ledger.json').write_bytes(encoded(ledger))
        check()
    elif sys.argv[1:] in ([],['--check']):
        check()
    else:
        raise SystemExit('Use --write once or --check')
