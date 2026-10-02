# Independent Astra exact-contract review

Verdict: **APPROVE the exact guarded pilot**, subject to the existing human-authorization and action-time launch gates. This is not model promotion or a promise of complete evaluation.

Reviewer: `/root/dose_design_critic`; model: `gpt-6-astra`. Implementers: root and scoped Sol6.1 agents; reviewer did not edit implementation/data. Reviewed on 30 September 2026.

- Contract SHA-256: `5a4e482ec0cb01b0955d5b23ff9aca05d5c7a51194deb78995ae50f19c176cb7`.
- Job SHA-256: `57479ba5d4dea0f7d9bfdc81c936de9d34120fb3092a4adcdab324ee15be7ba5`.
- Acquisition record SHA-256: `4b0dce6724dcf99b2497d2a31ba85c6f6f437d51e59642ecc6d85f5568f73502`.
- Decision record SHA-256: `45d952e6cedbbb22437995e630bac95c711d82da1bc8900e54d8ef7f1521926b`.
- Validation record SHA-256: `7dae64aff68be08eb1a70c191b4e8dcfe6d1afab6b33481f229c19c5dc362be4`.

## Evidence and resolved findings

Independently rehashed all 51 unique frozen artifacts and compared each with its live source. Validation source hashes and recorded test-log hashes match. Fresh-process reconstruction of the saved proposal now exactly matches both saved specification and receipt, including the contract job. All embedded child sources match their reviewed files. The earlier command-order defect was reproduced independently and approval withheld; recursive canonical sorting now fixes it, and the new order/JSON-roundtrip regression test independently passes.

Earlier independently executed checks comprised all 16 core/runtime/package tests (7 real CPU training checks, 6 runtime checks, 3 package checks), both execution tests, and an extra real tiny-model run using accumulation16 over four identical16-row cycles. That extra run verified64 actual forwards, snapshots at16/32/64 slots, continuous optimizer/scheduler and final stream identity. The added canonical-order test brings the maintained suite to19 tests; root's final19-test evidence was hash-verified. Tests establish CPU behavior and offline packaging, not full-model GPU behavior. Confirmation selection was rebuilt in memory and all recorded source hashes checked, with Windows newline normalization when comparing generated text.

Other identified defects were repaired: list/dict prompt-identity mismatch (now covered by actual57-prompt tokenizer replay), missing parent reconciliation after killed child, and an unbound-model cleanup exception during baseline-to-training reload. Real PEFT four-name unload/reload and a real killed-child ledger check passed. Export tests preserve all four adapter-only snapshots. Historical adapter size implies approximately1.96GB for four snapshots, within the3GiB export ceiling.

## Scientific and execution scope

Start from retained step280; repeat the exact pre-existing corrected1536 rows four times, with one fresh optimizer and one384-update linear schedule. Save96/192/384 without optimization resets. This measures an acquisition trajectory under the declared recipe; it does not isolate exposure from learning-rate evolution or permit causal comparison to historical corrected96.

The jointly reviewed NF4 diagnostic did not rescue complete lexical acquisition (0/6 in both reviewers). The LD-021 negation regression and targeted event errors were inspected, retained and qualified; no accepted-count module checkpoint ordering reverses. These results justify a bounded acquisition test, not deployment. Training selection is unchanged and independent of those revealed failures. Five confirmation cases are pilot-heldout under documented checks, not proven unseen in pretraining/step280; they do not validate broad translation.

The frozen98 new first attempts retain full24-case fixed-merit baseline/final, all28 final diagnostic cases,12 intermediate lexical outputs and10 confirmation outputs. Original merit prompts,4096-token/1200-second caps, rubrics and promotion screen remain unchanged. Diagnostic/confirmation caps remain512 tokens/90seconds. Every baseline-accepted whole-passage case must remain accepted, and the same confirmation case must newly pass both reviewers. Intermediate quality cannot select the endpoint or trigger more optimization.

The360-minute provider limit,20400-second compute cutoff,21000-second internal deadline and600-second export reserve are consistent. Baseline must pass within2400seconds;20/96/192-step forecasts retain6600seconds evaluation plus300seconds reload. Per-attempt admission preserves the full task-specific cap plus finalization. This is empirical admission with a real risk of an inconclusive incomplete panel; it does not pretend that summed20-minute caps fit. At the observed rate the compute ceiling isUSD15.000120, withUSD0.50 planning reserve, and current checks refuse allowances aboveUSD15.51. Current funds/rate/account/private bucket/idle jobs must be rechecked at launch.

Staging refuses conflicting existing remote inputs, verifies readbacks, inspects reference metadata without downloading pretrained weights locally and delegates server weight rehashing to the guarded job. Submission uses the existing exclusive claim and no automatic retry. Child termination is reaped before ledger reconciliation/export. Partial outputs remain evidence; manifests alone do not establish remote persistence.

## Remaining mandatory runtime checks and limits

No network/cloud call, pretrained-weight download,31B execution or NF4 GPU experiment was performed in this independent review. The actual server must pass pinned environment/base/tokenizer/adapter checks, NF4/dtype checks, longest-prompt prefill checks, training masked-loss/gradient canary and measured time admission. Later authenticated output readback must verify persisted hashes and complete first-attempt coverage before any quality conclusion. Missing/capped/timed-out outputs retain their scheduled denominators and make the quality decision inconclusive.

The root must record the actual user authorization accurately, complete the existing admission receipt, recheck current external conditions, stage/read-verify exact evidence, submit once, verify startup and stop active assistant work during the long job. This review authorizes none of those external actions by itself and grants no retry, recharge, promotion or full-pool follow-up.
