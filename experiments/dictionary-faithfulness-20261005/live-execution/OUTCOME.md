# Faithfulness instruction comparison: screen failed, measurement instability identified

5 October 2026. Same retained Gemma4 31B step280, same complete dictionary and source inputs. A uses the previous dictionary-assisted prompt; B adds one general instruction against unsupported glosses. All 30 fresh first outputs passed technical checks. No training or new model.

| Provisional fixed-rubric result | Reviewer A: existing instruction → new | Reviewer B: existing instruction → new |
| --- | --- | --- |
| Accepted whole passages, out of 15 | 1 → 2 | 2 → 2 |
| Critical errors | 5 → 5 | 6 → 6 |
| Newly accepted | 003 | 003 |
| Lost acceptance | None | 009 |
| Net accepted change | +1 | 0 |

Both reviewers fail the unchanged continuation screen: neither achieves net at least two new acceptances across two named works. Critical counts do not increase, and no accepted-to-critical transition occurs. Case003 improves according to both reviewers; that isolated result is insufficient for promotion. Preserve all judgments, including acceptance agreement 14/15 for A and 15/15 for B, and category/severity disagreements. This is a familiar exposed DEV panel and provisional AI assessment, not expert gold or unseen accuracy.

## Important measurement finding

All 15 control translations are byte-for-byte and output-token-for-output-token identical to the earlier dictionary-assisted B outputs. All 15 recorded input-token hashes also match. Nevertheless, the earlier reviewer cohorts accepted 5/15 each, while these fresh reviewers accept 1/15 and 2/15. Seven and six full judgment labels respectively changed on identical control text. This is rating variability, not a model regression. The scoring rubric and code remain fixed, but fixed rubric text alone does not make AI semantic judgments reproducible. The historical 2/15 → 5/15 result stays preserved as its original provisional observation; it is not a stable demonstrated accuracy estimate. No historical result is overwritten or re-rated here.

## Decision and next local step

Do not promote the new instruction or launch another GPU experiment from this result. Retain the existing reference model. Before spending on training or another prompt, audit the disputed accepted-to-rejected examples against the published references and case constraints, separate actual errors from defensible alternatives or reference omissions, and establish source-grounded adjudication/calibration. A Pahlavi specialist remains the strongest reference check. If a reference or judging rule requires correction, version it explicitly and recompare the affected historical outputs under one common panel; do not silently repair protected references, add panel-derived training targets or alter the frozen merit. Any future claimed improvement needs a reliable measurement and separately qualified confirmation.

Technical recovery verified 104 final files (103 manifest entries plus the manifest), 1,731,935 bytes, exact identities and recorded output-token/text/hash replay. GPU longest-input canary passed. Zero optimizer updates and unchanged retained adapter. Only small artifacts downloaded; model weights remain cloud-only. Actual job invoice/current balance were not refreshed.

Private raw files, frozen opaque packets, original review bytes and full scored evidence: `resources/local/dictionary-faithfulness-results-20261005/6b54f5bc4e984dbe9a4b53e89e4bf5d8/`. Durable evidence: [comparison](comparison.json), [semantic checks](SEMANTIC-CHECKS.json), [control repeat check](CONTROL-REPEAT-CHECK.json), [recovery checks](RECOVERY-CHECKS.json). Development-version impact NONE; no code change or automatic training admission. No Git remote is configured, so local commits are not GitHub updates.

## Bounded technical critic and AutoCode gate

Classic + Critic: reuse the existing frozen pipeline; Main integrates evidence, a separate critic verifies technical recovery, and two separate fresh contexts assess meaning.

- Lead agent/request id: /root
- Critic agent/request id: /root/faithfulness_recovery_critic
- Critic model and reasoning effort: gpt-6.1-sol, inherited effort (not independently exposed)
- Independent from lead: yes
- Evidence reviewed: score.py, PLAN.md, preview/review/final pins, recovery receipt and closed run/reconciliation metadata; no translations or judgments
- Verification evidence: independently checked 104 local hashes/sizes and exact closed inventory, current pins, 30-output accounting, unchanged adapter and zero optimizer updates; Main independently downloaded provider artifacts and ran the exact scorer successfully
- Critic verdict: pass

Critic limits: local hash checks cannot authenticate the lead-recorded provider observation; critic did not run token replay or certify meanings. Main executed replay. The two blinded semantic reviews passed schema checks; their unfavorable scores are preserved. Completed-result Astra review is requested separately and cannot grant new paid/training authority.

Actual AutoCode Critic validator: PASS on this report. All three local subagents completed; no local reviewer remains active. The exact completed-result request was sent once to the existing Astra chat; its verdict is pending.

## Completed Astra closure

[Astra completed review](ASTRA-COMPLETED-REVIEW.md) independently confirms the closed byte inventory, frozen reviews, screen arithmetic and all15identical historical/fresh controls. Packet content/instructions also match apart from opaque IDs. Bounded comparison/HOLD verdict: PASS; the preceding pending-review note is historical. Three diagnostic cases007/014/015 require source-grounded contextual-inference calibration. No reference omission or specialist linguistic adjudication is established. Original merit/reviews/references remain unchanged; no new execution or training authority.
