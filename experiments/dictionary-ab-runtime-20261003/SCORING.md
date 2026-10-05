# Offline recovery and comparison

3 October 2026. This adds an adapter for the existing frozen DEV merit; it does not add a rubric or new judgments. Lead and worker each passed all 11 synthetic recovery/scoring tests, including the actual local CLI preparation path. No real model output or provider recovery was exercised.

`score_ab.py` checks the closed manifest, every file including logs/snapshots, the exact inventory and 16 MiB limit. It binds the retained model, adapter, reviewed runtime, original messages, source/work identity, longest-input canary and fixed 30 first attempts. It reuses the established review validator and preserves the original references and their qualifications. Every supplied rating file is preserved byte-for-byte.

An independent provider recovery receipt must list the manifest and every final artifact with matching byte count and SHA256. Its `independent_remote_verified` flag records the lead's actual provider observations. It is a trusted operator record, not a proof this offline program can independently authenticate. Mounted server readback alone cannot justify that flag. Keep the receipt outside the closed recovered folder; preparation copies it to the lead-only archive.

Preparation creates a fresh directory with two separately shuffled, opaque 30-record reviewer packets. Raw outputs, preview, recovery evidence and arm/work mapping stay in `lead-only/`. Share only the respective reviewer's packet and instructions in two separate fresh contexts. This hides condition labels, not similarities a reviewer might infer from the text. AI reviews remain provisional and can be correlated.

Scoring rebuilds every original packet and mapping from the recovered bytes before accepting reviews. Both complete valid 30-record reviews are required. Each arm retains a denominator of 15. For each reviewer, continuation requires a net gain of at least two accepted passages, newly accepted passages in at least two named works, no increase in critical errors and no accepted-to-critical regression. The four named works do not establish independent corpus families or statistical confirmation.

All 30 first attempts must be technically complete and independently recovered before primary scoring. An intact EOS abstention is technically valid and reviewed as not assessable; it is never accepted merely for completing. A valid A abstention followed by an accepted B may improve acceptance. A failed, missing, capped or interrupted A cannot create a semantic gain. Incomplete evidence retains all 30 statuses, creates no primary reviewer packets and returns HOLD. Complete local evidence without independent recovery can prepare packets, but primary scoring stays HOLD.

Use the shared Python interpreter with `-B -X utf8`. The CLI is:

```text
score_ab.py prepare RECOVERED_FINAL_FOLDER RECOVERY_RECEIPT.json FRESH_PACKET_FOLDER
score_ab.py score RECOVERED_FINAL_FOLDER RECOVERY_RECEIPT.json FRESH_RESULT_FOLDER --packet-dir PACKET_FOLDER --review-a REVIEW_A.jsonl --review-b REVIEW_B.jsonl
```

The exact one-shot launch handoff is in `EXECUTION.md`. No credential use, source transfer or paid submission has occurred. Fresh live checks and exact authorization remain before launch; GPU behavior and independent remote recovery remain later boundaries. Runtime Astra review is closed; the focused scoring/admission review is recorded separately when returned.
