# Automatic dictionary A/B runtime

3 October 2026. Local implementation only. The next question is whether automatic access to complete published dictionary meanings helps the **same retained model** translate these 15 familiar DEV passages. There is no new model, translation result, training or paid job in this checkpoint.

## What changed

The maintained component runner now admits one closed `dictionary-ab-v1` protocol. Its 30 inputs retain the original system and user messages, exact source/work bindings and token/text hashes. A has no dictionary evidence; B has all exact-form alternatives. All other instructions are identical. Execution alternates AB/BA across the 15 cases, with one first attempt per arm/case and a fresh cache. No cached plain A output may substitute for the new A prompt.

Retained step280 uses the same BF16 base and FP32 LoRA adapter, greedy decoding, seed42 and disabled thinking in both arms. No optimizer exists in this experiment. Model loading checks reject quantization, wrong floating-point types and CPU parameters before the canary; pre/post adapter verification remains required. These local mocked guards do not establish real GPU correctness.

The new protocol accepts at most8192 input tokens and4096 new output tokens within12288 tokens. Actual cached tokenizer replay covers all30 prompts, including the longest, `QUALITYDEV1-006:B`, at5135 input tokens. Inputs are never shortened. The earlier 9/12-output protocols retain their literal prompts, schedules and limits.

## Explicit new timing proposal

The reviewed `ab-contract.json` and its1200-second attempt limit remain unchanged, hash`71d386912ac9325891bc5121efd51c6ef79dda399c0e7f4dc3f6380675aec21d`. This implementation adds a separately named **`dictionary-ab-90s-v1`** prospective contract. It changes censoring relative to that specimen; it must not be described as an identical rerun.

Each attempt has a90-second cooperative stopping criterion and the unchanged4096-token cap. Existing retained DEV15 output maxima were about23–24seconds, and the earlier own-analysis run produced248 tokens in about39seconds. These observations motivate90seconds for a bounded trial. They do not prove that the new longer prompts or4096 generated tokens fit. A blocked CUDA call can exceed the cooperative limit; child, computation and native deadlines provide the outer stop boundaries. No speed or memory guarantee is claimed.

After the longest-input prefill canary, the runner requires3420 seconds:30×90 generation,30×20 snapshot allowance and120 tail allowance. Each start/done snapshot receives10seconds. It rechecks the remaining full denominator before each slot and reserves future slots/tail before generation. A late startup cannot quietly begin a partial trial.

The one-job **proposal**, not permission, has a120-minute native limit. Computation stops at6600seconds; the child is bounded within that window with180seconds reserved for parent checks. Final export has up to360seconds, persistence60seconds, and180seconds remain before the native cutoff:6600+360+60+180=7200. Initial transfer/loading is inside the computation envelope;1800seconds is a planning estimate, not an extra allowance. Final publication failure still disarms the local alarm before the process exits. No automatic retry is configured.

Official documentation checked3October lists A10080GB atUSD2.50/hour and per-minute billing during Starting/Running. At the previously observed rounded minute rate,120minutes isUSD5.00004; propose **USD5.01 compute allowance**, pending a fresh rate/funding check and exact authorization. Storage, tax and existing cumulative spending are separate, unverified here. [HF pricing and billing](https://huggingface.co/docs/hub/en/jobs-pricing). HF supports custom timeouts and runs jobs once by default. The installed pinnedSDK1.23.0 lacks an `attempts` parameter; it is preserved, using the documented default rather than installing a new client. [HF configuration](https://huggingface.co/docs/hub/en/jobs-configuration#timeout).

## Evidence and recovery

Before dispatch, every slot has a durable start journal and incremental snapshot. Every returned result is flushed and fsynced before its done snapshot. Raw outputs include complete messages, actual input hashes/counts, output token IDs/text/hash, work/source, dispatch flag and stop/cap reason. Interrupted, unattempted and committed slots remain distinct; none is replaced. A partial JSONL tail is preserved and rejected, not repaired into invented evidence.

Reconciliation requires the exact30-slot schedule, historical specimen and new controls, the byte-identical source-only input file, dispatch accounting and per-output message/source/work/token identities. Empty, non-EOS, capped or timed-out outputs cannot masquerade as successful translations. A legitimate EOS-ended abstention is technically valid but still receives semantic review. All30 valid recovered first attempts and both complete blind reviews are required before the semantic gate. Failed A followed by successful B never counts as a semantic improvement.

Incremental and final publication use immutable files, manifest hashes and mounted readback. Final evidence is limited to16MiB. Mounted readback is **not independent remote durability**: provider inventory plus download/readback of every small final artifact and its manifest remain required after the job. Models/adapters stay on the server/private bucket; no weights are downloaded to this computer.

## Review and remaining gates

Main passed15 runner tests in56.578seconds and5 wrapper tests, plus the existing components12/stages12/own-analysis9 protocols with their real cached tokenizer/SDK and failure scenarios. The reused subprocess primitive's real Windows child timeout/interruption test kills and reaps exactly one child in each scenario. Engineering critic independently passed the same20tests and four extra CPU cases (EOS abstention,4096tokens ending with EOS, bad prefix and global deadline). Its evidence and bounds are in `critic-result.json` and `autocode-critic.txt`. Python's private Temp ACL initially prevented local test access; normal inherited workspace ACLs fixed the fixture without changing runtime behavior. Test journals remain ignored scratch. No expert, GPU or provider behavior was inferred from these tests.

The engineering critic and Astra review records are stored with this checkpoint when returned. Local CPU mocks and SDK roundtrip prove only the exercised local interfaces and failure behavior. The science question, frozen exposed DEV15 references, same uniform merit, per-rater reporting and cross-work continuation rule are unchanged. This cannot establish unseen-language generalization, specialist validation or promotion.

Before launch: complete independent review of these exact artifacts, refresh funding/rate/cumulative-budget and idle-job inventory, verify the private input transfer and fresh output prefix, bind the maintained one-shot admission/claim to the preview, obtain exact one-job permission, and run the real longest-prompt GPU canary within that job. The canary generates no experimental answer and cannot guarantee a full4096-token decode fits; any subsequent OOM/timeout makes the primary test inconclusive. Training remains held.
