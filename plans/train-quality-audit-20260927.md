# Full TRAIN quality audit before further use

The user requires the complete training set to be checked before use. Hold further training and TRAIN-example-assisted cloud inference. The goal stays active; work continues locally. Preserve the original dataset and trained adapter. Current cumulative cloud authorization is USD25, estimated compute USD7.1103; no GPU is running.

Scope: every one of the 2,484 actual Middle Persian scholarly-transcription→Persian TRAIN rows used for the step312 adapter. Payload SHA256: `844a5b64d43a423b69d5989527a53273290a43be15c399056c979f5abb0678a1`. This is not native-script/OCR validation or validation of unknown-word decipherment. The frozen PAL-REF benchmark remains unchanged and does not supply training labels.

Classic + Critic: root owns the audit and final disposition; `/root/model_choice_review` owns the isolated audit script/tests; separate reviewers inspect results and linguistic concerns. No overlapping writers or paid operations. Reuse existing provenance and tokenizer checks where their input identities match. Do not run `scripts/verify_collection.py`, which rewrites collection metadata.

## What counts as complete

Every original row must have an explicit disposition and evidence pointer. Unreviewed rows remain ineligible. Report these dimensions separately:

1. Mechanical integrity: IDs, hashes, actual prompt/token/label mapping, encoding and direction.
2. Archived-source fidelity: original publisher record, source/translation, attribution, locator and revision.
3. Alignment: translation belongs to the supplied passage, with no shifted or duplicated paragraph boundary.
4. Linguistic qualification: recorded review of meaning, participants, negation, quantities, omissions and handling of uncertainty.
5. Specialist validation: claim only when actual identifiable specialist review exists; otherwise false.

Exhaustive check coverage is achievable. Automated and AI review cannot guarantee100% linguistic correctness. Faithful archive copying does not certify the publisher's translation. The old curation status `alignment=verified` checked paragraph IDs/fields and explicitly excluded sentence-level or expert semantic validation.

## Audit and review

The initial exhaustive read-only provenance check passed all2,484 row mappings, all166 original response-file sizes/hashes and exact raw source-unit identity. Preserve reproducible row-level evidence in the new audit rather than rely on this summary. Reconstruct actual deduplication/control-token exclusions; keep all source records accounted for.

Check full TRAIN versus original DEV/TEST/PAL-REF by IDs, works and defined exact source/target normalizations. Enumerate every length-feasible cross-split source pair for a declared0.8 token-sequence similarity threshold; safe bounds may prune impossible matches, but no silent sample or candidate cap. Report limits: this cannot establish absence of semantic parallels or foundation-model exposure.

Screen every actual row for conflicting exact/normalized-source targets, raw-paragraph suffix/prefix overlaps, unfinished boundaries, suspicious length ratios, unresolved readings, lacunae, commentary and source/target script anomalies. Use true chapter/sequence adjacency, including neighbors not retained in TRAIN. Punctuation and editorial glosses are review triggers, not automatic errors:700 targets have square brackets and330 sources have restoration asterisks; many are legitimate.

Known issues that must remain visible:

- TRAIN134004028 includes Persian words belonging to134004029. Quarantine134004028 without silently trimming it. Raw pointers: `sources/local/parsig-2026-09-20/corpus/134.json:1901` and`:1927`.
- The normalized formula group151001001/151019001/151027001 has an unresolved participant discrepancy involving `dānāg`. Preserve all witnesses and adjudicate or quarantine; do not infer a correction from model outputs.

Every row receives a brief recorded alignment/meaning assessment; flagged rows get deeper context review using the archived source, adjacent passages, available notes and corroborating English where present. There are457 actual TRAIN records with an English translation layer; this is corroboration, not automatic gold. Reuse prior witness checks by exact hashes only for the dimensions they actually examined. Preserve legitimate published alternatives, reconstruction markers and uncertainty.

Disposition options: ELIGIBLE; ELIGIBLE_WITH_QUALIFICATIONS; QUARANTINED; UNREVIEWED. Each needs a rationale, exact issue spans where relevant, source locator and reviewer identity/type. Unsupported or unresolved substantive concerns stay quarantined. Do not invent replacement targets, use held-out performance to select exclusions, or change original records. A supported correction requires separate recorded evidence and a new dataset version.

## Freeze and decide

Deliver complete row accounting, exception/adjudication records, retained/excluded counts by work, remaining uncertainty and reproducible input/code/output hashes. Freeze a new qualified-payload identity only after the audit/review is complete. Preserve all2,484 originals and the prepared69/68 evidence candidates.

Only then choose between a further diagnostic and fresh training from the corrected/filtered corpus. Filtering future examples does not remove information already learned by the current adapter. Material label problems may justify a new adapter rather than continuing the old one. Do not execute the previously planned assisted trial automatically just because its smaller witness screen passed. Any paid run needs updated readiness and a cost envelope inside the same USD25 cumulative limit.
