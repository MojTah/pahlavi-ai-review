# Collected Middle Persian source data

Collection date: **20 September 2026**. This checkpoint gathers published source texts and available translations for later study. It does not build a translator, align training sentences, or train a model.

The [collection status](collection-status.json) contains verified counts, failed URLs and exact PDF duplicates. The [document index](document-index.jsonl) locates source records. Paths in that index are relative to the project root. Original downloads are local and excluded from Git; a Git checkout alone does not contain the corpus.

## Coverage

| Collection | Retained material | Translation coverage and limits |
|---|---|---|
| Parsig Database | All 126 reader records, 334 chapters, 4,507 numbered units; introductions and edition metadata | 4,445 nonempty Farsi translation fields; 916 English translation units; 843 French translation units; 33 additional Farsi commentary units |
| Berkeley OpenAMPD | All 152 documents advertised by the inspected DTS catalogue, with original XML and editor credits | Declared layers: 151 transliteration, 129 transcription, 51 English, 58 German, 16 French. The 24 September content check finds nonempty counts of 149, 127, 51, 56 and 16 respectively; layers overlap |
| Oxford Invisible East | All 158 Middle Persian catalogue records offered by the inspected language filter | 14 records contain transcriptions and translations; 10 have transliterations. The other records are metadata, not translation examples |
| Avesta.org | 98 selected HTML/PDF documents, including 13 PDFs | Pahlavi editions and translations; source languages and overlapping editions require separation |
| Perso-Aryan Studies | 31 selected HTML/PDF documents, including 19 PDFs | Raham Asha editions, translations and supporting references; some material is Avestan, Pazand or influenced by New Persian |
| TITUS | 28 selected text collections: 2,351 HTML files, including 2,183 numbered content pages; no failed requests remain | Mostly source transcriptions. Three selected Manichaean collections mix Middle Iranian languages; 168 navigation/index files are not passages |
| ParsiPy and supporting repositories | Previously saved lexical files; credited software references; additional grammatical feature tables | Linguistic support, not a newly validated parallel corpus. The inspected UD Middle Persian repository offers metadata but no CoNLL-U files |

Counts are **source records or source fields**, not unique ancient works, human-checked translations or sentence pairs. Archives overlap. The same *Šak-ud-gumānīh-vizār* PDF occurs at both Avesta.org and Perso-Aryan Studies; its identical hash is recorded. Different editions or transcriptions must not be merged merely because titles resemble each other.

## Files to use

| Data | Location relative to the project root |
|---|---|
| Parsig source-unit export | `sources/local/parsig-2026-09-20/exports/text-units.jsonl` |
| Parsig book introductions and source metadata | `sources/local/parsig-2026-09-20/exports/book-metadata.json` |
| Parsig per-record original fields | `sources/local/parsig-2026-09-20/corpus/` |
| Parsig coverage | `sources/parsig-text-coverage.json` |
| Other collections | `sources/local/public-texts-2026-09-20/<collection>/` |
| Berkeley extracted layers and XML references | `sources/local/public-texts-2026-09-20/berkeley/documents.json` |
| Oxford text, translation, bibliography and editors | `sources/local/public-texts-2026-09-20/invisible-east/middle-persian.json` |
| HTML text extraction and page provenance | `<collection>/documents.json` and `<collection>/text/` |
| PDF page text | `<collection>/pdf-text/*.jsonl` and `<collection>/pdf-text-coverage.json` |
| Exact downloads and SHA-256 manifest | `<collection>/raw/` and `<collection>/manifest.json` |
| Previously supplied PDFs and lexical resources | [Existing resource guide](../resources/README.md) and [supplied-PDF study](../kb/supplied-pdf-study.md) |
| Attribution | [Credits](../CREDITS.md), retained introductions, XML contributors and individual source editions |
| Access and extraction gaps | [External access record](../sources/external-access-gaps.json) |

The Parsig export preserves every raw source field and separates derived language labels. The source field named `EnTranslation` is **not uniformly English**. No translation was generated to fill a missing field. Original script strings can use legacy font conventions, especially Book Pahlavi; transcription and original script are separate layers. Numbered source units include headings and colophons.

**Content review, 24 September:** the raw 4,445 populated Farsi fields include at least four attribution-only fields: `110000007`, `110000010`, `110000021` and `124000003`. Field population is not a usable-translation count. Record `124000001` also contains an uninterpreted fragment. OpenAMPD documents `MP0424` and `MP0504` have empty declared transliteration, transcription and German layers; only 46 of its 51 English-translated documents also contain nonempty transcription. These observations qualify the original collection snapshot without changing its raw source files or historical counts. [Independent audit](../sources/reviews/2026-09-24/data-quality-review.md).

The transcription field is also a source label, not a guarantee of Middle Persian running text: `225001001` and `225002001` contain Persian editorial notes, while other units quote Avestan or belong to mixed Middle Persian/Parthian records. Reading all saved fields does not turn every unit into a Pahlavi translation example. These exceptions and edition disagreements need passage-level review before future alignment.

PDF extraction covers **32 PDF files / 3,826 pages** before cross-source deduplication. **3,184 pages contain at least 40 alphabetic characters; 642 have little or no extracted text.** Two Pazand books are wholly scanned. These pages need separate OCR/transcription work before becoming usable text. Extraction did not perform OCR. Eleven pages in the Avestan grammar PDF needed invalid Unicode surrogate handling; replacement characters and the escaped original extraction are retained for review. The PDF remains unchanged.

## What remains unavailable or unprocessed

- MPCD opens in the normal browser, but a complete corpus/translation export was not obtained. Command-line requests returned HTTP 418/500. Its preliminary annotations and working translations require attention to the source's editorial notice.
- Fifteen Avesta.org links returned errors, mainly old chapter/navigation links. The manifest records exact failures. Berkeley's one failed exploratory URL was superseded by successful DTS acquisition of every listed document.
- Full Parsig word-by-word annotations were not collected. The private-inscription index has 406 forms and 1,135 occurrences; a broader query timed out. This does not reduce the completed reader-text inventory.
- Scanned pages, legacy-script decoding, PDF layout cleanup, language separation and sentence alignment remain future preparation work. No expert linguistic review has been performed on the full collection.
- Collection is limited to the inspected, accessible source inventories. It does not establish that every surviving Middle Persian text or every online translation has been gathered.

Source editions retain their own licenses and credits. Public access alone does not establish permission to redistribute a commercial dictionary or use every edition for training. [Credits](../CREDITS.md) records the observed notices without assigning one blanket license to the combined corpus.

## Independent downloader and verification

Run [Start-Text-Download.ps1](../downloads/Start-Text-Download.ps1) in PowerShell to continue the selected TITUS download outside Codex. It uses the already-installed shared Python, starts a hidden process, and writes its process record, progress logs and `run-status.json` under the TITUS archive folder. It verifies and reuses cached downloads. No installation or IDM setup is needed.

One process owns each collection. A lock prevents overlapping writers. Each TITUS run permits at most 1,800 new requests and 60 minutes, with at most two requests in flight and at least 0.55 seconds between admissions. The launcher allows one retry for a reset connection, unexpected TLS EOF or disconnected remote response; previous failures remain recorded. It does not retry HTTP errors or failures that already had a retry. An unexpected Windows termination can leave a lock: verify the recorded process has exited before recovering it.

After collection completes, run `C:\Users\mojta\.venvs\codex-science\Scripts\python.exe scripts/verify_collection.py` from the project root. It checks retained file sizes and SHA-256 hashes, source identifiers, document totals and language classifications, then rebuilds the catalogue and status report. Verification checks data integrity and recorded coverage, not translation accuracy.

**Current direction, 24 September:** Mojtaba authorized renewed Pahlavi study with parallel agents. [Study status](../kb/study-status.md) records the reading coverage and remaining gaps. Dictionary/translator implementation and training remain separate future work. The authored knowledge base is the durable study record; downloading or reading is not model training.
