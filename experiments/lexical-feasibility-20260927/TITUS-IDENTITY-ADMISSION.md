# TITUS candidate identity and admission review — 2026-09-27

**Select the complete `dk4` root for a private local extraction study: `dk4001.htm` through `dk4111.htm`, 111 numbered pages /10,484 raw whitespace terms. No source in these eight roots is yet training-ready.** Denkard IV is the smallest presently tractable transcription collection after excluding Denkard V from the first pilot for a bibliographic contradiction. The smaller Psalter is fragmentary transliteration and does not match the current transcription objective.

This is a source-identity review, not corpus admission or a legal determination. Existing inventory counts were reused, not rebuilt. Scope: eight roots, 995 numbered pages /199,043 raw whitespace terms. Inspected their first-page editorial headers, index/word-index metadata, raw HTML representation tags, and qualified TRAIN work IDs. Reused prior source-only overlap results. No held-out reference answers or predictions were read; no external fetch, downloads, corpus edits or model execution occurred.

## Root decisions

Here **RETAIN** means retain for bounded research/extraction. **HOLD** means defer the root from the first pilot for the stated issue. Training admission remains HOLD for every root. None of these eight roots has a confirmed whole-work identity with an excluded work, but metadata cannot clear embedded quotations, reused passages or unknown witness relationships.

| Root and reused size | Decision | Identity, edition and electronic provenance | Representation and material qualification |
|---|---|---|---|
| `arda`:101 pages;21,236 terms | **RETAIN**, second candidate | Ardā Virāz Nāmag. Data entry P. Vavroušek, Prague1995; TITUS Jost Gippert, revisions1998–2008. Header says chapter/sentence references follow P. Gignoux; it does not give a complete edition citation. Footer10.12.2008. | First-page HTML uses `miphts16`; source sample is vocalized Middle Persian transcription. Need full base-edition identification and quotation/parallel screening before admission. |
| `dk4`:111;10,484 | **RETAIN**, first extraction study | Dēnkard Book IV; Maryam Razāyī, *Dīnkard čahārom*, Tehran1393. Electronic preparation Mark Hale, Concordia3.4.2020; TITUS Jost Gippert2.1.2021. Footer10.9.2023. | `miphts16` transcription spans. Many pages have a Chapter locator rather than Paragraph/Sentence; the old inventory heuristic therefore missed75 pages. Extract structural source spans, not its incomplete approximation. |
| `dk5`:24;10,186 | **HOLD: edition identity contradiction** | Work/Book metadata says Dēnkard V and Book5, but the bibliographic heading literally says “Dēnkard Book7” under Amouzgar-Taffazoli, Tehran: Institute for Humanities and Cultural Studies1381. Mark Hale4.8.2018; Gippert7.9.2019/9.1.2021; footer9.1.2021. | `miphts16`; technically extractable, but do not silently correct the citation or copy Book7 metadata. Resolve edition identity first. |
| `dk6`:613;58,970 | **HOLD: constituent parallels unresolved** | Shaul Shaked, *The Wisdom of Sasanian Sages (Denkard VI)*, Persian Heritage Series/Bibliotheca Persica34, Boulder: Westview1979. Mark Hale3.4.2020; Gippert2.1.2021; footer4.1.2021. | `miphts16`. Many short wisdom units, with the greatest direct genre-level reason to check against held-out counsel collections. This is a screening priority, not a finding that those works are actually duplicated. |
| `dk7`:12;20,420 | **RETAIN**, later transcription candidate | Mohammad Taghi Rashed-Mohassel, *Dēnkard Book7*, Tehran: Institute for Humanities and Cultural Studies1381. Electronic preparation Ibrāhīm Šafiʿī, Tehran2016; Gippert19.11.2017/2.1.2021; footer10.9.2023. | Predominantly `miphts16` on inspected header page, which also has other language/style spans. Twelve pages contain long sections, not twelve tiny units. Passage-language and quotation review remains necessary. |
| `mhd`:42;40,411 | **HOLD: different representation** | M. Macuch, *Rechtskasuistik und Gerichtspraxis zu Beginn des siebenten Jahrhunderts in Iran. Die Rechtssammlung des Farroḫmard i Wahrāmān*, Wiesbaden1993, Iranica I. Electronic preparation Maria Macuch/Claudius Naumann, Berlin1993; TITUS Gippert with Thomas Jügel corrections,2002/2008/2010; footer9.1.2021. | Explicitly **transliterated text**; `miphtl16` and variant/note spans. Header says spelling was adapted to MacKenzie's dictionary conventions and original-script remarks were omitted/replaced by a symbol. Do not convert this mechanically into phonetic transcription or present it as untouched manuscript text. |
| `psalter`:27;4,894 | **HOLD: fragmentary transliteration** | Original manuscripts collated with F.C. Andreas/K. Barr, *Bruchstücke einer Pahlavi-Übersetzung der Psalmen*, Berlin Academy proceedings1933,pp91–152. Electronic editor Thomas Jügel, Frankfurt2008; TITUS Gippert7.8.2010/31.12.2020; footer16.11.2021. | Word index explicitly says `ChrMiddlePersian-trl.`; body spans use `ispstl16`. Source-only sample psalt002 has heterograms and numerous gaps/restorations. Smallest file collection, but not the smallest suitable transcription pilot. |
| `pahlriv`:65;32,442 | **HOLD: collection/parallel identity** | Mahšīd Mīrfaxrāyī, *Rivāyat-ī pahlavī*, Tehran1390. Electronic preparation Ibrāhīm Šafiʿī/M. Taghi Asl, Tehran2.3.2018; TITUS Gippert2.1.2021; footer10.9.2023. | `miphts16`. Do not equate the generic title with every separately named Rivayat, or clear overlaps with religious compilations by title alone. Needs explicit edition/constituent-work mapping. |

Iranian publication years are preserved as printed; this review does not guess Gregorian publication dates. Header revision dates and footer dates differ in several roots; preserve both. Index language menus in most roots offer Avestan, Pahlavi transliteration/transcription, Pazand and Modern Persian. These reusable menus are **not evidence that every listed language occurs in each text**. The Psalter's specific menu and the actual source-span markers give stronger representation evidence.

## All sixteen held-out work identities

Metadata came from the existing source index and the previously verified exclusion list. No title below is identical to an eight-root title. That observation does not establish non-equivalence; the remaining checks are stated explicitly.

| Excluded Parsig ID(s) | Metadata identity | Remaining equivalence issue |
|---|---|---|
|103 | Counsels of Adarbad Mahraspandan | Embedded or re-edited counsel passages, especially in Denkard VI; untested. |
|104 | Counsel of Behzad Farrokh Peroz | Same unresolved counsel/quotation issue. |
|110 | Counsels of the wise to Mazdayasnians | Collection title may hide reused smaller units; untested. |
|111 | Counsels of religious authorities to the faithful | Same constituent-unit problem. |
|112 | Sūr saxwan / banquet speech | No whole-root match established; quotation or parallel is untested. |
|114 | Five characteristics of religious authorities | Short doctrinal unit could recur within compilations; untested. |
|116 | Čīdag andarz ī pōryōtkēšān | Catechetical/counsel unit; no passage-level clearance. |
|117 | Khusro Qobadan and the Page | Different named work from Arda Viraz, but title distinction alone does not clear any reused passage. |
|118 | Nature and wisdom of a fortunate man | Short wisdom work; no constituent-unit clearance. |
|120 | Counsel of Baxt-Afrid | Same counsel/quotation screening requirement. |
|124 | Fragment1, Jamasp-Asana,p72 | **Unresolved title identity:** location-only metadata prevents a reliable named-work comparison across all eight roots. |
|130 | Month Farwardin, day Khordad | Religious/narrative parallels remain untested; no confirmed root match. |
|132 | A few words of Adarbad Mahraspandan | Short sayings could appear inside other counsel compilations; untested. |
|138 | Šāyist nē šāyist | No same-title root here; religious/legal excerpt parallels still need checking. The separately inventoried `snstrl/snstrs` roots remain excluded. |
|152 | Wizīdagīhā ī Zādspram | No same-title root here; cosmological/doctrinal parallels remain unresolved. The separately inventoried `zadspram` root remains excluded. |
|517 | `y (Middle Persian)` | **Unresolved manuscript/text identity:** the letter label is insufficient for an equivalence exclusion decision. Distinct-looking religious tradition is not a substitute for identifying the witness. |

These are risk-based review requirements, not findings that all such overlaps exist. **No entire root is newly EXCLUDED from study, and no entire root is cleared for training.** Identifiable navigation/word-index shells are excluded from any eventual running-text extraction; quotations or equivalents of excluded works must also be excluded if found.

Qualified TRAIN metadata contains neither an Arda Viraz, Denkard IV–VII, MHD, Psalter nor Pahlavi Rivayat work label. It includes substantial Menog-i xrad, Karnamag and other counsel/religious works. The prior source-only scan recorded one eight-term occurrence linking arda to TRAIN151, one linking dk6 to109, and pahlriv matches to301/302/151. These small exact matches can be formulas and do not identify whole-work duplication. The other roots' lack of recorded matches proves nothing about held-out equivalents or different orthographies. This review did not redo the scan or inspect held-out text.

## Rights evidence and permitted research scope

Archived content and index pages name TITUS copyright and restrict republication without prior permission. Source collection metadata additionally records scholarly/reference use and no commercial authorization. This is relevant provenance, not a blanket ruling that private research processing is illegal.

The parent reviewer reports newly checked public TITUS guidance at [texte2.htm](https://titus.uni-frankfurt.de/texte/texte2.htm) and [textex.htm](https://titus.uni-frankfurt.de/texte/textex.htm): publicly downloadable texts may be used for scholarly purposes with editor/date citation and without commercial use. The parent also distinguished the password/member-account declaration at `titusstd.htm` using `faq/faq2.htm`; do not import that separate context automatically into every public HTML page. **Those live pages were verified by the parent, not independently fetched in this local-only subtask.**

On that bounded evidence, creating a private local research extraction with preserved notices and provenance is a supportable next project action. Absence of a named ML license is not itself a universal prohibition. Permission for corpus republication, cloud upload, model/adapter redistribution or a commercial use is not established here. Those unresolved external scopes should not be silently bundled into the local extraction decision. Training readiness also depends independently on split equivalence and source quality, which this review has not cleared.

## Exact next subset and acceptance boundary

Extract **only the archived111 numbered URLs** under `https://titus.uni-frankfurt.de/texte/etcs/iran/miran/mpers/dk4/`, from `dk4001.htm` to `dk4111.htm`, using the existing `documents.json` and prior page inventory hashes. This is the complete archived numbered root, not a claim that the archive is complete against the printed edition. Exclude its six frame/index/word-index pages. Save a new research-only artifact; leave raw/text archives unchanged.

First-page raw file: `sources/local/public-texts-2026-09-20/titus/raw/7b770079645358a0377d5f94b021527b5fb631ca785cbe1299cd3067a8481aa5.source`. It exposes `miphts16` spans and chapter anchors suitable for a small standard-library extraction proof. The previous prose-locator heuristic is unsuitable because it misses chapter-only pages. Do not normalize away diacritics, emendments, variant readings, separators or internal language boundaries to make the text look uniform.

Root owns implementation. A useful proof should preserve URL, raw/text hash, work/book/chapter anchors and edition credits; reconcile all111 expected pages; report excluded headings/notes/other-language spans and unresolved segments; compare samples from beginning/middle/end against archived source spans; and keep a prominent **RESEARCH_ONLY / NOT_TRAINING_ADMITTED** status. Resolving the sixteen-work equivalence questions, especially metadata-poor124 and517, remains a separate prerequisite for CPT admission. The experiment would establish extraction feasibility and a reliable size estimate, not training efficacy or a newly cleared corpus.

Handoff update: the parent reports completing an in-memory HTMLParser probe over all111 pages:196 `miphts16` spans,4,665 whitespace terms, no empty pages or exact duplicate spans, anchors present for every span, no unterminated spans, and every archived raw hash matching. These are **parent-executed results, not independently reproduced here**; the parent will preserve the command/evidence in `SOURCE-DECISION.md`. They support technical tractability and show why the10,484 raw-page terms overestimate extracted running text. Training admission remains unchanged.
