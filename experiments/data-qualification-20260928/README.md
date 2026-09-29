# Source-qualified supervision release v1

28 September 2026. **The reviewed release is frozen and its saved outputs passed independent verification. No training was started.** This completes the declared source-qualification pass; it does not claim exhaustive world literature coverage or that every available book has been semantically qualified. The original 2,237 Persian translation pairs remain byte-identical.

The canonical local package is [ready-v1](../../resources/local/data-qualification-20260928/ready-v1/), bound by [release-v1.json](release-v1.json). Its ten files total 14,873,104 bytes. Raw books, downloaded responses, earlier staging and rejected readings remain preserved at their original locations. Git contains the code, source packets, decisions and receipts; ignored local resources are required to reproduce the release.

## What changed since the last training

| Resource | Qualified units now available | Meaning of a unit |
|---|---:|---|
| Historical Persian control | 2,237, unchanged | Existing translated paragraph/passage pair; not a new addition |
| Six Persian dictionary families | 2,676 | Complete source-scoped form/meaning inventory |
| MacKenzie CPD, English | 3,506 | Complete direct-sense block, with form and scope preserved |
| Manichaean Middle Persian dictionary, English | 1,426 | Generic lexical inventory with grammatical role and domain |
| Amouzgar–Tafazzoli Persian teaching material | 240 | Grammar/form/meaning context; only 16 are labeled pedagogical clauses |
| Documentary editions, English | 57 | 19 whole passages and 38 annotated fragments, across 52 witnesses |
| Kanheri, Persian | 6 occurrences / 4 pair types | Supported exact spans from already catalogued witnesses |
| Asefi article, English | 4 | Two predicate scopes and two temporal fragments |

The lexical components total 7,608 source-scoped inventories covering **6,253 distinct complete normalized form strings**, not 7,608 new words or sentence translations. Orthographic normalization here is NFC, casefold and whitespace only; spelling systems and compound boundaries are not equated. English labels remain English. No generated Persian translation was substituted for a published target.

The change is principally lexical coverage and qualified grammatical evidence. Contextual translation material grew much less. This is a substantially more useful resource than the earlier unqualified 26,377-group queue, but its size alone cannot establish a numerical probability of improvement or a future model score.

[Coverage census](coverage-v1.json) records rows and published-text volume. The old control contains 37,492 source and 41,985 target whitespace units. The new documentary, inscription and article spans contain 2,075 source and 2,810 target units together; teaching material adds 328/368. Dictionary counts include all preserved variants and senses. These are **not model tokens**; tokenizer, prompt and exposure counts depend on the later training design.

## Quality and multiple meanings

- Six Persian families received full literal/anomaly review and exact independent reconstruction from their original XML. Of 2,799 groups, 2,676 qualified and 123 remain held. The 207 [shared-form bundles](../../resources/local/data-qualification-20260928/persian-v1/shared-form-bundles.jsonl) preserve cross-source meaning differences without declaring one source the winner.
- MacKenzie uses complete XML sense structure and the correction evidence, with print/website checks where documented. All 54 generic correction checks were reconciled. Website and PDF are often the same underlying source, not independent corroborating dictionaries. Of the CPD qualification units, 720 remain held, including malformed or ambiguous cases.
- All 1,990 declared MMP entries were reviewed; 1,426 qualified and 564 remain held. The independent critic checked every structural join and selected span, then sampled complex semantic cases, all variant bundles and risky omitted tails. This is not a second exhaustive expert reading of the entire dictionary.
- Homographs, multiple senses, variant spellings, grammatical person/number, register and compound scope stay explicit. Form-by-sense Cartesian expansion is prohibited. Grammar context is part of the conditioned auxiliary task; these records must not be presented as unconditioned sentence translations.
- Source typos or contradictory quantities normally remain held. Five narrowly documented derived repairs were independently supported: three S22 target readings/list boundaries and two single-character documentary target typos. Raw evidence is unchanged; every derived row carries its decision.
- The 37 surface source/target repetition groups are a diagnostic ledger, not instructions to merge different grammatical contexts or treat repeated witnesses as independent evidence. Training sampling must respect source, witness and task grouping.

“Source-qualified” means traceable published evidence with checked extraction and bounded scope. It **does not mean error-free, specialist-certified or legally cleared for every possible downstream use**. Source attribution and recorded use restrictions remain attached through provenance. No review disagreement was solved by manufacturing a target.

## Exclusions and protection

The release records 2,317 scoped exclusion decisions. This includes 123 Persian, 720 CPD and 564 MMP holds, all 888 newly extracted S22 glossary groups, four Parsig format-recovery cases, unresolved grammar, documentary boundaries, restricted inscription/article spans and an already-covered seal formula. It is not an exhaustive row count of every held parent or every rejected item in prior corpora.

All 888 S22 glossary groups remain reference-only: the book selects meanings from mixed readings that include protected works, and entry-level lineage is unresolved. The two new Pasargadae frames and the uncertain full Kanheri/S23 parents also stay out. Known uncertainty, damaged readings, numeral conflicts and unsupported speaker/name assignments are not silently converted into certain prose.

All 16 protected work families remain excluded under the existing policy. The final copy screen compares source spans against archived protected source text only; it is a bounded one-way exact normalized containment check, not universal paraphrase detection. Generic vocabulary overlap does not make an unseen-vocabulary claim valid. Full XML, contextual quotations and held neighboring clauses stay outside the learning fields. Raw review reports and provenance are not serialized, while explicitly selected grammatical qualifications remain visible as the conditioned task's context.

The fixed benchmark is unchanged and was checked by byte hashes. The [plan](PLAN.md#benchmark-exposure-incident) records an accidental additional root exposure to two reference excerpts during an earlier broad search; none was used to construct this release. Treat the benchmark as the established, repeatedly seen regression standard, not a fresh blind test.

## Remaining source limits and next boundary

The strongest specific access gap is Nasrollahzadeh's **کتیبه‌های خصوصی فارسی میانه ساسانی و پساساسانی (گورنوشته، یادبودی)**, volume 1 (1398/2019). It could help adjudicate 95 inscription source-edition failures, but those are not 95 promised additions. An [exact book listing](https://taaghche.com/book/97482) was found; it was not purchased. The accessible earlier Kanheri article was acquired and reviewed, including a year disagreement that remains unresolved.

[New-source research](NEW-SOURCES.md) and [project source coverage](../../SOURCE-COVERAGE.md) retain the other limits: Nyberg and further primer/scan pages, German and markup-bearing dictionary resources, source-only corpora lacking aligned translations, uncertain work identities, missing attribution and related editions with unresolved overlap. They remain references or review candidates. Neither raw availability nor a populated gloss admits them automatically.

The next discussion can use this frozen pool to choose the task mixture, model, sampling and one justified comparison. Final model-specific serialization for the seven new components must expose only `learning` fields and preserve their context. The byte-identical historical control has its original schema: use a separate explicit `text`/`target` whitelist, never its old token arrays, credits or full record. Tokenizer/template census, source-group sampling, use-scope review and paid-run readiness still precede execution. The USD25 cumulative cap remains in force. No model weights were downloaded, and no training, paid job, new Gemini task, Drive action or credential change occurred in this phase.

## Verification and reproduction

[Final independent release review](RELEASE-REVIEW.md) verifies all seven learning projections, all ten persisted files and 144 input bindings. [Package QA](PACKAGE-QA.md) records the component reviewers, execution results and limits.

```powershell
& '[USER_HOME]\.venvs\codex-science\Scripts\python.exe' -B -X utf8 experiments/data-qualification-20260928/freeze_release.py --check
```

The command rebuilds and compares the complete frozen release. It does not train. The actual overwrite-refusal test passed and left every output and receipt unchanged. The smaller solution here is the existing local JSONL archives plus a typed, checksummed learning view; another database or downloading model weights would not improve source qualification.
