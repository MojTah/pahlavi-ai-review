# Qualified TRAIN occurrence inventory

2026-09-27. **Occurrence inventory only: zero new labels or training admissions.** Expert adjudication: false.

A small independent annotation effort is feasible, especially for directive function around standalone `ma`. These counts do not establish reliable prohibition, imperative morphology, necessity, or aligned numeric-value supervision. Original translations and qualifications remain evidence to review, not automatic gold.

## Scope and validation

All 2,237 qualified TRAIN rows passed the existing `validate(row, entry, heldout)` function: eligibility, heldout exclusion, row/source/target hashes, literal text agreement with the final ledger, and non-expert status. There are 76 works and 37,492 source whitespace-separated terms. Changed-source, quarantine, and heldout negative checks rejected their inputs. No heldout work occurred in the validated pool.

Extraction used only qualified TRAIN, its final ledger, heldout work IDs from the existing unlabeled inventory, and the validation helper. The helper build function was not called. No model outputs, DEV/TEST answers, unrelated knowledge bases, dictionary drafts, external services, or original review files were read for extraction.

| Frozen input | SHA-256 |
|---|---|
| `experiments/train-audit-20260927/qualified-v1/train.jsonl` | `15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc` |
| `experiments/train-audit-20260927/qualified-v1/final-ledger.jsonl` | `d79af2e64fbb92954c8b8d0ed9cb7a34e7e7d24d4c22ea9c22f1da6d569a8e77` |
| `experiments/dev-assisted-qualified-20260927/UNLABELED-DATA-INVENTORY.json` | `7eba461256dfcf44e324dde31d2b119cac1b4fae866ca0a53e705217389ba060` |
| `scripts/prepare_lexical_feasibility.py` | `d1fba3afed539bb9ccdcdf2de61af3e44aa8fabb6ae87b635d666e9b5bf9165e` |

Inventory SHA-256: `5eead36cf1b422da43779759faa795d611a5a955322521e6f737babb2cac2d7c`.

The machine-readable companion retains 1,019 candidate rows: exact original source/target strings, full original ledger entries (including qualifications, editions, credits, raw-source pointers and hashes), original file line numbers and byte offsets, and raw-line hashes. Span coordinates are Unicode code points, end exclusive, with UTF-8 byte coordinates also retained. Full target spans are paragraph witnesses, not word alignments. Original input bytes remain unchanged.

## Deterministic extraction rules

The complete finite form/number-word lexicons and thresholds are frozen in `inventory.json` under `selection_rules`. Completeness means all occurrences matching these declared rules within qualified TRAIN, not exhaustive linguistic recognition.

- **Standalone ma:** exact lexical token `ma`; every occurrence is retained. A narrower candidate requires `bāš`, a listed bare form, or a token ending `ēd` among the next four lexical tokens, before punctuation or `ud`. This surface co-occurrence window does not adjudicate clause boundaries, scope, mood, or prohibition. Endings can belong to optatives or other constructions: directive function needs independent review. Attached forms such as `ma-iz` are outside the standalone rule.
- **išn forms:** every lexical token containing literal normalized `išn`, with words ending in it separated from those with further material. Exact full tokens and internal sequence spans are retained. Deverbal nouns, adjectives, compounds and potentially modal constructions receive no necessity label.
- **Numerals:** decimal digit expressions and components matching finite cardinal/ordinal lexicons, independently on each side. Hyphen/ZWNJ/apostrophe components can be matched. One/indefinite uses, homographs such as Persian `نه`, `ده` and `سد`, ordinal senses, editorial digits and unequal segmentation remain unresolved. Other inflections and lexicon omissions are outside the finite rule. Matches are neither numeric-value nor alignment labels.
- Unicode normalization/case folding, and Persian yeh/kaf/combining-mark folding for numeral lookup, apply only to matching. Stored texts and offsets never change. There is no target correction or inferred gold label.

## Counts

| Candidate rule | Occurrences | Distinct TRAIN rows | Works |
|---|---:|---:|---:|
| All standalone ma | 63 | 54 | 12 |
| ma + visible-form window | 54 | 48 | 10 |
| ma + bāš window | 10 | 10 | 2 |
| Tokens containing išn | 1040 | 618 | 57 |
| Tokens ending išn | 788 | 481 | 53 |
| Source numeral matches | 584 | 345 | 43 |
| Target numeral matches | 777 | 457 | 50 |

Numeral matches occur on both sides in **310 rows**, source only in 35 and target only in 147. These are row intersections, not proven aligned numeric facts. Selected ambiguity flags occur on 124 source and 209 target occurrences; absence of a flag does not certify a reading.

Digit expressions alone account for 2 source occurrences in 1 row, and 23 target occurrences in 19 rows. Most candidates depend on number-word interpretation. There are 290 distinct exact token spellings containing išn.

## Short examples selected without model outcomes

Unique rows are ordered by shortest exact source character length, then TRAIN ID: first 12 ma-window rows and first 6 išn rows. Concentration in single works follows that ordering and is not a diversity sample. Source, target and qualifications are copied from frozen records. Target ranges cover the complete short translation and are not word alignments.

### ma with a visible following form

| TRAIN ID | Exact source | Exact target | Source spans; full target range | Existing qualification |
|---|---|---|---|---|
| `parsig:151001020:pal>fa` | `bēš ma bar,` | غم مخور، | `ma` [4,6); following `bar` [7,10); target [0,8) | No additional recorded qualification; not expert-adjudicated. |
| `parsig:151001037:pal>fa` | `ēw-mōg ma raw,` | با یک کفش راه مرو، | `ma` [7,9); following `raw` [10,13); target [0,18) | No additional recorded qualification; not expert-adjudicated. |
| `parsig:151001008:pal>fa` | `spazgīh ma kun,` | افترا مزن، | `ma` [8,10); following `kun` [11,14); target [0,10) | No additional recorded qualification; not expert-adjudicated. |
| `parsig:151001029:pal>fa` | `būšāsp ma warz,` | بیش از حد مخواب، | `ma` [7,9); following `warz` [10,14); target [0,16) | Demon/personification of sleep is translated by the behavior it names. |
| `parsig:151001016:pal>fa` | `xēšmēnīh ma kun,` | خشمگینی مکن، | `ma` [9,11); following `kun` [12,15); target [0,12) | No additional recorded qualification; not expert-adjudicated. |
| `parsig:151001023:pal>fa` | `waranīgīh ma kun,` | شهوت‌رانی مکن، | `ma` [10,12); following `kun` [13,16); target [0,14) | No additional recorded qualification; not expert-adjudicated. |
| `parsig:151001013:pal>fa` | `āz-kāmagīh ma kun,` | به آز متمایل مباش، | `ma` [11,13); following `kun` [14,17); target [0,18) | No additional recorded qualification; not expert-adjudicated. |
| `parsig:151001025:pal>fa` | `arešk ī abārōn ma bar,` | رشک زشت مبر، | `ma` [15,17); following `bar` [18,21); target [0,12) | No additional recorded qualification; not expert-adjudicated. |
| `parsig:151001100:pal>fa` | `was gētīg-ārāy ma bāš,` | بسیار گیتی‌آرای مباش، | `ma` [15,17); following `bāš` [18,21); target [0,21) | No additional recorded qualification; not expert-adjudicated. |
| `parsig:151001033:pal>fa` | `drāyān-ǰōyišnīh ma kun,` | در هنگام غذا خوردن سخن مگو، | `ma` [16,18); following `kun` [19,22); target [0,27) | No additional recorded qualification; not expert-adjudicated. |
| `parsig:151001035:pal>fa` | `wišād-dwārišnīh ma kun,` | بدون کستی و سدره راه مرو، | `ma` [16,18); following `kun` [19,22); target [0,25) | Kusti and sudreh unpack the ritual term wišād-dwārišnīh. |
| `parsig:151001039:pal>fa` | `az-pāy pēšārwār ma kun,` | ایستاده ادرار مکن. | `ma` [16,18); following `kun` [19,22); target [0,18) | No additional recorded qualification; not expert-adjudicated. |

### Tokens containing išn

| TRAIN ID | Exact source | Exact target | Source spans; full target range | Existing qualification |
|---|---|---|---|---|
| `parsig:133000082:pal>fa` | `kunišn wad.` | کُنش (= عمل)ِ بد. | `kunišn` [0,6); išn [3,6); target [0,17) | No additional recorded qualification; not expert-adjudicated. |
| `parsig:133000198:pal>fa` | `kunišn ī wad.` | عملِ بد. | `kunišn` [0,6); išn [3,6); target [0,8) | No additional recorded qualification; not expert-adjudicated. |
| `parsig:133000074:pal>fa` | `dēn-ōšmārišnīh.` | رسیدگی (= مراقبت) از دین. | `dēn-ōšmārišnīh` [0,14); išn [9,12); target [0,25) | No additional recorded qualification; not expert-adjudicated. |
| `parsig:133000167:pal>fa` | `kē āwēnišnīgtar?` | چه کسی بیشتر سزاوارِ سرزنش؟ | `āwēnišnīgtar` [3,15); išn [7,10); target [0,27) | No additional recorded qualification; not expert-adjudicated. |
| `parsig:133000196:pal>fa` | `kunišn ī frārōn.` | کنش (= عمل) درست. | `kunišn` [0,6); išn [3,6); target [0,17) | The parenthetical عمل merely glosses کنش. |
| `parsig:133000137:pal>fa` | `kē pad-rāmišntar?` | چه کسی آسوده‌تر؟ | `pad-rāmišntar` [3,16); išn [10,13); target [0,16) | No additional recorded qualification; not expert-adjudicated. |

The nominal short examples with `kunišn` and the differently formed words demonstrate why surface `išn` cannot be an automatic necessity label. Ordinary questions and explanatory Persian glosses remain as published and are not automatically errors.

## Counts per work

Each cell is occurrences / distinct rows. A dash means zero for that rule. JSON also retains per-work counts for bāš and ends-išn subsets. Work IDs are existing corpus IDs; no title or genre is inferred.

| Work | All ma | ma + form | išn | Source numeral | Target numeral |
|---|---:|---:|---:|---:|---:|
| parsig:101 | — | — | — | 1 / 1 | 2 / 1 |
| parsig:105 | — | — | 1 / 1 | 1 / 1 | 1 / 1 |
| parsig:106 | — | — | 1 / 1 | 1 / 1 | 1 / 1 |
| parsig:108 | — | — | 4 / 4 | — | — |
| parsig:109 | 2 / 2 | 2 / 2 | 3 / 2 | 1 / 1 | — |
| parsig:113 | — | — | 4 / 4 | 1 / 1 | 6 / 1 |
| parsig:115 | — | — | 2 / 2 | 1 / 1 | 1 / 1 |
| parsig:119 | — | — | 2 / 1 | — | 7 / 6 |
| parsig:121 | — | — | 1 / 1 | — | — |
| parsig:122 | — | — | 2 / 1 | 6 / 5 | 8 / 7 |
| parsig:123 | — | — | 4 / 3 | 28 / 10 | 31 / 11 |
| parsig:126 | — | — | 2 / 2 | — | — |
| parsig:133 | — | — | 73 / 59 | 3 / 2 | 3 / 2 |
| parsig:134 | 4 / 3 | 2 / 1 | 47 / 35 | 83 / 42 | 104 / 59 |
| parsig:135 | — | — | — | 1 / 1 | 1 / 1 |
| parsig:136 | 8 / 6 | 7 / 5 | 29 / 21 | 34 / 24 | 36 / 29 |
| parsig:137 | — | — | 72 / 35 | 58 / 24 | 87 / 33 |
| parsig:150 | 2 / 1 | 2 / 1 | 33 / 18 | 57 / 37 | 52 / 36 |
| parsig:151 | 33 / 33 | 33 / 33 | 372 / 277 | 183 / 128 | 241 / 186 |
| parsig:301 | — | — | 282 / 78 | 52 / 17 | 93 / 21 |
| parsig:302 | — | — | 8 / 2 | — | — |
| parsig:501 | — | — | 1 / 1 | — | — |
| parsig:502 | — | — | 7 / 4 | 1 / 1 | 2 / 1 |
| parsig:503 | — | — | — | 3 / 1 | 2 / 1 |
| parsig:506 | — | — | 3 / 2 | 8 / 5 | 9 / 5 |
| parsig:507 | — | — | 2 / 2 | — | 1 / 1 |
| parsig:508 | — | — | 3 / 1 | — | — |
| parsig:509 | 1 / 1 | 1 / 1 | 5 / 3 | 6 / 4 | 5 / 3 |
| parsig:511 | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 |
| parsig:512 | — | — | 2 / 1 | 3 / 2 | 2 / 1 |
| parsig:513 | — | — | 1 / 1 | — | — |
| parsig:514 | — | — | 7 / 3 | 3 / 2 | 3 / 2 |
| parsig:515 | 5 / 2 | — | 1 / 1 | 4 / 2 | 2 / 2 |
| parsig:516 | — | — | — | 8 / 1 | 9 / 1 |
| parsig:518 | — | — | 2 / 2 | 3 / 3 | 1 / 1 |
| parsig:521 | 1 / 1 | 1 / 1 | 8 / 5 | 1 / 1 | 3 / 3 |
| parsig:522 | — | — | 3 / 2 | 1 / 1 | 4 / 1 |
| parsig:523 | — | — | — | 2 / 2 | 1 / 1 |
| parsig:524 | — | — | — | 2 / 2 | 5 / 4 |
| parsig:525 | — | — | 3 / 1 | 2 / 2 | 5 / 3 |
| parsig:527 | — | — | — | 1 / 1 | 1 / 1 |
| parsig:528 | — | — | 1 / 1 | — | — |
| parsig:529 | — | — | 3 / 3 | 1 / 1 | 4 / 2 |
| parsig:530 | — | — | 3 / 3 | — | 2 / 1 |
| parsig:531 | — | — | 1 / 1 | — | 1 / 1 |
| parsig:532 | — | — | — | — | 1 / 1 |
| parsig:533 | — | — | 1 / 1 | — | — |
| parsig:534 | — | — | 1 / 1 | — | 1 / 1 |
| parsig:536 | — | — | 1 / 1 | — | — |
| parsig:537 | — | — | 2 / 2 | — | — |
| parsig:539 | — | — | 4 / 1 | — | — |
| parsig:541 | — | — | 1 / 1 | — | — |
| parsig:543 | — | — | 3 / 2 | 1 / 1 | 1 / 1 |
| parsig:545 | — | — | 1 / 1 | 4 / 3 | 5 / 4 |
| parsig:546 | — | — | 2 / 2 | 1 / 1 | 2 / 1 |
| parsig:547 | — | — | 1 / 1 | — | 1 / 1 |
| parsig:548 | — | — | 1 / 1 | 2 / 1 | 2 / 1 |
| parsig:549 | — | — | 2 / 1 | 4 / 3 | 3 / 3 |
| parsig:550 | 4 / 2 | 4 / 2 | 2 / 1 | — | — |
| parsig:551 | 1 / 1 | — | 1 / 1 | 1 / 1 | 1 / 1 |
| parsig:552 | — | — | 7 / 6 | 6 / 4 | 8 / 4 |
| parsig:553 | — | — | — | 1 / 1 | 1 / 1 |
| parsig:554 | — | — | 7 / 6 | 2 / 1 | 3 / 2 |
| parsig:555 | 1 / 1 | 1 / 1 | 2 / 2 | — | 2 / 1 |
| parsig:557 | — | — | 1 / 1 | — | — |
| parsig:559 | — | — | 1 / 1 | 1 / 1 | 9 / 3 |

## What independent annotation could establish

**Directive function is a bounded first target.** All 54 standalone-ma rows could be reviewed, including the six outside the visible-form subset; the 48 window candidates provide a smaller start. They cover 10 works, but 33 of 48 rows (68.75%) come from work 151. The bāš subset has only 10 rows across two works, nine from work 151. Review could resolve predicate, scope, directive/prohibitive function, mood uncertainty, and whether the Persian witness supports the same reading. Ten bāš examples cannot support a broad work-independent claim. Annotation must permit abstention and alternative readings; directive function does not establish imperative morphology.

**išn supports a diagnostic annotation pilot, not 1,040 necessity labels.** The 618 rows span 57 works, but works 151 and 301 supply 654 of 1,040 occurrences (62.9%). A small work-stratified review should distinguish nominal/adjectival uses, predicate constructions, and unresolved cases. That provides information absent from a suffix search. All six shortest examples are from work 133 and cannot characterize the full pool. Accepted modal-instance counts remain unknown.

**Numeral alignment is feasible as a separate small task.** The 310 rows with matches on both sides offer candidates, but values, units, participants, exact aligned spans, editorial status and uncertainty need independent adjudication. Lexical counts do not establish whether `نه` is nine or negation, “one” is indefinite, or two matched expressions refer to the same quantity. No match should become number-preservation gold automatically.

These inventories justify a limited independent annotation exercise, with adjudication of disagreements and preserved provenance/qualifications. A meaningful later training change requires new accepted span/function/alignment supervision beyond the existing translation pairs. Merely oversampling those pairs supplies no new evidence, and these counts alone cannot establish a benefit. Any comparison would need a predeclared change and separate fixed assessment with work-aware accounting. No annotation, admission, benchmark alteration or training is performed here.

## Verification boundary

Every retained occurrence span and UTF-8 coordinate is checked against the original field. Retained record strings and complete ledger entries, original raw-line byte locations/hashes, totals/per-work totals, example ordering/caps, and unchanged input hashes are checked after writing. Extraction is deterministic surface filtering. Linguistic accuracy, completeness beyond those rules, expert agreement, and model benefit remain untested.
