# Next existing-model comparison — preparation only

1 October 2026. **DRAFT / NOT READY / zero runnable case prompts.** No model, optimization or paid job is used. The [approved strategy](../strategy-reset-20261001/REPORT.md) remains conditional; this document makes the intended inputs and missing admission evidence explicit. Do not lower the work-family requirement to fill the panel from the familiar S22 textbook examples.

## Question and conditions

Does supplying independently verified sentence relations improve translation beyond supplying complete relevant dictionary inventories? Keep retained Gemma step280 as the existing comparison system. This tests an assisted upper bound; improvement would not prove an automatic analyzer or unaided translator works.

| Condition | Model-visible input |
|---|---|
| A — source | Exact qualified Pahlavi transcription plus the common translation instruction. |
| B — source + dictionary | Same source/instruction, plus complete source-qualified inventories for the bound forms/lemmas; retain every applicable sense, qualifier and entry. |
| C — source + dictionary + analysis | Exact B input, plus independently supported occurrence-specific participants, morphology, relations, negation/scope and uncertainty, where attested. |

Use the existing common historical instruction (`cloud_pilot/bundle.py::PROMPT`) for all three. Append evidence in clearly labelled sections to B/C. Dictionary evidence means relevant complete inventories for the passage, **not all7,438groups stuffed into its context**. The selector must use source-qualified form/lemma bindings and preserve all applicable homonym/sense alternatives; no invented lemma, target-derived preferred sense or arbitrary first match. Display English evidence as English, not uncertified Persian gold. The full dictionary lookup remains available independently of actual case selection.

Analysis must add source-span-specific information beyond the earlier S04/S07 notes and58-attachment experiment. Preserve attributed traditional analyses, unresolved referents, optional participants and competing readings. Source/analysis authors must not derive relations from the Persian target or candidate model output. A published grammatical construction alone does not establish exhaustive token roles or a complete reference.

Keep the same precision, template, decoding settings and output budget in all conditions. Do not combine this with another precision/backbone search or training. Added information/length are deliberate; a gain cannot uniquely be credited to formatting.

## Required case record before freezing

Each case needs: exact source/witness/work-family and hashes; split/exposure history; source-unit bounds; relevant complete dictionary entry IDs/pins and source-form/lemma bindings; each supplied analysis claim's exact source span and independently published/qualified evidence; unresolved-field dispositions; independently qualified reference evidence; critical meaning constraints; and comparison-specific component denominators. No actual reference bodies or protected answers are included in this draft.

Select by declared source/structure strata, not known output success. Planning cap:24short cases across at least4work families,3conditions each, at most72first outputs in one load. Twenty-four is an upper cap, not a minimum; it is not a power claim. Start qualification with one bounded occurrence per additional family. At least one novel independently supported relation can qualify an analysis component; exhaustive token/POS/dependency coverage is not required. No legacy DEV/PAL rerun is part of that budget. Exclude unavailable/ambiguous cases before freezing; never shrink a denominator after a failed attempt. If eligibility, novel information or complete context capacity cannot be established, hold before payment. A familiar pedagogical-only question would require an explicit revised protocol and evidence limits.

## Measurement and prospective decision

Keep the old fixed merit and its recorded results intact. Apply the same semantic acceptance/critical-error definitions uniformly to A/B/C on the supplementary panel, reporting its own N and raters separately. Component fields cover only source-qualified constraints, with explicit denominators; do not turn an unscored unknown into a correct answer. Blind assessors receive output/reference evidence without condition/checkpoint identity. Same-family AI agreement remains provisional, not independent specialist calibration.

Primary pair: C versus B; secondary pair: B versus A. A proposed operational continuation screen is at least2net newly accepted cases across at least2work families, agreed separately by both raters, with no increase in critical errors versus either comparison condition and no previously accepted case becoming critical. Freeze the actual thresholds and full component rubric **after qualifying the panel and before generation**. These are proposed decision rules, not an established significance test, guaranteed power or model-promotion criteria. Incomplete outputs, unresolved rater/reference conflict or one-family gains make the result inconclusive rather than triggering automatic retries.

- C improves safely over B: prioritize authentic contextual analysis-conditioned supervision; qualify any automatic analyzer separately.
- B improves safely over A but C does not improve B: investigate retrieval/source-scoped sense use before paying for a grammatical pipeline.
- Neither qualified assistance helps: reconsider the representation/model path once, or pause for better evidence; no epoch/model sweep.
- Critical errors rise, evidence is incomplete or gains concentrate in one lineage: resolve the specific failure before another paid experiment.

## Current readiness and launch boundary

The saved [analysis candidate ledger](../usable-resource-20261001/analysis-candidates.json) has15construction candidates from one S22 textbook lineage,14previously selected, and **zero complete pilot cases**. Missing full lexical/analysis/reference/split qualification and multi-work coverage remain. The source-only view has no translation targets. The five Parsig occurrences are lexical-only; target-assisted directive/contrast labels and incomplete S23 fragments cannot fill condition C.

The newer [occurrence evidence ledger](../occurrence-evidence-20261001/README.md) adds12partial leads and3printed-checked typed dictionary recoveries for review. All6historicalnote parents were already selected; documentary readings/fragment scope and reference qualification remain unresolved. Four Annotated MPCD work options are acquisition leads, not complete cases. Literal exact dictionary hits do not resolve pronoun/adverb homographs or past-verb/noun categories; occurrence-to-lemma/source bindings remain required. Zero complete eligible cases are established.

The new plain-target candidate package is a separate training-data engineering artifact. It neither supplies an independent evaluation panel nor selects a new training stream. There is no executable comparison packet, cloud launch artifact or asserted current credit/price here. Avoid writing a speculative retrieval/scoring framework before case qualification; the existing template/tokenizer/scoring tools can be reused when concrete cases exist.

Before one later paid inference job: freeze cases/references/novelty audit and component rules, render all three complete prompts with the actual template/tokenizer without dropping evidence, verify capacity and bounded runtime/persistence, obtain independent exact-artifact review, check live funding/rate/idle jobs and obtain the exact launch authorization. Model weights stay cloud-only. No automatic training follows from a diagnostic result.
