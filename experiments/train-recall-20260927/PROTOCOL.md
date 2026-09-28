# Seen-TRAIN recall diagnostic

27 September 2026. **Frozen scientific scope before new predictions; execution admission pending.** Classic + Critic. Root owns submission and spending; isolated agents prepare the evaluator and job specification. The prior goal turn was progress:20 provisional auxiliary labels were independently qualified. This turn added eight reviewed contrasts and identified a cheaper information gap before another training experiment.

## Question and selection

Does the qualified Gemma step-280 checkpoint preserve already learned passage meanings and the reviewed local distinctions on familiar TRAIN passages? Does recall differ between the exact training instruction and the existing PAL-REF instruction? This is a mechanism diagnostic on seen material, not generalization, decipherment accuracy, a new benchmark or evidence that auxiliary training works.

Use all20 distinct TRAIN parents of the28 independently qualified auxiliary annotations, sorted by original TRAIN ID. They cover16 works. This selection was fixed before any recall prediction and uses no DEV/TEST answer or new model output. Four positive commands share parent passages with qualified prohibitions. Two withheld contrast candidates and the earlier ambiguous directive do not add a case. Selected passages may contain other unresolved material; full original qualifications and interpretive brackets survive in local review records.

- Source-only input SHA256: `5a2b29c878b67e05bb1051fab015feae33753e7c23568ab57517af0cf84c233a`.
- Local-only reference SHA256: `7146aaa3173b2795f18fc231675453f34fd0ed50703c0386a0a5224af0d5bd06`.
- Selection and qualification identities: `selection.json`; reproduce with `scripts/prepare_train_recall.py --check`.

The existing step-312 instruction diagnostic already compared these formats on held-out DEV. Its negative result is retained. It does not answer whether the current step-280 model recalls these familiar passages. A targeted search of existing experiment reports/runners found proposed TRAIN-recall packets but no completed equivalent prediction set; do not repeat this probe if a matching completed set is subsequently located.

## Exactly two existing formats

For every parent, use `dev_diagnostic.messages(row, "training")` and `dev_diagnostic.messages(row, "evaluation")` unchanged. These are the exact translation-training instruction and the unchanged PAL-REF system/source instruction. Alternate pair order by parent index: training/evaluation, then evaluation/training. Exactly40 first attempts; no prompt search, resampling, replacements or retries.

Use the qualified step-280 adapter on its original pinned BF16 base, greedy decoding, seed42, thinking disabled, fresh unconfigured DynamicCache for every case, one beam, EOS[1,106,50],4096 output-token ceiling,1200-second per-case ceiling and the job's shorter remaining deadline. These reuse existing protocol constants. Check the longest actual prompt by prefill without an experimental generation. Save exact messages, token counts/hashes, adapter/base/protocol/source identity, output tokens, timing, cap/timeout/errors and all unattempted IDs after a failure.

Local tokenizer-only validation passed **20/20 exact matches** between the training-format prompt tokens and the original supervised TRAIN prefix. Maximum input is327 tokens across both formats; total input count5,180. No model was loaded. The shared science runtime lacked huggingface_hub; its already-installed project copy was appended only to that process's import path, with no install or persistent environment change. `token-audit.json` records exact package and tokenizer identities. Cloud rendering must independently match this saved audit before generation.

## Assessment and interpretation

Use the unchanged semantic error dimensions and accepted/meaning-error/critical-error/uncertain categories. Two independent reviewers see shuffled anonymous outputs, original source, published TRAIN witness and preserved qualifications; they do not see format, pair labels, historical scores or the other review. Allow defensible paraphrases rather than demanding verbatim reproduction. Unresolved full-passage meanings cannot be promoted to acceptance just because a short reviewed function is correct.

Report each reviewer's counts over the fixed20 TRAIN cases per format, paired changes and work breakdowns. Also record whether the already qualified local gloss/function distinctions are preserved, contradicted, omitted or unassessable, with exact output spans. These local checks explain recall; they do not replace the translation merit function or create a comparable PAL-REF score. Do not pool these20 seen passages with the40 PAL-REF cases, the15 whole DEV cases or the9 constrained DEV cases. Failure and timeout cases remain visible in the fixed schedule.

Predeclared interpretation:

- Success in both formats supports familiar-passage performance only. A small matched grammar-task pilot can then test transfer; more lexical collection is needed for broader lexical claims, not as an arbitrary universal sample-size gate.
- Success only in the exact training format supports format sensitivity on this selected set. It does not establish a better standard benchmark score or justify silently changing evaluation prompts.
- Failures in both formats leave fitting, source difficulty, supervision and pipeline issues unresolved. Verify the already bound adapter, prompt/masking and training-fit evidence before assuming new lexical labels are the only missing ingredient. Failure alone is not proof of an implementation bug.
- Mixed results should be diagnosed at the known local distinctions; no automatic epoch increase, model switch or larger sweep follows.

This adopts the independent strategy critic's recommendation (`/root/qwen_penalty`) and corrects an overly categorical reading of the earlier “twenty labels are inadequate” wording. Capability limits, class coverage and the exact question determine readiness; there is no invented minimum label count. The eight new contrasts permit a narrower grammar hypothesis even while public-source credential approval is pending. The broader matched-arm design remains a preparation framework, with actual task loss weighting and state reset still to be tested.

## Proposed execution envelope — not launch admission

One A10080 HF job, native30-minute timeout, no automatic retry, no training. Proposed compute alarm24 minutes, absolute internal deadline27 minutes, export reserve180 seconds and bounded persistence window. At the previously observed USD2.50002/hour, native compute maximum isUSD1.25001; reserveUSD0.25 for incidental costs, giving aUSD1.50 incremental envelope. Refresh provider rate, funded credit and active-job inventory immediately before launch. Existing funded credit is authorized; no recharge or purchase is authorized.

Only the20-source input file and checked code are newly transferred to the existing private HF bucket. The already uploaded qualified bundle and adapter are mounted read-only. Base weights download only onto the server. Locally retain small predictions, provenance and reviews after full SHA recovery; no model weights reach the laptop. Stop the job after provider persistence is verified and confirm terminal status. Preserve partial outputs on errors; a native timeout is the outer cost bound if monitoring fails.

At10:46:48UTC a fresh official API inventory returned14 existing jobs and zero nonterminal jobs. Both earlier comparison jobs remain CANCELED after their successful exports. No recall job has been submitted. Required before launch: final runner/specification tests, independent exact-artifact review, source commit and upload verification, token-audit binding, fresh live credit/rate/admission check and a single execution owner. Scientific scope is frozen; these operational gates are not yet claimed complete.
