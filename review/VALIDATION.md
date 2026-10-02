# Public snapshot validation

The publication process copies research files without modifying their originals, retains the existing
review repository's history, and generates per-file SHA256/size metadata. It scans final public bytes
for common credential/private-key/JWT forms and excludes named operational responses and bulk
third-party source exports. These bounded checks do not prove absence of every possible secret
or establish linguistic correctness. The source repository's full Git history is not published.

Public-entrypoint references, frozen benchmark verification and remote commit/tree checks are
performed before delivery. The corrected-v2 cloud run and its local blinded comparison have
separate execution and verification evidence in `experiments/training-ready-v2-20260929/`.
Publication checks do not establish semantic correctness. Full data-dependent tests require
separately supplied private files and pinned dependencies. Acquisition, dose and later inference diagnostics have completed; consult the current overview and dated results.
Publication is not a new experiment, and no new quality claim is made.

## Checks completed on 2 October 2026

The lead verified all 1,597 payload sizes and SHA256 hashes, exact file inventory, current entrypoint links, JSON parsing, and the latest own-analysis comparison counts. The bounded common-credential scan found no matches. The public checkout passed `python -B -X utf8 benchmarks/pal-reference-v1/benchmark.py verify` (40 passages, 160 cases), and the pre-staging `git diff --check`. The complete staged diff later identified preserved progress-bar whitespace in raw execution logs; the code/document/JSON/PowerShell diff check passed. Original log bytes are retained as evidence. An independent read-only critic confirmed the factual handoff and publication scope, including 181 omissions and zero omitted files present. No model execution or exhaustive linguistic audit was performed for publication.

Final Git inventory validation caught 46 selected component-result JSON files hidden by an inherited ignore rule. These exact 172,576 bytes were explicitly staged, and the Git index was checked against every manifest path before the final push. No additional data family was added.
