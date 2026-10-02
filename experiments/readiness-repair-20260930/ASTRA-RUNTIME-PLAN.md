# Independent Astra runtime and forward-plan review

30 September 2026. Reviewer: `/root/astra_runtime_plan_recheck`, independent from the lead and implementation agents. Read-only review of implementation, scientific packet and archived evidence; only this report was authored. No authentication, network request, model-weight access, paid job or training occurred.

**PASS for local preparation within the tested boundaries. No blocking finding remains in this review scope. This is not launch authorization or approval of an actual training contract.** Live funding, provider admission/deadline semantics, full GPU execution and remote persistence remain pending.

## Independently exercised evidence

- `python.exe -B -X utf8 -m unittest cloud_pilot.test_learning_eval cloud_pilot.test_hf_learning_eval -v`: all **18 tests passed in 37.941 seconds**, using the shared science interpreter and existing local dependency folders. Expected missing-CLI-argument stderr belongs to a passing boundary test.
- The actual `run_logged` subprocess kill exercised real evaluator control flow with a CPU stub: two recorded answers survive unchanged; the third interrupted attempt becomes one unknown-output record; 53 cells remain genuinely unattempted; the denominator stays 56. Reconciliation repeats without changing prediction bytes. This is stronger than an exception-only test, but does not exercise Linux signals or a hung GPU kernel.
- Other affected checks exercise committed partial/timeout-row preservation, rejected corrupt tails and inconsistent ledgers without mutation, parent export of original corrupt evidence, wrapper incomplete status, loading failure with zero attempts, full-budget admission, named adapter switching, canaries, and unchanged 56/512/90 generation limits. Parent export is mocked; remote durability is not established by these tests.
- `python.exe -B -X utf8 experiments/readiness-repair-20260930/prepare_runtime.py --check`: **PASS**. Exact frozen packet reconstruction, current embedded-helper bytes, decoded program compilation, source-only input shape and real installed SDK serialization succeed offline. I did not repeat the separate submission-reviewer's full training-gate audit.
- Independently read back every file in the actual isolated checkout recorded by `checkout-check.json`: **44 tracked files match both current working bytes and recorded hashes; 12 ignored local files match their recorded hashes**. Reviewed the checker's real `git -c core.autocrlf=true checkout-index` procedure and byte-preservation checks. This is a verified archived export, not a claim that private data/tokenizers are distributed by Git or that a fresh machine has installed dependencies.

## Deadline, cost and provenance assessment

The concrete specimen carries compute 6,600 seconds, internal 6,900 seconds and provider 120 minutes; cooperative child cutoff is compute minus 180 seconds, approximately 6,420 seconds from runner start. Both prefill canaries and loading precede the 5,100-second admission test (56 x 90 + 60). Thus approximately 1,320 seconds is the latest generation-eligibility point. **It is not a separate setup watchdog**: a hung setup/load can still consume the hard compute allocation before reconciliation/export. The legacy 3,000-second default cannot pass this full-cycle check and does not silently run a shortened panel.

The 60-second finalization component and cooperative token-level timeouts are reserves, not hard guarantees for arbitrary GPU or filesystem stalls. The later hard stop and reconciliation are still necessary. The plan appropriately retains provider deadline semantics and persistence verification as launch-time gates.

Archived `terminal.json` records 2,854.201 seconds; the final training progress row records 1,819.185124 seconds. Recomputed all 24 DEV elapsed fields: sum 238.678833638 seconds, median 8.078072636, maximum 32.534985677. The plan's rounded figures are consistent. The exact residual is approximately 796.337 seconds; its stated 796.321 uses its rounded lifecycle/training inputs. Neither residual isolates download/setup time or predicts this diagnostic's duration. These are different prompts and a different full lifecycle.

At the archived rate USD0.041667/minute, 120 minutes costs USD5.00004; adding the stated USD0.50 reserve yields USD5.50004. Arithmetic passes. The plan correctly identifies this as a proposed planning envelope, not a current rate, available balance, actual invoice or provider-enforced account cap. Current funds, all-in charges, idle jobs and authorization remain required before submission.

The largest command argument is 96,828 bytes (96,829 including NUL), below 100 KiB; aggregate arguments including NUL total 158,208 bytes. Local compilation and serialization pass. This does not establish provider acceptance.

## Scientific and forward-plan assessment

The plan keeps the corrected28 packet, both existing checkpoint identities, BF16 comparison, task-matched prompts, balanced first-arm schedule and fixed generation limits. It describes acquisition/retention on a purposive and partly dependent familiar-task panel; it does not mislabel this as unseen translation accuracy or a causal training-effect experiment. Grammar cues remain conditioned recall. The NF4-training versus BF16-evaluation caveat correctly limits a negative acquisition conclusion.

The ancient-language research and other-chat reassessment are incorporated as bounded hypotheses. Aeneas does not establish Pahlavi translation quality; ParsiPy motivates representation-compatible baselines; PahGen's direction and constructed/historical distinctions preclude automatic gold-data adoption. Prior paper checks are documented in the earlier Astra report; I did not perform another literature/network review here.

Existing failed assisted/prompt experiments remain part of the evidence. The plan prohibits renaming and repeating them without a distinct changed hypothesis, preserves historical merit and module-specific interpretation, keeps correlated AI ratings provisional, requires expert calibration and lineage/exposure-qualified confirmation, and does not automatically retrain after any outcome. Future training still requires substantive diagnostic interpretation, a frozen actual contract, separate Astra review and human authorization. These limits match the reviewed preparation's evidential strength.

## Reviewed identities and remaining gate

| Artifact | SHA-256 |
|---|---|
| `PLAN.md` | `b084b474de57c28a7288749322484dcf4ba3c9fa13e9242f8ccc6258c209b6d9` |
| `prepare_runtime.py` | `cb4cca4b15b18c0b250c0e3430e42eedbaa130613e08722fbbec7c7a187ab3a6` |
| `job-spec.json` | `78cbd278b45e0a5db76a8faf949dc49e30db171adc772f32523e967713b5a521` |
| `job-receipt.json` | `036e4107429dc41cd2e2d4559fed940354048016a02596e4fc9d45bdae716ba7` |
| `runtime-check.json` | `474b947a0325dcd7b2f6161cc2099f0d234a71b1f859899d7bba50935448c1dc` |
| decoded runnable program | `7e9fd8bfb35e590c86ddfac95b608a36f829dcb70a8a4bd13039c86a3c63c20a` |
| `cloud_pilot/hf_learning_eval.py` | `e0681f1f56b1a5f3350cb1f4f4934923f9e327bdc5f74dc3221929f5cd51f5ff` |
| `cloud_pilot/learning_eval.py` | `8f9ae586b562004eaa21ac26e22f190d4c82e187377c88307fbf2035ea12db12` |

Proceed only to the plan's separately authorized live launch gates. Generate a fresh run identity through the reviewed preparer, compare exact semantic payload and hashes, verify source-only staging and adapter manifests, and preserve a single submission receipt. No existing result or this local PASS authorizes missing-cell retries, another training run, a monitor or model-weight download.

Final integration check: the only PLAN change after the initial review explicitly distinguishes the 1,320-second generation-eligibility check from a setup watchdog and states that a hung load can reach the hard compute cutoff. Reversing that exact clarification reproduces the previously reviewed PLAN hash. The clarification accurately reflects this review; the table now binds the final PLAN bytes. Runtime conclusions and pending live gates are unchanged; tests were not repeated for this prose-only delta.
