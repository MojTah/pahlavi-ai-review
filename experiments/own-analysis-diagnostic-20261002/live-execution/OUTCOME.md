# Completed direct versus own-analysis comparison

2 October 2026. [Job6abf6e59fbc85ba682369cf0](https://huggingface.co/jobs/Mojionix/6abf6e59fbc85ba682369cf0) completed the frozen nine-call schedule using retained Gemma4-31B step280. **Own analysis produced no newly accepted complete translation. Retain the checkpoint; the prespecified larger-confirmation signal fails. No training or automatic next job is admitted.**

Both fresh assessors independently accepted **1/3 direct finals and 1/3 analysis-fed finals** under the unchanged semantic merit. They accepted the same short Kanheri clause in both arms. These are three provisional development cases, not a 33% general translation-accuracy estimate, new benchmark, statistical improvement or unseen generalization. Two separate AI contexts are not independently calibrated or expert measurements.

| Case | Direct D: assessor A / B | Own analysis then P: assessor A / B | Paired interpretation |
|---|---|---|---|
| KANHERI01, arrival | accepted / accepted | accepted / accepted | Already accepted; no new gain. |
| AMOL1, obligation and receipt | critical_error / critical_error | critical_error / critical_error | Essential name and supported events still fail. P additionally invents a decree/ordering event. |
| BERLIN6, allocation and sealing | meaning_error / meaning_error | meaning_error / critical_error | P preserves restored year3(9), but remains unacceptable. Assessor B treats `روز 3 جو گریو` as misassigning the essential quantity to a calendar day; A leaves that parsing uncertain. Retain this disagreement. |

Per assessor: newly accepted cases **0**, acceptance regressions **0**, uncertain whole labels **0**, unavailable final slots **0**. P critical-error counts are **1/3 for A and 2/3 for B**, versus D **1/3 for each**. No acceptance regression does not mean no severity worsening: B flags Berlin P as a new critical error. No adjudicated replacement label is invented. [Validated paired summary](comparison-summary.json) preserves both submitted ratings and the original continuation rule; it fails for both assessors. Promotion remains false regardless of this exploratory result.

## Actual execution and evidence

Provider start08:42:07.609UTC, finish08:52:50.994UTC: **643.385 seconds**, approximately10m43s. At the freshly checked launch rate41667microUSD/minute, estimated compute is **USD0.44679871325**, approximatelyUSD0.45. This is interval-times-rate arithmetic, not a verified invoice or current balance. The approved allowance wasUSD3.01 with a60-minute native cutoff.

All **9/9 scheduled slots, dispatched calls and committed outputs** succeeded without cap, timeout, dependency skip, retry or replacement. GPU prefill passed on A10080GB. BF16 base/FP32 retained LoRA, eager attention, greedy seed42, fresh contexts/no thinking,2048 context,256 new-token ceiling and90-second cooperative per-call limit match the reviewed recipe. Zero optimizer updates; saved post-inference tensor check reports the loaded adapter unchanged. This was inference, not retraining.

Independently recovered and verified **46 small files totaling223,206 bytes**, including the manifest, from the exact run's `/final` export. All manifest-listed sizes/SHA256 hashes and provider path inventory match. Manifest SHA256 is `2f065307220a3c791573c6a26234ecadb736ebba12fa419ec487a0ac4deb20b9`. Initial lookup at the run root found no manifest; the existing final subdirectory was then recovered. No data was lost or job repeated. Model weights remain cloud-only.

The reviewed `review.py prepare` passed against real evidence: exact packet/recipe/source/checkpoint pins, execution accounting, raw outputs, first same-case analysis dependency, full resolved P prompts and frozen local tokenizer replay. Each of two fresh assessors saw only its six shuffled final records and identical complete provisional reference evidence, without arm labels, analyses, actual prompts, case IDs or the other's ratings. Raw output wording may still hint at the method; perfect blinding is not claimed. Both rating files passed the existing validator unchanged. [Assessor provenance](assessor-provenance.json), [recovery proof](recovery.json), [technical review](recovery-review.json) and [raw outputs](raw-predictions.jsonl) preserve the evidence.

Summed recorded workflow intervals: D **25.827s**, A→P **107.611s**, approximately4.17times D. Known committed generated tokens: D164; A→P688, including analyses. Subtracting those workflow intervals from provider elapsed time leaves an **unallocated residual of509.948s**, including shared startup/load/export/provider overhead; this is not a measured breakdown or an arm-specific charge. Tokens are not billing units. These descriptors do not prove production latency or repeated-run performance.

## Separate analysis observations, after final ratings were frozen

These are lead observations against the already qualified references, not a new scored endpoint or expert grammatical adjudication:

- Kanheri A calls `hamdēnīgān` “contemporaries” instead of the supplied fellow-believers meaning, while retaining plural past arrival. P nevertheless renders fellow believers correctly. Analysis can contain an error without that error appearing in the final; no internal causal conclusion follows.
- Āmol A treats the title `ostāndār` as “stand/remain,” lamp-oil refining as “extinguish,” and sealing `āwišt` as “be appointed/assigned.” It retains the1000 quantity, recipient and obligation, but supplies incorrect supported event interpretations. The final also has persistent defects; this experiment does not uniquely attribute each final error to A.
- Berlin A assigns the allocation agent to Zādānfarrox, whereas the qualified pairing assigns allocation to Friyag and sealing to Zādānfarrox. It correctly associates3 with grīw and marks the restored year uncertain, but leaves the manager and sealing functions unresolved. P preserves the year uncertainty yet fails whole translation, with the quantity-parsing disagreement above.

Thus generic self-analysis is not reliable external linguistic evidence. Do not turn generated A texts or these test references/reviewer corrections into training targets, clean away opaque words, or treat another prompt/epoch sweep as justified.

## Next decision

The present workflow does not meet its own continuation criterion; do not scale it or train on it. A first free [bounded token-coverage trace](coverage-trace.json) is now complete: the pinned step280 training file contains2,237rows, while the current resource contains9,971candidates. Normalized exact token search finds11older source rows for `mar`/`marī`, and no older source match for the checked title/refining/sealing/manager/ration forms. The current resource has lexical candidates for refining/sealing/ration and contextual candidates for all six query groups. This is spelling-bounded presence evidence, not proof of missing lemmas/senses, actual optimizer exposure or learned competence. The current candidates are not the retained checkpoint's training set; recent acquisition-model results remain separate historical evidence.

The next free local task is to qualify the **same senses and occurrence-specific roles** in the traced original records, checking their actual target languages and supervision rather than equating token hits with correct training. Use nonpanel training occurrences; never add this comparison's reference answers or reviewer corrections to training. Distinguish a missing lexical/occurrence target from a learned-task failure; preserve homographs, morphology and unadjudicated technical senses. This is not another blanket claim that every dictionary entry is certified.

The distinct critic [independently recounted the original corpora](coverage-review.json), matched all six query-group counts, hashes, IDs and lexical projections, and found no reporting error. This closes the calculation check that Astra's addendum deliberately did not perform; semantic qualification remains a separate next task.

After that trace, consider one matched adapter-off versus retained-step280 control on these exact source-only prompts if it can answer whether the retained adaptation worsens these outputs beyond the base. This exact matched control has not been established by earlier differently prompted baselines. It would diagnose adapter effect in this setup, not resolve reference truth or internal mechanism. Freeze and independently review a concrete proposal, expected decision, cost and execution safeguards before requesting any new run. No new model choice, recharge, paid job, training or local weight download follows automatically from this report.

External [Astra result review](../astra-result-review.json) **passes the completed experiment's reporting and bounded next step**. It verifies recovered evidence, actual prompt/token/dependency sequences and scoring arithmetic; its addendum checks trace internal consistency without recounting the underlying corpora. Dataset presence must remain separate from whether a model learned or can apply that supervision. It grants no further paid-run authority and does not certify the references as expert gold. Original cases, inputs, references, historical ratings and merit are unchanged.
