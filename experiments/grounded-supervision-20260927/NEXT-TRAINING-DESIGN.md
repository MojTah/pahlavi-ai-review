# Controlled auxiliary-training design

27 September 2026. **Preparation only; no paid run admitted.** This refines the next experiment after the negative plain/assisted comparison. The scientific question is whether a small, reviewed lexical/function task mixture improves ordinary source-only Pahlavi-to-Persian translation beyond an equivalent additional translation-training exposure. It is an exploratory recipe comparison on the existing development set, not a new untouched confirmation or a general claim about ancient-language learning.

## Two arms, one changed recipe

- **Control:** further supervised translation training from the qualified step-280 adapter, including the original translation pairs belonging to the auxiliary examples' parent passages.
- **Candidate:** the same initialization and regular translation stream, with designated parent-passage slots replaced by the reviewed contextual-gloss/function tasks. The parent passage remains the same; only the task and its target change in those slots.

Use identical base revision, adapter bytes, quantization, optimizer recipe, trainable layers, random seed, total optimizer-update budget and source-parent slot order. This controls additional update count and extra exposure to selected passages. Task prompts and answer lengths inherently differ; report actual prompt, supervised-token and task counts, and verify the real loss weighting. Equal steps alone do not prove equal token exposure or a pure causal effect of linguistic labels.

Start both arms from the same saved adapter in separate fresh output directories. Use fresh optimizer/scheduler/RNG initialization under the same declared seed and schedule in each arm; call this **further adapter training with a new optimization phase**, not exact continuation of the previous optimizer. Restore the original adapter and the same newly seeded pre-phase RNG snapshot before the second arm and verify tensor equality; do not substitute the historical checkpoint RNG state. Do not continue arm B from arm A's updated weights. One cloud base download shared by sequential arms is preferable if it avoids duplicate paid setup; source qualification and reviews can remain parallel.

## Direct execution evidence that changes the plan

The saved qualified trainer state has `global_step=280`, `max_steps=280`, `epoch=2.0`. Its final logged learning rates decline to `3.690036900369004e-07` at step280. The contract specifies a linear schedule. The final post-step scheduler binary was not loaded here, so its exact stored learning rate is not independently asserted. This is a completed schedule, not an unfinished training session that can safely be extended without a new design.

The current `runtime.train` enforces identical data/model/training identity on resume, while `bundle.tokenize_row` always constructs the translation prompt and `bundle.validate_row` rejects task/prompt fields outside its translation schema. Therefore a mixed-task run must not masquerade as an ordinary resume or place task instructions inside the attested source text. Preserve the old runtime/bundle and their historical hashes. Reuse their tokenizer rendering, answer-only masking, controls, model loading and safety checks in the smallest explicitly task-aware preparation/execution path once the data are ready.

Verified local evidence:

| File | SHA256 / observed fact |
|---|---|
| `experiments/retrain-qualified-20260927/continuation/training/checkpoint-280/trainer_state.json` | `1ba7c18671c477722b69cabb4cc204b06bce6b784218588343b5a7f827b8ee20`; completed280/280 |
| `experiments/retrain-qualified-20260927/continuation/training/contract.json` | `2f974dca27dc8c68664efe6721f7f420a801513c6cf95d80aace8c18d5e940cc`; linear schedule, initial learning rate0.0001 |
| `cloud_pilot/runtime.py`, `cloud_pilot/bundle.py` | Current source inspected; no changes made. Resume identity and translation-only preparation restrictions directly present. |

## Data and launch decisions still required

The20 qualified labels are a feasibility sample, not an adequate balanced training set. Retain source qualifications and abstentions. Add modest published noun/verb coverage and reviewed ordinary-negation/affirmative-command contrasts; a classifier that always says “prohibition” must not fit the entire function task. Classification/scope answers must be supported by the exact source and published parallel witness. Keep dictionary glosses, derived function annotations and original whole translations separately identifiable. No DEV/TEST references or corrections enter any training task.

After collection/qualification, perform a **local tokenizer-only census** using the existing pinned tokenizer: unique parents, works, forms/functions, duplicate and near-duplicate source groups, source lengths, prompt lengths and loss-bearing tokens per task. Set one fixed mixture and one small update budget from that actual census and the measured earlier training throughput; do not try a hyperparameter grid. A possible initial layout is regular translation slots plus a minority of auxiliary slots, but no ratio, learning rate, update count or dataset is frozen for launch yet.

Require a real small CPU numerical check of task masking, loss weighting and same-adapter/fresh-optimizer initialization; then use the existing paid-lifecycle readiness checks against the exact new artifacts. Preserve intermediate/final adapters on the cloud and verify small-result recovery before shutdown. A maximum incremental envelope must be checked against a fresh credit balance and provider timeout before any job is submitted. The earlierUSD17.12 observation is not current launch admission. Existing funded credit is authorized; top-up is not.

## Fixed evaluation and stopping rule

Both arms receive the same existing24 DEV inputs, unchanged source-only prompt/decoding and first-attempt policy. Reuse the frozen two-reviewer blind procedure and acceptance/critical-error definitions:15 whole cases,9 separate constrained cases, paired transitions and work-level results. Compare the candidate with the matched control and retain the existing step-280 outputs as a disclosed descriptive reference. The existing improvement screen remains unchanged. Training-task fit is a mechanism diagnostic only, never the translation merit score.

If the candidate fails that screen, preserve the null result and stop this recipe branch; do not automatically increase epochs or try several mixtures. If it passes, obtain the unchanged40-case source-only PAL-REF regression comparison before considering local delivery. PAL-REF has already been reused and is not fresh independent confirmation. Independent specialist review and eventual local8GB timing/quality checks remain necessary for stronger claims and delivery; no laptop model download occurs before satisfactory cloud quality.
