# Next controlled translation comparison

5 October 2026. Local preparation only; no new provider call, credential use, training, submission or model-weight download.

The completed dictionary comparison improved provisional acceptance in the fixed familiar DEV sample from 2/15 to 5/15 for each fresh blinded AI reviewer. Five gains and two regressions remain recorded. Ten dictionary-assisted passages still failed acceptance. The lexical-versus-compositional mechanism is unproved, and these exposed passages do not measure unseen accuracy. Astra passed the bounded continuation screen and the narrow recovery-validator repair, with these limits.

## One hypothesis

The same retained Gemma4 31B step280 model may preserve useful dictionary assistance while producing fewer unsupported explanatory glosses when given one more specific instruction. This is a compliance hypothesis, not a claim that punctuation itself causes error.

- A: the previous dictionary-assisted B messages, exactly, with fresh generation.
- B: the same complete source and dictionary user message; append exactly this sentence after one newline to the system message:

  `Do not add explanatory glosses or equate alternative dictionary meanings unless the source context supports the added meaning.`

No senses are removed, selected using expected answers or rewritten. No case-specific examples, answer hints or post-generation cleanup. All 15 cases remain, with 30 fresh first outputs. Historical results and ratings remain unchanged. Case017's reported negation-scope reversal is separately flagged for specialist checking; this experiment adds no targeted negation correction.

## Fixed measurement and execution

Same model/revision/retained adapter, BF16 base with FP32 LoRA, eager attention, greedy generation, seed42, thinking disabled, fresh context/cache per output. Same 90-second first-attempt limit, 4096 output tokens, 8192 input cap and 12288 context limit. Actual cached tokenizer replay validates all 30 frozen inputs, 480–5156 tokens, including the new longest input. No truncation.

Preserve the semantic merit and two fresh opaque 30-record review packets. Report each rater separately and preserve disagreements. The existing continuation screen requires net at least two newly accepted cases across at least two named works for each rater, no increase in critical counts, and no accepted-to-critical transition. This is continuation evidence only. Capped, timed-out, failed, missing or technically invalid attempts make the primary comparison inconclusive; valid abstention is not acceptance. Never exploit a failed control or silently omit a case.

The 60-minute/USD2.51 draft was rejected locally: its 3000-second compute window cannot admit the unchanged 3420-second post-canary schedule/export reserve. The concrete preview instead preserves 6600 compute seconds, 7020 internal seconds and 120 native minutes, proposing USD5.01 compute. Exit early when complete. Fresh live rate, funding, cumulative funded spending, idle jobs, bucket privacy, retained provenance and source readback remain launch gates; this is not an all-account billing guarantee.

## Readiness and ownership

Agent Company: Main is sole integration/execution owner. Two implementers owned separate runtime and scorer files; a separate critic is External QA and the existing Astra chat is External Judge. No overlapping writers or Antigravity outsourcing. Separate versioned files are necessary because the old frozen contract prohibited dictionary content in A and required identical system prompts. Old code, specimens, merit and hash pins remain untouched.

`prepare.py` freezes/replays source-only input/contract bytes. `prepare_runtime.py` creates a no-network Hugging Face SDK1.23 preview. `score.py` validates closed recovery, exact preview/input/contract identities, token/text replay, denominator accounting, opaque provenance and both reviews. CPU/mock tests and SDK roundtrip do not prove real GPU behavior: the server must pass the longest-input prefill canary with zero experimental outputs and zero optimizer updates.

Review concrete files before launch. Any correction to the frozen prompt/runtime requires a new explicit revision and renewed review; do not re-pin a failed result into eligibility. Exact run-specific credential/transfer/paid approval remains required. After authorized startup, hand off the long job without continuous polling, as requested. Recover small result artifacts only on return, then run the unchanged scoring pipeline.

## Decision after results

If the fixed screen passes, retain this prompt as a provisional DEV candidate and review remaining failures before separately qualified confirmation. If it fails or is inconclusive, preserve the result and revise the research decision rather than repeating the same job or initiating training automatically. No training, model switch or local weight download is admitted by this plan.
