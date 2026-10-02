# Independent quality-aggregation check

30 September2026. Reviewer `/root/astra_runtime_plan_recheck`. **PASS for mapping, arithmetic and preservation of review scope.** This is a calculation/integrity review, not a third linguistic vote.

Read `summarize_reviews.py`, both56-row rating files, saved summary/transitions, blind packet/mapping, raw56 predictions, frozen input/reference packet and review instructions. Used a separate read-only calculation to reconstruct counts and verify identities; did not rewrite ratings, aggregation code or outputs, call an API, use GPU/model weights or assign new quality labels.

The mapping is bijective over all28 cases and both arms. Every blind answer equals its raw prediction and output hash; prompts equal the frozen case input. Blind module names map correctly to the original modules. Each supplied evidence/qualification field equals the defined projection from the frozen reference: learning target, expected answer where applicable, scoped qualification/gold/expert flags, and published/linguistic qualifications where available. No checkpoint/arm field is present in the blind records. This establishes packet construction; fresh-context review conduct is separately documented by the lead.

Each rater supplies exactly56 distinct required blind IDs. Independently reproduced each module/arm's label, structure and scope counts and checked every saved paired transition against the original rating object and mapping. All source hashes in `review-summary.json` match current packet, mapping, instructions and ratings. Denominators are unchanged; all28 pairs remain included per rater.

| Module | Reference accepted | Candidate accepted | Agreement |
|---|---:|---:|---|
| Lexical recall |0/6 |0/6 |Both raters |
| Conditioned grammar |3/4 |4/4 |Both raters |
| Inscription recall |2/2 |2/2 |Both raters |
| Historical retention |2/12 |4/12 |Both raters |
| Targeted sense applicability |1/4 |1/4 |Both raters |

Historical critical errors are3→2 for reviewer A and4→2 for B. Historical occurrence-scope preservation is6→9 for A and6→10 for B. Two individual output-label disagreements are retained in the separate ratings; equal acceptance totals do not imply identical judgments. Scope preservation is distinct from whole-answer acceptance. Zero fully accepted lexical records means the full supported-inventory rubric was not met; it must not be paraphrased as zero correct words or no learned lexical content.

The summary keeps `pooled_accuracy:null`, provisional AI review true and expert adjudication false. No new promotion threshold or pooled merit is introduced. These descriptive counts concern familiar, qualified task cases and correlated AI ratings, not unseen population accuracy, causal attribution to training, expert certification or automatic checkpoint promotion. Historical12 and targeted4 are separate diagnostic modules; neither is interchangeable with the earlier15-passage development benchmark.

Reviewed SHA-256 identities:

- reviewer A: `62aff80bd406e659facf4c9201ab213f1b3ac4962bc50ef04eb401253113cdff`
- reviewer B: `5e3ddba1d159bb4e242b7d213a86589e82d5c4dbb7163e578b5fe519d57a09db`
- review summary: `1c25c74a6e2f8f00d64b83f876f7db9fb4f48f40c7a7f396111c1fbcfea87c78`
- paired transitions: `3dd8c76c80fa0f24ab64bb4c7f394c732e28f45e5d076008eab7187050913e10`
- blind packet: `35c9eb33b6d470dea94d03dfbf51ec1bdfc85083d528490b95a2b01ab6d498ee`
- blind mapping: `bfba8384b69ddf5048d352e27386a18f02c90c1de8130009c152a3173a9fddcf`

The prior training-health review establishes execution of the earlier96-step continuation. The result-integrity review establishes complete later inference. This aggregation review establishes faithful arithmetic on the supplied provisional judgments; these three evidence scopes should remain distinct.

Final OUTCOME consistency check: the accepted-count table, grammar gainLD-009, historical gainsLD-013/014/018 and LD-021 regression match saved transitions. Historical critical/scope counts and the0/6→4/6 target-schema counts are correct. Independently parsed all12 lexical outputs after stripping optional presentation fences. Reviewer A labels the six reference structures `valid_json_different_schema`, while B labels them `invalid_json`; the successful normalized parsing is a separate mechanical check, not agreement between their raw structure judgments. Both rating files preserve that disagreement. The tiny dependent-panel limits, unchanged historical DEV criterion and no-promotion/no-automatic-training language are appropriate. A matched-NF4 comparison is consistent with the already identified precision caveat and remains a proposed, separately specified/authorized control; this aggregation check does not establish that it is uniquely the best next scientific experiment.

Metadata closure: checked the new mechanical-syntax calculation and independently reproduced raw JSON parseability0/6→6/6 and optional-unfencing parseability6/6→6/6. Removing only `mechanical_lexical_json_syntax` from the final summary and restoring its existing Windows newline serialization reproduces the previously reviewed summary hash, proving its other content is unchanged. The final OUTCOME paragraph accurately distinguishes the two raw structural judgments from this mechanical check. Updated the summary identity above; no ratings or semantic decisions were changed.
