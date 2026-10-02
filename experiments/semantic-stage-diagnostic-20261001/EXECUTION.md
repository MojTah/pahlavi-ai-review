# Single authorized launch and startup handoff

**Launch-mechanism clarification,2October:** the caller creates the exclusive `submission-claim.json` before the one API POST; `submit_once` does not create that claim itself. The historical wording below attributes both steps too broadly to the helper. Existing receipts/claim and this completed job's results remain unchanged. The new own-analysis proposal explicitly separates these steps.

Submitted once1October2026 at17:56:29UTC (14:56:29America/Halifax): [HF job6abe9ecdfbc85ba682363d86](https://huggingface.co/jobs/Mojionix/6abe9ecdfbc85ba682363d86). Run identity `4b81ec26dfa248959a18538067f261d6`; output prefix `semantic-stage-diagnostic/4b81ec26dfa248959a18538067f261d6` in the existing private bucket.

At17:57:20UTC, provider confirmed **RUNNING** and logs confirmed checksum-verified inputs and dependency bootstrap started. Setup had not completed and experimental inference had not started at this handoff. Initial dependency download timeouts were followed by successful download/progress; this is not a new job or an inference retry. No quality result is claimed.

Live API confirmed A100-large USD0.041667/minute, no active/matching jobs and fresh output prefix. Billing page showedUSD18.95 credit with automatic recharge off. Native60-minute bound permitsUSD2.500020compute plusUSD0.50reserve, within the conservative **USD3.01 one-job allowance**. This is an allowance, not an invoice or permission for another job.

The16,844-byte prompt-only JSONL was uploaded and independently read back with its exact SHA. Original qualified6,372,448-byte bundle was read back and verified. Retained manifest/config/provenance/status hashes and remote weight size were checked; weights were not downloaded locally. Initial staging found an SDK generator/list mismatch; materializing that iterator completed staging under the same prepared run identity before any submission. The exclusive existing `submit_once` helper creates the preserved claim before the sole API call; provider receipt identifies the job.

Reviewed shared runtime, complete packet replay, both old/new actual-tokenizer/SDK/mock checks and AutoCode Critic gate passed before launch. Source checkpoint `3a7c45e`; job-spec SHA `8b38ba8441d0aad6ab21b0f3dcec53abee811d0cb58aad015377d3bb36930feb`. Exact prepared command, mounts, checksums, input staging and cost admission are saved beside this file. No credentials, references or assessment rubric were added to the model-visible input.

**Stop active monitoring here**, as the user previously requested. On return inspect this exact job, recover its small final/incremental artifacts and independently verify their hashes, then perform fresh label-blind semantic assessment using the frozen separate endpoints. Do not automatically resubmit, train, download model weights or consume additional credit. Provider completion alone does not prove twelve successful generations or satisfactory quality.

This workspace has no configured Git remote. These are local checkpoints, not a GitHub synchronization. Privacy restoration of the separate review repository already completed; no GitHub-access change is part of this run.

## Completion status check — 1 October,23:40America/Halifax

The user's status request resumed a bounded read-only check. Provider confirms COMPLETED. Independent small-file bucket readback verifies final manifestSHA `47ed875de9cbf7cfc766095053d3a223954bf57187550a8b370e2b160e86bc04`, run state, predictions and reconciliation:12/12technical successes, completed fixed schedule, saved adapter unchanged and zero optimizer updates. Full artifact inventory has not yet been recovered, and semantic quality assessment remains PENDING. See `live-execution/completion-check.json` for exact byte/hash evidence. No weights were downloaded.

Approximately653seconds from submission to the last recorded job log givesUSD0.45355estimated compute at the observed rate; this is not a provider invoice or a new billing observation. No new paid job, training or automatic retry was started. Next comparison uses the frozen task-specific endpoints, with conditional Zand interpretation and no internal-cause claim.
