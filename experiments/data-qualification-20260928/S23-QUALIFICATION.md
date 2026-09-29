# S23: bounded Hastijan source qualification

Result: four main editions preserved as four held full-document parents, with **four nonredundant proposed source-bound scopes**, one already-covered sealing formula occurrence, and one restricted provision clause. Independent visual review is pending. Training additions remain zero. The four proposed additions comprise two predicate scopes and two complete temporal-phrase fragments; they are not four complete independent sentences.

Writer: `/root/blind_dev72_b`. Source: Nima Asefi (2025), “Ewer, Garden and Gardening: An Edition of Berk.25 and Revised Readings of Berlin26, Berk.11, and Berk.122 Documents Belonging to the Pahlavi Archive of Hastijan,” *Journal of Iranian Linguistics*2(1),6–29, DOI10.46991/jil/2025.01.01. The exact supplied PDF is `sources/01+-+Nima+Asefi.pdf`,28pages, SHA256 `480670343730bdac72d1af78ff699d8cca69d71b908472a890c9ea1f51c6a1ce`.

## Preserved source and proposed boundaries

The main tables were read visually at PDF8/printed9, PDF14/printed15, PDF20/printed21 and PDF23/printed24. Relevant commentary at PDF8–9,12,14–18,20–25 was read; principal risk statements were also image-checked. `kb/supplied-pdf-study.md` and the source-backed documentary notes supplied locators, but no study-note paraphrase or Persian translation was used as a target.

Each JSONL parent preserves all numbered MP transcription lines and the complete associated published English block, including unresolved names, reconstruction punctuation and known contradictions. Published Aramaic transliteration is not substituted for MP transcription. Exact parent character spans, line labels, PDF/print pages, PDF hash and image hashes bind each nested scope. The original PDF/page images remain authoritative for typography.

Whitespace and line breaks are normalized; source line numbers are metadata; footnote reference numerals are separated from actual reading/year values; typographic line-break hyphenation is joined. These changes are declared. Odd English, source spelling, quantities and punctuation carrying uncertainty are retained. In particular, the English “Transliteration:” heading above Berk.122 is recorded as printed while the text's actual language/role is identified as English translation. Berlin26's vertical `Zādānfarrox āwišt` is source-only: no English target is supplied in that translation block, so none was invented.

| Final proposed addition | Source boundaries within full parent | Published English boundaries | Evidence and grain |
|---|---|---|---|
| `S23-BERK25-TRANSACTION-RECEIPT` | Starts `may 10 sabōy ō Wahman-Ohrmazd`; ends `padīrāy pad-iš stad`, lines6–8 | Starts `gave Wahman- Ohrmazd 10 ewers`; ends `from Wahman- Ohrmazd.` | PDF8/9. Complete coordinated transfer/receipt predicates; the damaged opening agent is outside scope and is not supplied. |
| `S23-BERLIN26-DATE-RANGE` | `az māh Ardwahišt ī sāl 40` through `pad 2 māh ud 22 rōz`, lines3–7 | `from the month Ardwahišt (2nd month)` through `for two months and 22 days` | PDF14/15. Complete temporal modifier, explicitly a fragment, not a standalone sentence or gardener claim. |
| `S23-BERK11-RECEIPT` | `ud pad gugāymuhrīhā ī awestwārān padīrāy pad-iš stad`, lines17–19 | `And for that received a receipt sealed by trustees’ / witness’s seals.` | PDF20/21. Complete receipt predicate with anaphoric transaction context retained in parent. No barley amount/unit is included. |
| `S23-BERK122-PERIOD` | `pānzdah-rōzag rāy az rōz Ohrmazd frāz`, lines6–7 | `for fifteen days, starting from the day Ohrmazd onward` | PDF23/24. Complete temporal modifier; no donkey count, recipient name or sealer asserted. |

All four carry `nonredundant_release_eligible=true` as a proposal subject to independent review and root release decisions, while `training_admitted=false`. The two predicate targets are elliptical because their agents are outside the selected scope; the packet labels this and preserves the full context. Do not add an inferred giver or make them into invented standalone English sentences.

## Explicit holds and attributed revisions

- `S23-BERK25`: full parent held for the unknown opening personal name, locality and reconstructed administrative title/account. The later known sealer Dēnabzūd must not be made the giver. Main line8 `awetwārān` is preserved even though commentary discusses `awestwārān`.
- `S23-BERLIN26`: full parent held. The revised gardening reading is Asefi's edition, separate from Weber's earlier marriage-related interpretation reproduced on PDF15. Line9 `bāγbān(?)` and footnote23 explicitly state an uncertain name and non-final gardener reading, although the English lacks a question mark. The proposed date range avoids the disputed lexical/participant content. Prior and revised readings are recorded as separate edition evidence, not merged into consensus.
- `S23-BERK11`: full parent held. Transcription line13 says `jaw grīw 12`; English says `twelve kabīz of barley`. PDF21 explicitly discusses12grīw=120kabīz in its local calculation. Both original layers survive; the English is not silently corrected. The receipt predicate excludes the entire disputed ration passage.
- `S23-BERK122`: full parent held. Line5 Aramaic layer `ḤMRʼ III` conflicts with MP `xar 4` and English four donkeys. Neither number is selected as certain. The terminal `Yazdānp…dār(?)` remains uncertain and the English drops its question mark; that seal clause is not proposed.
- `S23-BERK122-PROVISION-REVISED-NAME`: restricted, `nonredundant_release_eligible=false`. The wheat/barley quantities match the printed English and avoid the donkey numeral, but the recipient `Asmāndād` is a revision of Gignoux's `Asmānzādān`; PDF23 says the final mark most likely represents a stroke. The exact transfer predicate and target are retained for independent adjudication, not counted among the four clear proposals. No hidden certainty is created by its unmarked main transcription.

## Archive57/TRAIN comparison and nonredundant counting

Comparison inputs were pinned: archive71 dispositions (57qualified units from53packets) at `experiments/data-qualification-20260928/archive-alignment.jsonl`, SHA256 `051b4644ef0a4613f48232b9149398242a953f19726f36670919b10eb320019c`; historical TRAIN2237 at `experiments/train-audit-20260927/qualified-v1/train.jsonl`, SHA256 `15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc`. Only source fields and identity metadata were used; no TRAIN target or benchmark answer was consulted.

The named witnesses Berk.25, Berlin26, Berk.11 and Berk.122 are absent from the53 archive packet identities. All TRAIN2237 work IDs belong to Parsig. Full-source and proposed-scope exact normalized equality/whole-unit containment found no match against TRAIN. Normalization is NFKC, casefold and punctuation/hyphen token separation; containment uses at least6tokens. This does not prove semantic novelty or absence under another spelling.

A separate short-formula check was required because the general6-token threshold excludes the three-token seal:

| Scope/context | Archive57 coverage | Final treatment |
|---|---|---|
| `S23-BERK25-SEAL` | Entire `čak Dēnabzūd āwišt` occurs in `openampd:MP0408:full`, normalized token span[31,34) | Source-supported occurrence retained, but `nonredundant_release_eligible=false`; **zero new example** from this seal. |
| Berk.11 final sealing clause | Same exact formula occurs in MP0408 and the Berk.25 parent | Removed from the final `S23-BERK11-RECEIPT` scope. Its exact source/target parent offsets remain under `excluded_duplicate_parent_context`; no extra seal row. |
| `S23-BERK25-TRANSACTION-RECEIPT` | No whole-scope containment or contiguous match of4+normalized tokens found | Proposed addition, while acknowledging common administrative formulae. |
| `S23-BERLIN26-DATE-RANGE` | Short shared date formulae occur, including `ī sāl 40 ud rōz` in MP0602/MP0085 and `ud rōz day pad ādur` in IEDC1062; no whole range is covered | Proposed temporal fragment; not independent evidence for each repeated calendar word/formula. |
| `S23-BERK11-RECEIPT` and `S23-BERK122-PERIOD` | No whole-scope containment or contiguous match of4+normalized tokens found | Proposed additions at their stated fragment/predicate grain. |

The final packet therefore contains five source-supported scope occurrences, of which one is entirely already covered, yielding **four proposed nonredundant scopes from four additional named witness identities relative to archive53**. It also contains one restricted scope, excluded from that count. This is not an assertion of four newly discovered manuscripts or four independent statistical observations. S23's comparison quotations overlap Berk.32, Berlin5, Berlin8, Berlin12, Berk.24 and Berk.43C; those comparison passages were not exported.

Source-only short/partial overlap receipts are in `resources/local/data-qualification-20260928/s23/formula-overlap.json` and `archive-partial-overlap.json`. The latter is bound to the final candidate hash and records the precise matched archival unit IDs. Source containment is not a claim that every English translation is identical.

## Validation, rights and handoff

Candidate JSONL: four unique parent IDs;6nested scopes;5source-supported occurrences;4nonredundant proposals;1already-covered occurrence;1restricted clause;4held whole parents. All source/target offsets reconstruct exactly; page/image/PDF hashes pass; all uncertainty markers and known quantity contradictions remain. Images and UTF-8 strings were read back. All training and expert-certification flags remain false.

The inspected first article page, PDF5/print6, explicitly states **CC BY-NC4.0**. This is source-access/license-notice evidence. Root must apply attribution/noncommercial and release-use constraints; this packet does not authorize a model run or redistribution independently. Protected16 policy was used only as identity metadata; these named documentary witnesses differ from the protected literary families. Final work/witness grouping and independent review still control release.

Final candidate SHA256: `22fb5038b17cb49161ad7d1bb10e04fe7649e6ecd25e4613ab30eeecc7805547`.
Builder SHA256: `636d859019c421efa9485a52bc32e22df545b4bde2348e8657f13048895e1b17`.
The scratch manifest is written after candidate validation. Before independent review, root's duplicate instruction caused one checked narrowing of the staged closing scope; the builder permits replacement only of that exact earlier staged hash and refuses any final/unrecognized output. No original source, archive, TRAIN, benchmark or other agent's file changed. No download, cloud/model/GPU job or new installation was used.
