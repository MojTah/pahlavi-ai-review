# Bounded plain/assisted cloud comparison

27 September 2026. **Code checks passed; commit/provenance binding is the final launch gate. No job submitted yet.** Classic + Critic. Root is the sole execution and repair owner; agents review or prepare isolated files only. This is an inference experiment, with no training or automatic next experiment.

## Scope and decision

One Gemma qualified step280 job and one original Qwen3.6-27B job each collect48 first attempts on the same24 DEV sources, with/without the same58 qualified TRAIN attachments. The frozen uniform-evaluation contract is unchanged: `4165e8150f291c2cd6077d2daee86513ad08e1851acbfc3e83169bc40263f8c2`. The15 whole-passage cases and nine constrained cases retain separate denominators. References and scoring stay local. Two fresh blind reviewers will compare the96 outputs before selecting another paid intervention. The fixed40-case PAL-REF is not rerun or modified here.

The specific question is whether a different model family or supplied linguistic examples improves meaning preservation. Repeating SFT without this information would leave both assumptions untested. An incomplete comparison is inconclusive; preserve all attempts and diagnose the cause before authorizing any revised experiment.

## Exact entry points and immutable inputs

From the project root, the execution owner uses the existing project HF interpreter:

```powershell
& resources/local/hf-client-venv/Scripts/python.exe -B -X utf8 -u -m cloud_pilot.run_hf_dev_assisted --family gemma
& resources/local/hf-client-venv/Scripts/python.exe -B -X utf8 -u -m cloud_pilot.run_hf_dev_assisted --family qwen
```

After the independent critic gate passes, commit the frozen sources, bind the ignored provenances to that exact HEAD/controller/admission, and run the controller preparation/admission checks before either POST. This final binding cannot precede the source commit.

Each command gets a separate monitored process. Prepared JSON specifications and provenance are stored under `resources/local/hf-dev-assisted-{family}-20260927*`; their exact command, controller, input and source-commit hashes are checked before submission. The shared admission records both unique trial IDs, current credit observation and the sum of both reservations. No duplicate or unlisted job is permitted.

Model revisions: Gemma `842da3794eaa0b77d5f08bae87a17459d91ff475`; Qwen `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`. The Gemma completed adapter is recovered from `continuations/1ae0f16dae9c4dffa36d15a24345fded`, manifest SHA256 `b61409386550270efa1ae738fabe962a167cd2fffcd4ced0d7cc3e3f1d78c3f6`. The Qwen publisher-file inventory is bound by `qwen-source-identity.json`, SHA256 `b0d6d51fe7603d4a955be4dec41b551100a4ca401b5d1d8a1a5a4c8d5427f8ce`.

The existing qualified bundle SHA256 is `41fbbe703b7eb3cfc471c83e344ede16c1e92cae8a604b91f638a57d856477b9`. Source inputs, exact evidence and qualification audit are checked before installation/download; no reference-answer files are uploaded. The two new input files total239,919 bytes and passed independent bucket-download SHA256 round trips before launch. Proof is `resources/local/hf-dev-assisted-transfer-20260927/transfer-proof.json`.

## Resource and recovery limits

Live billing read recorded by09:05:54UTC: creditUSD18.37, usageUSD11.86, automatic recharge unset. The latest user authorization permits this existing funded balance; no credit purchase or auto-recharge is authorized. Live API verifies `a100-large` at41,667 microUSD/minute, one A10080GB. Two55-minute native timeouts reserveUSD4.58337 total compute, plusUSD0.75 unspent allowance. This is the first experiment's reservation, not a requirement to spend the remaining balance. Unrelated account use is outside these two job limits; reject unexpected active jobs and stale funding observations before launch.

Each job uses the existing immutable Linux/Python3.12/Torch2.11 CUDA12.8 image and hashed Linux dependency lock. At least90GiB ephemeral disk is required. Model weights download only to the server's temporary directory; no laptop checkpoint or model download occurs. Only the private bucket `Mojionix/pahlavi-pilot` is mounted, with inputs and any trained adapter read-only and a fresh `comparisons/<trial_id>` output prefix writable.

The native provider timeout is55min; the internal total deadline is50min, with computation interrupted at47min and up to3min reserved for result publication. Each experimental output retains its first attempt,4096-token ceiling and1200-second case limit inside the stricter job deadline. Require at least15min remaining after setup. Expected completion is below the native ceiling; actual full-checkpoint load, longest-prompt memory and throughput remain unmeasured until the server canaries.

Both models must pass a longest-prompt prefill check before experimental generation. Qwen additionally runs two short synthetic cached-generation requests to check same-seed/fresh-cache behavior. Failure saves a zero-attempt run record and stops; no automatic repair, alternative settings or paid restart. Cloud installation, snapshot verification, canary and output collection share the same hard timeout. Successful canaries permit the fixed remaining schedule in that same job without a second download.

Read-only observation has bounded retries. Submission is never retried: uncertain submission is reconciled by its unique label, then any found job is stopped. Publication writes closed artifacts and a manifest; the controller checks committed provider inventory before canceling idle compute. Final cancellation is confirmed, and only small result files are recovered and SHA256-verified. Native timeout remains the backstop if the local controller loses contact. There is no resumed or repeated experimental attempt in this recipe.

Done means both jobs terminal, all96 first attempts retained, manifests and local small-result hashes verified, then the unchanged blind scoring procedure completed. A canceled status after verified publication means deliberate shutdown, not loss of an otherwise complete experiment. No quality improvement is claimed before that comparison.
