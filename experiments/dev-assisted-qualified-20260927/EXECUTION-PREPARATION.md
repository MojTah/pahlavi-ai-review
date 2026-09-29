# Parallel comparison preparation — 27 September 2026

Status: **RUNNERS AND CONTROLLER IMPLEMENTED; FINAL COMMIT/ADMISSION BINDING PENDING.** Classic + Critic. Root owns integration and the eventual paid lifecycle. The user requested parallel work, a uniform merit function and use of the currently funded credit without brute-force experiments.

## What is new, and what is already done

| Intervention | Actual status |
| --- | --- |
| Gemma baseline and ordinary translation SFT | Completed and preserved |
| Original versus filtered-data Gemma retraining | Completed; small paired gains and regressions |
| Two instruction styles on base/trained Gemma | All96 outputs completed; trained acceptance unchanged at3/15 |
| Earlier Qwen3-4B Persian/English diagnostic | Completed12 outputs; different model and question |
| Qualified step280 Gemma with/without checked TRAIN examples | 48-output runner implemented and tested; not executed |
| Original Qwen3.6-27B on the same plain/assisted inputs | 48-output runner implemented and tested; not executed |
| Mixed lexical/grammar supervision or additional-text CPT | Not trained; data prerequisites remain unresolved |

The new Gemma plain arm is necessary for a within-run comparison at the qualified step280 checkpoint and identical common instructions. Earlier D3 used step312 and a different message envelope; it is a historical anchor, not a substitute matched control. Do not rerun D0–D3 or the earlier language-choice experiment.

## Uniform meaning measurement

[uniform-evaluation-contract.json](uniform-evaluation-contract.json), SHA256 `4165e8150f291c2cd6077d2daee86513ad08e1851acbfc3e83169bc40263f8c2`, binds the existing protocol, scorer and assessment/reference identities. It creates no new metric. All four conditions use the same24 DEV cases,15 whole-translation denominator, nine separately constrained cases, semantic categories and decision screen. Retain all failures and first attempts; blind each of two reviewers to model/condition and have each review all96 new outputs. Keep individual ratings and work-level paired gains/losses. Meaning preservation is primary; fluency or training loss cannot substitute.

The fixed40-case Pahlavi-to-Persian PAL-REF remains unchanged, with its source-only score separate from assisted conditions and DEV results. No criterion, reference, denominator or case is changed after seeing outputs. Historical review panels remain distinct; uniform rules cannot make different earlier raters identical measurements. AI judgments remain provisional.

The scoring contract and reference files stay local. Cloud inference receives only source inputs plus the exact admitted TRAIN examples and qualifications for the assisted arm. Both model families must reuse the same literal prompt-construction helper. Model-native tokenizers and declared decoding policies differ and must be reported; this is an operational comparison, not a causal architecture experiment.

## Funded envelope and parallel ownership

Root read the authenticated Hugging Face billing and jobs UI during this turn, recorded by08:29:43UTC. Account `Mojionix` showed **credits USD18.37**, current-period usage **USD11.86**, automatic recharge unset,12 jobs total with **running0 / scheduling0**, four completed, one error and seven canceled. This replaces reliance on the earlier compute estimate as a balance. A fresh tab recovered from the unresponsive old billing tab; it was closed after the read. No billing setting, payment, credit purchase, credential or job was changed.

The latest user instruction authorizes use of this existing funded balance, superseding the earlierUSD25 cumulative ceiling for this funded scope. It does not authorize buying more credit or automatic recharge. Keep a ledger of charges from this observed balance and recheck it at launch; intervening usage reduces the amount available. The first complete comparison retains its approximatelyUSD5 incremental compute target and at leastUSD0.75 reserve. Do not use the increased envelope as a reason for a model sweep or repeated training.

Gemma runner implementation and Qwen runtime/penalty preparation proceed in parallel under separate writers. Paid jobs may overlap only after their individual checks pass and the **sum** of bounded costs fits the available envelope. Root is the sole submit/cancel owner. Each job must retain partial first-attempt results and have its own deadline and persistence/cleanup path; no duplicate retries or speculative second training job.

## Remaining launch boundaries

- The initial independent component review passed. The final runners now include longest-prompt prefill canaries; final launch review covers that delta.
- Both runners reuse the exact shared prompts and58 attachments. A tiny random-weight native CPU Qwen generation/loading check passed; real full-checkpoint Linux/GPU checks remain inside the bounded server canary.
- The two new evidence files passed bucket SHA256 round trips. Existing HF persistence is reused; the two55-minute native timeouts reserveUSD4.58337 compute plusUSD0.75 allowance. See LAUNCH.md for exact commands and recovery boundaries.
- Freeze the launch revision and verify fresh funding, rate, zero unintended jobs, recovery paths and a bounded real Linux/model canary before the full comparison. Model weights are downloaded only on the server. No automatic paid launch follows from this document.

The [source follow-up](../lexical-feasibility-20260927/SOURCE-DECISION.md) preserves the separate deeper-training research: a real second-book reading route and a111-page extraction probe with4,665 source terms. Those findings inform later learning-regime choices; they do not manufacture verified labels or delay the independent inference preparation.
