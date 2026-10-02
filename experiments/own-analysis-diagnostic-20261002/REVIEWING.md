# Local result-review handoff

The frozen semantic merit and prospective decision in `PROTOCOL.md` remain unchanged. `review.py` reuses the established DEV rating categories, schema and validator. It prepares six D/P finals for each of two fresh assessors; analysis A is excluded and evaluated separately after final ratings are frozen. Separate contexts and shuffles reduce anchoring, not correlated AI judgment or reference uncertainty.

First independently recover the provider's small final artifacts and verify their remote manifest fingerprint. Then use the shared Python runtime:

```text
review.py prepare --recovered <verified-final-directory> --remote-manifest-sha <independently-read-back-SHA256> --review <new-review-directory>
```

The preparer verifies the manifest inventory, reviewed packet/specification/receipt pins, exact job/input/source/checkpoint recipe, journal accounting, raw output hashes and actual direct/dependent prompts. It replays the frozen local tokenizer for every called D/A/P input and checks token counts, rendering and ID hashes plus the dependent receipt's analysis identity and token IDs. The receipt's token count is derived from its saved ID list, matching the existing runner schema. It never downloads or evaluates a model. A missing verified execution journal stops preparation: report the technical failure with the fixed N=3 per arm, rather than inventing generations. A started/interrupted journal preserves available finals and accounts for missing ones.

Give each assessor only its own `reviewer-a` or `reviewer-b` folder. They read `INSTRUCTIONS.md` and `packet.jsonl`, and write `ratings.jsonl` there. The packet includes each source and the identical complete provisional reference evidence in both arms, including technical uncertainty and optional editorial content. It contains opaque IDs and no A text, actual dependent prompt, arm, case ID, dependency, sequence, timing, model identity or other rating. Raw final text is never cleaned; its wording may still suggest the workflow, so perfect blinding is not claimed.

Failed, capped, abstaining, skipped, interrupted and missing finals use the neutral reviewer marker `unavailable`; precise status and output presence remain in the lead-only mapping. Partial output stays verbatim; absent output stays empty. `unavailable` must be `not_assessable`, never accepted. All six final slots remain, with three cases in each arm. An unavailable final is not a demonstrated meaning error.

After both rating files are complete:

```text
review.py summarize --review <review-directory>
```

The local summary validates exact coverage, hashes, categories, adverse text spans, frozen packet/source fingerprints and duplicate consistency. It preserves each assessor's gains, regressions, critical-error labels, disagreements and the intersection of gains. The existing continuation signal requires **each assessor** to find at least two new complete acceptances across both broader groups, no P critical errors or acceptance regression, and complete technical execution. It does not secretly add a same-two-cases requirement. A positive signal supports a larger confirmation proposal only; promotion is always false. Token/time descriptors do not establish a provider invoice.

A successful whole rating that marks supported critical severity must use the whole `critical_error` judgment. The shared validator rejects a contradictory milder judgment for correction; it does not silently relabel or overwrite submitted ratings. The severity field covers supported meaning and is not automatically equal to every whole judgment: a critical error in unresolved material can still determine the whole judgment. Constrained-only reviews retain their separate severity endpoint. Historical ratings/results are not rewritten by this validation repair.

`check_review.py` exercises synthetic local recovery, preparation and summary paths plus rejection/denominator/blinding/decision mutations. Synthetic fixture labels are software checks, not translation evidence. The provider/GPU/model path remains unexercised by these checks. Existing old review tools, prompts, references, merits and twelve-output results are untouched.
