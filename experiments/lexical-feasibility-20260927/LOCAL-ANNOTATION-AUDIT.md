# Local lexical/construction annotation feasibility audit

27 September 2026. **Five exact qualified source spans can seed a small review packet; zero independently published word-sense/POS labels are admitted as training gold by this audit.** The draft dictionary is explicitly authored as Codex source-assisted study analysis. Passage qualification does not independently validate its inferred lexical senses or grammatical explanations.

## The exact five original-TRAIN-only entries

Offsets below are zero-based Unicode codepoints, end exclusive, in the exact qualified TRAIN `text` field. The metadata JSON binds each field to file hashes, row numbers, corpus JSON pointers, edition/translator credit and final-ledger qualification pointers; it does not copy proposed word meanings.

| Entry | Cited record(s) | Current decision | Admitted exact form/span | Edition |
| --- | --- | --- | --- | --- |
| `mp-hunsandih-n` | `parsig:119000001`, `parsig:119000002` | **Partial only:** first record is QUARANTINED; second is ELIGIBLE_WITH_QUALIFICATIONS | `hunsandīh`, 119000002 `[68,77)` | Jamasp-Asana 1913 p.154 |
| `mp-xrad-n` | `parsig:107000001` | Source span eligible; draft lexical/POS labels need independent review | `xrad` `[16,20)` | Jamasp-Asana 1913 p.40 |
| `mp-frazand-n` | `parsig:107000003` | Source span eligible; draft lexical/POS labels need independent review | `frazand` `[14,21)` | Same |
| `mp-xwastag-n` | `parsig:107000004` | Source span eligible; draft lexical/POS labels need independent review | `xwāstag` `[14,21)` | Same |
| `mp-ruwan-n` | `parsig:107000006` | ELIGIBLE_WITH_QUALIFICATIONS; preserve the published explanatory qualification | `ruwān` `[25,30)` | Same |

The source Persian translations are credited to Goshtasb and Hajipour, 1398 SH in the retained records. The four work107 entries explicitly say that occurrence-level word annotation and manuscript collation were not checked. Their published passage targets can supervise the already qualified whole-passage task; the draft's narrower noun senses, POS and possession-construction analysis are project inferences. They must not be relabeled as a published lexical dictionary.

`119000002` retains a reconstructed numeral and elliptical syntax; `107000006` retains the distinction between literal possession wording and the translator's care-of-soul interpretation. Exact qualifications are in the ledger pointers. The five surviving source texts are distinct, but four share one work and a repeated construction; they are not five independent construction families.

Eleven other dictionary entries cite held-out work120, including mixed-source `mp-weh-adj`, and are rejected wholesale for this packet. The JSON lists only their entry/work IDs and rejection status. Do not import related-entry links or the complete dictionary object into training: `mp-hunsandih-n` also links to another draft entry with held-out witnesses.

## The one saved explicit word annotation

`sources/local/parsig-2026-09-20/canary-sentence_detail_119000001003.json` is an upstream Parsig occurrence detail, not a Codex-generated POS label. It has transcription, transliteration, translation, category, lemma and two reference fields, and belongs to occurrence **119000001003 / paragraph119000001**. Its source lemma field differs from the draft's derived headword, a distinction the draft preserves.

**Reject it from the current qualified packet:** paragraph119000001 was quarantined for unresolved clause negation. This audit does not override that disposition. The word's individual label has not thereby been disproved, but admitting an isolated annotation from that quarantined witness would require an explicit separate adjudication. Never transfer this occurrence-specific annotation to qualified paragraph119000002 merely because the same form occurs there. This leaves zero directly retrieved word-detail annotations admitted under the current qualified-row rule.

## Other existing local annotation resources

| Resource | Verified local evidence | Legitimate use / current outcome |
| --- | --- | --- |
| Parsig `vocabulary-group-2.json` | 406 forms, 1,135 occurrences, 97 distinct paragraph IDs, 25 works; **zero** parent-ID matches in original TRAIN or qualified TRAIN | Source occurrence/category indexing. No admitted TRAIN word senses or context labels. |
| `ezafe-modeling-mp` archived CSVs | LR inputs/features/target each 23,234 rows; RF inputs/features each 8,468 rows. Lemma/form, POS, dependency and ezafe columns exist. | A real project-derived construction-label resource worth a separate provenance join; **HOLD**, not current TRAIN-only supervision. |
| UD Middle Persian–MPCD snapshot | Manifest lists only LICENSE, README and stats.xml; **zero CoNLL-U files** | No local token annotations to admit. |
| ParsiPy selected snapshot | `stems.csv`: 6,925 rows (header status not inferred), two columns; transition table 15×15; emission table 7,261×15. No witness/context identifiers in these headers. | Lexical/spelling/POS-tool support, not independent word-in-context supervision. MIT tool licensing does not create passage-level TRAIN provenance. |
| Berkeley / Invisible East archives | Manifest/index structure provides document identities, credits and edited text layers, not an already matched qualified-Parsig token-label packet | Potential separately curated published context; no cross-archive deduplication or TRAIN membership established here. **HOLD**. |
| `kb/grammar.md`, `kb/glossary.md` | Grammar metadata explicitly names original TEST record152008001; the glossary has no admitted witness-level split ledger | Reject wholesale ingestion. General exposition and source-assisted study glosses are not gold context annotations. |
| Retained scholarly dictionary PDF | `sources/A-Manual-of-Pahlavi-II-Dictionary.pdf` exists as a published lexical reference | Candidate independent lexical corroboration, not a pre-extracted, occurrence-aligned TRAIN dataset. No new senses or PDF-body review performed here. |

The ezafe README attributes its raw annotated Zoroastrian corpus to MPCD and says the raw CoNLL-U is not distributed in that repository; it declares MIT for the project. The retained CSVs identify 12 source files but **have no sentence/paragraph/record ID column**. `(source_file, nominal_head_id, dependent_id)` collapses 23,234 LR rows to 4,997 keys and 8,468 RF rows to 2,404 keys, so token IDs repeat and do not locate unique contexts. The RF tables each contain only 8,445 exact distinct full rows (23 duplicate excess rows). LR feature/target and RF input/feature views must not be counted as independent annotations; neither can the two model tables simply be added as unique training examples. Source-file abbreviations require a manuscript/work crosswalk and exclusion of all held-out/parallel witnesses before any linguistic labels are opened for a candidate packet.

## Practical packet boundary

Use the five positively qualified source spans above with their full unchanged source context, published passage evidence, citation, review limitations and exact hashes. Present existing draft labels as **hypotheses to adjudicate**, not accepted supervision. Keep the quarantined occurrence, 11 work120 entries, unjoined external CSV labels and general KB prose outside the packet. No new lexical meanings, source repairs or admission exceptions were created.

The exact source metadata and hashes are in `LOCAL-ANNOTATION-AUDIT.json` (SHA256 `ebdf52fb852f2e69879bbd36796b3e2bb7f779704f0a8667c99dfc84ac721336`). Qualified TRAIN remains SHA256 `15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc`; final ledger remains `d79af2e64fbb92954c8b8d0ed9cb7a34e7e7d24d4c22ea9c22f1da6d569a8e77`.

Boundary disclosure: the initial legacy lexicon-review read exposed mixed TEST-work120 discussion before filtering. None of those labels or passages is reused in these outputs. This audit is therefore a preparation/provenance note, not an independent blind assessment. No benchmark reference file, model prediction, network, cloud action, installation or source-data change occurred. Only this report and its metadata companion were written.
