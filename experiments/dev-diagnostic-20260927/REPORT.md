# Instruction diagnostic: the tested instruction change did not increase acceptance

The trained adapter improved on the original model in this development sample, but neither instruction format delivered satisfactory translations. Both trained conditions accepted the same three of the fifteen passages eligible for provisional whole-translation assessment. The next intervention should address use of attested meanings and composition, rather than assume a prompt-format repair or more epochs will solve the problem.

| Condition | Accepted / 15 | Meaning errors | Critical errors | Uncertain |
| --- | ---: | ---: | ---: | ---: |
| Original base, training-style instruction (D0) | 0 | 8 | 7 | 0 |
| Original base, fixed-evaluation-style instruction (D1) | 0 | 7 | 8 | 0 |
| Step 312 adapter, training-style instruction (D2) | 3 | 5 | 4 | 3 |
| Step 312 adapter, fixed-evaluation-style instruction (D3) | 3 | 7 | 4 | 1 |

These are two blinded AI reviewers' provisional judgments, with all four conditions for a passage assigned to the same reviewer. They are not expert certification, population accuracy, or a new PAL-REF score. The unchanged forty-case test remains 5/40 original versus 15/40 trained under its previously recorded review. Its percentages cannot be compared directly with this different DEV sample.

Independent result audit passed. Four accepted reviews originally marked source uncertainty as `not_applicable`; the still-blinded reviewer clarified that this meant no material unresolved source uncertainty, equivalent to satisfactory handling under the rubric. Original reviews remain unchanged alongside `reviewer-clarification.json`. No acceptance label changed. The raw DEV reviews were not passed through the unchanged PAL-REF validator, which also requires its own benchmark-specific schema.

The qualified DEV denominators are four passages from work 103, five from 112, four from 138 and two from 517. Both trained conditions accepted respectively 1, 2, 0, 0. All three newly accepted cases are QUALITYDEV1-003,008,009, with no accepted cases lost because neither base condition accepted a case. There is still a critical regression on 013 under the training-style instruction relative to its matching base. Switching the trained model between instructions trades a critical error on 013 for one on 002; neither is a clear winner under the predeclared rules. Full paired transitions and per-work counts are in `comparison.json`.

Nine further passages retain constrained assessment only. Each trained condition has five critical supported-span errors, two meaning errors, one uncertainty and one without an identified supported-span error. Each base condition has seven critical supported-span errors, one meaning error and one without an identified error. These are not whole-translation acceptance rates and are excluded from the primary fifteen-case count.

## What to investigate next

Some errors involve attested training vocabulary. In 002, the trained model under the fixed instruction translated `hamēmāl` as a sexual partner instead of a rival/enemy. The exact source substring appears in eight actual TRAIN passages; records 133000026 and133000027 explicitly pair it with Persian enemy wording. In 005, a named day and the righteousness sense of `frārōnīh` were lost; that substring appears in 21 TRAIN passages. Exposure alone did not secure reliable translation. Conversely, exact forms `hamāg-zōhr` and `hōšag` have no matches in the current TRAIN payload; this exact-form check is not a lemmatized vocabulary audit.

A justified next diagnostic is a separately labeled comparison with fixed, source-selected, published examples from the TRAIN archive as supporting context. Freeze the retrieval rule and allowed inventory before generation; keep DEV and TEST answers out, preserve uncertainty, and audit selected witnesses for answer-equivalent overlap. This can test whether explicit access to existing evidence helps before another training run. It would measure assisted translation, not a better unaided model or a replacement PAL-REF result. Do not use the unaudited dictionary/grammar files wholesale; see `NEXT-OPTIONS.md`.

The next preparation is one trained, TRAIN-example-assisted condition, at most 24 new outputs compared with cached D3. Keep the same assessment split. Do not regenerate the four completed conditions. The goal remains active; source selection, overlap checks and bounded runtime readiness precede the next paid job. Further training and laptop delivery remain unjustified by the present quality.

## Execution and cost

Job `6ab888ff52d0dbd7f1d99b8e` generated all 96 first-attempt outputs successfully: no errors, abstentions, token-cap hits or timeouts. Every same-instruction original/adapter pair had identical input-token hashes. All six exported files passed full SHA256 recovery. The server was deliberately canceled after verified persistence and confirmed terminal at 2026-09-27T03:31:56Z. A temporary monitoring connection failure recovered on the same job; there was no restart or duplicate submission.

The complete controlled session took about 22.1 minutes. Conservative compute accounting rose from USD 6.19 to USD 7.1103, an increment of approximately USD 0.9203; this is not a finalized invoice. The user-authorized cumulative cap is now USD 25. No model weights were downloaded to the laptop, no weights were changed, and no cloud GPU remains active.

Reproduction records: `run.json`, `predictions.jsonl`, `reviews.jsonl`, `comparison.json`, `assessment-contract.json`, `review-design.json`, `execution-audit.json`, `recovery-verification.json`, and `cloud-run.json`. Frozen source revision: `c2abd192be15449d4a1df69998c22993e020dad2`. Reviewers: `/root/dev_blind_a` and `/root/dev_blind_b`.
