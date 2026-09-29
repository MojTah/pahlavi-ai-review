# Independent audit review

Lead agent/request id: /root
Critic agent/request id: /root/final_external_judge
Critic model and reasoning effort: inherited session settings; no override
Independent from lead: yes
Critic verdict: pass with notes
Evidence reviewed: token reconstruction, audit_training_corpus.py, its tests, original pinned source helpers, corpus-audit-v1 and corpus-audit-v2 artifacts.
Verification evidence: independent byte-identical token reconstruction for all2,484 rows; fourteen corpus tests passed in0.899s; all192 current input hashes/sizes and v2 output hashes verified; exhaustive3,529,764-pair accounting and13 near-source matches; pruning independently matched3,844 brute-force fixture pairs.

The v1 checker reported59 mechanically failed rows, containing60 error instances. The critic traced every instance to historical outer-whitespace and blank-line rules missing from the checker. No training data were changed. The designated implementer reproduced the pinned historical transformations and added negative controls rejecting changed nonblank content. V1 remains preserved as superseded diagnostic evidence. V2 passed with zero mechanical failures. Exactly59 ledger rows changed only to clear those false mechanical errors; all other ledger content and all near-pair records remained unchanged.

Frozen identities:

| Artifact | SHA256 |
| --- | --- |
| scripts/audit_training_tokens.py | 199009cba490f4c39a6da288fc70b3abbf2a2bfef243ac8dec0d765423a5c2fd |
| token-reconstruction/summary.json | ed7253282527259b599f3ef25c691352736b5b616952e6cb59fb0eb3cdfb65b2 |
| token-reconstruction/rows.jsonl | 3964e97059d1511b13c48a86cbff1a004f0efdf773739beed7c67a836c3609b4 |
| scripts/audit_training_corpus.py | 9c616eae976683ce16e5428af10b3e4425aa4d72e0f8ac4e33020f5238325abc |
| tests/test_training_corpus_audit.py | 60f380d311b03f81b335b8df4e1beb57bb41675e25d34c5a9fe26e0141885748 |
| corpus-audit-v2/summary.json | b46d06e510f8299c4188585fe2f6966edb17b52a28dbebdf998b1822def86b29 |
| corpus-audit-v2/ledger.jsonl | d0fd897ad6d0b650023d31426468d4351b519a8c03077dcb2d192f3109db8baa |

These checks establish archive and token fidelity, not semantic correctness. Marker and boundary flags are review prompts, not automatic exclusions. All mechanical-ledger semantic states remain UNREVIEWED; separate hash-bound linguistic judgments and structural adjudications determine the provisional derivative.

## Independent linguistic spot check

Reviewer `/root/train_review_01` independently inspected the17 explicit-error judgments in completed packets03/04 and12 retained rows selected by ascending SHA256 of complete row IDs. It also verified schema, coverage, hashes and spans for all621 reviews. No new material issue was identified in the retained sample. This sample does not establish whole-corpus accuracy.

Retained sample IDs (each prefixed `parsig:` and suffixed `:pal>fa`):151001082,151001141,136003015,137000001,151001197,151001144,150000019,151001126,136007001,151005013,136008007,151001087.

Additional findings, all affecting rows already quarantined:

- 137001056: `dām ī ohrmazd` becomes `هرمزد را`, adding a participant mismatch beyond the recorded concern.
- 137002013: the spatial gloss `[هرمزد آفریده شدند]` introduces an unsupported reference point after river geography.
- 137002019: source `rōz aštād` versus target `روز اَرد` is a real mismatch, but the target agrees with the stated25-day duration and published English. Classify this as unresolved source/edition inconsistency, not a proven Persian calendar error.
- 150000033: the target preserves `زیانکارتر`; the added `[و بیشتر آسیب می بیند]` requires lexical adjudication. The original review's claim of reversal is too strong; retain quarantine as substantive uncertainty.

Original judgments remain preserved. These qualifications change neither retained membership nor targets. Aggregate raw review-category counts must not be described as adjudicated counts of definite translation errors. All linguistic reviewers are AI; no specialist certification exists.

## Structural reconciliation and finalization

The same independent critic passed `structural-review.jsonl`, SHA256 `5f46070fc87e39ddd66ce09b40cd0e474e5ee743150d5bc67e1574b82be01d56`: all28 nonmarker-flag IDs,22 clearances and six quarantines. It independently checked17 archived response files,65 evidence locators, both spillover line pointers and all13 heldout-source pairs. Four split-precaution exclusions are not translation-error claims. Their exposure in the old adapter remains disclosed.

Finalizer and `qualified-v1` independently passed after all eight packets were frozen. Ten tests passed in0.062s; six additional full-pipeline negative probes rejected partial/missing reviews, wrong review hash, UNREVIEWED, contradictory eligibility and missing structural coverage. Existing/authoritative output guards rejected overwrites. All217 recorded input files and every output hash were rechecked. The complete2,484-row final ledger reconciled to its source, mechanical, linguistic and structural inputs.

The derivative retains2,237 complete original row byte sequences in their original order:1,411 eligible and826 qualified. It quarantines247, including four structural overrides of linguistic eligibility. Source, target, prompt and token mutations: zero. `CLEAR_FLAG` cannot remove a separate linguistic quarantine, checked on133000004,545000005 and503000003.

| Final artifact | SHA256 |
| --- | --- |
| scripts/finalize_training_audit.py | fa0c21abb38da10a7d42882b0a082b8d1c4011b6b8940e2bb3b92a504a41e00a |
| tests/test_training_audit_finalizer.py | e5a47f890f2a255014ad5106427ce4017f8fbb7e9855e8ef2d20213963c2a2d8 |
| qualified-v1/train.jsonl | 15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc |
| qualified-v1/final-ledger.jsonl | d79af2e64fbb92954c8b8d0ed9cb7a34e7e7d24d4c22ea9c22f1da6d569a8e77 |
| qualified-v1/summary.json | fc7131ac6600b1acda4351220d5458bf60d5a866b8f17002231eb6797996ebba |
| qualified-v1/manifest.json | a5031b6f2abe81b103fb0c863602a7441776efc5b4dccf11b2e1dc6a2050ec15 |

Verdict: PASS for provisional AI-qualified data preparation. No specialist certification or paid-run admission is implied. Root owns any subsequent launch, with separate readiness, budget and identity verification.
