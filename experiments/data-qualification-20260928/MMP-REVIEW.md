# MMP generic lexical qualification

Reviewer: `/root/nllb_source_method`. Date: 2026-09-28. Component review, with independent QA still required. The data-quality review skill was used for grain, source joins and preservation checks. Only this note and `mmp-review.json` were written; no sources, historical TRAIN, benchmark answers or other components were modified. No model, network, paid service or external reviewer was used.

## Result and meaning

**1,426 generic lexical inventories qualified; 564 inventories held, out of 1,990 reviewed.** All 1,990 source form/English fields were read in six complete compact batches, followed by focused inspection of complex definitions, XML grammar, discarded tails and form associations. Mechanical checks alone did not determine the final decisions.

Qualified means a source-supported generic English sense inventory for an explicitly Middle Persian entry, with its complete form bundle and published POS retained. It does not mean a new sentence translation, an independently verified decipherment, guaranteed philological truth, or permission to train. Multiple senses remain together; no form-by-sense Cartesian expansion was made. Forty-four qualified entries contain multiple forms. Counts are entry inventories, not unique words or independent attestations.

The 564 holds are not declarations that these entries are false. They include unresolved scope, uncertain readings, context-specific interpretations, source spelling issues and inventories needing finer manual separation. This pass deliberately retains a useful clean subset without discarding those candidates.

## Exact machine-readable scope

`mmp-review.json` contains the full accepted-ID list, a reason for every held ID, source pins and one `qualified_scopes` record per accepted entry. The integration contract is:

- Join `resource_id` to the frozen lexical-resources file and confirm its one-based source line and file hash.
- Verify `original_meaning_sha256` against UTF-8 bytes of `meaning_as_published`.
- Slice that exact string with `target_spans_unicode_codepoints_half_open`; the concatenation must equal `expected_complete_selected_text` exactly. Offsets are Python string/code-point offsets, not UTF-8 byte or UTF-16 offsets.
- Preserve the entire original forms list in its original order, and `pos_grammar_as_published` as grammatical context. Check `source_xml_sha256` against the original observation XML.
- Keep discarded paratext as evidence through the frozen source pointer, never as generated translation text. Do not serialize the original XML, `attest`, `see`, `trl`, raw records or entire review objects into training targets.

All current accepted spans are contiguous, but some contain multiple ordered numbered or grammatical senses. A contiguous span does not mean a single meaning. There is no generic “take the first quoted gloss” permission: accepted endpoints are per-ID review decisions. Bibliographic tails were removed only where the entry's generic English meaning inventory remained complete. Entries with later new glosses, disputed interpretations or unsafe compound/context associations remain held.

## Important accepted and held boundaries

| Source ID suffix | Disposition | Evidence and scope |
|---|---|---|
| 5 | Qualified | Complete `-z`, `-iz`, `-uz` bundle; generic “also, too”; no attestations exported. |
| 398 | Qualified | Transitive “lift up/raise/lead up” and intransitive “rise up/ascend (= die)” both retained. |
| 531 | Qualified | Immaculate, goddess usage and Venus retained together. |
| 679 | Qualified | Justice/righteousness and the collective community/church sense retained together. |
| 2428 | Qualified | Demonstrative, definite article and personal pronoun uses all retained. |
| 2662 | Qualified | Ear/cluster and astronomical Spica/Virgo senses retained. |
| 3990 | Qualified | Both the dish/sweetmeat and curdling-substance senses retained. |
| 4387, 4903, 4904 | Qualified | Explicit second meanings retained, not discarded as duplicate alternatives. |
| 5418 | Qualified | Full three-form bundle, size/greatness, plural great things and Grandee status retained. |
| 836, 3006 | Qualified | “Perhaps” and “when?” are actual meanings, not evidence that their readings are uncertain. |
| 303, 568, 917 | Held | Generic grammatical senses are mixed with additional form/construction scope; no first-sense clipping. |
| 887, 969 | Held | Additional meanings/grammatical roles and foreign quoted glosses need explicit complete scoping. |
| 476, 688, 1781, 2256, 3344, 4503, 4959, 5554, 5759 | Held | Longer usage, contextual, comparative or disputed interpretation inventories require separate scope review. |
| 752, 1797, 2845, 3955, 5113 | Held | Explicitly uncertain or disputed form/meaning structure. |
| 1769, 1834 | Held | Cross-reference-only or bibliography/conditional language identity does not supply a self-contained generic target. |
| 196, 2230, 2831, 3809 | Held | Source comments raise form spelling, vocalization or transitivity/attestation questions; no silent correction. |
| 3055, 3602 | Held | XML grammar reveals a contextual misunderstood abbreviation or uncertain proper-name interpretation. |
| 3004, 3937, 4925 | Held | XML grammar shows an additional `yazad` component outside the primary form, affecting the “god” interpretation. |
| 4832 | Held | “Four” belongs to `čahār` in the grammar's compound context; it cannot silently be assigned to the shorter form bundle. |
| 4983, 5583 | Held | Published English `inter-pretation` and `deamon` need an explicit correction disposition. |
| 4874 | Held | Book of Giants contextual discussion and a quoted passage; its exact mapping to protected work 517 is not asserted. |
| 5457 | Held | Disputed divine identity and Šābuhragān discussion; contextual/manuscript lineage remains unresolved. |

An unfamiliar meaning, borrowed word, religious technical sense or valid alternative was not treated as an error merely because it differed from another dictionary. For example, `abyānag` retains the publisher's “bridle” or “rushes” alternatives rather than inventing one winning sense. Names and culturally specific concepts remain names/concepts with their grammatical/domain metadata.

## Source and structural evidence

The recovered file has 1,990 rows matching collection `mmp` and kind `SOURCE_LABELED_MP_LEXICAL_ENTRY`. Every row has exactly one direct XML `lang` element with text `MP`, one plain-text `sense` and one `trc` bundle. There are 1,896 one-form entries and 94 multiple-form entries. Grammar exists in 1,989 source rows and all 1,426 qualified rows.

Two source shapes have a minor structural difference: one lacks `gramm`, and one ends in `see` instead of `attest`; no nested sense tags exist in this subset. Form lists match original XML exactly. Meanings match after NFC/whitespace comparison. Entry 2202 alone has an NFC-equivalent Greek accent encoding difference; it is held for substantive uncertainty, not for Unicode normalization.

The original public response contains 5,837 MMP records, including Parthian/shared/other shapes outside this bounded 1,990-entry task. This review does not imply clearance of the complete dictionary. All 1,990 original XML strings were joined back to the raw response by ID and compared exactly. The raw response hash, observation hash and recovered-source hash all passed. No manuscript attestations were turned into new source/target pairs.

Source pins:

- `resources/local/dataset-expansion-20260928/lexicon-v1/lexical-resources.jsonl`: `3f963c94c00f79cf8c04421fcd55a539649c1b2a62eb4ac029ae195c1d73871c`.
- `resources/local/kosh-quality-20260928/complete-v4/observations.jsonl`: `3b0b14ce6e6520ad801839388d7362596c0cdfd1480f1a5b63d378071c0c1a65`.
- `sources/local/public-texts-2026-09-20/kosh-xml-gaps-20260928/raw/329562c1d69f9b0c34e87420392df4dfd348c6ac90afe7062cd3e91a96b4ae0c.source`: `ce1b476f41a3faa004b863fb98a61eeb8b1a472ea43604c30a9f96b7690192a3`.
- Historical TRAIN remains `15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc`.

The JSON was written with exclusive creation, read back and reconciled to all 1,990 unique IDs. One pre-handoff wording refinement replaced an overly strong “protected work” reason for 4874 with the correct unresolved-manuscript-quotation reason; no qualification or count changed. No claim of immutable completion was sent before this final handoff.

## Limits and required independent QA

This is a complete review of the declared recovered subset, not a new comparison against every printed page or an exhaustive manuscript source study. The source is the published Durkin-Meisterernst dictionary as represented in the pinned Kosh XML. The original collection decision and attribution remain authoritative provenance. Generic dictionary vocabulary can overlap work 517 without constituting a protected passage; conversely, vocabulary overlap is not evidence of unseen-word generalization. Attestation/work identity, protected contextual interpretations and unseen-vocabulary evaluation therefore remain separate gates.

The independent critic should stress-test complete multi-sense preservation, grammar-hidden compounds, excluded tails and exact offsets. Root must still verify the canonical exporter and count entries separately from alternate forms, duplicated resources and sentences. Intended-use rights are not inferred from this review. No training has been admitted or performed.
