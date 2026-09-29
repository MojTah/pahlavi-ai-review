# Focused methods update: evidence that could change the next experiment

27 September 2026; `/root/model_choice_review`. Fresh inspection of five primary full texts, emphasizing methods, results and limitations. No models, code, cloud resources or datasets were changed. This supplements the [post-comparison review](../retrain-qualified-20260927/POST-COMPARISON-STRATEGY-REVIEW.md); it does not admit a job. No study below establishes Pahlavi effectiveness or current model superiority.

## 1. MTOB ablation: examples versus explanations versus fine-tuning

**Inspected:** [Aycock et al., full HTML, v2, 24 April 2025](https://arxiv.org/html/2409.19151v2), §§3–5, Tables2–4 and limitations.

Kalamang resources include1,239 book examples,400 additional parallel sentences and500 development examples. Evaluation combines100 test sentences; Nepali/Guarani use1,012 FLORES cases. Main comparisons use Gemini1.5Flash, Llama3.1-8B and fine-tuned NLLB1.3B; scoring is chrF++, without proficient-speaker evaluation. Book examples largely account for translation gains; grammatical explanations add little. On book-only training, NLLB scores34.2/28.6 versus Gemini26.6/33.1 for English→Kalamang/reverse. Adding400 authentic pairs raises NLLB to38.7/36.9; backtranslation instead gives32.0/31.6. Small-model fine-tuning is therefore credible, but direction and data matter. Retrieved examples also help some fine-tuned-model conditions. The paper trims outputs after their first newline, unlike our preserved-first-attempt evaluation.

**Mismatch/inference:** this supports the proposed example test and keeps specialist fine-tuning a later alternative; it does not show that larger models or grammar prose solve our task. Its scores cannot replace semantic review.

## 2. DiPMT++: relevant examples help, but richer context can hurt

**Inspected:** [Teaching Large Language Models an Unseen Language on the Fly, full PDF](https://aclanthology.org/2024.findings-acl.519.pdf), §§3–7, Tables1,4–6.

ZhuangBench supplies4,944 parallel pairs,16,031 dictionary headwords and200 held-out cases:75 easy,60 medium,65 hard. Three retrieved examples accompany lexical expansion. Qwen72B improves from DiPMT's5.1/16.3 to16.4/27.3 BLEU in Chinese→Zhuang/reverse; chrF is also reported. With Qwen14B, BM25 beats random/POS retrieval. More context is not consistently better:5,000 monolingual tokens induce fabricated words; Qwen14B fails with an added1,000-token block. A six-participant assistance study uses non-Zhuang-speaking NLP students and60 easy items; outputs are scored by BLEU/chrF, not certified by proficient speakers. Assistance improves scores but does not save time in both directions.

**Mismatch/inference:** their dictionary and Chinese-capable backbone are substantial additional resources. Our few whole examples do not replicate DiPMT++. Keep evidence concise, contextual and bounded; do not add unverified dictionary induction, synonym expansion or long text automatically.

## 3. GrammaMT: reliable glosses are different from self-generated glosses

**Inspected:** [GrammaMT, ACL2025, full PDF](https://aclanthology.org/2025.acl-long.1447.pdf), §§4–6, Tables1–3, Figure4 and AppendixA. This is gloss-based inference, distinct from the **GrammarMT** synthetic-augmentation project discussed in older notes.

Llama3-70B receives21 TRAIN examples; development ablations select that count. SIGMORPHON test sizes are37/87/99/445 for Gitksan/Lezgi/Natugu/Tsez. Average BLEU is3.94 for ordinary examples,3.41 with example glosses,4.25 for self-generated glosses and15.97 with specialized GlossLM predictions. Thus the large gain is not demonstrated by merely adding21 annotated examples. GlossLM draws on a250,000-sentence/1,800-language resource; its target-language specialized models are additional supervision. Tsez gloss accuracy is20.61% for Llama versus88.53% for GlossLM. Evaluation uses BLEU/chrF++/xCOMET, without a dedicated speaker-rating study. They suppress model-gloss results where its training exposure overlaps evaluation.

**Mismatch/inference:** Pahlavi lacks a validated equivalent gloss model/annotation resource. Gold-gloss oracle gains do not license feeding DEV answers or treating guessed lexical labels as truth. Reliable gloss preparation is promising, not ready-made infrastructure.

## 4. Counterevidence: retrieval can degrade a stronger model

**Inspected:** [Shortcomings of LLMs for Low-Resource Translation: Retrieval and Understanding Are Both the Problem, WMT2024, full PDF](https://aclanthology.org/2024.wmt-1.125.pdf), §§4–6, Tables1–4, limitations.

The test has50 Southern Quechua→Spanish pairs, checked by a native bilingual instructor. Three LCS-selected corpus examples come from combined AmericasNLP/IWSLT resources; §4.2.3 does not give their combined pool size. Four pretrained models are tested without fine-tuning. Corpus context changes BLEURT from0.19→0.27 for GPT3.5 but0.66→0.59 for GPT4o; morphology helps weaker systems, while manually improving retrieval still does not uniformly beat strong-model zero-shot. BLEU and author MQM-style judgments accompany BLEURT. Human evaluation has acknowledged non-native/partly machine-translated-reference limitations; the language-speaking author checks annotations.

**Mismatch/inference:** model knowledge and morphological resources differ from Pahlavi. Nonetheless this directly supports retaining a plain control, rejecting automatic assistance promotion and separating retrieval relevance from the model's ability to use it. A negative58-example-package result would not prove all retrieval methods futile.

## 5. Data quality: error type matters more than a “clean” label

**Inspected:** [Khayrallah and Koehn2018, full PDF](https://aclanthology.org/W18-2709.pdf), §§5–6, Tables1/3. PDF text extraction succeeded; the requested table screenshot failed, so numbers below come from the extracted table/text.

This is a mechanistic counterexample, **not a small-data LLM study**: German→English shallow-RNN NMT and phrase-based SMT use approximately83million clean tokens per language; newstest2015/2016 support tuning/development and2017 is test. Automatic BLEU is the outcome, without semantic human judging. Adding raw noisy web data changes NMT27.2→17.3 BLEU while SMT24.0→25.2. Five-percent untranslated source-copy target noise causes NMT17.6, whereas five-percent misalignment gives26.5. Some short-segment additions help slightly rather than universally damaging quality.

**Mismatch/inference:** those noise rates and architecture do not predict Gemma's response to removing247 rows. The relevant lesson is to classify defects and preserve valid short/qualified material, not equate every difference, fragment or repetition with corruption or expect filtering to improve every work.

## Initial recommendation before the user's cross-model steering

**Retain the48-output qualified-model plain/assisted comparison as a bounded diagnostic, with lower confidence in an automatic win.** The positive and negative studies make the control more valuable, not dispensable. None establishes that Gemma4-31B is the right or wrong backbone for Pahlavi. Switching now would conflate a new model/interface with a new evidence method; more epochs likewise lack a diagnosed learning need.

Refine preparation in three ways without adding inference arms:

1. Audit the58 retained query–witness pairings for *contextual sense and construction relevance*, separately from exact identity and token overlap. Record unsupported/ambiguous cases without using DEV reference answers to hand-pick replacement examples. Existing qualifications remain visible. This measures limitations of the offered evidence; it must not pretend to establish word-level gold.
2. Preserve the same model, literal system instruction, decoding and fixed15-whole/nine-constrained DEV assessment. The contrast estimates the entire example/caution package. Keep paired regressions, critical roles/negation errors and unsupported certainty alongside any lexical improvement. Do not use chrF/BLEU gains as a substitute for the existing semantic decision.
3. Interpret failure narrowly: insufficient relevant evidence, poor use of reliable evidence, and reference ambiguity are different explanations. A later gloss or specialist-model study would require its own evidence and bounded proposal. Do not immediately respond with more retrieved material, synthetic words, a larger model or another training run.

These findings refine a testable hypothesis, not a promise of success. Native-script reading and unknown-lexicon discovery remain separate, unvalidated goals. No automatic escalation or new budget allocation follows from this review.

## Revised prospective recommendation after the user's cross-model steering

The user explicitly asks us to avoid getting trapped in one model's limitations. That changes the decision being studied. **Replace the prospective 48-output proposal with one preregistered cross-family challenge, subject to technical and budget admission:** the current qualified Gemma adapter and one different-family pretrained instruction model, each plain and with the identical frozen 58-example package, on all unchanged 24 DEV inputs. This produces 96 first attempts, preferably in two bounded model jobs. The earlier recommendation above remains history; it is not the current launch recommendation.

This measures four **deployable conditions**, including whether the usefulness of evidence depends on the model. It does not isolate architecture, model size or the effect of fine-tuning: one contender has received Pahlavi supervision and the other has not. That unequal adaptation is acceptable for choosing the next practical system, provided it is explicit. Neither the papers nor our existing results establish that this particular challenger will win.

### Freeze before any generation

- Select exactly one challenger from the independent primary-document and feasibility review; freeze its model revision and execution settings before seeing DEV outputs. Require a credible eventual 8 GB GPU plus approximately 64 GB RAM route, without claiming runtime fit or preserved quality until tested. No automatic fallback model, adaptation sweep or selection using PAL-REF failures.
- Keep all 24 already selected cases: 15 whole-passage and nine constrained assessments, with six cases from each of four works. A smaller subset selected after observing earlier outcomes would weaken this test. If the full comparison cannot pass the budget gate, revise the scope before launch; do not quietly substitute favorable cases or silently omit expensive failures.
- Use identical literal instructions, source texts, example order, example content and qualification notices across models. Use each model's official template and tokenizer; cross-model token-ID equality is neither expected nor required. Preserve the entire input without truncation, matched output/time ceilings and fresh contexts. The earlier cross-family greedy recommendation is superseded by PLAN.md: Gemma remains greedy/nonthinking, while Qwen follows its declared vendor nonthinking sampling policy. This tests operational systems with disclosed decoding differences, not a pure architecture effect.
- Freeze the 58 admitted pairings without replacements or reranking. A source-only contextual-relevance audit can describe their limitations, but cannot edit them using DEV reference answers. Keep no-support and uncertain evidence visible. Preserve and score every first attempt, including timeout or format failures; permit no semantic retries.
- Obtain blind independent reviews of all four conditions using the existing assessment contract. Preserve the whole/constrained distinction, paired changes, results by work, critical errors and unsupported certainty. Two agents from the same model family remain provisional AI judges, not independent philological certification.

### Predeclared decision and stopping rules

As a conservative **operational decision threshold**, not a powered significance test, promote a condition over the current Gemma plain control only if both reviewers independently find at least two net additional accepted whole passages out of 15, no increase in critical cases among those 15, no whole passage changing from accepted to critical, and improvement in at least two works. Separately, require no worsening of supported-span critical errors and no new unsupported certainty among the nine constrained cases, judged under the existing assessment contract. Keep these denominators separate. Report every lost acceptance, paired regression and reviewer disagreement even when these guards pass. The lead should freeze this threshold or an explicitly justified alternative before launch, rather than adjusting it to the observed scores.

Apply the same safety guards to each model's assisted-versus-plain comparison. If assistance helps only one family, retain that interaction instead of declaring a universal retrieval improvement. A challenger that clears the promotion rule justifies pursuing that system without first fine-tuning it; it does not establish architectural superiority. If several conditions qualify but their comparisons conflict, report the unresolved tradeoff rather than force a winner.

If neither family offers an admissible improvement, stop this model-search round and automatic retraining. Examine the already available source-only evidence audit together with DEV error categories to distinguish absent lexical evidence, irrelevant examples and failure to use relevant examples. The next proposal should then address the diagnosed bottleneck—for example, expert-checked lexical senses and constructions—rather than add epochs, generated dictionary entries or another model by default. Failure of this one challenger does not prove all model alternatives exhausted.

PAL-REF stays unchanged and outside selection, prompt changes, retrieval ranking and threshold setting. A later final evaluation would require an explicit frozen choice; repeated use of its existing cases would not constitute a newly independent confirmation. Do not claim that this DEV translation experiment validates native-script reading or discovery of genuinely unknown meanings.

The extra model entails another load and a separate tokenizer/interface check. The execution owner must price setup, inference and shutdown under the remaining authorized $25 cumulative cap and existing $0.75 reserve before admission. This note supplies no new price quote, approval or cloud command. A failed technical or budget gate stops the proposal for explicit reassessment; it does not authorize substituting another model or spending on retries.
