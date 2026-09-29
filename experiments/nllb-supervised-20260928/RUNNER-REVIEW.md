# Bounded NLLB canary review

Lead agent/request id: /root
Critic agent/request id: /root/nllb_final_preflight_review
Critic model and reasoning effort: inherited GPT-6 Astra and parent reasoning effort
Independent from lead: yes
Critic verdict: pass with notes
Evidence reviewed: Exact runner, HF wrapper, controller, failure-boundary tests and frozen PLAN; scientific review by /root/finetuning_kb_research.
Verification evidence: Root passed two numerical/schedule tests in 28.122 seconds, four package/lifecycle tests in 38.844 seconds and repaired actual start-event test in 0.673 seconds. Critic independently executed actual launch AST with ambiguous submission plus record-write failure and observed shutdown; nine admission negatives, inventory recovery selection, cost arithmetic and actual repaired start-event call passed.

This review admits the bounded paid canary only. Continuation requires the complete initialized24 outputs, first20 scheduled updates, verified full state, committed cloud inventory, small evidence recovery, terminal confirmation and measured throughput/persistence gates. No GPU, translation-quality or laptop-readiness claim follows from local tests.

| Source | SHA256 |
|---|---|
| cloud_pilot/nllb_train.py | 8a392db05c5a38ad75e7cc767bda05d3dc1218b9d61348d161f64fa757b7708d |
| cloud_pilot/hf_nllb.py | 87bbebcab446c523db99fb0d2974ff96c66af0d54118e59415b2ed48a5ce110a |
| cloud_pilot/test_nllb_train.py | a00c1cc685e379771c423705916e27d85c5c54391218b4a49516557e5ef1a6e2 |
| cloud_pilot/test_hf_nllb.py | f5698905826b9f912adf274ad57949009348a77ce29fc2620ac6b805213772f9 |
| experiments/nllb-supervised-20260928/cloud_control.py | 9de4c49fb4735788bb84bc7d51e7108655272ec5be28e8943f464b00735815d3 |
| experiments/nllb-supervised-20260928/PLAN.md | 10b920dcea3953f0122ed5d21405523d380e7d0a204dcf50d6340879ea63df61 |

Scientific critic's final verdict: PASS, no must-fix scientific issue in the frozen implementation. Reviewed pooled token loss, actual M2M100 shifting helper, fixed700 schedule, baseline-before-training, dropout/RNG continuation, populated-optimizer edge backward, appended-row diagnostics and atomic verified checkpoints. This critic inspected code and reported local test evidence, without independently rerunning model tests.

Lifecycle critic's final verdict: PASS WITH NOTES for canary. Previous findings corrected before any paid launch: partial saves are outside export and cannot replace verified state; record-write failure cannot bypass shutdown; actual full-state persistence is measured in a separate canary before continuation; an event keyword collision was fixed and its real call executed. The critic did not run a full generated wrapper lifecycle.

Canary compute/internal/native bounds12/18/20 minutes; continuation25/31/33. Aggregate53 native minutes at41667 microUSD/minute plus0.75 reserve equals2.958351 USD. Fresh funding, rate, no recharge, no active/duplicate trial, exact small-package round trip, clean source commit and exclusive submission journal still gate launch. No blind paid retry.

Cached Gemma comparator integrity passed the existing complete original-run validator; see [receipt](COMPARATOR-CHECK.json). Fresh blind ratings will compare retained24 plain outputs; prior ratings are not copied. Merit and whole15/constrained9 denominators remain fixed.

## Measured continuation review

Continuation verdict: pass with notes

The same independent critic `/root/nllb_final_preflight_review` audited the recovered canary and then the resource-only delta. It verified all nine small hashes, exact committed18-file inventory of16,481,560,972 bytes,20 finite update records/320parents,24 first attempts (21success/3capfailures) and the503.903386-second closed interval. Baseline failures are cases009,022,023 and remain in all denominators. No semantic acceptance is inferred.

Independent AST execution of actual `continuation_source`/`closed_minutes` yields9 closed plus50 native continuation minutes; eight identity/time/stage/recovery tampering cases are rejected. Root's three affected tests pass in1.760 seconds, including identical scientific package SHA. The actual forecast2119.195014 fits2400 seconds and persistence282.807670 fits360 seconds. Revised59-minute compute bound plus unchanged0.75 reserve is3.208353 USD, within the communicated3.25 suballocation and user25 cumulative cap.

| Final continuation source | SHA256 |
|---|---|
| cloud_pilot/hf_nllb.py | 7621083eba7e7d0468daf76d56378fd5e61282f192d10674581b39a76d3d7116 |
| cloud_control.py | c1256b26f70d292d2f2da5d85bc968d62e68e6bb66f46fa96ba98cda9126aeee |
| cloud_pilot/test_hf_nllb.py | c0f1d6d6b03be5033b0ff8a1e0bfd5e238f29e4c70693edb93ec3839f29ad273 |
| canary/termination.json | 473aeb1194e6a47be9eb95568a711215efff7983c8cab9029bccd368beec1e54 |
| canary/recovered/manifest.json | 5f3d9760ea188364c433a84cfe592db0761ff2f95b2989e7d61dd9159bb0de5f |

Runner8a392db and scientific package4ff0ae48c2de917af47525dc456d8d58604d914b3aea3a7e393dfa689e267229 are unchanged. The reviewed generic exporter excludes `checkpoint-*` names, so its local verification marker is not exported; closed canary status, runner identity and full manifest hashes bind successful reload instead. Continuation verifies every manifest file on server before loading. Fresh account/rate/cumulative cap, no recharge, clean bound source, verified input transfer and no duplicate/active job remain required. This admits one continuation, not a retry or quality claim.
