# Nonlexical closure review for corrected training projection

Date: 2026-09-29. Reviewer: `/root/uncertainty_closure`. Mode: bounded source/meaning review, with no cloud, model execution, source editing or evaluation-answer access.

**PASS with seven narrow holds and exact derivations for 17 typography rows.** This resolves the named admission decisions for the next projection; it is not professional philological certification or a claim that all remaining corpus words are correct. [Machine-readable decisions](nonlexical-decisions.json) bind every decision and transformation to exact source, target and archive hashes. Original data were not changed.

## Admission decisions

| Record | Action | Reason and evidence boundary |
|---|---|---|
| `parsig:151061036:pal>fa` | Hold | The archived source contains bracketed negative `nē` within a negative conditional; target purpose is positive. Immediate surrounding source explains ritual destruction of harmful creatures, but does not establish the edition's bracket convention. Do not allege a reversal or silently remove negation. |
| `parsig:123000032:pal>fa` | Hold | Persian and archived English both use the Amitus/Caesar's-nephew apposition. Source contains bracketed conjunction; the current prompt does not explain its apparatus status. Parallel translations support the reading but do not resolve the input ambiguity. |
| `parsig:136006008:pal>fa` | Hold | Source offers three alternatives; Persian and archived French choose “now.” The plain translation task does not condition that editorial selection. Retain the source, and hold this supervision until the alternatives can be represented explicitly. |
| `iedc:IEDC1262:folio0` | Hold | Questioned/restored recipient in source becomes an unqualified English servant. |
| `iedc:IEDC1265:folio0` | Hold | English preserves competing food/hunger readings but not the question attached to the final personal name. |
| `iedc:IEDC1040:folio0` | Hold | Questioned measure term becomes an unqualified term. The archived content summary also states uncertainty about payer/payment; no new payer or unit should be invented. |
| `openampd:MP6003:full` | Hold | Source/target uncertainty differs locally; additionally, an actual empty TEI damage element in the retained address was dropped by the renderer. |
| `openampd:MP2100:greeting` | Admit unchanged with existing context | Full selected TEI lines 4–6 and both layers were read. The temporal adverb has no explicit English word, but a greeting can express continuing well-wishing idiomatically. This is insufficient evidence of a translation defect. Keep it as a source-bound published interpretation, never literal temporal-completeness gold. |

All three historical raw records and immediately neighboring paragraph units were inspected, including the parallel English/French translations where present. The three IEDC entries were read with their original transcription/translation HTML, publication description and content summary. Both OpenAMPD TEI documents were read. All eight current canonical source/target/context representations were inspected, as was actual mixed-prompt serialization: the documentary prompt really includes the context and expressly asks to retain uncertainty. The four documentary holds therefore address supervision inconsistent with that narrow requirement; source-side warnings alone do not mark a certain-looking answer as uncertain. None is labeled a proven false translation.

The parent MP2100 letter remains excluded except its previously selected greeting. Admission of that greeting does not clear the full damaged letter. There is no invented “always” correction.

## Concrete TEI damage issue

`MP6003_trc-p1` line 1 has `<damage extent="unclear"/>` immediately after the address word. The canonical source lacks that marker because `archive_align.py` and the prior auxiliary checker render only gap/unclear/supplied as explicit annotations. Thus the previous source-fidelity check did not cover this kind of damage element. The raw original remains intact.

A bounded census of all released OpenAMPD source/target raw blocks for damage/del/add/choice/subst/sic/corr/orig/reg found one other damage instance in MP2561. It is on excluded line 1; the released lines 2–4 do not contain it. No additional MP2561 hold is warranted. This census is limited to the retained blocks and listed tags, not an assurance that every possible TEI semantic feature has been audited.

## Typography: the proposed blanket deletion was unsafe

All 17 complete source/target pairs and their proposed outputs were read. All 17 targets are exactly present in their raw archived translations. Fourteen records safely collapse repeated U+200C to one U+200C, preserving the intended nonjoining boundary. The ledger provides exact old/new strings, expected occurrence counts, original source hashes, before/after full target hashes, and archive pointers. Apply these operations only to those exact bound rows in a new version.

**Do not simply delete U+200E/U+00AD.** These three controls occur at real Persian word/morpheme boundaries. Exact replacements with U+200C preserve the correct typography:

| ID | Exact supported replacement |
|---|---|
| `parsig:151001160:pal>fa` | `بزه\u200eای` → `بزه\u200cای` (بزه‌ای). Deletion produces the joined letters بزهای. |
| `parsig:109000003:pal>fa` | `به\u00adکار` → `به\u200cکار` (به‌کار). Deletion produces بهکار. |
| `parsig:109000011:pal>fa` | `می\u00adخواهند` → `می\u200cخواهند` (می‌خواهند). |

One already-counted repeated-control record, `parsig:151006015:pal>fa`, also needs a missing space: after duplicate-control collapse, `خوش‌ترو` → `خوش‌تر و`. The exact archived source has `xwaštar ud`, and the complete Persian comparison requires the already-present conjunction before the following comparison. This inserts one boundary space, with no letters, words, meanings or Pahlavi source changes. This was found by actually reading the normalized output; mechanical deletion alone would have retained a visible target defect.

Independent executable assertions replayed all operations, checked 17 unique affected IDs, 14 duplicate-ZWNJ rows, 3 exact control replacements, the one within-row spacing repair, absence of remaining duplicate ZWNJ/LRM/soft-hyphens in transformed targets, and identity of all noncontrol/nonspace characters. The Pahlavi sources remain unchanged. Exact before/after hashes make these reversible derived corrections; the canonical originals remain authoritative evidence.

## Limits and next gate

These decisions close this bounded review scope by excluding unresolved supervision rather than fabricating translations. The new projector must apply the seven holds, retain the MP2100 scope/context, use exact hash-bound target transformations, retokenize changed targets, and verify prompt/label round trips and exclusion integrity. This review did not run the new projector or grant a cloud launch. No claim connects these issues causally to previous model performance.
