# Independent strategy critique

28 September 2026. **PASS with notes for research and preparation only. No implementation, model replacement or paid launch is approved.** Classic + Critic; the critic did not write the research notes or synthesis.

## Next decision

**Prioritize B: prepare one trained translation specialist, provisionally NLLB-200-distilled-1.3B. Keep C as bounded parallel semantic-evidence work. Do not make A a mandatory paid gate.** This ranking serves the practical objective of finding a better translator; it is not an established scientific ordering of all possible interventions.

The failed contextual comparison closes that tested recipe. It does not test a properly adapted translation-pretrained encoder–decoder. The earlier untrained Qwen comparison cannot answer this question either. Reusing the qualified pairs gives B a concrete, testable contrast without requiring an indefinite annotation campaign. Neither architecture nor more data can settle genuinely unresolved source meanings; the provisional targets remain a limitation for every arm.

The proposed 1.3B choice is defensible as one predeclared capacity/budget compromise with the cited small-data precedent. It is **not** evidence that 1.3B is better than 600M on Pahlavi. Do not follow a failed result with an automatic size ladder. The official card identifies a research model, noncommercial licensing and a 512-token training-length caveat; it establishes neither Pahlavi support nor this laptop's memory/quality result. [Author model card](https://huggingface.co/facebook/nllb-200-distilled-1.3B).

A would answer a real missing question: whether the exact twelve auxiliary tasks were learned. Candidate-only recovery suggests acquisition without demonstrated whole-translation transfer; equal recovery suggests redundancy; failure leaves learning/output-contract issues unresolved. None, by itself, selects between Gemma and NLLB or reopens the closed recipe. It should precede B only if a specific outcome changes an available next intervention. A fresh reload has nonzero cost; “free generation” is not free compute. The linguistic note's preference for A is scientifically coherent but has lower immediate decision value under the lead's stated objective.

## A live alternative, not a discarded prompt test

Source-contrastive decoding deserves to remain conditional. Independent inspection of the EACL paper confirmed source-contrast gains of 1.3/1.1 chrF for M2M-100/SMaLL-100, with regressions on high-resource averages. The often-quoted 67–83% reduction in the low-chrF proxy is for **combined source and language contrast**, not source contrast alone. Its Llama experiment tests **language** contrast and off-target output, not Gemma source-faithfulness. [Methods, Tables 1–3 and §5](https://aclanthology.org/2024.eacl-short.4.pdf).

This is a genuinely different inference intervention from prompt assistance. It changes decoding and adds conditional evaluations; zero updates do not establish lower total cost. Retaining it behind B is reasonable because B explores an untested trained system, whereas contrast's Pahlavi semantic effect and Gemma implementation remain unverified. This ordering is judgment under uncertainty, not a paper-proven superiority result. Reconsider it if B's compatibility or complete-cycle budget gate fails. Do not add it to the first B arm and confound two new changes.

## Conditions preserving a meaningful comparison

- Compare against the **retained qualified step-280 Gemma**, not the latest failed contextual control. Cached outputs are usable only with exact source, coverage and inference provenance; historical rater scores are not the new paired baseline.
- Preserve all 2,237 qualified pairs and their uncertainty. Full adaptation is a reasonable candidate, but the schedule must be fixed before its DEV result. Same optimizer steps across architectures are not matched learning opportunities. Document parent/token exposure, native serialization and decoding differences. This compares attainable systems with different priors and histories, not a causal architecture effect.
- Resolve unsupported-source conditioning, character/token preservation and the 512-token issue before admission. No silent truncation, dropped cases or reference-derived splitting. A startup failure or deliberately inadequate allocation is not a negative test of the model family.
- Preserve the 15 whole/9 constrained denominators, first-attempt failures, separate fresh reviewers and existing critical-error safeguards. The exact existing rule is **global net accepted gain at least two, plus newly accepted cases in at least two works** for each reviewer; a work need not have positive net gain. The final synthesis explicitly preserves this distinction after the critic's correction.
- Untouched NLLB DEV generation plus trained NLLB and cached Gemma makes **72 outputs per fresh reviewer**, including 48 new NLLB generations. The final synthesis now prices this scope, reviews every condition and keeps the primary trained-NLLB-versus-Gemma comparison distinct. The untouched baseline is descriptive, not a new selection branch. This closes the draft's review-coverage ambiguity.
- USD 3 is a proposed complete-cycle reservation, not a measured quote or spending guarantee. USD 13.70 is a historical observation. Admission still needs fresh funding/rate evidence and measured startup, download, adaptation, evaluation, recovery and shutdown feasibility. No automatic shortening, top-up or model sweep.

Repeated DEV use supports exploratory selection only. A passing screen is not significance, specialist certification, unseen-word decipherment or deployment readiness. The unchanged PAL-REF regression and independent semantic confirmation remain separate. A failed candidate closes that recipe, not the encoder–decoder family.

## Verification and evidence

Read the three research notes, the lead's synthesis and latest contextual report. Checked the unchanged uniform contract and the actual `paired_report` implementation for denominator, gain and critical-error rules. Independently spot-checked the NLLB author cards, the Ibom low-resource training methods, and the EACL source/language-contrast methods and results. The lead repaired the two synthesis precision issues and the EACL attribution; the critic re-read those final sections and rebound their hashes. No unresolved blocker remains for this research/preparation recommendation. This was not a re-audit of every cited paper. No held-out answer bodies, model outputs, weights, credentials or cloud state were inspected; no runtime/model tests were performed.

Reviewed SHA256:

| Artifact | SHA256 |
|---|---|
| Contextual `REPORT.md` | `b3859a251781a4da3b76754a9ee9b1ec7426e1813a97a2768f6aa46283aa1102` |
| Uniform evaluation contract | `4165e8150f291c2cd6077d2daee86513ad08e1851acbfc3e83169bc40263f8c2` |
| `LEARNING-OBJECTIVES.md`, final | `df7b159fc93f2a6497915469b5e77ba682c2539b2ebf3eb8cec36cba36b2822a` |
| `LINGUISTIC-STRUCTURE.md` | `c9c0e20f1932d3222a83cdd65be18514d2c26e6d20abe1b6c046d3cfb9961654` |
| `MODEL-AND-DATA.md` | `cef162bb7e4fe9872d7c6ed00e74dd83e6bd8d9ed7aeaa8fbd8a7b1584771387` |
| Lead synthesis, final | `896b6289ac0c860eb1a6d3c38f5f4fbbc492ad69c58d77ef4cd3d4c402d8aa95` |

Lead agent/request id: /root
Critic agent/request id: /root/final_external_judge
Critic model and reasoning effort: inherited session settings, no override
Independent from lead: yes
Critic verdict: pass with notes
Evidence reviewed: Three pinned research notes, lead synthesis, contextual result, uniform contract, existing paired scorer and primary-source spot-checks described above.
Verification evidence: Direct local reads and SHA256 checks; direct comparison of contract with paired_report; primary model-card/method/table inspection. Research/design only; launch and full runtime remain unverified.
