# NLLB familiar-passage diagnostic: completed outcome

28 September 2026. **Both fresh blind AI reviewers accepted the same 2/20 familiar TRAIN translations.** All scheduled calls completed. Correct sources strongly improve likelihood of supplied reference targets, but this does not establish reliable free translation. Retain qualified Gemma step280 as the comparator; no model is promoted or downloaded locally.

## Semantic result under the existing rubric

| Reviewer | Accepted /20 | Meaning error | Critical error | Uncertain | Execution error |
|---|---:|---:|---:|---:|---:|
| A | 2 | 8 | 10 | 0 | 0 |
| B | 2 | 10 | 8 | 0 | 0 |

Both accepted `TRAINRECALL1-003` and `TRAINRECALL1-006`. Both identified unsupported additions in18/20 outputs. These are selected, previously trained passages across16 works, not held-out generalization or a population accuracy estimate. The reviewers remain separate; agreement is not independent philological certification. The original references and uncertainty qualifications were retained.

The28 inherited local scopes answer narrower questions. Both reviewers preserved all5 published contextual glosses. Among the other23 functional/construction scopes, A recorded2 preserved,17 contradicted,2 omitted and2 unassessable; B recorded4 preserved,14 contradicted,2 omitted and3 unassessable. Local scope checks are not extra whole-translation votes. The evidence therefore supports some familiar lexical recovery alongside frequent failures in propositions, participants, negation and directives; it does not establish universally correct word meanings.

For example, a prohibition against grief became an instruction about someone going before us. A passage about having nobody became an incomplete inability construction. The preserved local negative-assertion form in the latter does not validate its changed predicate. See the separate judgments in [scored/summary.json](scored/summary.json).

## Conditional target fit

| Equal-parent diagnostic | Result |
|---|---:|
| Correct-source full-target NLL | 1.7465892340 |
| Fixed mismatched-source full-target NLL | 4.9727921577 |
| Mean mismatch penalty | 3.2262029237 |
| Median mismatch penalty | 3.2344818199 |
| Penalty range | 1.0398834997–5.6354277867 |
| Positive penalties | 20/20 |
| Content-only mean penalty | 3.3713623020 |

NLL units are nats per supervised model token. Full targets include the language tag and EOS, as prospectively specified; content-only excludes exactly those tokens and also has20/20 positive penalties. All40 likelihood calls and20 first generations completed, without an optimizer update. Source lengths7–208 and target lengths6–201 were unchanged.

This establishes sensitivity to the selected source permutation while the correct answer prefixes are supplied. Mismatched sources are not expert-certified negatives. It does not identify exposure bias, prove that incorrect generated continuations are source-independent, or establish a decoding cure. Do not compare these NLL values numerically with Gemma's different tokenization. The older partial Gemma TRAIN recall also had different coverage/panels, so it is not a matched accuracy comparison.

## Preserved failure and verified repair

The [first attempt](../FAILED-ATTEMPT.md) stopped during readiness, before any of60 scored calls. CUDA BF16 native cross-entropy differed from the independent FP32 likelihood calculation. Root and critic reproduced the numerical mechanism with tiny synthetic logits; the failed A100 attempt did not preserve its raw loss values, so this is not an exact reconstruction of that unrecorded value.

The [prospective repair](PLAN.md) changed only the calibration reference to explicit FP32 cross-entropy, preserving the FP32 estimand,1e-5 tolerance, inputs, model, generation and rubric. Raw native loss remained recorded. Actual repaired A100 readiness and all40 forwards passed; maximum FP32-reference discrepancy was4.772534198949074e-7. Raw native discrepancy reached0.006516999650193256. The original training objective already used explicit FP32 cross-entropy and is not implicated by this diagnostic bug.

Both separate review files were hash-frozen before scoring. Root schema, coverage, hashes and literal-span checks passed. The [independent outcome audit](OUTCOME-QA.md) reconstructed packets byte-for-byte and reproduced all arithmetic, then separately verified the frozen semantic summaries. This validates records and calculations, not linguistic truth. No failed attempt was replaced in the historical record.

## Resources

The first job ended ERROR; the repaired job `6aba47e96b030d633f69c82d` ended COMPLETED at11:02:01.187 UTC. A provider check at11:04:40 UTC found all22 jobs terminal. Conservative rounded compute estimates for both attempts totalUSD0.541671, within theUSD1.25 combined allocation; these estimates are not invoices.

The authenticated billing page at11:07:31 UTC showedUSD18.73 period usage andUSD11.66 credit. The displayed usage roseUSD0.45 across both attempts, while credit fellUSD0.46; these account deltas are not per-job invoices. The authorized cumulativeUSD25 ceiling leavesUSD6.27 of spending headroom at that observation, distinct from the available credit. Automatic recharge was unset. [Billing receipt](execution/billing-after.json), [terminal receipt](execution/terminal.json). Recheck mutable account/rate/idle state before any further paid work.

All weights remain on cloud. Only small records, evaluation outputs and packages were recovered locally.

## Next decision: additional grounded composition supervision

**Deprioritize another paid decoding diagnostic and automatic extra epochs.** Before unblinding, the research reviewer specified that broad failure of qualified familiar constructions would weaken the case for source-contrastive decoding. The observed2/23 and4/23 preserved functional scopes meet that concern. Five preserved glosses and strong teacher-forced source preference do not outweigh poor whole-clause generation.

The strongest counterargument is that both raters flag unsupported additions in18/20 cases, a behavior that source contrast aims to reduce. [Sennrich et al., EACL2024](https://aclanthology.org/2024.eacl-short.4/) supplies a credible inference alternative, but its other-language results are not Pahlavi evidence, and our diagnostic did not show source-independent incorrect continuations. Keep it conditional rather than spend next by default. This does not prove decoding cannot help.

The next constructive work is to identify genuinely additional, published whole-clause source–translation pairs illustrating negation, modality, comparison and participant assignment. Start with the existing local source inventory; preserve exact wording, bibliographic/page evidence, alternatives and uncertainty. Check duplicate/work separation against TRAIN, DEV and PAL before qualification. Keep uncertain candidates in a separate staging record; do not modify the frozen dataset or invent targets from model guesses or reviewer corrections.

Prioritize independent philological qualification before admitting those relations as new training supervision. This must add new attested contexts, not repeat the23-scope audit or the failed12-anchor mixture. If useful new supervision is secured, predeclare one controlled training intervention with the unchanged merit and a justified comparator/recipe. If it is not secured, conserve funds and record the exact evidence gap. No training job is admitted by this report alone.
