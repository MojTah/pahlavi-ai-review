# Direct collection run

Started 2026-09-20 20:13 UTC, following the user's instruction to do the setup and use it after IDM collected very little. Classic Codex, one local collection owner. No subagents or external execution service.

The first same-site read-only API test returned the four known groups. Further tests matched record 120's 13 units and revision note and the previously inspected word annotation. The public frontend's authorization is held in memory and sent only to its exact HTTPS API host; it is not copied into source, logs or export manifests. No user account or VPN settings are changed.

## Ready: text corpus phase

Command: `[USER_HOME]\.venvs\codex-science\Scripts\python.exe scripts/collect_parsig.py corpus`

Done: live inventory matches all 126 saved IDs/titles; every offered chapter's paragraph-ID list matches the saved response; original script, transcription, translations and notes retained in JSON with source URL, time and SHA-256. This phase does not claim all word annotations or images.

Source checkpoint: `1f0b38c`. Collector SHA-256: `4a03ffd475ed36e4afa3b3a8d8020e6ebf0914ca12527c2e4798eda716e4dab6`. Site client SHA-256: `01cb5e6e4ec786173b86e1b68024961939686b373b1d9b2a251f8fda4adeec69`.

Host: Windows, shared codex-science Python, standard library only. Writable archive: `sources/local/parsig-2026-09-20/`, excluded from Git. External endpoint: `https://mpdb.parsigdatabase.com/`, GET only, redirects refused. One process and exclusive lock; no scheduled/background owner.

Bounds: 30-minute expected acquisition, warning at 45 minutes, hard timeout 90 minutes per run; sequential requests spaced at least 0.55 seconds, 40-second request timeout, at most 2,000 new requests/run and 500 MB response cache. No automatic request retries. One repair owner. Stop on identity/schema errors and retain verified responses. Reassess before an image or annotation workload exceeds these limits.

Canaries passed: bounded run stopped at eight requests after saving record 120; resumed run reused all eight cached responses and completed records 207, 302 and 506; separate record 137 canary saved three chapters/90 paragraphs. These cover single/multiple chapters, notes, legacy script, Manichaean text and damaged inscription text. All 32 saved response hashes checked, known unit counts matched, and the lock was released. Runtime evidence: local `runs.jsonl`, `manifest.json` and corpus files.

Resume: rerun the same command; cached bytes are verified before reuse. Each response and book file is atomically replaced after a complete write. Ctrl+C or a request limit stops at a resumable boundary; an unclean OS kill may leave the lock and requires process inspection before recovery. No valid cached data is deleted during repair. Remote state is never modified.

Monitor by request/book progress and the run log. Collection never promotes a record to read, analysed or expert reviewed. Supporting pages, images and word inventories follow only after their own sampled responses and sizes are inspected.

## Core result and supporting phase

The full text run completed at 20:27 UTC in 436 seconds: 126 records, 334 chapters, 4,507 numbered units. All 799 core response files are retained and their hashes verified. Layer coverage: original script in 4,343 units, transcription in 4,507, Farsi translation in 4,445, the source field named EnTranslation in 1,792 and notes in 563. These are nonempty field counts, not expert assessment of completeness within a paragraph.

Supporting/image canary completed at 20:28 UTC: 87 new responses, all shared guide pages and tag definitions, introductions and version metadata for records 120, 207 and 506, and five image files totaling 1,237,232 bytes. The expected edition-image IDs 284 and 285 were present; JPEG/PNG signatures and hashes were checked. Empty lists remain evidence of no data offered at that endpoint. Same host, collector identity, lock, cache and stop/resume boundaries as the text run.

Full supporting command: `[USER_HOME]\.venvs\codex-science\Scripts\python.exe scripts/collect_parsig.py images`. It retains Farsi/English introductions, edition/manuscript lists and available page images. The same 2,000-request, 500-MB response-cache and 90-minute limits apply. The image canary established approximately 250 KB decoded per sample image; actual sizes are monitored rather than assumed uniform. No word-detail completion claim follows from this phase.

The generated offline reader passed a browser check: filtering for 120 produced one result, its page contained 13 units and the §11 correction note, and the return link pointed to the local index. A separate cache contract check rejected corrupted bytes and a foreign destination without making network requests. Its first temporary-directory attempt hit Windows sandbox permissions; a normal project-local scratch folder worked. This did not affect the collector or valid archive.


## Final scope correction and text-only continuation

Mojtaba clarified that the requested product is source texts and translations. The image acquisition was stopped; existing incidental files were preserved. No further site pictures, fonts or style assets were gathered.

The misleading `EnTranslation` field was classified from book introductions, source-language samples and explicit Persian note markers: 916 units contain English translations, 843 French translations and 33 Persian notes. The original responses remain unchanged. The source-unit export retains original identifiers, every raw field and exact provenance.

All nonimage supporting endpoints completed at 21:08 UTC: 1,024 new requests and 303 verified cache reuses, with 2,390 cached responses overall. That overall count includes 252 previously captured image responses; **2,138 responses are nonimage data/metadata**. All 126 records' introduction endpoints and chapter version metadata were visited. Empty source responses stay empty.

The optional private-inscription grammatical index contains 406 forms and 1,135 occurrences. The first full-group query timed out after 40 seconds. Full per-word annotation acquisition is not complete and is not counted as text acquisition.

Additional text-only collection follows explicitly selected TITUS, Avesta.org, Berkeley, Oxford and Raham Asha sources. Every saved response has source URL, time, byte count and SHA-256. One owner per collection; requests admitted at least 0.55 seconds apart. TITUS later used two requests in flight after a bounded cached canary and transport-recovery check. Public collection runs have a 60-minute bound, maximum 1,800 requests for TITUS and smaller limits for other sets. Failures are recorded; no blind automatic retry. A single reviewed recovery retained previous errors. One 50.8-MB Pazand book exceeded the initial 40-MB per-file limit; its bounded retry used a 128-MB limit. PDF extraction preserves page numbers and flags missing text; it does not invent OCR readings.

Reproducible final checks and current acquisition totals are in `data/collection-status.json`. Downloading is not linguistic study or model training. No remote state is modified.

## Independent TITUS download

At Mojtaba's request, `downloads/Start-Text-Download.ps1` starts the existing Python collector as a hidden Windows process with independent stdout/stderr logs. It needs no installation and does not change IDM, VPN settings, services or scheduled tasks. The launcher refused a duplicate start while the collector lock existed. Its process record is `background-process.json`; the Python worker's own PID and outcome are in `run-status.json`. A Windows virtual-environment launcher can have a different PID from the actual worker.

Before starting, a narrowly scoped OS process inspection confirmed that the interrupted previous collector had exited. Only its stale lock was removed; saved source data remained intact. The first launched run ended with 1,620 retained documents and two transport errors. Both specific failures were recovered once, preserving their earlier errors. The restarted run also seeds every Dēnkard VI section explicitly from the observed chapter-index navigation rule and its 613 options, avoiding dependence on a single next-page chain. The index hash and URL derivation are retained in `sources/titus-collection.json`.

Validation of the completed external collections passed all retained byte-count and SHA-256 checks. All 32 PDF text files parsed as UTF-8 JSONL with the recorded page counts. Final verification must wait for the active TITUS owner to finish; it checks the lock, final run state and catalogue/manifest counts.

## Final collection result

The independent TITUS run completed with 2,351 files / 54,201,387 bytes and zero unresolved requests. These include 2,183 numbered content pages and 168 navigation/index files across 28 selected collections. All 613 indexed Dēnkard VI sections are present. The final run reused 2,098 cached responses and made 254 requests, including bounded transport recovery.

Recurring connection resets justified one retry per interrupted connection, enabled only by the launcher's explicit flag. The collector waits two seconds and preserves the first failure. It never automatically retries HTTP errors or a request already carrying an earlier attempt. Local injected-failure checks passed for recovery, cache reuse, no HTTP-error retry and no third attempt after persistent failure. The initial temporary-directory test hit the previously observed Windows sandbox permission issue; the same checks passed in an ordinary project-local scratch directory. The final real run exercised the recovery path successfully. No request, time or concurrency limit increased.

Offline verification passed source byte counts and SHA-256 hashes, 4,507 unique Parsig units, 126 books / 334 chapters, 152 Berkeley document IDs, 158 Oxford IDs, PDF source associations/page counts, and mixed-language regression checks. The source index contains 2,916 records, including navigation and metadata-only records explicitly labelled in the guide. Sixteen historical failed URLs are retained: 15 Avesta.org links and one superseded Berkeley exploratory route, resolved through DTS. A shared PDF across two sources is flagged as an exact duplicate.

No downloader remains active at this checkpoint. Acquisition is finished for the selected accessible inventories, with the documented MPCD, unavailable-link, scanned-page and word-annotation gaps. Linguistic study, OCR, alignment, training and translator development remain separate future work.
