# Recovery follow-up: useful additions versus inflated counts

28 September 2026. The raw export remains SHA256 `c42e0a5a0d4d108218a0481ca073c07c6bb00cdcba0bffb462b67bb6d7a60789`; the [277-row join](provenance-recovery.json) remains `2bf5b6dd7f484ab5ca15e5e1dddf9f8001f26ae94656b3cfe7cce490b9464778`. Root inspected the110 source-edition and28 target-attribution exclusions. A separate critic inspected the13 shared-target records. No changes to source records, translation targets, curation policy, split, benchmark or admitted training data.

## Source-edition failures:110 accounted for

-95 are inscription records201–224.91 explicitly name Nasrollahzadeh in the Persian target. The other4 cite him only in notes:205012001/205013001/205032001 concern uncertain names;205030001 is heavily damaged and repeats parts of a known inscription formula. Those4 are not definite full-clause additions.
-11 are sequence-zero headings:508000000,509000000,514000000,518000000,521000000,525000000,528000000,530000000,533000000,537000000,548000000. Treat headings separately from whole-clause supervision.
-4 are running text:134008007 has an unfinished Anklesaria citation;137002020 has a doubled final parenthesis and cites Hajipour1400 as forthcoming;510000002 has a final space plus Armenian U+0559 after the complete Boyce1975 pp.44–45 citation;512000004 lacks a source citation.

For510000002, root ran the existing `pahlavi.curation.citation_parts` function in memory. Removing **only** that final space and U+0559 makes it recognize the existing Boyce citation. The Persian citation is already present. [Probe receipt](format-repair-probe.json) binds source/parser hashes and proposed strings; assertions verified the original fails citation recognition, the proposal returns exactly `(Boyce, 1975, pp.44-45).`, and raw bytes remain unchanged. This is an isolated metadata-format recovery candidate, not an edition or semantic validation and not an automatic training admission. No general regex relaxation was made.

## Target attribution:28 accounted for

One is the title150000000;16 are work151;11 are Manichaean535000004–535000012,537000003 and546000004. The latter introductions return only placeholder strings, not missing translator-credit evidence. Root verified their archived introduction hashes:535 `636ff5f0002fc20d683a34eeee62b0602bdc522f9b745dca7ea1006a348bdd20`;537 `8b64997c448d446d273ac5da8104d99c6c67533449e24988dcd664214bb210c3`;546 `820829ab00340566332c3f854ff06ddd6f4896b15a9649f610630c2306781ab5`.

Two work151 notes **explicitly say the sentences are absent from Tafazzoli's translation**:151035029 refers to1379 p.51,151039009 to p.54. Attributing them to Tafazzoli by inheriting surrounding citations would fabricate provenance. They need an actual identified translator or independently reviewed project annotation with that status, not an invented published credit. Other work151 rows still need individual page/translator confirmation. None has been discarded merely because its credit is incomplete.

## Shared targets:13 rows, five short groups

Independent critic `/root/nllb_final_preflight_review` verified all13 exported fields against raw publisher fields and excluded all16 held-out work families before comparing targets. It found plausible repetitions and lexical variants, not proven paragraph fragments to concatenate. Existing source/target normalization and original TRAIN identities were reused.

| IDs, prefix parsig: | Finding | Nonheldout raw occurrences / original TRAIN |
|---|---|---:|
|105000010,125000002 |Short colophon: `frazaft` versus `fazaft`; printed spelling needs review |2/0|
|106000000,107000000,108000000,125000000,128000000 |Invocation; `yazadān`, `yazad`, `yazdān` not automatically interchangeable; the principal form already exists in115000000 |6/1|
|106000010,108000013 |Colophon with one additional `ud`; plausible equivalent translation, not established mismatch |2/0|
|133000157,133000159 |`bēšōmandtar` versus `dardōmandtar` rendered by one Persian question; edition/context semantics unresolved |2/0|
|151027007,151045003 |Menog-i Xrad response formula; source differs only by comma |62/59|

Groups1–4 already cite Jamasp-Asana1913 pp.39–40,78,83,96 and Goshtasb/Hajipour1398; group5 cites Anklesaria1913 pp.95/131 and Tafazzoli1379 pp.47/59. The original curation preserves punctuation/diacritics, so it excludes some formula variants while retaining many others. This does not justify globally relaxing shared-target controls. Resolving these13 could preserve valid lexical/formula examples, but adds little independent compositional breadth.

Critic scope: reliable triage only, not expert certification or training admission. Original TRAIN SHA256 `3b3edf5550e95b13baaf9842ecaeaf53a50a0aa130d9a5dfe17d366ee62d7d43`; curation SHA256 `716094cfa3b50cd1f1701b714f099f6db0e94ea399fc504194f92cd484584be7`.

## Effect on the next action

The [consolidated coverage table](../../SOURCE-COVERAGE.md) now separates actual source opportunities from repeat counts and reference material. Prioritize missing edition evidence for authentic Persian clauses, complete S22 coverage and reliable lexical acquisition, and retain qualified non-Persian parallel material as a possible separately labeled auxiliary task. Do not fabricate Persian gold, silently inherit attribution, or retrain on each small recovery. All remaining [readiness gates](../../DATASET-READINESS.md) still apply.
