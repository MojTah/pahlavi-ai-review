# One controlled contextual-training pilot

27 September2026. Classic + Critic. Preparation, not paid-launch admission. Root owns implementation integration and any paid lifecycle; reviewers remain read-only. This replaces the deferred three-anchor recipe, without changing the model, benchmark or merit function.

## Question and intervention

Does replacing four ordinary translation replays of each of12 TRAIN passages with four contextual-expression tasks improve source-only translation beyond matched further ordinary training? The proposed contexts cover9works and3 related families, selected from TRAIN diagnostics and a bounded TRAIN census. No DEV/PAL correction supplies a label. The qualifications and limits in both proposal packets, both independent source reviews and `qualification-decision-v2.json` remain binding.

The candidate sees the complete source plus one unique selected expression and an explicit instruction to give only that expression's contextual Persian meaning. Its target is the exact reviewed published span or complete attributed occurrence gloss. The control sees the same parent passage with the unchanged ordinary-translation prompt and complete published Persian translation. These are task-and-target recipe differences; this is not an isolated causal test of linguistic labels or equal-token training. Short contextual targets must never be paired with a whole-passage translation instruction.

## Fixed exposure and optimization

Both arms start from the verified qualified Gemma4-31B step280 adapter on the same pinned base and NF4 configuration. Load it once for training, restore exact original trainable tensors before each arm, clear gradients and initialize a fresh optimizer/scheduler/RNG under seed3407. Neither arm resumes the finished historical schedule or learns from the other arm's updates.

Each arm has48 optimizer updates, microbatch1, accumulation16:768 example slots, comprising720 distinct ordinary TRAIN parents and48 designated slots. Select the regular parents by ascending SHA256 of `contextual-pilot-v1|3407|<train_id>`, excluding all12 anchor parents, taking the first720. Each update has15 regular examples followed by one designated parent. Preserve that exact common parent order with native sequential sampling, and separately verify delivered slots and completed updates.

Use packet indices0–11 as the first anchor cycle, reverse that order for cycle2, rotate the original order left by6 for cycle3, and reverse cycle3 for cycle4. Each anchor appears four times and has mean within-cycle position5.5. This balances position, not exact cumulative learning-rate dose under warmup. The same frozen schedule serves both arms; there is no permutation search.

Use the historical peak learning rate0.0001, AdamW with betas0.9/0.999, epsilon1e-8, weight decay0, gradient clipping1.0, and a fresh48-step linear schedule with2 warmup steps. Preserve LoRA rank16, alpha32, dropout0, existing trainable layers and NF4 double quantization/BF16 compute. No hyperparameter grid, new synthetic labels or automatic additional epochs. The48-step budget gives four contextual exposures per anchor and a measured approximately30-minute combined training estimate at prior18.21–18.80seconds/update; this is a conservative exploratory design choice, not an optimized recipe or guarantee of transfer.

Use native per-example mean supervised-token loss with microbatch1 and explicit `model_accepts_loss_kwargs=False`, no smoothing or custom reduction. The designated slot has6.25% of each update's example weight; each of its answer tokens has weight inversely proportional to its answer length. Terminators remain supervised. Candidate/control token totals differ:108694/110050 sequence tokens and28365/30085 supervised tokens. Auxiliary phrases are short; terminator fraction and changed per-token weight are part of the intervention. Do not compare the arms' training losses as translation merit.

## Fixed comparison and decision

Save both final adapters on the cloud, release training state, and evaluate both on the original BF16 base using the exact existing qualified plain DEV prompt: `dev_assisted.messages(row, 'plain', [])`. Check its24 rendered token hashes against the saved qualified plain run. Keep greedy decoding, seed42, no thinking,4096 output-token ceiling,1200-second per-case ceiling and the same EOS/cache policy. Alternate arm order within each case and preserve all48 first attempts. No reference answers reach the inference job. The original step280 result is a disclosed descriptive reference; the primary comparator is the newly trained matched control.

The unchanged uniform contract remains authoritative:15 whole translations and9 separate constrained cases; two fresh blinded AI reviewers; net accepted gain at least2 for both reviewers across at least2works; no increased critical count, accepted-to-critical transition, worse constrained critical error or new unsupported certainty. Missing/failed outputs remain visible and cannot shrink denominators. Both complete training arms and all48 recorded first attempts are required for an interpretable complete comparison; incomplete execution is not evidence for or against the training hypothesis. A failed improvement screen ends this recipe branch. Do not respond by automatically increasing epochs or trying mixtures. A null result does not reject contextual supervision in general.

If the candidate passes, run the unchanged PAL-REF40 regression comparison before considering delivery. That reused panel is not untouched confirmation. No local pretrained-model download occurs before satisfactory cloud quality. All semantic judgments remain provisional until specialist review.

## Cost and execution limits

Last observed funded credit isUSD15.82 at12:32:29UTC, not a fresh launch balance. No server is launched by this protocol. Plan one A100-large job that downloads the base once, trains the two arms sequentially and evaluates them after BF16 reload. At the last verified rateUSD0.041667/minute, a75-minute native timeout permitsUSD3.125025 of compute; allowUSD0.50 separately for delayed/other charges and cleanup. The resultingUSD3.625025 planning reservation is belowUSD3.65, not a provider billing guarantee. Refresh balance, rate, autorecharge state and active-job inventory before admission; require the entire reservation to be available.

Proposed time allocation:65minutes for setup, training and evaluation;5minutes reserved for export;5minutes for provider persistence confirmation and termination. Prior training throughput plus the earlier approximately17-minute48-output Gemma job suggests this may fit, but longer generations or setup can exhaust it. Preserve verified final arm artifacts and small partial evidence on failure, then stop; no automatic retry or recharge. The native timeout remains the outer control. Root must verify provider persistence before deliberate shutdown and recover only small records locally. Full implementation tests, exact source/package identities and independent paid-readiness review remain required.

## Evidence and remaining work

`numerical-check/` preserves the actual random tiny Gemma/LoRA CPU loss check: native equal-parent loss, gradients and one AdamW update exactly matched the manual reference; pooled-token reduction differed. This establishes the tested CPU reduction only. `token-census/` preserves exact local token reconstruction and exposure accounting. `TWO-ARM-READINESS.md` identifies existing helpers and the necessary small new entrypoint; its old-prompt recommendation was corrected by lead inspection to preserve the qualified plain condition.

Source qualification and scientific-design review are complete at the stated provisional level. Finish and independently check the small training core, exact tensor/RNG resets and native order. Then wire the existing checked cloud bootstrap/export and fixed BF16 evaluation, test failure persistence, freeze all launch identities and refresh live admission. Current code or documentation alone must not be reported as a successful cloud run or improved translation.
