# Qwen runtime preflight — metadata and source verification only

27 September 2026. **Native architecture support is present in the pinned Linux stack; the exact prescribed sampling policy still needs a small presence-penalty implementation and an execution canary.** No weights were downloaded, model inference performed, package installed, credential accessed or cloud job launched. The meaning rubric, merit function, DEV cases, evidence selection and adjudication policy remain unchanged for every model.

## Frozen model identity

Official public, ungated repository: `Qwen/Qwen3.6-27B`; immutable revision **`6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`**. Retrieved from the [official revision API](https://huggingface.co/api/models/Qwen/Qwen3.6-27B/revision/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9?blobs=true). The companion JSON records every metadata URL, byte count and computed SHA-256, plus the 15 shard identities supplied by the public API. **Shard checksums are publisher metadata, not locally verified weight bytes.** Eleven metadata/tokenizer/license files were read into memory, including the 12.8 MB tokenizer; no metadata snapshot directory or cache was created.

| Actual downloaded metadata | SHA-256 |
| --- | --- |
| `config.json` | `69db4eb7196bc8190813231b3018ca05d8c2e3abc7b1af19d55c157af44a9d9c` |
| `chat_template.jinja` | `e84f32a23fdda27689f868aa4a1a5621f41133e51a48d7f3efcbea2839574259` |
| `tokenizer_config.json` | `5186f0defcd7f232382c7f0aebcd2252d073bb921ab240e407b7ae8745d2b29b` |
| `tokenizer.json` | `5f9e4d4901a92b997e463c1f46055088b6cca5ca61a6522d1b9f64c4bb81cb42` |
| `generation_config.json` | `e70c136c1b78ddc1fb0905bac8e733a4dc448d4f852a5dd75143fffc70be550e` |
| `model.safetensors.index.json` | `a8ad2c26fb707ff8c245806315b03e3b4b74595528492423af5dae0ce39b4d9b` |

The config uses `qwen3_5` / `Qwen3_5ForConditionalGeneration`, with nested `qwen3_5_text`. It specifies BF16, hidden size5120, vocabulary248320, 64 layers (48 linear attention /16 full attention), 24 query heads, four KV heads, full-attention head dimension256, and context262144. The saved `transformers_version=4.57.1` is checkpoint metadata, **not evidence that 4.57.1 supports this model**. The index has language, vision and MTP parameter namespaces. [Pinned official config](https://huggingface.co/Qwen/Qwen3.6-27B/blob/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9/config.json).

## Existing runtime compatibility

The Linux lock pins Transformers5.13.1, Torch2.11.0+cu128, tokenizers0.22.2, huggingface-hub1.23.0 and Jinja3.1.6. Eight installed Transformers source files matched the official **v5.13.1** source bytes exactly, including configuration/modeling, auto mappings, weight conversion and generation/serving code. Native `Qwen3_5ForCausalLM` exists, AutoModelForCausalLM maps the VLM model type to it, and the conversion map removes the checkpoint's `language_model` prefix. The text class explicitly permits unused vision/MTP keys. No remote model code is required. [Native implementation](https://github.com/huggingface/transformers/blob/v5.13.1/src/transformers/models/qwen3_5/modeling_qwen3_5.py), [conversion mapping](https://github.com/huggingface/transformers/blob/v5.13.1/src/transformers/conversion_mapping.py).

The current Linux lock lacks the optional `flash-linear-attention` and `causal-conv1d` acceleration packages. Native code has Torch fallbacks; absence is not an architectural blocker, but speed and peak-memory behavior are unmeasured. Do not add kernels merely to pass a static preflight. The present Windows science environment contains the matching source packages but lacks `huggingface_hub`: an actual `from transformers import Qwen3_5ForCausalLM` canary failed with `ModuleNotFoundError`. This local environment cannot validate the complete Linux runtime; the Linux lock includes the missing dependency. No installation was attempted.

## Exact sampling policy and the concrete blocker

Preserve `do_sample=True`, temperature0.7, top_p0.8, top_k20, min_p0, repetition_penalty1.0, presence_penalty1.5 and seed42; `enable_thinking=False` belongs in `apply_chat_template`, not `generate`. The [official model card](https://huggingface.co/Qwen/Qwen3.6-27B) supplies this nonthinking recipe. All listed sampling controls except presence penalty are native generation settings in5.13.1.

**Presence penalty is not natively implemented by `generate`, and the5.13.1 HTTP serving handler explicitly rejects it.** Passing it as an unused generation attribute or omitting it would not reproduce the plan. Repetition penalty is a different operation and cannot substitute. [Pinned serving source](https://github.com/huggingface/transformers/blob/v5.13.1/src/transformers/cli/serving/chat_completion.py).

Lowest-change proposal: retain the Linux lock, use direct Transformers generation, and add one reviewed `LogitsProcessor` implementing `score[token] -= 1.5` once for each distinct token already generated in the current response. Exclude the prompt from this count, reset per case, do not multiply by occurrence frequency, and apply it before temperature/top-k/top-p. The native generation source merges custom processors before sampling warpers, so this is the appropriate extension point. This processor is **not implemented or execution-tested in this preflight**. Pin its exact semantics and source hash before use. Moving to vLLM/SGLang would provide a native serving penalty but requires another runtime/lock and is a larger change.

The pinned template was rendered directly with Jinja3.1.6 on synthetic messages: nonthinking correctly appends the empty `<think>…</think>` prefix before generation. This was a template-only check, not AutoTokenizer/model validation. Preserve the official generation EOS IDs **[248046,248044]** and pad ID **248044**; do not reuse Gemma EOS/pad IDs or override from the text-config EOS alone.

## Smallest loader path to canary

A dedicated Qwen inference runner can use `AutoTokenizer.from_pretrained(verified_local_snapshot, local_files_only=True, trust_remote_code=False)` and explicit `Qwen3_5ForCausalLM.from_pretrained` on that same snapshot with BF16, one GPU, safetensors, native eager attention and `output_loading_info=True`. Let its text-config class extract the nested config and its native mapping load `model.language_model.*`. Check every missing/mismatched language-model weight as a hard failure; record ignored vision/MTP keys. No Gemma adapter, processor, model constant or tokenizer may be reused.

Use the existing fixed source-only messages/evidence payload, the pinned Qwen template, explicit nonthinking mode, fresh model cache per case and `torch.inference_mode()`. Let Qwen create its own `DynamicCache(config=text_config)` rather than forcing Gemma cache settings. Generate only the final token logits (`logits_to_keep=1`), retain the fixed4096 output cap and deadline/finish-status reporting, and keep seed42/reset policy identical between plain and assisted cases. No reviewer/scorer changes are needed. This is a proposed API path based on matching source code, **not a successfully loaded checkpoint**.

Before48 real outputs, a bounded synthetic API canary must verify: complete dependency import; exact tokenizer/config hashes and special IDs; nonthinking prompt IDs; strict language-weight loading; prefill plus repeated cached decoding; presence-penalty arithmetic with repeated tokens/prompt-only tokens and its position before sampling warpers; fresh-request isolation; same-seed repeatability on the chosen hardware; EOS/cap/deadline outcome handling; and peak GPU memory/seconds per generated token at the actual longest source/evidence prompt. If an HTTP server is chosen instead, its endpoint must additionally prove all requested parameters are accepted and applied; the current Transformers serving endpoint fails that prerequisite.

## Memory estimate, not a measured fit

Official index tensor payload: **55,562,855,904 bytes =51.747 GiB**, including vision and MTP. Shard files total55,563,006,400 bytes including serialization overhead. Text-only loaded weights should be smaller, but exact live allocations have not been measured.

For batch1 BF16 full-attention KV, the real config implies `16 layers ×2 K/V ×4 heads ×256 dimensions ×2 bytes =65,536 bytes/token`: **0.5 GiB at8192 total tokens**, or1GiB at16384. A conservative FP32 linear recurrent-state calculation adds about144MiB plus a few MiB of convolution state; temporary tensors, logits, attention workspaces, allocator and CUDA overhead remain additional. A bounded batch1 run is plausibly within A10080 capacity with this ~52GiB checkpoint, but peak eager-prefill memory and Torch-fallback latency must be measured. Do not preallocate the advertised262K context: full-attention KV alone would then be16GiB. No performance or cost guarantee follows from these estimates.

**Preflight status: metadata/source checks passed; exact-policy execution readiness remains PARTIAL pending the presence processor and Linux canary.** Same merit function, case IDs and rubric remain mandatory across Gemma/Qwen; no score or scientific superiority claim is made here.

Full metadata/source evidence: `qwen-source-identity.json`, SHA256 `b0d6d51fe7603d4a955be4dec41b551100a4ca401b5d1d8a1a5a4c8d5427f8ce`.

## Presence processor implementation — 27 September 2026

`cloud_pilot/qwen_presence.py` now provides `GeneratedTokenPresencePenalty(prompt_length, penalty=1.5)`, a stateless callable for native `generate(logits_processor=[...])`. Use the initial `input_ids.shape[1]`, including padding, as the boundary. It subtracts the penalty once per distinct generated token in each row, leaves prompt-only tokens unchanged, and preserves score dtype. Constructor and tensor metadata checks reject invalid parameters, shapes, dtypes and devices. Torch scatter enforces generated-token bounds without a Python GPU synchronization; CUDA error reporting remains asynchronous. Prompt-token validity belongs to the tokenizer/model input boundary. Continuous batching is unsupported.

The rule and finite `[-2,2]` range were checked against official vLLM **v0.19.1** [penalty arithmetic](https://github.com/vllm-project/vllm/blob/v0.19.1/vllm/model_executor/layers/utils.py) and [sampling parameters](https://github.com/vllm-project/vllm/blob/v0.19.1/vllm/sampling_params.py). SHA256 of the retrieved source bytes: `67bc1e3c6983387005ee5a4e7ec9e7993650dcca524bfc67eb90a6a01714973a` and `8512e73c45a6d2f8015f2ca8d94c9fc9a05ca390d6206e2b387ad6550e9b014a`, respectively. The already verified Transformers5.13.1 source accepts this callable and merges custom processors before temperature/top-k/top-p. Do not pass an unsupported `presence_penalty` generation kwarg.

Six real CPU Torch2.11.0+cu128 tests passed: prompt exclusion, repeats, batch independence, fresh requests, distribution/ranking, temperature-order arithmetic, FP16/BF16/FP32/FP64, and invalid inputs. Exact command from the project root:

```powershell
& '[USER_HOME]/.venvs/codex-science/Scripts/python.exe' -B -m unittest cloud_pilot.test_qwen_presence -v
```

| Frozen helper | SHA256 |
| --- | --- |
| `cloud_pilot/qwen_presence.py` | `299e25706752946ff86b60af71d77758b77acc932abd3adcae7946b4cae6279e` |
| `cloud_pilot/test_qwen_presence.py` | `f914aea253d64986d95e4839ee9c970997b9afd12a3e9b69250356699bd9fbc4` |

**Helper arithmetic is execution-tested; native generation integration remains unverified.** A direct local `LogitsProcessorList` import still fails because `huggingface_hub` is absent. No source extraction or stub bypass was used. No GPU inference, model loading, packages, weights or cloud jobs were involved. The Linux API/model canary remains required before real outputs; earlier statements that the helper was unimplemented are superseded only by this narrow result.
