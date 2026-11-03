# Data: download and browse

This is the public data entry point for **MojTah/pahlavi-ai-review**. No GitHub account is required. The separate `MojTah/pahlavi-language` repository is private.

**[Download the public repository ZIP](https://github.com/MojTah/pahlavi-ai-review/archive/refs/heads/main.zip)**, or use the direct links below. The ZIP contains the published code, data and evidence; model release assets are separate and are not needed for data review.

## Complete research package (private)

**[Open the complete Drive folder](https://drive.google.com/drive/folders/1wQ5mPAZauHwYa7v1qVpwFzElsGFt95TQ)** · **[Contents, checksums and access instructions](review/COMPLETE-DATA-PACKAGE-20261103.md)**.

**3 November delivery status: LOCAL ARCHIVE VERIFIED; TRANSFER INCOMPLETE.** The full snapshot includes raw source collections/books, local training-set versions and exports, code/configuration, research notes and actual evaluation results: 40,551 project files, a 2.16 GB ZIP prepared in five parts. Drive currently confirms only `README.md`, `TRANSFER-MANIFEST.json` and `SHA256SUMS.txt`; none of the five archive parts is confirmed online. The complete data cannot yet be downloaded, and friend access has not been granted. The owner must grant your email access after transfer verification. This does not require a GitHub account and does not make the full corpus publicly readable. The public repository ZIP contains only the selected public release.

## Actual source data

These are source collections, **not a combined, fully approved training set**. Counts use different units and must not be added together as translation-pair counts.

| Collection | Open the data | Provenance and reuse |
|---|---|---|
| OpenAMPD: 152 document records | [Document JSON](sources/local/public-texts-2026-09-20/berkeley/documents.json) · [Download JSON](https://raw.githubusercontent.com/MojTah/pahlavi-ai-review/main/sources/local/public-texts-2026-09-20/berkeley/documents.json) · [Original XML/source captures](sources/local/public-texts-2026-09-20/berkeley/raw/) | [Source manifest](sources/local/public-texts-2026-09-20/berkeley/manifest.json); recorded CC BY-NC-SA 4.0 and document/editor credits |
| Legacy Cologne CPD: 4,218 dictionary records, distinct from current Kosh | [Dictionary JSONL](sources/local/public-texts-2026-09-20/cologne-legacy-cpd-20260928/cpd.jsonl) · [Download JSONL](https://raw.githubusercontent.com/MojTah/pahlavi-ai-review/main/sources/local/public-texts-2026-09-20/cologne-legacy-cpd-20260928/cpd.jsonl) · [Original TSV](sources/local/public-texts-2026-09-20/cologne-legacy-cpd-20260928/cpd-original.tsv) | [Source manifest](sources/local/public-texts-2026-09-20/cologne-legacy-cpd-20260928/manifest.json); recorded CC BY-NC-SA 3.0 for data, separate software terms |
| Ezafe modeling: five grammatical research CSV inputs | [Captured files](sources/local/public-texts-2026-09-20/ezafe-modeling-mp/raw/) · [Manifest mapping captures to upstream filenames](sources/local/public-texts-2026-09-20/ezafe-modeling-mp/manifest.json) | Original README/license retained with captures; [recorded licenses and attribution](review/DATA-LICENSES.json) |

Hash-named `.source` captures retain their original bytes. Use each manifest to identify the upstream filename, URL and file type; a `.source` extension does not imply plain text. Preserve source-specific attribution, noncommercial and ShareAlike restrictions where applicable. There is no blanket license for the whole repository.

## Translation inputs, outputs and assessment evidence

These are **already exposed development/evaluation records**, not material to add to training or an unseen test.

- [Dictionary-assisted comparison: inputs, outputs and reviews](resources/local/dictionary-ab-results-20261005/d68800b3b35c44a4a97adc0c5129a3de/).
- [Faithfulness comparison: final server outputs](resources/local/dictionary-faithfulness-results-20261005/6b54f5bc4e984dbe9a4b53e89e4bf5d8/final/), with [packets and scored review evidence](resources/local/dictionary-faithfulness-20261005/).
- [Common archived-output assessment](resources/local/measurement-calibration-20261005/) and [interpretation/limits](experiments/measurement-calibration-20261005/REPORT.md).
- [Frozen benchmark protocol](benchmarks/pal-reference-v1/PROTOCOL.md): preserve existing exclusions and frozen bytes.

## What is NOT published

The **complete training/candidate arrays are not on public GitHub**. Bulk Parsig/TITUS texts, current Kosh inventories, MacKenzie/Nyberg and other supplied books include restrictive or unresolved redistribution terms. The complete review ZIP is verified locally but not yet confirmed online in the private Drive folder above; its source-text payload is not in the public GitHub tree. More detail: [data access and gaps](review/DATA-ACCESS.md), [omission inventory](review/OMISSIONS.json), [training/model recipe](MODEL-AND-TRAINING-RECIPE.md).

A reviewer can inspect the selected public data immediately. The complete local research snapshot will require both a verified full upload and owner-granted Drive access. Source permissions still govern reuse and reproduction. No model weights were downloaded to prepare the complete data package.
