# Familiar conditional fit: complete diagnostic

27 September2026. All80 first-attempt forwards completed for the frozen20 TRAIN parents across16 works. The step280 adapter improved known-target likelihood for every selected parent; a mismatched Pahlavi source worsened it for every parent, both with and without the adapter. This supports familiar conditional fit and source dependence in this specific teacher-forced test. It does not measure free translation accuracy, establish a causal mechanism, prove generalization or validate laptop delivery. No training or free generation occurred.

## Fixed comparison

Each cell is equal-parent mean answer/terminator negative log-likelihood, in natural-log units per supervised token; lower is better. These are not percentages or the translation merit function.

| Condition | Correct source | Mismatched source |
| --- | ---: | ---: |
| Pinned base, adapter off |4.299214|8.785442|
| Qualified step280 adapter on |0.884414|4.581620|

Mean correct-source adapter gain (off minus on) is3.414800; all20 gains are positive, range0.677995–5.085921. Mean mismatched-source gain is4.203822, also positive for20/20. Mean mismatch penalty is3.697206 with the adapter and4.486227 without it; both penalties are positive for20/20. **The mean source-mismatch penalty is smaller with the adapter. Do not claim adaptation increased source sensitivity.** Every paired value, sign count, median and work summary is preserved in `analysis.json`.

All inputs reproduce the frozen TRAIN instruction, labels and original target suffix; only the predetermined source permutation changes in the mismatched conditions. Same-parent/work pairing is excluded, but these unpaired sources are not expert-certified semantic negatives. Source length/content differ and gold prefixes supply strong answer information. The20 parents were selected for a prior TRAIN diagnostic, not randomly sampled; this is a repeated-measures computational contrast, not80 independent replicates or a significance test. Historical training used NF4; this inference diagnostic uses BF16.

## Numerical and operational evidence

Independent shifted masked cross-entropy matched native model loss for all80 calls; maximum absolute mean-loss difference was4.334883261236655e-07, within the frozen1e-5 absolute/relative tolerance. Every call retained the expected adapter on/off state and restored it afterward. All80 inputs and targets matched the frozen token map; no missing slot, retry, numerical failure or generation-cap substitution occurred. The80 forward calls took29.802 seconds in total. Setup, transfer, full model verification and loading dominate the roughly9-minute job lifecycle.

The exact request was frozen in source commit `2b81b5d7cc053ffff9eface2b913f9621055408d`; job `6ab90a5e6b030d633f699327` started at12:21:49.934662UTC. Downloaded base bytes were62,578,654,714, entirely on the server. The previous qualified adapter was mounted read-only. No optimizer or model state was updated.

All seven small artifacts,164,349 bytes, passed committed provider-inventory, size and full SHA256 recovery before cancellation. Manifest SHA256: `34a218c906b10ffbbb6d06564bcfb840386ecf9666b5bdeb0451f1decfa8f00e`. Raw results SHA256: `477a8a891c1bc39ffe605e8e62b9f2269c6064c41e82e8a954186c5f2f8eb23f`. Analysis SHA256: `6f69f977f33a0eb51072aa7e96d04a2adcba7cb3453e09b251defe8f5690f152`. CANCELED was confirmed at12:30:49.139031UTC after verified recovery; all16 jobs were terminal. This is successful diagnostic shutdown. No model or adapter weights were downloaded to the laptop.

The subsequent authenticated billing page showsUSD15.82 credit andUSD14.48 period usage, with automatic recharge unset. Relative to the previous observation, displayed credit fellUSD0.38 and usage roseUSD0.41. These unequal account deltas are preserved honestly and are not a per-job invoice. The elapsed539.204-second compute estimate is aboutUSD0.374, not a billed-charge upper bound. The USD1.50 experiment envelope was not approached; no purchase/recharge occurred. Root remains the sole paid execution owner.

## Next decision

This result weakens the hypothesis that the adapter is simply inactive or fails to condition on the source. It does not explain the previously weak whole translations or repetition failure. Repeating ordinary epochs, another prompt comparison or this same likelihood diagnostic is not justified automatically. All prior PAL-REF/DEV scores, missingness and uniform merit remain unchanged.

Use the existing TRAIN-only blind error analysis to select the next intervention. Many full-meaning errors survive even where the reviewed gloss/function is preserved: equal versus limit, stealing versus coveting, being afflicted versus pain itself, and low worth versus misfortune. Only a small subset supports a local scope defect. Therefore a generic repetition of the23 function labels is not established as the best next primary intervention. First qualify narrowly defined contextual predicate/construction anchors against existing scholarly witnesses, retaining ambiguity and exact source spans; whole-passage translations alone do not certify word alignment. No new model sampling or GPU allocation is needed for that qualification.

If sufficient defensible new supervision survives independent review, freeze one contextual-supervision candidate against a matched ordinary-translation continuation from the same step280 checkpoint. Preserve parent exposure, actual supervised-token accounting, regular translation rehearsal, the fixed source-only DEV15 whole/9 constrained merit and both blind reviewers. Do not train on held-out answers, generated unverified labels or the mismatched diagnostic pairs. No next paid training recipe is admitted by this report. The broader improvement goal remains active, with current funded credit available strategically.
