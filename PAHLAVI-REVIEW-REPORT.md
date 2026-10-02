# Pahlavi external partial review

**Later update,30 September:** the complete external report was subsequently found locally and read. [The integrated reassessment](experiments/external-review-20260930/RESPONSE.md) records its identity, the findings of **Review project failures**, three bounded audits and the current decision. The summary-only availability statements below describe the earlier integration and are superseded by that reassessment.

Received 30 September 2026 from the user's chat message. Integration source checkpoint: `69a1e1e`. Version impact: NONE; documentation only.

## Provenance and limits

This file preserves the **supplied summary**, followed by separately labeled local verification notes. The original full report, results timeline, ranked findings table, owner list and inspection appendix mentioned in the summary were not supplied. They are not reconstructed here. The reviewer identity and review date were not provided.

The external reviewer reports that private data ZIPs were unavailable and that the timeline recount and full data-pipeline audit were stopped before completion. This is an unblinded external review, not another blinded model evaluation or a full corpus certification. The local reconciliation below checks selected claims against saved records; it is not a new full data audit.

## Supplied review summary

> **Task completed:** I stopped as you asked. The report for the developer is `PAHLAVI-REVIEW-REPORT.md`.
>
> It is a partial review. I did not have the private data ZIPs, and I stopped the timeline recount and the full data-pipeline audit before they finished. The report lists exactly what was and wasn't checked.
>
> **Main conclusions:**
>
> **Biggest bottleneck: the test set can't show whether training helps.** It has 15 passages from only 4 works and has been reused at least 5 times. Its references have never been checked by an expert. The two AI reviewers agree on every accept/reject decision, so they are not two independent measurements. The latest "gain" (1/15 → 2/15) is one passage changing because of one word (case 009), which is statistically indistinguishable from no change.
>
> **The prompt used in training differs from the prompt used in evaluation** (`bundle.py:37` vs `dev_assisted.py:92-98`). Every model is scored on a format it never trained on, which may hide what it learned. This has never been tested. There is also an untested precision difference: training on 4-bit weights, evaluating on full-precision weights.
>
> **Each continuation run restarts the learning rate at its peak** on an already-trained model, so forgetting and the effect of new data are mixed together. In the extra training data, about 84% of the target text is English, and much of the loss on very short examples just teaches the model when to stop.
>
> **Patterns in the model outputs that the team hasn't flagged:**
>
> The models copy the references' editorial notes, «(=…)» and «[…]», to present invented meanings confidently.
>
> Unknown words are written out in Persian letters without any sign of uncertainty.
>
> *zahag* ("offspring") is translated as «ضحاک» (the mythical king) by all three checkpoints. No training round fixed it.
>
> **Recommended next steps**, cheapest first. No more training is recommended yet.
>
> Re-run the existing checkpoints with the training prompt versus the evaluation prompt, in both precisions, bundled with the planned 28-prompt diagnostic. This is inference only, roughly 1–2 GPU-hours; the cost estimate is from past runs, not a quote.
>
> Build a larger set of word-pair and sentence-pair probes (the correct reference versus a minimally changed wrong version) from protected records no model or reviewer has seen yet. The actual scoring needs under an hour of GPU; the main cost is a human checking every item.
>
> Have a Pahlavi specialist check the 15 test references and the repeated errors above.
>
> The report also includes a results timeline, a ranked findings table with file and line references, a short owner action list, and an appendix of what was inspected, which checks ran, and what remains inaccessible or unresolved.

## Local reconciliation, 30 September 2026

| Claim | Evidence and disposition |
|---|---|
| Small, repeatedly inspected panel; no expert gold | Supported limitation. DEV has 15 whole translations and nine separately constrained cases across four works. It supports descriptive paired development/regression decisions, not population accuracy or fresh confirmation. The exact "at least five" reuse count was not independently recounted in this integration. Agreement alone does not establish reviewer dependence; separate contexts within the same AI family do not establish independent scientific replications. See [latest comparison](experiments/training-ready-v2-20260929/REPORT.md) and [frozen contract](experiments/dev-assisted-qualified-20260927/uniform-evaluation-contract.json). |
| Latest gain is case009 | Comparator matters. Against retained step280, corrected-v2 adds acceptance009; against previous mixed96, it restores acceptance003. Both are +1/15 and fail the unchanged screen. No formal significance claim is supported by this small, purposive, reused panel; avoid presenting "statistically indistinguishable" as an executed statistical test. See [latest comparison](experiments/training-ready-v2-20260929/REPORT.md). |
| Different training/evaluation prompts have never been tested | Prompt difference is confirmed for the cited Gemma paths, but "never tested" is incorrect. The completed [TRAIN-recall comparison](experiments/train-recall-20260927/REPORT.md) used both formats: 12 completed pairs, with 5 training-format and 4 evaluation-format acceptances per reviewer. One capped attempt and 15 unattempted slots limit inference. This does not settle prompt effects on corrected-v2 or the held-out panel. The blanket "every model" claim is too broad: NLLB has a separate encoder-decoder representation. |
| Four-bit training versus full-precision evaluation | The Gemma precision difference is documented: NF4 training with BF16 computation versus unquantized BF16-base inference. "Full precision" should not imply FP32. No matched prompt-by-precision crossover is established by the inspected records. Its contribution to errors remains unknown. See [model recipe](MODEL-AND-TRAINING-RECIPE.md). |
| Learning-rate restart causes forgetting | Fresh optimizer/scheduler and a new 1e-4 peak are confirmed for mixed continuation; four warmup updates precede decay, so the run does not simply begin at peak. Forgetting is a hypothesis, not an isolated causal result. A matched historical-only control is needed to separate continuation effects from auxiliary supervision. See [trainer](cloud_pilot/mixed_train.py) and [recipe](MODEL-AND-TRAINING-RECIPE.md). |
| About 84% of extra target text is English | Correct for previous mixed96 **auxiliary supervised tokens**, including terminators and structured output: 7,866/9,351 = 84.12%. It is not 84% of all training targets or gradient influence. Corrected-v2 is 8,305/10,583 = 78.47% of auxiliary tokens, 8,305/68,724 = 12.08% of all supervised tokens, and 153/1,536 = 9.96% of equal-example terms. See [old census](experiments/learning-diagnosis-20260929/census.json) and [corrected manifest](experiments/training-ready-v2-20260929/data-manifest.json). |
| Short targets mostly teach stopping | Short answers plus supervised terminators are a legitimate diagnostic concern. No measured terminator-loss decomposition was supplied or executed here, so their actual loss/gradient contribution and causal effect remain unresolved. Equal-example loss weighting must be distinguished from token counts. |
| Repeated Zahhak error and uncertainty handling were unflagged | Saved plain outputs from all three checkpoints contain «ضحاک» in cases021 and023. The latest [reviewer A ratings](experiments/corrected-review-20260930/reviewer-A/reviews.jsonl), including lines2,10,15,59,63, explicitly flag offspring being replaced by Zahhak and confident assignments to unresolved forms. The persistent error is real in the saved provisional assessment; "the team hasn't flagged" is incorrect. Specialist adjudication remains necessary. |
| Editorial notation demonstrates copying from references | Literal `(=...)` appears in previous-mixed and corrected case021 outputs. Its presence alone does not establish that the model copied a particular reference, that every bracketed span is invented, or how training caused it. Source tracing and semantic adjudication remain required. |
| Inference will take 1–2 GPU-hours; probes under an hour | Preserve these as external planning estimates, not verified current costs or runtime guarantees. Expanded arms, caps, model reloads and specialist review affect scope. No current funding, provider price or live job inventory was checked here. |

## Integrated next-action priorities

1. Update the existing 28-prompt acquisition-versus-transfer diagnostic for corrected-v2, rejoining every prompt/target to its corrected selected exposure. Keep the old packet and prior partial format comparison as historical evidence. Freeze the smallest additional prompt/precision contrasts that resolve a named question; do not automatically multiply every task into a large factorial run.
2. Obtain Pahlavi-specialist adjudication of the existing 15 whole references and persistent source/sense/participant errors. Preserve the current rubric and benchmark bytes. Any new confirmation or contrastive probe set must use separately qualified, unexposed material with source-supported alternatives and genuinely wrong contrast targets; foundation-model pretraining exposure cannot be guaranteed absent. Teacher-forced probe scores do not substitute for free translation quality.
3. Decide on a controlled training intervention only after acquisition, contextual application, retention and prompt/precision evidence are distinguished. Do not infer that more epochs, another architecture, a full-pool run or a schedule change is already justified.

This integration authorizes no training, cloud inference, model-weight download, paid execution, external contact or publication. Existing execution and permission boundaries remain in force. The complete external report and its missing appendices remain unavailable in this project.
