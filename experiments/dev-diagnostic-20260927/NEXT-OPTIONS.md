# Existing evidence for a later intervention

Read-only reconnaissance by `/root/model_choice_review`, performed without current diagnostic outputs. These are candidates, not selected interventions or authorized automatic launches.

The existing `dictionary/entries.json` contains 16 draft entries. Only five have exclusively original TRAIN witnesses: `mp-hunsandih-n` (119000001,119000002), `mp-xrad-n` (107000001), `mp-frazand-n` (107000003), `mp-xwastag-n` (107000004), and `mp-ruwan-n` (107000006). These witnesses occur in the actual frozen training payload. The senses are Codex draft analyses informed by credited translations, not validated isolated-word gold. Coverage is narrow: their forms occur in 1,3,6,9,7 of the 402 DEV records respectively, with overlap and no work 517 matches.

Eleven dictionary entries use original TEST work 120, including mixed-source `mp-weh-adj`. `kb/grammar.md` also quotes original TEST record 152008001. `kb/glossary.md` has 45 contextual study glosses without a full witness-level split audit. Do not feed these files wholesale into training or retrieval. The 406-form vocabulary index with 1135 inscription occurrences is an occurrence index, not translation labels, and none maps to actual TRAIN records.

The smallest plausible assisted comparison would supply a fixed, source-selected set of attested examples from the existing TRAIN archive. It must be labeled reference-assisted, preserve citations and source uncertainty, and exclude original TEST/DEV answers and answer-equivalent witnesses. It tests whether access to existing evidence helps before spending on further training. The five draft dictionary entries alone offer too little verified coverage to support a broad experiment.

Further composition supervision could start from natural TRAIN passages illustrating negation, participants and quantities, keeping their published whole-passage translations. Word glosses, segmented targets and synthetic role reversals require new evidence; they must not become invented training truth. Select the intervention only after the current blinded diagnostic is complete.
