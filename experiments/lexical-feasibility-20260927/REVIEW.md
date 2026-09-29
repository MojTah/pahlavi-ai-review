# Independent lexical-feasibility checkpoint review

27 September 2026. **PASS for this fixed local preparation packet and its stated research conclusions.** No blocking code or methodological issue was found. This is not admission of lexical labels, CPT material, model training or a paid job. REPORT.md was not yet present during this bounded review.

## Executed verification

Ran `resources/local/hf-client-venv/Scripts/python.exe -B -X utf8 scripts/prepare_lexical_feasibility.py --check`. Exact reconstruction passed, as did changed-text, quarantined-witness and held-out-work rejection checks.

An independent in-memory check verified all 14 selected qualified TRAIN records: nine one-whitespace-item recall units and five contextual proposals. All source and Persian passage-target UTF-8 bytes match TRAIN; retained provenance and linguistic qualifications match the final ledger. All source spans reproduce their stated text with valid Unicode offsets and safe word boundaries. The five contextual spans match the local annotation audit. No selected work is held out; quarantined119000001 is excluded, and its occurrence annotation is not imported into119000002. The repeated frazaft units remain one recall group: nine rows, eight groups.

Every record has `training_admitted=false`, `expert_adjudicated=false` and null accepted lexical/grammar labels. Draft senses/POS remain explicitly unaccepted Codex proposals. In particular,107000006 and119000002 preserve their passage qualifications. Published passage translation and exact source identity do not certify a proposed narrower word sense or grammatical relation.

Traced the generator's reads: exactly its four pinned inputs, with no benchmark or model-output file opened by the build. The complete draft dictionary is an input, but only the five selected proposal fields are emitted; this is not a claim that the legacy dictionary itself is an untouched holdout. An independently injected altered draft-input byte sequence failed the input-hash check. Fresh creation refuses existing output files; that branch was inspected, not executed. Span safety is verified for this hash-pinned packet, not claimed for an arbitrary future lexical extractor.

## Independent visual dictionary check

Verified the retained S24 PDF SHA256 and inspected the five supplied full-page images. The six brief quotations and headword/page/column locators agree with the images:

| Candidate | PDF page / printed page | Column | Finding |
| --- | --- | --- | --- |
| frazand |87 /78|left|Exact headword and brief definition agree.|
| frazaft |87 /78|left|Past-form gloss and book-subscription context agree; vowel-length mapping remains pending.|
| ruwan |180 /171|right|The ruvan entry and brief definition agree; w/v mapping and contextual interpretation remain pending.|
| xrad |228 /219|right|The xrat entry and its five listed generic senses agree; final d/t mapping remains pending.|
| hunsandih |229 /220|left|The displayed abstract-noun entry and two-word definition agree; lexical-family similarity does not prove form equivalence.|
| xwastag |230 /221|right|The displayed property entry agrees; superscript-u/w and final k/g mappings remain pending.|

ASCII candidate labels in this table are navigation aids; exact diacritics and editorial headword displays remain in scholarly-checks.json and the images. These are AI visual/source checks, not a Pahlavi specialist's adjudication. No generic definition was promoted into an accepted contextual Persian label or universal normalization rule.

## Inventory and interpretation

Verified all source hashes/sizes listed by LOCAL-ANNOTATION-AUDIT.json and the seven hashes in ADDITIONAL-SOURCE-INVENTORY.json. Independently read and rehashed all2,351 archived TITUS page extracts and reproduced every recorded raw whitespace count. Aggregation gives2,183 content pages/903,313 terms; the eight-root candidate pool gives995 content pages/199,043 terms and146,700 terms under the stated crude body heuristic. The metadata contains1,656 overlap-checked pages and190 with a match. I did not rerun that heuristic or its eight-term matching algorithm, or adjudicate work identities and language layers.

Thus TITUS is a substantial potential source reservoir beyond the Parsig-only inventory. None of the raw totals establishes cleaned, novel, permitted Middle Persian CPT volume. Unmapped collections are not automatically outside held-out works; zero exact matches cannot establish independence. All new admitted CPT material and accepted lexical/grammar labels remain zero.

The external note correctly confines its reported CC BY4.0 finding to the exact June2026 Oxford release. It does not license the separate September archive by implication, and Oxford English translations are not Persian gold or grammatical annotation. My bounded Zenodo metadata request was unavailable through the web tool, so the live license declaration relies on the eligibility author's recorded metadata evidence, not independent successful retrieval here. MPCD's empty local UD annotation release and access limitations are not proof that useful internal annotations do not exist.

No model-quality, generalization, expert-certification, rights-clearance, budget or launch claim follows from this checkpoint. The next prerequisite is qualified review of exact lexical mappings and source eligibility, preserving uncertainty and all work/witness exclusions.

## Artifact identities

| Artifact | SHA256 |
| --- | --- |
| scripts/prepare_lexical_feasibility.py | `d1fba3afed539bb9ccdcdf2de61af3e44aa8fabb6ae87b635d666e9b5bf9165e` |
| packet.jsonl | `7791c308a9fd32acb868613a8afa0f0be248776e5ccf5b65b11b45eb491b46a3` |
| packet-audit.json | `b60ce69464b7ddda10c8eef53a1e62705b8afad64c29a0d626f9d3cba84bd738` |
| scholarly-checks.json | `4864e047fca2890a8b71a1407882bc14e193a9c5cda189c7b6afc177638c3a4a` |
| LOCAL-ANNOTATION-AUDIT.md | `d1fcba07a311e122467f672042da97723e213eb00d7410f8a4696972ebc92512` |
| LOCAL-ANNOTATION-AUDIT.json | `ebdf52fb852f2e69879bbd36796b3e2bb7f779704f0a8667c99dfc84ac721336` |
| EXTERNAL-ANNOTATION-ELIGIBILITY.md | `e0433b5f899f96845e4c0cef100c2e35630daeb33c9b3f27f72d1dec1546725a` |
| ADDITIONAL-SOURCE-INVENTORY.md | `8c70edcd45ba6b5cd412f38bbd64380aa2d8f274c9af77fc458e4a3db47af055` |
| ADDITIONAL-SOURCE-INVENTORY.json | `b1d7194c96b4d0cc4a5dab1b01ca880510750b2ff9953efa4cfc00d1fe642041` |
| sources/A-Manual-of-Pahlavi-II-Dictionary.pdf | `d49aaebbe1f51ebc07c616f538ff40a2a8d7ae9c3b810836c65689ab8a50f8c9` |
| nyberg-87.png | `053bdeea31685925b7087529723e3f8cedef58a8cf265d58cafe8be135c78e96` |
| nyberg-180.png | `4c8bcc2a85dd80934ac64dd5e996f2bbf5f83d8331d2f3070b1c84236c848f04` |
| nyberg-228.png | `23f5a20c055f9a7a629ae3bb6a73e95392c8faeeb36bdea89dee69dcdfbec911` |
| nyberg-229.png | `f41d704f3471a96a979f3326eaa28a515717e3122fdfd1ebec751d84145064bc` |
| nyberg-230.png | `2a3eb4688702c2aa8427d8ece6eba95ea1a7c09f925f5a4590af9e50dff20c9f` |

## AutoCode Critic record

- Mode: Classic + Critic.
- Lead agent/request id: /root
- Critic agent/request id: /root/final_external_judge
- Critic model and reasoning effort: inherited session settings, no override
- Independent from lead: yes
- Critic verdict: pass
- Evidence reviewed: generator, packet/audit, scholarly checks, three research reports and their JSON companions, pinned TRAIN/ledger/drafts, five Nyberg page images and source PDF identity, archived TITUS page extracts.
- Verification evidence: generator --check passed; independent fourteen-row payload/span/provenance checks and zero-label assertions passed; four-input read trace and changed-input hash rejection passed; all listed inventory input hashes matched; all2351 page hashes/counts matched; six dictionary quotations visually checked.

The critic wrote only this REVIEW.md and made no source, code, model, benchmark, cloud, credential, Drive, budget or commit change. PASS is limited to preparation and its stated evidence. Technical checks do not certify linguistic correctness or admit training.

## Frozen report prose delta

Subsequently reviewed REPORT.md, SHA256 `b4357f8ccabeb972f96a449211ac243a3af573ba08ddec9217f6a54e97ba99e2`. **PASS for consistency and claim limits.** This extends the earlier verdict to that report; its initial absence above records the original review timing.

The report agrees with the checked artifacts:14 records, nine single-item rows/eight groups, five contextual candidates, six source checks linked to seven records, and zero accepted auxiliary labels or admitted external CPT records. TITUS totals and the candidate subtotal match the verified inventory; neither the raw total nor the crude146,700-term extraction is called clean eligible volume. Oxford's June release declaration is not transferred to the September archive. Unchanged benchmarks, separate learning-regime and cross-family questions, budget scope and pending launch gates are preserved.

Book coverage is appropriately bounded. This checkpoint's Nyberg evidence consists of the specified five page images and six definition checks. Other books are identified through bibliographic, publisher or contents records; the report does not claim their full texts or target entries were read. It distinguishes inaccessible chapter retrieval from global unavailability, references earlier local book coverage as earlier work, and avoids treating another Nyberg printing as independent corroboration. I did not independently validate the newly cited bibliographic metadata or earlier book-study coverage in this prose-only delta.

No correction or new blocking issue was identified. Expert linguistic adjudication, variant mappings, source rights/eligibility, sufficient supervision and actual training effectiveness remain unresolved. No completed check was rerun for this delta; the review file alone was updated. The AutoCode evidence record above now additionally includes this hash-bound report consistency review, with the same limited PASS scope.
