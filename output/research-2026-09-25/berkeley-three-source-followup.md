# Berkeley three-document bibliography follow-up

Observed 2026-09-25, 04:39–04:44 UTC. Result: PARTIAL. Bibliography identities are resolved; explicit English-translator attribution and edition-specific text-use scope remain unresolved. This report grants no permissions, approves no alignment and adds no training examples.

## Method and evidence boundary

Read the existing S03 review and the retained header census, then used the official OpenAMPD website through Chrome's rendered accessibility tree. The in-app browser was unavailable; the available Chrome connection succeeded. Followed the site's About and Bibliography links, bibliography search, and linked document pages. Dynamic content loaded after the initial shell. No endpoint guessing, login, messaging, private access, external publisher retrieval, GPU action, or held-out dataset inspection occurred. Only the three requested document pages were opened. The research tab was closed after inspection.

Local census directory: `[USER_HOME]\Documents\Codex Projects\01-Software\Pahlavi Translator\runs\diagnostics\berkeley-header-census-20260925`.

- `manifest.json` SHA256: `3fa5b9217940f988da1d298b7eb237eb7ea18c0226f6ef39dbde7fe4ef16dfe8`.
- `curation.jsonl` SHA256: `8911584bd719f0fedb594e5a9153846ac17a07911e019f047c22c543c8bd344d`.
- All three retained XML copies were rehashed and matched their recorded source identities. Header metadata only was extracted from these copies.

## Resolved bibliography mappings

### MP0603 / Ebrahimi Doc.

[Official bibliography entry: Asefi_2023a](https://mp.melc.berkeley.edu/exist/apps/OpenAMPD/Asefi_2023a) identifies Nima Asefi, 2023, article title **A New Middle Persian Document from Hastijan belonging to the Farroxzād Family**, in *Berkeley Working Papers in Middle Iranian Philology*, volume 1, issue 4, pages 1–14. The entry links back to MP0603.

[MP0603 metadata](https://mp.melc.berkeley.edu/exist/apps/OpenAMPD/MP0603?view=div&odd=openampd&panels=0.1.2) identifies Asefi 2023a as the first edition and explicitly says: “The edition used for OpenAMPD.” The retained TEI gives page 7. Nima Asefi's retained responsibility is **Text edition**, not an explicit translator role.

Exact local source: [862785…xml](<[USER_HOME]/Documents/Codex Projects/01-Software/Pahlavi Translator/runs/diagnostics/berkeley-header-census-20260925/sources/8627857141d78f7b5133b1a8be8276b22d59ecb03f6f7c17b8e4bea065f2e046.xml:33>).

- SHA256: `8627857141d78f7b5133b1a8be8276b22d59ecb03f6f7c17b8e4bea065f2e046`.
- Line 33: `teiHeader/fileDesc/sourceDesc/listBibl/bibl/@corresp = #Asefi_2023a`.
- Line 34: child `biblScope/@unit = page`, text `7`.

### MP5650 / Qal‘eh Iraj O. 1

[Official bibliography entry: Cereti_etal_2022](https://mp.melc.berkeley.edu/exist/apps/OpenAMPD/Cereti_etal_2022) identifies Carlo G. Cereti, Mohammadreza Nemati and Mahdi Mousavinia, 2022, chapter **Ostraca and bullae from Qal‘eh Iraj**, in *Ancient Arms Race*, volume VII, pages 461–474; publisher Oxbow Books. The entry supplies DOI `10.2307/jj.1127635.21` and links back to MP5650. Editors listed are Eberhard W. Sauer, Jebrael Nokandeh and Hamid Omrani Rekavandi. This resolves the publication identity; the DOI destination was not opened.

[MP5650 metadata](https://mp.melc.berkeley.edu/exist/apps/OpenAMPD/MP5650?view=div&odd=openampd&panels=0.1.2) names Cereti et al. 2022 as the first edition. Carlo Cereti's retained responsibility is **Text edition**. The page does not explicitly name an English translator.

Exact local source: [07a773…xml](<[USER_HOME]/Documents/Codex Projects/01-Software/Pahlavi Translator/runs/diagnostics/berkeley-header-census-20260925/sources/07a773e8c6bfaa2ea03cabf8a69846f9f17f3a73f7fa68ede6387ded3d5705fb.xml:29>).

- SHA256: `07a773e8c6bfaa2ea03cabf8a69846f9f17f3a73f7fa68ede6387ded3d5705fb`.
- Line 29: `teiHeader/fileDesc/sourceDesc/listBibl/bibl/@corresp = #Cereti_etal_2022`.
- Line 30 is literally `<biblScope unit="462-463"/>`: empty text and an unusual unit attribute. Preserve this anomaly. Publication pages 461–474 do not justify silently replacing the document-specific source markup.

### MP0404 / Berlin 4

[Official bibliography entry: Weber_2008a](https://mp.melc.berkeley.edu/exist/apps/OpenAMPD/Weber_2008a) identifies Dieter Weber, 2008, **Berliner Pahlavi-Dokumente. Zeugnisse spätsassanidischer Brief- und Rechtskultur aus frühislamischer Zeit**, series *Iranica* 15, Wiesbaden: Harrassowitz. The entry links back to MP0404.

[Official bibliography entry: Weber_2022c](https://mp.melc.berkeley.edu/exist/apps/OpenAMPD/Weber_2022c) identifies Dieter Weber, 2022, **Sasanian Festivals in the Documents from the “Pahlavi Archive.”**, in *Sasanian Studies / Sasanidische Studien*, volume 1, pages 323–345. The entry links back to MP0404.

[MP0404 metadata](https://mp.melc.berkeley.edu/exist/apps/OpenAMPD/MP0404?view=div&odd=openampd&panels=0.1.2) calls Weber 2008a the first edition and attaches the literal note “The used for OpenAmpd.” to Weber 2022c. The retained TEI credits Dieter Weber with **Edition used for OpenAMPD**. It does not explicitly credit him as English translator.

Exact local source: [b41fd9…xml](<[USER_HOME]/Documents/Codex Projects/01-Software/Pahlavi Translator/runs/diagnostics/berkeley-header-census-20260925/sources/b41fd98f95d43503f397936a8b07ec0e964698239e2b982412c91a5d8801de4b.xml:33>).

- SHA256: `b41fd98f95d43503f397936a8b07ec0e964698239e2b982412c91a5d8801de4b`.
- Lines 33–34: `bibl/@corresp = #Weber_2008a`; child `biblScope/@unit = page`, text `18–23`.
- Lines 37–38: `bibl/@corresp = #Weber_2022c`; child `biblScope/@unit = page`, text `331–334`.
- Both `bibl` elements are under `teiHeader/fileDesc/sourceDesc/listBibl`.

## Translator attribution and text-use statements

The three live document metadata panels and four linked bibliography entries contain no explicit English-translator responsibility. Bibliographic authors and retained text-edition/TEI contributors remain distinct from a verified translator attribution. This is an observed metadata gap, not evidence that the named scholars did not translate the documents.

The [official About page](https://mp.melc.berkeley.edu/exist/apps/OpenAMPD/about?view=single&odd=teipublisher) explains that the digital editions closely follow published scholarly editions. Source line numbering follows those editions, while translation layout can be paragraph-based or line-based. It directs readers to the published editions for philological and interpretive commentary. These editorial statements support preserving document association and prohibit assuming line-by-line alignment from layout alone.

The About page and inspected document pages display the footer **“OpenAMPD © 2023–2024 CC BY-NC-SA 4.0”**, linked to the Creative Commons licence. The About page separately describes the software components as open source. No inspected page explicitly distinguishes the licence scope of underlying editions/translations, grants a named use for these three texts, or mentions machine-learning training. The website notice, software statement, source edition identity and translator identity are separate facts. This report makes no legal determination from the absence of additional wording.

## Concrete local metadata gap and disposition

The existing census curation rows have `bibliography_references: []` for all three records even though the checksum-verified TEI contains the `bibl/@corresp` values above. This is a supplemental metadata-recovery opportunity. Do not rewrite the original immutable census or normalize the malformed MP5650 scope silently.

All four publication identities are now resolved through the official site's displayed entries and reverse document links. The remaining next evidence is the explicitly attributed translation and relevant text-use terms in those named publications or an authoritative clarification of their inclusion under the website notice. Alignment and work/edition overlap review also remain separate. All current unknown permissions, source-association alignment states, corpus versions and dataset partitions are unchanged.
