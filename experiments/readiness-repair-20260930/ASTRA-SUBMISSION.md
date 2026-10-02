# Independent Astra submission repair review

2026-09-30. Reviewer: `/root/astra_submission_recheck`. Read-only implementation review against `e7b17a9`; report is the only authored file. Prior finding: `experiments/astra-preparation-review-20260930/GATE-REVIEW.md`, GATE-001. Writer handoff: `SUBMISSION-REPAIR.md` in this directory.

**PASS for the local submission-boundary repair. GATE-001 is resolved. No new actionable defect found in the reviewed diff. This is not a scientific contract approval or authorization for a provider job.**

## Evidence

Reviewed `cloud_pilot/training_admission.py` and `cloud_pilot/test_training_admission.py`, including the unchanged admission/claim code surrounding the patch. Inspected the installed `huggingface_hub` 1.23.0 `Volume`, `_create_job_spec`, and `HfApi.run_job` source; no API instance was constructed.

The saved camelCase volume dictionary is reconstructed as a native Volume and checked for exact dictionary preservation. Invalid or silently discarded settings are rejected. The real installed run_job signature is bound and defaults applied; its pure serializer and strict JSON encoding run before exclusive claim creation. The original spec/provenance comparisons and evidence bindings remain in place. Copies protect the caller's objects. The single operator-supplied API call follows the exclusive claim and final evidence validation. Unknown provider outcomes retain their claim.

Focused reproducible command (PowerShell, repository root):

```powershell
$env:PYTHONPATH = 'resources/local/hf-client-venv/Lib/site-packages'
& '[USER_HOME]\.venvs\codex-science\Scripts\python.exe' -B -X utf8 -m unittest cloud_pilot.test_training_admission cloud_pilot.test_hf_train cloud_pilot.test_hf_continue cloud_pilot.test_hf_contextual -q
```

**37 tests passed, 12.861 seconds.** This includes real SDK native/saved-JSON equivalence, malformed inputs without a claim or API call, duplicate submission refusal, and retained claims after a simulated unknown outcome. `git diff --check -- cloud_pilot/training_admission.py cloud_pilot/test_training_admission.py` passed.

Independent extension beyond the writer tests: all five actual builders (`hf_train`, `hf_continue`, `hf_contextual`, `hf_mixed`, `hf_nllb`) were admitted/submitted to an offline boundary with separate synthetic fixtures for native and saved JSON representations. For all ten cases, a wrapper around the installed pure serializer asserted no claim existed when prevalidation ran; the offline boundary asserted exactly one claim already existed and matched submitted spec/command hashes and the original job hash. Each pair produced equal actual SDK payloads, and canonical caller spec/provenance bytes were unchanged. No intended training command was executed by this extension.

SHA-256 of reviewed files:

- `cloud_pilot/training_admission.py`: `2161901434fc2afbf9b5107d7104b4bd758b1130c817dcac0d82ecfbb1edaa1d`
- `cloud_pilot/test_training_admission.py`: `342cbf127d223a29514cb690ff93118cf657cc55596ba2ab870934f9c329726d`

## Limits and forward gate

This validates the installed local SDK representation/serialization boundary, not complete provider-side semantic validation. The implementation depends on the installed private SDK serializer and should be rechecked when that SDK changes. No credentials, HfApi instance, authentication, network, download, cloud job, GPU runtime, model load, or training was exercised. All approvals/results in test evidence were synthetic fixtures. Actual acquisition completion, scientific justification, exact contract review, reviewer/human authenticity, remote evidence staging/readback, provider acceptance and recovery remain unverified. Existing documented manual trust and local-lock limitations remain unchanged.

The repair can advance as a working local checkpoint. A real submission still requires completed acquisition evidence, a reasoned scientific decision, exact contract validation and independent Astra review, staging/readback, and explicit authorization for the exact human-approved job. This report supplies none of those live approvals.
