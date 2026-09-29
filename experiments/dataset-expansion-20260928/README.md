# Expanded source resource before the next training decision

28 September 2026. **A larger, checked source-resource checkpoint is saved; the next training dataset is not yet released.** The last NLLB run used 2,237 qualified Pahlavi-to-Persian pairs. Those exact historical training bytes remain unchanged. New material below is recovered source evidence, not evidence of improved model quality.

## Concrete additions

| Resource | Before this expansion | Saved now | What the count means |
|---|---:|---:|---|
| Kosh structured resource records | 26,377 flat form/meaning groups | 31,918 typed records | Includes complex entries, references and explicit holds; not 31,918 sentence pairs. |
| Previously quarantined observations recovered | 0 in this version | 5,541 | 3,101 MacKenzie CPD entries; 1,990 explicitly Middle Persian MMP entries; 328 markup-bearing NMP/PYV entries; 122 definitions/cross-references. |
| S22 published teaching evidence | 7 prior clause examples | 7 prior + 113 additional records | 9 additional clauses, 16 finite paradigm cells, 23 finite predicates and 65 derivational form/gloss records. |
| Archived MP–English document packets | Unqualified 46 Berkeley + 14 Oxford associations | 53 retained, 7 explicitly held | 42 Berkeley and 11 Oxford documents; document association is not sentence alignment. |
| Parsig format-recovery packets | 4 identified cases | 4 source-bound reversible views | Existing translations with citation/token-format issues, not invented new targets. |
| Historical trained pairs | 2,237 | 2,237 | Zero new training admissions; no paid job or local model download. |

The resource records have different units. Adding the rows of this table would produce a misleading training-size total.

## What became more useful

All 31 Kosh collections now have explicit source/language/lineage decisions. CPD's ordered senses, grammatical details and examples survive separately, including unresolved form/sense associations. The MMP subset is selected using explicit source-level `MP` labels; Parthian/mixed cases are not silently relabeled. NMP/PYV markup and missing-glyph indicators survive rather than disappearing in flattened text. Definitions lacking a main translation gloss are kept as references.

The derived export applies the previous review: six punctuation-only primary meanings and three compound-scope records are held. Another 1,956 flat groups contain published glyph placeholders and remain source-gap references. There are 26,402 structurally usable flat lexical candidates, still requiring appropriate language/context/lineage decisions before a learning view. The four known protected Kosh families remain outside the resource payload, with their dispositions recorded.

The inherited review of 200 ambiguous-form cases preserves 49 paraphrase candidates, 46 differing published meaning/role cases, 103 context-required cases and two compound-scope cases. These are provisional judgments, not proof that every same-spelling word has one meaning. Published uncertainty, synonyms, homographs and grammatical roles are not merged by majority vote.

## Non-duplicate coverage

The 26,402 flat candidates contain **17,094 distinct normalized complete form strings**; 14,405 are absent as exact contiguous token sequences from TRAIN2237. This is spelling/form coverage, not 14,405 proven new words or meanings. Complex CPD entries are excluded from this statistic because their forms require scoped interpretation.

The newly recovered MMP subset contributes 2,054 distinct full form strings: **1,332 absent from the old flat candidate pool**, and 1,335 absent from historical training by the stated token comparison. Different comparisons have different denominators. The reused normalization is NFC/casefold/whitespace with boundary-punctuation token matching; it is not a model tokenizer and does not conflate diacritics or expand variants.

The exact form/gloss duplicate ledger identifies 129 clusters containing 270 records; provenance is retained rather than counted as independent evidence. Different gloss strings are not automatically different senses, so this does not certify complete semantic deduplication.

The 113 new S22 records contain 110 distinct source strings and no exact source-string repeats of the original seven. Three printed forms repeat with different grammatical contexts/targets; they must remain grouped. The new packet has 152 source and 168 target whitespace terms, showing why 113 short records should not be mistaken for 113 substantial passages. Its first nine examples belong to five related teaching families, not nine independent manuscripts.

## Direct website cross-check

The user's requested [targeted live checks](ONLINE-CROSSCHECKS.md) retrieved five source entries across four small queries. All returned XML matches the archived copy. GBD489 resolves the reading of kištan toward cultivation; GBD15–16 confirm that the questionable short-form/long-phrase mappings already exist online. Those holds therefore remain. Rechecking the same website verifies fidelity, not independent scholarly agreement.

## Files and reproducible checks

- [Lexical manifest](lexicon-summary-v1.json), [independent review](LEXICAL-QA.md), [all collection decisions](COLLECTION-NOTES.md).
- Lexical payloads: `resources/local/dataset-expansion-20260928/lexicon-v1/`: lexical-resources, observation-dispositions, exact-pair-duplicates and collection-decisions JSONL.
- [S22 clauses](S22-EXPANSION.md), [S22 morphology supplement](S22-SUPPLEMENT.md), [archive recovery](ARCHIVE-RECOVERY.md), [four Parsig cases](PARSIG-FORMAT-RECOVERY.md).
- [Combined package manifest](package-manifest.json) binds the frozen lexical output and all four candidate packets at their correct grains. The previous unified corpus remains an immutable historical snapshot; this package is its explicit later addition.

Run with the existing shared Python interpreter:

```powershell
& '[USER_HOME]\.venvs\codex-science\Scripts\python.exe' -B -X utf8 experiments/dataset-expansion-20260928/expand.py --check
& '[USER_HOME]\.venvs\codex-science\Scripts\python.exe' -B -X utf8 experiments/dataset-expansion-20260928/check_package.py
```

The lexical check rebuilds the outputs deterministically and compares every byte. The combined check verifies source/PDF/image/archive bindings, citation reconstruction, frozen training identity and coverage calculations. Neither check proves every translation linguistically correct. Final paths refuse overwrite; no historical data is removed.

## Remaining high-value work before training design

1. Finish S22's remaining explicit lexical pairs on PDF70–76, then its glossary as a separate extraction task. The complete book is locally available; the current grammar pass is substantial but not an exhaustive book transcription. Keep source quotations separate from generic morphology and screen their work lineage.
2. Finish scoped CPD meaning/use qualification and resolve the specific source-page problems. The recovered XML is now available in useful structure; guessing the missing associations or glyphs would reduce reliability.
3. Review and align the 53 retained authentic document translations, resolve the seven named witness/edition holds, and compare any additional book editions without counting the same witness twice. English remains explicitly labeled auxiliary evidence; no Persian gold is synthesized.
4. Obtain/inspect the identified Nasrollahzadeh inscription edition pages and remaining Parsig attribution/reading evidence. A populated translation field alone does not settle those defects.
5. Freeze qualified task-specific training views, family exclusions and sampling units from the resulting resource. Only then choose the controlled training comparison under DATASET-READINESS.md and the unchanged USD25 cumulative cap.

This checkpoint expands the material we can responsibly work from. It does not claim a worldwide maximum dataset, error-free scholarship, satisfactory model quality, or admission to start training.
