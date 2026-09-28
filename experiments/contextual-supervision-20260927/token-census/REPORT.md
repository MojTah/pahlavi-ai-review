# Provisional contextual pilot tokenizer census

TOKENIZER_CENSUS_ONLY_PROVISIONAL_NOT_LAUNCH_ADMITTED

No model, network, cloud, package installation, held-out reference or model-output access. Source qualification is recorded separately in qualification-decision-v2.json (fingerprinted in result.json); this census remains not launch-admitted.

48 updates per arm, microbatch 1, accumulation 16: 720 distinct ordinary TRAIN parents, then one designated parent in slot 16 of each update. Candidate and control share the same four fixed balanced cycle orders; designated candidate targets use the exact contextual proposals, controls use complete frozen translations.

Cycle orders use zero-based original packet indices: [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0], [6, 7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5], [5, 4, 3, 2, 1, 0, 11, 10, 9, 8, 7, 6]]. Every anchor has mean within-cycle position 5.5 across the four cycles. This balances position; it does not establish perfect learning-rate-dose equality because warmup is unchanged. Regular IDs and their order are unchanged.

All 732 ordinary parent token/label reconstructions match saved TRAIN exactly. All 12 candidate answer boundaries, exact answer-plus-terminator decodes and <=2048 checks pass. Focus uniqueness: True.

Regular works: 54; anchor works: 9; family counts: {'affliction': 3, 'equal_temporal_spatial_contrast': 4, 'theft': 5}.

| Arm | Total prompt tokens | Total target tokens | Total supervised tokens | Total sequence tokens | Maximum sequence |
|---|---:|---:|---:|---:|---:|
| candidate | 80329 | 26829 | 28365 | 108694 | 660 |
| control | 79965 | 28549 | 30085 | 110050 | 660 |

Target counts exclude the two terminator tokens; supervised counts include them. Prompt labels are -100; the first answer label is at prompt_tokens, predicted by the previous token's logit. No truncation or padding is introduced.

| Parent | Family | Candidate prompt / target / supervised / total | Control prompt / target / supervised / total | Unique focus |
|---|---|---|---|---|
| parsig:107000001 | affliction | 76 / 4 / 6 / 82 | 68 / 10 / 12 / 80 | True |
| parsig:108000001 | equal_temporal_spatial_contrast | 74 / 5 / 7 / 81 | 68 / 7 / 9 / 77 | True |
| parsig:109000005 | theft | 88 / 3 / 5 / 93 | 80 / 32 / 34 / 114 | True |
| parsig:151026026 | affliction | 79 / 4 / 6 / 85 | 73 / 15 / 17 / 90 | True |
| parsig:518000014 | affliction | 94 / 2 / 4 / 98 | 89 / 20 / 22 / 111 | True |
| parsig:151001046 | theft | 70 / 2 / 4 / 74 | 64 / 8 / 10 / 74 | True |
| parsig:151045004 | theft | 131 / 3 / 5 / 136 | 123 / 45 / 47 / 170 | True |
| parsig:509000008 | theft | 211 / 3 / 5 / 216 | 205 / 111 / 113 / 318 | True |
| parsig:513000002 | theft | 227 / 2 / 4 / 231 | 222 / 109 / 111 / 333 | True |
| parsig:151001162 | equal_temporal_spatial_contrast | 94 / 4 / 6 / 100 | 81 / 20 / 22 / 103 | True |
| parsig:136005007 | equal_temporal_spatial_contrast | 128 / 5 / 7 / 135 | 116 / 37 / 39 / 155 | True |
| parsig:137001027 | equal_temporal_spatial_contrast | 150 / 2 / 4 / 154 | 142 / 55 / 57 / 199 | True |

Expected weighting: Gemma4ForConditionalGeneration accepts_loss_kwargs=False; native Trainer uses each microbatch's mean answer-token loss, divided by 16. Each example nominally weighs 1/16, including answer terminator. This is source inspection, not executed training or gradient evidence; verify the eventual PEFT wrapper retains the flag and no custom reduction overrides it.

Consequently short contextual answers receive the same example-level weight as long translations; each answer token has weight 1/(16*N). Equal token mass across arms is not implied. Result JSON records each update's token denominators and the different weights that a token-normalized implementation would produce.

Duplicate screening (report-only; full 66-pair values are in result.json):
- CONTEXT1-109000005 / CONTEXT1-151001046, proposed_target: exact=False, normalized similarity=0.800000.

Reproduce from the project root:

```powershell
& 'C:/Users/mojta/.venvs/codex-science/Scripts/python.exe' -B resources/local/contextual-token-census/census.py
```

Script SHA-256: `83a53d66d38bef6a5ceb3d826de010c3088d3b50049536d7b8d2c424dd2969fa`
Result SHA-256: `406843264d8c9f9ddef7cfc5d8f40354b7c7d1845165a541dde8ae6d5d2981e7`

Actual loaded package paths/versions, pinned input hashes, all 720 regular IDs, 48 update orders, exact source focus spans in code points and UTF-8 bytes, answer boundaries and token-array hashes are in result.json.

Runner preparation files (still not launch admission): `auxiliary-tokenized.jsonl` has 12 masked tokenized auxiliary rows; `regular-id-order.jsonl` has 720 frozen ordinary IDs; `ordered-slots.jsonl` has 768 ordered parent slots with candidate/control row IDs. Ordinary and control tokens come unchanged from pinned TRAIN. Hashes are recorded in result.json.
