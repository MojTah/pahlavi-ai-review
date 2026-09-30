# Model identities and executed training recipes

Updated 30 September 2026 for static scientific and implementation review. This document describes saved experiments; it does not authorize a new run. No model weights were downloaded, loaded or transferred to prepare it. Weights remain in the project's cloud storage. The public review copy contains descriptions and evidence, not a runnable model distribution; some linked corpus files belong only to the separate research archive.

## Identity and checkpoint lineage

Current reuse restriction: the unchanged v1 projection remains blocked by the [full pretraining review](experiments/full-pretraining-audit-20260929/REPORT.md). Its [corrected v2 successor](experiments/training-ready-v2-20260929/README.md) completed an authorized96-update repair comparison from retained step280, followed by24 source-only DEV outputs. [Recovery](experiments/training-ready-v2-20260929/recovery.json) verifies the small evidence files and provider inventory. Execution completion does not establish semantic improvement or authorize another run.

| System | Frozen identity | Executed lineage |
|---|---|---|
| Gemma original | [`google/gemma-4-31B-it`](https://huggingface.co/google/gemma-4-31B-it), revision `842da3794eaa0b77d5f08bae87a17459d91ff475`; `Gemma4ForConditionalGeneration` | Pinned pretrained base, without the project's adapter. |
| First Gemma adapter, 26–27 September | Same base; final `checkpoint-312` | Fresh LoRA on the original 2,484-row training set, two epochs. |
| Qualified Gemma, 27 September | Same base; final `checkpoint-280` | **Fresh** LoRA on 2,237 retained rows, two epochs; not a continuation of step312. The fresh step20 canary resumed its own optimizer/scheduler/RNG state through step280. |
| Contextual branches, 27 September | Qualified step280 plus separate control/candidate adapters | Each branch starts from the same step280 state and receives 48 updates/768 ordered slots with fresh optimizer, scheduler and RNG. They are siblings, not successive stages of the mixed run. |
| NLLB, 28 September | [`facebook/nllb-200-distilled-1.3B`](https://huggingface.co/facebook/nllb-200-distilled-1.3B), revision `7be3e24664b38ce1cac29b8aeed6911aa0cf0576` | Separate full-model adaptation on the 2,237 qualified pairs. Initialized baseline, then step20 canary and exact continuation through step700. No Gemma adapter is involved. |
| Mixed Gemma, 29 September | Qualified step280 plus 96 new updates | Fresh optimizer/scheduler on 1,536 selected examples; the first20 updates belong to the same96-update schedule. It does not inherit the contextual candidate. |
| Corrected-v2 mixed Gemma, 29 September; reviewed30 September | Qualified step280 plus a separate96-update continuation | Same recipe and1,536-slot budget, using corrected supervision. It starts from step280, not from the previous mixed96 adapter. Eleven selected IDs change: four canonical remaps and seven replacements. |

Sources: [first adapter provenance](experiments/palref-v1/trained-20260927/provenance.json), [qualified training provenance](experiments/retrain-qualified-20260927/continuation/training/provenance.json), [qualified completion audit](experiments/retrain-qualified-20260927/CONTINUATION-RESULT-AUDIT.md), [contextual pilot](experiments/contextual-supervision-20260927/PILOT.md), [NLLB saved run](experiments/nllb-supervised-20260928/continue/recovered/nllb/run.json), [mixed saved run](experiments/mixed-supervision-20260929/recovered/mixed/training/run.json).

The original 2,484 rows and qualified 2,237 rows are different corpus versions: 247 rows were excluded, with no source/target/token mutation in the retained subset. The qualified payload SHA256 is `15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc`. The preparation code distinguishes original tokenized and qualified hashes explicitly: [bundle.py](cloud_pilot/bundle.py). Qualification remains provisional AI/source review, not specialist certification.

## Gemma representation and adaptation

- Training uses 4-bit NF4 with double quantization and BF16 computation. Only language-model LoRA weights train; vision components and the original base parameters remain frozen. Gradient checkpointing uses `use_reentrant=False`.
- LoRA: rank16, alpha32, dropout0, bias `none`, task `CAUSAL_LM`; no DoRA or RSLoRA. Targets are `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj` **only** under `model.language_model.layers.<index>`. See [runtime](cloud_pilot/runtime.py) and [saved mixed adapter configuration](experiments/mixed-supervision-20260929/recovered/mixed/training/adapter/adapter_config.json).
- Training seed3407; microbatch1; gradient accumulation16; maximum sequence length2,048. Original and qualified runs use AdamW (`adamw_torch`), learning rate0.0001, linear schedule, warmup ratio0.03, two epochs and checkpoint saves every20updates. Their canary callback stops at20 without replacing the full two-epoch schedule.
- The original/qualified runner delegates sampling and unspecified optimizer details to the pinned Transformers `Trainer`/`TrainingArguments`; it does not freeze a consumed-ID stream like the mixed runner. Exact historical replay should use the saved training arguments and runtime revision, rather than silently borrowing the later mixed settings. This document does not invent unrecorded defaults or a historical exact permutation.
- The tokenizer, tokenizer configuration and chat template are pinned to the base snapshot. SHA256: tokenizer `cc8d3a0ce36466ccc1278bf987df5f71db1719b9ca6b4118264f45cb627bfe0f`; tokenizer configuration `9f4fec4b1dc6ecddf8f4a92e9caea5971c0e67d81309f3f9066a2bee8c362633`; chat template `ae53464bf3be25802b3a5b37def7fd89667067d7577049b3b2d74c4d8de4c6d4`.
- Text is scholarly Latin transcription. The historical instruction in [bundle.py](cloud_pilot/bundle.py) asks for Farsi only and preservation of negation, participants, names, numbers and uncertainty. The template uses `enable_thinking=False`; the answer ends with `<turn|>\n`.
- Prompt labels are `-100`; only the answer and terminator are supervised. Padding has attention0 and label`-100`; unpadded records have attention1. Prefix/answer boundaries and exact answer decoding are checked. The original/qualified runner uses the pinned model/Trainer causal loss without a custom corpus/task weighting layer. See [runtime training path](cloud_pilot/runtime.py) and [bundle construction](cloud_pilot/bundle.py).

## Mixed continuation: actual dose, not full-pool training

The release has10,152 typed records; preparation collapses one exact duplicate to10,151 pool records. **Only1,536 selected records were consumed**, comprising1,152 historical pairs and384 auxiliary records. Selection uses SHA256 of `3407:id`, source/witness-group round robin without replacement, and fixed task quotas. The training runner verifies the exact sequential ID stream; it does not shuffle it.

| Task | Selected records | Supervised tokens |
|---|---:|---:|
| Historical Persian translation | 1,152 | 58,105 |
| Persian lexical inventories | 96 | 783 |
| CPD English structured senses | 64 | 2,046 |
| Manichaean Middle Persian English inventories | 32 | 299 |
| Persian pedagogy/conditioned grammar | 127 | 651 |
| English documentary spans | 57 | 5,378 |
| Persian inscription spans | 4 | 51 |
| English edition spans | 4 | 143 |

Every update contains12 historical +2 lexical +2 other auxiliary examples, in that order. AdamW has learning rate0.0001, betas0.9/0.999, epsilon1e-8, weight decay0, maximum gradient norm1, linear decay and4warmup updates. The saved run confirms96updates,1,536consumed slots and a fresh optimizer.

Loss is the **mean of per-example supervised-token means**, giving nominal task-group example weights75%/12.5%/12.5%; it is not one pooled token-normalized objective. Equal example weights do not imply equal gradient magnitudes. Actual selected supervision totals67,456tokens across258,988sequence tokens. Source: [data manifest](experiments/mixed-supervision-20260929/data-manifest.json), [preparation](experiments/mixed-supervision-20260929/prepare.py), [trainer](cloud_pilot/mixed_train.py).

Auxiliary instructions preserve the task distinction: complete lexical inventories, CPD recursive sense JSON, conditioned grammar, or bounded translation spans. English targets stay English. CPD targets retain numbering, nested text/tails, component roles and attributes. Historical rows preserve the original token arrays; new rows serialize only selected learning fields and context, not raw provenance or neighboring evidence. No rows are truncated. These choices do not establish that dictionary-inventory recall transfers to contextual Persian translation.

## Corrected-v2 continuation: executed dose

The corrected pool contains9,973 unique inputs representing10,145 original records, with seven holds. The new run again consumes1,536examples:1,152historical,96Persian lexical,64CPD English,32MMP English,131pedagogy,53documentary,4distinct inscription pairs and4edition spans. It retains the same12:2:2 equal-example mixture,96updates, learning rate0.0001, warmup4 and fresh optimizer from qualified step280. Changes include consolidated complete sense inventories, scoped apparatus/typography corrections, and the declared parent substitutions. This is a combined correction package, not an isolated dictionary-cleanup experiment.

The selected corpus has274,703 total sequence tokens and68,724 supervised tokens. [Frozen manifest](experiments/training-ready-v2-20260929/data-manifest.json), [executed training receipt](experiments/training-ready-v2-20260929/recovered/mixed/training/run.json), [evaluation outputs](experiments/training-ready-v2-20260929/recovered/mixed/evaluation/predictions.jsonl). The final adapter file SHA256 is `c2305fc9cdc1fb99a346e58c92ae2ba1faa030ff6961bf0be1452f75006a8df0`, recorded server-side and bound into the recovered export manifest. Weight bytes remain cloud-only; local recovery did not recompute their hash. The comparison preserves the fixed source-only DEV protocol and separate reviewers.

## NLLB: full-model recipe and token-normalized loss

All model parameters train in FP32 with BF16 autocast; this is not LoRA or 4-bit training. Five epochs expose each of2,237parents five times:11,185parent exposures in700updates. Each epoch shuffles indices with Python `random.Random(3407 + epoch)`. Groups contain16parents, except the final13-parent group of each epoch; microbatches contain at most4.

AdamW uses learning rate3e-5, betas0.9/0.999, epsilon1e-8, weight decay0.01 except biases/norms (0), gradient clipping1.0,42warmup updates and linear decay to zero at update700. Label smoothing is0. Cross-entropy sums over nonpadding target tokens and divides by their **total across the complete optimizer update**, not by each microbatch separately. Padding labels are`-100`; decoder inputs use `shift_tokens_right`. See [nllb_train.py](cloud_pilot/nllb_train.py).

The prepared tokenizer preserves original IDs/merges/normalizer and adds eight TRAIN-observed missing characters plus `pal_Latn`. Two named reserved tokens represent original model rows256204–256205. Final vocabulary size256215; `pal_Latn`=256214 and `pes_Arab`=256053. New character embeddings initialize from the mean of original non-special rows; the source tag initializes from the mean of202original language-tag rows. Original rows and tied encoder/decoder/output embeddings are checked. This makes the initialized baseline an explicitly adapted system, not untouched stock NLLB.

Source and target are separate sequences, each language-tag-prefixed and EOS-terminated. No truncation or unknown tokens are admitted; observed maxima are407TRAIN-source,341TRAIN-target and269DEV-source tokens, all below the declared512limit. The additions were selected using TRAIN, not DEV references. See [tokenizer evidence](experiments/nllb-feasibility-20260928/README.md), [prepared tokenizer manifest](experiments/nllb-feasibility-20260928/prepared-tokenizer-manifest.json) and [training plan](experiments/nllb-supervised-20260928/PLAN.md).

## Saved weight identities and verification limits

These are SHA256 **file hashes recorded in saved evidence**, not hashes recomputed from current local weights for this document. Tensor-content digests in training logs are a different identity and must not be substituted for file hashes.

| Artifact | Recorded SHA256 |
|---|---|
| Gemma base shard1 | `eeef8791537bc04f110967c513149e037d2a9ae97d49add7291ebfa62806bbfa` |
| Gemma base shard2 | `018912220f559f7025d60333e0996183cd538aa77ad6f4988a89ce47be681f10` |
| First step312 adapter | `e329333a79a30e82dfad7a751939afa71529800570fb6f8b0cfac78427ec2827` |
| Qualified step280 adapter | `a51bcd02c6077bcec400c1f342ede3205f260e419ed4f9e3ad0f4338a7e4afdf` |
| Mixed final adapter | `f01d10058f26c1fc6fc212820b183e42d033fed0b959d200a87befa3d142cbca` |
| NLLB upstream `pytorch_model.bin` | `7e40f838a5aad3d60e9254632ab876bda44340386ca7ebad3e099db7432b04e1` |
| NLLB step700 shard1 | `4fdcd06144599b30fbc6df5a0921bbf025346caba10e6083ea33dd1e54c2f812` |
| NLLB step700 shard2 | `d3a4c0a8f26cdab1fc109a5eb974a6c256ff66ef01c4a7dc71810ee45875ba82` |

Bindings: [Gemma base provenance](experiments/mixed-supervision-20260929/recovered/base-provenance.json), [first adapter evaluation](experiments/palref-v1/trained-20260927/run.json), [qualified manifest](experiments/retrain-qualified-20260927/continuation/manifest.json), [mixed training record](experiments/mixed-supervision-20260929/recovered/mixed/training/run.json), [NLLB final manifest](experiments/nllb-supervised-20260928/continue/recovered/manifest.json). The first adapter had historical local verification before its local copies were removed; see [dated report](experiments/palref-v1/trained-20260927/REPORT.md). Qualified/mixed/final-NLLB weight identities are remote-run manifest evidence; recovering small metadata does not independently rehash those weight files locally.

## Generation and interpretation

Gemma PAL40 and the later plain DEV24 comparisons reload the original BF16 base plus the selected adapter, with greedy decoding, seed42, thinking disabled and4,096new-token ceiling. This inference precision differs from NF4 training. Exact prompts/token identities are recorded in the run evidence; training-style prompts and evaluator prompts are not interchangeable. Mixed DEV uses the existing `dev_assisted.messages(row, 'plain', [])` protocol with no retrieval examples.

NLLB uses source-only input, greedy beam1, no sampling, Persian forced BOS256053, suppression of reserved IDs256204/256205 and512new-token ceiling. Initialized/trained outputs use the same rule. Preserve capped/error first attempts; do not replace them or remove them from denominators. These system comparisons change model, adaptation, representation and optimization, so they do not isolate architecture.

Retained reference is qualified Gemma step280. Neither the contextual candidate, trained NLLB nor mixed continuation passed its specified promotion conditions. These are bounded negative results, not proof that their entire model or supervision families cannot work. PAL40, DEV15whole/9constrained, familiar TRAIN recall and teacher-forced NLL are separate assessments; repeated panels are development/regression evidence. Read the respective [contextual report](experiments/contextual-supervision-20260927/REPORT.md), [NLLB report](experiments/nllb-supervised-20260928/REPORT.md) and [mixed report](experiments/mixed-supervision-20260929/REPORT.md).

## Reproduction entrypoints and remaining requirements

Saved Gemma runtime: Linux x86_64, Python3.12.3, A100-SXM4-80GB; torch2.11.0+cu128, Transformers5.13.1, PEFT0.21.0, bitsandbytes0.50.2, Accelerate1.14.0, tokenizers0.22.2, huggingface-hub1.23.0, safetensors0.8.0. Use [requirements](cloud_pilot/requirements.in), [hash lock](cloud_pilot/requirements-linux.lock) and each saved environment record; do not assume another installation's defaults reproduce these runs.

The following are **worker command templates**, preserving actual flags while replacing environment-specific paths/timestamps. They are documentation, not instructions to launch jobs or fetch weights. Full package bindings, deadlines, verified inputs and authorized model access are prerequisites.

```text
python -u runtime.py train --contract CONTRACT --bundle BUNDLE --base BASE --output OUTPUT --deadline-utc UTC --max-steps 20
python -u runtime.py train --contract CONTRACT --bundle BUNDLE --base BASE --output OUTPUT --deadline-utc UTC --full --resume CHECKPOINT20
python -u mixed_run.py --bundle BUNDLE --base BASE --tokenizer TOKENIZER --adapter QUALIFIED_ADAPTER --train TRAIN --data-manifest MANIFEST --settings SETTINGS --inputs DEV_INPUTS --output OUTPUT --deadline-utc UTC
python -u nllb_train.py --package PACKAGE --output OUTPUT --deadline MONOTONIC_DEADLINE --program-start MONOTONIC_START
python -u nllb_train.py --package PACKAGE --output OUTPUT --deadline MONOTONIC_DEADLINE --program-start MONOTONIC_START --resume CANARY
```

Exact assembly/worker invocation is in [hf_train.py](cloud_pilot/hf_train.py), [hf_continue.py](cloud_pilot/hf_continue.py), [hf_mixed.py](cloud_pilot/hf_mixed.py) and [hf_nllb.py](cloud_pilot/hf_nllb.py). Historical package manifests and runner hashes, not the current generic contract's readiness/status text, identify what actually executed.

Static review needs no weights or download: inspect code, configurations, selection/census, saved outputs and review evidence. Real execution reproduction additionally needs authorized frozen source data, the exact tokenizer/package and authorized base/adapter or complete NLLB checkpoint files, followed by independent hash verification and compatible compute. This document makes no claim of current local-weight availability, bitwise GPU reproducibility, expert-certified translation or successful8GB laptop inference.
