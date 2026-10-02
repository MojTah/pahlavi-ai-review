# Independent Astra review of the matched-NF4 proposal

30 September2026. Reviewer `/root/astra_runtime_plan_recheck`, distinct from implementation writer `/root/sol_submission_repair` and lead `/root`. **PASS for the exact local implementation, scientific plan and runnable proposal below, conditional on the declared live/server gates.** No unresolved blocker remains in this bounded review. This does not certify full31B GPU execution, provide human authorization or admit training.

## Scope and repairs

Reviewed the new NF4 runner/tests, `prepare.py`, `test_prepare.py`, `execute.py`, `PLAN.md`, exact final proposal and the relevant prior numerical path/installed PEFT behavior. Frozen BF16 helpers, scientific packet, cached outputs and other recorded sources reconstruct unchanged. I edited only this report; no authenticated API, network request, credentials, model weights, submission or training were used.

Three identified gaps were corrected before this verdict:

1. PEFT's adapter wrapper and bitsandbytes' actual base layer are both named `Linear4bit`. Class-name counting would double-count adapted layers and reject the real model. The final validator uses actual bitsandbytes types, and the test includes a same-name wrapper around the packed base.
2. NF4-load recovery originally changed the original ledger before validating its full schedule/counters. It now validates an isolated scratch ledger first and replaces the original only on success. The corruption test proves original bytes survive rejection.
3. Exact preparation initially omitted new transitive execution helpers. Final source bindings include the old `prepare_execution.py`, `submit_once.py` and `stage_inputs.py` as well as the new execution helper. The submitted proposal cannot silently inherit changed local claim/reconstruction code while retaining a passing source check.

## Numerical and scientific parity

Prior corrected96 training used NF4 double quantization, BF16 compute, `prepare_model_for_kbit_training`, FP32 nonquantized parameters, PEFT adapter upcasting and BF16 autocast. Installed PEFT source confirms that preparation casts all BF16/FP16 non-Params4bit parameters, not just normalization layers. The final runner preserves that policy while disabling backward-only checkpointing and freezing/evaluating both adapters. Server validation checks packed NF4/double-quant state, actual BNB compute dtype, all nonquantized floating parameter dtypes, absence of gradients, eager attention and disabled checkpointing; it records actual dtype inventories.

BF16 autocast surrounds both prefill canaries and every generation. Direct function diff confirms the paired generation loop differs from frozen BF16 only in its NF4 loading marker and those autocast contexts. Case/arm schedule, prompt construction, adapter switching, fresh caches, seed42, greedy generation,512-token/90-second caps, full56 admission, logging and first-attempt finalization are unchanged. Each adapter is verified before inference and after its56-cell panel; final numerical state must also match. Evaluation/dropout-off mode and cached autoregressive generation remain intentional differences from teacher-forced training. This is a matched numerical-policy control, not an exact replay of training forward/backward computation or an isolation of one arithmetic bit-width.

The plan freezes28 cases/56 new attempts and reuses all56 cached BF16 outputs for a jointly blinded112-record review. Module denominators, rubrics and individual raters remain separate. The predeclared primary rule is a **net accepted-count gain of at least two lexical inventories** for corrected96 under NF4 versus jointly re-rated BF16, in both reviewers; every gained/lost case and corresponding step280 change remains visible. This is an operational diagnostic rule, not a new deployment merit or significance test. Other-module safety/order reversals are retained. Absent or weak rescue closes the precision branch with appropriate uncertainty; incomplete execution authorizes neither retries nor training. Later training remains a separately reviewed contract, with no failure-targeted oversampling or invented gold.

## Direct local verification

- Independently ran `python.exe -B -X utf8 -m unittest cloud_pilot.test_nf4_learning_eval -v`: **6 tests passed in8.606seconds**. These cover actual installed PEFT FP32 preparation on a stub, strict load arguments, actual-type/same-name-wrapper validation, CPU autocast throughout56 mocked outputs, adapter/canary failures, refusal to retry existing attempts, outer run finalization/loading failure, and a tiny randomly initialized real Gemma/LoRA CPU forward with finite output and unchanged FP32 parameters. The tiny model is not real NF4 or full31B GPU evidence.
- The two preparation tests exercised exact allowed payload changes, embedded helper identities, parent-function preservation, SDK specification equivalence and interrupted-load recovery. The transport/payload test passed. The recovery test first encountered the known Windows sandbox TemporaryDirectory ACL failure before exercising recovery; rerunning that single offline test outside the sandbox passed in0.193seconds. No product defect was inferred from the ACL failure.
- Independently called `prepare.verify` on the final proposal with socket connections and API-client construction blocked. All63 recorded source bindings and exact proposal reconstruction passed, as did installed real SDK serialization/round-trip.
- Executed the actual transport's LZMA decode and SHA-256 verification statements without executing the decoded job. They reproduce the reviewed runtime bytes exactly. LZMA is a standard-library transport substitution: the larger two-runner gzip payload exceeded the existing100KiB bound. After the final fresh identity regeneration, the largest argument is78,663bytes (78,664with NUL), aggregate140,043bytes including NUL. Bounds were retained rather than relaxed. Original parent function source segments remain exact, with one separately reviewed NF4-load recovery wrapper added.

Final integration repair: root's readback-only entrypoint encountered a post-save display error because two observations both supplied `utc` to a `dict` call. The one-line dictionary merge now handles that overlap. I inspected the change and independently passed its fully mocked staging-entrypoint regression in0.601seconds, verifying serialized STAGED_NOT_SUBMITTED and no claim/submission. No scientific or server-runtime code changed. The old unsubmitted proposal was preserved as superseded, and I reconstructed the final fresh proposal under blocked sockets/API construction; its exact source bindings and SDK round-trip pass. The final identities below supersede the earlier draft report's proposal identities.

## Execution boundary

Static review of `execute.py` confirms reviewed source/proposal reconstruction and SDK restoration before live use; fresh funding observation, account/private-bucket identity, minute rate, USD5.51 ceiling includingUSD0.50 reserve, idle/matching-job checks and empty output prefix. Existing inputs and small adapter metadata are read back; adapter weight sizes/hashes are bound through manifests, with full weight-byte hashing required on the server. No upload, recharge or local weight download is introduced. The independent review gate binds the exact proposal check hash. Root alone can call the reused exclusive-claim/single-submission helper; ambiguous outcomes retain the claim and prevent automatic retry.

These live gates were inspected, not called by this reviewer. Full GPU loading/BNB behavior, runtime canaries, provider acceptance/time accounting and persisted result recovery remain execution checks. The120-minute ceiling,6,600-second compute cutoff,6,900-second internal deadline,180-second cooperative reserve and5,100-second full-panel admission requirement remain unchanged. The current local PASS does not guarantee export through arbitrary GPU/kernel/provider faults.

## Exact reviewed identities

Final run ID: `814f0551174743d7951e0d1e9cd349cc`.

| Artifact | SHA-256 |
|---|---|
| `cloud_pilot/nf4_learning_eval.py` | `f998b83ac37e80430a037e4b107ef580291c775ebdadd1e75e278311a2be150b` |
| `cloud_pilot/test_nf4_learning_eval.py` | `9c4808c6f47aa16365824938bb711644b96e3d7d817020102e8aca22b90c5d1a` |
| `PLAN.md` | `89fc573ddfdc7c9275ac4989bab1e971dc57ed0e09b425a645ff84bef74602a1` |
| `prepare.py` | `2139adf7e01d4476c8336eaf54d704410c6b04ba3d22dc96cae26075cab47ded` |
| `execute.py` | `5e37cc8995826c0f46d19a41ec290fb6b2b32d5c7ab9a86a9ff05464b6408665` |
| `test_prepare.py` | `cfcdc44daa18e0d6a83308e2e75ec5dd7941c77dc80fabdfa2440af29ff4e93d` |
| `execution-proposal/check.json` | `e15dc399b086072793a087cf968cfcf3595ec54513d9c7426aa0dc94de546b07` |
| `execution-proposal/job-spec.json` | `b542d4859dee1da4ecab5a7e9fc9063cd4243849f2c81c705e7317336c6a9e25` |
| `execution-proposal/job-receipt.json` | `80c5520253d9c26379cef076e9dc655ad7aba7a4209ba42582b932080190a1d3` |
| decoded runnable program | `1f4fe04647ab69254b6acdfb7b93ca5a6155e221cfb32c395125b429613cf952` |

This PASS binds these bytes and the declared one-run inference scope. Any substantive numerical/scientific/implementation change requires renewed review; no automatic expansion, promotion or retraining follows from this record.
