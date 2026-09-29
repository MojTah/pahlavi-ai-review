# Inference launcher readiness

29 September 2026. **PASS for bounded local preparation checks; cloud execution remains untested.** Independent integration review by `report_training_audit`; root remains the launcher owner. The reviewer authored the evaluator earlier, so this is not an independent review of that evaluator's own implementation. Only its regression test and this note were edited during this review. No scientific data or frozen prompt changed. No credentials, network, upload, job submission, pretrained-model download or training were used.

## Repaired integration error

The initial launcher wrote its full settings into the evaluator's `stage/settings.json`. The evaluator requires exactly seven fields; twelve extra transport/lifecycle fields caused `ValueError: Diagnostic settings/schema/generation contract differs`. That revision would have failed after server setup.

Root repaired `cloud_pilot/hf_learning_eval.py:114–117` to serialize the seven-field evaluator projection while preserving full lifecycle settings separately. The new regression in `cloud_pilot/test_learning_eval.py` prepares and decodes the actual packed command, executes only its data assignments and settings-write statements, and passes the resulting file to `learning_eval.validate_settings`. This now passes. The regression also confirms that passing the full launcher settings still fails. No outstanding local blocker was found within this bounded audit.

## Checks completed locally

- Ran `hf_learning_eval.prepare` with the frozen 28-prompt input and fixed local test run ID `0123456789abcdef0123456789abcdef`. Socket connection methods were patched to reject network access. No job API was invoked; installed SDK signature binding passed. The regression additionally blocks job submission with an autospecced mock.
- Decoded the compressed command, checked its SHA256 and compiled it. Only the bounded data/settings-write statements were executed for the repaired contract test. Largest argument: 93,524 bytes; aggregate arguments including NULs: 154,904 bytes. Both remain within the existing 100 KiB/1 MiB guards.
- Verified all eight embedded Python files byte-for-byte against current local sources and compiled each. The bootstrap prefix stops before `tiny-smoke`; no training smoke test is part of this proposed inference lifecycle.
- Validated exact 28-case ordering and frozen input hash. The input file is 12,784 bytes; no diagnostic reference file is included in the prepared input specification or embedded runner sources.
- Matched both saved manifest hashes and all four adapter config/weight entries against the recovered local manifests. Each weight entry is 489,840,816 bytes. This is saved provenance verification, not a current cloud inventory or local weight hash check.
- Traced child-process failure reaping and bounded evidence export. Native 60 minutes, internal 3,300 seconds and computation 3,000 seconds are preparation settings, not verified completion forecasts. Case caps of 90 seconds × 56 can exceed the available computation window; partial coverage remains possible and must be reported.

All eight local tests passed in 13.211 seconds, including 56 mock attempts, 28 exact pinned-tokenizer prefixes and the new serialized-settings boundary. After strengthening the job mock to preserve its real signature, that boundary test passed again in 0.695 seconds. Commands used the default `[USER_HOME]\.venvs\codex-science\Scripts\python.exe -B -X utf8 -m unittest cloud_pilot.test_learning_eval -v` and the single-test selector. No pretrained weights were loaded.

Frozen SHA256 identities after checks:

- Launcher: `f0e82667cf2d2138fb087497cf6a095a9fb7445f64f0f4549ddd7b07b3d804e2`.
- Evaluator, unchanged: `01b06a0db00d7e9870490c5bb85c9f368d3c855c8e2701f7f0a5a2abec77fa40`.
- Tests: `3057a391c36e4df3c505433e17fef09111b2af40ebb679e4595b0860dc9a787f`.

## Remaining boundary

Real Linux/A100 loading, both adapter tensor checks, prefills, timing, current cloud artifact availability, billing admission and remote persistence remain untested by this local audit. `completed_with_errors` retains all recorded attempts and is not translation success. No paid execution is admitted by this note.
