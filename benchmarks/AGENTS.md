# Frozen benchmark contract

Mojtaba requested a permanent translation-quality standard. `pal-reference-v1/` and `pal-reference-v1.sha256` are frozen. Do not edit them, replace cases, refresh hashes, change denominators or silently fix references. Preserve bytes and Git history. Any future version needs explicit user authorization.

Run `pal-reference-v1/benchmark.py verify` before use. Store predictions, review forms, reports and any errata outside the frozen directory. Report suspected reference errors and withhold affected claims without rewriting v1.

Read the frozen protocol before evaluating. Never expose the whole input queue or reference answers to the model. Exclude the five held-out works and answer-equivalent copies from training and retrieval. The mechanical guard is integrated into the separate translator on branch `codex/translation-eval-guard`, commit `f671078`; see its `docs/HOLDOUT_INTEGRATION_20260926.md`. It enforces identities, metadata lineage and whole-field normalized exact copies, not every unknown witness or paraphrase. Future training, CPT, augmentation or retrieval paths must retain this guard and separate lineage/semantic-duplicate review.

The references are published scholarship screened for consistency, not newly specialist-certified gold. The scorer aggregates recorded judgments; it does not establish semantic correctness. AI-only or single-review results remain provisional.
