# Independent technical outcome audit

Lead agent/request id: /root
Critic agent/request id: /root/nllb_final_preflight_review
Critic model and reasoning effort: inherited GPT-6 Astra and parent reasoning effort
Independent from lead: yes
Critic verdict: pass
Evidence reviewed: Recovered eight-file manifest and inventory, source/package/model bindings, real canaries,60first attempts, numerical analysis, neutral packets and saved terminal receipt.
Verification evidence: Independently checked hashes, recomputed all overall/per-work arithmetic, and reconstructed all19packet/provenance files byte-for-byte. No model/GPU repeat or cloud call; semantic review files were not opened during this audit.

Forty likelihood calls and20generations completed without failures or missing calls; optimizer updates0. Shortest014 and padded013+014 real canaries passed. Correct-source meanNLL1.7465892340; mismatched4.9727921577; equal-parent full-target mismatch penalty3.2262029237, content-only3.3713623020. All20penalties are positive under both definitions. Maximum FP32-reference discrepancy4.772534198949074e-7, within unchanged1e-5; raw native discrepancy up to0.006516999650193256 remains recorded.

Each independently shuffled packet contains20successful outputs and28qualified scopes. Model/condition/likelihood metadata are absent. This audit supports source sensitivity on the selected seen TRAIN cases, not semantic accuracy, generalization, decipherment or a causal explanation. The original zero-scored-call failure is preserved. The saved terminal receipt states COMPLETED; the critic verified that receipt but made no live provider call.

| Evidence | SHA256 |
|---|---|
| execution/recovered/manifest.json | 8dffe0c1676576d5044ecbd2d4b8725ff5fb0a5e89a0ae53a05ff13a2029a0c5 |
| execution/recovery.json | 6f532a66113decd09fe02604696e3f1e42f534592f098e459a3cc5d8667dd283 |
| analysis/likelihood-analysis.json | 5b330d142f9689d697562e8b679cdc027bdfb6252a2c0129dfe49024170dd7be |
| ../../seen-review-20260928/lead-only/provenance.json | 9c24c92846651fa5566d0b218c2dd69ce043a172ff555e402219be613da18cc3 |
| execution/terminal.json | dc2f329f4f7ba613471430d75af2cefc66b2cd6aa442369fb46236eff49c7b67 |

## Independent frozen semantic-score audit

The same independent critic subsequently reviewed the frozen semantic files and returned PASS with no blocking findings. It rebuilt the neutral packets byte-for-byte, verified both review hashes and scored copies, and reran schema, coverage, exact-span and aggregation checks. This was an integrity/arithmetic review, not another linguistic judgment.

Both raters accepted2/20, exactly TRAINRECALL1-003 and006. A recorded8 meaning errors and10 critical errors; B recorded10 and8. Both preserved all5 published contextual glosses. Among23 functional scopes, A recorded2 preserved/17 contradicted/2 omitted/2 unassessable, B4/14/2/3. All overall and per-work summaries matched exact recomputation. Fresh-context reviewer provenance is preserved in the freeze receipt; judgments remain provisional AI assessments.

| Evidence | SHA256 |
|---|---|
| scored/summary.json | b5441eb91365c0f5eda214ecfeb2196d9b6011e0281ac6e285e5d7b0ec0697de |
| ../../seen-review-20260928/reviewer-freeze.json | 28ad36c7691f433d6f0f296980987d8eb2eb8c6aa86d27bce0dfaaeb3127b8c4 |
| ../../seen-review-20260928/lead-only/mapping.jsonl | c64fae61d8e7a33864e98fa68ff7d5ae6b38d68956d6b6c03a499851d0b1af7b |

## Decision write-up check

Research reviewer `/root/finetuning_kb_research` separately checked REPORT.md and the knowledge-base decision register after integration: PASS, no material correction. The text faithfully applies its pre-unblinding predicate, retains unsupported additions as the strongest decoding counterargument, avoids causal/universal/generalization claims, and proposes new independently qualified whole-clause supervision rather than repeating the old audit or mixture. This check neither certifies the linguistic labels nor admits another paid run.

The AutoCode Critic metadata gate and root checks of frozen score hashes and updated local document links passed. Those checks validate the stated artifact properties, not a new model execution.
