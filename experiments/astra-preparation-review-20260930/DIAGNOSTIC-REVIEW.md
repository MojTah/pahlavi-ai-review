# Independent corrected diagnostic preparation review

Reviewed commit `e4fd2bdc71b983f395b1a8459044159f1f527a75` on 2026-09-30. Scope: corrected packet, serialized launcher, paired evaluator, old packet/rubrics and recovered corrected training provenance. RESULT: **PARTIAL — scientifically suitable for the stated bounded descriptive question; execution preparation has an additional reproducible failure-accounting defect. No launch or training approval.**

No cloud/API/authentication, model download or training was performed. Frozen inputs/code were not changed. Scratch results are under `resources/local/astra-diagnostic-review/`. The lead separately reviews checkout byte preservation; that finding is not duplicated here.

## Ranked finding

### P2 — The outer computation deadline kills the evaluator before its own deadline and leaves the active attempt classified as unattempted

Locations: `cloud_pilot/hf_learning_eval.py:74-81,86-91,174-175`; `cloud_pilot/hf_contextual.py:113-117`; `cloud_pilot/learning_eval.py:124-125,153-175`.

`execute_evaluation` starts a 3,000-second SIGALRM but derives the child deadline and `run_logged` timeout from the 3,300-second internal deadline minus 180 seconds. Thus the child's cooperative cutoff is approximately start+3,120 seconds, **120 seconds after the outer hard stop**. An alarm raised while waiting for the child reaches `run_logged`'s exception handler, which calls `child.kill()` immediately. The evaluator cannot execute its error-recording/finalization handlers after that kill.

Independent local reproduction used the actual `run_logged` and actual `generate_pairs`, with the repository's CPU `StubModel`, two successful generations, then a 40-second sleep on the third generation and a 20-second parent timeout. Result:

```json
{"status":"running","attempted":3,"recorded":2,"active":"LD-002:candidate","unattempted_count":54,"active_marked_unattempted":true}
```

Evidence: `resources/local/astra-diagnostic-review/hard-stop-40ecb24185104750865e00c5cb0fd136/result/run.json`, adjacent `predictions.jsonl` and `driver.log`. The two prior prediction rows survive. The schedule still allows reconstruction of the full 56 denominator; **this is not loss of prior results or disappearance of the denominator**. However the third attempt has no failure row, the ledger remains `running`, and an already attempted cell remains in `unattempted_output_ids`. Consumers must not equate that stale field with genuinely unattempted cells or rerun the active cell as a fresh first attempt.

Runnable reproduction from the repository root (about 20 seconds, writes only a fresh ignored scratch folder):

```powershell
& '[USER_HOME]\.venvs\codex-science\Scripts\python.exe' -B -X utf8 resources/local/astra-diagnostic-review/reproduce_hard_stop.py
```

The corrected test at `test_prepare.py:91-114` injects a catchable `RuntimeError` inside generation; it verifies the cooperative failure path only. It does not exercise a child process or parent termination. Its passing result therefore does not establish failure accounting at the actual compute ceiling. The README's explicit lack of full-cycle recovery evidence is accurate, but does not repair this defect.

Smallest repair direction for the implementation owner: derive the evaluator's cooperative cutoff from the actual compute cutoff with a finalization margin, retain a later hard stop, and reconcile any remaining active cell into an explicit interrupted/unknown-output record after a forced kill. Initialize the complete schedule before model loading if uniform zero-attempt failure ledgers are required. Test the actual parent-child stop path. This review makes no such edits.

## Already documented timing/readiness limitation — separate from the defect

`README.md:47` explicitly states that 56 times 90 seconds is 5,040 seconds before loading/canaries, exceeding the inherited 3,000-second compute ceiling. This is **not a newly discovered omission**. It means worst-case completion is not admitted, not that every real run must exceed the bound. Representative full-cycle timing is still needed. The 90-second stopping criterion is cooperative between model-generation steps, not a preemptive GPU-kernel interrupt.

The packet contains fixed flavor and timeout limits, but no current dollar balance, current price or externally verified spending/readiness control. The README correctly withholds launch admission. Serialization, local mocks and an existing successful training run cannot replace the missing operational evidence for this specific inference lifecycle.

## Scientific and provenance checks that passed

- **The task is now actually tied to corrected96.** `prepare.py:43-74` verifies corrected projection/pool/train/audit/parent-map byte hashes, the recovered manifest, training status of 96 steps and 1,536 consumed slots, exact consumed-ID order and the canonical consumed-stream hash. The training implementation records consumed rows through its collator and only emits completed `ordered_ids` after order/update checks (`cloud_pilot/mixed_train.py:81-85,149-159`). This is stronger than merely testing membership in a proposed schedule.
- **Exposure is classified correctly.** All 12 auxiliary probes were consumed by corrected96. Overall 24/28 cases were consumed. LD-019, LD-020, LD-021 and LD-028 were not consumed in corrected continuation; they remain historical retention/applicability cases, not new auxiliary-acquisition failures. Each of the 16 historical records retains its original qualification ledger and exact step280 learning-record parity. The six lexical targets changed as intended; their IDs did not need replacement.
- **Prompt, target and arrays match.** `prepare.py:102-126` checks prompt/answer hashes against corrected audits and re-tokenizes the complete arrays against the corrected pool, including prompt prefixes. The real pinned AutoTokenizer test independently matches runtime-rendered prefixes to those saved in references. This checks the actual runtime template path, not only equal text strings. Largest expected target including terminators is 113 tokens; no reference inherently exceeds the 512-token cap.
- **Checkpoint/mount binding matches this proposal.** The frozen candidate adapter SHA is `c2305fc9cdc1fb99a346e58c92ae2ba1faa030ff6961bf0be1452f75006a8df0`; manifest SHA is `4ccf49623f1753efffc922a97f882cdbadbfcecabbda5ebccbe30e9f3e084dac`; mount prefix is `mixed-supervision/157531204582c50f2d8f73aaa76ce8ac`. The reference remains the retained step280 identity. `copy_adapter` verifies mounted manifest, expected inventory, sizes and copied weight bytes before use. Remote bytes have not been reverified by this review. The legacy default deliberately remains the old mixed96 comparison; the corrected call supplies its explicit binding.
- **The 56-cell design is coherent.** The fixed 28-case order interleaves two-case module blocks; alternate first-arm positions balance within every module. Runtime changes named adapters, freezes gradients again and creates a fresh cache per attempt. There is no automatic generation retry. Local success, cap and ordinary-error paths retain their first-attempt identity. Case completion counts are operational coverage, not semantic quality.
- **Reference nonleakage is respected by the prepared payload.** Only case IDs and original task prompts are serialized as inputs. Complete target/reference/qualification rows remain local and are not embedded in the scripts or passed to generation. Source-task contexts intentionally retain their original legitimate cues. This is static/local payload evidence, not inspection of remote bucket contents.

## What this diagnostic can and cannot establish

The original REPORT's descriptive question survives the correction: compare what step280 and corrected96 reproduce under the actual auxiliary instructions, plus familiar-context retention. The packet can provide acquisition-related observations on these selected training tasks. **There are no predictions yet, so acquisition is still unmeasured.**

The packet is purposive, small and dependent across entry families, grammar templates and inscription formulas. It cannot estimate full-corpus accuracy, unfamiliar-passage generalization, or the causal contribution of a particular dictionary entry. Grammar prompts supply analysis cues; passing means conditioned-task recall. Corrected96 also received additional historical supervision, so before/after differences do not isolate auxiliary supervision. The four nonconsumed historical cases are not a randomized control. Baseline pretraining exposure remains unknown.

Keep full inventories/alternatives and qualifications, blind checkpoint/exposure identity during review, retain separate reviewer results, and report case transitions and module counts. Do not pool English lexical JSON, short clauses and Persian passages into one accuracy number. Existing historical uncertainty and whole-translation critical-error policy remain necessary. No new gold, new ablation or additional training is authorized by a preparation pass.

## Independent verification record

1. `prepare.py --check`: PASS against the current checkout; no frozen writes.
2. All four corrected `PacketTests`: PASS (11.105 seconds), with only `setUp` redirected to ignored `resources/local/astra-diagnostic-review/<uuid>` so the experiment folder was not modified. The serialized settings/mount boundary, unchanged old default, real tokenizer prefix equality and mocked 56-attempt lifecycle were exercised.
3. Independently decoded the **saved** `job-spec.json` compressed command, verified its decoded SHA against the saved receipt, verified each embedded helper byte-for-byte against current files and compared saved settings with the receipt: PASS. This supplements tests which prepare a new specification.
4. Actual parent-child hard-stop reproduction: confirmed finding above. The child used a CPU fake model, no weights and no GPU.
5. All 16 historical `exact_step280_target_parity` fields independently inspected: true. Expected answer lengths inspected: maximum 113 tokens including terminators.

Not exercised: actual 31B loading/inference, GPU memory, generation latency, real adapter activation against GPU weights, remote checksum reread, remote persistence/recovery, current funds/pricing or paid launch. Tests demonstrate the specific local boundaries stated here, not scientific success or operational launch readiness.
