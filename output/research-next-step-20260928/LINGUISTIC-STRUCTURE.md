# Linguistic structure after the contextual SFT pilot

28 September 2026. Bounded primary-paper review; planning only. No model, dataset, credentials, cloud job, held-out answer body, or new label example was accessed. Six papers' full PDF methods/results or appendices were inspected through the browser; the numerical claims below are not abstract-only claims. Hardware omissions are explicit. Paper metrics are not calibrated Pahlavi meaning scores.

**Decision:** first measure whether the existing 12 auxiliary tasks were learned. The failed whole-translation comparison cannot distinguish failure to learn those targets from failure to use learned knowledge in translation. The most promising subsequent linguistic intervention is an explicitly source-aligned analysis supplied during translation, with its correctness measured separately. It is not yet a validated Pahlavi pipeline.

Project inputs supplied by the lead, not re-scored here: 2,237 qualified rows / 37,492 whitespace terms, approximately half from one work; qualified Gemma4-31B around 16–17/40 provisional PAL acceptances; both latest 48-update arms 0/15 whole DEV acceptances, with worse candidate critical errors. Twelve anchors cover nine works; their post-training auxiliary mastery remains unmeasured. The newly accessible Parsig *xrad* noun record proves an access/identity route, not a complete or gold annotation corpus.

## What is new relative to the existing reviews

I skimmed the titles and relevant sections of `RESEARCH-METHODS-UPDATE.md`, `RESEARCH-REGIMES-UPDATE.md`, `RESEARCH-EVALUATION-UPDATE.md`, and the model/institution notes under `experiments/dev-assisted-qualified-20260927`. GrammaMT, GlossLM, Aycock's grammar-book ablation, DiPMT++, PahGen, MITRA, and the institutional corpora are existing evidence; they are not counted as fresh discoveries here. The six studies below were not discussed in those inspected review notes. This is a comparison against that local review set, not a claim of novelty across all project history.

## Six primary studies

### 1. Morphology encoding matters more than simply mentioning tags

Rapacz & Smywiński-Pohl, **Low-Resource Interlinear Translation: Morphology-Enhanced Neural Models for Ancient Greek** (LoResLM 2025), §§3–5, Tables 2/4–7, Appendix C. [Full paper](https://aclanthology.org/2025.loreslm-1.11.pdf).

Ancient Greek→English/Polish **interlinear**, word-aligned translation uses 7,940 New Testament verses / 137,323 Greek words; random splits are 6,352/794/794. GreTa, PhilTa, mT5-base/large are compared across 144 configurations. Each uses one A100, effective batch 32, length 512; total training hours are not established here. Gold source tags enter text directly or dedicated embedding layers. Table 6 reports English best BLEU 44.67 baseline versus 60.40 autoencoder embeddings; configuration averages are 32.40 versus 53.26. Plain text tags average **30.86**, with best 46.00. Polish best increases 42.92→59.33. These are configuration aggregates/bests, not one isolated matched 15.73-point effect.

**Transfer:** evidence for aligned features, not generic tag prompting or another architecture purchase. Random verses from one corpus and literal output do not demonstrate unseen-work Persian translation. Prerequisites are trustworthy word alignment and morphology at inference; our 12 phrase targets do not provide these. No expert whole-translation acceptance metric was established.

### 2. Linguistically plausible augmentation often fails a matched control

Groshan, Ginn & Palmer, **Is linguistically-motivated data augmentation worth it?** (ACL 2025), §§3–7, Appendix A, Table 9. [Full paper](https://aclanthology.org/2025.acl-long.1307.pdf).

ByT5-small (300M) handles Uspanteko↔Spanish, Arapaho↔English, and glossing. Full training sets contain 9,096/41,824 sentences; fixed tests 1,064/4,892; subsets span 100–5,000. Three runs compare linguistic transformations, nonlinguistic noise, and unaugmented controls. Crucially, controls receive both training phases and the optimizer reset too: 500+1,000 Uspanteko steps; 2,000+4,000 Arapaho steps. The whole study consumed about 1,000 A100 GPU-hours; grammar preparation took about 200 hours.

At 1,000 Uspanteko→Spanish examples, chrF changes are +1.07±1.04 for conjunction insertion, +1.27±0.55 for noise, and +0.30±1.19 for tense/aspect/mood changes. At full size, those changes are −0.63, +0.13, −0.72. Many strategies harm performance.

**Transfer:** supports matched update/exposure controls and measuring the actual auxiliary skill; does not validate automatic Pahlavi sentence permutation or tense rewriting. Appropriate transformations require grammar and alignment expertise, and benefit is not guaranteed by grammaticality.

### 3. Gloss generation is a separate, imperfect task

Ginn, Hulden & Palmer, **Can we teach language models to gloss endangered languages?** (Findings EMNLP 2024), §§3–6, Tables 1/3, Figure 7. [Full paper](https://aclanthology.org/2024.findings-emnlp.337.pdf).

Unsegmented Gitksan/Lezgi/Natugu/Uspanteko→IGT uses 74/705/791/9,774 training examples and 31/87/99/633 tests as reported in this paper. Command R+ (104B) compares 0–100 examples and retrieval strategies; final tests also use GPT-4o, Llama3.1-8B (8-bit), and Gemini1.5Pro. No parameter updates; total inference hardware-hours/cost are not reported in the inspected methods.

In preliminary Uspanteko experiments, 50 source-chrF-selected examples yield **59.5±0.7% morpheme accuracy**, versus random 29.1±1.2%. This preliminary setting supplies the known translation. The final test removes translation lines after observing inappropriate lexical copying; LLMs then generally trail the segmentation-aware supervised system on three of four languages. The accuracy metric ignores excess predicted glosses.

**Transfer:** measure morphology, sense selection, and translation separately. This is not evidence that 50 gloss examples deliver reliable Pahlavi analyses. Missing prerequisites: consistent annotation conventions, independently checked glosses, and evaluation that also penalizes extra or invented analyses.

### 4. Source analysis can help translation, but some analyses are oracle inputs

Zhang et al., **Hire a Linguist!: Learning Endangered Languages in LLMs with In-Context Linguistic Descriptions** (Findings ACL 2024), §§3–5, Tables 1/4, Appendix C. [Full paper](https://aclanthology.org/2024.findings-acl.925.pdf).

LingoLLM combines dictionaries, available morphology, grammar descriptions, and an analysis-before-translation prompt. It evaluates eight languages / ten directions using GPT-4-1106-preview and 4-bit Mixtral-8x7B, one output/input, temperature 0.8, without fine-tuning. Resources include 70 Manchu pairs and 100 sampled examples per five SIGMORPHON languages; Bribri/Wolof use other benchmarks. Their full aggregate count and GPU-hours were not established in the inspected sections.

Table 1 GPT-4 averages are 0.5 spBLEU zero-shot, 3.2 three-shot, 8.2 dictionary-only, **10.5 full**. Thus 10.5 is the final score, not a 10.5-point gain over its 0.5 baseline. Gitksan dictionary-only versus morphology-assisted BLEURT is 0.4573→0.5448. Several resources/ablations use supplied corpus glosses or oracle mappings.

**Transfer:** supports an oracle-analysis diagnostic before building an analyzer. It does not prove an LLM can infer trustworthy Pahlavi morphology unaided. Sense ambiguity, participant roles, and source uncertainty must remain explicit; one published noun annotation cannot supply a passage analysis.

### 5. Dictionary-term inclusion and translation correctness can diverge

Dinu et al., **Training Neural Machine Translation to Apply Terminology Constraints** (ACL 2019), §3, Table 2, Appendix. [Full paper](https://aclanthology.org/P19-1294.pdf).

English→German uses 2.2M sentence pairs with roughly 10% additional terminology-annotated versions from the same pool. A two-layer encoder/two-layer decoder Transformer compares baseline, constrained decoding, and trained append/replace source annotations. Wiktionary/IATE tests contain 727/414 sentences and 884/452 terms. Single-GPU AWS P3 batch-one P99 decoding latency is measured; training GPU-hours are not established.

On IATE, constrained decoding raises term use 76.3→82.0% while BLEU **falls 25.8→25.3**. Trained append reaches 92.9% and BLEU26.0. On Wiktionary, hard constraints reach99.5% term use but BLEU25.8 versus baseline26.0; append yields90.7%/26.9. Latency is about0.68s constrained versus0.19s baseline/append. This table supplies correct reference-matching terms, an unusually favorable lexical condition.

**Transfer:** dictionary matches are evidence candidates, not mandatory Persian strings. Hard inclusion cannot establish the correct sense, inflection, scope, or participant role. Missing prerequisites include contextual disambiguation and a tested constraint-compatible model; this is not a drop-in decoder fix for current Gemma.

### 6. A structured intermediate representation can improve composition without a larger model

Herzig et al., **Unlocking Compositional Generalization in Pre-trained Models Using Intermediate Representations** (2021), §§3–5, Tables1/2/7/8. [Full paper](https://arxiv.org/pdf/2104.07478).

This is English→formal semantic parsing, **not translation**: CFQ, SCAN, and text-to-SQL. T5-base (220M) maps into source-aligned reversible representations, optionally combined with a lossy intermediate stage. CFQ has95K train/12K dev/12K test per split; smaller SQL template-training sets range408–4,812. T5-base/large use32 TPUv3 cores and under16 hours; T5-3B uses128 cores/about48 hours.

With the same T5-base, CFQ compositional-split exact-match mean rises34.6→60.8 with reversible representation, and67.8 with the combined variant. IID performance stays near99.5%. Controls use unchanged architecture and compare intermediate forms and model sizes.

**Transfer:** supports testing new combinations separately from familiar-parent recall, and a compact representation that preserves scope/roles. Executable gold programs and reversible transformations make supervision unusually reliable. Pahlavi lacks that representation and parser; inventing fluent chain-of-thought is not equivalent. No Persian translation gain follows from these exact-match results.

## Ranked next experiment

**First: a 24-response auxiliary-mastery diagnostic using the already frozen 12 parent/target tasks.** Compare the 48-update ordinary-translation control and the 48-update contextual candidate, whose adapters already exist in private cloud storage. Use the exact frozen auxiliary prompt, identical decoding/output cap, fresh contexts and one retained attempt per item. Freeze the scoring instructions before generation; assess only fidelity to each existing qualified contextual target and its uncertainties, with exact target match reported separately. Keep the existing qualification caveat: these targets are provisionally source-supported, not expert-certified gold. No additional training, synthesized examples, or new target labels are needed. Root must separately assess loading/serving cost; 24 short outputs do not eliminate model setup cost or authorize a paid job.

This differs from earlier TRAIN recall, which used whole-translation prompts, and from the completed DEV comparison. Report all12 items and all9 works; do not select the best-looking examples or aggregate this result into PAL accuracy. Whole passage translation remains the actual end goal.

**Falsifiable prediction:** the contextual candidate will gain at least two faithful auxiliary responses over its matched control, distributed across at least two works, without introducing a new critical contextual reversal. If control already has11–12 faithful responses, label the contrast ceiling-limited rather than moving the threshold. A miss means the assumed learned auxiliary skill has not been demonstrated; larger gloss pipelines or broader annotation collection should not be justified by this pilot. A pass alongside failed DEV identifies a task-transfer gap worth testing with source-aligned analysis supplied during translation. It still does not establish that the analysis itself is complete or that transfer will improve.

The strongest *conditional learning direction* is therefore a short, explicit analysis record—attested source span, lemma/sense alternatives, justified grammatical features, participant links, negation/modality and unresolved readings—followed by Persian translation. Before training that pipeline, compare verified analyses against a dictionary-only information control on independently qualified TRAIN-eligible material. Supplied analyses must come from attested annotation or competent review, not by reverse-engineering held-out Persian answers. This conditional direction is not an authorization to create a corpus or launch another experiment now.

## One tempting method to defer

**Defer dictionary-enforced decoding.** It is easy to obtain an impressive constraint-hit rate while preserving or worsening meaning errors. Our current access evidence has not established contextual dictionary coverage, and forced words cannot repair predicate/role composition. A future falsifiable test would require independently verified senses and compare hard inclusion against the same senses supplied as optional evidence; higher hit rate without better blinded whole-meaning outcomes would count as failure, not progress.

The same evidence gives no basis for more generic epochs, a third backbone, or large synthetic grammatical drills now. The resource bottleneck is trustworthy, occurrence-linked structure and its demonstrated use, not the mere availability of a noun endpoint. Keep all sixteen held-out work exclusions, original reference qualifications, unchanged DEV whole/constrained separation, and the existing uniform merit rules. Any later annotated evaluation condition must be named as assisted/oracle; its analyses and answers must never become training labels.

## Scope and limits

PASS for the bounded literature task: six primary full texts inspected; methods, numeric effects, controls, scale and compute information recorded with missing fields identified. Greek Table6 and augmentation Table9 were checked in extracted PDF text; a requested augmentation-page screenshot failed, so no claim of visual verification is made. Other searched papers, including the Sanskrit commentary study and morphology-constrained 2021 paper, were not included as established evidence in this note. No downloaded datasets, local paper files, model execution, expert adjudication, or new annotations were produced. All Pahlavi recommendations above are prospective inferences, not validated effect estimates.
