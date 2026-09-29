# Semantic/source spot check — 2026-09-29

AI-assisted provisional review; not expert certification. This is a purposive 21-record high-risk check, not a random audit or an estimated corpus error rate. Eighteen selected records occur in the actual mixed train. Frozen data, source files, references, benchmarks, and merit results were not changed.

## Result

No confirmed extraction or alignment error remains in these 21 records after source-level review. This does not establish that all corpus translations or linguistic interpretations are correct. Specific source uncertainties and a corrected reviewer misreading are recorded below.

**Withdrawn candidate — S22GRAM-095.** My initial message incorrectly assigned a gloss from the next entry to kū. Re-viewing PDF page 75 / printed page 72 resolves the typography: kū has the two supplied Persian glosses and a reported-speech usage mention; the subsequent **ka** entry supplies «که، زمانی که». The canonical target and context preserve that distinction. There is no demonstrated missing explicit kū gloss, and no correction is warranted on this evidence. This correction supersedes the initial message. The exact ID is absent from all 28 serialized rows of `experiments/learning-diagnosis-20260929/references.jsonl`; absence of that ID alone is not a comprehensive semantic-overlap analysis.

**Withdrawn documentary suspicion.** MP0603 ends in āwišt in the archived TEI, canonical source, and decoded training text. A JSON newline followed by āwišt must not be read as the lexical sequence nāwišt. There is no observed negation reversal.

## Method and boundaries

Read canonical learning source, target, context and provenance; inspected archived source XML/TEI or actual PDF text, plus existing rendered page images for scanned S22 and Kanheri. Historical review labels were not used as the deciding evidence. Compared each of the 18 selected actual-train targets after decoding with the configured tokenizer against its canonical target: all 18 match, including structured CPD sense lists. Directly inspected conditioned S22 prompts and documentary decoded text. Mechanical equality establishes retained bytes/structure, not translation correctness.

No live source retrieval, model inference, source-data editing, benchmark editing, package installation, or archive rebuilding was performed. Source quotations below are deliberately brief; locators identify the complete supporting material locally. Source fidelity and language expertise are distinct: reproducing a published uncertain interpretation does not resolve that interpretation.

## Records actually audited

`Train` denotes presence in the actual mixed training JSONL, not proof of gradient consumption. Source keys are resolved in the evidence manifest below.

| # | Exact record ID | Train | Raw-source locator and semantic finding |
|---|---|---|---|
| 1 | `kosh:cpd:ff7bb53fd1df1619b01008bd275fa9817729d4d4:block:0` | No | CPD, entry ff7bb53… XML. ā retains the suffixed-pronoun usage condition. Omission of a dictionary illustration is not omission of its substantive gloss. |
| 2 | `kosh:cpd:f380125e9283c9d4910a0eb95d844aefb963b0a3:block:1` | Yes | CPD, entry f380125… XML, later form dastwarīh. Its two numbered senses remain separate; preceding dastwar senses are not incorrectly attached. |
| 3 | `kosh:cpd:99f6df4e02753a3d96f990e85a9c04142fb8c918:block:0` | Yes | CPD, entry 99f6df4… XML, ēr. Both noble/hero senses retained; subsequent ērīh senses excluded from this form. Decoded train retains both sense numbers. |
| 4 | `kosh:cpd:7504547dd231e0956b2b14fa49cd543bb19d8e7e:block:0` | Yes | CPD, entry 7504547… XML. hambāy retains companion/partner and adversary; apparently contrasting meanings are not collapsed or selected arbitrarily. |
| 5 | `FAINV:lex:9600eac496b25ee2eab3e306292c859c661639bb607a71632d9cff9cc7dcdd07` | Yes | GBD entry 747 XML. yask/jask are preserved as the published form bundle for the same Persian sense, avoiding artificial separate alignments. |
| 6 | `FAINV:lex:d994337c7b01a63d0ca08748407de325cf4f5c6c1ac720050e400da9992880a1` | Yes | RAF entry 74 XML. dāštan/dār- bundle and all four Persian meanings retained; infinitive and stem are not mistaken for independent senses. |
| 7 | `FAINV:lex:af87f9bbde61318b41553317cf6997382ff09102a85daf217974db2f0edf3e1d` | Yes | YZ entry 11 XML. Xᵛast retains the published Persian variant/meaning list and figurative qualifier. Historical layer is contextualized; etymological classification is not independently certified here. |
| 8 | `recovered:kosh:mmp:2357` | Yes | MMP entry 2357 XML, giyāw/guyāw. MP language mark, noun grammar, variants and generic meaning agree; excluded material is bibliography/cross-reference apparatus. |
| 9 | `recovered:kosh:mmp:5152` | Yes | MMP entry 5152 XML, wurrawišnīg/wurrōyišnīg. MP and adjective grammar retained, with both believing/devout senses; no noun coercion or Parthian relabeling observed. |
| 10 | `recovered:kosh:mmp:5418` | Yes | MMP entry 5418 XML. Three variants, noun status, size/greatness, plural qualification and Grandee-status sense retained; bibliography is not substituted for a sense. |
| 11 | `S22SUP-009` | No | S22 PDF 79 / printed 76, past-transitive paradigm. man dīd and Persian target align under the stated grammatical teaching context. This is a conditioned example, not unrestricted narrative translation. |
| 12 | `S22GRAM-082` | Yes | S22 PDF 74 / printed 71, prepositions paragraph. ō/bē and supplied Persian gloss align. Decoded prompt explicitly labels conditioned grammar. |
| 13 | `S22GRAM-095` | Yes | S22 PDF 75 / printed 72, conjunctions paragraph. kū target and reported-speech context agree with the source; initial proposed omission withdrawn after separating the following ka entry. |
| 14 | `S22CLAUSE-002` | Yes | S22 PDF 80 / printed 77, transitive-past table. tō mardān dīd hēnd preserves agent/patient roles and plural-patient auxiliary under the supplied grammar context. No role reversal observed. |
| 15 | `KANHERI-ARTICLE-01-OPENING` | Yes | Kanheri PDF 10 / printed 116. Invocation source and Persian target align within the opening scope. Parent transcription/translation year discrepancy lies outside this scope and is not evidence against the opening. |
| 16 | `KANHERI-ARTICLE-02-OPENING` | No | Kanheri PDF 11 / printed 117. Repeated invocation is a separate occurrence, not a new unique phrase; only one of these two opening IDs is in actual train. Distinct occurrence/witness identifiers retained. |
| 17 | `KANHERI-ARTICLE-02-DATED-ARRIVAL` | Yes | Kanheri PDF 11 / printed 117, source lines 2–4 and Persian rendering. Year 378, month/day and arrival scope agree. Do not transfer Article 01's outside-scope date discrepancy to this occurrence. |
| 18 | `openampd:MP0603:full` | Yes | TEI blocks MP0603_trc-p1 / MP0603_trans-p1, transcription lines 1–13. Names, year 38, 3 grīw/2 kabīz, damaged-text markers and final sealing clause agree at source/target witness level. Final āwišt is not nāwišt. |
| 19 | `openampd:MP5650:full` | Yes | TEI blocks MP5650_trc-p1 / MP5650_trans-p1, lines 1–10; Qal‘eh Iraj O.1 witness. Month/date fragment, commodities, Mihrād and 14 men agree. Gaps and unresolved lexemes remain source uncertainty, not invented completeness. |
| 20 | `S23-BERK25-TRANSACTION-RECEIPT` | Yes | Asefi PDF 8 / printed 9, Berk.25 transcription lines 6–8 and matching translation. Giving ten ewers of wine and receipt from the same named recipient align. Agent before the selected span and seal after it are outside the explicitly declared scope. |
| 21 | `S23-BERLIN26-DATE-RANGE` | Yes | Asefi PDF 14 / printed 15, Berlin26 transcription lines 3–7 and matching translation. Year 40, Day/Ādur through Amurdād/Ohrmazd, two months and 22 days retained. Footnote numbers are not incorporated as date quantities. Temporal-fragment task is appropriate. |

## Residual limits and reviewer action

The Kanheri parent Article 01 date disagreement is a source-level uncertainty outside the audited opening, not a demonstrated new defect in the selected units. Documentary damage and unrendered lexemes remain unresolved where the edition itself leaves them unresolved. CPD/MMP/Persian lexical checks establish form/sense scope against the archive; they do not prove that every published philological analysis is true. The S22 line-break mistake demonstrates why the provisional reviewer finding required independent visual confirmation.

Do not change frozen records based on either withdrawn candidate. A qualified human can inspect the identified source pages/entries and assess difficult historical-linguistic interpretations. No corpus-wide semantic pass, expert approval, benchmark change, or merit upgrade is claimed.

## Evidence manifest

Paths are project-relative. SHA-256 values identify the source snapshots actually checked and the selected canonical/training inputs. The PDF page number is the physical PDF page; printed page numbers are given separately above. Declared S23 source/target character spans are offsets into parent candidate text, not raw PDF character offsets.

- **CPD**: `sources/local/public-texts-2026-09-20/kosh-catalogue-sized-20260928/raw/4b77cb976e9af1d4842f40bed847ea51ee00a5177e28e8fee6239184d49220c3.source`; SHA-256 `7237ee7bad641b74437b153d52cb440ae74f4ab5e06c79acf742cba2e527a2c4`.
- **GBD**: `sources/local/public-texts-2026-09-20/kosh-catalogue-sized-20260928/raw/97ba0a3d0d7ece1956d8bc8189d4d1e43d489b5b84f61bf7ebcf9eda568118b3.source`; SHA-256 `152ffb8836437919ab088fd06998b022cec4fe2498f76e997745ea58f002ba1e`.
- **RAF**: `sources/local/public-texts-2026-09-20/kosh-catalogue-sized-20260928/raw/a6cc78e618ab7fff053bd49c85b998ea6dda5d72d8de0a884b514533e05072f8.source`; SHA-256 `461ec664394f89e5d47de48d6854d56098dc76ae321b145a7cecaeff2ed23573`.
- **YZ**: `sources/local/public-texts-2026-09-20/kosh-catalogue-sized-20260928/raw/5d2823270bb73f729d854374286771356c97869e8e32796a26cf998316a41c6d.source`; SHA-256 `2fbe2d35d9c68e0296234061f0b071d64e76f743895258d9e3d626192312b751`.
- **MMP**: `sources/local/public-texts-2026-09-20/kosh-xml-gaps-20260928/raw/329562c1d69f9b0c34e87420392df4dfd348c6ac90afe7062cd3e91a96b4ae0c.source`; SHA-256 `ce1b476f41a3faa004b863fb98a61eeb8b1a472ea43604c30a9f96b7690192a3`.
- **S22**: `sources/@RastarLib_زبان_پهلوی،_ادبیات_و_دستور_آن.pdf`; SHA-256 `207aeda5eae48227902f0f208f9b24fd5623627dd4ca589b217268e69596df92`.
- **S22 page 75 image**: `resources/local/dataset-expansion-20260928/s22/pdf-075.png`; SHA-256 `9e3d5983f8a05de559f4134d19945a7a06d38ece7ccce84d7d055ec92de98288`.
- **Kanheri**: `sources/local/public-texts-2026-09-20/qualification-source-search-20260928/raw/b385981ef422d96884dc19c958c274bf2e9efb0aefd923d83dbb71a2ae9fca1f.pdf`; SHA-256 `720d3db41ea76865c65d4a6875f0c03bf785dcae1a37f20dd6365a6e1501800f`.
- **MP0603**: `sources/local/public-texts-2026-09-20/berkeley/raw/ffc6ccb92c976cd76d5c9ad213d24503b7530cf5af412549ef52f11ef654addf.source`; SHA-256 `8627857141d78f7b5133b1a8be8276b22d59ecb03f6f7c17b8e4bea065f2e046`.
- **MP5650**: `sources/local/public-texts-2026-09-20/berkeley/raw/e68c7610d1a941356b24be98ee5e1f6cc0d5f426b2e01bb28354959807359317.source`; SHA-256 `07a773e8c6bfaa2ea03cabf8a69846f9f17f3a73f7fa68ede6387ded3d5705fb`.
- **Asefi**: `sources/01+-+Nima+Asefi.pdf`; SHA-256 `480670343730bdac72d1af78ff699d8cca69d71b908472a890c9ea1f51c6a1ce`.
- **documentary-en**: `resources/local/data-qualification-20260928/ready-v1/documentary-en.jsonl`; SHA-256 `d604e2b66e8c38de18b5e0675fbc9a58f739efd6c845d3cf0a3661542796924b`.
- **edition-spans-en**: `resources/local/data-qualification-20260928/ready-v1/edition-spans-en.jsonl`; SHA-256 `62bed1c4712b464326c82e2dc0e7bb2cdbd754a88a23471ef7208d05a1ca2bf1`.
- **inscription-fa**: `resources/local/data-qualification-20260928/ready-v1/inscription-fa.jsonl`; SHA-256 `c56c346750d23910a96ab6be3dab6f1bfc153bfa9286c5517581fa8dbe6de6cc`.
- **lexical-en**: `resources/local/data-qualification-20260928/ready-v1/lexical-en.jsonl`; SHA-256 `4d8c2489eca369d0d11a3364f5844cb5440d32eb53777c4ad138f5aff16c0f48`.
- **lexical-fa**: `resources/local/data-qualification-20260928/ready-v1/lexical-fa.jsonl`; SHA-256 `7979a688dc73a67f646920a668fbdeed6d1e21eb3f10f3810a59de9c427290fe`.
- **lexical-mmp-en**: `resources/local/data-qualification-20260928/ready-v1/lexical-mmp-en.jsonl`; SHA-256 `8411819339113f16ba45dab1c67ce8a044cb6ec5df3d589e912772ba207ff2aa`.
- **pedagogy-fa**: `resources/local/data-qualification-20260928/ready-v1/pedagogy-fa.jsonl`; SHA-256 `d96d95610ac354222029d30ae0252425df57859ab8f23bfd14d68a6b71a8edd6`.
- **Actual mixed train**: `resources/local/mixed-supervision-20260929/data/train.jsonl`; SHA-256 `c32a7f21639c34107fd4a86c1c8dae3a8815b40c8107ff8c3075e0167535dc4a`.
- **Pending diagnostic references**: `experiments/learning-diagnosis-20260929/references.jsonl`; SHA-256 `ff4548af6dced50411e15628c3034f19d54a5a9a64718d24bad5925ddaea6d42`.
- **Tokenizer**: `resources/local/cloud-pilot-qualified-20260927/tokenizer/tokenizer.json`; SHA-256 `cc8d3a0ce36466ccc1278bf987df5f71db1719b9ca6b4118264f45cb627bfe0f`.
