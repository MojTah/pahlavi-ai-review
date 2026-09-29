# Mixed-supervision pilot

**Comparison complete: both reviewers reject promotion.** Each accepts1/15 whole translations before and after; whole critical errors rise4→6 and3→6. [Outcome and recommendation](REPORT.md); [full comparison](scored/comparison.json). Retain step280. No new cloud job or model download.

29 September2026. One authorized Gemma4-31B continuation from qualified step280; the [cloud job](https://huggingface.co/jobs/Mojionix/6abb82b6e2f3c356be0389a3) was accepted at09:19:52UTC and verified RUNNING in dependency bootstrap. Root stopped after launch as requested. The job subsequently completed and the user-requested comparison is recorded above. No recurring monitor or further experiment is scheduled. The goal remains paused.

The [plan](PLAN.md) freezes96 updates,1536 examples and the unchanged DEV24 comparison. The [data manifest](data-manifest.json) binds258,988 sequence tokens and67,456 supervised tokens, maximum length1144/2048, with no truncation. Each update has12 historical translations,2 lexical tasks and2 other evidence tasks. The full10,151-record unique tokenized pool remains available; this pilot samples it and does not claim to train on every new dictionary entry.

Local preparation and the seven runner checks passed, including exact historical token parity, complete source/meaning/context projection, manual tiny-model loss/update parity, order, numerical failure, deadline and fixed first-attempt evaluation. The [independent review](REVIEW.md) found and verified fixes for the candidate adapter-name check and explicit20-step weight-change admission.

Native100-minute timeout;95-minute internal deadline;85-minute computation window;10-minute export reserve. At the verified rate, maximum compute reservationUSD4.16670 plusUSD0.50 contingency remains below the observedUSD6.27 headroom. [Budget observation](admission-observation.json) is separate from launch-time rechecks. Final and20-step adapters stay on cloud. A real20-step timing/numerical check decides whether the remaining updates fit; failure preserves evidence and ends the attempt.

The new dataset transfer, exact spec and later provider job ID are recorded in `transfer.json`, `execution-preparation.json` and `execution.json`. Cloud completion and persistence were subsequently checked; see recovery.json and OUTCOME-QA.md. Only small logs/evaluation files were recovered. Do not restart or download model weights automatically.

## Prelaunch review

The prelaunch independent data/runner review passed; its exact evidence and identities remain in [REVIEW.md](REVIEW.md). The completed-comparison gate below is the current handoff record.

Reproduce local checks with shared science Python: `-B -X utf8 experiments/mixed-supervision-20260929/prepare.py --check` and `-B -m unittest cloud_pilot.test_mixed -q`. Neither command submits a job or downloads model weights. The existing checked cloud bootstrap/export and local JSONL workflow are reused; no new scheduler or training framework was introduced.

Launch-time hashes, idle-job check, rate and budget passed in `launch-admission.json`; exact submission and startup status are in `submission-intent.json`, `execution.json` and `startup-log.txt`. Preparation checkpoint: `e0ba397629b4e9d9c4962600080ae0d751e829f9`. Frozen CRLF artifacts and final blank lines were preserved intentionally; the staged whitespace check used per-command CRLF/EOF formatting allowances without changing source hashes.

## User-requested comparison

Started 2026-09-29T11:05:50.199975+00:00. Mode: Classic + Critic. Root owns recovery/reporting; one converter writer owns the small mixed-run adapter; two fresh-context reviewers independently rate anonymized48-record packets; a separate critic verifies conversion and arithmetic. Existing preparation/scoring helpers and the frozen uniform contract are reused unchanged. Expected local review20minutes, warning30minutes; no new cloud compute, weights, paid calls or model launches. All48 paired first attempts remain; report15whole and9constrained separately for each reviewer. Main descriptive contrast is retained step280 versus96-update mixed continuation. No attribution to a particular source or claim of general accuracy. Completion means both reviews frozen, validated, mapped, independently checked and reported with the predeclared improvement screen.

## Completed comparison checkpoint gate

Mode: Classic + Critic
Lead agent/request id: /root
Critic agent/request id: /root/mixed_launch_review
Critic model and reasoning effort: Inherited parent settings; no override.
Independent from lead: yes
Evidence reviewed: Completed recovery, exact anonymous48-record packets per reviewer, frozen ratings and reviewer receipts, comparison.json, REPORT.md.
Verification evidence: Independent file rehashing,30-file byte replay,96 packet records reconstructed, two tests passed, all scores/transitions/screen flags independently recomputed, report evidence checked; see OUTCOME-QA.md.
Critic verdict: pass

The integrity/report audit passes; both scientific improvement screens fail. Gate formatting recovery: the first invocation against OUTCOME-QA.md lacked required labels; the next README invocation found duplicated prelaunch/current labels. The prelaunch record now links REVIEW.md, leaving one current gate record. No source, ratings, score or audit conclusions changed.
