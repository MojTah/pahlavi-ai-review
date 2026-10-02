# Training health and completed diagnostic

30 September2026. **The earlier corrected96 training really happened. Today's shorter job was the planned inference comparison, and all56 first attempts completed.** No new training, retry, model-weight download or credit purchase occurred in this check.

| Run | What happened | Direct evidence | Duration |
|---|---|---|---|
| Prior corrected96: `6abc15b8031314b696342162` | LoRA adapter continuation from step280 |96 completed optimizer steps;1,536 processed slots; changed tensor digests at step20 and final; finite loss/gradient records; valid answer masks |30m19s training;47m34s complete job |
| Current diagnostic: `6abd2a1d404719ba376138e8` | Inference with both existing adapters |28 cases each;56 saved first outputs; both A100 prefill canaries passed; no timeouts/caps/missing attempts; adapter weights unchanged during inference |14m37s RUNNING lifecycle |

The detailed independent [training-health audit](TRAINING-HEALTH-REVIEW.md) rehashed prior training records and checked all96 logged steps plus all1,536 selected token/mask arrays. Initial, step20 and final trainable-tensor digests differ. The final adapter SHA-256 is `c2305fc9cdc1fb99a346e58c92ae2ba1faa030ff6961bf0be1452f75006a8df0`, matching the candidate verified and loaded on the server for this comparison. Step280 is the distinct `a51bcd02c6077bcec400c1f342ede3205f260e419ed4f9e3ad0f4338a7e4afdf`. A zero initial logged learning rate belongs to warmup;96 completed steps does not claim96 separately verified nonzero weight changes.

The important exposure limit remains: the available pool contained9,973 unique prompts, but this bounded pilot processed1,536 slots. It did not train on the whole enlarged pool. The first16 versus last16 logged mean loss declined1.062→0.694 across different batches; this is not a controlled quality measurement. Changed weights, finite gradients and lower loss establish execution, not useful translation learning.

## Current inference integrity

The recovered manifest matches its hash printed in the final server log. All9 declared output files match their recorded sizes and SHA-256 hashes; the complete recovery, including manifest, is126,844bytes. The server's historical `remote_inventory_verified:false` records that it could not certify remote persistence before exit. The subsequent authenticated bucket readback and local verification now establish persistence for these exact files; the original manifest remains unchanged.

[Reproducible verification](verify_results.py) checks the run/proposal identity, matching scientific settings, both exact adapter identities, full fixed alternating schedule,56 unique ordered outputs, all input prompt/token-prefix hashes, output-text hashes and token counts, EOS termination, both GPU canaries and unchanged final adapters. [Machine-readable result](result-integrity.json) records the actual observations. Raw exports remain immutable.

Generation itself took356.745seconds for2,099 output tokens across56 answers, with median3.737seconds and maximum40.274seconds per answer. The rest of the run included environment setup, server-side model download/loading, verification and export. The reviewed implementation loads the base once and switches the two frozen adapters; it does not retrain or reload a whole base per prompt. This explains why it finished much sooner than the two-hour ceiling, which was a timeout rather than a predicted duration.25/28 paired answer texts differ; textual difference alone is not improvement.

At the verifiedUSD0.041667/minute rate,15 rounded compute minutes gives approximately**USD0.63**. This is an estimate, not a final invoice or refreshed credit balance. The job is COMPLETED and no new cloud job was started.

## Interpretation boundary

Technical execution passes. The separate blinded module review is now complete. The56 outputs were shuffled with checkpoint and exposure identities hidden; both reviewers received the same complete reference qualifications in fresh contexts. Their individual records and every case transition remain separate. Do not pool lexical JSON, conditioned grammar, inscriptions and passages into one accuracy percentage. AI reviewers are not independent expert measurements, and the panel mostly measures familiar tasks rather than unseen generalization.

Prior training used an NF4 base with BF16 computation; the current diagnostic loads BF16 weights. The exact prompt-prefix parity check passes, but the numerical precision caveat remains. No result here automatically admits another training run or promotes a checkpoint. Follow the already frozen [decision plan](../PLAN.md) after reviewing the diagnostic pattern.

## Blinded comparison under the frozen module rubric

| Module | Reviewer A: step280 → corrected96 accepted | Reviewer B: step280 → corrected96 accepted |
|---|---:|---:|
| Complete lexical meaning inventory |0/6 → 0/6 |0/6 → 0/6 |
| Conditioned grammar |3/4 → 4/4 |3/4 → 4/4 |
| Inscription task |2/2 → 2/2 |2/2 → 2/2 |
| Familiar historical passage |2/12 → 4/12 |2/12 → 4/12 |
| Targeted contextual sense passage |1/4 → 1/4 |1/4 → 1/4 |

These are provisional AI judgments on deliberately selected, dependent cases. They do not replace or change the15-passage DEV merit, and they do not establish general accuracy or statistical superiority. Grammar prompts supply their intended grammatical context; both inscription prompts share a formula.24/28 cases received exact corrected-continuation exposure; the remaining four preserve their older step280 exposure. There is no fresh unseen confirmation here.

The lexical0/6 means **zero fully supported inventories**, not that every output word is wrong. Both arms partially recover greatness/size onLD-006, while omitting plural great-things and Grandee-status senses; corrected96 adds unsupported power. Other important failures remain source-scoped homonyms: `²kardan` is returned as doing rather than slaughter/cut; `ēr` is returned as here rather than the supplied adjective lower; CPD`agār/agārīh` meanings are not recovered. Corrected96 learned some output shape:4/6 lexical outputs match their supplied target schema, versus0/6 for step280; its two CPD outputs still flatten the structured sense/component schema. All12 lexical answers parse as JSON after stripping presentation fences where present. Formatting improvement is separate from lexical meaning.

Grammar gain isLD-009. Historical gains areLD-013,014 and018; LD-021 regresses from accepted to uncertain for A and meaning_error for B. There are no accepted→critical transitions in this diagnostic. Historical critical errors decline3→2 for A and4→2 for B; the different baseline count is theirLD-018 disagreement. Qualified occurrence scopes improve6/12→9/12 for A and6/12→10/12 for B; A leavesLD-023's candidate scope uncertain, whereas B preserves it. Whole-passage failure and scoped success remain different outcomes. Targeted passages retain one critical error per checkpoint per reviewer.

Structural ratings also differ: A strips presentation fences and records all six reference lexical answers as valid JSON with a different schema; B judges the raw fenced answers invalid JSON. Both original ratings remain unchanged. The separate mechanical check confirms raw parseability0/6→6/6 and parseability after optional fence removal6/6→6/6. This explains a presentation convention difference; it does not improve any semantic label.

See [all case transitions](case-transitions.jsonl), [per-reviewer/module counts](review-summary.json), original [reviewer A](reviewer-a.jsonl) and [reviewer B](reviewer-b.jsonl), [fixed review instructions](BLIND-REVIEW.md) and [aggregation program](summarize_reviews.py). No disagreement was erased or re-rated after unblinding. `result-integrity.json` retains `semantic_quality_scored:false` because it is the separate technical-audit record; this later semantic review is recorded here and in `review-summary.json`.

## Next decision

Keep step280 as the retained reference; corrected96 is a candidate with limited familiar-task gains and a continuing lexical-acquisition problem. The health checks rule against the simple explanation that no optimization happened. Exact prefix/mask/truncation checks already passed, so do not repeat that broad audit or increase corpus size as an automatic remedy.

A useful remaining control in the frozen plan is a separately specified **matched-NF4 inference comparison on these existing checkpoints**, holding prompts, cases, adapters, seed and generation policy fixed. This addresses the known precision difference before blaming the training objective or paying to retrain. It is a proposed follow-up, not authorized or launched by this result, and not established as the uniquely best experiment. If lexical failure persists under matched precision, design one controlled acquisition intervention focused on effective exposure and loss/task weighting, with explicit Persian/context transfer and retention checks. Do not change model, data, optimizer and prompts together or repeat the same96-step recipe without a hypothesis. Expert calibration of disputed meanings remains necessary before stronger philological claims.

## Review evidence

Mode: Classic + Critic. Root recovered/verified small records and aggregated independent fresh-context semantic reviews; no new service, model run or training framework.

Lead agent/request id: /root
Critic agent/request id: /root/astra_runtime_plan_recheck
Critic model and reasoning effort: gpt-6-astra; existing selected reviewer, unchanged reasoning effort
Independent from lead: yes
Evidence reviewed: TRAINING-HEALTH-REVIEW.md, RESULT-INTEGRITY-REVIEW.md, QUALITY-AGGREGATION-REVIEW.md; exact prior training records, recovered current inference records, verifier, blinded packet/mapping, both rating files and final report arithmetic
Verification evidence: Independent current result verifier execution plus inventory/ID/token checks; prior96-step loss/gradient/mask/hash checks; independently reconstructed blind mapping and per-rater/module aggregation of both56-output reviews; separately executed JSON parsing with and without fence removal
Critic verdict: pass

The technical critic does not constitute a third semantic vote or specialist validation. No new paid action is implied by this completed checkpoint.
