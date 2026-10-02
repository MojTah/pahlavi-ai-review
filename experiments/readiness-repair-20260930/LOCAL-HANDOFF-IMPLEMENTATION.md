# Local execution handoff implementation

2026-09-30. Local preparation only: **NOT_SUBMITTED / NOT_AUTHORIZED**. No provider client, authentication, credential access, network, upload, model load or paid execution.

`prepare_execution.py` first verifies the independently reviewed runtime-check hash, every bound source hash and saved specimen hashes, then replays `prepare_runtime.build()` against the exact saved bytes. It calls the existing diagnostic preparer with a fresh UUID, corrected binding and unchanged reviewed budget. The fresh decoded program must equal the reviewed program after replacing only its single run-ID literal. All specification and receipt fields must match except the run ID, output prefix, trial label and independently recomputed command hashes/lengths. The installed SDK's pure boundary is exercised before writing.

The helper exclusively creates a new destination and writes the specification, receipt, exact prompt-only input and handoff inventory using exclusive file creation. Existing folders are refused; it never overwrites a proposal. A failed partial filesystem write leaves the folder in place, requiring operator inspection rather than automatic retry/cleanup. This is application-level refusal to overwrite, not an OS write-protection guarantee.

The two-item proposed transfer inventory binds the 15,474-byte prompt-only input and existing 6,372,448-byte qualified bundle by their reviewed SHA-256 identities. The bundle is checked locally and retained at its existing path; it is not copied. References, scientific metadata, job metadata and local model/adapter weights are explicitly excluded from transfer. Nothing is uploaded and remote staging remains unverified.

```powershell
& '[USER_HOME]\.venvs\codex-science\Scripts\python.exe' -B -X utf8 experiments/readiness-repair-20260930/test_prepare_execution.py -q
& '[USER_HOME]\.venvs\codex-science\Scripts\python.exe' -B -X utf8 experiments/readiness-repair-20260930/prepare_execution.py --out experiments/readiness-repair-20260930/execution-proposal
```

The test command passed **3 tests in 17.287 seconds**. Checks exercise real SDK serialization, blocked API construction/network, equal frozen-packet bytes, refusal to reuse an existing folder without mutation, rejection of unexpected specification changes before writing and missing/changed reviewed-byte rejection. A default CLI smoke also produced one local ignored handoff with both explicit unsubmitted/unauthorized statuses. No `--launch` option exists.

Independent Astra verification and the lead's exact proposal review remain separate from this implementation evidence. Live funds/rate/active-job checks, exact transfer/readback, adapter/environment checks and one paid inference submission still require the user's separate action-specific approval. This implementation creates no human-approval record.
