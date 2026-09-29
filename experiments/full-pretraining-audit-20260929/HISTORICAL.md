# Historical component: exhaustive raw alignment and targeted quality review

Date: 2026-09-29. Reviewer: independent AI critic `/root/blind_pair_b`, using inherited model/reasoning settings. Provisional, not expert-certified. No frozen/source edits, network, cloud, credentials, installations, model downloads, training, inference or Git actions.

**Result: all 2,237 historical records have exact archived source/target mappings. The deeper screen identifies 17 records with inherited target-format artifacts and preserves three editorial-reading uncertainties. No confirmed material extraction/alignment defect or number/negation/participant reversal was established by this review. This is not a corpus-wide linguistic pass.**

## Coverage and method

The audit independently reopened and hashed 164 raw paragraph-endpoint JSON files spanning 76 works, using the archive manifest and publisher `Code`, `ChapterCode` and `Sequence`. It joined every historical ID to its raw list position, original export record and parent work. It compared the complete `Transcription` and `Translation` fields with each canonical source/target after removing only the exact recorded trailing edition/translator citation and exterior whitespace. All 12 mapping/provenance checks passed for every record. The raw embedded export object also exactly matches the independently read endpoint object.

All 207,146 source characters and 208,487 target characters were scanned. Coverage is 2,237 unique IDs, with no missing/duplicate ID. All targets pass the conservative Persian-script screen; no replacement-character, surrogate, empty-pair or extreme target/source-length candidate emerged. These tests cannot classify all language, grammar or meaning errors.

The existing ledger was used only for administrative membership, citations and exclusion identity. All 247 ledger rows outside the retained set remain absent; the retained set exactly matches its administrative inclusion set. No retained row belongs to the 16 protected work IDs. Prior `ELIGIBLE` or qualified labels were **not** accepted as semantic proof. This checks the registered exclusion policy, not unregistered alternate-witness or paraphrase leakage.

The final mechanical screen flagged 129 unique rows. I read those complete source/target strings to adjudicate the flags, plus the four duplicate-group members and one initial detector false positive: **134 unique pairs received targeted full-pair reading**. Both duplicate groups additionally had their neighboring raw units inspected. The other 2,103 pairs received exhaustive mechanical/provenance screening, not individual linguistic reading. No claim that all 2,237 pairs were linguistically reviewed is made.

[historical-audit.json](historical-audit.json) contains an entry for every ID, hashes, raw file and exact zero-based JSON pointer, publisher code/sequence, canonical/export line, checks, features and actual selected-train occurrence. Its 134 adjudications are bound to source and target hashes. It contains metadata and English adjudication reasons, not bulk source/target copies. All 129 currently flagged IDs have adjudications.

## Adjudicated findings

### Confirmed inherited formatting artifacts — low severity

Fourteen target records contain consecutive join controls under `[U+200C U+200D]{2,}`; in these records the controls are ZWNJs. All fourteen complete pairs were inspected. The exact same runs occur in the publisher's archived translation, so this is inherited typography rather than a new extraction corruption. Eleven of the fourteen occur once in the selected 1,536-row mixed train.

- `133000037`, `133000089`, `133000265`, `151006015`, `151042005`, `134007039`, `559000003`, `540000003`, `531000003`, `539000003`, `557000001`, `557000002`, `557000003`, `541000001` (all IDs have prefix `parsig:` and suffix `:pal>fa`).
- The most conspicuous is `parsig:134007039:pal>fa`: a run of **30 ZWNJs** within the Persian plural expression. Exact locator: `sources/local/parsig-2026-09-20/responses/d16626d600771a523ed15915fe93eded69fe4fbb316155ac86ceae8c5725de33.json`, JSON pointer `/38`, publisher code `134007039`. It occurs once in selected train.
- `parsig:151001160:pal>fa` contains U+200E LRM, and `parsig:109000003:pal>fa` and `parsig:109000011:pal>fa` contain U+00AD soft hyphens. All three occur once in selected train and exactly match their archived targets.

These are **17 distinct affected records, 14 selected-train records**. Readable lexical meaning remains. No effect on training quality or causation of the previous model result was demonstrated. A future authorized data version could normalize these controls with a reversible before/after map and tokenizer revalidation. Do not mutate the frozen version during this audit.

### Numbers, negation and kinship flags — no confirmed error

- All **19 quantity flags** were inspected. They resolve to fused hundreds, fractions, additive numerals represented by digits, contracted spellings, or homographs. Examples: the source components for 99,999 match `99999`; source one-third expressions match Persian ordinal fractions; `dah` in the praise instruction is the imperative “give,” not ten. The corresponding ID-specific explanations are in the receipt.
- All **77 negative-marker flags** were inspected. Most are Persian prohibitions, inflected negatives or compound predicates outside the deliberately narrow detector. Two source `ma-agar` cases are lexicalized lest/perhaps constructions, not independently omitted prohibitions. Metadata records short evidence offsets rather than bulk quotations.
- The one kinship flag, `parsig:136001020:pal>fa`, uses literary Persian “دخت” for daughter. The kinship and giving-in-marriage relation remain.
- The initial detector incorrectly split the casefold decomposition of the word for fifty in `parsig:122000011:pal>fa`, producing a false five candidate. Reading the pair showed agreement with target 50. The audit script was corrected to apply NFC **after** casefold; no corpus data changed. This extra reviewed ID is retained in the adjudication record.

These observations clear the identified flags only. The detector does not count every linguistic negation or derive grammatical roles, and absence of a flag is not a meaning pass.

### Editorial notation and reading uncertainty — retain for specialist review

All **18 angle-bracket candidates** were inspected. They are archived scholarly transcription apparatus, not leaked HTML. Editorial notation must not be stripped as markup. Three require explicit limits:

| ID | Exact raw locator within the archive | Unresolved issue |
|---|---|---|
| `parsig:151061036:pal>fa` | Endpoint `surf/paragraph/151/151061/All`, publisher code `151061036`; receipt supplies file and JSON pointer | An angle-bracketed negative is embedded in a larger negative conditional; the target expresses a positive destruction purpose. Deletion/emendation convention and clause scope must be established before alleging or clearing a reversal. |
| `parsig:123000032:pal>fa` | Endpoint `surf/paragraph/123/123000/All`, publisher code `123000032`; receipt supplies file and JSON pointer | An angle-bracketed conjunction affects the expression involving Amitus and Caesar's nephew. The target uses an apposition. The edition's apparatus convention determines the intended participant structure. |
| `parsig:136006008:pal>fa` | Endpoint `surf/paragraph/136/136006/All`, publisher code `136006008`; receipt supplies file and JSON pointer | The source explicitly supplies alternative readings; the published target selects “now.” Source fidelity preserves the choice but does not settle the philological alternatives. |

These are unresolved published-reading questions, **not confirmed new data defects or instructions to repair targets**. Exact source/target byte identity alone does not settle them.

### Duplicate source groups — compatible meanings

Only two repeated normalized-source groups occur within this historical component, both with two records:

1. `151001010` and `151014005` are separate *Mēnōg ī Xrad* introductory formulas. Raw neighbors show distinct chapter contexts. One target adds an optional explanatory “because” gloss; neither changes the formula's meaning. Neither record occurs in selected mixed train.
2. `107000007` and `113000007` are the closing formula at the ends of two separate works. Targets differ only by the final period. Both occur once in selected mixed train. **These are not incompatible translations.**

There is no group of the same normalized target paired with different normalized sources under this script's deliberately conservative NFC/casefold/whitespace normalization. This is not a near-duplicate or semantic equivalence census.

## Sentence scope and residual limits

The original alignment grain is a **publisher paragraph association**, including clauses, headings, formulas and fragments. It is not a set of independently certified sentences. Full-corpus mechanical scope cues find 160 sources of at most three whitespace tokens, 599 ending in comma/colon/semicolon, 1,113 starting with a common connective, and 519 containing an editorial/gap marker. These overlap and are **not error counts**. They show why original parent context and uncertainty must remain available; this audit did not realign or merge units.

No non-Persian target or garbled-target failure was established by the conservative screen and targeted reading. This does not prove every target's language or fluency, resolve quoted-language source content, certify every name/role, or rule out subtle omissions. Source-font legacy text is retained in raw objects but was not decoded as a new script-validation exercise. No dictionary/source edition was newly fetched. Qualified human philological review remains necessary for a whole-corpus semantic certification and the three apparatus questions above.

## Reproduction and boundaries

Run only the metadata checker with the existing interpreter:

```powershell
& '[USER_HOME]\.venvs\codex-science\Scripts\python.exe' -B -X utf8 'experiments\full-pretraining-audit-20260929\historical_check.py'
```

The checker writes only its allowed `historical-audit.json`, retains hash-bound AI adjudications entered after targeted reading, and rejects stale source/target bindings. It does not generate linguistic judgments. Source and output identities are recorded inside the receipt. It includes executable assertions for 2,237 unique IDs and 247 administrative exclusions. No prior review flags, corpus labels or targets were changed to make checks pass.
