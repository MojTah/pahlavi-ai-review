# Controlled model and evidence comparison

27 September 2026. **None of the four planned comparisons passes the frozen improvement screen.** The next step is a bounded linguistic diagnosis and qualification of supervision; these results do not justify another training run, a third model, or deploying the supplied-example workflow. Existing funded credit remains available. The overall improvement goal continues.

All 96 first attempts completed successfully, and both cloud jobs are off. Two fresh-context AI reviewers independently assessed every anonymous output. Their acceptance decisions agree on every whole-translation record; they differ on some error severities and uncertainty handling. The judgments are provisional, not specialist certification.

## Results under the unchanged rubric

Each condition has the same 24 DEV cases: **15 assessable whole translations and nine separately constrained passages**, from four works. A/B means the two independent reviewers, kept separate. These are development results, **not the forty-case PAL-REF benchmark**, not general population accuracy, and not pooled scores.

| Condition | Accepted A /15 | Accepted B /15 | Whole critical errors A /15 | Whole critical errors B /15 | Constrained critical errors A/B /9 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Qualified Gemma step280, source alone | 1 | 1 | 3 | 4 | 4 / 4 |
| Qualified Gemma step280, supplied examples | 3 | 3 | 6 | 5 | 6 / 5 |
| Original Qwen3.6-27B, source alone | 0 | 0 | 6 | 6 | 6 / 7 |
| Original Qwen3.6-27B, supplied examples | 1 | 1 | 6 | 6 | 5 / 5 |

Gemma assistance adds the same two acceptances for both reviewers, cases002 and009, spanning works103 and112, without losing an acceptance. However, whole critical errors rise by3 for A and1 for B, and constrained critical errors rise by2 and1. Both reviewers identify new critical failures in cases004,008 and018 (004/018 are constrained). Reviewer B additionally identifies new unsupported certainty in constrained case004. Therefore the acceptance gain does not pass the predeclared guardrails.

Qwen assistance adds only case002, in one work. Whole critical counts remain6, but both reviewers identify new critical errors in cases013 and015 alongside other improvements; an unchanged total does not mean unchanged failures. Reviewer A additionally flags new overconfidence in constrained cases004 and018. Qwen does not outperform qualified Gemma in either matched evidence condition: it loses acceptance on003 without examples, and003/009 with examples. None of these four matched contrasts passes both reviews. No accepted-to-critical transition occurs, but this alone is insufficient to pass.

All accepted whole translations occur in works103 or112; neither system receives a whole acceptance in works138 or517. The fixed whole-case work denominators are4,5,4,2. Detailed case transitions, category counts, constrained uncertainty and reviewer disagreements remain in [comparison.json](scored-comparison/comparison.json); no failures or difficult cases were removed.

## What this changes

Keep qualified Gemma as the existing development baseline. Do not promote these supplied examples as an improvement or infer that switching to the tested unadapted Qwen configuration solves the problem. The broad model-family assumption has now been challenged empirically rather than only through research.

The completed seven-case diagnosis covers the two agreed Gemma gains and all agreed newly critical assistance cases across the models:002,009,004,008,018,013,015. The two gains have relevant sense/construction support. The failed cases often lack evidence for the decisive technical sense, polarity or participant relation; case015 also contains a negative phrase matching an unrelated witness. These observations suggest missing evidence and possible misuse, but do not establish causation. The audit checked28 actual outputs and19 supplied witnesses. This is openly exposed DEV analysis, not new training supervision; no reference answer or corrected DEV output may become a training label. See [ERROR-DIAGNOSIS.md](ERROR-DIAGNOSIS.md).

The single next prerequisite is a small, linguistically qualified sense/construction evidence pack drawn from independently sourced, non-held-out material. Preserve citations, contextual meanings, imperative polarity, participant roles, scope and unresolved readings. State what each witness supports instead of equating token overlap with meaning coverage. This prerequisite can be prepared without paid GPU time; a missing label remains missing rather than being supplied from a DEV answer.

The earlier source audit still has **zero newly admitted lexical/grammar labels** and no admitted external CPT corpus. Therefore another training objective is not ready merely because credit remains. The preferred next training hypothesis remains translation plus independently grounded lexical/construction supervision, conditional on actual qualified labels. CPT remains a separate conditional hypothesis, not a fallback job on unqualified text. The existing [source decision](../lexical-feasibility-20260927/SOURCE-DECISION.md) and [book-access findings](../lexical-feasibility-20260927/BOOK-ACCESS-FOLLOWUP.md) record concrete prerequisites. No automatic extra epochs, new retrieval selection, synthetic expansion, or additional paid run follows from these negative results.

## Execution, cost and reproducibility

| Run | Outputs | Confirmed terminal state | Conservative compute estimate |
| --- | ---: | --- | ---: |
| [Gemma job](https://huggingface.co/jobs/Mojionix/6ab8dfdc52d0dbd7f1d9b0f3) | 48/48 successful | CANCELED09:37:11UTC, after verified persistence | USD0.697174 |
| [Qwen job](https://huggingface.co/jobs/Mojionix/6ab8dfed6b030d633f6988a4) | 48/48 successful | CANCELED09:34:54UTC, after verified persistence | USD0.589664 |

Combined conservative wall-time estimate: **USD1.286838**, including scheduling/control time, not a finalized invoice. The combined reservation wasUSD4.58337 plusUSD0.75 allowance. The HF billing UI observed by09:54:59UTC showed **USD17.12 remaining credit**, current-period usageUSD13.15 and automatic recharge unset. Balance and usage updates need not reconcile synchronously; no payment or recharge was made. Refresh credit/rate before any later paid admission.

Both full-model A10080 canaries passed. All 96 outputs are first attempts, with zero errors, timeouts or output-cap hits. All11 declared small result files, totaling682,923 bytes, passed full SHA256 recovery. A final API check found no active jobs. **No model or adapter weights were downloaded to the laptop.** Local8GB operation, quantization quality and eventual latency remain untested. Exact manifests, canaries, shutdown events and costs are preserved in [execution-result.json](execution-result.json).

The launch source is commit`0b773cee14a4c491f13d3a511bccac1db5bc9fc4`; recovery and reviewed scoring tools are checkpoint`02f8b3f`. The same literal task, sources and58 qualified TRAIN attachments were used across model families, with model-native templates. Within each model decoding was fixed; Gemma was adapted and greedy, Qwen unadapted with its declared sampling policy. This is an operational comparison, **not an isolated causal architecture or training-regime effect**. No repeated-seed estimate is available, and weak unadapted Qwen performance does not establish its post-training ceiling.

The frozen [evaluation contract](uniform-evaluation-contract.json), SHA256`4165e8150f291c2cd6077d2daee86513ad08e1851acbfc3e83169bc40263f8c2`, and all eight bound source files were revalidated. PAL-REF and its historical scores are unchanged. EarlierDEV and PAL-REF scores used different outputs/review panels and cannot be treated as a matched causal regression against this table.

ReviewerA is `/root/dev96_blind_a`, reviewerB `/root/dev96_blind_b`; both were spawned with fresh history and received only their own sanitized packet/instructions. Each reviewed96 outputs with distinct randomized opaque IDs, without condition identity, supplied witnesses, historical scores or the other review. Raw review SHA256: A`4e89104f4f26e0f40010add2cf0e04f1f8d219f19a8a22475ad5baf5abc4f2e6`; B`55ff464d3d192ab5ea56637d044a19dcb2f96d0db33a6002f7e46ff9f60e413f`. These are independent contexts, not independent human experts or a guarantee against shared AI biases. Raw packets, private mapping, runs, ratings and [review freeze](scored-comparison/blind-review-freeze.json) are retained.

The [blinding/code review](BLINDING-REVIEW.md) passed11 focused checks and the AutoCode Critic gate. Actual scoring revalidated full run identity, exact prompts/schedule, packet reconstruction, review coverage, hashes, schema and quoted evidence spans before producing the result. A separate [result audit](RESULT-REVIEW.md) checks the arithmetic and provenance independently; its verdict does not certify the linguistic judgments.

```powershell
& resources/local/hf-client-venv/Scripts/python.exe -B -X utf8 scripts/score_blind_dev_assisted.py experiments/dev-assisted-qualified-20260927/blind-comparison experiments/dev-assisted-qualified-20260927/blind-comparison/lead-only/raw/gemma280 experiments/dev-assisted-qualified-20260927/blind-comparison/lead-only/raw/qwen36_27b resources/local/dev96-score-reproduction-FRESH
```

Use a fresh output directory; the scorer refuses overwrite. The two-net-gain rule is a conservative operational screen, not statistical significance or a deployment standard. Four works, repeatedly inspected DEV material, uncertain references and provisional AI assessment limit generalization. Specialist adjudication and a separately curated, unexposed confirmation set remain necessary for research-grade correctness claims.
