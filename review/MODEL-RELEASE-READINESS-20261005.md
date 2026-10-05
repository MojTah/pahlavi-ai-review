# Exact retained adapter publication

5 October 2026. State: **PUBLISHED**. The owner explicitly approved using the existing Hugging Face credential to recover and publicly publish only this exact retained adapter. The tensor's size and SHA256 now match saved provenance. No base weights, inference, training, paid job, credential change or bucket/GitHub visibility change was performed.

| Identity | Verified value |
| --- | --- |
| Source bucket | `Mojionix/pahlavi-pilot` |
| Object | `continuations/1ae0f16dae9c4dffa36d15a24345fded/training/adapter/adapter_model.safetensors` |
| Bytes | 489,840,816 |
| SHA256 | `a51bcd02c6077bcec400c1f342ede3205f260e419ed4f9e3ad0f4338a7e4afdf` |
| Base | `google/gemma-4-31B-it` |
| Revision | `842da3794eaa0b77d5f08bae87a17459d91ff475` |

The first native Xet transfer failed with Windows socket/DNS errors; the escalated retry was stopped after the same lack of progress. Both task-owned partial files were retained privately. Direct HTTPS recovery of the same named object succeeded; the hub credential was removed for the signed CDN redirect. Credential values, signed URLs, account responses and downloader logs are excluded from the public snapshot.

[Release assets](https://github.com/MojTah/pahlavi-ai-review/releases/tag/gemma-step280-research-v1): unchanged `adapter_model.safetensors` and `gemma-step280-metadata.zip`. The metadata ZIP contains the portable config, original archival config/card, current model card, Apache2.0 license/NOTICE, provenance and SHA256SUMS. Only two configuration fields changed: public base ID and revision. See [model package](../models/gemma-step280/README.md).

The pinned upstream public Gemma4 inventory contains no separate LICENSE/NOTICE; its README links [Google's Apache2.0 license](https://ai.google.dev/gemma/docs/gemma_4_license) and credits Google DeepMind. The package includes the full license, attribution and prominent adaptation/configuration notices. It makes no blanket open-license claim for third-party training/source text.

Verification: actual streaming binary SHA256 and size; safetensors header/dtypes/contiguous offset bounds; exact original metadata hashes; exactly two changed config fields; ZIP byte parity; publication manifest and Git/remote checks. A full model load was not exercised. The CUDA loading example requires the separately obtained 62.5 GB base and substantial memory. Semantic ratings are provisional; latest fixed screens failed and identical controls reveal rating variability. Full data/retraining reproduction remains incomplete; see [data access](DATA-ACCESS.md) and [omissions](OMISSIONS.json).

Publication receipt: [PUBLICATION-20261005.json](PUBLICATION-20261005.json) verifies the release-target commit, complete Git blob inventory, anonymous raw reads, both GitHub whole-file SHA256 digests, metadata ZIP byte parity and anonymous adapter range access. This final documentation checkpoint is verified separately after its push.
