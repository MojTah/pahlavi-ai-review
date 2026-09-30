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
separately supplied private files and pinned dependencies. The older checkpoint-diagnostic
launcher remains a separate, unexecuted proposal.
