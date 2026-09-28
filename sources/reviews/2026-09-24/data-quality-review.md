# Independent data and study-coverage QA — 24 September 2026

RESULT: PASS for the bounded audit; PARTIAL for corpus readiness. This is a read-only audit of source data. Only this report was written. No downloader, corpus generator, model training, installation, Drive access, or core-file edit was performed.

## Fresh verification

The independent Python checks used the shared science interpreter and standard library. All **5,047 successful manifest response entries** matched their recorded byte lengths and SHA-256 hashes: Parsig 2,390; Avesta 98; Berkeley 159; ezafe research 7; Invisible East 6; Perso-Aryan 33; TITUS 2,351; UD metadata 3. These are manifest entries, not unique text passages. The retained Parsig export hash remains `c42e0a5a0d4d108218a0481ca073c07c6bb00cdcba0bffb462b67bb6d7a60789`.

The existing `scripts/verify_collection.py` was inspected but **not executed**: despite its verification name it writes book metadata, the document catalogue, and collection status. Independent read-only checks avoided those mutations. One console encoding failure occurred after successful hash/count checks; UTF-8 output fixed the remaining reporting check. No failed hash or data-integrity check occurred.

| Collection | Verified retained coverage | Meaning and limit |
|---|---|---|
| Parsig | 126 records; 334 chapters; 4,507 unique source units | All 4,507 have nonempty transcription fields; 4,343 have original-script fields; 4,445 have nonempty Farsi fields; 563 have notes. Field presence does not establish usable translation. |
| Parsig additional translation field | 916 source units classified English translation; 843 French translation; 33 Farsi commentary | There are 919 English layer entries and 847 French entries because some units contain multiple entries. Retain the **unit** wording for 916/843. |
| OpenAMPD | 152 documents | Declared layer counts are 151 transliteration, 129 transcription, 58 German, 51 English and 16 French. **Nonempty** counts are 149, 127, 56, 51 and 16, respectively. |
| Invisible East | 158 catalogue records | 14 records have transcription and translation; 10 have transliteration. Folio-layer counts are 16, 16 and 12, respectively. The other 144 catalogue records are not translation examples. |
| Avesta.org | 98 documents; 13 PDFs / 2,221 pages | 1,719 PDF pages meet the 40-letter extraction threshold; 502 do not. Fifteen unresolved URL failures remain recorded. |
| Perso-Aryan | 31 documents; 19 PDFs / 1,605 pages | 1,465 pages meet the extraction threshold; 140 do not. The 33 verified responses include discovery indexes. |
| TITUS | 2,351 HTML files; 2,183 numbered content pages | 168 other HTML files are not numbered passages. Mostly transcriptions, not complete parallel translations. |

The aggregate 32 PDFs / 3,826 pages is before deduplication; 3,184 pages meet the extraction threshold and 642 do not. That threshold measures presence of extractable alphabetic characters, not clean Pahlavi text, OCR accuracy, or translation availability.

## Important content-quality distinctions

1. **Four confirmed Farsi fields contain credit only:** `parsig:110000007`, `parsig:110000010`, `parsig:110000021`, and `parsig:124000003`. Each contains only the Gashtasb/Hajipour 1398 attribution. Keep 4,445 as the raw nonempty-field count; do not present it as the count of useful translation pairs. The first two contain Avestan quoted text; 110000021 is a colophon; 124000003 is also Avestan. The scan establishing these cases was not a complete semantic audit of every field.
2. **Record 124000001 is fragmentary and uninterpreted in context:** its Farsi field lists disconnected word renderings. A fluent synthetic reconstruction would falsely conceal the unresolved source reading.
3. **OpenAMPD has empty declared layers:** MP0424 / Berlin 24 and MP0504 / Tehran E contain empty transliteration, transcription and German-translation TEI divisions. Count these as declared markup only. Preserve original XML. Only **46 of the 51** documents with nonempty English translation also have nonempty transcription; the other five require a different source-layer path. Document-level layer co-presence is not sentence alignment.
4. **`EnTranslation` is not an English-only source field.** Samples from all books carrying that field were inspected: French in records 117, 136 and 152; Persian note-marked commentary in numerous records; English in the separately enumerated source books. The exporter uses inspected book-level language assignments and explicit note markers. This supports the recorded classifications, not exhaustive linguistic validation of every segment. No majority-Persian-script outlier was found among the Farsi fields; that check cannot detect wrong meanings or credit-only entries.
5. **Mixed languages remain:** 75 Parsig units belong to six explicitly mixed Middle Persian–Parthian records (504, 505, 526, 538, 542, 556). This is a record-level caution, not proof that every unit is mixed. A further 4,107 units carry the general Middle Persian/possible Avestan-quotation warning, and 325 are labeled Middle Persian. TITUS also includes three selected mixed Manichaean collections. Language filtering must work at the passage level.
6. **Deduplication is incomplete by design:** the identical SGV PDF at Avesta and Perso-Aryan is recorded; the two Nyberg PDFs are copies of the same work even when byte hashes differ. Related witnesses, editions, translations and cross-site reprints must be grouped before any future held-out evaluation. Hash deduplication alone is insufficient.
7. **Script is not plain Unicode transcription:** retained legacy Book Pahlavi strings require the source font/convention. They must not be silently treated as modern Farsi or as decoded manuscript input. PDF text extraction and downloading do not resolve this.

## Baseline study coverage and stale statements

Before this parallel review, the live inventory records seven studied records and 52 units: 101 (4), 120 (13), 107 (8), 119 (10), 302 (10), 207 (2), and 506 (5). The other 119 were collected but not marked read. This verifies the **recorded study ledger**, not independent proof of mastery. Today's new verified readings should be added separately, only by the lead after checking delivered evidence.

Exact stale locations found at audit start:

| File/location | Existing statement | Required correction |
|---|---|---|
| `kb/parsig-database.md:14` | Five records / 31 units / 121 inventory only | Identify as historical or replace with current inventory-backed study coverage and collected/unread wording. |
| `kb/parsig-database.md:61` | Five live readings; no bulk export performed | Historical claim conflicts with the completed acquisition if read as current. Label its date or update it. |
| `kb/parsig-live-study.md:21` | Six records / 44 units / 120 inventory only | Baseline was already seven / 52 / 119 collected unread. Add today's changes only after source review. |
| `kb/translation-study.md:48` | Five read / 121 remaining | Reconcile with the study ledger and today's verified increments. |
| `kb/study-status.md:1,21,44` | Data gathering; no subagents; study deferred | These correctly describe the old checkpoint but not today's authorized parallel study. Date the historical baseline and record current scope. |
| `data/README.md:61` | Next phase requires direction | Direction to resume Pahlavi study has now been given. Translator design/training remains separate. |

`kb/parsig-live-study.md:118` says twelve dictionary entries for that specific earlier study; the project total is sixteen. This is not necessarily contradictory if explicitly tied to that checkpoint/subset. Avoid mechanically changing all occurrences of twelve.

## Readiness matrix

| Dimension | Supported status | Missing evidence |
|---|---|---|
| Collected | PASS for the inspected local snapshot inventories and fresh manifest integrity | No claim of all surviving Pahlavi, all online sources, complete MPCD export, complete word annotations, or all broken-link recovery. |
| Actually read | PARTIAL: baseline seven Parsig records / 52 units plus the separately recorded books/articles at stated depth; today's new reviews require integration | Most collected material was not in the baseline study ledger; whole dictionaries and grammars remain unread. |
| Linguistically validated | PARTIAL at explicitly discussed examples only | No full-corpus expert review, complete script decoding, semantic field validation or verified sentence alignment. |
| Translation evaluated | NOT ESTABLISHED | No independent expert-scored held-out Pahlavi-to-Farsi/English translation test. No valid numerical accuracy score exists. |

The defensible outcome is a stronger, source-backed study knowledge base with documented gaps. It is not a trained or complete translator and not permanent model-weight learning. Recommended next evidence is a small genre-diverse, source-located reading set with agent, negation, modality, technical-term and damaged-text checks, then independent specialist evaluation before any accuracy claim.

## Timing and handoff

Audit completed within the assigned 10-minute expected window. Main extra cost was reading and hashing 5,047 retained response entries; no new downloads occurred. Risks and corrections were sent to the lead during the audit. Ready for independent read-only QA of the lead's integrated notes and ledger.
