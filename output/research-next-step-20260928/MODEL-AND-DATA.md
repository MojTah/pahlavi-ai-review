# Backbone and data-allocation challenge

28 September 2026. Bounded primary-source research; no experiment was run.

**A trained multilingual encoder–decoder deserves one controlled comparison before any further Gemma contextual-SFT sweep. It does not yet deserve replacement status.** The stronger immediate investment is additional independent semantic evidence, selected across useful contexts and works. Model choice and data allocation remain competing explanations: neither the failed 12-anchor recipe nor the untrained Qwen comparison resolves them.

The project facts used here are the supplied 2,237 pairs / 37,492 source whitespace terms, 1,099 rows from one work (49.1%), and the prior reports. These are not a fresh data census. Qualified Gemma's provisional PAL result is not compared numerically with the new contextual DEV panel: their cases and reviewers differ. The contextual report's matched negative result does close that particular recipe. USD13.70 is the last reported credit observation, not a newly verified balance.

## Six studies that discriminate between the explanations

### 1. An encoder–decoder at 1,000 pairs is not automatically enough; related-language training matters

**Kalejaiye et al., _Ibom NLP_ (IJCNLP-AACL 2025).** Anaang, Efik, Ibibio and Oro ↔ English: 1,000 newly translated training pairs per language, 997 DEV and 1,012 test examples, with linguistic review. M2M-100 418M and NLLB-200 600M receive three epochs. A second condition first adapts on approximately 331,000 Efik–English religious pairs. For NLLB, mean X→English chrF++ rises **25.7→31.8**; English→X rises **19.4→24.1**. However, zero-shot Gemini 2.0 Flash reaches **34.7** on X→English. The paper's prose claiming all one-stage scores are below 25 conflicts with its table; the numbers here follow Table 3.

This supports testing translation-specific priors and related-language transfer, not an intrinsic encoder–decoder victory. LLMs were prompted, not equivalently trained; the extra 331K pairs are a major resource difference. There is no corresponding verified Pahlavi resource here.

Read depth: full-text §§4–6, dataset construction, training setup and Table 3. [Primary paper](https://aclanthology.org/2025.ijcnlp-long.22.pdf).

### 2. Representation can help related-language transfer, but stripping distinctions can harm it

**Amrhein and Sennrich, _On Romanization for Model Transfer Between Scripts in NMT_ (Findings EMNLP 2020).** Transformer transfer from five languages with one million English-parallel pairs each is evaluated on seven lower-resource languages. Yiddish has only **7,718 pairs**. Yiddish→English BLEU is **6.9** without transfer, **22.5** with original-script transfer, **24.9** with uroman and **28.9** with uconv. Marathi→English moves the other way: **45.0** original-script transfer versus **42.8** with uconv. Controls include original-script transfer, two romanizers, bilingual baselines and paired bootstrap tests on 2,000 test sentences. Vocabulary-transfer and segmentation details also differ; this is not simply “Latin characters are better.”

Pahlavi is already scholarly Latin transcription. This result gives no reason to strip diacritics, discard uncertainty markers or reconstruct a Persian-script source. A new representation must preserve distinctions and justify the actual transfer benefit; shorter tokenization alone is insufficient.

Read depth: §§5–7 and Tables 1–5. [Primary paper](https://aclanthology.org/2020.findings-emnlp.223.pdf).

### 3. Active selection contributes less than a misleading bundled comparison suggests

**Koneru, Liu and Niehues, _Cost-Effective Training in Low-Resource NMT_ (2022).** Kannada↔English experiments use 29K available bitext pairs, a 1.1K-entry dictionary, and **46M English / 15M Kannada monolingual examples**. At a 10K annotation budget, Kannada→English BLEU is **10.4** with random selection and no initialization, **21.7** with random selection plus dictionary-informed initialization, and **22.2** with the same initialization plus their cross-entropy-difference selector. Thus the controlled selection increment is **0.5 BLEU**, not the entire 11.8-point improvement. Diversity-only n-gram selection can lose to random; uncertainty-based selection depends on a competent starting model.

For us, acquire representative *and* informative attested contexts, not merely the rarest or highest-loss sentences. The paper does not establish an affordable CPT recipe for 37,492 source terms, and its dictionary entries are additional supervision, not labels inferred from model answers.

Read depth: full-text §§3–4, Tables 2–6, including the initialization/selection matrix. [Primary paper](https://arxiv.org/pdf/2201.05700).

### 4. More exposure to the minority portion can make its own generalization worse

**Chen et al., _On the Pareto Front of Multilingual NMT_ (NeurIPS 2023).** Over 200 multilingual Transformer experiments vary model size, resource scale and sampling ratios. Main comparisons include English→German 4.6M, French 10M, Chinese 260K and Hindi 260K. With imbalanced data, increasing a low-resource direction's sampling beyond an intermediate optimum worsens its held-out cross-entropy. In the four-direction test, proportional sampling averages **19.7 BLEU**, temperature 2/5 **21.8**, and fitted allocation **21.9**; therefore the main practical gain is avoiding a bad allocation, not a magical new optimizer. Models span 64M–317M parameters; validation selects checkpoints.

This directly challenges automatic equal-work sampling. Our 49.1% concentration is known; it does not prove harmful interference or identify an optimal cap. Languages are not literary works, and the published fitted law is not calibrated for Gemma/Pahlavi. Do not reproduce their large sweep.

Read depth: §§2–4, sampling curves, Tables 2–4 and data/training appendices. [Primary paper](https://arxiv.org/pdf/2304.03216).

### 5. Translation breadth can help, but the most striking comparison adds direct supervision

**Stap and Monz, _The Effect of Language Diversity When Fine-Tuning LLMs for Translation_ (Findings EMNLP 2025).** TOWER-7B is fine-tuned on 1,997 professionally translated NTREX sentences per direction across 10, 30 or 132 directions, evaluated on FLORES. Languages include German, English, Korean, Dutch, Russian, Chinese and six additional languages. Fully supervised COMET-STRICT changes only **0.876→0.880** from 10 to 132 directions. For originally unsupervised directions, **0.253→0.739** is much larger—but the 132-direction condition now trains directly on those directions. The 30-direction condition, which still excludes them, reaches **0.490**. Adding directions also adds training examples; this is not fixed-total-data evidence. Replications include Gemma-2-2B, 13B models and non-multiparallel data.

The result keeps related-language/translation-task mixtures eligible, but does not justify arbitrary multilingual filler or claim that 2K Pahlavi examples have the information content of 132×2K supervision. Work diversity is a separate hypothesis.

Read depth: §§2–3, Figures 1–2, Table 1 and appendices B/C.1–C.2. [Primary paper](https://aclanthology.org/2025.findings-emnlp.224.pdf).

### 6. A small-model success may actually be a strong-teacher and large-data success

**Song et al., _Are Small Language Models the Silver Bullet to Low-Resource Languages Machine Translation?_ (LoResMT 2026).** This is the publication of the earlier preprint line, not independent new replication. Luxembourgish↔English training uses **621,033 source examples per teacher condition**. The methods identify GPT-4o-mini for DG; teacher naming varies in surrounding prose. Distilled Gemma-2-2B's FLORES spBLEU reaches **23.50** English→Luxembourgish and **42.73** reverse with dictionary checking, while unadapted NLLB-3.3B scores **31.14 / 48.45**. Stronger in-domain validation results therefore do not establish universal superiority. Full fine-tuning substantially exceeds the tested LoRA settings; this is recipe-specific evidence, not a universal LoRA failure theorem.

The prerequisites are a capable teacher and hundreds of thousands of examples. We have not established either for Pahlavi. A smaller instruction LLM plus synthetic targets is consequently a lower priority than a translation-pretrained challenger.

Read depth: §§3–4, data/teacher methods and Tables 2–4; not every supplementary-language appendix. [Primary paper](https://aclanthology.org/2026.loresmt-1.1.pdf).

## Ranked next choices

| Rank | Action worth considering | Evidence required to change the decision |
|---|---|---|
| 1 | Allocate the next semantic-evidence effort to genuinely additional, interpretable contexts across relevant works. Use the existing provenance infrastructure. | A specialist or defensible published analysis settles a useful sense/role relation, and the context adds coverage rather than another copy of the same wording. Count annotation effort and new semantic coverage, not only rows. |
| 2 | One trained multilingual encoder–decoder challenger, before another Gemma mixture/epoch variation. | It must learn from the same qualified parallel resource and be evaluated under the same meaning rubric. An untrained zero-shot loss cannot reject a trainable family. A trained gain across works without extra critical errors would justify continuation. |
| 3 | A conservative work-allocation contrast on Gemma, only if existing work-level summaries suggest concentration-related failure. | The hypothesis must predict which underrepresented works/phenomena should improve. Hold total exposure fixed, retain the large work, and compare against the same-start control. Improvement must survive work-level reporting; a micro-average change is insufficient. |
| 4 | Related-language transfer or a small verified auxiliary translation mixture. | Establish actual lexical/grammatical relevance, rights, alignment quality and scale. Modern Persian fluency alone does not establish Pahlavi comprehension. Parthian, Avestan and Pahlavi cannot be pooled as one language. |
| 5 | Tokenizer changes, lossy transliteration, student distillation, or another small instruction-model substitution. | Admit only after a concrete failure mechanism or competent independent teacher is demonstrated. Neither shared alphabet nor parameter count is enough. |

These rankings are project-specific inferences. They do not claim a paper directly studied this corpus or its exact quality rubric. A rejected ByT5 checkpoint remains a checkpoint/task result; it is not disproof of byte-level models or the whole encoder–decoder family.

The 1,099-row concentration does **not** justify another descriptive census. Reuse the existing counts and work reports. Uniform-by-work sampling could repeat tiny works excessively and discard useful diversity within the large work. If an allocation experiment is later warranted, predeclare one moderate capped or smoothed distribution, report realized parent and target-token exposure, and change no other ingredient. The literature does not supply its optimal numeric cap.

## Cheapest informative model test

The smallest new modeling contrast is **one translation-pretrained encoder–decoder adapted on the unchanged qualified bitext**, against the retained qualified Gemma system. It is not another Qwen closed-book/assistance comparison, another TRAIN-recall audit, or another contextual-anchor run.

1. **Choose one candidate, not a model sweep.** My first research candidate is NLLB-200-distilled-600M; mBART-50 many-to-many is the fallback if adaptation prerequisites or permitted use make NLLB unsuitable. NLLB's author card identifies a 600M research translation model, a noncommercial license and a 512-token training-length caveat. mBART's author card explicitly lists Persian `fa_IR` and multilingual translation training. Neither card establishes Pahlavi support. [NLLB author card](https://huggingface.co/facebook/nllb-200-distilled-600M), [mBART author card](https://huggingface.co/facebook/mbart-large-50-many-to-many-mmt).
2. **Before admitting a run, settle only candidate-specific readiness.** Verify Persian output support, scholarly-character preservation, sequence length/truncation and a reproducible way to introduce an unsupported source language. Do not silently label Pahlavi as another language. Reuse existing corpus/token-census findings; only inspect what the new tokenizer changes. Token counts cannot certify semantic quality.
3. **Use unchanged data and merit.** Preserve all qualified targets, uncertainty and work exclusions. Predeclare the adaptation budget in parent/target-token exposure, a primary checkpoint and at most an earlier diagnostic checkpoint. Do not equate the same number of optimizer steps across architectures with equal training. A small model permits considering full adaptation rather than copying Gemma's LoRA restriction automatically.
4. **Score a matched source-only DEV comparison once, blinded.** Reuse exact qualified-Gemma outputs only if their input content, decoding provenance and coverage match; otherwise collect a matched comparator. Keep whole translations and constrained spans separate. Reused DEV supports development triage, not new confirmation. Do not reopen PAL-REF for tuning. Carry the existing meaning/critical-error/uncertainty gate forward rather than substituting BLEU, validation loss or “looks fluent.”
5. **Interpret the result narrowly.** This compares attainable trained systems with different foundation priors and adaptation histories; it does not isolate architectural causality. If the challenger clears the predeclared screen, obtain independent confirmation before replacing Gemma or downloading deployment weights. If it fails, close that bounded candidate recipe without converting the result into family-wide disproof.

This requires a new trained arm, so a literature review or tokenizer check cannot itself answer it. It also does not isolate the allocation question: doing that simultaneously would require additional controlled arms. Under the remaining balance, do not launch both branches merely to fill a matrix.

### Would testing the 12 trained auxiliary anchors change this choice?

A candidate/control unconstrained-generation check of the existing 12 anchors could establish whether the auxiliary task was mastered. It **cannot discriminate Gemma from an encoder–decoder**:

- Candidate-only mastery would show learning without whole-translation transfer, strengthening the case to stop narrow auxiliary repetition and seek broader semantic evidence.
- Both arms mastering the anchors would suggest the intervention was redundant for those examples.
- Both arms failing would leave learning, output-contract and adaptation constraints unresolved; it would not establish an architectural defect or authorize another training attempt.

All three leave the new-backbone hypothesis open. Therefore this is not a required model-selection gate. Run it only if a predeclared downstream action genuinely differs from the already-decided closure of the contextual recipe; otherwise skip it. “Free generation” describes unconstrained decoding, not verified zero compute cost.

The 8GB GPU and 64GB RAM make a 600M-class inference candidate more plausible than a new large local LLM, but full-training optimizer/activation memory is a different requirement. No local fit, latency, training duration or dollar cost was measured here. The user's willingness to wait 10–20 minutes weakens speed-only arguments for switching. No top-up or local weight download is justified by these papers alone.

## What would change my recommendation

- **Prioritize evidence allocation over the model test** if newly reviewed contexts reveal conflicting targets, unsupported glosses or systematic compositional gaps. Reweighting or architecture cannot decide historical meaning that the supervision leaves unresolved.
- **Prioritize the encoder–decoder pilot** if source/target evidence is stable enough for a meaningful comparison but no matched trained translation backbone has been tested. This is a genuinely different hypothesis from repeating the failed contextual recipe.
- **Prioritize related-language transfer** only after locating a usable, sufficiently substantial and linguistically relevant supervised resource. Generic language-family kinship is not that resource.
- **Prioritize a sampling contrast** only when existing aggregate work results make a falsifiable prediction; the already-known 49.1% fraction alone does not.
- **Promote no model from literature.** A provisional multi-work semantic gain with no critical-error regression is a reason for confirmation, not a guarantee of unseen-text translation or decipherment.

## Inspection boundary

Local project reading was limited to the model/regime/institution report summaries in `experiments/dev-assisted-qualified-20260927`, the latest contextual `REPORT.md`, and this report for verification; this file is the only write. I did not open underlying per-case label, test-answer or generation files, credentials or account data for this task. Primary public paper text and official model-card metadata were inspected through web retrieval. No code artifact, nested agent, paid job, model/corpus download, external account action, Drive access or email was used. Broader search leads were screened; the six studies above carry the recommendation. This report does not count the LoResMT publication and its earlier preprint as two independent studies.
