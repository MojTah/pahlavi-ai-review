# Authorized inference execution

**Completed:** [Outcome and training-health verification](OUTCOME.md) supersede the startup status below. All56 first outputs were recovered and verified; the current job performed zero optimizer updates. The separate earlier96-step training was independently verified as real.

30 September 2026. [Job 6abd2a1d404719ba376138e8](https://huggingface.co/jobs/Mojionix/6abd2a1d404719ba376138e8) was accepted at15:26:21 UTC and reported RUNNING, with bootstrap complete, at15:26:52 UTC. This confirms startup, not completed inference or translation quality. Root stops active monitoring after this checkpoint, as requested; inspect this exact job on the next user check. No automatic retries, training, recharge or follow-up jobs.

The user explicitly answered “yes and we can increase the credit if needed” to the concrete credential/staging/single-job request. The user-added USD20 was visible in billing, giving USD27.62 available before launch; automatic recharge was unset. No further funds were needed or purchased. The approved envelope remains120minutes andUSD5.51, not the whole available balance. The live rate wasUSD0.041667/minute: USD5.000040 maximum scheduled compute plusUSD0.50 allowance for ancillary cost. This is a conservative planning allowance, not a provider-enforced account cap or final invoice. The provider timeout remains120minutes; startup accounting and persistence are not guaranteed by the planning arithmetic.

The exact reviewed [proposal](../execution-proposal/handoff.json) was submitted without scientific changes: retained step280 versus corrected96,28 cases/56 first attempts, BF16, identical training-task prompts, greedy seed42,512 tokens and90seconds per attempt. This diagnoses learning and familiar retention; it does not establish unseen generalization or resolve the separate NF4-training/BF16-inference question.

Only the15,474-byte prompt file required upload. The existing6,372,448-byte bundle was reused after readback SHA-256 verification. Adapter manifests/configurations were read and hashed locally; weight sizes matched their manifests. Full model/adapter weights remain cloud-only, and the runtime must still rehash them and pass both GPU prefill canaries before generation. No reference answers or review labels were transferred.

Evidence:

- [Initial live checks](live-check.json): account, hardware/rate,24 existing terminal jobs, observed credit.
- [Staging/readback](staging.json): exact inputs, manifest/config hashes and local-download limits.
- [Exclusive submission claim](submission-claim.json): authorization, refreshed rate/idle-job/output checks and approved identity. Its UNKNOWN wording is the immutable pre-call state, resolved by the following receipt; never remove it to retry.
- [Provider receipt](provider-receipt.json): accepted job ID and original SCHEDULING observation.
- [Startup observation](startup.json): RUNNING and successful bootstrap; GPU/model/canary/output success remains unverified.
- [Independent Astra review](ASTRA-LAUNCH-REVIEW.md): local wrapper and recorded-evidence PASS; reviewer made no authenticated calls.

The original proposal's NOT_AUTHORIZED/NOT_SUBMITTED fields preserve its preparation-time state. This execution record and provider receipt supersede that status without rewriting those frozen records. The app Goal remains paused. The source checkout has no Git remote; this checkpoint is local, not a GitHub update.

## Local execution review gate

Mode: Classic + Critic; reuse the existing reviewed builder and installed SDK. The only new launcher is a one-shot wrapper; no service, scheduler or automatic recovery system.

Lead agent/request id: /root
Critic agent/request id: /root/astra_runtime_plan_recheck
Critic model and reasoning effort: gpt-6-astra; existing user-selected reviewer, unchanged reasoning effort
Independent from lead: yes
Evidence reviewed: submit_once.py, live-check.json, staging.json, exact execution-proposal; see ASTRA-LAUNCH-REVIEW.md
Verification evidence: Root executed the isolated ambiguous-outcome/duplicate-claim self-check; critic independently checked current file hashes, arithmetic and control flow; actual provider receipt and startup are root-produced live evidence
Critic verdict: pass

Reproduce the no-network duplicate-submission check with the shared Python and `submit_once.py` without arguments. `--submit` is not a retry command: the durable claim now makes it refuse before constructing an API client. The next action is status/result recovery for the existing job, then fixed-denominator blind diagnostic review and one justified decision from the [forward plan](../PLAN.md), with no automatic retraining.
