# Grounded auxiliary-supervision feasibility

27 September2026. Mode: **Classic + Critic**. This checkpoint supplies source-backed development annotations, not a trained model or a new quality score. Root owns integration; agent03 prepared the bounded TRAIN inventories/directive proposals; final_external_judge independently checked them. The previous goal turn made progress by completing the negative model/evidence comparison; this turn makes progress by replacing speculative auxiliary labels with actual source evidence.

## What changed

The public [Parsig grammatical search](https://parsigdatabase.com/tags/?lang=fa) returned five genuine occurrence IDs for the five previously selected, qualified TRAIN contexts. Their dialogs supply contextual Persian glosses, grammatical categories and edition/section locators. Every full source and Persian context matches frozen TRAIN after **comparison-only whitespace normalization**. Original TRAIN bytes, qualifications and source spans remain unchanged.

| Form | Published occurrence | Published gloss | Locator |
|---|---|---|---|
| xrad |107000001004|خرد|Jamasp-Asana1913:40/7; HP3:1|
| frazand |107000003004|فرزند|Jamasp-Asana1913:40/8; HP3:3|
| xwāstag |107000004004|خواسته، ثروت، دارایی|Jamasp-Asana1913:40/9; HP3:4|
| ruwān |107000006006|روان|Jamasp-Asana1913:40/11; HP3:6|
| hunsandīh |119000002009|خرسندی، قناعت|Jamasp-Asana1913:154/5; DH:2|

The fifth supplies the missing **occurrence-specific contentment sense**. It does not invalidate the separate legal “agreement” sense in the earlier book check. The source's lemma field `hunsand` is retained as observed, not promoted into lemma supervision. The earlier quarantined occurrence119000001003 was not opened or reused. Paragraph translations credit گشتاسب و حاجي‌پور،1398. Parsig is the annotation publisher; individual word-annotation authorship is not independently established.

`published-occurrences.json` is an explicitly labeled lead transcription of browser-visible fields, **not a raw API export**. Independent review checks its consistency and scholarly support, but cannot independently establish its transcription fidelity from that same file. The live footer permits use with attribution and retains copyright; this is not a blanket claim about all underlying edition rights. A single anonymous API request returned401; no authorization value was read or retried. Browser research tab closed.

The separate directive pilot selects the shortest standalone-ma TRAIN row in each of12 works without model outcomes or held-out answers. It contains16 occurrences:15 narrowly supported directive-function proposals across11 works, and one abstention. The independent critic provisionally accepts the15 local functions; reported advice in515 remains morphology-neutral, and555 retains only a minimal, non-exhaustive scope. Row551000002 remains unresolved. The inspected Amouzgar–Tafazzoli and Nyberg grammar pages support the functional distinction, not automatic morphology labels.

**Decision:** five lexical glosses plus15 local directive functions qualify as **20 provisional auxiliary-development annotations**. They are not expert-adjudicated gold,100% correctness, full-clause reinterpretations or automatic training admission. Immutable proposal files keep their original pending flags; `qualification-decision.json` records the subsequent reviewer-qualified decision separately. No training file changed.

## What this implies for the next experiment

There is now a concrete path to translation-plus-lexical/function supervision. Twenty labels establish feasibility; they do not justify another GPU run by themselves. Four lexical entries share one formulaic work, and all15 directive proposals contain ma. A constant “prohibition” answer could fit that one-class sample. Before training, obtain a modest, diverse set of published lexical examples and independently review assertion/positive-command contrasts; preserve ambiguity rather than filling gaps with generated labels. Regex-selected išn and numerals remain unadmitted.

The [bounded acquisition plan](COLLECTION-PLAN.md) would reuse the existing public-source collector for five raw canaries plus at most120 further eligible noun/verb occurrences. It awaits the user's specific credential-handling permission; no private account or paid service is involved. Index metadata may include excluded works, but their annotation details must never be requested or admitted. First establish actual response shape and check it against the five browser observations, then use deterministic TRAIN-only selection.

If enough genuinely new supervision survives review, the next paid hypothesis is **one mixed-task candidate versus a matched ordinary-translation continuation**, both starting from the same qualified Gemma checkpoint. That control distinguishes the recipe's effect from merely training longer. Predeclare data mixture, update budget and scoring before launch; record unequal target-token exposure where tasks differ. Reuse one downloaded cloud base if sequential arms reduce setup cost. Do not run a grid of epochs, models or prompts. No such training package or launch is admitted in this checkpoint.

The uniform merit contract is unchanged: PAL-REF source-only acceptance/critical errors each use40 cases; DEV uses15 whole translations plus9 separately assessed constrained cases. Preserve both reviewers and paired/work-level regressions, first attempts and failures. Auxiliary-task fit is a diagnostic, not a replacement merit function. No new model-quality result exists here.

## Evidence and operating boundary

- `SCHOLARLY-GRAMMAR-CHECK.md`: visually inspected, hashed local book pages; no new book download.
- `TRAIN-INVENTORY.md` / `inventory.json`: all2,237 qualified TRAIN rows checked; no held-out membership. Standalone-ma inventory54 rows/12 works; broader surface inventories remain candidates only.
- `lexical-packet.jsonl`: five exact TRAIN/context bindings, full original ledger qualifications and published fields. Reproduce with `resources/local/hf-client-venv/Scripts/python.exe -B -X utf8 scripts/prepare_grounded_lexical.py --check`.
- `DIRECTIVE-PILOT.json` / `.md`:12 rows,16 occurrence-level decisions;79 exact/UTF-8 span checks reported and independently verified.
- `REVIEW.md`: independent lexical/function/source-page review and actual negative checks; `qualification-decision.json` binds its result to exact proposal hashes.

No GPU job, cloud upload, model-weight download, credential access, Drive or email action occurred in this checkpoint. Last live HF balance remains the earlier09:54:59UTC observation of **USD17.12**, not a fresh balance read. All previously launched jobs were already terminal, and none was started here. Latest user authority permits strategically using existing funded credit; it does not authorize a top-up or require spending it. Development version remains0.10.4; version impactNONE for source qualification and research evidence.
