# Final independent integration QA — 24 September 2026

RESULT: **PASS for artifact consistency, provenance, coverage and stated limitations.** This is not a certification of Pahlavi proficiency or translation accuracy. No required fixes were found in the reviewed frozen artifacts.

## Scope and verification

- Reconciled the original export with the historical seven-record baseline (52 units), the eight-record first-wave ledger (81 units), and all seven corpus-reader sets (607, 659, 583, 644, 609, 612, 660 units). The exact sets are disjoint: **52 + 81 + 4,374 = 4,507 unique IDs**, equal to the source export with no omission or extra ID.
- Verified all **354 assignment chunk files**. Every ID, order and supplied field value in each chunk matches the original export. This includes transcription, Farsi fields, additional translation/commentary layers, notes and the identity metadata carried by the chunks.
- Checked each reader's reported read-ID list against the assignment and complete ledger. All seven report zero skips. Recorded display-truncation repairs are explicitly distinguished from unread source content. This check relies on the readers' reading attestations; it does not independently replay their full tool transcripts or measure comprehension.
- Verified every inventory record's chapter IDs and ordered sequence labels against the original export: **126 records, 334 chapters, 4,507 labels**. All records carry the intended read status, with the scope limited to saved offered paragraph layers. Per-record corpus files still match the original collection SHA-256 values.
- Freshly rechecked all **5,047 successful original manifest entries** across Parsig and the retained external collections. All retained response byte lengths and SHA-256 values match their manifests. Source originals were not rewritten. The source-unit export still hashes to `c42e0a5a0d4d108218a0481ca073c07c6bb00cdcba0bffb462b67bb6d7a60789`.
- Parsed all **11 scoped ledger/dictionary/reader-coverage JSON files**. The dictionary still contains 16 entries. Verified **195 local Markdown file links** and **62 local heading anchors**; none were broken. The intentionally pending `sources/reviews/2026-09-24/integration-review.md` was excluded, as instructed, and must be created by the lead before final delivery.
- Checked current study statements in README, PROJECT_STATE, study status, the main review and translation notes. Old five-/six-/seven-record limits are now superseded or clearly historical. The old five-record description in the dated source-register entry concerns the original live visit; its opening explicitly directs readers to the current ledger. It is not used as current total coverage.
- Compared the main review's material claims with the reader reports. Directly spot-checked source units `134009001` (1,800/1,600 discrepancy), `138005007` (possible Farsi polarity mismatch), and `225001001`/`225002001` (Persian editorial notes in transcription fields). Their descriptions preserve uncertainty and do not overwrite the original layers.
- Confirmed the lead's correction in corpus-reader-7: `framud kardan` in `216001001` is described as finite past governing an infinitive, not an imperative. The reviewed hash below was captured **after** that correction.

## Remaining limitations and delivery condition

Coverage checks establish which saved fields the readers report reading, their exact source identity, and consistency of the integrated record. They do not establish that every uncertain clause was resolved correctly. Broad linguistic review, manuscript collation, full dictionary/manual study, independent translation evaluation and reading of all other archives remain incomplete and are stated explicitly.

The unchanged raw Farsi field count is not a usable-pair count. Credit-only fields, editorial-only transcription fields, mixed languages, empty XML layers and cross-unit translation spans remain documented. No translator or trained model has been produced, and no accuracy score is justified.

No core changes, downloads, mutation-prone verification script, package installation, git operation or external write was performed by this QA. Only this report was written. One PowerShell wildcard search failed and was replaced by the equivalent directory-plus-glob search; substantive checks were unaffected. The review completed within the eight-minute expected window.

The lead may create the excluded operational `integration-review.md` after this review. If any of the hash-bound files below change, this PASS applies only to the identities listed, and the changes need focused rechecking.

## Exact artifact identities reviewed

SHA-256 values below bind this PASS to the inspected bytes. Some historical/supporting notes received consistency/link checks rather than new full linguistic review.

| Path | SHA-256 |
|---|---|
| `PROJECT_STATE.md` | `dc46d5a1a83b777cde5514d4991083ea3dfd0fd4398b2d12af515affc418c63d` |
| `README.md` | `683be04fa13479de47b3f0c8fb7670a3a3df388dc9a6c59f1bef3d61b1d096b9` |
| `data/README.md` | `43180de8ddc4ef62723e4060a29f80f9f1b8fe424caeaa96b02362c379f22561` |
| `data/collection-status.json` | `4ab96bfee84e452fbd27242f4313efc12294f62a4af39c30160f6b85d6977a35` |
| `dictionary/entries.json` | `e962acaca1714e361a0ff06269816c19f21cd9a470033d9d68c2c462346f9074` |
| `kb/ancestral-counsels-3-study.md` | `7914e0f60ea3816de443b4965cdba8217aed345651cc8bf87c0b5e5d3b69c6f4` |
| `kb/baxt-afrid-study.md` | `2d3da73dc43e9ec7c1b0f88e0e14314d5b15f9f6a407e09cf5b06d9672ded93b` |
| `kb/bilingual-reading.md` | `081591eb23fc317b0ec954d0fab14693b9c7352bdb5cd2aa6e7c5c4fce5d85e7` |
| `kb/documentary-readings.md` | `98833c151f8b00da0d65be88ba27ac1836333a913d741232c9ea5d398ce92498` |
| `kb/glossary.md` | `fc37641e2e6903113802c3710be56203c9f59c5fd8a9b1feb4738908b32be611` |
| `kb/grammar.md` | `21307f346f756dbd55e71e57f9ef9acdbad2a5b9f62742f25b6754536d1b1845` |
| `kb/karnamag-ii-iii-study.md` | `5f738635749771a9e45e40a86b8567c72fefeb0d769892c3eacd45bf9b95d284` |
| `kb/khusro-page-study.md` | `8bd409381c363c5c375239f079229c15a1f2705a6168ab58ef8f6744bfc66467` |
| `kb/language-and-corpus.md` | `efe1691b38715030fc6fb6f02c42e8d903e8e79266730178f66a3bd3feee5c23` |
| `kb/parsig-database.md` | `d7f0b099b226c0f6f0ff30cc3dea8e3d64f4f768c9660c19b713b7c9e945ec02` |
| `kb/parsig-live-study.md` | `40bbe852b6d68afa2c9ee63686af4331ce7b0957f5e4c51c80849325ba9ece1f` |
| `kb/practice.md` | `14be07d69f9f02661b2bf620b9ec0a93b2a64062e0a9d3768078bcd2ca8a97d4` |
| `kb/reading-method.md` | `ba37d99bc323a5b518ad0502fe0c541a16fb23c6fe179f5034dd9ea1ad4c473f` |
| `kb/review-2026-09-24.md` | `fcf46c64428597bc3ae281772997eba1db18ea434f9d868eafc51e1c5949991b` |
| `kb/short-texts-review.md` | `8013304e656195003e070a97cc50c18e85189dbf60e3ebded260659cc354f8f9` |
| `kb/sources.md` | `4d03d39433e66247bd25af736ac6c9cdde2232d7a1f8587277b5153b52656364` |
| `kb/study-status.md` | `3eb78323cbb787dfe70b2a13be7c5d7fe047a7f36f95717df16cb97f765b3ace` |
| `kb/supplied-pdf-study.md` | `4a414dda0a2a0b83eaee2f7223e8e8d2246de6d3a1baec43ec198b029fea8741` |
| `kb/translation-study.md` | `970270732ac42565fa5b19faf5002784e65897da11ecfbc21593189459df451f` |
| `kb/worked-readings.md` | `59c4a7af0c4494ca0c8ba10f6737757cf1100b9a866abfe1217d71c42902683c` |
| `kb/writing-system.md` | `918ef3a0f856ae33aebfd49e1f5c1f460bf34203f042476cdf1f95f20c5cdced` |
| `sources/parsig-complete-study-2026-09-24.json` | `548d9b88541c2046019492307512add5159a9d4e2d26e73dc034c77df81f845e` |
| `sources/parsig-live-inventory.json` | `68473251ce1206f0b1beb721ae52599c82c2bfaf1a3013ef40a461eba5b08e4e` |
| `sources/parsig-study-2026-09-24.json` | `e6bb92a574f2a50317b7d9a0fabf79fdd110256d935b96bbf75c44e75a55bd6f` |
| `sources/reviews/2026-09-24/corpus-reader-1-coverage.json` | `d6f1db992b34afa219ed8df88f5cfb1bf613d5a10ba1e68f4f0625256bb4fb30` |
| `sources/reviews/2026-09-24/corpus-reader-1.md` | `119eac2fa561b875eb76ddf9f2b1b1651ad5a90eb575ac3aa1d70f195fd4c286` |
| `sources/reviews/2026-09-24/corpus-reader-2-coverage.json` | `c01e86ed82e03c9dad2c9c3861eb184d03440456bb8c579aaa105812e049768d` |
| `sources/reviews/2026-09-24/corpus-reader-2.md` | `fbb9e7d1571b81b3320ddf79760dfe5b7abb520ecb82a29a12dda8d74a99a40b` |
| `sources/reviews/2026-09-24/corpus-reader-3-coverage.json` | `cc388610872a358251beb70f1ac0b5d4f71ed48f3ce795bc36ab76570d035304` |
| `sources/reviews/2026-09-24/corpus-reader-3.md` | `5a431525afdaa0f6ea533ffbf7ff017554336e58577b851ac6ad85540a2599de` |
| `sources/reviews/2026-09-24/corpus-reader-4-coverage.json` | `ba4d08b88a0dc259e1ad81a144e8579150476b9fafad34e01f15f13304c33693` |
| `sources/reviews/2026-09-24/corpus-reader-4.md` | `d65df0984fc970cb1764819182afc6aed74b979a537c43b4189efa2670007646` |
| `sources/reviews/2026-09-24/corpus-reader-5-coverage.json` | `d21391ea51c98de105e3084afe994673989954e85dee85408bc4a39248d300d0` |
| `sources/reviews/2026-09-24/corpus-reader-5.md` | `4cb1d7b0b7f010afb037b9dd4258a39fc3dc5efc99bf0670695412709bc51b95` |
| `sources/reviews/2026-09-24/corpus-reader-6-coverage.json` | `a508f67f180c9cd41afeefb29279b2f4efff1498e34048c7a13d8c170356eebe` |
| `sources/reviews/2026-09-24/corpus-reader-6.md` | `c92403fd7f7b4ff6ade7cab1b25cdaf8222e6b6514607498351ca7c0c2dbe8e8` |
| `sources/reviews/2026-09-24/corpus-reader-7-coverage.json` | `855506bbcfdb47de9edc871759e627db1be7676247bace4b2b5167bae0950f88` |
| `sources/reviews/2026-09-24/corpus-reader-7.md` | `bd19a3168ba21400b755c7ffdcc8642753aa622040fd5e828f12b44eb63d5e96` |
| `sources/reviews/2026-09-24/data-quality-review.md` | `097b03ec51340aa58ba529a19b87e6243a953300f3c8b24f224af8c2451774d2` |
| `sources/reviews/2026-09-24/grammar-review.md` | `be19ff12e8da1ac3d7831ccc4274185703d28daf51ea6b043dbddfe6cf0d048a` |
| `sources/reviews/2026-09-24/lexicon-review.md` | `745a3a41a4c4dc36c7e533560391244bce628f9bb3190563006bbcbdf4478262` |
| `sources/reviews/2026-09-24/script-review.md` | `c06604fa6cd65e0b65a2f7c95f0ce35a8137773130c448fc6d263102e0f4ebcc` |

## Source manifest identities

Each successful entry in these manifests was rehashed during this QA.

| Manifest | SHA-256 |
|---|---|
| `sources/local/parsig-2026-09-20/manifest.json` | `516c5d38780ac29f9e29ce6b22592ac69d6604e14ae0c9d75a0a471bff199ec5` |
| `sources/local/public-texts-2026-09-20/avesta/manifest.json` | `1895530d4d77901ee3b5575812cb78e3513dfde5f96b508498173a0737d2e85c` |
| `sources/local/public-texts-2026-09-20/berkeley/manifest.json` | `f1e7ae7efeaaad7de987fa2f71b40ce2d48fd9d26429582e20dfbe7d888773dc` |
| `sources/local/public-texts-2026-09-20/ezafe-modeling-mp/manifest.json` | `efb47b7e1c35c77ffdd9c3c50c5cfc70dec9721dc9aea6b6ff4b8c687fcb1224` |
| `sources/local/public-texts-2026-09-20/invisible-east/manifest.json` | `3336cc5a2036b476e871ee3997063135e36be22958b2e1f2048bdb0c9ae8399c` |
| `sources/local/public-texts-2026-09-20/persoaryan/manifest.json` | `15e16d0b63be33581f6e74150ac353dc70346cfc2432be13d559896690bea5e6` |
| `sources/local/public-texts-2026-09-20/titus/manifest.json` | `32366108b5b5adbc2de66293ea4d866e38743b0212ec67dba49e7a5f348f528d` |
| `sources/local/public-texts-2026-09-20/UD_Middle_Persian-MPCD/manifest.json` | `55a072ef90608667bb472d639d724fd7514f21d2ef73d0388559f87d102ebcff` |

Checked at 2026-09-24T04:27:01.518565+00:00.
