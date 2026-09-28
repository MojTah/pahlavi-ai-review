# Independent contrast and training-design review

27 September 2026. **PASS for bounded preparation and eight provisional local-function qualifications.** Retain both withheld candidates without function labels. The matched-arm framework is defensible as an exploratory recipe comparison; implementation, exact training exposure and paid admission remain unverified. This review changes neither the prior twenty-label qualification nor any training data, model, benchmark or launch authorization.

## Checkpoint and runtime evidence

Directly read the saved qualified checkpoint metadata and contract. `trainer_state.json` records `global_step=280`, `max_steps=280`, `epoch=2.0`, and two training epochs. The final logged learning rate is `3.690036900369004e-07`; the contract specifies linear scheduling, initial learning rate0.0001, seed3407, microbatch1 and gradient accumulation16. These are completed-schedule metadata. The local recovered checkpoint contains no optimizer/scheduler/RNG binary or adapter tensor file, so this review does not assert their stored tensor values or the exact final scheduler learning rate.

Inspected current `runtime.train`, `resume_checkpoint`, `bundle.tokenize_row` and `validate_row`. Resume requires the same model/training settings, TRAIN hash, runtime identity and base files; it also requires a complete passing-canary checkpoint. The fresh path constructs a new LoRA adapter, while the current resume path restores a full checkpoint. Neither is already an implemented “load step280 adapter, begin fresh mixed-task optimization” path. The tokenizer always renders the fixed translation task, masks its full prompt and supervises the answer plus terminator.

Executed `bundle.validate_row` against a real current tokenized TRAIN row: valid input passed; adding either a `task` or `prompt` field separately raised `Unexpected training field`. This is direct offline evidence of the schema restriction, not a GPU execution test. Mixed tasks must use a separately identified preparation/execution path, not altered attested source strings or a disguised resume. The reviewed runtime/bundle were not edited.

## Matched-arm design assessment

The final reviewed design correctly starts both arms from identical saved step280 adapter bytes and the same base revision, then uses a new optimizer/scheduler phase. Its revised RNG instruction explicitly restores the same newly seeded pre-phase snapshot for each arm, rather than historical checkpoint RNG or arm A's updated state. This resolves the earlier wording ambiguity. The intended separation between ordinary translations and derived task answers is appropriate.

Matching parent-slot order, update count, seed, trainable layers and optimizer recipe controls additional updates and parent-passage exposure. It does **not** equalize prompt lengths, supervised-token totals, gradient contributions or effective loss weights. Read the introductory “equivalent additional translation-training exposure” as this limited parent/update matching, not token equality. The body explicitly acknowledges that distinction and appropriately describes an operational recipe effect rather than the isolated causal value of linguistic labels.

Before an implementation can be admitted, the existing planned census must bind the actual parent slots, repetitions, task mixture, prompt/answer token counts, supervised tokens, update budget and loss normalization. The real numerical check must establish how losses combine across tokens, examples and gradient-accumulation steps; assert identical starting adapter tensors, fresh optimizer state and reset RNG; and exclude truncation of targets. These checks are requirements still to perform, not results established by prose or this review. Sharing a base download is compatible with independence only if per-arm mutable model/optimizer/scheduler/RNG state is reset and verified. Separate outputs must preserve both arms and partial failures.

The design leaves ratio, learning rate, update count, dataset, budget admission and new task-aware code unfrozen. Its feasibility judgment about a small label set is a planning judgment, not an empirically proved minimum sample size. Label count alone neither proves benefit nor categorically rules out a bounded, predeclared learning diagnostic or exploratory pilot. A broader strategy decision outside the reviewed file is outside this review's approval.

## Fixed evaluation boundary

Verified the uniform evaluation contract SHA and all eight bound source/metric hashes by raw bytes without decoding DEV/TEST reference bodies. The reviewed design preserves source-only24-case DEV assessment, first attempts, two fresh blinded reviewers,15 whole and9 separately constrained cases, work-level accounting and the existing improvement screen. Both reviewers must independently meet the net-gain/two-work and harm guards; counts are not pooled. The matched control, rather than the historical step280 ratings, is the primary comparator.

The existing contract's four-condition names belong to the previous96-output experiment. A future two-arm packet needs new run/condition identities while preserving the rubric, case membership, denominators, missingness policy and screen; silently reusing old condition labels would not be identity-preserving evaluation. No such packet or scorer adaptation was executed here. The plan correctly discloses reused DEV and PAL-REF, treats training fit as a mechanism diagnostic, and does not call the reused40-case PAL-REF an untouched confirmation. No new gold standard or metric is approved.

## Contrast artifact verification

Executed an independent standard-library check with `resources/local/hf-client-venv/Scripts/python.exe -B -X utf8`; it exited0/PASS. It verified every pinned input hash, all2,237 TRAIN row qualifications against the frozen ledger and held-out works, and the eight proposed plus two withheld row identities. Exact original source/target strings, row/source/target hashes, qualifications, citations, raw source pointers and TRAIN/ledger line/byte hashes match. All32 retained span/UTF-8 coordinate checks pass. A changed source and a deliberately shifted span were rejected in memory.

An independent Unicode lexical scan reproduced419 standalone `nē`/`nēst` occurrences in333 rows across29 works. The work/shortest-source/ID ordering agrees with the recorded selection trace. Eight unique proposal IDs cover eight works, four per function. The four positive clauses reference previously reviewed `ma` occurrences in those same parent rows. Their source scopes do not include the neighboring negative particle. This provides contextual training candidates against a whole-row `ma` shortcut; it does not demonstrate that a model learns or generalizes the distinction.

I read all selected and withheld original contexts and witnesses. The scholarly basis is the same S22 printed80/83 and Nyberg printed281 pages independently inspected in the prior review; they were not re-rendered here. S22 printed83 supports the `nē`/`ma` distinction, while the cited imperative discussion does not uniquely assign morphology from an ending. The local source and Persian witness, not the particle alone, support the following functions. No new source repair, translation, lexical sense or morphology gold was introduced.

| TRAIN record | Reviewed local function | Decision and boundary |
| --- | --- | --- |
|`parsig:101000002:pal>fa`|Negative comparative assertion, `nēst wattar...`|ACCEPT provisional. Preserve its relative-clause context, reconstructed `*andar` and all ledger qualifications; no evaluation of the wider narrative or participant identities.|
|`parsig:107000005:pal>fa`|Negative assertion in a relative clause, `kas nē dārēd`|ACCEPT provisional. This states a lack of someone; it is not a prohibition on having. No indicative-morphology or lexical-sense target.|
|`parsig:108000001:pal>fa`|Negative assertion, `dānāgīh rāy tā nēst`|ACCEPT provisional. Keep `nēst` as the attested whole-token span; do not invent particle/copula decomposition offsets.|
|`parsig:115000009:pal>fa`|Negative narrated event, `pad freh nē pahikārd`|ACCEPT provisional. No command is expressed by this local witness; the qualified surety/agent identification remains unresolved.|
|`parsig:109000005:pal>fa`|Positive contentment instruction, before the separate theft prohibition|ACCEPT provisional. Preserve the positive local scope and editorial Persian material; no inferred alignment for supplied wording.|
|`parsig:150000053:pal>fa`|Positive reported instruction, `har kas dōst bāš`|ACCEPT provisional. Neighboring negative and conditional clauses do not negate this local instruction.|
|`parsig:509000001:pal>fa`|Positive reported instruction, `any ānōh pattāy`|ACCEPT provisional. Retain the contrastive connective and local stay-there instruction; the previous do-not-come command is separate.|
|`parsig:521000003:pal>fa`|Positive petition, `panāh-griftag udāy`|ACCEPT provisional. The preceding negative petition does not negate this request; no addressee identity or universal lexeme sense is assigned.|
|`parsig:106000002:pal>fa`|Normative `nē āzārdan` candidate|Retain EXCLUDED_OUTSIDE_CATEGORY. The Persian deontic witness does not support an ordinary factual-negation target. This is not a rejection of the original translation or a new prohibition label.|
|`parsig:106000008:pal>fa`|Temporal/conditional outcome candidate|Retain ABSTAIN_FOR_THIS_PILOT. A broader assertion analysis may be possible, but this packet leaves contextual force unassigned. Do not turn the abstention into a claim that the passage is false, mistranslated or a directive.|

All eight acceptances are **provisional local-function qualifications for auxiliary development**. Four examples of each type do not establish representative work/genre coverage, balanced optimization or universal `nē` behavior. They address the previous absence of explicit positive/ordinary-negation contrast labels; model discrimination, transfer to unseen combinations and translation improvement remain untested. The original twenty-label decision stays frozen, and all proposal files still record zero training admissions.

## Exact reviewed identities

| Artifact | SHA256 |
| --- | --- |
| `NEXT-TRAINING-DESIGN.md` | `3561e5cb5be3e199f08b17fc102b64d03f396818b8ce007a1313d287379d6058` |
| `CONTRAST-PILOT.json` | `21b614cfd9082d5a30e0e9576dd9e6f4f3ee6ec25d49579fd449a44717bf27ec` |
| `CONTRAST-PILOT.md` | `2f61ab2bf0b60a71bafd642d248c90a94a41bfbe53c709cfb45eb692a587202d` |
| Saved checkpoint280 `trainer_state.json` | `1ba7c18671c477722b69cabb4cc204b06bce6b784218588343b5a7f827b8ee20` |
| Saved training `contract.json` | `2f974dca27dc8c68664efe6721f7f420a801513c6cf95d80aace8c18d5e940cc` |
| `cloud_pilot/runtime.py` | `5f42bcc70dd80de22c624130a07b179b134cec767164e33cb28604f1b497298d` |
| `cloud_pilot/bundle.py` | `60094706124ee58b78a2b73b6a43c30eb9310a2a1d3786f83749e95b597b1a2d` |
| Uniform evaluation contract | `4165e8150f291c2cd6077d2daee86513ad08e1851acbfc3e83169bc40263f8c2` |
| Qualified TRAIN | `15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc` |
| Final ledger | `d79af2e64fbb92954c8b8d0ed9cb7a34e7e7d24d4c22ea9c22f1da6d569a8e77` |
| Held-out inventory | `7eba461256dfcf44e324dde31d2b119cac1b4fae866ca0a53e705217389ba060` |
| Previous qualification decision | `e466aa2bc1b2129e802605ff60882b550b1517a6b2c9ffba84b1419a8bc8fdd6` |
| Previous independent review | `d6922164dfe34399c3095bc272c2eca976784f26eaa55e99bb02e70421eb2462` |

## AutoCode Critic record

- Mode: Classic + Critic.
- Lead agent/request id: /root
- Critic agent/request id: /root/final_external_judge
- Critic model and reasoning effort: inherited session settings, no override
- Independent from lead: yes
- Critic verdict: pass
- Evidence reviewed: Exact design, checkpoint metadata, historical runtime/bundle, frozen evaluation identities, contrast proposals and withheld witnesses, qualified TRAIN/ledger/heldout bindings and previously inspected scholarly source pages.
- Verification evidence: Direct saved-state/contract inspection; real bundle validation plus two unexpected-field rejections; independent hash/qualification/line-pointer/span checks for all ten contrast records;32 spans;419/333/29 lexical scan and selection ordering; changed-source/shifted-span failures; independent narrow semantic decisions. No GPU, cloud, network, credentials, installation, nested agents, reference-answer decoding or edits outside this review.

The pass covers preparation and scoped annotation only. Fresh optimizer/adapter reset execution, real task-loss numerics, tokenizer census, training/runtime implementation, model quality, budget refresh and paid lifecycle admission were not exercised or approved.

Validation: `validate-autocode-gate.ps1 -Mode Critic -Path experiments/grounded-supervision-20260927/CONTRAST-REVIEW.md` exited0 with `AutoCode Critic gate passed`.
