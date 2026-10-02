# Selected supervision and saved behavior: bounded independent audit

30 September 2026. Local evidence only; no training, inference, weights, network, source/reference changes, or Git actions. This audit recomputed labels for both actual 1,536-example streams and inspected the saved 24-case by three-checkpoint packets and both current reviewers. Full-pool composition is not training exposure. Findings are provisional linguistic interpretations, not specialist certification.

## Findings that change the diagnosis

1. **84% is accurate for old auxiliary supervised positions assigned to English-target tasks, not for corrected data or gradient share.** Old: 7,866/9,351 = 84.119%; corrected: 8,305/10,583 = 78.475%. Excluding the two-token terminator gives 7,552/8,583 = 87.988% and 7,999/9,815 = 81.498%. These are task-language buckets: their payloads include JSON syntax, numbers, names and other material; this is not token-by-token English identification. The often quoted wording “84% auxiliary target text is English” needs this denominator qualification.
2. **The two trailing labels are not two EOS tokens.** Verified tokenizer encoding is `[106,107]`, `<turn|>` then newline. EOS itself is ID 1. Every selected row in both streams ends with those two labels. There are exactly 19 examples with one payload token plus these two labels in each stream. In corrected data all 19 are pedagogy; in old data 18 are pedagogy and one is Persian lexical. No corrected lexical task has a payload of five tokens or fewer: lexical wrappers materially change this diagnosis.
3. **The output problems are real and already rated.** Unsupported glosses, untranslated-looking Persian spellings, role changes and confident handling of unresolved spans occur in the saved outputs. The fresh panel already records the material examples below as meaning/critical errors. This is not evidence that the review screen missed them.
4. **The local dictionary pool contains zahag = offspring, but neither selected stream exposes the model to that entry.** Exact source search for word-boundary zahag/zahāg finds zero in either selected stream after joining each selected ID to its source projection. Pool availability must not be described as successful teaching of this word. This bounded spelling search does not prove absence of all morphological variants or all earlier checkpoint training.

## Exact selected-label census

For a row with n supervised positions, its two terminator positions receive coefficient 2/n in the per-example mean objective. The last column below is the mean of that coefficient over the group. It is **not measured loss, probability, gradient norm, parameter effect or damage**. Those require teacher-forced NLL/gradient evidence or a controlled comparison, unavailable here.

| Stream / group | Examples | All labels | Payload labels | Terminator coefficient mass |
|---|---:|---:|---:|---:|
| Old all | 1,536 | 67,456 | 64,384 | 12.2244% |
| Corrected all | 1,536 | 68,724 | 65,652 | 10.9500% |
| Old auxiliary | 384 | 9,351 | 8,583 | 26.0497% |
| Corrected auxiliary | 384 | 10,583 | 9,815 | 20.9932% |
| Old historical FA | 1,152 | 58,105 | 55,801 | 7.6160% |
| Corrected historical FA | 1,152 | 58,141 | 55,837 | 7.6023% |
| Old pedagogy FA | 127 | 651 | 397 | 42.9496% |
| Corrected pedagogy FA | 131 | 669 | 407 | 43.0885% |
| Old lexical FA | 96 | 783 | 591 | 30.1902% |
| Corrected lexical FA | 96 | 1,558 | 1,366 | 13.0619% |
| Old lexical EN | 64 | 2,046 | 1,918 | 6.5369% |
| Corrected lexical EN | 64 | 2,618 | 2,490 | 5.3932% |
| Old lexical MMP EN | 32 | 299 | 235 | 25.1548% |
| Corrected lexical MMP EN | 32 | 523 | 459 | 12.8937% |
| Old documentary EN | 57 | 5,378 | 5,264 | 5.5132% |
| Corrected documentary EN | 53 | 5,021 | 4,915 | 5.5169% |

Edition-spans EN is unchanged: four examples, 143 labels, 135 payload labels, 8.2054% mean terminator coefficient. Inscription FA is unchanged: four examples, 51 labels, 43 payload labels, 19.9621%.

| Payload-token count | Old all | Corrected all | Terminator share within one example |
|---|---:|---:|---:|
| 1 | 19 | 19 | 66.667% |
| 2 | 46 | 37 | 50% |
| 3 | 60 | 31 | 40% |
| 4 | 42 | 32 | 33.333% |
| 5 | 39 | 26 | 28.571% |

Thus terminator coefficient exceeds half only in 19/1,536 examples in each stream; equals half in 46 old / 37 corrected examples. Saying “short-example loss is mainly EOS” overstates what is known. Even for a one-token payload, loss magnitude need not follow its coefficient because an already predictable terminator may contribute little NLL.

English-target auxiliary examples are 157/384 old and 153/384 corrected: 40.885% and 39.844% of auxiliary equal-example weight, or 10.221% and 9.961% of the full stream. Their payload-only coefficients sum to 9.199% and 9.256% of the total objective, respectively. English task token bulk therefore does not establish objective or gradient dominance. The substantive mismatch remains that dictionary/structured reconstruction and Persian passage translation are different tasks; transfer is unproven.

Runtime evidence: `cloud_pilot/mixed_train.py:67,138,147` fixes microbatch one, accumulation 16, `model_accepts_loss_kwargs=False`, mean of per-example supervised-token means. Recovered corrected `experiments/training-ready-v2-20260929/recovered/mixed/training/run.json:26-27` records the same loss reduction. Tokenization appends `bundle.TERMINATOR` in `experiments/mixed-supervision-20260929/prepare.py:113`; its definition is `cloud_pilot/bundle.py:40`.

## Saved behavior and existing ratings

Line references below use `experiments/corrected-review-20260930/reviewer-A/packet.jsonl`; the same row numbers in A's `reviews.jsonl` hold the cited ratings. B line references refer to B's `reviews.jsonl`. Mapping is from `lead-only/mapping.jsonl`, not inferred from output style.

- **Invented authority through an explanatory gloss:** corrected case020, A packet/review line65, explicitly adds `هوشگر (= عطارد)` and `[حرکت را]`, then says kings are killed. The published reference says اختر خوشه and seasonal cold/tree withering/autumn. Both A65 and B69 mark critical errors. Mixed case020 also says Mercury (A46/B48); step280 is already critical (A67/B57). This proves an unsupported gloss in the output, not the causal origin of the formatting habit.
- **Unsupported restriction in a constrained case:** corrected case018, A55/B44, adds `سردگان (= گوسفندان پیشکش)`. Both rate supported meaning error plus overconfidence; the final starred verb remains unresolved in the evaluation contract. The incorrect sheep restriction is judged independently of that uncertainty.
- **zahag:** cases021 and023 contain explicit `ضحاک` in all three checkpoints. Case021 A lines10/14/20 and B29/14/26; case023 A63/2/49 and B68/20/58 (step280/old/corrected respectively). Both reviewers classify supported errors as critical. This is a repeated participant-identity error rather than merely unknown wording. Case024 has `ضحاک` four times in step280 and old mixed (A59/15); corrected A35 spells the form `ضحک` four times. It is not a demonstrated recovery to “offspring,” but the spelling alone does not establish intended mythical identity. A rates corrected024 critical; B41 rates meaning error and explicitly avoids settling disputed final bindings. Do not overstate reviewer unanimity here.
- **Opaque Persian spellings rather than usable translated meaning:** corrected case006, A21, renders the refuge clause as `بی‌ستن` and the elapsed-time clause as `دیگر نمد`. A marks meaning error; B55 marks critical. Corrected case015, A54, retains opaque technical forms and turns “only the dog” into “the dog's voice.” Those are actual semantic failures; an exhaustive count of “transliterations” would require expert criteria and was not invented here.
- **Brackets are not uniformly bad:** case011 preserves `[...]` at the genuine unresolved lacuna in all three outputs; both reviewers classify unknown-span handling appropriately uncertain (A69/5/9, B27/34/70). Corrected case010 inserts `[است]`, a supplied copula, which cannot be called hallucination solely because it is bracketed. Bracket stripping would destroy useful uncertainty information.

Across 24 outputs each, literal `(=` appears in 2 step280, 4 old mixed and 3 corrected outputs; literal `[` appears in 5, 3 and 4. These counts are descriptions, not error counts. In the selected training targets, 397/1,152 historical examples contain `(=` and 425/1,152 contain `[`, unchanged across runs. This is compatible with a learned editorial style, but no ablation or base-model comparison identifies its causal source. Corrected lexical JSON targets also use brackets as serialization; raw bracket counts must not conflate JSON arrays, editorial supply and genuine lacunae.

## Existing local source evidence for zahag

- `resources/local/data-qualification-20260928/ready-v1/lexical-en.jsonl:3426`: CPD source variant `zahag`, published sense `child, offspring`.
- `resources/local/data-qualification-20260928/ready-v1/lexical-fa.jsonl:2552`: source-scoped `zahag`, target `زه (= بچه)، فرزند، بطن`.
- Corrected projections preserve these at `resources/local/training-ready-v2-20260929/data/learning-projections.jsonl:8173` and `:4716`, respectively; a distinct compound inventory is at `:4551`. The provenance identifies the raw Kosh files and raw/XML digests. No new DEV answer was added or used as a label.
- Neither exact lexical ID appears in the selected streams, and the joined selected source texts have zero bounded zahag/zahāg matches. Do not call this evidence that the updated adapter was explicitly taught these senses and refused them. A local qualified source is supporting evidence, not independent philological adjudication; no new remote source was fetched.

## What is established, and the smallest useful next decision

Established mechanics: payloads from heterogeneous tasks, equal-example weighting, terminator/newline positions, short pedagogy responses, dictionary entries available but unsampled, and repeated output failures already recognized by the review. Established limitation: 96 updates on 1,536 selected examples did not produce adequate passage quality.

Not established: that English “overwhelmed” Persian gradients, terminator supervision damaged translation, editorial formatting caused invention, or a particular optimizer/epoch/model change will fix the failures. The saved outputs cannot discriminate task non-acquisition from failure to transfer acquired skills. A new bulk review of these same 72 outputs will not supply that missing evidence.

Next bounded decision: first define a source-derived, non-DEV acquisition/transfer probe using genuinely consumed auxiliary examples and independent source context, with explicit unknown-span criteria. If paid inference is separately authorized, measure retained and corrected checkpoints on those same prompts and include payload-versus-terminator teacher-forced loss only if the approved runtime can report it. Use that result to choose between improving task acquisition and improving contextual transfer; do not automatically add epochs, strip every bracket, translate English dictionaries by machine, or train on DEV errors. A clean terminator policy can be specified for a future controlled comparison, but this audit does not justify claiming a quality gain from changing it.

## Reproducibility and hashes

`DATA-BEHAVIOR-COUNTS.json` stores the complete task census, coefficients, and short-example IDs/line numbers. Computation used the configured science Python with the already installed local `tokenizers` dependency. Labels were read from the actual train files; each row was checked for contiguous answer-only masking and exact trailing IDs, then decoded with the frozen tokenizer. No retokenization estimate or row-only proxy supplied the token census.

| Evidence | SHA-256 |
|---|---|
| Old selected train.jsonl | c32a7f21639c34107fd4a86c1c8dae3a8815b40c8107ff8c3075e0167535dc4a |
| Corrected selected train.jsonl | 22266b73d3a0f3c697aa4ced00f32d07e4d0198c11d36507778d4b6084a3ac59 |
| Frozen tokenizer.json | cc8d3a0ce36466ccc1278bf987df5f71db1719b9ca6b4118264f45cb627bfe0f |
| ready-v1/lexical-en.jsonl | 4d8c2489eca369d0d11a3364f5844cb5440d32eb53777c4ad138f5aff16c0f48 |
| ready-v1/lexical-fa.jsonl | 7979a688dc73a67f646920a668fbdeed6d1e21eb3f10f3810a59de9c427290fe |
| Corrected learning-projections.jsonl | d3e1ebee3cec70f748b95d241652f6e78ae265f084f1e09f83b809901a40d772 |
| reviewer-A/packet.jsonl | 72f839d0819cf841fc14415ca011e652c16528ceaf2c508e7c4e957b8c7e9ba2 |
| reviewer-A/reviews.jsonl | 2e7ed7c70c4c7a2cda61bf9c7a6c14c41ffb9f7cb39594b755654aa026b1e2d0 |
| reviewer-B/reviews.jsonl | 71c3d8792c60f6fbfc2c89efcf631c0d65331a7bf29264f0310a62eb7880425e |
| lead-only/mapping.jsonl | e31f0b329b669a9127f139f0fa2b9843b78646931ff50c029c4a954d723b1039 |


## Addendum: full external report F5–F10, Unicode and variety

The full external report `[USER_HOME]/Downloads/Telegram Desktop/PAHLAVI-REVIEW-REPORT.md` was read for F5–F10 after the initial audit. Its F6 proposed inference needs correction: a correct word sense somewhere in the inventory plus a persistent DEV error is **not direct evidence of failed auxiliary transfer** unless that supervision was actually consumed and acquisition demonstrated. F8 likewise conflates label coefficients with loss magnitudes; the corrected census above supplies the missing denominators. F7's claim that the model has “no means of abstaining” is stronger than these outputs establish: case011 already preserves an unresolved lacuna. The narrower supported finding is inconsistent uncertainty marking.

F5 reference comparison: of the 24 distinct case packets, 13 Persian reference translations contain literal `(=` and 19 contain `[`. Outputs contain these markers less often (2/4/3 and 5/3/4 by checkpoint). These are formatting rates, not comparable error rates, and the reference sample is tiny. Invented *contents* of individual glosses are the actual failure; a high training reference marker frequency does not by itself identify the cause.

### Private Unicode census, read only

Source census recursively counts source strings only; payload census for selected rows decodes actual nonmasked labels after removing the terminator. Pool targets recursively count target string values rather than metadata, property names, or prompts. The old learning-projection inventory has 10,152 records before its one exact duplicate collapse; corrected has 9,973. Detailed codepoint counts and representative decomposed strings are in the companion JSON.

| Scope | Records | Non-NFC source records | Non-NFC target records |
|---|---:|---:|---:|
| Old learning-projection pool | 10,152 | 16 | 11 |
| Corrected learning-projection pool | 9,973 | 16 | 11 |
| Old actual selection | 1,536 | 16 | 11 |
| Corrected actual selection | 1,536 | 16 | 11 |
| Distinct DEV source passages | 24 | 0 | not tested here |

All 16 selected non-NFC sources are documentary EN examples. Representative corrected train lines are 16 (`openampd:MP0046:full`), 112 (`MP0067:verso`), 192 (`MP0044:full`) and 256 (`MP0602:full`). Decomposed forms include i + U+0304, o + U+0304 and s + U+030C. All 16 source strings produce different token ID arrays after NFC under the frozen tokenizer. Its normalizer is only space-to-U+2581 replacement; it does not silently apply NFC. Thus this is a real, small representation inconsistency, not a merely theoretical concern. It does not explain the broad DEV failure by itself.

The 11 non-NFC targets are ten documentary examples and one historical Persian example, corrected train line116 (`parsig:545000007:pal>fa`), involving combining marks in `خیِّرند`. In both selections the decoded target payloads contain 134 Arabic yeh U+064A and 95 Arabic kaf U+0643. These are not replaced by NFC; treating Persian letter variants is a separate, language-aware policy. The corrected selected sources contain 541 U+00A0 nonbreaking spaces (old543), 140 combining macrons and 25 combining carons. DEV sources contain 19 NBSPs but no NFC changes. U+02BE occurs 44 times in selected sources and twice in DEV; it should not be casually removed as noise. Corrected source counts include š3,493, č482, ǰ219, ā9,777, ē5,478 and ō3,011.

No normalization was applied to saved training, references, or DEV data. A future canonicalization design should preserve raw originals and freeze transformed learning fields consistently before retokenizing or comparing prompts. Canonical-equivalence cleanup is defensible data hygiene; a quality improvement claim requires a separate experiment. No spelling substitution or diacritic stripping is supported by this census.

### Variety proxy

The external count is confirmed: 198/1,152 historical selected examples have work IDs beginning 5xx, in both runs; MMP English lexical examples contribute another32 selected rows. This is an ID/source convention proxy, not a fresh philological classification. DEV has six cases each from works103,112,138,517. Work517 has only two whole-translation cases (020/021) and four constrained cases; the others have 13 whole and five constrained cases.

| Reviewer / stratum | Step280 accepted | Old mixed accepted | Corrected accepted | Constrained critical step/old/corrected |
|---|---:|---:|---:|---|
| A, work517 | 0/2 | 0/2 | 0/2 | 4/4, 4/4, 4/4 |
| B, work517 | 0/2 | 0/2 | 0/2 | 4/4, 4/4, 3/4 |
| A, other works | 1/13 | 1/13 | 2/13 | 0/5, 1/5, 0/5 |
| B, other works | 1/13 | 1/13 | 2/13 | 0/5, 1/5, 0/5 |

Both work517 whole translations are critical under both reviewers at all checkpoints. This identifies a difficult work/subdomain, but work, content, length, transcription and variety are confounded, and the whole subset is only two cases. It cannot establish that mixing varieties caused harm, or that inserting a variety tag will fix it. Any future held-out probe should preserve source/variety strata in reporting before deciding whether tags are a useful intervention.
