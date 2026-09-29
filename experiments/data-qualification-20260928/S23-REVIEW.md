# Independent S23 source and scope review

**Result: PASS for the four bounded proposed scopes below.** No blocking transcription-to-published-translation extraction mismatch was found. This review supports source qualification at the declared scope, not admission to a training run, a new decipherment, global novelty, statistical independence, or certification of every scholarly reading. Four full parents remain held. Training additions remain zero in the reviewed packet.

Reviewer: `/root/finetuning_kb_research`; writer: `/root/blind_dev72_b`. The reviewer did not edit the candidates, qualification report, sources, archive, TRAIN, or benchmark. This file is the only review output.

## Frozen evidence

- `s23-candidates.jsonl`: SHA256 `22fb5038b17cb49161ad7d1bb10e04fe7649e6ecd25e4613ab30eeecc7805547`.
- `S23-QUALIFICATION.md`: SHA256 `bfbb4efd7f23ca9f09b26a343e1b49aeab931135dc0ba5f49366ce5739be97cb`.
- `sources/01+-+Nima+Asefi.pdf`: SHA256 `480670343730bdac72d1af78ff699d8cca69d71b908472a890c9ea1f51c6a1ce`.

The source is Nima Asefi (2025), “Ewer, Garden and Gardening,” *Journal of Iranian Linguistics* 2(1), 6–29, DOI `10.46991/jil/2025.01.01`. The published target language is English. No Persian translation was synthesized.

I independently inspected existing rendered images of PDF pages 5, 8, 14, 20, 21, 23 and 24 (printed pages 6, 9, 15, 21, 22, 24 and 25), supplemented by the source's extracted commentary text. These cover every selected main source/translation block, the license notice, and the material uncertainty/quantity statements. This is not a claim to have visually inspected every commentary page. All 15 distinct page-image hashes referenced by the final packet were verified, separately from the seven-page visual review.

## Accepted scope boundaries

| Eligible proposed ID | PDF / printed page | Review conclusion |
|---|---|---|
| `S23-BERK25-TRANSACTION-RECEIPT` | 8 / 9; lines 6–8 | The transfer of 10 ewers of wine to Wahman-Ohrmazd and the following receipt predicate align with the published English. The damaged opening agent is outside scope. The known sealer Dēnabzūd must not become an inferred giver. Main-table `awetwārān` is preserved rather than silently replaced by commentary spelling `awestwārān`. |
| `S23-BERLIN26-DATE-RANGE` | 14 / 15; lines 3–7 | The range from Ardwahišt, year 40, Day pad Ādur, to the beginning of Amurdād/Ohrmazd, and the printed duration of two months and 22 days align. This is a complete temporal modifier, not a standalone sentence. The uncertain name/gardener clause is excluded. |
| `S23-BERK11-RECEIPT` | 20 / 21; lines 17–19 | The receipt predicate aligns with “And for that received a receipt sealed by trustees’ / witness’s seals.” Its agent and anaphoric transaction context remain in the parent. No barley quantity is selected, and the following already-covered seal has been removed from this child. |
| `S23-BERK122-PERIOD` | 23 / 24; lines 6–7 | The fifteen-day period starting from Ohrmazd aligns with the English. This is a complete temporal modifier, not a standalone sentence; donkey quantity, revised recipient and uncertain sealer are outside scope. |

These are two predicate scopes with omitted/contextual agents and two temporal fragments. Preserve those grain labels and parent context; do not turn them into four complete independent sentences.

## Holds and duplicate treatment remain necessary

- All four full parents remain held. The selected clear portions do not resolve the rest of their editions.
- Berk.11's printed MP `jaw grīw 12` and English “twelve kabīz of barley” disagree. PDF21 discusses 12 grīw as 120 kabīz. The conflict is retained, and the selected receipt contains neither competing quantity.
- Berk.122's Aramaic `ḤMRʼ III` conflicts with MP `xar 4` and English four. The selected period avoids the numeral. `Yazdānp…dār(?)` remains uncertain and unselected.
- Berlin26 footnote 23 explicitly qualifies the name and gardener reading. Its unqualified-looking English does not make the full revised gardening interpretation certain. The date fragment avoids that dispute; the source-only vertical sealing text has no invented target.
- `S23-BERK122-PROVISION-REVISED-NAME` remains restricted and ineligible for the four-scope count. Its grain quantities align, but `Asmāndād` is an attributed revised reading whose commentary uses tentative reasoning. This review does not upgrade that name.
- `S23-BERK25-SEAL` remains source-supported but already covered. I checked the exact source formula `čak Dēnabzūd āwišt` across source lines 7–8 of `openampd:MP0408:full` in the pinned archive. The same closing formula was correctly removed from the Berk.11 child and retained as excluded parent context. Neither occurrence adds a new example. Formula overlap is not whole-witness equivalence.

## Mechanical checks and release boundary

Direct local assertions passed: four unique held parents, six nested scopes, the exact four eligible IDs above, one excluded duplicate-context span, no training or expert-certification flags set, all source/target character slices reconstructed exactly, correct MP/English language metadata, matching PDF/image hashes, and the final candidate hash bound by the partial-overlap receipt. The pinned archive and historical TRAIN file hashes match those stated in the writer report. No benchmark answer was consulted. The writer's broader source-only containment results remain bounded orthographic checks, not proof of semantic or global novelty.

PDF5 visibly states CC BY-NC 4.0. That notice and the published attribution must travel with any permitted downstream use; this review does not independently authorize redistribution or a model run. Root retains release integration, work/witness grouping, use restrictions and final admission decisions. No blocking correction to the frozen candidate packet is requested.
