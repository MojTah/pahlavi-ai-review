# Strategic consultation for Design Pahlavi translation model

25 September 2026. Authorized research handoff; this is strategic advice for the execution owner, not a new run request, budget change, interruption or model activation.

**Decision: continue the project, redirect the next evidence-gathering phase, and pause only unsupported repeat sweeps or scale-up. There is no basis yet to declare either a working general translator or an impossible goal. Do not wait idle for a larger GPU.**

Complete the existing ByT5 checkpoint recovery and matched meaning comparison at the original run's safe termination boundary. Three recorded epochs and a declining DEV loss are not a semantic result. Include the eight regressions plus the three additional critical screen cases, then the matched screen; the eleven diagnostic rows share six passages. Preserve the already frozen S04 diagnostic and all existing execution/permission gates. No active configuration or original run is to be changed by this message.

The most credible next comparison is a strong reference-guided model versus a properly adapted translation-specialized model, followed by their combination if each contributes. Compare the same strong base with source context alone, manually selected verified references, and automatically retrieved references. The manual-reference condition diagnoses whether retrieval or use of evidence is failing. Select references from a frozen permitted pool excluding held-out answers and answer-equivalent copies. Keep exact translation-memory results separate.

Prioritize authentic alignment and philological evidence. The new TRAIN audit's 463 English pairs / 2,609 Farsi pairs and 6,144 reversed directional examples describe the adaptation dataset, not independent passage coverage or the foundation model's knowledge. Zero reference-checked senses and one-work English DEV are important evidence gaps. Acquire broader data and expert adjudication; do not restrict the project to the currently collected corpus.

New concrete leads:

- Oxford Invisible East has an inspected Middle Persian document with numbered source and English lines, editor/publication provenance and structured export options. Audit genuinely new pairs by shelfmark/edition against existing Berkeley material; record counts are not pair counts. Sample: https://www.invisible-east.org/corpus/1024/ .
- MPCD offers a strong representation and contextual-lexicon model. Its approximately 800k-token project description is not a verified public English-parallel release. Resolve obtainable layers and reuse scope before counting data. https://www.mpcorpus.org/methodology/ .
- BBAW MIRTEXT supplies substantial authentic Middle Persian/Parthian source text; filter language and textual variants. A separate 23-page Middle Persian–German reader supplies corresponding translations. Derived English/Farsi targets would remain labeled and reviewed. https://turfan.bbaw.de/bilder/texte/textempdeutsch.pdf .
- Exclude the Pahlavi Psalter's English KJV comparison from gold MP→English pairs: the edition explicitly says it is not a translation of its Middle Persian.
- Preserve exact supplied text, editorial reading and contextual meaning separately. Roles, negation, omitted arguments, ritual/legal terminology, quotation/commentary and legitimate alternate readings must enter evaluation. A plausible generated gloss cannot become verified evidence by repetition.

Keep full fine-tuning, larger ByT5/NLLB-style models, strong long-context models and specialist models such as Hy-MT2-30B-A3B, MiLMMT-46-12B, TranslateGemma-27B and Tower+-72B eligible. No Pahlavi success is established for these cards; check template/language support. MITRA provides a substantial historical-language adaptation precedent, not a ready Pahlavi solution. Use strong teachers for aligning existing scholarship; test synthetic targets, glosses, CPT and expert post-edit training as separate interventions.

Evaluate held-out works, natural unfamiliar passages and expert-validated new combinations, by direction. Blind qualified reviewers to systems, preserve disagreement and adjudicate serious errors. Calibrate any COMET/LLM judge against Pahlavi meaning before using it for selection or reward. Public held-out texts may already be in foundation pretraining; privately authored expert examples help test composition.

Continue a route when independent review shows repeatable new-material meaning gains. Redirect when verified references help but retrieval does not, or when even correct evidence leaves systematic role/negation failures. Pause new expensive scale-up when supervision, evaluation or required expert review is inadequate. Stop a particular recipe after a bounded matched comparison fails its declared useful-gain criterion; this does not establish failure of the entire project.

Resource summary: hosted strong-model reference trials need model access/token budget and expertise, not a local training GPU. Illustrative BF16 inference envelopes are one 48–80GB GPU for 7–12B, around one 80GB GPU with expansion capacity for 27–30B, and two 94GB or four 80GB GPUs for 72B. Full tuning needs substantially more; the full report gives cluster classes and accounting assumptions. MITRA's reported eight-A100/four-week pretraining stage is precedent, not a Pahlavi minimum. Measure actual throughput and present quality plus resource needs before the resource decision.

Full checkpoint, hardware table, primary citations and source limitations:

- [USER_HOME]\Documents\ChatGPT\Pahlavi language\output\research-2026-09-25\FOUNDATIONAL_RESEARCH_CHECKPOINT.md
- [USER_HOME]\Documents\ChatGPT\Pahlavi language\output\research-2026-09-25\EVIDENCE_INDEX.md
- [USER_HOME]\Documents\ChatGPT\Pahlavi language\output\research-2026-09-25\research-database.json

No model, corpus import, source permission, dataset, held-out TEST text or active training state was changed by this research. Your narrow Berkeley bibliography work was not duplicated.
