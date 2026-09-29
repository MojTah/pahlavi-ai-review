# Independent recovery and comparison audit

Reviewer: `/root/mixed_launch_review`. Date: 2026-09-29. Scope: execution/recovery integrity, blind-packet conversion, and score arithmetic; no semantic rerating.

**PASS for recovery, blind-packet integrity, frozen review provenance, independent score arithmetic and report consistency. Both reviewers' improvement screens FAIL.** The audit verifies what the ratings say; it does not independently rerate their philological judgments.

The critic independently rehashed all 15 recovered small files plus the manifest (236,759 bytes total). The manifest agrees with the provider log's `ready_to_persist` receipt and the saved provider inventory's complete filename/size set. No weights were downloaded or opened; weight integrity evidence remains server SHA256 plus provider committed metadata. This audit made no network call.

Training receipts show exactly 96 updates, 1,536 final slots, and the frozen ordered IDs. The measured training duration is 1,852.139958 seconds. The step-20 numerical/update/admission checks passed. Intermediate `consumed_slots` includes a prefetched row; it does not imply 17 trained examples per update.

All 24 mixed outputs and 24 retained step-280 plain outputs completed successfully without caps, retries or errors. Casewise source hashes, source identities, input token counts and rendered prompt hashes match exactly. Base-file identities, initial step-280 adapter lineage, decoding seed/settings and input set also match. All outputs differ bytewise; that observation alone says nothing about quality.

The critic replayed all 30 prepared files byte-for-byte, then independently reconstructed both seeded orders, opaque IDs and all 96 packet records' source/output/reference/constraint/mapping fields. Each reviewer receives 24 old and 24 mixed outputs, retaining 15 whole and nine constrained cases per condition. The packet schema contains no model or condition identity. Two independent invocations of reviewers are owned by the root; this audit does not certify human-level philological expertise.

The critic independently ran `python -B -X utf8 -m unittest scripts.test_review_mixed -v`: two tests passed, exit 0, 3.207 seconds. They exercise actual recovered artifacts, source/output/prompt/adapter/attempt/order/step/recovery tampering, separate-rater decisions, incomplete comparison handling, and fixed denominators. Synthetic ratings remain test data in memory and were not written as review evidence.

| Evidence | SHA256 |
|---|---|
| Recovered manifest | `795d337284175325eaf18f5878bd89642d0c3ea0bf9720c34b678a9211a6de13` |
| Mixed predictions | `f2ce560bf9f239f0ded0802c2e67574630bb24cb78773a5b2227ce80c37a9e0a` |
| `scripts/review_mixed.py` | `3df24a1b32c59f18060b186ba1eb1c3218c7b0155606ea8b38e9363f45bccb76` |
| Packet provenance | `fc5fb3df9ac345ae08bee6a08fd3ddbb4cd8726a86a3706a772f3abdd16b473c` |
| Reviewer A packet | `aa9bbb3cf08285ecba588c923da287f5bcf0f7a88cee9dfa9743f4834ff21833` |
| Reviewer B packet | `ac0965637a7d36b7e5280d3d5df9845acc4f032f6190b25707c3839b1195120c` |

## Frozen reviews and independent arithmetic

Both 48-record review files match their reviewer receipts, scored copies and freeze hashes. Their IDs cover the corresponding packets exactly; all output hashes, quoted spans and mapping joins match. Root receipts identify distinct fresh-context agents with identities hidden until both reviews completed. This is provenance evidence for separate AI reviews, not specialist certification.

The critic independently recomputed every condition and per-work counter, category count, percentage, paired case, transition and all eight screen checks directly from raw ratings and private mappings, without calling the aggregation helper. All match `scored/comparison.json`.

| Reviewer | Accepted old/new, out of 15 | Whole critical old/new, out of 15 | Constrained critical old/new, out of 9 | Screen |
|---|---:|---:|---:|---|
| A | 1 / 1 | 4 / 6 | 3 / 4 | FAIL |
| B | 1 / 1 | 3 / 6 | 4 / 5 | FAIL |

Both identify newly accepted 009 and lost 003, an accepted-to-critical regression: net acceptance change zero and gains in one work. Both show increased whole and constrained critical counts. A additionally records new constrained overconfidence on 018; B does not. Overall overconfidence falls, but that does not remove A's case-level finding.

The reviewers agree on acceptance status for all 15 whole cases under both models. Exact whole-judgment agreement is 13/15 for the previous model and 12/15 for the candidate; constrained severity agreement is 7/9 and 8/9 respectively. Disagreements remain separate and unadjudicated.

`REPORT.md` tables, quoted outputs and attributed reasons for 003/009 match the source records. Its 1,152 historical plus 384 auxiliary exposure, 96 updates, 1,852.14-second training duration, limited development-panel interpretation and decision not to promote the candidate are supported. The report does not claim full-pool learning or a causal explanation for the regression. The recommendation for a further training-side audit is a proposal, not evidence that such an audit or another run occurred.

| Final evidence | SHA256 |
|---|---|
| Reviewer A ratings | `4cc118c247956bd42fb39651bbd01648392e0f1af6f48b8a3a34b65776251843` |
| Reviewer B ratings | `3b0d36eb13f8a0d64a05e9d903a5e1c454267e01106cb26f15a11f253f0c1554` |
| Reviewer receipts | `3cd3f31da5a2f784362451ff9b2d373b82ff84b27780dcaf0562bceb0d4662e7` |
| `scored/comparison.json` | `b18cd113993e23471bb5781f3d5e9a604082ea7ce943da9b970c647ec07cefd4` |

Machine-readable independent audit receipts are in `resources/local/mixed-comparison-audit/`. No ratings, implementation or frozen input was changed by this critic. The fixed exposed DEV comparison cannot isolate auxiliary data effects from further training, establish population accuracy, or authorize automatic promotion.
