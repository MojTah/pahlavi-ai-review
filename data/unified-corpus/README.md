# Unified corpus and training preparation

Current learning resource: the independently verified [source-qualified release](../../experiments/data-qualification-20260928/README.md) freezes 2,676 Persian lexical inventories,4,932 English lexical inventories/blocks,240 conditioned teaching units,57 English documentary spans,six Persian inscription occurrences andfour English article scopes. These are separate tasks and grains; complete meanings, context and all holds remain explicit. Its ten-file local package includes an unchanged historical2,237-pair control. It does not rewrite this catalogue, admit every earlier candidate, or start training.

Earlier addition: the separately frozen [expanded source-resource package](../../experiments/dataset-expansion-20260928/README.md) binds31,918 typed lexical/reference records,113 additional S22 teaching records,53 archived document associations and4 Parsig format-recovery candidates. It supplements this historical unified snapshot without rewriting it or increasing the trained2,237-pair control. Follow the newer qualification release above for the scopes subsequently reviewed.

28 September 2026. This is the single entry point for old collections, the final Kosh download, supplied books and subsequent annotations. Original archives stay in their verified locations; the catalogue links to exact files and records instead of copying PDFs or counting earlier downloads twice.

## Execution contract

Mode: Classic + Critic. Root is the only writer and execution owner. `/root/nllb_source_method` inventories coverage; `/root/nllb_final_preflight_review` independently reviews integrity. No external service, credentials, new download, training job or package installation is involved.

Bounded local import: shared `codex-science` Python, expected under two minutes and 200 MB additional disk, five-minute allocation checked between file operations. This is not an interrupting I/O timeout. Root stops a stalled process; no automatic retry. Inputs are the frozen qualified TRAIN, its audit ledger, final Kosh v4 and existing source manifests. `build.py --check` validates and prepares everything in memory; `build.py --write` creates a new local output directory only after validation. Existing outputs are never overwritten. A partial write remains visibly incomplete without a manifest; stop and review rather than delete or resume blindly. The output manifest binds code and input/output hashes. Run the self-check before either operation.

```powershell
& '[USER_HOME]\.venvs\codex-science\Scripts\python.exe' data/unified-corpus/build.py --self-check
& '[USER_HOME]\.venvs\codex-science\Scripts\python.exe' data/unified-corpus/build.py --check
& '[USER_HOME]\.venvs\codex-science\Scripts\python.exe' data/unified-corpus/build.py --write
```

## Outputs and interpretation

Local outputs live in `resources/local/unified-corpus-20260928/v2/`. The tracked `manifest-v2.json` and `quality-report-v2.json` bind that local resource; Git alone does not include the corpus.

**Executed:** v1 validation took 6.0 seconds and its write 6.2 seconds. The second independent review then found 121 known held-out archive documents marked only as references. V2 adds explicit protection: validation took 5.0 seconds and its write 5.4 seconds. It binds 5,716 input files: the original 5,709 plus seven v1 audit artifacts. All v1 output bytes are preserved; its builder snapshot is retained at `resources/local/unified-corpus-20260928/v1/build-source.py`. The first read-only pass was stopped after repeated path resolution made it unnecessarily slow; no output was created then. A cache of already-validated paths fixed that overhead. The reviewer also identified and corrected a hash-versus-parsed-bytes race before the successful run; a mutation regression now rejects changed bytes.

| Disposition | Indexed items | Meaning |
|---|---:|---|
| Historical qualified control | 2,237 | Existing paragraph translation pairs, still provisionally AI-reviewed |
| Review required | 26,880 | 26,377 lexical groups, 468 other Parsig paragraphs, 7 teaching pairs, 28 auxiliary annotations |
| Protected held-out | 3,161 | 1,555 Parsig paragraphs, 1,485 Kosh observations and 121 known archive witnesses; targets are not copied into the index |
| Quarantined | 14,386 | Existing rejected Parsig rows plus Kosh structural/language/edition exceptions |
| Reference only | 2,840 | Document/file/index grain; not 2,840 translation pairs. Unmatched lineage remains uncleared. |
| **Catalogue total** | **49,504** | Mixed grains, not an effective training-set size |

Newly admitted training pairs: **zero**. Exact duplicate core pairs: **zero**. Two short identical-source groups have published target variations; their four original rows remain unchanged and flagged in the report. One difference is final punctuation; another includes an explanatory Persian gloss. These are not automatically classified as wrong translations. Eight groups of byte-identical input files are recorded, including the same SGV PDF at two sites. The 903 repeated Kosh observations remain provenance for their groups, not additional training examples.

- [catalogue.jsonl](../../resources/local/unified-corpus-20260928/v2/catalogue.jsonl): typed records with family, disposition and exact original file/row locator. Document, paragraph, lexical-group and annotation grains are explicit and must not be added into a sentence-pair total.
- [review-queue.jsonl](../../resources/local/unified-corpus-20260928/v2/review-queue.jsonl): unresolved candidates. No row here is authorized for training. It links to intact source records, including their original XML and edition information.
- [quarantine-index.jsonl](../../resources/local/unified-corpus-20260928/v2/quarantine-index.jsonl): protected held-out material and retained rejected evidence. Nothing is deleted or silently repaired.
- [train-core.jsonl](../../resources/local/unified-corpus-20260928/v2/train-core.jsonl): model-independent export of the existing 2,237 provisionally AI-qualified pairs, preserving text, targets, attribution and qualifications. This is a historical control, not a newly specialist-certified dataset or authorization for another run.

[Current manifest](manifest-v2.json) binds every input and output. [Current quality report](quality-report-v2.json) gives per-family/grain counts and duplicate diagnostics. [Gemini review disposition](GEMINI-REVIEW.md) distinguishes a successful Pro execution from its unsupported proposed CPD-de patch.

No new source is admitted merely because it parses, has a populated translation field or contains Persian-script letters. Normalization for duplicate diagnostics is NFC plus whitespace only. Original text, diacritics, uncertainty and variants survive unchanged. Exact repeats retain provenance; different meanings, languages and editions are not merged automatically. Source-equivalent target variants are flagged, not declared incorrect without contextual review.

## Remaining admission work

1. Resolve per-entry source/target language and the actual word-to-sense relationship. Dictionaries, attested clauses, teaching examples and grammatical annotations need separate task definitions.
2. Establish work/edition/quotation lineage across archives, protect all 16 held-out work families and carry the prior contamination exclusions forward. An unfamiliar title or zero exact matches is not proof of independence.
3. Verify translations against their cited source, preserve uncertainty and keep unresolved or contradictory cases out. AI review must remain labelled as AI review.
4. Resolve source-specific intended-use restrictions and attribution, then freeze one reviewed dataset and compare the planned experiment against the unchanged evaluation. No synthetic Persian translation becomes gold by default.

Known local gaps: PahGen's reported 317 pairs have no verified local dataset here; S27 has no valid local PDF; full MPCD annotations, most scan-only pages and complete dictionary semantic qualification remain unavailable or unfinished. KB prose and authored dictionary drafts are research-exposed support material, not automatic training labels.

The smaller approach used here is a file catalogue plus existing source archives and JSONL exports. A new database or physical duplication of every PDF would not improve the current review task.


## Independent review evidence

- Lead agent/request id: /root
- Critic agent/request id: /root/nllb_source_method
- Critic model and reasoning effort: inherited session configuration; no override
- Independent from lead: yes
- Evidence reviewed: v2 protection mappings, current builder and receipts, v1 preservation, core and queue identity; earlier full integrity audit by /root/nllb_final_preflight_review
- Verification evidence: exactly 121 correct document-protection changes; 3,161 protected, 2,840 references and 17,547 quarantine-index rows; v1 output hashes unchanged; v2 core and queue byte-identical to v1; v2 output/code/report receipts and self-check pass. Earlier integrity audit checked all 5,709 original input hashes, unique IDs, all locators and historical core qualifications.
- Critic verdict: pass

The first critic's integrity pass did not establish perfect protection metadata. A separate coverage review by `/root/nllb_source_method` found the 121-document issue; v2 explicitly protects 16 Parsig book records, 100 TITUS pages, two Avesta Zadspram artifacts and three PersoAryan HKR/Sūr artifacts. No v1 or v2 row was automatically admitted to training. The second reviewer independently passed the v2 correction, correct work mappings, unchanged non-document rows and preservation of all four v1 outputs. The unknown-work documents remain uncleared references; no absence-of-match rule grants clearance.

Root additionally compared every historical core row's audit `raw_export_sha256`, `raw_unit_sha256` and `raw_pointer` with the current Parsig export and publisher receipts; all 2,237 matched. The core has 1,411 prior ELIGIBLE and 826 ELIGIBLE_WITH_QUALIFICATIONS judgments, all by AI reviewers. No new linguistic certification is inferred.
