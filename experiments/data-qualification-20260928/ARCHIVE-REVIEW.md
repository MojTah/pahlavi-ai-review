# Independent archive qualification review

Reviewer: `/root/nllb_source_method`, separate from the archive implementer `/root/seen20_blind_b`. Local review on 2026-09-28. No network, training, benchmark answers, source edits or generated translations were used. Only this review file was written.

## Verdict

**PASS as bounded source-correspondence evidence, with two known target spelling defects requiring a release disposition and mandatory export constraints below.** This is not unconditional admission of all 57 units as clean or certain translation targets. The frozen evidence packet itself need not be rewritten: a canonical release can hold affected units or make explicit, reversible source-backed correction overlays.

I read every proposed source/English pair: 19 whole passages and 38 fragments, including quantities, dates, participants, negation, surviving clauses, alternatives and editorial additions. They represent **52 witnesses**, not 57 independent documents or sentences. The complete packet contains 71 units from 53 witnesses; 14 are held contexts. One witness, IEDC1263, has no proposed qualified unit. IEDC1270 has a usable recto and a separately held empty verso.

## Concrete release findings

1. **`openampd:MP0416:full`, target:** `Spandaimad` differs from source `Spandarmad`. The implementer explicitly identifies it as a spelling artifact. The source and target locate the same fifth day, so it must not become a learned alternative calendar name. Proposal: hold this unit from the clean release, or record an exact `Spandaimad` → `Spandarmad` correction overlay citing the source layer and preserving the original target. Do not silently change the frozen packet.
2. **`openampd:MP0046:full`, target:** `transction` is an evident English spelling defect. It does not change the transaction's quantities or alignment, but a release advertised as clean should either record the exact English spelling correction `transction` → `transaction` or keep the uncorrected unit out of the clean target view. The raw target remains evidence.

Neither finding licenses correction of uncertain source readings, technical vocabulary or differences that might reflect genuine interpretation. For example, `hutuxšān` → “scribes” in MP2561 remains an edition-specific interpretation, not a general lexical equivalence.

## Export boundary gate

All selected `source.text` / `target.text` strings reproduce their explicit selection boundaries. However, `context_lines` deliberately retains complete boundary lines for review. **Never serialize entire qualified JSON objects or `context_lines` into learning text.** The following nine side fields contain text outside the accepted selection:

| Unit | Side | Characters outside selected text |
|---|---|---:|
| MP1029:dateline | source | 85 |
| MP1029:dateline | target | 329 |
| MP1027:dateline | source | 360 |
| MP1027:dateline | target | 495 |
| MP1026:address | source | 31 |
| MP1026:address | target | 35 |
| MP0003:provision-clause | target | 30 |
| MP0439:ration-heading | source | 12 |
| MP0439:ration-heading | target | 29 |

These are evidence-only continuations, not additional accepted context. They include disputed legal bodies, the rejected closing in MP0003, and the excluded ration continuation in MP0439. Use selected `.text` for selected units, preserve their scope locator and a separate uncertainty annotation, and retain full evidence only through non-learning provenance pointers.

For whole block/folio units, preserve block/face boundaries. For TEI lines use `text_with_uncertainty_markup`, **not bare `text`**: bare text loses empty gaps and the distinction between supplied/unclear and readable words. Oxford brackets, alternatives, question marks and folio identities must likewise survive. Reviewer findings, raw XML/HTML, bibliography and full context are evidence fields, not extra translation targets.

All 14 `HELD` rows have `qualification_is_content_evidence=false`; all 71 rows retain `train_admitted=false`. Selecting only non-held dispositions is necessary but does not replace the explicit field whitelist or the spelling dispositions above.

## Substantive checks and qualifications

- MP1027's mismatched body quantities and names stay in held context; only its matching dateline is selected. MP1029 similarly excludes its conflicting land descriptions and `quotaNote` token.
- MP0071's “no coherent translation possible” statement is outside the accepted lines 1–3. It must not become a translation target.
- MP0067 excludes the unrendered 50-grīw item; the one sheep / 36 lambs line and the separate verso have matching scope.
- MP0439 excludes the supplied English daily quantity 4; the selected date/ration heading does not invent this number.
- MP0437's 31 is split across source lines as 30 + 1. Its account totals and separately positioned 2 drahm are compatible with the published target. No false 30/31 mismatch was asserted.
- MP1023's years 103 and 102 occur on both sides; retaining this edition inconsistency is different from silently harmonizing it. The duplicated `[the scribe]` is an explicit editorial token, not a second participant.
- MP0410's separate recipients, commodities, prices and totals remain distinct. IEDC1062 preserves its stated total and uncertain `30 [gerd] [?]`; the review did not invent a corrected amount.
- MP2500 retains `(dād)//mard` despite the English choosing a man interpretation. MP5652, MP6003, IEDC1262, IEDC1265 and IEDC1040 contain source-side uncertainty not repeated identically in English. These can only be presented as annotated edition interpretations, with the source uncertainty and alternatives attached. They are not certain targets for an unqualified translation task.
- IEDC1266 contains little more than a restored personal name and bread amid ellipses. It is a sparse lexical fragment, not a complete proposition or an additional full sentence. MP0003's `rāst` endorsement and MP1026's sender endorsement likewise remain short contextual units.
- “Whole passage” describes selection scope, not certainty or completeness of a larger contract. MP0410 explicitly refers to an earlier contract; MP0085 preserves questioned itinerary readings.

No additional unequivocal quantity or named-participant mismatch was found in the 57 selected units. This bounded result is not a specialist rereading of all manuscripts, and it does not settle ambiguous legal grammar or edition-specific technical senses.

## Lineage and overlap

All packet witness identities, the 16 metadata-only held-out exclusions, original credits and alias metadata were preserved verbatim. Cross-archive matches point to metadata-only Oxford records (`has_pair=false`), rather than being counted as new independent translations. Multiple selected fragments and faces of a witness retain the same witness group.

I visually checked the existing images `s23-pdf21.png`, `s23-pdf25.png` and `s25-pdf9.png` under `resources/local/data-qualification-20260928/archive/`. They confirm the Berk.32 comparison, Berk.43C title glyph and Berk.62 numeral context, respectively, and the Asefi2023a bibliography entry. These comparisons are not new independent attestations. Other cited S23 pages were not independently rendered in this review. The exact/whole-unit source comparison against historical TRAIN reports no duplicates; that does not prove absence of formulaic, fuzzy, partial or quotation overlap.

## Executed verification

An independent in-memory Python check, without importing or replaying the writer's output-writing script, verified:

- all 53 raw source receipts match their hashes;
- all 57 qualified units / 114 sides match the frozen packet fields;
- all 92 Berkeley sides retain original XML fragments and fragment hashes; independently parsed text and uncertainty markup agree;
- all 22 Oxford sides retain the exact original folio HTML and independently extracted list text;
- each selected span follows its declared unique start/end boundary;
- provenance work identities, witness groups and held-out metadata remain identical;
- 7 unclear, 13 supplied and 26 gap marker occurrences across accepted source/target representations survive;
- 14 held contexts are not marked as qualified content evidence;
- historical TRAIN remains at its fixed hash.

Execution completed with `PASS`, exit 0, about 0.4 seconds. The full writer script was inspected but not executed because it writes outputs. No claim about a future canonical exporter is made before that exporter is exercised.

Frozen archive JSONL SHA256: `051b4644ef0a4613f48232b9149398242a953f19726f36670919b10eb320019c`.

Frozen input packet SHA256: `fe2e80cbb323b2072c673fb0e715dba8d100f670bad9fbaf975b4b3b2ddba48d`.

Historical TRAIN SHA256: `15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc`.

Rights and intended-use authorization remain separate from this semantic/extraction review. No training admission, performance claim or guaranteed correctness claim follows from this report.

## Addendum: explicit derived spelling overlay approved

On 2026-09-28, I independently reread the complete selected source and English text for `openampd:MP0046:full` and `openampd:MP0416:full`, then checked `archive-derived-decisions.json`. **PASS for these two exact derived-target repairs only:**

- MP0046: `transction` → `transaction`, exactly one occurrence in target line 10. This inserts the missing English `a`; the transaction, negated further demand, quantities and surrounding interpretation are unchanged.
- MP0416: `Spandaimad` → `Spandarmad`, exactly one occurrence in the target's line-3 reference. Source transcription line 3 explicitly reads `Spandarmad ī māh Mihr ī sā[l ...]`. Replacing `i` with `r` makes the corresponding named calendar day agree with that source transcription; it is not a new manuscript reading or a correction of the uncertain year.

The approved overlay SHA256 is `189ec7c27b4667bb8b73e12d91e8fefd838ecbd051a97ec9668acfa030564baa`. The frozen archive packet remains `051b4644ef0a4613f48232b9149398242a953f19726f36670919b10eb320019c`.

An independent, read-only in-memory check passed the exact two-ID scope, declared substitutions and single-occurrence counts; reversible character-only differences; unchanged numeral sequences, gap/supplied markup, brackets, parentheses, question marks and tentative asterisks; both original raw-source receipt hashes; and unchanged archive and MMP overlay hashes. No corrected source packet was written. The two affected units may therefore remain in the derived release **as annotated fragments**, under the export-boundary constraints above. Their lacunae, restoration and other uncertainty remain unresolved; this addendum does not turn them into certain complete translations or authorize training.
