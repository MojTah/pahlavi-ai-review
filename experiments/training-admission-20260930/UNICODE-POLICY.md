# Unicode policy for future training projections

Policy ID: `nfc-derived-v1`,30 September2026. Proposed projection policy; it has not been applied to a training release. The corrected96 acquisition packet must use the exact bytes/tokens on which that checkpoint trained.

## Source preservation and transformation

- Keep each acquired raw source, published reading, target, source locator and original hash unchanged.
- Normalize only admitted derived learning strings with Unicode NFC before prompt construction and tokenization. Apply the same policy recursively to actual source/context/target string values within structured learning fields; do not normalize record IDs, file names or provenance fields as a substitute for content review.
- Preserve diacritics, scholarly transcription signs, capitalization and grammatical/sense distinctions. NFC composes canonically equivalent sequences; it does not justify removing accents or modernizing historical spelling.
- Arabic/Persian yeh and kaf, apostrophe signs, nonbreaking spaces and whitespace conventions require separate field/language-aware decisions. Do not silently include them in this policy. Existing prompt trimming must remain explicit.

## Qualification before a future release

Rebuild a new named projection rather than overwriting a frozen release. Record pre/post string hashes and token IDs, full changed-record census, source/context/target scope, tokenizer/template identity and policy ID. Verify normalization is idempotent and retains Unicode-canonical equivalence. Repeat exact prompt/answer collision and deduplication checks after transformation; canonically equivalent inputs with different targets must retain supported senses or be held, rather than arbitrarily collapsed. Recalculate actual selected exposure and sequence/label census.

References and fixed benchmark bytes are not changed. If inference applies a new normalization interface, predeclare it as a separately named diagnostic condition. Compare with the original interface using matching checkpoint/numerics and fresh joint ratings; do not silently revise historical scores.

The known issue is bounded: both recent selected streams contain16 non-NFC sources and11 non-NFC targets. All16 source tokenizations change under NFC. This proves a representation inconsistency, not that it caused the observed translation failures. [Exact evidence](../external-review-20260930/DATA-BEHAVIOR-AUDIT.md).

Before training on a transformed release, independent source/token review and the exact training-admission contract must cover the transformed artifacts. This policy alone is not clearance for training or a claim of improved quality.
