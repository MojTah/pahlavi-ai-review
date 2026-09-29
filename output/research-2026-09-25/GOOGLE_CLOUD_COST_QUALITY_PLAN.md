# Google Cloud cost, quality and investment plan

Prepared 25 September 2026. USD; Compute Engine baseline us-central1 (Iowa). Public list prices, not an account quote. This addendum extends the completed foundational research; it does not authorize cloud spending or a new training run.

Work mode: Agent Company, with root as sole artifact writer, a bounded primary-source pricing/model comparison researcher, and independent QA/Judge review. The main training task remains the execution owner.

## Recommendation for the investment decision

**Invest first in a comparison that can reveal a useful translator, then fund the method that wins on meaning. Do not buy a large training campaign merely because the current small model failed.** Keep large models and full training eligible. The proposed broad comparison has about **$905 of cloud usage, or $1,177 with 30% contingency**, plus separately budgeted scholarship and engineering. A proposed $1,000–$1,500 cloud allowance is a planning range, not approved spending or a promise that every job finishes within it.

The strongest near-term candidates are a capable hosted model using verified references, a 7–12B versus 27–30B open-model comparison with matching evidence, and targeted adaptation of the promising base. Preserve the existing ByT5 baseline and compare ByT5-XL where aligned data support it. A larger continued-pretraining campaign remains a later option if the evidence identifies missing language knowledge and a suitable corpus can be assembled.

The current project record establishes serious meaning failures in the inactive Qwen3-4B adaptation. ByT5 has completed three epochs but its translation comparison is pending. **There is no measured Pahlavi quality ranking for these cloud candidates.** Neither a larger GPU nor declining training loss establishes better translation.

## What paying for 27–30B instead of 7–12B might buy

These sizes mean **billions of parameters**, not millions. They describe model capacity, not the number of Pahlavi examples learned.

| Desired gain | Why extra model capacity might help | When paying for size is unlikely to solve it |
|---|---|---|
| Correct meaning across a passage | Better use of clauses, referents, exceptions and supplied examples | Missing or mistranslated source evidence |
| Choose the right sense of a word | Better reconciliation of grammar, genre and dictionary evidence | The relevant historical sense is absent or the reference is wrong |
| Translate an unfamiliar combination | More capable composition of learned constructions and explicit rules | Neither training nor references establish the construction |
| Learn from a modest adaptation set | A stronger pretrained representation may need fewer new examples | Repetition of the same few works or unverified synthetic targets |
| Reduce expert work | Fewer substantive corrections and repeated checks | Smoother prose conceals the same negation, role or factual mistakes |

These are **testable expectations**, not measured Pahlavi gains. My expectation is more favorable for using supplied evidence and maintaining context than for magically knowing unattested Pahlavi meanings. A failure to preserve “must not lend” is a meaning error even if the English becomes elegant. Resolving water versus milk requires correct lexical/contextual evidence as well as a model able to use it.

There is concrete evidence for trying the larger size, although it cannot predict the Pahlavi gain:

| Published comparison | Smaller → larger | What the result means |
|---|---|---|
| TranslateGemma 12B → 27B, WMT25 ten language pairs, human MQM | 7.94 → 5.86 | 26.2% lower weighted error score; not 26.2% more correct sentences |
| Same models, WMT24++ 55 languages, COMET22 | 83.5 → 84.4 | +0.9 metric points; not a percentage of translation accuracy |
| Hy-MT2 7B → 30B-A3B, WMT25 twelve directions | XCOMET 63.86 → 62.89; GEMBA 82.24 → 84.34 | Mixed automatic/judge results; larger is not uniformly better |

These are publisher-reported modern-language results, not our replication or a clean causal isolation of parameter count. Google's professional human review is more directly informative about translation errors than model size alone. Neither establishes Middle Persian competence. [Google model card](https://huggingface.co/google/translategemma-27b-it), [Google technical report](https://arxiv.org/pdf/2601.09012), [Tencent technical report](https://arxiv.org/html/2605.22064v1)

The pretrained weight files already exist: [TranslateGemma 12B](https://huggingface.co/google/translategemma-12b-it/tree/main), [27B](https://huggingface.co/google/translategemma-27b-it/tree/main), [Hy-MT2 7B](https://huggingface.co/tencent/Hy-MT2-7B/tree/main), [30B-A3B](https://huggingface.co/tencent/Hy-MT2-30B-A3B/tree/main). Google's files require accepting its usage terms. We would adapt these existing models; we are not waiting for a finished Pahlavi release. Stock TranslateGemma language/template constraints require deliberate Pahlavi support before admitting it to a trial; do not silently label Pahlavi as modern Persian.

TranslateGemma 12B/27B are dense models. Hy-MT2's 30B-A3B has approximately 30B stored parameters with 3B active per token, so 7B-versus-30B also changes architecture. Its weights still occupy roughly 60GB in BF16; fewer active parameters do not guarantee proportionally lower total costs. [NeMo architecture documentation](https://docs.nvidia.com/nemo/automodel/latest/model-coverage/large-language-models/hy-mt-2)

Training quality can outweigh parameter count. A LoResMT 2026 study reports that targeted distillation enabled 2–3B systems to match or exceed much larger systems on its evaluated low-resource languages. That result supports testing better supervision, not assuming its teacher can translate Pahlavi. [Primary study](https://aclanthology.org/2026.loresmt-1.1/)

Modern-language scaling evidence is encouraging but has limits. MiLMMT reports improved multilingual translation with both adaptation data and model scale, but explicitly limits its scaling study to models below 15B. It does not establish a Pahlavi 12B-to-27B return. [Paper, sections 5–6 and limitations](https://arxiv.org/html/2602.11961v3)

Repeated generation is another investment option, but not a guaranteed substitute for a stronger model. A WMT24 study found useful best-of-N gains in supported settings and failures from metric blind spots in a low-resource setting. A Pahlavi reranker must first be checked against expert judgments. [Primary study](https://arxiv.org/abs/2509.19020)

### Keep the quality questions separate

| Method | Potential benefit worth testing | Main uncertainty | Investment position |
|---|---|---|---|
| Strong hosted model + verified references | Contextual interpretation and explicit use of scholarship | Fluent unsupported interpretations; Pahlavi competence unmeasured | First diagnostic candidate |
| Open 7–12B + references | Controllable baseline; potentially sufficient after good adaptation | May fail to integrate complex evidence | Compare directly with a larger sibling |
| Open 27–30B + references/adaptation | Better evidence use, ambiguity resolution and composition | Extra capacity may add no useful Pahlavi gain | Worth a bounded trial, not yet justified as the winner |
| Open ~72B | Tests whether the smaller candidates hit a capacity limit | More expensive setup and inference; still needs language evidence | Keep eligible; expand if the smaller-vs-larger trend or strong hosted result warrants it |
| Managed Gemini SFT + references | More consistent task behavior and terminology | Can learn errors/overfit; limited training controls | Compare tuned and untuned versions of the same base |
| ByT5-XL full adaptation | Direct learning of source forms and aligned translation | Generalization beyond the corpus and long byte sequences | Complementary translation-specific experiment |
| Open-model continued pretraining + full adaptation | Learn more language structure from a broader corpus | Corpus quality/coverage, forgetting and training effectiveness | Fund after a data audit and a bounded positive pilot |

The evidence requirement for all rows is the same: better meaning on new, independently reviewed material. There is no defensible “70% versus 90% Pahlavi accuracy” forecast from parameter count.

## Concrete cloud configurations

Full-machine rates below already include the attached GPUs, CPU and RAM; A2/A3 bundle local scratch SSD. Do not add those charges twice. Durable storage, networking and tax are additional. [On-demand pricing](https://cloud.google.com/products/compute/pricing/accelerator-optimized), [machine specifications](https://docs.cloud.google.com/compute/docs/accelerator-optimized-machines)

| Configuration | GPU memory | vCPU / RAM GiB | On-demand $/hour | Example purpose |
|---|---:|---:|---:|---|
| a2-ultragpu-1g | 1 × A100 80GB | 12 / 170 | 5.0688 | 7–12B or 27–30B inference |
| a2-ultragpu-2g | 2 × A100 80GB | 24 / 340 | 10.1376 | ByT5-XL full-tuning pilot |
| a2-ultragpu-4g | 4 × A100 80GB | 48 / 680 | 20.2752 | ~72B inference or smaller full tuning |
| a2-ultragpu-8g | 8 × A100 80GB | 96 / 1,360 | 40.5504 | Larger full tuning / continued pretraining |
| a3-highgpu-1g | 1 × H100 80GB | 26 / 234 | Unavailable | Single-GPU alternative via Flex/Spot |
| a3-highgpu-8g | 8 × H100 80GB | 208 / 1,872 | 88.4900 | Faster cluster candidate; profile throughput |
| g4-standard-48 | 1 × RTX PRO 6000 96GB | 48 / 180 | 4.49993 | More memory for open-model inference |

These are starting allocations, not measured fit guarantees. BF16 weights alone require approximately 14–24GB for 7–12B, 54–60GB for 27–30B, and 144GB for 72B, before cache and runtime overhead. Context, batching and implementation determine fit. Full tuning adds gradients, optimizer states and activations; it is not covered by the inference estimate. G4 optional SSD is budgeted separately. GPU capacity cannot be treated as one unsharded memory pool.

A 12B and 27B model may both use the same $5.07/hour VM. The larger model may process fewer passages per hour. Compare **cost per successfully reviewed passage**, not just VM price. Changing A100 to H100 with the same checkpoint, precision and inference settings mainly changes speed/capacity; it does not confer language knowledge. Quantization is a separate quality intervention and must be evaluated.

### Alternative allocation modes

| Machine | Spot $/hour | Flex-start $/hour |
|---|---:|---:|
| a2-ultragpu-1g | 3.04124 | 2.40 |
| a2-ultragpu-2g | 6.08248 | 4.80 |
| a2-ultragpu-4g | 12.16495 | 9.60 |
| a2-ultragpu-8g | 24.32990 | 19.20 |
| a3-highgpu-1g | 6.62029 | 4.79 |
| a3-highgpu-2g | 13.24057 | 9.58 |
| a3-highgpu-4g | 26.48115 | 19.16 |
| a3-highgpu-8g | 52.96230 | 38.32 |
| g4-standard-48 | 1.77164 | 2.25 |

Spot prices are variable and jobs may be interrupted. Flex-start waits for capacity and allows runs up to seven days; it is not ordinary Spot. One-, two- and four-H100 A3 High shapes require Spot or Flex-start. Longer campaigns need checkpointed allocations or another provisioning mode. Google announces Flex/Calendar price changes in November 2026. Requote before execution. [Spot pricing](https://cloud.google.com/spot-vms/pricing), [Flex pricing](https://cloud.google.com/products/dws/pricing), [Flex behavior](https://docs.cloud.google.com/compute/docs/instances/about-flex-start-vms)

A2 Ultra, A3 High and G4 are listed in us-central1, but no user-account capacity/quota check has been performed. Regional availability is not a reservation. Official pages disagree on A2 Ultra 1g local SSD (275 versus 375GiB); the hardware specification says 375. This estimate uses the published full-machine rate without relying on that scratch-capacity discrepancy. [GPU locations](https://docs.cloud.google.com/compute/docs/regions-zones/gpu-regions-zones)

## Hosted inference and managed adaptation

Google's managed generative pricing currently redirects from Vertex AI to Gemini Enterprise Agent Platform. For requests up to 200k input tokens, Gemini 3.1 Pro Preview is $2 per million input tokens and $12 per million billed output tokens; Gemini 2.5 Pro is $1.25/$10. Reasoning tokens count where billed. These are priced candidates, not a Pahlavi endorsement. [Managed pricing](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing)

At an illustrative **20,000 input + 2,000 billed output tokens per call**, 1,000 calls cost **$64** for 3.1 Pro or **$45** for 2.5 Pro. The same call count in eligible 3.1 Pro Batch/Flex is $32. Longer contexts, more reasoning, retries and repeated rounds change the bill. Actual response time is not measured.

Managed Gemini 2.5 Pro supervised tuning costs **$25 per million training tokens**, including repeated epochs: a 3M-token formatted dataset × four epochs costs **$300**; 1M × four costs $100; 10M × four costs $1,000. Tuned inference is additional. Count the actual formatted training tokens before booking a job. [Managed pricing](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing)

Gemini 2.5 Pro is in the supported SFT list; Gemini 3.1 Pro is not listed there. The service exposes adapter tuning rather than an unrestricted full-weight/CPT recipe. Compare tuned 2.5 Pro against untuned 2.5 Pro with matched evidence and settings; comparing only to 3.1 Pro would confound base model and adaptation. [Supported tuning and controls](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/tuning/supervised-tuning)

## Proposed experiment basket and larger commitments

All hours below are **allocations for estimating spend, not predicted convergence times or equivalent amounts of work**. Exceeding a cap returns an incomplete experiment rather than silently increasing the budget.

| Item | Assumption | Estimated USD |
|---|---|---:|
| Hosted 3.1 Pro comparison | 1,000 illustrative calls above | 64.00 |
| Matched 2.5 Pro base/tuned evaluation pool | 1,000 total calls | 45.00 |
| One managed 2.5 Pro SFT candidate | 3M dataset tokens × four epochs | 300.00 |
| ByT5-XL adaptation pilot | 24 hours, a2-ultragpu-2g | 243.30 |
| Small/larger open inference comparison | 20 total VM-hours, a2-ultragpu-1g | 101.38 |
| ~72B inference probe | Five hours, a2-ultragpu-4g | 101.38 |
| Storage/boot/operations allowance | Planning allowance, not exact usage | 50.00 |
| **Total / plus 30% contingency** | Rounded only after calculation | **905.05 / 1,176.57** |

Run the basket in stages rather than all at once. The first hosted 900-call source/manual-reference/retrieval comparison would be $57.60 under the stated 3.1 Pro assumption. Use a smaller screen to retire clear failures before consuming the whole allocation. The full basket is not a factorial test of every model, data recipe and language direction, and it does not purchase expert validation.

For larger full tuning, illustrative on-demand allocations are 4–8 A100 80GB for 7–12B, 8–16 for 27–30B, and potentially 32 for 72B under conventional mixed-precision optimizer accounting. These are planning classes, not minima. A 16-GPU configuration means two 8-GPU VMs with verified distributed networking/sharding; 32 means four. Reserve only after profiling the exact model, sequence lengths, optimizer and checkpoint path.

One eight-A100 VM for 24 hours costs **$973.21**; 28 days (672 hours) costs **$27,249.86**. Eight H100s on demand for the same 28-day allocation cost **$59,465.28**. This is a rental comparison, not a claim that either produces equal work or a working Pahlavi translator. Profile throughput before comparing cost to reach a quality target.

At 730 hours/month, 1,000GiB regional Standard Cloud Storage is about $20/month and 100GiB pd-balanced boot disk about $10/month. Operations, retained versions, additional disks and network traffic add cost. Local SSD is scratch; durable checkpoints belong in the same-region bucket. [Storage pricing](https://cloud.google.com/storage/pricing), [disk pricing](https://cloud.google.com/compute/disks-image-pricing)

## The investment test: what would make the larger model worth it?

The primary outcome is the fraction of new passage-direction items whose translation is acceptable without a substantive meaning correction. Also record critical errors (negation, roles, entities, quantities), terminology, omissions, calibrated uncertainty/coverage, and expert correction minutes. Exact previously translated passages are a separate translation-memory outcome.

A concrete **proposed decision threshold**, to freeze before results, is at least a **10 percentage-point gain in first-pass acceptable translations OR a 20% reduction in expert correction time**, with no material increase in critical errors or loss of difficult-case coverage. These are investment criteria chosen for this project, not research-predicted effects. A five-point gain may still pay at high volume; the economic calculation should decide borderline cases. An abstaining system must not win just by answering fewer hard passages.

Illustrative economics, **not observed performance**: if a larger system saves two expert minutes per passage at an assumed $60/hour, it saves $2 per passage. If extra inference costs $0.20, net saving is $1.80. An additional $1,000 experiment/adaptation cost breaks even after roughly **556 passages**. Replace each assumption with measured throughput, actual reviewer rates and observed corrections. Include still-wrong or rejected passages and fixed setup costs in the accounting.

General formula: incremental value per passage = reviewer hourly rate × minutes saved / 60 − added inference cost. Break-even volume = added fixed investment / incremental value, only when the denominator is positive. Report a sensitivity range. This is an operational saving calculation, not a full commercial business case or a monetary valuation of undetected errors.

A useful routing option is small-model translation for cases it demonstrably handles, stronger-model review for difficult cases, and expert review for unresolved cases. A second option is to distill verified strong-model/expert corrections into the smaller model after proving the teacher's Pahlavi competence. Routing and distillation require their own evaluation; model confidence alone cannot certify correctness.

## Process and plan change for the main task

1. **Finish the current owned baseline.** Preserve the original run, deadlines, frozen S04 and existing eligibility gates. Evaluate the saved ByT5 result before inferring that its route failed.
2. **Prepare evidence and a new evaluation pool.** Acquire/verify source-aligned scholarship and contextual lexical senses. Do not open or reuse sealed TEST for method selection. Separate duplicate editions, reversals and related passages.
3. **Run an exploratory size-by-evidence screen when spending is authorized.** Use roughly 60 newly prepared passage-direction items to compare two sizes from one family, each source-only and with the same manually verified permitted references. Add a strong hosted comparator. Keep input representation, context, precision and scoring rubric matched; honor each model's actual template/context constraints. The four-condition size/evidence grid diagnoses whether evidence, model capacity or their interaction matters.
4. **Test retrieval and adaptation conditionally.** If manual evidence helps, compare retrieval against it. If correct evidence still yields systematic errors, test a different base or verified correction training. Compare SFT to its own base, then keep ByT5-XL and larger full tuning as eligible interventions.
5. **Confirm the selected improvement on fresh material.** Aim initially for 300 new items across multiple works/genres and novel compositions, reporting every direction separately. This is a planning sample, not a power guarantee. Estimate paired differences with intervals that preserve work/passage clustering; use screen variance and cluster counts to refine sample size before confirmation. Freeze one primary model contrast and economic criterion before this stage.
6. **Fund the winner at the appropriate scale.** Report acceptable translations, critical errors, correction time, cost per accepted passage, latency and coverage together. Increase compute when observed quality value justifies it. Redirect to data/philology when all models fail the same missing-evidence cases. Stop an unproductive recipe without declaring the entire project impossible.

Use reviewers blinded to system identity and randomized output order; double-review/adjudicate the confirmatory comparison. Human evaluation can dominate the bill: 300 items × two systems × two reviewers × 5–20 minutes is **100–400 reviewer-hours**, before source preparation and adjudication. At a purely illustrative $60/hour that is $6,000–$24,000, not a quotation. Screen first to avoid paying that for every candidate.

After a launch decision, use Linux accelerator VMs or managed SFT, a versioned same-region storage bucket, pinned model revisions and containers, durable checkpoints, explicit runtime/token caps, and a measured warm-up/profile before larger reservations. Predict completion from tokens/steps divided by measured throughput plus evaluation/checkpoint overhead; capacity waiting and expert work are separate. Alerts-only billing budgets are not hard caps; Google's spend-cap preview applies only where supported. [Budget behavior](https://docs.cloud.google.com/billing/docs/how-to/budgets)

No cloud resources, external uploads, paid calls, model downloads or training jobs were created by this research. Model availability does not imply permission to import project data or that Pahlavi adaptation is already solved.
