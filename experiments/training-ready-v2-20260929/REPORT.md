# Corrected-data continuation: small gain, improvement screen fails

30 September 2026. **The corrected run improves one complete translation over the previous mixed run, but does not qualify to replace retained step280.** Both fresh blinded reviewers accept2/15 whole translations from corrected-v2, versus1/15 from step280 and1/15 from the previous mixed96. Both comparisons to corrected-v2 fail the unchanged improvement screen. Preserve this candidate for diagnosis; retain step280 and stop this recipe without automatically adding epochs or launching another run.

## Matched comparison

Each reviewer independently assessed72 shuffled, opaque records: the same24 cases from three checkpoints. Model identities and historical scores were withheld. Both rating files were frozen before aggregation. The15 provisional whole translations and9 constrained cases remain separate; reviewers are not pooled. All72 model outputs are successful first attempts, with no caps, replacements or reduced denominators.

| Reviewer | Checkpoint | Accepted /15 | Meaning error /15 | Critical error /15 | Uncertain /15 | Constrained critical /9 | Constrained overconfidence /9 |
|---|---|---:|---:|---:|---:|---:|---:|
| A | Retained step280 | 1 | 10 | 4 | 0 | 4 | 7 |
| A | Previous mixed96 | 1 | 7 | 7 | 0 | 5 | 5 |
| A | Corrected-v2 mixed96 | 2 | 9 | 4 | 0 | 4 | 7 |
| B | Retained step280 | 1 | 10 | 4 | 0 | 4 | 8 |
| B | Previous mixed96 | 1 | 8 | 6 | 0 | 5 | 6 |
| B | Corrected-v2 mixed96 | 2 | 8 | 5 | 0 | 3 | 8 |

Relative to step280, both reviewers find one newly accepted case009 and no lost acceptance. The net gain is1, below the required2; it occurs in only one work, below the required two works. ReviewerA finds unchanged whole critical errors; reviewerB finds an increase from4 to5. Both find case002 worsened from meaning error to critical error. A also finds a compensating critical-to-meaning change in case017; B does not. A stable total therefore does not mean every passage stayed equally safe.

Relative to previous mixed96, both reviewers find restored acceptance of case003 and no lost acceptance. Whole critical errors fall7→4 for A and6→5 for B; constrained critical errors fall5→4 and5→3. Nevertheless, acceptance gains still fall short and cover only one work. Both reviewers flag newly unsupported certainty in constrained cases001 and022. These are improvements on some dimensions, not a passing overall result.

## Concrete changes

Case003: the previous mixed run said «بهمن روز چهارم جامۀ نو بپوشد.» The corrected run says «روز بهمن جامۀ نو بپوش.» Both reviewers accept the corrected instruction and reject the previous unsupported addition «چهارم». Retained step280 already handled this case correctly.

Case009: corrected-v2 retains the previous mixed run's accepted reading «درازای رود», where step280 said «درنای رود». Thus the new candidate combines this lexical success with recovery of case003. That accounts for the two accepted whole translations; it is not broad passage-level competence.

Twenty-one of24 output texts changed versus previous mixed96; three are identical. One corrected output is identical to step280. Identical packet content has consistent ratings within each reviewer. The small number of accepted passages is not the fraction of words translated correctly.

## What was executed and what this comparison can establish

Both mixed candidates start independently from qualified step280 and receive96 new updates on1,536 selected examples, with the same optimizer settings, seed,12:2:2 equal-example mixture and fixed source-only evaluation prompts/decoding. Corrected-v2 does not continue from the previous mixed96 adapter. Runtime source hashes are recorded separately; reader admission/recovery fixes mean not every launcher/reader source byte is identical across runs.

The corrected pool has9,973 unique inputs representing10,145 original records. This pilot still consumes only1,536 examples. Input/target token arrays change at214 selected positions: all192 lexical positions,18 historical positions and4 documentary-to-pedagogy replacements. Eleven selected IDs change, comprising four canonical remaps and seven replacements;203 positions change arrays without changing their ID. Sequence tokens rise258,988→274,703 and supervised tokens67,456→68,724. This measures the combined correction package, not the isolated causal effect of dictionary cleanup, one source, or full-pool training.

The cloud job completed in47minutes34seconds; training progress records1,819seconds. Estimated compute isUSD2.00 at the launch rate, not a final invoice. [Terminal record](terminal.json), [training receipt](recovered/mixed/training/run.json), [outputs](recovered/mixed/evaluation/predictions.jsonl).

These are descriptive results on an already exposed, four-work development panel. They are not fresh confirmation, population accuracy, statistical significance or specialist philological certification. The two AI reviews share a model family and are not independent scientific replications. Fresh reviewers differ from the earlier panel on severity and uncertainty; historical ratings remain unchanged in their original report. Compare columns within this new matched panel rather than subtracting across review panels. The fixed merit contract did not change.

## Decision and evidence

Retain step280. Keep the corrected supervision package and candidate as evidence; a failed quality screen does not invalidate verified data repairs. Close this tested96-update mixed recipe. Do not automatically train the full pool, add epochs, launch PAL-REF evaluation or download model weights. The next decision needs evidence about auxiliary-task acquisition versus contextual transfer and specialist review of persistent errors, before choosing another learning strategy. The earlier checkpoint-diagnostic proposal remains unexecuted and would need an updated scope and fresh execution admission; this comparison does not authorize it. Do not convert these DEV answers or reviewer judgments into training data.

- [Comparison plan](COMPARISON-PLAN.md) and [unchanged evaluation contract](../dev-assisted-qualified-20260927/uniform-evaluation-contract.json).
- [Recovered evidence](recovery.json):15 small files plus manifest,247,412bytes, all local hashes verified. All18 provider inventory entries match; two weight files remain cloud-only, with size/commitment and server-recorded hashes rather than a local rehash.
- [Fresh reviewer receipts](../corrected-review-20260930/reviewer-receipts.json), [frozen ratings](scored/blind-review-freeze.json), [full paired arithmetic and per-case transitions](scored/comparison.json).
- [Integrity verification](comparison-verification.json), [independent outcome QA](OUTCOME-QA.md). Four focused integrity/arithmetic tests pass; frozen PAL-REF verification passes. No new paid work occurred during scoring.

Full local replay, including private training/input checks, writes to a fresh output folder: `python -B -X utf8 -m scripts.review_corrected score experiments/corrected-review-20260930 <fresh-output-folder>`.

For arithmetic-only replay from the public snapshot, without private training data or model weights:

```python
import json
from pathlib import Path
from scripts import review_corrected as r
p = Path('experiments/corrected-review-20260930')
read = lambda name: json.loads((p / name).read_text('utf-8'))
lines = lambda name: r.prep.decode_lines((p / name).read_bytes())
contract_bytes = r.prep.CONTRACT.read_bytes()
assert r.sha(contract_bytes) == r.prep.CONTRACT_SHA
result = r.summarize(lines('lead-only/mapping.jsonl'),
    {x: lines(f'reviewer-{x}/packet.jsonl') for x in ('A', 'B')},
    {x: lines(f'reviewer-{x}/reviews.jsonl') for x in ('A', 'B')},
    json.loads(contract_bytes), read('lead-only/provenance.json')['completion'])
saved = json.loads(Path('experiments/training-ready-v2-20260929/scored/comparison.json').read_text('utf-8'))
assert result['reviewers'] == saved['reviewers']
assert result['both_reviewers_screen'] == saved['both_reviewers_screen']
```
