# Fixed comparison after qualified-data retraining

Frozen before the new model produces PAL-REF outputs. Lead: `/root`; independent protocol reviewer: `/root/final_external_judge`. The user requests the measured change first, followed by a broader strategy review before selecting another experiment.

## Conditions and identity

Use the unchanged forty-case PAL-REF v1 Pahlavi-to-Persian test, manifest SHA256 `a3932f7510f101376cc91c47bb23f3c9872656c41f563701fa3dcb2b6c89a5e8`, frozen rubric and `cloud_pilot/score_palref_fa.py`. No rubric, reference, prompt, decoding or denominator changes. No best-of sampling, checkpoint selection by quality, or regeneration of unsuccessful cases.

Previous predictions are cached in `experiments/palref-v1/trained-20260927/predictions.jsonl`, SHA256 `fec20ebde33897c7103b7427d3a00ca2ca8f51b415a55b59db5f9ec1a4473396`. Keep that run, its reviews and its historical 15/40 accepted result untouched. Obtain new predictions only from the final 280-step adapter, with cloud manifest identity and complete SHA recovery verified before review. Tensors remain remote.

Check the same 21 inference fields listed in the previous `comparability.json`, exact forty IDs, rendered input-token counts, tokenizer and base-file hashes. Disclose differing bundle/train/adapter identities. Old training used 2,484 rows and312 updates; new training uses2,237 rows and280 updates under the same two-epoch recipe. Filtering changes both examples and schedule length. The comparison tests that combined condition; it cannot isolate the effect of any particular excluded label.

## Blind assessment

Use two fresh agents without conversation history. Each independently assesses all80 outputs: both models across all40 passages. Hide model names, old/new labels, training details, archived scores and other reviewers' judgments. Give only pseudonymous output IDs, exact output hashes/text, input, frozen reference/meaning checks and frozen rubric. Assign independent deterministic shuffled orders and record the mappings outside reviewer packets. Do not invite relative preference; each output receives its own unchanged rubric judgment.

Each reviewer may process fixed manageable batches, but coverage must total80 exact unique output identities. Require the frozen schema, all categories, both meaning checks, precise output spans and stated reasons. Preserve uncertainty, abstention and operational failures. Adverse judgment spans must match actual output. Do not revise ratings after revealing model identities or aggregate results.

After validating coverage, schema and hashes, decode IDs and create four scoring copies: reviewerA/previous, reviewerA/qualified, reviewerB/previous, reviewerB/qualified. Each keeps the genuine inference provenance and records the actual reviewer ID, type `ai` and status `provisional_single_review`. Execute the unchanged scorer separately for each. Do not invent a pooled score or expert consensus. Keep raw cloud run metadata and archived historical reviews intact.

## Reporting and next decision

Report the historical original-model5/40 and previous-trained15/40 with their original single-review caveat. Separately report each fresh reviewer's paired previous-versus-qualified acceptance and critical-error fractions, percentage-point changes, newly accepted cases, regressions and per-work counts. Denominator remains40 even for failures or uncertainty. Show agreement and disagreement between the two reviewers, including whether the direction of change agrees. Same-family AI agreement is provisional evidence, not independent specialist certification.

Disclose the small fixed sample, five-work coverage, known old-training near-overlap precautions, unexcluded semantic parallels or foundation-model exposure, and lack of specialist validation. This previously evaluated fixed test is now a regression benchmark, not a fresh unseen confirmation. Do not tune candidates from its individual failures; use DEV. No general accuracy, causal or laptop-quality claim follows from these scores alone. The prior instruction diagnostic used a different DEV sample and must not be compared numerically as if it were this test.

Only after results are recovered and compared, review next-step strategy: which error types persist, data adequacy and uncertain labels, isolated words versus compositions versus new inscriptions, source-evidence assistance, benchmark limitations and need for independent specialist assessment, suitability of the current model, remaining USD25 budget, and practical8GB local inference. Keep the previous assisted-inference proposal pending; choose a further experiment only if the evidence supports it.

Independent reviewer re-executed the archived scorer and confirmed its existing counts. The reviewer endorsed two complete independent reviews, while noting fatigue/context carryover and the need to preserve separate scores. Runtime execution of this new review protocol remains pending the new outputs.
