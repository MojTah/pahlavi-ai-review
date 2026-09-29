# Independent Gemini review: dataset, training strategy and latest result

Prepared 29 September 2026 at the user's request. This is a saved handoff for the user to give Gemini; Codex has not sent it externally or started Gemini. Review the project read-only. Return a report before proposing edits, training, paid jobs, credential access, or uploads. No model weights need to be downloaded.

## Start here

Project root: `[USER_HOME]\Documents\ChatGPT\Pahlavi language`.

Read `PROJECT_STATE.md`, `GOAL.md`, `DATASET-READINESS.md`, `SOURCE-COVERAGE.md`, then the evidence below. Treat earlier chronological bullets as historical snapshots; use the latest report for current results. Inspect actual files rather than trusting this summary or Codex's conclusions.

The goal is reliable Pahlavi-to-Persian translation, including ambiguous and partly understood language, ultimately usable on an8GB GPU machine. Speed is secondary to quality. Total cloud-spending ceiling remainsUSD25; do not infer remaining spending authority from account credit. Preserve fixed evaluation, source uncertainty, multiple meanings and provenance. No local model delivery before satisfactory cloud quality.

## Crucial distinction: corpus size versus actual training exposure

The historical corpus contains2,237 Persian translation pairs. The new source-qualified release adds7,915 typed supervision records; most are dictionary inventories or grammar tasks, not full sentence translations. Combined release10,152; tokenized unique pool10,151 after one exact same-task/context MMP duplicate collapse.

| Added resource | Available units |
|---|---:|
| Persian dictionary form/meaning inventories | 2,676 |
| MacKenzie CPD English complete sense blocks | 3,506 |
| Manichaean Middle Persian English inventories | 1,426 |
| Conditioned Persian teaching/grammar units | 240 |
| Documentary English spans | 57 |
| Kanheri Persian occurrences | 6 (4 pair types) |
| English article scopes | 4 |

**The latest pilot did not train on this entire expanded corpus.** It used1,536 selected examples in96 updates:1,152 historical translations,96 Persian lexical,64 CPD English,32 MMP English,127 grammar,57 documentary,4 Kanheri types and4 article scopes. Therefore only384 examples came from the new auxiliary resources. Every update had12 historical,2 lexical and2 other auxiliary examples. It is incorrect to describe the outcome as a full-corpus training result.

The user explicitly wanted the largest reliable training set assembled before further training. Review whether the bounded subset and task allocation were scientifically appropriate and adequately served that objective. Distinguish preparing all available data from actually exposing the model to it.

## Dataset evidence and actual files

- `experiments/data-qualification-20260928/README.md`, `release-v1.json`, `coverage-v1.json`: qualification rules, counts, exclusions, source limitations and hashes.
- `resources/local/data-qualification-20260928/ready-v1/`: all10 canonical release files. Inspect each row's learning fields, task/language, complete meanings and provenance. Includes original control, all new source types, exclusions and duplicate ledger.
- `experiments/mixed-supervision-20260929/prepare.py` and `data-manifest.json`: exact transformation, selection, token census and masks.
- `resources/local/mixed-supervision-20260929/data/learning-projections.jsonl`:10,152 readable projected learning records.
- Same directory: `pool.jsonl` (10,151 eligible tokenized rows), `train.jsonl` (actual1,536-row pilot), `row-audit.jsonl`, `duplicates.jsonl`, `exclusions.jsonl` and `census.json`.
- `experiments/mixed-supervision-20260929/saved-data-inventory.json`: all16 canonical release/preparation payloads rehashed and confirmed present at handoff.

These local resource files are intentionally Git-ignored. They remain on disk, but a Git-only clone is not the whole dataset. Raw books, XML/site acquisitions and earlier decisions remain at source paths bound in `release-v1.json`; do not delete or rewrite them. Source-qualified does not mean error-free or specialist-certified. Shared website/PDF editions are not independent corroboration.

## Exact latest training and outcome

Read `experiments/mixed-supervision-20260929/PLAN.md`, `REPORT.md`, `OUTCOME-QA.md`, `execution-preparation.json`, `execution.json`, `recovery.json` and `scored/comparison.json`.

Base: pinned Gemma4-31B; retained step280 adapter;96 additional QLoRA updates, fresh optimizer, seed3407, rank16, learning rate0.0001, accumulation16. The plan and runner contain full precision, optimizer and schedule details. The recipe mixes Persian translations, lexical inventories including English, structured CPD targets and conditioned grammar/documentary tasks. Do not assume these are equivalent supervision units.

Cloud job `6abb82b6e2f3c356be0389a3` completed96/96 updates and24/24 evaluation outputs. Recovered small evidence is under `experiments/mixed-supervision-20260929/recovered/`; inspect `mixed/training/run.json`, `progress.jsonl`, `mixed/evaluation/run.json`, `predictions.jsonl` and `driver.log`. No model weight was downloaded. The final and step20 adapters remain in private HF bucket `Mojionix/pahlavi-pilot`, prefix `mixed-supervision/ad548e0f8b7b454682dc2fd6c3298966`.

Both independent fresh-context reviewers accepted1/15 whole answers for both old and new models. Whole critical errors rose4→6 for A and3→6 for B; constrained critical errors rose3→4 and4→5. Both newly accepted case009 and lost case003, which became a critical error. Both fixed improvement screens fail. Some lexical/category counts improve; these do not erase critical regressions.

Retained comparison outputs and raw reviewed answers are archived under `experiments/mixed-review-20260929/lead-only/`. Each reviewer folder has anonymous48-row packets and final ratings. `reviewer-receipts.json` records their isolation and hashes; `scored/blind-review-freeze.json` freezes them. `scripts/review_mixed.py` uses the unchanged existing scoring helpers; independent reconstruction, two tests and arithmetic audit passed. These checks establish reproducibility, not philological correctness.

## Evaluation boundaries

Use `experiments/dev-assisted-qualified-20260927/uniform-evaluation-contract.json`:15 whole cases plus9 constrained cases, separate per reviewer. Same24 prompts, token identities, base revision and greedy decoding; all first attempts retained. A candidate needs net acceptance gain≥2 for both reviewers across≥2works and the predefined critical/uncertainty safeguards. Current comparison uses reused development cases; it is not fresh confirmation or a global accuracy estimate. Older PAL-REF40 scores are a different denominator/panel. Do not train on DEV/PAL answers, revise references to rescue a score, or silently replace the merit function.

## Questions for your independent report

1. Is extraction, source alignment, deduplication, polysemy/context handling and training serialization trustworthy? Identify exact rows/files and source-backed corrections; distinguish errors from permitted alternatives or unresolved readings.
2. Did the pilot adequately test the expanded data? Analyze actual exposure, task/language balance, short lexical versus passage supervision, CPD JSON targets, and whether the translation objective was diluted.
3. Could the learning rate, continuation schedule, optimizer reset, masks, chat template or sampling explain regression? State evidence versus hypothesis. The experiment has no matched old-data-only continuation, so it cannot isolate the effect of new data.
4. Audit the semantic judgments against supplied references, especially cases003 and009 and the constrained cases. Preserve originals; report any disagreement separately rather than editing ratings. Is stronger specialist adjudication needed?
5. Compare reasonable next methods/model choices, including full-source coverage with careful weighting, staged lexical/contextual learning and retrieval, using relevant primary research where helpful. Do not recommend a broad brute-force grid.
6. Recommend one next discriminating experiment, with prediction, required dataset, unchanged comparison, negative controls where warranted, stopping rule, realistic cloud cost and8GB deployment path. Explain what evidence would reject your recommendation.

Return a concise executive summary, prioritized findings with exact evidence, limitations, and one justified next plan. It is acceptable to conclude that further training should wait. Current decision is to retain step280 and pause new training; this is open to evidence-based review, not a requirement to agree with Codex.
