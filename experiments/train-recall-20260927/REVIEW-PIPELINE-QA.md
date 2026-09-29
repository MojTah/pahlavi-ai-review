# Independent TRAIN-recall review-pipeline QA

27 September 2026. **PASS for local packet preparation and descriptive scoring at the frozen identities below.** No blocking defect found. This review used only synthetic predictions/ratings and frozen TRAIN materials; it did not inspect recovered model outputs, produce semantic ratings or perform cloud actions.

## Executed verification

- Both focused tests in `tests/test_train_recall_review.py` passed independently in **0.290 seconds**, using project HF-client Python with `-B -X utf8`. The tests exercise exact frozen material, synthetic prepare/score round trip, blinding, fresh-output refusal, partial-run placeholders and fixed denominators, and corrupted run/review rejection.
- An additional independent in-memory check passed five boundaries: zero recovered outputs retain40 slots and20 unattempted cases per format; a fsynced prediction with stale run counters remains a recovered first attempt with disclosed incomplete state; deliberately distinct synthetic A/B and training/evaluation labels produce the correct separate condition/work counts and20 matched transitions; acceptance with all categories marked not-applicable is rejected; a changed local-reference pin is rejected.
- The synthetic arithmetic check returned A's20 `accepted -> critical_error` transitions and B's20 `uncertain -> accepted` transitions exactly, without pooling. This deliberately assigned test labels to synthetic strings, not judgments on any model translation.

The test module's hard-coded scratch root was redirected in-process beneath `resources/local/train-recall-review-tmp/packet-tests/`. Frozen material was loaded from the real project before that redirection. All test files remain inside the allowed scratch tree; no ACL edits, model downloads, installation or source edits occurred.

## Source binding and scope enrichment

The loader checks the exact20-source input hash, qualified TRAIN membership, local-reference hash, token audit and both separate qualification decisions. The latter bind the lexical, directive and contrast proposal files. All28 requested annotations must match an accepted decision and their exact parent. Local references retain the original published Persian, source text, ledger qualification and source/target hashes.

Lexical scope descriptions come from the accepted occurrence's verbatim publisher gloss and citation. Function scopes come from the accepted exact source/Persian ranges and preserve their limitations, including the minimal non-exhaustive scope. Withheld or unaccepted annotations do not become review targets. Each of the28 scopes appears once per format: **56 diagnostic scope checks per reviewer**, not56 translations or independent merit votes. Their preserved/contradicted/omitted/unassessable counts are explicitly separate from translation merit.

The loader does not introduce DEV/TEST answers, repaired sources, new glosses or generated reference translations. Published witnesses and derived annotations retain provisional, non-expert status. The helper imports the existing eight categories, four successful-output meaning labels and validation vocabulary; their current source hashes are recorded below.

## Blinding and fixed accounting

Each reviewer receives a separately shuffled40-slot packet. Review IDs are unique and disjoint across reviewers; each exposed scope also gets a separate opaque ID. Public records have only `review_id`, source text, references, scopes, execution status, output text and output hash. Condition/model identity, TRAIN parent IDs, original annotation IDs, schedules, historical outputs/scores and reviewer mappings remain in `lead-only`. Full source citations remain visible as linguistic evidence; anonymity here concerns experimental identity, not concealment of the cited work itself.

Instructions require a fresh independent context, prohibit inspecting the other reviewer/history/private mapping, permit supported paraphrases, preserve uncertainties and optional editorial glosses, and distinguish whole meaning from local diagnostic scopes. Mechanical packet separation cannot prove that reviewers actually obeyed those contextual restrictions; the lead must use fresh reviewer contexts and preserve their files before unblinding.

There are always20 parent slots per format per reviewer, including errors, timeouts, abstentions, interrupted attempts and unattempted cases. These execution outcomes receive `not_assessable`, not a fifth meaning-quality label or a pass. Missing slots cannot shrink the denominator. Each work's denominator sums to20 per format; each reviewer has20 parent-paired transitions. No score is pooled across reviewers or mixed into PAL-REF/DEV. No promotion, significance or improvement screen is introduced.

Acceptance requires positive assessment of lexical meaning, omissions, unsupported additions and source uncertainty, no failed/uncertain categories and no supported-span error. Adverse successful-output judgments need a category and an exact nonempty output substring. Every local scope must receive exactly one diagnostic finding; non-unassessable findings require an exact output span. Failed execution cannot receive local merit. These are integrity constraints, not proof that an eventual linguistic judgment is correct.

## Run/recovery validation and limits

The parser verifies the frozen runner/model/adapter/settings, token audit and helper policy; reconstructs the immutable run identity; checks the full40-slot schedule and literal messages; checks all input token hashes; and validates source/parent/sequence identities, output-token hashes, stopping metadata and first-attempt prefix/counters. Complete runs must satisfy complete40-attempt accounting. Partial runs retain explicit completed/recorded/active/unattempted state. A recoverable line written before its run-counter update remains distinguishable from a retry or a clean unattempted case.

Scoring reconstructs every packet/archive byte from the saved raw files and pinned material before accepting ratings, revalidates coverage and exact output hashes/spans, records separate review hashes and refuses output overwrite. The independent checks covered both complete synthetic runs and meaningful partial states. Unfinished preparation, corrupt identity or unreadable raw JSON fails closed rather than manufacturing a valid inference result.

The helper establishes internal artifact consistency, not independent provider authenticity: the root's manifest/inventory/SHA recovery must first bind the real raw files to the executed job. It does not rerun a model or independently decode output token IDs into text. No actual recovered file or reviewer judgment was audited here. A later outcome audit should verify the actual frozen ratings, provenance and reconstructed arithmetic without re-rating semantics.

## Reviewed identities

| Artifact | SHA256 |
| --- | --- |
| `scripts/review_train_recall.py` | `79fbfb3f2cfc73a2cf770f30aabd19463dacc3c5f4f6ef8055199813ec897a0b` |
| `tests/test_train_recall_review.py` | `0719e59988bf6fad12cfb415c9fecb575289102488ed7a20ef1ea9e68ff35d2f` |
| Imported `scripts/prepare_blind_dev_assisted.py` | `dbb601e9ec806b4c4fe69c0fb39f2261d8e978441cf0fbf0975918ed4197153e` |
| Imported `scripts/prepare_blind_palref_comparison.py` | `f0fbcf7cbc54d75865ae340f9b873594ac59ab209df30b5399fc1feacfa0d806` |
| Imported `scripts/score_blind_dev_assisted.py` | `89ecf3fb0f521df833b90966fb35145ef22e10ab72a9aa7026d3272c1e68798c` |
| Bound TRAIN-recall runner | `8d2b56c2807c52d2f103faac252f8e90de4a2ca5ce9d1df6b9a2f05fdb9dc639` |
| Bound source-only input | `5a2b29c878b67e05bb1051fab015feae33753e7c23568ab57517af0cf84c233a` |
| Bound local references | `7146aaa3173b2795f18fc231675453f34fd0ed50703c0386a0a5224af0d5bd06` |
| Bound token audit | `2b1632e86f504ddea2a44f736d00997fb14b67c7710b5a874b9abf42766d6b16` |
| Bound original qualification decision | `e466aa2bc1b2129e802605ff60882b550b1517a6b2c9ffba84b1419a8bc8fdd6` |
| Bound contrast qualification decision | `ee7d06f3c3746c4dbe7c78c70ff5c9b5b8b68e10044563c68f9036292e68db68` |

## AutoCode Critic record

- Mode: Classic + Critic.
- Lead agent/request id: /root
- Critic agent/request id: /root/final_external_judge
- Critic model and reasoning effort: inherited session settings, no override
- Independent from lead: yes
- Critic verdict: pass
- Evidence reviewed: Frozen review helper/tests and imported rubric helpers; pinned TRAIN input/reference/qualification/scope material; synthetic complete/partial packets, run identities and ratings only.
- Verification evidence: Two focused tests PASS0.290s; five additional concrete synthetic boundary/arithmetic checks PASS; opaque40-slot/56-scope coverage and disjoint-ID checks; exact source hash and review-span/positive-assessment rejection checks. No real model outputs, semantic ratings, network, cloud, GPU, credentials, installation or source mutations.

This pass concerns the local review pipeline. It is not a finding about recall performance, expert correctness, remote job success or a further training admission.

Validation: `validate-autocode-gate.ps1 -Mode Critic -Path experiments/train-recall-20260927/REVIEW-PIPELINE-QA.md` exited0 with `AutoCode Critic gate passed`.
