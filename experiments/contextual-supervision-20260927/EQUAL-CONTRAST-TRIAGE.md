# Equal and homograph contrast triage — 2026-09-27

Status: **PROPOSED_PENDING_REVIEW** for three additional contextual spans; all other candidates **WITHHELD** from this proposed packet. No training admission.

## Scope and result

Reviewed the exact source and Persian witness for all 69 parents in the inventory’s `equal_or_homograph_candidates` family: 12 works, 77 occurrences. All 77 surface matches are `tā`; the census contains no actual `tāk` or `ham-tāk` match. Membership, complete text equality and UTF-8 hashes were rechecked against the frozen qualified TRAIN file for all 69. No held-out references, model outputs, network, cloud or credentials were used.

These are provisional contextual triage bins, not newly certified lexical senses or 69 auxiliary labels. A Persian `تا` alone is insufficient: the three proposals additionally have a clear local endpoint/duration construction and a matching Nyberg rule. The full census is retained below; unselected rows were not silently discarded.

| Triage bin | Parents | Surface occurrences |
|---|---:|---:|
| Temporal endpoint / duration | 37 | 45 |
| Spatial endpoint / extent / numeric range | 11 | 11 |
| Purpose / governed clause | 11 | 11 |
| Other / uncertain contextual use | 9 | 9 |
| Existing equal anchor | 1 | 1 |
| **Total** | **69** | **77** |

Three proposed parents span three works (136, 137, 151). The remaining 66 are withheld from this packet, including the separately documented existing equal anchor. “Withheld” here is a selection/qualification status, not a claim that the publisher text is wrong.

## Book rule and equal-sense boundary

Primary reference inspected as existing page images: H. S. Nyberg, *A Manual of Pahlavi II* (Wiesbaden: Otto Harrassowitz, 1974), printed pp. 93, 189–190. Printed p. 93 gives `ham-tāk` as an equal. Printed pp. 189–190 distinguish temporal/local `tāi` uses, governed/final uses and the separate unit/piece entry. The book alone does not establish a universal bare `tā` → equal mapping.

The newer `published-occurrence.json` records the exact public occurrence `108000001003`: `tā` / `tʾk`, target `همتا، جفت`, references `Jamasp-Asana1913:40/13` and `HP4:1`, parent `dānāgīh rāy tā nēst.` / `دانایی را همتا نیست.` It addresses the missing occurrence-specific evidence behind the earlier book-only withholding in `PROPOSAL.md`. Its capture is a lead transcription of the visible UI and remains pending independent fidelity review; it is not a raw API capture or training admission. It does not transfer the equal sense to the other 68 parents.

## Three proposed exact witness spans

Targets below are verbatim contiguous substrings of the saved publisher Persian response and frozen TRAIN witness. Offsets are Python Unicode-code-point indices, zero-based, end-exclusive; they are not UTF-8 byte offsets. Full contexts remain visible to avoid converting a phrase into an unconditional word-gloss.

### parsig:151001162 — Spatial endpoint

Status: **PROPOSED_PENDING_REVIEW**; `training_admitted=false`.

- Literal source span: `tā ō činwad puhl`; offsets `[36, 52]`; UTF-8 hex `74c481c2a0c58d20c48d696e776164207075686c`.
- Literal target span: `تا پل چینود`; offsets `[32, 43]`; UTF-8 hex `d8aad8a720d9bed98420da86db8cd986d988d8af`.
- Full source witness: ud pad hamēstārīh ī srōš ahlā nayēd tā ō činwad puhl.
- Full Persian witness: و علیرغم مخالفت سروش مقدس او را تا پل چینود می‌کشد.
- Publisher transcription edition field: (Anklesaria, 1913, p.29); Persian credit field: (تفضلی، 1379، ص 26).
- Rule/context justification: Nyberg printed p. 189 (PDF image 198): local preposition and the tā ō construction. This supports an endpoint reading here; the exact target comes from the publisher, not from the dictionary.
- Existing qualification: `ELIGIBLE`, `PROVISIONAL_AI_PASS`, `PROVISIONAL_AI_QUALIFIED_DATA_NOT_EXPERT_CERTIFIED`, `NOT_EXPERT_ADJUDICATED`. Linguistic reviewer `/root/train_review_04`, meaning `no_identified_issue`, retained linguistic qualifications `[]`; retained flags `[]`.
- Existing curation scope: publisher paragraph ID and fields, not sentence-level or expert semantic validation. This triage does not upgrade that scope to expert adjudication.
- Source SHA-256: `468b08532ab0e805ff48a4bec2b44adc68f71ff9247c50309aba34bf51ab8a50`; target SHA-256: `e4de527f8efc85be4c423e05076905a393d575a4f19f821b5ca09008d1367ea3`.
- Existing TRAIN row SHA-256: `9558fbe7a87f9793719f627f9ae94c12454639d56586bf3ac2c50a7b0c37fdca`; revision `8caa7b472e62a997fe8441cd89e0b2b8fce2cfd454cb3bd907e13e67b8e4483e`.
- Raw publisher response: `sources/local/parsig-2026-09-20/responses/d5837e516d7d01f61da4f44f68f64167a69b42183c46b31d0057b59141651154.json`; SHA-256 `546c32d199bf9c32c930904de0042342342256aeee3b0e0effadea55c08faa31`; record `Code=151001162`. Both raw section strings exactly equal the corresponding TRAIN text plus their recorded citation suffix.
- Recorded publisher URL (not accessed in this task): https://mpdb.parsigdatabase.com/surf/paragraph/151/151001/All.
- Preserve U+00A0 between `tā` and `ō`; the displayed phrase is not normalized to an ordinary space.

### parsig:136005007 — Duration / as long as life lasts

Status: **PROPOSED_PENDING_REVIEW**; `training_admitted=false`.

- Literal source span: `tā zīndag bawēm`; offsets `[67, 82]`; UTF-8 hex `74c481207ac4ab6e64616720626177c4936d`.
- Literal target span: `تا زنده باشم`; offsets `[56, 68]`; UTF-8 hex `d8aad8a720d8b2d986d8afd98720d8a8d8a7d8b4d985`.
- Full source witness: pas banāg ō pēš ardaxšīr mad ud sōgand xward ud abēgumānīh dād kū, tā zīndag bawēm xwad abāg frazandān framān-burdār tō bawēm.
- Full Persian witness: پس بناک به پیش اردشیر آمد و سوگند خورد و بیگمانی داد که تا زنده باشم، خود با فرزندان فرمان‌بردار تو باشم.
- Publisher transcription edition field: (Anklesaria, 1935, p. 32); Persian credit field: (فره‌وشی، 1378، ص45).
- Rule/context justification: Nyberg printed pp. 189–190 (PDF images 198–199): temporal duration / as-long-as construction. The existing Persian witness supplies the first-person phrase; no new translation or person/number adjudication is asserted.
- Existing qualification: `ELIGIBLE`, `PROVISIONAL_AI_PASS`, `PROVISIONAL_AI_QUALIFIED_DATA_NOT_EXPERT_CERTIFIED`, `NOT_EXPERT_ADJUDICATED`. Linguistic reviewer `/root/train_review_03`, meaning `no_identified_issue`, retained linguistic qualifications `[]`; retained flags `[]`.
- Existing curation scope: publisher paragraph ID and fields, not sentence-level or expert semantic validation. This triage does not upgrade that scope to expert adjudication.
- Source SHA-256: `6425b5edd201e2783794b8a72300a593c148da7eaa88f0a6a1dac6e6384d19ff`; target SHA-256: `4c01d3ba05870aae877e9ec6b607453effbd60ab0b105fc21c4faec813a36288`.
- Existing TRAIN row SHA-256: `406c219eb39cea9efeba3db4ebffd7396fa0f78d416770fb8cd9330e2e6a3ccf`; revision `2a333c54756cdd60d84a0cbe71020f2c8bd03f04befab1dfcf6430c3b9303cf8`.
- Raw publisher response: `sources/local/parsig-2026-09-20/responses/1668f91130ce98b51532f41779cf388c6356f215e2273bcbf133578ab8f1cec7.json`; SHA-256 `7dbe4693a20f4f413b98d24a845607a49a60aa50e59f92898661c06db6b700cd`; record `Code=136005007`. Both raw section strings exactly equal the corresponding TRAIN text plus their recorded citation suffix.
- Recorded publisher URL (not accessed in this task): https://mpdb.parsigdatabase.com/surf/paragraph/136/136005/All.

### parsig:137001027 — Temporal endpoint / until night

Status: **PROPOSED_PENDING_REVIEW**; `training_admitted=false`.

- Literal source span: `tā šab`; offsets `[144, 150]`; UTF-8 hex `74c48120c5a16162`.
- Literal target span: `تا شب`; offsets `[131, 136]`; UTF-8 hex `d8aad8a720d8b4d8a8`.
- Full source witness: ēg ganāg-mēnōg, awēnāg-frazāmīh rāy pad ān paymānag ham-dādestān būd, ēdōn čiyōn dō mard [ī] ham-kōxšišn kē zamān frāz kunēnd kū-mān wahmān rōz tā šab kārezār kunēm.
- Full Persian witness: آنگاه، اهریمن، به سبب نادیدن فرجامِ [کار]، بدان پیمان همداستان شد، به همان گونه که دو مردِ هم‌نبرد زمان فراز کنند که «ما بهمان روز تا شب کارزار کنیم».
- Publisher transcription edition field: (Hajipour, 1400, forthcoming); Persian credit field: (بهار، 1380، ص 35).
- Rule/context justification: Nyberg printed pp. 189–190 (PDF images 198–199): temporal endpoint / until construction. The surrounding appointed day and night constrain the use; it is not an equal-sense occurrence.
- Existing qualification: `ELIGIBLE`, `PROVISIONAL_AI_PASS`, `PROVISIONAL_AI_QUALIFIED_DATA_NOT_EXPERT_CERTIFIED`, `NOT_EXPERT_ADJUDICATED`. Linguistic reviewer `/root/train_review_03`, meaning `no_identified_issue`, retained linguistic qualifications `[]`; retained flags `[{"count": 2, "field": "text", "kind": "marker:square_brackets"}, {"count": 2, "field": "target", "kind": "marker:square_brackets"}]`.
- Existing curation scope: publisher paragraph ID and fields, not sentence-level or expert semantic validation. This triage does not upgrade that scope to expert adjudication.
- Source SHA-256: `c15037b883608384e9bbf9287b64300f57bab596ba3631a5260c44fb54db832b`; target SHA-256: `2b6d90e9764b38b708538ac0767a8639e20e50c649b96542971445fe76657c93`.
- Existing TRAIN row SHA-256: `b3f9a32b7b62f3cdebfd6a7412390c225e3b37615a9bc090af6b7a9ebaf1d918`; revision `7389365bbf086e221079291467cd08424c80d349e36a24a9ef3eccc6c5989acd`.
- Raw publisher response: `sources/local/parsig-2026-09-20/responses/251c60fab5d7e63218268d029003737237689254afc5b8917b99aea4bc3cad9e.json`; SHA-256 `eb63074767c8c7a827b3d2eb5adc3e43b4e8edd2459a38eca109a0af05869517`; record `Code=137001027`. Both raw section strings exactly equal the corresponding TRAIN text plus their recorded citation suffix.
- Recorded publisher URL (not accessed in this task): https://mpdb.parsigdatabase.com/surf/paragraph/137/137001/All.
- Retain the publisher’s “forthcoming” transcription-edition qualification. This task verified the saved public database witness, not a final published Hajipour edition. Source `[ī]` and target `[کار]` are outside the selected spans; brackets remain in the full contexts. If independent review requires a final print edition for the source phrase, withhold this third proposal rather than substitute a generated reconstruction.

## Complete census disposition

Rows retain inventory order within this family. Bins summarize a provisional reading of the complete source/Persian context; they are not admissible labels. The nine uncertain/other rows comprise contrastive/exceptive uses (24–25), five repeated Yasna commentary constructions (32–36), and governed/interrogative or otherwise unclear contexts (44–45). Numeric range row 62 is outside the three narrowly selected proposals.

| # | Parent | Work | Occurrences | Triage bin | Packet status |
|---:|---|---|---:|---|---|
| 1 | parsig:133000172 | parsig:133 | 1 | Temporal endpoint / duration | WITHHELD |
| 2 | parsig:151000028 | parsig:151 | 1 | Temporal endpoint / duration | WITHHELD |
| 3 | parsig:151001018 | parsig:151 | 1 | Temporal endpoint / duration | WITHHELD |
| 4 | parsig:151001114 | parsig:151 | 1 | Temporal endpoint / duration | WITHHELD |
| 5 | parsig:151001115 | parsig:151 | 1 | Spatial endpoint / extent / numeric range | WITHHELD |
| 6 | parsig:151001157 | parsig:151 | 1 | Temporal endpoint / duration | WITHHELD |
| 7 | parsig:151001162 | parsig:151 | 1 | Spatial endpoint / extent / numeric range | PROPOSED_PENDING_REVIEW |
| 8 | parsig:151001193 | parsig:151 | 1 | Temporal endpoint / duration | WITHHELD |
| 9 | parsig:151006009 | parsig:151 | 1 | Spatial endpoint / extent / numeric range | WITHHELD |
| 10 | parsig:151006010 | parsig:151 | 1 | Spatial endpoint / extent / numeric range | WITHHELD |
| 11 | parsig:151006011 | parsig:151 | 1 | Spatial endpoint / extent / numeric range | WITHHELD |
| 12 | parsig:151006017 | parsig:151 | 1 | Temporal endpoint / duration | WITHHELD |
| 13 | parsig:151006018 | parsig:151 | 1 | Spatial endpoint / extent / numeric range | WITHHELD |
| 14 | parsig:151007009 | parsig:151 | 1 | Temporal endpoint / duration | WITHHELD |
| 15 | parsig:151012003 | parsig:151 | 1 | Temporal endpoint / duration | WITHHELD |
| 16 | parsig:151015005 | parsig:151 | 1 | Temporal endpoint / duration | WITHHELD |
| 17 | parsig:151020023 | parsig:151 | 1 | Temporal endpoint / duration | WITHHELD |
| 18 | parsig:151020026 | parsig:151 | 1 | Temporal endpoint / duration | WITHHELD |
| 19 | parsig:151026002 | parsig:151 | 1 | Temporal endpoint / duration | WITHHELD |
| 20 | parsig:151026036 | parsig:151 | 1 | Temporal endpoint / duration | WITHHELD |
| 21 | parsig:151026044 | parsig:151 | 1 | Spatial endpoint / extent / numeric range | WITHHELD |
| 22 | parsig:151039030 | parsig:151 | 1 | Temporal endpoint / duration | WITHHELD |
| 23 | parsig:151039031 | parsig:151 | 1 | Temporal endpoint / duration | WITHHELD |
| 24 | parsig:151043023 | parsig:151 | 1 | Other / uncertain contextual use | WITHHELD |
| 25 | parsig:151061021 | parsig:151 | 1 | Other / uncertain contextual use | WITHHELD |
| 26 | parsig:151061042 | parsig:151 | 1 | Purpose / governed clause | WITHHELD |
| 27 | parsig:134004031 | parsig:134 | 1 | Purpose / governed clause | WITHHELD |
| 28 | parsig:134007015 | parsig:134 | 1 | Spatial endpoint / extent / numeric range | WITHHELD |
| 29 | parsig:134009015 | parsig:134 | 1 | Temporal endpoint / duration | WITHHELD |
| 30 | parsig:134009018 | parsig:134 | 1 | Purpose / governed clause | WITHHELD |
| 31 | parsig:134009020 | parsig:134 | 1 | Purpose / governed clause | WITHHELD |
| 32 | parsig:301001003 | parsig:301 | 1 | Other / uncertain contextual use | WITHHELD |
| 33 | parsig:301002003 | parsig:301 | 1 | Other / uncertain contextual use | WITHHELD |
| 34 | parsig:301003005 | parsig:301 | 1 | Other / uncertain contextual use | WITHHELD |
| 35 | parsig:301004008 | parsig:301 | 1 | Other / uncertain contextual use | WITHHELD |
| 36 | parsig:301007005 | parsig:301 | 1 | Other / uncertain contextual use | WITHHELD |
| 37 | parsig:301007025 | parsig:301 | 1 | Temporal endpoint / duration | WITHHELD |
| 38 | parsig:136001018 | parsig:136 | 1 | Purpose / governed clause | WITHHELD |
| 39 | parsig:136001019 | parsig:136 | 1 | Temporal endpoint / duration | WITHHELD |
| 40 | parsig:136002007 | parsig:136 | 1 | Purpose / governed clause | WITHHELD |
| 41 | parsig:136002014 | parsig:136 | 1 | Spatial endpoint / extent / numeric range | WITHHELD |
| 42 | parsig:136003003 | parsig:136 | 1 | Temporal endpoint / duration | WITHHELD |
| 43 | parsig:136003007 | parsig:136 | 1 | Temporal endpoint / duration | WITHHELD |
| 44 | parsig:136003010 | parsig:136 | 1 | Other / uncertain contextual use | WITHHELD |
| 45 | parsig:136004005 | parsig:136 | 1 | Other / uncertain contextual use | WITHHELD |
| 46 | parsig:136004007 | parsig:136 | 1 | Temporal endpoint / duration | WITHHELD |
| 47 | parsig:136004012 | parsig:136 | 1 | Temporal endpoint / duration | WITHHELD |
| 48 | parsig:136005007 | parsig:136 | 1 | Temporal endpoint / duration | PROPOSED_PENDING_REVIEW |
| 49 | parsig:136008003 | parsig:136 | 1 | Spatial endpoint / extent / numeric range | WITHHELD |
| 50 | parsig:136008007 | parsig:136 | 2 | Temporal endpoint / duration | WITHHELD |
| 51 | parsig:137001000 | parsig:137 | 1 | Temporal endpoint / duration | WITHHELD |
| 52 | parsig:137001011 | parsig:137 | 1 | Temporal endpoint / duration | WITHHELD |
| 53 | parsig:137001013 | parsig:137 | 1 | Temporal endpoint / duration | WITHHELD |
| 54 | parsig:137001020 | parsig:137 | 1 | Purpose / governed clause | WITHHELD |
| 55 | parsig:137001022 | parsig:137 | 1 | Temporal endpoint / duration | WITHHELD |
| 56 | parsig:137001026 | parsig:137 | 1 | Purpose / governed clause | WITHHELD |
| 57 | parsig:137001027 | parsig:137 | 1 | Temporal endpoint / duration | PROPOSED_PENDING_REVIEW |
| 58 | parsig:137001042 | parsig:137 | 1 | Temporal endpoint / duration | WITHHELD |
| 59 | parsig:137002016 | parsig:137 | 2 | Temporal endpoint / duration | WITHHELD |
| 60 | parsig:137002017 | parsig:137 | 2 | Temporal endpoint / duration | WITHHELD |
| 61 | parsig:137002018 | parsig:137 | 2 | Temporal endpoint / duration | WITHHELD |
| 62 | parsig:150000001 | parsig:150 | 1 | Spatial endpoint / extent / numeric range | WITHHELD |
| 63 | parsig:150000028 | parsig:150 | 5 | Temporal endpoint / duration | WITHHELD |
| 64 | parsig:119000004 | parsig:119 | 1 | Temporal endpoint / duration | WITHHELD |
| 65 | parsig:101000002 | parsig:101 | 1 | Purpose / governed clause | WITHHELD |
| 66 | parsig:109000008 | parsig:109 | 1 | Purpose / governed clause | WITHHELD |
| 67 | parsig:109000009 | parsig:109 | 1 | Purpose / governed clause | WITHHELD |
| 68 | parsig:122000007 | parsig:122 | 1 | Temporal endpoint / duration | WITHHELD |
| 69 | parsig:108000001 | parsig:108 | 1 | Existing equal anchor | WITHHELD |

## Reproducibility and limits

Only this report was written. No rows, auxiliary targets, admission files or corpus files were changed. Independent review should check local phrase alignment and the inherited editorial qualifications; the three proposals demonstrate contextual contrast, not independent evidence of three more equal-sense occurrences. No fourth proposal was added merely to fill a quota.

Input fingerprints:

- `experiments/contextual-supervision-20260927/inventory.json`: `cb0606c9d7e4cd62bb678f23128b3223f75e5e099de8412c2385273d5102ef61`
- `experiments/train-audit-20260927/qualified-v1/train.jsonl`: `15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc`
- `experiments/train-audit-20260927/qualified-v1/final-ledger.jsonl`: `d79af2e64fbb92954c8b8d0ed9cb7a34e7e7d24d4c22ea9c22f1da6d569a8e77`
- `experiments/contextual-supervision-20260927/PROPOSAL.md`: `c15877ba05cac4053cc9260af5ebf2a109e013a81c0a61a60bd6c181f524b954`
- `experiments/contextual-supervision-20260927/published-occurrence.json`: `07cdd3ca85e26114bbac4a93a51ae4fd5c05f7152570920077db8e3fc39a19e5`
- `sources/A-Manual-of-Pahlavi-II-Dictionary.pdf`: `d49aaebbe1f51ebc07c616f538ff40a2a8d7ae9c3b810836c65689ab8a50f8c9`
- `resources/local/contextual-supervision-check/nyberg-pdf102.png`: `6bbe366bed86f612e3137d7e303fa7f1bc2680b3bce313fd6bc8a85fb0943569`
- `resources/local/contextual-supervision-check/nyberg-pdf198.png`: `5f5cb9370296e5c4199d4356161dff871dc1a8dbcefac6f6efeefa4c4d9a0ebe`
- `resources/local/contextual-supervision-check/nyberg-pdf199.png`: `9bde305786ea25452b1b99283907d3be6ed76b7c0c1342bd005449ad32eb9ff8`
