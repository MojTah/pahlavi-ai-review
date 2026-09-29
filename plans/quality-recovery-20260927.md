# Quality recovery decision — 27 September 2026

**Current update:** qualified-data retraining and the paired fixed-test comparison are complete. Both reviewers find a small net gain with regressions. The science-grade review covers learning regimes, university/research-centre projects and scholarly books. The [completed feasibility checkpoint](../experiments/lexical-feasibility-20260927/REPORT.md) prepares 14 TRAIN review records and six Nyberg definition checks, with zero new accepted labels. The scarce untranslated finding applied only to Parsig: additional TITUS inventory identifies a 995-page / 199,043-raw-term candidate pool requiring source, rights and overlap qualification. Keep verified task-mixed supervision and CPT followed by SFT as conditional hypotheses. A 96-output Gemma/Qwen plain/assisted comparison remains a separate conditional development option. See [results](../experiments/palref-paired-20260927/REPORT.md) and [current research plan](../experiments/dev-assisted-qualified-20260927/PLAN.md). No new paid job is admitted. Earlier decisions and cost figures below, including the 48-output proposal, are historical.

**Decision: diagnose data and instruction sensitivity before another training run. Keep all model execution on the cloud. Do not download a model to the laptop until cloud quality is satisfactory.**

Update 27 September: the user explicitly raised the cumulative spending ceiling from USD 10 to **USD 25**, including the USD 6.19 already used. This does not authorize automatic recharge or model downloads. The first diagnostic retains its 55-minute native limit. Source-context qualification is complete: `assessment-contract.json` freezes 15 provisional whole-translation cases and nine constrained cases before outputs. The earlier plan and initial audit below remain the rationale; unresolved spans are preserved, not a demand for guessed gold or indefinite source research.

Completed diagnostic: all 96 outputs succeeded and were recovered; the GPU is off. Independent result audit passed. Both trained prompts accepted the same 3/15 qualified DEV cases versus 0/15 for base, with nine constrained cases separate. Estimated cumulative compute is USD 7.1103. Next: freeze source-selected TRAIN examples for one assisted condition (up to 24 new outputs) compared with cached D3. The original preparation below is retained as the pre-run plan; see `experiments/dev-diagnostic-20260927/REPORT.md` for results.

Classic + Critic: root is the sole execution owner and writer; three bounded read-only audits checked training preparation, true DEV membership and reference quality. Independent methodological critic `/root/philology_evaluation_review` conditionally supports the diagnostic, subject to completing reference and runtime/budget readiness. No paid job is running or admitted by this document.

## What the evidence supports

The completed model improved from 5/40 to 15/40 accepted PAL-REF translations under separate blind AI reviews, but ten critical errors remain. This is provisional improvement, not acceptable delivery or general translation accuracy. The same fixed test must not become the training curriculum.

The actual training payload contains 2484 Pahlavi-to-Persian rows. The frozen data and tokenizer identities match the completed run. Prompt masks and supervised turn-end tokens are valid, exact pair duplicates were removed, and maximum length 1113 is below the 2048 training limit. Wrong language direction, all-token supervision and truncation are not demonstrated explanations.

One work supplies 1136/2484 rows (45.7%). Only nine inputs are single whitespace-delimited words. This shows uneven coverage and little direct isolated-word supervision; it does not prove that vocabulary cannot be learned from sentences or that reweighting would improve quality.

Four identical-source groups have different target strings. Three appear to be punctuation, paraphrase or editorial-gloss differences. One pair—rows 324/774, `pursīd dānāg ō mēnōg ī xrad`—has a potential participant-level conflict. A bounded source audit confirmed that the omission already exists in raw Parsig data; preprocessing preserved it. The cited Persian edition (Tafazzoli 1379, pp.20 and40) was not available locally, so do not automatically correct the label. An independent offline reconstruction of every row also matched all token IDs, answer masks and exact decoded targets, including end-of-turn plus newline. Eight rows do not establish widespread bad alignment.

Training used a single user message containing its canonical instruction. Fixed evaluation uses system instruction plus raw source, including an explicit `[UNRESOLVED]` option; training contains no such answer targets. Both use the official template with thinking disabled. This is a genuine instruction-distribution difference, not proof of a serialization bug or its effect size. The run had no intermediate semantic DEV evaluation, so loss alone cannot choose epochs or learning rate.

## Resolve reference quality without paid compute

Use the existing authoritative DEV dataset, not a new final benchmark. Its 402 Persian-reference passages come from works 103, 112, 138 and 517, with verified manifest hashes and zero actual TRAIN/original TEST/PAL-REF work overlap. Historical DEV previously informed Qwen/ByT5 selection; it is development material, not pristine certification data.

A deterministic 24-passage subset (six per work, six source-length strata, minimum SHA256 of `42|record_id`) is preserved in `experiments/dev-diagnostic-20260927/`. It gives equal work emphasis, not the frequency distribution of the 402-row pool. Eligibility and selection use source/reference metadata, never model outputs.

The first blind reference screen found 13 cases without an obvious packet-level issue, seven with qualifications and four with missing readings or material disagreement. Next, inspect the cited source/context for those questions; preserve legitimate alternatives and unknown readings. Freeze which meanings/cases are assessable before inference. Keep unresolvable cases visible as uncertainty diagnostics and out of any claim of fully checked correctness. Do not substitute guessed gold or silently replace selected passages.

The older staged panel contains seven original TEST records, one explicit TRAIN recall control and other provisional materials. Preserve it unchanged; exclude it from tuning. The independently frozen 40-case PAL-REF benchmark, prompt, answers and scorer remain unchanged.

## First paid experiment, only after readiness

Use the current original base and the existing step 312 adapter; add no training. Compare the same DEV passages in a 2×2 design:

| Model condition | Instruction condition |
| --- | --- |
| Original BF16 base | Training-style instruction |
| Original BF16 base | Fixed-evaluation-style instruction |
| BF16 base plus step 312 adapter | Training-style instruction |
| BF16 base plus step 312 adapter | Fixed-evaluation-style instruction |

At most 96 first-attempt outputs for the frozen 24 passages. Same model revision, tokenizer, decoding, fresh context and per-case caps. No reference answers or dictionary context in inference. Balance condition order where practical; record all incomplete cases if the deadline ends the job. Do not report only the easier completed subset. A changed instruction is an explicitly different condition, never a revised standardized PAL-REF score.

Use opaque condition labels, a fixed randomized review order and the same blind review configuration across all conditions. Preserve case-level reasons, accepted/meaning-error/critical-error/uncertain/execution outcomes, and per-work paired gains/regressions. Reference uncertainty must not be misreported as model error or correctness. AI assessment remains provisional; this is a small diagnostic, not qualification.

**Updated prelaunch envelope:** provider billing shows USD 6.19 used; the user has raised the total ceiling to USD 25. The verified A100-large rate is USD 0.041667/minute. Native job ceiling is 55 minutes (USD 2.291685), with five additional minutes allowed for termination verification and USD 0.75 reserved for uncertainty. Conservative cumulative planning total is USD 9.44002. Automatic recharge stays off. No automatic second job or follow-on training.

The 55-minute limit replaces the initial 45-minute proposal based on measured input size. The 96-output reference-length proxy is 7276 tokens; previous trained inference produced 1308 tokens in about 211 seconds. A 1.5x generation allowance is approximately 1761 seconds. Reserve 90 seconds bootstrap, 60 adapter recovery, 360 download, 273 load/checks and 180 export: about 2724 seconds total, below the 3000-second internal deadline. This is a planning proxy, not a speed guarantee; output lengths may differ. The 2820-second compute alarm, 3000-second inner deadline, native timeout and controller remain independent limits. All setup, loading, export and shutdown count. The first real executions test adapter switching and generation; any system failure preserves partial evidence and stops the attempt, without an automatic retry.

## Decide from the diagnostic

- Prefer an instruction only if acceptance improves without increased critical errors or new substantive regressions on previously accepted cases; otherwise report a tradeoff or no clear winner. Report work-level behavior, not one pooled number alone.
- Gains concentrated under the training-style instruction support investigating instruction alignment first. They do not justify more epochs or changing the frozen benchmark.
- Gains under both instructions support the adapter within this DEV sample. Continued critical failures require targeted data diagnosis.
- Wrong attested word meanings motivate verified lexical supervision or a separately labeled reference-assisted trial. Correct words with wrong participants, negation or relationships motivate verified compositional examples. Those examples must come from permitted training material, not PAL-REF or original TEST answers.
- Ambiguous or unknown readings must remain uncertain or explicitly proposed hypotheses; generated guesses do not become training truth.
- If neither trained condition improves upon its matching original-base condition, do not automatically escalate training or model size. Reassess supervision and then compare a justified alternative intervention.

A reference-assisted condition may be valuable later, as the project's prior research recommends, but it adds evidence selection as another variable. Freeze a permitted TRAIN/dictionary source pool excluding held-out answers before testing it. Do not introduce it into this instruction diagnostic mid-run.

Only after a justified development improvement is fixed should the selected model undergo the unchanged PAL-REF comparison and an explicit cloud-quality acceptance review. No numeric delivery threshold has been agreed; 37.5% with ten critical errors clearly fails. Nothing in this plan authorizes an automatic laptop download or claims reliable unknown-word decipherment/native-script reading.

## Cleanup and evidence

The user-authorized cleanup removed the partial Q8 base, its transfer cache and the two local final-adapter copies: 1,021,571,418 bytes in total. Exact cleanup logs remain under `resources/local/`; the cloud original was rechecked against its stored content identity before deletion. Evaluation outputs, small provenance records, code and synthetic test fixtures remain. Prior local tensor-verification records describe checks performed before authorized deletion, not currently present model files.

Evidence: `experiments/palref-v1/trained-20260927/`, `experiments/dev-diagnostic-20260927/`, frozen v5 training bundle/provenance, and `cloud_pilot/{bundle.py,runtime.py,palref_eval.py}`. No model weights, training data, historical split, or benchmark were changed during this review.
