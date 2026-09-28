# Qualified model: familiar-passage recall

27 September 2026. Partial first-attempt diagnostic; two independent blind reviews complete. This is seen-TRAIN recall, not a PAL-REF or DEV result. The unchanged merit contract and all eight bound benchmark/development files passed SHA verification. No new training occurred.

## Execution and recovery

The qualified Gemma step-280 adapter was tested on the frozen twenty TRAIN parents using the two existing instruction formats. The first twelve parents produced both outputs successfully. The thirteenth parent's training-format output reached the unchanged 4,096-token ceiling without EOS after668.090 seconds. It entered a repetition loop: one twelve-token window recurred499 times. This is a generation failure, not evidence that the GPU was idle. The runner stopped at this first failed attempt as declared; fifteen slots were never attempted. Nothing was retried, replaced or silently omitted.

There are **24 successful outputs, one capped error and fifteen unattempted slots**. The complete paired prefix contains twelve parents, selected by frozen TRAIN-ID order. Its truncation may depend on generation behaviour; it is not a representative random subset of the twenty parents. Both format denominators remain twenty, with semantic and execution outcomes distinguished. Any completed-pair comparison must state its twelve-pair denominator and cannot establish the result for all twenty parents.

Job `6ab8fa5d6b030d633f698f47` used one A10080. All six exported evidence files,212,777 bytes, passed provider committed-inventory, size and full SHA256 checks before shutdown. Manifest SHA256 is `cd4c606d1fc5b9db4db84faad8575cf2fa114bb910769c93f8fe9a751ead1816`. All25 saved output strings independently matched decoding of their recorded token IDs with the pinned local tokenizer. No model or adapter weights were downloaded to the laptop.

CANCELED was confirmed at11:34:41.866487UTC after verified recovery; it is deliberate shutdown of this incomplete diagnostic. The11:35:55UTC provider inventory contains fifteen jobs, all terminal. The elapsed-time calculation is **USD0.88038**. A subsequent live billing read shows **USD16.20 credit**, USD14.07 period usage and automatic recharge unset: displayed account usage increasedUSD0.92 from the prior observation. That is not a per-job invoice; rounding/billing detail remains unresolved. The old shutdown field is named `compute_upper_estimate_usd`, but this calculation is **not an upper bound on billed charges** and is retained as the original observation. The declaredUSD1.50 envelope was not approached. No purchase or recharge occurred. Evidence: `execution.json`, `recovery.json`, `shutdown.json`, `billing-after.json`, `job-inventory-after.json`, `technical-output-audit.json`.

## Independent assessment

Two new reviewers received independently shuffled, anonymous forty-slot packets. They saw source, published witness, preserved qualifications and occurrence-specific scopes, but no format/model labels, historical scores or each other's judgments. The original eight meaning dimensions and four successful-output labels remain unchanged; failures/missing outputs receive no semantic merit. Each reviewer also assessed56 local scopes separately from whole-translation quality. These are provisional AI reviews, not expert certification.

| Reviewer | Instruction | Accepted | Meaning error | Critical error | Uncertain | Capped error | Unattempted | Scheduled |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | Training | 5 | 4 | 2 | 1 | 1 | 7 | 20 |
| A | Standard evaluation | 4 | 5 | 2 | 1 | 0 | 8 | 20 |
| B | Training | 5 | 4 | 2 | 1 | 1 | 7 | 20 |
| B | Standard evaluation | 4 | 6 | 1 | 1 | 0 | 8 | 20 |

Among the twelve completed pairs, both reviewers accept five training-format translations and four evaluation-format translations: four shared acceptances and one acceptance lost under the evaluation format. This is a selected partial comparison, not a new accuracy percentage or proof of a format effect. Ratings remain separate; agreement does not make them expert truth. The full twenty-slot transitions and work breakdowns remain in `scored/summary.json`.

All five reviewed contextual glosses are preserved in both formats by both reviewers. Of nine assessable local function scopes, reviewer A records eight preserved/one contradicted in each format; reviewer B records seven/two under training and eight/one under evaluation. Fourteen further scopes per format are unassessable because of execution coverage. Correct short scopes do not imply correct whole passages. The observed full-meaning problems include “no equal” becoming “no limit”, “being afflicted” becoming “pain itself”, stealing becoming coveting, teaching becoming tasting, and altered participants, negations or exception boundaries. These are TRAIN-derived diagnoses; no held-out corrections were added to training.

The packet/scoring helper passed two focused tests and five additional independent boundary checks; see `REVIEW-PIPELINE-QA.md`. Both actual reviews passed complete schema, forty-slot/56-scope coverage, output-hash and literal-span validation, followed by deterministic score reconstruction. Reviewer A SHA256: `f757cfc91eb55ec4b5c907ea1ece8197753ccff01407c801f5a3829f6f656d3b`; B: `0bb9eeaf73d5865bb6bb1d8830790e0546490a5121268e2ccec96cab7a6b682d`. Fresh reviewer identities are `/root/recall_blind_a` and `/root/recall_blind_b`.

## Training evidence and limits

The existing qualified-training logs contain280 contiguous steps with finite loss and positive finite gradient norms, and report122,429,440 trainable parameters. Mean logged loss declines from2.7061 over the first twenty steps to0.7522 over the last twenty; the final logged loss is0.8188. This supports optimization activity, not correct translation or adequate fit on the selected passages.

The reported resumed aggregate `train_loss=0.986148` equals the sum of logged losses for steps21–280 divided by280. The actual mean over those260 logged steps is1.062006. It must not be described as an endpoint quality measure. The frozen stored2237 training rows have83,243 loss-bearing target/terminator positions; the twenty selected parents have934. Stored labels and static masking checks are not an independently recorded actual-batch loss trace. Historical training used NF4; this recall run used the pinned BF16 base. A failed recall output alone establishes neither a masking defect nor a need for more epochs.

## Next scientific decision

Keep the original partial run and fixed evaluation rules. Do not launch an automatic rerun, increase epochs, switch models or change decoding to improve the reported score. Familiar whole-passage recall remains weak in both formats, although many local distinctions survive. That does not isolate either a pipeline fault or a general grammar deficit. A grammar-only intervention is not yet established as the best next use of credit, particularly because eleven of the fifteen qualified negative-directive scopes were never assessed.

The next mechanism check is conditional target fit with zero optimizer updates: adapter on/off crossed with correct/one predetermined unpaired source, using all twenty frozen TRAIN parents and their original targets. The four-condition design and source permutation are frozen in `../train-fit-20260927/PROTOCOL.md` and `source-control.json`; implementation and paid admission remain pending. One model load serves eighty forward evaluations with no free generation. Target likelihood is not translation merit or causal proof; gold prefixes and potentially overlapping unpaired source content limit interpretation. Mixed lexical/construction supervision remains a candidate learning change; any eventual candidate requires its matched translation control and unchanged source-only DEV comparison.

The qualified function sample contains23 scopes but only15 parents/15 works. Repeating each full parent once per scope would give the long `150000053` parent42% of target characters in those repetitions. That observed clustering requires explicit parent exposure and actual supervised-token accounting before setting a mixture. No grammar-target serialization, numeric training recipe or new run is admitted here. The broader improvement goal remains active.
