# Four-pass training result — 1 October 2026

**The model learned the taught dictionary inventories, but did not pass the fixed passage-quality/safety or confirmation screens. Do not promote this adapter or automatically extend training.**

Classic + Critic: root owns recovery and analysis; Astra (`/root/dose_design_critic`) checks execution integrity; two fresh-context Sol6.1 reviewers (`/root/dose_blind_a`, `/root/dose_blind_b`) independently assess a jointly blinded packet. Development version remains0.11.5; version impactNONE (result analysis only).

## Execution actually observed

- HF job `6abd57e0fbc85ba68235c601`: COMPLETED,30September2026 at21:26:58UTC (18:26:58Halifax). Provider RUNNING duration9,914.892seconds (2h45m15s).
- Gemma4 31B qualified step280; unchanged corrected1,536-example pilot repeated four times. Exactly384 optimizer updates and6,144 forwarded examples; the9,973-prompt full pool was not trained.
- Actual optimization duration8,003.701seconds (2h13m24s). Mean logged loss per pass:0.84897,0.45948,0.25123,0.13317. Loss is a fitting measure, not translation accuracy. The Trainer reports one epoch over the pre-expanded four-cycle stream; that does not mean only one pass over the1,536 distinct examples.
- All29 baseline and69 post-training first attempts completed successfully. No missing, capped or timed-out outputs. Prompt tokens, matched NF4 numerical conditions and all saved checkpoint identities remain inspectable in recovered records.
- Authenticated readback verified hashes for21small files plus the manifest:896,608bytes. Four adapter objects remain in the private cloud bucket with expected sizes. The runner's adapter SHA-256 values are recorded; their bytes were not independently downloaded/rehashed locally. No model weights downloaded.
- Conservative rounded compute estimateUSD6.916722 at the launch-observedUSD0.041667/minute, below theUSD15.51 allowance. This is not an invoice or a fresh balance check; incidental charges are not calculated here.

Evidence: [terminal/readback](terminal.json), [technical audit](RESULT-INTEGRITY-REVIEW.md), [training record](recovered/dose/training/run.json), [per-update progress](recovered/dose/training/progress.jsonl), [baseline outputs](recovered/dose/evaluation-baseline/predictions.jsonl), [post-training outputs](recovered/dose/evaluation/predictions.jsonl).

Verification scope: the lead reproduced every recovered small-file hash, the exact 1,536-row token/mask cycle repeated four times, all 6,144 ordered exposures, 384 update records, snapshot counters, and finite loss/gradient logs. [Runnable check](verify_results.py) and [recorded result](root-verification.json). The separate Astra technical audit is **PARTIAL**, not a full independent PASS; its unfinished checks are listed in its report. Neither this analysis nor the earlier prelaunch approval certifies a new training launch.

## Paired semantic comparison

The same frozen meanings, scope rules and fixed denominators were used.126outputs were jointly blinded:98from this job plus28cached matched-NF4 step280 diagnostic outputs. Counts below are this fresh paired review, not a merged timeline of older panels or reviewer decisions.

| Panel | Starting step280, reviewers A/B | Final384, reviewers A/B | Interpretation |
|---|---:|---:|---|
| Complete taught lexical inventories |0/6,0/6|5/6,5/6|Acquisition screen passes; this is recall of exposed examples.|
| Conditioned grammar |3/4,3/4|4/4,4/4|Small diagnostic gain; context was supplied.|
| Inscription task recall |1/2,2/2|2/2,2/2|Reviewer disagreement on one baseline case.|
| Historical passage diagnostics |2/12,2/12|9/12,9/12|Mixed exposure panel; not12new independent generalization examples.|
| Targeted sense-in-passage diagnostics |0/4,0/4|3/4,3/4|Improved on these fixed diagnostic occurrences.|
| **Fixed whole-passage merit** |**0/15,0/15**|**1/15,1/15**|Only one newly accepted passage.|
| Critical errors within fixed15 |3/15,4/15|5/15,6/15|Safety worsened for both reviewers.|
| Critical supported-scope errors, constrained9 |2/9,2/9|3/9,3/9|Separate safety panel; no whole-translation accuracy assigned.|
| Five pilot-heldout confirmation cases |1/5,1/5|1/5,1/5|No newly accepted case in either review.|

Lexical trajectory: baseline0/6 for both; step96=0/6(A),1/6(B); step192=1/6for both; final384=5/6for both. The final endpoint was preselected, not chosen after comparing checkpoints. All six taught inventory cases are assessed semantically; JSON schema is a separate field.

Examples: LD003 now preserves all of “inactive, powerless, useless”; LD004 preserves “inactivity, impotence.” LD006 still omits required senses/qualifications. The single newly accepted fixed passage isQUALITYDEV1-002. New critical classifications include invented participants inQUALITYDEV1-012 and turning affliction into killing in constrainedQUALITYDEV1-022. All case evidence and disagreements remain in [paired transitions](case-transitions.jsonl).

Both reviewers therefore pass the lexical acquisition gate but fail the retention/safety and confirmation requirements. **The frozen full-pool-proposal screen fails.** There is no accepted-whole-to-critical transition because this fresh baseline had zero accepted whole passages; that does not override the increased critical-error count. No model promotion follows.

Six of126 labels differ between reviewers; preserve both. They used separate contexts but the same model family and shared provisional references, so their agreement is not statistically independent expert validation. The repeatedly used15passages from four works cannot establish population accuracy or a statistically reliable improvement. The five confirmation cases exclude this pilot's specified forms/source group, but base/older-checkpoint exposure remains unknown.

Reproduce counts: `python -B -X utf8 experiments/dose-acquisition-20260930/live-execution/summarize_reviews.py`. The script enforces exact coverage, labels, types, duplicate-answer consistency, denominators and paired decision rules. [Machine-readable summary](review-summary.json), [review A](reviewer-a.jsonl), [review B](reviewer-b.jsonl).

## What this changes

This result rules out the strong claim that the current model cannot learn these lexical targets at all. It does not identify repetition alone as the cause: the longer schedule also changed learning-rate exposure, as the frozen plan already states. It does not show that memorized dictionary inventories transfer adequately to passage translation.

The JSON wrapper did not prevent acquisition of five of six complete inventories. Its overhead and task mismatch remain reasonable design concerns, not proven causes of the remaining failure. Latin transcription versus original-script reading was not tested by this experiment.

Do not buy another repetition of this exact subset. The next proposal should address the user's full-data goal: preserve the rich source archive, derive concise task-appropriate targets without losing senses/qualifiers, balance dictionary and sentence supervision, and define full-pool exposure and unchanged quality/safety evaluation before any paid launch. The failed transfer/safety screen must be acknowledged and reviewed when deciding that new recipe; simplifying targets or enlarging data is not guaranteed to repair it. Specialist reference calibration and a genuinely protected evaluation remain unresolved.

No additional job, recharge, full-pool training, model promotion or local weight download was performed by this result check.
