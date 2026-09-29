# Independent DEV blinding and scoring review

27 September 2026. Lead `/root`; critic `/root/final_external_judge`. Classic + Critic. Review scope is the conversion and scoring code, frozen measurement contract and synthetic fixtures. No actual cloud outputs or reviewer ratings were opened, interpreted or graded.

**PASS for the repaired local blinding/scoring implementation. Both initially reproduced blockers are closed. No actual output quality or reviewer judgment has been evaluated.**

## Reviewed contract and conversion

Initial preparer SHA256 `dbb601e9ec806b4c4fe69c0fb39f2261d8e978441cf0fbf0975918ed4197153e`; scorer SHA256 `09a2126cb7a587ba81370b54028dad30c29378e65b4a7e1df15d45ce7a495d4b`; test SHA256 `a7a485697e6a7c524a8857267149b6e195d5504fe923f136de34e4979f122b6f`.

The preparer binds the unchanged uniform contract SHA256 `4165e8150f291c2cd6077d2daee86513ad08e1851acbfc3e83169bc40263f8c2` and all eight source-file hashes. It checks exact24-source/reference/assessment coverage, source equality and the whole-case work denominators4/5/4/2. The fixed15 whole translations and nine constrained cases remain separate. Reference translations, edition, notes, screening qualifications, expert flag and assessment constraints are preserved in local packets. No new reference, criterion or PAL-REF score is created.

Both families must match their frozen runner/model/prompt/evidence identities and schedule. Validation requires a unique ordered first-attempt prefix, exact source/prompt hashes, counters and explicit unattempted IDs; retries, duplicates, skipped IDs, successes after a fail-closed stop and mismatched metadata are rejected. Declared complete runs require all48 completed outputs. Raw input artifacts are preserved in the private archive. Missing outputs become visibly unattempted empty placeholders; they are never represented as generated answers.

Each reviewer receives96 records with independent opaque IDs and deterministic independently shuffled order. Packets omit model, condition, support examples, work/case IDs and historical outputs/scores. Actual output style can still suggest a model; no anonymization can guarantee absence of all inference from content. The model/condition mapping, randomization seeds, raw runs and provenance remain in `lead-only`. Reviewer instructions require fresh independent contexts and access only to the assigned folder. The lead must enforce that assignment; filesystem separation here is organizational, not an OS security boundary.

The scorer rebuilds the packets/private mapping exactly from their original runs and frozen references, verifies byte identities, freezes both review files, and writes a fresh output directory only after validation. Duplicate-looking outputs remain independent records. Every review must cover its complete96-record packet, copy its output hash, use all eight unchanged categories, and supply a rationale. Adverse successful-output judgments require a nonempty exact output substring. Accepted whole translations require affirmative core meaning categories; constrained cases cannot receive whole acceptance. Abstention, timeout, error and unattempted outputs cannot receive a meaning pass.

Four matched contrasts are reported separately for each reviewer: assisted versus plain within Gemma, assisted versus plain within Qwen, Qwen versus Gemma in plain mode, and Qwen versus Gemma in assisted mode. Counts retain full denominators; transitions, losses, work results, constrained severities and overconfidence remain visible. No pooled reviewer quality score, statistical significance or expert certification is claimed.

## Direct synthetic evidence and required corrections

Independently ran the original focused suite with the project HF interpreter: **nine tests passed in0.569 seconds**. Tests exercise identity/retry/order failures,96-by-two blinding and duplicate retention, fixed denominators under missingness, false acceptance and fabricated spans, four contrasts, reviewer separation, critical/overconfidence guards, fresh directories and the complete in-memory conversion/scoring path with tamper rejection. These are synthetic results, not model quality measurements.

Three additional independent synthetic reproductions exposed two gaps not covered by that original suite:

1. **Per-work gate silently tightened.** With three newly accepted cases across two works, one lost acceptance in the first work and therefore overall net+2, the scorer rejected the screen because the work nets were0/+2/0/0. The frozen rule says gains in at least two works while applying the net+2 requirement globally. The fix must count works containing newly accepted cases and retain work net changes as descriptive evidence; it must not retrospectively require positive net change in every contributing work.
2. **Attempted is not complete.** A validated run with all48 attempts but an error on its final constrained case could pass the screen. Separately, a complete Gemma pair could pass while all Qwen outputs were unattempted. Both contradict the plan's requirement that an incomplete four-condition comparison is inconclusive. All descriptive results and failures must remain available, but no prospective improvement screen may pass without both family runs complete under the fixed run contract.

The lead acknowledged both findings and assigned surgical repairs to the implementation owner. No actual output or judgment informed either correction.

## Frozen repair verification

The preparer remains unchanged at SHA256 `dbb601e9ec806b4c4fe69c0fb39f2261d8e978441cf0fbf0975918ed4197153e`. Final scorer SHA256 is `89ecf3fb0f521df833b90966fb35145ef22e10ab72a9aa7026d3272c1e68798c`; final test SHA256 is `69f25a1441b493f6a91bf709c0602f798b41fd7f1229b775f5798af28b889f85`.

Independently reviewed the frozen delta and executed `resources/local/hf-client-venv/Scripts/python.exe -B -X utf8 -m unittest tests.test_dev_assisted_review -v`: **11 tests passed in0.977 seconds**. The new work-gain regression exactly covers a gain and loss that cancel within one work, while another work supplies the global net+2. The scorer now reports both the works containing newly accepted cases and unchanged per-work net changes; it preserves the declared global threshold.

The new completion check is supplied from both validated raw runs by the actual `score` entry point. It requires final completed state,48 attempted and48 completed outputs per family, the full fixed ordered schedule and success/abstain statuses for every first attempt. Final errors/timeouts, missing outputs or a still-running final state make every contrast explicitly `inconclusive`, with `screen_pass` and both-reviewer screen values null. A summary called without completion evidence also defaults to inconclusive. Descriptive accepted/error counts and the15/9 denominators remain available. Regression variants cover a final Gemma error, final Gemma timeout, final Qwen error, missing Qwen output and a running Qwen state despite48 recorded outputs.

No additional concrete blocker remains in the reviewed scope. The frozen references, rubric, uniform contract and packet builder were not changed to repair the two decision-bookkeeping errors.

## Limits

This code validates identities, bookkeeping and declared review consistency. It does not establish semantic correctness of any reference or rating, absence of unknown foundation-model exposure, reviewer expertise or adequate statistical power. Fresh semantic reviewers must start without this review context or prior model outputs. The critic changes only this report; no cloud calls, model execution, data repair, commits or semantic ratings are authorized by this review.

## Independent critic record

- Mode: Classic + Critic.
- Lead agent/request id: /root
- Critic agent/request id: /root/final_external_judge
- Critic model and reasoning effort: inherited session settings, no override
- Independent from lead: yes
- Critic verdict: pass
- Evidence reviewed: Frozen uniform contract, relevant existing PLAN/LAUNCH requirements and benchmark category/acceptance logic; exact preparation/scoring/test sources at the hashes above; existing first-attempt validator; synthetic runs, packets and ratings only. Reference identity and coverage checks ran programmatically; no actual generated translation or human/AI evaluation rating was opened.
- Verification evidence: Original nine-test suite PASS0.569s; three independent in-memory reproductions established the two original blockers; final repaired11-test suite PASS0.977s with work-gain and whole-comparison completion regressions; source hashes matched and unchanged builder confirmed. Full synthetic conversion/scoring and packet-tamper rejection executed without file output. Actual96-output conversion and fresh semantic review remain subsequent lead-owned steps.

This pass is a code/methodology verdict for the stated local scope, not a translation-quality result, new metric approval or scientific certification.

Validation: exact-schema AutoCode Critic gate **passed**, exit0; scoped whitespace check passed.
