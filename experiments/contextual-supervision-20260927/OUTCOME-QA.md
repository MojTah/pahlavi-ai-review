# Independent outcome QA

27 September 2026. **PASS for evidence integrity, arithmetic and the final interpretation. The candidate fails the predeclared improvement screen.** No unresolved defect was found in this outcome audit. QA did not change or semantically re-rate either review.

## Execution and provenance

The independent `outcome-qa-evidence/runtime_audit.py` completed successfully using project Python and local records only. It verified all18 exported small files,278467bytes, against manifest SHA256/size and the exact committed provider inventory. The5689-byte manifest is separately bound to recovery proof; the inventory contains21 objects including two cloud-only adapter weight files. The saved launch/spec, compressed/decoded command hashes, source/helper/review pins, package, step280 origin and recovered records agree for job `6ab9237d52d0dbd7f1d9c66b`, run `555064e068b54aacafee67e37375ec78`.

Both arms completed48 updates and768 exact common ordered slots. Their initial adapter, initial RNG and training-start RNG hashes match; recorded optimizer states were empty and schedulers began at zero. Both final adapter hashes differ and each is consistently bound through training, top-level metadata, evaluation and export records. The actual Linux/A100 NF4 canary passed with zero updates, finite native/manual loss agreement, BF16 autocast and gradient checkpointing; the BF16 evaluation prefill also passed. These are recovered server execution records, not a new local GPU test. Weight bytes remain on the cloud: their SHA values come from the server manifest, while committed provider size/Xet evidence is separately recorded.

All48 scheduled predictions are unique, ordered successful first attempts,24 per arm, with no active or unattempted output. Source hashes, arm/adapter identity, output hashes/counts/EOS and24 original plain-prompt token identities match. The frozen greedy/seed42/4096-token/1200-second policy remains bound. The actual converter had already checked token decoding; this audit did not repeat its slow per-token tokenizer-length loop. The fixed uniform contract `4165e8150f291c2cd6077d2daee86513ad08e1851acbfc3e83169bc40263f8c2` and all eight source bindings are unchanged.

Recovery completed14:59:34UTC, before recorded terminal CANCELED14:59:55.992UTC. The subsequent account inventory has18 distinct terminal jobs and none active. One submission is recorded for this run. The earlier pre-Python transport failure remains a separate preserved attempt, with no generated scientific outputs.

## Independent score reconstruction

After both reviews were frozen, `outcome-qa-evidence/score_audit.py` validated all96 ratings against the exact packets, raw predictions and references: schema, disjoint opaque IDs, source/assessment mapping, output hashes, category consistency and exact adverse spans. Both original reviews are byte-identical to their scored copies and match the pre-unblinding receipts. The script imports no scoring helper; it independently reconstructs condition counts, per-work counts, every paired transition, screen check and reviewer disagreement. Its full structures exactly equal the frozen converter result.

| Fixed measure, control → candidate | Reviewer A | Reviewer B |
|---|---:|---:|
|Whole accepted /15|0 → 0|0 → 0|
|Whole meaning errors /15|9 → 9|8 → 7|
|Whole critical errors /15|6 → 6|6 → 7|
|Whole uncertain /15|0 → 0|1 → 1|
|Constrained critical /9|3 → 4|3 → 4|
|Constrained meaning errors /9|6 → 4|6 → 4|
|Constrained supported severity none /9|0 → 1|0 → 1|
|Constrained overconfidence /9|5 → 4|5 → 3|

All execution-failure counts are zero. Denominators remain15 and9 per arm; there is no pooled whole/constrained or reviewer score. Both screens fail zero net accepted gain, zero works with new acceptance and the increase in constrained critical errors. B also fails the whole-critical-count check. Neither panel has accepted→critical transitions or new constrained overconfidence. Judgment/severity/unknown-handling disagreement occurs on5 control and6 candidate cases out of24; these are not category-level agreement statistics or adjudications.

## Interpretation and cost

The final REPORT correctly stops this recipe, with no promotion, extra epochs, mixture sweep, conditional PAL40 run or currently admitted paid successor. Zero accepted cases is not proof that every word is wrong, equivalence of the arms, or impossibility of future progress. The result is descriptive on development-exposed cases under two provisional AI panels, without specialist adjudication, significance or a causal mechanism claim. Different historical panels are not a matched comparison. Task wording, target length and token weighting differed by design; training losses are not translation-quality measurements.

The three illustrative summaries match the frozen outputs and existing reviewer rationales:001 is a constrained command-expression improvement for both panels;014 introduces the thousand-sins expression and both classify the candidate as critical, with control severity disagreement;022 changes the supported actions to house-building/planting and both classify that candidate as critical. This checks the report's fidelity to frozen evidence, not a new semantic judgment or new training label. The report preserves the unresolved source qualifications and acknowledges that auxiliary-task mastery was not measured.

The saved billing observations independently recompute toUSD15.78→13.70 credit andUSD14.53→16.61 usage: -USD2.08/+USD2.08 account deltas, with automatic recharge unset. Observed server-start to terminal confirmation spans2954.219567seconds; rate arithmetic givesUSD2.0515577783. Neither this arithmetic nor the account delta is an exact per-job invoice or billed-charge upper bound. TheUSD3.625025 reservation remains a planning value. No model weights were transferred locally in this recovery, and QA made no cloud, credential, purchase, inference or launch calls.

## Frozen evidence

| Artifact | SHA256 |
|---|---|
|REPORT.md|`b3859a251781a4da3b76754a9ee9b1ec7426e1813a97a2768f6aa46283aa1102`|
|scored-comparison/comparison.json|`988bcec7d0202f5f94b3c7a3a2d11b6fa6e5ba2e8b92ce09cc90f68751b6b888`|
|Reviewer A original review|`5980d8f7aeb912518103ddda99f28ee6819b6bcf9df772463906e0dc835cbfdd`|
|Reviewer B original review|`6e3f08c0c5cb2d0c0631421be0fa4a0bb5651e7928d86a35bc7644e489760578`|
|outcome-qa-evidence/runtime-result.json|`01e9bd00a73ca3b5912c70a85092bfe9086483dd43fe01d97a97e4c0ff60496b`|
|outcome-qa-evidence/score-result.json|`ec26e3c92a2c5de9f0b0844c03c6e8e88bc8ca3f5c05a282b320a7d4c9f4c1ce`|
|outcome-qa-evidence/score-parity.json|`c46ec98822c6cd85b1c8cd097bf540e5832fbbbf473be966861108c68b13ff5e`|

The runtime result includes individual launch/recovery/training/evaluation/terminal/billing hashes. Reproduction uses the two adjacent audit scripts with project Python, `-B -X utf8`; they read existing evidence and write only this isolated evidence folder.

- Lead agent/request id: /root
- Critic agent/request id: /root/final_external_judge
- Critic model and reasoning effort: inherited session settings, no override
- Independent from lead: yes
- Critic verdict: pass
- Evidence reviewed: Exact recovered artifacts, launch/spec/recovery/provider inventory records, frozen packets and completed reviews, uniform contract, scored comparison, terminal/billing records and final REPORT.md.
- Verification evidence: Independent runtime/byte/provenance audit PASS; all96 review records validated; independently reconstructed counts, work reports, transitions, screens and disagreements exactly match the frozen scorer; review hashes unchanged; report illustrations and limits checked without re-rating. No new GPU, cloud, network, credential or model-weight use.
