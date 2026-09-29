# External Judge: contextual pilot integration

2026-09-27. **PASS for one bounded, attended exploratory attempt, subject to the root-owned live admission gates. No unresolved integration blocker was found.** This is a technical/scientific readiness judgment, not evidence of improved translation, production GPU feasibility, provider persistence or a billing guarantee. No job, model download, network request or semantic review was performed by this judge.

## Scientific comparability

The implemented contrast matches PILOT.md: both arms start from the verified qualified step280 adapter and receive the same 720 distinct regular parents plus 48 designated slots, in the same parent order. Each of twelve designated parents appears four times; the source evidence spans nine works and three families. The candidate changes the designated task to an explicitly contextual expression request and its qualified short target; the control retains the original whole-passage translation task and published target. This estimates the effect of that combined recipe replacement. It does not isolate label quality from task wording, answer length, terminator share or per-token weighting.

The native microbatch-one, sixteen-example accumulation and `model_accepts_loss_kwargs=False` preserve equal parent-example weight; the designated example contributes 1/16 of an update. The previously saved tiny-Gemma numeric check distinguishes this reduction from pooled-token loss, including gradients and updated parameters. Candidate/control training losses are not comparative translation merit. Warmup and anchor order do not produce exactly equal effective learning-rate exposure, although the schedule is identical between arms; no family-specific causal claim is supported.

The core restores exact initial trainable tensors, clears gradients, checks unchanged buffers and starts fresh optimizer, scheduler and RNG state before each arm. Independent tiny random Gemma/PEFT tests reproduce exactly equal final adapters for equal streams and different adapters for changed targets. The unchanged source-only evaluation comprises 24 cases per arm, 48 first attempts total, with the old qualified plain prompt/token identities, greedy decoding and alternating arm order. Its primary comparison is the matched control. Step280 remains descriptive. Both arms must complete before the frozen two-reviewer screen can pass; failures and unattempted cases cannot disappear from the denominator.

Twelve selected parents and one seed are adequate for this explicitly exploratory, fixed-cost question; they do not establish broad linguistic generalization. Source qualifications remain provisional rather than expert gold. A null result ends this recipe branch, not the general method. Fresh blinded reviewers and the unchanged 15 whole-reference/9 constrained-reference treatment remain necessary; no scoring was done here.

## Execution, stopping and recovery

The runner checks helper/package/TRAIN/source/adapter identities, reconstructs all ordinary and auxiliary token rows and verifies all evaluation prompt identities before loading model weights. The server then has a zero-update canary on the longest actual training sequence: NF4, BF16 autocast, nonreentrant checkpointing, native-versus-manual masked loss, finite nonzero LoRA gradients and unchanged adapter tensors. Failure prevents training. These full-size CUDA checks are implemented but remain unexercised locally.

Both final arm adapters are saved and verified before BF16 evaluation. The NF4 model is released with garbage collection and CUDA cache release; the BF16 base is loaded once, both named adapters are checked against saved tensors and every generation checks the active frozen adapter. External QA additionally exercised real tiny-model named-adapter loading, differing logits, restoration and tamper rejection. Full-size allocator behavior, NF4 kernels and BF16 reload capacity still require the real server attempt.

The final wrapper streams child output to both provider logs and its saved log. Timeout/interruption kills and reaps the child before export. Closed partial evidence and an already completed arm are retained; no model attempt or submission is retried. The root controller binds the source/specification/reviews, requires clean committed source, checks price/account/active jobs/fresh output prefix and refreshes funded-credit admission immediately before its exclusive submission journal and sole POST. Ambiguous acceptance is reconciled without repeating POST; identified jobs and local-record-write failures enter cancellation. Recovery downloads only bounded small evidence; remote weights remain server-side, with server SHA evidence distinguished from independently checked committed provider size/Xet inventory.

The controller is intentionally attended, not an autonomous watchdog. Root must observe through inventory confirmation, small-file recovery and terminal-state confirmation. Native 75 minutes is the fallback. The wrapper bounds compute to 3900 seconds and its internal lifetime to 4200 seconds, reserving export time and bounding persistence waiting; the provider timeout adds an outer margin. If hard termination prevents a closed manifest, recovery remains incomplete and the comparison cannot pass.

At the pinned 41667 microUSD/minute rate, 75 minutes gives USD3.125025 planned compute; adding USD0.50 yields the USD3.625025 reservation. Historical approximately 18–19 seconds/update suggests roughly 29–30 minutes for 96 updates, with prior 48-output evaluation approximately 17 minutes. This leaves plausible, finite setup/reload headroom within the 65-minute compute window, but current sequence lengths, download time and generated lengths can exhaust it. No estimate justifies extending the frozen timeout. Root's fresh live credit/rate/autorecharge/job checks and final source commit remain launch prerequisites; this judge did not independently access billing.

## Independently executed verification

- `resources/local/hf-client-venv/Scripts/python.exe -B -X utf8 -m unittest cloud_pilot.test_hf_contextual`: **7 tests passed**, 5.280 seconds. Includes real child log visibility, timeout/interruption kill and reap, exact generated wrapper lifecycle and partial export.
- `[USER_HOME]/.venvs/codex-science/Scripts/python.exe -B -X utf8 -m unittest cloud_pilot.test_contextual_train cloud_pilot.test_contextual_run`: **19 tests passed**, 9.385 seconds. Includes real random tiny Gemma/PEFT optimizer reset, order, target sensitivity and failure preservation; actual pinned tokenizer/package reconstruction; synthetic 48-attempt lifecycle, caps, switching failure and zero-attempt prefill failure.
- Final External QA PASS and its durable evidence were reviewed. Its final controller tests cover seven admission cases, expiration during provider reads producing zero POST, ten inventory negatives, one POST/relaunch rejection, ambiguous-submission cleanup, record-write cleanup and exact-trial stop without an execution record. These are mocked provider boundaries, not live service proof.

## Frozen review identities

| Artifact | SHA256 |
|---|---|
| `cloud_pilot/contextual_run.py` | `ab93adcdc4db96808313b651b721bb815ba6a3008a358560aab305a6532ce77f` |
| `cloud_pilot/contextual_train.py` | `86ce4762a9a4e9356803ba2ed6e1c4c6689982a4cee3dab9b5e4bedd62b38122` |
| `cloud_pilot/hf_contextual.py` | `6cdee28e8da30a10bbe9429c140619c3d1fbe4470caab31f133e31478ed43b22` |
| `cloud_control.py` | `340f8accac8b88239f65460f99dae80e3988a1e461b294fd58d38f6eec69778a` |
| Package ZIP | `bb3795d9a49927f333e8f565fc1b961c35d7069d9848a9649421ddf233243563` |
| Package manifest | `7920e92e73bb1fee9d606b67c2055c0e114d225252d72bddcfb0071abbe7a7c1` |
| `PILOT.md` | `83b876220d30d5e19211c44ba62093816d4061e6afaf9afb955c777b1aa5d332` |
| `TWO-ARM-READINESS.md` | `50afe93e7eac782df84a9377534bc6dc67448d7cb4db9a8482cfefb01cd43c70` |
| `LAUNCH-PREPARATION.md` | `ddc0f60807d56b176b00182950cf9a1e800896052f2557b84b6e1aea9723a470` |
| `INTEGRATION-QA.md` | `2d690ae16287bcd5a2c99658ab8a517315232ccfab0d7df861dd3ea4393c4c5b` |

Agent Company roles: lead and controller implementer `/root`; driver implementer `/root/train_review_01`; wrapper implementer `/root/qwen_penalty`; External QA `/root/final_external_judge`; distinct External Judge `/root/train_review_03`. Judge model/reasoning settings were inherited, with no override. This judge made no production edits and did not independently re-adjudicate the source anchors. Final verdict: **PASS within the bounded scope above; full server execution and translation merit remain unproven.**
