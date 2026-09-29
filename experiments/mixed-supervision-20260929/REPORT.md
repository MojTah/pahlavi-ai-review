# Mixed-supervision continuation: paired translation outcome

29 September 2026. **Do not replace retained Gemma step280 with this candidate.** Both blinded reviewers find one accepted whole translation before and one after. Both identify the same new acceptance and lost acceptance, while critical errors increase. The unchanged improvement screen fails for both. This is a negative result for this specific96-update continuation, not proof that the new corpus or all mixed-task training is ineffective.

## Matched results

The exact same24 source-only prompts and greedy decoding were used. Both models completed24/24 first attempts without errors, caps or replacement. Two fresh-context AI reviewers each rated48 shuffled, opaque records. The15 whole translations and9 constrained cases remain separate; reviewers are never pooled.

| Reviewer | Model | Accepted /15 | Meaning error /15 | Critical error /15 | Uncertain /15 | Constrained critical /9 | Constrained overconfidence /9 |
|---|---|---:|---:|---:|---:|---:|---:|
| A | Previous step280 | 1 | 10 | 4 | 0 | 3 | 4 |
| A | Mixed continuation (+96 updates) | 1 | 7 | 6 | 1 | 4 | 3 |
| B | Previous step280 | 1 | 10 | 3 | 1 | 4 | 3 |
| B | Mixed continuation (+96 updates) | 1 | 6 | 6 | 2 | 5 | 1 |

Both reviewers: newly accepted case009; lost case003, which changes from accepted to critical error. Net acceptance gain0 (required at least2). The only new acceptance is in workparsig:112 (required gains in at least2works); workparsig:103 loses one. Whole critical errors rise by2 for A and3 for B. Constrained critical errors rise by1 for each. ReviewerA additionally flags newly unsupported certainty in case018; B does not. These judgments remain separate, not adjudicated by the lead.

Some category counts improve: lexical-meaning failures fall13→11 for both reviewers, and omissions/unsupported additions decrease. Those limited improvements do not compensate for unchanged acceptance and more critical errors under the frozen merit function. Lower total overconfidence counts also cannot erase a new case-level regression.

## Two concrete changes

**Regression, case003.** The reference instructs wearing new clothing on Bahman day. Previous output: «روز بهمن جامۀ نو بپوشید.» New output: «بهمن روز چهارم جامۀ نو بپوشد.» Both reviewers identify the unsupported addition «چهارم» as a material change to the calendar instruction. ReviewerA also flags the altered grammatical construction; B does not.

**Improvement, case009.** The previous blessing used «درنای رود» where the reference requires the length of the river. The new answer says «درازای رود» and preserves the complete blessing. Both reviewers accept the new answer and reject the previous one for that lexical error.

## What this run tested

Starting from the retained qualified step280 adapter, this run performed96 additional optimizer updates on1536 selected examples:1152 historical translation pairs and384 newly qualified auxiliary examples. Every update used12 translation,2 lexical and2 other auxiliary slots (grammar, documentary, or inscription). The full10,151-record unique pool was prepared, but this budgeted pilot did not train on every entry. Training took1852.14seconds; the entire provider job completed successfully, including output persistence. Training loss and completion are not translation-quality measures.

This contrast tests the resulting candidate against its parent. It does not isolate new data from additional training, learning rate or task mixture. It cannot identify a causal source for the regression. The four-work development panel has been exposed in earlier experiments; this is descriptive development evidence, not population accuracy, statistical significance or fresh confirmation. The1/15 strict whole-answer acceptance must not be read as a percentage of correctly translated words. Older PAL-REF40 scores used a different set/panel and are not directly comparable. Both reference screening and AI judgments remain provisional, without specialist philological certification.

## Decision and next step

Keep step280 as the retained reference; preserve the new adapter for diagnosis, but do not promote it, download weights to the laptop, run the PAL40 follow-up, add epochs or launch another paid run from this result. First inspect the training-side word/sense/context mappings and mixture for evidence explaining regressions, using independent TRAIN/development diagnostics. Do not turn these24 DEV answers into training labels. Choose one further experiment only if that audit identifies a testable correction; additional dictionary volume alone is not evidence that more of this same training will help. No new training or paid job was launched during this comparison.

## Verification and evidence

- [Frozen plan](PLAN.md): unchanged two-reviewer15/9 improvement screen.
- [Cloud recovery](recovery.json):15 small files plus manifest,236759bytes; exact hashes verified. Two adapter weight files remain cloud-only; provider sizes/Xet commitments observed, no local weight hash recomputation.
- [Reviewer receipts](../mixed-review-20260929/reviewer-receipts.json): fresh contexts, isolated folders,48 judgments each, both frozen before aggregation.
- [Full machine-readable comparison](scored/comparison.json) and [frozen reviews](scored/blind-review-freeze.json).
- Reused meaning validation/aggregation helpers unchanged; two focused integrity/score tests passed independently. All30 prepared evidence/packet files independently reconstructed byte-for-byte, with a separate96-record mapping/reference check.
- [Independent audit](OUTCOME-QA.md): recovery, blind packets, frozen rating provenance, independent arithmetic and report consistency PASS. This audit does not certify the semantic judgments.

Reproduce aggregation into a fresh folder: `python -B -X utf8 -m scripts.review_mixed score experiments/mixed-review-20260929 <fresh-output-dir>`. No inference, cloud compute or model download is performed.
