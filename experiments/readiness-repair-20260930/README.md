# Readiness repair and next-run plan

**Completion checkpoint:** the [recovered diagnostic and prior-training health audit](live-execution/OUTCOME.md) verify56/56 successful first outputs and genuine earlier96-step adapter training. Independent Astra integrity checks pass. The job completed in14m37s, with approximatelyUSD0.63 compute; no new training or model-weight download. The launch/preparation statuses below are historical.

**Live checkpoint,30 September:** the user-authorized [single inference job](live-execution/README.md) is RUNNING with bootstrap complete, observed15:26:52 UTC. Exact proposal and scientific settings are unchanged. The current120-minute/USD5.51 envelope is covered by observedUSD27.62 credit; no recharge, retraining or local model download. Active monitoring stops after startup as requested. The historical preparation statuses below are superseded only by the live execution record; no quality result is available yet.

**Implemented local handoff, version0.11.3:** [Execution proposal and independent Astra review](EXECUTION-HANDOFF.md) add a fresh run ID, exact-equivalence checks and verified two-file transfer inventory. The proposal is not submitted or authorized; live credential/account/transfer/paid-job approval remains separate. The version0.11.2 runtime/specimen below stays unchanged.

30 September2026. Version0.11.2. **Local preparation passed independent Astra review; no paid execution, model/data change or training authorization.** [Forward plan](PLAN.md) is the current route from diagnosis to one evidence-led intervention. Keep step280 as the reference and the app Goal paused.

This checkpoint repairs the three concrete gaps from the [independent review](../astra-preparation-review-20260930/REPORT.md), then versions the larger runtime envelope without editing the frozen scientific packet or old job receipts. Sol6.1 implemented disjoint diagnostic and submission scopes; root integrates; Astra independently reviews. The report history remains intact.

| Evidence | Scope |
|---|---|
| [Diagnostic repair](DIAGNOSTIC-REPAIR.md) | Deadline ordering, first-attempt ledger, actual child termination, idempotent reconciliation, corrupt-tail preservation and capacity admission |
| [Submission repair](SUBMISSION-REPAIR.md) | Native/saved-JSON SDK equivalence before claiming; unknown-result claims retained |
| [Astra submission review](ASTRA-SUBMISSION.md) | Independent37-test run and all five actual builder boundaries; local PASS |
| [Astra runtime/plan review](ASTRA-RUNTIME-PLAN.md) | Independent18-test run, exact runtime reconstruction, checkout readback and timing arithmetic; local PASS |
| [Runtime reconstruction](runtime-check.json) | Fixed packet replay, current embedded helpers, real SDK serialization and command-size guard; no API call |
| [Actual checkout comparison](checkout-check.json) |44 tracked byte-bound files exported with `core.autocrlf=true`, all identical;12 ignored local files separately hash-verified |
| [Runtime specimen](job-receipt.json) |56 attempts, BF16,512 tokens/90seconds; explicit6,600s compute/6,900s internal/120-minute provider envelope; prepared, not submitted |

The original inputs, references, binding and census reconstruct exactly. The corrected packet integration suite passed all four tests; only its fake execution deadline changed to satisfy the new full-cycle admission rule. The existing bundle's runtime and locked dependency bytes match the local bootstrap sources. New preparation uses canonical SDK camelCase volumes; historical `dataclasses.asdict` JSON receipts remain historical and must not be submitted directly.

The Git check is an actual isolated export from the staged snapshot, not just a text search for attributes. Private data/tokenizer files remain ignored; a repository-only checkout is not a standalone full-corpus install. No raw data normalization, changed hash pin, or frozen benchmark modification was used to make checks pass.

The lead accepts the repaired local checkpoint with the reviewers' stated limits. [AutoCode review record](AUTOCODE-GATE.md) records the distinct implementer/critic identities. The three prior implementation findings are closed for these verified local paths; Linux/GPU/provider behavior and the scientific outcome remain unexercised.

## Reproduce local checks

Use the shared Python interpreter and the existing dependency paths; do not install or download models. From the project root in PowerShell:

```powershell
$env:PYTHONPATH = "$PWD\resources\local\train-fit-deps;$PWD\resources\local\hf-client-venv\Lib\site-packages"
& '[USER_HOME]\.venvs\codex-science\Scripts\python.exe' -B -X utf8 -m unittest cloud_pilot.test_learning_eval cloud_pilot.test_hf_learning_eval -q
& '[USER_HOME]\.venvs\codex-science\Scripts\python.exe' -B -X utf8 -m unittest cloud_pilot.test_training_admission cloud_pilot.test_hf_train cloud_pilot.test_hf_continue cloud_pilot.test_hf_contextual -q
& '[USER_HOME]\.venvs\codex-science\Scripts\python.exe' -B -X utf8 experiments/corrected-learning-diagnosis-20260930/test_prepare.py -q
& '[USER_HOME]\.venvs\codex-science\Scripts\python.exe' -B -X utf8 experiments/readiness-repair-20260930/prepare_runtime.py --check
& '[USER_HOME]\.venvs\codex-science\Scripts\python.exe' -B -X utf8 experiments/readiness-repair-20260930/check_checkout.py
```

The last check needs the reviewed files in the Git index and writes a fresh ignored export plus its receipt. It does not replace or delete the working tree. Counts from overlapping suites/reviewer reruns are not independent experiments and must not be summed as such.

## Paid gates remain separate

The proposed inference envelope isUSD5.50004 including aUSD0.50 reserve at the **historical** rate; obtain a fresh all-in price and funding/idle-job check at launch. Exact authorized submission, remote input readback, full31B GPU behavior and remote result persistence remain unverified. The5,100-second generation reserve is checked after loading/canaries: it is not a separate setup watchdog, and a hung load can last until the hard compute cutoff. Generation time limits are cooperative; provider timeout is the outer safety bound.

After the inference outcome, use module-specific blind review to decide whether prompt/precision, acquisition, retention or composition needs investigation. The plan incorporates the two other chats and the Aeneas/ParsiPy/PahGen lessons without claiming their results transfer directly. Do not begin another training run from this repair's approval; it needs its own completed acquisition evidence, substantive decision, exact contract, Astra review and human authorization.
