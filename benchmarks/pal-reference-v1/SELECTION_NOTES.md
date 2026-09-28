# Selection record — PAL-REF v1

Prepared 26 September 2026 UTC (25 September local). Mode: Classic Codex, one lead. No independent agent or human specialist review was performed. This document records the pre-freeze selection, not a later revision of the benchmark.

The candidate pool was the 199 trilingual records in five works assigned to TEST in the existing translator dataset. Forty passages were chosen for interpretable source spans and agreement between their published English and Persian references. Selection was not based on fresh model predictions or a desired model score. The intended balance yielded to reference suitability: 8, 4, 10, 10 and 8 passages respectively from works 104, 110, 116, 130 and 132. This purposive selection likely favors more readily adjudicated text and must not be presented as a random difficulty sample.

Concrete exclusion reasons considered during curation included:

- Work 104: differences in imperative/declarative force in the opening counsel; materially different renderings around records 20, 23 and 30; an uncertain reading at 15. Saved prior response exposure also excluded records 3, 6, 8, 12 and 17. Records 6 and 17 were removed from a preliminary candidate list before any version was frozen.
- Work 110: adjective/adverb or participant/mood differences in several candidates, and disagreement involving “with/instead” and polarity in others. Four sufficiently aligned passages were retained, so this work has a smaller allocation.
- Work 116: multiple differences between the historical English translation and the Persian reference. Ten retained passages have substantially aligned propositions, including explicit quantities where present. No attempt was made to repair a translation to increase coverage.
- Work 130: record 11 has a razing/digging difference; 18, 24 and 27 have tense disagreements; 8 leaves an avoidable participant/mounting ambiguity. Records 12–14 were joined as one intact passage, in every language, because their connected Faredun narrative supplies the referents. Starred editorial readings in other selected passages remain visible.
- Work 132: records 9–10 have a translation boundary issue; several other candidates contain material semantic differences. These were excluded. The historical religious and kinship prescriptions retained here are source content, not modern advice.

These are examples of substantive decisions, not a claim that all 157 unselected source records are incorrect. Some were simply unnecessary for the fixed size or narrower context.

All 42 final source records were checked against the saved raw archive and existing curated dataset: each transcription, English and Persian text matches after removal of a terminal bibliographic citation only. Raw response hashes were checked. The existing TRAIN/DEV/TEST files were not edited. The full selected references and source texts were read during curation.

Normalized source comparisons against TRAIN/DEV found no selected match at the documented SequenceMatcher threshold, and exact normalized target comparisons found none. A scan of 22 saved prediction/input/response files found no final selected ID. The scan found references in prior responses, including retrieved citations, and conservatively treated them as exposure. These are bounded checks, not proof against semantic duplicates or public pretraining exposure. `selection-audit.json` records file hashes and methods.

Previously saved corpus-reader reports were also searched for all 42 selected IDs. Three matches concerned contextual readings at 116000012, 116000015 and 132000003; none recorded a material English/Persian disagreement for the selected span. This cross-check is not an independent expert re-review.

`ASSEMBLY_SOURCE.py.txt` preserves the exact one-time assembly script used at `tmp/benchmark-review/build.py`. Its paths are relative to that original location. It is provenance, not a command for rebuilding or changing the frozen release. Verification and scoring use `benchmark.py` instead.
