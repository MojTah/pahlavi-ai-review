# Review-package validation

28 September 2026. Documentation and local packaging only; no model training, inference,
cloud access, credential access or new semantic rating was performed.

## Checks performed

- **Entrypoint links:** all relative file links in `README.md`, `REVIEW.md` and
  `PROJECT_STATE.md` resolve inside the selected package.
- **Archive integrity:** ZIP CRC check passed; every included payload matches its manifest
  path, byte count and SHA-256. The manifest excludes itself to avoid a circular hash;
  the adjacent archive checksum binds the complete ZIP.
- **Cross-platform bytes:** the package's generated `.gitattributes` disables text
  normalization so a later Git checkout preserves its manifest hashes. It is deliberately
  different from the working project's attributes. Original documentation archives also
  have explicit byte-preservation attributes in the project.
- **Frozen benchmark:** the existing `benchmark.py verify` passed in an extracted package:
  40 passages, 160 directional cases, manifest SHA-256
  `a3932f7510f101376cc91c47bb23f3c9872656c41f563701fa3dcb2b6c89a5e8`.
- **Latest score reconstruction:** the existing independent `score_audit.py` passed in an
  extracted package. All 96 ratings validate; counts, transitions, screens and disagreements
  exactly match the frozen comparison. Both screens fail, as the brief reports.
- **Preservation:** original README and prior state are byte-identical to `STUDY_GUIDE.md`
  and `PROJECT_STATE_HISTORY_20260928.md`. Original benchmark and experiment evidence
  checksums match the pre-cleanup inventory, except the separately owned annotation-access
  README and timeline. These and the five new strategy notes were completed by their owner
  at `b65b89f` and are included with matching content. The timeline retains Windows
  working-copy line endings; the other six match their Git blobs byte-for-byte. None was
  edited by this cleanup. The package manifest binds the exact included bytes.
- **Sharing scope:** selected paths exclude weights, PDFs, raw downloads, full training
  corpora, access/billing response files and Git history. Pattern checks found no matching
  common HF/GitHub/OpenAI token, JWT or private-key formats in the selected files.
- **Documentation diff:** whitespace check passed for this cleanup's tracked changes.

## Limits

These checks establish file integrity, package usability and arithmetic. They do not establish
semantic correctness, public redistribution rights, a full secrets/history audit, cloud-weight
identity from local tensors, or training reproducibility without the omitted inputs/runtime.
The whole implementation test suite was not rerun for this documentation-only change.

The first extraction attempt hit a Windows permission error in a temporary directory.
Validation succeeded after extracting into a normal workspace directory. Only the disposable
extracted copies received the arithmetic audit's output writes; frozen originals were preserved.
