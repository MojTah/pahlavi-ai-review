# External Judge: bounded transport repair

2026-09-27. **PASS for the frozen transport repair and one explicit, separately admitted attempt 2.** No unresolved blocker was found within this offline scope. The original integration review missed the operating-system argument-length boundary; its successful Python tests did not prove Linux process startup. This delta addresses the observed failure without changing the scientific experiment.

The preserved startup log is exactly `exec /usr/bin/python: argument list too long`. The recorded job `6ab920de52d0dbd7f1d9c57f` terminated in ERROR before bootstrap/training, with zero evaluation attempts. This is a pre-outcome infrastructure failure, not an unfavorable experimental result being discarded. Those provider observations were recorded by root; the judge made no cloud call.

## Independent checks

- Rebuilt the repaired specification using the **actual failed run ID**, decoded its gzip/base64 payload without executing the server program, and compared it against `resources/local/hf-contextual-run-20260927/spec.json`. All **133,680 decoded bytes are identical**, SHA256 `c2b374d69674bb5c8fd81e1d388c2e5d2746d818dff15965b48e9f243598d6e2`, matching the original preparation/execution identity. Every other request field is identical for that run ID. The checksum-verifying envelope adds only standard-library transport.
- For that exact identity, repaired argv sizes excluding NUL are **6, 2, 2, 56,136, 61,360, 4 bytes**, total **117,516 including the six NULs**. Each argument is below the new 100 KiB guard. Sizes differ slightly for another run ID because the payload is compressed; the guard executes for each fresh specification. The total guard covers argv, not provider environment strings.
- Independently ran `resources/local/hf-client-venv/Scripts/python.exe -B -X utf8 -m unittest cloud_pilot.test_hf_contextual`: **9 tests passed in 6.368 seconds**. They retain the prior lifecycle, child monitoring and partial-export tests, and add exact decoded-program identity, checksum/size rejection and a real Python subprocess using the envelope with a small synthetic program and unchanged argv. No full-size Linux command was executed locally.
- Independently exercised controller argument selection with mocked preparation: attempt 2 selects separate local/result paths and both supplementary review bindings; RUNNING, bootstrap-started and training-started prior states reject before preparation; attempt 3 is rejected. No provider call was made. Reviewed final External QA's additional source-bound tests for exclusive records, preserved original execution, one POST/no resubmission, both known-job cleanup branches, exact-owned stop and admission expiry during provider reads.

The original source/package/adapter, optimizer schedule, data, prompts, generation policy and merit remain unchanged. The new decoded command hash and compressed command hash are distinguished. Original attempt records remain intact; attempt 2 requires its own fresh run/output prefix, exclusive preparation and submission journal, committed-source/spec/review bindings and live admission. There is no automatic retry or attempt-3 path. The startup gate consumes the frozen failure record; it does not independently rediscover the provider state.

The previous scientific-comparability judgment remains applicable. Full-size Linux startup, GPU/NF4/BF16 behavior, runtime canary, training, evaluation and persistence remain unproven until executed. Root retains attended monitoring, partial recovery and terminal-state confirmation, with the unchanged native 75-minute fallback. USD3.625025 is the new attempt's planning reservation after a fresh funded-balance check. The failed startup has no finalized charge attribution; absence of Python work does not prove zero billing or that combined attempt costs fit the original reservation.

## Frozen identities

| Artifact | SHA256 |
|---|---|
| `hf_contextual.py` | `c5630b5765eca339e917e52241c0ee133e0243c70c3a3ae08cf5cd852cbea2c8` |
| `test_hf_contextual.py` | `545a17bc98fb9228520badc4a3c7eb703e14ca9b340410936320fa606600a2d5` |
| `cloud_control.py` | `0bd876d2d7986db49b55d1d6153a9908b31154afd12f21f90cd5b1ffacede857` |
| `startup-failure.json` | `0cdd1faebb835226425a0de97f15d9dff559653074a1f8077d63b50a50e6075e` |
| `startup-error.log` | `7db93886e4b221d793d64a6dbf4a27b6b8882459564641bd6b7e414521ffdf2d` |
| `TRANSPORT-REPAIR-QA.md` | `eb86ca4f377b23a4636ff88a96b536f5e08b85bc061ec12f2d19d66509e6e4f8` |

Lead/controller implementer: `/root`. Wrapper implementer: `/root/qwen_penalty`. External QA: `/root/final_external_judge`. Distinct External Judge: `/root/train_review_03`, inherited model/reasoning settings, no override. Judge production edits, network/cloud requests and semantic ratings: none. **Final verdict: PASS for this bounded repair; live admission and execution remain root-owned.**
