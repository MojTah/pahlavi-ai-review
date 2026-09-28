# Three contextual TRAIN anchors

27 September 2026. Bounded source qualification; AI proposal by `/root/train_review_03`. **Two proposals pending independent review; one withheld.** Every item has `expert_adjudicated=false` and `training_admitted=false`. No training target, corpus row, benchmark, model output or previous qualification was changed. These are occurrence-specific development proposals, not dictionary gold or independent evaluation cases.

## Evidence and method

The three unchanged parent references come from `experiments/train-recall-20260927/references.local.jsonl`, SHA256 `7146aaa3173b2795f18fc231675453f34fd0ed50703c0386a0a5224af0d5bd06`. Their source and Persian text hashes match the embedded qualified TRAIN ledger. Qualified TRAIN file SHA256 remains `15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc`.

The relevant primary book is **H. S. Nyberg, A Manual of Pahlavi II, Wiesbaden: Otto Harrassowitz, 1974**, local S24 `sources/A-Manual-of-Pahlavi-II-Dictionary.pdf`, SHA256 `d49aaebbe1f51ebc07c616f538ff40a2a8d7ae9c3b810836c65689ab8a50f8c9` (rechecked). Complete page images newly inspected: printed28/PDF37, printed58/PDF67, printed93/PDF102, printed154/PDF163, printed189/PDF198 and printed190/PDF199. OCR located entries; the rendered pages determined the readings and printed locators. Nyberg's numerical example locators refer to his own cited material; they are not assumed to identify these Parsig parents or Jamasp-Asana pages.

Prior work reused: `grounded-supervision-20260927/SCHOLARLY-GRAMMAR-CHECK.md`, `REPORT.md`, `lexical-packet.jsonl` and `published-occurrences.json`; `lexical-feasibility-20260927/REPORT.md`, `scholarly-checks.json` and `BOOK-ACCESS-FOLLOWUP.md`; and `kb/supplied-pdf-study.md`. The earlier occurrence-specific lexical check for107000001 concerned **xrad**, not pad-dard. The earlier ma/directive and nēst/assertion qualifications do not automatically qualify their lexical predicates. S22's previously visually checked prohibition rule is retained as attributed prior evidence: آموزگار و تفضلی، *زبان پهلوی، ادبیات و دستور آن*, Moin, fourth printing1382 SH, printed80 and83/PDF83 and86; local PDF SHA256 `207aeda5eae48227902f0f208f9b24fd5623627dd4ca589b217268e69596df92`. Selected S22 glossary navigation pages were also inspected, but yielded no additional qualifying lexical evidence and are not cited as proof of these meanings.

Archived publisher paragraphs were checked only for the three specified records, with their raw-file hashes verified. Persian translations credit **گشتاسب و حاجي‌پور،1398**. The publisher supplies paragraph-level source/translation fields; it does **not** supply a newly inspected word-alignment annotation for any of these three anchors. Each proposed subspan alignment below is explicitly our inference from book evidence plus this occurrence, pending independent review.

All offsets below are **zero-based Unicode code points, end exclusive**, against the exact displayed parent source/target; UTF-8 byte offsets are separately labelled. The original nonbreaking space between `any` and `kas` in109000005 is retained (U+00A0 at source offset41).

## 1. parsig:107000001 — PROPOSED_PENDING_INDEPENDENT_REVIEW

Exact source: `pad-dard ast kē xrad nē dārēd.`

Exact published Persian witness: `دردمند است کسی که خرد ندارد.`

Proposed contextual predicate alignment: **`pad-dard ast` → `دردمند است`**. Source `[0,12)`; Persian `[0,10)` (UTF-8 bytes `[0,19)`). The narrower lexical anchors are source `pad-dard` `[0,8)` and Persian `دردمند` `[0,6)` (bytes `[0,12)`). The proposal concerns the predicated afflicted/pained state; it does not relabel the bare noun dard as an adjective everywhere, or make an alignment for the remaining clause.

**Attested support.** Nyberg printed58, right column, entry **dart**, gives “pain, illness” and explicitly records the corresponding `drd` and `dard` forms in its language comparisons. Printed154, right column, **pat**, A.II.11, describes composition with a substantive forming adjectives meaning “provided, connected with”. Thus the book supplies a constructional reason to preserve the whole pad-dard expression, beyond extracting a noun meaning from the sentence translation. The exact publisher occurrence107000001 renders this predicate as دردمند است and cites Jamasp-Asana1913, p.40.

**Proposed inference and limits.** Connecting the corpus's pad-dard to Nyberg's pat construction and dart family, and aligning the whole predicate with the Persian span, remains an occurrence-level analysis. An exact **pad-dard** dictionary headword or separately aligned publisher annotation was not verified. No universal d/t conversion, exact morphological segmentation, illness diagnosis or unique literal English synonym is proposed. This is sufficient to submit a narrow phrase proposal for review, not to declare a new lexical gold entry. The original source and target have no editorial brackets or uncertainty marks recorded in their ledger.

## 2. parsig:108000001 — WITHHELD

Exact source: `dānāgīh rāy tā nēst.`

Exact published Persian witness: `دانایی را همتا نیست.`

Investigated alignment, **not accepted**: source `tā` `[12,14)` (UTF-8 `[16,19)`) with Persian `همتا` `[10,14)` (bytes `[18,26)`). The surrounding predicate spans are `tā nēst` `[12,19)` (bytes `[16,25)`) and `همتا نیست` `[10,19)` (bytes `[18,35)`).

**What is attested.** The exact publisher paragraph108000001, citing Jamasp-Asana1913, p.40, has the Persian witness above. Nyberg printed93, left column, has **ham-tāk**, “an equal”, with a reference to tāk. Printed190, right column, has **tāk, tāi**, “unit, piece”. Printed189–190 separately describes **tāi** as a preposition/conjunction with temporal, extent and related uses.

**Why withheld.** Those are distinct dictionary forms and senses. They do not establish a direct attested mapping from this bare **tā** to همتا, and the similarity of ham-tāk cannot justify deleting ham- or silently changing the corpus reading. Conversely, the temporal/extent entry does not justify inventing a noun translation «حد» or replacing the published sentence with an “unlimited wisdom” reading. The paragraph translation alone is insufficient for the new word alignment. This bounded lookup found no exact occurrence-level gloss or independently verified bare-tā equal-sense entry. The original published translation and previously qualified local nēst assertion function remain unchanged; this withholding applies only to the new lexical anchor. No editorial marks are present in this parent. Further progress needs an exact scholarly entry or occurrence annotation, not additional AI agreement.

## 3. parsig:109000005 — PROPOSED_PENDING_INDEPENDENT_REVIEW

Exact source: `pad bahr ī xwēš hunsand bēd ud bahr ī any kas ma apparēd.`

Exact published Persian witness: `به بهره (و سهم) خویش[در زندگی] خرسند (= راضی) باشید و بهرۀ کس دیگر را مدزدید.`

Proposed contextual negative-predicate alignment: **`ma apparēd` → `مدزدید`**. Source `[46,56)` (UTF-8 `[52,63)`); Persian `[70,76)` (bytes `[118,130)`). The lexical predicate anchor is `apparēd` `[49,56)` (bytes `[55,63)`), while the whole negative expression supplies the proposed Persian span. Supporting local clause spans are source `bahr ī any kas ma apparēd` `[31,56)` (bytes `[35,63)`) and Persian `بهرۀ کس دیگر را مدزدید` `[54,76)` (bytes `[90,130)`). No word-by-word object alignment is proposed.

**Attested support.** Nyberg printed28, right column, entry **appurtan**, present **appur-**, defines the action as “to rob, to seize and carry off”. Its entry explicitly includes **apparēt** among present-form variants; the adjacent **appar** entry concerns plundering. The exact archived paragraph109000005, citing Jamasp-Asana1913, p.56, gives the Persian مدزدید. Its additional English field credits Asha, n.d., and also renders the action as robbing. This is corroborating publisher passage evidence, not an independent word gloss or automatic gold. The previously checked S22 ma rule supports the negative directive function separately from the verb's meaning.

**Proposed inference and limits.** The dictionary's explicit appar- variant plus this object-bearing occurrence supports a taking/stealing action for the bounded phrase; merely desiring or coveting another's share would not preserve that attested action. The correspondence **apparēt / apparēd** is retained explicitly as a transcription/form comparison requiring review, not a universal spelling rule. No unique imperative morphology, person/number analysis, reconstructed infinitive label or new positive-form Persian translation is admitted. The earlier function-only ma scope remains distinct from this new lexical-predicate proposal.

**Editorial material retained.** `[در زندگی]` is target `[20,30)`, `(و سهم)` is `[8,15)`, and `(= راضی)` is `[37,45)`. These are supplied context and parenthetical explanatory glosses in the first clause. They remain verbatim in the witness; no Pahlavi token is invented for them. The ledger records two square-bracket characters and treats the flag as a qualification, not an exclusion. The first, affirmative bēd clause lies outside the proposed negative predicate scope.

## Provenance bindings and review boundary

All three parents retain `disposition=ELIGIBLE`, `qualification_status=PROVISIONAL_AI_QUALIFIED_DATA_NOT_EXPERT_CERTIFIED`, `alignment_status=PROVISIONAL_AI_PASS` and `expert_status=NOT_EXPERT_ADJUDICATED` from their original ledgers. Those statuses concern the existing TRAIN pair and its recorded qualifications; they do not admit this proposal. The authoritative full ledger objects remain embedded in the frozen reference file named above; they were not copied or rewritten here.

| Parent | Exact source SHA256 | Exact Persian SHA256 | Original ledger row SHA256 |
|---|---|---|---|
|107000001|`dec8d0ea9136b50e22af403cb44e14a57631f390773deb4d6b2469f4caa18cd5`|`2b0d455da5de2611695dbf9992749f45b5e8e0d28360a09c3417fafb9013312a`|`8b1519cf6b850500524c4820975500e6cb7396646f1bc1c73235d8d5e3c25f90`|
|108000001|`54d88044d51087cf037b62d23f13584f5fc506d352f17ead8295a5e3e20362e0`|`6b54340aacb51e9d3607a3d29b64bdfe64bb92c51d5c0ed845c8f419d33c090f`|`cc8e477ef4b470a319ab21c26cbe1fd53d212128f16e208d480d120e50312332`|
|109000005|`0a2476b534b97cccd042fe49a80d73ba413c8f1b0d9a9025dd7959014061c88b`|`37d619f8712b4963d0a31b28a1e7dae06ab57c7d6db4c00534fa369486d29596`|`a7c3f3c2930b7fcfd6d3e09ef8dc58ef136e8c910ea31693f57d907a96bb79e0`|

Verified raw publisher files, relative to `sources/local/parsig-2026-09-20/responses/`:

- 107000001: `ccebd4a3f989a11dcd8bdb255aa70f3591227e8a8c6c7dff5fd311290ddeb2e6.json`, SHA256 `2db77dc03cb22966314c482c281152095d03d296c8ab7a3e41a8cc019e6d1879`.
- 108000001: `508eedf6dfac0cb9e93bb4e89107d5251e7f03d1cbc5bdc9f325035786161a1d.json`, SHA256 `7862520981528099be27c2a59c8794400fd08f021d308137c718031036643851`.
- 109000005: `df124169fbb186fec6e6acbd4bb26890239d779708e2e408edd0a58f76f5feb7.json`, SHA256 `61d210ec6f59c44cd45305ccabebbe493f0de63867d22d442a17ae5095ae04e7`.

Original publisher URLs recorded in those ledgers are `https://mpdb.parsigdatabase.com/surf/paragraph/107/107000/All`, `https://mpdb.parsigdatabase.com/surf/paragraph/108/108000/All` and `https://mpdb.parsigdatabase.com/surf/paragraph/109/109000/All`. **No network request was made.** Their Jamasp-Asana edition locators are publisher metadata; the original Jamasp-Asana printed pages were not independently inspected in this task.

Only the local study copies and three selected TRAIN witnesses were used. Original book rights are retained; lookup permission is not a dataset-reuse license. Rendered aids are confined to `resources/local/contextual-supervision-check/`. No cloud job, paid call, new download, credential, Drive/email action, corpus sweep, model-output review or DEV/PAL reference access occurred. Independent review should inspect the exact book pages, check the stated transcription comparisons and decide each phrase scope separately. Even acceptance would be provisional TRAIN development qualification, not training admission or evidence of improved translation.
