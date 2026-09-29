# Training regimes under limited Pahlavi supervision

27 September 2026; `/root/model_choice_review`. Bounded primary-source review prompted by the user's distinction between supervised, unsupervised and combined learning. Methods/results/limitations below were inspected in full-text HTML or extracted PDF text, rather than inferred from abstracts. No experiments, datasets, model downloads or cloud actions were performed. The scientific research methods skill informed the separation of regime, resource assumptions and claims.

**Recommendation:** retain supervised translation as the semantic anchor. Before another weight update, establish whether we possess additional clean monolingual coverage or trustworthy lexical/morphological supervision. If the latter exists, a small controlled task-mixed SFT experiment is the more direct candidate for known-word/composition errors. CPT followed by SFT remains a conditional alternative, not a rejected method. Synthetic self-training and judge-driven preference/RL training are not justified by the current evidence pipeline.

## What is actually being compared

- **SFT** learns a specified target from an input, here attested Pahlavi-to-Persian translation. Current LoRA training is an implementation of this regime.
- **LoRA/QLoRA** specify parameter updating and numerical representation. They can be used with several learning objectives; they are not alternatives to supervised or self-supervised learning.
- **Continued pretraining (CPT)** predicts or reconstructs authentic raw text. It can learn recurring forms and contexts, but does not itself supply a Persian meaning for an unanchored word. Lower raw-text loss is not proof of better translation.
- **Task-mixed supervision** can teach translation, attested word senses, morphology and composition together. Those auxiliary targets require independent justification; copying a whole passage translation into guessed word labels is not annotation.
- **Backtranslation/self-training** creates synthetic parallel supervision. For our Pahlavi-to-Persian direction, backtranslation requires credible Persian-to-Pahlavi generation; labeling untranslated Pahlavi with predicted Persian is forward pseudo-labeling. These have different failure paths.
- **DPO/CPO and online RL** optimize preferences or rewards. Their objective is only as reliable as its preference labels/reward for this task. CPO evidence is not direct evidence for an online RL pipeline.
- **Retrieved examples** condition inference without changing weights. The earlier model-by-assistance comparison addresses deployable model/inference choices, not which training regime is best. It must not be presented as answering this new question.

## Five primary studies that change our priorities

### 1. Historical-language CPT works at substantial scale, with bilingual anchors

[MITRA, January 2026, §§4–5/9](https://arxiv.org/html/2601.06400v1), full HTML inspected. Gemma 2 9B receives two epochs over 4.4 billion tokens: 20% parallel and 80% monolingual/domain material, then 10,000 multidirectional and 30,979 document translation instructions. Reported CPT cost is eight A100s for four weeks. Tests contain 2,662 Chinese, 5,552 Sanskrit, 4,053 Tibetan and 1,900 Pāli pairs, removed from adaptation data; quality uses Gemini-based GEMBA. The final system beats general baselines, but the translation comparison does not isolate CPT from subsequent supervision. Mined alignments include 11% wrong pairs in a 100-pair manual sample; some instruction-data choices caused repetitive hallucinations. Its test translations are not publicly distributable.

**Inference:** useful historical-language precedent for mixed CPT→SFT, not evidence that a few thousand untranslated Pahlavi passages suffice, nor that untranslated-only learning identifies meanings. This is not a budget quotation or a minimum-compute theorem for our project.

### 2. Combining objectives helps selectively; “all methods together” can lose

[Pang et al., Rethinking the Exploitation of Monolingual Data, 2024, §§2–4/Table 3](https://aclanthology.org/2024.cl-1.2.pdf), PDF text inspected. Controlled encoder–decoder experiments use five million monolingual sentences per language, with 5k–500k English–German pairs and additional language tests. Development/test use separate WMT years; the main outcome is BLEU, not expert semantic judging. At 5k bitext, baseline/BT/pretraining score 1.04/1.39/12.41. After pretraining, adding causal-language-model supervision gives 14.59, BT 13.68, and BT+CLM+denoising 13.55. Larger bitext changes the preferred recipe. The authors link weak extreme-low-resource BT to unreliable reverse translations; simultaneous multitask learning also loses to staged pretraining in smaller settings.

**Inference:** a real reason to keep CPT→SFT and controlled mixtures eligible, but their enormous monolingual resource and encoder–decoder objectives differ from our decoder-only model. Do not paste masked/denoising losses into the current trainer or assume an arbitrary mixture ratio is validated.

### 3. Lexical/morphological supervision can transfer, but labels are the resource

[GlossLM, EMNLP 2024, §§5–7/Table 2](https://aclanthology.org/2024.emnlp-main.683.pdf), PDF text inspected. ByT5-base (582M) learns gloss generation from 250,585 unsegmented multilingual training examples in the reported partition, then target-language gloss data. Four held-out languages have 74/705/791/2,100 training examples and 37/87/99/263 test examples. Inputs normally include a translation; targets are annotated interlinear glosses. Metrics are morpheme/word accuracy and chrF++, not whole-translation expert acceptance. Fine-tuning beats the prior best on five of seven languages, but loses on the smallest Gitksan and Lezgi settings, where a segmentation-aware model performs better. The authors observe inconsistent lexical labels and overreliance on supplied translations.

**Inference:** directly motivates reliable word/morphology tasks, not guessed glosses. Its “pretraining” is supervised cross-language gloss learning. A free-translation-assisted gloss result cannot validate a Pahlavi translator that receives no known translation. Native-script transcription remains an additional task.

### 4. Preference optimization has positive evidence, including a limited human test

[Xu et al., CPO/ALMA-R, ICML 2024, §§3–5](https://arxiv.org/html/2401.08417v4), full HTML inspected after publisher PDF retrieval failed. ALMA 7B/13B is already adapted before roughly 22k preference examples across ten directions update about 0.1% of parameters. Preferences combine model/GPT-4/human-reference candidates ranked by COMET-family estimators, plus some human preference data. WMT 2021–2023 provides separate tests. Four bilingual judges assess 400 Chinese→English cases, each assigned 100: mean rating rises from 4.86 to 5.16/6. This validates a narrow benefit beyond automatic scores, not Pahlavi reward calibration. Plain DPO performs below the baseline on several reported aggregate metrics; CPO's supervised anchoring term matters.

**Inference:** preference learning is a legitimate later option. It requires credible contrasting candidates and rankings, not merely more sampled answers or a fluent general LLM's approval. These experiments mainly concern established modern translation directions.

### 5. Preference gains can track the chosen metric while other measures worsen

[Is Preference Alignment Always the Best Option?, September 2024, §§3–6](https://arxiv.org/html/2409.20059v1), full HTML inspected. This independent ALMA-13B study uses over 20k FLORES-based pairs across ten directions, with 17,471 WMT 2022 test pairs and further WMT 2023 evaluation. It compares CPO with SFT on the same preferred translations. Candidate and ranking choices substantially change conclusions: CPO can improve its neural alignment metric while reducing lexical scores; some fixed-preference configurations fall below the unaligned model across metrics. Same-system candidates reduce these adverse effects, but the experiment generates 50 candidates per source and still requires ranking. Outcomes are automatic neural/lexical metrics, not a new human semantic study.

**Inference:** reward optimization is an extra uncertainty source when the reward lacks Pahlavi calibration. A judge score improving during training is not independent validation, and a lexical-score decline alone does not prove semantic decline either.

The earlier [methods report](RESEARCH-METHODS-UPDATE.md) already documents mixed Kalamang backtranslation results. It remains supporting context; no synthetic-data success is established for this corpus.

## Regime priorities for this project

These are project-specific judgments from the evidence above, not claims that one regime always wins.

| Regime | Priority and prerequisite | Smallest credible diagnostic |
|---|---|---|
| Existing translation SFT with LoRA | Keep as a fixed baseline; another identical run lacks a diagnosed reason. More epochs do not add missing semantic evidence. | Use fixed DEV to distinguish isolated-word failure, role/composition failure and unsupported invention; keep uncertainty in the reference visible. |
| SFT plus lexical/morphological/composition tasks | First candidate **if** cited TRAIN-only sense/annotation records can be verified. Parallel passages alone do not certify every alignment. | First audit a small fixed annotation packet without training. Then one predeclared SFT-only versus task-mixed contrast from the same starting checkpoint; preserve whole-passage supervision and equalize the declared update/token budget where possible. |
| Authentic monolingual CPT→SFT | Conditional on independently useful, clean and split-safe raw text. A few repeatedly seen works are not automatically adequate coverage. | Count unique tokens/works, assess OCR/transcription quality and overlaps first. If admitted, one short CPT branch followed by the unchanged SFT recipe versus matched no-CPT SFT; measure translation and retention, not only perplexity. |
| Simultaneous raw-text and translation mixture | Later than a simpler staged contrast; fixed loss weighting changes the amount of translation supervision. | Declare sampling/loss weights and actual tokens per objective before training; do not grid-search ratios on the small DEV panel. |
| Backtranslation or forward self-training | Not admitted now; reverse-direction competence/teacher reliability and independent checking are unproven. | Inspect a fixed small synthetic packet against existing attested source meanings before accepting any pseudo-labels. Never promote a model's own guess to gold because it agrees with itself or round-trips. |
| DPO/CPO or LLM-judge RL | Not admitted now; no validated Pahlavi preference/reward set. Extra candidates also consume budget. | First compare blinded preference rankings against qualified philological adjudication, including critical meaning errors. Without that agreement evidence, stop before preference training. |

The 2,237 qualified rows are still provisional AI-reviewed parallel supervision, not expert-certified word gold. Root's offline inventory must establish actual untranslated data availability; this review does not assume an amount or authorize collection. Modern Persian fluency is not the missing target by default, so a target-language modeling improvement in another study does not justify spending primarily on more Persian raw text here.

## Minimal next decision, without a training sweep

1. **Finish the resource inventory before choosing the regime.** Distinguish genuinely additional Pahlavi source text, repetitions of our parallel sources, commentary about Pahlavi, native script and scholarly transcription. Require work/edition provenance and exclude all DEV, TEST and PAL-REF texts and witnesses from weight-training material, even when their translations are absent. Unlabeled exposure to a test source still compromises the intended generalization test.
2. **Verify whether lexical supervision can exist honestly.** A fixed small packet of TRAIN witnesses should carry exact attested source spans, sense alternatives, grammatical evidence and qualified approval; uncertain assignments remain unlabelled. Reuse scholarship and existing corrections. Do not fabricate a full morphological inventory or generate hundreds of supposedly certain meanings to make a multitask dataset possible.
3. **Choose one training contrast only if its prerequisite passes.** Prefer task-mixed SFT if reliable task labels are available and errors concern known forms/roles. Prefer a bounded CPT→SFT contrast if substantial additional authentic contexts exist and the evidence points to source-language modeling gaps. Freeze data, total updates, starting model, evaluation and stop rule first. A model-family change at the same time would confound the regime comparison. The existing model-by-assistance proposal is a separate question, not an obligatory extra stage.
4. **Keep claims limited.** Reuse the fixed DEV translation comparison, reporting its 15 whole cases and nine constrained cases separately. New lexical/composition checks require independent attested labels and a declared development role; they must not become another secretly tuned final benchmark. The existing conservative promotion guards are operational, not powered significance tests. No gain, increased critical errors or judge disagreement means no automatic extension, extra epochs or new synthetic round. PAL-REF remains outside tuning.

For isolated attested words, the immediate bottleneck is verified sense/reading evidence. For new combinations, supervision must establish roles, morphology, negation and compositional meaning rather than merely repeat word lists. For genuinely unknown inscriptions, distributions can suggest hypotheses but cannot certify a decipherment without external anchors and expert checks. None of the five studies removes that distinction.

Changing the learning objective need not change the eventual model's parameter count, but local 8 GB VRAM/~64 GB RAM fit, quantized quality and 10–20-minute timing remain runtime questions. A100 80 GB compatibility of the current SFT path does not prove that a new objective is implemented or affordable. The reported spend is approximately $11.75 against the $25 cumulative authorization; the remaining nominal amount is not a quote for any proposed regime. Price preparation, both comparison arms if required, evaluation and shutdown, preserving the existing reserve, before any admission. No new training is authorized by this report.
