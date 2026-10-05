# Pahlavi translation research: specialist review

Updated 5 October 2026 for independent specialist review. Development version: 0.11.7.

Start with the latest completed [dictionary comparison](experiments/dictionary-ab-runtime-20261003/live-execution/OUTCOME.md): both blinded AI reviewers accept 2/15 without dictionary help and 5/15 with it. Five gains and two lost acceptances give net +3. The fixed familiar-DEV continuation screen passes; unseen accuracy and specialist confirmation remain unestablished. This changes supplied inference evidence, not model weights.

The newest [faithfulness comparison](experiments/dictionary-faithfulness-20261005/PLAN.md) tests one general instruction against unsupported glosses using the same retained Gemma step280. Its latest saved [startup receipt](experiments/dictionary-faithfulness-20261005/live-execution/STATUS.md) recorded RUNNING at 05:52:29 UTC on 5 October. Final outputs and a semantic result have not been recovered in this publication checkpoint. That saved status is not a live provider check.

The repository now includes the complete locally collected OpenAMPD, legacy Cologne CPD and Ezafe research-data families with their notices, plus three papers with recorded Creative Commons terms. [Data access and remaining gaps](review/DATA-ACCESS.md) names the full training/candidate arrays and source families still withheld for unresolved or restrictive republication terms. The retained model adapter is cloud-only; model bytes are not included. [Manifest](review/MANIFEST.json) binds every published file, and [omissions](review/OMISSIONS.json) records exact withheld research-file hashes. This is an expanded review repository, not a complete runnable model release.

Specialists should examine sense selection, unsupported explanatory additions, negation, gains/regressions and the validity of the familiar development screen. Preserve disagreement and source attribution. Review does not authorize cloud jobs, training, credential access or contacting anyone.

## Evidence map and historical results

# Pahlavi translation research: independent review snapshot

Updated 2 October 2026. Start with [the consultation prompt](REVIEW-PROMPT.md), then inspect the evidence rather than accepting our conclusions. This snapshot supports an independent Opus second opinion for Mojtaba and the continuing Codex researcher. The reviewer provides advice and findings; it does not take over implementation or launch experiments.

## Evidence and decision recorded on 2 October

The 2 October [direct versus own-analysis comparison](experiments/own-analysis-diagnostic-20261002/live-execution/OUTCOME.md) completed nine calls on three provisional development cases using retained Gemma step280. Both assessors accepted the same one of three translations in each arm: no new acceptance. One assessor found a new critical error in the analysis-fed Berlin result; the other assigned a meaning error. Preserve that disagreement. This is not a general accuracy estimate or an expert-certified evaluation.

The preceding [four-pass acquisition trial](experiments/dose-acquisition-20260930/live-execution/OUTCOME.md) improved taught lexical recall from 0/6 to 5/6, but passage safety and confirmation screens failed. Later [component](experiments/component-diagnostic-20261001/live-execution/OUTCOME.md) and [semantic-stage](experiments/semantic-stage-diagnostic-20261001/live-execution/OUTCOME.md) probes test different tasks and supplied evidence. Their results do not establish a deployable translation pipeline or uniquely locate an internal model failure. Read the [reporting clarification](experiments/semantic-stage-diagnostic-20261001/REPORTING-CLARIFICATION.md) and preserve the disputed Kanheri interpretation.

The current [plain-target resource](experiments/plain-target-preparation-20261001/README.md) has 9,971 candidates, including 7,438 lexical inventories. These are not all Persian sentence translations and were not all consumed by the retained model. The latest [coverage trace](experiments/own-analysis-diagnostic-20261002/live-execution/coverage-trace.json) is spelling-bounded presence evidence, not proof of sense coverage or optimizer exposure.

The next step proposed on 2 October is to qualify the same senses and occurrence-specific roles in original, nonpanel training records. A matched base-versus-step280 inference control is only a possible later proposal. No new paid run, training, model promotion or automatic extension is authorized by this review. Challenge this direction if the evidence supports something better.

| Review priority recorded on 2 October | Evidence |
|---|---|
| Present objective and historical qualifications | `GOAL.md`, `PROJECT_STATE.md`; dated older plans are superseded |
| Strategy and competing explanations | `experiments/strategy-reset-20261001/REPORT.md` |
| Acquisition versus contextual transfer | `experiments/readiness-repair-20260930/live-execution/OUTCOME.md`, `experiments/nf4-diagnostic-20260930/live-execution/OUTCOME.md`, `experiments/dose-acquisition-20260930/live-execution/OUTCOME.md` |
| Full lexical senses and occurrence qualification | `experiments/usable-resource-20261001/README.md`, `experiments/plain-target-preparation-20261001/README.md`, `experiments/occurrence-evidence-20261001/README.md` |
| Latest complete comparison | `experiments/own-analysis-diagnostic-20261002/PROTOCOL.md`, `source-qualification.json`, `REVIEWING.md`, `live-execution/OUTCOME.md`, `live-execution/comparison-summary.json`, `live-execution/raw-predictions.jsonl`, `live-execution/reviewer-a.jsonl`, `live-execution/reviewer-b.jsonl` |
| Exact public scope and checksums | `review/PACKAGE.md`, `review/MANIFEST.json`, `review/OMISSIONS.json`, `review/PUBLIC-COPY-CHANGES.json` |

Full source books and bulk training text remain excluded. The public package cannot support a claim that every dictionary word or corpus meaning has been independently verified. It includes selected diagnostic prompts/references, actual outputs and ratings for inspection. Access gaps must be explicit.

## Historical checkpoint: 30 September

**30 September review update:** [Integrated reassessment](experiments/external-review-20260930/RESPONSE.md) incorporates the complete external report and **Review project failures**. Three bounded audits support measuring acquisition before further training, distinguish available data from consumed exposure, confirm a small Unicode inconsistency and two metadata/reconstruction defects, and qualify the prompt/precision hypotheses. This local documentation update does not itself publish a new snapshot or authorize compute.

**Historical corrected-v2 result: a small gain after correction, but no passing improvement screen.** Two fresh blinded reviewers each accept2/15 whole translations from corrected-v2, versus1/15 from both retained step280 and previous mixed96. Whole critical errors for retained/previous/corrected are4/7/4 for A and4/6/5 for B. Relative to the previous mixed run, correction recovers case003 but adds unsupported certainty on two constrained cases. The gain is only one accepted passage in one work; the fixed threshold requires at least two across two works plus safety conditions. [Full comparison and reproducible evidence](experiments/training-ready-v2-20260929/REPORT.md). No candidate is promoted, and this recipe is closed to automatic repetition.

The [corrected package](experiments/training-ready-v2-20260929/README.md) resolves150 lexical-input ambiguity groups while preserving supported meanings, scopes20 dictionary apparatus cases, repairs17 typography records and holds seven unresolved cases. Its9,973 unique inputs represent10,145 original records. The authorized1,536-example/96-update pilot and all24 source-only outputs completed; small artifacts and provider inventory were independently verified. The preceding [all-record audit](experiments/full-pretraining-audit-20260929/REPORT.md) remains the defect discovery record; the unchanged v1 projection remains disallowed for relaunch.

The retained reference is qualified Gemma4-31B step280. The first mixed-supervision continuation failed; its corrected sibling has a limited gain but also fails. NLLB training and its later familiar-example diagnostic also completed; recommendations written before those runs are historical.

The original expanded release contained10,152 typed records, or10,151 after one prepared duplicate collapse; corrected-v2 has9,973 unique model-visible inputs. These are **not all translated sentences**. Each mixed run used1,536 examples:1,152 historical and384 auxiliary, including192 lexical records. Neither trained on the full expanded corpus. The two mixed runs match update count and optimizer settings, but the correction package changes214 input/target representations and includes parent substitutions. It cannot isolate the causal effect of one correction or source.

At the 30 September checkpoint, the offline learning diagnostic prepared 28 prompts per checkpoint to compare auxiliary-task recall with contextual translation on a fixed sample; it cannot by itself establish acquisition or transfer. It is deliberately a training-side diagnosis, not a new generalization score. Its local checks are complete, including correction of a launcher settings-contract defect and independent tiny-model CPU checks. **That comparison was pending at this historical checkpoint; the completed later diagnostics are linked above.** Consult `experiments/data-recheck-20260929/REPORT.md` for 53 structural checks, the bounded 21-record source review, configuration evidence and remaining limits. Passing these checks does not certify every corpus meaning or real GPU execution.

## Evidence map

| Area | Start here |
|---|---|
| Current state and objective | `PROJECT_STATE.md`, `GOAL.md`, `DATASET-READINESS.md`, `SOURCE-COVERAGE.md` |
| Corrected data and executed job | `experiments/training-ready-v2-20260929/README.md`, `INDEPENDENT-REVIEW.md`, `READINESS.md`, `verification.json`, `data-manifest.json`, `launch.json`, `terminal.json` |
| Superseding full pretraining review | `experiments/full-pretraining-audit-20260929/REPORT.md` and its five component reviews / all-record metadata ledgers |
| Latest local data/configuration recheck | `experiments/data-recheck-20260929/REPORT.md`, `INTEGRITY.md`, `SEMANTIC-SPOTCHECK.md`; `experiments/learning-diagnosis-20260929/INDEPENDENT-LAUNCH-REVIEW.md` |
| Fresh independent audit of an external review | `experiments/strategy-audit-20260929/RESPONSE.md` and `external-review.txt` |
| Complete data release and limitations | `experiments/data-qualification-20260928/README.md`, `release-v1.json`, `coverage-v1.json` |
| Actual mixture and exposure | `experiments/training-ready-v2-20260929/data-manifest.json`, `recovered/mixed/training/run.json`; prior recipe in `experiments/mixed-supervision-20260929/PLAN.md` |
| Latest results, actual outputs and scoring | `experiments/training-ready-v2-20260929/REPORT.md`, `OUTCOME-QA.md`, `scored/comparison.json`, `recovered/`; `experiments/corrected-review-20260930/`; `scripts/review_corrected.py` |
| Previous mixed result and original ratings | `experiments/mixed-supervision-20260929/REPORT.md`, `scored/comparison.json`; `experiments/mixed-review-20260929/` |
| Local learning diagnosis | `experiments/learning-diagnosis-20260929/REPORT.md`, `diagnose.py`, `census.json`, `references.jsonl` |
| Frozen evaluation | `experiments/dev-assisted-qualified-20260927/uniform-evaluation-contract.json`, `benchmarks/pal-reference-v1/PROTOCOL.md` |
| Prior alternatives | `experiments/nllb-supervised-20260928/REPORT.md`, `experiments/nllb-seen-20260928/precision-repair/REPORT.md`, `experiments/contextual-supervision-20260927/REPORT.md`, `experiments/dev-assisted-qualified-20260927/REPORT.md` |
| Source rights and provenance | `CREDITS.md`, `sources/manifest.json`, `resources/manifest.json`, `review/OMISSIONS.json` |

## Results to keep separate

| Comparison | Recorded outcome | Interpretation |
|---|---|---|
| Base Gemma vs first adapter, PAL-REF40 | Historical AI acceptance 5/40 → 15/40 | Early improvement; different evaluation panel from DEV |
| First adapter vs qualified step280, paired PAL-REF40 | A: 14→16; B: 16→17; critical 9→7 for each | Fresh ratings; cleaning and training exposure changed together |
| Qualified Gemma supplied examples, DEV15 | 1→3 accepted for both reviewers, with more critical errors | Existing improvement screen failed |
| Matched contextual continuation, DEV15 | 0→0 accepted for both reviewers | One tested recipe failed; does not rule out contextual supervision |
| Trained NLLB vs retained Gemma, DEV15 | NLLB 0 accepted; Gemma 1 for both; one NLLB cap | No promotion; formal screen technically incomplete |
| Original mixed96 vs retained step280, historical DEV15 panel | 1→1 accepted for both; critical A 4→6, B 3→6 | Earlier ratings preserved; no screen pass |
| Corrected-v2 comparison, fresh DEV15 panel | Retained/previous/corrected acceptance1/1/2 for both; critical A4/7/4, B4/6/5 | Small gain; unchanged improvement screens fail |
| Same fresh comparison, constrained DEV9 | Critical A4/5/4, B4/5/3; overconfidence A7/5/7, B8/6/8 | Separate denominator; uncertainty regression versus previous mixed |

All semantic judgments are provisional AI assessments. Reused DEV cases are development evidence, not untouched confirmation. Never pool reviewers or plot these different panels as one accuracy curve. The full repo exposes model identities and previous ratings; a new review here is unblinded.

## What is available

This is a **public review snapshot with a source-acquisition manifest; the corpus is not fully self-contained**. Code, authored research, selected evaluation evidence, counts, source locators, hashes and data preparation decisions are public. Full dictionaries, textbook extracts, raw source downloads and bulk training text with unestablished redistribution rights remain outside the public repository. The owner has separate local companion packages for direct review sharing. See [exact scope](review/PACKAGE.md) and [omissions](review/OMISSIONS.json).

If the companion data are not supplied, review code, experimental logic and available evidence, and identify the specific unverified data claims. Do not certify the full training set from metadata. No blanket license is granted over third-party sources.

## Safe starting checks

Inspect a check before running it. In a disposable copy, Python 3.11+ can verify the frozen benchmark:

```text
python -B -X utf8 benchmarks/pal-reference-v1/benchmark.py verify
```

Additional tests may require omitted data or the pinned dependencies. Their absence is a package limitation, not evidence of a model defect. Do not launch cloud scripts, install dependencies automatically, or download weights for this review.
