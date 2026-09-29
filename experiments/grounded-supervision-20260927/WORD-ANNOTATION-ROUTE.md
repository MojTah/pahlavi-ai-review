# Published occurrence annotation: bounded access route

2026-09-27. Offline access-feasibility audit, not semantic adjudication or label creation. No network requests, credential use, DEV/TEST answer reads, corpus changes, or new annotations were performed. The quarantined occurrence `119000001003` supplies no reusable meaning or alignment in this report.

**Finding:** Parsig's archived public client exposes a plausible route to published occurrence-level lexical and grammar fields. The existing local archive does **not** establish genuine occurrence IDs for the five selected TRAIN paragraphs. One narrowly filtered grammar-index request, followed by one returned occurrence-detail request, is the smallest useful live feasibility check. Successful access would establish source evidence, not expert-validated labels.

## Verified local identity and coverage

All five selected records are present in `experiments/train-audit-20260927/qualified-v1/train.jsonl`; only identity fields were inspected there.

| Qualified record | Work / book | Archived chapter | Paragraph sequence | Genuine occurrence IDs locally established |
|---|---|---|---:|---|
| `parsig:107000001:pal>fa` | `parsig:107` / `107` | `107000` | 1 | None |
| `parsig:107000003:pal>fa` | `parsig:107` / `107` | `107000` | 3 | None |
| `parsig:107000004:pal>fa` | `parsig:107` / `107` | `107000` | 4 | None |
| `parsig:107000006:pal>fa` | `parsig:107` / `107` | `107000` | 6 | None |
| `parsig:119000002:pal>fa` | `parsig:119` / `119` | `119000` | 2 | None |

The relevant raw paragraphs have `Code`, `ChapterCode`, `Sequence`, and layers containing `[{"Section": ...}]`. Their script/transcription strings contain no HTML tags or token-ID attributes. The export preserves paragraph association and explicitly does not assert vetted sentence alignment. A paragraph's presence in qualified TRAIN does not independently qualify every word annotation later retrieved for it.

The archived grammar index is `vocabulary-group-2.json`, with twelve `tags/textproperty/<category>/All/2/All/All` responses. These are the inscription group, whereas books 107 and 119 belong to group 1. No matching group-1 index response or non-canary occurrence-detail response was found in the manifest. The absence of local IDs is an archive-coverage limitation, not evidence that the site lacks annotations.

## Observed endpoint contract and response fields

The archived client `sources/local/parsig-2026-09-20/site-assets/main.a548495a.js` and the existing collectors establish these read-only request families on `https://mpdb.parsigdatabase.com/`:

| Route | Observed role / schema |
|---|---|
| `surf/paragraph/{book}/{chapter}/{selection}` | Paragraph reader; the frozen corpus used `All`. Returns paragraph `Code`, `ChapterCode`, `Sequence` and associated source/translation layers. |
| `tags/textproperty/{category}/{properties}/{group}/{book}/{chapter}` | Client constructs these exact five parameters from its selections. Category `10` is Noun; `All` means unfiltered properties. Results contain `Transcription`, `BookList[]`; each book has `BookCode`, `Book`, `BookTitle`, `TextList[]`; each occurrence has `TextCode`, `Sequence`. |
| `sentence/detail/{TextCode}` | Grammar-search links pass the **returned** `TextCode` directly to this detail request. Client display code expects `Transcription`, `Transliteration`, `Translation`, `Category`, `Lemma`, `Reference1`, `Reference2`, `Note`, `Paragraph`, `ParagraphTranslation`, `EnTranslation`, `ParagraphNote`. These are observed client field names, not a verified response schema for any selected occurrence; actual types, completeness and values remain to be checked. |

The reader also has a distinct click/selection path which computes a three-digit suffix from the number of ordinary spaces before the selection, appending it to the paragraph code; one component uses a `/null` suffix on the detail route. The vocabulary collector reverses the convention with `TextCode[:-3]`. This is useful evidence about the site's ID convention, **not permission to invent or enumerate occurrence IDs**. Whitespace-based positions do not establish word boundaries, compound membership, clitic alignment or annotation existence. Prefer returned index IDs and independently verify the parent and source context.

## Smallest proposed live check — not executed

The exact first candidate request is:

`GET https://mpdb.parsigdatabase.com/tags/textproperty/10/All/1/107/107000`

This exact parameter combination has not been fetched locally. It is justified by the archived client's explicit parameter construction, the observed Noun category `10`, and the archived book/group/chapter metadata; it is not a guessed API family. The equivalent public page is `https://parsigdatabase.com/tags/?lang=fa`, selecting Noun, all properties, group 1, book 107 and chapter 107000.

1. Inspect the index's identity structure first. Retain candidate IDs only when `BookCode == "107"` and the site's suffix convention maps them to **one of** `107000001`, `107000003`, `107000004`, `107000006`. Do not read or use annotation bodies for other parents. Stop if no matching occurrence is returned; do not broaden automatically.
2. Select the lexicographically lowest matching **returned** `TextCode`, then make exactly one `GET https://mpdb.parsigdatabase.com/sentence/detail/{returned TextCode}`. No concrete suffix is prescribed because none is verified offline. Do not substitute or revisit `119000001003`.
3. Preserve the raw response, full request URL, retrieval time, status/content type and SHA-256. Verify the returned source form, full parent context and reference locators against the frozen allowed paragraph before accepting the identity association. An ID-prefix match alone is insufficient. If the response has no explicit parent ID, record that limitation and require agreement of the independent context/locator evidence; leave ambiguous associations unresolved.
4. Record which lexical/grammar fields actually exist and whether references are usable. Stop after this one occurrence. Do not convert it into a label, infer missing fields, propagate a gloss to another occurrence, or regard a nonempty response as semantic validation.

This probe tests availability and identity binding, not the adequacy of lexical coverage for all five contexts. It does not retrieve book 119 or require a broad group-1 export. A later bounded request for 119 would need its own explicit scope.

## Access, attribution and interpretation limits

`collect_parsig.py` does not perform anonymous requests: its constructor extracts the site's public-client `Authorization` value from the archived JavaScript and sends it to the exact HTTPS API host. It refuses redirects and checks JSON and size limits. The value was neither displayed nor used here. **Do not run that collector under the present no-credentials restriction.** Whether this API accepts an anonymous request today, whether the public UI still works, and whether current client behavior changed remain untested. If a future authorized anonymous probe receives an authentication/access denial, stop rather than extracting or replaying a header. Any different access method belongs to a separate explicitly authorized scope. The current collectors also write archive manifests/runs and are therefore not suitable for this report-only task without modification or a separately owned collection step.

Archived book metadata attributes both records to Jamasp-Asana's edited text (1897–1913): book 107 is *handarzīhā ī pēšēnīgān*, described as complete with Persian translation; book 119 is *dārūg ī hunsandīh*, described as complete with Persian and English translation. This book-level attribution does not identify the author or edition behind every individual gloss or grammar field. Preserve Parsig as annotation publisher plus both returned reference fields; use the site's abbreviation/bibliography pages to resolve actual locators rather than supplying guessed citations.

The locally documented search guide distinguishes edition-based transliteration from transcription, contextual Persian glosses from exhaustive definitions, and compound lemmas from individual forms. Editorial stars/brackets carry meaning and must be preserved. Its grammatical scheme is adapted from Bijankhan/Ghayoomi, not Universal Dependencies. The live category metadata has twelve entries, including separate preposition/postposition, Ezafe and verb-marker categories; guide summaries differ, so decode actual returned category fields against the source tables rather than silently normalizing them. Published annotation still requires occurrence-specific qualification; paragraph approval is not lexical or grammatical adjudication.

The local site study records attribution-required research-use permission and retained copyright. Public availability and the ParsiPy software license do not establish unrestricted commercial training or redistribution rights for underlying text, translations or annotations. This audit does not decide those rights or claim a blanket prohibition. The notes' book-119 English citation inconsistency also remains unresolved; do not assume a returned reference resolves it.

## Offline evidence anchors

- Read: `scripts/collect_parsig.py`, `scripts/collect_parsig_vocabulary.py`, `scripts/export_parsig_texts.py`; `kb/parsig-live-study.md`, `kb/parsig-database.md`; narrowly selected archive metadata/client snippets. The quarantined canary JSON was not opened.
- Archived client SHA-256: `01cb5e6e4ec786173b86e1b68024961939686b373b1d9b2a251f8fda4adeec69`.
- `surf/paragraph/107/107000/All`: 3,031 bytes, SHA-256 `2db77dc03cb22966314c482c281152095d03d296c8ab7a3e41a8cc019e6d1879`.
- `surf/paragraph/119/119000/All`: 8,786 bytes, SHA-256 `a84065c2c279b1932031e15b6292a4b87e9929669ab7b1842340e180ccd96c33`.
- Both archived response byte counts and hashes matched `manifest.json`. Only the five permitted paragraphs' structural metadata and script/transcription HTML attributes were inspected; translation bodies were not needed for this audit.

**Recommendation:** perform the one-index/one-detail access canary only within an explicitly authorized live-access scope, then separately review its parent binding, citation and annotation quality. Until that succeeds, there is no verified published occurrence annotation for these five contexts to promote into grounded supervision.
