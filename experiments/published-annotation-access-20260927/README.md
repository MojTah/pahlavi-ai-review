# Published annotation access check

27 September 2026. Reuses the exact route and TRAIN-only boundaries in `../grounded-supervision-20260927/WORD-ANNOTATION-ROUTE.md`. It does not repeat the occurrence inventory or create labels.

One anonymousGET to `https://mpdb.parsigdatabase.com/tags/textproperty/10/All/1/107/107000` returned401 and an empty body. Timeout20seconds, response bound2MiB, no cookies/credentials/environment proxy/redirects; no annotation data saved. The request receipt is `anonymous-access.json`. There was no further request or credential extraction.

The requested next scope is reading the public website's embedded API authorization value from the archived client, without displaying or persisting it, and using it only at the exact HTTPS API origin for this one index and at most one detail. Choose the lexicographically lowest returned occurrence whose BookCode is107 and whose returned identity maps to one of107000001,107000003,107000004,107000006. An index-prefix match alone does not establish a valid semantic association. Stop if no permitted ID, redirect, denial, unexpected schema or oversized result; no guessed occurrence, account login, broad export, alternate host or automatic retry.

The user explicitly approved this scope on 28 September. The two authorized requests are now complete; no further request is authorized by that approval. No paid GPU, cloud upload, model download, account change or Google Drive action occurred.

## Authorized result — 28 September 2026

Classic + Critic, lead `/root`, independent identity reviewer `/root/final_external_judge`. Both exact-origin GETs returned HTTP 200 with JSON. The pinned public-client authorization value was held only in memory, never printed or saved. Both used 20-second network timeouts, a 2 MiB response bound, no cookies, environment proxies, redirects or automatic retries.

| Evidence | UTC retrieval | Bytes | SHA-256 |
|---|---|---:|---|
| `authorized-index.json` | 03:07:32 | 1,405 | `c2a74a216d3f0f84fdbbb62852a49795d02b71563eb03b54fc07b0906e75883e` |
| `authorized-detail.json` | 03:08:11 | 441 | `0b9ab104751acc25a1214a0fb298ba4b495d2c899e02987496a4188f286d6f23` |

The index genuinely returned four eligible IDs: `107000001004`, `107000003004`, `107000004004`, `107000006006`. The lexicographically lowest, `107000001004`, was selected. The only detail request was `https://mpdb.parsigdatabase.com/sentence/detail/107000001004`. Full URLs, timestamps, status and limits are in the corresponding `*-receipt.json` files. These receipts contain no credential value.

The returned occurrence is `xrad`, contextual Persian gloss `خرد`, category `اسم` (noun), lemma `xrad`, transliteration `hlt`. Its three `Paragraph` fragments concatenate exactly to archived paragraph `107000001`, including the edition citation. `ParagraphTranslation` exactly matches the archived Persian text and attribution. Removing only the literal citation/credit suffixes gives the unchanged qualified TRAIN source and target. The focus occupies the unique source span `[16,20)`. The detail has no explicit parent or occurrence ID; returned-index association and full contextual agreement, not prefix alone, support its identity.

The critic independently recomputed both response hashes, the selection and exact source/translation matches, and returned PASS for identity. This is one accessible database annotation, not specialist certification, a general dictionary entry, measured corpus-wide coverage or training admission. No training packet or benchmark changed.

### Citation resolution and remaining uncertainty

The detail returns `Reference1 = Jamasp-Asana1913:40/7` and `Reference2 = HP3:1`. The archived abbreviations page (`pages/htmlpages/603/fa`, SHA `4d5750d85db7f9b88e56dc1a94de70b38cef6e6989898f9d078f94d8d9e9a1ca`) maps `HP1,2,3,4` to *Andarz ī pēšēnīgān*, Jamasp-Asana 1913, pp. 39–40. This agrees with book 107's third-part title, sequence 1 and the paragraph's p. 40 citation. The printed page/line 40/7 was not inspected independently.

The archived bibliography (`pages/htmlpages/604/fa`, SHA `21d81d87b6986035cb472ea312a4d13d050b4ac426e8a067dbab4895cd596b17`) identifies J. M. Jamasp-Asana, *Pahlavi Texts*, Bombay, 1897–1913. It lists the Goshtasb/Hajipour transcription and Persian translation work as **1399**, unpublished with database access, while this paragraph credits **1398**. Preserve this unresolved date discrepancy. Database publication does not establish external peer review or independently attribute this individual word gloss to a printed edition.

The access question is resolved. Any further collection needs a separately defined scope; deciding whether more annotations would address the failed training recipe is a scientific question, not an access problem.
