# Existing AI approaches for a general Pahlavi translator

Research checked 25 September 2026. This is a research handoff, not a completed model benchmark or a claim that translation is solved.

User requirement: translate supplied Pahlavi/Middle Persian text into English and Farsi and vice versa, including previously unseen passages. OCR is excluded. Keep the offline/no-paid-API objective. The user explicitly authorized agents and relevant skills in this research task.

The implementation owner is the Codex task **Design Pahlavi translation model** (01a0c368-c6e0-78b2-96b0-fdfa72388eb3). Its live implementation root is `[USER_HOME]\Documents\Codex Projects\01-Software\Pahlavi Translator`. This research task has not changed its code, data, environment, processes, or active model.

## What is new relative to the existing project review

The existing strategy already discusses PahGen, ParsiPy, ByT5, Qwen, LingoLLM, NLLB, the Akkadian NMT paper, Deep Past Challenge, and a possible Farsi intermediate translation. They should not be presented as new discoveries. A search of the current translator's docs and experiment configurations found no Hy-MT2, TranslateGemma, MADLAD, BYOL, Apollo, Aeneas, or Ithaca references.

The current project records explicitly say that no translation-quality gain is confirmed. The global review documents serious meaning errors despite better surface scores, and poorer results from the earlier five-call procedure. ByT5 is an active, separately motivated experiment; preserve its frozen execution and complete its meaning comparison. Read current run records before inferring its current progress from dated notes.

## New translation-specialist candidate: Tencent Hy-MT2

[Hy-MT2-1.8B](https://huggingface.co/tencent/Hy-MT2-1.8B) is a downloadable translation specialist. Its official language list includes English and modern Persian, but does not list Pahlavi. The family also offers 7B and 30B-A3B variants. The 1.8B card is Apache-2.0 and publishes terminology and contextual translation instructions. Its performance claims are on other languages, not Pahlavi.

The official [training guide](https://huggingface.co/tencent/Hy-MT2-1.8B/blob/main/train/README.md) supplies full fine-tuning and LoRA recipes, including `hy_dense_1_8b_lora_sft.yaml`. Thus the reusable asset includes a training recipe, not just a paper. Check the source before executing it: the published path uses remote-code loading and Linux/DeepSpeed or LLaMA-Factory tooling. The [model card](https://huggingface.co/tencent/Hy-MT2-1.8B) requests Transformers >=5.6.0; the active experiment records use 4.57.6. Do not upgrade the live training environment.

**Recommendation, not a measured result:** prioritize a bounded Hy-MT2-1.8B adaptation comparison after the current experiment. It tests whether starting with a translation-specialized model transfers better than a general chat model or a denoising model. Small parameter count is not proof that training fits; measure it. Use the published training and inference format consistently and ordinary reviewed parallel pairs first. Do not begin with extremely low-bit weights when establishing the quality baseline.

Hy-MT1.5 surfaced first during research; the official repository points to Hy-MT2 as its successor, so use the current family for the primary feasibility check.

## Secondary existing translation models

- [Google TranslateGemma](https://huggingface.co/google/translategemma-4b-it): an existing 4B/12B/27B translation family with a specialized translation template. The card specifies 2K input context, restricted language-code handling, and Gemma access terms. Pahlavi support was not established; a custom template is not evidence of learned language competence. Consider it a secondary adaptation candidate, not a ready Pahlavi translator.
- [Google MADLAD-400-3B-MT](https://huggingface.co/google/madlad400-3b-mt): a translation-trained T5-family model with an Apache-2.0 card. This is a distinct hypothesis from fine-tuning a general ByT5 checkpoint. Pahlavi tokenizer coverage, language conditioning, input lengths, and task performance must be checked. Its much larger size than ByT5-small makes it a secondary resource-gated candidate. The Hugging Face conversion card credits its converter; consult the linked original research for paper claims.

## What ancient-text AI establishes

**MITRA is an actual ancient-language translation precedent.** It covers Sanskrit, Pali, Tibetan and Buddhist Chinese, with domain pretraining, translation instruction tuning and semantic retrieval. A [Gemma translation checkpoint](https://huggingface.co/buddhist-nlp/gemma-2-mitra-it) and [corpus/evaluation repository](https://github.com/dharmamitra/mitra-parallel) are public. The [January 2026 paper](https://arxiv.org/html/2601.06400v1) used 4.4 billion tokens and four weeks on eight A100s; its into-English evaluation does not establish reverse-direction or Pahlavi performance. Reuse its alignment/provenance and domain-training lessons. The repository advertises newer models; do not attribute January Gemma results to a newer release without checking it.

[Aeneas and Ithaca](https://deepmind.google/science/workflows/conversing-with-antiquity/) restore, date and locate Greek/Latin inscriptions. Aeneas also retrieves contextual parallels. Those are useful design precedents for evidence retrieval and visible alternatives, but they do not supply a trained Pahlavi translation model.

[Apollo, announced by the Austrian Academy on 23 September 2026](https://www.oeaw.ac.at/en/news/ai-speaks-ancient-greek-apollo-restores-2000-year-old-texts), restores missing Ancient Greek text. The announcement describes approximately 600 million training words and a freely accessible application. This is a newly released ancient-language AI, but its reported restoration results must not be described as translation accuracy or evidence that our small corpus can reproduce its training.

## New reusable methods identified by the research agents

**GrammaMT: explicit grammar alongside word meanings.** [ACL 2025 paper](https://aclanthology.org/2025.acl-long.1447.pdf). It supplies interlinear lexical and morphological glosses to an existing translation LLM. External language-specific glossing was substantially more effective than asking the same model to invent its own analysis in the unseen-language tests. The published prompts are reusable; its glossing models are not validated Pahlavi analyzers. A useful inference for this project is one matched comparison of independently checked word senses versus the same senses plus checked morphology. This tests whether grammatical interpretation, not merely missing vocabulary, explains errors. Reference translations must not be used to manufacture input glosses. Current draft dictionary senses do not automatically meet that requirement.

**Lexical-confusion repair.** Google's [Alligators All Around, NAACL 2025](https://aclanthology.org/2025.naacl-short.18.pdf) studies semantically related word substitutions. Its best setup combines an MT draft with a bilingual lexicon for post-editing; exact-match word retrieval can miss inflected forms. The tested post-editor is Gemini 1.5 Pro with an 850M MT model, so success with a small offline replacement remains unproved. The useful lesson is to audit inflection-aware dictionary coverage and compare actual corrected meanings, rather than repeat an unsupported self-review chain. Require independent evidence for every correction and preserve the original draft.

**BYOL: reuse the decision process, not its entire pipeline.** The [Microsoft framework](https://github.com/microsoft/byol) separates model selection, corpus cleaning, adaptation and evaluation. The [paper's Inuktitut experiment, section 3.2](https://arxiv.org/html/2601.10804v1), used 1.3 million parallel pairs plus 29,632 internal pairs, with substantial back-translation data. Its language-model adaptation path also used hundreds of millions of tokens. These resources are unlike this project's few thousand passage pairs. Public local backends exist, but parts of the research use paid GPT/Azure processing. Released Chichewa/Maori models are not Pahlavi translators. Do not bootstrap more training labels from the translator's presently unreliable guesses.

These investigations were read-only and independently scoped. The lead checked the primary GrammaMT, lexical-confusion, MITRA, and BYOL publication/repository pages before integration. No agent changed either project's files or launched training.

## Acceptance tests matching the user's clarified goal

- **Known-translation fidelity:** reproduce the meaning of established translations, allowing defensible alternative wording. Seen training passages are a learning sanity check; known translations deliberately excluded from training measure generalization.
- **Unseen composition:** use independently checked sentences that recombine familiar vocabulary, change negation/tense/participants, or require different word senses. Separate these constructed probes from naturally occurring held-out passages. Respect work/copy groups and preserve test isolation.
- **Unseen passages and context:** evaluate complete passages from excluded works or genres when available, preserving enough surrounding context to resolve references and elliptical expressions. Report gaps in genre coverage.
- **Supported interpretation:** test idioms, omitted-but-recoverable elements and contextual word senses. Where evidence permits multiple readings, represent alternatives; do not reward added facts simply because the result reads fluently.

These are four complementary checks, not four model-building projects. A dictionary lookup or memorized passage alone does not satisfy the general translator goal.

## Proposed next decision for the implementation owner

1. Finish the current ByT5 comparison and evaluate saved outputs for meaning. This new research does not justify interrupting healthy training.
2. Register one new translation-specialist route with a bounded admission check: model/source license, exact revision, reviewed loading code, tokenizer round trip on actual typed input, no silent truncation, local runtime compatibility, memory, and save/resume. Keep it isolated from the frozen environment and use the existing execution owner.
3. Compare the unadapted specialist with one fine-tuned candidate on the same permitted TRAIN snapshot and fixed development passages. This distinguishes pre-existing competence from learned improvement. Match full source text and evaluation denominators; use each model's proper template. No held-out references in prompts or retrieval.
4. Use a published reference-linked semantic rubric: lexical senses, grammatical roles, negation, names/quantities, omitted/added meaning, target language and answer coverage. Score all four directions separately. Familiar failures are regressions, not new generalization evidence; include previously unreviewed development works/passages where available and keep final test sealed.
5. If direct Pahlavi-English remains weaker, evaluate the already-proposed Farsi intermediate route with an existing English/Farsi specialist. Inspect both intermediate and final outputs, because a fluent second stage can conceal first-stage errors. This route still requires a competent Pahlavi-to-Farsi stage.

Typed native-script coverage is part of the translator contract. If training uses scholarly transcription, document and test any supported text-to-text representation conversion separately. Do not silently relabel Pahlavi as modern Persian or make OCR a prerequisite.

No models were installed or run for this research. No Pahlavi improvement is measured here. The useful result is a concrete new candidate and reusable published methods for the training owner to assess.
