# Independent local preparation review

2026-09-27. **PASS for the identified locally checked components; no paid-launch admission.** Source qualification remains frozen. This review does not repeat linguistic adjudication or claim translation improvement.

## Design and data

The twelve proposal parents and twelve decisions match exactly, span nine works, retain their provisional qualifications, and keep expert/training admission false. All six qualification-decision bindings passed. The original whole attributed occurrence gloss remains distinct from exact published-reference subspans; none of the source, fragment, participant or forthcoming-edition limits is cleared.

Independent reconstruction from qualified TRAIN verified the SHA256-ranked selection of 720 distinct regular parents across 54 works, excluding all twelve designated parents. Both arms have 48 updates, microbatch1 and accumulation16: 768 slots, comprising 720 regular translations and 48 designated slots. Every update has the same fifteen regular parents followed by its designated parent. The four twelve-item cycles are original order, reverse, original rotated left six, and that rotation reversed. Every anchor appears four times with mean within-cycle position5.5. This balances position rather than exact learning-rate dose under warmup.

I recomputed sequence/prompt/supervised totals from the actual tokenized rows and ordered slots:

| Arm | Sequence tokens | Prompt tokens | Supervised tokens | Maximum sequence |
|---|---:|---:|---:|---:|
| Candidate |108694|80329|28365|660|
| Control |110050|79965|30085|660|

All six canonical token-census files are byte-identical to the completed census outputs. The saved census records exact reconstruction of all732 ordinary parents and twelve auxiliary answer boundaries; I checked its input/runner identities and independently reconstructed exposure arithmetic, rather than rerunning that entire tokenizer census. Candidate/control use the same parent IDs; designated candidate tokens must be selected from the auxiliary bank, while control tokens come from unchanged TRAIN. The common IDs do not make those row contents interchangeable.

The candidate explicitly requests the selected expression's contextual meaning and includes the complete source. The control uses the original full-translation task. Equal-parent loss therefore does not equalize token exposure or isolate a causal effect of linguistic labels alone. These differences and the short answers' terminator contribution are disclosed in PILOT.md. The fixed48-step, two-warmup-step recipe has no automatic extension or retry.

## Executed local checks and code review

I independently executed the exact frozen test entrypoint with the shared science Python, using its existing process-only project dependencies:

`python.exe -B -X utf8 cloud_pilot/test_contextual_train.py`

**Nine tests passed in4.028 seconds.** They exercised a real random tiny Gemma4 with nonzero LoRA: identical streams produce identical final adapter digests/losses after fresh tensor/optimizer/scheduler/RNG restoration; changed targets alter the update; actual delivered order corruption is rejected; invalid lengths/order/masks, pre-existing output and expired deadline fail; nonfinite gradients stop before updating; a candidate failure preserves the completed control adapter; and mutable-buffer changes are rejected. The core records delivered slots separately from completed optimizer steps, validates final counts, saves only completed arm adapters and preserves incomplete status/progress on an exception. No optimizer-resume or automatic-retry behavior was added.

**These tests use CPU FP32, bf16=False and gradient_checkpointing=False**, two optimizer updates and accumulation2. They do not execute the production48-step stream, NF4, BF16, gradient checkpointing, full31B model or A100 memory/timing boundary. The data schedule was checked independently; its full-model execution is still pending.

The canonical numerical-check script and result are byte-identical to their completed local evidence. Script and installed Trainer source hashes match the recorded values. The saved native-versus-manual test reports zero loss, gradient and updated-parameter difference for equal-parent reduction, while pooled-token weighting differs. The core explicitly sets `model_accepts_loss_kwargs=False`, uses microbatch1, native loss, zero smoothing and a fresh sequential Trainer. I inspected that implementation and the numerical comparison evidence; I did not rerun the separate one-update numerical study or generalize its CPU result to production precision.

No concrete blocker was found in this bounded core review. The low-level core accepts token streams/settings supplied by its caller; it does not itself establish the final step280 artifact, dataset-package or live-admission chain. That responsibility remains with the unfinished wrapper/integration.

## Evaluation and cost boundary

The corrected readiness trace and PILOT.md preserve **`dev_assisted.messages(row, 'plain', [])`**, including its caution and empty-example payload. I loaded only the historical run metadata and source-only inputs, then used the existing pinned local tokenizer: all24 message objects, input lengths and rendered-token SHA256 values exactly match the saved qualified plain run. No prediction text or reviewer ratings were read. `palref_eval.messages` would change this operational prompt and is not the proposed DEV path.

The uniform contract itself retains SHA256 `4165e8150f291c2cd6077d2daee86513ad08e1851acbfc3e83169bc40263f8c2`; all eight bound files were checked by raw hash only, without reading held-out answers. The pilot preserves separate15-whole/9-constrained denominators, two fresh blinded reviewers, first-attempt failures, the original improvement/harm screen and a distinct reused PAL40 regression stage. The newly trained matched control is the primary comparator; historical step280 scores remain descriptive. Incomplete execution cannot establish the training hypothesis. These are preserved design requirements, not an implemented or executed evaluation loop.

The arithmetic `75 × USD0.041667 + USD0.50 = USD3.625025` is correct as a **planning reservation**, not a provider charge guarantee. The documented credit is historical; this review makes no live balance, rate, job-status or billing claim.

Still unfinished before any paid admission: thin cloud/package wiring and exact source/artifact bindings; verification/loading of the actual step280 adapter; full-model NF4/BF16 and gradient-checkpointing behavior; BF16 base reload and two-adapter inference switching; the exact48-attempt evaluation/persistence path; cloud export and failure recovery; native75-minute timeout/termination and fresh credit/rate/autorecharge/job-inventory admission. No server, model-weight download or paid job was used here.

## Pinned evidence

| File | SHA256 |
|---|---|
|PLAN.md|`e11685e23ef1a72939c6ca3c7ff9136eb5a24e8d16880b6101eb2ede0fb4df3f`|
|PILOT.md|`83b876220d30d5e19211c44ba62093816d4061e6afaf9afb955c777b1aa5d332`|
|qualification-decision-v2.json|`70e6a477ebe8d0db714d7fb03cf49e9368001229488deeeff93c987b7eec21f4`|
|TWO-ARM-READINESS.md|`50afe93e7eac782df84a9377534bc6dc67448d7cb4db9a8482cfefb01cd43c70`|
|token-census/census.py|`83a53d66d38bef6a5ceb3d826de010c3088d3b50049536d7b8d2c424dd2969fa`|
|token-census/result.json|`406843264d8c9f9ddef7cfc5d8f40354b7c7d1845165a541dde8ae6d5d2981e7`|
|token-census/auxiliary-tokenized.jsonl|`270a0134c417a00744b274f0ad6ff0523aba5271a6177c4210d0042a0cdd25cc`|
|token-census/ordered-slots.jsonl|`d9e2e2e39ad912399be60dd473d22fb1d0a7e1f3791fbeccbe18e246ce2d6b1a`|
|token-census/regular-id-order.jsonl|`91d78e7b17484b9f93be0488d08ab2044fe768da7e17e331935f863b53950687`|
|qualified-v1/train.jsonl|`15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc`|
|numerical-check/check_native_parent_loss.py|`2723044c8b3e06b1ea6e5fbaaa9c49a474f86c00238b2f2c8717c301f41e0093`|
|numerical-check/result.json|`0f5dea1bcf369d032bef240e0c345ddec32477e5dfcbf62255dd2426d512554e`|
|cloud_pilot/contextual_train.py|`86ce4762a9a4e9356803ba2ed6e1c4c6689982a4cee3dab9b5e4bedd62b38122`|
|cloud_pilot/test_contextual_train.py|`942b0fe78e04c39963a14a518ef7584ad77d891c50405f9f019ca2c7cdccfb8f`|
|core-check.json, lead's separately recorded run|`1df2ad5947fd01b0415a54d015ccd5960af51f283320fbd032bb67ca057ec9fd`|

## AutoCode Critic record

- Mode: Classic + Critic.
- Lead agent/request id: /root
- Critic agent/request id: /root/final_external_judge
- Critic model and reasoning effort: inherited session settings, no override
- Independent from lead: yes
- Critic verdict: pass
- Evidence reviewed: The pinned plan, pilot, qualification decision, canonical census/numerical evidence, corrected readiness trace and frozen two-arm core/tests; uniform contract and its eight raw file hashes; historical qualified plain run prompt metadata.
- Verification evidence: Independently executed9 tiny CPU tests passed in4.028s; exact12-parent/9-work decision,720-parent/54-work selection,768-slot schedules, four cycle orders and token arithmetic reconstructed; canonical copies and hash bindings checked; all24 historical plain prompt/message/token hashes reproduced with the local tokenizer. No full-model, GPU, cloud, held-out-answer or model-output inspection occurred.

Verdict covers local preparation only. Full cloud integration, evaluation/export and paid admission remain open.
