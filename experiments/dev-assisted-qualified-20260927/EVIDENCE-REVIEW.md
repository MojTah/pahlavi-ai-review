# Independent qualified-evidence review

Verdict: PASS for local evidence preparation only. Independent critic: `/root/final_external_judge`; lead: `/root`. No cloud admission, inference integration or linguistic certification is implied.

## Executed checks

- Ran `resources/local/hf-client-venv/Scripts/python.exe -B -X utf8 scripts/prepare_qualified_dev_evidence.py --check`: PASS. Evidence and audit regenerated exactly in memory. Wrong hash, existing output and altered example payload negative checks passed.
- Independently confirmed all 24 source-only query IDs, order, fields and source hashes. Surviving examples are the exact ordered intersection of the previously witness-reviewed 68 attachments and the qualified TRAIN membership: 58 attachments, 56 distinct witnesses, all 24 cases supported; 14 cases have three, six have two and four have one. Ten attachments representing nine quarantined witnesses were removed. No replacements, reranking or text repairs occurred.
- All complete surviving example objects, selection metadata and UTF-8 source/target bytes match the prior evidence and qualified TRAIN. Every retained/removed audit entry binds the original example index and canonical hash, exact qualified-ledger row/pointer/hash, disposition, full linguistic review, qualifications, edition and flags. The prior witness receipt and audit hashes bind the earlier 68-attachment screening; its limits remain intact.
- Traced every `Path.read_bytes` call during a second in-memory check: exactly 11 distinct files were read, comprising the eight pinned inputs, this generator, and its two existing outputs. No DEV reference-answer file, PAL-REF answer file, model prediction or credential file was read. Published TRAIN targets are intentionally included as contextual examples.
- Verified the token-normalization function against the frozen legacy generator by AST equality. Only covered/uncovered terms are recalculated after filtering. The original 291 rare case-terms and original selection/IDF metadata remain explicitly labeled legacy coverage: 139 covered and 152 uncovered. These are descriptive lexical-overlap counts, not qualified-pool IDF, verified word senses or translation accuracy.

## Limits and remaining gates

This reuses existing archive/witness and provisional AI qualification evidence; no new source collation, specialist adjudication or semantic review was performed. Retained qualifications are preserved in the audit, not silently converted into certainty. Exact future prompts, qualification/caution handling, token lengths, qualified-adapter integration, timing, budget and runtime readiness remain separate pending checks. No inference or paid job is admitted. No original or previously completed audit was edited.

| Artifact | SHA256 |
| --- | --- |
| `scripts/prepare_qualified_dev_evidence.py` | `3c92eebdd8f922138a92a4d8b0f9eed2074e8936d6a91b2a71da82ea05f769ab` |
| `evidence/evidence.jsonl` | `1d5e02cfb91dad1da94db072e9f5fcd6be463746bbc951425cb6631b5ea2ce4a` |
| `evidence/audit.json` | `193f49f54dd1649a6a0002ed423bdf3dfa7176a7a093e1532cdd1ce1ea32d8f1` |
