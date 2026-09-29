# Full pretraining review — 29 September 2026

**Decision: HOLD. Do not train the unchanged full pool.** This deeper pass found problems that source preservation and token-mask checks alone did not catch. No project training, pretrained-model download, cloud inference or paid job was performed. The frozen corpus, previous results and evaluation merit remain unchanged.

Classic + Critic: five disjoint evidence tracks covered CPD, Persian/MMP lexicons, historical translations, auxiliary examples and runtime; the lead performed an independent cross-record token audit and the recovery-code repair. Existing tools and archived sources were reused. This is a full-record source-fidelity/mechanical review with explicitly bounded semantic adjudication, **not a guarantee that every linguistic interpretation or possible future failure is correct**.

## Findings that change readiness

| Finding | Evidence and practical consequence | Disposition |
|---|---|---|
| Identical dictionary prompts request different complete answers | **150 lexical groups / 319 rows**: CPD 79/173, Persian 66/136, MMP 5/10. Complete model-visible token prefixes are identical within each group. Separate source entries or homonyms survive in provenance but do not distinguish the task input. | Repair the derived learning projection before full-pool training. Preserve all supported senses and source-entry boundaries in a reviewed complete inventory, or use meaningful context available at inference. Never select one meaning arbitrarily. |
| A standalone target refers to an absent “previous word” | `kosh:da:68`, consumed at position 782. The archived definition is not shown false, but its relative reference cannot be resolved from this input. | Resolve the exact source reference into a typed note, or hold the record in the next version. Do not invent the missing content. |
| Dictionary apparatus is mixed with prediction targets | 17 Persian targets include etymologies/related forms; one contains subordinate inflected forms. Three MMP targets retain attribution/crossreference labels. These are faithfully copied source notes, not necessarily meanings. | Explicitly distinguish dictionary reproduction from translation supervision. Separate notes while preserving sense qualifiers and form-to-meaning relations. |
| Historical target formatting noise | **17 records**, 14 selected previously: 14 repeated-ZWNJ records, one LRM record and two soft-hyphen records. A target contains 30 consecutive ZWNJs. All match the archive. | Normalize only in a new derived version, with a reversible change ledger and tokenizer check. No claim that these artifacts caused regression. |
| Completed training can be reported incomplete after evaluation failure | Reproduced in the active mixed wrapper. The outer flag previously depended on both phases completing. | **Fixed locally:** independent verification of closed training receipts, exact parent order, source/settings bindings and adapter inventory/hashes now preserves training completion while retaining the evaluation failure. New failure-injection regressions cover valid and invalid evidence. No cloud execution is claimed. |

The all-pool screen found 152 groups / 323 rows in total. The additional two historical groups are compatible translations, including a final-punctuation variant; they are not demonstrated semantic contradictions. Only **nine lexical collision rows** were consumed in the last mixed run, and no lexical collision group had both alternatives consumed. The sole co-exposed group is the historical punctuation variant. Therefore the collisions are a concrete **full-pool readiness problem**, not demonstrated causal evidence for the previous quality regression.

For example, the same source-scoped `may` prompt has a wine inventory in one record and a prohibitive-particle inventory in another. Both may be valid published entries. A request for the complete inventory cannot silently choose between those entries. Giving the model an arbitrary record ID would distinguish storage records without supplying useful linguistic context.

## What was actually reviewed

| Component | Exhaustive checks | Semantic/source reading and limits |
|---|---|---|
| Cross-record training projection | All **10,152** released records, **55,654** string fields and **1,220,439** Unicode codepoints; every prepared prefix/answer across 10,151 rows; selected exposure joined for all 1,536 rows. No unknown model tokens. | Characters and hashes are not word-meaning certification. All exact-prompt collision groups were referred to the component reviewers. |
| CPD | All **3,506** released rows and **720** held units reconciled independently to 3,103 archived entries; 3,509 form strings and 8,470 target string atoms compared. | All 79 collision groups classified by source-entry distinctions; flagged XML exclusions reviewed. No exhaustive new comparison of every gloss to MacKenzie's printed pages or philological retranslation. |
| Persian/MMP dictionaries | All **4,102** inventories reconciled to 4,142 XML observations in seven responses; selected/excluded MMP spans fully accounted. | All 71 collision groups, 148 flagged Persian targets and 544 excluded MMP tails read. Unflagged entries are not newly expert-certified. |
| Historical translations | All **2,237** pairs independently joined to 164 raw endpoint files / 76 works, with complete-string screens and registered work exclusions. | All 129 flagged rows adjudicated; **134 full pairs** read, including duplicate-group context. The other 2,103 pairs had mechanical/provenance review, not individual linguistic reading. |
| Grammar/documentary/inscription/article units | All **307** records reconciled, including five declared pre-existing derivations. | All 307 learning records read; all 240 grammar records checked against 18 page images, 57 documentary records against raw editions, and ten inscription/article spans against pages/offsets. 27 page images inspected in total. |
| Training implementation | **27 existing offline tests** passed; full preparation reproduced seven frozen outputs and manifest; exact packed helper bytes and argument guards checked. | Tiny random CPU numerical/failure tests, not a rerun of the pretrained model or current A100/NF4 environment. Recovery repair has separate receipt-only regression evidence. |

No unexplained source-to-release mapping difference was found. Source fidelity remains distinct from choosing a valid standalone learning task. The prior 53-check pass established integrity of a given projection; it did not establish that the projection retained every discriminator needed for its requested answer. That missing check explains why the earlier pass did not reveal the lexical issue.

No frozen evaluation answers were imported into training or used to select repairs. The fixed work exclusions and historical controls remain intact. Existing source-only exclusion checks do not prove the absence of every alternate witness, paraphrase or shared formula.

## Unresolved issues, not established defects

- Three historical editorial readings remain uncertain: `parsig:151061036:pal>fa`, `parsig:123000032:pal>fa`, `parsig:136006008:pal>fa`. The audit records the source qualifications; it does not invent replacements.
- The MP2100 greeting's temporal scope needs philological interpretation if used as exact full-meaning gold. Both spans match the raw edition. A missing word-for-word English rendering is not by itself proof of mistranslation. Four documentary uncertainty-marker asymmetries remain source-level qualifications.
- The historical contextual wrapper has a similar static phase-flag pattern; it is not executed by the active mixed path and was not repaired or approved for renewed use here.
- Current 31B loading, NF4/BF16 behavior, Linux signals, full-model memory/throughput and remote persistence remain hardware/server checks. Prior successful runs and local tests do not guarantee them on a future machine.
- The mixed interruption saves adapters, not complete optimizer/RNG state. Such an adapter supports diagnosis, not exact continuation of the interrupted trajectory. Evaluation-time forecasts also cannot guarantee complete coverage within the job deadline.
- Source-qualified lexical expansion is not automatically effective sentence-translation training. The previous run used only 1,536 selected rows and lacked a matched historical-only continuation. Auxiliary learning, contextual transfer and generalization are not established by this audit.

The pinned native Gemma CPU loss probe supports equal-example averaging in both the original native Trainer path and the explicit mixed path. It does **not** support blaming regression on a newly introduced switch from pooled-token loss. Token proportions and per-token scalar coefficients are not measured gradient influence.

## Required before another training proposal

1. Make a **new versioned learning projection**, leaving this historical release intact. Resolve all lexical prompt collisions with source-grounded inventories/context; resolve or hold the dangling reference; type dictionary notes; normalize the identified formatting artifacts reversibly. Preserve homonyms, source lineage, uncertainty and the existing exclusions.
2. Re-run source bindings, exact-input/target ambiguity checks, complete tokenizer reconstruction, length/mask/terminator checks and the actual intended exposure census on that version. Review every changed record against its original source. Do not launch a run with unresolved complete-inventory collisions.
3. Decide the intended tasks and one controlled training comparison using the corrected corpus. State exact exposure, language/task weighting, optimizer continuation/restart, stopping rules and unchanged merit. More rows alone are not a sufficient hypothesis.
4. Only with new authorization, complete the necessary bounded server checks. Training and the existing-checkpoint inference proposal remain **NOT LAUNCHED**. No automatic retraining follows this report.

## Evidence and reproduction

- [Cross-record checker](cross_record_check.py) and [all-record metadata](cross-record-audit.json): exact token-prefix ambiguity, character screens and actual exposure. Its `REVIEW_REQUIRED` status is deliberate, not a semantic pass.
- [CPD review](CPD.md), [FA/MMP review](LEXICAL-FA-MMP.md), [historical review](HISTORICAL.md), [auxiliary review](AUXILIARY.md): exact IDs, locators, adjudications and reproducible metadata ledgers.
- [Training review](TRAINING.md) and [receipt](training-audit.json): pre-repair reproduction and subsequent independent repair review. The original failure receipt remains historical evidence. Its reproducer is hash-pinned to the old launcher and now refuses stale replay, directing operators to the current recovery tests.
- `python -B -X utf8 -m unittest cloud_pilot.test_hf_mixed_recovery -v`: current recovery regressions, with synthetic files only. No weights, optimizer or network.

All corpus-dependent checks require the authorized local source archive/private companion. Public metadata cannot replace the full data. No new source redistribution permission, universal zero-error guarantee, expert certification or training approval is implied.

## Independent final review

The final critic recomputed collision/exposure counts from token arrays, checked all component totals and 266 file/hash bindings, and requested narrower wording about CPD semantic coverage. That correction was applied and independently verified. The separate runtime critic passed the scoped recovery repair and exact packed-helper tests. These are report/code review passes; dataset admission remains HOLD.

- Lead agent/request id: /root
- Critic agent/request id: /root/full_audit_critic
- Critic model and reasoning effort: Inherited unchanged from lead; no override requested or applied
- Evidence reviewed: This report, six audit receipts, component reports, prepared token arrays and source/hash bindings
- Verification evidence: 266 file/hash bindings passed; 152 groups/323 rows, lexical 150/319 and selected exposure independently recomputed; coverage correction verified
- Independent from lead: yes
- Critic verdict: pass
