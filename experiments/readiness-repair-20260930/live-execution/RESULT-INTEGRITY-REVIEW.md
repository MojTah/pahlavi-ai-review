# Independent recovered inference-integrity review

30 September2026. Reviewer `/root/astra_runtime_plan_recheck`. **PASS for technical completeness and integrity of the recovered inference evidence. No semantic-quality conclusion is made.**

Independently ran `verify_results.py` using the shared science Python, locally with no API, credential access, network or model weights. It passed and deterministically regenerated the same result summary and blinded packet/mapping. I did not read reviewer files or judge answer meanings, and did not repeat unrelated unit suites.

The provider receipt, terminal record and recovered manifest bind job `6abd2a1d404719ba376138e8` to reviewed run `7352dda33542431abb025b1443087aed`. Every recovered manifest-listed file matches its recorded size and SHA-256; the manifest itself matches the server's `ready_to_persist` log hash. Independently compared the terminal inventory with the manifest plus manifest file: exactly10 files and126,844 bytes, with matching paths/sizes. These are checks of locally recovered remote evidence; I did not independently query the provider.

All56 first attempts are present in the frozen balanced order, comprising28 complete pairs, with28 successful reference and28 successful candidate outputs. No active cell, unattempted cell, timeout, interrupted result, missing result or output-cap failure remains. Each case/arm ID, sequence, run identity, adapter identity and output-text hash checks correctly. Independently confirmed every token count is positive and at most512, and input lengths agree with the pre-generation prompt inventory. The verifier confirms proper EOS endings, no stopping-limit reason and finite generation times below90 seconds.

Both recorded GPU prefill canaries passed on the A100-SXM4-80GB, with zero experimental attempts and no generated answers. Every generated prompt's token-prefix hash agrees with the recorded rendered prefix and frozen packet token array; corrected-task audit prefixes agree where applicable. The two expected adapter identities match the reviewed receipt, and the evaluator's final loaded-adapter check reports unchanged adapters. Manifest and evaluator records both show **zero optimizer updates**; training was not launched.

Actual provider run duration is877.174 seconds, or14 minutes37.174 seconds. The56 generations total356.744743 seconds, median3.737145 seconds, maximum40.273860 seconds and2,099 output tokens. This measured short inference workload explains completion far below the120-minute ceiling; the ceiling was a safety allowance, not a promised runtime. The15-minute rounded compute estimate isUSD0.625005 at the recorded rate, not a final invoice or all-in charge. Twenty-five of28 paired texts differ; that is a text-difference count, not evidence that either answer is better.

## Exact reviewed identities

| Artifact | SHA-256 |
|---|---|
| `verify_results.py` | `bb857be894aa68b09b32335a3d3caf95350503fdcd9fed491453a7da43ef9665` |
| `result-integrity.json` | `30bdfe97854ef000b2e7e5345f3ebc676893b7868908f904d298e3788475641a` |
| `terminal.json` | `c35ef3e3b87a2fbbb69706676a590647139cf449a41ebfb11c8fa27b4ab3c370` |
| recovered manifest | `a55fe3b25aea56e3655822883af6a923e0ea63fd9e88afa74d81f153db243c92` |
| recovered predictions | `f719d7e408d3db94afa2fb99cc77158aa732cd116e0970ae79229c91cfa24816` |
| recovered evaluator state | `402b6043e318b9674f57bd21ac0f36bb5b5c7ea7fe1d2cdf511c2f191086f536` |

The separate [training-health review](TRAINING-HEALTH-REVIEW.md) establishes saved evidence of the earlier corrected96 adapter training:96 completed optimizer steps and1,536 slots. This report verifies the later inference-only comparison; it does not reclassify it as training. Technical success means the intended answers were generated and recovered, not that they are linguistically correct or that acquisition/generalization improved. Blinded semantic reviews, source qualifications, NF4-training versus BF16-evaluation limits and the unchanged scientific decision criteria remain separate.
