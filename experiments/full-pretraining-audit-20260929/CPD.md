# Exhaustive CPD source-projection audit — 2026-09-29

**PARTIAL overall: archived-XML fidelity passes; the learning task has a confirmed conditioning gap.** This is a complete machine comparison of the CPD release to its archived XML, with review of flagged exceptions. It is not a new page-by-page certification of MacKenzie's printed dictionary or expert adjudication of every gloss.

## Coverage and independence

[cpd_check.py](cpd_check.py) reads the archived API response directly, parses its XML with the Python standard library, independently partitions source form/sense blocks, and reconstructs the complete ordered generic sense inventories. It neither imports nor executes the old extractor or qualifier. It reads the qualifier's literal edition-policy lists solely to test the stated historical hold reasons; those policy choices are not independently re-proven from print here.

[cpd-audit.json](cpd-audit.json) contains a metadata-only disposition ledger, input hashes, per-row comparison results, reviewed exceptions, and exact collision groups. No bulk forms, glosses, XML, examples or target token sequences are copied into it.

| Scope | Exhaustively accounted for |
|---|---:|
| Raw CPD entries / well-formed entries | 3,103 / 3,101 |
| Independent form/sense blocks | 4,224 |
| Released lexical-en rows | 3,506 |
| Held units, including two malformed XML entries | 720 |
| Ledger dispositions, with no missing or duplicate IDs | 4,226 |
| Released form strings | 3,509 |
| Released target string atoms / target text fields | 8,470 / 3,920 |

The 8,470 atoms include structure strings such as component kinds and published sense numbers; they are **not 8,470 translations**. Each complete form bundle and target tree was compared without normalization or splitting polysemy. All released rows also occur in the actual tokenized CPD pool; 64 CPD rows were selected in the mixed pilot.

## What passed

- Every archived entry is represented exactly in the CPD observations. Raw-file and XML hashes, observation identities, block boundaries, form paths, sense paths, and release origin locators agree.
- All 3,506 form bundles, full ordered sense trees, sense counts, published sense numbers, grammatical/usage components, component attributes and supported inline text agree with independently reconstructed XML projections. The release and intermediate qualified component agree with these reconstructions.
- The target contains 3,791 `tr`, 37 `def`, 12 `gram`, 15 `gramGrp` and 64 `usg` top-level sense components. No unexplained lost target attributes, semantic inline nodes, unprojected sense text/tails or dangling released references were found.
- All excluded source paths agree. Released blocks exclude 1,956 comparative-transcription nodes, 287 etymology nodes, 34 top-level crossreferences, three top-level examples and one label. One additional example inside a sense is excluded. Their sentences are not substituted for generic glosses.
- Form nodes contain 3,509 transcription children, 2,839 orthographic transliterations, 254 ideogram spellings and two internal crossreferences. The two internal references resolve and accompany direct generic senses; neither reference is substituted for a target. Thirteen form-node `DICT` attributes identify the dictionary, rather than a lost sense qualifier. Two transcription children also carry `DICT="MPCD"`.
- No replacement characters, private-use/unassigned/surrogate characters, or unexpected control characters were found in released form/target strings. This scan does not establish philological correctness or rule out ordinary-letter transcription errors.
- Input hashes were rechecked after completion; all audited input bytes remained unchanged.

One automatic omission flag was resolved by inspecting its raw XML: `kosh:cpd:af7f6c8954361b77a45ab410745b6c6af181fdc9:block:0`, `/entry/lbl[3]`, is the equality label between spelling and comparative transcription evidence. Its declared exclusion does not drop a gloss or grammatical qualifier. The machine ledger preserves this reviewed resolution. There are no unresolved projection mismatches.

## Confirmed task-design finding: indistinguishable inventories

**79 CPD groups, comprising 173 released rows, have exactly the same model-visible source and context but different target inventories.** Each group also has identical actual `pool.input_ids[:prompt_tokens]`; this result does not depend only on release metadata or a stored prompt hash.

Of these groups, 65 have distinct raw entry-level homonym numbers. Eleven further groups have distinct XML entry labels, and three consist of separate unlabeled source entries. In total, 219 released rows originate from entries with a published entry-level `n`; that attribute is absent from the learning context. Preserved sense-level numbering is a separate level and does not supply the omitted entry distinction.

Two brief, source-faithful examples illustrate the problem:

| Identical input form | First source inventory | Alternative inventory | Pilot exposure |
|---|---|---|---|
| āzarm | `a1135f930019a3b5fc5a01c8cbbac854699f7086:block:0`, entry 1: “honour, respect” | `8c3177eefbf04c844015521004e3151cd8a04cb5:block:0`, entry 2: “harm, injury” | First only |
| čašmag | `7154a79988a9f64fcc64b6ebc341a4c6c935b567:block:0`, entry 1: “spring, source” | `f393b3800ab25709942b4c9537e0ba2a44793b75:block:0`, entry 2: “renowned” | First only |

All IDs in the table have the prefix `kosh:cpd:`. Full exact IDs and selected exposure are in the collision ledger.

**Seven affected rows were selected, and zero CPD collision groups have more than one selected alternative.** Thus the full released pool has an underdetermined inventory task; this audit does not show paired contradictory CPD exposure in the actual mixed pilot, nor establish a causal effect on model results.

Before another training selection, decide and document whether a task requests a particular dictionary entry or a deliberately inclusive inventory. Entry-specific tasks need the relevant source distinction in their conditioning. Inclusive tasks require an explicit scope policy and source review; do not silently merge homonyms or collapse alternative senses. A dictionary homonym number alone also does not tell a model which meaning applies to an uncontextualized passage.

## Held boundaries and remaining uncertainty

Every one of the 720 held units remains outside this release. All 718 well-formed held blocks match their raw form/sense boundaries and exact form strings. Each declared reason has supporting direct XML evidence or a matching saved edition-policy condition; the two malformed entries fail XML parsing as declared. Reasons overlap:

| Reason | Units |
|---|---:|
| Unresolved form/sense association | 266 |
| No direct sense | 260 |
| Uncertain/damaged form / sense | 117 / 22 |
| Semantic inline markup | 35 |
| No generic gloss within a sense | 24 |
| Explicit language needing separate qualification | 19 |
| Sense reference or note / dangling reference | 13 / 12 |
| Historical added-sense scope / historical generic-sense mismatch | 6 / 3 |
| Unscoped sense tail | 5 |
| Entry note | 3 |
| Complex block grammar / missing form / malformed XML | 2 / 2 / 2 |
| Complex sense grammar | 1 |

This supports the recorded conservative exclusions; it does not prove that every held unit is unrecoverable or that the exclusion policy is optimal. The saved 1986 correction checks remain prior evidence, not a new exhaustive visual comparison. The 119 released rows from `supplemental` entries, eight from `grammar` entries and four from `xref` entries were included in the same direct-sense checks; their entry types are recorded, not converted into new claims of expert approval.

Further uncertainty remains in upstream XML spelling/gloss accuracy, derivational applicability, and whether complete dictionary inventories teach the intended contextual translation behavior. Ordinary-letter typos can survive a byte-faithful projection. No held text was admitted, no frozen data or builders changed, and no model/training/inference job ran.

## Reproduction and evidence pins

Run from the project root with the configured Python environment:

```text
python -B -X utf8 experiments/full-pretraining-audit-20260929/cpd_check.py
```

This reads project-local snapshots and overwrites only `cpd-audit.json`. A successful run currently reports source fidelity `PASS`, task identifiability `REVIEW_REQUIRED`, overall `PARTIAL`. Input sizes and full SHA-256 values are in `inputs`; the executable's own hash is also recorded.

| Artifact | SHA-256 |
|---|---|
| Archived CPD API response | `7237ee7bad641b74437b153d52cb440ae74f4ab5e06c79acf742cba2e527a2c4` |
| Qualified CPD component | `ee054589280b8b24c452ebcf4f4c108c03d31f256282cd8704211b4825dd3f8a` |
| Held CPD component | `6434711a1b58990522ed2dc8fdab50f5e3efa3bb582a4cd87b0276cb9dbb1f4b` |
| Released lexical-en | `4d8c2489eca369d0d11a3364f5844cb5440d32eb53777c4ad138f5aff16c0f48` |

Source locations, block paths and per-row hashes make the comparison reproducible for an authorized holder of the corpus. This metadata report does not itself supply the full dictionary or settle redistribution rights.
