# Public snapshot validation

The publication process copies research files without modifying their originals, retains the existing
review repository's history, and generates per-file SHA256/size metadata. It scans final public bytes
for common credential/private-key/JWT forms and excludes named operational responses and bulk
third-party source exports. These bounded checks do not prove absence of every possible secret
or establish linguistic correctness. The source repository's full Git history is not published.

Public-entrypoint references, frozen benchmark verification and remote commit/tree checks are
performed before delivery. The latest evaluator has mock/local tests; no real GPU run is claimed
by publication. Full data-dependent tests require separately supplied companion files and pinned
dependencies. See `experiments/learning-diagnosis-20260929/LAUNCH-READINESS.md`.
