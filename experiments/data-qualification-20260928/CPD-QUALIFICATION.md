# Generic English CPD sense inventories: qualification component

28 September 2026. This component produces **3,506 source-qualified inventory units pending independent review**, and holds **720 units**. These are complete publisher-block sense inventories, not 3,506 new words, sentence translations, independent attestations or final training admissions. Root owns release integration, duplication/split checks and independent review. Training additions remain zero.

## Frozen inputs and output contract

`cpd_qualify.py` verifies the prior extractor, all 42,904 source observations, the English corrected MacKenzie PDF and historical TRAIN2237 against hard-coded SHA256 values. It processes only the 3,103 current English CPD observations. The prior extraction yields 4,224 ordered form/sense blocks in 3,101 well-formed entries; two malformed entries remain separately held. Qualified3506 + held720 = 4226 accounted units. The code never repairs original XML or updates an earlier artifact.

Output directory: `resources/local/data-qualification-20260928/cpd/`.

- `qualified.jsonl`: complete form bundles, all direct ordered senses, explicit grammar/usage, English targets, source observation/block/XML paths and hash pointers. It excludes etymological/comparative evidence and quoted examples from the supervision view. This is a proposed lexical component, not an admitted training dataset.
- `held.jsonl`: every other block or malformed entry, with reasons and source pointers. Reasons overlap; no meaning is guessed to remove a hold.
- `correction-checks.jsonl`: 54 explicit generic-form/sense checks against visually read corrections, including the three unresolved results.
- `manifest.json`: completion receipt written last, with code/input/output hashes, counts and limits. Existing output directory causes refusal before processing; no overwrite route is supplied.

API: `build()` returns `(qualified, held, correction_checks, summary)` without writing. Running the script without arguments executes the pinned-source checks and prints a summary. `--write` freezes outputs once. Import has no data read or write side effects. Use the shared `codex-science` Python with `-B`.

## Qualification rules actually applied

Keep all direct senses together, including printed sense order/numbers, definitions, grammar and usage. Keep comma/stem strings and complete source bundles intact. Never form the Cartesian product of spellings and meanings. Different same-spelling entries remain separate attributed inventories; downstream grouping must preserve their relationship rather than select one winner. Complete here means the entire scoped publisher block, not proof that all historical senses or other editions have been discovered.

The following require holds: unresolved multiple form elements or multiple transcription nodes; missing source/gloss; uncertain/reconstructed/damaged forms or senses; unresolved language labels; semantic markup whose flattening would change scope; entry notes needing review; dangling XML links; and known correction-scope mismatches. A reference is considered mechanically resolved only when its exact target names an actual `xml:id`; no fuzzy matching or cross-reference substitution supplies a missing meaning. This conservative rule can retain recoverable material in holds.

Direct generic translation/definition text is preserved exactly, including permitted inline italic text. POS/usage components remain structured, not concatenated onto the gloss. Examples and context nodes stay inspectable in the frozen source via paths but are excluded from the proposed supervision view. Inline semantic cross-references and complex usage stay held instead of silently deleting essential meaning. No printed sense is dropped merely to make an otherwise ambiguous inventory pass. No English meaning is translated into invented Persian gold.

Three complete source bundles receive narrow printed-evidence exceptions: `hūkar`/`hūkarag`, `bahr`/`bahrag`, and `bahrwar`/`bahragwar`. The correction pages explicitly print the corresponding optional-ending forms. They remain one bundled inventory each, not several independent examples. Other multiple-form associations remain unresolved, including `wihēz`/`wihēzag`.

## MacKenzie correction cross-check

Primary source: `sources/local/mackenzie-pdf-20260928/english-1986.pdf`, SHA256 `594421d8c58e3f6b0ae169e383ae2917fe7572ac53fe568350b1b4ea62b1e091`. All four correction-page images, PDF19–22, were read directly using the existing rendered images. This supplements the source identity and `xrad` evidence in `experiments/mackenzie-access-20260928/README.md`.

The 54 exact generic checks reconcile to **51 matches and three added-sense/scope mismatches** in the pinned full XML. Matched examples include: `hūkar(ag)` porcupine, explicitly not hedgehog; `mizīdan` suck; `sneh` club/weapon rather than sword; `ēkānag` loyal/faithful; `pad-nigerišn` carefully; and corrected added meanings for `agār`, `āštīh`, `baxtan`, `buland`, `čimīg`, `drubušt`, `kardagān`, `mānīg`, `mayānǰīg`, `padist`, `purnāy`, `xwarg` and others listed in the machine-readable checks. Match means the specified printed correction is represented; it is not a full page-by-page validation of the entire entry.

| Held main form | Correction page | Current XML main inventory | Why held |
|---|---:|---|---|
| guftār |20|speaker|Correction adds eloquence for the headword/derivative family; the derivative guftārīh has it, but the main inventory does not. Exact applicability needs original entry/edition adjudication.|
| nēk |21|good, beautiful|Benefit appears under nēkīh, not the main form. Preserve this unresolved correction scope rather than manufacture a new sense.|
| niyāz |21|need, want, misery|Necessity appears under niyāzōmandīh, not the main form. Same unresolved scope issue.|

The three `wiyābān` headword inventories are additionally held because PDF22's confusing-sense addition has uncertain scope across homographs; the explicit derivative `wiyābānīg` passes its separate literal check. These are review holds, not claims that every current headword definition is demonstrably wrong.

Eighteen exact obsolete/replaced headword checks found none present in the current snapshot, including `xūkar`, `xūg`, `mēzīdan`, `mādayār`, `karbunag`, `karxōš`, and `wizāštan`. This is a local complete-snapshot check, not a claim of current live-site absence. No live API queries were required.

Scope limitation: this pass explicitly checks selected generic meaning/headword changes. It does not certify every transliteration, comparative-language spelling, Pahlavi key, English reverse-index amendment or typographical correction on those pages. Such evidence is omitted from the supervision view, while the raw source remains authoritative. An unlisted source error can still exist; no claim of error-free data is made.

## Held-unit counts

| Reason | Units |
|---|---:|
| Unresolved form/sense association |266|
| No direct sense |260|
| Uncertain/damaged form |117|
| Semantic inline markup |35|
| No generic gloss in a sense |24|
| Uncertain/damaged sense |22|
| Explicit language requires separate pool |19|
| Sense reference/note review |13|
| Dangling XML cross-reference |12|
| Added-sense correction scope unresolved |6|
| Unscoped sense-tail text |5|
| Generic correction mismatch |3|
| Entry note review |3|
| Complex block grammar/usage |2|
| Malformed XML |2|
| Missing source form |2|
| Complex grammar |1|

Counts overlap and must not be summed as independent rejected records. Two malformed entries are held whole; no source-supported repair was made.

## Executed checks and limits

Local execution takes approximately two seconds and uses no network, external model, GPU or new package. Tests cover `xrad` wisdom/reason versus derivative wise; the unresolved two-form/three-sense `wihēz` entry; retention of all source sense counts; the corrected hūkar bundle; absence of obsolete/held correction forms from the passing pool; grammar/usage without embedded examples; all 4,226 unique disposition IDs; input/source pins and unchanged historical TRAIN. The first command exposed Windows stdout encoding only; explicit UTF-8 output resolved it before freezing any result.

Qualification here concerns source-supported **generic lexical supervision**. Dictionary vocabulary may overlap benchmark words, so these resources cannot support an unseen-vocabulary claim. Authentic quotations and document-level passage use still require independent work/witness clearance; none is created by a dictionary match. This component does not establish a new license, public redistribution permission, a final train/dev/test split or specialist certification. Root must review and reconcile the component before any use.

## Related-source flags requested by root

The same pinned CPD XML gives `kāstan, kāh-` → `diminish, decrease, lessen` (observation `kosh:cpd:cdaeccbe4bee4be525d16b0797c64b95ec1ae0f0`), supporting review of DK8's `کاشتن، کاهش دادن`; it does not authorize inventing a replacement Persian target. No exact `apōhišn` or `apōhišndārīh` match was found. CPD has related but differently spelled `hu-fraward` → `blessed, the late` under observation `kosh:cpd:5a2cb022a8addd32b3f64445e00442fc4a881a8b`; that does not settle RAF's `hu-frawand` spelling or its `محروم` gloss. Their printed source pages remain necessary.
