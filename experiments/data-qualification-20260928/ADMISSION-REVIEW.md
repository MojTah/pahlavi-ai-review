# Admission and leakage review — 28 September 2026

Reviewer: `/root/nllb_final_preflight_review`, independent of the release writer. Scope: admission policy and a later release checklist, not a new linguistic certification or training authorization. Only this report is written by this reviewer.

**Policy verdict: the proposed source-qualified pool is justified with the rules below. Lack of specialist certification alone is not a blanket hold. Actual release approval remains pending inspection of its records and reconciliation.** The six proposed Persian glossary families are a practical first release; they must not inherit a stronger correctness claim from the historical TRAIN label.

## What qualification means

A qualified item faithfully represents an attributable published source at a declared task and unit. Its source/target relationship, language, boundaries and relevant work lineage are established; known defects are resolved or the affected unit is held. Qualification is not proof that the publication is infallible, that every item received an independent philological review, or that additional training will improve the model.

The same word may correctly have several meanings. Preserve the complete published form bundle, roles and sense inventory at the qualified scope. Do not turn one inventory into every possible form/sense combination, select a winning meaning by frequency or reviewer vote, or count alternate editions as independent attestations. A multiword gloss is not automatically a translated sentence.

Use separate usable classes: lexical sense inventory, printed morphology context, pedagogical clause, and authentic aligned passage/document. Preserve contextual examples and unqualified source material in the archive, outside the learning payload. Count the classes separately. Dataset qualification does not open a paid job or decide tokenizer serialization.

## Concrete admission decisions

| Material | Admit when | Hold or restrict when |
|---|---|---|
| Generic dictionary inventory | Attributed edition/entry; literal extraction; defensible headword/form-to-sense boundary; complete meanings and roles within the declared scope; explicit language; no identified protected-work derivation of the admitted content. A batch of uniform, clear structures may use deterministic full-record validation and an independently checked interpretation of that structure. | Ambiguous association, damaged headword/gloss, placeholder-only meaning, unresolved language, known contradictory source evidence or a meaning whose interpretation requires an uncleared quotation. Mark the actual review method; do not claim every batch member received semantic adjudication. |
| Work-specific glossary | The source work/edition is identified and outside the protected families; preserve the glossary's wording, context restrictions, grammar and attestations. | A protected work remains protected even if its glossary looks generic. A mixed-source glossary needs origin clearance for each admitted scope. |
| Printed morphology/example | Image-verified transcription and target; grammatical heading/context and alternatives retained; editorial signs preserved; lineage cleared. A printed paradigm cell can qualify as that cell. | Generated expansion of a paradigm, unsupported changes of person/tense, unidentified quoted passage, uncorrected erratum, or a target detached from its governing heading. Do not relabel cells as independent full clauses. |
| Pedagogical clause | Its complete printed source and corresponding target have the same boundaries; substantive participants, negation/modality and editorial uncertainty survive; quotations are identified and cleared. | A fragment is silently completed, neighboring target text is attached by proximity, or a protected quotation is renamed a textbook example. Five related teaching families are not nine independent manuscripts. |
| Authentic passage/document | Edition/witness and translation layer are identified; the same source span is covered, with explicit omissions/gaps retained. A complete document may qualify at document grain without forced sentence segmentation if its full translation coverage is actually verified. | Metadata association alone, mismatched coverage, unresolved witness/edition identity or contradictory interpretation. Equal line numbering does not establish alignment. A partial translation needs a defensible bounded source span before admission. |
| Four Parsig format recoveries | Exact original fields and citations remain recoverable; the prior content decision and known concern remain visible; the task-specific scope is accepted explicitly. | Reversible formatting is mistaken for semantic approval. A prior `FORMAT_RECOVERY_CANDIDATE` is not automatically promoted by a successful parser or display patch. Token compatibility is a later view check; JSON escaping alone does not resolve a decoded special-token collision. |

The six Persian Kosh families `da`, `dk8`, `dmx`, `gbd`, `raf`, `yz` may therefore supply qualified lexical inventories. Keep their source-defined grammatical strata and edition distinctions; do not silently equate a transmitted Middle Persian form, an older Parthian layer and a reconstruction. `dmx`/`gbd` overlap with existing TRAIN work families, so their lexical records do not automatically constitute new independent contexts. The proposed counts of 2,799 groups / 2,795 structural candidates are the lead's current release scope, not independently re-counted admissions in this policy review. Known content-review decisions still apply after structural filtering.

## Completeness, uncertainty and known source errors

“Complete” must have an object: complete within this published entry, this explicitly separated derivative block or this printed grammatical context. It does not mean all meanings across the language. Preserve source ordering and numbered senses; do not infer a sense count from semicolons or gloss-string differences.

An ambiguous derivative or quotation need not block a demonstrably separate generic entry. Record the excluded node/span and reason, and label the parent entry partially qualified. Never call a headword's admitted subset a complete inventory if known senses for that same headword were removed. If separation itself changes the meaning or association, hold the affected inventory.

Published question marks, starred readings, brackets, alternatives and modality are content. They must survive. Unresolved readings may remain source-qualified uncertain evidence, but are not certain translation labels. The initial ordinary lexical/translation learning view should exclude unresolved assignments rather than silently flatten their uncertainty. This is a task restriction, not deletion of the scholarly evidence.

A known typo or wrong mapping cannot qualify merely because extraction matches the website. Apply a published erratum or a directly checked correction in a derived field, with the original, corrected value, exact authority/page and decision preserved. Agreement between a live page and its archived copy proves fidelity, not independent corroboration. A differing dictionary gloss may represent context or polysemy; do not “correct” it by majority vote. If the contradiction is unresolved, hold that scope. Do not reopen every otherwise clear entry merely because dictionaries can contain errors.

## Held-out protection and the generic-definition distinction

Keep the full existing protected union: `103, 104, 110, 111, 112, 114, 116, 117, 118, 120, 124, 130, 132, 138, 152, 517`. PAL's five-work policy is a subset, not permission to train on the other DEV/TEST works. Known Kosh aliases `hkr → 117`, `sns → 138`, and `wz/mz → 152` remain excluded. The restriction includes alternate editions/witnesses, translations, reverse pairs, paraphrases, source-only adaptation and retrieval evidence.

A general dictionary is not disqualified merely because a common word also occurs in a held-out work. An independently published generic definition can be qualified as generic lexical knowledge; that prevents any later claim that the word was unseen. Conversely, a quoted protected passage, its translation, or a context-dependent gloss derived from that protected work cannot be laundered by deleting its citation. Source/work provenance decides this distinction, not text length or the absence of a benchmark ID.

For mixed dictionary entries, retain the raw tree but make an explicit field/node allowlist for the learning view. Protected or uncleared quotations, translations, contextual notes and attestations must not enter it through nested XML, metadata, retrieval chunks or serialization of the whole source record. A protected reference attached to a sense needs a source-scope decision: it is not safe to assume the sense is generic solely because the quotation was omitted.

**S22's glossary requires a different gate from its generic grammar tables.** Its introduction says meanings were selected from textbook readings, including protected works. An entry with unresolved originating reading stays out of the learning view. Trace the entry to a cleared reading, or qualify an independently sourced general-dictionary inventory on its own evidence. The latter does not clear the S22 record or make it a second independent example. Do not target extraction to known benchmark words or answers.

Unknown aliases are not automatically clear, but qualification need not prove an impossible absence of every historical quotation. Use identifiable work/witness metadata, citations, the established alias ledger and relevant existing source fingerprints; route concrete ambiguity to a hold. Report the residual limit as “no identified protected lineage under these checks,” not universal contamination freedom. This reviewer did not open benchmark answers to perform semantic matching.

## Exposure incident and evaluation claims

The lead's accidental exposure to two reference excerpts is recorded in PLAN.md. No excerpt is reproduced here. Preserve that incident and keep subsequent extraction rules based on the pre-existing source queue and published evidence, not the exposed answers. Independent release review must inspect provenance and scoped payloads without opening answer-bearing files. The exposed lead cannot describe its later judgment as fresh blind benchmark confirmation.

The frozen benchmark remains unchanged. Its standard condition is source-only inference; dictionary retrieval is a separately declared condition. Generic lexical training knowledge does not authorize answer assistance at evaluation time. PAL remains a repeatedly exposed fixed regression benchmark, not an unlimited fresh test. Do not change its prompts, meaning rubric, cases or denominators to accommodate the new pool. A benchmark reference concern is recorded externally; it does not authorize a correction to v1 or a training example from its answer.

## Final release checklist

1. Freeze named source/code/review inputs and hashes. Reconstruct every admitted field from its exact source locator; preserve original bytes and explicit corrections. Independently inspect representative structures and every known scope/typo exception. Reuse earlier verified work rather than redoing unrelated acquisition.
2. Reconcile the entire declared scope into qualified, held and not-yet-processed units, without missing or repeated IDs. Count records, full sense inventories, morphology contexts, clauses and documents separately; retain variant/duplicate/work families.
3. Give each admitted unit an explicit task, source/target language, edition/context, form/sense boundaries, uncertainty disposition, lineage result, review method and source-rights status. Unknown redistribution rights do not become invented permission; preserve the intended local-use constraint and resolve any actual prohibition before that use.
4. Preserve full source-scoped meaning bundles. Demonstrate no Cartesian expansion, silent one-sense collapse, uncertainty removal, unsupported translation into Persian or conversion of definitions into sentence gold. Carry relevant earlier content-review holds forward.
5. Run metadata identity/alias guards over the final learning view, covering all 16 protected families. Inspect nested payload inclusion and all protected/unknown-origin quotation decisions. Include negative cases for alternate editions, a protected work-specific glossary, mixed S22 origins and an innocent generic same-word overlap; the latter alone must not be rejected as answer leakage.
6. Verify clear scope boundaries for document/paragraph pairs and reversible format changes. A declared whole-document unit may remain whole; do not invent alignment to inflate counts.
7. Verify immutable historical TRAIN and benchmark metadata hashes; preserve failed/held evidence and write a completion receipt last. This review verified only the safe protocol/policy hashes, not a full benchmark verification involving answer-bearing files.
8. Publish qualified additions and coverage limits, with AI-assisted review and `expert_certified=false` truthful where applicable. Final independent release review must inspect the actual pool. New source-qualified records are not evidence of better translation quality, and admission does not authorize model training.

## Evidence read for this policy review

- Current qualification PLAN SHA256: `0af896b83eb79d91f7704e7702fb814f36656fb1bc229cd8c26060704569723c`.
- PAL protocol SHA256: `91b70ac4d7e278050074128d68f4b197f3b80cb90d71d6c1771ea73eb12ef938`.
- PAL manifest SHA256: `a3932f7510f101376cc91c47bb23f3c9872656c41f563701fa3dcb2b6c89a5e8`.
- PAL holdout policy SHA256: `eb2425c5711b4166980df2f4205d9f11223c2c55e19c2121f3b228b7af43cddc`; protocol/policy hashes match that frozen manifest.
- Collection decisions SHA256: `ce1b1c348678e5f6e5592d120f9b2c604bd64630cac0fd0166ce59e283f90c3f`; existing unified builder's metadata-only `HOLDOUT` constant confirms the 16-work union.
- Also read `benchmarks/AGENTS.md` and safe inventory metadata. No benchmark answer/reading file, network, model or GPU was accessed. No corpus/code/output was changed.
