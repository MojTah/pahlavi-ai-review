# CPD independent component review

RESULT: PASS for the frozen, source-attributed lexical inventory component, within the limits below. No blocking defect was found. This is an independent technical/source-scope review, not linguistic expert certification, training admission, or a license decision.

Reviewer: independent agent `/root/blind_dev72_b`; writer: `/root/nllb_source_method`. Date: 2026-09-28. I wrote only this review. Checks were read-only, used the existing Python runtime with `-B -X utf8`, and used no network, external model, GPU, benchmark answers, or package installation.

## Frozen material reviewed

| File | SHA256 |
|---|---|
| `experiments/data-qualification-20260928/cpd_qualify.py` | `a4d07c5df8910841d4b5dd420c4ca3795bc078b74334c8b0a7abb634df8be85c` |
| `experiments/data-qualification-20260928/CPD-QUALIFICATION.md` | `65e5266c5d068eded0be2d91f045757a6a1ed96e711f6577db7f92ae18c2c417` |
| `resources/local/data-qualification-20260928/cpd/qualified.jsonl` | `ee054589280b8b24c452ebcf4f4c108c03d31f256282cd8704211b4825dd3f8a` |
| `resources/local/data-qualification-20260928/cpd/held.jsonl` | `6434711a1b58990522ed2dc8fdab50f5e3efa3bb582a4cd87b0276cb9dbb1f4b` |
| `resources/local/data-qualification-20260928/cpd/correction-checks.jsonl` | `db004eb8abdd2c705bb38c10e244ecf045b86ae56e1971ccaae0319410edee02` |
| `resources/local/data-qualification-20260928/cpd/manifest.json` | `8dcf27bb4651b16b689f9f8742adc7e738b3e1bee607288bddadb616c859cae4` |

I read the qualifier and frozen prior extractor, original CPD XML in the pinned observations, output records and report. I visually inspected the existing correction images `resources/local/mackenzie-pdf-review-20260928/reviewer-a/pdf-019.png` through `pdf-022.png`. I additionally rendered and viewed English PDF93 / printed page71 in memory to check a grammatical annotation. The source PDF SHA256 is `594421d8c58e3f6b0ae169e383ae2917fe7572ac53fe568350b1b4ea62b1e091`.

## Executed evidence

The qualifier's no-argument run passed. Its in-memory `build()` output equals every persisted JSON record in all three JSONL files, and all persisted hashes and counts match the manifest: 3,506 proposed inventories, 720 held units, and 54 correction checks. The validator accounts for 4,224 XML blocks plus two malformed entries with unique disposition IDs. All input pins passed, including the unchanged historical TRAIN hash; I did not inspect TRAIN content.

A separate source-to-output traversal of all 3,506 accepted inventories confirmed exact form bundles, complete ordered direct sense paths/counts, printed sense numbers, exact direct gloss/definition/grammar/usage text and attributes, grammatical group children/tails, and block-level grammatical/usage annotations. It checked 3,791 translation components, 37 definitions, 12 grammar components, 15 grammatical groups and 64 usage components. No form-by-sense Cartesian rows are generated. Same-spelling observations retain separate source identities.

The accepted-source attribute census found only sense `n` attributes, which are retained. Form/transcription attributes beyond empty attributes are `DICT=MPCD`, not discarded grammatical restrictions. The only accepted association-warning flags are the three explicitly documented correction-supported form bundles. No accepted complex-form flag or uncertain block grammar/usage annotation was found.

The code rejects semantic inline descendants in glosses instead of flattening nested quotations, references or examples into targets. It rejects unsupported direct sense children and incomplete generic senses as whole inventory holds. Accepted grammatical annotations contain no embedded example/reference nodes. An exhaustive scan found no discarded nonempty tails after excluded `eg`/`q` nodes in accepted senses. Top-level contextual examples and comparative/etymological material are excluded by source paths. This establishes structural exclusion for this snapshot; it does not certify that every unmarked English string has been semantically classified by a specialist.

## Source-scope and correction spot checks

- `kosh:cpd:04922df1d3095c85d144db82f2322eab708cfa34:block:0`: `xrad` retains the complete generic string `wisdom, reason`.
- `kosh:cpd:a288be38c6e2914c9d5dd1cfb303c4f0d5a7e6c2:block:0`: the complete `hammōxtan, hammōz-` bundle retains numbered senses `teach` and `learn`, rather than selecting one or splitting the stem string.
- `kosh:cpd:4b65e6f0922faca443fbc945b6b2e26afdcf49c9:block:0`: `zan` retains `woman, wife` plus its separate plural grammar `(pl. -ān, -īn)`.
- `kosh:cpd:d969f18bdd6b717b6fd10e76f293c29063d8f9a3:block:1`: `rawišnīh` retains `behaviour` and the suffix annotation. Visual PDF93 / print71 confirms the printed entry places `as a suffix, forms abstract nouns.` on this derivative line; it is not invented target text.
- PDF19–20 explicitly support optional-ending bundles `bahr(ag)`, `bahr(ag)war`, and `hūkar(ag)`. The accepted `hūkar`/`hūkarag` inventory retains `porcupine (not hedgehog)` as one bundled unit. Other unresolved multiple-form associations, including `wihēz`/`wihēzag`, remain held.
- The 54 selected literal correction checks yield 51 matches and three mismatches. I checked that every passing accepted inventory's required correction terms are present in its retained generic components, not merely in excluded context. The `guftār`, `nēk`, `niyāz` mismatches and ambiguous `wiyābān` headword scopes remain held; no new meaning is manufactured. The 18 exact obsolete-headword checks report absence from this pinned snapshot.

## Limits and downstream gate

The supported claim is preservation of all direct senses and explicit scope in the accepted publisher blocks of this pinned XML snapshot. It is not proof of complete historical coverage, semantic correctness of every publisher association, or visual transcription accuracy for every dictionary page. Most original dictionary pages were not independently read.

The correction audit is explicitly selective. Its match count does not certify all 1986 amendments, all transcriptions, all English index changes, or every sense of a matched entry. The component report states these limits correctly. The generic `edition` label must be read with that bounded audit, not as full 1986-edition certification.

The parser contains some branches that would merit renewed scrutiny for a changed source: excluded example tails are not universally guarded, only `n` is projected from sense attributes, and uncertainty checks do not apply to every metadata node. The exhaustive current-snapshot scans above found no affected accepted record; these are reasons to repeat review if inputs or parser change, not current blocking defects.

All accepted records remain `training_admitted=false`, `expert_certified=false`, and prohibit an unseen-vocabulary claim. Preserve these states until root completes source/work restrictions, duplication and split review, and any required licensing or specialist decisions. A dictionary surface match does not clear a protected passage or grant independent attestation.
