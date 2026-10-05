# Qualified Gemma step280: Pahlavi research adapter

5 October 2026. An unchanged retained LoRA adapter for specialist inspection. This is a research checkpoint, with no reliable-translation, decipherment, native-script or unseen-accuracy claim.

The tensor is a [GitHub release asset](https://github.com/MojTah/pahlavi-ai-review/releases/tag/gemma-step280-research-v1), `adapter_model.safetensors`: **489,840,816 bytes**, SHA256 `a51bcd02c6077bcec400c1f342ede3205f260e419ed4f9e3ad0f4338a7e4afdf`. It is too large for ordinary Git and is intentionally stored in Releases. Small configuration, provenance and license files are also in this directory and in the release's `gemma-step280-metadata.zip`. Base weights are not included.

Base: [`google/gemma-4-31B-it`](https://huggingface.co/google/gemma-4-31B-it), pinned revision `842da3794eaa0b77d5f08bae87a17459d91ff475`. Fresh qualified LoRA: 2,237 examples, two epochs, 280 optimizer updates; rank16, alpha32, dropout0. The qualified step20 canary resumed its own state to step280. This is neither the earlier step312 adapter nor a later four-pass/contextual branch. See [executed recipe](../../MODEL-AND-TRAINING-RECIPE.md).

The binary hash matches the saved cloud checkpoint. Publication validated SHA256/size and the safetensors tensor header/offset structure without executing tensor data or model code. The original config's temporary base path and null revision were replaced in `adapter_config.json` with the public base ID and pinned revision; every other field is unchanged. Originals are retained in `original/`, including the old placeholder card, which is archival evidence superseded by this card.

Download both release assets into an adapter directory and extract the metadata ZIP into that same directory. Place `adapter_model.safetensors` beside the extracted `adapter_config.json`. Verify each file against `SHA256SUMS`; hashes of metadata and the ZIP are also recorded in the repository manifest and release metadata.

Loading example for an appropriately provisioned CUDA server:

```python
from pathlib import Path
import hashlib
import torch
from transformers import AutoTokenizer, Gemma4ForConditionalGeneration
from peft import PeftModel

BASE = "google/gemma-4-31B-it"
REV = "842da3794eaa0b77d5f08bae87a17459d91ff475"
ADAPTER = Path("/path/to/extracted/adapter")
with (ADAPTER / "adapter_model.safetensors").open("rb") as stream:
    assert hashlib.file_digest(stream, "sha256").hexdigest() == "a51bcd02c6077bcec400c1f342ede3205f260e419ed4f9e3ad0f4338a7e4afdf"
tokenizer = AutoTokenizer.from_pretrained(BASE, revision=REV, trust_remote_code=False)
base = Gemma4ForConditionalGeneration.from_pretrained(
    BASE, revision=REV, trust_remote_code=False, use_safetensors=True,
    dtype=torch.bfloat16, device_map={"": 0}, attn_implementation="eager",
)
model = PeftModel.from_pretrained(
    base, ADAPTER, local_files_only=True, is_trainable=False,
).eval()
```

This example was not executed for publication. Running it obtains the approximately 62.5 GB base weights and requires substantial GPU memory; it is not an 8 GB GPU compatibility claim. Recorded successful inference used an A100 80 GB with Transformers5.13.1, PEFT0.21.0 and PyTorch2.11.0+cu128. Publication downloaded only the approved adapter and ran no model, training or paid job. The model's text inputs in this research use transliterated Middle Persian; Persian outputs and their philological correctness require specialist review. Inspect the original input/output files and task-specific prompts rather than treating this loading example as an evaluated translator application.

Latest evidence: the [faithfulness instruction comparison](../../experiments/dictionary-faithfulness-20261005/live-execution/OUTCOME.md) failed both fixed continuation screens. All15control outputs match the earlier dictionary-assisted outputs, while fresh AI cohorts rated them differently. Historical 2/15→5/15 dictionary results are provisional observations, not a stable accuracy estimate. Neither the latest prompt nor a new model is promoted; expert source-grounded adjudication/calibration is needed.

Gemma4 is published under [Apache2.0](https://ai.google.dev/gemma/docs/gemma_4_license); LICENSE and NOTICE preserve upstream attribution and identify adaptation/config changes. This release makes no blanket license claim for third-party training text. Full restricted or uncleared training/source collections remain unavailable; [data access](../../review/DATA-ACCESS.md) and [omissions](../../review/OMISSIONS.json) document that reproduction gap. Adapted NLLB weights and the base model are absent from this release.
