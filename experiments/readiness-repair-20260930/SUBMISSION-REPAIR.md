# Submission boundary repair

2026-09-30. Scope: GATE-001 in the independent preparation review. This is local implementation evidence, not an actual scientific approval, human job authorization, or permission to start a paid run.

`submit` now admits the unchanged frozen draft, reconstructs SDK `Volume` objects from the saved CLI JSON representation, and exercises the installed SDK's pure `_create_job_spec` serializer before creating its exclusive submission claim. It also binds the installed `HfApi.run_job` signature without creating an API instance, applies its defaults, and checks the resulting payload with strict JSON serialization. Native SDK volumes remain supported. Input specifications and preparation/provenance bytes are unchanged.

Volume reconstruction accepts only the exact emitted camelCase representation: required `type`, `source`, `mountPath`, and optional `revision`, `readOnly`, `path`. It rejects unknown fields, unsupported representations/types, empty or wrongly typed strings, nonabsolute mount paths, and nonboolean `readOnly`. Reconstruction must preserve the complete volume dictionary. This avoids the SDK constructor's silent dropping of unknown fields. The scientific artifact/job bindings and runtime guard remain intact.

Malformed local inputs leave no submission claim and make no API call. An exclusive claim still precedes the single operator-supplied API call; an API timeout or ambiguous outcome retains the claim and refuses a retry. Provider inspection and manual recovery remain required after an unknown outcome.

## Verification

- Shared runtime: `[USER_HOME]\.venvs\codex-science\Scripts\python.exe -B`; existing SDK imported from `resources/local/hf-client-venv/Lib/site-packages`.
- `-m unittest cloud_pilot.test_training_admission -q`: **10 passed**.
- `-m unittest cloud_pilot.test_training_admission cloud_pilot.test_hf_train cloud_pilot.test_hf_continue cloud_pilot.test_hf_contextual -q`: **37 passed**.
- `git diff --check` for the two modified Python files: passed.
- Added tests run the actual installed pure SDK serializer for equivalent real-builder native and saved-JSON specifications, assert equal payloads and semantic submitted specifications, and assert unchanged original inputs/provenance. Malformed volume settings, timeout, image representation and unsupported SDK arguments fail before the claim. Existing tests still exercise duplicate submission refusal and retained claims after an unknown provider result.

All approval records in these checks are explicit synthetic test fixtures. No credentials, HfApi instance, authentication, network/provider call, model load, dependency installation, paid inference or training was used. The tests establish local representation and serialization behavior; actual cloud staging, provider acceptance, GPU execution, reviewer identity and completed acquisition remain unverified.

## Forward handoff

Independent Astra verification should repeat the serializer-boundary regression and check retained-claim behavior. Saved CLI JSON drafts can then follow the documented admission/submission boundary after the separate scientific/acquisition, exact-contract review, evidence staging/readback and exact human authorization gates are satisfied. This repair does not satisfy or waive those gates.
