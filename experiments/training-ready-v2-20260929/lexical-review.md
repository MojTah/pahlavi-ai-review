# Lexical ready-v2 source projection review

**PASS for source projection, reviewed note scope, and unique input inventories.** This is not permission to train, a prediction of quality improvement, or expert certification of the source dictionaries.

## Result

| Pool | Released parents accounted for | Versioned output rows |
|---|---:|---:|
| Persian source-scoped inventories | 2,676 | 2,606 |
| MacKenzie CPD English inventories | 3,506 | 3,412 |
| Manichaean Middle Persian English inventories | 1,426 | 1,420 |
| Total | **7,608** | **7,438** |

The 170-row reduction is consolidation, not deletion of supported meanings. All 150 different-target identical-input groups are combined into inclusive inventories with distinct source entries. One additional MMP group, entries 1030/1267, has an exactly identical target inventory; it shares one target entry while retaining both source-parent mappings. Every original lexical ID appears exactly once in lineage. There are no new lexical holds. Existing unreleased/held source material remains excluded.

## Data contract and boundaries

`lexical.py:build_lexical(projections)` returns `(new_projections, changes, holds)`. It requires all 7,608 unchanged released lexical parents. Nonlexical projections pass through byte-equivalent as JSON values. Source release files are SHA-256 pinned and never overwritten.

Each lexical output retains the first canonical parent ID and carries ordered `parent_ids`. The model receives the original source and context and one structured target, `{"entries": [...]}`. The integration owner updates the instructions to request all retained source-scoped entries, preserving meanings, qualifiers, compound components and related-form boundaries. IDs and notes are outside `learning` and must never be serialized into model input.

Within each target, unchanged complete inventories are wrapped as `{"senses": original_target}`. Only records with the same complete task/source/context are combined. Forms with different context, grammatical role, source scope or full form bundle are never combined merely because one surface spelling matches. No Cartesian product of forms and meanings, invented contextual translation, majority-vote meaning, or arbitrary entry-ID discriminator is introduced. Identical entry inventories can share an index; different inventories remain separate even when they overlap in wording.

`lexical_provenance.entries` retains every parent, its target-entry index, original learning/source/target hashes, original target, exact raw response/XML hashes and typed notes. The tracked `lexical-decisions.json` contains hashes, IDs, locators, spans and dispositions, not bulk lexical content. Full derived outputs stay in the ignored local corpus directory.

## Exact source review

The build rechecks every original lexical target and form against archived XML, rather than merely trusting the previous audit's status. CPD sense trees are reconstructed from their declared paths including sense numbering, grammatical components, nested grammar, attributes and usage qualifiers. FA plain-text senses are compared with the same declared NFC/whitespace normalization. MMP selected Unicode spans and grammatical role are matched to the original meaning and XML. Previously excluded examples and other held material are not imported.

All 150 unequal-inventory groups were read again for this projection decision: 79 CPD, 66 Persian and 5 MMP. Source boundaries are retained; no different published meaning was declared false. The one exact duplicate group was also read. These are whole-inventory inclusion decisions, not independent retranslation of every dictionary entry.

All 20 changed apparatus records were reviewed individually against their exact source text. The 17 Persian observation IDs are `da:3,42,56,58,59,68,69,76,83,84,85,96,101`, `dmx:107,550`, and `yz:13,70`; the three MMP IDs are `3127,4217,4856` (all Kosh).

- Fourteen Persian entries have exact, individually declared gloss/note splits. Main-headword senses remain in the target; derivation or related-form commentary moves to typed provenance. There is no general split-at-punctuation heuristic.
- `da:68` is resolved rather than held. Its explicitly named `watist` reference matches the archived same-collection entry `67`, whose form and gloss were checked. The derivation note points to this exact XML hash. Numeric adjacency alone is not treated as evidence; the explicit matching form supplies the referent. No meaning from entry 67 is added to entry 68's core target.
- `dmx:107` consists entirely of a compound analysis. Its two form/meaning components are represented directly under `components`; no fluent whole-word translation is invented and no empty definition is created.
- `dmx:550` keeps the infinitive's two numbered senses separately from the two inflected form/meaning pairs. Inflected translations are not attached to the infinitive.
- `yz:13` keeps the core sense separately from the named related form `ōpastan`, its published past-stem relationship and the published Old Shirazi qualifier. The key `headword_relation_to_this_form_as_published` makes the direction explicit: headword `ōpast` is the past stem of related form `ōpastan`, never the reverse. The qualifier is retained beside its source form, not silently deleted or generalized to unrelated forms. The full original line also remains in provenance; this is not independent adjudication of the author's historical linguistic claim. A targeted check pins this relationship direction after independent review identified the earlier key as ambiguous.
- MMP 3127/4217 move only the exact `[Boyce]` attribution to metadata. Their semantic/grammatical qualifiers and original surrounding punctuation remain. MMP 4856 moves only its `Cf.` reference, preserving the main definition.

## Runnable checks and evidence

From project root:

```text
[USER_HOME]\.venvs\codex-science\Scripts\python.exe -B -X utf8 experiments/training-ready-v2-20260929/lexical.py
```

The CLI writes only `resources/local/training-ready-v2-20260929/lexical/{projections,changes,holds}.jsonl` and the metadata decision ledger. It performs a second full replay and checks exact equality, input immutability, nonlexical preservation, full parent accounting, canonical first IDs, unchanged senses for all ordinary entries, unique full inputs, all 20 special dispositions, the resolved cross-reference and the separated inflections. Deliberately missing a lexical parent or modifying an original target must fail admission. All checks passed locally; the output and script SHA-256 values are in `lexical-decisions.json`.

No model weights, tokenizer, GPU, cloud access, training, paid inference, credential, package installation, or network action was used by this lexical task. Prompt tokenization, sequence lengths, leakage checks, mixture selection and runtime checks remain integration responsibilities. Mechanical source agreement cannot prove that the upstream XML has no ordinary-letter typo or that dictionary supervision will improve contextual translation.
