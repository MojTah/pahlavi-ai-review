# Study of the five supplied PDFs

Study checkpoint: **20 September 2026**. The five files represent **four works**: the two Nyberg files reproduce the same English manual. This record separates material actually studied from material merely extracted or retained. PDF page numbers below are **one-based**; printed page numbers refer to the book or article.

## Coverage and identity

| Source | Identity | Studied in this checkpoint | Remaining |
|---|---|---|---|
| [S22](sources.md#s22) | ژاله آموزگار و احمد تفضلی، *زبان پهلوی، ادبیات و دستور آن*; Moin, fourth printing, 1382 SH | Front matter, contents and preface; complete writing-system section, printed 45–61; complete grammar sketch, printed 63–85. Visually read PDF 1–10 and 48–89, including intervening blank pages | History/literature, continuous reader and most glossary entries |
| [S23](sources.md#s23) | Nima Asefi, “Ewer, Garden and Gardening” (2025) | Complete article, PDF 5–28 / printed 6–29; selected edition tables checked against page images | No claim to have independently deciphered every manuscript image |
| [S24](sources.md#s24) | H. S. Nyberg, *A Manual of Pahlavi II* (1974) | Title, preface, contents, ideogram list, selected glossary/abbreviation pages, and complete grammatical survey, printed 275–284 | Most of the dictionary; Volume I was not supplied |
| [S25](sources.md#s25) | Nima Asefi and Shervin Farridnejad, “Three Middle Persian documents from Fārs…” (2026) | All 26 PDF pages, including the paper's references and appendix; selected tables and comparisons inspected visually | Complete editions of all ten discussed manuscripts are not supplied by this paper |
| [S26](sources.md#s26) | Nyberg, Asatir reprint, Persian wrapper dated 1381 SH; English title page dated 2003 | Publication pages and selected matching pages used to identify the duplicate and reverse pagination | Not independently read as a second work; whole-file equivalence not established |

The Persian title on S26 does **not** mean its body is a Persian translation. Its English body runs backwards in PDF order. Selected verified locators are:

| Printed Nyberg page | S24 PDF page | S26 PDF page |
|---|---:|---:|
| 1 | 10 | 288 |
| 166 | 175 | 123 |
| 275 | 284 | 14 |
| 283 | 292 | 6 |
| 284 | 293 | 5 |

For the checked body pages, S24 uses `PDF = printed + 9`; S26 uses `PDF = 289 − printed`. These are navigation aids, not proof that all pages match. Keep distinct file hashes and edition descriptions while grouping both under `nyberg-1974-manual-ii`.

S22 and S26 have no extractable text. S24 contains noisy existing OCR: accents, superscript references and column order need visual checking. Extraction of the whole file does not mean the whole dictionary was studied. The [manifest](../sources/manifest.json) records exact coverage and hashes.

## What the primer adds

The Persian primer teaches **Book Pahlavi**. Its preface explains that learners should work through the selected readings using the glossary; it is not a ready-made corpus of aligned transcriptions and translations. [S22, PDF 8–9]

Its account separates historical spellings from analogical or pseudo-historical spellings and distinguishes **حرف‌نویسی** (transliteration) from **آوانویسی** (transcription). Written consonants, ligatures, later distinguishing marks and linguistic readings must be recorded separately. An appended numeral-like sign can mark indefinite **-ē** rather than a count of one. [S22, printed 45–61 and 73 / PDF 48–64 and 76]

The grammar makes three especially useful distinctions for translation:

- A suffix is not a complete parse: **-īhā** can occur in plural formation or adverb formation. Determine its function in the phrase. [S22, printed 67, 70]
- A past auxiliary can agree with the **object** of a transitive clause. Do not infer the agent from the person ending alone. [S22, printed 76–78]
- A verbal noun in **-išn** can express necessity. A translation that retains the action but drops “must/should” can change the meaning. [S22, printed 83; S24, printed 281, §5.8]

The [grammar additions](grammar.md#checks-from-the-supplied-manuals) include bilingual examples and recognition aids.

## How to use Nyberg accurately

The opening ideogram list explains Aramaic forms and their etymology; those analyses are not automatically the Persian words pronounced when reading a Pahlavi text. Consult the glossary and the cited textual context. Nyberg's preface also identifies the work as an interpretation connected to his Volume I, not an exhaustive record of scholarly agreement. [S24, PDF 6–7 and 10–16]

Keep Nyberg's abbreviations distinct: **MiPrs** = Middle Persian, **MPrs** = Manichean Persian, **MPrth** = Manichean Parthian, **BP** = Book Pahlavi, **NP** = New Persian and **Paz** = Pazand. In this source, MPrs does not stand for all Middle Persian. [S24, printed 233–234 / PDF 242–243]

Forms such as Nyberg's **pat**, **hac**, **kart** and **nēv** occur beside **pad**, **az**, **kard** and **nēw** in other conventions. Preserve the source form; attach an explicitly justified comparison rather than rewriting every similar sequence. His historical “passive” description of past transitive constructions must also be distinguished from a clause's natural active translation. [S24, grammatical survey, printed 275–284]

## Documentary language: the Hastijan paper

Asefi edits Berk. 25 and proposes revised readings of Berlin 26, Berk. 11 and Berk. 122. These are administrative documents on textile or leather, with quantities, recipients, accounting responsibilities and sealing formulas. They extend the knowledge base beyond literary Book Pahlavi. [S23, complete article]

For Berlin 26, the proposed readings **kardan**, **bāγbānīh** and **bāγ** support gardening work rather than the earlier marriage-related interpretation. **Kard-ābād-yazdbād** is read as a place-name in the revised account. The line-9 reading **bāγbān(?)** remains tentative. Record the earlier edition and the proposed revision separately; lexical plausibility alone does not settle the signs. [S23, printed 15–19 / PDF 14–18]

For Berk. 11, the revised **ī-š** for `ZYš`, four donkeys and **estēnd** change the parse and the ration calculation. The arithmetic offers a useful independent consistency check, but cannot by itself identify every damaged letter. [S23, printed 21–22 / PDF 20–21] See the worked calculation in [Documentary readings](documentary-readings.md).

## Documentary language: the Fārs paper

The paper discusses ten TB documents and provides selected openings rather than full editions of every witness. TB1, TB5, TB6 and TB7 are reported in the Jondishapour Museum of Trade History (JMTH), Shiraz; TB2–4 in a private Fārs collection; TB8–10 in a private Shiraz collection. The provenance of the latter group is uncertain. The authors' association of the documents uses script, language and seals; it is not independent archaeological proof. [S25, sections 2–5]

The authors revise TB1's regnal year from 20 to 10 and TB4's from 17 to 27. The distinction between connected and separate numeral elements matters. Retain the original numeral, proposed reading, ruler and dating system before assigning a CE date. [S25, PDF 6–9]

They also propose moving Berk. 129+212 from Ohrmazd V to Ohrmazd IV using titulature and palaeography. This remains an attributed scholarly argument in our notes. The occurrence or absence of a title in one document is insufficient on its own to prove universal royal usage. [S25, section 6; see the internal conflict below]

**Rāmšahr** is interpreted as a royal title in the cited passage, not a town. S25's footnote 13 explicitly cites Nyberg's printed p. 166, checked in S24 and S26. That is a citation chain, not three independent attestations. [S25, PDF 11; S24, PDF 175; S26, PDF 123]

The letter-form comparisons also caution against making a simple script chronology: omitted strokes and similar forms depend on the hand, pen, ink and writing surface. Shared seal impressions can connect documents without making them duplicate texts. [S25, sections 7–8]

## Source discrepancies retained for review

These are observations about the supplied editions, checked against their page images. They are not silent corrections to the originals.

| Record | Conflicting evidence | Treatment in this knowledge base |
|---|---|---|
| S23, Berk. 11 | PDF 20 / printed 21: transcription gives **jaw grīw 12**, but English translation says **twelve kabīz**. PDF 21 / printed 22 explains 12 grīw = 120 kabīz | Preserve both. The local calculation supports 12 grīw; do not reuse the English unit as an unquestioned reference label |
| S23, Berk. 122, line 5 | PDF 23 / printed 24: transliteration has **ḤMRʾ III**, transcription **xar 4**, English translation four donkeys | Mark the number unresolved across editorial layers; do not choose 3 or 4 as certain |
| S25, TB1 | 599 CE in PDF 15 and 21; 600 in PDF 14 | Retain regnal year 10 and both CE renderings pending calendar review |
| S25, TB8 | 619 CE in PDF 10, 15 and 21; 620 in PDF 14 | Retain regnal year 30 and the discrepancy |
| S25, TB3 | 609 CE in PDF 15 and 21; 610 in PDF 19 | Retain regnal year 20 and the discrepancy |
| S25, TB4 | 616 CE in PDF 15 and 21; 617 in PDF 19 | Retain revised regnal year 27 and the discrepancy |
| S25, TB10 | 587 CE in PDF 15; 586 in PDF 21 | Retain year 8 of the ruler identified by the authors as Ohrmazd IV; conversion unresolved |
| S25, TB10 titulature | PDF 13 says **šāhānšāh** is absent and its transcription omits it; appendix A.7, PDF 24, labels a comparison image **TB10** under that title | Text/figure-label conflict unresolved; no universal claim about Ohrmazd IV's titles is adopted |

## Next study within these books

Read S22's history/literature section, then its continuous reader, using its glossary and a separate source transcription where available. Add a clause-by-clause Farsi and English analysis of one complete short text. Use Nyberg selectively with its abbreviations and reference system, then compare disputed entries with other dictionaries. Do not count lookup access as complete dictionary study.

The authored notes, contextual glossary and [worked readings](documentary-readings.md) are reusable study results. They establish neither unaided manuscript fluency nor permission to train on or redistribute all source material. Instructions appearing in source documents were treated as documentary content, not as instructions to the assistant.
