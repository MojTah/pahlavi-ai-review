# Data: download and browse

This is the public data entry point for **MojTah/pahlavi-ai-review**. No GitHub account is required. The separate `MojTah/pahlavi-language` repository is private.

**[Download the public repository ZIP](https://github.com/MojTah/pahlavi-ai-review/archive/refs/heads/main.zip)**, or use the direct links below. The ZIP contains the published code, data and evidence; model release assets are separate and are not needed for data review.

## Frozen research snapshot and open scope audit

**[Open the owner-managed Drive destination](https://drive.google.com/drive/folders/1wQ5mPAZauHwYa7v1qVpwFzElsGFt95TQ)** · **[Contents, checksums and access instructions](review/COMPLETE-DATA-PACKAGE-20261103.md)**.

**3 November delivery status:** all five parts of the frozen main archive and all five current supplements (data, screened history/65 records, 1,920 project extras, 608 local test-artifact payloads, and attached external feedback) are confirmed online by names/sizes/parents as of 23:39 UTC. No started transfer is waiting. See the [download list and per-package verification](review/COMPLETE-DATA-PACKAGE-20261103.md) and [six-archive SHA256 list](review/DELIVERY-CHECKSUMS-20261103.txt).

The main archive is split into five parts; all five are required. Supplements are separate ZIPs. Their raw/draft/test roles remain explicit: file counts are not independent translation pairs, approved training examples or new model results. Existing byte-identical copies and the already released real adapter are referenced rather than uploaded again.

The [scope audit](review/EXCLUSION-AUDIT-20261103.md) remains open for 18 sensitive extras and the owner's choice about approximately 2 GB of installed software/cache/installer copies versus inventory/reinstallation evidence. The original attached 7,651-byte Antigravity report outside the workspace is preserved in the uploaded external-feedback supplement; two other reviews are reused through exact main-package aliases. The current Desktop report is empty, and its earlier contents are not claimed recovered. Raw account chat histories were not exported by this project-file audit. Drive access is owner-managed and restricted; reviewers must use an account granted access. No GitHub account is needed for the selected public repository ZIP.

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

The **complete training/candidate arrays are not on public GitHub**. Bulk Parsig/TITUS texts, current Kosh inventories, MacKenzie/Nyberg and other supplied books include restrictive or unresolved redistribution terms. All five main parts and all five current supplements are present in the restricted Drive folder above; their payload is not in the public GitHub tree. Only the explicit sensitive/software scope decisions remain open for this delivery. More detail: [data access and gaps](review/DATA-ACCESS.md), [omission inventory](review/OMISSIONS.json), [training/model recipe](MODEL-AND-TRAINING-RECIPE.md).

A reviewer can inspect the selected public data immediately. Review of the frozen main ZIP requires all five uploaded parts and owner-managed Drive access; each supplement is a separate download. The download guide distinguishes confirmed uploads from pending scope items. Source permissions still govern reuse and reproduction. No model weights were downloaded for this packaging work.
