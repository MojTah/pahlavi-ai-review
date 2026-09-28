# Independent review of three contextual anchors

27 September 2026. **PASS for three narrowly qualified, provisional occurrence-level development anchors.** This is an AI review, not expert gold, universal lexical/morphological annotation, a training batch or paid-training admission. The original proposal files remain unchanged; a separate lead decision may record these qualifications.

## Per-anchor decisions

| Anchor | Decision and scope |
| --- | --- |
| `CONTEXT1-107000001`: `pad-dard ast` → `دردمند است` | **Provisionally accept the contextual predicate.** Nyberg printed58/PDF67, right column, has `dart` for pain/illness and comparison forms `drd`/`dard`. Printed154/PDF163, right column, `pat` A.II.11 explicitly treats composition with a substantive as adjective-forming. Together with the exact published occurrence, this supports the afflicted/pained state expressed by the whole phrase. The corpus `pad`/`dard` to book `pat`/`dart` correspondence and phrase alignment remain bounded analysis. No exact `pad-dard` headword, universal spelling rule, clinical diagnosis or universal adjectival meaning of bare `dard` is certified. |
| `CONTEXT1-108000001`: `tā` → `همتا، جفت` | **Provisionally accept only the attributed published occurrence gloss, retaining both words.** The recorded occurrence is `108000001003`, transcription `tā`, transliteration `tʾk`, publisher category noun, references `HP4:1` and `Jamasp-Asana1913:40/13`. Its displayed sentence and Persian witness match this TRAIN parent after explicitly allowing UI whitespace differences in the displayed source. The entire gloss is preserved; it is not falsely represented as a contiguous subspan of the sentence translation. The Nyberg-only bare-`tā` lookup remains **withheld**. This new decision relies on the separate publisher observation, not on deriving the sense from `ham-tāk` or silently changing the reading. |
| `CONTEXT1-109000005`: `ma apparēd` → `مدزدید` | **Provisionally accept the contextual negative predicate.** Nyberg printed28/PDF37, right column, `appurtan`, present `appur-`, supports robbing/seizing/carrying off and explicitly includes `apparēt` among its listed variants; the adjacent `appar` entry concerns plundering. Combined with the exact object-bearing publisher passage and the previously qualified negative-directive scope, this supports the bounded taking/stealing action. The comparison `apparēt`/`apparēd` is retained as a transcription/form qualification. No unique mood, person/number analysis, reconstructed infinitive label, universal spelling conversion or new positive-form translation is admitted. The first affirmative clause remains outside this focus. |

The two phrase alignments are our occurrence-specific inferences from book evidence and paragraph witnesses, not publisher-supplied word alignments. The third is a separately reported publisher word-occurrence gloss. These evidence types must remain distinct.

## Source and fidelity limits

I directly viewed the existing complete page images `nyberg-pdf37.png`, `nyberg-pdf67.png` and `nyberg-pdf163.png`; their printed page numbers 28, 58 and 154 and the cited entries are visible. The exact local S24 PDF was independently rehashed. This review does not claim a broader book search, independently inspected Jamasp-Asana printed pages, or a newly rechecked S22 grammar page. The negative-directive function reuses the prior bounded qualification; these new proposals concern lexical/construction content.

`published-occurrence.json` is explicitly a **lead transcription of public UI text**, not raw API output. I verified its local identity and consistency with the exact parent, citation and whole gloss. I did **not** independently revisit the UI or certify transcription fidelity. Qualification of the tā item is therefore provisional with that limitation attached. Its noun/lemma/transliteration fields remain attributed publisher metadata, not independently established morphology. The word gloss and paragraph witness are from the same publisher, not two independent scholarly confirmations. The recorded attributed-use notice does not establish blanket rights to redistribute underlying editions.

## Executed mechanical checks

Local project Python checks passed for exactly three packet records:

- Packet SHA/count and preparation bindings; exact source, Persian reference, TRAIN membership and original ledger identity. All three remain `ELIGIBLE`, with existing `PROVISIONAL_AI_QUALIFIED_DATA_NOT_EXPERT_CERTIFIED` and `NOT_EXPERT_ADJUDICATED` limits. Their existing split checks pass, with no recorded split/mechanical errors. No held-out reference was opened to create a new alignment or label.
- Each archived response file's full SHA and byte size, then its exact selected `Code` record. The original transcription plus edition and translation plus credit equal the saved TRAIN witnesses. The 109000005 archive also contains the stated English corroboration; this is paragraph evidence, not an independently aligned lexical gloss.
- Source code-point and UTF-8 offsets, target/source/reference SHA values, Persian witness subspans, unchanged citation/credit/raw-pointer fields and retained flags/qualifications. The full publisher gloss has a null sentence-subspan field, appropriately distinguishing it from an extracted reference phrase.

| Parent | Source code-point span | Source UTF-8 span | Persian witness span |
| --- | --- | --- | --- |
| 107000001 | `[0,12)` | `[0,12)` | `[0,10)` |
| 108000001 | `[12,14)` | `[16,19)` | None: whole published gloss `همتا، جفت` |
| 109000005 | `[46,56)` | `[52,63)` | `[70,76)` |

Offsets are zero-based, end exclusive. The U+00A0 at source offset41 of 109000005 survives. Its target `[در زندگی]`, `(و سهم)` and `(= راضی)` remain verbatim at their recorded positions, with the two-square-bracket flag retained; no source word or alignment is invented for those additions. The larger supporting object/clause spans also match exactly.

No other candidate received qualification. The separate surface inventory is outside this verdict and cannot supply senses, alignments or additional accepted labels. Three reviewed anchors alone do not establish coverage, a broad quality benefit, a numeric supervision recipe or readiness to spend on training. No corpus, benchmark, model, existing qualification or training row was changed.

## Exact evidence

| Artifact | SHA256 |
| --- | --- |
| `experiments/contextual-supervision-20260927/PROPOSAL.md` | `c15877ba05cac4053cc9260af5ebf2a109e013a81c0a61a60bd6c181f524b954` |
| `experiments/contextual-supervision-20260927/proposals.jsonl` | `f465bfac2d3f818c1960386dc0ef1edbc6b2a87561ede3b0e6c657ed2860923e` |
| `experiments/contextual-supervision-20260927/preparation.json` | `ac6313824c5e9c3c5ed09fdaa9a873324582385b885e685c55d4f42e31fd92c2` |
| `experiments/contextual-supervision-20260927/published-occurrence.json` | `07cdd3ca85e26114bbac4a93a51ae4fd5c05f7152570920077db8e3fc39a19e5` |
| `experiments/train-recall-20260927/references.local.jsonl` | `7146aaa3173b2795f18fc231675453f34fd0ed50703c0386a0a5224af0d5bd06` |
| `experiments/train-audit-20260927/qualified-v1/train.jsonl` | `15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc` |
| `experiments/train-audit-20260927/qualified-v1/final-ledger.jsonl` | `d79af2e64fbb92954c8b8d0ed9cb7a34e7e7d24d4c22ea9c22f1da6d569a8e77` |
| `sources/A-Manual-of-Pahlavi-II-Dictionary.pdf` | `d49aaebbe1f51ebc07c616f538ff40a2a8d7ae9c3b810836c65689ab8a50f8c9` |
| `resources/local/contextual-supervision-check/nyberg-pdf37.png` | `88690eb9a4e1679a31faffaf49d2224406cf6bf95c44f28582e227a42d7f3acd` |
| `resources/local/contextual-supervision-check/nyberg-pdf67.png` | `a76a588a14e6b8939c4740bcd82db4023bf7df78d0be6de4765d6357259df6dd` |
| `resources/local/contextual-supervision-check/nyberg-pdf163.png` | `741b6222b517e884fe1ae817ca250b2d369f3fd72d43579ebf3899de0d8f7e54` |

The three exact archived-response hashes and parent source/target/ledger-row hashes embedded in the frozen packet were independently checked against the local responses and authoritative reference/ledger objects.

## AutoCode Critic record

- Mode: Classic + Critic.
- Lead agent/request id: /root
- Critic agent/request id: /root/final_external_judge
- Critic model and reasoning effort: inherited session settings, no override
- Independent from lead: yes
- Critic verdict: pass
- Evidence reviewed: Exact three-anchor proposal/packet/preparation, separate lead-transcribed tā occurrence, three original TRAIN witnesses/ledgers/archived paragraphs, local Nyberg PDF and directly viewed printed28/58/154 page images.
- Verification evidence: Independent visual book reading; PDF/image/artifact hashes; three exact TRAIN/reference/ledger/raw-response joins; source code-point/UTF-8 and Persian-span checks; retained editorial/NBSP/qualification checks; published whole-gloss/context consistency with explicitly unverified independent UI fidelity. No network, cloud, credentials, paid calls, held-out-reference use, source repairs or training admission.

PASS qualifies only the three bounded development anchors under the limitations above. It does not resolve the withheld book-only tā inference, create expert gold or approve a learning experiment.
