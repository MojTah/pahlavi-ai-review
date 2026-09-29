# Conditional-fit diagnostic launch

Long-run classification; Classic + Critic. Root owns launch, observation, recovery, shutdown and repairs. The independent critic is report-only. This is one bounded first-real-A100 numerical canary followed by the remaining frozen forwards only while each check passes; local tests do not establish full-model GPU behavior.

## Frozen action and completion

Use `hf_train_fit.specification` with run ID `5e4fe4fbd90c47748bdb608bcb8b3cda`, input `train-recall-5a2b29c878b6.jsonl` and control `train-fit-control-3db2398a95b6.json`, each with its full SHA from preparation.json. The exact prepared SDK request is `resources/local/hf-train-fit-20260927/spec.json` (SHA256 `07395b28fe42bcab21602d647bc68d50d4df6f67f6508bab213bfcc72511a57c`). Its embedded command SHA256 is `82bea787af14e95cdbf765c632b8b12e44804b11f8c110fa76632b780569065a`. Regenerate and compare exact wire dictionaries immediately before the single `submit_once` call. Record the clean source commit and returned job ID in execution.json. An exclusive submission-started.json prevents duplicate POSTs; ambiguous responses use read-only label reconciliation.

Exactly 80 frozen forwards, no optimization/generation/resampling. First numerical, provenance, adapter-state or deadline failure stops further forwards and publishes partial evidence. Scientific completion requires all 80 identities, verified source/target tokens, finite independent masked CE matching native loss, source/adapter restoration, full artifact SHA recovery, and terminal provider state. An incomplete run remains incomplete and receives no aggregate contrast. The unchanged translation merit is not replaced by this diagnostic.

## Resources and host

HF account Mojionix, private bucket Mojionix/pahlavi-pilot; pinned Linux PyTorch image and frozen requirements from preparation.json. A100-large, one 80GB GPU, BF16/eager, maximum 504 input tokens and 215 supervised tokens per forward. 80 scheduled forwards contain 12,576 input and 3,736 supervised token positions. Prior same-host setup took about eight minutes; anticipated total roughly 10–20 minutes, with actual full-model forward speed still unmeasured.

Native timeout29m; computation alarm24m; internal deadline27m including export/persistence. Persist for at most180s after publication, ending earlier on verified recovery and root cancellation. Live rate41,667 microUSD/min gives native compute ceilingUSD1.208343; additional USD0.25 reserve gives admission allowanceUSD1.458343, below this experiment's USD1.50 ceiling. Reserve is not a provider billing guarantee. Live creditUSD16.20 at12:17UTC; autorecharge unset. User authorizes existing funded credit strategically, no purchase/recharge. Fresh active-job/rate check before POST; all15 jobs terminal at12:18UTC.

Input and trained-adapter mounts read-only. Only fresh `train-fit/5e4fe4fbd90c47748bdb608bcb8b3cda` writable; ephemeral server /tmp staging/cache. Base weights are downloaded only on the server. Laptop receives only small evidence. New8,881-byte source-control JSON has a committed-Xet/full-SHA roundtrip proof; qualified bundle and adapter rechecked on server.

## Verification and recovery

Local actual Gemma4 random-weight FP32/BF16 numerical tests, nonzero PEFT switching/restoration, exact tokenizer census, generated wrapper success/failure/partial-publication tests, and complete/partial artifact-analysis integration passed. Independent READINESS-REVIEW records exact hashes and boundaries. Previous same-host immutable bundle/bootstrap/transfer/persistence path ran successfully; new full-size GPU forwards remain to be exercised here. No separate paid preflight or retry job is justified.

`observe.ps1` inspects this exact recorded job and saves provider logs/progress every roughly30s. Setup absence of useful progress for five minutes triggers diagnosis from current logs, not a duplicate launch. First forward performs the full numerical check; every subsequent forward repeats it. Runtime timeout is a hard backstop if observation fails. At ready_to_persist, `recover.ps1` requires committed provider inventory, logged manifest SHA/identity, safe seven-file whitelist, maximum16MiB and every file's full SHA before recording recovery.json. Then cancel this job once and inspect terminal state/all-job inventory. CANCELED after verified recovery is intentional shutdown, not discarded results.

No automatic technical retry, changed threshold, changed control, free-generation retry or checkpoint overwrite. Preserve failures/partials; root alone chooses a bounded repaired experiment after evidence review. Analyze through `scripts/analyze_train_fit.py --experiment experiments/train-fit-20260927`; report parent/work NLL contrasts as diagnostic evidence only. Next training requires a specific intervention with its matched control and uniform DEV merit.
