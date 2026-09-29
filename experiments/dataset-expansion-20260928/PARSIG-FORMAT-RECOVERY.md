# Four Parsig format-recovery candidates — 28 September 2026

Status: **provisional AI qualification; zero training admissions**. The four existing review dispositions are preserved. These are existing published Persian translations, not newly generated targets. Only the candidate JSONL and this note were produced.

## Exact scope and dispositions

| ID | Existing disposition | Preserved qualification |
|---|---|---|
| 151043031 | FORMAT_RECOVERY_CANDIDATE | Ten men's eating/satiety align provisionally. Keep leading conjunction and terminal comma; one linked clause is not independent sentence certification. |
| 151015025 | QUALIFIED_FORMAT_RECOVERY | Keep `*wizōstan` and `nē abāyēd`. The prior examination reading is context-supported; lack of necessity must not silently become prohibition. |
| 150000054 | QUALIFIED_FORMAT_RECOVERY | Keep literal `<pad>`, `*be šud`, all brackets and the disputed `tēmās` note. The separate English lost-wealth clause is not merged with the Persian. |
| 510000002 | CITATION_FORMAT_RECOVERY | Isolate final space plus U+0559 after the Boyce citation. Preserve names, kinship wording, dialogue, oath, negation and questions. |

## Preservation and provenance

The JSONL stores each complete exported source/target field verbatim, plus exact citation-free `source_text` and `target_text`. Source/target bodies are exact contiguous prefixes: only their explicitly recorded trailing citation wrappers are separated. Raw fields reconstruct exactly from body, separator, citation and source trailer. No spelling, whitespace, Unicode, punctuation, ancient text or target meaning was normalized. Credits remain metadata and do not enter `target_text`.

Each row records its export line, byte offset, exact line hash, publisher response file/hash, response-array index and raw Code. All four archived response hashes were recomputed; each selected raw publisher unit equals `raw_source_unit`, and its Transcription/Translation fields equal the exported fields exactly. The frozen export hash is `c42e0a5a0d4d108218a0481ca073c07c6bb00cdcba0bffb462b67bb6d7a60789`.

Inline credits are Anklesaria 1913 p.129 / Tafazzoli 1379 p.58; Anklesaria p.65 / Tafazzoli p.38; Dhabhar 1930 pp.8–9 / Goshtasb–Hajipour 1392 p.78; and Boyce 1975 pp.44–45 / Mostafavi Kashani 1401. Exact original citation strings, publisher notes, language scope, alignment qualification and rights are retained per row. Printed edition pages were not inspected. Publisher paragraph association is not specialist sentence alignment.

## Reversible view recommendations

For the three `<pad>` passages, authoritative source text retains literal `<pad>`. A separate display-only view uses `⟨pad⟩` at the recorded codepoint span; inverse substitution recovers the exact source body. This is not a selected training serialization or a tokenizer validation. Merely escaping angle brackets inside JSON would restore the collision when decoded.

For 510000002, a proposed citation-wrapper view removes only final U+0020 plus U+0559. Appending them recovers the original exactly. The existing parser-probe receipt is preserved as evidence; its before/after source-string hashes were independently reproduced here, but the parser was not reexecuted. The ancient source body and Persian target are unchanged.

## Validation and limits

Executed checks: four unique requested IDs; exact response/export field equality; raw file/line/field hashes; reversible source/target citation separation; inverse display patches; absence of target credits from `target_text`; and unchanged frozen export bytes after writing. No DEV/TEST answers, training artifacts or original source files were altered; no network or cloud request was made.

The nonheldout scope follows the prior content audit and the lead's four-ID selection. This pass does not independently clear work/manuscript lineage, rights, token limits, use permissions or all admission gates. All records remain `STAGED_NOT_TRAIN_ADMITTED` with `admission: false`.

Candidate JSONL SHA256: `f4dbc011c80bc7616f9f31c9ff46db0cc938aadc7c47fd7ae1e94ceba45042aa`.
