# Independent grounded-supervision review

27 September 2026. **PASS for this bounded preparation checkpoint.** Five occurrence-specific lexical glosses and fifteen local directive-function proposals are provisionally acceptable for auxiliary development. One directive occurrence remains an abstention. These are AI-reviewed, source-qualified proposals, not expert gold, general dictionary entries, complete grammatical analyses or authorization for a training run. The proposal files remain unchanged and unadmitted; a separate lead-owned decision must preserve these limits.

## Direct verification

Executed with `resources/local/hf-client-venv/Scripts/python.exe -B -X utf8`:

- `scripts/prepare_grounded_lexical.py --check` exited0: exact five-record/two-work rebuild, four negative checks, packet SHA256 `60fc03d2b93549e31435f06b1011d570802654572c5a0099004ca5339d461a83`, zero training admissions.
- An additional in-memory check rejected changed source text, a quarantined ledger disposition, a held-out work, an embedded substring instead of the exact headword, a changed source citation and a changed translation citation. No evidence file was modified for these tests.
- Independently validated all2,237 qualified TRAIN rows against the existing frozen ledger and all16 held-out work IDs. Checked all1,019 inventory record texts, full ledger objects, raw-line byte locations/hashes and7,040 retained source/target span and UTF-8 coordinate checks. Recomputed the declared occurrence/distinct-row/work and per-work counts for all seven table subsets; they matched. This establishes retained-artifact integrity and count consistency, not exhaustive linguistic recognition or correctness of every surface candidate.
- Independently checked all directive input hashes, deterministic shortest-row selection,12 rows/12 works,16 unique occurrence IDs,79 exact source/target span and UTF-8 coordinate checks, original text and complete qualification/ledger preservation. All15 proposal states and the single abstention matched; eight rows are at most160 source characters, and each longer selected row is its work's only standalone-ma row.

The generator's parent identity removes the final three occurrence-ID digits and binds the result to the exact qualified TRAIN record. Displayed context comparison collapses whitespace only, to accommodate highlight spacing; citations must match literally. The saved original source and target strings are unchanged. Every selected headword has exactly one word-boundary-safe occurrence. The full existing ledger travels with each record. The excluded119000001 occurrence is neither substituted nor admitted, and no held-out work enters these packets.

Code inspection confirms that the new generator reads only the pinned TRAIN, ledger, held-out inventory and frozen publisher-transcription file. Importing the prior helper does not execute its build function or read its dictionary drafts. The helper was inspected at its recorded hash. No DEV/TEST answer, model output, source repair or new translation is used in this lexical binding.

## Publisher evidence and lexical decisions

The publisher file is correctly described as a **lead transcription of visible UI text**, not a raw API capture. Its local immutable bytes and their consistency with TRAIN are independently verifiable. The actual website dialog transcription, occurrence-number display and original observation cannot be independently replayed from these local files; my acceptance retains that evidence limit. The anonymous401 is recorded by the lead, not independently requested here. No credential retry, browser or network operation occurred in this review. The displayed reuse notice is not a blanket license for all underlying editions.

The following accepts apply only to the exact occurrence's verbatim `translation1`. They do not independently validate every publisher metadata field.

| Occurrence ID | Exact form and source range | Provisional decision | Qualification |
| --- | --- | --- | --- |
|107000001004|`xrad` [16,20) → خرد|ACCEPT contextual gloss|Keep the cited lack-of-wisdom context; no exhaustive sense inventory.|
|107000003004|`frazand` [14,21) → فرزند|ACCEPT contextual gloss|Occurrence-specific gloss only.|
|107000004004|`xwāstag` [14,21) → خواسته، ثروت، دارایی|ACCEPT published gloss string|The parallel translation uses ثروت; the list is a publisher gloss, not three independently aligned token senses.|
|107000006006|`ruwān` [25,30) → روان|ACCEPT contextual gloss with existing qualification|The passage's care-of-the-soul explanation is explicitly interpretive; it does not change the gloss or establish a universal phrase meaning.|
|119000002009|`hunsandīh` [68,77) → خرسندی، قناعت|ACCEPT occurrence gloss with existing qualification|Retain reconstructed numeral/elliptical-clause qualifications. The recorded lemma is `hunsand`; this review does not approve a lemma/derivation target from that field or transfer the annotation from quarantined119000001.|

All five lexical records retain `expert_adjudicated:false` and `training_admitted:false`. Their saved pending-review status is historical proposal state; this separate review supplies a scoped decision without overwriting the proposals.

## Independently inspected grammar evidence

I viewed the complete local rendered pages `primer-083.png` (printed80), `primer-086.png` (printed83), and `nyberg-290.png` (printed281), and checked the full source PDF hashes.

- S22 printed80 explicitly supports `ma` for prohibition; printed83 distinguishes it from `nē` negation. This supports a contextual negative-directive function, not automatic polarity for adjacent clauses.
- S22 printed80's footnote and Nyberg printed281 §§5.6–5.7 support caution about unique mood inference. A surface ending alone is insufficient for the proposed universal imperative label.
- S22 printed83 and Nyberg printed281 §5.8 support nominal as well as modal-predicate uses of `-išn`; §§5.9–5.11 add further constructions. An `išn` substring is not an obligation label.

I did not newly inspect all other pages cited in `SCHOLARLY-GRAMMAR-CHECK.md`, nor certify its broader agent/patient and passive claims. Those broader claims create no accepted auxiliary labels in this checkpoint. Neither book's illustrative passages are admitted to TRAIN by this review.

## Directive decisions

I read each selected full source and unchanged Persian witness, then the proposed local ranges. All decisions below concern **negative-directive function within the stated context**, not a verb's lexical gloss, unique morphology, complete clause semantics or independent correctness of the entire translation. IDs below append the occurrence suffix to the original `parsig:<record>:pal>fa` TRAIN ID.

| Record / occurrence | Decision | Reason and retained boundary |
| --- | --- | --- |
|109000005 / ma1|ACCEPT provisional|The stealing prohibition is separate from the preceding positive contentment instruction.|
|134002003 / ma1|ACCEPT provisional|Local quoted prohibition on concealment; preserve reporting context.|
|134002003 / ma2|ACCEPT provisional|Keep the exception phrase within the teaching prohibition; no universal sense for `paywand` is inferred.|
|136001015 / ma1|ACCEPT provisional|A negative request inside reported speech; the narrative request itself is not negated.|
|150000053 / ma1|ACCEPT provisional|The local ridicule prohibition does not negate neighboring positive instructions.|
|150000053 / ma2|ACCEPT provisional|The bad-disposition prohibition is local; supplied Persian `[خويش]` remains editorial.|
|151001020 / ma1|ACCEPT provisional|The short prohibition is supported; idiomatic Persian does not establish a lexical equivalent for `bar`.|
|509000001 / ma1|ACCEPT provisional|The reported command not to come here is distinct from the instruction to remain there.|
|511000001 / ma1|ACCEPT provisional|Local negative exhortation remains distinct from the preceding wish; existing gaps and explanatory gloss survive.|
|515000002 / ma1|ACCEPT provisional function only|`andarz`, the `ma hēb bawēnd` context and Persian witness support reported negative advice. Do not relabel its finite morphology as imperative, optative or jussive.|
|515000002 / ma2|ACCEPT provisional function only|The reciprocal negative advice is supported locally; final damage and unresolved finite mood remain.|
|521000003 / ma1|ACCEPT provisional|Negative petition is supported; positive adjacent requests and addressee identity are outside this decision.|
|550000001 / ma1|ACCEPT provisional|Retain the frequency restriction; do not convert this to an unconditional prohibition of all oaths.|
|550000001 / ma2|ACCEPT provisional|Separate negative directive about imposing an oath on another; no unique mood inference from the ending.|
|551000002 / ma1|ABSTAIN|Retain uncertainty over the reported third-person warning/wish/directive and following subordinate scope. Do not turn its general `ma` rule into a positive label.|
|555000002 / ma1|ACCEPT minimal scope only|The local prayer-related prohibition is supported. The following coordinated phrase may extend its scope; `minimal_supported_scope_only` must not be converted into an exhaustive scope boundary or a negative label on that continuation. Initial damage survives.|

Thus fifteen local function labels across eleven works can receive provisional auxiliary-development qualification, with one explicit abstention. Their diversity is a selected twelve-row pilot, not evidence that all63 standalone occurrences or any model generalization are correct. The five lexical glosses plus fifteen functions are twenty narrow provisional labels, not twenty fully corrected translations. The inventory's1,040 `išn` occurrences and numeral matches remain unlabeled candidates.

All fifteen accepted directive examples contain `ma`. This pilot has no independently accepted assertion or positive-command contrast labels. It therefore cannot establish directive discrimination, rule out a particle shortcut, or by itself justify a training batch. Mentioning adjacent positive clauses as scope exclusions is not equivalent to independently annotating a contrast set.

## Frozen artifact identities

| Artifact | SHA256 |
| --- | --- |
| `scripts/prepare_grounded_lexical.py` | `f438e9bedb27b71b9c9a11f65d34c013c95a05e1bcfa21a2e1201bde6be5b500` |
| Imported `scripts/prepare_lexical_feasibility.py` | `d1fba3afed539bb9ccdcdf2de61af3e44aa8fabb6ae87b635d666e9b5bf9165e` |
| `published-occurrences.json` | `dcd0c41b66cc17623426b0d49da7cbad6a9efa576479bdaf4afd244eacc93301` |
| `lexical-packet.jsonl` | `60fc03d2b93549e31435f06b1011d570802654572c5a0099004ca5339d461a83` |
| `inventory.json` | `5eead36cf1b422da43779759faa795d611a5a955322521e6f737babb2cac2d7c` |
| `TRAIN-INVENTORY.md` | `fc8e1d38a7072fc11038a49739728ed605d6e829c88b739f5561d869f3cdfceb` |
| `SCHOLARLY-GRAMMAR-CHECK.md` | `ecf5c6e9ee1bf2458e46b5645a5e1cbdc4e6daf40b8485e81e9cfd37f8715bd7` |
| `DIRECTIVE-PILOT.json` | `c74482c97eff39759356c44ddb6c1f3a4b21c3dcf0a4ff34c484e4e554db4cf9` |
| `DIRECTIVE-PILOT.md` | `de70b95a21af648100649806b8c5484d654218b4a4f97bb536fa902e2e207d33` |
| Qualified TRAIN | `15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc` |
| Final ledger | `d79af2e64fbb92954c8b8d0ed9cb7a34e7e7d24d4c22ea9c22f1da6d569a8e77` |
| Held-out inventory | `7eba461256dfcf44e324dde31d2b119cac1b4fae866ca0a53e705217389ba060` |
| S22 full source PDF | `207aeda5eae48227902f0f208f9b24fd5623627dd4ca589b217268e69596df92` |
| S24 full source PDF | `d49aaebbe1f51ebc07c616f538ff40a2a8d7ae9c3b810836c65689ab8a50f8c9` |
| `primer-083.png` | `86ca3789c452c38c5ac5fcc8def4cc7973906b14c9c9fff5e831d4b4a9e9685a` |
| `primer-086.png` | `2903160e6eda4f26b0022e6a1772900434845617e9507f2d3a0696cd0114125b` |
| `nyberg-290.png` | `2232cc788eccf8ef8f37a2b5474c0a1ed1278646895b01cadda84d868fb714c9` |

## AutoCode Critic record

- Mode: Classic + Critic.
- Lead agent/request id: /root
- Critic agent/request id: /root/final_external_judge
- Critic model and reasoning effort: inherited session settings, no override
- Independent from lead: yes
- Critic verdict: pass
- Evidence reviewed: The exact artifacts and hashes above, all five lexical bindings, all sixteen directive proposals/abstention, qualified TRAIN/ledger/heldout identities, and three independently viewed source-page images.
- Verification evidence: Actual generator --check exit0; six additional in-memory rejection checks; direct all2,237-row qualification and1,019-record/7,040-span inventory integrity check; independent12-row/16-occurrence/79-span directive validation; per-label provisional semantic review and retained abstention. No network, browser, credentials, cloud, model, installation, benchmark changes, source repairs or edits outside this review.

No mechanical blocker was found. Expert accuracy, publisher UI transcription fidelity, exhaustive grammatical scope, legal rights beyond the observed notice and model benefit remain unproven. This scoped pass keeps the fixed benchmark unchanged and does not authorize paid training.

Validation: `validate-autocode-gate.ps1 -Mode Critic -Path experiments/grounded-supervision-20260927/REVIEW.md` exited0 with `AutoCode Critic gate passed`.
