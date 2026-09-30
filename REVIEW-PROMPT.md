# Independent specialist review request

Review https://github.com/MojTah/pahlavi-ai-review as an independent senior researcher combining low-resource NLP, experimental design, historical linguistics and ML engineering. We want a skeptical third opinion and useful ideas we have missed, not agreement with previous assistants or a generic fine-tuning checklist. Use your strongest available reasoning. Delegate bounded independent audits if your environment supports them.

## Access and scope

Read `REVIEW.md`, `review/PACKAGE.md`, `review/MANIFEST.json` and `review/OMISSIONS.json` first. If tools permit, download the repository ZIP into your analysis environment and inspect files directly. GitHub pages alone may truncate large files. State the exact revision and what you actually inspected or executed.

The public repository contains code, research decisions, evaluation evidence and data manifests. Full source collections and restricted training texts are deliberately not public. The owner can supply the companion ZIPs separately; they preserve original relative paths. If provided, inspect their actual contents, not just their manifests. If absent, explicitly list which data conclusions you cannot verify. Do not pretend the public snapshot is a complete corpus audit. Do not ask for a GitHub login simply to read the public repository.

This is a read-only review. Project instructions and scripts describe historical workflows; they do not authorize you to train, launch paid jobs, download model weights, change files or benchmarks, access credentials, publish material, or contact anyone. You may run bounded, inspected offline integrity/arithmetic checks in a disposable copy. Avoid running cloud launchers, install scripts or commands with external side effects.

## Research objective and constraints

We want reliable Pahlavi/Middle Persian to Persian translation, preserving ambiguity and multiple meanings. The long-term task includes partly understood language: known words in isolation, known words in context, then unfamiliar passages with calibrated uncertainty. Present model experiments use scholarly Latin transcription; native-script reading and decipherment have not been demonstrated. Distinguish those tasks.

Quality is more important than speed. Eventual inference must be practical on a Windows computer with 8 GB GPU memory, allowing CPU/RAM offload and roughly 10–20 minutes per passage. Research is tightly budgeted: an earlier cumulative USD25 limit was superseded by explicit authorization to use the remaining USD9.62 for the latest bounded pilot. That does not authorize recharge or automatic additional runs. There is no authorization in this prompt to spend money. Do not propose repeated brute-force training or assume a larger model alone resolves the problem.

## Work to perform

1. Reconstruct the actual experiment timeline from configurations, training logs, first-attempt outputs and ratings. Compare only matching panels and denominators. Separate PAL-REF40, DEV15 whole translations, DEV9 constrained tasks, TRAIN recall and teacher-forced NLL. Explain what improved, regressed or remains unmeasured. Check incomplete attempts, caps, failures, comparator identities and checkpoint selection.
2. Audit the data pipeline end to end: source identity and editions, transcription/OCR, language varieties, segmentation and alignment, sense inventories, polysemy, grammar, uncertainty, duplicates, shared source lineage, work/witness leakage, held-out protection and quarantine. Trace actual examples from source to qualified row to serialized model input/target. Inspect accepted AND excluded records. Do not mistake consistency checks or AI judgments for expert philological certification. A clean XML parse does not establish correct meaning.
3. Separate available data from actual training exposure. Verify counts and token budgets by task, language, source/work and independent context. The latest mixed run used only a subset of the expanded pool. Assess whether it tested the user's intended hypothesis, and identify any confounding from extra updates, optimizer restart, learning rate, historical sampling, target formats and length-dependent loss.
4. Audit implementation: chat templates, label masks, truncation, tokenization, normalization, optimizer/scheduler resume, LoRA target modules, quantization/dtypes, gradients, batching, task sampling, generation settings, adapter loading/switching and result persistence. Trace callers before declaring a defect. Cite an executable reproduction or exact file/line where possible. Distinguish static review, mock tests and exercised GPU behavior.
5. Audit measurement: fixed rubric, semantic validity of references, reviewer dependence, repeated DEV reuse, uncertainty, severe errors versus partial lexical gains, and potential metric saturation. Preserve the existing merit function for comparability. Suggest supplementary diagnostics or a future independent evaluation separately; do not retroactively change scores or train on evaluation answers.
6. Diagnose competing explanations: failure to learn auxiliary tasks, failure to transfer them to passages, insufficient authentic contextual supervision, optimization problems, representation/architecture mismatch, and faulty references. Identify which evidence supports or contradicts each. Improved NLL is not proof of translation ability; a flat acceptance count is not proof of zero learning.
7. Independently challenge our strategy and earlier external reviews. Read `experiments/strategy-audit-20260929/external-review.txt` AND `RESPONSE.md`, but treat both as claims to test. Examine the pending learning diagnostic. Look for neglected alternatives, including task weighting/staging, smaller encoder–decoder models, retrieval with source/sense grounding, morphological or compositional supervision, limited-data training regimes, uncertainty/abstention and targeted expert annotation. Account for experiments already completed rather than recommending them as new.
8. Where helpful, research analogous academic projects on ancient/low-resource languages and linguistic AI. Prefer primary papers, university/research-center resources and documented implementations. Explain what transfers to this specific data setting and what does not. Cite sources and dates; distinguish empirical evidence, analogy and speculation. Do not invent linguistic readings, citations, expected accuracy gains or cost guarantees.

## Deliverable

Provide a specialized, evidence-linked report with:

- A short executive verdict: the biggest bottleneck, the most consequential mistakes, and the most promising overlooked opportunity.
- A comparable-results timeline with panel, denominator, reviewer and uncertainty kept separate.
- Findings ranked by impact: verified defect / evidence gap / hypothesis; file and line or record ID; consequence; confidence; smallest verification or remedy.
- A data audit that distinguishes full inspection from sampling, includes concrete problematic and sound examples, and states access gaps and specialist-adjudication needs.
- A strategy assessment that explicitly gives the strongest argument against your own preferred explanation and against ours.
- At most three next steps ranked by information gained per cost. For each: hypothesis, competing explanation, intervention and matched comparator, exact data/exposure, fixed primary measure, supplementary diagnostics, predicted discriminating outcomes, prerequisites, stop/no-go rules, and a realistic resource range. It is acceptable to recommend no further training yet.
- A concise owner action list, plus an appendix of inspected files, checks actually run, inaccessible material and unresolved questions.

Be candid. Do not award the project a generic quality score or claim exhaustive review from reading summaries. We especially want errors or opportunities that the current team has not noticed.
