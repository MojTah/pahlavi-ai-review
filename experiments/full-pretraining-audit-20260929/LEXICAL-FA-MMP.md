# Full Persian and Manichaean lexical audit, 2026-09-29

**Disposition: HOLD before another training release.** The archived words were transferred faithfully, but the current complete-inventory prompts do not distinguish all source entries. Correct extraction alone does not establish a coherent learning target.

Reviewer: `/root/lexical_full_audit`. This task used only existing local evidence and the Python standard library. No training, model inference, cloud jobs, paid service, network, credentials, installs, source changes or Git operations were performed.

## Coverage and reproducibility

Run `[USER_HOME]\.venvs\codex-science\Scripts\python.exe -B -X utf8 experiments/full-pretraining-audit-20260929/lexical_fa_mmp_check.py` from the project root. The independent script does not import the qualification builder. It writes only the accompanying metadata audit JSON.

| Coverage | Result |
|---|---:|
| Released Persian inventories | 2,676 / 2,676 |
| Released Manichaean Middle Persian inventories | 1,426 / 1,426 |
| Raw archived XML observations compared | 4,142 |
| Original response files verified by SHA-256 | 7 |
| Prepared pool rows reconciled | 4,101 |
| Rows selected in the last 1,536-example run | 128 |
| Declared form/target/source-scope/grammar fidelity | 4,102 passed |
| Different-target prompt collisions | 71 groups / 146 rows |

Every released record has a coverage ledger entry with ID, source locator, raw XML hash, target hash, prepared-pool presence and selected position. All input hashes are in `lexical-fa-mmp-audit.json`; it contains no bulk forms, senses or XML. The 4,102 to 4,101 difference is the expected duplicate MMP entries 1030/1267: the same `ēr` input and the same English target. Entry 1030 was selected at position 1,485; entry 1267 was removed by exact deduplication.

For every Persian row, all source pointers were joined directly to the original response's entry ID. XML matched the frozen observation exactly; NFC/whitespace-normalized form bundles and the **whole** plain-text sense matched the released record. No nested sense was flattened. Source collection, declared language, attribution, source scope and stratum were reconciled to the original lexical resource. **None of the Persian rows has an XML grammar field**: grammar was not accidentally dropped by the release exporter.

For every MMP row, direct XML language is exactly `MP`; complete form bundles, exact grammar and all selected sense spans matched. Included and excluded spans account for the entire original meaning without gaps or overlap. Grammar is preserved with its original Unicode representation; MMP 1444 has a valid decomposed diacritic, not corrupt text. Damaged/private-use characters and unexpected format controls were screened across every released learning object, with no findings. All Persian targets contain Persian/Arabic-script text and have balanced parentheses and brackets. These checks establish fidelity, not whether the dictionary itself is philologically correct.

## Confirmed issue: complete-inventory prompts have multiple different gold targets

The audit grouped the complete learning input: task, full form bundle, source scope, stratum, target/source language and MMP grammatical role. It also verified equality of the already prepared prompt SHA-256 values. This is stronger than merely finding repeated surface words.

- Persian: **66 groups, 136 rows**.
- MMP: **5 groups, 10 rows**.
- All 71 groups were read. The JSON records a disposition for every group: distinct published sense/grammatical role, or overlapping wording/expanded inventory. Both categories matter because the instruction asks for one **complete** inventory while each row provides only its separate entry's target.

Brief source-backed examples:

| Archived entries | Same visible input | Different published target scope |
|---|---|---|
| `kosh:dmx:182`, `kosh:dmx:200` | `ēwārag`, same source | «دور» versus «عصر» |
| `kosh:dmx:196`, `kosh:dmx:242` | `may`, same source | wine versus prohibitive particle |
| `kosh:dmx:395`, `kosh:dmx:396` | `dānēd`, same source | indicative versus imperative |
| `kosh:dmx:678`, `kosh:dmx:679` | `puhl`, same source | bridge versus punishment |
| `kosh:mmp:911`, `kosh:mmp:912` | `ōx`, noun, same source | existence/life versus mind |
| `kosh:mmp:4345`, `kosh:mmp:4346` | `rōy`, noun, same source | face versus copper/brass |

This **does not show that one meaning is false**. Homonyms and multiple meanings are legitimate. It shows that the prompt lacks an entry discriminator and the answer fails to represent the entire set requested by the prompt. For example, synonyms «بی سود» and «بی فایده» are not contradictions; they still should not be counted as separate independent complete-inventory targets without an explicit policy.

**Required repair before reuse:** for each identical full input, preserve source-entry boundaries and all supported alternatives in one reviewed inventory, or provide a meaningful grammatical/contextual discriminator that is available at inference. Do not pick a majority meaning, silently drop senses, or pretend an arbitrary record ID supplies linguistic context. Keep original data immutable and version the derived learning projection. A unique-complete-prompt check must then reject any remaining unadjudicated target collision.

### What this can and cannot explain about the previous run

Only **two** of these 146 collision rows were actually selected: `kosh:gbd:626` at example 61 (update 4, slot 13) and `kosh:gbd:527` at example 478 (update 30, slot 14). **No conflicting group had two alternatives consumed by that run.** These collisions are a real full-pool readiness defect, but there is no evidence that contradictory updates from these pairs caused the observed regression. Increasing dataset size would make exposure more likely unless the projection is repaired.

## Meaning versus dictionary notes

All **148** long/annotated Persian targets caught by the declared scan were read. All **544** excluded MMP tails were read, alongside selected scopes and the complex grammar entries. The screen preserves multi-sense numbering, inflectional roles, semantic qualifiers, contextual labels and legitimate alternatives. Punctuation such as `perhaps` and interrogative `when?` in MMP denotes actual meanings in their respective entries; these are not grounds to invent a correction.

**17 Persian targets include Latin etymologies or embedded related forms.** They are source-faithful, not translation hallucinations. IDs: `da:3,42,56,58,59,68,69,76,83,84,85,96,101`; `dmx:107,550`; `yz:13,70` (all prefixed `kosh:`). These strings mix definitions, derivations and grammar notes. If the task remains exact dictionary-entry reproduction, that must be stated. If it is meaning prediction/translation, preserve these notes in a separate typed field rather than teaching them as undifferentiated Persian output.

- `kosh:da:68` includes an out-of-record “previous word” reference. It was consumed at example **782** (update 49, slot 14). The core definition is not demonstrated wrong, but the cross-reference is incomplete in a standalone example. Resolve it from the exact source as a typed note, or hold the row; do not guess.
- `kosh:dmx:550` mixes an infinitive's numbered senses with two additional inflected forms and their meanings inside the same flat target. All text matches XML. Preserve these subordinate form-to-meaning associations explicitly before any sentence-translation reuse; do not attach the inflected translations directly to the infinitive.
- MMP `3127` and `4217` retain a `[Boyce]` attribution; `4856` retains a `Cf.` cross-reference inside the target. None was selected in the last run. These are source labels, not extra senses. Separate them as metadata in a cleaned dictionary task; no claim that the core English meanings are wrong.

The 544 removed MMP tails are bibliography, cross-references, etymology, spelling/attestation observations or source comparison. No additional generic sense was shown to be lost. Important examined distinctions: MMP 2758 retains the demonic qualifier in the selected gloss; MMP 5127 retains both transitive/intransitive roles in the grammatical input; 1266's discarded quoted words describe the Aramaic donor, not an extra MP sense. Late/dialect and spelling notes (e.g. 2049, 2561, 2726, 4175, 5623, 5720) remain available in provenance; use them if the future task requires that distinction.

## Remaining limits

This is an all-record **source-fidelity** audit plus an independent full collision/flag/tail review, not an expert retranslation of 4,102 inventories from manuscripts or printed dictionary pages. The unflagged entries have not each received a fresh philologist's semantic judgment. Archived Kosh transcription can itself contain an error; raw-byte agreement would faithfully reproduce it. No test can establish that every possible training/runtime failure is impossible. The new prompt-scope gate and explicit annotation policy address concrete defects revealed here; learning efficacy, whole-phrase composition, model runtime and generalization remain separate tests under the user's training hold.
