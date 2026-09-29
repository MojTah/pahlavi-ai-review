# Independent inscription source review

RESULT: PASS WITH EXPLICIT HOLDS. The six proposed clear Kanheri scope occurrences are supported by the printed article; they represent four distinct source/target pair types and no newly independent usable Kanheri witness. Both Pasargadae6 whole frames remain uncertain published interpretations. No blocking extraction mismatch was found in the reviewed artifacts. This review does not admit training data, resolve reuse rights, or provide linguistic/epigraphic expert certification.

Reviewer: `/root/blind_dev72_b`, independent of writer `/root/finetuning_kb_research`. Date: 2026-09-28. I wrote only this file. All validation was read-only using the existing runtime; no downloads, model calls, protected benchmark answers, or source corrections were used.

## Frozen inputs and inspection

| Artifact | SHA256 |
|---|---|
| `NEW-SOURCES.md` | `22c41427f66422a87c1889e7882912250489cebc2774e523ee89844f84ada764` |
| `new-source-receipts.json` | `e535e17231faaae8ddd969a45a4a368be01ff2a2257e97655a5784f23be97be3` |
| `KANHERI-QUALIFICATION.md` | `70bc32a47e509a90674638360ad99e8dd71bdcff59c0d3ee0b49794e89e0b0de` |
| `kanheri-candidates.jsonl` | `d01b002f17641f3d62a98e67538bd79ba12712624ca62cd5645ba82ec7bec242` |
| `pasargadae6-candidates.jsonl` | `f17c0f3650860bbccc96f5e74bf3602354f55e77cd369c4c93a35935cbc14bea` |

Paths in the table are under `experiments/data-qualification-20260928/`. I verified the two PDF hashes against their acquisition receipts: Kanheri `720d3db41ea76865c65d4a6875f0c03bf785dcae1a37f20dd6365a6e1501800f`; Pasargadae6 `486d88c21ef76f9fbfae64d8dd5474c73fd9fe56a0274c998cba0f1c2792d89b`. The referenced images' hashes also pass.

I visually read Kanheri PDF9–14 / printed115–120, PDF20 / print126, PDF23 / print129 and PDF27 / print133, using the existing `inspection/kanheri/page*.png` files. I visually read Pasargadae6 PDF11,15,16,17 / print83,87,88,89 using `inspection/bulaghi-*.png`. These images are under `sources/local/public-texts-2026-09-20/qualification-source-search-20260928/`.

All six Kanheri parent IDs and both Pasargadae IDs are unique. Each of the seven nested Kanheri scopes reconstructs exactly from the recorded source/target character offsets. Five Kanheri parents have source/target text; the unreadable fifth has null/null. The Pasargadae blocks preserve eight and three numbered source lines. All training flags remain false.

## Exact scopes supported for source qualification

These IDs qualify as bounded article-supported spans, pending root's release, split and rights decisions. They are not seven new sentences or new inscriptions. The name phrase and opening formula retain their actual grain.

| Eligible scope ID | Exact source | Exact Persian target | Page evidence |
|---|---|---|---|
| `KANHERI-ARTICLE-01-OPENING` | `pad nām ī yazad` | به نام ایزد | PDF10 /116 |
| `KANHERI-ARTICLE-02-OPENING` | `pad nām ī yazad` | به نام ایزد | PDF11 /117 |
| `KANHERI-ARTICLE-03-OPENING` | `pad nām ī yazad` | به نام ایزد | source PDF12 /118; target PDF13 /119 |
| `KANHERI-ARTICLE-01-ARRIVAL` | `hamdēnīgān ō ēn gyāg āmad hēnd` | همدینان به اینجا آمدند | PDF10 /116 |
| `KANHERI-ARTICLE-02-DATED-ARRIVAL` | `ēn sāl 300 ud 70 8 yazdgird , māh Ābān rōz Mihr hamdēnīgān ō ēn gyāg āmad hēnd` | سال ۳۷۸ یزدگردی، ماه آبان روز مهر، همدینان به اینجا آمدند | PDF11 /117 |
| `KANHERI-ARTICLE-06-NAME` | `Ābāngušnasp ī Farroxān` | آبان‌گشنسپ پسر فرخ | PDF14 /120 |

The first three occurrences collapse to one formula type. The two arrival scopes are related formulaic clauses, not independent experimental observations. `KANHERI-ARTICLE-06` and its nested `-NAME` are the same patronymic phrase and must be counted once. Thus six eligible occurrences reduce to four pair types. All are linked to already represented Kanheri witnesses.

## Holds and restrictions that must remain

| ID | Disposition and directly inspected reason |
|---|---|
| `KANHERI-ARTICLE-01` | Hold full block. PDF10 prints source `300 70 8` (378) but Persian `۳۷۶`; PDF9 introduction gives378. Preserve the contradiction rather than silently replacing376. PDF14 also characterizes the opening prayer as conjectural. Names contain `Ērā[n]`, `B(u)zurgādur`, `Māh[baxtān]`, parentage alternatives and brackets; terminal damage remains. The doubled `ud ud` is printed and retained. Only the two listed unaffected scopes qualify. |
| `KANHERI-ARTICLE-02` | Hold full block. The dated arrival has matching378 evidence, but the later name list and `murw[āg]?` are not certain. PDF20 explicitly discusses damage and competing interpretations of the terminal word. Bracketed Persian kinship explanations remain interpretive; do not export the full parent through the clear child. |
| `KANHERI-ARTICLE-03` | Hold full block. Restored names and unresolved `Yazadān’/hšlc` / `یزدان-؟` remain. Only the listed opening formula qualifies as clear. |
| `KANHERI-ARTICLE-03-DATED-ARRIVAL` | Restricted uncertain interpretation, excluded from the six eligible occurrences. PDF20 explicitly says `gyāg` is read by analogy with inscriptions1–2 and the photograph's first letter could be `m`. The main transcription alone hides this uncertainty; the candidate correctly restores it in metadata without altering the published source. |
| `KANHERI-ARTICLE-04` | Restricted disputed patronymic, not an undisputed father/son label. PDF23 says West regarded Šahrayār and Māhfarrōbay as two people; the author instead infers one person plus father by analogy and damage. No clear nested scope is proposed. |
| `KANHERI-ARTICLE-05` | Hold as unreadable inventory metadata, no source/target pair. PDF13 says only two or three of the original seven vertical lines remain and few letters are readable. PDF27's drawing does not authorize a guessed reading. |
| `BULAGHI6-MIDDLE` | Hold whole eight-line frame as an uncertain published interpretation. PDF11 preserves stars and lacunae. PDF15 states that the final sentence is incomplete and infers its lost continuation. The target correctly retains `[است]` and `[تخریبش برآید]`. No independently clear nested pair was demonstrated in this review. |
| `BULAGHI6-SECONDARY3` | Hold whole three-line frame. PDF16 contains stars and a long lacuna; PDF17 explicitly calls line3 badly damaged and tentative. The supplied predicate `[ساخته شد]` remains bracketed. `ابر سال` is printed and preserved; do not normalize it into a different wording. The article's lower/upper headings disagree, so the neutral identifier is appropriate. |

The article's Persian spellings, names, numerals, restoration punctuation and stated uncertainty are retained under the declared whitespace/joiner and vocalization normalization. These are source-faithful published interpretations, not diplomatic typography or independent readings of the stone. No correction of a scholarly reading is supplied by this review.

## Witness identity and protected-work boundary

I checked the fixed16 protected IDs only as policy metadata in `data/unified-corpus/build.py:24`;201 and219 are outside that set. I inspected non-protected201 source transcriptions and titles to verify witness identity, and219 only for titles/record IDs. No protected target was read.

Article inscription4's `sāl 390 ī Yazdgird Šahrayār Māhfarrōbay` matches non-protected `201005001`, whose site title calls it Kanheri5 and whose transcription spells the numeral `se-sad nawad`. Actual text therefore establishes the4↔5 numbering alias. The article's unreadable fifth must not receive that record or be counted as a new usable translation pair. Inscriptions1,2,3,6 likewise match201001001,201002001,201003001,201006001. This is direct evidence from another edition of existing witnesses, not independent witness novelty.

The local219 metadata lists only219001001–219004001, titled Pasargadae1–4. The new article identifies Pasargadae6; the two staged frames belong to that one inscription. This supports the narrower local-metadata distinction, not an exhaustive cross-corpus novelty claim. Persian and English renderings would remain translations of the same context, not independent attestations.

The unavailable1398/2019 book was not inspected and is not certified through this earlier Kanheri article. Known-work metadata screening does not replace final duplicate/witness review. Reuse rights remain unresolved at release level, and uncertain material must stay distinguishable from clear supervision. Training additions authorized by this review: zero.
