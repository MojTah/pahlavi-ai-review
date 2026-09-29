# Active attended run

**Completion update, 27 September 2026:** Both arms completed48/48 updates and768 ordered slots; all48 first-attempt DEV outputs succeeded. The closed export was announced14:58:50UTC. At14:59:34UTC the controller verified committed provider inventory and recovered18 small evidence files (278467bytes) with full SHA checks. Both adapter weights remain in the cloud. Deliberate shutdown was confirmed CANCELED14:59:55.992UTC; `post-stop-inventory.json` confirms all18 account jobs terminal. No further monitoring of a running GPU is needed.

Authenticated Chrome billing after shutdown displayedUSD13.70 credit andUSD16.61 current-period usage, automatic recharge unset. Displayed credit fellUSD2.08 and usage roseUSD2.08 from the last admission observation; this is not an exact per-job invoice. See `post-stop-billing.json`. No recharge or local model-weight transfer occurred. Actual local provenance/prompt/token conversion passed and two fresh independent blinded semantic reviews are in progress; completed computation does not establish better translation.

The launch snapshot and recovery instructions below remain historical evidence.

Root is the sole lifecycle owner. Job `6ab9237d52d0dbd7f1d9c66b`, run `555064e068b54aacafee67e37375ec78`, source `0c2b869c0e0c0bd08fd0014a9130c14b4366e934`. Submitted14:09:01UTC; provider started14:10:41.773UTC on27September2026. Startup and pinned Linux/A100 environment checks succeeded. This document is a launch snapshot, not a live status source.

Use the project HF interpreter with `-B -X utf8` and `experiments/contextual-supervision-20260927/cloud_control.py observe --attempt 2`. Use the same script with `recover --attempt 2` only after `ready_to_persist`; then `stop --attempt 2` and confirm terminal state. No resubmission, timeout extension, further attempt or automatic top-up. Model/adapter weights stay in the cloud.

The wrapper began at14:10:41UTC. Its declared compute alarm falls around15:15:41UTC and internal export/persistence deadline around15:20:41UTC, with provider-native75minutes as the outer fallback. These are schedule estimates from the observed start, not a provider completion guarantee. Observe provider state and actual phase logs throughout. Preserve closed partial evidence if interrupted; never call an incomplete comparison successful.

Initial fresh creditUSD15.78, usageUSD14.53, automatic recharge unset at14:04UTC; retry planning reservationUSD3.625025, separate from the earlier startup charge. Final billing must be refreshed after terminal confirmation.

Local review preparation runs in parallel in Classic + Critic mode: writer `/root/train_review_01` owns the isolated DEV48 converter and its tests; `/root/final_external_judge` independently checks provenance and unchanged rubric/denominators; root integrates. Runtime sources stay frozen. Two fresh blinded semantic reviewers are assigned only after verified cloud evidence is recovered and the job is stopped.
