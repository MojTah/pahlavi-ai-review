# Qualified-data retraining: paired fixed-test comparison

The filtered-data run gives a small descriptive improvement on the unchanged forty-case PAL-REF test, with material regressions. It is not ready for laptop delivery. Two fresh blinded AI reviewers independently assessed every output from both models; their separate results agree on the direction of the aggregate change, not on every translation.

| Reviewer | Previous accepted | Qualified accepted | Change | Previous critical | Qualified critical |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | 14/40 (35%) | 16/40 (40%) | +5 percentage points | 9/40 (22.5%) | 7/40 (17.5%) |
| B | 16/40 (40%) | 17/40 (42.5%) | +2.5 percentage points | 9/40 (22.5%) | 7/40 (17.5%) |

Reviewer A finds five newly accepted translations and three lost acceptances. Reviewer B finds six newly accepted and five lost acceptances. Both conditions produced all forty outputs, with no abstentions, timeouts, execution failures or token-cap hits. Complete output is not correct translation.

| Reviewer and condition | Meaning errors | Uncertain | Newly accepted | Lost acceptance |
| --- | ---: | ---: | ---: | ---: |
| A previous | 14 | 3 | — | — |
| A qualified | 16 | 1 | 5 | 3 |
| B previous | 14 | 1 | — | — |
| B qualified | 16 | 0 | 6 | 5 |

The archived original-model result remains **5/40**, and the archived first-trained result remains **15/40**. Those were separate single-AI reviews. Do not subtract the historical 15 from a new reviewer's qualified score and call that the controlled gain. The paired comparisons above use the same reviewer for old and new. The fresh old-model ratings of14 and16 illustrate reviewer variability; no averaged or invented consensus score replaces any record.

## Uneven changes across works

Each cell is accepted count/total (percentage). The cases represent five works, not the entire Pahlavi language.

| Work | A previous | A qualified | B previous | B qualified |
| --- | ---: | ---: | ---: | ---: |
| parsig:104 | 3/8 (37.5%) | 1/8 (12.5%) | 3/8 (37.5%) | 2/8 (25%) |
| parsig:110 | 1/4 (25%) | 0/4 (0%) | 2/4 (50%) | 0/4 (0%) |
| parsig:116 | 5/10 (50%) | 6/10 (60%) | 5/10 (50%) | 6/10 (60%) |
| parsig:130 | 3/10 (30%) | 6/10 (60%) | 3/10 (30%) | 6/10 (60%) |
| parsig:132 | 2/8 (25%) | 3/8 (37.5%) | 3/8 (37.5%) | 3/8 (37.5%) |

Both reviewers count critical errors rising from1 to3 in work104 and falling from4 to1 in work132; work116 falls from1 to0, work130 stays3, and work110 stays0. The aggregate reduction therefore does not establish a uniform reduction in serious errors. Lexical errors and omissions remain widespread; overlapping category failures do not consistently decrease. Keep both adapters and their evidence.

The two reviewers agree on the complete judgment in36/40 previous outputs and37/40 qualified outputs. All seven disagreements concern acceptance versus an adverse/uncertain label; acceptance agreement has the same counts. Full disagreement identities and paired transitions remain in [comparison.json](scored/comparison.json). No ratings were revised after decoding identities. Agreement between two agents from the same AI family is not independent specialist certification.

## What changed, and what stayed fixed

The same pinned Gemma4 31B base, NF4/BF16 LoRA recipe, learning rate, seed and two epochs were used. The previous run used2,484 rows and312 updates. The new run started a fresh adapter from the base and used2,237 retained rows and280 updates. All2,484 original rows received an individual AI disposition;247 were quarantined. Retained examples kept their exact source, target, prompt, token bytes and order. This was filtering, not rewriting translations. Coverage of review does not certify100% linguistic correctness;826 retained examples keep documented qualifications.

Filtering also changes token exposure, update count and the learning-rate schedule. This comparison tests that combined condition; it does **not** isolate a causal effect of cleaning or of an individual excluded example. No seed replication was run.

All21 frozen inference-comparison fields and all40 rendered input-token counts match the previous evaluation. The unchanged benchmark, references, rubric, denominator40, evaluator, prompt, greedy decoding, fresh context and generation caps were reused. No output was regenerated for selection. Both reviewers received eighty exact anonymous outputs in independently shuffled orders, with source, English/Persian references and frozen meaning checks. The [protocol](../retrain-qualified-20260927/COMPARISON-PROTOCOL.md) was frozen before new predictions.

This is a small descriptive regression comparison. The benchmark was evaluated previously and is no longer a fresh unseen confirmation set. Known source-formula overlap precautions were applied; semantic parallels and foundation-model exposure remain unexcluded. Future development must use DEV, not individual PAL-REF failures. Input here is scholarly Latin transcription; native-script reading, unknown-word decipherment, general population accuracy and local8GB inference are unproved.

## Reproduction and preserved execution

Four separate [scoring directories](scored/) preserve exact predictions, decoded copies of frozen reviews, genuine runtime metadata and actual reviewer identities. Each `score.json` is generated by the unchanged `cloud_pilot/score_palref_fa.py`. The minimal [comparison script](../../scripts/score_blind_palref_comparison.py) checks coverage, identities and exact adverse spans, then calls that scorer; it does not assign meanings. Its `--check` rejects duplicate/missing reviews, wrong output hashes, extra fields and invented spans. Reviewer B removed an extra status field caused by an ambiguous brief before freezing; judgments were not changed by that schema correction.

- Reviewer A frozen SHA256: `1464fc91fb203cc4993140955b98642790ace22c1d446757259a24b4801e3c37`.
- Reviewer B frozen SHA256: `8ee1205ee267c968c24090c9e5dd53f236eead2f1db87ff9509485831ef593e6`.
- New predictions SHA256: `a38cd914fee26fecf7757380b5c4798ea66a7b78298659222f5499ef88481a30`.
- New adapter cloud SHA256: `a51bcd02c6077bcec400c1f342ede3205f260e419ed4f9e3ad0f4338a7e4afdf`.

Job `6ab8a8c66b030d633f698091` completed280/280 updates and saved29 cloud artifacts. After persistence verification it was deliberately stopped; CANCELED was confirmed at2026-09-27T07:02:22.518460Z. All23 selected small records,129,496 bytes, passed complete local SHA recovery. No model weights or optimizer were downloaded. Conservative cumulative compute estimate is **USD11.7482 of25**, not a finalized invoice or current credit balance. Training loss0.9861 is not a quality score. [Independent technical audit](../retrain-qualified-20260927/CONTINUATION-RESULT-AUDIT.md) records checks and limitations.

The next decision is a broader strategy review using these results and existing research. This report admits no automatic retraining, model download or next paid job.
