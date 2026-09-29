# MacKenzie dictionary: public lookup and PDF reading evidence

28 September 2026. Read-only public source inspection; no credential, paid job, bulk extraction, training admission or change to the frozen evaluation.

## Verified access and identity

The official [MPCD glossaries page](https://www.mpcorpus.org/glossaries/) links [Kosh](https://www.mpcorpus.org/kosh/) and identifies MacKenzie and Daniel Kölligan's 2012 Cologne Pahlavi-English dictionary resource. The glossary page was indexed by web search but direct web retrieval returned403. Its linked Kosh interface loaded in Chrome and returned dictionary entries with only `cpd` selected. This establishes an access route, not equivalence with every part of the 1986 corrected print edition.

The interface exposed the exact [structured xrad query](https://kosh.uni-koeln.de/mpcd/cpd/restful/entries?field=trc&query=xrad&query_type=wildcard&size=20). One ordinary unauthenticated GET at11:44:20 UTC returned200 and578 bytes of JSON. The raw response is `xrad-response.json`; `xrad-receipt.json` records URL, timestamp, content type and SHA256 `ccc387439b5c8860354c4f52a509cc76d557fc460072880aa76b61cc7496ca25`. The request had a25-second timeout and1MiB response bound.

## Concrete extraction hazard

The entry's simplified fields contain two transcription groups, `xrad` and `xradīg, xradōmand`, but only one scalar sense, `wise`. Its full XML preserves two successive form/sense groups:

| Form group | Following XML sense |
|---|---|
| xrad | wisdom, reason |
| xradīg, xradōmand | wise |

Assigning the simplified sense to every displayed form would incorrectly label the noun `xrad` as `wise`. Preserve raw XML and verify form/sense boundaries, derived forms and language-specific evidence. This single specimen does not establish a general parser for the full dictionary. No extraction framework or new dependency was added.

The English meanings here are source evidence. They are not newly certified Persian translation targets, full-sentence supervision, or evidence of improved model performance.

Independent read-only critic `/root/nllb_final_preflight_review` verified the578-byte response hash, receipt and ordered XML form/sense relations. It returned PASS for one-entry access and label-integrity evidence only; bulk completeness and training readiness are expressly outside that verdict. Receipt SHA256: `4fdcaea5279af7e3b70356c114e1ca0fcece8a5053eb78b02f41c0c14200a730`.

## Prior training and remaining work

The current2237 qualified rows contain no explicit MacKenzie credit in their serialized fields. Four archived notes associated with qualified work151 records cite MacKenzie indirectly:151004012,151039031,151056008 and151056011. This does not prove absence of historical influence; it establishes that a complete, directly attributed dictionary extraction was not part of the current training package.

Before acquisition can contribute to the next dataset: establish full resource coverage and edition details, inspect the supported export/access method and use terms, preserve all entry structures, qualify any Persian targets, separate generic lexical entries from quoted contextual examples, and enforce existing held-out work/witness exclusions. Dictionary rows must not overwhelm whole-clause training or be counted as independent sentence attestations.

Follow the consolidated [dataset-readiness gate](../../DATASET-READINESS.md). Finish all known high-value source dispositions and freeze the resulting dataset before choosing one controlled training comparison. Adding this resource alone must not trigger retraining.

The older [book-access note](../lexical-feasibility-20260927/BOOK-ACCESS-FOLLOWUP.md) remains a correct record of the failed legacy links on27 September. Later observations below supersede its lookup and local-PDF gaps; neither book has been read in full or ingested as training data.

## Bounded resource acquisition, after the working entry canary

The [official Kosh API documentation](https://kosh-docs.vercel.app/apis) documents wildcard queries, the requested result `size`, and preservation of full XML in REST entries. The Kosh homepage redirects to that documentation site. The dictionary-specific Swagger page returned HTTP500; this is an observation of that page, not a failure of the previously verified entry endpoint. The public sample `cceh/kosh_data` repository lists unrelated dictionaries and is not a discovered CPD export.

The planned ordinary unauthenticated `trc=*`, wildcard, size10000 request against the verified CPD entries endpoint was executed once. Purpose: source acquisition and structural audit, with a proposed raw capture in ignored `sources/local/mackenzie-kosh-20260928/`. Limits were25-second socket timeout,60-second total read deadline,25MiB body, no automatic retry, no credentials, publication or training admission. It returned **HTTP500 immediately**, so no complete capture was written. Fewer than10000 returned unique entries would only have avoided this requested cap; it would not prove print-edition completeness or coverage of unindexed forms.

One known-good `xrad` query was rechecked at11:56:48 UTC to distinguish a bulk-query problem from broader access failure. It returned **HTTP403: Request forbidden by administrative rules**; see `canary-recheck.json`. No further API requests, alternate-host/protocol attempts or prefix/ID sweeps followed. The earlier200 is historical one-entry evidence, not a statement that access still works. The public glossary catalogue remained readable in Chrome; its search page displayed no dictionary choices. Both research tabs were closed.

Read-only critic `/root/nllb_source_method` inspected upstream Kosh revision `a79cd742e9140b42aa7b5beb1050b8cbd5eca53e`. [REST](https://github.com/cceh/kosh/blob/a79cd742e9140b42aa7b5beb1050b8cbd5eca53e/kosh/api/restful.py#L68-L86) accepts field/query/type/size but no pagination; [search](https://github.com/cceh/kosh/blob/a79cd742e9140b42aa7b5beb1050b8cbd5eca53e/kosh/elastic/search.py#L35-L61) slices the result and catches search exceptions. That code does not establish a simple size-limit explanation for the500. Deployment revision/configuration is unknown, and upstream differs from the public guide in defaults. The synchronization feature consumes source repositories; it does not identify a public CPD XML export.

**Disposition at that observation:** bulk acquisition unavailable; preserve the specimen and continue local source qualification. No contact was sent and no source was admitted. The user was given the ordinary Kosh page and exact20-result `xrad` link to check normal browser access themselves. Later browser/PDF evidence follows.

## Later user-directed Chrome check and PDF route

After the user opened Kosh in Chrome and requested inspection, root checked that exact user-owned tab. Its dictionary catalogue loaded. Root selected only CPD and searched `xrad`; the first snapshot showed no results, but the completed asynchronous response returned the same form groups and simplified `wise` sense. **Normal browser lookup therefore worked again at this later observation.** This does not explain the earlier direct403, guarantee stable bulk access, or establish that any access control was changed. No token, proxy, login or endpoint workaround was used. The user-owned tab remains open.

The user explicitly asked to read the actual PDF. No MacKenzie PDF was found in the project's existing `sources` or `resources/local` filenames. The public Parsianjoman catalogue links a Persian scan and an English scan; both returned valid PDF bytes and were saved for local study. [Acquisition receipts](pdf-access.json) record exact URLs, timestamps, sizes and hashes. The Persian scan contains422 pages; the English scan259. Their title/copyright images confirm the editions below. The hosting page's criticism of the Persian translation is not treated as an independently established error count.

Raw PDFs remain in ignored `sources/local/mackenzie-pdf-20260928/`; no publication or cloud transfer occurred. Copyright notices are retained and no blanket training/redistribution license is inferred. This changes **book reading access**, not dataset readiness. Root assigned separate bounded English and Persian source-inspection tasks to `/root/seen20_blind_a` and `/root/seen20_blind_b`, with scratch render paths only and no authority to edit the training set. No OCR package was installed: existing `pypdf`, `pypdfium2` and Pillow are available; an initial root `fitz` import failed before reading or changing any PDF.

## Completed parallel PDF inspection

Both reviewers verified file hashes against the receipts and inspected page images: **PASS for source identity and bounded reading; PARTIAL for extraction feasibility.** Root also visually checked both `xrad` pages. The reviewers inspected different editions independently, not every page twice. No full lexicon was extracted or validated.

| Evidence | English: `/root/seen20_blind_a` | Persian: `/root/seen20_blind_b` |
|---|---|---|
| Edition from images |MacKenzie, Oxford University Press, first1971; corrected reprint1986 |MacKenzie, translated by مهشید میرفخرایی; پژوهشگاه علوم انسانی و مطالعات فرهنگی, Tehran1373, first printing |
| All-page `pypdf` census |259 pages;253 with text and at least100 characters;368711 total characters |422 pages;0 embedded-text pages;0 extracted characters |
| Dictionary boundaries |PDF23–122 / printed1–100 |Starts PDF23 / printed27; reverse section starts PDF169 / printed175; pagination offset varies |
| Other sections checked |Corrections PDF19–22; English index123–163; appendix164–165; Pahlavi key167–258 |Translator introduction PDF5–6 / printed7–8; reverse-index sample171 / printed177 |
| Lexical sample images |PDF23,116,122; introduction13–14 and symbols18 |PDF25–26 / printed29–30 and PDF160 / printed164 |

English zero-text pages:4,6,11,17,166,259. PDF11 is a populated script table, not blank. The key's alphabetical direction differs from normal PDF reading order. Handwritten additions/check marks in the English scan are not printed source text. Persian sample scans are one-bit1264×1929 images; visual reading works despite having no embedded text. No new OCR engine was run.

**Cross-edition lexical check:** English PDF116 / printed94 and Persian PDF160 / printed164 both distinguish `xrad` (wisdom, reason; خرد، عقل) from subordinate `~īg, ~ōmand` (wise; خردمند). Expanding the tilde yields `xradīg, xradōmand`, not two independently printed full headwords. The English OCR corrupts the bracketed spelling and diacritics; text extraction can locate entries but cannot certify them. This is lexical evidence, not a new translation score or proof of novel training coverage.

**Mandatory corrections:** the English main page94 retains `xūkar(ag)` and the older animal identification; PDF20 changes the headword to `hūkar(ag)` and the animal sense, and PDF22 deletes the earlier entry. Main pages alone would therefore introduce superseded data. No correction for the three checked `xrad` forms was found in PDF19–22. Persian PDF6 / printed8 states that1986 changes were incorporated into its main text; the statement alone is not an entry-by-entry audit.

Preserve parent/subentry links, variant parentheses, alternatives, bracketed spellings and comparative evidence, and `*` uncertainty. Keep the reverse index and Pahlavi key separate from main entries. Prefer available full structured website text; where only page images are available, retain complete entry images, both page numbers, coordinates, raw readings and correction provenance, then check available OCR against independently verified readings before scaling. Full coverage, linguistic qualification, lineage and held-out quotation checks remain required before dataset admission.

## User-requested website cross-check

Root used normal Chrome search with CPD alone while the two PDF reviewers checked the printed evidence independently. [Exact online observations](website-crosscheck.json) preserve two successful entry families and one unconfirmed lookup, with timestamps and XML from the visible page. This is a targeted check, not a random accuracy estimate or complete-edition certification.

| Case | Website observation | Cross-check conclusion |
|---|---|---|
| `xrad`, `xradīg`, `xradōmand` |Full XML preserves separate noun/adjective senses; simplified sense shows only `wise` |Agrees with the English/Persian page meanings when structure is preserved. A flat form-to-sense join would be wrong. |
| `hūkar(ag)` correction |Website has separate `hūkar`, `hūkarag` forms with `porcupine (not hedgehog)` and marks the entry supplemental |Agrees with English PDF20/22 correction. Persian PDF86 / printed90 independently has `hūkar(ag)` and «خوکره»; root checked the crop. Persian species equivalence remains unadjudicated. |
| Legacy `xūkar*` query |Search box changed but result link/table retained the preceding `hūkar*` result |Unconfirmed, not proof that the legacy form is absent. No repeated endpoint probing. |

The Persian reviewer also checked PDF159–161: the expected old headword slot on160 moves directly from `xūb` to `xuftan, xufs-` and `xumb`. This supports the correction's placement in that printed edition, not a website absence claim. `N xūkara` within the corrected entry is comparative New Persian evidence, not its Pahlavi headword.

**Decision:** use full structured online entries alongside source images and corrections. Neither flattened web columns nor unverified PDF OCR are sufficient training labels. These two sources share dictionary lineage and must not be counted as independent attestations or two distinct training examples. No new source was admitted, evaluation changed, cloud job launched or model weights downloaded.
