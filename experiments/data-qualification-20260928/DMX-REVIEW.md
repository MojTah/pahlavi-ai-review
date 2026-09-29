# DMX full literal/semantic anomaly review — 2026-09-28

**All 1,030 DMX lexical inventories were read;46 observation-level holds affect 46 inventories.** The other 984 have no newly detected anomaly hold in this bounded scan. That is not a claim of 984 error-free, expert-certified or training-admitted records. No source form, gloss, corpus, split or model was changed.

The actionable overlay is `dmx-review.json`, keyed by original `kosh:dmx:ID`. Every hold preserves the original form, target, complete-XML hash and raw-source receipt. The reviewer is `/root/seen 20_blind_a`. Root integrates and an independent critic may revise these provisional source judgments.

## Actual coverage and evidence

The DMX collection in `resources/local/dataset-expansion-20260928/lexicon-v1/lexical-resources.jsonl` contains 1,030 grouped inventories covering 1,039 original observations. I read the complete compact form/meaning output in five consecutive, nontruncated batches: rows 1–210, 211–420, 421–630, 631–840 and 841–1030. These row ranges are not source entry IDs; original observation IDs are retained throughout.

Original XML for flagged records was inspected from `resources/local/kosh-quality-20260928/complete-v4/observations.jsonl`. All 1,039 DMX observation senses were also checked mechanically against their inventory targets after NFC/whitespace normalization. That equality proves extraction correspondence, not linguistic truth. Suspicious spellings therefore cannot be dismissed as this extraction's mistakes: they are present in archived source XML.

I indexed the executed 200-case review (132 cases involve DMX) and reused targeted decisions POLY026, POLY095, POLY096 and POLY104 for the scribe/horse, creation/rending, cultivation/killing and wine/prohibitive questions. Reuse means relevant prior judgments informed this scan, not 132 new independent reviews or a fresh rerun. No Gemini output was used or submitted.

**28 complete MacKenzie/Kosh XML entries** were checked for targeted corroboration. Their IDs and XML hashes are in the JSON. No new PDF print page was inspected in this DMX task, and no claim of a new independent website retrieval is made. The dictionaries can preserve differing source senses; MacKenzie does not automatically override Tafazzoli.

## Hold inventory

All IDs below have prefix `kosh:dmx:`. JSON provides the individual reason, exact original forms/targets and evidence hash for every ID. Source-form holds denote unresolved suspected defects, not proof that every unfamiliar spelling is invalid.

| Reason class | Count | Observation suffixes |
|---|---:|---|
| LITERAL_TARGET_DEFECT | 16 | 22, 67, 70, 112, 191, 239, 367, 616, 649, 713, 780, 827, 904, 908, 1011, 1028 |
| SOURCE_FORM_DEFECT | 9 | 75, 194, 307, 389, 448, 479, 718, 1023, 1037 |
| GRAMMATICAL_SCOPE | 3 | 83, 387, 406 |
| SEMANTIC_ASSIGNMENT_UNRESOLVED | 7 | 133, 350, 502, 562, 579, 830, 866 |
| HEADWORD_ASSIGNMENT_UNRESOLVED | 1 | 201 |
| COMPOUND_TARGET_SCOPE | 4 | 352, 401, 402, 887 |
| LITERAL_DEFECT_AND_EDITORIAL_UNCERTAINTY | 1 | 435 |
| TARGET_COMPLETENESS | 2 | 474, 554 |
| NEGATION_SCOPE | 1 | 485 |
| EDITORIAL_UNCERTAINTY | 2 | 526, 722 |

The four pre-existing root holds 191,649,713,908 are retained. Newly noticed literal Persian defects include بدن غم, صقت, بهذین, کرانهف, سختن, خامص, کناهکار, عغمگین, مکن بودن, نابودن and نگزیدن. None was silently corrected. The correction candidate may look obvious, but original print is still needed before assigning a corrected source-qualified target.

Material mapping concerns include finite or infinitive phrases glossed at another grammatical scope (352,401,402,406,887), unlicensed-looking negation in 485, good-deed/thought confusion in 502, and speech/behavior wording in 866. These are held for headword/layout/context resolution; this review does not claim the original historical passage itself is wrong.

Some disagreement remains unresolved: a-pōhišn with thirstlessness, bōy with بودن, bunag with کامل فکری, and the belief/movement wording of 830. Their full raw sense inventories remain available. No consensus vote, dictionary-frequency rule or invented Persian translation chooses the winner.

## Editorial uncertainty versus a modal meaning

- **435:** اعتقد is a literal spelling concern; شاید به معنی ... باشد additionally marks the lexicographer's tentative interpretation. Both reasons remain visible.
- **722:** شاید نوعی باز باشد tentatively identifies a bird. It is not a lexical modal gloss and must not become a definite falcon identification.
- **526:** source byt? and target میوه؟ explicitly mark an uncertain assignment. It is not an empty placeholder, but it remains held rather than certified.
- **905:** ممکن است، می توان describes the lexical possibility/ability of šāyēd. MacKenzie corroborates that modal meaning. It is preserved, not rejected merely because it expresses possibility.
- **474/554:** the complete XML explanations have unclosed parentheses. They are held for page-level completeness/punctuation verification; this does not establish that the plant or ritual-object definitions are false, nor does it prove missing words.

## Corroborated distinctions preserved

- **853 kištan:** the complete MacKenzie entry gives cultivation senses, while a separate kuštan entry means kill. Persian کاشتن، کشتن is retained as cultivation; the unvowelled second spelling is not used to invent a killing sense. This agrees with the prior POLY096 check against GBD 489.
- **928/929 kirrēnīdan:** the complete MacKenzie entry explicitly contains both rending and creation, with creation marked daevic. Both published DMX senses are preserved; the initial headword concern is narrowed rather than solved by deleting one meaning.
- **249 arzōmand:** valuable/worthy is explicitly supported by MacKenzie; ارجمند is not rejected on superficial similarity to another word.
- **318/329:** MacKenzie groups xwāhrīh/xwārīh with happiness/bliss. The unusual-looking form is not grounds to remove خوشی.
- **902 sōg:** a MacKenzie homograph means use/profit/advantage. A benefit-related compound is not rejected because another homograph means burning.
- **181 ēwāz:** separate MacKenzie entries distinguish word/utterance and sole/only. The DMX voice-related sense remains source-specific, not a contradiction automatically resolved in favor of only.
- **196/242 may:** noun wine and explicitly labelled prohibitive particle keep separate grammatical roles, following POLY104. They are not collapsed into a single target.
- **777 ēstādan:** standing and auxiliary uses remain together with their grammatical explanation. Rich sense inventories and internal form/gloss examples such as 550 are not flattened to one dictionary meaning.

These semantic non-holds or cleared concerns are recorded under `releases`; that key only clears the specified provisional concern. It does not grant training admission or override source-work, rights, benchmark-exposure or split checks.

## Limits and remaining source work

Tafazzoli's glossary print pages are still required to adjudicate the 46 holds. The literal form flags are intentionally conservative and must not lead to automatic spelling modernization; historical spelling/transcription variation can be legitimate. Forms such as ašhahānih, kannām, gēhān-marnǰnīdār and nīmadōmend were noticed but not excluded merely because unfamiliar. Additional specialist review may find defects among unflagged records.

The DMX glossary is a lexical resource tied to the Menog-i Xrad work/edition lineage, not 1,030 independent manuscripts or sentence translations. Complete numbered senses, form bundles, qualifications and grammatical scope must survive integration. Contextual expressions require their own passage clearance before contextual learning. Generic vocabulary supervision does not establish unseen-vocabulary generalization. No benchmark answers were inspected in this task.

## Deterministic verification and receipt

- Exactly 1,030 inventory groups and 1,039 distinct DMX source observations reconciled.
- All 46 hold IDs resolve to the reviewed collection, with no accidental release/hold overlap.
- All DMX inventory targets match archived sense text after the declared normalization.
- Hold evidence and 28 MacKenzie XML hashes recompute correctly.
- The four prior root holds remain; cultivation 853 is not held or merged with killing.
- All declared input file hashes rechecked unchanged; only the two owned review outputs were written.

Review JSON SHA256: `f5dfd81afb1f8ee5108692a135e82eabe50862411a4ffed9492cf852f2e3d369`. Input hashes and the precise original-source receipts are included in the JSON. No training admission, automatic source correction or expert certification follows from this review.
