# Corrected training package v2

**Quality decision, 30 September:** [Fresh blinded comparison](REPORT.md) finds2/15 whole translations accepted by each reviewer, versus1/15 for both earlier checkpoints. This is a limited gain, but both unchanged improvement screens fail. Retain step280; preserve corrected data and this candidate; no automatic extra training or laptop weight download.

**Execution update, 30 September:** the authorized [cloud job](https://huggingface.co/jobs/Mojionix/6abc15b8031314b696342162) completed96/96 updates and24/24 source-only DEV outputs in47minutes34seconds. All15 small output files plus the manifest (247,412bytes) have been recovered with verified hashes; the complete cloud inventory and provider commitments match. Both adapter binaries remain cloud-only; their bytes were not locally rehashed. [Recovery evidence](recovery.json), [comparison plan](COMPARISON-PLAN.md). The preparation-era statements below are preserved as history, not current execution status. Completion alone does not establish better translation quality.

29 September 2026. **Local corrected data and exact package: PASS; no training or cloud submission.** [Final verification](verification.json) records byte-identical data/job replay and10 passing runtime/regression tests; independent review found no remaining issue within its defined scope. The old source-qualified-v1 release, all previous training data/results and the fixed evaluation remain unchanged.

## Corrections and scope

The corrected pool contains **9,973 unique model-visible inputs**, representing **10,145 original records**; seven unresolved records are held. The original released total was 10,152. Fewer output rows reflect 170 lexical consolidations, two compatible historical translation consolidations and seven holds, not the deletion of supported dictionary meanings.

| Task | Corrected pool | Prepared pilot exposure |
|---|---:|---:|
| Historical Persian translations | 2,232 | 1,152 |
| Persian lexical inventories | 2,606 | 96 |
| MacKenzie English sense inventories | 3,412 | 64 |
| Manichaean Middle Persian English inventories | 1,420 | 32 |
| Conditioned Persian teaching units | 240 | 131 |
| Documentary English spans | 53 | 53 |
| Persian inscription occurrences | 6 | 4 distinct pairs |
| English edition spans | 4 | 4 |
| **Total** | **9,973** | **1,536** |

- All 7,608 lexical parents remain represented. Each identical input now has one complete structured answer containing all distinct supported entry inventories. An exact repeated inventory shares an entry index with all its provenance retained. Compound components and inflections keep their own form-to-meaning associations.
- Twenty lexical apparatus cases have exact source-backed dispositions. Editorial notes stay outside model-visible fields; genuine sense, grammar and dialect qualifications remain. The `da:68` reference is resolved to the explicitly named `watist` in archived `da:67`.
- Seventeen historical target typography cases are corrected through exact operations and before/after hashes. Three control characters become proper Persian half-spaces; they are not blindly deleted. One already-affected row also gains a source-supported missing conjunction space. Pahlavi source text is unchanged.
- Seven narrow holds cover three unresolved historical apparatus readings and four documentary uncertainty cases. MP6003 also has an omitted TEI damage marker, so its current rendering is excluded rather than treated as clean supervision. No invented replacement translation was supplied. MP2100's published idiomatic greeting remains source-conditioned, not literal-completeness gold.
- Two independently reviewed compatible historical variants share a canonical published target; alternatives and source IDs remain in provenance. The repeated Kanheri invocation is not sampled as additional independent phrase evidence.

The all-record checks cover exact source lineage, masks, prompt/answer round trips, reserved/unknown tokens, input collisions and length. No row is truncated; the largest sequence is 1,144 of 2,048 tokens. The full pool has 1,936,762 tokens; the prepared pilot has 274,703. These are tokenizer counts, not word counts or quality scores. Source-fidelity and bounded AI review do not provide professional philological certification of every word.

## Concrete next comparison, prepared only

Reuse the pinned `google/gemma-4-31B-it` revision and qualified step280 adapter. Keep the exercised NF4/BF16 LoRA recipe: rank16, alpha32, dropout0; fresh AdamW, learning rate0.0001, four warmup updates, seed3407, microbatch1, accumulation16, 96 updates. Every update has 12 historical, two lexical and two other examples under the existing equal-example loss. Full-pool training would exceed the current fixed schedule and is not silently substituted.

The corrected pilot preserves the previous parent order where possible. Its ledger records eleven ID changes: four canonical merged-parent remaps and seven replacements for held or duplicate parents. The four held documentary slots become unused reviewed pedagogy units. Therefore a comparison to the prior mixed96 candidate measures the **combined correction package**, not an isolated causal effect of dictionary cleanup. Retained step280 remains the qualification baseline. No claim that the previous regression was caused by the corrected records is supported.

This is the smallest controlled correction experiment using the existing runner, not a claim that repeating mixed supervision is an optimized strategy. Keep the existing source-only DEV24, first-attempt generation protocol, two-reviewer merit and promotion rules unchanged. A failed improvement screen ends the recipe; no automatic extra epoch, model switch, PAL promotion or laptop model download follows.

## Reproduction and execution boundary

Use the configured science Python with `-B -X utf8` from the project root:

```text
experiments/training-ready-v2-20260929/prepare.py --check
experiments/training-ready-v2-20260929/prepare_job.py --check
-m unittest cloud_pilot.test_mixed cloud_pilot.test_hf_mixed_recovery -v
```

The first two commands reproduce frozen data/package bytes without submitting a job. The unit suite uses tiny randomly initialized CPU fixtures; it does not train the project model. The local data and job spec are under `resources/local/training-ready-v2-20260929/`, with manifests and review evidence here. Code refuses to overwrite a frozen output. Original raw text and provenance remain available; only whitelisted `learning` fields enter the tokenizer.

**A paid launch remains closed.** The prepared A100 job uses a 100-minute provider timeout, 95-minute internal deadline and a 10-minute export reserve; the measured 20-update canary must admit continuation. GPU/NF4 behavior, Linux lifecycle and bucket persistence must be checked on the actual host. Current credit, cumulative spend, price and idle jobs must be checked immediately before any authorized launch. The pre-mixed-run USD18.73 observation is stale and cannot fund another run; do not assume the remaining USD25 ceiling fits this package. No recharge or budget increase is authorized.

The launcher now rejects duplicate IDs, failed data status, tokenizer identity mismatch, invalid/unknown token IDs, broken terminators and duplicate corrected prompts before model loading. It refuses relaunching the superseded v1 projection. The earlier training-completed/evaluation-failed recovery repair remains covered. Intermediate adapters preserve diagnostic state, not full optimizer/RNG resumption.

Git attributes preserve the exact bytes of the new package and its preceding audit receipts. This also corrects a Windows checkout issue where prior audit files had different line endings in Git than their hash-bound working copies; their actual evidence content and local files remain unchanged.

See [lexical decisions](lexical-review.md), [nonlexical decisions](NONLEXICAL-REVIEW.md), [runtime review](RUNTIME-REVIEW.md), [independent review](INDEPENDENT-REVIEW.md), and [readiness matrix](READINESS.md). All readiness claims are scoped to their direct execution evidence.

## Independent handoff

- Lead agent/request id: /root
- Critic agent/request id: /root/ready_v2_critic
- Critic model and reasoning effort: Inherited unchanged from lead; no override requested or applied
- Evidence reviewed: Corrected lexical/nonlexical source decisions, all9973 prepared arrays, exposure and frozen benchmark hashes
- Verification evidence: 7608 lexical parents checked against7648 XML observations;52 artifact bindings and12 benchmark hashes; final157531204582c50f2d8f73aaa76ce8aca0c83e2c6e624d60bbc8c8daa1515b54 manifest passed
- Independent from lead: yes
- Critic verdict: pass
