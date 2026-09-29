# Evaluation evidence and acceptance protocol

Checked 25 September 2026. This is a primary-source evidence audit, not a Pahlavi benchmark. No model or evaluation code was run. The companion JSON contains 12 source records, author affiliations, applicability and limitations.

## Findings that change the decision

A high automatic score, fluent English, agreement between models, or successful recovery of familiar passages cannot alone establish the requested general translator. The useful endpoint is preservation of source meaning on independent material, including difficult terminology, unfamiliar combinations and context.

The research synthesis already correctly separates known-passage retrieval from generalization and requires grouped splits. Add three safeguards: distinguish original-source translation from reverse reconstruction; validate the judge before optimizing its score; evaluate generated contextual translations rather than only candidate ranking.

## Verified source register

| ID | Primary evidence and consequence |
|---|---|
| EVAL-01 | [Experts, Errors, and Context: A Large-Scale Study of Human Evaluation for Machine Translation](https://aclanthology.org/2021.tacl-1.87.pdf). TACL 2021 study uses professional MQM raters, full document context, anonymized systems and randomized presentation. Expert-derived rankings differ from crowd rankings. Full paper inspected. |
| EVAL-02 | [Evaluating LLM-Based Translation of a Low-Resource Technical Language: The Medical and Philosophical Greek of Galen](https://arxiv.org/pdf/2602.24119v2). April 2026 preprint revision: 60 blinded translations of 20 paragraphs from two Galenic works; expert modified MQM and seven automatic metrics. Rare technical passages concentrate catastrophic errors. Full paper inspected. |
| EVAL-03 | [MITRA-zh-eval: Using a Buddhist Chinese Language Evaluation Dataset to Assess Machine Translation and Evaluation Metrics](https://aclanthology.org/2025.nlp4dh-1.12.pdf). 2025 paper compares metrics against 182 outputs rated by five subject specialists; average pairwise rater Spearman correlation 0.4. GEMBA performs best in their calibration. Human calibration excludes the judge model's outputs. |
| EVAL-04 | [COMET for Low-Resource Machine Translation Evaluation: A Case Study of English-Maltese and Spanish-Basque](https://aclanthology.org/2024.lrec-main.315.pdf). LREC-COLING2024 paper tests unsupported or weakly supported language settings against human judgments; metric fine-tuning can help, but sensitivity to training-score distributions and inconsistent gains remain. |
| EVAL-05 | [COMET official documentation: Languages Covered and Interpreting Scores](https://github.com/Unbabel/COMET). Official README explicitly warns that uncovered language pairs produce unreliable results. Its listed XLM-R language coverage includes Persian, but not Pahlavi/Middle Persian. Model-specific scoring and comparison interfaces are documented. |
| EVAL-06 | [On Compositional Generalization of Neural Machine Translation; CoGnition](https://aclanthology.org/2021.acl-long.368/). ACL2021 benchmark separately tests novel compounds and ordinary test sentences; standard translation scores can hide compound errors. Public repository README supplies dataset splits and evaluation entry point at github.com/yafuly/CoGnition. |
| EVAL-07 | [Measuring Compositional Generalization: A Comprehensive Method on Realistic Data](https://arxiv.org/pdf/1912.09713). ICLR2020 DBCA constructs partitions with similar distributions of atomic elements but different compound distributions. Demonstrated on CFQ semantic parsing/question answering. |
| EVAL-08 | [Evaluation and Large-scale Training for Contextual Machine Translation](https://aclanthology.org/2024.wmt-1.112.pdf). WMT2024 compares contextual training/inference and tests both contrastive scoring and actual generation. Contrastive preference is only a proxy for generating the contextually correct form; context-dense evaluation reveals otherwise small gains. |
| EVAL-09 | [When Flores Bloomz Wrong: Cross-Direction Contamination in Machine Translation Evaluation](https://aclanthology.org/2026.eacl-short.26.pdf). EACL2026 study demonstrates target-side memorization can inflate other translation directions; source paraphrasing and entity changes do not reliably remove memorized-reference effects. |
| EVAL-10 | [When LLMs Struggle: Reference-less Translation Evaluation for Low-resource Languages](https://aclanthology.org/2025.loreslm-1.33.pdf). LoResLM2025 tests prompting and instruction-tuning for quality estimation; prompt-based LLM approaches are outperformed by fine-tuned encoder-based QE, with transliteration and named-entity failures. |
| EVAL-11 | [Statistical Power and Translationese in Machine Translation Evaluation](https://aclanthology.org/2020.emnlp-main.6.pdf). EMNLP2020 shows source-original versus reverse-created test material can change conclusions and cautions that low-powered nonsignificant comparisons do not establish human parity. |
| EVAL-12 | [Statistical Significance Tests for Machine Translation Evaluation](https://aclanthology.org/W04-3250.pdf). EMNLP2004 primary paper describes paired bootstrap comparisons and tests their behavior for BLEU. Provides a foundational uncertainty method for comparing systems on shared examples. |

All are reported results or documentation inspected in this audit, not independently reproduced results. The CoGnition repository README was accessible, but its evaluation script fetch failed; therefore this audit does not certify its implementation. No hardware constraint was used to exclude any model or method.

## Concrete evaluation design

These are proposed project requirements, not performance thresholds established by the papers.

1. **Define the deployment population.** Specify each translation direction, source representation and intended genres. Score authentic Pahlavi-to-English/Farsi separately from English/Farsi-to-Pahlavi. A reversed scholarly translation is a reconstruction task; add newly composed, expert-approved modern-language prompts for the latter direction.
2. **Freeze families before splitting.** Keep work, source passage, edition, translation lineage, alternate language translations, reverse pairs and synthetic derivatives together. Record rights/provenance, normalizations and source variants. Keep final-test references out of training, retrieval, prompt demonstrations and development review.
3. **Use distinct test strata.** Report familiar passage retrieval, new passages in familiar works, entirely held-out works/genres, and expert-authored unfamiliar combinations. Tag rare terminology, negation, argument roles, possession, quantities, tense/aspect where linguistically appropriate, and ambiguous passages. Do not make mechanically edited ungrammatical strings the only generalization test.
4. **Make context measurable.** Include matched passages whose correct interpretation depends on surrounding text. Compare source-only, correct source context, and controlled irrelevant/context-changing conditions. Inspect actual generated meaning. Gold neighboring target translations must be identified as an assisted condition; ordinary deployment uses source context or generated target context.
5. **Make human assessment the primary endpoint.** At least two qualified reviewers should independently annotate blinded, randomized candidate translations against source and permitted context. Calibrate on a separate set; record error spans, seriousness, acceptable alternatives and reasons. Adjudicate disagreements after preserving original ratings. A philologist and target-language editor have complementary roles.
6. **Audit automated judges.** Test ranking and error detection on human-approved translations, valid paraphrases and controlled corruptions: negation flip, omitted condition, wrong entity, reversed agent/patient, numerical change and fluent unsupported addition. Use distinct calibration and confirmation samples. Compare reference-based and reference-free conditions. Neither modern Persian coverage nor English semantic similarity establishes understanding of Pahlavi.
7. **Estimate uncertainty honestly.** Use paired candidate comparisons on identical items and report serious-error incidence, annotated adequacy and error categories separately by stratum/direction. Resample independent work or passage-family clusters where feasible; report the number of independent works. A small screening set can eliminate obvious failures but cannot demonstrate general reliability or human parity.
8. **Preserve reproducibility.** Archive model/checkpoint revision, tokenization and input conventions, complete prompt/reference pack, retrieval identifiers, generation settings, exact outputs, evaluator version and rubric. Record resource usage after the quality comparison; it is an outcome to report, not an eligibility filter.

## Proceed, change, or pause

**Proceed to bounded comparison:** keep a training path eligible when losses/outputs are technically healthy and it has a distinct, testable hypothesis. Compare a strong reference-guided model, strong translation-specialized adaptation, their justified combination, existing baseline and translation memory on the same locked development families. Large models and full fine-tuning remain eligible.

**Change the method or data:** repeated negation, argument-role or terminology errors require diagnosing supervision, alignment, representation, context and lexicon coverage. A training-loss reduction without independent semantic improvement does not justify merely adding epochs. Compare corrected data or a different adaptation method under a controlled rerun.

**Pause further scale-up:** stop committing additional expensive runs when the evaluation partition is contaminated, the metric is unvalidated for Pahlavi, meaningful supervision is misaligned, or repeated matched trials provide no independent meaning improvement. Preserve completed checkpoints and logs. This is a gate on new expenditure, not authority to interrupt another task's active run.

**Promote a candidate:** predeclare the acceptable serious-error ceiling and meaningful improvement for the intended use, then require the paired confidence interval to support that gain without a material deterioration in critical strata. There is no scientifically justified universal BLEU, COMET or sample-count cutoff. A qualified human should validate successful new combinations, unresolved ambiguity and rare terms before claiming general translation.

## Citation cautions and unresolved inspection

- The Galen paper's dramatic rarity correlation is based on ten pharmacological passages and is sensitive to two extreme observations. It motivates targeted tests, not a universal rarity law.
- MITRA-zh supports the possibility of a useful LLM judge after domain-specific calibration; Surrey's low-resource QE study and COMET coverage evidence show why that success cannot be presumed for another language. These are different settings, not contradictory universal claims.
- DBCA demonstrates a split-design principle in semantic parsing; CoGnition supplies the closer translation precedent. Neither is an off-the-shelf Pahlavi evaluator.
- The root reported suspicious reference-count signatures in the Coptic Syntax as a Rosetta Stone appendix. This audit did not verify the corresponding scoring code. **Unresolved: do not call it a confirmed metric bug or use it to dismiss the method.**
- A public-code fetch failed in the sandbox; its escalated read was interrupted at host approval. It produced no source inspection result, installed nothing and executed no downloaded code.
