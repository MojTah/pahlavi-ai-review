# Independent mixed-pilot launch review

2026-09-29. Reviewer `/root/mixed_launch_review`; root is the sole launch owner.

**PASS for the reviewed local launch artifact and bounded design.** No remaining local blocker. This is not a GPU execution, cloud persistence, translation-quality, or provider-invoice guarantee. The root must complete its live admission and exact submission checks.

## Executed evidence

- `prepare.py --check`, using the shared science Python with `-B -X utf8`, exited 0 and replayed every frozen payload byte exactly. The full census has 10,152 typed records, 10,151 after one exact task/source/target/complete-context duplicate; no exclusions or truncation. These are not 10,151 independent translation pairs.
- A separate in-memory audit checked every pool row's contiguous answer-only labels, attention mask, length and terminator; all 2,237 historical arrays match the original qualified rows. Every new decoded answer and complete source/context matches its released learning object. CPD sense structures remain intact. Both known homographic grammar pairs retain their different contexts and targets.
- The pilot has 1,536 unique IDs in the frozen order: 1,152 historical, 96 Persian lexical, 64 CPD, 32 MMP, 127 grammar, 57 documentary, four Kanheri pair types and four S23 spans. Every update has 12 historical, two lexical and two other slots. Totals independently match 258,988 sequence tokens, 67,456 supervised tokens and maximum length 1,144.
- Independently ran `python -B -X utf8 -m unittest cloud_pilot.test_mixed -v`: **7 tests passed**, exit 0. This exercises tiny random Gemma/LoRA optimization against a manual equal-example loss calculation, exact order, nonfinite gradients, canary denial with adapter preservation, expired deadlines, exact generated transport, and mocked 24-output generation with first-error termination. Additional independent read-only checks rejected malformed masks, extra answer fields, and invalid clocks; fit/nonfit forecasts behaved correctly.

## Boundaries and fixes

Two review findings were corrected and retested: the candidate evaluator now checks the singleton candidate adapter rather than a nonexistent `mixed_train.ARMS`; the step-20 gate verifies and records an actual adapter digest change before admitting continuation.

Static tracing confirms pinned qualified step-280/base/tokenizer checks, fresh optimizer and RNG, fixed 96 updates, preserved LoRA/NF4/BF16 recipe, answer-only training, and unchanged source-only plain DEV24 prompt identities. Training preparation reads qualified learning fields; no benchmark answers are supplied to the job. This does not independently re-certify all source scholarship or prove absence of every semantic overlap.

The unchanged merit screen remains two reviewers, 15 whole/9 constrained, net accepted gain at least two across at least two works for both reviewers, with the existing critical-error and uncertainty restrictions. Incomplete output cannot pass. No automatic promotion or further experiment is authorized by this review.

Final limits are **100 minutes native / 95 internal / 85 computation**, with 600 seconds reserved for export. The measured 20-update forecast remains fail-closed. At the recorded rate, compute plus USD0.50 reserve is USD4.66670, leaving USD1.60330 below the observed USD25 cap; the earlier provisional 80-minute observation is superseded by PLAN's pre-launch correction. Root owns freshness of billing, idle-job and storage observations. Export retains intermediate/final adapters and incomplete evidence, with remote inventory truthfully unverified until separately checked. No GPU/NF4 training or remote persistence was exercised by this critic.

## Reviewed SHA256 identities

| Artifact | SHA256 |
|---|---|
| `train.jsonl` | `c32a7f21639c34107fd4a86c1c8dae3a8815b40c8107ff8c3075e0167535dc4a` |
| `data-manifest.json` | `ebda721f77db1c60377d75cd3e9d578aebeb749a244c386d2ac96e896427b6fe` |
| `prepare.py` | `2aacc66128669e26b34db22c3f12139558ae88207a435cc43f1d6c2c61365ca2` |
| `mixed_train.py` | `b81dd8dcd873f5e6134780def3541b7e1c9ce5e813041e5da224b78ac161adf4` |
| `mixed_run.py` | `514ad71cb634bbc3c24b13562a61815be823f02e0191a104200c8b965ff1cd72` |
| `hf_mixed.py` | `4fec5d53e300da55be2b297002e9ffe67397f335a2d30c7bca32c905b0eee23a` |
| `test_mixed.py` | `7df9cde6b4589ebd6c095cd4017a672ae021feb876151aa681a82703fbbb4ea8` |
| `PLAN.md` | `e1f52c76c957dbc181f874e1b642d7b5e69b731bfbc4aa7a04cc7785efb45da6` |
| `admission-observation.json` | `80dcedffff892d66f53bc49b08f60207333a2c9907e39517346819eb222824d8` |

The critic changed only this report and, after specific root authorization, generated the existing test suite's scratch artifacts. No cloud, authentication, network, frozen-data or implementation mutation was performed.
