# Diagnostic deadline and first-attempt accounting repair

30 September 2026. Local implementation evidence; independent Astra review remains required. No cloud access, authentication, model download, training, commit or paid launch occurred.

## Implemented boundary

The evaluator's cooperative cutoff now derives from the actual computation deadline minus the existing 180-second reserve. The child remains subject to the later computation hard stop. The parent reaps the child through the unchanged shared `run_logged`, then reconciles durable evidence before export. The diagnostic parent and evaluator wrapper both retain incomplete status when finalization is interrupted.

The complete 56-cell schedule is written before model loading. Each first-attempt ledger removes its active cell from genuinely unattempted cells before generation. After both prefill canaries, the evaluator requires 56 × 90 + 60 = 5,100 seconds remaining before its first generation. Insufficient capacity produces an incomplete zero-attempt ledger without shortening or retrying the panel.

`prepare(..., corrected_binding=..., timing_budget=...)` accepts only the explicit reviewed three-key budget: computation 6,600 seconds, internal 6,900 seconds, provider 120 minutes. Existing defaults remain 3,000 / 3,300 / 60 minutes, with the unchanged 180-second reserve and 60-second maximum persistence wait. The old default cannot satisfy the new full-cycle admission guard; it fails closed. The scientific 56 first attempts, 512 tokens and 90-second per-attempt limit remain unchanged.

## Durable recovery

Reconciliation validates the fixed schedule, committed prediction identity/order/status, attempt counts and prior committed counters. A durable active attempt with no complete output row receives one `interrupted` record with null text/token/output hashes and explicit unknown-output evidence. It is never regenerated. A complete prediction written before its ledger update is retained with its original status, including real partial/timeout output. Recovery can be repeated without appending another interrupted row.

An inconsistent ledger, malformed complete JSON or partial JSONL tail is rejected without modifying the original prediction or ledger bytes. The parent records a separate reconciliation error and still exports the original evidence and driver log. This is failure evidence, never a full-panel result. Existing non-loading evaluation directories and predictions cannot be overwritten through `generate_pairs`.

## Local checks

Interpreter: `[USER_HOME]\.venvs\codex-science\Scripts\python.exe`. Existing local dependency folders supply the fake-model/tokenizer tests; no dependency was installed.

Command: `python.exe -B -X utf8 -m unittest cloud_pilot.test_learning_eval cloud_pilot.test_hf_learning_eval`.

The evaluator suite checks 56 first attempts, named adapter switches, separate caches, output caps, ordinary errors, canary failures, case/global timeout distinction, source/template boundaries and insufficient-budget zero-attempt admission. Recovery checks cover unknown output, committed real partial-output preservation, repeated finalization, zero-attempt loading failure, inconsistent counters/schedule and partial tails, computation/child cutoff ordering, explicit serialized budget override, and the parent's pre-export success/error reconciliation paths.

The actual subprocess test uses unchanged `run_logged`, actual `generate_pairs` and a CPU `StubModel`: two generations complete, the third sleeps 40 seconds, and the parent kills/reaps it at 20 seconds. The two original rows survive byte-for-byte. Recovery yields attempted 3, recorded 3, successful 2, unattempted 53, denominator 56, with the third row interrupted/unknown. A second recovery leaves prediction bytes unchanged.

Final result: all 18 tests passed in 33.819 seconds. An earlier combined run exposed a test-only floating-point comparison (`6600.000000000001` versus `6600`); its boundary assertion now allows one microsecond of rounding. Production timing was unchanged. `git diff --check` passed for the modified tracked evaluator/launcher files. The expected CLI-missing-arguments stderr belongs to the passing argument-boundary test.

## Remaining limits

These are Windows CPU fake-model, real pinned-tokenizer and mocked parent-export checks. Linux SIGALRM delivery, full 31B BF16 load/inference, real GPU-kernel interruption/latency, provider timeout semantics, remote persistence/recovery and current funds/rates were not exercised. The stopping criterion is cooperative between generation steps; the independent parent kill remains necessary. Local results do not authorize launch or establish acquisition quality.
