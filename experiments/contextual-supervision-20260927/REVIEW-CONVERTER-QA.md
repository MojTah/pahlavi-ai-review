# Independent DEV48 converter QA

2026-09-27. **PASS for local review preparation and aggregation on the frozen source below.** No actual new predictions or ratings were inspected. This is a Classic + Critic checkpoint, separate from runtime/cloud admission and eventual outcome review.

The initial converter had a material provenance gap: a locally replaced export manifest could validate its own metadata, and complete adapter metadata was not linked to exported weight records. The final repair closes that gap through the root recovery proof's run ID, manifest SHA, exact committed provider inventory, exact small-file verification set and rechecked local hashes/sizes. Each completed arm's adapter inventory/digests must match export records, including its cloud-only safetensors. Recovery bytes are retained in the private packet archive. Weight SHA evidence remains server-reported, backed by provider inventory; no local tensor verification is claimed.

I independently ran all **eight focused tests: PASS in 63.203 seconds**, using shared science Python, existing process-local dependencies, offline flags and isolated QA scratch. Tests exercise the real pinned tokenizer and synthetic output/review fixtures, including disk preparation→scoring→deterministic reconstruction; stale/replaced manifest proof, wrong/missing adapter weight records, provider inventory, verified-file-set and record-byte failures; launch/source/token/order/counter/adapter tampering; complete, failed, missing and no-evaluation cases; and default96 versus explicit48 compatibility. No production sources were edited by QA.

The two packets each contain48 opaque records with disjoint reviewer IDs and private control/candidate mapping. Reference qualifications and the existing instructions are preserved, with only the stated review count changed. Both arms retain15 whole cases and9 separate constrained cases, including failure/missingness placeholders. Both completed training arms and complete first-attempt evaluation are needed for an assessed screen. Inconsistent active/counter records fail closed and require explicit recovery; the converter does not silently repair an interrupted write.

The rubric, adverse-span requirements and score helpers are reused. The old scorer's only change is an `expected_count=96` default parameter, overridden as48 here. Per-work counts are restored using the existing helper. Additional independent fixtures passed the exact distinction between gains in two works and global net gain: one work may have a newly accepted case but zero net gain, while total net gain remains two. Whole critical increase, accepted→critical, constrained critical and new-overconfidence vetoes all fail the screen; an incomplete comparison stays inconclusive. Two reviewer reports remain separate. The primary contrast is matched control→candidate; neither historical step280 scores nor PAL40 are pooled into it.

All eight source bindings in uniform contract `4165e8150f291c2cd6077d2daee86513ad08e1851acbfc3e83169bc40263f8c2` remain unchanged. Actual cloud recovery, reviewer freshness, frozen real ratings and outcome arithmetic still require their later checks.

| Frozen source | SHA256 |
|---|---|
|scripts/review_contextual.py|`1e100fd41535db1d0b361e9096d65af0885a3747f0f4fc8c8bf458977677e7af`|
|scripts/test_review_contextual.py|`43b5a96dd503003099c757203cced0b593829eb1be30e6f1f045f22027d17200`|
|scripts/score_blind_dev_assisted.py|`7dfa3ac29b038fb370f27a6afbfab6d6d2c733644a62c40fa26cac7e5bbeb5b5`|

Executable evidence and source-bound results: [checks.py](review-converter-qa-evidence/checks.py), [result.json](review-converter-qa-evidence/result.json), [tests.txt](review-converter-qa-evidence/tests.txt). Run the harness with shared science Python and `-B -X utf8`; it redirects test output to `resources/local/contextual-review-qa` and uses no API or pretrained weights.

- Lead agent/request id: /root
- Critic agent/request id: /root/final_external_judge
- Critic model and reasoning effort: inherited session settings, no override
- Independent from lead: yes
- Critic verdict: pass
- Evidence reviewed: The frozen converter/tests, minimal old-scorer delta, fixed uniform contract and helper rubric, runtime field definitions, launch metadata, package and actual tokenizer; synthetic fixtures only.
- Verification evidence: Eight tests PASS in63.203s; independent work-gain/global-net and critical/overconfidence/incomplete fixtures PASS; all eight frozen merit hashes unchanged. Provenance blockers repaired and exercised. No semantic re-rating, actual output inspection, network, cloud, credentials, model weights or GPU execution.
