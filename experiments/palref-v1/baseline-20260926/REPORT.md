# Original-model PAL-REF baseline

The original Gemma 4 31B instruction model completed all forty Pahlavi-to-Persian cases, but the provisional blind AI review accepted only **5/40 (12.5%)**. This is a descriptive result on the fixed published-reference sample, not a population accuracy estimate or a specialist-certified judgment.

| Judgment | Cases | Fraction |
| --- | ---: | ---: |
| Accepted | 5 | 12.5% |
| Meaning error | 20 | 50% |
| Critical error | 14 | 35% |
| Uncertain | 1 | 2.5% |
| Abstention / timeout / execution error | 0 | 0% |

Complete-output coverage is **40/40**, separately from correctness. Per-work accepted counts are 1/8, 0/4, 0/10, 3/10 and 1/8 for work IDs 104, 110, 116, 130 and 132 respectively. Full counts, output-bound reviews and provenance are in `score.json`, `reviews.jsonl` and `run.json`.

For example, case 001 changes the reference's wealth into social standing; case 003 loses the contrast between a wise person understanding at the beginning and an ignorant person understanding at the end. Case 025 remains uncertain because the output's “imperishable” may not preserve “ageless.” These case explanations are review evidence, not instructions for tuning the next candidate.

## Reproduction and scope

- Model: `google/gemma-4-31B-it`, revision `842da3794eaa0b77d5f08bae87a17459d91ff475`, original BF16 weights, no adapter.
- Benchmark: unchanged PAL-REF v1, manifest `a3932f7510f101376cc91c47bb23f3c9872656c41f563701fa3dcb2b6c89a5e8`. Only its forty `pal>fa` cases were evaluated; the other 120 directional cases were not run.
- Condition: exact frozen source-only messages; official model template, thinking disabled; fresh cache per case; greedy decoding, seed 42, 4096-token and 1200-second per-case ceilings. No reference or retrieval context was supplied to inference.
- Generation: 170.819 seconds total. Submitted-to-confirmed-terminal time: 640 seconds, including setup, transfer, verification and shutdown. This is cloud A100 performance, not measured laptop speed.
- Reviewer: `/root/blind_palref_review_a`, fresh context restricted to source text, both published references, existing meaning checks, exact predictions and rubric. Model identity and prior scores were withheld. AI-only single-review assessment remains provisional; `expert_adjudicated=false`.
- Reproduce aggregation from the project root: `resources/local/hf-client-venv/Scripts/python.exe -X utf8 cloud_pilot/score_palref_fa.py experiments/palref-v1/baseline-20260926`. The wrapper verifies the complete frozen benchmark, selects the forty cases and invokes its unchanged scorer. No benchmark bytes, definitions or denominators were edited.
- Job `6ab854576b030d633f696f93`, inference source commit `9de0b9dc91533049b22d35f9ca8c3355a442e002`. Controller confirmed all remote files before deliberately canceling the idle job; all six exported files subsequently downloaded with matching full SHA256. Provider CANCELED means deliberate post-computation shutdown in this case.
- Original immutable remote prefix: `baselines/29f80b545dad40cd9b1422275692597d`. Local recovery evidence: `resources/local/hf-baseline-downloaded-20260926/recovery-verification.json`. The copied review run adds reviewer metadata; original remote inference provenance is retained unchanged.

The training recipe and data were fixed before this benchmark exposure. Preserve every first attempt and compare the final trained model under the same conditions. Do not tune prompts, select checkpoints or alter training examples using these forty results. Local 8 GB inference and quantization parity remain untested.
