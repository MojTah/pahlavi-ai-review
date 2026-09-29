# Candidate content review — 28 September 2026

Status: provisional AI review; **zero new training admissions**. These are actual content findings, separate from the earlier full structural/integrity audit. Historical TRAIN2237 and all evaluation sets remain unchanged. Root integrates three independent read-only reviews and separately records Gemini results. Published pages/manuscripts not directly inspected in this pass are explicitly unresolved.

## Scope and evidence

| Review | Actual coverage | Reviewer |
|---|---|---|
| Unused Parsig material | Classified 468 queue rows; examined 20 selected passages with raw source, translations, notes and neighboring context | `/root/nllb_source_method` |
| Printed teaching examples | All seven S22 candidates, using existing page/image evidence and grammar context | `/root/seen20_blind_a` |
| Persian dictionary subset | Structural comparison of all 2,848 raw records / 2,799 staged groups in six collections; semantic inspection of 24 representative groups | `/root/finetuning_kb_research` |
| Same-form/different-meaning wording | All 200 cases / 455 groups compared locally; original XML checked for suspicious text and every multi-form group | `/root`; three preliminary Gemini judgments separately recorded |

This does **not** mean 26,880 queue items have all received linguistic review. A model judgment is not specialist certification. Correct extraction, plausible meaning, source attribution, work-level split clearance and permission to reuse are separate gates.

The executed [200-case ledger v2](decisions-v2.tsv) has 49 paraphrase candidates, 46 different published senses/roles, 103 context-required cases and two form-scope cases. Counts classify comparisons, not accepted words or unique verified senses. All decisions retain the original source-group and observation IDs in the frozen joined overlay. V1 is preserved; independent criticism corrected one overconfident relationship classification and narrowed one imperative explanation.

## Explicit meaning holds

The existing staging predicate missed six targets containing only uncertainty marks and punctuation. All six remain unchanged as source evidence, with a `WITHHOLD_NO_LEXICAL_MEANING` overlay in `placeholder-holds.jsonl`. No replacement gloss is invented.

| Observation | Form | Published target |
|---|---|---|
| kosh:gbd:361 | pasazagīha | `(؟)` |
| kosh:ps:25 | ʾhwʾdšny | `'?'` |
| kosh:ps:130 | drīdāg | `'?'` |
| kosh:ps:247 | nhlʾn- | `'?'` |
| kosh:ps:384 | tāhegar | `'?'` |
| kosh:wdpw:1753 | sapahāgān | `(?),` |

Comments offering possible interpretations are retained as comments, not silently promoted to gold targets. This is a review overlay on already non-admitted staging; original v4 artifacts are immutable.

## Twenty Parsig passage decisions

Evidence: `sources/local/parsig-2026-09-20/exports/text-units.jsonl`, frozen in the unified-corpus manifest. All 468 reviewed queue IDs lie outside the current 16 protected work IDs, but that does not clear all edition/manuscript lineage questions. Of 468 rows, 406 have Persian and 62 are source-only headings. Of 406, 122 are known repeated pairs, 277 belong to the first rejection pool, three contain literal `<pad>`, and four previously unexplained exclusions are 137001004, 137001006, 150000055 and 302002000. These categories describe earlier exclusion history, not new training acceptance.

| ID | Review disposition | Specific evidence / remaining check |
|---|---|---|
| 201001001 | WITHHOLD_NUMERAL_MISMATCH | Source `se-sad haftād hašt` gives 378; Persian explicitly gives 376. Root confirmed both raw strings. Check Nasrollahzadeh 1398, vol. 1 p.184 before choosing either reading. |
| 151014011 | WITHHOLD_ALIGNMENT | Positive comparative source ending versus Persian negation and explanatory/modal clause; neighboring passages and disorder notes suggest alignment/reading trouble. Root confirmed the mismatch; edition realignment required. |
| 151025005 | WITHHOLD_PUNCTUATION_CONTEXT | Persian question mark after the preceding passage introduces an answer; verify sentence function and attribution. |
| 137001006 | WITHHOLD_EDITION | `har dō hēnd` versus noted Pakzad reading `har dō(w)ān mēnōg`; retain both readings. Forthcoming edition attribution remains unresolved. |
| 151035029 | WITHHOLD_ATTRIBUTION | Note explicitly says absent from Tafazzoli 1379 p.51; cannot inherit that translator's credit. |
| 151039009 | WITHHOLD_ATTRIBUTION | Note explicitly says absent from Tafazzoli 1379 p.54. |
| 221001001 | FRAGMENT_ONLY | Three surviving source words versus extensive bracketed daughter/tomb/construction restoration. Do not train the restoration as wholly attested source. |
| 209001001 | QUALIFIED_EDITION_REVIEW | Names vary; construction/calendar supplied in brackets. No demonstrated semantic contradiction; edition check outstanding. |
| 208001001 | QUALIFIED_EDITION_REVIEW | Witness-list gaps and final patronymic need source-page verification. |
| 206001001 | PROMISING_WITH_SUPPLEMENTS | Prayer, Christ, patronymics and relative clause align; `[cross]` is contextual supplementation. Check Nasrollahzadeh vol.1 p.253. |
| 202001001 | PROMISING_WITH_RESTORATION | Blessing and names align; reconstructed `[ān]` and filiation remain qualified. Vol.1 p.191. |
| 203001001 | CONTEXT_REQUIRED | Property list/giving align; `pad abzūd…` needs clause context. Vineyard/fruit/yield alternatives are not automatically mistranslations. Vol.1 p.194. |
| 214001001 | PROMISING_DATE_ALIGNMENT | Numbers 242, 260, 15 and 28 align; multiple eras are not themselves errors. Vol.1 p.115. |
| 218001001 | QUALIFIED_RESTORATION | Year six and 200 staters align; CE/day gloss is editorial. Vol.1 p.94. |
| 224001001 | QUALIFIED_RESTORATION | 245 and 343 align; Arabic parallel 265 may use another era. Names and `[dirham]` are restored. Vol.1 p.232. |
| 151043031 | FORMAT_RECOVERY_CANDIDATE | Ten men's food/satiety align. Literal editorial `<pad>` collides with tokenizer token: preserve raw source and design reversible serialization. Anklesaria 1913 p.129 / Tafazzoli 1379 p.58. |
| 151015025 | QUALIFIED_FORMAT_RECOVERY | Literal `<pad>`; examination reading is context-supported. Preserve `*wizōstan` and scope of `nē abāyēd`. Anklesaria p.65 / Tafazzoli p.38. |
| 150000054 | QUALIFIED_FORMAT_RECOVERY | Literal `<pad>`; excess wealth/three groups align, disputed `tēmās` remains qualified. Dhabhar 1930 pp.8–9 / Goshtasb-Hajipour 1392 p.78. |
| 510000002 | CITATION_FORMAT_RECOVERY | Stray U+0559 `ՙ` after citation; dialogue roles, oath, negation and questions align. Repair only citation wrapper after review; do not alter disputed names. Boyce 1975 pp.44–45 / Mostafavi Kashani 1401. |
| 151048022 | WITHHOLD_ATTRIBUTION | Stars/fravahrs alignment plausible, translator credit absent; Anklesaria p.137. |

Root independently checked the numeral and alignment defects, the three literal `<pad>` cases and the stray citation character in the raw export. No source correction or serialization transformation has been applied.

## Seven S22 teaching examples

Source: `sources/@RastarLib_زبان_پهلوی،_ادبیات_و_دستور_آن.pdf`, PDF pages 80–81 / printed pages 77–78. Existing extraction receipts and page-image verification remain authoritative. These are published pedagogical examples, not seven independent manuscript attestations. All remain staged pending lineage/use gates.

| ID | Published pair | Contextual decision |
|---|---|---|
| S22CLAUSE-001 | `man (tō) dīd hē` → من تو را دیدم | Supported: first-person observer, second-person patient; auxiliary agreement does not make the patient the observer. |
| S22CLAUSE-002 | `tō mardān dīd hēnd` → تو مردان را دیدی | Supported: second-person actor, plural patients; no plural actor inference from auxiliary. |
| S22CLAUSE-003 | `man mardān dīd hēnd` → مردان را دیدم | Supported: Persian verb retains first-person subject without explicit pronoun. |
| S22CLAUSE-004 | `mardān ōzad hēnd` → مردان کشته شدند. | Qualified: book's passive interpretation supported; no general rule that every omitted agent implies passive. |
| S22CLAUSE-005 | `um tō pursīd hē` → از تو پرسیدم | Qualified: first-person questioner/second-person addressee; page-specific construction, not a universal agreement rule. Initial connector omission is not licensed generally. |
| S22CLAUSE-006 | `um tō dīd estē` → ترا دیده‌ام | Supported perfect; preserve printed spelling `ترا`, avoid unsupported extra aspectual claims. |
| S22CLAUSE-007 | `raft estād hēm` → رفته بودم | Supported first-person past perfect; auxiliary is not another physical standing event. |

001/006 and 002/003 share teaching templates. They must not inflate counts of independent evidence or be separated across data splits as unrelated passages.

## Dictionary lineage and polysemy

| Collection | Groups | Source / qualification |
|---|---:|---|
| da | 102 | Navvābī, Draxt ī āsūrīg; publisher `pal→fas` with historical Parthian-layer qualification. |
| dk8 | 480 | Naẓarī-Fārsānī, Denkard VIII specifically; 284/483 raw rows contain a non-placeholder attestation field. |
| dmx | 1,030 | Tafazzoli, Menog-i Xrad glossary; same work family as Parsig151, not independent new witnesses; no attestation field in these records. |
| gbd | 773 | Bahar, Bundahishn glossary; same work family as Parsig137, different edition. One punctuation-only target held, leaving 772 content candidates. |
| raf | 285 | Rezaei-Baghbidi, Ādurfarnbay legal responsa; 198/285 raw rows have attestation references. Same author does not make it Parsig135. |
| yz | 129 | Navvābī, Yādegār ī Zarīrān; historical language-layer qualification; 53/141 raw rows have attestation references. Not Parsig133. |

All 2,799 staged targets match their original XML sense after NFC/whitespace normalization; this proves extraction correspondence, not universal linguistic correctness. Full catalogue attribution and original XML are in the frozen packets. Attestation strings are references, not inspected manuscript passages.

Concrete distinctions to preserve:

- `mādayān`: noun “مجموعه، کتاب، نوشته” versus adjective “اساسی، اصلی”; retain grammatical role and source, not a single winning gloss.
- `frāz dādan`: creation versus handing over; preserve both and request context. The supplied records lack usable attestation references.
- `abēbar`: “بی بر، بی سود” versus “بی بر، بی فایده” is a likely paraphrase; not evidence of two independent senses.
- `axtar` in `kosh:dmx:1` enumerates multiple meanings inside one entry. The existing cross-record different-wording flag does not detect internal polysemy.
- `multiple_published_meanings_for_form_group` means differing strings, **not proven linguistic polysemy**. Related senses, homographs, historical variation and editorial paraphrases need distinct treatment.

Additional root findings from the 200-case pass:

- **Compound scope:** original XML for `kosh:gbd:11`, `:15` and `:16` lists a short form together with a longer phrase. Their meanings describe practicing righteousness, righteous kingship and harming a righteous person. Preserve the full records, but withhold any independent short-form-to-phrase-gloss mapping until the source layout is resolved. This is a mapping risk, not a claim that the published phrases are wrong.
- **Source text defects remain possible on a website:** `دیگرف`, `نخستف`, `هشتنف`, `محققاف`, `نجام`, `مادن`, `نحراب` and other suspicious spellings are already in original XML. They were not introduced by this extraction. Retain raw text and check a source page before creating corrected targets.
- **Unvowelled Persian can create false contradictions:** DMX853 gives `کاشتن، کشتن`, while GBD489 gives `کاشتن، کِشتن`. Do not invent a killing sense merely because the unvowelled Persian string can also be read that way.
- **Internal lexical/grammatical polysemy:** `ēstādan` explicitly includes perfect auxiliary use alongside lexical standing. A token-to-single-gloss dictionary would lose exactly the construction information this project needs.
- **Distant meanings are not automatically errors:** scribe-name/horse, respect/desire, salvation/division and urinating/sucking warrant source-headword checks, but this pass does not discard either reading on model intuition.

## Next admission gate

First finish source-grounded review overlays and disagreements, prioritizing the four format-recovery passages and dictionary meaning/lineage issues. Resolve or explicitly leave blocked edition evidence; retain context-qualified multiple senses. A frozen training expansion requires complete readiness checks and an explicit source-family split/weighting decision. Neither agreement between models nor a large candidate count opens that gate.
