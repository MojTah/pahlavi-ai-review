# Study toward a Pahlavi translator

Mojtaba's intended outcome is a simple translator from **Pahlavi into Farsi and English**. Current authorization is to study the language and supplied resources. This note retains learning requirements; it is not an implementation specification or a training run.

## Preserve the evidence needed for translation

For each real passage, retain the following separately. These are proposed fields for our knowledge base, not a claim about the site's actual schema.

| Evidence | Why retain it? |
|---|---|
| Work, edition, witness and chapter/line | Find the passage again and distinguish dependent copies |
| Language, script and tradition | Avoid treating Parthian, Manichaean Middle Persian and Book Pahlavi as one uniform input |
| Exact supplied text or image pointer | Preserve the primary evidence and editorial damage marks |
| Transliteration and its convention | Record written signs without confusing them with pronunciation |
| Transcription and its convention | Record the proposed linguistic reading, including uncertainty |
| Token spans, stems, lemma candidates and grammatical analysis | Preserve clitics, compounds and alternative parses |
| Farsi translation and its author | Keep published reference translations separate from our drafts |
| English translation and its author | Evaluate this target independently of Farsi |
| Literal rendering and natural rendering | Make idiomatic additions visible |
| Alternatives, unresolved points and review history | Prevent a plausible guess from becoming an unquestioned label |
| Source access date and reuse terms | Track the version and provenance of usable material |

A dictionary gloss alone is not a sentence translation. A collection of spelling pairs alone is not a parallel corpus. The [Parsig-related file inspection](parsig-database.md) demonstrated why a one-to-one spelling lookup would discard useful alternatives.

## Questions to resolve through study

- Which resources provide connected passages with both target translations, and which only provide word meanings?
- Which genres, manuscript traditions and orthographic conventions are actually represented?
- How do editors mark damaged, supplied, uncertain or normalized text?
- How are verbal stems, agent clitics, auxiliaries, negation and compounds annotated?
- Which terms have specialized religious or legal meanings that familiar modern Persian cognates do not capture?
- Are apparently separate sources reproducing the same edition or translation?

The live database states that research use is free with attribution and retains a copyright notice. Its actual export facilities and permissions for later training or redistribution of each underlying edition, translation and image remain unestablished. A software repository's MIT license does not establish those permissions. See [live observations](parsig-live-study.md).

## Later validation requirements

This is a proposed evaluation approach, not an experiment already run.

Keep passages used for learning separate from future blind tests. Group duplicate editions and related witnesses together when splitting data, so memorizing a parallel copy cannot masquerade as translating unseen material. Report coverage by work and genre as well as by word count.

Assess spelling recovery, tokenization, grammatical analysis and target-language translation separately. For Farsi and English, check who did what, negation, tense/aspect, modality, names, technical vocabulary, and the handling of gaps. Fluency alone cannot establish fidelity. A smooth sentence can still reverse the agent or erase a prohibition.

Build a small expert-reviewed reference set before making accuracy claims. Record abstentions and competing readings. Do not infer that a model family is adequate, or inadequate, merely from a paper about a different processing task.

## Next concrete study

The [24 September review](review-2026-09-24.md) completes source-assisted reading of all 4,507 paragraph units in the saved 126-record Parsig snapshot. This supersedes the earlier five-record count. Next study should resolve flagged readings against critical editions, extend the manuals and dictionary work, and compare script with edited transcription. The [exact ledger](../sources/parsig-complete-study-2026-09-24.json) records coverage; it is not a translation-accuracy result.

The first live readings establish concrete constraints: mixed Middle Persian–Parthian records need language separation; supplied translations sometimes disagree; editorial brackets change search results; some text layers contain font-dependent encoding; and the same reader record may contain only selected or fragmentary material. Preserve these distinctions before any later data preparation.

## Requirements demonstrated by the five supplied PDFs

The [new study](supplied-pdf-study.md) provides concrete examples of the earlier requirements:

- **Dependent copies:** S24 and S26 are the same Nyberg work. Keep them together in any later training/evaluation split, despite different filenames, wrappers and hashes.
- **Edition conflicts:** Berk. 11 has a grīw/kabīz disagreement; Berk. 122 has a three/four disagreement across layers. Retain the source values and uncertainty, with any proposed correction stored separately.
- **Dates and quantities:** preserve regnal year, ruler, numeral reading, measure and local conversion assumptions. Do not overwrite them with a single CE year or modern unit.
- **Roles and modality:** distinguish giver, recipient and sealer; distinguish object agreement from agency; preserve necessity expressed by the construction.
- **Source dependence:** the Fārs paper cites Nyberg for rāmšahr. Multiple file references do not establish multiple independent attestations.
- **Rights and usable data:** the two papers display different noncommercial Creative Commons licenses, one also prohibiting derivatives. The books retain their own rights. Local reading permission is not a blanket training or redistribution license.

The new Farsi renderings are authored study drafts, not expert-validated reference translations. The [documentary examples](documentary-readings.md) should be reviewed before use in an evaluation set. No translator implementation or training was started.

## Review safeguards added on 24 September 2026

- Count a source field separately from a usable translation. Credit-only Farsi, empty XML divisions, Persian notes in transcription fields, and cross-unit translations are verified counterexamples in the collected data.
- Separate grammatical agreement from agency; the database's own note at Zādspram 8.1 explicitly illustrates plural object agreement with one sender. See [Grammar](grammar.md#past-transitive-clauses).
- Compare exact editions and spans. The [Kārnāmag study](karnamag-ii-iii-study.md) maps nonmatching chapter numbers and flags different participants, animals and places in the older English rendering.
- Distinguish extant text from secondary reconstruction. The [Xusrō/page edition](khusro-page-study.md) includes a Pahlavi rendering based on Arabic and a Persian version mediated through Arabic; these are not independent ancient witnesses or automatic sentence pairs.
- Retain possible polarity, numeral and role disagreements with unit IDs. A review flag is not permission to replace the source with an unverified correction.
- A reading pass supports familiarity and a durable knowledge base. It is not expert semantic validation. Studied examples cannot become a blind test merely by hiding their answers later; future evaluation needs genuinely independent source material and specialist adjudication.
