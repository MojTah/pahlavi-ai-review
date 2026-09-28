# Batch 6 corpus reading report

RESULT: PASS for the assigned shard-reading task. All 612 assigned units in all 51 chunks were read, including every supplied transcription, Persian translation, additional translation/commentary layer, and note. These are partial record shards: this report does not assert whole-record completion outside its assigned IDs. Whole-record aggregation belongs to the lead.

Reading started 2026-09-24T04:09:03Z. The final source-reading call completed before the 2026-09-24T04:14:27Z coverage checkpoint. Exact report completion and elapsed time are recorded in coverage.json. Expected/warning/hard limits were 25/35/45 minutes. No time threshold was reached. One metadata-printing encoding failure was repaired once by setting Python stdout to UTF-8; this did not affect reading coverage.

## Evidence and limits

I read the actual source contents through sequential bounded tool outputs of two or three chunks, with a 14,000-token maximum per call. No source-chunk output was truncated. The initial full assignment display was truncated; it was metadata only, and was subsequently loaded mechanically for coverage validation. IDs/counts were generated only after reading, to record and verify coverage, not to stand in for reading. Progress was saved at 10, 20, 30, 40, and 51 chunks (the last output included chunks 49–51 together). The manual 30-chunk tally of 441 in one progress note was corrected to 442 and independently counted. Exact cumulative counts are 133, 268, 442, 547, 603, and 612 at chunks 10, 20, 30, 40, 50, and 51.

The source export was verified at SHA-256 `c42e0a5a0d4d108218a0481ca073c07c6bb00cdcba0bffb462b67bb6d7a60789`, matching assignment.json. The original per-unit provenance was recovered by ID from `sources/local/parsig-2026-09-20/exports/text-units.jsonl`; source URLs/hashes and rights are retained in coverage.json. Only local supplied material was consulted. There was no manuscript or inscription-image inspection, independent edition verification, or live research. This is source-assisted study, not certification of independent translation accuracy, manuscript fluency, or complete knowledge.

## Per-record and section understanding

| Record | Assigned sections | Reading summary |
|---|---|---|
|103, Ādurbād counsel|22–43;108–129|Prudence about debt, property, authority and confidants; restraints on lying and anger; work, moderation and religious calendar activities. Commands often take `ma` plus verb. The property passage has a real lacuna across116–117.|
|104, Wehzād Farrox Pērōz|0–14|Wisdom governs action and protects body/soul; personal responsibility coexists with acceptance of destiny. Persian imperative renderings and Tafazzoli's descriptive clauses differ in1–5. English13–14 covers two units as one sentence.|
|111, Priestly counsel|18–35|Ritual utensils, protection of souls in hell, measured punishment, charity and corpse-related food restrictions. Questions and answers remain separately attributed. The material is historical religious law.|
|112, Sūr saxwan|0–17|A banquet blessing moves through divine/cosmic powers, king and officers, then host and household prosperity. Preserve the repeated `hamāg-zōhr` invocation and optative blessings.|
|116, Pōryōtkēšān counsel|59–60|Only the concluding arrangement/teaching statement and completion formula are assigned; no inference about the rest of the text.|
|117, Khusraw and page|0–13;72–88|The page describes genealogy, education, writing, riding, polo and music. The later shard compares floral scents with persons, relationships and social qualities. French is a translation layer, not English.|
|121, Thirty-day text|1–2|Bahman and Ardwahisht day prescriptions concern counsel, learning, affection, healing and religious work.|
|122, Wonders of Sistan|15–17|Survival and restoration of religious knowledge through women/children, followed by a requested rite and colophon. Book-name and speaker/beneficiary interpretations disagree.|
|123, Cities of Iran|42–56|City foundations attached to royal and legendary figures; patronymics and place-name readings require restraint. The supplied English of55 contains an apparent imported continuation from50.|
|130, Frawardin/Hordad|0–15;30–42|The same calendrical date gathers creation, royal legends, future saviours, resurrection and the ending of evil. Past legend and future prophecy should not be flattened into one tense.|
|133, Wuzurgmihr|39–58;249–266|Spiritual/mental faculties have distinct functions: innate and learned wisdom, disposition, hope, contentment, religion, consultation. Terse comparative questions close with blessing and colophon.|
|134, Zand Wahman Yasn|5.4–6.4;7.2–13|Religious endurance under future oppression, restoration, celestial signs and royal saviours. Alternate commentators, manuscript variants, and editorial additions are explicit, not one consistent geography.|
|136, Kārnāmag|2.10–24;6.4–9;7.1–7|Ardashir's hunting success and royal dispute lead to stable service; later raids and the Worm-lord conflict. Attribution of action and proper-name versus geographical readings affect the narrative.|
|137, Bundahišn|2.25 only|A forward reference promising an individual description of natures. The surrounding cosmology is not assigned here.|
|138, Šāyest nāšāyest|3.19–35;4.1–14;5.1–6|Purity conditions, permitted ritual dress, thresholds of liability, meal-prayer and initiation. Different rulings and an author's explicit uncertainty remain visible.|
|139, Dādestān ī dēnīg|43.12–14;44.1–8;45.1–5|Support of religious teachers; reciprocal king/priest guardianship; teacher and pupil as relational roles; livelihood through teaching and ritual service. Several additional layers are Persian editorial commentary.|
|150, Ošnar|42–52|Moral restraint, peace, speech, anger and generosity; questions about existence, deception, merit and wholesome/immortal nourishment. Some source editions allocate the short answers very differently.|
|151, Mēnōg ī xrad|0.45–61;1.0–3,26–48;20.25–21.2;54.6–56.10;60.4–61.14|Wisdom's proem and practical counsel; criticism of laziness, suspicion and contempt; mountains/seas and innate wisdom; rads of beings; opening mythic-geography questions. Restorations from Pāzand and unresolved words are marked.|
|152, Zādspram|3.51–60;8.12–9.1;10.18–11.8;20.3–21.9;26.1–27.7;34.42–51;35.7–16,39–47|Animal classifications, Zoroaster's birth and family conflict, revelation, priestly virtues, cosmological renovation, judgement and compassion. Taxonomic levels, numbers, agency and doctrinal analogies must remain distinct.|
|201, Kanheri|inscriptions1,2,3,5,6|Visitor lists, dated arrivals and names. Patronymic chains require care; year378/376 mismatch is present in inscription1.|
|205, Darband|inscriptions19–32|Building formulae and officials' names; rival readings of Mošīg/plaster/stone, regional accountant/patronymic, damaged fragments. Repetition is source repetition, not independent corroboration.|
|218, Eqlid|inscription1|Tomb commission, death and deposition dates, and payment/endowment. The supplied complete narrative contains restorations and interpreted titles.|
|220, Zirab|inscriptions1–2|A blessing for the dead and an enclosure/building inscription; initial word and Farrox-zād/Farrox-dād are disputed.|
|221, Firuzabad|inscription1|Very short damaged daughter/commission formula. Missing owner and construction wording cannot be reconstructed confidently.|
|301, Zand Yasna|1.12–23;2.1–2;4.22–25;5.1–6;6.1–4|Ritual announcement/completion, libations, barsom, invocations, penitential and confessional wording, and explanatory glosses. Braces visibly separate interpretive clauses.|
|505, ar|1–5|Mixed Middle Persian/Parthian eschatological petition: persecuted elect ask about final signs and reversal of fortunes.|
|513, t|1–2|Middle Persian exhortation to pursue divine wisdom amid worldly occupations and avoid passion/violence; care for beings of divine light. The text is incomplete at both ends.|
|543, dgb|1–5|Middle Persian hymn invoking religious guardians, Jesus, Mani and divine powers for protection and peace. Manichaean context controls shared divine vocabulary.|
|545, dh|1–8|Fragmentary mountains/tower allegory: hypocrites, wealthy people, divided minds, resistant learners, talkers and generous believers. Eighth mountain has only an incomplete label.|
|555, du|1–4|Fragmentary apostolic invocation, supplication, religion as a bride, and the saviour's hand; syntax of3 explicitly remains uncertain.|
|556, dv|1–9|Mixed Middle Persian/Parthian hymns use new/full moon and new year imagery with appeals to Jesus and Mani; repeated invocations and vocatives are structural.|

## Fifteen translation insights grounded in the reading

1. **Negative commands and purpose clauses must stay connected.** `ma ... kū-t ... nē` commonly joins a prohibition with its intended protection, e.g.103000113–114 and151001033–041. A unit boundary can interrupt that syntax.
2. **Enclitic pronouns can encode agents, possessors or beneficiaries.** The apparatus for152008018 explicitly contrasts these analyses of `-š`;152010020 changes who hides or fails to reach whom. Do not infer a pronoun's function from its position alone.
3. **`ī` is not an automatic English “of.”** In201/123 it frequently participates in filiation, but205024001–205029001 contrasts a regional office with a proposed patronymic. These require different translations.
4. **Infinitives and impersonal necessity have instructional force.** `abāyēd ...`, forms in `-išn`, and `šāyēd/nē šāyēd` distinguish duty, permission and possibility in138/139. Modern Persian “باید/جایز است/می‌توان” should follow the specific function.
5. **Preserve blessing modality.** `bawād`, `dahād`, `padīrād` in112 and epitaph220001001 are wishes, not assertions that the blessings occurred.
6. **Comparatives need context rather than a fixed superlative.**133's repeated `-tar` clauses compare capacities or values;134's `škoft/škeft` concerns severity/distress, and cannot always be translated with modern Persian شگفت in its common “wonderful/strange” sense.
7. **Homographs and cognates invite false confidence.** `bōy` in117's floral analogies means scent, while133000056 uses it for a cognitive faculty. `gōhr`, `xwāstag`, `āzād`, `dastwar` similarly require genre-specific decisions.
8. **Learn/teach and voice are substantive translation choices.**139044002–004 makes teacher/pupil roles relational;130000030 and152027003 show translation disagreements involving instruction, acquisition and passive morphology.
9. **Quoted rulings remain plural.** `ast kē ...` and `būd kē ...` in138 and134 introduce alternative authorities.138005004 openly leaves the calculation basis unknown; a smooth single-rule paraphrase would remove evidence.
10. **Zand layers must remain layered.**301's braces, `kū/hād` explanations and alternate interpretations are not all a continuous original Avestan utterance. Prayer names and embedded Avestan wording, such as `ašəm` in122000017 and formulas in138, should be flagged separately.
11. **Edition marks carry meaning.** Asterisks, square brackets, angle brackets, question marks and ellipses recur throughout.134007008's K20 addition,151's Pāzand supplements and152009000's disputed name must survive a working translation apparatus.
12. **Numerals require side-by-side checking.**201001001 reads378 versus Persian376;152003055 has1000 versus French10000;152021008's90 is editorially uncertain. Apparent precision is not proof of a secure reading.
13. **Units are not reliable sentence or translation-span boundaries.**104000013–014 repeats one English rendering for a two-unit phrase;103000116–117 straddles a lacuna;123000055 likely imports English material from another unit. Translate with adjacent context and retain original unit IDs.
14. **Do not impose modern taxonomy on traditional categories.**152003053–060 distinguishes several classification levels and includes aquatic “cattle,” wild/free-ranging animals, and named subgroups. A fluent modern zoological label may erase the text's categories.
15. **Language and religious context can change within a batch.**117/136/152 carry French translations despite `EnTranslation` provenance labels;139/220/301/513 carry Persian commentary there.505/556 explicitly combine Middle Persian and Parthian; `bōž`, `zirδān`, `žīrīft`, vocative `-ā`, and `kādūš` need separate handling. Divine names shared with Zoroastrian texts do not erase the Manichaean setting.

## High-priority uncertain/problem units

These are unresolved source-assisted findings, not corrections to the corpus. The detailed reading ledger below preserves further exact IDs and their issues.

| Exact ID(s) | Issue affecting later translation |
|---|---|
|parsig:103000116; parsig:103000117|Lacuna and cross-unit continuation.|
|parsig:104000013; parsig:104000014|Same combined English13–14 sentence appears in both units.|
|parsig:117000007|Legal `stūr`: page as successor/heir versus father's curator.|
|parsig:117000012|Polo wording has multiple edited/uncertain readings and different final imagery.|
|parsig:117000072|Transcription/Persian lacuna versus French “sons(?)”.|
|parsig:122000015; parsig:122000016|Nask name and statement-versus-request interpretation differ.|
|parsig:123000055|English adds a long Simran/Arab-land passage matching123000050, absent local transcription/Persian. Likely alignment/copy contamination; verify original edition before reuse.|
|parsig:130000011|`kand`: digging ossuaries in Persian versus razing them in English.|
|parsig:130000030|Saviour name and learn/teach agency differ.|
|parsig:134005004; parsig:134005008; parsig:134005009|yašt-āb/yašt-wāz; panj/gyāg; diadem/oppressive sovereignty alternatives.|
|parsig:134007006|The date may attach to the saviour's birth or father's death.|
|parsig:134007011|Persian makes enemies the victims of killing; English makes them the killers.|
|parsig:136007002; parsig:136007003; parsig:136007004|Obedience/Kerman, sent/came, and person/place interpretations.|
|parsig:138004001; parsig:138004006; parsig:138004011|Textile, lining/garment and knot/rent readings substantially differ.|
|parsig:138005004|The author explicitly does not know whether liability is per meal, mouthful or tasting.|
|parsig:150000044; parsig:150000046|Hope/religion and assignment of soul/body/deception/nonexistence differ.|
|parsig:151060007|`wmyhkwn` is unresolved; the note questions an earlier reading.|
|parsig:152003055|1000 transcription/Persian versus10000 French.|
|parsig:152008018; parsig:152008019|Speaker, agent and statement of religious authority are disputed.|
|parsig:152009000; parsig:152009001|Personal/group-name readings remain highly uncertain.|
|parsig:152021008; parsig:152021009|Editorially uncertain90, then feet versus steps.|
|parsig:152034048|At age30 in Persian versus for30 years in French.|
|parsig:152034051|Air versus deserts; moon-like light versus brown/blue coloration.|
|parsig:152035009|Ardwahisht as first recipient versus Medyomah praising Ardwahisht.|
|parsig:201001001|378 transcription versus376 Persian; no date resolution made.|
|parsig:205030001; parsig:205032001; parsig:221001001|Damaged epigraphic fragments and disputed names.|
|parsig:301006002|One Persian editorial note occurs in both additional layer and notes; not two independent sources.|
|parsig:545000001; parsig:545000003; parsig:545000004; parsig:545000005; parsig:545000006; parsig:545000008; parsig:555000003|Fragmentary allegorical/hymnic passages; do not fill missing text from expectations.|

## Three short provisional original renderings

These are my own concise working renderings after reading the supplied editions and translations, not independent philological validation.

- **parsig:103000037**, `kas-iz rāy drō ma gōw`: «به خاطر هیچ‌کس دروغ نگو.» / “Do not lie for anyone's sake.” `rāy` expresses the beneficiary or reason.
- **parsig:104000008**, the first clause `xrad dāštār [ud] pānāg ī gyān`: «خرد، نگاهبان و پشتیبان جان است.» / “Wisdom guards and sustains the soul.” The conjunction is editorially supplied; “soul” remains context-sensitive alongside `tan` in the second clause.
- **parsig:556000008**, `baγ mār mānī, man-ā ruwān bōž`: «ای بغ، ای سرور مانی، روان مرا رهایی بخش.» / “Divine lord Mani, deliver my soul.” This comes from the explicitly mixed Middle Persian/Parthian record; I do not reclassify it as purely Middle Persian.

## Source credits

The local Parsig corpus snapshot supplies all transcriptions, translations and apparatus consulted here. Its per-unit rights statement is: “Parsig attribution-required research use; underlying edition rights retained.” Credit remains with Parsig and the underlying scholars; this reading report does not establish new rights or replace their editions. Source URLs, local response files, retrieval times and response hashes are recorded in coverage.json.

- 103,104,111,112,116,117,121,122,123,130,133: Jamasp-Asana1913 transcription citations; Persian گشتاسب و حاجی‌پور1398. Additional translations: Tafazzoli1972(104), Tarapore1933(116), Azarnouche2013 French(117), Asha n.d.(122,123), Grenet2009(130).
- 134: Anklesaria1957, راشدمحصل1370, Cereti1995; apparatus distinguishes DH/K20 and editorial choices.
- 136: Anklesaria1935, فره‌وشی1378, Grenet2003 French.
- 137: Hajipour1400 “forthcoming” as recorded, بهار1380, Agostini and Thrope2020. “Forthcoming” is source metadata, not a verified current publication status.
- 138: Persian مزداپور1369 and Tavadia1930 English. The assigned transcription strings do not supply an inline edition credit; I do not invent one.
- 139: Anklesaria1958, میرفخرایی1397, and the corpus's Persian editorial commentary.
- 150: Dhabhar1930, گشتاسب و حاجی‌پور1392/1393 as the units themselves differ.
- 151: Anklesaria1913 and تفضلی1379; notes additionally discuss Pāzand, manuscript readings and MacKenzie1984.
- 152: Anklesaria1964, راشدمحصل1385, Gignoux and Tafazzoli1993 French; apparatus includes other scholarly proposals with their own attribution.
- 201,205,218,220,221: نصراله‌زاده1398, volume1; rival epigraphic readings are credited in the source notes.
- 301: Dhabhar1949, حصارپولادی و مصطفوی کاشانی1400; note citations include Cantera2004 and a Dhabhar/Darmesteter comparison.
- 505,513,543,545,555,556: Boyce1975 transcription selections and مصطفوی کاشانی1401 Persian.

## Detailed reading ledger

The following contemporaneous notes retain lower-priority uncertainties and section-specific observations. Their statements remain provisional; numeric corrections above and in coverage.json supersede the early manual tally.
# Batch 6 actual reading progress
Start UTC: 2026-09-24T04:09:03Z. Read chunks 001–010 in full, all fields, no source-chunk output truncation; 133 units.
001–002: record103 advice22–43 and108–129, negative imperatives ma, property/debt and prudent social relations, virtue/reward, moderation, snake/swimming warnings, calendar-day duties. Problems103000032 syntax,103000039 čašm-āgāh,103000113 edited *mīrē,103000116–117 lacuna across units.
003: record104 wisdom discourse0–14. Persian commands versus Tafazzoli descriptive relative clauses1–5; 104000000 wisdom/mēnōg segmentation,104000007 lacuna,104000009 strength/wealth ambiguity;104000013–014 one English clause duplicated across units. Sources Jamasp-Asana1913; Goshtasb/Hajipour1398; Tafazzoli1972.
004: record111 catechism18–35; toothpick ritual, divine oversight of hell protects souls from annihilation, proportionate punishment, charity, carrion and three-night mourning pollution.111000018–019 abar-sar unresolved;111000025 eschatological consequence needs caution.
005: record112 Sur Saxwan0–17; litany hamāg-zōhr, cosmic/divine hierarchy then king/officers then host and prosperity.112000005 restorations,112000012 east/west/south titles; blessing optatives preserve modality. Same JA/GH sources.
006: record116 closing59–60, wisdom/cosmic arrangement and colophon; Tarapore1933 English differs nōg-dādārīh good creation vs new creation; no independent resolution.
007–008: record117 Khusraw/page0–13,72–88; aristocratic education, scribal/martial/musical prowess; floral scent analogies. French Azarnouche2013 is French despite source field EnTranslation.117000004 benefactors gods/ancestors vs nobility;117000007 stūr legal curatorship vs page as substitute-heir;117000009 yašt vs Yasna;117000012 polo obscure edited words and different conclusions;117000072 lacuna vs fils(?),117000077–078 plant ID tentative,117000087 sick people vs diseases. Keep scent metaphors figurative.
009: record121 calendar1–2; Bahman consultation/love/learning, Ardwahisht healing and ritual duties.010: record122 Sistan15–17; textual preservation by women/children and closing prayer.122000015 nask name differs Dva.yasna vs duzd-sar-nizad;122000016 statement vs beneficiary prayer disagreement;122000017 final Avestan ašəm switch, not ordinary MP noun.
Next chunk011.

Chunks011–020 read fully; cumulative268 units/20chunks. No source-output truncation. 
011 record123 cities42–56: repetitive foundation formula šahrestān…kard with patronymics;123000045 Humay descent vs noble birth;123000048 place-name readings differ;123000051–052 names heavily uncertain;123000055 English incorrectly includes long text matching123000050 after short city-foundation clause—alignment contamination candidate. Asha n.d. English.
012–013 record130 Frawardin/Hordad0–15,30–42: festival mythic creation/kings then eschatological renewal.130000008 Persian awkwardly reverses mount relation, English makes Ahriman mount;130000011 kand dig vs raze ossuaries;130000030 Ošidar/Xwaršedar, learn vs teach/memorization agency;130000036 zanēd smite vs kill; resurrection ages40/15 conditioned on meat-eating. Grenet2009 English.
014–015 record13339–58,249–266: seven mental/spiritual supports and their functions, innate/acquired wisdom, contentment; comparative questions answered elliptically, ending blessing.133000046 cannot happen vs Farsi not lasting;133000056 bōy cognitive awareness distinct from floral smell117;133000258 lacuna;133000251 škeft not automatically modern شگفت.
016–017 record134 Zand Wahman5.4–6.4,7.2–13: future religious distress/restoration, prognostics and rival geographical commentaries. Source Anklesaria1957,Rashed-Mohassel1370,Cereti1995. Critical apparatus actually read:134005004 yašt-āb vs yašt-wāz;134005005/006 DH/K20;134005008 panj vs gyāg;134005009 diadem vs oppressive rule;134005011 Yenghehatam-derived Zand layers;134006004 English loses explicit moon;134007006 date birth vs father's death expressly unresolved;134007007 place readings;134007008 sentence K20 addition absent DH;134007009 war lake vs fort;134007011 Persian targets slain vs English enemies doing killing (major agency reversal);134007012 three battles but two named.
018–019 record136 Karnamag2.10–24,6.4–9,7.1–7: Ardashir hunting superiority/dispute, punished stable service; night raid then worm-lord conflict. Anklesaria1935;Farahvashi1378;Grenet2003 French.136002012 raw wwltk;136002018 sarīh/dilīh note;136006004 gašt vs dašt, one elder vs elders;136006008 undecided kym/kē-m/nūn;136007001 Worm lord vs place-name explanation;136007002 framān vs Kerman variants;136007003 hēnīh vs ēwīh and sent vs came editorial note;136007004 Ardashir person vs Ardashir-khwarrah place.
020 record137 Bundahishn2.25 forward-reference only: will discuss their natures separately. Hajipour1400 forthcoming transcription, Bahar1380 Farsi, Agostini/Thrope2020 English; no whole chapter claim.
Next chunk021.

Chunks021–030 read fully; cumulative441 units/30chunks. All fields and notes, no source-text truncation.
021–023 record138 Shāyest nāshāyest3.19–35,4.1–14,5.1–6: historical menstruation/purity law, thresholds and graded liabilities; ritual dress construction, sleeping prayer and meal-speech law; preserves alternate authorities Aparag/Medyomah. Mazdapur1369,Tavadia1930.138003022 pregnancy/miscarriage conditional parse materially differs;138003031 xwān ǰāmag tablecloth vs tray/cup;138004001 parwand/parand identity vs silk and nax thread vs low-status;138004006 gawr-mānāg(?) vs warm clothing plus negation uncertainty;138004011 fringe/end-knot vs rent/woman-knot disagreement;138005004 author explicitly does not know whether liability per meal/morsel/taste; no harmonization. Avestan prayer names138003035/138004014/138005002 remain distinct.
024 record139 Dadestan43.12–14,44.1–8,45.1–5: financial support for religious teachers, reciprocal king/priest bodily/spiritual guardianship; a person can teach juniors while learning from seniors; hērbed expertise in zand vs hāwišt Avestan memorization; livelihood via ritual work.139043012 Persian commentary mislabeled EnTranslation says religious friends;139044005 manuscript/editorial omitted duplicate phrase, ōstān vs harwispān;139045003 conjunction/interpretation proposal. Anklesaria1958,Mirfakhrayi1397; commentary layer Persian, not English.
025 record150 Ošnar42–52: moral conduct, terse Q/A, generosity and suppression of greed/wrath. Dhabhar1930;Goshtasb/Hajipour1392/1393 (date discrepancy retained).150000042 good deed/place vs fertile land;150000044 hope restored vs English religion/lacuna;150000046 soul/body/nonexistent/deception allocation and repentance negation differ;150000049 poor vs cannot impoverish store of good deeds;150000050 anōš immortality-food vs wholesome;150000051 segmentation of training/temperament;150000052 dstk(?) lacuna.
026–030 record151 Menog i Xrad:0.45–61+1.0–3 wisdom proem;1.26–48 practical religious counsel;20.25–44 condemn laziness/suspicion/contempt then21 opening;54.6+55–56 cosmological utility and wisdom;60.4–11 rads of beings;61.0–14 mythic geography questions. Anklesaria1913/Tafazzoli1379. Read Pāzand restorations notes151000045–047,151060004;151000056 editorial ēzišn/yazišn;151000059 Ašem-vohu explanation;151001034 K43 vs Pazand amahraspand/mārspand;151020025 anērīh gloss contextual enmity not simple ethnicity;151056004 syntactic alternate;151056008 āwāmīgān disagreement MacKenzie1984 vs Tafazzoli;151060007 wmyhkwn explicitly unresolved (earlier meh-kūn rejected). Zero-Farsi heading units are present and read, not skipped.
Next031.

Chunks031–040 read fully, all fields including long Persian apparatus; no truncation. Correction:30-chunk cumulative is442, not441; manual tally40chunks=547 pending mechanical coverage validation (count does not establish reading).
031–038 record152 Wizidagiha i Zadspram3.51–60;8.12–9.1;10.18–11.8;20.3–21.9;26.1–27.7;34.42–51;35.7–16,39–47. Cosmological taxonomy; Zoroaster birth/laughter and Akoman trick; adversarial priests/parents; revelation/river depth symbolism; priestly virtues and differentiated worship/care; demon hunger/escheatological defeat; resurrection ritual and sevenfold divine/human correspondence; judgement, grief, universal maternal mercy. Sources Anklesaria1964,Rashed-Mohassel1385,French Gignoux/Tafazzoli1993. Notes explicitly distinguish readings and proposed translations, not adopted facts.
Problems152003051 agrē highest/full parasang;152003052 ham-juxtihist vs ham-dosast/hamēnihist;152003053 taxonomic levels and KRHA pah heterogram note;1520030551000 MP/Farsi vs10000 French;152003057 missing gōkān in Farsi;152008016 tarsid/tarsist;152008017 authority vs directives;152008018 clitic agent/possessor;152008019 speaker and gōwēd/gōwēm editions;152009000–001 unread name xwarrah-kāstārān vs raw consonants;152010020 agency/passive problem;152011001 considers/fears versus suggested instruction not to listen;152020003 Arastay vs Medyomah as Porushasp brother;152021002 four depth-stages vs anatomical measure;15202100890 uncertain manuscript digits;152021009 feet vs steps;152026001 negative a-prefix;152027002 ethical kill/not-kill vs abstract destruction/survival;152027003 learn/teach voices;152027004 zahagān mothers/elements, kištan+ pazzāftan;152034042 ruzdagihā/rōzigihā;152034048 age30 vs duration30 French;152034049 6000-year/calendar drift numerals and uncertain celestial motion;152034051 air vs deserts and lunar brightness vs brown/blue;152035009 first convert Ardwahisht vs Medyomah;152035010 tōhmagtar/tahmagtar noble/brave;152035015 sarādagān kinds vs pavilions;152035040 demon āhr/xār/āl/anahr;152035042 Farsi omits ān dōst and weakens addressee agency. No resolutions manufactured.
039 record201 Kanheri inscriptions1,2,3,5,6: date-and-visitor formulas, names and genealogical ī.201001001378 transcription vs376 Persian;201003001 unread father name;201005001 šahryār potentially title/name rather than safely supplying filiation. Nasrollahzadeh1398vol1.
040 record205 Darband inscriptions19–32: repeated Mosig built vs Nyberg plaster/Lukonin stone readings; Adurbadagan accountant title vs patronymic, Darius/driyosh readings; fragment30; uncertain Rashn32. All repeated apparatus actually read; no manuscript inspection.
Next041.

Chunks041–051 read fully, all fields; reading completed2026-09-24T04:14Z (approx; exact completion stamped in coverage/report). No chunks skipped. All assigned source contents read via bounded outputs of2–3chunks; assignment display alone was truncated and was never used as evidence of textual reading.
041–043 inscriptions218 Eqlid death/deposition/endowment,220 Zirab epitaph/enclosure,221 Firuzabad damaged daughter/commission fragment. Names/official titles and reconstructed text require caution;220002001 abar/čē and Farroxzad/Farroxdad note read (Persian commentary, not English). Source Nasrollahzadeh1398.
044–045 record301 Zand Yasna1.12–23,2.1–2,4.22–25,5.1–6,6.1–4. Recurrent niwēyēnēm hangerdēnēm devotional performatives, libation/barsom, divine/time invocations, repentance, religious profession, glossed theological qualities. Braces separate Zand explanations from base translation. Dhabhar1949 with Hesarpuladi/Mostafavi Kashani1400; Cantera2004 noted for plural demonstrative+singular nouns301001016.301001017/301004022 ī-to-ud editorial corrections;301005001 dropped ī.301001015 Dhabhar/Darmesteter curse phrase alternatives;301006002 same Persian correction duplicated in additional layer and notes.301005006 parallels134005011 Yenghe Hatam interpretive rendering; no unmediated Avestan reading claim.
046 record505 ar mixed MiddlePersian/Parthian: petition about arrival/final age, righteous elect persecuted, role reversal and reward. Preserve stated mixed scope;505000005 explicitly uncertain strangers/brokenhearted reading.
047 record513 t MiddlePersian: worldly occupations contrasted with pursuit of divine knowledge; abstention from passions and violence, less harm to beings of divine light.513000001 čay- grief/care vs hygiene conjecture in Persian commentary,513000002 incomplete frame.
048 record543 dgb MiddlePersian: hymn to guardians/apostles, Kaphthinos/Jacob, Jesus and Mani, Father Zurwan, protection of eastern religion. Context Manichaean; same surface divine terms not automatically Zoroastrian referents.
049 record545 dh MiddlePersian: fragmentary mountain/tower allegory with stones accepted/rejected, hypocrites, rich, divided-minded, proud learners, talkers, generous believers.545000001,003–006,008 gaps real; eighth mountain only label, cannot fill allegory.
050 record555 du MiddlePersian: fragmentary apostle/angel invocation; remember petition, pure religion as king's bride and saviour's right hand, plea to guard religion.555000003 overt question mark/ellipsis prevents confident syntax.
051 record556 dv mixed MiddlePersian/Parthian: new/full moon and New Year hymns to Jesus, Mani and deities; vocative -ā, Parthian forms wxaš,zirδān, bōž, žīrīft; kādūš borrowed sacred acclamation retained.556000001 moon rises from NewParadise;556000004/006/009 fragmentary. All505/513/543/545/555/556 Boyce1975 transcription and Mostafavi Kashani1401 Persian. No additional English translation furnished in these chunks.
Next: produce report and exact coverage; all51 source chunks actually read.

