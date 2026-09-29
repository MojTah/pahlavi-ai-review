# NLLB compatibility review checkpoint

28 September 2026. Final independent review now passes **local preparation only**, with one lifecycle note. This is not release or paid admission.

Lead agent/request id: /root
Critic agent/request id: /root/nllb_final_preflight_review
Critic model and reasoning effort: inherited session settings, no override
Independent from lead: yes
Critic verdict: pass with notes
Evidence reviewed: Final check_tokenizer.py, check_model_plumbing.py, result.json, model-check.json, passive assets, prepared tokenizer, receipts/manifests and actual TRAIN/DEV source files. See SHA256 bindings below.
Verification evidence: Distinct critic performed stdlib-only independent checks of all 2,261 row identities and 4,498 text hashes, all eight TRAIN-only added-character counts, every original token ID, all 514,098 BPE merge pairs/order, unchanged normalizer, reserved/model rows, final append IDs and receipt hashes. Critic reviewed CPU-canary code and hash-bound saved execution evidence; it did not rerun the model or tokenizer census.

The earlier critic `/root/nllb_source_method` confirmed that append-only source-tag adaptation is supported, while requiring honest initialized-baseline labeling and preservation of original IDs. It found that 256,205 tokenizer entries would incorrectly shrink a 256,206-row model under a naive resize. Root retained both unrepresented model rows and appended the eight TRAIN-observed character rows and distinct source tag beyond them. Final vocabulary size is 256,215. It also identified unknown-token contamination of raw marker counts; root corrected that check.

The earlier critic's final message was a provider usage-limit failure, leaving the previous checkpoint partial. The distinct final critic completed the checks above on 28 September. This new evidence supersedes that incomplete status; the earlier strategy review is not being reused as implementation approval.

The final critic verified zero unknowns and preserved canonical uncertainty markers across the recorded census, length maxima 407/341/269, and accounted-for format-spacing normalization affecting one TRAIN source and 1,059 targets. This does not establish byte-exact preservation or linguistic correctness. Reviewed canary evidence covers original-row preservation, tied weights, padding-only masks, finite loss/nonzero source-row gradient, Persian output forcing and save/reload equivalence. The tied output-head contribution prevents interpreting that gradient as isolated source conditioning.

**Non-blocking preparation note:** rerunning `check_tokenizer.py` rewrites timestamped `result.json`; neither documented command regenerates `prepared-tokenizer-manifest.json`. Current saved bindings match. The future executable package must refresh the dependency chain or reject stale bindings before upload. This remains a lifecycle-readiness item.

## Exact evidence reviewed

| File | SHA256 |
|---|---|
| `check_tokenizer.py` | `3f66dcf6ee0a9542000d6b757320ab09f208648e45297bfc787ec3fb0487ad3c` |
| `check_model_plumbing.py` | `024cd2ec3d6ed75f95c2ced778f76080ba1339d47808e7b700c903b5f9a8faf5` |
| `result.json` | `cb82776256b9822214658566b8ffa7dd558e337c58aba5dc1fea8e993eaf7416` |
| `model-check.json` | `5a2c45f0192daa3258c6be6c85acdc8968c38b30ede2884e081f2aa187c5bbfc` |
| `asset-receipt.json` | `7673e245f82ce0dd9540d537c4b359bf898eb02782770987a4ecaaa4ab35ca3c` |
| `prepared-tokenizer-manifest.json` | `7c2d57816f4806bc78b354b33fd57dde55656e69487e8a3b6567178e392bbf89` |

The pre-status-update README and REVIEW hashes were respectively `224396f5ad87a12e3e3225f14db65e0c1a6ecf2f8784b05de92bf0038fa7cf04` and `72f5f8cc0c34b789ea6d3ea4f1c00a6c82257cbaabf67a1f880c691b89781eed`. Only documentation changed to record the completed review. The final critic made no edits, network calls, model imports, credential access or downloads.

Local checks are reproducible from the two checked-in entrypoints and pinned passive assets, subject to the manifest refresh caveat. Paid launch, pretrained 1.3B initialization/update behavior, new-row/source-conditioning learning, translation improvement, GPU memory/throughput, training schedule, full lifecycle recovery/shutdown and fresh cost/balance remain unverified. No launch occurred, and no public upload or external message was sent.
