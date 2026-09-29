# Grammar evidence for a qualified supervision packet

27 September 2026. This is a source check and annotation specification, **not a new training set or a claim of improved translation**. Root visually inspected the complete listed pages of the existing local study copies. No Drive access, new book download, corpus admission, benchmark change or paid computation occurred.

## Checked sources and pages

| Source | Exact local identity | Pages inspected in this checkpoint |
| --- | --- | --- |
| S22: ژاله آموزگار و احمد تفضلی، *زبان پهلوی، ادبیات و دستور آن*, Tehran: Moin, fourth printing,1382 SH | `sources/@RastarLib_زبان_پهلوی،_ادبیات_و_دستور_آن.pdf`; SHA256 `207aeda5eae48227902f0f208f9b24fd5623627dd4ca589b217268e69596df92` | PDF81–86, printed78–83; full page images, not OCR |
| S24: H.S. Nyberg, *A Manual of Pahlavi II*, Wiesbaden: Otto Harrassowitz,1974 | `sources/A-Manual-of-Pahlavi-II-Dictionary.pdf`; SHA256 `d49aaebbe1f51ebc07c616f538ff40a2a8d7ae9c3b810836c65689ab8a50f8c9` | PDF290–291, printed281–282; full page images, with noisy OCR used only to locate text |

Both complete source-file hashes match the existing manifest. Page images are local aids under `resources/local/grounded-supervision-pages-20260927/`; the source PDFs remain unchanged and excluded from Git. This does not imply complete new study of either book. The authors' illustrative text passages are not copied into a training set or treated as split-safe merely because a grammar cites them.

## Supported distinctions

1. **Prohibition versus assertion.** S22 printed80 explicitly describes `ma` as the particle used for prohibitions; printed83 distinguishes `nē` for negation from `ma` for prohibition. A narrowly defensible auxiliary label could identify the *function of an exact particle in a checked TRAIN clause*. It must not automatically assign the polarity of every neighboring clause, convert a prohibition into an affirmative instruction, or invent the meaning of its verb. A label such as “نهی” is a proposed project annotation grounded in this rule, not a verbatim publisher occurrence annotation.
2. **Imperative form is not always uniquely identifiable by an ending.** S22 printed79–80 and Nyberg printed281,§§5.6–5.7 describe several imperative forms. S22's printed80 footnote notes that an ending can also mark an optative. Therefore begin with clear *directive function*, not an unsupported universal morphological tag. A fragmentary or reported construction needs separate review.
3. **The `-išn` suffix does not always mean obligation.** S22 printed83 describes both verbal nouns and a necessity use. Nyberg printed281,§5.8 distinguishes abstract-noun, modal-predicate and other nominal/adjectival uses, with further compounds in§§5.9–5.11. An occurrence inventory is useful, but suffix matching cannot produce a “must/should” gold label. Only a checked contextual predicate can support a necessity annotation; retain non-modal occurrences as genuine contrasts, not mistakes to discard.
4. **Agent/patient relations require a construction, not a suffix guess.** S22 printed78 and81 explains how a transitive past construction and its auxiliary relate to agent expression and object agreement, including passive readings when no agent is expressed. Nyberg printed282,§§7.1–7.5 uses a historical passive description and discusses variation and later mixed constructions. Preserve the distinction between a traditional grammatical analysis and a natural Persian active translation. Do not infer who acted from a person ending alone.
5. **`-īh-` is not a universal passive detector.** S22 printed80 discusses passive morphology, while printed82 also illustrates intransitive formations from non-verbal bases. Nyberg printed282,§6.1 discusses the restricted synthetic passive and related formations. Assigning all matching strings to passive would introduce false supervision. A stem, context and participant analysis are prerequisites.

These rules explain why a simple regex can select review candidates but cannot certify clause-level meanings. The suggested annotation fields are: exact source occurrence and context; exact supported span; construction/function; published passage evidence and qualification; scholarly rule locator; what remains unresolved; annotation author/reviewer; and separate acceptance status. Do not add a lexical gloss where only a grammar rule is supported.

## Admission boundary

Use only unchanged rows in the qualified TRAIN file with validated ledger identity and all held-out work exclusions. Keep published passage translations separate from new project annotations. Each new occurrence annotation needs its own source/target compatibility review; two AI checks can support provisional development but are not specialist certification or 100% correctness. Existing qualifications survive every derivative.

No label is admitted by this note alone. The next concrete step is to join these rules to the actual candidate inventory and check a small varied packet, including contrasts and ambiguous cases. Do not train on DEV references, error corrections or model-written rationales. No new benchmark or score is defined here.
