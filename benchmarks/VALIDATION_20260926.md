# PAL-REF v1 release validation

Validated locally on 26 September 2026 UTC, using `C:\Users\mojta\.venvs\codex-science\Scripts\python.exe`. One lead, Classic Codex; no independent agent or human specialist review. No model execution.

Frozen manifest SHA-256:

`a3932f7510f101376cc91c47bb23f3c9872656c41f563701fa3dcb2b6c89a5e8`

`benchmark.py verify` returned PASS: 40 passages, 42 source records, five works and 160 directional cases; 11 data/code/document files checked against the manifest. The manifest itself is checked against its separate anchor. `.gitattributes` disables newline normalization for these byte-preserved artifacts, including the anchor.

Git's staged copies of all 12 frozen packet files and the separate anchor were compared byte-for-byte with the verified working files and matched. `git diff --cached --check` passed; the attributes recognize preserved CRLF line endings. The AutoCode gate script was inspected and supports Critic/AgentCompany modes only, so it is not applicable to this Classic Codex checkpoint.

## Source checks

- All 42 copied raw source records compare equal to the saved archive entries. The archive export still matches its recorded SHA-256.
- Exact extracted transcription, Persian and English text was checked during assembly against both raw archive and curated records. Only terminal citations were separated; the connected three-record passage was joined with newlines in every language.
- Selected raw response hashes were verified during assembly.
- All six original translator TRAIN/DEV/TEST JSONL files still match their pre-assembly hashes. No original split was edited.
- The selected five works are absent from the recorded TRAIN/DEV. No selected normalized source overlap at the stated similarity threshold or exact normalized target overlap was found there.
- None of the final selected IDs occurs in the 22 scanned saved prediction/input/response files. The exact file list and hashes are in `selection-audit.json`. This is not proof against unrecorded exposure or foundation-model pretraining.

## Executed software checks

```powershell
& 'C:\Users\mojta\.venvs\codex-science\Scripts\python.exe' -B -m unittest discover -s tests -p test_translation_benchmark.py -v
& 'C:\Users\mojta\.venvs\codex-science\Scripts\python.exe' -B benchmarks/pal-reference-v1/benchmark.py verify
```

All **10 tests passed**. They exercise refusal of blank templates, missing/duplicate cases, changed inputs, reviews bound to a different output, unsupported passing judgments, undocumented adverse judgments, blank/abstaining/late outputs labeled successful, and nonstandard retrieval/shared-context declarations. They also execute the whole-work training guard and detect tampering with a copied reference or manifest.

Arithmetic was checked using explicitly synthetic fixtures: seven non-pass outcomes among 40 cases yield 33/40 accepted, while execution failures remain in the denominator. Per-work totals match direction totals. These numbers are test fixtures, **not model scores** and not a validation of human/AI judgment accuracy.

The first test attempts encountered Windows sandbox permissions on `tempfile` directories. The test harness now creates unique scratch directories with inherited permissions inside the ignored project `tmp/benchmark-tests` directory, verifies their resolved parent before cleanup, and passes there. The frozen benchmark files did not need changing for that environment issue.

## Outstanding boundaries

The fixed reference packet is built and verified. It is not newly certified by an independent Pahlavi specialist. No current-model score, general translation accuracy or readiness claim follows from these checks. The training guard and source-only protocol are supplied here but have not been integrated into the separate translator's pipeline. No repository remote is configured; preservation is local Git plus file hashes.
