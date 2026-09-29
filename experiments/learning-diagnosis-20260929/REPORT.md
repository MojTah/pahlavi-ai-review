# Learning diagnosis before another training experiment

29 September 2026. **Local diagnosis and a 28-prompt packet are complete; model acquisition remains unmeasured.** The next proposed compute task is inference on the retained step280 and mixed96 checkpoints, not retraining. No cloud access, paid run, weight download, training-data mutation or benchmark-content read occurred in this work. The goal and training pause remain in force. Version impact: NONE (offline research analysis and diagnostic preparation).

Mode: Classic + Critic. Root owns analysis and files; `report_data_audit` performed read-only source triage, while `report_training_audit` performed read-only methods review. Existing qualification decisions were reused rather than commissioning another broad data review. The one standard-library script makes counts and packet reconstruction reproducible; no new model runner or translation pipeline was built.

## Findings that change the next step

1. **Most new target-token supervision was English.** The 384 auxiliary examples contain 9,351 supervised tokens, of which 7,866 (84.12%) belong to English-target tasks. These counts include terminators and, for CPD, JSON structure; they are not natural-language word counts. The main outcome asks for Persian passage translation. This is a task-alignment concern, not proof that English supervision is harmful. Per-example averaging also means token proportions are not gradient-influence proportions.
2. **The run never measured whether the new material was learned.** Saved mixed96 predictions contain only the 24 development translations. The historical teacher-forced and TRAIN-recall results concern step280. Neither provides a measurement of mixed96 dictionary or grammar recall. The correct status is **unmeasured**, not failed.
3. **Word matching is not sense matching.** The selected MMP entry `recovered:kosh:mmp:1030` teaches `ēr` as English “lower” under its published adjective scope. Historical `parsig:134004021:pal>fa` contains the same form with published Persian «آزاده». Its original qualification notes an interpretation as noble/free rather than the English edition's Iranian, and a softened superlative. This is not unique expert-certified gold. In `parsig:509000009:pal>fa`, `ēr kaft` appears in the passage rendered «فروافتاد». Both original targets and their complete historical qualification ledgers are preserved; the isolated MMP sense must not automatically replace either contextual reading.
4. **Apparent lexical coverage is inflated by common forms.** Exact normalized surface matching links selected lexical forms to 815 of the 2,237 historical records. The form `kē` alone matches 436 records. This only detects character sequences at word boundaries; it does not resolve morphology, homographs, register, compounds or senses. The detailed [surface links](surface-links.jsonl) are discovery candidates, not retrieval-admitted evidence or new labels.
5. **Many grammar prompts supply the analysis we want the model eventually to infer.** The selected S22 examples explicitly state roles, person or tense in their context. Correct answers therefore demonstrate conditioned-task recall. Removing those cues can change ambiguity; this packet does not silently turn the same target into unique context-free gold. Fifteen of 16 available teaching clauses were selected in mixed96; the remaining clause shares an exposed construction family. Unselected duplicate inscription openings are not fresh tests either.

Sources reused: [frozen training manifest](../mixed-supervision-20260929/data-manifest.json), [original task prompts](../mixed-supervision-20260929/prepare.py), [mixed outcome](../mixed-supervision-20260929/REPORT.md), [existing content review](../candidate-review-20260928/CONTENT-REVIEW.md), [context qualification](../contextual-supervision-20260927/qualification-decision-v2.json), [prior recall evidence](../train-recall-20260927/REPORT.md). This diagnosis preserves the existing provisional status; it does not certify the entire corpus.

## Frozen diagnostic packet

The descriptive question is: **What can each existing checkpoint reproduce under the actual auxiliary instruction, and which familiar contextual meanings does it preserve?** The quantities to report are paired, case-level changes within each module. Selection is deliberate and risk-focused, not a random accuracy sample. There is no statistical-significance or novel-language-generalization claim.

| Module | Prompts per checkpoint | Intended measurement |
|---|---:|---|
| Dictionary task recall | 6 | Two Persian, two CPD English and two MMP English records, actually selected in mixed96; preserve full alternatives and CPD structure |
| Conditioned grammar recall | 4 | Published agent/patient and tense contrasts under the complete original grammatical context |
| Inscription task recall | 2 | One arrival clause and one dated arrival clause; preserve participants and quantities |
| Historical contextual retention | 12 | All previously qualified contextual TRAIN parents; retain their occurrence-specific scope limits |
| Targeted sense applicability | 4 | Original historical passages contrasting `ēr`, `agār` and `agārīh`; full published targets, without inventing isolated-word gold |
| **Total** | **28** | **56 first attempts across two checkpoints** |

All 12 auxiliary records were exposed in mixed96. All 16 historical pairs were exposed in step280; 12 also received exact additional exposure in mixed96. Exposure is recorded per case. Pretraining exposure is unknown. Some dictionary records share an entry family, grammar rows share templates and inscription rows share a formula. These are fewer independent sources/constructions than prompts.

- [inputs.jsonl](inputs.jsonl) contains only opaque case IDs and exact original prompts. Original conditioned prompts retain their legitimate context; no new answer or reviewer metadata is inserted.
- [references.jsonl](references.jsonl) retains complete original learning records, published alternatives, expected serialized answers, exposure labels, all16 original historical qualification ledgers and existing scoped qualifications. Keep it local to review; do not mount it as model input.
- [census.json](census.json) binds inputs, source helpers, the script and generated payloads by SHA256. No trained weights or tokenizer downloads are needed for reconstruction.

The packet intentionally measures acquisition and familiar-context retention. It does **not** establish that a particular new dictionary entry caused an improvement, nor test unfamiliar-passage generalization. That would require a separately qualified occurrence link and appropriate independent context panel. The existing fixed development merit remains unchanged.

## Interpretation and scoring fixed before predictions

Run the same prompts on both checkpoints with identical model precision, template, generation settings and fresh context. Freeze the runner, actual checkpoint identities, output cap, time cap and spending bound before execution; those operational checks are not completed by this packet. Do not adjust prompts after seeing outputs, replace failed cases, or use references in generation. Preserve raw first attempts, errors, caps and missing outputs in the full denominator.

Reviewers should receive shuffled anonymous answers with the appropriate task, source and complete reference evidence, but no checkpoint or exposure labels. Keep reviewer results separate. Report:

- **Lexical tasks:** supported senses recovered, omitted senses, unsupported meanings and preserved grammatical/scope restrictions. For CPD, record structural validity separately from semantic preservation. A correct subset is partial, not full-inventory success. Do not invent Persian references for English tasks.
- **Conditioned grammar:** agent/patient, person/number and stated temporal distinction preserved, contradicted or unresolved. Success does not establish parsing without cues.
- **Inscription tasks:** participants, date/numbers and uncertainty under the published scope. The dated and undated formula are dependent cases.
- **Historical contexts:** retain the frozen whole-translation critical-error rubric and separately assess only the already qualified occurrence scopes. For the four additional sense cases, use full published targets and record uncertainty; no new isolated-word gold has been admitted.

Output a case-transition table and per-module counts, never one pooled “accuracy” across English JSON, short clauses and Persian passages. There is no post-hoc composite merit or lowered safety threshold. Improvement only on conditioned tasks, accompanied by poor passage results, would support further investigation of transfer/cue reliance; it would not prove the mechanism. Failure even on selected task records would raise acquisition/exposure or format questions first. Mixed or uncertain evidence should remain inconclusive.

## One next compute task; conditional training design

**First run the 56 inference attempts above after an exact cloud cost/readiness check.** Reuse the existing trained checkpoints. This is the smallest proposed measurement that distinguishes auxiliary-task performance from the already observed passage result; no extra training is needed to obtain it. The existing checkpoint comparison on DEV is already saved and does not need repeating merely to collect these diagnostics. Paid execution is not admitted by this local record, and current credit was not accessed or inferred from old notes.

Only if these measurements support a specific acquisition/retention question, consider one matched auxiliary-gradient ablation. Start both arms from identical step280 weights and fresh optimizer state. Hold the same 1,152 historical examples, order, 96 updates, schedule, historical loss coefficient and decoding fixed. For each update:

`L(w) = [sum(12 historical example-mean losses) + w * sum(4 auxiliary example-mean losses)] / 16`, with `w=0` versus `w=1`.

This tests adding the selected auxiliary supervision under a fixed historical schedule. Keep the divisor 16; renormalizing the control over 12 changes historical gradient dose. It does not equalize total gradients/tokens, isolate individual auxiliary families, or answer the benefit of training the entire expanded corpus. Gradient/optimizer equivalence, RNG handling and actual delivered schedule need verification before implementing or launching this design. Replacing auxiliary slots with more historical examples is a different recipe comparison because it changes historical exposure. No new training code was written here.

If the 56 outputs instead point to missing or inapplicable contextual evidence, resolve those bounded source/sense issues before choosing that ablation. Do not respond automatically with more epochs, more corpus collection, a new architecture, or a dictionary-to-sentence substitution pipeline.

## Verification and reproduction

Run from the project root with the shared Python interpreter:

```powershell
& '[USER_HOME]\.venvs\codex-science\Scripts\python.exe' -B -X utf8 'experiments/learning-diagnosis-20260929/diagnose.py' --check
```

The check reconstructs outputs in memory without modifying them, verifies upstream hashes and counts, checks exact original prompt/answer hashes, verifies selected-record identity and exposure, checks prompt/reference separation, and exercises diacritic/homograph/boundary cases in the mechanical surface matcher. It cannot validate philology or model quality. Generation is not implemented or invoked by this script.

Independent source review passed exact preservation of all28 learning records and answers. The methods critic caught missing parent-level interpretation caveats in the first draft; all16 original historical ledgers were then added and hash-bound without changing inference inputs. The critic reran the reconstruction check and passed the corrected packet and causal/scoring limits. Both agents completed; neither ran a model or edited files.

AutoCode review record:

- Lead agent/request id: /root
- Critic agent/request id: /root/report_training_audit
- Critic model and reasoning effort: Inherited unchanged from lead; no override requested or applied
- Evidence reviewed: diagnose.py, census.json, inputs.jsonl, references.jsonl and this report
- Verification evidence: Independent --check exit0; all16 original historical qualification ledgers preserved;28 exact prompt/answer identities and exposure joins verified
- Independent from lead: yes
- Critic verdict: pass
