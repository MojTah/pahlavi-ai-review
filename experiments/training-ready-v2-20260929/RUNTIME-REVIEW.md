# Runtime readiness review for corrected data

**RESULT: PASS for the three repaired admission defects; PARTIAL for overall launch readiness.** Independent reviewer `/root/runtime_readiness`, 29 September 2026. The fixed 96-update path supports a corrected, same-sized pilot. The pre-repair findings below are retained as evidence and superseded for those defects by the independent after-repair checks at the end. The exact real corrected corpus and future cloud gates remain separate. No project training, optimizer step, model load, network access, credentials, cloud job, or spending occurred.

## Concrete pretraining findings

1. **RUNTIME-V2-001, P2 — duplicate IDs fail too late.** `cloud_pilot/mixed_run.py:31` accepts two rows with the same ID when the manifest repeats that ID. The synthetic 1,536-row probe passes the actual `read_data`; the active recovery validator at `hf_mixed.py:30` requires unique IDs and would reject completion after paid training. Reject duplicate IDs before loading the model. Repeating words or compatible translations is a separate linguistic issue; this check concerns record identity.
2. **RUNTIME-V2-002, P2 — failed manifest is accepted.** `mixed_run.py:26` checks the checksum-bound data bytes and schedule but not the manifest's declared status. A synthetic manifest explicitly marked `FAIL` passes. Require `PASS`, and bind the new preparation to its completed correction/audit receipt. This is a fail-closed admission improvement, not evidence that the historical manifest failed.
3. **RUNTIME-V2-003, P2 — invalid vocabulary token is accepted.** The actual reader accepts input token `999999999`, with otherwise valid masks, schedule and hashes. That value cannot enter the real embedding table. Validate every ID against the already pinned tokenizer vocabulary before model loading. The corrected builder must retain exact prefix identity, answer decode, terminal IDs and reserved-token checks. No malformed real row was demonstrated; these probes target avoidable future admission failures.

The lead owns all fixes. The runnable, no-model reproduction is `tmp/runtime_readiness_probe.py`; metadata is frozen in `runtime-readiness.json`. The probe intentionally proves the current bad inputs are accepted. Once fixed, replace those expectations with negative regression checks rather than treating the historical probe as a success gate.

## Exact artifact and dependency evidence

The actual `hf_mixed.prepare` was called on a valid synthetic 1,536-row schedule. Its generated transport compiled, decompressed and executed only its definitions/settings, with the final job invocation removed. All seven embedded script bytes match the local originals. The serialized `completed_training` helper is present before its callers. Largest argument: **70,612 bytes**; total including NULs: **131,992 bytes**. Existing 100 KiB per-argument / 1 MiB total guards pass. The embedded bootstrap ends before the older `tiny-smoke` entry.

The image remains pinned by digest, and requirements remain hash-locked. Runtime pins are Torch 2.11.0+cu128, Transformers 5.13.1, PEFT 0.21.0, bitsandbytes 0.50.2, Accelerate 1.14.0, tokenizers 0.22.2, huggingface-hub 1.23.0 and safetensors 0.8.0. The local Python is Windows 3.11.15; all those installed package pins match except bitsandbytes is absent. Real admission explicitly requires Linux amd64 Python 3.12 and one BF16-capable A100 with at least 75 GiB. This check is not a new Linux/A100/NF4 execution.

The prior 27-test audit and the three after-repair tests remain the numerical/recovery evidence. This reviewer verified their unchanged relevant source hashes rather than rerunning identical tiny-model tests. They cover answer-only masks, single native label shift, equal-example loss, deterministic order, nonfinite gradients, fresh optimizer/scheduler, changed step-20 adapter, failure preservation, packed helpers and successful/error evaluation paths. The repaired receipt checks cover 12 invalid cases. All source and report hashes used here are recorded in JSON.

The starting adapter is strongly pinned on disk, and the final BF16 reload checks every loaded adapter tensor against saved safetensors. A cheap optional hardening is to reuse `contextual_run.verify_loaded_adapter(model, args.adapter, 'default')` immediately after the trainable original adapter load at `mixed_run.py:178`, before the canary. It has not been demonstrated that the original load is incorrect. If added, test the actual helper with a tiny saved random adapter and a deliberate tensor mismatch; do not download real weights.

## Fixed schedule and corrected-data requirements

The production path intentionally has a fixed **96 updates × 16 examples = 1,536 unique rows**, in blocks of 12 historical, 2 lexical and 2 other rows. Relevant hardcoded points:

| File | Fixed assumptions |
| --- | --- |
| `mixed_train.py:16` | 96 maximum steps, accumulation 16; forecast also splits by 16. |
| `mixed_run.py:28` | Manifest rows 1,536. |
| `mixed_run.py:33` | 96 updates, microbatch 1, accumulation 16, exact 12:2:2 quota. |
| `mixed_run.py:36` | Ordered 16-row task blocks. |
| `mixed_run.py:189` | Candidate identity records 96 new steps. |
| `mixed_run.py:206` | Final state and completion event record 96 steps. |
| `hf_mixed.py:29` | Recovery requires 96 steps, 1,536 slots and unique ordered IDs. |
| `hf_mixed.py:136` | Startup event declares 96 steps. |
| `hf_mixed.py:244` | Prepared settings declare 96 steps and 100-minute timeout. |
| historical `prepare.py:185–213` | Fixed task quotas, 96 blocks, 1,536 selected IDs. |

A same-sized corrected pilot fits this contract. A full-pool run does not: editing only the JSONL or manifest cannot safely change the schedule. Do not imply a 1,536-row pilot has trained on the full corrected inventory.

Before freezing the new package, verify every source-to-projection disposition; no silent dropped meanings, arbitrary homonym selection or guessed reference repairs; zero unresolved conflicting exact prompts; explicit held records; preserved source-entry boundaries; no evaluation/work leakage; deterministic sampling; unique IDs; exact token decode and masking; valid vocabulary IDs; no unknown tokens, truncation or reserved controls; every sequence at most 2,048 tokens; and the exact 12:2:2 block schedule. Prepare twice and require byte-identical outputs. Freeze train, manifest, source/audit/script identities, then rebuild and inspect the exact final packed artifact. A longer corrected target must be admitted or explicitly held, never truncated.

## Budget and archived timing

The last mixed job's archive records **1,852.14 seconds (30.87 minutes)** for 96 training updates. Provider log stages span approximately **48.13 minutes**, including a five-minute persistence window. Historical rate: **41,667 micro-USD/minute**. These are archived observations, not live price or billing facts.

The old full eligible pool has 10,151 rows / 1,365,977 sequence tokens; the old pilot has 1,536 / 258,988. Simple row and sequence-token scaling gives **2.71–3.40 hours of training**, or **USD 6.78–8.50** at that historical rate, before download, reload, evaluation and reserve. These crude proxies do not predict throughput for changed targets or preserve the pilot task mixture. They demonstrate that full-pool exposure cannot be quietly substituted into the 100-minute pilot. Keeping the 12:2:2 mixture while exposing every lexical row would require additional repeated historical rows and a different, still larger schedule.

The unchanged launcher limits are 100 minutes native, 95 internal, 85 computation, 600 seconds export reserve and at most 300 seconds waiting for persistence. At the archived rate, the maximum compute reservation is USD 4.16670 plus the existing separate USD 0.50 reserve. The most recent located admission observed USD 18.73 usage and USD 6.27 cap headroom **before** that already-completed mixed job. It cannot authorize another run. A fresh usage/credit/rate/idle-job/storage/output-prefix check must precede submission; this review changes no billing logic and creates no submission authority.

## Boundaries that remain for a future authorized launch

The fresh longest corrected sequence must pass the in-job zero-update NF4 loss/gradient check. Step 20 must show a changed adapter and pass the measured finish forecast; if it does not, stop and retain evidence. The reload/evaluation allowance is an estimate, not guaranteed completion, and incomplete results must keep the frozen denominator. Export/persistence must be independently confirmed before claiming a durable model. No CPU check certifies A100 memory/throughput, Linux signal handling, provider storage or network behavior.

The intermediate/final saves are adapters, not optimizer/scheduler/RNG checkpoints. Exact interrupted optimizer resumption is unsupported and already declared false; never automatically restart training from an unconfirmed outer status. The inactive historical contextual wrapper has the previously documented phase-reporting risk and is outside this corrected mixed path.

**Handoff:** fix the three pre-load admission gaps, freeze and validate the corrected package, then retain explicit fresh-cloud and user-launch gates. Dataset preparation can be locally ready without claiming paid execution has already passed.

## Independent after-repair check — PASS

At `2026-09-29T19:20:55Z`, the lead's repaired `mixed_run.read_data` and `hf_mixed.prepare` passed **10 negative cases**: duplicate IDs, failed manifest, absurd out-of-vocabulary ID, upper vocabulary boundary, unknown token 3, malformed answer terminator, conflicting complete prefix, wrong tokenizer binding, missing tokenizer binding and attempted legacy preparation. The valid corrected synthetic 1,536-row schedule was accepted. The read-only legacy path still accepts its historical compatible duplicate prefix, while the preparation gate refuses relaunching that legacy projection. This explicitly closes all three findings above for the reviewed hashes.

The new synthetic exact artifact also compiled/decompressed and all seven embedded scripts matched current source. The largest argument is **71,300 bytes**, total **132,680 bytes** including NULs. Source hashes:

- `mixed_run.py`: `1326526a5a32d9200ee58851d75cb9acda4e039ea95f9b594abc64e997287249`.
- `hf_mixed.py`: `c710a063e5157f5ad645ede8e3ffc5a0bc6d57681d5771e7df0cf9cc7accba37`.

`mixed_train.py` and `contextual_train.py` remain byte-identical to the previously tested numerical path. The repair changes admission only; no numerical rerun was needed. Reproduction: `python -B -X utf8 tmp/runtime_readiness_after_repair.py`. Its full evidence is appended under `after_repair` in `runtime-readiness.json`. This fixture did not load or optimize any model, and did not inspect benchmark answers.

**Remaining handoff:** the lead must replay and inspect the exact final corrected-data package, whose bytes differ from this synthetic fixture, and retain the fresh billing, real GPU and persistence gates. The 10 passing negative cases are not a claim that future cloud execution or every linguistic target is certified.
