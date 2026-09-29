# NLLB compatibility preparation and accepted review corrections

28 September 2026. Classic + Critic: root owns the small implementation and decision record; an independent read-only reviewer checks source-language adaptation and the final evidence. This is local compatibility preparation, not paid training admission.

## Scope and checks

Use the unchanged 2,237 qualified Pahlavi–Persian TRAIN pairs and 24 DEV sources. Preserve all cases; do not read held-out targets, change translations, drop long examples, or strip diacritics/uncertainty. Acquire only five passive public tokenizer/configuration JSON files at fixed revision `7be3e24664b38ce1cac29b8aeed6911aa0cf0576`; no pretrained weights, credentials, cloud jobs, package installation, or billing actions. Ordinary bounded local work: target ten minutes for first census, warning at five minutes without progress, no automatic retry or paid fallback.

`check_tokenizer.py --fetch` performs anonymous acquisition followed by an offline census. Without `--fetch`, it verifies recorded hashes and runs offline. The existing science Python and project dependency fallback are reused. The census records separate source/target lengths, unknown spans, exact and NFKC/whitespace round trips, and uncertainty-marker counts. NFKC/whitespace equivalence is a diagnostic, not permission to change the corpus. Non-equivalent changes require inspection.

Append `pal_Latn` through public tokenizer APIs and preserve all existing language tokens and IDs; Persian remains `pes_Arab`. A tokenizer save/reload check does not prove model embedding, learning, GPU memory, timing, or translation quality. The initial model embedding will need a declared initialization and actual trainability check. If initialized from the mean of original language-tag embeddings, describe that exactly; do not call it linguistically neutral or empirically optimal. The baseline is **pre-fine-tuning NLLB with declared source-tag initialization**, not literally untouched stock NLLB.

## External report decisions

The supplied `pahlavi-ai-review-report.md` motivates making compatibility the first execution step and keeping task/token weighting explicit. It does not justify immediately retraining the contextual recipe or changing the model priority.

- The [official model card](https://huggingface.co/facebook/nllb-200-distilled-1.3B) describes training inputs up to 512 tokens and warns about longer-text quality. This is not a hard 512-token architecture limit. The [pinned configuration](https://huggingface.co/facebook/nllb-200-distilled-1.3B/blob/7be3e24664b38ce1cac29b8aeed6911aa0cf0576/config.json) records 1,024 positions; neither number establishes a safe quality range. Source and target sequences are separate. The default 200-token generation limit also needs an explicit override before evaluation.
- The contextual per-example loss was disclosed in [PILOT.md](../contextual-supervision-20260927/PILOT.md), including 6.25% nominal designated-example weight, short targets and different token totals. Equal scalar weights do not imply equal gradient norms; a possible 20-fold coefficient ratio is not measured causal influence.
- Its proposed miniature comparison already exists in [numerical-check/result.json](../contextual-supervision-20260927/numerical-check/result.json). The native implementation matched manual per-example gradients and one AdamW update; pooled-token gradients differed. This tiny random CPU result establishes arithmetic, not production translation superiority. Do not repeat it merely to rediscover the difference.
- A token-normalized alternative must normalize over the full accumulated update, not each microbatch of one, which would reproduce the existing mean. Such an alternative changes the task dose and is a prospective experiment, not a proven repair.
- Teacher-forced improvement with weak free translation does not diagnose exposure bias. Keep source-contrastive decoding conditional, with its setup/inference cost and full unchanged acceptance screen.
- Evidence-integrity checks and separate AI reviewers do not establish expert semantic validity or statistical independence. Preserve specialist calibration and repeated-DEV limitations. The reported 5/24 and 6/24 reviewer disagreements include judgment, severity or uncertainty handling; they are not exclusively critical-error disagreements.

## Decision and remaining gates

Keep one NLLB-1.3B supervised challenger against retained qualified Gemma. No new training-data campaign or model ladder. First establish tokenizer compatibility and source-tag plumbing. Next freeze the actual training schedule, loss/masking, initialization, save/reload, output policy and full lifecycle cost. The proposed USD 3 allocation remains conditional on measured feasibility and a fresh provider observation, not a guaranteed quote. Keep the fixed 15-whole/9-constrained merit and fresh paired review of all three 24-case conditions.

The paper's [public Kalamang implementation](https://github.com/Sethjsa/XLR-MTOB) supports investigating tag extension, but contains demonstration/commented sections and inconsistent configurations. It is not a ready-to-copy verified launch recipe. The [versioned tokenizer implementation](https://github.com/huggingface/transformers/blob/v5.13.1/src/transformers/models/nllb/tokenization_nllb.py) and actual local checks control this preparation.

## Executed results

All 2,237 TRAIN sources, all 2,237 Persian targets and all 24 frozen DEV sources were checked. Their maximum serialized lengths are respectively **407, 341 and 269 tokens**. No row exceeds 512 tokens, and none was excluded or truncated. TRAIN remains SHA256 `15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc`; DEV sources remain `06ac58310bf67767fae4124d8e935c808d15debcd8daebce07b583937cd97182`.

The stock tokenizer had 325 unknown source tokens in 258 TRAIN rows, 233 unknown target tokens in 93 rows, and one unknown DEV source token. The missing characters were `ǰ`, curly quotes/apostrophe, guillemets, and en/em dashes. A naive ordinary AddedToken extension introduced spaces within words (`ǰadag` became `ǰ adag`) in a directly executed check. The prepared tokenizer instead appends the eight TRAIN-observed missing characters to the existing BPE alphabet while preserving every original vocabulary ID, merge and normalizer. Selection uses TRAIN only; no DEV target or reviewer correction was read. The comparison now tests this explicit adapted tokenizer as part of the attainable NLLB system, not stock tokenizer competence or an isolated architecture effect.

After extension, **all 4,498 checked text fields have zero unknown tokens and no uncertainty-marker change after canonical Unicode normalization**. Length maxima remain unchanged. Byte-exact round trips are not claimed: the unchanged stock normalizer performs Unicode/whitespace normalization and maps zero-width non-joiner and left-to-right mark to spacing. Only one TRAIN source needs that additional format-spacing equivalence; 1,059 targets do. All 24 DEV sources round-trip under NFKC/whitespace alone. Original data files remain untouched, and all differences are accounted for in [result.json](result.json).

The stock tokenizer has 256,204 entries while the configured model has 256,206 rows. Two named reserved tokens retain the unrepresented original rows. Eight new character rows and the `pal_Latn` row extend the final vocabulary to **256,215**, without shrinking or overwriting original model rows. All original token IDs/special tags and source/target serialization survived tokenizer save/reload. The intended model initialization is the mean of original non-special rows for added characters and the mean of 202 original language-tag rows for the new source tag. This is an explicit engineering choice, not a claim of optimal linguistic initialization. Reserved rows must be suppressed in generation consistently for both NLLB conditions.

[check_model_plumbing.py](check_model_plumbing.py) additionally passed a local **random tiny CPU M2M100** canary with the real vocabulary dimensions: original rows preserved before training, input/encoder/decoder/output embedding sharing, padding-only label masking, finite loss, a nonzero new-source-row gradient, forced Persian output tag, and identical deterministic generation after save/reload. The gradient also contains tied output-head effects and does not isolate source conditioning. This check used synthetic token pairs and one update; it establishes plumbing, not translation quality, real 1.3B GPU memory or throughput. [Evidence](model-check.json).

Only 17,336,285 bytes of five public passive assets were fetched. Local adaptation and the random tiny model generated additional local test files; no pretrained model weights were downloaded. [Original asset receipt](asset-receipt.json), [prepared tokenizer manifest](prepared-tokenizer-manifest.json).

An initial local assertion caught the old bundle's six-item smoke-test file before any result was admitted; the census was corrected to the existing pinned 24-case DEV input. A second local assertion was corrected because the special-token API counts existing tokens newly marked special as well as genuinely new vocabulary entries. The final checks use actual vocabulary size and full ID preservation. These were local preparation repairs, not paid attempts or translation outcomes.

The earlier independent reviewer identified the vocabulary-size/shrink risk and the fact that `<unk>` itself contaminates raw angle-bracket marker counts; both were addressed. Its final post-fix review was interrupted by a Codex usage-limit response. A distinct final critic has now checked the implementation and hash-bound artifacts and gives **PASS for local preparation only**, with a manifest lifecycle note. [Independent verification and exact scope](REVIEW.md). Paid admission still requires an executable full lifecycle, real pretrained GPU canary, frozen training schedule and fresh cost/balance verification. No paid job is admitted by this document.

The [fine-tuning knowledge base](../../kb/model-finetuning/README.md) records the model-specific method choices and remaining work. A census rerun changes timestamped `result.json`; the commands below do not refresh the dependent prepared-tokenizer manifest. Refresh those bindings or reject them as stale before packaging/upload. The current saved bindings match.

Reproduce offline with the existing science Python:

```powershell
& '[USER_HOME]/.venvs/codex-science/Scripts/python.exe' -B experiments/nllb-feasibility-20260928/check_tokenizer.py
& '[USER_HOME]/.venvs/codex-science/Scripts/python.exe' -B experiments/nllb-feasibility-20260928/check_model_plumbing.py
```
