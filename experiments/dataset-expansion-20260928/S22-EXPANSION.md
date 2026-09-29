# S22 bounded expansion receipt — 2026-09-28

Result: **9 additional image-checked pedagogical clause pairs**, staged in `s22-candidates.jsonl`. None is admitted to training. The existing 7 S22CLAUSE records are unchanged. These 9 additions occupy **5 related teaching context families**, not 9 independent manuscript attestations. Root independent review, split/lineage checks and training-use decisions remain outstanding.

## Source and actual scope

- Source: Amouzgar and Tafazzoli, *Zaban-e Pahlavi, adabiyat va dastur-e an*, Moin, fourth printing, 1382 SH.
- Local PDF: `sources/@RastarLib_زبان_پهلوی،_ادبیات_و_دستور_آن.pdf`.
- Source SHA256: `207aeda5eae48227902f0f208f9b24fd5623627dd4ca589b217268e69596df92`.
- 170 PDF pages. The all-page embedded-text check found zero nonempty text pages; extraction needs images/manual reading or a separately validated OCR workflow. This census is not a claim that all page contents were read.
- All 170 pages were visually overviewed in contact sheets, which establish section/layout coverage only. Detailed full-page images were inspected for PDF 6, 7, 70, 71, 72, 74, 75, 76, 78–86 and 92. Some pages were read selectively around examples rather than transcribed completely. PDF 80–81 were also inspected in the earlier seven-pair review and rechecked here.
- The **actual exported examples were each read from full rendered PDF pages 79–82**, corresponding to printed 76–79. PDF-to-print offset minus 3 is established locally for these pages, not asserted for the cover/front matter.
- Existing receipts consulted: `experiments/composition-evidence-20260928/candidates.jsonl`, its README/source-copy-screen context, and current dataset-readiness scope. No held-out translations were opened, no external model or website was called, and no protected-work target was copied into this candidate file.

## New candidates

| ID | PDF / printed page | Teaching evidence | Qualification |
|---|---|---|---|
| S22EXP-001 | 79 / 76 | paymōxt with present have | Preserve published idiomatic and literal renderings separately; participants unresolved. |
| S22EXP-002 | 80 / 77 | First-person agent, singular nominal patient, zero auxiliary | φ is editorial notation; serialization remains undecided. |
| S22EXP-003 | 80 / 77 | First-person agent, singular pronominal patient, zero auxiliary | Same zero-symbol issue; reference and gender not resolved. |
| S22EXP-004 | 81 / 78 | First-person transitive perfect | Persian parenthesized patient supplied by textbook retained. |
| S22EXP-005 | 81 / 78 | Second-person transitive perfect | Agent encoded by -t; auxiliary does not make agent third person. |
| S22EXP-006 | 81 / 78 | Agentless perfect read as passive | Local teaching context retained; duplicate occurrence at PDF 84 / print 81 recorded, not counted again. |
| S22EXP-007 | 81 / 78 | Transitive past perfect with estād | Parenthesized source and target patient retained; temporal reference absent. |
| S22EXP-008 | 81 / 78 | Transitive past perfect with būd | Auxiliary alternative to preceding pair; absent patient not invented. |
| S22EXP-009 | 82 / 79 | paymōxt with past have | Published idiomatic/literal distinction retained; -š reference unresolved. |

Verbatim lexical content and diacritics are in JSONL. Layout/separator colons are omitted; Persian spacing/ZWNJ and quotation glyphs are typographically normalized. The φ glyph is transcribed with a Unicode approximation and explicitly tagged as editorial zero notation. These normalization statements are material: the Unicode text is not a facsimile transcription of typesetting. No dashes from paradigm tables were expanded into invented sentences.

Each row carries source PDF hash, page image hash, exact locator, translation origin, grammatical/semantic qualification, context family and related candidate IDs. The reader should preserve those fields if generating a later training view. The main Persian translation and explanatory literal gloss must not be counted as two independent examples.

## Book coverage and what remains

The contact-sheet and contents overview indicates: PDF 1–13 front matter; 14–64 language/literature/script discussion; 65 blank; approximately 66–88 grammar; 89–93 reading-section transition and introduction; 94–116 native-script selected readings; 117–121 glossary transition and introduction; 122–167 glossary; 168 erratum; 169–170 English publishing/back matter. These are broad section positions, not an exhaustive content inventory. PDF 92 explicitly describes editorial additions, deletions and corrections; native-script readings must retain those distinctions.

The complete grammar still deserves a systematic line-by-line audit, particularly PDF 66–69, 73, 77, 87–88 not inspected at full-page detail here. Detailed pages can also contain candidates not selected in this bounded pass. The later glossary was only overviewed and is not proved to contain zero eligible larger phrases. The native-script reader lacks an immediately obvious aligned Latin-transcription/Persian sentence series; it needs a separate source-aware treatment, not automatic import.

## Deliberate holds and exclusions

- PDF 75 / print 72 has a complete unattributed admonitory maxim. Its underlying work may overlap a protected admonition family; held without quotation export until lineage is resolved.
- PDF 78 / print 75 has attributed Denkard/Rivayat quotations; PDF 82 / print 79 has attributed Menog Xrad/Rivayat conditionals, some explicitly abbreviated. These were not exported. Exact work/section lineage and excerpt completeness need separate resolution; nonprotected-looking titles alone do not settle it.
- Reader selections include protected Zaduspram around PDF 107–109 and admonition material requiring lineage checks. No reader quotation was exported.
- The root supplied canonical held-out family IDs: 103, 104, 110, 111, 112, 114, 116, 117, 118, 120, 124, 130, 132, 138, 152, 517. Metadata/title-level screening was respected; underlying held-out translations were not consulted.
- PDF 80's introductory reporting expression ends with “that”; it is incomplete as a freestanding sentence and was not split off as a candidate.
- Finite-form and morphology tables around PDF 79, 81, 83–86 contain useful future morphology evidence, but this pass does not inflate sentence count by exporting abbreviated paradigm cells, isolated lexical glosses or derivational fragments. Dedicated morphology records would be a different data type.

## Validation and use bounds

Nine JSON records parse, have unique IDs, match the verified local page offset and have existing SHA256-linked source images. No new Pahlavi string exactly duplicates one of the prior seven; semantic and constructional overlap remains substantial. Candidate 006's repeated printed occurrence is explicitly recorded. These checks do not establish source-family independence or absence of overlap with the full training corpus.

All records are `STAGED_NOT_TRAIN_ADMITTED`, `admission_allowed=false`, `expert_certified=false`. Before any admission: independently check the images/text; resolve editorial-symbol serialization; screen source-copy/near-duplicate and family lineage without consulting held-out answers; group near-identical paradigmatic examples to prevent split leakage; establish permitted training use. These records support the textbook's contextual translations, not a single universal meaning for every word or construction.

Only this report, its JSONL and allowed scratch images were written by this expansion task. Original PDFs, prior receipts, corpus and model files remain untouched.

JSONL SHA256: `e24a63448805f5e99f54874e32d502af350febb57e3830f07ed51d069b061e11`.
