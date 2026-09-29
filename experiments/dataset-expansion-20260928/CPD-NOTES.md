# English CPD structure recovery

28 September 2026. Bounded local recovery, Classic Codex implementation with independent root review pending. This is a structural extraction aid, not linguistic certification, split clearance, licensing approval or training admission. No source text, gloss, existing corpus or evaluation file is changed.

## Integration API

Import `cpd_extract.py` and call `extract(xml_string)`. Import is inert; the helper performs no file I/O. The result contains:

- `source_xml`: the exact original string, including malformed material; `source_xml_sha256` hashes its UTF-8 encoding.
- `tree`: ordered nodes with `path`, `tag`, `attributes`, `text`, `tail` and `children`. This retains grammatical labels, transcription versus transliteration versus heterograms, attribution/uncertainty attributes, translations, definitions, examples, usage, etymology and cross-references in their original nesting. XML parser character/newline normalization can affect this tree; the original string remains authoritative.
- `blocks`: provisional scope units whose zero-based indices reference `tree.children`. Separate lists identify forms, direct senses, direct cross-references and other metadata. The first form-bearing block is `main_block_index`; later blocks often contain derivatives or compounds, not extra senses of the initial headword.
- `scope_flags` and `association_status`: more than one transcription-bearing form element in a block remains unresolved. A form containing only spelling/heterogram information is retained alongside its neighboring transcription-bearing form. A new form after a direct sense or cross-reference opens a new provisional block. This follows XML sequence; it is not an independently verified dictionary-layout rule.
- `explicit_language_nodes`: locations of explicit language attributes. Do not assume every CPD item is unqualified Middle Persian: some entries/forms explicitly say `P`. Historical comparison languages under `trcEvid`/`etym` remain separate evidence nodes.
- `training_admitted=false` and `source_correctness_certified=false` on every result. Unknown tags/root structures are held; malformed XML receives `HELD_MALFORMED_XML` with no partial recovery. Declarations are not processed.

Do not concatenate an entire sense with `itertext()` to create a target: nested cross-references, usage, examples and grammar are not ordinary translation words. Preserve each `tr`/`def` node and its inline structure. Do not split comma-separated form strings, expand stems, invent variants, distribute all senses over all forms, inherit a later gloss backwards, resolve cross-references automatically, or translate English glosses into Persian here. Metadata nodes stay in the ordered tree; their assignment to the surrounding block is positional, not a certified scope claim. Numbered senses retain their printed `n` attribute and order; implicit POS is not inferred.

## Executed full census

Pinned input: `resources/local/kosh-quality-20260928/complete-v4/observations.jsonl`, SHA256 `3b0b14ce6e6520ad801839388d7362596c0cdfd1480f1a5b63d378071c0c1a65`.

| Unit | Count |
|---|---:|
| Current English CPD observations | 3,103 |
| XML structures recovered, all still review-required | 3,101 |
| Malformed XML held intact | 2 |
| Distinct top-level tag sequences profiled | 188 |
| Direct form elements | 4,515 |
| Direct sense elements | 4,344 |
| Provisional blocks | 4,224 |
| Single transcription-bearing form sequence with a direct sense, still review-required | 3,856 |
| Unresolved blocks | 368 |
| Blocks with multiple transcription-bearing form elements | 111 |
| Blocks without a direct sense | 260 |
| Blocks without a direct transcription | 2 |
| Entries containing explicit language attributes | 20 |
| Training additions | 0 |

Flag counts overlap; they are not additive partitions. Form, sense and block counts are structural units, not counts of independent translations, unique headwords or ready training examples. Several direct senses contain grammar or references without a usable gloss. Existing quarantine/lineage/rights dispositions must remain alongside this overlay; successful parsing never clears them.

Malformed observation IDs retained:

- `kosh:cpd:8a25cd9aab91d28e0ee26362420a038d79c28d90` — invalid token, line1 column194.
- `kosh:cpd:18e5fce7abcc6ac96b157109ffd59b462a3a1e65` — junk after document element, line1 column230.

No source-supported repair was available locally in this task, and none was attempted.

## Verification

Run `[USER_HOME]\.venvs\codex-science\Scripts\python.exe -B experiments/dataset-expansion-20260928/cpd_extract.py` from the project root. It hashes the frozen input, profiles all 3,103 observations, checks complete top-level-node coverage, and prints JSON only. It creates no output files. The local full check completed in roughly two seconds.

Actual pinned examples checked:

- `04922df1d3095c85d144db82f2322eab708cfa34`: `xrad` keeps **wisdom, reason**; the separate complete form string `xradīg, xradōmand` keeps **wise**. Nominal/adjectival interpretation is evident in the supplied glosses but is not invented as a printed POS field.
- `20194fd2eed4636d5ceb9bed2f27f1bb2375e952`: `wihēz` and `wihēzag` precede three senses. The two forms/three senses remain one **unresolved** block; no six-pair Cartesian expansion is emitted.
- `4cdd1efd4cd2ad48e400cf5c6d48965422ce271a`: `ān` has a separate transliteration-only form; `ān ī` has its own direct sense. The nested example translation remains inside `eg`, not a third main sense or a headword target.
- Both actual malformed XML records remain held. Synthetic malformed, unknown-tag and nested-form inputs exercise explicit failure/complex-scope handling.

The first local run exposed an omitted root tag in the known-tag set; it was corrected, and the self-check now asserts the exact parse-status partition. Final full check passes. No external service, model, package installation, cloud job or file dispatch was used.
