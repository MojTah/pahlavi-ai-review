# Pahlavi translation research: independent review snapshot

Prepared 29 September 2026. Start with [the complete review prompt](REVIEW-PROMPT.md), then inspect the evidence rather than accepting our conclusions. This snapshot supersedes the 28 September review brief. It is an external review package, not a production translator.

## Present conclusion

**Latest full pretraining review: HOLD.** The [all-record audit](experiments/full-pretraining-audit-20260929/REPORT.md) found source-faithful but underdetermined lexical prompts: 150 groups / 319 rows have identical inputs with different complete-inventory targets. It also records standalone crossreference/note issues and 17 inherited formatting artifacts. A recovery-status bug was reproduced and fixed locally. Review the new evidence before relying on the earlier structural pass. Frozen data/results remain unchanged; no new cloud run or training is authorized.

The retained reference is qualified Gemma4-31B step280. The latest mixed-supervision continuation completed, but did not improve the fixed development screen and increased critical errors. No new model is promoted. NLLB training and its later familiar-example diagnostic also completed; recommendations written before those runs are historical.

The expanded source-qualified release contains 10,152 typed records, or 10,151 after one prepared duplicate collapse. These are **not 10,151 translated sentences**. The latest run used 1,536 examples: 1,152 historical and 384 auxiliary, including 192 lexical records. It did not test training on the full expanded corpus. There was no matched historical-only continuation, so the result cannot isolate the effect of adding the data.

The latest offline learning diagnostic prepares 28 prompts per checkpoint to compare auxiliary-task recall with contextual translation on a fixed sample; it cannot by itself establish acquisition or transfer. It is deliberately a training-side diagnosis, not a new generalization score. Its local checks are complete, including correction of a launcher settings-contract defect and independent tiny-model CPU checks. **The real server comparison has not run; training and paid inference are on hold at the user's instruction.** Consult `experiments/data-recheck-20260929/REPORT.md` for 53 structural checks, the bounded 21-record source review, configuration evidence and remaining limits. Passing these checks does not certify every corpus meaning or real GPU execution.

## Evidence map

| Area | Start here |
|---|---|
| Current state and objective | `PROJECT_STATE.md`, `GOAL.md`, `DATASET-READINESS.md`, `SOURCE-COVERAGE.md` |
| Superseding full pretraining review | `experiments/full-pretraining-audit-20260929/REPORT.md` and its five component reviews / all-record metadata ledgers |
| Latest local data/configuration recheck | `experiments/data-recheck-20260929/REPORT.md`, `INTEGRITY.md`, `SEMANTIC-SPOTCHECK.md`; `experiments/learning-diagnosis-20260929/INDEPENDENT-LAUNCH-REVIEW.md` |
| Fresh independent audit of an external review | `experiments/strategy-audit-20260929/RESPONSE.md` and `external-review.txt` |
| Complete data release and limitations | `experiments/data-qualification-20260928/README.md`, `release-v1.json`, `coverage-v1.json` |
| Actual mixture and exposure | `experiments/mixed-supervision-20260929/prepare.py`, `PLAN.md`, `data-manifest.json`, `saved-data-inventory.json` |
| Latest results, actual outputs and scoring | `experiments/mixed-supervision-20260929/REPORT.md`, `OUTCOME-QA.md`, `scored/comparison.json`, `recovered/`; `experiments/mixed-review-20260929/`; `scripts/review_mixed.py` |
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
| Latest mixed96 vs retained step280, DEV15 | 1→1 accepted for both; critical A 4→6, B 3→6 | Some lexical changes, no screen pass; unmatched continuation |
| Same latest comparison, constrained DEV9 | Critical A 3→4, B 4→5 | Separate task denominator |

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
