# Qualified Gemma plain/assisted DEV runner

Prepared 2026-09-27 in the isolated approved coding scope. Classic Codex preparation; root owns independent review and integration. No inference, model downloads, cloud/API calls, submission, scoring, credential access, or billing changes occurred. Existing files and frozen helpers were not edited.

`cloud_pilot/dev_assisted.py` runs exactly 48 first attempts: the frozen 24 source-only DEV cases under `plain` and `assisted`, both using the qualified completed step-280 Gemma adapter. It does not implement a submission controller. The original step-312 `dev_diagnostic.py` remains unchanged and is reused only for its source-input validation and shared constants/control-text helper.

## Frozen identities and prompt contract

- DEV source-only input SHA256: `06ac58310bf67767fae4124d8e935c808d15debcd8daebce07b583937cd97182`.
- Qualified evidence SHA256: `1d5e02cfb91dad1da94db072e9f5fcd6be463746bbc951425cb6631b5ea2ce4a`.
- Qualification audit SHA256: `193f49f54dd1649a6a0002ed423bdf3dfa7176a7a093e1532cdd1ce1ea32d8f1`.
- Qualified TRAIN SHA256: `15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc`.
- Adapter config SHA256: `9e7f2895e1ab5fe3707e7e533653df2b64003b1b7823194e72e79b63372b20f4`.
- Adapter safetensors SHA256: `a51bcd02c6077bcec400c1f342ede3205f260e419ed4f9e3ad0f4338a7e4afdf`.
- Source continuation manifest SHA256: `b61409386550270efa1ae738fabe962a167cd2fffcd4ced0d7cc3e3f1d78c3f6`.
- Existing qualified adapter PAL-REF run metadata SHA256: `31851757809214362c8175d247d35055c04cb2090cc7c92b357858e248863d45`. Only run metadata, not predictions/references, was used to corroborate adapter identity.
- Frozen evaluation helper SHA256: `050a38880c68113ca5e5ebc4abd26945d05959eeda52f5df64f00292acfe4a49`.
- Local uniform evaluation-contract reference SHA256: `4165e8150f291c2cd6077d2daee86513ad08e1851acbfc3e83169bc40263f8c2`. Inference records this digest only; the assessment/reference contract is not an inference input.

Both arms use the identical literal `palref_eval.SYSTEM`, identical common caution, and a canonical JSON user envelope containing the exact supplied source. Plain has `examples: []`. Assisted has each original complete frozen TRAIN example and its complete original retained qualification record. No reranking, replacement, correction, deduplication, or newly generated translation is introduced. All 58 attachments/56 unique witnesses and their original order and qualification hashes are checked; DEV answer fields at the source/example schema boundary are rejected. Frozen byte hashes additionally protect nested metadata.

Reusable APIs for the other model family:

```python
rows = dev_assisted.frozen.read_inputs(inputs_path)
witnesses = dev_assisted.read_evidence(evidence_path, audit_path, rows)
messages = dev_assisted.messages(row, "plain", witnesses[row["id"]])
messages = dev_assisted.messages(row, "assisted", witnesses[row["id"]])
ordered = dev_assisted.schedule(rows)
```

The schedule visits six existing strata and four sorted works, alternating pair order by stratum plus work index: 12 plain-first/12 assisted-first overall, and 3/3 within each work. Each row appears exactly once per arm. Same policy in both arms: official frozen tokenizer/chat template, nonthinking, seed42, greedy, one beam, 4096 new-token ceiling, 1200-second case deadline, EOS `[1,106,50]`, pad0, BF16 original base plus frozen adapter, fresh DynamicCache/context per attempt. Inputs are not truncated; actual token counts and input-ID hashes are recorded after checking input plus output limit against model context.

## Execution and preservation

The CLI requires explicit `--bundle`, `--base`, `--tokenizer`, `--inputs`, `--evidence`, `--audit`, `--adapter`, `--output`, and `--deadline-utc`. It only accepts already local verified assets and sets the Hugging Face/Transformers offline flags. Runtime/GPU imports are lazy. Bundle verification, exact qualified TRAIN hash, exact adapter weights/config/status/provenance, base/tokenizer provenance, protocol hash, and the source/evidence checks precede model loading.

The output directory must be new. `run.json` includes exact prompts, schedule, model/adapter/tokenizer/runtime/recipe identities, input token counts/hashes, and unattempted IDs. `predictions.jsonl` is exclusive-create and flushed after every first attempt. Errors, empty outputs, output-cap failures, case timeouts, and global deadline stops preserve already recorded attempts and mark the run incomplete; no retry or automatic resume is implemented. The final EOS return is also checked against both deadlines before success is recorded. Loading failure preserves a run manifest with zero attempted outputs.

Deadlines inside generation are cooperative stopping criteria. A blocked CUDA kernel or process failure needs the outer controller/job timeout and export reserve; this runner alone is not a hard GPU-process kill mechanism. No budget policy is implemented here. Root must assemble the required frozen helper modules and verified local assets, and complete runtime/controller readiness before execution.

## Offline validation

Command actually executed:

```powershell
resources/local/hf-client-venv/Scripts/python.exe -B -X utf8 -m unittest cloud_pilot.test_dev_assisted
```

Result: **8 tests PASS**, final run 0.158 seconds. Tests read the real frozen source/evidence/audit and qualified adapter metadata; model execution and file writes are mocked. Coverage:

1. Exact 58/56 evidence identity, example order, full original qualifications, common prompt/caution, protocol and local evaluation-contract digests.
2. Changed bytes and added DEV reference fields rejected even when a test rebinds outer hashes to exercise independent schema checks.
3. Qualification text-hash identity mismatch rejected independently of the audit outer hash.
4. Complete 24-by-2 schedule with globally and per-work balanced condition positions.
5. Fresh-output requirement before GPU admission.
6. Qualified adapter hashes corroborated against both released continuation manifest and existing run metadata; steps20/312, wrong TRAIN identity, and checksum failures rejected.
7. Full mocked 48-output execution: single base/adapter load, frozen settings, fresh caches, ordered unique predictions, identity binding, 24 completed pairs.
8. Mocked generation exception, case timeout, output cap, global deadline before next attempt, and deadline detected at final EOS preserve exact first-attempt denominators and unattempted IDs without retries.

Not exercised: real tokenizer rendering/token counts, model loading, actual safetensors weight hashing/loading, CUDA/BF16 memory use or numerical inference, wall-clock throughput, GPU kill/export, cloud bootstrap/import packaging, paid submission, and semantic scoring. The mocked run is execution-path evidence, not a claim that inference succeeded on hardware.

Frozen code SHA256:

- `cloud_pilot/dev_assisted.py`: `f26e8c29ab1b3390455f6a93e2ea34cb44f3ff6d627f4957de583a737c884940`.
- `cloud_pilot/test_dev_assisted.py`: `c6aeb4014519544fb809d6d4e6106efc34772c4a1306b9cb5756ce7ebfc95808`.
