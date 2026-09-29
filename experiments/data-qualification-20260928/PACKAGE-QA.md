# Qualification package QA

**PASS for the declared frozen source-qualified release.** No model run is admitted. Date: 28 September 2026.

- Lead agent/request id: /root
- Critic agent/request id: /root/nllb_final_preflight_review
- Critic model and reasoning effort: Inherited parent configuration, no override; exact runtime identifier is not exposed in the agent result.
- Independent from lead: yes
- Evidence reviewed: freeze_release.py, seven typed projections, component decision/QA packets, all ten persisted outputs, release-v1.json, original TRAIN and benchmark byte receipts.
- Verification evidence: Final critic preflight 3.53s; independent all-component projection assertions 4.04s; persisted --check 3.59s; direct-byte audit 0.87s. All144 input bindings and ten output hashes/sizes/row counts passed. Original2237 control byte-identical. Root write3.63s and subsequent exact replay passed; a second --write was refused before mutation, with all output and manifest hashes unchanged.
- Critic verdict: pass

Release manifest SHA256: `763e49a9e11b35c0565bed14869e1b09c53e09a28431f026abc7610f4bf2bed0`.

Builder SHA256: `893f5922dd7f2f36426a56640ab6b1c35e4aca3e4be5834af7b336798dcd2d44`.

Final [RELEASE-REVIEW.md](RELEASE-REVIEW.md) SHA256: `c61d20e136201b34829338ecc18cd1821e27cd37d4285167dd66a744a54c4589`.

## Evidence scope

| Component | Qualification writer | Independent critic | Result |
|---|---|---|---|
| Persian six-family pool | Root, seen20_blind_a, nllb_final_preflight_review on disjoint families | seen20_blind_b | 2,676 qualified /123 held; all accepted fields reconstructed from original XML |
| MacKenzie CPD | nllb_source_method | blind_dev72_b | 3,506 qualified blocks /720 held units; complete structured senses retained |
| MMP | nllb_source_method | blind_dev72_a | 1,426 qualified /564 held; all structural joins/spans and targeted semantic samples checked |
| S22 new grammar | seen20_blind_a | blind_dev72_a plus root image checks | 120 new qualified plus120 earlier units; one unresolved new glyph held |
| Documentary archive | seen20_blind_b | nllb_source_method | 57 qualified spans;14 held; two exact derived typo repairs approved |
| Kanheri / Pasargadae | finetuning_kb_research | blind_dev72_b | Six Kanheri occurrences qualified; uncertain full parents and Pasargadae frames held |
| S23 article | blind_dev72_b | finetuning_kb_research | Four scopes qualified; full parents, restricted reading and duplicate formula excluded |
| Canonical export | Root | nllb_final_preflight_review | Persisted replay and byte audit PASS |

Every source/output scope is narrower than a claim of perfect scholarly correctness. The independent MMP semantic sample is not an all-entry second reading. The S22 glossary is excluded despite extraction. Documentary fragments preserve uncertainty and do not become complete certain sentences. Same-source websites and print copies are not independent witnesses. Component reports preserve individual review methods and limitations.

No new runtime model quality, improvement percentage, tokenizer capacity, training balance, full rights clearance or universal leakage freedom was tested. The exposure incident is documented in PLAN.md. Statistical/evaluation and paid-run decisions remain separate.

The coverage census is descriptive: whitespace units, full form strings and surface-pair diagnostics, not model tokens or independent observations. Its first local counting attempt rejected nested CPD grammar nodes before writing any census file; recursive component text/tail counting resolved that accounting issue. The learning export itself already preserved those nested nodes and was unchanged.

The final critic independently reconstructed every coverage-v1 field in0.68s and confirmed its SHA256 `75ba0fbcb43f5cfe9ec56dcf2d37c1bfaf974fb52d8082098510c1b96d3f8934`. Its read-only documentation review found two wording ambiguities; root clarified that selected grammatical context stays model-visible and the historical control needs its own `text`/`target` whitelist. No frozen payload, builder or release review changed. The AutoCode Critic gate and Git whitespace checks passed; these validate the recorded handoff structure and formatting, not linguistic correctness.
