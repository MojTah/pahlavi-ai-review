# Pahlavi translation research

Research into Middle Persian (Pahlavi) translation, primarily scholarly Latin transcription to Persian. This repository contains source-study notes, a fixed benchmark, experiment records, evaluation tools and later cloud-training work. It is an experimental research project, not a validated translator.

**Current state: 28 September 2026. Development version: 0.10.11.** The [bounded NLLB experiment](experiments/nllb-supervised-20260928/PLAN.md) completed700 updates; the server job is terminal and its cloud checkpoint is preserved. Two fresh blind reviewers each accepted0/15 trained NLLB translations versus1/15 retained Gemma, with more critical errors for NLLB. [Outcome](experiments/nllb-supervised-20260928/REPORT.md). No promotion; Gemma remains the reference. See the [revised research objective](GOAL.md).

## Start here

| Purpose | Read |
|---|---|
| Ask another AI to review the project | [Review brief, results and ready-to-paste prompt](REVIEW.md) |
| Understand current status | [Current project state](PROJECT_STATE.md) |
| Choose how to fine-tune the next model | [Fine-tuning knowledge base: Persian summary, model recipes and evidence](kb/model-finetuning/README.md) |
| Review the latest proposed next step | [28 September strategy](output/research-next-step-20260928/REPORT.md) and [independent critique](output/research-next-step-20260928/STRATEGY-CRITIC.md) |
| Inspect the latest experiment | [NLLB plan and execution](experiments/nllb-supervised-20260928/PLAN.md), [completion record](experiments/nllb-supervised-20260928/continue/completion-check.json) |
| Inspect the retained reference model | [Qualified-data paired comparison](experiments/palref-paired-20260927/REPORT.md) |
| Understand evaluation | [Frozen PAL-REF protocol](benchmarks/pal-reference-v1/PROTOCOL.md) and [uniform contract](experiments/dev-assisted-qualified-20260927/uniform-evaluation-contract.json) |
| Find earlier language studies | [Study guide (original README)](STUDY_GUIDE.md) |
| Trace earlier decisions | [Preserved state history](PROJECT_STATE_HISTORY_20260928.md) |
| Check attribution and sources | [Credits](CREDITS.md), [source register](kb/sources.md), [collection guide](data/README.md) |

## Latest result

The [completed NLLB comparison](experiments/nllb-supervised-20260928/REPORT.md) does not establish improvement: both fresh reviewers accept0/15 whole translations for initialized and trained NLLB versus1/15 Gemma. Training reduces NLLB whole critical counts8→5 and10→7, but trained critical counts remain above Gemma3/4. One trained cap failure remains; the formal screen is inconclusive and semantic improvement conditions are unmet. These fixed DEV results are provisional, separate from PAL-REF scores.

## Earlier contextual comparison

The contextual-training candidate and its matched ordinary-training control each completed 48 additional updates from the same qualified Gemma 4 31B step280 adapter. Both produced all 24 scheduled DEV outputs. Two blinded AI reviewers each accepted **0/15 whole translations from either arm**. Constrained critical errors increased **3/9 → 4/9** for both reviewers. Both predeclared improvement screens failed.

The prior qualified step280 model remains the experimental reference. Its separate PAL-REF comparison received **16/40 and 17/40 accepted translations**, one result per reviewer. These scores cannot be compared directly with the latest DEV 0/15: cases, conditions and reviewer panels differ. All semantic scores are provisional AI judgments, not Pahlavi-specialist certification.

The contextual recipe is closed. The subsequent NLLB-200-distilled-1.3B candidate has now completed training and paired semantic scoring without meeting improvement conditions. It produced23 complete trained outputs and one capped output; all remain in the evaluation. Training completion is not a demonstrated quality improvement. Native-script reading, unknown-word decipherment and satisfactory 8 GB laptop inference remain unproved.

## Repository map

| Folder | Role |
|---|---|
| `benchmarks/` | Frozen PAL-REF reference set and integrity/scoring tools; preserve its bytes |
| `experiments/` | Dated protocols, outputs, ratings, audits and decisions |
| `cloud_pilot/`, `scripts/`, `tests/` | Training/evaluation implementation and checks; no cloud launch is needed for review |
| `kb/`, `dictionary/` | Language-study notes, contextual study aids and an agent-facing model fine-tuning knowledge base |
| `sources/`, `data/`, `resources/`, `downloads/` | Collection indexes and attribution; original downloads are mostly local and ignored |
| `plans/`, `output/` | Earlier strategy reports and research handoffs |
| `review/` | Portable-package manifest and verification record |

## Sharing for review

Use the local portable review ZIP described in [REVIEW.md](REVIEW.md), or a fresh private GitHub repository containing that selected snapshot. Access for a reviewing AI must be arranged explicitly. Do not upload the entire working folder or its Git history as a shortcut: they contain material outside the review package's scope.

The package includes attributed reference excerpts needed for assessment; it grants no new redistribution license. Public publication needs a separate rights and content review. No Git remote or external upload was created by this cleanup.
