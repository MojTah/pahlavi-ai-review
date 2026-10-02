# Complete readable resource and partial source analysis

**1 October 2026: implemented and locally verified; no training or paid inference admitted.** Classic + Critic, one writer. This implements the local part of the [strategy decision](../strategy-reset-20261001/REPORT.md), including the user's request to remove unnecessary target structure and signs. The complete qualified inventory is available through lookup; this is not a claim that every translation is expert-certified or ready for optimization.

## What is ready

The separate v3 resource at `resources/local/usable-resource-v3-20261001/` contains all **9,973** qualified input groups, representing **10,145** original parents. Its **7,438** dictionary groups retain every source-scoped entry, supported sense, alternative, qualification, compound component and related form. The **2,535** nonlexical targets remain unchanged. The original seven held parents are still excluded. No original corpus, tokenizer, fixed benchmark, training configuration, checkpoint or evaluation output was changed.

| Task | Full available groups | Selected in the previous 1,536-row pilot |
|---|---:|---:|
| Historical Persian clauses | 2,232 | 1,152 |
| Persian lexical inventories | 2,606 | 96 |
| MacKenzie English inventories | 3,412 | 64 |
| Manichaean Middle Persian English inventories | 1,420 | 32 |
| Persian pedagogy | 240 | 131 |
| English documentary units | 53 | 53 |
| English edition spans | 4 | 4 |
| Persian inscriptions | 6 | 4 |
| **Total** | **9,973** | **1,536** |

This is the same qualified inventory in a more usable representation, **not newly acquired data or 9,973 new sentence translations**. No selection/exposure schedule is proposed here. The complete task/language/source-scope census is in [resource-manifest.json](resource-manifest.json). Source-scope counts do not establish independent work families.

The **Export and classify training sets** chat confirmed that all 64 selected CPD training answers contained JSON wrappers; the old lexical prompt requested JSON. Its spreadsheet display fix did not change those frozen labels. This implementation changes the separate derived lexical targets, rather than only the export display. The existing export helper was inspected; it could not be reused unchanged because it omits compound/related-form fields.

Simple target example:

```text
Form: ābādānīh
Meaning: prosperity, cultivation
```

The actual simple derived answer is exactly `prosperity, cultivation`. Complex inventories retain minimal readable entry/sense boundaries and typed qualifications. For example, `ēč` keeps `Grammar: with a negative; Meaning: not any`. Inflected forms retain their own meanings; `ōpastan` remains the form of which the headword is a past stem, with the published Old Shirazi qualification. A compound's component meanings are never assigned to unrelated isolated headwords. All matching scopes/languages are returned by exact lookup; no preferred meaning is selected automatically.

## Target cleanup and its limit

JSON storage keys/braces are removed from every derived lexical answer. Archival targets and full provenance remain in `dictionary.jsonl` and the derived projections. Each nonempty lexical string leaf has a source path and an exact output mapping, or an explicit structural-role disposition. Output/source offsets are Unicode code points, end exclusive.

- **1,362** MMP whole-gloss quotation pairs removed across **1,357** groups; full contents and final punctuation preserved.
- **23** exact CPD leaves lose enclosing parentheses while keeping their grammar/usage scope. [Decisions](punctuation-decisions.json) bind ID, path, text and kind.
- **9** redundant outer periods removed from those reviewed leaves: eight transitivity abbreviations and one inches-unit abbreviation. Internal periods remain.
- Interior parentheses, uncertain readings, optional participants, alternative meanings, reconstructions and documentary damage/supplied markers remain. Removing their contents would change supervision. `final(ly)` and `rise (sun)` are not disposable decoration.

Across the full lexical pool, old supervised content has **177,445** tokens; the new standalone reader targets have **38,527**. Old counts are decoded from the pinned actual labels; new counts exclude the chat prompt and end tokens. This measures answer formatting overhead, not training speed, gradient balance or an expected quality gain. Every previous full-pool example had two supervised terminal tokens, counted separately in the manifest. The actual prior selected stream and later four-pass exposure remain historical evidence.

`target-audit.jsonl` records remaining marker flags for every row. Flags do not mean the translation is wrong. A separate [named review ledger](pending-target-review.json) holds **11** specific rows from the next clean translation-training proposal: seven historical delimiter cases, three documentary fragment cases and one CPD spacing case. The original release and full lookup remain intact. The CPD `abus` raw XML was re-read: `(woman)havingjust given birth` is already upstream. No unverified spacing or sense correction was invented. The printed entry and fragment conventions still need checking. The ledger is a preparation decision, not an implemented cloud admission gate or a newly certified release.

**Do not substitute these plain targets into the old JSON-requesting training prompt.** Any later training must freeze a matching lexical instruction, retokenize complete prompts/answers, check masks/terminators/limits, choose task exposure and loss explicitly, resolve the review ledger, and pass the existing independent Astra/human launch gate. Those steps, semantic certification and model-quality validation have not run. No new training-ready claim follows from mechanical preservation.

## Source-analysis preparation

[Candidate ledger](analysis-candidates.json) and the local source-only view preserve **15** S22 construction candidates linked to exact source spans, PDF/image hashes and printed grammar prose. The source view contains no Persian translation targets. [Checker](check_analysis.py) verifies identities, bounds and prior exposure. Examples include agent/patient agreement, zero auxiliary, agentless constructions, perfect/past-perfect and optional patients.

These are **one textbook lineage, zero complete pilot cases**. Fourteen were selected previously; `S22EXP-003` was not in that selected stream but is in the full qualified pool. They are familiar development candidates, not unseen confirmation. The first/second-person clitic labels additionally cite the agent paradigm on PDF79–80/printed76–77; their primary example page is not the sole support. The constructions are project annotations grounded in published prose, not published exhaustive dependency parses or specialist-certified analyses.

The five Parsig noun/lemma occurrences are partial lexical evidence only. Earlier directive/contrast labels use target witnesses and cannot supply independent analysis. The four S23 scopes are fragments/elliptical predicates within one archive lineage, with English targets and incomplete analyses. `S22EXP-009` remains pending precise PDF82 prose binding. None pads the four-family requirement.

The planned 24-case/three-condition inference pilot is therefore **held before payment**. Missing prerequisites are independently supported complete occurrence analyses from additional work families, qualified reference/split status and prospective component/safety/decision rules. New annotations must add source-bound information beyond earlier S04/S07/generic assistance; no novelty admission is claimed here. If only pedagogical evidence can be obtained, revise the research question explicitly before freezing a familiar-development diagnosis. Do not silently fill the panel from model guesses, target-derived relations or repeated paradigms.

## Reproduce

Use the already installed project/science interpreter; no installs or model files are needed:

```powershell
& '[USER_HOME]\.venvs\codex-science\Scripts\python.exe' -B -X utf8 experiments/usable-resource-20261001/test_resource.py
& '[USER_HOME]\.venvs\codex-science\Scripts\python.exe' -B -X utf8 experiments/usable-resource-20261001/prepare.py --check
& '[USER_HOME]\.venvs\codex-science\Scripts\python.exe' -B -X utf8 experiments/usable-resource-20261001/check_analysis.py
& '[USER_HOME]\.venvs\codex-science\Scripts\python.exe' -B -X utf8 experiments/usable-resource-20261001/prepare.py --lookup 'ābādānīh'
```

Build without `--check` only in a fresh versioned output directory; it refuses overwriting. Lookup is deliberately exact/case-sensitive and returns complete matching records. No guessed lemmatization or fuzzy sense selection is added. JSONL scanning covers 7,438 groups without a database or retrieval framework.

[Independent review](REVIEW.md) passes bounded rendering/preservation and partial source-evidence preparation. No expert semantic audit, full new prompt/tokenization, GPU execution, training, model download, credential/Drive access or app Goal change occurred. Bulk source-derived data remain ignored local study artifacts; qualification is not a public redistribution license.
