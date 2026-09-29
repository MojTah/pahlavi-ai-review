# NLLB full-adaptation pilot: paired DEV outcome

28 September 2026. **Do not promote this NLLB checkpoint over retained Gemma step280.** Full adaptation completed, but neither fresh blind reviewer accepted any of its 15 whole translations. Each accepted one Gemma translation. The formal improvement screen is inconclusive because one trained output hit the generation cap; the observed semantic conditions also fail. This is a negative result for this exact system/recipe, not for all NLLB or encoder–decoder approaches.

## Matched comparison

Each fresh reviewer independently judged all 72 anonymized records: 24 initialized NLLB, 24 trained NLLB and 24 cached qualified Gemma outputs. The unchanged rubric distinguishes 15 whole translations from 9 constrained cases. Reviewers, case types and denominators are not pooled. All outputs are first attempts; failure records remain. AI judgments are provisional, not specialist certification.

| Reviewer | System | Whole accepted /15 | Whole meaning error | Whole critical error | Whole uncertain | Whole execution error | Constrained critical /9 | Constrained execution error |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| A | Initialized NLLB | 0 | 6 | 8 | 0 | 1 | 5 | 2 |
| A | Trained NLLB step700 | 0 | 8 | 5 | 1 | 1 | 7 | 0 |
| A | Qualified Gemma step280 | 1 | 10 | 3 | 1 | 0 | 4 | 0 |
| B | Initialized NLLB | 0 | 4 | 10 | 0 | 1 | 5 | 2 |
| B | Trained NLLB step700 | 0 | 6 | 7 | 1 | 1 | 5 | 0 |
| B | Qualified Gemma step280 | 1 | 8 | 4 | 2 | 0 | 4 | 0 |

Constrained critical counts for initialized NLLB include only its seven successfully generated constrained outputs; the two failures are separately shown and stay in the nine-case denominator. A decrease in errors among successful outputs cannot erase a failed output. Zero whole acceptance does not mean every word is wrong.

For the primary Gemma→trained-NLLB contrast, both reviewers record net acceptance −1, no new acceptance, and loss of case003. Whole critical counts increase by2 for A and3 for B; constrained critical counts increase by3 and1. Newly unsupported certainty is recorded for cases016/018 by A and016 by B. Both primary screens remain `inconclusive`, not a passing result or an imputed score.

Training changes initialized NLLB whole critical counts from8→5 (A) and10→7 (B), while acceptances remain0→0. Completion improves21→23/24. Constrained critical counts change5→7 and5→5 with two additional assessable cases; do not treat this unequal successful subset as a clean worsening estimate. Unknown-span judgments differ between reviewers and remain separate in the full comparison.

## Why fixing the cap alone is not the next promotion step

The trained failure is case020, a repetition of the Persian word for thousand until the 512-new-token ceiling. It is retained as an execution error, not a semantic pass. Even if a prospective decoding change made this one output acceptable while every other result stayed fixed, NLLB would have1/15 acceptances against Gemma's1/15: net0, below the unchanged required gain of2. Existing critical-error regressions would remain. Therefore a cap-only rerun cannot establish the required improvement.

A short shared failure illustrates the semantic issue. Case003 instructs wearing new clothing on Bahman day. Gemma says “روز بهمن جامۀ نو بپوشید.” Both reviewers accept it. Trained NLLB says “بهمن روز، رستگار، جاامۀ نو پاییز.” Both identify loss of the instruction and wrong lexical meanings. This completed short output cannot be explained by the length cap alone. Case016 additionally changes an eleventh participant into a third deity; this is outside the permitted uncertainty about which participant is eleventh.

## Execution and cost evidence

The frozen full-adaptation recipe used 2,237 qualified pairs, five epochs,700 updates and11,185 parent exposures. Exact optimizer/RNG continuation followed the20-update persistence canary. Peak allocated GPU memory was28,609,147,904 bytes. Source/model identity, pooled-token loss, schedule, initialization and decoding are recorded in [PLAN.md](PLAN.md) and the [completed run](continue/recovered/nllb/run.json). Lower training loss is not this semantic result.

The continuation job `6aba244c6b030d633f69bee2` finished `COMPLETED` at08:54:13.961 UTC. The earlier canary was intentionally canceled after verified preservation. [Provider check](continue/completion-check.json) at09:18:11 UTC found no active jobs. Conservative rounded compute time is9+30=39 minutes, estimatedUSD1.625013 at the previously verified rate. This is not a fresh billing invoice; no current remaining-credit claim is made. The pilot stayed within its communicatedUSD3.25 allocation. Any further paid experiment needs fresh account/rate/admission evidence under the cumulative fundedUSD25 cap.

The full model/optimizer states remain in the private cloud bucket. Only small records and outputs were recovered locally. The delayed local recovery's elapsed persistence field includes the user-requested chat pause and is not a valid network-throughput measurement. Use the original attended canary measurement for its recorded admission decision.

## Integrity, interpretation and decision

The scorer validated actual model/recipe/source/work identities, package and recovery lineage, all48 NLLB first attempts, retained initialized outputs and the original Gemma run. Both fresh review files passed the existing schema, output-hash and exact-span checks. Both files were frozen before mapping/aggregation; [reviewer receipts](../translation-review-20260928/reviewer-receipts.json), [implementation review](EVALUATION-REVIEW.md), [machine-readable comparison](scored72/comparison.json), and [review freeze](scored72/blind-review-freeze.json) preserve evidence. Two focused implementation tests and the AutoCode Critic gate passed. The separate [outcome audit](OUTCOME-QA.md) passes: independent reconstruction matched all33 files and independent arithmetic matched every reported count. It does not certify philology.

These exposed DEV cases cover four works and have been reused in development. No population accuracy, significance, fresh confirmation or causal architecture claim is supported. NLLB full adaptation and Gemma QLoRA differ in model, representation, exposure and decoding. Initialized NLLB includes the declared new-row/tag initialization; it is not untouched stock NLLB. The previous16/40 and17/40 PAL-REF acceptances come from a different case set/panel and must not be subtracted from these DEV counts.

Retain Gemma step280 as the reference and preserve this NLLB checkpoint for diagnosis. Do not run PAL-REF, transfer weights to the laptop, add epochs, switch adapters or buy more credit from this result alone. Inspect the existing error/training evidence to select one discriminating next diagnostic: determine whether a correctable source-conditioning, representation, data or free-generation limitation has evidence. A diagnostic is not a replacement merit function or permission to train on DEV answers. Record the hypothesis and prediction before any new paid call. Native-script reading, unknown-word decipherment and satisfactory8GB local inference remain unproved.
