# Pahlavi translation: foundational research and strategic decision
Research checkpoint: 25 September 2026. Scope: supplied text, Pahlavi/Middle Persian ↔ English/Farsi, familiar translations and genuinely new combinations. Resource needs are described without excluding expensive approaches.

[Evidence index](EVIDENCE_INDEX.md) · [Structured research database](research-database.json) · [Training-task consultation](TRAINING_STRATEGIC_CONSULTATION.md)

## Decision for the training task

**Continue the project, redirect the next experiments, and withhold any claim of a working general translator.** Existing failures do not show that the goal is impossible. They do show that further small-model training or longer self-review prompts need a concrete new hypothesis and independent meaning evidence.

| Decision | Recommendation and reason |
|---|---|
| Current bounded ByT5 comparison | Complete the existing recovery and reference-linked translation evaluation at the training owner's safe boundary. The latest project record says three epochs completed; no semantic-quality gain is established. Preserve its useful baseline result, whether positive or negative. |
| Repeating the current Qwen/LoRA or self-review recipe | Pause additional long repetitions without new evidence, data or a specific tested diagnosis. Previous source diagnostics still failed critical meanings; a falling loss cannot settle them. |
| Corpus and linguistic work | Continue immediately. Expand authentic aligned translations, verify senses against scholarship, preserve text layers and build expert-reviewed tests. This work does not need a larger GPU first. |
| Stronger models and larger training | Keep eligible. Test strong reference-guided inference and strong translation-specific adaptation. Select by Pahlavi meaning, then discuss the necessary compute. |
| Declaring the whole project hopeless | Not justified by the inspected evidence. Historical-language translation and unsupported-language adaptation have credible precedents, though none guarantees Pahlavi success. |
| Waiting for resources | Pause the dependent experiment if its required expert, data, model access or compute is missing. Continue other useful work. Do not equate “need a scholar” with “need a bigger GPU.” |
| Releasing a general translator | Wait until unseen-work and compositional meaning tests pass. A useful narrow-domain assistant may be an earlier outcome, but must be described with that scope. |

The live training project state was read at this checkpoint: Qwen3-4B adaptation remains inactive with meaning failures; the previous eight-output diagnostic ended NEEDS_REVIEW; the dictionary has zero reference-checked senses; English DEV covers one work. The newer ByT5 result is pending translation comparison. These are recorded project findings, not a new independent runtime audit. The implementation task remains the sole owner of training, recovery, permissions and GPU scheduling.

The pause recommendation does not cancel the already frozen S04 mechanism test or permanently reject Qwen/LoRA. Complete the current owner's bounded, informative diagnostics under their existing gates. Review the eight regressions and three additional critical screen cases, recognizing that those eleven diagnostic rows share only six passages and cannot establish general accuracy. Suitable continued-pretraining data may be acquired; the proposal is not restricted to today's corpus.

The training owner's new TRAIN-only audit records 463 English pairs across ten work IDs and 2,609 Farsi pairs across 78. Reversal yields 6,144 directional examples, not that many independent bilingual passages; there are 2,613 distinct stored source records, all using Latin transcription. Record identity does not establish statistical independence. These counts describe this adaptation dataset, not what the foundation model knows, and do not by themselves explain any error. Evaluation must specify the supplied representation. The owner is already resolving three Berkeley bibliography examples; this research does not duplicate that task or inspect TEST text.

## What the evidence supports

There are two serious routes worth comparing: a strong model given reliable Pahlavi evidence at inference time, and a pretrained translation model adapted using high-quality Pahlavi parallel/domain text. Their combination is also eligible. This is a development recommendation, not a claim that one released checkpoint already solves Pahlavi.

The [MITRA study](https://arxiv.org/html/2601.06400v1) provides a substantial historical-language adaptation precedent. [DiPMT++](https://aclanthology.org/2024.findings-acl.519.pdf) and [GrammaMT](https://aclanthology.org/2025.acl-long.1447/) motivate explicit lexical and grammatical support. [MTOB-related experiments](https://arxiv.org/html/2409.19151v2) show why example translations and grammar prose should be tested separately. Results transfer as hypotheses; different languages, corpora and evaluation methods prevent a simple leaderboard ranking.

Ancient-language success is often partly a data achievement. The [Deep Past second-place account](https://www.kaggle.com/competitions/deep-past-initiative-machine-translation/writeups/2nd-place-data-centric-akkadian-nmt) uses strong-model alignment of existing scholarly translations and much more external data than the seed competition corpus. Its failed synthetic-label variant is a warning to distinguish alignment from inventing new ground truth. [MAFAND](https://aclanthology.org/2022.naacl-main.223.pdf) supports translation adaptation with limited but relevant in-domain pairs; it supplies no universal pair-count threshold.

The [ancient-language survey](https://aclanthology.org/2023.cl-3.5/) led to source checks of Sumerian NMT and Hanja historical translation. MIT decipherment, Sanskrit linguistic tools, LMU electronic Babylonian Literature, Georgetown Coptic work, and Oxford/Berlin/Bochum/Cologne/SOAS projects contribute different parts of the solution. None should be misrepresented as an existing Pahlavi translator.

## The foundational data work

The immediate database deliverable is a source-linked research registry, not an imported or licensed training corpus. It records evidence, intended use, limits and access status. A corpus record count is not an aligned-pair count; a page count is not a token count.

| Priority asset | What was verified | Required next step |
|---|---|---|
| [Oxford Invisible East](https://www.invisible-east.org/corpus/1024/) | A real Middle Persian document with numbered source/English lines, scholarly references and named editor; corpus offers structured exports. | Audit export coverage, rights and shelfmark overlap with existing Berkeley data. Count only new usable alignments. |
| [MPCD](https://www.geschkult.fu-berlin.de/en/e/iranistik/forschung/MPCD/index.html) | Institutional corpus/dictionary project and layered annotation methodology; approximate 800k-token project scale in a university abstract. | Resolve released versus planned volume, obtainable annotations and exact reuse terms. This is not 800k English parallel pairs. |
| [MPCD Kosh](https://www.mpcorpus.org/glossaries/) | Searchable scholarly lexical resources are documented. | Recover attributable senses and attestations; distinguish a verified meaning from an automatic draft. |
| [BBAW MIRTEXT](https://turfan.bbaw.de/bilder/mirtext-2.pdf) | Substantial published Manichaean Middle Persian/Parthian text collection. | Separate languages, duplicates, variants and editorial supplements; verify reuse. Mainly source-side evidence. |
| [BBAW German reader](https://turfan.bbaw.de/bilder/texte/textempdeutsch.pdf) | Middle Persian forms and corresponding German translations. | Preserve German originals. Any English/Farsi conversion is derived supervision requiring separate labels/review. |
| [Berkeley OpenAMPD](https://mp.melc.berkeley.edu/exist/apps/OpenAMPD/landing.html), [TITUS](https://titus.uni-frankfurt.de/texte/texte2.htm), [MUYA](https://muya.soas.ac.uk/tool/transcriptions-editions/) | Editions, provenance, source coverage and/or editorial workflows. | Check individual completeness, language, licensing and overlapping witnesses before admission. |

One consequential exclusion is semantic, not resource-based: the [Pahlavi Psalter comparison](https://turfan.bbaw.de/bilder/texte/psaltermpsyrgrengversesglossarysept2012.pdf) explicitly says its English KJV column is not a translation of the Middle Persian. Shared verse labels do not make these gold translation pairs.

Use bibliographies to acquire further scholarly editions and English/Farsi translations, including costly or offline resources where they add coverage. No large newly reusable Middle Persian–Farsi parallel corpus was verified in this research. That is an acquisition gap, not evidence that none exists. No scholar was contacted and no access agreement was obtained here.

## What “understanding” requires

[MPCD methodology](https://www.mpcorpus.org/methodology/) and the philology review support preserving three different things: supplied written form, interpreted linguistic reading, and contextual meaning. Typed input removes the OCR problem; it does not necessarily remove ambiguity.

Maintain a minimal traceable record with work/document and passage ID, edition/witness, exact input and convention, optional scholarly reading, surrounding text, target translation, translator, uncertainty, rights and data lineage. Add lemma/sense/morphology and alternative readings when supported. Automatically inferred annotations must keep that status.

The system must preserve who did what to whom, negation and obligation, omitted participants, names, quantities, possession, technical legal/ritual meanings, quotations and commentary. Experts sometimes legitimately disagree. A good output can state the unresolved alternative; inventing a confident resolution is a failure.

For known passages, use provenance-linked translation memory where appropriate. For new combinations, the model must condition on the actual source relations and context. Both are useful features; report their quality separately. English/Farsi → Pahlavi is a generation task with different evidence and grammaticality needs from translating Pahlavi into a modern language.

## Recommended comparison sequence

1. **Finish the present baseline.** Evaluate saved ByT5 and Qwen outputs against references and source meaning, including all known serious failures. Separate run completion, DEV loss, similarity metrics and expert meaning outcomes.
2. **Measure a strong model's best supported performance.** Compare the same capable base model with source/context alone, with manually selected verified references, and with automatically retrieved references. Select both reference conditions from a frozen permitted evidence pool. For unseen-material tests, exclude held-out target translations and answer-equivalent witnesses, quotations or near-duplicates. The manually selected condition is an oracle diagnostic: it distinguishes missing retrieval from inability to use correct evidence, without revealing the test answer. Exact translations remain allowed in the separately reported known-passage translation-memory condition.
3. **Adapt a strong translation model.** Use authentic aligned passages, balanced directional supervision and document context. Include full fine-tuning of larger ByT5/NLLB-style models and eligible larger translation specialists. Compare properly tuned adapters rather than generalizing from one failed LoRA recipe.
4. **Test substantial continued pretraining where justified.** Use authentic monolingual Middle Persian/domain text, then supervised translation and expert corrections. Keep a matched no-CPT baseline; extra pretraining is not automatically beneficial.
5. **Combine only demonstrated strengths.** Compare adapted-model-plus-references against its components. Consider ensembles, post-edit/preference training and targeted synthetic composition when independent DEV evidence identifies a benefit.

Hy-MT2-30B-A3B, MiLMMT-46-12B, TranslateGemma-27B and Tower+-72B belong in the eligible large-model pool, alongside a capable current long-context general model. Their model cards establish modern-language interfaces, not Pahlavi competence. Some stock templates reject unsupported language codes; licenses and intended contexts differ. The model audit records these concrete issues. Model size is neither an exclusion rule nor proof of superiority.

Use strong teachers preferentially to align or annotate existing scholarship; retain synthetic provenance when creating new targets. A Pahlavi-capable expert must check novel-combination examples before they become evaluation truth. Do not optimize an unvalidated Pahlavi reward merely because it is called COMET or a translation reward model.

This sequence selects experiments by information gained and quality prospects, not by what fits the current laptop. It also avoids launching a large undiagnosed sweep. Exact budgets follow the measured pilot and the user's resource discussion.

## Evidence required to continue, redirect or stop a route

Partition underlying works/documents, editions, parallel witnesses and translation lineages before segmentation, reversal, augmentation or retrieval indexing. Known quotations and formulaic near-duplicates need grouping. Public texts held out locally may still have appeared in foundation pretraining.

Report four conditions separately: exact-known material; new passages in familiar works; held-out works/genres; and privately authored, expert-validated new compositions/context contrasts. Separate all requested directions. Negation, participant roles, possession and reference changes should alter the answer appropriately. A successful contrastive choice is not enough: test generated translations too.

Use blinded specialist assessment with legitimate reference alternatives, serious-error labels and adjudication. Published translations are evidence, not infallible labels; preserve defensible alternative readings. Automatic metrics are secondary until their relation to Pahlavi judgments is measured. An exploratory 300-item screen spreads thinly over four directions and four conditions; it cannot certify a general translator. Expand final testing by work and error type, reporting uncertainty and abstention coverage.

The [Galen expert study](https://arxiv.org/pdf/2602.24119v2) motivates explicit rare-terminology and catastrophic-error checks. [MITRA-zh-eval](https://aclanthology.org/2025.nlp4dh-1.12.pdf) shows that an automated judge can become useful after domain-specific human calibration, while its modest reviewer agreement also supports calibration and adjudication. Neither establishes Pahlavi metric validity. The [evaluation audit](evaluation-evidence.md) also covers cross-direction contamination, translationese, contextual generation and statistical power. Reversing a published Pahlavi translation tests reconstruction; add expert-approved natural English/Farsi prompts to evaluate new Pahlavi generation.

Proposed decision rules for the implementation owner:
- Continue a route when independent source-linked review shows repeatable meaning gains on new material, with known critical errors corrected and no material directional regression.
- Redirect retrieval if oracle references help but retrieved references do not. Redirect the base model or supervision if even verified oracle support leaves systematic role/negation errors.
- Stop a particular recipe after a preregistered bounded comparison shows no practically meaningful gain; retain its negative result. Do not extrapolate one recipe's failure to every architecture.
- Pause an expensive dependent stage when its corpus, scholarly review or compute cannot be supplied. If only hardware is missing, proceed with corpus/evaluation preparation.
- Defer a broad product claim when only formulaic or known-domain material passes. Agree the acceptable serious-error rate and coverage before final qualification; no threshold has been approved by this research task.

A matched system comparison should hold source representation, source-context availability, test items and output requirements fixed; reference access deliberately varies by experimental condition. Report paired differences with work-level uncertainty where enough independent works exist. Do not claim success from self-consistency, reciprocal translation agreement, training loss or an LLM judging its own answer.

## Methods and hardware summary for Mojtaba

These are planning envelopes, not measured Pahlavi requirements or purchase specifications. Larger resources remain allowed. GPU count alone is insufficient: software sharding, interconnect, sequence length, batch, optimizer and checkpoint policy matter.

| Method | Hardware planning envelope | Other essential resources |
|---|---|---|
| Strong hosted model with verified references | Ordinary local computer; inference runs at provider. No local training GPU needed. | Capable model access, token budget, licensed reference pack and expert judgments. |
| Open 7–12B reference-guided model | Illustrative 48–80GB GPU for BF16 pilot inference; raw nominal weights are 14–24GB before cache/runtime. | Same evidence and evaluation; long contexts/batches can require more. |
| Open 27–30B model | Start sizing around one 80GB GPU for short/moderate-context BF16 inference, with multi-GPU capacity available. Raw weights about 54–60GB. | Profile actual model/template and context; this is not a guaranteed fit. |
| Open 72B model | Illustrative two 94GB GPUs or four 80GB GPUs with supported sharding. Raw weights about 144–146GB. | Extra inference budget; Pahlavi and even Persian coverage varies by model. |
| ByT5-XL full adaptation | Official XL size is about 3.7B parameters. An illustrative 1–2 × 80GB pilot allocation, with checkpointing/sharding as needed. | High-quality parallel data; byte sequences can be long. Profile before reservation. |
| Full 7–12B / 27–30B adaptation | Illustrative 4–8 × 80GB / 8–16 × 80GB cluster classes. Full 72B adaptation can require a larger cluster, e.g. 32 × 80GB under conventional mixed-precision Adam. | Broad corpus, reliable holdouts, training engineering, expert corrections, ample checkpoint storage. These are examples, not minima. |
| Extensive historical-domain pretraining | Cluster-scale option remains eligible. MITRA reported eight A100s for four weeks for its pretraining stage. | Billions of mixed domain tokens in that precedent; Pahlavi needs its own data/throughput plan. |
| Corpus, dictionary and expert benchmark | Ordinary CPU workstation and secure versioned storage suffice for much preparation; no major GPU purchase prerequisite. | Editions, alignment work, Middle Persian expertise, English/Farsi reviewers and adjudication. |

Raw BF16 weights use approximately two bytes per parameter. Conventional mixed-precision Adam can require roughly 18 bytes per parameter for weights/master copy, gradients and optimizer state **before activations**; alternative optimizers, precision and sharding change this. Thus 72B full training has approximately 1.3TB of such state before activation overhead. [Memory accounting](https://huggingface.co/docs/transformers/model_memory_anatomy), [ByT5 sizes](https://github.com/google-research/byt5/blob/master/README.md), [H100 specifications](https://www.nvidia.com/en-us/data-center/h100/). The [A100 datasheet](https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/a100/pdf/a100-80gb-datasheet-update-a4-nvidia-1485612-r12-web.pdf) confirms the named 80GB configuration. No throughput, dollar price or wall time was measured here.

The largest non-hardware commitment may be scholarship. Illustratively, 300 outputs × two reviewers × 5–20 minutes requires 50–200 reviewer-hours per candidate. These are assumptions to calibrate, not observed annotation times. Budget corpus acquisition and adjudication separately. Do not reduce this need to “someone checks fluency.”

**My strategic advice:** fund and organize the evidence-and-evaluation phase now; preserve the current ByT5 baseline; then compare a strong reference-guided model with a properly adapted translation model. Do not wait idle for hardware, and do not commit to a large training campaign solely because the smaller run failed.

## Audit trail and scope

The evidence database and index link the source records and companion reports: academic resources, philology, ancient methods, interdisciplinary systems, small-data transfer, practical/Reddit/code inspection, model interfaces and evaluation. This checkpoint is a substantial exploratory research synthesis with citation tracing, not an exhaustive systematic review or a reproduced benchmark.

No model was downloaded, called on project texts, trained or activated by this research task. No corpus export was imported. No professor was contacted. Proposed methods and capacity estimates remain to be tested by the implementation owner.
