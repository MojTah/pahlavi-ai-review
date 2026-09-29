# Independent corrected-data review

Reviewer: `/root/ready_v2_critic`, 29 September 2026. Read-only review apart from this report and its JSON evidence. Root owns integration; this reviewer did not implement the corrections.

**PASS for the defined corrected local data projection and prepared pilot.** Final staged manifest SHA-256: `157531204582c50f2d8f73aaa76ce8aca0c83e2c6e624d60bbc8c8daa1515b54`. Every array was independently reconstructed again after the relation-direction repair. This review does not authorize a cloud launch.

## Scope and method

The review read `PLAN.md`, `prepare.py`, `lexical.py`, the lexical and nonlexical decision ledgers/reports, and the old serializer/prompt definitions. It independently reconstructed source targets and training arrays rather than accepting the implementer's PASS label. No model weights, network, credentials, GPU, paid inference or project training were used. Evaluation files were hash-checked without inspecting reference contents.

All 7,608 released lexical parents were checked against 7,648 archived XML observations from eight independently hashed raw archives. Every parent maps exactly once into 7,438 output inventories. All 7,588 ordinary targets remain exact JSON values; the 20 apparatus cases were read individually against the source XML and corrected targets. All 150 unequal-input groups retain their supported inventories. A further exact-duplicate MMP group shares a target index while preserving both source parents. These source/structure checks do not claim an independent retranslation of every dictionary word.

The four particularly sensitive cases were inspected explicitly: `da:68` keeps its own gloss and resolves the named `watist` reference against entry 67; `dmx:107` preserves the two components rather than inventing a whole-compound translation; `dmx:550` keeps two infinitive senses and two separately scoped inflected forms; `yz:13` retains the published past-stem phrase and Old Shirazi qualifier, subject to the direction-key repair below.

All 17 source-bound typography transformations were independently replayed and their complete before/after targets read. Archive, source, before and after hashes match. The transformations preserve every noncontrol/nonspace character. The three LRM/soft-hyphen cases replace the control with a nonjoining boundary, and the `خوش‌تر و` repair separates the existing conjunction. Blanket deletion was not applied.

All eight nonlexical uncertainty cases were read in canonical form and again at their exact archived source/translation locations. The seven holds are justified by unresolved apparatus or uncertainty retention under the specified task, not assertions that the underlying translations are false. The MP6003 empty damage tag is actually present in retained TEI. The MP2100 greeting can remain a scoped published interpretation; its admission does not certify literal temporal completeness or admit its damaged parent letter.

## Reproduced artifact checks

For the staged build recorded in the companion JSON, this reviewer independently checked every one of the 9,973 tokenized records. Exact prefixes were reconstructed from task instructions, source and context only; complete input IDs, prompt boundaries, all -100 mask positions, attention masks, exact target-plus-terminator decoding, no unknown tokens, no truncation and unique complete prefixes all passed. Provenance and review evidence were absent from prompts. Maximum actual length was 1,144 tokens under the 2,048-token contract. The final full pool contains 1,936,762 sequence tokens; the selected pilot contains 274,703. All 2518 unchanged nonlexical rows independently retain their exact prior token arrays. Fifty-two current manifest/source/output hash bindings and 12 frozen benchmark file hashes passed.

Parent accounting was exact: 10,152 original records = 10,145 represented parents + seven holds. The reduction to 9,973 model records comes from inventory consolidation and the two reviewed historical equivalents, not unrecorded deletion. Frozen benchmark hashes and excluded historical work identities remained intact; no evaluation target was used to choose a correction.

The prepared pilot contains 1,536 unique records and preserves 96 updates of 12 historical, two lexical and two other records. Its counts are 1,152 historical, 96 Persian lexical, 64 CPD, 32 MMP, 53 documentary, four article spans, four distinct inscription pairs and 131 pedagogy records. Eleven selected IDs differ from the prior schedule: four canonical merge remaps and seven actual replacements. The four held documentary slots become four fresh pedagogy rows rather than duplicate inscription pairs.

Selected changed-record exposure is explicit: ten merged lexical inventory groups, one apparatus correction (`da:68`) and 14 typography rows. This is a matched repair pilot, not full-pool exposure. Larger available inventory does not imply that all 9,973 records will be consumed by this 96-update configuration.

## Finding and disposition

`DATA-V2-001` (P2), `lexical.py`, `kosh:yz:13`: the first projection used `relation_to_headword_as_published` inside a related-form object naming `ōpastan`. That direction was ambiguous against the source statement that headword `ōpast` is the past stem of `ōpastan`. The implementation owner changed the key to `headword_relation_to_this_form_as_published`, preserving the exact published phrase and qualifier, and added a targeted direction assertion. Static source inspection and independent final staged-target reconstruction confirm the repair. All 9,973 model arrays were checked again; the selected training file is unchanged because this corrected row is outside its 1,536-row selection. No open finding remains in this review scope.

## Limits of PASS

A local PASS means the defined source-grounded projection and prepared arrays passed the checks above. It is not professional philological certification, a guarantee of no future defect, proof of improvement, or an explanation of the prior regression. GPU/NF4 execution, live funded balance, host lifecycle and remote checkpoint persistence remain NOT TESTED by this reviewer. Runtime readiness is covered separately, and cloud submission remains a separate gate.
