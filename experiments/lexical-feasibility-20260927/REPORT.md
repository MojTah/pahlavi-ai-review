# Lexical supervision, additional text and book-source feasibility

27 September 2026. Mode: Classic + Critic. Root owns preparation; isolated read-only audits and an independent critic checked the evidence. No paid computation, new model download or training was performed.

The feasible next work is source validation, before selecting another training recipe. We now have a reproducible **14-record TRAIN-only review packet**, six dictionary-definition checks and a substantially larger potential source-text pool than the earlier Parsig-only inventory established. **Zero new lexical/grammar labels and zero external CPT records are admitted.** This is concrete preparation, not a measured improvement in model quality.

## What was prepared and checked

| Artifact | Result | What it does not establish |
| --- | --- | --- |
| [packet.jsonl](packet.jsonl), [audit](packet-audit.json) | Nine existing single-item translation units, eight form groups, plus five contextual word candidates; 14 records across four TRAIN works | New independent gold, unseen-word performance or an expanded benchmark |
| [scholarly-checks.json](scholarly-checks.json) | Six short Nyberg definition checks linked to seven packet records; printed and PDF page locators visually inspected | Exact Persian contextual meanings, universal spelling normalization or specialist adjudication |
| [Local annotation audit](LOCAL-ANNOTATION-AUDIT.md) | Five of sixteen draft dictionary entries qualify for TRAIN-only investigation; existing grammatical datasets need source/occurrence alignment | Sixteen trusted labels or ready-to-use grammar supervision |
| [Additional source inventory](ADDITIONAL-SOURCE-INVENTORY.md) | TITUS has 2,183 content pages / 903,313 raw whitespace terms; a bounded eight-root candidate pool has 995 pages / 199,043 raw terms | That these counts are clean, novel, permitted Middle Persian training data |
| [External annotation eligibility](EXTERNAL-ANNOTATION-ELIGIBILITY.md) | Exact June Oxford release has a recorded CC BY 4.0 declaration; published English/source layers exist; no usable current MPCD UD annotation files verified | That the separate September archive is identical/licensed by implication, or English translation is Persian gold |

The packet retains exact source and passage-target bytes, edition/translator provenance, raw-record locators, hash identity and the existing linguistic qualifications. The five contextual candidates are `xrad`, `frazand`, `xwāstag`, `ruwān` and `hunsandīh`. Proposed meanings and parts of speech remain explicitly marked as earlier Codex drafts. All accepted auxiliary labels are null; all records have `training_admitted=false` and `expert_adjudicated=false`.

The saved annotation for occurrence `119000001003` belongs to a quarantined passage. It was excluded, not transferred to the selected occurrence of `hunsandīh` in `119000002`. Nine isolated translation units include two `frazaft` occurrences: those form one recall group, not two independent novel-word tests. No benchmark answer or model prediction determined selection. The generator reads the legacy draft dictionary but emits only the five selected proposal fields; that legacy file itself is not asserted to be wholly split-safe.

## Books: evidence already used and exact priorities

Books supply attested meanings, transcription conventions and grammatical analyses. Reading a dictionary entry is not equivalent to verifying every occurrence; reprints and books quoting each other are not independent votes. Keep the original source layer, alternatives, context and page citation together. Book passages used to develop annotations must not later be described as sealed confirmation material.

1. **Already available and used: H. S. Nyberg, A Manual of Pahlavi II (Wiesbaden: Otto Harrassowitz, 1974).** Existing source S24 is `sources/A-Manual-of-Pahlavi-II-Dictionary.pdf`, SHA256 `d49aaebbe1f51ebc07c616f538ff40a2a8d7ae9c3b810836c65689ab8a50f8c9`. This checkpoint visually checked PDF pages 87, 180, 228, 229 and 230, corresponding to printed pages 78, 171, 219, 220 and 221. The exact `frazand` entry supports a generic child sense. The other comparisons retain explicit transcription or lexical-family questions: `xrad/xrat`, `xwāstag/xᵘāstak`, `ruwān/ruvān`, `hunsandīh/xᵘansandēh` and `frazaft/frazāft`. These are six source checks, not six accepted new labels. S26 is another printing of Nyberg's English text, not independent corroboration. Existing earlier coverage is recorded in [supplied-book study](../../kb/supplied-pdf-study.md).
2. **Highest-priority additional dictionary: D. N. MacKenzie, A Concise Pahlavi Dictionary (Oxford University Press, 1971); preferably the 1986 reprint with Addenda and Corrigenda.** Its bibliographic identity and corrected reprint are documented by Desmond Durkin-Meisterernst's [scholarly bibliography](https://www.iranicaonline.org/articles/mackenzie-david-neil/). This checkpoint has not inspected a complete copy or its specific entries. Use it to cross-check the five lexical candidates and their transcription correspondences with Nyberg, preserving disagreements. A searchable internet scan is not assumed to confer a dataset-reuse license. This is the most useful exact title for the user to help locate through an available personal or library copy.
3. **Priority grammar: Desmond Durkin-Meisterernst, Grammatik des Westmitteliranischen (Parthisch und Mittelpersisch), Vienna: Austrian Academy of Sciences Press, 2014.** ISBN **978-3-7001-7556-8** (print), **978-3-7001-7605-3** (online); 602 pages. The [official publisher record](https://austriaca.at/7556-8) and [online contents](https://austriaca.at/7556-8inhalt) were inspected. Script, sound, morphology and syntax chapters are relevant to our task decomposition. Publisher scope explicitly excludes ninth-century scholastic Zoroastrian literature; therefore it cannot stand alone for the whole Book Pahlavi domain. Contents were accessible but extracted garbled; two linked chapter PDFs returned no readable content through this tool. Full-chapter access and study remain unverified, not proven globally unavailable. The official online edition is the first access route; an available library copy would help if that route remains unusable.
4. **Secondary cross-check: P. Oktor Skjærvø, “Middle West Iranian: Middle Persian and Parthian,” chapter 4 in Gernot Windfuhr (ed.), The Iranian Languages (Routledge, 2009).** The [publisher's contents](https://www.routledge.com/The-Iranian-Languages/Windfuhr/p/book/9780415622356) confirm the chapter and author. Bibliographic identification only: no full chapter read here. This is distinct from the previously unavailable Harvard Introduction to Pahlavi teaching primer.

The existing Persian primer by ژاله آموزگار و احمد تفضلی, زبان پهلوی، ادبیات و دستور آن (Moin, fourth printing, 1382 SH), already has writing-system and grammar coverage recorded in the supplied-book study. Reuse it for Book Pahlavi context rather than asking the user to supply it again. No new book was purchased or added to a training corpus.

## How the findings change the next experiment decision

The earlier finding of only 62 untranslated headings / 260 terms was explicitly about Parsig. It cannot rule out continued pretraining using the project's other archives. TITUS contains a substantial potential reservoir. Arda Viraz, Denkard IV–VII, Madigan-i hazar dadestan, the Middle Persian Psalter and Pahlavi Rivayat provide a concrete bounded starting pool. Its 199,043 raw terms include editorial material and unresolved witness/quotation overlap; the crude extraction result of 146,700 terms is not a cleaned estimate or lower bound. Mixed Parthian material, alternative orthographies and held-out works elsewhere in TITUS must remain separate.

Conversely, we do not yet have enough independently qualified auxiliary labels to justify saying task-mixed training is ready. The 14-record packet checks feasibility, not sample adequacy. The existing grammar datasets have potentially useful labels but incomplete sentence/paragraph identity; unresolved joins can corrupt supervision. MPCD's current access/release gap is not evidence that its internal annotation does not exist.

**Keep two hypotheses live:** translation SFT plus verified lexical/construction supervision; or qualified additional-source CPT followed by unchanged translation SFT. Choose one controlled contrast after its prerequisites are demonstrated. Do not change backbone and training regime simultaneously and interpret the result as a regime effect. The existing Gemma/Qwen inference comparison remains an optional separate operational test, with its launch checks still pending.

## Bounded next actions and stopping rules

1. Cross-check the five contextual forms against a second scholarly dictionary and the appropriate Book Pahlavi convention. Record explicit sense/form correspondence, source page, uncertainty and the exact occurrence. Leave a candidate unresolved when only generic resemblance is available. Keep original bytes. No synthetic Persian target becomes gold through agreement between models.
2. Audit the eight-root TITUS candidate pool in stages: edition/work identity and applicable reuse terms first, then source-language extraction, witness/quotation exclusions and duplication. Unmapped title or absence of an exact eight-term match is insufficient. Report the actual retained size and unresolved fraction before considering CPT; do not build a general scraper or ingest the full archive now.
3. If eligible source quantity or reliable labels support a feasible contrast, freeze objective/token exposure, starting checkpoint, comparison controls, unchanged development measurement and cost/time bounds before cloud launch. Otherwise record the failed prerequisite and use the existing translation/inference option. A specialist review and later independent confirmation are still needed for science-grade correctness claims; provisional development can continue meanwhile.

PAL-REF, its historical scores and the existing 24 DEV cases remain unchanged. TRAIN recall, new combinations and uncertain/unknown forms are different outcomes; none should be collapsed into a single claim of decipherment. No new empirical quality result is reported here. The USD25 cumulative authority and the hold on laptop weight downloads remain in effect.

## Reproducibility and review

Run from the project root:

```powershell
& resources/local/hf-client-venv/Scripts/python.exe -B -X utf8 scripts/prepare_lexical_feasibility.py --check
```

The check reconstructs packet/audit bytes from four pinned inputs and tests rejection of altered source text, quarantined witnesses and held-out works. Packet SHA256: `7791c308a9fd32acb868613a8afa0f0be248776e5ccf5b65b11b45eb491b46a3`. The separate scholarly overlay preserves the initial packet and source-check chronology. Its six entries, seven packet bindings, exact source PDF hash and page locators were checked; it is not part of the packet generator's reconstruction claim.

The [independent critic](REVIEW.md) ran reconstruction and separate byte/span/provenance checks, inspected all five Nyberg images, and recounted/rehashed all 2,351 TITUS extracts. The critic did not independently reproduce the inventory's extraction/overlap heuristic or its work identities. Core preparation passed; source eligibility, philological adjudication, training effectiveness and paid launch readiness remain unproved.
