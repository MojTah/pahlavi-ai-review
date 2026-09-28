# Independent outcome QA: partial TRAIN recall

27 September 2026. **PASS for recovered evidence, fixed review arithmetic and bounded interpretation.** The diagnostic itself remains incomplete. This is neither semantic re-adjudication nor approval of another model run, training change or claimed improvement.

## Independently executed checks

All checks were local, read-only except this report, using the project HF-client Python with `-B -X utf8`. A separate offline tokenizer-only check used the existing shared science interpreter and project client dependencies; no model weights were loaded. No cloud calls, credential access, package installation, source edits or broad test-suite reruns occurred.

1. Rehashed all six recovered export files against both `recovered/manifest.json` and `recovery.json`; verified sizes and the total **212,777 bytes**. Verified manifest identity, recovered run/prediction byte identity with the private packet archive, and the step-280 training manifest/metadata chain. Base provenance equals the run's model/revision/file hash map. Saved trainer state and metrics match the trained manifest. Adapter tensor identity is a bound cloud-recorded hash, not a fresh local tensor measurement.
2. Called the frozen helper's material/run validators and rebuilt all **nine** packet/archive files in memory; every byte equals the actual saved file. This binds the twenty source/reference parents, qualification decisions and 28 qualified scopes, exact prompts and recorded token hashes, runtime identity and first-attempt partial schedule. Both packets contain forty slots and 56 scopes; all eighty review IDs are unique and disjoint across reviewers. No explicit condition/model/history fields are present in the reviewer schema; identifying mappings remain private. This verifies packet construction, not an audit of reviewers' unseen mental context or immunity to guessing a format from output style.
3. Validated both actual review schemas, forty-slot/56-scope coverage, hashes and literal output spans. The scored copies are byte-identical to the frozen reviewer originals. Independently joined mapping, packets and reviews and reconstructed every condition total, failed-category count, uncertainty-handling count, local-scope count, all sixteen work breakdowns per condition, and all twenty paired transitions. Every field matched `scored/summary.json`; the scorer's aggregation function was not used for this independent reconstruction.
4. Independently loaded the pinned local tokenizer after hashing its three files. **All 25** recorded output strings exactly equal decoding their saved output-token IDs with `skip_special_tokens=True`. The last output has 4,096 tokens, 41 unique token IDs, no recorded EOS ID, and a maximum repeated twelve-token window count of **499**. Recorded elapsed time is 668.0900821429677 seconds. The actual counters agree: 25 attempted/recorded, 24 successful, twelve complete parents, fifteen unattempted slots, no active output.
5. Rehashed the unchanged uniform merit contract and all eight bound benchmark/development files. Reconstructed training-loss arithmetic, stored supervised-position counts, function-parent clustering, elapsed cost and the latest recorded account delta independently, as detailed below.

## Fixed denominators and separate reviews

| Reviewer | Format | Accepted | Meaning error | Critical error | Uncertain | Capped error | Unattempted | Scheduled |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | Training | 5 | 4 | 2 | 1 | 1 | 7 | 20 |
| A | Evaluation | 4 | 5 | 2 | 1 | 0 | 8 | 20 |
| B | Training | 5 | 4 | 2 | 1 | 1 | 7 | 20 |
| B | Evaluation | 4 | 6 | 1 | 1 | 0 | 8 | 20 |

Each reviewer has exactly **twelve completed pairs**: five accepted training-format outputs, four accepted evaluation-format outputs, four shared acceptances, one acceptance lost (`TRAINRECALL1-004`), and no acceptance gained. These are separate within-reviewer comparisons. The twenty scheduled parents remain the coverage denominator. Across the 24 successful outputs, whole-meaning labels agree on 23; agreement is not pooled merit or expert validation.

The five contextual gloss scopes are preserved in both formats by both reviewers. Nine function scopes are assessable per format: A records eight preserved/one contradicted in both; B records seven/two for training and eight/one for evaluation. Fourteen scopes per format are unassessable: eleven negative-directive and three affirmative-directive scopes. These local diagnostic counts do not vote on whole-passage acceptance. The eleven unassessed negative-directive scopes account for eleven of the fifteen qualified scopes of that kind.

The report correctly treats the completed parents as a sorted-ID prefix with potentially generation-dependent truncation, not a representative random sample. It preserves failure/missingness, separates this seen-TRAIN result from DEV/PAL-REF, avoids a causal format claim, and does not infer a masking defect or general grammar deficit from failed recall. Its example diagnoses remain attributed to the frozen reviews; I did not independently re-rate those meanings.

## Training and clustering arithmetic

All 280 logged update numbers are contiguous, losses finite, and gradient norms positive and finite. Reported trainable parameters are 122,429,440. Independently calculated:

- First twenty mean logged loss: **2.7060996651649476**; last twenty: **0.7521619111299515**; last loss: **0.8188119530677795**.
- Mean of steps 21–280: **1.0620056136296345**. Their sum divided by 280 equals the stored resumed aggregate **0.9861480697989464**. This numerical identity does not turn that aggregate into endpoint quality or prove the implementation cause of its denominator.
- Frozen 2,237 TRAIN rows contain **83,243** labels unequal to `-100`; the selected twenty rows contain **934**. These are static stored target/terminator positions, not independent traces of actual loss-bearing batches.
- The qualified function inventory contains **23 scopes / 15 parents / 15 works**. Repeating a full target once per scope gives parent `150000053` three copies of its 551-character target: **1,653 / 3,932 = 42.039674%**. The report's 42% claim is accurate and explicitly about target characters under that hypothetical repetition scheme, not token weighting or an admitted recipe.

Declining training loss supports recorded optimization activity, not semantic quality. The NF4-training/BF16-recall distinction remains explicit. The proposed next-fit paragraph preserves zero optimizer updates, twenty existing parents and eighty forward evaluations, with no refill of failed recall slots. Its linked source-control permutation hashes correctly and shift five is independently the smallest positive cyclic shift excluding same-work pairs. This narrow consistency check does not review an implementation, admit spending, or certify the prospective diagnostic's results.

## Recovery, shutdown and billing evidence

The locally saved records consistently identify one new job, `6ab8fa5d6b030d633f698f47`, run `b9a65cd416124617a68db6580349b32f`, the same admission and preparation hashes, a 30-minute native timeout and no automatic retry. Recorded recovery at 11:34:21 precedes confirmed `CANCELED` at 11:34:41.866487 UTC; the 11:35:55 inventory records fifteen total jobs and no nonterminal jobs, versus fourteen before submission. No second submission is represented in this evidence.

Submission-to-terminal elapsed time is **1,267.736938 seconds**. At 41,667 micro-USD/minute it yields **USD0.8803799165941**, rounded to USD0.88038. The subsequent saved billing observation records credit **USD16.20** and period usage **USD14.07**; both changes from USD17.12/USD13.15 equal **USD0.92**. The report correctly supersedes any implication that the old `compute_upper_estimate_usd` name proves a billed-charge ceiling. Neither figure is a per-job invoice, and the account-level discrepancy is unresolved. Both observed numbers are below the declared approximately USD1.50 envelope; automatic recharge is recorded unset.

Remote committed-inventory checks, cancellation, account observations, absence of purchases/recharges and absence of prior local weight downloads are lead-recorded observations. I verified their internal identities, timing and arithmetic, and independently verified all recovered local bytes; I did not requery the provider or inspect billing credentials. The saved cloud manifest's `remote_inventory_verified` and `cross_job_sha256_verified` remain false because it predates the lead's subsequent recovery observation; this report does not rewrite those historical fields or mistake them for completed local checks. Fresh independent review contexts are lead-declared identities, while actual packet/review separation and hash bindings are directly checked here.

## Exact reviewed identities

Paths below are relative to the project; SHA256 values bind the reviewed bytes.

| Artifact | SHA256 |
| --- | --- |
| `experiments/train-recall-20260927/REPORT.md` | `17dc5e4f29efbf1188fa8b4a1804d1f6d2deecacbcccd05fda06ef7b9aaa88fd` |
| `experiments/train-recall-20260927/recovered/manifest.json` | `cd4c606d1fc5b9db4db84faad8575cf2fa114bb910769c93f8fe9a751ead1816` |
| `experiments/train-recall-20260927/recovered/recall/run.json` | `1b648677a8c587e553c6d6eaffa9b8da8fb289dccf51576ff439030b143f5e06` |
| `experiments/train-recall-20260927/recovered/recall/predictions.jsonl` | `b4a4349b4beba3d9b2640810ac3248ceb6a3d9390c867d77f478fbaa3f993734` |
| `experiments/train-recall-20260927/recovery.json` | `c65a9e9239a263139c041a9d07f185fe9fc6d6eac55c83956db9eae1fdab7d6c` |
| `experiments/train-recall-20260927/execution.json` | `a7d7660ff18b15c936b1e6b21f69d22ad0ea36fc0a9938920209c7d6bbee5da5` |
| `experiments/train-recall-20260927/admission.json` | `7edbb0d0e72ed77ce5629b2a956de03b6a0367fe4afc1c96d13ce472a233d8c1` |
| `experiments/train-recall-20260927/shutdown.json` | `19026d00550ada1a87a7918af56f1098fb9d224d180e9b356e5f015ff024b4ca` |
| `experiments/train-recall-20260927/job-inventory-after.json` | `dda1abc45491d0db65c8d3fb666e43efab4f441ca2dac9180abc7621cc7fdcb8` |
| `experiments/train-recall-20260927/billing-after.json` | `66ab651b649ed2949335608a0c968fd418fce6dd40b22a42c3d3d660c67b0b5e` |
| `experiments/train-recall-20260927/technical-output-audit.json` | `df389e5b1f0f5ad77ca45e29729ee922e539a0400c8904d594c9d73f8ec96408` |
| `experiments/train-recall-20260927/blind-review/lead-only/provenance.json` | `0eef3fc69b9f9d2099648de954731041614d36a126c3c8b22f68943353b01aeb` |
| `experiments/train-recall-20260927/blind-review/lead-only/mapping.jsonl` | `ef0d456cf37d07e1ad371d9c3fd4ce22eecc3d4b0175d98cc2ea88d01350c04d` |
| `experiments/train-recall-20260927/blind-review/reviewer-A/reviews.jsonl` | `f757cfc91eb55ec4b5c907ea1ece8197753ccff01407c801f5a3829f6f656d3b` |
| `experiments/train-recall-20260927/blind-review/reviewer-B/reviews.jsonl` | `0bb9eeaf73d5865bb6bb1d8830790e0546490a5121268e2ccec96cab7a6b682d` |
| `experiments/train-recall-20260927/scored/summary.json` | `d02eab449a0bef6306e93d199f04340b317d57a43204cde463070d11b6dadb57` |
| `scripts/review_train_recall.py` | `79fbfb3f2cfc73a2cf770f30aabd19463dacc3c5f4f6ef8055199813ec897a0b` |
| `experiments/dev-assisted-qualified-20260927/uniform-evaluation-contract.json` | `4165e8150f291c2cd6077d2daee86513ad08e1851acbfc3e83169bc40263f8c2` |
| `experiments/retrain-qualified-20260927/continuation/training/checkpoint-280/trainer_state.json` | `1ba7c18671c477722b69cabb4cc204b06bce6b784218588343b5a7f827b8ee20` |
| `experiments/retrain-qualified-20260927/continuation/training/metrics.json` | `5327988bac7e0b68766bf63c15913675cd583c4fdfd36a06d381265e381f4473` |
| `experiments/train-fit-20260927/PROTOCOL.md` | `bcf6d74c7491d5294917b129c63149e1b0cda03a462f60980027b7d7715b3830` |
| `experiments/train-fit-20260927/source-control.json` | `3db2398a95b6480ad2522dc2fe30d2d38156564e3a4a72714b43bcc2a54393a0` |

The rebuilt packet provenance additionally preserves the exact input, reference, TRAIN, tokenizer-audit, qualification-source, packet and instruction hashes; those nine source bindings and nine rebuilt files were verified rather than merely copied into this report.

## AutoCode Critic record

- Mode: Classic + Critic.
- Lead agent/request id: /root
- Critic agent/request id: /root/final_external_judge
- Critic model and reasoning effort: inherited session settings, no override
- Independent from lead: yes
- Critic verdict: pass
- Evidence reviewed: Exact artifacts and hashes above; all recovered files, both frozen review packets/ratings, unchanged uniform contract, cited training/qualification evidence and final report.
- Verification evidence: Direct local SHA/size checks; nine-file in-memory packet reconstruction; actual review coverage/span validation; independent full condition/work/transition/local arithmetic; 25 actual tokenizer decodes; loss, label-count, repetition, clustering, elapsed-cost and account-delta calculations. No outcome or rating edits. No remaining blocking defect in this outcome-reporting scope.

PASS is limited to the actual partial-run evidence and its reporting. Semantic correctness remains provisional AI assessment; provider-side observations were not repeated; model tensor identities were not locally rehashed; no new inference/training launch is approved.
