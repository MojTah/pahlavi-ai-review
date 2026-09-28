# PAL-REF v1 — fixed Pahlavi reference benchmark

Frozen scope: 40 passages, 42 source paragraph records, five works, 160 directional cases.
Primary task: Middle Persian scholarly Latin transcription → English / Persian (80 cases).
Secondary, separately reported task: English / Persian → attested Middle Persian transcription (80 cases).
The reverse task measures reconstruction of attested passages, not free composition of new Pahlavi.

## Reference status and claim boundary

This is a **local published-reference benchmark**, not an internationally standardized test or an independently philologist-certified gold corpus. The named scholars supplied the translations; Codex did not generate or rewrite them. Codex checked exact extraction, attribution, matching paragraph spans, visible agreement between English and Persian, and absence of known material contradictions in the selected passages. `expert_adjudicated: false` remains truthful.

References reproduce the Parsig snapshot collected on 20 September 2026. English credits include Tafazzoli 1972, Asha n.d., Tarapore 1933, Grenet 2009 and Skjærvø 2011 as retained by the source. Persian credits are گشتاسب و حاجی‌پور 1398. The transcription edition and per-segment citation are in `references.jsonl`. Full raw selected records, source URLs and response hashes are retained in `source-evidence.jsonl`. This validates the saved publisher attribution and extraction; it is not a claim that every cited original book or manuscript was independently collated here.

Only a terminal bibliographic citation was separated from each text. Whitespace inside the source, spelling, editorial brackets, starred readings and published wording remain unchanged. Paragraphs 130000012–014 are joined with newline separators into one complete Faredun passage so its actors and pronouns are supplied by the actual text. No missing translation was invented. Preserve all editorial signs when submitting the input.

The sample was chosen for reference agreement and interpretability before running any model on it. It is **not a random sample of all Pahlavi**: it emphasizes counsel, religion and calendrical/mythic narrative, contains no native-script decipherment task, and does not certify legal/documentary or long-text translation. Work allocation is 8/4/10/10/8; report results by work as well as direction. Five works are five clusters. Forty passages, their 42 constituent records and their 160 translation directions are not independent sample sizes.

## Permanent identity

- Version identifier: `pal-reference-v1`. Do not edit, replace, add or remove any v1 case, reference, meaning check, prompt, normalization rule, count or scoring rule after the freeze.
- Run `benchmark.py verify` before every evaluation. A hash difference invalidates the run; never silently rebuild the manifest to make a changed benchmark pass.
- The manifest digest is anchored in `../pal-reference-v1.sha256` and Git. Results must record this exact digest, model/checkpoint identity, prompts, decoding, retrieval and timeout policy.
- Discovering a reference error means recording an external erratum and withholding affected claims. Do not silently fix v1, delete the difficult item, substitute an easier item or rescore history under a new denominator. Only an explicit user decision may authorize a separately named future version; v1 bytes and old results remain preserved.
- Prediction files, filled review sheets and reports belong outside this frozen directory.

## Leakage and partition rules

All 42 records originate in the existing TEST partition and their five work IDs are absent from the recorded TRAIN and DEV partitions. The original dataset files and split membership are unchanged. References for this curated subset have now deliberately been read by the benchmark curator; never claim this subset is still curator-unseen. The remaining original TEST retains its prior status.

Exclude all five works and their parallel witnesses, translations, reversed examples, paraphrases and answer-equivalent copies from subsequent training, continued pretraining, prompt tuning and retrieval evidence. `holdout-policy.json` freezes the work/record list. Passing the mechanical ID guard does not prove absence of undocumented semantic duplicates. The recorded normalized source-similarity and exact target checks found no selected matches in the existing TRAIN/DEV; the historical prediction/input/response scan found no selected IDs. These checks do not rule out base-model pretraining or unrecorded earlier exposure.

**Never give `references.jsonl`, `source-evidence.jsonl`, meaning checks or the whole `inputs.jsonl` to the model.** The queue includes reverse-direction inputs that are reference answers for other cases. Submit one case's source text and frozen prompt only, using a fresh conversation/cache state for each case. No prior case answer or review may carry into the next case. A runner may mechanically read the queue, but must not place the whole queue in context.

The standard v1 condition is source-only, with no retrieval, browsing, examples or answer-aware tools. Reference-assisted experiments may use these fixed cases only as explicitly separate conditions with a frozen permitted evidence inventory and leakage audit. Do not combine their scores with the source-only score or use benchmark feedback to tune the next candidate. Use DEV for tuning. Log every benchmark exposure; repeated comparisons make it a fixed regression benchmark, not unlimited fresh confirmation.

## Fixed run conditions

Use the source and target names `Middle Persian (Pahlavi), scholarly Latin transcription`, `English`, and `Persian (Farsi)`.

System instruction (literal English text):

> Translate the supplied text from {source_language} into {target_language}. Preserve its meaning, participants, negation, names, quantities, and uncertainty. Do not add explanations, citations, or facts. Return only the translation. For Middle Persian output, use scholarly Latin transcription. If you cannot translate it, return exactly [UNRESOLVED].

The user message is exactly `source_text` for that case, without a gold translation, neighboring reference or meaning checklist. The instruction's language remains fixed across models. A model-specific official chat template may wrap these messages; record it and its hash. For an encoder-decoder model, serialize the identical instruction followed by two newlines and the source; record this interface difference.

Maximum output is 4096 model tokens and maximum generation time is 1200 seconds per case. These are generous fixed ceilings, not target runtimes, and not permission to launch a costly run. No truncation, hidden retries or cherry-picked seeds. Record the first attempt; stop a system-level failure as an incomplete run. Greedy decoding is the v1 standard where supported. A different decoding policy or evidence condition needs its own disclosed result; it never changes the benchmark. Pin model revisions and adapters, seed 42 where applicable, and the runtime. No model was run as part of this benchmark construction.

## Meaning assessment and fixed scoring

Blind reviewers to model identity. Read the source, both published references and the case's reference-grounded meaning checks. All substantive clauses must be preserved, not just keywords in the checklist. Accept equivalent spelling, transliteration, synonyms and natural paraphrase when supported by the source. The checklist is a review aid, not an extra target translation or an automated keyword test. Optional explanatory source glosses are not mandatory additions. Never penalize a defensible alternative solely because it differs lexically from one reference. If source interpretation is unresolved, mark `uncertain` and retain the reason.

Review these eight categories: lexical meaning, grammatical roles, negation/modality, names, numbers/quantities, omissions, unsupported additions, and source uncertainty. Record an output span and a source/reference-grounded reason for an adverse decision.

- `accepted`: all substantive meaning preserved, with no substantive correction needed. Minor stylistic/orthographic issues alone do not fail it.
- `meaning_error`: a substantive mistranslation, omission or unsupported addition.
- `critical_error`: reversal of prohibition/obligation, material participant-role reversal, wrong essential name/quantity, or invented content that materially changes the instruction/event.
- `uncertain`: meaning cannot be confidently adjudicated; this is not a pass.
- Execution outcomes `abstain`, `timeout` and `error` are recorded independently and stay in all denominators. A complete-looking answer is not automatically correct. `[UNRESOLVED]` must be `abstain`.

For each direction, report counts and:

1. Accepted fraction = accepted / **40**.
2. Critical-error fraction = critical_error / **40**.
3. Complete-output coverage = success / **40**.
4. Separate counts for meaning errors, uncertainty, abstentions, timeouts and errors.
5. Per-work counts and accepted fractions. Do not hide directions or work differences in one overall accuracy percentage.

These are descriptive scores on this fixed sample, not an exact population accuracy or a powered superiority test. One case changes a direction score by 2.5 percentage points. No significance threshold, general deployment pass mark or automatic model promotion is authorized here. For paired comparisons retain every case and show accepted→failed, failed→accepted, ties and unresolved cases; preserve passage/work dependence.

The supplied script aggregates recorded judgments; it **does not understand Pahlavi or independently validate a rating**. AI-assisted labels must stay labeled AI-assisted. A specialist-confirmed report requires two qualified independent human reviews, reconciliation of disagreements and evidence of qualifications outside this packet. Single-review or AI-only reports are provisional. Do not invent human reviewer identities. Published reference status is separate from reviewer status.

Automatic chrF++ may be reported as a secondary diagnostic with a pinned implementation and recorded normalization, but it is not the v1 meaning score and must never be displayed as percent-correct translation. No chrF threshold determines a pass.

## Practical use

Run `python benchmarks/pal-reference-v1/benchmark.py verify` from the project root.
Run `.../benchmark.py templates <new-output-directory>` to create a run manifest and blank predictions/reviews. Fill copies outside v1, never the frozen files.
Run `.../benchmark.py score <output-directory>` to validate identity/completeness and aggregate judgments. Untouched templates fail scoring. Use `.../benchmark.py audit-training <records.jsonl>` to reject named holdout works/records mechanically before training; also perform the semantic/witness overlap review above.

Local attributed research only. Source permissions are not expanded by benchmark creation; public redistribution needs its own source-rights decision. No corpus import, model training, paid inference, Drive action or email is part of this task.
