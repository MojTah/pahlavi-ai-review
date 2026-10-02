# Pahlavi translation research

Research into Middle Persian (Pahlavi) translation, primarily scholarly Latin transcription to Persian. This repository contains source-study notes, a fixed benchmark, experiment records, evaluation tools and later cloud-training work. It is an experimental research project, not a validated translator.

**Current state: 1 October 2026. Development version: 0.11.5; version impact NONE for this research update.** The [four-pass trial completed](experiments/dose-acquisition-20260930/live-execution/OUTCOME.md): taught lexical recall improved from 0/6 to 5/6, but fixed whole-passage acceptance only from 0/15 to 1/15, critical errors increased and confirmation stayed 1/5. Retain qualified Gemma step280. Independent technical closeout is PARTIAL; lead verification is recorded separately. No new model is promoted and no new paid run is admitted.

**Latest evidence qualification:** [Occurrence evidence and dictionary recovery](experiments/occurrence-evidence-20261001/README.md) saves12partial claim leads and three complete typed MacKenzie inventories (`ī`, `pad`, pronoun `ōy`) independently checked against printed pages. All six historical note parents were already selected for training; documentary readings retain attribution, damage and conflicts. Four annotated MPCD work options are identified, not admitted as gold. Zero complete comparison cases and no training/paid launch; original data, candidates and fixed merit are unchanged. Next qualify one bounded occurrence per additional family, complete references and context-specific lexical bindings.

**Completed candidate checkpoint:** [Reviewed plain-target candidates](experiments/plain-target-preparation-20261001/README.md) resolves all 11 named questions: six narrow repairs, three unchanged annotated fragments and two new standalone holds. All 9,971 retained candidates are tokenized with matching instructions; 7,438 complete lexical inventories preserve multiple meanings and qualifiers. Five tests, exact replay and independent engineering review passed. Original archival records and the seven earlier exclusions remain unchanged. The [three-condition comparison draft](experiments/plain-target-preparation-20261001/COMPARISON-DRAFT.md) still has zero complete pilot cases: fifteen analysis candidates occupy one textbook lineage and fourteen were previously selected. Next qualify independent occurrence analyses, references and more work families. [Strategy](experiments/strategy-reset-20261001/REPORT.md) and fixed merit remain unchanged. No training schedule, paid launch or semantic certification is admitted; no new model weights were downloaded.

## Start here

| Purpose | Read |
|---|---|
| Ask another AI to review the project | [Review brief, results and ready-to-paste prompt](REVIEW.md) |
| Understand current status | [Current project state](PROJECT_STATE.md) |
| Choose how to fine-tune the next model | [Fine-tuning knowledge base: Persian summary, model recipes and evidence](kb/model-finetuning/README.md) |
| Review the latest proposed next step | [1 October research decision](experiments/strategy-reset-20261001/REPORT.md) |
| Inspect the full readable resource and remaining annotation gaps | [Local implementation and review](experiments/usable-resource-20261001/README.md) |
| Inspect resolved target questions and aligned candidate tokens | [Source decisions, verification and comparison draft](experiments/plain-target-preparation-20261001/README.md) |
| Inspect the latest experiment | [Four-pass result and evidence](experiments/dose-acquisition-20260930/live-execution/OUTCOME.md) |
| Inspect the retained reference model | [Qualified-data paired comparison](experiments/palref-paired-20260927/REPORT.md) |
| Understand evaluation | [Frozen PAL-REF protocol](benchmarks/pal-reference-v1/PROTOCOL.md) and [uniform contract](experiments/dev-assisted-qualified-20260927/uniform-evaluation-contract.json) |
| Find earlier language studies | [Study guide (original README)](STUDY_GUIDE.md) |
| Trace earlier decisions | [Preserved state history](PROJECT_STATE_HISTORY_20260928.md) |
| Check attribution and sources | [Credits](CREDITS.md), [source register](kb/sources.md), [collection guide](data/README.md) |

## Latest result

The [latest paired comparison](experiments/dose-acquisition-20260930/live-execution/OUTCOME.md) shows acquisition without adequate passage transfer. The run repeated 1,536 examples four times; it did not consume the full 9,973-prompt pool. Both reviewers pass lexical acquisition but fail the passage safety and confirmation screens. Earlier outcomes below remain separate historical panels and cannot be combined into a single accuracy curve.

## Earlier NLLB result

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
