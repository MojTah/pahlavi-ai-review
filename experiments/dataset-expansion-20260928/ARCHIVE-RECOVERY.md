# Offline archive recovery: document-associated auxiliary candidates

28 September 2026. Mode: Classic Codex, bounded offline recovery. Writer/reviewer `/root/seen20_blind_b`; root alone integrates. No network, acquisition, external model, training or source edits.

**53 lossless document-level Middle Persian-to-English candidates: 42 Berkeley OpenAMPD and 11 Oxford Invisible East. Zero training admissions.** These are extractions of already archived documents, not new acquisitions, not Persian targets, and not sentence-pair counts.

## Association and preservation

- Inspected existing `scripts/collect_openampd.py`, Berkeley/Oxford adapters in `scripts/verify_collection.py`, `data/unified-corpus/build.py`, source coverage and pinned manifests before export. No general parser was added.
- Berkeley:152 documents,46 with nonempty transcription:pal and translation:en layers. The shared TEI and manuscript/edition identifiers justify document association. Every exported row preserves complete raw XML verbatim, the original archive record/layers, exact source byte hash and XPath/JSON locators. The collector flattened whitespace; that text field alone is not treated as lossless.
- Oxford:158 records,14 paired documents/16 paired folios. Raw downloaded JSON equals the derived archive exactly. Complete original records and all folio HTML survive, including side, li value, data-range-end, editorial alternatives and lacunae. Two folios do not become two independent documents.
- Berkeley explicitly tags pal/en. Oxford labels the source Middle Persian (Pahlavi script); its14 translation fields were inspected as English, with no explicit per-field target-language tag.
- Edition/editor/TEI credits are not silently renamed translators. No separately designated English translator was found in the inspected structured credits; names and exact edition references are retained. The Berkeley bibliography register is not among its archived manifest URLs; abbreviated IDs are left unresolved.

## Exclusions

| Record | Reason |
|---|---|
| OpenAMPD MP0072 | Berk.67 also occurs as Oxford IEDC1024, with materially different bitten/stung versus gazidag-fiscal interpretations. Editions remain unreconciled. |
| OpenAMPD MP0600 | Unknown Doc.1 has edition references but no physical shelfmark or independently reconciled identity; conservative identity hold. |
| OpenAMPD MP1019 | Title/siglum Tab.16 conflicts with sourceDesc calling Gignoux2014 pp43-45 the first edition of Tab.19. |
| OpenAMPD MP1022 | Conservative companion hold on Tab.19 until the MP1019 Tab.16/Tab.19 identity collision is resolved; not a finding that MP1022 itself is wrong. |
| Oxford IEDC1024 | Same Berk.67 witness as MP0072; materially different edition interpretations remain unreconciled. |
| Oxford IEDC1036 | Berk.34 also occurs as Berkeley MP0035 with other-language edition layers; readings/editions not reconciled. |
| Oxford IEDC1261 | CT-133/4 cites the BSOAS fiscal-system article (printed395-420) with pages18-19 for an ostracon. Underlying edition/reference unresolved. |

All7 exclusions are absent from the candidate JSONL and remain untouched in their original archives. MP1022 is a conservative companion hold, not a demonstrated error in its own record.

## Held-out families and overlap

- Screened all16 frozen work identities: 103, 104, 110, 111, 112, 114, 116, 117, 118, 120, 124, 130, 132, 138, 152, 517. Only work/title metadata were read; no held-out answer content was opened, reproduced or compared. Exported items are specific documentary physical objects/sigla distinct from those literary/Manichaean families. This does not certify absence of all shared quotations or formulas.
- Berk.67: MP0072 and IEDC1024 represent the same witness with materially different bitten/stung versus gazidag fiscal interpretations. Both are excluded until editions are reconciled.
- Berk.34: Oxford IEDC1036 overlaps Berkeley MP0035 with other-language layers; Oxford candidate withheld pending comparison. Other exact shelfmark matches to Oxford metadata-only records remain explicit candidate metadata, not extra independent attestations.
- Named S23 overlap check (Berk.25, Berlin26, Berk.11, Berk.122 from SOURCE-COVERAGE): none appears among the53 exported witness identities. This is not an exhaustive cross-book quotation audit.
- Exact NFC-plus-whitespace comparison:0 complete Berkeley candidate transcription matches to qualified TRAIN source strings. This does not establish absence of partial/formula or cross-edition overlap. Oxford HTML was not flattened into an unsupported all-clear.

## Admission gaps and next concrete work

1. Resolve the seven named exclusions, starting with Berk.67 interpretation variants, Tab.16/19 sourceDesc conflict and CT-133/4 citation mismatch. The archived originals are already available.
2. Resolve explicit translation authorship, Berkeley bibliography-register references and Oxford print/PDF page units. Preserve questionable citation strings rather than correcting from memory.
3. Check source/translation completeness, readings and uncertainty against editions. Segment only with explicit alignment evidence; metadata association is not sentence-alignment gold.
4. Reconcile exact intended-use scope: Berkeley metadata records CC BY-NC-SA4.0; the Oxford CC BY4.0 release has not yet been conclusively joined to this download. Image notices do not establish text licenses. No source here is training-admitted.

## Verification receipt

- Candidate SHA256: `fe2e80cbb323b2072c673fb0e715dba8d100f670bad9fbaf975b4b3b2ddba48d`.
- Rows53; unique IDs53; Berkeley42; Oxford11; task pal-to-en; training admissions0.
- All152 Berkeley raw XML hashes match saved receipt, Berkeley manifest and unified-v2 pins. All152 reproduce archived layer text exactly under the existing collector whitespace rule. NFC normalization is diagnostic only; original Unicode sequences remain unchanged.
- Oxford raw/derived hashes match unified-v2 pins and their parsed objects are equal. Exported source hashes and canonical original-record hashes verify. Every embedded Berkeley raw XML round-trips byte-exact through UTF-8.
- All output rows parse; all exclusion IDs absent. No model-generated translation or inferred line pair was produced.

## Candidate identity and edition inventory

| Candidate | Witness | Original edition references and scopes |
|---|---|---|
| openampd:MP0603 | Ebrahimi Doc. 1 | #Asefi_2023a 7 |
| openampd:MP5650 | Qal‘eh Iraj O. 1 | #Cereti_etal_2022  |
| openampd:MP1024 | Tab. 21 | #Gignoux_2012 72–75; #Weber_2019b 92–96 |
| openampd:MP0404 | Berlin 4 | #Weber_2008a 18–23; #Weber_2022c 331–334 |
| openampd:MP0602 | Āmol Doc. | #Weber_2015b 103-104 |
| openampd:MP0032 | Berk. 32 | #Gignoux_2001 296–298; #Gignoux_2003 86–87; #Gignoux_2010a 72–73; #Weber_2010b 46–47; #Weber_2022a 536–537 |
| openampd:MP0045 | Berk. 43B | #Weber_2014b 133 |
| openampd:MP1029 | Tab. 25 | #Gignoux_2016 180–182; #Weber_2022b 119–122 |
| openampd:MP0408 | Berlin 8 | #Weber_2008a 40–43; #Weber_2020_2021 38–39 |
| openampd:MP0070 | Berk. 65 | #Gignoux_2019 132-133; #Weber_2020_2021 51-53 |
| openampd:MP1027 | Tab. 24 | #Gignoux_2016 172–180; #Weber_2019b 102–110 |
| openampd:MP2500 | P. Weill Série III arabe n°1 (pehlevi) | #Gignoux_Weber_2019  |
| openampd:MP0409 | Berlin 9 | #Weber_2008a 44–47; #Weber_2020_2021 40–41 |
| openampd:MP0047 | Berk. 43D | #Weber_2014b 137 |
| openampd:MP0048 | Berk. 43E | #Weber_2014b 139 |
| openampd:MP5651 | Qal‘eh Iraj O. 2 | #Cereti_etal_2022 463-464 |
| openampd:MP0437 | Berlin 36 | #Weber_2008a 150–153; #Weber_2015b 88–90 |
| openampd:MP0046 | Berk. 43C | #Weber_2014b 135 |
| openampd:MP1026 | Tab. 22bis | #Weber_2022b 115–118 |
| openampd:MP0071 | Berk. 66 | #Gignoux_2009b 90-91; #Weber_2020a 147 |
| openampd:MP0407 | Berlin 7 | #Weber_2008a 34–39; #Weber_2020_2021 36–37 |
| openampd:MP0405 | Berlin 5 | #Weber_2008a 24–27; #Weber_2022c 328–330 |
| openampd:MP0024 | Berk. 24 | #Gignoux_2001 294–296; #Gignoux_2003 81–82; #Weber_2022c 335–336 |
| openampd:MP0412 | Berlin 12 | #Weber_2008a 56–59; #Weber_2020_2021 42–44 |
| openampd:MP0076 | Berk. 71 | #Gignoux_2010c 114-115; #Weber_2023 150-151 |
| openampd:MP1023 | Tab. 20 | #Gignoux_2014 56–57; #Weber_2022b 112–114 |
| openampd:MP0003 | Berk. 3 | #Weber_2023 291-293 |
| openampd:MP2100 | P.44 | #Weber_1992a 145; #Weber_2009a  |
| openampd:MP5652 | Qal‘eh Iraj O. 3 | #Cereti_etal_2022 464-466 |
| openampd:MP6003 | Khalili 129 | #Weber_2018a 99–108 |
| openampd:MP0410 | Berlin 10 | #Weber_2008a 48–51; #Weber_2015b 85–87 |
| openampd:MP0147 | Berk. 142 | #Weber_2022c 324–325 |
| openampd:MP0406 | Berlin 6 | #Weber_2008a 28–33; #Weber_2020_2021 30–31 |
| openampd:MP0067 | Berk. 62 | #Weber_2010b 50-53; #Weber_2020a 154-155 |
| openampd:MP0085 | Berk. 80 | #Weber_2008a 7–9; #Gignoux_2010a 80–81; #Weber_2010b 54–55 |
| openampd:MP2561 | P.Pehl. 562 | #Zeini_2016 39–52 |
| openampd:MP0416 | Berlin 16 | #Weber_2008a 72–75; #Gignoux_2010a 122–123; #Weber_2012 70–71 |
| openampd:MP2150 | P.45 | #Weber_1992a 150; #Weber_2018b 1-2 |
| openampd:MP0044 | Berk. 43A | #Weber_2014b 129; #Gignoux_2019 129–131 |
| openampd:MP0439 | Berlin 38 | #Weber_2008a 158–161; #Weber_2012 72–74 |
| openampd:MP0435 | Berlin 34 | #Weber_2008a 142–145; #Weber_2015b 105–106 |
| openampd:MP0093 | Berk. 88 | #Weber_2022c 338–339 |
| iedc:IEDC1266 | PM 37-33-42 (field no. CT-135/6) | Thompson, D. & Colt Archaeological Institute. 1976. Stucco from Chal Tarkhan-Eshqabad near Rayy. Warminster: Aris and Phillips. \| pages None; Benfey, Thomas. 2024, “Windādag’s Orders: Ten Unpublished Middle Persian Ostraca from Chāl Ṭarkhān-ʿEshqābād.” In Maria Macuch & Arash Zeini (eds.), Deciphering the Illegible: Festschrift in Honour of Dieter Weber. Wiesbaden: Harrassowitz Verlag. (Pages: 123-145) \| pages 22-23 |
| iedc:IEDC1267 | ISACM A154067 (field no. CT-205.1) | Benfey, Thomas. 2024, “Windādag’s Orders: Ten Unpublished Middle Persian Ostraca from Chāl Ṭarkhān-ʿEshqābād.” In Maria Macuch & Arash Zeini (eds.), Deciphering the Illegible: Festschrift in Honour of Dieter Weber. Wiesbaden: Harrassowitz Verlag. (Pages: 123-145) \| pages 23 |
| iedc:IEDC1268 | ISACM A154069 (field no. CT-205/3a) | Benfey, Thomas. 2024, “Windādag’s Orders: Ten Unpublished Middle Persian Ostraca from Chāl Ṭarkhān-ʿEshqābād.” In Maria Macuch & Arash Zeini (eds.), Deciphering the Illegible: Festschrift in Honour of Dieter Weber. Wiesbaden: Harrassowitz Verlag. (Pages: 123-145) \| pages 24 |
| iedc:IEDC1269 | ISACM A154070 (field no. CT-205/3b) | Benfey, Thomas. 2024, “Windādag’s Orders: Ten Unpublished Middle Persian Ostraca from Chāl Ṭarkhān-ʿEshqābād.” In Maria Macuch & Arash Zeini (eds.), Deciphering the Illegible: Festschrift in Honour of Dieter Weber. Wiesbaden: Harrassowitz Verlag. (Pages: 123-145) \| pages 24-25 |
| iedc:IEDC1270 | ISACM A154068 (field no. CT-205/4) | Benfey, Thomas. 2024, “Windādag’s Orders: Ten Unpublished Middle Persian Ostraca from Chāl Ṭarkhān-ʿEshqābād.” In Maria Macuch & Arash Zeini (eds.), Deciphering the Illegible: Festschrift in Honour of Dieter Weber. Wiesbaden: Harrassowitz Verlag. (Pages: 123-145) \| pages 25 |
| iedc:IEDC1262 | PM 37-33-54 (field no. CT-135/1) | Benfey, Thomas. 2024, “Windādag’s Orders: Ten Unpublished Middle Persian Ostraca from Chāl Ṭarkhān-ʿEshqābād.” In Maria Macuch & Arash Zeini (eds.), Deciphering the Illegible: Festschrift in Honour of Dieter Weber. Wiesbaden: Harrassowitz Verlag. (Pages: 123-145) \| pages 19 |
| iedc:IEDC1263 | PM 37-33-52 (field no. CT-135/2) | Thompson, D. & Colt Archaeological Institute. 1976. Stucco from Chal Tarkhan-Eshqabad near Rayy. Warminster: Aris and Phillips. \| pages pl. xxxiii, fig.3; Benfey, Thomas. 2024, “Windādag’s Orders: Ten Unpublished Middle Persian Ostraca from Chāl Ṭarkhān-ʿEshqābād.” In Maria Macuch & Arash Zeini (eds.), Deciphering the Illegible: Festschrift in Honour of Dieter Weber. Wiesbaden: Harrassowitz Verlag. (Pages: 123-145) \| pages 19 |
| iedc:IEDC1264 | PM 37-33-50 (field no. CT-135/4) | Thompson, D. & Colt Archaeological Institute. 1976. Stucco from Chal Tarkhan-Eshqabad near Rayy. Warminster: Aris and Phillips. \| pages pl.xxxiii, fig. 2; Benfey, Thomas. 2024, “Windādag’s Orders: Ten Unpublished Middle Persian Ostraca from Chāl Ṭarkhān-ʿEshqābād.” In Maria Macuch & Arash Zeini (eds.), Deciphering the Illegible: Festschrift in Honour of Dieter Weber. Wiesbaden: Harrassowitz Verlag. (Pages: 123-145) \| pages 20-21 |
| iedc:IEDC1265 | PM 37-33-21 (field no. CT-135/5) | Benfey, Thomas. 2024, “Windādag’s Orders: Ten Unpublished Middle Persian Ostraca from Chāl Ṭarkhān-ʿEshqābād.” In Maria Macuch & Arash Zeini (eds.), Deciphering the Illegible: Festschrift in Honour of Dieter Weber. Wiesbaden: Harrassowitz Verlag. (Pages: 123-145) \| pages 21-22 |
| iedc:IEDC1062 | Berk. 154, recto | Weber, Dieter. 2013. “Taxation in Pahlavi Documents from Early Islamic Times.” In Commentationes Iranicae: Сборник статей к 90-летию Владимира Ароновича Лившица, edited by S. R. Tokhtas’yev and P. B. Lur’ye, 171–81. St. Petersburg: Nestor-Istoriya. \| pages 176-177; Benfey, Thomas. 2024. "Middle Persian documents and the making of the Islamic fiscal system: problems and prospects." BSOAS 87: 395 - 420. \| pages 411-414 |
| iedc:IEDC1040 | Berk. 27, recto | Weber, Dieter. 2003. “New Information on the Date and Function of the Berkeley MP Archive.” Bulletin of the Asia Institute 17: 17–29, 27-29. \| pages 27-9; Weber, Dieter. 2013. “Taxation in Pahlavi Documents from Early Islamic Times.” In Commentationes Iranicae: Сборник статей к 90-летию Владимира Ароновича Лившица, edited by S. R. Tokhtas’yev and P. B. Lur’ye, 171–81. St. Petersburg: Nestor-Istoriya. \| pages 172-4; Benfey, Thomas. 2024. "Middle Persian documents and the making of the Islamic fiscal system: problems and prospects." BSOAS 87: 395 - 420. \| pages 408-411 |

## Input bindings

| File | SHA256 |
|---|---|
| `sources/local/public-texts-2026-09-20/berkeley/documents.json` | `abe347c57356666d6ebbb5984c792fef57c9c3ae7f9387fe972a1716054167dc` |
| `sources/local/public-texts-2026-09-20/berkeley/manifest.json` | `f1e7ae7efeaaad7de987fa2f71b40ce2d48fd9d26429582e20dfbe7d888773dc` |
| `sources/local/public-texts-2026-09-20/invisible-east/middle-persian.json` | `522fd18e024ba30fde22e867b6c72b53ed3a9e549dbe2f09453044a73d445692` |
| `sources/local/public-texts-2026-09-20/invisible-east/raw/731b861881223408575150879df686759f0b56bbb368dca6ab17edff1f5ade6f.source` | `94a517d2048e245e14e5d0c5ec025e8bc7a10ac16727ca01b7a0dec3287d9fb3` |
| `sources/local/public-texts-2026-09-20/invisible-east/coverage.json` | `575cda4d3510ac86970e819c3fc4393494d9c567281ebd4f3ebcbb854c189d6a` |
