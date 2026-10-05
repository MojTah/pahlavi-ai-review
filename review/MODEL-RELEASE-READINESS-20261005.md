# Retained adapter: exact publication preparation

The actual Gemma step280 tensor is absent locally and is not included in this GitHub update. Local files named like model weights inside test trees are fixtures.

| Identity | Saved value |
| --- | --- |
| Private bucket | `Mojionix/pahlavi-pilot` |
| Object | `continuations/1ae0f16dae9c4dffa36d15a24345fded/training/adapter/adapter_model.safetensors` |
| Bytes | 489,840,816 |
| SHA256 | `a51bcd02c6077bcec400c1f342ede3205f260e419ed4f9e3ad0f4338a7e4afdf` |
| Base model | `google/gemma-4-31B-it` |
| Pinned revision | `842da3794eaa0b77d5f08bae87a17459d91ff475` |

Identity comes from saved continuation provenance, manifest and volume specifications, not a live private-bucket read. Matching local adapter config/README hashes were independently checked. The archival config references a temporary server base path with `revision:null`; its README has an unresolved license placeholder. Preserve those originals and identify any usable release config separately.

[Google's Gemma 4 license](https://ai.google.dev/gemma/docs/gemma_4_license) is Apache 2.0; the older custom Gemma terms exclude Gemma 4. A conservative adapter release preserves applicable upstream attribution, supplies the license, marks adaptation and retains NOTICE if present in the original distribution. The actual pinned upstream distribution's notice inventory still needs checking. Model licensing does not clear publication of third-party training text.

The remaining exact action needs permission under the user's credential gate: use the existing Hugging Face credential only to verify and recover the named 489,840,816-byte adapter, verify the pinned SHA256/size, then publish it with licensed release metadata as a large-file asset in this same public GitHub repository. No base-model download, training, inference, paid job, credential change or bucket-visibility change is proposed. [GitHub Releases supports distributing large binaries](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github); ordinary Git rejects files over 100 MiB.

No credential was accessed and no weight was downloaded during this preparation. Public adapter publication remains HOLD until the exact credential/recovery action is approved and verified.
