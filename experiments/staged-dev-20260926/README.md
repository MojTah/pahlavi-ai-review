# Frozen provisional staged DEV panel — 26 September 2026

Status: **FROZEN FOR A DESCRIPTIVE EXPLORATORY SCREEN; NOT INDEPENDENTLY ADJUDICATED GOLD**. The panel contains **24 cases: 8 lexical, 8 composition, 8 new-text**. This directory remains local review material, not an upload/training bundle. No candidate-model output was used to choose the cases, references or constraints, and this task ran no inference. This file does not itself authorize a paid launch or change `stage_dev_ready`.

The minimal amendment retains the original 19 records byte-for-byte and appends exactly five natural composition cases. Stage 2 now combines three published grammar teaching examples with five natural passages. Four artificial matched contrast pairs are not required for this screen. Do not describe the eight probes as eight natural passages, a controlled minimal-pair experiment, or eight independent observations. The inherited `PROVISIONAL_REVIEW_CANDIDATE_NOT_APPROVED_FOR_SCORING` status in the original records is preserved as historical provenance; it is not silently promoted to expert gold. Descriptive evidence-supported observations must distinguish verified source constraints from pending constraints and unscorable meanings.

## Freeze and amendment boundary

- `candidates.jsonl` SHA256: `6cc3c34679b653d5e490dfaf22e6b84e321906847a0ab499ca8d31319da82df7`.
- Original 19-record byte prefix: 42,459 bytes; SHA256 `849f7d3f2371f2346660a39abf7e099fa3e67180cf8e3906ccfa596b2b9f0903`.
- Verified TRAIN payload: `resources/local/cloud-pilot-20260926-v3.zip`, inner `train.jsonl`, 2,484 rows; SHA256 `844a5b64d43a423b69d5989527a53273290a43be15c399056c979f5abb0678a1`.
- Record order is preserved: the original 19 records remain first, followed by S2-004 through S2-008. Read `stage`, not file position, when grouping.
- Inputs, raw references, review notes and the five new cases' `reference.allowable_readings_and_scoring_notes` are frozen together. For the original 19, the existing source layers and review notes define the current constraint boundary; null references remain null, and unresolved meanings remain unresolved. Any later change needs a dated revision and disclosure of whether model outputs were already seen. No outcome-driven replacement or selective retry is allowed.
- This completes the planned 24-case size. It adds no generations beyond the existing 78-output budget. Runtime sentinels, input-only export and launch authorization remain the lead's separately reviewed responsibilities.

## Five natural composition additions

| Panel ID | Corpus record | Exact local locator | Surface tokens seen in TRAIN |
|---|---|---|---:|
| S2-004 | parsig:120000008 | `corpus/120.json`, `chapters[0].paragraphs[8]` | 10/10 |
| S2-005 | parsig:138007005 | `corpus/138.json`, `chapters[6].paragraphs[4]` | 10/10 |
| S2-006 | parsig:152003071 | `corpus/152.json`, `chapters[3].paragraphs[71]` | 12/12 |
| S2-007 | parsig:152008011 | `corpus/152.json`, `chapters[8].paragraphs[11]` | 6/6 |
| S2-008 | parsig:152021007 | `corpus/152.json`, `chapters[21].paragraphs[7]` | 13/13 |

The `corpus/` paths above are relative to `sources/local/parsig-2026-09-20/`. Exact source-file hashes and published citation locators are in each record. The added cases cover coordination/negation, conditional permission, number and sequence, participant roles, and reported commands/addressees. The retained three primer cases have normalized surface-word coverage 4/4, 4/4 and 2/2, respectively; their original per-record review notes remain unchanged.

Lexical coverage is computed from actual TRAIN source text: remove a final bibliographic parenthesis containing a digit for lookup only; replace NBSP with space; split whitespace; apply NFC then casefold; strip boundary punctuation `.,;:!?*+[]()<>«»` and double quote. Internal hyphens and clitics remain; there is no lemmatization or semantic alignment. Lookup does not rewrite the model input. Each added case records per-token counts and up to two TRAIN witness IDs. **Surface exposure does not prove that the model learned a word's meaning or that every sense has an aligned lexical annotation.**

## Source and scoring limits

Stage 1 uses existing glossary/source-assisted lexical evidence with dictionary or edition locators. Its clear published facts may be checked against those sources without requiring a newly hired reviewer for every fact. The three primer examples are published teaching examples, not manuscript sentences; their KB Persian/English wording is a Codex study aid, so no invented target translation was added. Their original-page collation remains pending. An unverified constraint must not contribute a claimed gold-accuracy score.

The five new Stage 2 records and eight Stage 3 records copy authentic local corpus translations and editorial layers. Every record remains `expert_adjudicated=false`. The five new constraint lists are source-assisted evaluation design, not a specialist's adjudication or a new translation. Their source references have not been independently collated against every printed page in this task. Preserve editorial brackets and legitimate ambiguity. For example, S2-007 allows an unresolved “against him” rather than requiring an invented named antecedent. S2-006 requires forty years and the participants supported by the stored translation; it does not license extra mythological details.

For comparison, record whether each source-supported relationship was preserved, lost, reversed, or left uncertain, and record omissions, unsupported additions, and appropriate/inappropriate abstention. Report case-level before/after changes and fresh major errors, grouped by work family. Do not derive a universal success percentage or a causal adaptation/composition effect from this small, dependent, purposive panel. No unknown reading becomes true because the model states it confidently or agrees with another model. Genuinely disputed readings and newly proposed meanings require appropriate specialist judgment before a truth claim.

## Separation and leakage

`input` contains only instruction/source text, language/representation metadata, and currently-null allowed evidence context. `reference`, constraints, review notes, evidence locators and lexical/leakage diagnostics are review-only. **Never upload this whole JSONL to an inference endpoint.** The lead must create and inspect a separate input-only export; target-specific translations and editorial commentary cannot enter prompts or training.

All Stage 2/3 complete source texts, source record IDs and explicit Parsig works are absent from the checked TRAIN; complete stored Persian references are also absent after the stated whole-text normalization. Each new passage is absent even as a normalized contiguous substring of a longer TRAIN source. All candidate inputs pass the existing checksum-pinned PAL-REF guard; no candidate names protected works 104, 110, 116, 130 or 132. Frozen PAL-REF content was not used for selection. No TRAIN or benchmark file was edited.

The guard requires a nonempty work/record identity. For the nine dictionary/primer cases without Parsig work IDs, validation uses `local-source:<published-specialist evidence path>` and the panel ID, checking each published source separately (25 source checks over 24 cases). These are traceable bibliographic identities, not invented Parsig IDs. Passing the unadapted candidate row directly to the guard correctly fails for missing identity; the later input-only export must explicitly carry the same bibliographic identity. The original candidate metadata was preserved rather than silently rewritten.

These checks do **not** establish zero semantic overlap, zero related formulas, exhaustive edition-family separation, or absence from foundation pretraining. In particular, existing **S3-001 (`parsig:120000004`) parallels the peace/no-war counsel inside TRAIN `parsig:150000044`**. Preserve it as a familiar-content diagnostic; do not count it as evidence of novel composition/generalization. Proposed addition `120000005` was excluded because it also restates that TRAIN counsel. The new five received a bounded source/nearest-TRAIN review, not an exhaustive philological lineage audit.

Stage 2/3 include repeated work families. Group related passages and do not treat them as statistically independent. The two original Stage 3 complete-known-vocabulary candidates still require a full sense-level lexical audit; their label is provisional, not proof that all words or senses are known. Future training or retrieval must exclude selected evaluation works and derived target-specific copies. Stage 1 intentionally permits known-word training overlap and is a recall diagnostic.

## Validation and remaining limits

Completed: JSONL parse; 24 unique IDs and stage counts 8/8/8; exact preservation of the original 19-record prefix; source existence and SHA256 matches; raw source/translation equality for the five additions; all expert flags false; source-only input/reference separation; full surface-word coverage for the eight composition cases; current-TRAIN exact text/record/work/reference checks; new-input contiguous-substring checks; existing PAL-REF guard.

Not established: independently adjudicated gold; complete semantic lexical alignment; exhaustive template/edition lineage exclusion; foundation-pretraining nonexposure; accuracy on unknown decipherment; general translation quality; local runtime or cloud launch readiness. Source constraints still awaiting verification must be reported as such rather than converted into fabricated gold. This amendment removes the unnecessary four-pair requirement, not these factual limits.

Runnable structural check from repository root (standard library only):

```text
python -B -c "import json,pathlib,collections,hashlib; p=pathlib.Path('experiments/staged-dev-20260926/candidates.jsonl'); b=p.read_bytes(); r=[json.loads(x) for x in b.decode('utf-8').splitlines()]; assert len(r)==len({x['id'] for x in r})==24; assert collections.Counter(x['stage'] for x in r)=={1:8,2:8,3:8}; assert hashlib.sha256(b[:42459]).hexdigest()=='849f7d3f2371f2346660a39abf7e099fa3e67180cf8e3906ccfa596b2b9f0903'; assert all(x['expert_adjudicated'] is False and x['evidence'] for x in r); assert all(hashlib.sha256(pathlib.Path(e['path']).read_bytes()).hexdigest()==e['sha256'] for x in r for e in x['evidence']); print('PASS: 24 cases, stages 8/8/8, original 19 preserved; provisional evidence')"
```

Only `candidates.jsonl` and this README were edited by this amendment. No source corpus, training dataset, frozen benchmark, plan, launch contract, inference output or cloud resource changed.
