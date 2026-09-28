# Contextual-supervision pilot: no translation improvement

27 September 2026. The complete candidate/control experiment fails the predeclared improvement screen for both fresh blinded reviewers. Both give zero accepted whole translations out of15 to either arm. The contextual candidate adds a critical error on the nine separately constrained cases for both reviewers, and adds a whole critical error for reviewer B. Close this recipe branch; do not add epochs, adjust mixtures, promote either new adapter or run the conditional PAL-REF follow-up. This is a negative result for this bounded recipe, not proof that contextual supervision or Pahlavi modeling cannot work.

## Fixed comparison

Both arms started from the same qualified Gemma4-31B step280 adapter and received48 new updates with768 ordered parent slots, fresh optimizer/scheduler and identical initial RNG. The candidate replaced48 ordinary-translation slots with four exposures to each of12 source-qualified contextual-expression targets from9works. The remaining720 ordinary parents and the parent order were shared. Task wording, target length and per-token weight differ by design; the comparison does not isolate a universal linguistic-label effect. See [frozen pilot](PILOT.md).

The same24 source-only DEV prompts, BF16 inference, greedy generation and first-attempt rules apply to both arms. Every scheduled output succeeded. Fifteen whole translations and nine constrained cases remain separate. All reviewer judgments are provisional AI assessments, not specialist adjudication. Zero whole acceptances means none preserved all substantive meaning under this rubric; it does not mean every word was wrong.

| Fixed merit | Reviewer A: control → candidate | Reviewer B: control → candidate |
|---|---:|---:|
| Accepted whole translations |0/15 → 0/15|0/15 → 0/15|
| Whole critical errors |6/15 → 6/15|6/15 → 7/15|
| Constrained supported-span critical errors |3/9 → 4/9|3/9 → 4/9|
| Constrained unsupported certainty |5/9 → 4/9|5/9 → 3/9|
| Works with a newly accepted whole translation |0 → 0|0 → 0|
| Predeclared screen |Fail|Fail|

Each reviewer has zero net accepted gain rather than the required minimum two, no gain across two works, and increased constrained critical errors. Reviewer B also finds increased whole critical errors. No accepted-to-critical transition or newly overconfident case occurs. The paired transitions, separate work reports and all disagreement details are retained in [comparison.json](scored-comparison/comparison.json). Reviewers differ on judgment/severity/uncertainty for5/24 control and6/24 candidate records; their scores are not pooled or adjudicated after unblinding.

The unchanged uniform contract is `4165e8150f291c2cd6077d2daee86513ad08e1851acbfc3e83169bc40263f8c2`; all eight bound files remain byte-identical. These are DEV results, not PAL-REF40 results. Historical step280 and PAL scores used different reviewer panels and cannot be treated as a matched causal comparison with these new arms. Reused DEV supports development decisions, not untouched confirmation.

## What the paired outputs show

Three illustrative, development-exposed cases were inspected after both reviews were frozen. They do not create new training labels or establish the cause of an error.

- Case001 improves from a good-ending expression to a command-related expression. Both reviewers find the assessable meaning and unresolved obeying/issuing distinction better preserved. This constrained gain is real within their provisional assessments, but is not whole-translation acceptance.
- Case014 still mishandles the technical daily penalty and its bearer. The candidate invents a thousand sins. Both call that critical; they disagree whether the control's distorted technical term was already critical or a meaning error.
- Case022 retains some participants, negations and the number five, but the candidate replaces filling springs and striking vegetation with building a small house and planting vegetation. Both judge the changed actions critical. The untranslated source form remains separately constrained; it does not license the invented actions.

The narrow contextual intervention has not transferred into sufficiently correct full translations on this panel. These observations do not distinguish inadequate breadth, optimization effects and missing lexical/compositional evidence, and the pilot did not measure post-training auxiliary-task mastery. More repetitions would therefore be an untested response, not a supported remedy.

## Execution, persistence and cost

Actual source `0c2b869c0e0c0bd08fd0014a9130c14b4366e934`; job `6ab9237d52d0dbd7f1d9c66b`; run `555064e068b54aacafee67e37375ec78`. The server's pinned Linux/A100 runtime, NF4 training canary, both exact adapter resets, completed48-step arms and BF16 adapter reload/switch checks passed. Root verified the committed cloud inventory and recovered18 small files totaling278467bytes with full SHA256 checks at14:59:34UTC, before deliberate shutdown confirmed CANCELED14:59:55.992UTC. All18 account jobs were terminal in the subsequent inventory.

Both adapters remain in the cloud. Their full weight hashes are server-manifest evidence supported by independently checked committed provider size/Xet inventory, not local tensor verification. No pretrained or trained model weights were downloaded to the laptop. The earlier separate startup attempt failed before Python ran; its error and narrow transport repair remain preserved, not silently removed or treated as another scientific trial.

Post-stop authenticated billing displaysUSD13.70 credit andUSD16.61 period usage, with automatic recharge unset. Compared with the fresh pre-run observation, displayed credit fellUSD2.08 and usage roseUSD2.08. These are account deltas, not a per-job invoice. No purchase or recharge occurred. Native timeout75minutes remained in place; deliberate completion used less than that envelope.

Both fresh reviewers saw only their48-row opaque packets. Their completed ratings were frozen before unblinding in [reviewer-receipts.json](reviewer-receipts.json). The unchanged converter then validated actual launch/recovery/prompt/output-token identities and produced the scored comparison. The independent [outcome audit](OUTCOME-QA.md) verifies provenance, arithmetic and interpretation without changing ratings. See also [recovery proof](attempt-2/recovery.json), [job inventory](attempt-2/post-stop-inventory.json) and [billing observation](attempt-2/post-stop-billing.json).

## Strategy decision

Retain the prior qualified checkpoint and all results; neither new arm is a delivery candidate. The conditional PAL-REF40 run is not reached. Preserve theUSD13.70 funded balance rather than spend it on an automatic sweep. The overall improvement goal remains active, with no current evidence-backed paid successor admitted.

Do not repeat the already completed model/assistance comparison, TRAIN recall, conditional-fit diagnostic, source inventory or23-function annotation audit. The four within-parent affirmative/prohibition contrasts and their shortcut discussion already exist in `../grounded-supervision-20260927/CONTRAST-REVIEW.md`; an independent strategy reviewer initially proposed repeating that audit, then withdrew the recommendation after checking those records. The prior TRAIN diagnosis also found many full-meaning failures despite preservation of the reviewed local functions, so generic scope drilling is not established as the next remedy.

The substantive next requirement is better independent semantic evidence: specialist adjudication of representative source/translation relations, or genuinely additional attested contexts with defensible senses and composition. A new training contrast must address a diagnosed gap and preserve the same merit; existing credit alone does not justify one. This is a present evidence limit, not a claim that all possible models or learning regimes are exhausted. CPT still lacks adequate verified additional source text; synthetic/preference/RL training still lacks independently validated targets or rewards. The existing institutional, regime and book-access reports remain the resource starting point; no new collection, contact or credential access was performed here.
