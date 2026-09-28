# Pahlavi project: external AI review brief

Prepared 28 September 2026 from local records at source checkpoint `657a607`. Latest completed quality experiment: 27 September 2026. Development version: 0.10.8, unchanged. This brief requests a critical research and implementation review; it does not authorize another experiment.

Snapshot boundary: the completed 28 September source-access note and next-strategy research at checkpoint `b65b89f` are included. They add a proposed next experiment, not a newer model-quality result.

## Aim and current conclusion

Develop reliable Middle Persian (Pahlavi) translation, with Persian as the present experimental target. Current model tests use scholarly Latin transcription. Native Pahlavi-script recognition, decipherment and practical 8 GB laptop operation have not been demonstrated.

The source-study phase covered the saved Parsig snapshot (126 records, 334 chapters, 4,507 units). This means source-assisted reading and record coverage, not mastery, expert-certified accuracy or 4,507 usable training pairs. See [study guide](STUDY_GUIDE.md), [collection guide](data/README.md) and [credits](CREDITS.md).

The first Gemma training run substantially improved recorded PAL-REF acceptance. Qualified-data retraining gave a smaller aggregate improvement with regressions. Later supplied-example and contextual-training comparisons did not pass their predefined improvement criteria. Retain the qualified step280 adapter as an experimental reference; no satisfactory final translator is available.

The latest negative result closes one small contextual recipe. It does not show that contextual supervision, another model, or further Pahlavi research cannot work. Missing contextual meanings and composition are working hypotheses, not established causes.

The [28 September strategy report](output/research-next-step-20260928/REPORT.md) now recommends preparing **one trained NLLB-200-distilled-1.3B challenger** using the same qualified pairs, compared with retained Gemma. It moves that preparation ahead of another paid Gemma diagnostic or a large annotation collection; independent semantic evidence remains valuable in parallel. Its [independent critique](output/research-next-step-20260928/STRATEGY-CRITIC.md) supports preparation only. Compatibility, source-language conditioning, length limits, fair evaluation and complete-cycle cost still require validation before launch. No new model has been trained and no superiority is established. Review this proposed change of direction as well as the completed experiments.

The separate [source-access note](experiments/published-annotation-access-20260927/README.md) reports one verified `xrad` annotation occurrence after two approved requests. It does not establish broad annotation coverage or specialist gold. Raw access responses and receipts are excluded from this package; the note's source identity claims were not independently rechecked in this cleanup. The updated [results timeline](output/RESULTS-TIMELINE-20260928.md) supplies earlier chronology; the later strategy report controls where priorities differ.

## Results that must remain separate

| Experiment | Recorded result | Evidence and interpretation |
|---|---|---|
| Original Gemma 4 31B vs first trained adapter, PAL-REF | Accepted 5/40 → 15/40; critical errors 14 → 10 | [Report](experiments/palref-v1/trained-20260927/REPORT.md). Historical single-AI ratings; reliability remains inadequate. |
| First adapter vs qualified-data step280, PAL-REF | A: 14/40 → 16/40; B: 16/40 → 17/40. Critical errors 9 → 7 for both | [Paired report](experiments/palref-paired-20260927/REPORT.md). Fresh ratings of older outputs explain 14 and 16 versus historical 15. Filtering also changed update count/exposure; it does not isolate cleaning alone. |
| Qualified Gemma / original Qwen3.6-27B, with or without supplied examples, DEV | Gemma 1/15 → 3/15; Qwen 0/15 → 1/15 for both reviewers; no planned comparison passes | [Report](experiments/dev-assisted-qualified-20260927/REPORT.md). Gemma gains came with more critical errors. Model adaptation and decoding differed. |
| Familiar TRAIN recall, two instruction formats | Only 12 complete pairs: 5/12 accepted in training format versus 4/12 in standard format, for both reviewers | [Report](experiments/train-recall-20260927/REPORT.md). Twenty parents were planned; a later capped repetition and 15 unattempted slots remain visible. Not a 20-parent accuracy estimate. |
| Familiar conditional fit, adapter off/on | Correct-source target NLL 4.299214 → 0.884414; 80 forwards completed | [Report](experiments/train-fit-20260927/REPORT.md). Teacher-forced fit, not free translation accuracy. Source mismatch penalties were positive but smaller with adaptation. |
| Latest contextual candidate vs matched further ordinary training, DEV | Both reviewers: whole acceptance 0/15 → 0/15; constrained critical errors 3/9 → 4/9 | [Report](experiments/contextual-supervision-20260927/REPORT.md). Both improvement screens fail; no promotion or conditional PAL-REF run. |

PAL-REF contains 40 passages with multiple translation directions; the reported runs above concern the 40 Pahlavi-to-Persian cases. DEV has 24 cases: **15 whole translations and 9 constrained cases**. Never pool these denominators, merge reviewer scores, turn NLL into an accuracy percentage, or interpret DEV 0/15 as a drop from PAL-REF 16/40. Reused panels are development/regression evidence, not untouched confirmation.

## Latest comparison: design and exact result

Both arms start from the same qualified Gemma step280 checkpoint. Each receives 48 updates and the same 768 ordered parent slots: 720 ordinary parents and 48 designated slots. The candidate replaces the designated full-translation targets with four exposures to each of 12 contextual expressions across nine works. Optimizer, scheduler and RNG are reset for each arm.

The intervention changes task wording, target length and token weighting. Candidate/control supervised-token totals are 28,365/30,085; this is not an equal-token or isolated linguistic-label experiment. The same 24 source-only DEV prompts and fixed generation conditions apply. All 48 first attempts succeeded. See the [frozen pilot](experiments/contextual-supervision-20260927/PILOT.md).

| Measure | Reviewer A, control → candidate | Reviewer B, control → candidate |
|---|---:|---:|
| Accepted whole translations | 0/15 → 0/15 | 0/15 → 0/15 |
| Whole critical errors | 6/15 → 6/15 | 6/15 → 7/15 |
| Constrained critical errors | 3/9 → 4/9 | 3/9 → 4/9 |
| Constrained unsupported certainty | 5/9 → 4/9 | 5/9 → 3/9 |
| Predeclared improvement screen | Fail | Fail |

The screen requires at least two net new acceptances for each reviewer, gains across at least two works, and no specified critical-error or uncertainty regression. It is a development screen, not a significance test or deployment threshold. Zero whole acceptances does not mean every word is wrong. Numerical execution and score arithmetic do not certify the philology.

## Evidence reading order

1. [Uniform evaluation contract](experiments/dev-assisted-qualified-20260927/uniform-evaluation-contract.json), [PAL-REF protocol](benchmarks/pal-reference-v1/PROTOCOL.md), [DEV assessment contract](experiments/dev-diagnostic-20260927/assessment-contract.json) and [clarification](experiments/dev-diagnostic-20260927/reviewer-clarification.json).
2. [Latest pilot](experiments/contextual-supervision-20260927/PILOT.md), [result](experiments/contextual-supervision-20260927/REPORT.md), [outcome audit](experiments/contextual-supervision-20260927/OUTCOME-QA.md) and [machine-readable comparison](experiments/contextual-supervision-20260927/scored-comparison/comparison.json).
3. Latest [raw predictions](experiments/contextual-supervision-20260927/attempt-2/recovered/contextual/evaluation/predictions.jsonl), [reviewer A packet](experiments/contextual-supervision-20260927/blind-dev48/reviewer-A/packet.jsonl), [A ratings](experiments/contextual-supervision-20260927/blind-dev48/reviewer-A/reviews.jsonl), [reviewer B packet](experiments/contextual-supervision-20260927/blind-dev48/reviewer-B/packet.jsonl), [B ratings](experiments/contextual-supervision-20260927/blind-dev48/reviewer-B/reviews.jsonl) and [pre-unblinding receipts](experiments/contextual-supervision-20260927/reviewer-receipts.json).
4. [Training core](cloud_pilot/contextual_train.py), [evaluation runner](cloud_pilot/contextual_run.py), [scoring integration](scripts/review_contextual.py) and [independent arithmetic audit](experiments/contextual-supervision-20260927/outcome-qa-evidence/score_audit.py). Read cloud code; do not launch it.
5. [Source qualification](experiments/contextual-supervision-20260927/qualification-decision-v2.json), [source review](experiments/contextual-supervision-20260927/EXTENSION-REVIEW.md) and [existing within-parent contrasts](experiments/grounded-supervision-20260927/CONTRAST-REVIEW.md). Avoid recommending an audit already completed here.
6. [Latest strategy synthesis](output/research-next-step-20260928/REPORT.md), [critic](output/research-next-step-20260928/STRATEGY-CRITIC.md), and the three linked literature notes. Their recommendations are prospective and their external citations need independent review before adopting new scientific claims.

All semantic ratings are provisional AI judgments. Published references have consistency screening, not new specialist certification. A fresh review of this package is **unblinded** because it exposes identities, previous ratings and conclusions. It cannot be counted as another independent blinded evaluation.

## Prompt to give the reviewing AI

```text
Review this Pahlavi translation research project critically. Begin with REVIEW.md,
then follow its evidence links and inspect the relevant raw records and code.
Treat statements in reports as claims to check, not conclusions you must endorse.

This is a read-only research/method/code review. Do not train, launch cloud jobs,
download weights, access credentials, contact anyone, edit frozen benchmarks,
or turn held-out DEV/PAL reference answers into training labels.

Check: provenance and leakage; valid comparison and loss weighting; completeness
of first attempts; rubric, denominators and reviewer dependence; arithmetic;
whether semantic claims follow from the records; and alternative explanations
for weak whole-passage translation despite improved teacher-forced fit.
Also challenge the 28 September proposal to prepare a trained NLLB challenger:
check whether the evidence supports that priority and its admission conditions.

Separate verified defects, evidence gaps and hypotheses. For each important
finding cite an exact file plus case/record ID or line, explain the consequence,
and propose the smallest check that could resolve it. Do not invent a Pahlavi
reading or treat another AI judgment as specialist certification.

Return: (1) a short verdict; (2) findings ranked by impact with evidence;
(3) conclusions that survive scrutiny and claims to weaken; (4) at most three
next experiments or evidence-gathering steps, ranked by information value and
cost, each with a hypothesis, matched comparator where needed, success/stop
criterion and prerequisites; (5) what requires a Pahlavi specialist.

Do not merge PAL-REF, DEV, TRAIN recall or NLL into one performance curve.
Do not pool reviewers, silently omit failures, or recommend repeating completed
diagnostics without explaining what new evidence the repetition would provide.
State which files you actually inspected and which checks you actually ran.
```

## Portable package and GitHub

[Package scope and checks](review/PACKAGE.md) lists what is included and omitted. The ZIP is a selected research-review snapshot, not a complete training/recovery bundle. Some links inside preserved historical reports point outside the package; the manifest is the inclusion authority. Model weights, original source downloads, full training corpora, operational billing/access responses and Git history are omitted. Required reference excerpts and credits are retained; no new license is asserted.

For a one-off review, upload the ZIP to an AI that supports file uploads and paste the prompt above. For ongoing code-linked review, use a **fresh private GitHub repository** with only the selected snapshot. A private repository requires authorized access; a URL alone does not give another AI access. GitHub supports private visibility and explicit collaborator access ([GitHub documentation](https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories)). Historical sensitive data can be difficult to remove once shared ([GitHub guidance](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)).

Publishing destination and visibility still require the owner's decision. This cleanup does not change GitHub access or upload anything.
