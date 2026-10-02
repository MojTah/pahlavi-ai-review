# Evidence and decision register

**New local evidence, 1 October:** [Four-case component packet](../../experiments/component-diagnostic-20261001/PROTOCOL.md) binds actual occurrence/reference scopes and12real A/B/C prompts. Independent Astra review passes after scoring/status consistency fixes;887maximum prompt tokens and six mutation checks establish local preparation, not runtime or linguistic certification. Corrected witness-level exposure and the full protection union prevent treating Kanheri's alternate ID as unseen or acquiring Zādspram answers from WZ-K35. This separate semantic-assistance diagnostic can guide whether a larger panel is worth assembling; it cannot promote a model or justify training. Missing past-stem bindings confound negative results. New source issue: printed MacKenzie `stadan` Manichaean spellings carry uncertainty stars omitted in XML; preserve this issue for future dictionary review, never create confident aliases from it. Main datasets and frozen merit remain unchanged.

**Current decision, 1 October:** use the [completed-history synthesis](../../experiments/strategy-reset-20261001/REPORT.md) and [four-pass outcome](../../experiments/dose-acquisition-20260930/live-execution/OUTCOME.md). Acquisition and NF4 controls are complete; occurrence-qualified composition and measurement are now the priority. The dated register below preserves earlier evidence and cannot authorize repeating its superseded next steps.

**Implemented resource:** [v3 preparation](../../experiments/usable-resource-20261001/README.md) preserves all9,973qualified groups and7,438lexical inventories in plain source-mapped targets. The full lexical answer token comparison177,445old label-content versus38,527new standalone target tokens establishes formatting overhead only, not its causal role in poor translation. Meaningful internal annotation remains;11named cases require source review. Fifteen published-construction candidates are one familiar textbook lineage,14previously selected, not a complete independent multi-work panel. Local preservation and evidence-preparation reviews pass; no new training or paid inference is admitted.

28 September 2026. Targeted synthesis for this project, not an exhaustive systematic review. Primary papers/official documentation below were inspected; findings are conditional on their experiments. See [recipes](MODEL-RECIPES.md) for local identities and implementation constraints.

## Local executed evidence

| Observation | Decision consequence | What it does not establish |
|---|---|---|
| [Qualified-data paired PAL review](../../experiments/palref-paired-20260927/REPORT.md): reviewer A accepted 14→16/40, B 16→17/40; critical errors 9→7 for both. | Preserve qualified Gemma step280 as the comparator and preserve data provenance. | Perfect training labels, specialist certification or uniform gains across works. |
| [Plain/assisted comparison](../../experiments/dev-assisted-qualified-20260927/REPORT.md): Gemma whole acceptances 1→3/15 per reviewer, but critical errors increased; Qwen inference did not pass the screen either. | Ordinary prompt assistance is not currently promoted. | All retrieval/decoding methods fail, or trained Qwen cannot work. |
| [Matched contextual pilot](../../experiments/contextual-supervision-20260927/REPORT.md): control and candidate each 48 updates; both 0/15 whole acceptances; constrained critical 3→4/9. | Close this particular continuation recipe. | Contextual or structured supervision can never help. |
| [Familiar-target fit](../../experiments/train-fit-20260927/REPORT.md): teacher-forced NLL fell 4.299→0.884 on 20 TRAIN parents. | Record optimization and translation quality separately. | An exposure-bias diagnosis, a proven loss bug, or adequate free translation. |
| [NLLB preparation](../../experiments/nllb-feasibility-20260928/README.md): tokenizer census and random CPU plumbing passed; independent review completed. | Proceed to concrete recipe/lifecycle preparation without repeating the same checks on unchanged artifacts. | Pretrained 1.3B training, GPU cost or better translations. |
| [NLLB completed adaptation and paired review](../../experiments/nllb-supervised-20260928/REPORT.md):700 updates, trained23/24 complete; both raters accept0/15 versus Gemma1/15, with more critical errors. | Retain Gemma; do not promote this NLLB recipe. Preserve the cap failure and choose one discriminating diagnostic before more spending. | All NLLB methods fail, training is inactive, an architecture cause, or a decoder-only fix will improve whole meaning. |

| [Completed NLLB TRAIN20 diagnostic](../../experiments/nllb-seen-20260928/precision-repair/REPORT.md): both raters accept2/20;5/5 contextual glosses retained but only2/23 and4/23 functional scopes preserved; all20 correct-source likelihood advantages positive. | Prioritize genuinely additional, independently grounded whole-clause supervision; deprioritize another paid decoding diagnostic or more epochs by default. | A unique cause, decoding cannot help, generalization, or a cross-model NLL comparison. |

Do not subtract historical PAL-REF scores from later DEV scores: cases and panels differ. The project [timeline](../../output/RESULTS-TIMELINE-20260928.md) preserves earlier results. Existing studies of [linguistic structure](../../output/research-next-step-20260928/LINGUISTIC-STRUCTURE.md), [learning objectives](../../output/research-next-step-20260928/LEARNING-OBJECTIVES.md) and [model/data choices](../../output/research-next-step-20260928/MODEL-AND-DATA.md) remain the deeper literature index.

## Primary external evidence that changes the next decision

### E1 — New direct comparison of adaptation methods

Stackhouse & DeBenedetto, **A Systematic Comparison of Parameter-Efficient Fine-Tuning Techniques for Low-Resource Neural Machine Translation: Evidence from Indigenous Languages of the Americas**, AmericasNLP 2026, Villanova University. [Paper and metadata](https://aclanthology.org/2026.americasnlp-6.4/), [methods/results PDF](https://aclanthology.org/2026.americasnlp-6.4.pdf).

NLLB 600M, 13 Indigenous→Spanish directions, 357–125,008 training pairs, three seeds. Test mean chrF++: full fine-tuning 25.12, OFT 25.06, LoRA 22.70. OFT retained an advantage on the two lowest-resource languages. Reported mean training hours were 1.63 for OFT, 0.96 full and 0.88 LoRA; fewer trainable parameters did not guarantee faster execution.

Limitations: one configuration per method, different learning rates, automatic metrics, one backbone/target language. Newly added language tags were initialized from Spanish, with embeddings frozen during PEFT. Our trainable transcription-character additions differ.

**Inference:** full fine-tuning remains a defensible initial proposal, not an established winner. Add OFT as a serious conditional alternative; do not start an adapter sweep or transfer the reported hours to our provider. Record quality, memory and elapsed cost separately.

### E2 — Small-data adaptation precedent

Aycock et al., **Can LLMs Really Learn to Translate a Low-Resource Language from One Grammar Book?**, University of Amsterdam, [paper](https://arxiv.org/html/2409.19151v2), [author code](https://github.com/Sethjsa/XLR-MTOB).

Distilled NLLB 1.3B was adapted using 1,239 book examples, with additional-data experiments. Book-only Kalamang→English chrF++ was 28.6 versus 33.1 for prompted Gemini; the reverse direction favored NLLB. Effects were direction-dependent, and back-translation was not uniformly helpful. The study used a separate development set; its hyperparameters are not calibrated for our repeated DEV cases.

**Inference:** a translation-specialist adaptation is credible at our data scale. This does not predict a Pahlavi gain or validate a specific epoch count. The author's public example code contains incomplete/demo paths and configuration inconsistencies; borrow the tested scientific idea, not an unchecked launcher. This source was already known to the project; its priority changes after the negative contextual result.

### E3 — Model-specific implementation constraints

- [PEFT v0.21 LoRA API](https://huggingface.co/docs/peft/v0.21.0/package_reference/lora): selected token embeddings can be trained alongside adapters. Tied weights and save/reload require explicit handling. **Project implication:** a PEFT fallback must prove that all added NLLB rows remain trainable and recoverable; ordinary attention LoRA alone is insufficient.
- [Versioned NLLB tokenizer implementation](https://github.com/huggingface/transformers/blob/v5.13.1/src/transformers/models/nllb/tokenization_nllb.py): use the pinned serialization and actual local checks. **Project implication:** stale examples of language-tag placement must not replace our verified source/target encoding.
- [Official seq2seq translation guide](https://huggingface.co/docs/transformers/en/tasks/translation), [Gemma tuning guide](https://ai.google.dev/gemma/docs/tune), and [TRL SFT documentation](https://huggingface.co/docs/trl/en/sft_trainer): consult only for the relevant architecture/trainer behavior. **Project implication:** no generic tutorial overrides our split, masks, no-truncation policy or semantic merit.

## Current decision and reopening conditions

| Option | Current decision | Evidence needed to change it |
|---|---|---|
| NLLB 1.3B full supervised adaptation | One candidate completed; no promotion. Formal completion screen inconclusive and semantic improvement conditions unmet. | A new specific, tested intervention supported by diagnosis; no automatic extra epochs. |
| NLLB LoRA / OFT | Conditional alternatives, not scheduled parallel jobs. | Resource infeasibility or a specific preservation/overfitting hypothesis; proven new-row learning and recovery; a bounded prospective comparison. |
| More Gemma training / fine-tuned Qwen | Retain as alternatives, not the immediate next run. | A new intervention with a discriminating prediction, rather than more epochs after failed translations. Qwen's trained potential remains open. |
| Source→analysis→translation / multitask learning | Conditional. | Reliable source-aligned labels and an experiment separating correct supplied analysis from model-generated analysis. Phrase-target training did not test all such systems. |
| Source-contrastive decoding | Conditional, deprioritized after familiar construction failures. | Evidence that it addresses actual generated errors, preserved source knowledge, stable controls and a prospectively bounded comparison; source preference under supplied gold prefixes is insufficient. |
| Continued pretraining, synthetic self-training or back-translation | Defer. | A sufficiently useful clean additional corpus or independently validated teacher; quality filtering and holdout protection. |
| DPO / RL / learned reward | Defer. | Trustworthy preferences/reward and evidence that optimizing it improves the unchanged translation merit. Fluent output or judge approval alone is insufficient. |
| Broad work reweighting / harder vocabulary constraints | Defer. | A controlled reason to expect improved whole meaning, with known losses and coverage protected. Frequency imbalance alone does not select an optimal sampler. |

**Next decision after the completed familiar-passage diagnostic:** source sensitivity with supplied reference prefixes coexists with poor free composition. Obtain genuinely additional published whole-clause parallel contexts for negation, modality, comparison and participant roles, with independent philological qualification and split protection before training admission. Start from the local source inventory. Do not repeat the already completed23-scope audit or failed12-anchor mixture. Preserve exact text, citations, alternatives and uncertainty; no DEV/PAL answer or reviewer correction becomes a target. The user's strengthened [dataset-readiness requirement](../../DATASET-READINESS.md) now requires consolidated coverage, review and freezing before another run; a small source addition alone is insufficient. [MacKenzie entry access](../../experiments/mackenzie-access-20260928/README.md) is verified, including a concrete flattened-field labeling hazard, but full acquisition and Persian target qualification remain open. Select the next model/method after the full data evidence; absent credible new supervision, conserve funds rather than substitute an unmotivated decoder/model/epoch sweep.

**Decoding alternative reconsidered before and after unblinding:** [Sennrich et al., EACL2024](https://aclanthology.org/2024.eacl-short.4/) and [author implementation](https://github.com/ZurichNLP/ContraDecode/blob/main/translation_models/m2m100.py) motivate source-contrastive probability subtraction, not a log-ratio. The research review's pre-unblinding predicate deprioritized the method if familiar qualified functions broadly failed; the2/23 and4/23 result satisfies that concern. Unsupported additions in18/20 are the strongest counterargument, but current likelihood measurements do not show that wrong generated continuations are source-independent. Keep the method open without claiming a Pahlavi benefit or launching another paid test by default.

Keep uncertainty explicit: limited qualified data, 49% concentration in one work, repeated development selection, AI semantic raters and absence of a demonstrated decipherment system are unresolved research limits. More reliable independent semantic evidence and expert calibration are useful parallel work; they do not require changing the fixed merit or purchasing another run now.
