# Canonical data integrity recheck — 29 September 2026

**Structural result: PASS. Semantic completeness: not certified.** The independent checker passed53checks over the10ready-v1 and7mixed-data files, totaling45,926,783bytes. Every frozen hash, byte count and record count matched; the mixed census also matched its separate manifest byte-for-byte. The17files were rehashed after reading and remained unchanged. No training, inference, cloud access, download or source edit occurred.

The initial omission claim for `S22GRAM-095` was withdrawn after two visual source rechecks. The existing record correctly retains its printed inventory and reported-speech usage context; no correction is warranted from this candidate. This audit confirms that the existing target reached training unchanged. Structural success still does not certify every corpus meaning.

## What was independently checked

- Exact release/mixed manifest bindings, builder/helper identities, and historical ledger identity; no blank JSONL lines or required top-level learning fields missing.
-10,152unique released IDs and verbatim learning projections;10,151unique tokenized pool IDs;1,536unique selected and consumed IDs. Actual training rows equal their pool records, and order equals both the frozen selection and recovered training log.
- All10,151pool records: valid integer token IDs, unpadded attention masks, contiguous answer-only labels, exact prompt boundary, and maximum length at most2,048. The observed maximum is1,144tokens. Every supervised sequence decodes exactly to its published released target plus `<turn|>\n`; row-audit target/prompt/learning hashes were independently reconstructed.
- All2,237historical rows preserve original token arrays and match eligible ledger source/target values. All247excluded historical rows remain out; the16protected work IDs are absent.
- All96optimizer blocks follow the fixed12historical +2lexical +2other order. No unselected or newly invented row was found in the consumed stream.

## Actual exposure

| Task | Released | Pool | Consumed |
|---|---:|---:|---:|
| Historical Persian translation | 2,237 | 2,237 | 1,152 |
| Persian lexical inventories | 2,676 | 2,676 | 96 |
| CPD English senses | 3,506 | 3,506 | 64 |
| Manichaean Middle Persian English inventories | 1,426 | 1,425 | 32 |
| Persian pedagogy/grammar | 240 | 240 | 127 |
| English documentary spans | 57 | 57 | 57 |
| Persian inscription spans | 6 | 6 | 4 |
| English edition spans | 4 | 4 | 4 |
| **Total** | **10,152** | **10,151** | **1,536** |

The consumed data contains67,456supervised tokens and258,988total sequence tokens. Pool supervision totals234,561tokens. These are task/exposure counts, not counts of independent passage translations or evidence of translation quality.

Historical data still spans76works with1,099/2,237pairs (49.13%) from `parsig:151`. The selected historical subset has a different concentration: its largest work is `parsig:133`,144/1,152slots (12.5%). Sampling changes exposure; it does not create new independent source evidence.

## Exclusions, duplicates and residual limits

The2,317scoped exclusion decisions remain separate:123Persian lexical holds,720CPD holds,564MMP holds,888textbook-glossary groups,4Parsig format-recovery cases,2S23cases and16decisions without a component label. No exact excluded ID occurs in the release. Persian parent resource IDs were also joined against all123held parent IDs, avoiding a false check caused by their different exported ID prefix.

All888S22glossary IDs, independently collected from the531+357candidate files, are represented in exclusions and absent from release, projections, pool and training. This does not mean all S22 material is excluded:240separately qualified pedagogical records are released and127were consumed.

Exactly one complete task/source/target/context duplicate was removed: `recovered:kosh:mmp:1267` maps to `recovered:kosh:mmp:1030`. The37registered source/target repetition groups remain represented; different grammatical or source contexts are not collapsed. There are1,108exact lexical form values shared by more than one inventory ID. They are not automatically duplicates, homonym errors or interchangeable senses. Projection equality confirms that this pipeline preserved the released inventories; it does not independently certify their completeness against every printed source.

The existing protected-source policy was independently repeated using only archived source transcriptions:1,555protected source strings;61auxiliary sources of at least5words screened;0normalized exact-containment hits. Another246short auxiliary sources fall outside that passage-length rule. The policy agrees across the release and corpus builders on all16protected works. It does **not** rule out paraphrases, short formulas, alternate witnesses, semantic overlap, shared vocabulary or unidentified work lineage. Benchmark reference answers were not parsed or serialized into supervision.

## Withdrawn candidate: S22GRAM-095

The released `kū` record teaches the Persian inventory “جایی که، تا اینکه” and retains the reported-speech usage in its supplied context. On PDFpage75/printed72, the following entry is separate: `ka`, glossed “که، زمانی که”. The initial reviewer incorrectly attached that following entry across the line break. The lead's independent image view and the source reviewer's subsequent visual recheck withdrew the omission claim. This structural audit did not itself perform either visual adjudication.

Exposure remains exact:1released row,1projection,1pool row,1selected row and1recorded consumption. It occupies training position1,183, i.e. update74/slot15. The decoded supervised target exactly matches the existing released target, with target SHA256 `39375b34086f9a7be4dc54b26fb7bac1e7e0628c30889dcaccedfe30612cd965`. These are exposure and serialization facts, not evidence of a semantic defect or an explanation of model behavior.

No source or training correction is warranted from this withdrawn candidate. Frozen data, source hashes and all53structural check results remain unchanged. The report and JSON semantic annotation were corrected after the visual rechecks; the structural checker did not adjudicate this reading. No data were admitted to training.

## Reproduction and evidence

Run from the full local research checkout with the project's installed tokenizer dependencies; the public snapshot intentionally omits the complete corpus:

```text
python -B -X utf8 experiments/mixed-supervision-20260929/prepare.py --check
python -B -X utf8 experiments/data-recheck-20260929/integrity_check.py
```

The first existing check passed and reproduced every mixed output byte-for-byte, including selection and reserved-token negative controls. The second independent check writes only [integrity.json](integrity.json), containing counts, hashes, check outcomes and a few diagnostic IDs, without source passages. See [checker](integrity_check.py), [release manifest](../data-qualification-20260928/release-v1.json), [mixed manifest](../mixed-supervision-20260929/data-manifest.json), [release decisions](../data-qualification-20260928/README.md) and [training log](../mixed-supervision-20260929/recovered/mixed/training/run.json).

Checks establish the stated structural invariants only. They do not certify all linguistic meanings, independent observations, optimal loss weighting, model quality, source redistribution rights or cloud/model state. No weights were needed or accessed.
