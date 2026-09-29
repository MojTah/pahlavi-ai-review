# Independent integration QA

2026-09-27. Agent Company, External QA. **PASS for the final source-bound integration and attended-controller preparation.** No unresolved blocker remains in the reviewed scope. Paid admission remains a separate root-owned gate. Source qualification and merit remain frozen.

## Independently executed evidence

The durable QA harness is `integration-qa-evidence/qa_offline.py`, beside this report. It uses existing science Python and process-only project dependencies, with offline flags. Test scratch is redirected to `resources/local/contextual-integration-qa`; production code is unchanged. No pretrained weights, network, credentials, cloud or held-out answers are used. Only synthetic prediction fixtures are inspected.

1. The tracked34,600-byte ZIP, local transfer copy and pinned manifest match exactly. There are exactly seven data files plus manifest, no duplicate or unexpected entries. Every file size/hash matches and payloads equal the canonical source/census files. The24 DEV prompt identity entries contain only case ID, input-token count and rendered-token hash; they contain no reference answers or model output text.
2. The frozen driver and initial wrapper passed15 focused tests together in7.402 seconds, with zero Windows permission retries. The driver actually reconstructs all732 ordinary/control rows and twelve auxiliary token rows with the pinned tokenizer, matches all768 ordered parent slots per arm and verifies all24 historical plain prompt identities. Package inventory/hash, qualification, focus, token, schedule and prompt mutations are rejected. The narrow spelling/fragment/participant/edition qualifications remain bound through the package and its decision, not upgraded to expert gold.
3. Stubbed generation exercised the complete48-first-attempt schedule, alternating named arms, exact sequence IDs and counters. A failure on attempt3 records that error once, leaves45 unattempted and stops; caps and wrong active-adapter state fail closed; a prefill failure records zero experimental attempts. These tests verify Python lifecycle behavior with stubs, not meaningful translations or full-model GPU generation.
4. A separate real random tiny Gemma4/PEFT FP32 CPU test saved two distinct LoRA adapters, loaded them as `control` and `candidate`, and exercised control→candidate→control. The driver's saved-versus-loaded tensor verifier passed both adapters; the installed PEFT status API reported the required available/active/unmerged/frozen states. Logits differed between adapters and returned exactly to the original control logits. Deliberately changing a loaded candidate tensor was rejected. This verifies real named-adapter serialization/loading/switching APIs locally, without claiming production BF16 or31B execution.
5. The exact generated initial wrapper definitions and invocation were executed with mapped local mounts and mocked bootstrap/driver/cloud boundaries. Complete output, candidate failure with preserved control adapter, bootstrap failure and package corruption exported the correct complete/incomplete evidence. Closed-file hashes were independently checked; `.tmp` files were omitted, no base/checkpoint was exported and a byte-limit violation failed. An additional injected `TimeoutError` preserved a closed partial adapter and incomplete manifest, retained the original exception, invoked the body once, and kept the declared alarm/export/persistence bounds. Provider persistence remains explicitly unverified by these tests.

The final durable harness was then executed against **all final driver/wrapper bytes:17 tests PASS in10.349 seconds, zero permission retries**, followed by the same additional real tiny-PEFT and exact-generated timeout/export checks, both PASS. `integration-qa-evidence/result.json` binds these final sources. Initial results are preserved separately and are not substituted for the final run.

The original wrapper's five tests also passed independently in2.904 seconds before the combined run. That earlier wrapper hash is historical evidence only; final acceptance requires the subsequent live-log delta below.

## Static integration review

The driver validates the exact package, qualified TRAIN, step280 adapter and frozen helpers before training. The longest actual660-token training sequence is the zero-update NF4 canary input. Its implementation enables nonreentrant gradient checkpointing and CUDA BF16 autocast, compares native loss with manual masked cross-entropy, checks finite nonzero adapter gradients and unchanged adapter tensors, and clears gradients. That GPU canary is implemented but **not locally executed** by this QA.

The already-reviewed core preserves fresh initial adapter tensors, optimizer/scheduler/RNG and identical parent order between the two48-update phases. Driver verification checks completed arm counters, saved adapter inventory/hashes, finite tensors and architecture. `target_modules` lists are compared as sets with duplicate/invalid-entry rejection, rather than treating PEFT serialization order as semantic. After training, the driver releases NF4 state and loads the BF16 base once, loads both named adapters, verifies exact saved tensors, then evaluates each source with the original qualified plain prompt. Auxiliary training targets are never placed under a whole-passage instruction.

The wrapper embeds source bytes into one SDK-signature-checked request; it does not instantiate an API client or submit. Input and trained-result mounts are read-only and the output prefix is a fresh run ID. Source package, trained manifest, step280 completion and individual adapter artifact checks precede the server-only base downloader. It invokes the driver once. Its outer controls are native75minutes, compute3900seconds, internal4200seconds, up to300seconds export reserve and300seconds persistence wait, with a2GiB evidence bound. The wrapper completion gate requires both48-step/768-slot arms and all48 distinct successful/abstaining first attempts with exact schedule/source identities; partial/error/retry/duplicate records cannot become a complete result.

The unchanged PILOT.md correctly treats USD3.625025 as a planning reservation, not a billed-charge guarantee. The12-parent/9-work intervention,720 regular parents, original/reverse/rotate-six/reverse cycle order and candidate/control task/token differences remain the previously reviewed design. Fixed15-whole/9-constrained merit, two fresh blinded reviewers, first-attempt failures and separate reused PAL40 regression remain required. No semantic scoring was performed here.

## Final wrapper and controller checks

The final wrapper's seven tests independently passed in5.042 seconds before the final combined run. An actual child-process handshake proved that progress reaches inherited stdout and the byte-identical log before the child exits. Real timeout and injected interruption tests verified one spawned child, kill/reap, closed pipe and bounded return. The exact generated wrapper also exported the completed control fixture and partial log after a real child timeout/nonzero exit. The log pump has per-line flush, a bounded join and exception propagation; no child retry was introduced.

The root-owned controller initially lacked identified-job cleanup after an ambiguous submission and after a local execution-record write failure. I reported this concrete issue; the reviewed repair invokes shutdown on known jobs and records a local fallback identity. Its stop path reconciles the exact trial ID without requiring execution.json. A separate immediate pre-POST funding freshness recheck closes the stale-during-provider-reads case.

The durable `integration-qa-evidence/controller_checks.py` executed only fake API methods and local fixtures against the final controller. It passed valid funding plus stale/future/NaN/infinite/insufficient/recharge rejection; ten unsafe-path/binary/incomplete/extra/uncommitted/size-mismatch inventory cases; small-record selection excluding safetensors; exact prepare/regeneration plus one mocked POST and rejected resubmission. Both identified-job cleanup branches passed. Stop without execution.json selected only the owned trial and excluded a foreign job. Admission that expires during provider reads produced zero POSTs and no submission-started record. These are direct local failure-path checks, not evidence of live provider behavior.

The controller is attended, not an autonomous watchdog. Its native75-minute fallback and source/package/spec/admission gates remain distinct from root's repeated observation, committed-inventory recovery and explicit termination confirmation. The final LAUNCH-PREPARATION.md correctly distinguishes this ownership and the separate root-reported transfer/live observations. QA did not independently access those external services.

Reproduce the two durable scripts from the project root with the shared science Python for `qa_offline.py` and project `resources/local/hf-client-venv/Scripts/python.exe` for `controller_checks.py`, both using `-B -X utf8`. Both write runtime fixtures/results only to the authorized local QA scratch; the preserved JSON copies in `integration-qa-evidence/` record this review's executions.

## Source-bound identities

| Artifact | SHA256 |
|---|---|
|contextual_run.py|`ab93adcdc4db96808313b651b721bb815ba6a3008a358560aab305a6532ce77f`|
|test_contextual_run.py|`0d5846f3b8d44e98efd55442f8300139f5b6a53058cd08bbdd2293b5d52b35f3`|
|contextual_train.py, unchanged|`86ce4762a9a4e9356803ba2ed6e1c4c6689982a4cee3dab9b5e4bedd62b38122`|
|Tracked package ZIP|`bb3795d9a49927f333e8f565fc1b961c35d7069d9848a9649421ddf233243563`|
|runner-package-manifest.json|`7920e92e73bb1fee9d606b67c2055c0e114d225252d72bddcfb0071abbe7a7c1`|
|PILOT.md|`83b876220d30d5e19211c44ba62093816d4061e6afaf9afb955c777b1aa5d332`|
|LAUNCH-PREPARATION.md final reviewed version|`ddc0f60807d56b176b00182950cf9a1e800896052f2557b84b6e1aea9723a470`|
|hf_contextual.py final wrapper|`6cdee28e8da30a10bbe9429c140619c3d1fbe4470caab31f133e31478ed43b22`|
|test_hf_contextual.py final tests|`3bd9d618942ced00515a038552f0b8be137793dd081d829c091f60d5f454cb4d`|
|cloud_control.py final controller|`340f8accac8b88239f65460f99dae80e3988a1e461b294fd58d38f6eec69778a`|
|integration-qa-evidence/qa_offline.py|`5bc5c82b1ac96e68da7b20f518017e2701c130312569c35d1deaa92697b49ac8`|
|integration-qa-evidence/result.json|`ba1baba1f412767f51a7259351cf304e7f1168d3e46140b495862fcacbd9c309`|
|integration-qa-evidence/controller_checks.py|`294bc07de973444518cc8bff3f1d02c6054d98031a5c558360ba5bd7567015ad`|
|integration-qa-evidence/controller-result.json|`3b98441c293d6819af8a3eba10260576846b856adbbdaffe753f6d6a06cb079e`|
|integration-qa-evidence/wrapper-final-result.json|`2a7a8c128e323358a60af7d4c7b2d96b5771c5c3930538375a441121992985bd`|

The offline generated-command hash for fixed dummy run ID `eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee` was `81be4ad494d5cec36bdd78ba5a96520540408409f7337f47fdf79d0aa0407b29`. A real prepared run has its own command/spec identity; this dummy run was never submitted.

## Agent Company record and limits

- Lead agent/request id: /root
- Implementer agent/request ids: /root/train_review_01 (driver), /root/qwen_penalty (wrapper), /root (controller/package)
- External QA agent/request id: /root/final_external_judge
- External Judge agent/request id: /root/train_review_03
- External QA model and reasoning effort: inherited session settings, no override
- Independent from lead and implementers: yes
- External QA verdict: pass
- Evidence reviewed: The final pinned driver/core/wrapper/controller/package and experiment documents, exact generated wrapper, actual local tokenizer and tiny PEFT APIs, and the durable executed QA scripts/results.
- Verification evidence:17 final integrated tests passed in10.349s with zero permission retries; extra native tiny-adapter roundtrip/switch/tamper and exact-generated timeout/partial-export checks passed. Final controller admission/inventory/single-POST/cleanup/stop/freshness mocks passed. No actual API or pretrained-model execution occurred.

No full31B/GPU/NF4/BF16 training/evaluation, real CUDA checkpointing, Linux signal delivery, cloud export/persistence or end-to-end timed job was executed locally. Root's source-commit/spec binding, upload roundtrip, fresh credit/rate/autorecharge/job inventory and single-owner submission/recovery admission remain separate prerequisites. This QA supplies no billing guarantee or permission to recharge, retry or launch.
