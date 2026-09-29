# Consolidated source coverage before the next training

28 September 2026. **A source-qualified release is now frozen; overall literature/source coverage remains partial.** This consolidates inspected families and unresolved work, not exhaustive world literature coverage or permission to start training. Root integrates; independent source reviewers and the final critic checked the declared release. No new cloud job, model download or paid acquisition.

The latest [qualified release](experiments/data-qualification-20260928/README.md) supersedes earlier dispositions below only for its named scopes:2,676 Persian lexical inventories;3,506 CPD and1,426 MMP English inventories/blocks;240 S22 teaching units;57 archive English spans;6 Kanheri Persian occurrences (4 pair types);4 S23 English scopes. All888 newly extracted S22 glossary groups stay reference-only because protected-reading lineage is unresolved. Remaining held parents, dictionary scopes and other resources remain unqualified. [New-source work](experiments/data-qualification-20260928/NEW-SOURCES.md) found the exact Nasrollahzadeh volume and acquired the earlier Kanheri and Pasargadae articles; the paid book remains unavailable locally. Independent saved-output verification passed; no training started. Earlier tables retain their snapshot counts and explain the wider unresolved source queue.

## What the counts mean

The later [reviewed expansion checkpoint](experiments/dataset-expansion-20260928/README.md) supplements this inventory:31,918 lexical/reference resource records including5,541 recovered observations;113 additional S22 teaching/morphology records;53 documentary MP–English associations after7 explicit holds;4 Parsig format-recovery packets. These are saved, source-bound outputs at separate grains, not additions to the historical2,237 trained pairs. Its README records exact remaining extraction, source-page and alignment work. Earlier counts below describe their original inventory snapshots.

The [unified local catalogue](data/unified-corpus/README.md) now binds these families and later additions in one place. Its49,504 rows have explicit grains and dispositions; only the unchanged2,237 historical pairs are exported as the provisional control. PahGen's317-pair count below is external research evidence, not a verified local dataset.

Additional local material now explicitly indexed:5 published contextual glosses,15 directive annotations and8 contrast annotations (all auxiliary development only); the406-form/1,135-occurrence Parsig vocabulary index (not a sense dictionary);16 authored dictionary drafts stored in one artifact,11 concerning held-out work120; and the separate7 S22 teaching pairs. These overlap earlier source texts and must not inflate independent passage counts. The later authorized annotation-detail capture verifies an existing gloss, not a sixth one. ParsiPy files and overlapping Ezafe feature views remain support artifacts rather than translation labels.

- Historical qualified control:2237 Persian pairs /76 works. The earlier audited serialized set was2484, with247 quarantines:243 linguistic and4 held-out formula cases. The original2613 allocation differs because of earlier filtering; do not call all376 a single new recovery pool.
- Separate unadmitted Parsig pool:277 records with Persian fields, outside the16 frozen held-out work families. Their first rejection reasons are110 source-edition,79 mixed/possible Avestan,45 work139 identity,28 attribution/no usable published pair,13 shared targets and2 encoding. A populated target is not a qualified pair.
- The additional62 untranslated Parsig records are short question headings,260 whitespace terms, not a substantial untranslated corpus.
- Dictionaries, parallel sentences, source-only text and grammar/annotation evidence have separate counts. Orthographic variants and repeated formulas do not create independent attestations. Token counts require the eventually selected tokenizer.

Evidence: [Parsig inventory](experiments/dev-assisted-qualified-20260927/UNLABELED-DATA-INVENTORY.md), [277-record first-rejection join](experiments/composition-evidence-20260928/provenance-recovery.json), [qualification audit](experiments/train-audit-20260927/), [source manifest](sources/manifest.json).

## Current Persian and lexical candidates

| Source | Current disposition | Exact remaining action |
|---|---|---|
| Parsig qualified2237 | Historical control; not new data | Preserve bytes, provenance and existing uncertainty. |
| Parsig277 unadmitted | Recoverable possibilities, not277 promised additions | Resolve each actual first rejection and downstream quality gates; no broad parser relaxation. |
| Inscription works201–224 / Nasrollahzadeh1398 vol.1 |95 source-edition failures;91 have explicit Nasrollahzadeh credit in target fields | Check printed source transcription and translation against exact locators. Four other targets have only notes naming the source and describe uncertain names or severe damage; do not infer definite labels. Work205 pp.208/213 and work222 pp.141–162 are concrete access priorities. |
| Work151 / Tafazzoli1379, Anklesaria1913 |16 missing target credits; some formulas, some longer clauses | Recover exact translator/page per row. Notes for151035029 and151039009 explicitly say their sentences are absent from Tafazzoli pp.51/54: do not assign that translator by inheritance. |
| Manichaean535/537/546 target-credit gaps |11 rows with actual Persian wording but no per-row credit | Archived introductions are placeholder strings, not attribution evidence. Nearby rows' credit does not establish these rows' authorship. Preserve fragment boundaries and uncertain readings. |
| Other source-edition failures |11 code-like headings plus4 running-text cases |134008007 has a truncated reference;137002020 a doubled closing parenthesis and a forthcoming-source citation;510000002 a stray final Armenian mark after an otherwise visible Boyce citation;512000004 no source citation. Resolve individually, retain originals. |
| Separate247 quarantines |Already rejected, not an unseen new corpus |Only new source evidence can reopen linguistic cases. The4 held-out formula exclusions remain excluded. |
| S22 Amouzgar–Tafazzoli Persian primer |7 image-verified pedagogical pairs staged; no corpus admission |Complete coverage of relevant examples and distinguish constructed pedagogy from manuscript quotations. Resolve lineage/use scope and linguistic review. Do not start training for this packet alone. |
| MacKenzie / Kosh CPD and print scans |English/Persian PDFs acquired; parallel bounded edition/page review completed. Normal Chrome search and two entry-family cross-checks worked after earlier direct403 |Complete image-verified main-entry extraction, preserve ordered senses and corrections; Persian is image-only and English OCR is imperfect. Treat website/PDF as shared lineage. No complete lexicon or training admission established. |
| All Kosh dictionaries |Integrated final v4 preserves all38,686 catalogue records across30 nonempty collections plus GPV0, including AWN190 once. All34,539 v3 records are unchanged. Every original JSON field and XML survives; catalogue metadata is a provenance hint, not per-entry truth. This covers Kosh catalogue counts, not every MPCorpus product |[Local curation](experiments/kosh-quality-20260928/README.md) stages26,377 form/meaning groups and retains every original field. Missing/ambiguous/language-risk/held-out-related entries stay separate. No complete export or training admission is claimed. |
| Legacy Cologne CPD |4218 original records, separate from current CPD; pinned source declares CC BY-NC-SA3.0 |All remain preserved in local quarantine until legacy transcription encoding and edition equivalence are established. Do not count the same dictionary twice as independent new meanings. |
| S24 Nyberg ManualII |English lexical/grammar reference; most entries unread, OCR noisy |Use source images and preserve multiple senses, cited contexts and transcription system. Do not assign one flattened gloss to every form. |
| S26 Persian-wrapper Nyberg |Same English work with reverse PDF body order |Use only as an image reference. It is not a separate Persian translation or independent data. |
| Skjærvø Primer2020 |Author-linked English teaching text accessible; targeted entries checked |Qualify full relevant examples, glyphs, locators, permission scope and quoted held-out works. Earlier blanket “unavailable” statements are superseded. |
| S28 Asha, Xusrō and a Page |Held-out work117; Persian mediated through Arabic, different structure |Exclude training and retrieval even through an alternate edition. |

The exact Nasrollahzadeh book sought is **کتیبه‌های خصوصی فارسی میانه ساسانی و پساساسانی (گورنوشته، یادبودی)**, volume1, Cyrus Nasrollahzadeh,1398/2019. Exact printed pages have not been inspected. Possessing a book would resolve access, not automatically translation or training qualification.

## Additional authentic material and institutional sources

An English, German or French translation can be considered for a **separately labeled auxiliary task** if provenance, alignment and split checks pass. Lack of Persian alone does not make that evidence useless. It cannot be silently relabeled as Persian gold. Whether auxiliary training helps our fixed Persian merit remains a prospective hypothesis, not an observed benefit.

| Source family; covered works | Current disposition | Missing condition / action |
|---|---|---|
| S23 Asefi2025; Berk.25, Berlin26, Berk.11, Berk.122 |Authentic MP/English documentary clauses; CC BY-NC4.0 notice recorded |Separate edition alternatives, reconstructed text, manuscript overlap and known numeral/unit ambiguities. Berk.25 PDF8/printed9 is a concrete participant/obligation passage. |
| S25 Asefi–Farridnejad2026, three Fārs documents |MP/English excerpts, not complete editions of all10 witnesses; CC BY-NC-ND4.0 notice recorded |Resolve intended derived-use scope, source/date/reading disagreements and actual aligned coverage. |
| Berkeley OpenAMPD |152 documents;46 with nonempty MP transcription and English layers |Verify exact passage/editor/translator and cross-archive shelfmark duplicates; metadata association alone is insufficient. |
| Oxford Invisible East |158 records;14 with transcription and English |Reconcile archived items with the identified CC BY4.0 release and Berkeley overlaps. No repeated recollection of already archived records. |
| PahGen Parsig–English |Existing report counts317 distinct released pairs, versus360 in paper |Resolve underlying editions, translator, release scope and overlaps with all frozen partitions. Do not count related Parsig records as new attestations. |
| TITUS DenkardIV |Completed structural probe:111 pages,196 spans,4665 source whitespace terms |Retain actual counts, not10484 raw-page terms. Qualify quotations/lineage and recover corresponding translation from the exact Razāyī1393 edition if available. |
| TITUS Arda, DenkardV–VII, Pahlavi Rivayat |Additional source transcription candidates |Arda edition incomplete; Dk5 book5/book7 metadata contradiction; Dk6 parallel counsels and Rivayat constituent identities unresolved. Dk7 cites Rashed-Mohassel1381. Need matching targets. |
| TITUS MHD and Psalter |Legal/Psalter transliteration, not interchangeable with current transcription |Establish scholarly reading and target alignment. English KJV is not a translation from the MP Psalter. |
| Other TITUS: andoshn, bundahis, dadden, kap, mx, zwy, purs, yvrpt, oavpt, yavpt, vdp, vd-19p, jamasp, mpt, mirmankb, manreadc, sermseel |Source-side MP, quoted Avestan, mixed MP/Parthian and editorial text |Use existing per-root inventory, constituent identities and quotation screening. Menog/Karnamag overlap TRAIN; dadden/work139 identity unresolved; mixed collections may contain held-out517. |
| TITUS snstrl/snstrs, zadspram |Held-out138/152 |Exclude including alternative witnesses and source-only learning. |
| Avesta.org Bundahishn/Greater Bundahishn, DkIII/V/VI/VIII/IX, Epistles of Manuščihr |English translations; notices differ (`dk5.pdf` explicitly CC BY4.0) |Find exact matching source witnesses, align, review and deduplicate. Not direct Persian data. |
| Avesta.org Zadspram |Held-out152 |Exclude. |
| Avesta.org Menasce1945 SGV; Asha SGV also at PersoAryan |French/English, Pazand textual history; Asha copies are exact duplicates |Separate mediated/reconstructed layers, inspect poor extraction and count the duplicate once. |
| Masani Pazand Afrins; Pazand/Avesta Nirangs |147+333 scanned pages, not extracted MP pairs |Lower priority than existing Persian candidates; would require OCR, language and edition qualification. |
| PersoAryan Medicine for Contentment; Coming of Vahrām Varzāvand |MP/English, likely counterparts ofParsig119/101 |Compare editions/reading rather than claim independent new contexts. |
| PersoAryan Blessings, Āfrīn ī myazd, Āfrīn ī rōzān, Zand ī gāhān |MP with English editorial material; complete translation coverage unproved |Identify liturgical parallels and actual aligned targets. |
| PersoAryan Ēvēnnāmag passages, Quality of Scribes, Reflections of Persian Sages |Arabic-mediated and English scholarly material |Separate an extant MP witness from modern reconstruction; no ancient-attestation claim for the latter. |
| PersoAryan Colophons of Mihrābān, Marriage Contracts, Jāmāspīg, Vīrāzagān |Potential contexts; MP/Pazand and other languages; partly overlapping witnesses |Separate languages, mapParsig115/Ardā Virāz relations and identify actual target coverage. |
| PersoAryan Dēn ī vizīrgird; Avesta Vocabulary/Grammar |New-Persian-influenced MP; Avestan/MP lexical and grammar material |Preserve language/status labels, missing-page and Unicode-repair evidence; not automatically classical-MP clause supervision. |
| PersoAryan Sūr/HKR |Held-out112/117 |Exclude, including alternate titles. |
| MPCD corpus, UD and ezafe views |Preliminary annotation/working translations; local UD snapshot has0 CoNLL-U files |No complete corpus acquired. Ezafe23234/8468-row views repeat token identifiers and lack stable sentence IDs; establish provenance joins before using labels. Kosh has separate access history. |
| BBAW MIRTEXT, MP German reader, Psalter comparison |MP/Parthian sources;23-page German reader; multilingual Psalter comparison |Separate languages/witnesses/use scope. German reader is potential auxiliary evidence; KJV English is not MP gold. |
| MUYA, CAB, Digital Turfan Archive |Primarily Avestan/liturgical editions and manuscript infrastructure |Identify an actual obtainable MP layer and matching translation. Collection/image totals are not training-pair counts. |

Authoritative detail: [all archived source groups](experiments/lexical-feasibility-20260927/ADDITIONAL-SOURCE-INVENTORY.md), [completed TITUS follow-up](experiments/lexical-feasibility-20260927/SOURCE-DECISION.md), [institutional annotation limits](experiments/lexical-feasibility-20260927/EXTERNAL-ANNOTATION-ELIGIBILITY.md), [supplied-book study](kb/supplied-pdf-study.md), [local data holdings](data/README.md).

## Interpretation references, not a hidden parallel corpus

S1–S17 Iranica, University of Texas, ASPIRANTUM and UD guidance; S3 Oxford handbook preview; S12 Unicode proposal; S18/S20 ParsiPy paper/data; S27 Jügel2015; Skjærvø2009; Durkin-Meisterernst2004/2014 are accounted for in [kb/sources.md](kb/sources.md) and the [book access note](experiments/lexical-feasibility-20260927/BOOK-ACCESS-FOLLOWUP.md). Their roles include orthography, grammar, representation, lexicon and attribution. Most do not supply Persian parallel passages; several full books remain unread/unavailable. Software licenses do not establish rights or provenance for every upstream data table. Project-authored KB explanations are not published translation gold.

## Next concrete completion work

1. Preserve the detailed Parsig recovery triage and obtain the specifically identified editions/pages, prioritizing direct Persian whole-clause material.
2. Complete S22 example coverage and MacKenzie lexical extraction/qualification now that reading access is established; retain incomplete coverage rather than claiming dictionary inclusion.
3. Qualify the strongest available authentic non-Persian parallel material as separately labeled auxiliary candidates, without inventing Persian targets or absorbing held-out works.
4. Publish actual admitted counts, exclusions, provenance and task balance, then freeze the full dataset and select one justified model/method comparison under [DATASET-READINESS.md](DATASET-READINESS.md).

The current table records dispositions and remaining work; it does not satisfy the final readiness gate. No source-dependent paid run is admitted.

Lead agent/request id: /root
Critic agent/request id: /root/finetuning_kb_research
Critic model and reasoning effort: inherited GPT-6 Astra and parent reasoning effort
Independent from lead: yes
Critic verdict: pass
Evidence reviewed: Consolidated source-family dispositions against the existing inventories; candidate/admitted distinctions, held-out rules and separately labeled non-Persian auxiliary potential.
Verification evidence: The critic found no substantive inaccuracies. Newly inspected source-credit details were checked for consistency with root's report, not independently re-examined. Later PDF acquisition and Chrome observations are root's separate receipts; /root/seen20_blind_a and /root/seen20_blind_b completed bounded independent English/Persian PDF checks recorded in the MacKenzie access README.
