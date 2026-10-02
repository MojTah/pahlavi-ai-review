# Independent review of Sol 6.1 preparation

30 September 2026. Reviewed source commit: `e4fd2bdc71b983f395b1a8459044159f1f527a75`. Version impact: **NONE**; review and current-state documentation only. Implementation, frozen data, benchmark and model weights were not changed. No paid execution occurred.

**Verdict: the scientific preparation is useful and substantially correct, but hold cloud execution. Three reproducible engineering gaps remain.** The original Sol tests passed the paths they exercised; they did not cover normal checkout byte conversion, forced child termination or the saved-JSON submission boundary. This report is an independent review of preparation, not Astra approval of an actual training contract.

Classic + Critic: root integrates; fresh `gpt-6-astra` reviewers `/root/astra_gate_review` and `/root/astra_diagnostic_review` independently examine disjoint runtime scopes. Both report PARTIAL with a concrete finding. They do not supply production approval records. Initial review allocation: approximately15 minutes per independent scope; local installed runtimes and CPU mocks only.

## Findings, in repair order

### 1. P2 — Hard termination leaves incorrect attempt bookkeeping

Locations: [hf_learning_eval.py](../../cloud_pilot/hf_learning_eval.py):74–91,174–175; [hf_contextual.py](../../cloud_pilot/hf_contextual.py):113–117; [learning_eval.py](../../cloud_pilot/learning_eval.py):124–175.

The parent computation alarm fires at3000 seconds, while the child's cooperative cutoff derives from3300 minus180 seconds: approximately3120 seconds. If the run reaches the parent ceiling, `run_logged` kills the child before its own finalization. The active attempt has been counted as attempted but is still listed as unattempted; it gets no final error row and `run.json` remains `running`.

The independent actual parent/child reproduction completed two CPU mock answers and interrupted the third. It retained two prediction rows and the full56-cell schedule, but reported attempted3, recorded2, active`LD-002:candidate`, and54 unattempted including that active cell. This is **not loss of prior results or of the overall denominator**. It can misclassify interrupted cells or encourage an invalid replacement first attempt. Outer failure/export metadata does not reconcile the stale inner ledger.

Repair the deadline ordering, allow a bounded finalization margin, and explicitly record any active cell left by a forced kill as interrupted/unknown. Preserve prior rows and the complete schedule. Verify using an actual parent/child termination check, not only a catchable exception inside a mock model. [Independent reproduction and full scope](DIAGNOSTIC-REVIEW.md).

### 2. P2 — Normal Windows checkout changes frozen diagnostic bytes

Locations: missing rules in [`.gitattributes`](../../.gitattributes); [corrected prepare.py](../corrected-learning-diagnosis-20260930/prepare.py):43–47,145–166.

The repository already protects many hash-bound experiments with `-text`, but neither the new corrected diagnostic nor the original learning diagnostic and several associated helpers have that protection. With this machine's current Git conversion, a normal checkout produces bytes different from the saved frozen identities. No file content was changed to demonstrate this: `git cat-file --filters HEAD:<path>` applies the configured checkout transformation in memory.

For the corrected inputs, current working bytes and the committed blob hash to `02c5ecc82e187847377d5891c31fcb9fc5fb0d3714ea4aa66e686c0a3fabce3c`; checkout-filtered bytes hash to `dc08b8040c4108ec3f9e60c72e0f00b17aa193585101249c3c826323aa87e9f2`. References, `training_admission.py` and `hf_learning_eval.py` also change. The already protected `bundle.py` remains exact. [Recorded five-file check](checkout-byte-check.json).

Consequently the current-checkout reconstruction pass is not a portable reconstruction pass. Restore/clone on Windows can fail exact packet or reviewed-source checks despite no substantive edit. Protect the complete byte-bound dependency set using the repository's existing attributes convention, without normalizing frozen files or changing checksums to hide drift. Verify an isolated checkout/export using those attributes. Protection missing from the old packet is inherited; the newly added packet and review identities continue that gap.

### 3. P2 — Saved JSON specifications pass admission but fail SDK serialization after claiming submission

Locations: [training_admission.py](../../cloud_pilot/training_admission.py):202–245; CLI output at [hf_train.py](../../cloud_pilot/hf_train.py):192–194 and [hf_continue.py](../../cloud_pilot/hf_continue.py):431–433.

Admission compares specifications through `plain`, so native SDK volumes and their JSON dictionary representation both pass an unchanged contract. The helper returns the caller's representation and creates the exclusive claim before calling the SDK. JSON-loaded CLI output then fails the installed SDK's pure serializer with `AttributeError: 'dict' object has no attribute 'to_dict'`; the claim remains, although no request was sent.

The native in-memory builder path works. This is a local boundary/recovery defect, **not a paid-job bypass**, and persisted input support is not clearly promised by the new helper's documentation. The minimum correction is to reject unsupported representations before claiming; alternatively reconstruct native volumes and validate serialization first. Claims after genuinely ambiguous provider calls must remain protected. [Independent reproduction using only the offline SDK serializer](GATE-REVIEW.md).

## What Sol did correctly

- The corrected28 packet actually binds to corrected96's recovered manifest,96 completed updates and1536 consumed slots, including exact ID order and stream hash. It is not merely a list of intended examples.
- All12 auxiliary probes were consumed. Overall24/28 had corrected-continuation exposure; four historical cases are explicitly nonexposed in that continuation. All16 historical cases retain step280 parity and their original qualifications. Six corrected lexical targets keep their selected IDs.
- Prompt/answer hashes, full token arrays and actual runtime tokenizer prefixes agree. The cloud candidate and retained step280 identities match the recovered records. References are kept out of the prepared inference payload. Remote bytes were not independently fetched here.
- The descriptive28-case design preserves56 scheduled first attempts, module-specific interpretation, uncertainty, separate raters and original criteria. It does not claim unseen translation accuracy, independent samples or a causal auxiliary-training effect. Grammar tasks correctly remain conditioned recall.
- All five native training builders refuse by default. All five complete synthetic-evidence positive paths pass their embedded guard. Missing/changed records and repeat local claims are rejected. This validates the declared manual-record mechanism, not reviewer authenticity or scientific truth.
- The legacy evidence repair reproduces the exact original69 attachments across24 cases. Root independently reran all seven evidence tests successfully. The mixed-run label correction uses the validated manifest. Historical receipts were preserved.
- The proposed Unicode policy preserves raw sources and frozen tests, restricts normalization to a future separately qualified projection, and requires collision/sense/token checks. No unsupported claim of quality improvement is made.

## Feedback from the two other chats

The current final messages in **Review project failures** (`01a0f1b3-6ca5-7942-bd74-e84fa9003303`) and **Research AI for extinct languages** (`01a0f295-56bb-7e90-b785-3f277fd0eb52`) were reread. Sol's updated sequence addresses their central request: measure what the existing checkpoints reproduce before further training; retain the benchmark; keep prompt, numerical and retrieval interventions separately justified.

The full reassessment correctly distinguishes earlier prompt experiments from the untested current wrapper, BF16 from FP32, available data from consumed examples, and token proportions from loss/gradient influence. It preserves the failed promotion decision and does not promise that a larger corpus alone will fix translation. The handoff was considered without silently adding another paid experiment. There are still no new diagnostic predictions.

Three especially relevant primary papers were spot-checked again:

- [Aeneas](https://www.nature.com/articles/s41586-025-09292-5) studies inscription contextualization/restoration with historians. Restoration character error decreased from39% alone to33% with parallels and21% with parallels plus predictions. This motivates an inspectable evidence experiment; it does not validate our Pahlavi translation. Its perceived-usefulness figure is not accuracy.
- [ParsiPy](https://aclanthology.org/2025.alp-1.17.pdf) provides transcription-oriented linguistic tools. Its rule-based phoneme-to-transliteration model outperformed its LSTM on the reported error measures. This supports a candidate baseline, subject to local representation, source-overlap and correctness checks; it is not demonstrated passage translation or OCR.
- [PahGen](https://aclanthology.org/2025.loresmt-1.16.pdf), sections4–6, distinguishes a200-pair evaluation set (167 created and33 historical sentences),20 human-evaluated outputs and a separate360-pair generated resource. The English-to-Pahlavi direction and constructed short-sentence task limit transfer to historical Pahlavi-to-Persian. These data are not automatically qualified training additions.

Those checks support the handoff's bounded interpretation. The remaining numerical literature claims were not exhaustively re-audited here and are not used to select a new model or grant readiness. Specialist calibration, independently qualified confirmation probes and leakage-controlled evidence assistance remain useful follow-ups. The current diagnostic does not establish which one will help.

## Verification and decision

The independent gate reviewer ran35 focused tests and seven selected preparation checks, plus all five native positive-path runtime guards. A broader run had seven sandbox `TemporaryDirectory` permission errors; those checks remain unverified, not declared product regressions. The diagnostic reviewer independently passed exact reconstruction, four corrected tests, saved-spec/helper identity checks and the real parent/child reproduction. Root passed seven legacy-evidence tests and the read-only Git checkout test. These overlapping groups must not be summed into an independence claim.

The already documented3000-second budget versus5040 seconds of summed case caps remains a separate admission limit. It does not prove the real run will take that long, but measured complete-cycle timing, current credit/rate/idle jobs, GPU loading and output durability are still required. No full31B inference or semantic outcome was verified.

**Keep the scientific plan; repair the three narrow boundaries before cloud use.** Do not reopen training, change models, expand the diagnostic or adjust the fixed merit on this review's authority. After repairs, rerun the affected checks and independently review the exact runnable artifact. The actual acquisition results and a later exact training contract still need their own Astra review and human authorization. This report leaves the three implementation findings open rather than silently changing the reviewed code.

## Review-report accuracy gate

Both independent reviewers checked this integrated report after their findings were incorporated and confirmed accuracy within their respective scopes. They did not approve the underlying implementation for launch. The source-paper spot checks and checkout-byte experiment were performed by the lead.

Lead agent/request id: /root
Critic agent/request id: /root/astra_gate_review
Critic model and reasoning effort: gpt-6-astra; inherited parent reasoning effort without an override
Independent from lead: yes
Evidence reviewed: This report, GATE-REVIEW.md and DIAGNOSTIC-REVIEW.md; the diagnostic reviewer separately approved its own scope
Verification evidence: Both fresh reviewers confirmed the integrated descriptions and test counts; root checked the Git byte-conversion reproduction and three cited primary papers
Critic verdict: pass with notes

This gate concerns report accuracy only. The reviewed implementation verdict remains PARTIAL/HOLD, with three open findings and no actual training admission.
