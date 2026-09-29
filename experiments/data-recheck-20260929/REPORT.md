# Local data and configuration recheck — 29 September 2026

**Decision: local audit complete; training and paid inference remain on hold at the user's instruction.** No new cloud job was submitted, no model weights were downloaded, and no training data, benchmark, merit rule or retained checkpoint changed. The proposed server comparison of existing qualified step280 and mixed96 checkpoints has **not run**. This report is not a claim of an error-free corpus or approval to spend.

Classic + Critic: the lead integrated separate structural, source-semantic and configuration reviews. Reused frozen data, source images and existing checks; no new audit framework or dependency installation.

## Evidence and limits

| Area | Direct evidence | What remains unproved |
|---|---|---|
| Frozen data and provenance | [53 structural checks passed](INTEGRITY.md); all 17 canonical files retained their hashes, sizes and counts. [Machine-readable receipt](integrity.json) binds the checker and files. | Hash identity does not establish linguistic truth. |
| Actual model inputs and targets | All 10,151 prepared rows passed mask, boundary, length, decoded-target and audit-hash checks. The 1,536 selected rows exactly match the saved consumed order. Every update retained its 12 historical / 2 lexical / 2 other ordering. | Correct serialization does not establish a useful task mixture or learning. |
| Exclusions and ambiguity | The 247 historical exclusions and all 888 S22 glossary groups remain excluded. All 37 registered surface-repeat groups are preserved; 1,108 shared lexical-form groups were counted without collapsing distinct senses or source contexts. | Short forms, alternate witnesses, paraphrases and shared formulas need contextual judgment; the existing exact/containment screen cannot certify zero leakage. |
| Source fidelity | [21 purposively selected high-risk records](SEMANTIC-SPOTCHECK.md) were compared with archived dictionary XML, TEI or source pages. All 18 selected records present in actual train retain their canonical targets. No confirmed extraction/alignment defect remains in this sample. | This is provisional AI review, not a random error-rate estimate, complete semantic re-audit or expert certification. Published uncertain readings remain uncertain. |
| Inference configuration | A launcher/evaluator settings mismatch was corrected before any paid execution; [all eight local tests passed](../learning-diagnosis-20260929/LAUNCH-READINESS.md). An [independent critic](../learning-diagnosis-20260929/INDEPENDENT-LAUNCH-REVIEW.md) checked the packed boundary, failure accounting and real named-adapter switching on a tiny randomly initialized CPU model. | Retained 31B weights, actual A100 memory/throughput, Linux bootstrap and remote export were not exercised. No translation result follows from the tiny CPU test. |
| Diagnostic generation cap | [Local token census](diagnostic-token-census.json): all 28 original references fit; longest is 113 tokens including the terminator, versus the fixed 512-token cap. | The actual model can still ramble or time out. 56 attempts at 90 seconds could exceed the 3,000-second compute window; complete coverage is not guaranteed. |

The structural check also repeated the existing source-only containment policy: 61 auxiliary sources of at least five words produced no matches to protected archived transcriptions; 246 shorter rows are outside that rule. Benchmark reference answers were not used by that checker. The separate token census only measured the existing training-side diagnostic references and did not alter them.

## Corrected reviewer findings

The source reviewer initially attached the following **ka** entry's gloss to **kū** (`S22GRAM-095`). Independent visual inspection and the reviewer's recheck withdrew that claim: the existing record preserves its own printed gloss inventory and reported-speech context. A second suspicion about MP0603 was also withdrawn: an escaped newline before **āwišt** had been misread as an extra letter. **Neither candidate warrants a data change.** The checker and report now agree; no frozen file was edited to accommodate a reviewer mistake.

## What the earlier training result actually tells us

The release contains 10,152 typed records, reduced to 10,151 prepared rows by one exact duplicate collapse. The latest paid run used only **1,536 examples: 1,152 historical and 384 auxiliary, of which 192 were lexical**. It did not test the full expanded corpus. Dictionaries, grammar exercises and documentary spans are different tasks; their row counts cannot be interpreted as equivalent translated sentences.

There was no matched historical-only 96-update continuation. Changes in optimizer state, learning rate, exposure and mixture prevent attributing the negative result specifically to new data. The auxiliary target-token census is 84.12% English, but this is not a measured gradient share: the runner averages loss per example. These are design limitations, not newly discovered extraction defects. See the [saved diagnosis](../learning-diagnosis-20260929/REPORT.md) and [strategy audit](../strategy-audit-20260929/RESPONSE.md).

Both existing AI reviewers still accept 1/15 whole DEV outputs for each checkpoint, with more critical errors for mixed96. Those frozen, reused development judgments remain unchanged. Retain qualified step280; no model promotion or laptop weight download.

## Required next decision

1. Keep the frozen data version and known holds intact. Confirm any future proposed correction against the source and preserve its lineage before changing a version.
2. Review the independent project feedback against this evidence. Decide whether the prepared 28-prompt-per-checkpoint learning diagnosis is worth the cost. It is intended to compare auxiliary-task recall with contextual translation on this fixed sample; it cannot by itself establish acquisition or transfer. It is not a new generalization benchmark. **It remains pending and requires new authorization for paid execution.**
3. Before any later training proposal, specify one controlled hypothesis, comparator, exact parent-example exposure and task/language mixture, optimizer schedule, unchanged quality/safety rules, and a bounded stop/cost plan. Recheck only inputs affected by that proposal; no automatic extra epoch or retraining follows from this audit.

Read-only cloud metadata was checked separately during preparation: retained adapter manifest/config/weight metadata matched saved identities and all listed jobs were terminal. Only small manifests were retrieved. This does not validate actual weight loading, certify current billing, or authorize execution. No compute was launched by this audit; existing storage charges are outside that claim.

## Reproduction

Use the project's existing pinned local dependencies; do not install or launch cloud scripts for this review. The structural checker writes only its metadata receipt:

```text
python -B -X utf8 experiments/data-recheck-20260929/integrity_check.py
```

The existing `experiments/mixed-supervision-20260929/prepare.py --check` independently replayed all seven prepared outputs byte-for-byte during this audit. The configuration test command and source hashes are in the linked launch review. The token census uses the saved `tokenizer.json` with `tokenizers.Tokenizer.encode(expected_training_answer + '<turn|>\n', add_special_tokens=False)` for each of the 28 existing reference records. Its receipt binds both input files. Full data-dependent reproduction requires the omitted private source/data companion; public metadata alone is insufficient.

## Independent report review

The critic requested narrower wording about what the unrun sample diagnosis can establish. The lead applied that correction; the critic verified it and passed this bounded evidence report. This gate approves the report, not training or paid execution.

- Lead agent/request id: /root
- Critic agent/request id: /root/blind_pair_b
- Critic model and reasoning effort: Inherited unchanged from lead; no override requested or applied
- Evidence reviewed: This report, integrity.json, SEMANTIC-SPOTCHECK.md and INDEPENDENT-LAUNCH-REVIEW.md
- Verification evidence: 53 passing structural checks with current checker/data hashes; independent source/configuration reports; critic verified the narrower diagnostic claim
- Independent from lead: yes
- Critic verdict: pass
