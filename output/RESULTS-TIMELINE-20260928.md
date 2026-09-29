# Results timeline and current strategy

Prepared 28 September 2026 from saved experiment records, with an independent chronology/comparability check. Updated after the completed NLLB pilot, fresh paired reviews and familiar TRAIN20 diagnostic. Dates below are UTC. This timeline itself launches no jobs.

The largest observed PAL-REF acceptance gain came from the first Gemma training run. Qualified-data retraining showed a smaller additional improvement, with regressions on some works. Subsequent prompt, supplied-example, contextual-training and the completed NLLB full-adaptation experiment have not established a safe further improvement.

These results are **not one continuous accuracy curve**. PAL-REF40 is the fixed 40-case benchmark; DEV has 15 whole-translation cases and 9 separately constrained cases. Familiar TRAIN recall and numerical target-fit tests answer different questions. Semantic ratings remain provisional AI judgments, not Pahlavi-specialist certification.

| Date/order | What we tested | Recorded result | What it establishes |
|---|---|---|---|
|21 September|Qwen3-4B, first full training: 6,144 directional examples, 1,152 updates|Pahlavi→Persian chrF++ rose 8.69 → 36.26 on 9 selected examples; serious meaning errors remained.|Character/word n-gram overlap improved. These are not accuracy percentages and predate the current uniform benchmark.|
|Before 26 September|Qwen prompting, self-review, small lexical/grammar aids|Five-stage generation completed 35/64 outputs versus 57/64 for one-stage. Small lexical/grammar trials gave mixed judgments without reliable meaning improvement.|More elaborate prompting was not a demonstrated solution. Completion counts are not correctness scores.|
|25 September|ByT5-small: 6 epochs, 2,304 updates|Training loss fell, but long generation repeated until the output cap; selected short outputs still had meaning errors.|This trained candidate failed its generation gate. The planned full comparison was not completed; the whole ByT5 family was not disproved.|
|26 September|Existing Qwen, six passages translated separately into Persian and English|All 12 outputs completed; important meaning errors remained in both languages.|No language winner was established. Persian remained the practical focus because more parallel supervision was available.|
|26 September|Untouched Gemma 4 31B on PAL-REF40|**5/40 accepted (12.5%)**, 14 critical errors.|Measured original-model baseline.|
|27 September, first training|Gemma: 2,484 rows, 2 epochs, 312 updates|**15/40 accepted (37.5%)**, 10 critical errors on the same PAL-REF40.|Largest observed benchmark gain; still unsuitable for unchecked translation.|
|27 September, instruction diagnostic|Original versus first-trained Gemma under two instructions|Original 0/15 under either instruction; trained 3/15 under either instruction.|The instruction change did not improve whole-translation acceptance. This is DEV, not PAL-REF40.|
|27 September, qualified-data retraining|Fresh Gemma adapter after 247 rows were quarantined; 2,237 rows, 280 updates|Fresh paired reviewer A: 14 → 16/40 accepted; reviewer B: 16 → 17/40. Critical errors 9 → 7 for both.|Small aggregate gain with losses on some cases/works. Filtering also changed exposure and update count, so this does not isolate cleaning alone.|
|27 September, model/evidence comparison|Qualified Gemma and original Qwen3.6-27B, each with/without supplied examples|Gemma 1 → 3/15 accepted but critical errors increased. Qwen 0 → 1/15. No planned comparison passed the improvement screen.|Neither the tested assistance package nor switching to this unadapted Qwen configuration solved the problem. Qwen's possible trained performance remains unknown.|
|27 September, familiar-passage recall|Qualified Gemma on 20 selected TRAIN passages, two instruction formats|Only 12 complete pairs: 5 accepted with training instruction versus 4 with evaluation instruction, for both reviewers. One later output hit the repetition cap; 15 slots were unattempted.|Even familiar full-passage generation was weak. The partial 12-pair result is not an accuracy estimate for all 20.|
|27 September, conditional-fit diagnostic|Adapter on/off with correct/mismatched sources; 80 forward evaluations|Known-target negative log-likelihood with correct source fell 4.299 → 0.884 when the adapter was enabled.|Teacher-forced likelihood improved with original answer prefixes supplied. This is not a translation score; source mismatch penalties did not increase with adaptation.|
|27 September, latest paired training|Same qualified checkpoint; 48 further updates each, ordinary-translation control versus contextual-expression candidate|Both reviewers: 0 → 0/15 accepted. Constrained critical errors 3 → 4/9 for both. Whole critical errors 6 → 6 (A), 6 → 7 (B).|**Both improvement screens failed.** Close this recipe branch; do not promote either new adapter or add epochs automatically.|
|28 September, NLLB full adaptation|NLLB-200-distilled-1.3B, qualified2237 pairs, five epochs,700 updates; fresh blind initialized/trained/Gemma comparison|Both raters: initialized0/15, trained0/15, Gemma1/15 whole accepted. Trained whole critical5/7 versus Gemma3/4. Initialized21/24 and trained23/24 outputs complete.|No promotion. Formal screen inconclusive from one trained cap; semantic gain/safety conditions also unmet. Lower whole critical counts than initialized NLLB do not establish better translations than Gemma.|

|28 September, NLLB familiar-passage diagnostic|Same trained checkpoint;40 correct/mismatched-source reference-likelihood calls and20 first translations, zero updates|Both fresh reviewers accept2/20. All5 contextual glosses preserved; functional scopes only2/23 and4/23. All20 source mismatch penalties positive, mean3.2262 nats/token.|Source-sensitive reference fit coexists with weak free composition. Separate TRAIN diagnostic, not a DEV/PAL score or a matched Gemma comparison. The first readiness failure is preserved and its numerical repair passed. |

The historical 5/40 baseline and 15/40 trained result came from separate single-review assessments and are preserved. The later 14/40 and 16/40 are two fresh reviewers' ratings of those same old trained outputs, not additional models. Each paired reviewer assessed both the old and qualified outputs. Do not subtract historical 15 from a new reviewer's 16 or 17 and call that the matched gain.

Likewise, the latest 0/15 does not establish a fall from 40% to 0% on PAL-REF40: the cases and reviewer panels differ, and the latest variants were not admitted to a new PAL-REF run. Zero whole acceptances also does not mean every translated word was wrong.

## Latest decision after NLLB

The [completed pilot and paired review](../experiments/nllb-supervised-20260928/REPORT.md) establish feasible full adaptation but no promoted quality gain. Gemma remains the comparator. The initialized/trained comparison uses the same fresh reviewer panel, preserves all failures, and is distinct from earlier PAL-REF panels. Even making the single capped trained case acceptable would give only1/15 versus Gemma1/15, below the fixed minimum net gain of2; a cap-only repair is not sufficient.

The [completed familiar-passage diagnostic](../experiments/nllb-seen-20260928/precision-repair/REPORT.md) now answers that next question: both raters accepted2/20 despite clear source preference under supplied reference prefixes. Qualified familiar constructions frequently failed. Seek genuinely additional, independently supported whole-clause supervision from published contexts; preserve split boundaries and qualify relations before any new training. Do not repeat the old23-scope audit or failed12-anchor mixture. A source-contrastive decoder remains conditional rather than the default next spend.

No PAL-REF follow-up or laptop weight transfer is admitted. The active [Goal](../GOAL.md) retains the cumulative fundedUSD25 cap. All22 jobs were terminal at11:04:40 UTC. Billing at11:07:31 UTC showedUSD18.73 usage,USD11.66 credit andUSD6.27 cap headroom; the latest two diagnostic attempts increased displayed usageUSD0.45, not a per-job invoice. Any new paid run requires fresh checks.

## Current perspective

The qualified Gemma step280 checkpoint remains our reference model, with provisional PAL-REF acceptance 16/40 and 17/40 from the two paired reviewers. That is an experimental baseline, not a finished translator.

The strongest working hypothesis is a gap in reliable contextual meanings and composition/generalization. We see correct local words or grammatical functions alongside wrong complete propositions, participants and technical meanings. This is not proof that data alone explains every failure or that a different architecture could never help. The latest intervention tested a small 12-anchor recipe; it did not settle contextual supervision in general.

The computational pipeline and optimization have been exercised, but valid numerical execution is not semantic competence. Native Pahlavi-script reading, unknown-word decipherment and satisfactory 8 GB laptop inference remain unproved. Current evaluations primarily use scholarly transcription.

Measurement remains a material uncertainty: two AI reviewers help expose disagreements but cannot certify philology. Specialist evaluation under the existing rubric is a higher-value next source of evidence than another unmotivated training run. Independent MT research also shows that professional contextual evaluation can produce different system rankings from less specialized assessment; this is methodological support, not Pahlavi-specific validation. [Freitag et al., 2021](https://aclanthology.org/2021.tacl-1.87/).

## Earlier strategy before the NLLB pilot

1. **Preserve the qualified checkpoint and stop the failed contextual recipe.** No automatic extra epochs, mixture search or third-model sweep. A larger or different model is not selected merely because this recipe failed.
2. **Strengthen independently grounded semantic evidence.** Check attested word senses, clause meaning, participant roles, negation and uncertainty against published contexts. Do not turn DEV answers or model guesses into training labels. The already completed 23-function annotation work and four within-parent contrasts should not be redone.
3. **Use the completed annotation access evidence at its actual strength.** After explicit approval, the exact Parsig index and one returned detail both succeeded on 28 September. Independent review verified the `xrad` occurrence's identity against TRAIN context. Printed line verification, a bibliography date discrepancy and independent semantic qualification remain unresolved. One occurrence establishes availability, not an adequate new training resource. [Access evidence](../experiments/published-annotation-access-20260927/README.md).
4. **Admit another experiment only when new evidence justifies its hypothesis.** Preserve the unchanged metric and matched control, predeclare one intervention and its cost/stop rule, and keep all first attempts. Reconsider the model or learning objective if a concrete diagnosis supports it. CPT needs suitable additional source text; synthetic/preference training needs independently validated labels or rewards.
5. **Require quality before delivery.** A passing DEV candidate would face the unchanged PAL-REF regression check, followed by local quantization/8 GB quality and timing checks. Reused benchmarks are regression evidence, not new untouched confirmation.

MPCD is a relevant model for manuscript-linked corpus annotation and a Pahlavi dictionary, not an already validated translator or a verified training-data release for us. Its institutional description supports grounding linguistic claims in annotated attestations; current usable coverage and access remain separate questions. [FU Berlin MPCD description](https://www.geschkult.fu-berlin.de/en/e/iranistik/forschung/MPCD/index.html).

No new paid job is admitted. The last verified balance was USD 13.70 on 27 September; live job inventory checked 28 September at 02:53 UTC showed no active jobs. Existing funded credit is authorized strategically, with no automatic recharge or new purchase. The exact approved Parsig access scope is complete. A further research update is being prepared at the user's request; this timeline preserves the strategy at this checkpoint.

## Experiment records

- [First Gemma benchmark comparison](../experiments/palref-v1/trained-20260927/REPORT.md)
- [Qualified-data paired comparison](../experiments/palref-paired-20260927/REPORT.md)
- [Model and supplied-example comparison](../experiments/dev-assisted-qualified-20260927/REPORT.md)
- [Familiar recall](../experiments/train-recall-20260927/REPORT.md) and [conditional fit](../experiments/train-fit-20260927/REPORT.md)
- [Completed NLLB pilot and fresh paired comparison](../experiments/nllb-supervised-20260928/REPORT.md)
- [Earlier contextual result and audited decision](../experiments/contextual-supervision-20260927/REPORT.md)
- [Earlier project synthesis and exact prototype references](../plans/translation-test-strategy-20260926-fa.md)
