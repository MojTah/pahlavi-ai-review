# Trained model versus original PAL-REF baseline

Current local cleanup: the partial base, transfer cache and both final-adapter copies were removed at the user's request. Cloud originals and all small result/verification records remain. The local checks below are historical checks performed before deletion.

## User hold on local downloads

The user said not to download yet. The Q8 base download was stopped immediately and no matching downloader process remained. Only **41,943,040 bytes (about 42 MB) of 32,635,676,448 bytes** reached the computer; the complete base model is absent. Preserve this partial. The user requires satisfactory cloud results before any model download to the computer. Current 15/40 accepted with 10 critical errors does not satisfy that gate; no further local model downloads or inference should proceed yet. The complete trained PEFT adapter (489,840,816 bytes) and converted F32 adapter (489,774,304 bytes) had already been saved and verified. No full model has been run locally. The cloud training and both fixed-test evaluations are already complete; all cloud jobs are off.

The fixed 40-case Pahlavi-to-Persian test shows a provisional improvement after training: **15 accepted translations (37.5%), up from 5 (12.5%)**. Critical errors fell from 14 to 10. This remains an unreliable translator for unchecked use; it is a useful training result, not a qualified decipherment system.

| Judgment | Original model | Trained model |
| --- | ---: | ---: |
| Accepted | 5 / 40 (12.5%) | 15 / 40 (37.5%) |
| Meaning error | 20 | 13 |
| Critical error | 14 / 40 (35%) | 10 / 40 (25%) |
| Uncertain | 1 | 2 |
| Abstention / timeout / execution error | 0 | 0 |

Twelve previously unaccepted cases became accepted; two previously accepted cases became meaning errors (030 and 031). Three remained accepted. Gains are uneven across works: accepted counts changed from 1 to 3 of 8 for work 104, stayed 0 of 4 for 110, rose from 0 to 6 of 10 for 116, stayed 3 of 10 for 130, and rose from 1 to 3 of 8 for 132. The paired transitions are preserved in `comparison.json`.

Both runs used the same frozen inputs, source-only prompt, original model revision, BF16 base, tokenizer/template, runtime, greedy seed 42, fresh context and 4096-token/1200-second limits. The model-condition difference is the trained LoRA adapter. All forty outputs completed; none reached the token cap. `comparability.json` records the matching fields. No benchmark definitions, reference answers, scoring rules, prompts or training examples were changed in response to these results.

## Evidence and limits

- Model: `google/gemma-4-31B-it`, revision `842da3794eaa0b77d5f08bae87a17459d91ff475`; 2,484 training rows, fixed two-epoch schedule, 312 optimizer steps, rank-16 LoRA.
- Training and final inference actually completed in job `6ab85fc76b030d633f697326`. The server was deliberately stopped after verifying 29 stored artifacts, including the final adapter and complete step-312 optimizer checkpoint. CANCELED denotes that planned post-export shutdown.
- Conservative cumulative compute estimate: **USD 6.1898 of the funded USD 10**, not a finalized invoice. All jobs were verified terminal. No top-up or further paid job was launched.
- The manifest and 26 small artifacts were downloaded and independently SHA-verified; the final 489,840,816-byte PEFT adapter was subsequently recovered and SHA-verified too. The duplicate checkpoint adapter and large optimizer file remain remote; no claim of full local checkpoint recovery is made.
- Original raw inference provenance remains unchanged under `resources/local/hf-continuation-downloaded-20260927/`. The reviewed run adds reviewer metadata only. Final adapter SHA: `e329333a79a30e82dfad7a751939afa71529800570fb6f8b0cfac78427ec2827`.
- Separate fresh AI reviewers assessed the original and trained outputs without model identity or the other score, using the same instructions, published references and frozen rubric. These single reviews are provisional, subject to reviewer variability, and **not specialist-certified accuracy**. Uncertain trained cases are 011 (merit versus reward) and 026 (Turan versus Turkestan). Published-text exposure during foundation pretraining remains unknown.
- Reproduce aggregation: `resources/local/hf-client-venv/Scripts/python.exe -X utf8 cloud_pilot/score_palref_fa.py experiments/palref-v1/trained-20260927`. The unchanged scorer verifies the complete benchmark and scores only its forty `pal>fa` cases.

## Local delivery and next decision

The final adapter was converted to F32 GGUF and all **820 tensors / 122,429,440 values matched bit-for-bit**, with matching rank and alpha. Source identity and conversion proof are recorded in `local-adapter-verification.json`. Conversion is not proof of native loading, speed or translation quality.

The next step is to recover the existing Q8 base, verify its full hash, and run the prepared bounded local load/tokenizer/timing check followed by the same fixed test. The 8 GB laptop path is still unverified. Keep the cloud off while transferring and checking locally. Further training decisions must use separate development evidence and training-data quality, not these frozen test failures; do not spend the remaining credit merely to exhaust it.
