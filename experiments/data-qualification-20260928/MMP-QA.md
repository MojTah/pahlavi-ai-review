# Independent QA of the MMP qualification decisions

Date: 2026-09-28. Critic: `/root/blind_dev72_a`; qualification writer: `/root/nllb_source_method`.

**RESULT: PASS for the frozen component qualification contract: 1,426 generic lexical inventories qualified and 564 held, with all 1,990 declared recovered entries reconciled. No blocking correction was found.** This approves the bounded source-scope decisions for integration under their field allowlist. It does not approve training, establish rights for an intended use, clear manuscript passages, certify expert truth, or validate a future exporter.

## Review method and frozen evidence

I read `ADMISSION-REVIEW.md`, `PLAN.md`, the frozen `MMP-REVIEW.md`, and the decision schema. I independently joined all 1,990 recovered records to the full archived XML and original observations and checked every qualified span. Semantic QA was a targeted independent sample, not a second manual semantic adjudication of all 1,990 entries. The writer's report describes its full compact-field reading; that claim is kept distinct from my executed checks.

| Artifact | SHA256 |
|---|---|
| `mmp-review.json` | `dc3728781a28591d592eb696dec3f96723b9daea267ba2eb2c3e0a58de0d33f8` |
| `MMP-REVIEW.md` | `05c99692e4db61dfc394ae047da00ecca8db62cd4d6961d84cbfcbeb853a6b53` |
| `resources/local/dataset-expansion-20260928/lexicon-v1/lexical-resources.jsonl` | `3f963c94c00f79cf8c04421fcd55a539649c1b2a62eb4ac029ae195c1d73871c` |
| `resources/local/kosh-quality-20260928/complete-v4/observations.jsonl` | `3b0b14ce6e6520ad801839388d7362596c0cdfd1480f1a5b63d378071c0c1a65` |
| Full response `sources/local/public-texts-2026-09-20/kosh-xml-gaps-20260928/raw/329562c1d69f9b0c34e87420392df4dfd348c6ac90afe7062cd3e91a96b4ae0c.source` | `ce1b476f41a3faa004b863fb98a61eeb8b1a472ea43604c30a9f96b7690192a3` |

These hashes were recalculated during this QA. Attribution remains Durkin-Meisterernst's *Dictionary of Manichean Middle Persian and Parthian*, represented by the pinned Kosh XML. This review did not compare the entire dictionary with original print pages.

## Executed full-scope checks

- The raw response has 5,837 unique entry IDs. Exactly the declared 1,990 recovered MMP IDs are in this review; Parthian, shared-language and other dictionary shapes were not silently included.
- The qualified list, qualified scope records and held map have unique IDs. Qualified and held sets are disjoint, cover all 1,990 recovered IDs exactly, and contain 1,426 and 564 entries respectively. There is no unprocessed remainder within this declared subset.
- Every recovered entry has exactly one direct XML language node equal to `MP`, one transcription bundle and one plain-text sense node. Every recovered form list matches its XML list exactly, in order. Every original observation XML string matches the archived response XML for that ID.
- All recovered meanings match XML after NFC/whitespace normalization for this comparison only. The actual qualified offsets were checked against the immutable lexical string without normalization. Normalization is not permission to move offsets or rewrite a target.
- All 1,426 one-based source-line locators, original-meaning hashes and XML hashes match. Each selected half-open Unicode code-point span is in bounds and reconstructs `expected_complete_selected_text` exactly. Selected and excluded spans account for the full original meaning string without overlap or unexplained loss.
- Every qualified POS/context string equals the corresponding XML `gramm` text exactly. All qualified entries have grammar. No qualified form bundle contains the tested unresolved-form signs `?`, `*`, `[` or `]`; the qualified target question mark was separately inspected below.
- All 44 qualified multiple-form bundles remain one inventory each; the contract retains every form in order. No form-by-sense Cartesian expansion occurs in this artifact. All per-scope admission flags are false.
- No selected target contains XML entry/sense/attestation markup or the raw attestation separator. The contract excludes `attest`, `see`, `trl`, full XML, raw-record serialization and excluded paratext from learning payloads. This is a checked decision contract, not an executed canonical-exporter test.

One harmless representation difference was checked explicitly: entry 1444's flattened JSON grammar uses precomposed `ḫ`, while its XML has decomposed `ḫ`. The decision preserves the exact XML spelling, as claimed; these are canonically equivalent. No correction is needed.

## Independent semantic and scope samples

I inspected all 44 qualified multiple-form bundles, the complex cases below, every qualified unusual grammar string identified by length or contextual-marker filters, and **117 of the 544 excluded-tail cases** selected by quotation, uncertainty, language, usage and cross-reference cues. That tail sample included selected text, complete omitted tail, forms and grammar. I also inspected long and uncertain source cases that the writer held. These are purposeful risk samples, not a random quality estimate or an exhaustive semantic pass.

| IDs (suffix of `recovered:kosh:mmp:`) | Finding |
|---|---|
| 5, 5418; all 44 multiple-form records | Full variant bundles survive. 5418 retains size/greatness, plural great things and Grandee status together. |
| 231 | The published alternative meanings remain alternatives; neither is selected as the sole winning gloss. |
| 398 | Both transitive and intransitive senses survive. The omitted tail supplies references and a comparative form, not an omitted generic English sense. |
| 531, 679, 2428, 2662 | Adjectival/name/astronomical, collective, pronoun/article and astronomical roles remain in the selected inventory. |
| 3990, 4387, 4903, 4904 | Explicit second meanings remain present with source numbering; the source's `1.` in grammar must remain with the target's `2.`. |
| 111, 4445, 4812 | Grammar carries essential impersonal, inflected-form or coin/weight context. Their qualification is conditional on retaining that context, not on presenting a bare word-to-gloss mapping. |
| 836, 3006, 1958, 2311 | “Perhaps”, interrogative punctuation and meanings about doubt are lexical content, not unresolved reading flags. |
| 1266, 1444, 3077, 4667 | Borrowing, foreign comparison or explicit MP-context information does not silently change the source language. The target remains the published English inventory; foreign comparison material is not made into an extra target. |
| 2758 | The selected gloss retains its demonic-use qualification; the excluded tail's fuller label does not hide an additional sense. |
| 303, 568, 887, 917, 969 | The holds appropriately avoid clipping additional construction, role or language scope down to a first gloss. |
| 476, 688, 1781, 2256, 3344, 4503, 4959, 5554, 5759 | Longer contextual/alternative/disputed discussions stay held rather than masquerading as complete generic inventories. |
| 752, 1797, 2845, 3955, 5113 | The source uncertainty/dispute is substantive; the hold is appropriate. |
| 196, 2230, 2831, 3809 | Spelling, vocalization, transitivity or attestation concerns remain unresolved and held. |
| 1769, 1834 | Cross-reference or conditional-language material supplies no self-contained generic target. |
| 3055, 3602 | Grammar reveals abbreviation/name context that prevents an unqualified ordinary-lemma mapping. |
| 3004, 3937, 4925, 4832 | Additional components in grammar supply meaning absent from the short headword bundle. Holding these prevents compound-to-part leakage. |
| 4983, 5583 | Known published English spelling defects are retained as repair tasks; parser fidelity alone does not clear them. |

The 117-tail sample found no omitted additional generic sense requiring a new hold. It includes many simple references, separately entered derivatives, comparative languages and etymologies; those are not automatically additional meanings of the current form. Conversely, known second interpretations and unsafe compound associations remain held. This supports the per-ID decisions; it does not license a general first-quote or first-sentence truncation rule.

## Protected-context and language boundaries

Entries 4874 and 5457 remain held. I inspected their source discussions but do not reproduce their contextual quotation here. The former's Book of Giants reference remains unresolved rather than being asserted to equal protected work 517; the latter explicitly discusses Šābuhragān and a disputed identity. Neither enters the selected payload.

Entry 4590 is a useful negative case: the dictionary's generic patronymic/title formation `šābuhragān`, with `a. (patr.)` and its two literal formation meanings, may remain qualified as lexical evidence. A protected-work title appearing as a dictionary headword does not itself turn the generic formation into an excerpt. This **does not clear any Šābuhragān passage, quotation, translation or retrieval context**. Likewise, entry 5 has manuscript attestations in its raw XML, but only its generic particle inventory and grammar are in the allowlist. Never serialize its raw record to obtain a learning input.

The bounded finding is **no identified protected quotation or context-dependent protected interpretation in the inspected qualified scopes under these checks**. It is not universal contamination freedom or clearance of the full MMP dictionary. The complete 16-family protection policy remains in force; overlap of common dictionary vocabulary with evaluation vocabulary cannot support an unseen-vocabulary claim. Actual protected aliases and provenance in any later joined context still require the release guard. No benchmark answers were opened for this review.

## Integration conditions and completion

Keep exact target spans, complete form bundles, original POS/grammar, Manichaean Middle Persian domain and source pointers. Keep evidence-only tails and raw XML out of both targets and retrieval/serialization payloads unless separately cleared. Source pointers are metadata, not permission to pull their entire contents into a model input. Retain all 564 holds and their reasons; no hold was overturned by this QA. Targets remain English, with no generated Persian counterpart.

The component may proceed to canonical integration under that contract. The final exporter, source-family/duplicate counts, protected metadata guards, rights for the intended use and frozen historical/evaluation receipts remain root's separate release checks. I did not independently reopen or hash historical TRAIN or answer-bearing benchmarks here; the writer's historical hash claim is not recast as my execution evidence. No model training or performance claim follows from this PASS.

Only `MMP-QA.md` was written by this critic. No data, code, source, original qualification decision or benchmark file was modified; no network, external model or GPU was used.
