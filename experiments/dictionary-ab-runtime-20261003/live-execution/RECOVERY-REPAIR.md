# Actual output recovery and validator repair

5 October 2026. Execution mode remains Classic + Critic. Main owns recovery and integration; `result_recovery_critic` independently reviewed metadata and the two-file correction read-only.

Hugging Face reports job `6ac124c7fbc85ba68237d56f` COMPLETED: started 3 October 15:54:06.820 UTC, finished 16:07:44.869 UTC, running 818 seconds. Only this run's closed `final/` directory was recovered: 103 files, 1,282,165 bytes. Direct provider inventory has content IDs and matching sizes; every downloaded file matches its closed-manifest SHA256. No model weights, training, resubmission or recharge.

The original scorer rejected the real export because it required `output_prefix` in the manifest. The reviewed server exports embedded `settings`; the prefix is a preparation-receipt transport field and was never embedded. This was the only mismatch among the 18 original manifest checks. The independent critic also checked all 36 fixed run controls, run identity and receipt bindings.

The surgical repair permits only that field's absence, rejects an explicitly conflicting manifest prefix, and retains the exact independently recovered receipt prefix/run/manifest/inventory checks. Test fixtures now follow the native exporter. New tests reject a wrong receipt prefix and a wrong explicit manifest prefix. No source, reference, prediction, merit, model, decoding, arm denominator or continuation threshold changed. The original scorer is preserved locally with SHA256 `9b6bdcbeb2596b3612cf877406256095a044abfb69057978b5f790841184a1aa`; older readiness pins remain historical evidence.

All 15 scoring tests pass. An initial full run passed 14 tests but its child CLI hit Windows paging-file error 1455 while importing PyTorch. The successful repeat disabled unused PyTorch/TensorFlow imports for these tokenizer-only local checks (`USE_TORCH=0`, `USE_TF=0` in that process environment); no installation or global setting changed. Successful test runtime: 84.831 seconds. The actual preparation CLI also passes, including full output-token decoding, frozen inputs, canary and unchanged adapter checks.

Technical result: 30/30 first attempts successful, complete independently recovered evidence, READY_FOR_BLIND_REVIEW. Two separate fresh contexts receive only their respective opaque 30-record packets. Translation quality remains unscored until both valid reviews return. AI judgment remains provisional; these familiar DEV passages do not establish unseen accuracy.

Local evidence root: `resources/local/dictionary-ab-results-20261005/d68800b3b35c44a4a97adc0c5129a3de/`. `recovery-receipt.json` stays outside `final/`; raw evidence and packet mappings are lead-only. This recovery adds no GPU compute. Provider duration supports an estimate, not an invoice; no new balance or actual charge is claimed.
