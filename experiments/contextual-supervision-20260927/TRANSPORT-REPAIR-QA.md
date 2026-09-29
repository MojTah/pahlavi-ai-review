# Independent transport repair QA

2026-09-27. **PASS for the frozen transport and explicit attempt-2 preparation delta.** No unresolved blocker was found in this bounded offline review. This does not establish successful Linux startup, GPU execution, translation quality or paid-job completion.

The first job's recorded pre-Python failure exposed a gap in the earlier integration tests: they exercised generated Python but did not check the operating system's per-argument limit. The preserved original dummy specification has a 133,680-byte Python argument, or 133,681 bytes including NUL, exceeding 131,072. The original integration report and evidence remain unchanged; its local Python results are not Linux process-start proof.

## Executed checks

The new `transport-qa-evidence/checks.py` ran against the frozen wrapper and controller with project Python, without an API client, credentials, network, pretrained model or GPU. Its final run passed all **nine wrapper tests in 6.172 seconds**, including the prior seven lifecycle/export/child-monitoring tests and two transport regressions.

- Independently executed the actual generated compressed envelope in process, intercepting its final `exec`, and compared the decoded bytes with the exact original program saved before the repair. For dummy run ID `eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee`, all 133,680 bytes match; decoded SHA256 is `81be4ad494d5cec36bdd78ba5a96520540408409f7337f47fdf79d0aa0407b29`. Its compressed command SHA256 is `b4ae66db37761523a1a7383c1e416df4b4ebffae2ea444424cd0ed4b99773ae7`. Other command arguments and all five scientific script hashes are unchanged.
- The six argument sizes including NUL are **7, 3, 3, 56,109, 61,361 and 5 bytes**; total **117,488**. Every argument passes the stricter 100 KiB guard. Independent multibyte UTF-8, terminating-NUL, aggregate-size and checksum-tamper negatives fail before execution. The aggregate guard counts argv bytes, not the provider's environment.
- The exact decoded wrapper lifecycle executes through mapped local mounts and mocked bootstrap/driver boundaries. Complete output, candidate failure, bootstrap/package failure, real child timeout and nonzero exit preserve the appropriate complete/partial manifest and closed artifacts. A real Python subprocess executes the same compression-envelope function with a small synthetic program and verifies unchanged trailing argv. This is not a full-size Linux `execve` test.
- Default attempt 1 retains its original paths and three review bindings. Explicit attempt 2 rejects six nonqualifying failure states, selects separate local/result directories, binds both new QA/Judge reports and regenerates the exact compressed specification. Repeated preparation and execution writes fail exclusively; the original execution fixture remains byte-identical. The gate accepts the recorded `ERROR` with literal false bootstrap/training flags; it does not independently rediscover the provider failure.
- A separate adapted controller harness patches **both EXP and RESULTS** and exercises the new result directory. It passes one mocked POST, refused resubmission, both identified-job cleanup branches, owned-trial-only stop without execution.json, and funding expiry during provider reads producing zero POSTs. Existing funding and small-only committed-inventory negatives also pass. No old harness or original attempt artifact was overwritten.

These checks preserve the frozen data, recipe, driver, training core, helper identities, native75-minute limit, compute/export/persistence bounds and source-only evaluation. The repair adds only deterministic gzip/base64 transport, decoded/transport hashes, argv guards and explicit separate attempt-2 journaling. It introduces no automatic retry.

## Evidence identities

| Artifact | SHA256 |
|---|---|
|hf_contextual.py|`c5630b5765eca339e917e52241c0ee133e0243c70c3a3ae08cf5cd852cbea2c8`|
|test_hf_contextual.py|`545a17bc98fb9228520badc4a3c7eb703e14ca9b340410936320fa606600a2d5`|
|cloud_control.py|`0bd876d2d7986db49b55d1d6153a9908b31154afd12f21f90cd5b1ffacede857`|
|transport-qa-evidence/checks.py|`e3f52b619700332a448601efc25412c284bc6e40571dd8a9c5c0853419e8cf52`|
|transport-qa-evidence/result.json|`375e039d5aeb7d225eecee0a48dc7ef1626b5f40cfa588691da22daa0357129f`|
|transport-qa-evidence/controller_checks.py|`2e749922195ed0d7fd16a4629166b57f3aba5ed6744be933c5a2886a6de5f933`|
|transport-qa-evidence/controller-result.json|`885a80cce02637000ff07d838e084069c01727fe2d8a57af3950ec5ea6049837`|

The executed result also records all unchanged scientific source hashes. `before.json` preserves the original size/hash observation; the exact original comparison fixture remains under `resources/local/contextual-integration-qa/transport/previous-generated.py`. Both QA scripts use ordinary isolated local scratch. Run them with `resources/local/hf-client-venv/Scripts/python.exe -B -X utf8`; they do not launch jobs.

## Independent review record

- Lead agent/request id: /root
- Critic agent/request id: /root/final_external_judge
- Critic model and reasoning effort: inherited session settings, no override
- Independent from lead: yes
- Critic verdict: pass
- Evidence reviewed: Frozen wrapper/tests and controller delta, preserved original generated code, startup-failure record, unchanged scientific source hashes and new source-bound local QA results.
- Verification evidence: Nine wrapper tests PASS; exact decoded byte comparison; UTF-8/NUL/aggregate/checksum negatives; explicit attempt-2 separation/regeneration/exclusive-write checks; controller single-POST, cleanup, funding and inventory mocks PASS.
- Implementer agent/request ids: /root/qwen_penalty (wrapper), /root (controller)
- External QA agent/request id: /root/final_external_judge
- External Judge agent/request id: /root/train_review_03
- External QA verdict: pass

The real failed job was observed by the lead, not through a QA cloud call. Full-size Linux startup and full-model GPU/NF4/BF16/canary/training/evaluation remain unexercised here. The lead still owns the final source-commit/review/spec bindings, fresh funded admission, separate attempt-2 submission, monitoring, recovery and terminal confirmation. The planning reservation is not a billing guarantee; this review itself does not authorize a launch or recharge.
