# Dictionary data-curation checkpoint

28 September2026. Root owns local execution and integration. Kosh downloads belong to the separate acquisition chat. The user requests clean, correct data, broad source coverage and Gemini Pro or higher for the dedicated [curation agent](AGENT.md). No paid training, new translation labels or benchmark edits.

## Frozen intake and executed local pass

`stage.py --self-check` and one `stage.py --complete` execution passed using shared `codex-science` Python. The pinned checkpoint contains 38,685 primary records plus the separate AWN190 `data.ids` response, counted exactly once. All 34,539 previous v3 current-site records retain identical source payloads; 4,147 current-site IDs are additional. The 4,218 legacy records remain a separate edition/encoding layer.

[Current summary](summary-v4.json) and [independent verification](verification-v4.json) bind actual code, input receipts and outputs. Every original field and ID is preserved. Earlier [v1](summary.json), [v2](summary-v2.json) and [v3](summary-v3.json) receipts and output bytes are unchanged. V1 code is in commit1579ebe; v2 code is in commit98aeaa6; v3 code is in commit1ad57cd. The runner now refuses to overwrite a version whose summary or outputs exist.

| Version | Current-site records | Legacy records | Staged groups | Collapsed repeats | Quarantines |
|---|---:|---:|---:|---:|---:|
| v1 | 5,992 | 4,218 | 4,381 | 857 | 4,972 |
| v2 | 9,597 | 4,218 | 7,071 | 857 | 5,887 |
| v3 | 34,539 | 4,218 | 24,012 | 901 | 13,844 |
| **v4 current** | **38,686** | **4,218** | **26,377** | **903** | **15,624** |

Accounting: 26,377 groups + 903 additional provenance rows + 15,624 quarantines = 42,904 preserved observations. V4 has 2,365 more staged groups than v3 and 19,306 more than v2. These are lexical review candidates, not admitted translations. Historical TRAIN remains 2,237 pairs; newly admitted pairs remain zero.

## Quarantine and interpretation

| Reason | Records |
|---|---:|
| Legacy encoding and edition relationship unresolved | 4,218 |
| Known held-out work or related collection: HKR/SNS/WZ/MZ | 1,485 |
| Mixed source language or Armenian-loanword review: MMP/WMIAR | 6,274 |
| Complex CPD form/sense grouping requires dedicated parsing | 3,101 |
| Malformed CPD XML | 2 |
| Missing or placeholder meanings | 200 |
| Nested source/meaning text needs review | 328 |
| Missing or placeholder source forms | 8 |
| Text outside a recognized form/sense scope | 1 |
| Ambiguous form/sense boundary, AWN190 has no source form | 1 |
| Ambiguous form group | 1 |
| Unsupported form metadata | 5 |

Quarantine preserves evidence; it is not deletion or a conclusion that every record is wrong. No variant list is expanded into independent examples. No legacy ASCII transcription is silently decoded. Published polysemy remains separate:765 staged groups belong to form groups with differing meanings. One hundred thirty-one exact form/meaning combinations occur across collections; these remain edition-separated pending lineage review. The legacy data itself has4217 unique raw headword/entry pairs, with one repetition; none is counted as newly usable language supervision.

2,798 staged groups contain Arabic-script letters in the meaning. That identifies a review priority, not verified Persian gold. No automatic Persian target was generated from English/German/French meanings. Multiword dictionary forms, notes and attestations are not counted as attested sentence translations.

Both malformed CPD records preserve trailing meaning text outside `</entry>`. ID `8a25cd9aab91d28e0ee26362420a038d79c28d90` is `āzād`; its simplified JSON sense is only `I`. This same broken payload recurs unchanged in the larger receipt, supporting a persistent publisher-side markup problem rather than a truncated local download. ID `18e5fce7abcc6ac96b157109ffd59b462a3a1e65` mixes `-sālag` and `-sālagīh` scopes and leaves `..years).` after the root. Neither is silently repaired or converted from flattened JSON.

The new text-boundary guard caught one real NMP entry, `•2124×173-a`, with trailing `f` outside its sense. Original text is preserved in quarantine. AWN190 contains a meaning and citation9.1 but no source form; no source word is invented.

## Local resource integration

The output is a versioned staging resource, not a migration of the translator database or an append to training. The [project resource registration](../../data/kosh-staging.json) points to:

- `resources/local/kosh-quality-20260928/complete-v4/observations.jsonl`: all original records and status/provenance.
- `resources/local/kosh-quality-20260928/complete-v4/staged-groups.jsonl`: conservatively normalized groups for further review.
- `resources/local/kosh-quality-20260928/complete-v4/quarantine.jsonl`: original IDs and reasons.

Raw/source dictionaries are ignored local files; the tracked registry and receipts alone do not redistribute them. No source archive owned by the downloader was modified. Historical TRAIN, corpus exports and evaluation bytes remain untouched.

## Next acceptance gates

The dedicated Gemini Pro review has now run through the separately user-approved, user-launched access-repair workflow. Its main proposed German CPD patch was rejected after independent all-entry structural verification. See the [review disposition](../../data/unified-corpus/GEMINI-REVIEW.md). Gemini executed no independent accounting audit and did not certify meanings. Root independently executes any revised code and checks input/output identity. Source bibliography, per-entry language, sense correctness, edition/quotation lineage and intended-use scope still require qualification. Unknown lineage remains unknown; zero known collection flags is not clearance. Only a separately reviewed and frozen dataset can authorize the next training design.

The structural self-check exercises one shared form/sense scope, alternatives, the dangerous multiple-form/multiple-sense misjoin, missing labels, NFC and path/hash rejection. Full-pass reconciliation verifies every original record and coverage. These checks establish mechanical fidelity, not that every published meaning is correct. No additional model run is admitted by this checkpoint.

## Source coverage and follow-up

Subsequent local parser repair: `extract` now rejects non-whitespace container text/tails outside the recognized form/sense fields. Three counterexamples were reproduced before the fix; five regression cases now reject, while formatting whitespace is accepted. [Executed check](unscoped-text-check.json) verifies all9597 current-site dispositions are unchanged and no current staged observation has this pattern. V1/v2 outputs and TRAIN are unchanged. This small follow-up uses Classic Codex; the earlier critic reviewed the frozen v2, not this later code. The original v2 script remains in Git commit98aeaa6. Do not regenerate the frozen output directories with revised code.

Historical website fallback, superseded by the completed CLI review: the normal signed-in Gemini website visibly offers Pro. A bounded prompt with the prior parser excerpt, four published CPD examples and a schematic scope regression is prepared in Chrome. Automatic approval review blocked Send because it requires explicit approval for this payload and website destination beyond the earlier Antigravity task permission. The user has been asked for that exact authorization. No website model response or Gemini-authored curation is claimed, and no eligibility patch was executed.

The final manifest reconciles all38,686 catalogue IDs across31 dictionaries (30 populated, GPV0). Missing-trc searches recovered847 MMP and6 PYV records using XML-field queries; the AWN190 lookup supplies the remaining one. Matching catalogue counts is not evidence of complete coverage of every MPCorpus webpage/product or linguistic correctness.

Every original JSON field/value/array and full XML is preserved in each observation's `source_record`. The acquisition [field audit](../kosh-download-method-20260928/field-coverage.json) distinguishes21 advertised display fields from17 actually present JSON keys. XML-only transliterations, usage, examples, grammar, citations, readings, cross-references and evidence remain intact; absent fields are not invented. Catalogue authors/titles/Zotero/language labels are linked in `summary-v4.json` as provenance, not per-entry truth; ACP's English label conflicts with observed German meanings. English CPD has3,103 IDs and CPD_DE4,589, but usable form/sense grouping is a separate qualification step.

Historical summary field `expansion_new_record_ids` measures growth from v1's5,992 current-site records. Use `new_current_site_ids_since_v2` or `new_current_site_ids_since_v3` for the later baseline comparisons. Legacy counts are always separate.

## Checkpoint review

Mode: Classic + Critic. One independent read-only reviewer checks raw-field preservation and partition accounting; root is the only writer. No second implementation or paid run.

- Lead agent/request id: /root
- Critic agent/request id: /root/nllb_final_preflight_review
- Critic model and reasoning effort: inherited session configuration; no override
- Independent from lead: yes
- Evidence reviewed: frozen raw payloads, baseline and expansion receipts, legacy JSON/TSV/dump, stage.py, all four output versions and historical TRAIN
- Verification evidence: self-check and final-capture execution passed; verification-v4.json records independent all-field/ID checks; root rechecked output hashes/sizes/counts and TRAIN hash
- Critic verdict: pass

The critic's executed findings are recorded in verification-v4.json. This is a mechanical PASS, not linguistic approval. Root accepts this staging checkpoint only after that independent check; Gemini code/summary review is complete; per-entry linguistic qualification and training admission remain unfinished. The current [unified corpus](../../data/unified-corpus/README.md) integrates this frozen resource with the older data.
