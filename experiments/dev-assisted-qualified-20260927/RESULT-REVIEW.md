# Independent DEV96 result audit

27 September 2026. **PASS for arithmetic, provenance and the report's bounded quantitative interpretation. All four improvement comparisons fail their frozen screens.** This audit adds no semantic ratings, changes no denominator, and provides no model promotion or paid-run authorization.

## Independent reconstruction

I executed two independent, standard-library Python checks with `resources/local/hf-client-venv/Scripts/python.exe -B -X utf8`, using in-memory calculations rather than the production scorer's aggregation functions. Both exited zero with PASS. A final independent case-ID/transition check also exited zero. No cloud calls, credentials, model execution, package installation or additional file output was involved.

The checks reconstructed every condition, per-work count, constrained severity and uncertainty count, paired transition, decision-rule component and reviewer-agreement field from the frozen mappings and reviews. All matched `scored-comparison/comparison.json`. The original reviews and their scored copies retain their exact frozen hashes. Adverse evidence spans occur literally in the corresponding outputs; this is a mechanical check, not endorsement of the interpretation of those spans.

Whole-translation counts below are accepted / meaning error / critical error / uncertain, always out of **15**. Constrained counts are none / meaning error / critical error / uncertain, separately out of **9**.

| Condition | A whole /15 | B whole /15 | A constrained /9 | B constrained /9 | Overconfidence A/B /9 |
| --- | --- | --- | --- | --- | --- |
| Gemma280 plain | 1 / 10 / 3 / 1 | 1 / 10 / 4 / 0 | 1 / 3 / 4 / 1 | 1 / 3 / 4 / 1 | 8 / 6 |
| Gemma280 assisted | 3 / 6 / 6 / 0 | 3 / 5 / 5 / 2 | 1 / 1 / 6 / 1 | 1 / 2 / 5 / 1 | 6 / 6 |
| Qwen3.6-27B plain | 0 / 9 / 6 / 0 | 0 / 9 / 6 / 0 | 0 / 3 / 6 / 0 | 0 / 2 / 7 / 0 | 6 / 7 |
| Qwen3.6-27B assisted | 1 / 8 / 6 / 0 | 1 / 8 / 6 / 0 | 0 / 3 / 5 / 1 | 0 / 4 / 5 / 0 | 7 / 7 |

There are 96 successful first attempts, 24 per condition; zero errors, timeouts, abstentions, caps or unattempted cases. Thus the comparisons are fully assessed, rather than inconclusive because of missing execution. The whole-case work denominators are 4, 5, 4 and 2. Accepted whole cases are confined to works103 and112. A/B agree on acceptance for all 60 whole-condition records, but broader judgment/severity/handling disagreements occur on 4, 4, 2 and 2 records respectively across the four 24-record conditions. Acceptance agreement is not complete semantic agreement or independent human validation.

## Why each screen fails

Each reviewer is kept separate. The table describes changes from the first condition to the second. There is no accepted-to-critical transition in any contrast.

| Matched contrast | Acceptance gain/loss/net, both reviewers | Other relevant changes A / B | Frozen screen outcome |
| --- | --- | --- | --- |
| Gemma plain to assisted | 2 / 0 / +2; gains in two works | Whole critical +3 / +1; constrained critical +2 / +1; newly overconfident 0 / 1 | A and B fail the critical-error safeguards; B also fails the new-overconfidence safeguard. |
| Qwen plain to assisted | 1 / 0 / +1; gain in one work | Whole critical 0 / 0; constrained critical -1 / -2; newly overconfident 2 / 0 | Both fail the minimum net gain and two-work requirements; A also fails new overconfidence. |
| Gemma plain to Qwen plain | 0 / 1 / -1; no gain work | Whole critical +3 / +2; constrained critical +2 / +3; newly overconfident 0 / 1 | Both fail gain/work and critical-error requirements; B also fails new overconfidence. |
| Gemma assisted to Qwen assisted | 0 / 2 / -2; no gain work | Whole critical 0 / +1; constrained critical -1 / 0; newly overconfident 1 / 2 | Both fail gain/work and new-overconfidence requirements; B also fails whole critical errors. |

Direct case reconstruction verifies the report's gains002/009 for Gemma assistance, gain002 for Qwen assistance, and Qwen's acceptance losses003 or003/009 against matched Gemma. The intersection of reviewers' newly critical Gemma-assistance cases is004/008/018;004 and018 are constrained. Both flag newly critical Qwen-assistance cases013/015 despite unchanged whole critical totals. The reported new-overconfidence identifiers also match the frozen ratings. These are reconstructions of existing labels, not new linguistic judgments.

The report appropriately treats the best observed acceptance, 3/15, alongside its increased critical errors. It separates DEV from PAL-REF, declines pooling, identifies adaptation/decoding differences, and avoids causal architecture, training-regime, statistical-significance or deployment claims. The new seven-case linguistic diagnosis is explicitly distinct from scoring; I have not independently certified its semantic witness interpretations. No such diagnosis changes the audited ratings or screen arithmetic.

## Identity, coverage and blinding evidence

All eight contract-bound source/metric files match their pinned hashes, including the unchanged PAL-REF protocol/scorer and DEV input/reference/assessment/clarification files. Each model has 48 raw predictions in the exact recorded schedule with sequences1–48, all24 source cases, identical literal cross-family task messages, and internally reconstructed run identity. Output token-list lengths, native EOS termination, finite bounded elapsed times, no cap hits and successful canaries agree with the raw records.

The private mapping has 192 unique opaque review IDs. Each reviewer packet contains exactly96 distinct records; the reviewers' ID sets are disjoint. Each mapped record matches its source, frozen reference fields, assessment restriction, work, raw output bytes/hash and execution status. Both reviewers cover the complete four-condition matrix. The sanitized packets and private mapping remain distinct. Fresh-context reviewer creation is the lead's execution record; packet integrity and disjoint IDs are directly verified here, not a claim that AI reviewers lack shared biases.

| Artifact | Verified SHA256 |
| --- | --- |
| Uniform evaluation contract | `4165e8150f291c2cd6077d2daee86513ad08e1851acbfc3e83169bc40263f8c2` |
| Packet provenance | `88b2bda7e0a6fe54604ef8feed6b624ae1c439fe83b1829ef981546a54b8f965` |
| Private mapping | `310c1ebbdcfad7bad9ea2c22ad3807f2010c3efa53e3850f336da125f4957f0b` |
| Packet A | `08dbfc124a0ab3a761b216c850d3b3e0b6c170ee80c6676283c425447bedeff3` |
| Packet B | `75a0e869e28d7f1aef2f3c4503e2d3b31787b211dc52d8caa6025d9e0f920bad` |
| Review A | `4e89104f4f26e0f40010add2cf0e04f1f8d219f19a8a22475ad5baf5abc4f2e6` |
| Review B | `55ff464d3d192ab5ea56637d044a19dcb2f96d0db33a6002f7e46ff9f60e413f` |
| Review freeze | `65d120c3ac0d7615fcf3d7bfd194aaa3dfd98ef4f609ef6dab3cc8a2fe20332b` |
| Scored comparison | `f3c2f75d021c188cab36820d1bb683b9832d95f4c32e174e0c4ac7049ae81d2e` |
| Production scorer | `89ecf3fb0f521df833b90966fb35145ef22e10ab72a9aa7026d3272c1e68798c` |
| Execution result | `9956f9c681343b25ad18687478e114d5e29db18fb7e3cca5f288926bb873b5db` |
| REPORT.md, including bounded diagnosis paragraph | `e07c80c5c35bfe64ab8f2485c67b324dfbc2589703ac94a735f4be96224ec9f6` |

## Execution, recovery and cost

The second direct check compared saved specs, admissions, raw controller events, persisted manifests and recovered files. Both controllers recorded exactly one submission, the admitted launch commit `0b773cee14a4c491f13d3a511bccac1db5bc9fc4`, verified inventory before cancellation, and confirmed terminal CANCELED with no automatic continuation. The event records copied into `execution-result.json` occur exactly in the original logs. Every declared small file's byte size and SHA256 matches its manifest: six Gemma files plus five Qwen files, totaling682,923 bytes. This is local evidence of those historical provider responses; I did not perform a live account query.

| Family | Job ID | Verified inventory UTC | Confirmed CANCELED UTC | Recorded compute estimate |
| --- | --- | --- | --- | ---: |
| Gemma | `6ab8dfdc52d0dbd7f1d9b0f3` | 09:36:59.022182 | 09:37:11.650775 | USD0.697174 |
| Qwen | `6ab8dfed6b030d633f6988a4` | 09:34:42.248904 | 09:34:54.509706 | USD0.589664 |

The pinned rate is41,667 microUSD/minute. Both elapsed intervals remain below their55-minute native limits. Their estimates agree with elapsed-time arithmetic within recorded rounding and sum to **USD1.286838**. This is a conservative compute estimate, not a finalized invoice. The two55-minute reservations totalUSD4.58337 before theUSD0.75 allowance. The updated execution record's USD17.12 credit, USD13.15 period usage and unset auto-recharge are the lead's billing-UI observation by09:54:59UTC; they were not independently observed live by this critic. The report correctly avoids forcing asynchronous balance/usage fields into an exact invoice reconciliation.

Manifest SHA256 values: Gemma `fef72c7e3f34319eb2380d7abda5ba0d531627d1b5660ba2560db5690223970c`; Qwen `491689196b7a24aa652c890727d6d00c46b1f5d4b62f91130af15e60f363b140`. Original controller event SHA256 values: Gemma `3c67908c468ae5a06283faa83e06f2afea52fb8cfd0bd0b50a20b8f5965efe27`; Qwen `1f0169732738a0289d1117372dc19ac46ad531710e7b6ddbdee1c708c12c9602`.

No blocker was found in the audited arithmetic, hash chain, coverage or report interpretation. The scientific limits remain: provisional AI judgments, uncertain references, repeatedly inspected DEV from only four works, unequal adaptation/decoding across model families, and no repeated-seed estimate. Local8GB fit, quantized quality and latency are untested. This audit certifies none of those boundaries and performs no new semantic assessment.

## AutoCode Critic record

- Mode: Classic + Critic.
- Lead agent/request id: /root
- Critic agent/request id: /root/final_external_judge
- Critic model and reasoning effort: inherited session settings, no override
- Independent from lead: yes
- Critic verdict: pass
- Evidence reviewed: Frozen contract and eight bound source files; raw runs/predictions; both packets/reviews; private mapping/provenance; comparison and review freeze; saved admissions/specs/controller events/manifests and all11 recovered small files; execution result and REPORT.md at the hashes above.
- Verification evidence: Two independent standard-library checks exited0/PASS, reconstructing all counts/screens and artifact/execution provenance without production aggregation calls; final direct case-ID/transition check exited0 and agreed with report; no semantic re-rating or cloud calls. AutoCode gate validation recorded below.

The pass is scoped to the outcome evidence audit. All four model-improvement screens remain false, and no deployment, new model trial or further paid training is approved by this review.

Validation: `validate-autocode-gate.ps1 -Mode Critic -Path experiments/dev-assisted-qualified-20260927/RESULT-REVIEW.md` exited0: `AutoCode Critic gate passed`.
