# Provisional linguistic review of every actual TRAIN row

Review the complete assigned source/target passages, in manageable batches, without model outputs, DEV/TEST answers or performance-based selection. The packets cover all2,484 actual TRAIN IDs exactly once; manifest.json freezes their bytes and boundaries. Their published Persian targets are material to assess, not automatically correct gold. English, where supplied, is corroboration. No new translations or silent label repairs.

This is AI review, not specialist certification. Separate archive copying from alignment and meaning. Mechanical checks run independently. For difficult or ambiguous cases, consult the identified archived paragraph and actual adjacent passages by chapter/sequence. Do not infer adjacency from numeric IDs alone. Do not fetch external material or access Drive. Keep ordinary interrogatives, editorial glosses, legitimate reconstructions and alternative readings; punctuation alone never establishes error.

Inspect participants, action/state, negation, modality, names, quantities, omitted material, unsupported additions and the treatment of unknown/reconstructed text. A translation extending into a neighbor, switching participants, inventing an uncertain reading or lacking support needs explicit review. If a substantive concern cannot be resolved from the evidence or the reviewer cannot justify a central reading, mark it uncertain and quarantine it; do not guess a correction.

Each review is one JSON object per line with exactly these fields:

- `id`, `source_sha256`, `target_sha256`: copied exactly from the assigned packet.
- `alignment`: `pass`, `qualified`, `uncertain` or `error`.
- `meaning`: `no_identified_issue`, `qualified`, `uncertain` or `error`.
- `disposition`: `ELIGIBLE`, `ELIGIBLE_WITH_QUALIFICATIONS`, `QUARANTINED` or `UNREVIEWED`.
- `reason`: a concise source-specific explanation of what was checked or the concern; never a bare generic pass.
- `source_span`, `target_span`: exact relevant substrings for a concern; empty strings when none is identified.
- `qualifications`: list of legitimate uncertainties, reconstructions or alternative readings retained; empty when none.
- `evidence`: list containing the packet locator and any additional archived paragraph IDs consulted.
- `reviewer_id`: the actual agent identity; `reviewer_type`: `AI`; `expert_adjudicated`: false.

ELIGIBLE requires alignment pass and no identified meaning issue. ELIGIBLE_WITH_QUALIFICATIONS requires no unresolved substantive concern and explicitly preserved qualifications. Any uncertain/error alignment or meaning requires QUARANTINED. UNREVIEWED is ineligible and must not be silently filled as a pass. Distinguish a detected defect from reviewer uncertainty in the reason.

Read every row before assigning its disposition. Scripts may check coverage, hashes and schema, but must not generate default semantic passes or infer acceptance from punctuation/length tests. Preserve partial completed reviews if time/context runs short and report exact remaining IDs. At completion, verify exact packet coverage, no duplicates and matching source/target hashes. Only write the assigned packet's reviews.jsonl; never change packet, protocol, original corpus or another reviewer's files.

The lead will combine these judgments with structural flags and cross-row conflict/boundary adjudication. An initial eligible judgment is not final release if another check reveals a concern. Final reporting must retain AI/provisional limits; neither coverage nor agreement establishes100% semantic correctness.
