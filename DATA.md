# Data: download and browse

This is the public data entry point for **MojTah/pahlavi-ai-review**. No GitHub account is required. The separate `MojTah/pahlavi-language` repository is private.

**[Download the public repository ZIP](https://github.com/MojTah/pahlavi-ai-review/archive/refs/heads/main.zip)**, or use the direct links below. The ZIP contains the published code, data and evidence; model release assets are separate and are not needed for data review.

## Frozen research snapshot and open scope audit

**[Open the owner-managed Drive destination](https://drive.google.com/drive/folders/1wQ5mPAZauHwYa7v1qVpwFzElsGFt95TQ)** · **[Contents, checksums and access instructions](review/COMPLETE-DATA-PACKAGE-20261103.md)**.

**3 November status: CURRENT MAIN ARCHIVE AND THREE-FILE SUPPLEMENT UPLOADED; FULL-PROJECT SCOPE AUDIT OPEN.** The main snapshot contains 40,551 project files (6,808,004,295 original bytes) in a 2.16 GB ZIP split into five parts. It includes source collections/books, selected local training-set versions and exports, code/configuration, research notes and actual evaluation results. As of 22:45:31 UTC, Drive confirms all five parts and the three sidecars by names/sizes. All five parts are required to reconstruct the ZIP; verify the published local SHA256 after download.

The [exclusion audit](review/EXCLUSION-AUDIT-20261103.md) found three omitted staged data exports (118,998,474 bytes) with no exact match in the frozen inventory. The [separately verified 8,443,356-byte supplement](https://drive.google.com/file/d/1gr9jxNDehFw6-D-JPB8pmdUQfmb-3TCY/view) preserves them unchanged; its online name/size/parent are confirmed. This does not establish new semantic examples or approved training records. Git history and other excluded project records are still under review, so this package cannot yet be described as everything in the project. Drive access is owner-managed and restricted; reviewers must use an account granted access. No GitHub account is needed for the selected public repository ZIP.

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

The **complete training/candidate arrays are not on public GitHub**. Bulk Parsig/TITUS texts, current Kosh inventories, MacKenzie/Nyberg and other supplied books include restrictive or unresolved redistribution terms. All five parts of the frozen main review ZIP and its first data supplement are present in the restricted Drive folder above; their source-text payload is not in the public GitHub tree. The scope audit remains open. More detail: [data access and gaps](review/DATA-ACCESS.md), [omission inventory](review/OMISSIONS.json), [training/model recipe](MODEL-AND-TRAINING-RECIPE.md).

A reviewer can inspect the selected public data immediately. Review of the frozen main ZIP requires all five uploaded parts and owner-managed Drive access; the three-file supplement is a separate download. Further coverage and history review have outstanding steps. Source permissions still govern reuse and reproduction. No model weights were downloaded for this packaging work.
