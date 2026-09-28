# Portable review package

Prepared 28 September 2026. Begin with `REVIEW.md` at the package root.

## Contents and limits

The selected snapshot contains the new overview/review brief, preserved study/state history,
attribution, frozen PAL-REF files, DEV definitions, latest raw outputs and both review packets,
ratings, comparison, source-qualification records, historical comparison evidence, and existing
Python implementation/check files. The completed 28 September strategy notes, timeline and
source-access summary at checkpoint `b65b89f` are included without their raw access responses.
`MANIFEST.json` gives every included path, size and SHA-256.
It binds working-tree bytes to the original evidence checkpoint; it is not a new experiment.

Excluded: Git metadata/history, weights, PDFs, raw source downloads, full training corpora,
operational billing/access responses, credentials and temporary files.
Reports retain their dated operational narratives.
This is not a complete training or cloud-recovery bundle. Some deeper links in preserved reports,
study guides and code dependencies are intentionally outside the selected snapshot. Current
overview, review-brief and state links are checked; the manifest governs package inclusion.

Reference excerpts retain attribution and existing rights. No blanket license or public-release
clearance is asserted. A fresh private repository is the proposed GitHub destination, subject to
the owner's decision and authorized reviewer access. Nothing has been uploaded.

## Offline checks

From an extracted copy, using Python 3.11 or newer:

```powershell
python -B -X utf8 benchmarks/pal-reference-v1/benchmark.py verify
python -B -X utf8 experiments/contextual-supervision-20260927/outcome-qa-evidence/score_audit.py
```

The second command recomputes arithmetic from all 96 frozen ratings and checks scorer parity;
it writes two audit JSON files in the extracted copy. Run it in a disposable extracted copy,
not over the original frozen evidence. Neither command requires model weights, inference,
cloud access or credentials. These checks establish integrity/arithmetic, not semantic validity.

Validation of this package is recorded in `VALIDATION.md`. Pattern checks for common token/key
formats are limited checks, not a full secret audit of this repository or its Git history.

## Local artifact

The generated archive is `output/review-packages/pahlavi-ai-review-20260928.zip` in the full
workspace; `pahlavi-ai-review-20260928.zip.sha256` sits beside it. Generated archives are ignored
by Git. The manifest and this scope/validation record are tracked. Use the ZIP as a one-off
AI upload, or extract only its contents into a fresh private GitHub repository after approval.
