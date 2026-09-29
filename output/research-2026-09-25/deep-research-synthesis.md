# A quality-first route to a general Pahlavi translator

Research and source inspection: 25 September 2026. Scope: native text translation, including new passages and new combinations of known words. This report supersedes the earlier handoff's preference for the smallest feasible model. Compute, data acquisition and expert effort are requirements to describe, not filters that eliminate an approach.

**Recommendation:** build a Pahlavi-specialized translation system from a strong pretrained model and a carefully aligned scholarly corpus, and compare it directly with a strong model supplied with dictionaries, grammar and relevant translated examples at inference time. Add document context and expert correction data. Select the winner by blinded Pahlavi meaning assessment, then investigate cost reduction. This is the most credible development route identified in the research; it is not a claim that a particular checkpoint has already passed Pahlavi tests.

The useful distinction is between a pretrained model's capacity, its actual Pahlavi evidence, and a test that demonstrates generalization. Increasing any one alone does not establish the other two. The current project's failed Qwen adaptation does not settle the prospects of stronger models, full fine-tuning, better supervision or reference-guided inference.

## What the deeper search changed

**1. Serious ancient-language translation has a substantial training precedent.** MITRA adapts a pretrained model to historical Buddhist languages using domain text, parallel material and translation instructions. Its published scale is a 9B model, a 4.4-billion-token dataset, two pretraining epochs, and four weeks on eight A100 GPUs. That is approximately 5,376 GPU-hours for that stage, calculated from the reported schedule. Its translation evaluation is largely model-judged and is not Pahlavi validation. Nevertheless, it is a concrete ancient-language adaptation recipe worth borrowing, including at substantial scale. [MITRA paper](https://arxiv.org/html/2601.06400v1), [public model](https://huggingface.co/buddhist-nlp/gemma-2-mitra-it), [parallel-corpus project](https://github.com/dharmamitra/mitra-parallel).

**2. Reference-guided translation deserves a strong-model trial.** The original Machine Translation from One Book work and the subsequent Gemini experiment demonstrate learning translation from supplied linguistic material. A later ablation finds that parallel examples explain much of the gain; supplying a grammar is not automatically the decisive ingredient. These findings support comparing examples-only, examples-plus-dictionary, and grammar/gloss-enriched variants. They do not justify repeating an elaborate self-review prompt without evidence. [MTOB project](https://github.com/lukemelas/mtob), [Gemini technical report](https://arxiv.org/html/2403.05530v5), [XLR-MTOB code](https://github.com/Sethjsa/XLR-MTOB).

**3. There are reusable implementations beyond generic retrieval.** DiPMT++ combines retrieved translation examples with expanded dictionary hints. Its Qwen-72B experiments are a useful concrete example of spending model capacity on a scarcely represented language. GrammaMT offers a different lever: supplying interlinear gloss information. For Pahlavi, compare these methods with a strong plain translation baseline; dictionary accuracy and the source of glosses are explicit experimental variables. [DiPMT++ code](https://github.com/luciusssss/ZhuangBench), [GrammaMT paper](https://aclanthology.org/2025.acl-long.1447/).

**4. Large translation models belong in the comparison.** Include Hy-MT2-30B-A3B, TranslateGemma-27B, Tower+-72B and MiLMMT-46-12B, alongside a capable current long-context general model. Their size is not a reason to exclude them. Their modern-language success is a reason to test transfer, not proof that they already understand Pahlavi. The [model audit](</[USER_HOME]/Documents/ChatGPT/Pahlavi language/output/research-2026-09-25/deep-translation-model-audit.md>) identifies actual interfaces, language coverage, source files and resource implications. NLLB and larger ByT5 variants also remain credible contenders because translation-specific adaptation can outperform a larger general model.

**5. Competition successes point strongly to alignment and corpus work.** Deep Past's leading Akkadian solutions used substantial external scholarly material; the second-place account describes using a strong teacher to align existing human translations, while one method for inventing translations from morphology harmed performance. The first-place account includes ByT5-XL and an ensemble but reports a strong single checkpoint as well. Transfer the data and evaluation lessons; do not treat the competition as proof that 1,561 documents alone solve general ancient translation. [Second-place account](https://www.kaggle.com/competitions/deep-past-initiative-machine-translation/writeups/2nd-place-data-centric-akkadian-nmt), [first-place account](https://www.kaggle.com/competitions/deep-past-initiative-machine-translation/writeups/dpc-1st-data-quality-dictates-everything).

## The proposed system

Use a shared Pahlavi evidence collection for both contenders: texts and trustworthy translations aligned at meaningful spans, work/edition/translator identifiers, verified dictionary senses, grammar examples, and surrounding document context. Preserve the original native text and any internal normalized representation together. Resolving text conventions is part of language modeling; an OCR component is unnecessary.

First run the same strong model with only the source and permitted neighboring context. Then add references, adaptation and their combination in matched comparisons wherever the architecture allows. Keep input representation, evaluation examples and output requirements fixed. This separates improvements due to the method from improvements due simply to choosing a different base model.

| Contender | Concrete method | Why it may work |
|---|---|---|
| Strong reference-guided model | Supply source passage and neighboring context; retrieve relevant verified translations, dictionary senses and grammatical examples. Compare a long-context reference pack with targeted retrieval. | Gives a capable model linguistic evidence it may lack in pretrained weights. |
| Pahlavi-specialized model | Adapt a strong translation model using parallel and domain text; compare supervised full fine-tuning with an appropriate continued-pretraining stage and properly tuned adapters. Retain balanced English/Farsi translation supervision. | Learns recurring lexical and grammatical relationships, rather than requiring every answer to resemble a retrieved passage. |
| Combined system | Give the adapted model the same relevant evidence; generate alternatives only when a measured ambiguity or error justifies it. | May combine learned composition with trustworthy rare-word and contextual support. This combination must beat its components experimentally. |

For “reading between the lines,” provide the actual neighboring text and domain. Test pronoun reference, ellipsis, idioms, implicit subjects and competing dictionary senses. The translator should distinguish its chosen rendering from unresolved alternatives when the source does not settle them. Fluent invented detail must count as an error, not successful interpretation.

Known passages can use exact, provenance-linked translation memory in the eventual product. Score that separately. Correctly retrieving a known passage is useful, but it does not demonstrate that the model can translate a new combination.

Expert corrections should become reusable supervision: source span, incorrect candidate, corrected rendering, error type, and supporting evidence. This directly targets the project's observed meaning substitutions and negation errors. Translation post-edit/preference training has an existing precedent in [Tower+](https://arxiv.org/html/2506.17080v1). Prefer corrections tied to identifiable source meaning over generic requests to improve style.

## Resource implications — without exclusion

| Approach or workstream | Resource to budget | What is established versus still unknown |
|---|---|---|
| Reference-guided frontier model | Access to a capable long-context model, reference preparation, inference tokens and expert evaluation | No new weight training is required for this contender. Pahlavi-specific quality and token cost require a measured pilot. Hosted and self-hosted options remain eligible. |
| Large open model inference | Approximately 24 GB raw BF16 weights for a nominal 12B model; 54 GB for 27B; 60 GB for 30B; 144 GB for 72B | Arithmetic estimates, not sufficient GPU-memory specifications. Actual weights, KV cache and runtime overhead add memory. See model audit. |
| Full language/domain adaptation | Training cluster time, checkpoint storage, aligned text, monolingual text and experiment engineering | MITRA's measured precedent above shows the scale can extend to several thousand GPU-hours. This is not a forecast or minimum requirement for Pahlavi. |
| Corpus acquisition and alignment | Relevant editions, existing scholarly translations, rights/provenance checks and philological review | The available Pahlavi corpus size must be inventoried. We should acquire additional data where it improves coverage, rather than freeze the current small corpus as a constraint. |
| Human evaluation | Pahlavi expertise plus English/Farsi expertise; independent review and adjudication | Planning example: 300 candidate translations × two reviewers × 5–20 minutes is 50–200 reviewer-hours **per candidate system**. These times are assumptions; time a small pilot before budgeting. |
| Ensembles and candidate reranking | Multiple strong models/checkpoints, extra inference and a validated selection method | Eligible if their independent meaning gain justifies the extra work. Agreement alone cannot certify a translation. |

Hardware prices and exact training duration are intentionally not quoted before model, corpus and sequence lengths are selected. A cost estimate should be based on measured throughput and actual run configuration, not parameter count alone. The first decision is which route produces acceptable meaning.

## How to establish that it works

Use four separately reported conditions: familiar translated passages, unseen passages from familiar works, entirely held-out works/genres, and expert-validated compositional changes. The last condition deliberately changes such features as negation, agent/patient, quantity, possession or tense while keeping much vocabulary familiar. Include context-sensitive examples where neighboring text changes the appropriate rendering.

Partition works, editions, duplicate passages and translation lineages **before** segmentation, reversal, augmentation, oversampling or retrieval indexing. This matters concretely: the inspected Deep Past ninth-place script performs reversal and augmentation before its random split, allowing related examples to cross its internal validation boundary. This is a static code finding, not a measured contamination rate or a claim about the competition's private test. [Training source](https://github.com/Eleftheria14/Deep_Past_Gold_Solution/blob/main/training/train_finetune.py).

Evaluate each requested direction separately. Have qualified reviewers assess preservation of meaning, including negation, entities, who did what to whom, temporal relations and unsupported additions. Allow legitimate translation variants; exact reference-string matching is not the definition of correct translation. Record serious-error rates and paired system preferences, with uncertainty across held-out works. Automatic overlap and learned-quality metrics can supplement that assessment.

A work held out from our adaptation corpus may still have appeared in a foundation model's original training. We cannot certify unseen-pretraining status for public Pahlavi texts. Separately authored, expert-validated compositions and context variations help probe dependence on memorized translations; their provenance and privacy must be preserved through evaluation.

Before launching a large experiment, freeze its test and promotion criteria. A proposed initial screen is 300 segment-direction items spanning the four conditions, with a separate final holdout after development. Across four directions and four conditions this averages only about 19 items per cell: it is an exploratory screen, not sufficient broad acceptance evidence. Expand the final test, particularly unseen-work and serious-error cases, according to the uncertainty observed. Compare the plain strong model, its reference-guided variant, a fully adapted translation model, the existing project baseline and a simple translation-memory baseline. Select additional candidates by actual DEV results. The final test should include new human-validated combinations not published as reference examples.

## What should not be copied blindly

- **Synthetic expansion:** keep it eligible, but test it as an intervention. MITRA reports benefits from mined translation instructions, while Deep Past and the recent [GrammarMT study](https://arxiv.org/abs/2607.22376) report important failures or uneven gains for other synthetic recipes. Preserve provenance and test each direction. Use strong teachers for alignment and targeted coverage; do not relabel their output as expert truth.
- **Reference-free RL:** the [MiLMMT reward code](https://raw.githubusercontent.com/xiaomi-research/gemmax/main/scripts/rl/rewards/mt_dual_comet_reward.py) does not use the supplied reference in its score. Its reward must first be shown to distinguish Pahlavi meaning errors. An English-looking result can otherwise receive a good score while mistranslating the source.
- **Grammar or self-review as a universal fix:** expose verified linguistic information, then ablate it. More rounds are useful only when they improve independent translation quality.
- **Restoration/decipherment headlines:** restoring missing letters or dating an inscription addresses a different output than translating a supplied text. Those projects can contribute retrieval or uncertainty methods but cannot serve as translator validation.
- **Research code as a turnkey product:** the companion notes identify hardcoded paths, mismatches between descriptions and scripts, missing repositories, and evaluation risks. These are reasons to adapt and validate the implementation, not to discard the underlying method.

## Research package and handoff scope

The research combined primary papers, actual GitHub source files, official model cards and Reddit discussions traced back to primary evidence. It is an exploratory synthesis, not an exhaustive systematic review or a new benchmark.

- [Ancient-language methods and artifacts](</[USER_HOME]/Documents/ChatGPT/Pahlavi language/output/research-2026-09-25/deep-ancient-methods.md>)
- [Small-corpus transfer and controlled augmentation evidence](</[USER_HOME]/Documents/ChatGPT/Pahlavi language/output/research-2026-09-25/deep-small-data-transfer.md>)
- [Competition code, practical evidence and Reddit leads](</[USER_HOME]/Documents/ChatGPT/Pahlavi language/output/research-2026-09-25/deep-practical-evidence.md>)
- [Large translation-model source audit](</[USER_HOME]/Documents/ChatGPT/Pahlavi language/output/research-2026-09-25/deep-translation-model-audit.md>)
- [Earlier research handoff](</[USER_HOME]/Documents/ChatGPT/Pahlavi language/output/research-2026-09-25/translation-ai-handoff.md>), retained for history; its hardware-driven ordering is superseded here.

This task performed research and static inspection only. No Pahlavi model was run, installed, trained or shown to pass these tests. The implementation owner should incorporate this quality-first shortlist and evaluation plan at a safe boundary in the existing training task, then bring the measured quality and resource needs back for the resource discussion.
