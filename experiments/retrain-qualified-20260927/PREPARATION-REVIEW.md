# Qualified-data retraining preparation

Lead agent/request id: /root
Critic agent/request id: /root/final_external_judge
Critic model and reasoning effort: inherited session settings; no override
Independent from lead: yes
Critic verdict: pass with notes
Evidence reviewed: new canary/continuation controllers, current contract, eighteen controller fault scenarios, four final-completion rejection checks; separate independent bundle and continuation-helper reviews.
Verification evidence: critic executed the actual controller bodies with a fully stubbed provider, one submission per case, owned-job cancellation, timeout recovery, explicit unconfirmed-termination warnings, native deadlines and bounded shutdown; root executed14 existing runtime/canary checks successfully. Individual module critics passed13 bundle tests and15 continuation tests plus independent artifact/negative/embedded-command checks. GPU training on the filtered data is not yet exercised.

The full dataset audit is committed at `9f58bb8`. The new qualified training payload has2237 rows,310745 tokens, maximum820 tokens and76 works; train SHA256 `15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc`. The pinned Transformers5.13.1 scheduling method was directly executed:140updates/epoch,280total. Full model imports were not needed; the shared science environment lacks huggingface_hub, so all HF work used the existing project HF-client environment.

Bundle implementation by `/root/train_review_07`; independent critic `/root/train_review_01` verified the actual directory and ZIP. Twelve parent files are byte-identical; only train, provenance, bundle verifier and reviewed contract differ. No token/text mutation or reference-answer upload. Contract permits only budget, notes and native-timeout differences from its frozen parent. Original model, recipe, tokenizer, runtime and dependency lock remain unchanged.

Standalone `bundle.verify` checks its own manifest and does not independently authorize arbitrary rehashed runtimes/contracts. Production additionally requires the externally reviewed ZIP SHA. The critic regenerated the actual spec exactly and executed both the library and embedded extractors: an internally consistent mutated ZIP was rejected before parsing or destination creation. The reviewed ZIP extracted and verified. This external identity boundary is mandatory.

Continuation implementation by `/root/model_choice_review`; independent critic `/root/train_review_03` passed actual offline tests and generated helper checks for280/312 schedules and USD10/25 ceilings. Local continuation admission must call `training_schedule` as well as `pre_submission_check`; the latter checks timing/state only. Cloud verifies row-derived schedule and saved training identity before base download. The old diagnostic remains intentionally restricted to its original312-step adapter and cannot accept the new model.

The controller critic found a real historical monitor flaw: loss of the submission response followed by a transient reconciliation lookup error could escape without discovering/canceling the job. Root repaired only the new controllers. Eighteen offline scenarios now pass, including transport and nontransport failures, persistent ambiguity, deadline expiry, failed cancellation and processing faults. Exactly one POST per scenario; no foreign cancellation. Four completion controls reject stale312/incomplete280 state. These simulations do not establish future provider availability; native timeouts remain the independent bound.

## Frozen preparation identities

| Artifact | SHA256 |
| --- | --- |
| bundle.py | 60094706124ee58b78a2b73b6a43c30eb9310a2a1d3786f83749e95b597b1a2d |
| test_bundle.py | 8e52b69b7f07c31bf1a671d4e8aec8bbc7f7b17ddb796e481a1f7a2b3868fe1d |
| contract.json | 2f974dca27dc8c68664efe6721f7f420a801513c6cf95d80aace8c18d5e940cc |
| hf_continue.py | 443d6c5a01df3e047e1a39f48d9bc309c11f2016e47661d59190937ea678d1d5 |
| test_hf_continue.py | 338d9f779a6e783f6efd2b70420f47b42228c4653da2b19ccb036a05574b6fbe |
| qualified ZIP | 41fbbe703b7eb3cfc471c83e344ede16c1e92cae8a604b91f638a57d856477b9 |
| bundle manifest | fc62c9138d926139dc1fa4e6b943f06a653aa8cb438ce5963628c24b77f853cd |
| canary controller | bc7d678796a0151d8d16d1c95d898556b5f6563632571109f6347906a9619531 |
| continuation controller | bc9ae9502ed738e16662a2865dcc3911a8af13a1a1a7a47cf7c4899198e16347 |
| canary spec | b70404af4b26803e2ef9d04534b83528dd908c7103ab6f1f54ffa53b37c43e1b |
| canary embedded command | 83732496e581522991f085ba24df18c5f7c17fbd027fe0b5ae4e796ef88fce98 |

Canary run ID: `aa880289a9614f80aaa5a430e53440ee`; approved bucket output prefix `trials/aa880289a9614f80aaa5a430e53440ee`. Input `inputs/cloud-pilot-qualified-20260927.zip` was uploaded and downloaded with exact full SHA agreement at2026-09-27T05:00:53Z. Size6372448bytes. This transferred data/code/tokenizer files, not model weights. No job was submitted by that operation.

Source copies with `.py.txt` suffixes are immutable evidence, not launch paths. Actual commands and readiness gates are in `plans/retrain-qualified-20260927.md`. Bind final Git revision in ignored provenance after committing, recheck spec/controller/bundle identities and current provider state, then admit only the fresh20-step canary. Full continuation remains blocked until its actual new canary evidence and forecast pass.

Budget: prior estimate rounded to USD7.12; current provider rate USD0.041667/minute. Canary30minutes plus5-minute shutdown and USD0.75 reserve = USD2.208345, below its USD3 bound. Combined canary35 plus continuation155minutes gives cumulative USD15.78673 including prior use/reserve, below the user's USD25 cap. No new purchase/top-up is authorized. Estimates are not a finalized invoice; no new GPU has run during preparation.
