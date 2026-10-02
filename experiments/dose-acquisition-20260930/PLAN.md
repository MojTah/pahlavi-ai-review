# Controlled acquisition trajectory

Status: preparation, not launched. Classic + Critic; Sol6.1 implements isolated training/runtime modules, root integrates and is the sole execution owner, and a distinct Astra reviewer must approve the exact contract before launch. The user authorized this pilot with “okay, do that then!” and previously permitted using available funded credit. No automatic follow-up, recharge, or local model-weight download.

## Question and fixed intervention

The completed matched-NF4 control did not rescue complete lexical acquisition: both blinded reviewers accept0/6 cases for both checkpoints in both precisions. Precision changes some individual negation/event errors, so hold it fixed. Test whether the model acquires the exact taught lexical inventories with repeated exposure while retaining passage translation.

Start from qualified Gemma4 31B step280. Repeat the **exact existing corrected1,536-row ordered pilot four times**:6,144 forwarded examples,384 optimizer updates, microbatch1, accumulation16. Preserve all token arrays, targets, masks, canonical IDs,12:2:2 task proportions, NF4/double quantization/BF16 compute, FP32 k-bit preparation, LoRA architecture and answer-only per-example loss. No newly selected training examples, repairs, failure-specific weighting or reshuffling. The full clean pool remains9,973 unique prompts; it is not all trained in this diagnostic.

One fresh AdamW optimizer and one linear384-step schedule, learning rate1e-4, warmup4, seed3407. Save adapters at96,192,384 without resetting optimizer or scheduler. Track actual training forwards rather than collator read-ahead. Save20-step technical-admission adapter and evidence too. Adapter snapshots do not contain full optimizer/RNG resume state; no automatic continuation is supported.

The longer schedule changes the learning-rate trajectory relative to the historical96-step run. This is a **within-run acquisition trajectory**, not a causal isolation of repetition or a clean old96-versus-new96 comparison. Historical results remain contextual only.

## Frozen evaluation

No reference answers enter generation. Greedy decoding, thinking disabled, exact pinned model/tokenizer, matched NF4 and BF16 autocast throughout. Preserve task-specific messages and caps:

- Existing lexical cases LD001–006 at96 and192:12 outputs. These are exposed acquisition probes, not generalization.
- All28 existing acquisition/retention diagnostic cases at384:28 outputs. Compare against the already completed NF4 step280 baseline using identical prompt tokens and numerical policy. Re-rate the cached baseline jointly and blindly with the new outputs.
- All24 unchanged source-only fixed-merit cases at baseline and384:48 outputs, retaining15 provisional whole translations and9 constrained safety cases separately. Exact `dev_assisted.messages(row, 'plain', [])`,4,096-token/1,200-second caps, unchanged references and scoring screen. Both endpoints are newly run in matched NF4; do not substitute old BF16 answers.
- Five newly frozen qualified confirmation cases at baseline and384:10 outputs. Four lexical forms exclude pilot forms/entry families across tasks; one inscription excludes the pilot source group. Broader dictionary editions remain shared. These are pilot-heldout cases, **not proven unseen by step280, pretraining, or all prior reviewers**, and too small for a generalization claim. No additional independently qualified composition families were available; do not pad the panel.

Total98 new first attempts, plus28 cached baseline diagnostic outputs for comparison. No intermediate evaluation inside the optimizer trajectory. Run the29 baseline outputs before optimization; evaluate saved dose adapters after training. Missing, timed-out, capped or failed scheduled outputs stay in their original denominators and make the quality decision inconclusive. Never retry an answer or select a checkpoint using interim quality.

## Decision after recovery

Verify all cloud hashes, exact exposure/order, finite gradients/loss, changed trainable tensors, frozen buffers, fresh optimizer and uninterrupted scheduler before semantic interpretation. Two separate blinded AI reviewers report counts per module/checkpoint; preserve disagreements, partial inventories and critical negation/event/uncertainty errors. They are provisional reviewers, not expert calibration.

An acquisition signal requires final complete-inventory acceptance to increase by at least2/6 over cached NF4 step280 in **both** reviewers. The96/192 checkpoints describe the trajectory;384 is the preselected endpoint. To propose full-pool training, also require preservation of every baseline-accepted whole-passage case, no increase in whole or constrained critical errors, and no new accepted-to-critical fixed-merit transitions in either reviewer. Confirmation must show at least one identical case newly accepted by both reviewers without increased critical errors; otherwise transfer is unresolved and needs method/evidence review. These are operational screens, not significance tests or proof of general performance.

The original fixed-merit model-promotion screen remains unchanged, including its net gain and cross-work requirements. Meeting this pilot's acquisition/retention screen does not promote a model, authorize full-pool training, or justify downloading weights locally. If acquisition fails, close automatic repetition and investigate objective/task design or evidence-conditioned methods; do not simply add epochs. If retention/safety fails, investigate that tradeoff first.

## Time, funds and recovery

Provider timeout360minutes; internal deadline350minutes with10minutes reserved for export/persistence within that envelope. A compute alarm stops the child with the export reserve intact. At the previously observedUSD0.041667/minute, maximum computeUSD15.000120; allowUSD0.50 separately for incidental charges, total planning allowanceUSD15.51. Verify current funded balance, exact hardware rate, private bucket, idle jobs and approved inputs immediately before submitting. No recharge, parallel paid job, extension or retry.

Historical96-step training took1,819.185seconds; four-pass extrapolation is121.28minutes, or157.66minutes with1.3× reserve. Prior corrected DEV24 generation took238.679seconds (maximum32.535); these BF16 observations motivate planning but do not prove NF4 completion time. Per-case caps do **not** all fit simultaneously:48×1,200seconds alone exceeds this job. Completion is conditional on measured progress, and a bounded inconclusive outcome is possible.

Planning allocations: bootstrap/load/checks20minutes; baseline29 outputs40minutes; training160minutes; remaining69 outputs/reload110minutes; export/persistence10minutes; margin20minutes. Baseline must complete without failures within its40-minute allocation before optimization. After20updates and at96/192, continue only if the length-aware remaining-training forecast with1.3× multiplier plus the full110-minute remaining-evaluation allocation and300-second reload allowance fits the actual child deadline. Do not reduce the panel to pass admission.

Before a fixed-merit attempt, require enough child time for its full1,200-second cap plus60seconds finalization; require90+60seconds for each acquisition/confirmation attempt. Export time is reserved outside the child. An incomplete panel is inconclusive even if training completes. Preserve durable attempt ledgers, partial adapters and stage receipts; output manifests do not prove remote persistence until authenticated bucket readback. Maximum export inventory must cover all four adapter snapshots and small evidence. No optimizer-state resume claim.

## Launch gates

Unchanged historical helpers and `training_admission` remain frozen. Versioned modules must pass real tiny-model Trainer checks, prompt/token reconstruction, schedule/deadline/failure tests, exact offline SDK serialization and export checks. Then freeze source/data/prompt/protocol/runtime/limits artifacts, completed prerequisite diagnostic, reasoned decision and test evidence. A distinct Astra reviewer must approve that exact contract. The user authorization record must accurately describe the authorized bounded pilot, not claim the user inspected hashes. Root alone stages and read-verifies the admission tree, calls the existing one-shot submission gate, verifies startup, and stops active assistant work during the long job.
