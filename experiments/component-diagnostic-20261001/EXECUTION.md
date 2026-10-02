# Authorized component inference execution

1 October 2026. Classic + Critic, root sole writer and execution owner. The user's “Happy with the changes as you wanted. Another test on.” authorizes the previously described four-case/twelve-output comparison. No training is authorized by this test. PROTOCOL.md and packet-manifest.json remain historical local-packet snapshots; this record supplies the separate runtime contract.

- One retained Gemma4-31B step280 adapter, pinned publisher revision and exact saved tensors. BF16 base, FP32 retained LoRA, eager attention, no thinking, fresh context/cache for every output. No numerical/model sweep.
- Fixed case order Kanheri, Berk.25, TB3, Zand; condition orders ABC/BCA/CAB/CBA. Exactly twelve first attempts; same greedy seed42, 256-token cap,2,048-token context cap. Actual server template text/token receipts must reproduce all twelve local receipts without truncation.
- Ninety seconds is a **cooperative generation cutoff**. Hung prefill/CUDA work is additionally bounded by the child watchdog,50-minute parent compute alarm,55-minute internal finalization limit and60-minute provider timeout. After loading/prefill, all twelve90-second allowances plus180seconds finalization must still fit. No automatic retry, model promotion or follow-up run.
- Input and retained-adapter mounts are read-only. The only new input is the21,374-byte model-visible JSONL; references/rubrics stay local. Original qualified bundle is reused, with hashes verified. Full base/adapter weight copies and tensor checks happen only on the ephemeral cloud server.
- Each attempt gets a closed immutable start snapshot and result snapshot under a fresh bucket prefix. Mounted destinations and manifests receive size/hash readback; these are not independent remote-durability evidence. Final artifacts use a separate `final` folder. An interrupted child gets separate accounting for all twelve scheduled IDs; raw journal/state remain unchanged and missing translations are never synthesized or retried.
- Live observation: creditUSD19.37, automatic recharge off, one A100-large rateUSD0.041667/minute, no active jobs. At60minutes, compute envelopeUSD2.50002; withUSD0.50 reserve the conservative rounded allowance is **USD3.01**. Refresh price, credit, idle jobs and fresh output prefix immediately before submission. This is a one-job allowance, not permission to consume the balance.

## Independent review

Lead `/root`; runtime critic `/root/plain_package_critic` (inherited settings); scientific reviewer `/root/component_astra_review` (user-requested gpt-6-astra/high). Independent bounded static reviews passed. Critic independently exercised SDK specification/volume serialization and five stopped-journal cases. Extracted primitives reuse existing reviewed code rather than importing training drivers. Reviewer fixes added mounted readback and explicit stopped-child accounting. No reviewer claims specialist linguistic certification, successful GPU execution or cross-job persistence.

Reviewed runner SHA256: `cafdaeed4e9f0544b886b74cb9e4f88e0530c1d7080bc1691cf7066bb22942d2`.
Reviewed extracted helper SHA256: `887b21031c27d427c838c7835585ca6388aab0fc8596b5d55df0334a79adff05`.

Local runnable check: `experiments/component-diagnostic-20261001/check_runtime.py`, using shared science Python and the existing project HF client dependencies. It checks real local tokenizer receipts, SDK serialization, twelve successes, output caps, cooperative timeouts, exception interruption, fixed denominator, immutable snapshots, overwrite refusal and full-panel time admission. CPU/mock evidence does not establish real BF16/GPU behavior; those checks run fail-closed on the server before experimental generation.

## Saved evidence and handoff

Submitted once at15:42:06UTC: [HF job6abe7f4e404719ba37618e63](https://huggingface.co/jobs/Mojionix/6abe7f4e404719ba37618e63), run`2fb3023097664133acb41e068fc6ee1e`. Provider confirmed **RUNNING** at15:45:35UTC. Logs confirm pinned dependency bootstrap completed and server-only base download started; the first49.8GB shard was reconstructed. No experimental output or quality result is claimed at this startup handoff. The exclusive claim, provider receipt and startup snapshot/log are saved. Active monitoring ends here at the user's standing request; inspect this exact job on return, never resubmit it.

`live-execution/receipt.json` and `job-spec.json` identify the exact prepared command and source hashes. `staging.json` records verified remote input readback and retained metadata/weight-size checks; no weights were downloaded locally. The initial transfer hit a local Xet cache permissions error; staging succeeded using a task-owned cache. Token creation/access expansion, billing changes, Drive/email and local model downloads were not needed.

Before the one API submission, create an exclusive `submission-claim.json`. Preserve it on an ambiguous provider response; inspect the provider rather than submitting again. Record the returned job ID, exact status and URL. Once startup is verified, end active monitoring as previously requested to preserve Codex tokens. Resume recovery and condition-blind assessment when the user returns. The comparison remains exploratory supplied-evidence use, with the frozen rubric; it cannot certify whole-passage translation quality.

No remote is configured in this working repository; commits are local and are not GitHub uploads.
