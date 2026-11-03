# Correction to full-package scope

3 November 2026. **SCOPE AUDIT OPEN.** The original five-part archive is a
verified frozen snapshot, but its earlier description as containing everything
was too broad. The owner did not approve omitting project history or research
records. The earlier instruction was to avoid downloading model weights.

The metadata audit identified 26,916 excluded files / 9,421,451,806 bytes,
including generated package copies, runtimes, staging/test trees, Git history,
agent configuration and run/access/billing records. These categories cannot all
be treated as irrelevant to project review. No original files were deleted.

## Data comparison and first correction

A bounded byte comparison checked 13 staged data files / 205,250,429 bytes.
All eight `tmp/ready-v2-stage/*.jsonl` files exactly match included canonical
training-ready-v2 files. Both inspected staged `source.jsonl` files exactly match
the included Parsig text-units export.

Three staged exports have no SHA256/size match in the frozen inventory:

- `tmp/training-export-workbook.json`: 68,336,829 bytes.
- `tmp/translator-stage/local/research-curation/343498f5b5a1b4960b3bf68526bae55938d1779d15b8f1a52008f747ea1f8223/records.jsonl`: 25,332,569 bytes.
- `tmp/translator-stage/local/research-curation/e3c5fe8cf2f40e085af8665ea597c7b3e3d06cbd3058b829cd8c3ce88f258b79/records.jsonl`: 25,329,076 bytes.

Their combined 118,998,474 original bytes are preserved unchanged in
`pahlavi-data-supplement-20261103.zip` (8,443,356 bytes, SHA256
`9cdab6d11a2ecb335df1653050c26012b3ff5c5f293a04a2cc2b110d2ff717a8`).
Local exact membership and per-file SHA256 verification passed. Independent
read-only verification also passed for all three original payloads and their
current source bytes. The supplement was uploaded to the same owner-managed
Drive folder as file `1gr9jxNDehFw6-D-JPB8pmdUQfmb-3TCY`; provider metadata
confirms its name, 8,443,356-byte size and folder parent. No provider digest
comparison is claimed. No exact match does not establish unique semantic examples
or admission to training; staging and canonical roles must remain distinct.

## Open scope

The metadata audit also identified 65 run/access/billing records excluded by
reusing a public-publication rule in a private package, 179 reachable Git commits,
project agent/configuration records, two `training_args.bin` files and two
`rng_state.pth` files. These binaries are not automatically model weights.
Two small annotation-access JSON files remain content-unverified. The bounded
13-file comparison does not prove completeness of every excluded subtree.

The owner explicitly approved the screening required by AGENTS.md for the
Git history and 65 records, credential redaction in export copies, and upload of
the screened supplement to the same private folder. Preparation is underway.
The next bounded audit compared 786 ordinary data-format files under excluded
staging/test roots: 174 files / 288,919,710 bytes match the main package or first
supplement exactly; 612 files / 12,739,065 bytes have no exact inventory match.
These include Wiktionary drafts, research/audit records and test fixtures. They
are being included without treating fixtures as real training or model results.
Credential/account/access paths and installed dependencies were not part of that
bounded comparison. No credentials, network settings, source history,
training data, frozen references, scoring rules or model weights were changed.
No training or paid run occurred. Complete-project and 100-percent data-coverage
claims remain withheld until the remaining scope is resolved.
