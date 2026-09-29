# Independent TRAIN-fit readiness review

27 September 2026. **PASS for the frozen implementation, local numerical checks and saved request.** Two analyzer defects found by direct execution were repaired and independently rechecked. No remaining blocker was found within this preparation scope. This review does not claim a completed GPU diagnostic, proven full-model memory fit, remote persistence, or a new translation result.

## Actual independent verification

The critic read the new runner, job packager, tests, analyzer and frozen scientific contract. No source files were edited. Writes were confined to this report and ordinary inherited-permission scratch directories beneath `resources/local/train-fit-test-tmp`. No cloud, network, credentials, pretrained model weights, package installation or nested agents were used.

**Thirteen focused tests passed in 7.050 seconds, with zero skips.** They were run together through `unittest` using the existing science Python, with process-only paths to `resources/local/train-fit-deps` and the HF-client environment. Actual imported versions were Torch **2.11.0+cu128**, Transformers **5.13.1**, and PEFT **0.21.0**. Model execution in these tests was CPU-only, with a locally initialized small random Gemma4 model; no pretrained weights were involved.

The directly executed numerical checks cover both FP32 and BF16: full logits, correct next-token shifting, answer/terminator-only masking, manual sum/count versus native masked loss, prompt-position perturbations having no effect on the masked calculation, and rejection of inconsistent/nonfinite evidence. The LoRA B parameters were explicitly nonzero. Actual adapter-off/on/off/on calls changed the result when appropriate and reproduced it when repeated. Enabled state and frozen parameters were restored after ordinary calls, a failed forward and an after-forward timeout. No optimizer, generation call, training mode or KV reuse is part of the new evaluator.

The actual local tokenizer recreated all twenty correct-source saved TRAIN arrays exactly and preserved each target suffix and terminator across the twenty mismatched-source inputs. The frozen map has forty distinct input identities and eighty scheduled forwards. Independently recomputed census: longest input **504 tokens**, largest supervised suffix **215 tokens**, **12,576** input positions and **3,736** supervised positions across the eighty forwards. This is a token census, not a measurement of full-model GPU memory or latency.

The runner tests directly exercised all eighty successful forwards, first-forward and eightieth-forward failures, durable active-attempt state before each model call, persisted result ordering/counters, and deadline failure before the first call. They confirmed first-failure stop without retry, no missing-slot replacement, and explicit incomplete state. Frozen input/control/helper hashes, source permutation, schedule balance and token-map corruption rejection were tested. CPU numerical calls exercise the actual core forward function; eighty-case lifecycle tests substitute the expensive model forward.

The packager tests executed definitions and invocation extracted from the **actual generated job command**, with external/bootstrap/model boundaries mocked. The real local publication helper produced manifests and matching exported file hashes for success, failed forward, bootstrap failure and input/control hash failures. Checks include no output-directory reuse, no authenticated client/submission, no bootstrap after bad input identity, and failure persistence without retry. Completion requires exactly eighty successful first-forward records, twenty completed parents, no active or unattempted slot, and matching source/token/adapter identities; stale, missing, duplicate and malformed numerical records were rejected. These mocks do not prove a Linux signal interruption, real download, full GPU forward or provider upload.

## Analyzer findings and closure

The initial analyzer returned early on partial runs before checking recovered row identities/counters. It also failed to compare `parent_provenance` with the frozen source/target/TRAIN-row identities. An independent synthetic artifact harness demonstrated both problems through the actual `analyze()` entry point, with internally consistent manifest/recovery hashes. Root repaired only the analyzer; runner, packager and saved job request hashes remained unchanged.

The final analyzer was independently challenged on thirteen complete artifact chains:

- Accepted a complete eighty-forward fixture and recovered the known four contrasts: adapter gain **1** and mismatch penalty **2** nats per supervised token, with twenty equal-parent units and work summaries.
- Accepted a valid eight-forward partial, a prepared zero-result partial, an active attempt without a durable result, a durable result one ahead of its run counter, and a terminal failed prefix. **Every partial returned no aggregate contrasts.**
- Rejected incorrect arithmetic, invalid run identity, incorrect recovered row input identity/sequence, incoherent partial counters, incorrect parent-source provenance, a nonterminal error followed by further results, and failed adapter restoration evidence.

The honest durability windows are preserved rather than rewritten as completed attempts. A failure before token preparation produces no valid prepared identity; such evidence must remain raw failure evidence, not be interpreted as a validated numerical comparison. The analyzer's separate `--self-test` also passed paired arithmetic and missing/duplicate rejection after the repair. All these are synthetic numerical fixtures, not model fit findings.

The retained executable harness is `resources/local/train-fit-test-tmp/critic_analyze_integration.py`; its fixtures remain beneath the same scratch root. It uses standard local file hashes, actual frozen parents/control/token maps and actual analyzer code, with no real output semantics or credentials.

## Scientific and operational boundaries

The implementation follows the predeclared four conditions: adapter on/off crossed with correct/one fixed mismatched source, twenty original TRAIN parents and eighty forwards. It retains the exact translation-training instruction, original answer/terminator and loss boundary. The mismatch changes only the source for this diagnostic; no new false translation pair is written to TRAIN. The cyclic shift of five excludes same-parent/work matches but is not a semantically certified negative. Equal-parent and per-work likelihood contrasts remain distinct from translation merit, causal proof, generalization or significance. The previous partial recall is neither retried nor refilled.

The unchanged uniform evaluation contract has SHA256 `4165e8150f291c2cd6077d2daee86513ad08e1851acbfc3e83169bc40263f8c2`; all eight files it binds were independently rehashed unchanged. No benchmark cases, references, scores or rubric were modified. The new fit question concerns conditional likelihood with gold prefixes; the protocol explicitly retains that interpretation limit and the NF4-training/BF16-inference distinction.

I regenerated the saved job request for run **`5e4fe4fbd90c47748bdb608bcb8b3cda`**. The entire wire dictionary equals `spec.json`, including SDK Volume dictionaries, read-only input/trained mounts, unique output prefix and all five embedded script byte strings. Preparation fields and command hash match. The SDK signature binds without instantiating a client or submitting a job. Image is pinned to `pytorch/pytorch@sha256:eee11b3b3872a8c838e35ef48f08b2d5def2080902c7f666831310ca1a0ef2be`.

The request specifies A10080, a **29-minute native timeout**, **24-minute compute alarm**, **27-minute internal deadline** and **three-minute export/persistence reserve**. At the recorded rate of 41,667 micro-USD/minute, 29 minutes plus USD0.25 reserve is **USD1.458343**, within the provisional USD1.50 envelope. This arithmetic is not a hard provider billing cap or finalized charge. Current credit, rate, job inventory and transfer/admission observations remain the lead's live responsibility before the sole submission.

Full 31B loading, exact GPU kernel/numerical tolerance, longest-input GPU peak memory, Linux watchdog behavior and provider-side persistence were **not exercised** here. Local CPU proof and prior cloud evidence cannot certify those new full-model boundaries. The admitted job must preserve the declared first-failure stop, recover and hash small evidence before shutdown, and confirm terminal state. There is no automatic second job or retry authorization in this review. Final source-commit/admission binding remains a pre-submission gate owned by `/root`.

### Final observation/recovery delta

The later saved admission records fifteen terminal jobs, USD16.20 credit, automatic recharge unset and the same A100 rate. The transfer record attests an 8,881-byte full-hash roundtrip of the exact source-control JSON. These are lead-recorded live observations, not provider calls repeated by the critic.

I read `observe.ps1` and `recover.ps1`, parsed both with the native PowerShell parser and compiled their embedded Python without executing it. No parse/compile errors occurred. The observer fetches only the recorded job's status/logs and saves progress; it does not submit or cancel jobs. Recovery requires one publication event, a committed provider manifest with bounded size, matching full manifest SHA and exact run/bundle/adapter/script/control/token-map identities. Its seven-name allowlist excludes model tensors, bounds total evidence to 16 MiB, verifies safe paths and committed file sizes, then hashes every downloaded artifact before writing success proof. It handles a status-only failed setup as partial evidence. Neither script creates a second job; neither supplies an autonomous shutdown controller. The sole owner must still perform bounded observation, explicit own-job cancellation when appropriate and terminal confirmation, with native timeout as the outer bound. This delta is a read/compile review, not executed network or recovery proof.

## Frozen evidence

Paths are relative to the project. All SHA256 values below were measured from the reviewed files.

| Artifact | SHA256 |
| --- | --- |
| `cloud_pilot/train_fit.py` | `1a29c09bf3c92f6923082e076cd28df74fe863a3d12f52f1bba73ed3af001a0d` |
| `cloud_pilot/test_train_fit.py` | `5f931ada4d45faf19dec49af110b52a72fffd3610b37ab002372d332a3e919c0` |
| `cloud_pilot/hf_train_fit.py` | `57f7746c0c4affe9797989f5c5c559b7019fb8b4462dce699ec6134067bc3f08` |
| `cloud_pilot/test_hf_train_fit.py` | `204da6a6baa4957fa55927da66ba429998807d92b37d13e311c9cdd2fd498416` |
| `scripts/analyze_train_fit.py` | `cae1785547a196d2ecd6793b224dab27332aafa634ab1e29df3efc894cea910e` |
| `experiments/train-fit-20260927/PROTOCOL.md` | `bcf6d74c7491d5294917b129c63149e1b0cda03a462f60980027b7d7715b3830` |
| `experiments/train-fit-20260927/source-control.json` | `3db2398a95b6480ad2522dc2fe30d2d38156564e3a4a72714b43bcc2a54393a0` |
| `experiments/train-fit-20260927/token-audit.json` | `a3dbbab31b5b893e032cc1fcac4d2b459f4231d3a367953e0191bb780ff3e7c8` |
| `resources/local/hf-train-fit-20260927/spec.json` | `07395b28fe42bcab21602d647bc68d50d4df6f67f6508bab213bfcc72511a57c` |
| `resources/local/hf-train-fit-20260927/preparation.json` | `95bb03bd10e7825d3eb3a7119a2c3a9d9eb1bd154ecdaab2df63f9e3212c215d` |
| `resources/local/train-fit-test-tmp/critic_analyze_integration.py` | `551c7f99704d10c0e492839b5bb5831994113a6a1a2a0004ac2b678506df9887` |
| `experiments/train-fit-20260927/observe.ps1` | `e8f5b6003b241d62ae327e45fafeb60b672d338c1419beab3063bd6dddd77b81` |
| `experiments/train-fit-20260927/recover.ps1` | `1b578350f356607d9244e74eff5114ba50d1e1e965e5de03dafad4a9f6d7f00c` |
| `experiments/train-fit-20260927/admission.json` | `7c4c3e50a0502227ab7741300fe9664bcf1f09bfe40b17679d38f9215a4ffd31` |
| `experiments/train-fit-20260927/input-transfer.json` | `98973856e3cf527d95bc2b10405e04f3a33775b2a8ca061adccf8c95a768cc3b` |

Generated command SHA256: `82bea787af14e95cdbf765c632b8b12e44804b11f8c110fa76632b780569065a`. Frozen forty-input token-map SHA256: `de1388e6ae8e260ec1233cefbbcdcbc4130871715707898973de1696e9f168bf`. Qualified TRAIN and step-280 adapter/manifest hashes are checked by the reused frozen helpers and are embedded in the reviewed request; no model tensors were locally read.

## AutoCode Critic record

- Mode: Classic + Critic.
- Lead agent/request id: /root
- Critic agent/request id: /root/final_external_judge
- Critic model and reasoning effort: inherited session settings, no override
- Independent from lead: yes
- Critic verdict: pass
- Evidence reviewed: The exact frozen implementation, tests, repaired analyzer, protocol/control/token census and generated request bound above; reused qualified TRAIN/adapter helpers and unchanged evaluation contract.
- Verification evidence: Thirteen focused tests passed with zero skips; real random Gemma4 CPU FP32/BF16 masked-loss and nonzero PEFT restoration checks; actual tokenizer parity; generated-wrapper success/failure publication tests; thirteen direct analyzer artifact integrations; analyzer self-test; exact saved-request regeneration and five embedded source-byte checks; independent token/budget census and eight unchanged benchmark/development bindings; native PowerShell parse and embedded Python compile of the two final observation/recovery scripts without executing their external calls.

This is a bounded implementation/readiness PASS with live admission and unexercised full-GPU limitations explicit. It is not a finding about learned translation quality and does not authorize a training experiment or broaden the frozen diagnostic.
