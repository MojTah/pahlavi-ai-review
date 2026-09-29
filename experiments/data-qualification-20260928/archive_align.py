"""Replay hand-reviewed archive dispositions; no classifier or translation generation."""
from pathlib import Path
from collections import Counter
from html.parser import HTMLParser
import hashlib, json, re, sys, unicodedata, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / 'experiments/dataset-expansion-20260928/archive-candidates.jsonl'
EXPECTED = 'fe2e80cbb323b2072c673fb0e715dba8d100f670bad9fbaf975b4b3b2ddba48d'
OUT = Path(__file__).parent
NS = 'http://www.tei-c.org/ns/1.0'
sha = lambda b: hashlib.sha256(b).hexdigest()
assert sha(INPUT.read_bytes()) == EXPECTED
packets = [json.loads(x) for x in INPUT.read_text(encoding='utf-8').splitlines()]
assert len(packets) == 53

# These are individual manual judgments after reading both complete layers.
# W = complete paired passage; F = paired fragment with damage/restoration;
# H = complete packet held, with independently selected salvage units below.
REVIEWS = {
'MP0603': ('F', 'Bābag the miller, Wahman year 38, 3 grīw garmak, Farroxzād’s sister, 2 kabīz wheat and Zādānfarrox sealing correspond. Both layers mark illegible material around the reckoning clause; do not learn a complete unbroken transaction.', 'Empty TEI unclear elements, the broken …tan word and target calendar/appositional glosses must accompany the pair.'),
'MP5650': ('F', 'Ardwahišt/Aštād/Asmān dates, Dēnhurām, barley, Mihrād’s 14 men, wine, and the visible 10/23 remnants occur in matching inventory order. This is an interrupted account, not reconstructed prose.', 'Many parenthetical gaps, unresolved name remnants and incomplete final clauses; retain them.'),
'MP1024': ('W', 'Address to Wazurgummēd and Wīrgušnasp, Xradzād’s greeting, Farroxgušnasp’s complaint concerning Yazdfarrox and Yazdweh, the inquiry/conditional order and Mihr year 104 Frawardīn date have matching passage scope. Complaint and conditional directions are not recast as an established verdict.', 'Keep *Haspīn-raz, *zaydār and *Halīg, pādixšāy, parenthetical participant identification and legal/explanatory wording. This qualifies the edition’s whole translation, not a new adjudication of every legal term.'),
'MP0404': ('W', 'Aškānīzag the tailor, Dēnabzūd the scribe, Mihrīgān year 39, 4 satēr and the Windād-Burzmihr festival witness-sealing clause match across the full receipt.', 'Retain the edition’s service-role reading of hammōzag as procurator; this is an edition-specific interpretation, not a context-free dictionary equivalence.'),
'MP0602': ('W', 'Dādēnwindād, Yazdānābestān, Ābān year 40/day Ābān, lamp-oil refining, 1000 šānčak to Mihr-Ādur and Yazdānpādār sealing correspond. English gathers the source’s discontinuous obligation into one passage.', 'šānčak and čak are retained technical terms; calendar numbers and grammatical line references are edition commentary.'),
'MP0032': ('W', 'Dādēnwindād gives Dēnbānag of Sarm a two-day ration for one horse and three donkeys: 2 grīw barley and 10 bundles lucerne, Mihr year 40/day Zāmyād; the ōstāndār seals. All quantities and roles match.', 'The English order differs from source line order; the whole receipt, not individual equal-numbered lines, is the unit.'),
'MP0045': ('F', 'Baxtiyār, the Windādburzmihr-ābād estate, Hordad year 48, acquisition of 40 grīw 8 kabīz copper, a small copper bun to boys, and Kurdōy sealing correspond.', 'Baxtiyār and year/restored words are supplied; smudged words remain gaps. Copper and the small bun retain the edition’s parenthetical interpretation.'),
'MP1029': ('H', 'The whole legal instrument cannot yet be qualified: the same pondik wanīh is rendered Hazelnut Groves in one place and beyond the vineyards in line 6; the target has the unexplained fused quotaNote token in line 16. The dateline can be isolated without those defects.', 'Do not silently harmonize the land description, repair quotaNote or infer the disputed obligation. The repeated account statements require edition reconciliation.'),
'MP0408': ('W', 'Aspbād, Ādur and Day year 32, Kurdōy’s 60 pails wine, the single-horseman allocation of 20 pails, Dēnabzūd sealing and the separate vertical dahag endorsement all have English counterparts.', 'Preserve the vertical endorsement boundary and the target’s *issuing office interpretation; line-label repetitions are layout commentary.'),
'MP0070': ('F', 'The value of spilled wine, presentation of the čak, Farrox as payer/source, and the caravaneer sealing with Aspbād’s witness seals correspond.', 'Initial [wah]āg and (a)zēr restorations, *kadagsbed and anonymous receiving subject stay uncertain; do not invent that subject.'),
'MP1027': ('H', 'Material whole-document discrepancies: source B9 line19 has 6 grīw but English has 5; B7 adds 4 grīw without a transcribed numeral; B8 omits Dēlānfarrox and Anagrān landholders; source final Yazdfarrox becomes Yazdānfarrox. The date formula is independently usable.', 'No replacement quantities or people are generated. Source TEI unclear/supplied spans, repeated property clauses and all original readings remain in held context.'),
'MP2500': ('H', 'The complete fragment leaves source line2 Yazdān-(?...) untranslated and contains unresolved (dād)//mard alternatives. Only the explicit information/barbar-man/King-of-Kings clause at lines3–4 is selected.', 'The selected fragment remains edition-bound; βάρβαρος is the English edition’s rendering of barbar and the source reading alternative must remain visible.'),
'MP0409': ('W', 'Aspbād supplies Farroxzād’s mother via her maidservant: 6 grīw wheat for Wahman/Spandarmad year33 and Frawardīn year34, sealed by Dādēnpanāh. Roles, multi-month span and amount agree.', '[ī xwarišn]/[as food], dōš(ār)am and bracketed conjunction/calendar explanations are retained.'),
'MP0047': ('F', 'Baxtiyār, Windādburzmihr-ābād, Ābān year48 and the order to give 1000 nuts as a gift correspond. Both preserve the following 26 with missing context and illegible ending.', 'The 26 is not assigned an invented commodity; property (jadag) remains an editorial reading.'),
'MP0048': ('W', 'Baxtiyār, manager of Windādburzmihr-ābād, gives 30 dōlag vinegar to the Chief Rad in Wahman year48; Āzarmīgduxt seals. Every transaction anchor and the distinct sealer match.', 'Keep bun and Rad as source-specific technical vocabulary; calendar gloss remains editorial.'),
'MP5651': ('W', 'The five-line note names Rēšbādag, the worker of Mihrbādārag, striking and giving 30 drahm in the same sequence.', 'Preserve the parenthesized ī and terse source syntax; do not add a cause, recipient or penalty interpretation to the 30 drahm.'),
'MP0437': ('F', 'The named accounts and rates correspond. Source line2 satēr-30 plus the next-line 1 forms the translated 31; 39+56+31=126. Tāzgird totals43 stater2 drahm; Grāmag includes the separate superscript2 drahm; Mihrābād and Rašnūg survive with the damaged end.', 'Preserve superscript [drahm2], tentative (D)axmagestān and gaps. The line break through 31 must not be treated as a numeral disagreement.'),
'MP0046': ('F', 'The damaged estate receipt retains Šahrewar year48, 6 kabīz garmak, 1 grīw4 kabīz for the ōstāndār, a single receipt, negated further demand, Mihrpanāh and Zādanfarrox witness seals.', 'Keep smudge gaps, supplied place name, tentative numbers/year and the distinction between principal signer and witness. S23 repeats a title glyph from this witness, not a separate attestation.'),
'MP1026': ('H', 'The body combines uncertain zanīh(?), a difficult Sazā/Xwāst-Dēlān family relation and unsettled reference/agency in the inquiry. The English does not expose all these uncertainties locally. Qualify only the explicit addressee/date opening and separate sender endorsement; retain the legal body for further reconciliation.', 'No inference that the English translator is wrong from the bibliography. This is a specific unresolved scope/participant problem in the available paired text.'),
'MP0071': ('H', 'Source lines4–8 have no translation: the target explicitly says no coherent translation possible. Source/target lines1–3 are a defensible fragment naming Xwarin, Tīr year48, Rašnīg, 3 grīw and the mosque.', 'The unknown commodity and torn material must stay unknown; the English editorial statement is not a translation target.'),
'MP0407': ('W', 'Aspbād’s Day year34 payment gives salt worth1 grīw barley to Pērōz ī Nēwbēhagān for the ōstāndār’s bath expenses; Farroxyān seals. Commodity versus valuation commodity and recipient are kept distinct.', 'The bath reading is starred in English; retain that uncertainty and the source technical title.'),
'MP0405': ('W', 'Xusrōyān’s mother receives New-Year clothing for year37 from Dēnabzūd: garment, pair of shoes, pair of trousers, and1 man cotton for a shirt; she seals the acknowledgement.', 'Retain the first-person aside and distinction between pairs and raw cotton. S23 only repeats the Dēnabzūd name glyph here.'),
'MP0024': ('W', 'Xwarin’s wife supplies the mother of Xusrōyān’s Mihrīgān allocation via her maidservant in Mihr year48:2 man cheese,5 kabīz garmak,500 nuts,5 dōlag wine; Frāy seals. Parties and quantities match.', 'Cottage cheese and beans are marked edition interpretations; preserve asterisks. S23 explicitly supports ī-š in this witness but is not a second independent receipt.'),
'MP0412': ('W', 'Aspbād, Day year34, Farroxzād’s mother requesting for the rāstār,5 pails vinegar to her maidservant and Dēnabzānīd sealing match as a whole receipt.', 'English *butcher remains tentative. S23 cites the rāy glyph, not a new full passage.'),
'MP0076': ('H', 'The first face ends wahāg... but English says and....; the damaged amount/commodity relation cannot be treated as a complete paired text. Select the explicit first five lines and preserve the distinct reverse horse-ration entry separately.', 'Do not infer the lost worth or flatten two faces into one transaction.'),
'MP1023': ('W', 'Dādēnbōxt address and greeting, the fire/fallow-land matter, request involving Pērōzōhrmazd and Farroxgušnasp,10 grīw land/seed allocation and command correspond. The body’s year103 and closing Day/year102/Den date both occur in the source and target; they are not silently reconciled.', 'Retain warzīd(?)n and *fallow land, seed interpretation in parentheses, the duplicated [the scribe] editorial token, and the separate Kurrag sender endorsement.'),
'MP0003': ('H', 'The useful provisioning clause is followed by source tar-[, which the English omits while supplying sealed. Qualify the clause ending dād/is to give and the separate rāst/Correct endorsement, not the complete closing.', 'Keep the published date conversion and kitchen interpretation as editorial; the broken closing is not repaired.'),
'MP2100': ('H', 'The full damaged letter has incomplete clauses, a fit/gift-looking English defect and unresolved pronouns. Its well-being/health/fortune greeting at lines4–6 is a matching fragment without those body defects.', 'Keep farrox[īh], missing words and plural addressee; no proposed repairs to the rest of the letter.'),
'MP5652': ('F', 'Both faces are retained separately: first includes month/wine/giving/Nōgdād/male sheep; second has40 rams, meat/sheep,1 pig,1.5 xwaran wine,40 barley grains(?) and Ardwahišt date/giving. These anchors match within each face.', 'Starred readings on the source side remain required uncertainty context even where the English omits a star. Unknown date/recipients remain gaps.'),
'MP6003': ('F', 'Wahrām’s address, storekeeper role, Ōz/Gandar interpretation, named recipients Wahrām/Mazdag/Wirgbad/Aštādag, five Razišt subdivisions, Kawād bringing the čak and requested consideration correspond.', 'Source unclear elements within the address/name, target uncertain names and *Razišt remain in the paired representation; explanatory consent is parenthetical.'),
'MP0410': ('W', 'Dēnabzūd and Bāragān’s separate allocations,34 cattle, cash2 staters,8 grīw wheat and price schedule,4 dōlag oil, total5 staters,12 man wool,3.5 man hair,4 man horse-tail hair and2 dāng for the consultant correspond.', 'Preserve the prior-contract reference: this passage is not a standalone complete contract. Restored as<p>-dumbag and fiscal interpretations are edition annotations.'),
'MP0147': ('W', 'Ōhrmazdabzūd’s New-Year year35 instruction and exceptions,2.5 man cheese,500 nuts,10 dōlag wine for Yazdānpanāh’s mother through her maidservant and ōstāndār sealing align.', 'Keep *household and *cottage cheese* interpretations plus line cross-references; do not collapse organizer, recipient and sealer.'),
'MP0406': ('W', 'Friyag of Namēwar, Ardwahišt year3(9),3 grīw barley to Dādēn responsible for ambaragān, and Zādānfarrox sealing correspond.', 'The partial year3(9) and English *poultry remain tentative. Duplicate English line6 labels are layout evidence, not two sealing acts.'),
'MP0067': ('H', 'The recto source lists190,50,50,50 grīw whereas English has190,50,50; additional damaged line14 matter is not translated. Isolate the complete one-sheep/out-of36-lambs entry and the verso endorsement; hold the recto account as a whole.', 'S25 reproduces the27 numeral from recto line12, creating a witness overlap, not an independent numeric observation.'),
'MP0085': ('W', 'Dādēnwindād of Yazdān-ābestān, Wahman year40/day Māh,6 donkeys from Namēwar/Dalīgān toward Paywēr,6 kabīz barley to their drivers and ōstāndār sealing correspond.', 'The ninth-station and bringing readings remain questioned in both layers; no certain itinerary is inferred.'),
'MP2561': ('H', 'The opening has two unclear words and ēd but English collapses it. Lines2–4 independently preserve the value condition, request to write via hutuxšān and final interrupted collecting clause.', 'Scribes is the edition’s interpretation of hutuxšān; retain the broken ending and uncertainty, do not generalize it as a dictionary gloss.'),
'MP0416': ('F', 'Dādēnwindād supplies Yazdānpādār’s trained horse for one month starting Spandarmad/Mihr:12 grīw barley,150 bundles lucerne,1.5 measure straw via Yazdānpādār’s boys; Yazdānpādār seals.', 'The year is lost, from-day restored and trained marked tentative; target Spandaimad is a visible spelling artifact, not a different calendar date.'),
'MP2150': ('F', 'The surviving document/organization/knowledge/Bābilōn/shortage/prior-action fragment has corresponding English scope.', 'Retain dān[istan čē] and incomplete syntax; Old Cairo is an explicit explanatory geographic gloss, not extra translated source content.'),
'MP0044': ('F', 'The memorandum about ōstāndār resources, cheques/receipts, Baxtiyār and the estate, year48 and Māhpērōz remains a matching damaged passage.', 'Many words are supplied and surviving clauses incomplete. Preserve supplied/gap spans in context, including gumārdag, rather than presenting it as intact prose.'),
'MP0439': ('H', 'English adds4 kabīz for the Arabian horse although the transcription has kabīz without a numeral at line7. The number may be inferred from totals, but this is an unmarked restoration. Qualify the explicit dated ration heading through day Xwar; hold the amounts pending the edition/manuscript.', 'Do not replace the absent numeral using the10-day totals. Tentative final consignment is also retained only in held context.'),
'MP0435': ('H', 'The source opens garmak gift, but the English lacks an explicit counterpart to gift before its explanatory beans/harvest construction. The whole account requires checking; the final ōstāndār sealing-the-tie clause is explicit and independently paired.', 'Retain starred beans/harvest and damaged/uncertain source ēstēd; no invented receive verb is added.'),
'MP0093': ('F', 'Mardōy receives30 drahm from Māhpērōz for three months from [Tīr] year49 until Mihrīgān and seals with Dādfarrox son of Dādōy’s witness seals. Amount and distinct participants agree.', 'Beginning/date lacunae and restored month stay visible. Dirham/drahm is orthographic target terminology, not a different amount.'),
'IEDC1266': ('F', 'Only Windād[ag] and nān/bread survive as matching content within the same damaged recto. Qualify as a sparse authentic fragment, never as a complete ration order.', 'Restored name ending and extensive ellipses must accompany it; it has no recoverable quantity or command.'),
'IEDC1267': ('F', 'Windādag, day Day [pad] Mihr, bread measured in restored kabīz, servants and give correspond across the six-source-line/one-target-item passage.', 'Quantity and accompanying persons are lost; preserve k[abīz], [pad] and ellipses.'),
'IEDC1268': ('F', 'Windādag, Day pad Dēn, bread and give correspond; to the servant is explicitly questioned/restored.', 'Keep both recipient question marks and r[ahīg] restoration; do not settle singular identity or quantity.'),
'IEDC1269': ('F', 'Windādag, day Ādur,4[?] kabīz bread to servants of an unknown group and give correspond.', 'Quantity4 and restored measure remain uncertain; no missing group supplied.'),
'IEDC1270': ('F', 'Recto: Windādag, day [Anag]rān[?],1 kabīz bread, a man[?], and give match. Verso contains only ellipses and has a separate hold.', 'Restored day/measure and questioned recipient remain explicit. Empty verso is not supervision.'),
'IEDC1262': ('F', 'Windādag’s damaged bread-giving clause to ra[hīg][?] has an English counterpart of matching scope.', 'English does not repeat the recipient question mark; source-side uncertainty is mandatory context. Neither recipient identity nor missing quantity is inferred.'),
'IEDC1263': ('H', 'The English ends Mihr…v but the transcription ends Mihr… dah. This unexplained terminal v could contaminate the recipient; the current target is held unchanged until the edition resolves it.', 'No automatic citation-to-translator accusation and no silent character deletion. The rest of the passage appears associated but does not resolve this target defect.'),
'IEDC1264': ('F', 'Windādag, day Mihr,5 kabīz bread and the imperative give match; the receiving group is lost.', 'Preserve restored measure and ellipses; no group name supplied.'),
'IEDC1265': ('F', 'Recto: Windādag, Spandarmad,2 kabīz bread, competing hungry-one/for-food readings and Burzādur. Verso: work, day Amurdād, grain. Each face has its own corresponding English passage.', 'Keep both alternatives, questions on the reading/name, restored measure, and the verso [For?] expansion; do not choose a winning sense.'),
'IEDC1062': ('W', 'Spandarmad year31/Day pad Ādur tax account: wheat38 stēr3 dirham, lentils5 stēr, alfalfa1 stēr1 dirham, total45 stēr and receipt sealing correspond.1-grīw/1-dirham and30-bundle/1-dirham schedules match.', 'Retain kulān[?],30[gerd][?], ba-aband[?], inserted ^wizārd^ and all English uncertainty.45 is a stated total, not our new correction.'),
'IEDC1040': ('W', 'Hordad year42/day Ādur, the frašn-hargarīg of Paywēšagestān, journey with the ōstāndār, Dēn-abzānēd/Xwadāgerd explanatory clause,2 pēlag from Dēn-abzūd’s dar and witness sealing correspond as a whole passage despite reordered lines.', 'The source pēlag[?] uncertainty remains mandatory context; technical offices are retained, not guessed. Translation line numbering is not used as alignment proof.'),
}
assert set(REVIEWS) == {p['work_identity']['document_id'] for p in packets}

OVERLAPS = {
'MP0032': ['S23 PDF21/printed22 and PDF23/printed24: xar3 comparison; PDF25/printed26: ōstāndār glyph. Same Berk.32 witness, not a new attestation.'],
'MP0405': ['S23 PDF12/printed13: Dēnabzūd name comparison from Berlin5 line3.'],
'MP0408': ['S23 PDF12/printed13: Dēnabzūd name comparison from Berlin8 line7.'],
'MP0412': ['S23 PDF17/printed18: rāy comparison from Berlin12 line5.'],
'MP0024': ['S23 PDF20–21/printed21–22: support for Berk.24 line12 ī-š reading.'],
'MP0046': ['S23 PDF25/printed26: ōstāndār glyph comparison attributed to Berk.43C.'],
'MP0067': ['S25 PDF9/printed7:27 numeral reproduction from Berk.62 line12.'],
}

def ws(s): return ' '.join(s.split())

def visible(e):
    tag=e.tag.rsplit('}',1)[-1]
    body=(e.text or '')+''.join(visible(c)+(c.tail or '') for c in e)
    if tag in ('gap','unclear','supplied'):
        attrs=' '.join(f'{k}={v!r}' for k,v in e.attrib.items())
        return f'⟦{tag} {attrs}⟧{body}⟦/{tag}⟧'
    return body

def xml_parts(layer):
    xml=layer['original_layer']['xml']; blocks=[]
    for a in re.finditer(r'<ns0:ab\b([^>]*)>(.*?)</ns0:ab>',xml,re.S):
        aid=re.search(r'xml:id="([^"]+)"',a[1]).group(1)
        lbs=list(re.finditer(r'<ns0:lb\b[^>]*/>',a[2]))
        lines=[]
        for i,lb in enumerate(lbs):
            raw=a[2][lb.end():lbs[i+1].start() if i+1<len(lbs) else len(a[2])]
            label=re.search(r'\bn="([^"]+)"',lb[0]).group(1)
            e=ET.fromstring(f'<root xmlns:ns0="{NS}">{raw}</root>')
            lines.append({'label':label,'raw_xml_fragment':raw,'raw_fragment_sha256':sha(raw.encode()),'text':ws(''.join(e.itertext())),'text_with_uncertainty_markup':ws(visible(e))})
        blocks.append({'block_id':aid,'raw_xml':a[0],'lines':lines})
    assert blocks
    return blocks

class Items(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.rows=[];self.current=None;self.number=0
    def handle_starttag(self,tag,attrs):
        if tag=='li':
            a=dict(attrs);self.number=int(a.get('value',self.number+1));self.current={'label':str(self.number),'html_attributes':a,'text':''};self.rows.append(self.current)
    def handle_data(self,d):
        if self.current is not None:self.current['text']+=d
    def handle_endtag(self,tag):
        if tag=='li':self.current=None

def html_parts(raw,side):
    h=Items();h.feed(raw)
    for x in h.rows:x['text']=ws(x['text'])
    return [{'block_id':side,'raw_html':raw,'lines':h.rows}]

def selected(blocks,block=0,labels=None,start=None,end=None):
    b=blocks[block]; lines=b['lines'] if labels is None else [x for x in b['lines'] if x['label'] in labels]
    assert lines
    text=' '.join(x.get('text_with_uncertainty_markup',x['text']) for x in lines)
    locator={'block_id':b['block_id'],'labels':[x['label'] for x in lines]}
    if start is not None:
        assert text.count(start)==1,(b['block_id'],start)
        text=text[text.index(start):];locator['start_exact']=start
    if end is not None:
        assert text.count(end)==1,(b['block_id'],end)
        text=text[:text.index(end)];locator['end_exclusive_exact']=end
    return {'scope':locator,'text':text.strip(),'context_lines':lines}

units=[]
def emit(p,disposition,s,t,note,uncertainty,suffix,scope='document'):
    i=p['work_identity']['document_id']
    units.append({'schema_version':1,'unit_id':p['candidate_id']+':'+suffix,'candidate_id':p['candidate_id'],'disposition':{'W':'QUALIFIED_WHOLE_PASSAGE','F':'QUALIFIED_FRAGMENT','H':'HELD'}[disposition],'evidence_type':'authentic_documentary_annotated_edition_translation','grain':scope,'source_language':'pal','target_language':'en','source':s,'target':t,'manual_review':{'reviewer':'/root/seen20_blind_b','method':'individual source/English semantic scope review; participants, action/negation, quantities/dates, explanations, restorations and gaps','finding':note,'uncertainty_and_editorial_context':uncertainty,'independent_review':'PENDING_ROOT_CRITIC','claim_limit':'Edition-bound source correspondence, not independent manuscript decipherment or guaranteed error-free translation.'},'provenance':{'packet_path':str(INPUT.relative_to(ROOT)).replace('\\','/'),'packet_sha256':EXPECTED,'packet_line_one_based':packets.index(p)+1,'raw_source':p['raw_source'],'archive_record_pointer':p['archive_record_pointer'],'work_identity':p['work_identity'],'edition':p['edition'],'credits_verbatim':p['credits_verbatim'],'translator_attribution':p['translator']},'split_and_overlap':{'heldout_screen':p['heldout_screen'],'witness_group':p['work_identity']['witness_group'],'existing_book_overlaps':OVERLAPS.get(i,[]),'cross_archive_metadata_matches':p.get('cross_archive_metadata_matches',[]),'counting_rule':'All units and alternate editions of this physical witness share one group; fragments are not additional independent attestations.'},'use_scope':{'train_admitted':False,'qualification_is_content_evidence':disposition!='H','training_authorization':'No training authorized in this phase. Root owns canonical release and independent review.','required_context':'Keep source/target uncertainty, alternatives, gaps, original selected context and editorial additions together; English stays English.','rights_original':p.get('rights_verbatim',p.get('rights'))}})

for p in packets:
    i=p['work_identity']['document_id']; d,n,u=REVIEWS[i]
    if p['archive_family']=='berkeley-openampd':
        s=xml_parts(p['source_layer']);t=xml_parts(p['target_layer'])
        emit(p,d,{'blocks':s,'raw_xpath':p['source_layer']['raw_xpath']},{'blocks':t,'raw_xpath':p['target_layer']['raw_xpath']},n,u,'full')
        # Explicit manually selected salvage scopes; never selected by a rating loop.
        if i in ('MP1027','MP1029'):
            se=' ka ';te=', when ' if i=='MP1027' else ' when '
            # The date formula itself ends immediately before the following when-clause.
            emit(p,'F',selected(s,labels=['1','2','3'],end=se),selected(t,labels=['1','2','3','3-4'],end=te),'Matched dateline: month, year, Yazdgird/Xusrō/Ōhrmazd royal genealogy and named day; body disputes excluded.',u,'dateline','subpassage')
        elif i=='MP2500':emit(p,'F',selected(s,labels=['3','4']),selected(t,labels=['3','4']),'Information came about a barbar-man whom the King of Kings is to make his slave; these two lines carry the corresponding English clause.',u,'lines3-4','subpassage')
        elif i=='MP1026':
            emit(p,'F',selected(s,labels=['1','2'],end='◯'),selected(t,labels=['1','2'],end='◯'),'Address to the archive keeper and elder in *Asp-gurd, followed by day Ardwahišt, independently corresponds.',u,'address','subpassage')
            emit(p,'F',selected(s,block=1),selected(t,block=1),'Separate sender endorsement az Dādborzmihr / From Dādborzmihr corresponds; retained as a short contextual fragment, not a full letter.',u,'sender','endorsement')
        elif i=='MP0071':emit(p,'F',selected(s,labels=['1','2','3']),selected(t,labels=['1','2','3']),n,u,'lines1-3','subpassage')
        elif i=='MP0076':
            emit(p,'F',selected(s,labels=['1','2','3','4','5']),selected(t,labels=['1','2','3','4','5']),'Dādēnwindād, Day pad Mihr,2 kabīz barley for the black-legged horse and give align; no lost value is supplied.',u,'front-lines1-5','subpassage')
            emit(p,'F',selected(s,block=1),selected(t,block=1),'Distinct reverse entry: Farroxzād’s horse, day Mihr, binding allocation of2 kabīz correspond. Commodity is not invented.',u,'reverse','face')
        elif i=='MP0003':
            emit(p,'F',selected(s,labels=[str(x) for x in range(1,14)]),selected(t,end='[14–15]'),'Dādēn, Hordād year49, promised provisions except those already given,1 pail juice, herbs/cumin and kitchen stock shortage align through the giving clause.',u,'provision-clause','subpassage')
            emit(p,'F',selected(s,block=1),selected(t,block=1),'Separate validation endorsement rāst / Correct corresponds.',u,'endorsement','endorsement')
        elif i=='MP2100':emit(p,'F',selected(s,labels=['4','5','6']),selected(t,labels=['4','5','6']),'Greeting wishing well-being, health and all fortune to the plural addressee, followed by health/peace fragment; damaged words remain gaps.',u,'greeting','subpassage')
        elif i=='MP0067':
            emit(p,'F',selected(s,labels=['6']),selected(t,labels=['6']),'From Friyag, one sheep out of36 lambs: actor, item, unit count and comparison group agree without the omitted-grain problem.',u,'recto-line6','subpassage')
            emit(p,'F',selected(s,block=1),selected(t,block=1),'Verso endorsement: outgoing bath-house expense, Hordād year38, matches; bath-house remains the starred edition reading.',u,'verso','face')
        elif i=='MP2561':emit(p,'F',selected(s,labels=['2','3','4']),selected(t,labels=['2','3–4']),n,u,'lines2-4','subpassage')
        elif i=='MP0439':emit(p,'F',selected(s,labels=['1','2','3','4','5','6'],end='harw rōz'),selected(t,labels=['1','2','3','4','5','6'],end='for each day'),'Friyag of Namēwar, Hordād year37, Mihr-ayār-Gušnasp’s mounts and ten-day period from Ōhrmazd to Xwar correspond. The untranscribed daily4 is outside this unit.',u,'ration-heading','subpassage')
        elif i=='MP0435':emit(p,'F',selected(s,labels=['7']),selected(t,labels=['7']),'The ōstāndār sealed the tie of this ayādgār/memoir: agent, object and action explicitly correspond.',u,'seal-clause','subpassage')
    else:
        for f in p['document_folios']:
            idx=f['folio_index'];o=f['original_folio'];sd=html_parts(o['transcription'],f['side']);td=html_parts(o['translation'],f['side'])
            dd='H' if i=='IEDC1270' and idx==1 else d
            nn='Only ellipses survive on the verso; no translated lexical content exists.' if dd=='H' and i=='IEDC1270' else n
            emit(p,dd,{'blocks':sd,'json_pointer':f['source_json_pointer']},{'blocks':td,'json_pointer':f['target_json_pointer']},nn,u,'folio'+str(idx),'folio')

assert {x['candidate_id'] for x in units} == {p['candidate_id'] for p in packets}
assert len({x['unit_id'] for x in units})==len(units)
# Verify all original raw files; no target/test-answer content is consulted.
for p in packets:
    assert sha((ROOT/p['raw_source']['path']).read_bytes()) == p['raw_source']['sha256']
# Source-only duplication check against the immutable qualified TRAIN source field.
train_path=ROOT/'experiments/train-audit-20260927/qualified-v1/train.jsonl'
norm=lambda s:ws(unicodedata.normalize('NFC',s)).casefold()
train_sources=[norm(json.loads(l)['text']) for l in train_path.read_text(encoding='utf-8').splitlines()]
def unit_text(x):
    if 'text' in x:return re.sub(r'⟦[^⟧]*⟧','',x['text'])
    return ' '.join(l['text'] for b in x['blocks'] for l in b['lines'])
for row in units:
    s=norm(unit_text(row['source']))
    matches=[j+1 for j,t in enumerate(train_sources) if s==t]
    long_containment=[j+1 for j,t in enumerate(train_sources) if len(s.split())>=6 and (s in t or t in s) and len(t.split())>=6]
    row['split_and_overlap']['train_source_screen']={'train_source_path':str(train_path.relative_to(ROOT)).replace('\\','/'),'train_file_sha256':sha(train_path.read_bytes()),'comparison':'NFC+whitespace+casefold; source strings only; complete equality and >=6-word complete-unit containment','exact_row_matches':matches,'containment_row_matches':long_containment,'limit':'Not a universal fuzzy, formula or quotation audit; no held-out answer text read.'}
    if matches or long_containment:
        row['split_and_overlap']['duplicate_status']='REQUIRES_CANONICAL_GROUPING'

counts=Counter(x['disposition'] for x in units)
payload=''.join(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n' for x in units).encode('utf-8')
dest=OUT/'archive-alignment.jsonl';report=OUT/'ARCHIVE-ALIGNMENT.md'
repair = len(sys.argv)==3 and sys.argv[1]=='--repair-known-output'
if repair:
    assert sha(dest.read_bytes())==sys.argv[2], 'Refusing repair: reviewed output changed.'
else:
    assert not dest.exists() and not report.exists(), 'Refusing overwrite; root must reconcile existing outputs.'
summary=f'''# Archive passage qualification

53 previously frozen source packets were individually read in full, including all source and English layers, edition metadata, restorations, gaps, quantities, participants and explanatory additions. Output has {len(units)} review units: {counts['QUALIFIED_WHOLE_PASSAGE']} qualified whole passages, {counts['QUALIFIED_FRAGMENT']} qualified fragments and {counts['HELD']} held contexts. These are units, not independent-witness counts. Qualified means bounded correspondence with the published annotated edition; it does not mean guaranteed correctness or a new translation. Root/independent critic owns final release. No training occurred or is authorized here.

## Representation and lineage

- All53 packets have an explicit disposition. Whole passages are kept whole where meaningful; equal line numbers never establish alignment by themselves. Source/target grouping is based on manually checked transaction, clause, date, people and quantity scope.
- Berkeley TEI ab boundaries, original XML fragments, supplied/unclear/gap elements and line metadata survive. Readable text carries explicit uncertainty markup, including originally empty gap elements. Oxford folios, exact HTML, list value/range attributes, alternatives and source JSON pointers survive. Two faces are not collapsed into a fabricated continuous text.
- The source and English are unchanged except whitespace in derived display strings; original XML/HTML and frozen packet pointers retain exact evidence. No translation was generated. English commentary such as month numbers, modern place explanations, grammatical line references and technical interpretations remains identifiable edition context. The task is annotated edition translation, not bare Persian gold.
- Unknown separate translation bylines do not automatically make a translation wrong. Exact scholarly edition/TEI/editor credits are retained without relabeling editors as translators. OpenAMPD itself is the traceable online edition. Abbreviated bibliography IDs remain exactly as archived; Asefi2023a is independently named in S23 PDF25/printed26 as A New Middle Persian Document from Hastijan belonging to the Farroxzād Family, Berkeley Working Papers1(3),1–14. Other unresolved titles were not invented.
- A sparse fragment such as IEDC1266 is counted as a fragment, with no complete proposition claimed; two short sender/validation endorsements likewise remain separately labeled. Empty IEDC1270 verso is held.

## Material holds and salvage

| Witness | Full-context issue | Independently selected usable scope |
|---|---|---|
| Tab.24 / MP1027 |6 versus5 grīw; added4; missing Dēlānfarrox/Anagrān landholders; Yazdfarrox/Yazdānfarrox name mismatch |Dateline before when-clause |
| Tab.25 / MP1029 |Inconsistent pondik wanīh rendering; unexplained quotaNote token |Dateline before when-clause |
| P.Weill / MP2500 |Untranslated Yazdān remnant and unresolved reading alternatives |Information/King-of-Kings clause, lines3–4, with alternatives |
| Tab.22bis / MP1026 |Unresolved marriage/family reference and inquiry agency; source uncertainty not localized in English |Address/day opening and separate sender endorsement |
| Berk.66 / MP0071 |English explicitly says no coherent translation possible for lines4–8 |Lines1–3 only |
| Berk.71 / MP0076 |wahāg versus English and at damaged ending |Front lines1–5 and distinct reverse entry |
| Berk.3 / MP0003 |Untranslated tar-[ and supplied sealed in closing |Provision clause through dād; separate Correct endorsement |
| P.44 / MP2100 |Damaged letter, unresolved pronouns and fit/gift-looking target defect |Greeting lines4–6 |
| Berk.62 / MP0067 |One50-grīw entry omitted; damaged line14 not translated |One sheep/out-of36 lambs entry; verso endorsement |
| P.Pehl.562 / MP2561 |Unrendered opening remnant and collapsed unclear words |Lines2–4 |
| Berlin38 / MP0439 |English supplies4 kabīz absent from transcription |Dated ration heading through day Xwar |
| Berlin34 / MP0435 |No explicit counterpart to source gift in opening construction |Final sealing clause |
| IEDC1263 |Unexplained terminal v in English Mihr…v |Held unchanged; no invented fix |
| IEDC1270 verso |Only ellipses |None |

Berlin36 is not a30/31 discrepancy: the source numeral31 straddles lines2–3. Its superscript2 drahm is preserved. Tab.20's year103 versus closing102 is already present on both sides and is retained as source evidence, not silently corrected.

## Held-out and overlap checks

All16 work-family exclusions from the frozen packet were retained:103,104,110,111,112,114,116,117,118,120,124,130,132,138,152,517. These documentary witness identities differ from the protected literary/Manichaean families; no held-out answers were read. This is not certification of every shared formula. Source-only comparison against qualified TRAIN used exact normalized equality and whole-unit containment with at least6 words; findings are recorded per unit. Root still groups all editions/fragments by witness before independent release review.

S23 and S25 were checked locally rather than assumed disjoint from their principal titles. S23's main Berk.25/Berlin26/Berk.11/Berk.122 editions do not enter these53 packets, but its comparison material overlaps Berk.32, Berlin5, Berlin8, Berlin12, Berk.24 and Berk.43C. S25's principal TB and Berk.129+212 texts are distinct, but PDF9/printed7 reproduces the27 numeral from Berk.62. These are shared glyph/word contexts, not additional independent attestations. Exact per-witness page locators are in JSONL. S23 PDF21/printed22 and PDF25/printed26 plus S25 PDF9/printed7 were rendered and visually checked; bounded additional citation pages were read via embedded text. No alternative edition was inferred solely from a mismatching citation year.

## Verification receipt

- Frozen input: `{EXPECTED}`.
- Output JSONL SHA256: `{sha(payload)}`.
- Replay script SHA256: `{sha(Path(__file__).read_bytes())}`.
- S23 SHA256:480670343730bdac72d1af78ff699d8cca69d71b908472a890c9ea1f51c6a1ce.
- S25 SHA256:2ac4c431f8ed4c0123ac147675e9c7ad6b0904435d22e1f848d5d9b3434857d2.
- Input/raw hashes rechecked; all53 covered; unique unit IDs; manually specified substring endpoints asserted; outputs written exclusively and read back. No originals, prior packets, test answers or other durable outputs modified.
- Rights remain exactly as in source packets; semantic qualification is not a blanket redistribution or training authorization. Independent critic review is pending and can narrow a scope on concrete evidence.

## Per-unit ledger

|Unit|Disposition|Grain|
|---|---|---|
'''
summary+='\n'.join(f"|{r['unit_id']}|{r['disposition']}|{r['grain']}|" for r in units)+'\n'
with dest.open('wb' if repair else 'xb') as f:f.write(payload)
assert [json.loads(l) for l in dest.read_text(encoding='utf-8').splitlines()]==units
with report.open('w' if repair else 'x',encoding='utf-8',newline='\n') as f:f.write(summary)
print(json.dumps({'packets':53,'units':len(units),'counts':counts,'qualified_witnesses':len({r['candidate_id'] for r in units if r['disposition']!='HELD'}),'train_source_duplicate_units':sum(bool(r['split_and_overlap']['train_source_screen']['exact_row_matches'] or r['split_and_overlap']['train_source_screen']['containment_row_matches']) for r in units),'jsonl_sha256':sha(payload),'report_sha256':sha(report.read_bytes()),'script_sha256':sha(Path(__file__).read_bytes())},indent=2))
