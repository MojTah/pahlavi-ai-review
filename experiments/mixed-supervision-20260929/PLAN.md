# Mixed supervision pilot: one candidate, then stop

29 September 2026. User authorized starting one cloud training job and ending the Codex turn while it runs. No continuous agent monitoring, automatic follow-up experiment, recharge or local pretrained-weight download. Mode: Classic + Critic. Root owns launch; data and server writers own disjoint files; final critic is read-only. Existing Scientific Research Methods workflow applies.

## Question and fixed comparison

Does a bounded continuation of retained qualified Gemma4-31B step280, using the newly source-qualified auxiliary tasks, improve the existing source-only Persian translation merit? Start from the exact pinned base and step280 adapter; fresh optimizer and RNG. The unchanged step280 plain DEV24 outputs are the comparator. This measures the resulting candidate versus the retained model; it does not isolate auxiliary data from the effect of further training or identify which source caused a change. No backbone switch, hyperparameter grid, synthetic Persian gold or benchmark-derived training labels.

The frozen source-qualified-v1 release remains unchanged. All available records receive an offline tokenizer census; a bounded pilot uses a predeclared subset. The large resource is not claimed to have been fully learned in this run. The selection is source-based and reproducible, with no DEV answer or model-output selection.

## Exposure and learning

96 optimizer updates; microbatch1; accumulation16; seed3407. Every update has12 original Persian translation slots,2 lexical inventory slots and2 grammar/document/inscription slots. These are75%,12.5%,12.5% of the equal-example loss weight. Token totals and sequence lengths are measured separately; short dictionary answers must not silently obtain pooled-token weights or swamp translation. Sequential order is fixed, with no trainer shuffle.

The1536 slots contain1152 original TRAIN pairs,96 Persian lexical inventories,64 CPD English inventories,32 MMP English inventories,127 grammar units,57 documentary spans,4 unique Kanheri pair types and4 S23 spans. Exact selection, exclusions, duplicate grouping and token census are frozen in data-manifest.json. Full form/sense bundles, grammatical qualifications, languages and source scope survive. CPD's structured target is a separately instructed lexical task; English targets are never relabeled as Persian. Historical prompts and token arrays must reconstruct exactly. New arrays supervise answer plus terminator only and mask every prompt token; no truncation beyond2048 is permitted.

Keep the previously exercised LoRA rank16, alpha32, dropout0, trainable modules, NF4 double quantization and BF16 compute. AdamW: learning rate0.0001, betas0.9/0.999, epsilon1e-8, weight decay0, gradient clipping1.0, linear schedule,4 warmup updates. This is a conservative bounded extension of the existing recipe, not an empirically optimized mixture. A single fresh96-step optimizer schedule is used; the20-update technical canary stays within the same run and does not restart the schedule.

## Automatic execution and stop rules

The first20 real updates must show finite losses/gradients, nonzero adapter updates, correct order/masks and a conservative measured projection that leaves room for the remaining76 updates, fixed evaluation and cloud persistence. Stop and preserve evidence if the projection does not fit. This is a technical/cost admission check, not a translation-quality score. Any numerical, identity, order, export or deadline failure ends this attempt; no retry or epoch extension.

Save the final adapter in the existing private cloud bucket, release training state and reload the original BF16 base plus candidate for the same existing source-only plain DEV24 protocol. Verify exact saved prompt token identities; greedy decoding, seed42, thinking disabled,4096 generated-token ceiling and unchanged first-attempt/error rules. No answer references travel to the job. Preserve incomplete/capped outputs rather than shrinking denominators. All outputs and logs remain on cloud until the user returns.

After completion, use the same two-reviewer15 whole/9 constrained merit contract: net accepted gain at least2 for both reviewers across at least2works; no increased critical count, accepted-to-critical transition, worse constrained critical error or newly unsupported certainty. Incomplete output makes the formal screen inconclusive. Loss reduction is not a substitute. A failed screen stops this recipe; a pass permits discussion of the unchanged PAL40 regression test, not automatic promotion or local delivery. No semantic checkpoint look occurs during this unattended job.

## Cost and readiness

Live observation29 September: account usageUSD18.73, funded creditUSD11.66, cumulative capUSD25, remaining headroomUSD6.27;22 jobs all terminal. Autorecharge unset. The A100-large price is41667microUSD/minute. Native100 minutes costs at mostUSD4.16670 compute at that rate; reserveUSD0.50 separately, total planning allocationUSD4.66670. This leavesUSD1.60330 below the observed cumulative cap. It is an engineering reservation, not a provider invoice guarantee. No purchase or billing configuration change.

Use the existing pinned Linux image, locked packages, checked base-fetch/export helpers and private bucket. Internal95-minute deadline sits inside the native100-minute timeout; preserve an explicit persistence tail. Final and useful intermediate adapters stay on cloud; do not retain huge optimizer/base copies unnecessarily. Available private storage was25.6GB. Root checks exact package identities, local tests, current SDK contract, read-through transfer, idle jobs and live credit/rate before submission.

Current status: PREPARING. Exact-artifact tests and independent launch review are required. CPU/random-model checks do not prove GPU/NF4 behavior; the in-job20-step canary covers that boundary and must fail closed. Once one provider job is accepted and its startup state verified, root records its ID/link and ends the turn. The existing Codex goal is already paused and stays paused. No watcher or recurring automation is created.

## Pre-launch timing correction

The initial80-minute proposal was revised once, before any job, to100 native /95 internal /85 computation minutes, retaining the600-second export reserve. Earlier measured candidate training took944.8 seconds for48 updates (contextual attempt2 driver.log line120). The new first320 rows contain57,074 tokens, about178 per row versus the prior roughly142; a linear proxy gives about495 seconds for20 updates. With the unchanged1.3 safety factor, remaining-step ratio3.8 and1,200-second reload/evaluation allowance, the former65-minute computation window would likely reject continuation. The added time fixes that predictable budget-envelope mismatch without changing data, optimization or stop criteria. It is a forecast, not a promise of GPU speed; the real20-step measurement still controls admission. This is one evidence-led estimate revision within the existingUSD25 authorization.
