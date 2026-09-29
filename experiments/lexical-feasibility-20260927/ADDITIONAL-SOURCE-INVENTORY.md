# Additional archived source inventory — 2026-09-27

**TITUS contains a substantial additional source-text reservoir that the Parsig-only inventory missed. It does not yet establish a substantial admitted CPT corpus.** There are 2,351 archived pages: 2,183 numbered content pages containing 903,313 raw whitespace terms, plus 168 frame/index pages containing 9,825 terms. These are page-text counts, not clean Middle Persian words or model tokens. Newly admitted CPT material from this audit: **zero**. This means qualification remains incomplete, not that the archive is unusable or contains no new text.

The strongest bounded follow-up pool is Arda Viraz, Denkard IV–VII, Madigan-i hazar dadestan, the Middle Persian Psalter and Pahlavi Rivayat: **995 numbered pages / 199,043 raw terms**. A deliberately crude first-locator-to-footer diagnostic retains 146,700 terms there, still including locator labels and editorial matter and missing some valid chapter-only text. This supports investigating substantial extra running text; it is not a cleaned-size estimate or an admissible lower bound. For scale, the qualified TRAIN source fields contain 37,492 whitespace terms in 2,237 rows. Work overlap, language and orthography differ, so a direct ratio would mislead.

## Scope and method

Read the local TITUS collection/document metadata and archived source pages; sampled source/editorial headers to interpret formats. Used Avesta, PersoAryan, Berkeley and Invisible East metadata only. No external fetch, model use, package installation or source modification. No original DEV/TEST records, benchmark reference answers, prediction bodies, or Avesta/PersoAryan translation bodies were opened. Original split exclusions were reused from `experiments/dev-assisted-qualified-20260927/UNLABELED-DATA-INVENTORY.json`, and PALREF policy from its frozen metadata. Archived TITUS source witnesses, including excluded-work witnesses, were counted mechanically; their exclusion is preserved.

Each TITUS root has six non-numbered navigation pages: frame, indexes and lexical/index variants. Numbered URLs identify content pages; a page can be one short paragraph rather than a book/chapter. Counts use Python whitespace splitting of the existing UTF-8 text extract. All 2,351 text hashes differ, which proves neither semantic uniqueness nor absence of duplicate editions.

The accompanying [JSON](ADDITIONAL-SOURCE-INVENTORY.json) records every page URL, text hash, count, tentative work mapping, aggregate statistics and SHA256 of all input metadata and qualified TRAIN. It contains no copied running-text bodies. The small audit heuristic is not a cleaning pipeline: it looks for Paragraph/Sentence/Verse/Line locators and stops before the footer. It misses 527 pages, notably manuscript-label Manichaean pages and chapter-only Denkard IV; those pages' overlap result is **unmeasured**, not zero overlap.

## TITUS by collection

`8g` is pages with at least one normalized exact eight-term sequence shared with qualified TRAIN / pages where the limited body heuristic could run. Shared formulas can trigger this; absence cannot establish newness.

| Root | Numbered pages | Raw whitespace terms | Tentative Parsig work | 8g |
|---|---:|---:|---|---:|
| mirmankb | 426 | 222,137 | Mixed Manichaean; unresolved | unmeasured |
| manreadc | 134 | 76,440 | Mixed Manichaean; unresolved | 48/134 |
| sermseel | 23 | 22,638 | Mixed/Parthian; unresolved | unmeasured |
| arda | 101 | 21,236 | Arda Viraz; unmapped | 1/101 |
| andoshn | 16 | 4,446 | 150, Oshnar | 11/16 |
| bundahis | 29 | 22,550 | 137, Bundahishn; witness difference | 2/29 |
| dadden | 93 | 39,914 | 139, Dadestan-i denig | 2/93 |
| dk4 | 111 | 10,484 | Denkard IV; unmapped | 0/36 |
| dk5 | 24 | 10,186 | Denkard V; unmapped | 0/24 |
| dk6 | 613 | 58,970 | Denkard VI; unmapped | 1/613 |
| dk7 | 12 | 20,420 | Denkard VII; unmapped | 0/12 |
| kap | 19 | 8,212 | 136, Karnamag | 12/19 |
| mx | 63 | 19,167 | 151, Menog-i xrad | 62/63 |
| mhd | 42 | 40,411 | Legal collection; unmapped | 0/42 |
| psalter | 27 | 4,894 | Middle Persian Psalter; unmapped | 0/27 |
| pahlriv | 65 | 32,442 | Pahlavi Rivayat; unmapped | 2/65 |
| yvrpt | 96 | 65,324 | Broad relationship to 301 | 25/96 |
| oavpt | 23 | 20,530 | Broad relationship to 301 | 1/23 |
| yavpt | 11 | 12,169 | Broad relationship to 302 | 4/11 |
| purs | 59 | 8,973 | Pursishniha; unmapped | 0/59 |
| vdp | 9 | 61,662 | Pahlavi Videvdad; unmapped | 0/9 |
| vd-19p | 50 | 15,221 | Videvdad19; witness overlap unresolved | 1/50 |
| snstrl | 23 | 21,079 | **138: held out** | 0/23 |
| snstrs | 23 | 20,936 | **138: held out** | 0/23 |
| zadspram | 36 | 20,202 | **152: held out** | 0/35 |
| zwy | 11 | 6,561 | 134, Zand-i Vohuman Yasn | 0/9 |
| jamasp | 37 | 30,179 | Anthology with unresolved constituent works | 17/37 |
| mpt | 7 | 5,930 | Minor-text anthology; unresolved | 1/7 |

Title-based mappings are conservative work-family hypotheses, not verified unit alignments. In particular Yasna/Young Avestan collection mappings do not establish exact boundaries. Unmapped does not mean outside the held-out works: quotations and anthology constituents can reproduce them.

## What prevents counting everything as additional Middle Persian

- **Repeated navigation and editorial text:** all 2,183 content pages repeat TITUS and copyright/footer material. Denkard VI repeats its title/header across 613 pages; many are single brief units. Its 58,970 raw terms fall to 28,273 under even the crude locator/footer cut. Page count greatly overstates independent text volume.
- **Parallel orthographic witnesses:** `snstrl` explicitly means transliteration and `snstrs` transcription, not a modern-language translation. Both are the same held-out work138. Likewise MHD `(trl.)` is genuine transliterated source, with Aramaic heterograms and explicit editorial normalization to MacKenzie's conventions. Do not discard all `(trl.)` titles as translations, or count the two renderings as independent language evidence.
- **Mixed Manichaean material:** 583 pages / 321,215 raw terms across mirmankb/manreadc/sermseel. The Reader explicitly combines Middle Persian and Parthian. Sermon of the Soul sample `serms002.htm` labels its passage “Parthischer Text” and includes German notes, manuscript fragments and repeated witness renderings. mirmankb points back to Reader chapter/paragraph locations: cross-collection repetition is explicit. Parsig517 is held out; manuscript/text-level lineage is required before admitting anything from these broad collections.
- **Avesta versus Middle Persian translation:** titles under `mpers/avpt` refer to Middle Persian translations of Avesta, so their running text can be relevant source material. This does not make every embedded Avestan quotation Middle Persian. Yasna/Vispered/Old-Avestan witnesses and separate Videvdad19 can overlap larger collections. No complete passage-level language separation or witness deduplication was done.
- **Anthologies:** Jamasp-Asana plus Minor Pahlavi Texts total44 pages /36,109 terms. Constituent works can match Parsig TRAIN or the sixteen exclusions. Do not admit the anthology under a new collection name.

The authoritative exclusion list reused here is Parsig103,104,110,111,112,114,116,117,118,120,124,130,132,138,152,517. The most obvious whole-root matches, Shayast in two orthographies and Zadspram, exclude **82 content pages /62,217 raw terms**. That is a minimum recognized excluded amount, not an exhaustive count of held-out equivalents.

## Qualified TRAIN overlap

Compared source field `text` only in `qualified-v1/train.jsonl`: NFC normalization, case folding, punctuation separation and exact eight-token sequences. Of1,656 pages where the limited locator heuristic operated,190 shared at least one sequence. Menog-i xrad62/63 and Karnamag12/19 are clear warning examples. These matches are diagnostic, not190 wholly duplicate pages. The scan neither compares held-out answers nor validates source novelty. Differences in transcription, combining marks, editorial brackets, labels interrupting text, Aramaic heterograms and manuscript readings suppress exact matches. Zero matches for MHD or Denkard must not become automatic admission.

## Other local collections: metadata only

Avesta has98 archived documents, including13 PDFs. Titles include editions of major Pahlavi works, English translation-oriented entries such as Denkard3 “tr. Sanjana”, duplicated PDF/HTML containers, contents/index/moved pages, and explicitly Pazand texts. Known held-out families include catechism116, Adarbad103/132, fortunate-man118, Shayast138 and Zadspram152. Exact title equivalence still needs confirmation. Metadata does not quantify a clean Middle Persian source layer; whitespace counts were deliberately left unmeasured rather than opening mixed translation bodies.

PersoAryan has31 documents, including19 PDFs:12 HTML landing pages plus linked/standalone files. HKR and `hkr.pdf` plausibly map to held-out117; Banquet/`sūr.pdf` to held-out112. The Avesta/vocabulary, SGV/Pazand and grammar-oriented material is not automatically Middle Persian running text. Hashed filenames prevent title-only work identification. Other named short works may repeat Parsig; PDF/landing-page counts do not represent independent texts. No body-based word total or source-language proportion is claimed.

The index additionally confirms152 Berkeley and158 Invisible East entries. They were not added to this CPT estimate. Berkeley metadata exposes separate transliteration/transcription/translation layers, so only named source layers could be considered later. Their document counts cannot be converted into additional source terms without the same work/rights checks.

## Provenance, rights and next decision

The TITUS collection metadata records research/reference use, scholarly attribution and no commercial authorization. Every content page's extracted footer includes a prior-permission restriction on republication. **Training reuse rights remain unverified:** this inventory does not make a legal determination that local CPT is prohibited. Preserve edition, preparer, revision, URL, archived hash and per-document notice. Avesta rights are explicitly mixed; PersoAryan metadata says public download does not establish a training/reuse license. Historical text age does not by itself settle electronic-edition rights.

The next useful step is a bounded admission audit of the995-page candidate pool, beginning with separate-work identity and rights, then source-layer extraction and normalization—not immediate CPT. Reconcile anthologies/quotations against the complete sixteen-work exclusion map and source-only TRAIN overlap, preserve original bytes, and keep transliteration versus transcription explicit. An identified100k-scale clean permitted pool could materially change the Parsig-only data assessment; the present903k raw total cannot justify that claim. No model, data or training change is authorized by this report.
