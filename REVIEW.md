# Pahlavi translation research: independent review snapshot

Updated 30 September 2026. Start with [the complete review prompt](REVIEW-PROMPT.md) and the [corrected-data comparison](experiments/training-ready-v2-20260929/REPORT.md), then inspect the evidence rather than accepting our conclusions. This snapshot includes the completed cloud pilot and fresh blinded assessment. It is an external review package, not a production translator.

## Present conclusion

**Latest result: a small gain after correction, but no passing improvement screen.** Two fresh blinded reviewers each accept2/15 whole translations from corrected-v2, versus1/15 from both retained step280 and previous mixed96. Whole critical errors for retained/previous/corrected are4/7/4 for A and4/6/5 for B. Relative to the previous mixed run, correction recovers case003 but adds unsupported certainty on two constrained cases. The gain is only one accepted passage in one work; the fixed threshold requires at least two across two works plus safety conditions. [Full comparison and reproducible evidence](experiments/training-ready-v2-20260929/REPORT.md). No candidate is promoted, and this recipe is closed to automatic repetition.

The [corrected package](experiments/training-ready-v2-20260929/README.md) resolves150 lexical-input ambiguity groups while preserving supported meanings, scopes20 dictionary apparatus cases, repairs17 typography records and holds seven unresolved cases. Its9,973 unique inputs represent10,145 original records. The authorized1,536-example/96-update pilot and all24 source-only outputs completed; small artifacts and provider inventory were independently verified. The preceding [all-record audit](experiments/full-pretraining-audit-20260929/REPORT.md) remains the defect discovery record; the unchanged v1 projection remains disallowed for relaunch.

The retained reference is qualified Gemma4-31B step280. The first mixed-supervision continuation failed; its corrected sibling has a limited gain but also fails. NLLB training and its later familiar-example diagnostic also completed; recommendations written before those runs are historical.

The original expanded release contained10,152 typed records, or10,151 after one prepared duplicate collapse; corrected-v2 has9,973 unique model-visible inputs. These are **not all translated sentences**. Each mixed run used1,536 examples:1,152 historical and384 auxiliary, including192 lexical records. Neither trained on the full expanded corpus. The two mixed runs match update count and optimizer settings, but the correction package changes214 input/target representations and includes parent substitutions. It cannot isolate the causal effect of one correction or source.

The latest offline learning diagnostic prepares 28 prompts per checkpoint to compare auxiliary-task recall with contextual translation on a fixed sample; it cannot by itself establish acquisition or transfer. It is deliberately a training-side diagnosis, not a new generalization score. Its local checks are complete, including correction of a launcher settings-contract defect and independent tiny-model CPU checks. **The real server comparison has not run; training and paid inference are on hold at the user's instruction.** Consult `experiments/data-recheck-20260929/REPORT.md` for 53 structural checks, the bounded 21-record source review, configuration evidence and remaining limits. Passing these checks does not certify every corpus meaning or real GPU execution.

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
