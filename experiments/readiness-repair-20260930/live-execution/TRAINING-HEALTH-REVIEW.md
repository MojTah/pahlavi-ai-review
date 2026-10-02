# Prior corrected96 training-health review

30 September 2026. Independent reviewer `/root/astra_runtime_plan_recheck`. **The saved, hash-bound evidence supports that corrected96 really underwent the intended adapter training and completed its 96-step schedule. No missing-training or nonfinite-training failure was found. This does not establish good translation quality.**

The training job was `6abc15b8031314b696342162`, run prefix `mixed-supervision/157531204582c50f2d8f73aaa76ce8ac`. Its provider lifecycle lasted 2,854.201 seconds (47 minutes 34 seconds); actual recorded training lasted 1,819.185 seconds (30 minutes 19 seconds). The later job `6abd2a1d404719ba376138e8` was prepared as inference-only on already trained checkpoints. Its shorter runtime therefore does not indicate skipped training; root is separately verifying its persisted inference outputs.

## What was independently checked locally

Rehashed recovered `driver.log`, `mixed/run.json`, `mixed/training/run.json`, `mixed/training/progress.jsonl` and `data-manifest.json` against their persisted manifest entries, checking both size and SHA-256. All matched. The manifest itself hashes to `4ccf49623f1753efffc922a97f882cdbadbfcecabbda5ebccbe30e9f3e084dac`, matching the reviewed candidate binding. No model weights were read or downloaded and no authenticated API was called.

- The progress file contains exactly 96 sequential steps, 1 through 96, with increasing elapsed time. Final receipt and progress agree on 96 completed steps and 1,536 slots. The 1,536 ordered IDs exactly match the hash-verified local training file. Intermediate slot counters include collator read-ahead (for example 17 at step1); the final schedule is exactly 1,536, not an additional example or update.
- Parsed all 96 logged loss/gradient-norm/learning-rate records. Every value is finite. Logged loss ranges from 0.3985 to 1.518; gradient norm from 3.162 to 30.22. The recipe specifies gradient clipping at 1.0; a larger reported pre-clipping norm is not itself a failed clip or numerical error. Final full-precision mean training loss in the receipt is 0.8258679937571287.
- Mean logged loss for the first16 steps is 1.06195625 and for the last16 is 0.6944375. This is a descriptive decline across different batches, not a controlled before/after evaluation or proof of acquisition. Individual losses are not monotonic.
- A fresh AdamW optimizer/scheduler started at step0; maximum learning rate was 0.0001 with four warmup steps, linear decay, batch size1 and accumulation16. The first logged rate is zero during warmup, so **96 completed optimizer steps does not imply 96 separately verified nonzero parameter changes**. There is strong direct evidence of nonzero overall learning updates below.

## Parameter changes and numerical checks

The starting trainable-tensor digest is `df16670b3b7bfc24da89c91724849d297b4b0a1db6298f1e8be16d1a62a53014`; step20 is `dd462d883eb796dd24e070aa31501594416b7b7cd59a2b44d4232d587f785588`; final is `440341d9890ddf4f21d1189aaf8d8914671b839002a565011e6182ef85680ea9`. These are three distinct recorded tensor states. Separately, retained step280's adapter-file hash is `a51bcd02c6077bcec400c1f342ede3205f260e419ed4f9e3ad0f4338a7e4afdf`, whereas corrected96's final file hash is `c2305fc9cdc1fb99a346e58c92ae2ba1faa030ff6961bf0be1452f75006a8df0`. Tensor digests and serialized-file hashes are different identities and are not compared with one another.

The recorded numerical canary passed: native and manually computed masked loss both equal 2.3988394737243652 on a 1,144-token example, using BF16 autocast and non-reentrant gradient checkpointing. That canary performs zero optimizer updates; it tests numerical/masking consistency, while the subsequent96-step records establish training. The hash-matching training runner enforces finite starting/updated adapter tensors, finite nonzero adapter gradients before each optimizer step, no gradients on frozen parameters, finite logged/final loss, exact consumed order, unchanged model buffers and changed final adapter digest before declaring completion.

This was LoRA adapter continuation from retained step280, with the base model quantized as NF4 and BF16 computation; it was not full-parameter retraining of all31B weights. The fresh optimizer is intentional and recorded. The new acquisition evaluation uses BF16 loading, so its results must retain the known training/evaluation precision caveat.

## Mask and exposure check

Independently checked the exact local training file (`22266b73d3a0f3c697aa4ced00f32d07e4d0198c11d36507778d4b6084a3ac59`): all1,536 rows have a nonempty prompt and supervised suffix, every prompt label is `-100`, every supervised label equals its corresponding input token, and every attention mask is the correct all-ones length. Totals are274,703 sequence tokens and68,724 supervised tokens; maximum selected length is1,144, below the2,048 admission ceiling. The saved data audit records zero truncated rows, unknown tokens and unresolved prompt collisions. I did not retokenize the full pool or re-adjudicate its linguistic truth.

The available corrected pool contains9,973 unique prompts; this pilot used1,536 selected slots, not the entire pool. Absence of truncation or mask errors cannot compensate for limited exposure, imperfect supervision or a poor optimization recipe.

## Limits and conclusion

The review revalidates persisted logs, metadata, token arrays and their identity bindings. Actual adapter tensor bytes were not independently rehashed locally; weights remain cloud-only, with saved server hashes and earlier remote size/commitment evidence. The runtime runner's source hash matches the training receipt, tying its guard logic to the recorded run. This is strong execution evidence, not a new GPU replay or retained optimizer-state audit. The runner intentionally did not save resumable optimizer checkpoints; the step20/final artifacts are adapters.

Training completed technically, but the earlier matched translation comparison still accepted only2/15 passages versus1/15 for retained step280 and failed the unchanged improvement screen. Finite loss, parameter changes and completed steps establish that training happened; they do not establish useful generalization, philological correctness or a reason to train again automatically. Keep step280 as the retained reference until substantive evaluation supports another decision.
