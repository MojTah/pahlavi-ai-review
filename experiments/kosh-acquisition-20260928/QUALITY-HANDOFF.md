# Local dictionary cleaning: bounded worker handoff

28 September 2026. The user directed this chat to focus on clean, correct data and selected Antigravity to use their Gemini allowance for heavier work. Another chat owns site downloads. This file prepares the exact local task; it does not claim a Gemini run has started or authorize credential handling/installations.

Dispatch update: the user separately approved official CLI installation and normal account use for this task. Installation succeeded, but the actual Gemini request returned a location-eligibility error before a model turn; [receipt](antigravity-dispatch.json) reports zero token usage. No worker outputs exist. The CLI prompt narrowed the task to file authoring only, with root responsible for executing/reviewing checks; no broad permission bypass was enabled. Further attempts await a legitimate available access route.

## Task and ownership

Produce a reproducible, conservative **staging** dataset from the three already acquired structured dictionaries. Preserve original readings, complete form/meaning groups, all provenance and uncertainties. Do not download, train, invent Persian targets or declare scholarly certification. Root integrates and independently reviews; the worker owns only the two new output directories below. Do not modify shared project state or source files.

- Workspace: `[USER_HOME]\Documents\ChatGPT\Pahlavi language`.
- Runtime: `[USER_HOME]\.venvs\codex-science\Scripts\python.exe`; stdlib is sufficient. No installs or new framework.
- Allowed writes: `experiments/kosh-quality-20260928/` for one small cleaning script, summary and runnable self-check; `resources/local/kosh-quality-20260928/` for staged/quarantine records. Check for pre-existing work and stop if another writer owns these paths.
- Forbidden: downloads/site access, credentials, Drive/email, paid/cloud jobs, model weights, benchmark or historical training changes, Git commits, outside-directory edits, other agents and lifecycle hooks.
- Initial timebox: one bounded local pass, expected under ten minutes. Report a blocker instead of retry loops or scope expansion. No network or billing is needed.

## Frozen inputs

Use the **tracked** `experiments/kosh-acquisition-20260928/acquisition-report.json`, SHA256 `075d3c4d7043ce10ab08aaa2e638af67735c48cc621bd2659bef91c42607dea3`. Do not follow a newer mutable acquisition report from the downloading chat.

Successful raw payloads are under `sources/local/public-texts-2026-09-20/kosh-all-dictionaries-20260928/`, at each receipt's `file`. Verify size and SHA256 before reading. Constrain resolved paths to that archive. Count only these successful collections: `acpv1_7`2602, `afnan`324, `awn`366. Other collections are absent, not empty. Do not open DEV/TEST answer files. The prior [novelty census](novelty-summary.json) already compares source spellings with TRAIN; do not redo or reinterpret it as semantic novelty.

## Independent local audit findings

`/root/finetuning_kb_research` verified all payload hashes and parsed every XML record. These findings guide implementation but must be checked by its executable assertions:

| Collection | Actual structure | Known quality issues |
|---|---|---|
| `acpv1_7` | All2602 have direct children `trc`, `sense`, `attest_with_avestan`, `attest_without_avestan` |20 placeholder meanings:17 `_`,2 `?`,1 `(?)`. All2602 Avestan-attestation fields nonempty; the other attestation field empty. |
| `afnan` | All324 have exactly one `entry/form` containing its own `trc` and `sense` |No missing meaning;135 comma-containing form strings and one semicolon-containing string must stay grouped. |
| `awn` | One `entry/trc` containing alternative `form` children; optional root `sense`, `citation`, `trl` |9 missing meanings.225 single-form,139 two-form and2 three-form entries;203 citations;56 `trl` elements omitted by simplified JSON. |

After NFC and whitespace normalization, JSON transcriptions match XML for all3292 entries. Eight ACP strings differ before NFC due to composed/decomposed `ē`. Preserve original strings and diacritics; normalization keys must not replace source evidence.

The audit found1746 ACP,323 Afnan and366 AWN distinct normalized **complete form-group + entire sense** combinations, including missing/placeholder meanings. Thus857 repeated rows collapse within collections, retaining every source ID and citation. These are textual duplicates, not proof of identical scholarly meaning or novel attestations. There are74 ACP,7 Afnan and1 AWN form groups with differing meanings: preserve separate senses and flag for review; polysemy is not automatically an error.

None has an explicit aligned sentence/example translation structure. No meaning contains Persian/Arabic-script characters or XML language attributes. Samples show German ACP glosses and English Afnan/AWN glosses; record these as collection-level evidence/hints, not independently verified language labels for every row.

## Required transformation

1. Validate input identity and the three observed XML schemas. Reject/quarantine unrecognized or ambiguous structures. Never globally join all descendant forms to all descendant senses: the known `xrad` specimen shows that this can attach an adjective meaning to a noun.
2. Preserve each complete ordered form group and its associated complete sense. Do not split comma/slash/parenthesis strings, expand variants, reconstruct text, translate targets or discard bracketed evidence.
3. Separate missing/placeholder meanings into a quarantine output with source IDs and explicit reasons. Preserve all originals; nothing is deleted.
4. Deduplicate only identical normalized full form-group + full meaning within the same collection and language evidence. Retain all original entry IDs, citations, raw-file hashes and XML locators for a merged row. Do not merge different meanings or editions because they look similar.
5. Preserve transliteration, attestations, citations and uncertainty evidence separately. Avestan attestations are not Pahlavi inputs; locators are not translation targets. Do not count multiword headwords as full-sentence translations.
6. Mark every output `STAGED_NOT_TRAIN_ADMITTED`, lineage unresolved and expert certification false. Meaning and language validation, source rights/use status and frozen-split lineage checks remain separate gates.
7. Emit a compact summary: input totals, quarantines by reason, duplicates collapsed, staged groups, source/meaning conflicts, and before/after **admitted** counts (historical2237 unchanged, new0). Bind code/input/output hashes and ensure every original ID is accounted for exactly once in staging or quarantine provenance.

## Lineage findings and unresolved evidence

Independent reader `/root/nllb_source_method` checked local source catalogues and TRAIN provenance. No collection is cleared for training:

- ACP: Cantera, Pahlavi Vidēvdād1–7, German meanings and separate Avestan evidence. Exact edition/digitization provenance is absent from responses. Establish bibliography and possible liturgical passage overlap; TRAIN contains113 work301 Zand Yasna rows.
- Afnan: philosophical lexicon with English meanings, no per-entry citations or edition metadata. Verify the historical/terminological layer and exact edition/pages before classifying attestation.
- AWN: Ardāwirāznāmag, English meanings and partial chapter-like citations. No numeric Parsig-work mapping is established. Work115 is the marriage contract, **not AWN**; work117 is Khusro and the Page. The existing TITUS Arda audit also leaves it unmapped. Do not turn absence of a mapping into split clearance; exclusions124/517 remain incompletely identified.

## Verification and return format

Leave one runnable self-check: demonstrate the three supported schemas, placeholder/missing quarantine, NFC preservation, complete alternative groups, duplicate provenance retention, rejection of the `xrad`-style independent-group misjoin, and path/hash mismatch rejection. Run it, then one real local pass. No full repeated audits after unchanged checks pass.

Return: `PASS`, `PARTIAL` or `FAIL`; exact output paths and hashes; counts with reconciled input-ID coverage; failures/ambiguities; what remains for admission. PASS means faithful mechanical cleaning only. Root will review the outputs before accepting the checkpoint. Do not change the established evaluation or claim the final training set has grown.
