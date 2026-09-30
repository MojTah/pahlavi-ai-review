# Independent corrected-data outcome QA

30 September 2026. **PASS for the recovered evidence, comparison arithmetic and scoped report.** The candidate fails the frozen improvement screen. This QA pass does not promote a model or authorize further execution.

- Lead agent/request id: /root
- Critic agent/request id: /root/corrected_outcome_qa
- Critic model and reasoning effort: inherited unchanged; no override requested or applied
- Independent from lead: yes
- Critic verdict: PASS
- Evidence reviewed: corrected and previous mixed-run manifests, small recovered artifacts, launch/recovery/terminal receipts, selected training arrays, frozen evaluation contract, comparison helper and reused scorer, both frozen rating files and mappings, comparison JSON, final report and current review/state/recipe summaries
- Verification evidence: independent SHA-256 and size checks; exact selected-order and token-count reconstruction; offline output decoding and prompt-parity validation; all four comparison tests; separate recomputation from raw ratings without the aggregation helper; successful arithmetic-only report replay

## Recovery and executed exposure

The recovered corrected run binds to job `6abc15b8031314b696342162` and run `157531204582c50f2d8f73aaa76ce8ac`. Its launch, recovery and terminal job IDs agree. All 15 small manifest-listed files and the manifest pass local hash/size checks: 247,412 bytes. The saved inventory contains the expected 18 provider entries. The two adapter binaries remain absent locally; their provider sizes/commitments and server-recorded SHA-256 values agree with the saved manifest. This review did not independently fetch cloud state or rehash weight bytes.

The run records 96 completed updates, 1,536 consumed slots and 24 successful first outputs. The 1,536 unique consumed IDs exactly match the corrected manifest order. Training uses a fresh optimizer from qualified step280. The previous mixed continuation is a sibling, not its parent. Both mixed runs share training settings, initial adapter, model revision, tokenizer, evaluation prompt identities and decoding settings. The corrected reader has a different source hash; source-byte identity across all launch helpers is not claimed.

Independent sums over the actual training arrays confirm:

| Exposure | Previous mixed | Corrected mixed |
|---|---:|---:|
| Selected examples | 1,536 | 1,536 |
| Sequence tokens | 258,988 | 274,703 |
| Supervised tokens | 67,456 | 68,724 |

There are 214 changed array positions: 192 lexical, 18 historical and four documentary-to-pedagogy replacements. Eleven IDs change: four canonical remaps and seven replacements. The other 203 changed positions retain their IDs. Thus the comparison concerns the combined correction package, not dictionary cleanup alone or exposure to the full 9,973-input pool.

The terminal timestamps differ by 2,854.201 seconds, or 47 minutes 34 seconds. At the recorded rate, 48 rounded minutes give estimated compute of USD 2.000016. This is not an invoice. The training progress endpoint of 1,819.185 seconds excludes other job phases.

## Frozen review and arithmetic

The critic opened ratings only after the lead confirmed that both reviewers had completed and frozen their files. All 53 packet/source artifacts reproduced byte-for-byte. Reviewer receipts, original ratings and scored copies agree with the freeze hashes. The converter validates source/run/adapter identities, output token decoding, output hashes, rendered prompt hashes, ordering, natural endings and all first-attempt counters. No model inference was performed for these checks.

Independent calculations joined the raw ratings to the opaque mapping and counted each reviewer separately. They match every reported whole/constrained total, acceptance percentage, gained/lost case, work-level gain, critical-error change and new overconfidence transition.

| Reviewer | Retained / previous / corrected accepted, of 15 | Whole critical, of 15 | Constrained critical, of 9 | Constrained overconfidence, of 9 |
|---|---|---|---|---|
| A | 1 / 1 / 2 | 4 / 7 / 4 | 4 / 5 / 4 | 7 / 5 / 7 |
| B | 1 / 1 / 2 | 4 / 6 / 5 | 4 / 5 / 3 | 8 / 6 / 8 |

All six individual screens and all three joint screens fail. Relative to retained step280, corrected-v2 gains case009 in one work, with no lost acceptance. Relative to previous mixed96, it gains case003 in one work, again without lost acceptance. Both gains fall below the required two net acceptances across two works. Both reviewers identify new constrained overconfidence in cases001 and022 relative to previous mixed96.

The report's quoted case003 and case009 changes match the packet outputs and reviewer rationales. Case002 changes from meaning to critical error relative to step280 for both reviewers. Case017 improves in severity only for A. The report preserves that disagreement. Corrected-arm severity/uncertainty judgments differ between reviewers on cases006,013,016,017 and024, while all 15 whole-acceptance decisions agree. Within each reviewer, identical packet content receives consistent semantic ratings.

Historical reviewer counts were checked separately and were not substituted into the new matched panel. The report correctly treats the new ratings as descriptive development evidence. It does not infer quality from training loss, isolate a correction's causal effect, pool reviewers, or turn accepted passages into a percentage of correctly translated words.

## Reproduction and limits

The configured science Python completed the following read-only check with four tests passing:

```powershell
& '[USER_HOME]\.venvs\codex-science\Scripts\python.exe' -B -X utf8 -m unittest scripts.test_review_corrected -v
```

This full check requires the existing private local data/tokenizer files. The arithmetic-only Python example in [REPORT.md](REPORT.md) also ran successfully; `r.prep.CONTRACT` exists and its hash matches the frozen contract. That example requires the public packet, ratings, contract and code, without model weights or private training arrays. Arithmetic replay verifies saved judgments and does not independently certify those judgments.

Reviewed comparison JSON SHA-256: `cc85230a7150803d80a3a7b63568dd1e14e359870eea68486b0dd3729f551b7c`.
Reviewed helper SHA-256: `72dfbbe68566891ba434fd40b6b1dfd43d1de1570edf92803ed3680c26dadcc5`.
Reviewed report SHA-256: `54b99555a9b6bbf27bc324458932373e7c7ce9fe3ee89293af169db2a886c9a5`.

No remaining blocker was found for this comparison. The reusable recovery helper binds run ID and prefix but does not itself check the recovery receipt's job-ID field; that field was explicitly verified for this result and recorded in [comparison-verification.json](comparison-verification.json). Further helper hardening is not necessary to establish the current outcome.

This review is engineering and arithmetic QA with bounded reading of semantic evidence, not an independent specialist translation adjudication. It did not repeat the full corpus reconstruction, load weights, rerun training, access credentials, publish to GitHub or verify the final public snapshot. Publication and its exclusion checks remain the lead's responsibility. The exposed DEV panel and related AI reviewers do not supply fresh scientific confirmation. Retain step280; preserve the corrected package and candidate as evidence; no further paid work follows from this pass.
