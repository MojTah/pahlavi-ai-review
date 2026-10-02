# Local execution handoff

30 September2026. User request: start implementation of the reviewed forward plan. Scope for this checkpoint is local implementation and a reviewable execution proposal. **No credential use, live account check, upload, paid job or training has been performed.** Those are a separate approval step; prior pilot permissions do not become an approval record for this proposal.

Classic + Critic: `/root/sol_submission_repair` implements the bounded local preparer; root integrates the concrete proposal and documentation; independent Astra reviews before handoff. Existing inference runtime, scientific packet and historical receipts remain unchanged. Reuse the reviewed builder and installed SDK serializer; add no launcher, new service, scheduler, dependency or billing logic.

The preparer must reconstruct the reviewed specimen, generate a fresh run identity, and permit only its necessary output-path/label/encoded-command changes. All prompts, adapters, generation settings, runtime helpers, mounts, resource limits and other settings retain the reviewed identities. Changed scientific/runtime settings require review, not an override flag. An existing output directory is refused; local preparation does not prove that the cloud prefix is unused.

The proposed transfer inventory is exactly:

| Existing local file | Bytes | Destination under the existing input bucket path |
|---|---:|---|
| `experiments/corrected-learning-diagnosis-20260930/inputs.jsonl` |15,474 | `learning-diagnosis-02c5ecc82e187847.jsonl` |
| `resources/local/cloud-pilot-qualified-20260927.zip` |6,372,448 | `cloud-pilot-qualified-20260927.zip` |

Both SHA-256 identities were verified locally against the reviewed receipt. The first file contains only case IDs and prompts. Reference answers and reviewer/exposure metadata stay local. The existing bundle provides the already reviewed runtime/tokenizer/training provenance; it is not supplied as retrieval context. Existing checkpoint weights remain on the server, and this handoff downloads no model weights.

The actual job specification is for one A100-large inference-only comparison,56 first attempts,120-minute outer timeout. No optimizer runs. The planning allowance is up toUSD5.51 from existing credit, conditional on a fresh all-in price and sufficient balance; this is not a verified current bill or a provider-enforced account cap.

After separate approval, the sole execution owner must verify live credit/rate and no active/conflicting job; verify the exact input and adapter manifests, empty fresh output prefix and remote readback; submit once and save its receipt. An ambiguous provider response requires inspection, never an automatic second submission. Server loading, canaries, first-attempt accounting and export use the already reviewed runtime. Stop active assistant work after confirmed startup as requested; inspect the exact job on the user's next check. No unrequested monitor or automatic retraining.

The local proposal and passing tests cannot replace current account evidence, real GPU behavior, persisted-result verification or the actual acquisition result. Future training still requires the separate diagnostic interpretation and exact-contract Astra/human gates in [PLAN.md](PLAN.md).

## Implemented proposal

Version0.11.3 adds the offline handoff only. [Implementation evidence](LOCAL-HANDOFF-IMPLEMENTATION.md), [preparer](prepare_execution.py) and [three regression tests](test_prepare_execution.py) cover exact reconstruction, identity-only changes, installed SDK serialization, missing/changed reviewed files and refusal to overwrite a proposal. The tests block network connections and API-client construction. The inference runtime and prior reviewed specimen are unchanged.

Root ran the actual CLI and prepared run `7352dda33542431abb025b1443087aed` in [execution-proposal](execution-proposal/handoff.json). Its [job specification](execution-proposal/job-spec.json), [receipt](execution-proposal/job-receipt.json) and source-only input were generated successfully. The proposal is explicitly `NOT_SUBMITTED / NOT_AUTHORIZED`; it creates no human approval record. Preserve this folder. Re-running preparation against it correctly refuses.

[Independent Astra review](ASTRA-EXECUTION-HANDOFF.md): PASS for the local handoff. Three tests passed independently in18.094seconds; Astra checked the exact four proposal files, both transfer payloads, SDK serialization and identity-only equivalence while API construction/network were blocked. The prompt inventory path is repository-root-relative; resolve it from this project root at any later authorized staging. The lead accepts this local checkpoint with the stated live-boundary limits.

Lead agent/request id: /root
Critic agent/request id: /root/astra_runtime_plan_recheck
Critic model and reasoning effort: gpt-6-astra; inherited reasoning effort, no override
Independent from lead: yes
Evidence reviewed: prepare_execution.py, its tests, unchanged reviewed specimen, actual execution-proposal and the two transfer payloads
Verification evidence: Independent3-test run, exact actual-proposal reconstruction/SDK checks and all generated/transfer file hashes; root actual CLI success; no cloud action
Critic verdict: pass

AutoCode validation result: pass; canonical Critic validator executed locally on30 September2026. This gate accepts local implementation only.

```powershell
& '[USER_HOME]\.venvs\codex-science\Scripts\python.exe' -B -X utf8 experiments/readiness-repair-20260930/test_prepare_execution.py -q
```

The narrow pending approval is use of the existing Hugging Face credential cache for live readiness checks, the exact two-file transfer/readback above, and one inference-only submission of this proposal within120minutes andUSD5.51 from available existing credit. Higher prices, insufficient credit, conflicting jobs or changed identities stop admission. No recharge, training, automatic retry or local weight download is included.
