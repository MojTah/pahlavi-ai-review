# Independent review of the four-condition development plan

27 September 2026. Independent critic: `/root/final_external_judge`; lead: `/root`.

**Verdict: PASS for research and prospective experiment design only.** No methodological blocker was found in the reviewed PLAN.md. This review does not approve an implementation, model download, paid job, or deployment. The project goal remains active.

## Supported design and interpretation

- The 2-by-2 comparison addresses two useful uncertainties together: the operational model system and the benefit of the same evidence package. It uses 96 first attempts over 24 existing DEV passages, not 96 independent passages. Six cases per work remain fixed; the whole-translation counts by work are 4, 5, 4 and 2. All failures and per-work regressions must remain visible.
- The qualified Gemma step280 adapter and the released Qwen3.6-27B checkpoint have unequal adaptation histories and different decoding policies. The plan correctly discloses these differences. A result can guide the next practical system; it cannot identify a causal architecture effect or Qwen's possible quality after adaptation. No particular challenger advantage is established by the research.
- Within each family, the plain and assisted arms keep the numerical policy fixed. Literal tasks, sources, evidence order and qualification notices must match across families, using their own official templates and tokenizers. Cross-family token IDs are not expected to match. The contrast concerns the entire offered evidence/caution package, not a universal retrieval effect.
- Directly checked the [official Qwen3.6-27B model card](https://huggingface.co/Qwen/Qwen3.6-27B): the proposed nonthinking template switch and numerical settings match its current instruct recipe. The card warns that framework parameter support varies. The plan appropriately requires effective runtime verification and discloses its 4,096-token ceiling versus the vendor's general 32,768-token recommendation. No settings were exercised here.
- The frozen assessment contract keeps 15 provisional whole translations separate from nine constrained cases. Two fresh reviewers independently assess all 96 anonymized outputs. The prospective two-net-acceptance threshold, critical-error guards, accepted-to-critical guard and gains across two works are coherent conservative development rules. They are neither a significance test nor a deployment standard. Every lost acceptance and reviewer disagreement remains reportable.
- Reused DEV supports development selection. PAL-REF stays outside prompt selection, evidence ranking and threshold adjustment; its later use is a regression check, not newly independent confirmation. This preserves the declared evaluation role without claiming an untouched final evaluation.
- The evidence package remains exactly 58 attachments/56 witnesses, with no replacements or reranking. Its 139/291 legacy source-form coverage is not semantic coverage. Existing qualification and overlap-screen limits remain applicable. Source-only contextual relevance review may describe missing or ambiguous support; it must not use DEV answers to improve the examples.
- The research records both positive and negative evidence, including tasks with different languages, directions, representations, supervision and metrics. It motivates this bounded challenge without guaranteeing a global optimum. A negative result cannot establish that all model families, retrieval methods, native-script reading or unknown-word discovery are exhausted.

## Clarifications to preserve during implementation and reporting

1. Qwen receives one sampled output per case at seed42. This does not measure variability across seeds or establish repeatable typical quality. Freeze whether the seed is reset per case, the balanced order and effective sampling implementation before generation; preserve first attempts without selective retries.
2. The revised methods research note still proposes greedy decoding across families. PLAN.md explicitly chooses vendor-recommended sampling for Qwen and greedy Gemma, supported by the later challenger review. Treat PLAN.md as the authoritative prospective decision and record that deliberate supersession; do not implement the earlier generic recommendation accidentally.
3. Use only the declared contrasts and show the complete four-condition result. An assisted condition beating its own weak plain control does not by itself establish that it should replace the current Gemma control. Conflicting matched-condition advantages remain a tradeoff, as the plan states. Do not derive a new promotion rule after observing outputs.
4. Two same-family AI reviewers do not provide independent philological certification. A specialist check remains necessary for research-grade correctness or decipherment claims. No new semantic audit or expert adjudication occurred in this review.

## Budget and readiness boundary

The arithmetic is consistent: USD25 minus the prior USD11.7482 compute estimate leaves USD13.2518. With a USD0.75 reserve, the nominal remaining amount is USD12.5018. The proposed USD5 incremental target is below that amount, but neither figure verifies the provider balance, current rate, setup time or 96-output feasibility. Separate bounded jobs, one submission per admitted job, preserved partial results and no automatic retry are appropriate planning constraints; none was exercised here.

Immutable model/runtime identity, full prompts and qualification propagation, complete untruncated inputs, memory/time measurements, effective decoding, funding and rate checks, failure recovery and a frozen launch commit remain pending. Local 8GB GPU/approximately64GB RAM fit, Q8/adapter fidelity and 10–20-minute latency also remain unproven. The next decisive evidence is a reviewed concrete implementation and admission projection, followed only then by an authorized bounded run.

## Review evidence

Read PLAN.md, all four research updates, the frozen DEV assessment contract and the prior independent evidence review. Reused the completed exact-intersection finding and rechecked evidence/audit hashes. Inspected Qwen's primary model documentation; did not independently reproduce every cited research result. Applied the scientific-research-methods design and inference checklist. No models, cloud jobs, credentials, code changes or commits were involved. This is the only file written.

| Reviewed artifact | SHA256 |
| --- | --- |
| PLAN.md | `9a474717af53e4b74e765cf715b8bc80bcf141851630de64416bde0d2a88926b` |
| RESEARCH-CHALLENGER-UPDATE.md | `9d603afdfe05faed9a7fe64a3b17c7fd6fb4c32f6f38a07c23f70934153d1118` |
| RESEARCH-EVALUATION-UPDATE.md | `1937130f9043c628d052c492b936c73a5b02b7aa67549eb048c3f628332ee620` |
| RESEARCH-METHODS-UPDATE.md | `c9f0b6d3d0a17070c2c3ca22068b62f09c991c902144e6f6a50e73ee981c1066` |
| RESEARCH-MODELS-UPDATE.md | `e9a995ee1d3cd105ee86192db7c2812578534990aa33642a1da026ca94fcc158` |
| ../dev-diagnostic-20260927/assessment-contract.json | `f719bc4568a2fc30c97c76c7b34aab4509b493f96a480d0e42efe8f8425e88a0` |
| evidence/evidence.jsonl | `1d5e02cfb91dad1da94db072e9f5fcd6be463746bbc951425cb6631b5ea2ce4a` |
| evidence/audit.json | `193f49f54dd1649a6a0002ed423bdf3dfa7176a7a093e1532cdd1ce1ea32d8f1` |


---

# Current review: institutions, learning regimes and scientific validation

27 September 2026. **PASS for research and prospective design only.** This appended assessment supersedes the priority ordering in the historical review above. That earlier review and its pinned artifact hashes remain unchanged; its original byte-prefix SHA256 is `30640ada1e06b7951ac421ab5afa7d5cc3f98aa15d48681adb0e0f4c42fd7199`. The newly frozen PLAN makes the 96-output comparison an optional development experiment, with annotation feasibility and resource provenance ahead of any new training decision.

## Findings and scope

No methodological blocker was found in the final plan. It addresses the user's three distinct goals: retrieving an attested contextual meaning, composing known meanings in unfamiliar combinations, and proposing uncertain interpretations with corroborating evidence. TRAIN exposure is explicitly acceptable for the first recall task; unseen combinations and documents require separate exclusions. Unknown forms receive no invented gold label. A dictionary or nearest-parallel baseline prevents attributing a simple lookup success to a new language-model capability.

The regime taxonomy and contrasts are sound. LoRA/QLoRA are not learning objectives; inference assistance is not training. Translation SFT remains the anchor, while task-mixed supervision depends on independently grounded lexical and grammatical labels. CPT is conditional on suitable additional source material, rather than ruled out universally. Raw-text loss, round-trip consistency and an uncalibrated judge reward cannot establish translation correctness. A future regime comparison must hold the starting backbone fixed and disclose actual objective-specific tokens, updates and changed factors. The optional cross-family comparison cannot answer that regime question.

The local inventory undermines the assumed large untranslated-data opportunity without claiming that all external corpora are exhausted. Independently checked all seven source hashes and byte sizes in its JSON. Recomputed raw 4,507 rows/109,854 whitespace terms, qualified 2,237 rows/37,492 terms, and all 62 untranslated IDs/260 terms. The untranslated rows all belong to work151, sequence0, with no translation layers. Confirmed the recorded exclusion pool contains 1,555 rows/47,189 terms. The largest qualified work has 1,099 of 2,237 rows, or 49.1283%. These are structural counts, not model tokens or a linguistic certification. An initial scratch assertion used the normalized work-ID form against the raw numeric string; correcting that inspection assumption produced the stated PASS without changing any data.

The institutional examples are used at an appropriate strength. Direct checks of FU Berlin's MPCD description confirm its manuscript-based corpus, three university partners and Avestan/Pahlavi interlinking. Invisible East's citation policy supports attributed use, not a blanket image/edition license. The MIT papers support constrained cognate/segmentation tasks: the 2019 Linear B dataset retains 919 pairs after uncertain readings are excluded; the 2021 Gothic evaluation uses top-ten stem matching and the Iberian case uses previously identified names. Aeneas's 23 participants/60 inscriptions concern epigraphic assistance, not Pahlavi translation accuracy. The eBL study uses 965 synthetic fragments, which cannot alone establish open-world discovery accuracy. These are valid methodological precedents, not ready Pahlavi translators or proof of an institution-endorsed training recipe.

Scientific rigor is an intended process here, not an achieved expert-validity label. The plan explicitly requires Pahlavi-qualified review of references and blinded outputs before expert-level correctness or decipherment claims. Expert access and cost are unsecured. The frozen 15-whole/nine-constrained assessment remains separate; repeated DEV/PAL-REF use is disclosed. Any later confirmatory set requires new unexposed documents, independent work groups and a prospective precision target. Previously inspected material cannot become retrospectively sealed evidence. Alternate witnesses and held-out sources stay excluded even from source-only CPT; unknown foundation-model exposure remains a limitation.

The earlier decoding-document discrepancy is resolved: the methods note now explicitly defers to PLAN.md's greedy Gemma and vendor-sampled Qwen policies. The prior warnings about a single sampled answer, unequal adaptation and provisional AI judges still apply. No new reference set, annotation labels, preference labels or training admission was created.

## Verification limits and next evidence

Read the final PLAN, regimes report, inventory Markdown/JSON and both institutional reports, plus the corrected methods paragraph. Performed bounded primary-source spot-checks and the local count/hash checks above. No semantic regrading or experiment reproduction occurred. MPCD methodology returned403 and Chicago's parsing page returned502 in this critic's requests; detailed annotation claims for those inaccessible pages rely on the supplied research reports and their stated access limits. Other reported study results were assessed for appropriate interpretation, not independently reproduced wholesale.

The USD25 cumulative cap, prior USD11.7482 estimate, USD0.75 reserve and USD5 nominal target remain unchanged. No current provider balance, timing or runtime was verified. The next useful evidence is a traceable, independently reviewed lexical/construction feasibility packet and a precise resource-eligibility decision. Only after those prerequisites can a concrete training contrast or the optional inference experiment receive technical and budget review. Local quality, quantization, latency, scientific correctness and paid launch remain unapproved. The overall goal remains active.

## Current artifact identities

| Artifact | SHA256 |
| --- | --- |
| PLAN.md | `f44a3c8fe890cb9e139e8a57ed529d81934459b1de71d6b9e2401e4dd6a56464` |
| RESEARCH-REGIMES-UPDATE.md | `e05f5d584cd8f8391ce674748adc3a62fa551d80c0199e0cd3e5ef5eeb4f8a37` |
| UNLABELED-DATA-INVENTORY.md | `3f3cb026678cab5c486aee9339157d6d0601b11c8031ea9e17e594f25dde0134` |
| UNLABELED-DATA-INVENTORY.json | `7eba461256dfcf44e324dde31d2b119cac1b4fae866ca0a53e705217389ba060` |
| RESEARCH-INSTITUTIONS-IRANIAN.md | `3ae56e042c4c308d407e2ec92ee6fdd67ebd19958b3ee95cdfe7566db6df9860` |
| RESEARCH-INSTITUTIONS-METHODS.md | `d96bcc884391943232e0fb21645c81fb58553f8c3dd1e362602234a93bb9a224` |
| RESEARCH-METHODS-UPDATE.md | `ee12b879f557cb5cda21ac0ceec52c4b5d10a5128c9355c1bd66956f7b2473e4` |

## AutoCode Critic record

- Mode: Classic + Critic.
- Lead agent/request id: /root
- Critic agent/request id: /root/final_external_judge
- Critic model and reasoning effort: inherited session settings, no override
- Independent from lead: yes
- Critic verdict: pass
- Evidence reviewed: final artifact hashes above; preserved historical review; primary-source spot-checks; seven inventory source hash/size checks; independently executed source-count assertions.
- Verification evidence: all seven inventory source hashes and byte sizes matched; independently executed source-count assertions passed; final PLAN hash matched; historical review byte prefix preserved.

The critic did not write the plan, research reports or inventory. Verification covers research/document design and local structural data only, with no model, GPU, cloud, deployment or expert semantic validation. PASS applies to the research/design checkpoint; it is not paid launch or training admission.

Remaining gates: trustworthy auxiliary labels, specialist measurement validation, split/rights eligibility, fixed concrete contrast, runtime/funding checks and eventual local-quality validation. The only critic-written file is STRATEGY-REVIEW.md. No code, corpus, benchmark, model, account, credential or cloud change; no commit.
