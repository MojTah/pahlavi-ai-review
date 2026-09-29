# S22 glossary A: PDF122–144

Status: complete assigned-page extraction, **provisional and not training-admitted**. All23 assigned pages were visually read; 531 printed entry groups are retained, including 4 native-script reference-only groups. Independent visual review remains pending. Every row is held for unresolved per-entry work/reader lineage; 11 also have a distinct extraction/context/printed-uncertainty hold.

## Source and layout

Source PDF SHA256: `207aeda5eae48227902f0f208f9b24fd5623627dd4ca589b217268e69596df92`. Each row binds its full-page image hash and source PDF hash. PDF page numbers are one-based; printed page = PDF page minus3 throughout the assigned range. The source PDF is unchanged.

PDF117 and119 are blank, PDF118 is the glossary divider, and PDF120–121 contain the instructions. The instructions say ordering follows native glyph appearance, transcription generally follows MacKenzie, meanings are chosen from the book's readings, and unusually different inflected forms can be separate entries. Thus these definitions are source-scoped lexical inventories, **not automatically general dictionary records**. Some underlying textbook readings may belong to protected works. Per-entry lineage remains unknown; another dictionary's matching surface form cannot clear S22.

The extraction uses the printed Latin phonological transcription, not adjacent Aramaic letter transliteration. Native-script forms, suffixes and cross-reference targets remain image evidence; none was converted into invented Latin. Complete form/meaning bundles are one row. Inflections, variants, POS comments and notes are separate fields. No form-by-sense Cartesian expansion was made. No reader quotations outside the glossary were exported.

Manual Unicode transcription joins print line wraps and represents Persian word spacing with spaces/ZWNJ. The exact printed words, alternative forms and explicit uncertainty are the intended transcription target; source images remain authoritative for typography and the pending independent review. This is not OCR output or philological certification.

## Complete page ledger

| PDF page | Printed page | Groups starting here | Coverage |
|---|---:|---:|---|
| 122 | 119 | 20 | Visual first pass complete |
| 123 | 120 | 24 | Visual first pass complete |
| 124 | 121 | 24 | Visual first pass complete |
| 125 | 122 | 22 | Visual first pass complete |
| 126 | 123 | 25 | Visual first pass complete |
| 127 | 124 | 26 | Visual first pass complete |
| 128 | 125 | 22 | Visual first pass complete |
| 129 | 126 | 26 | Visual first pass complete |
| 130 | 127 | 20 | Visual first pass complete |
| 131 | 128 | 26 | Visual first pass complete |
| 132 | 129 | 19 | Visual first pass complete |
| 133 | 130 | 24 | Visual first pass complete |
| 134 | 131 | 21 | Visual first pass complete |
| 135 | 132 | 22 | Visual first pass complete |
| 136 | 133 | 23 | Visual first pass complete |
| 137 | 134 | 23 | Visual first pass complete |
| 138 | 135 | 27 | Visual first pass complete |
| 139 | 136 | 22 | Visual first pass complete |
| 140 | 137 | 27 | Visual first pass complete |
| 141 | 138 | 13 | Visual first pass complete |
| 142 | 139 | 21 | Visual first pass complete |
| 143 | 140 | 27 | Visual first pass complete |
| 144 | 141 | 27 | Visual first pass complete |

No assigned page is unprocessed. Three group definitions continue onto the next page: Ērān-dehān (123→124), āwahan homānāg (124→125), and bowandag-menišnīh (133→134). Their rows retain both page hashes; continuation lines are not counted twice. Repeated Latin spellings with different printed headwords remain distinct groups.

## Explicit local holds

| Entry ID | Printed/tentative transcription | Reason |
|---|---|---|
| S22GA-124-012 | (no safe Latin reading) | This printed group supplies native Pahlavi headword(s) without a Latin transcription; do not reconstruct Latin from the glyph. |
| S22GA-124-017 | (no safe Latin reading) | Native-script cross-reference only; no Latin reading or Persian meaning supplied. |
| S22GA-127-010 | xūb-sār(?) | Printed transcription and gloss are explicitly uncertain. |
| S22GA-130-002 | āhen abar gumēxt estād | Finite-clause/period label within glossary; contextual source-family clearance required before any use as sentence supervision. |
| S22GA-131-006 | abāyīdan | Faded image band: tentative Latin reading and incomplete Persian definition require source confirmation. |
| S22GA-131-007 | (no safe Latin reading) | Faded source band; neither full Latin transcription nor Persian gloss safely readable. |
| S22GA-131-008 | (no safe Latin reading) | Faded source band; do not reconstruct a Latin verb or target. |
| S22GA-131-009 | ābādānīh | Tentative transcription in faded band; Persian آبادانی is visible but full form needs confirmation. |
| S22GA-137-004 | (no safe Latin reading) | Native-script cross-reference only; no Latin transcription or gloss supplied. |
| S22GA-138-007 | (no safe Latin reading) | Native-script cross-reference only; no Latin transcription or gloss supplied. |
| S22GA-144-002 | (no safe Latin reading) | Native-script cross-reference only; no Latin transcription or gloss supplied. |

The visibly faded band on PDF131 is genuinely incomplete in this scan. Enlarging it did not recover the missing ink; no dictionary-based guess fills those entries. Enlarged inspection did resolve uzdēszār → بتکده and asōyišn → تباه‌نشدنی. The printed uncertainty in xūb-sār(?) remains explicit. The finite phrase about the iron-mixing period is retained as a glossary record with a contextual-use hold, not admitted as sentence supervision.

## Validation and reproducibility

The scratch renderer manifest covers the required instruction and glossary pages. `build_extraction.py` binds the PDF, manual entry input, renderer manifest and its own bytes; it refuses final-output overwrite. Executed checks cover 531 unique IDs, exact declared per-page group counts, all23 pages present, PDF/print offsets, source/image checksums, reference-only null targets, required holds, no admission, and persisted JSONL re-read. Counts reconcile the manual page ledger; they do not independently prove every character correct.

Only `s22-glossary-a.jsonl`, this report and the assigned glossary-a scratch folder were written. No GPU/model run, network, OCR, source edit, corpus admission or evaluation-set change occurred. Any book erratum applicability still needs the lead's edition-level integration check; this extractor did not inspect an erratum page outside the assigned range.

JSONL SHA256: `6934b41a518a7a6dd5657c7d1528a2f20ce9f54104c6385a5f4c1f3da13d0c81`.
Manual group input SHA256: `89ad9efd5b862c6ce7dc933841af9a15e954b24175e29ba238aa899ae7db7ad2`.
Builder SHA256: `711b9e0937fadb44fbb9e06b038ca2c2154f6e84aaca3bf1d3879b5db7524059`.
