# TRAIN-example-assisted development diagnostic

Status: HOLD FOR FULL TRAIN QUALITY AUDIT. The user subsequently required the entire 2,484-row training set to be checked before use. Complete that local audit and quarantine unresolved rows before admitting even this assisted condition. Archive checks and AI judgments cannot establish 100% linguistic correctness. Original data remain immutable.

PREPARATION ONLY. No new cloud job admitted. Classic + Critic; root is the single execution owner. The next experiment generates at most 24 new outputs from the existing trained model and compares them with cached D3 from the completed instruction diagnostic. No additional training or laptop model download.

## Question and limits

Does showing authentic, source-selected TRAIN passages and their published Persian translations help the trained model use known meanings and constructions? This is an exploratory response to the previous DEV failures. It measures assisted translation, not improved model weights or independent test accuracy. No source-selected word is asserted to have an independently verified isolated-word gloss.

Keep the frozen 24 DEV inputs, 15 whole-translation cases and nine constrained cases. Keep the same model revision, step-312 adapter, BF16 inference, tokenizer, greedy decoding, seed 42, thinking-disabled mode, fresh context, generation ceilings and D3 system instruction. Append only clearly delimited TRAIN evidence to the user message. Tell the model that these are contextual examples, their senses may differ, and they do not establish unknown readings. Output remains a translation without commentary. Final message bytes and runner identity must be frozen before launch.

Reference answers, assessment constraints and DEV/TEST/PAL-REF answer content remain outside inference. Evidence uses only the actual TRAIN payload, whose SHA256 is `844a5b64d43a423b69d5989527a53273290a43be15c399056c979f5abb0678a1`. DEV source-only input SHA256 is `06ac58310bf67767fae4124d8e935c808d15debcd8daebce07b583937cd97182`. Do not use the draft dictionary or grammar files wholesale.

The contrast estimates the complete assistance package, including its caution instruction. It cannot isolate the examples' effect from that instruction. No extra control arm is needed for this exploratory decision.

## Source-only selection, chosen before assisted outputs

Two offline rules were compared on evidence coverage, without DEV answers or outputs. Initial weighted-Jaccard ranking required two rare shared terms; it selected 61 attachments, supported 22 cases, covered 125/291 attested rare case-terms and included 11 attachments adding no rare term. It missed attested terms in cases 002 and 005. The selected greedy rule covers 165/291 (53.7% IDF-weighted coverage), selects 69 attachments across all 24 cases and has zero attachments adding no rare term. Coverage increases in 19 cases and stays unchanged in five. Another 145 rare case-terms are absent from the concise inventory. These measurements concern available evidence, not translation quality. No further retrieval-rule search is planned for this trial.

1. Tokenize by Unicode NFC, casefold, whitespace split, then repeatedly strip edge Unicode punctuation. Preserve internal hyphens, clitics and vowel marks; do not stem or generate synonyms.
2. Group TRAIN rows by normalized source-token sequence. Normalize targets with NFC, casefold and whitespace collapse. Exclude every group with multiple distinct targets; otherwise keep the lexicographically smallest full TRAIN ID. Six conflicting groups contain 13 rows, including 151001001, 151019001 and 151027001. This is conservative ambiguity exclusion, not correction of their translations.
3. Keep whole examples with 3–60 source tokens and at most 320 existing TRAIN input tokens. Never truncate either side. Expected inventory: 2,251 rows across 74 works. Stored training-token counts are only a size proxy; measure actual final prompts separately.
4. Use eligible-TRAIN document frequency. For N rows, IDF is `1 + ln((N+1)/(df+1))`; a rare term has `df <= 0.05*N`. Unknown query terms have df zero but cannot be supplied by an example.
5. Exclude a candidate if the complete query token sequence occurs contiguously within it, token-set Jaccard is at least 0.8, or `SequenceMatcher(..., autojunk=False).ratio()` is at least 0.8. These are mechanical screens, not proof against semantic parallels.
6. Greedily choose at most three examples, at most one per TRAIN work. Each must add a previously uncovered rare query term. Rank by summed IDF of newly covered terms, then IDF-weighted Jaccard, then full TRAIN ID. Sum sorted terms and round both numeric scores to 12 decimals. Stop when no candidate adds a new rare term.
7. Preserve every case, including an empty evidence list if no support qualifies. Never substitute unrelated examples. Retain unmodified source/target strings, record/work IDs, credit and revision for each selected example.

Record all selected witnesses, exclusions, source hashes, coverage, unknown terms and actual prompt lengths. The source-only dry run predicts 22 cases with three examples, one with two and one with one. Work 151 contributes 18/69 attachments; this is not 69 independent evidence units. A bounded source/witness audit must check potentially parallel Manichaean passages (especially works 503/514 versus DEV work 517) before admission. Any exclusion must be based on documented source overlap or uncertainty, never model performance; record it and recompute once under the same rule.

Audit all selected attachments and any replacements, not only works 503/514: verify exact TRAIN membership, unaltered payload, publication locator where available, and alignment; screen the same passage, parallel recension and answer-equivalent content under other work IDs. Exclude unresolved provenance or parallel-passage concerns before generation. Ordinary polysemy alone is not grounds for exclusion. Do not infer a clean witness solely from different work IDs or a low mechanical similarity score.

## Comparison and next decision

Generate only one assisted condition, with at most 24 first attempts. Reuse the 24 original D3 outputs; do not rerun the four previous conditions. Mix assisted outputs and cached D3 into opaque, randomized blind review packets, keeping both outputs for a case with the same reviewer and the frozen reference qualifications. Fresh paired reviews of cached D3 may differ from previous judgments; preserve and disclose that variability rather than rewriting the completed diagnostic.

Freeze packet fields to source, qualified reference/constraints, opaque review ID and output text/hash. Omit retrieval examples, condition labels, prompt and runtime metadata. Apply the clarified accepted-category convention equally: satisfactory uncertainty handling is `pass`, including where no material source uncertainty exists. Preserve all original result files.

Report paired accepted/meaning-error/critical-error/uncertain counts for the same 15 whole cases, per-work behavior, and separate supported-span/uncertainty handling on the nine constrained cases. Keep failed or incomplete attempts in the record. More acceptance with no increase in critical errors and no substantive regression of accepted cases supports further assisted development; otherwise report the tradeoff or lack of improvement. This small exploratory sample cannot qualify deployment or prove decipherment of unknown words. Freeze the selected approach before any later use of the unchanged PAL-REF benchmark.

New unsupported certainty on the nine constrained cases also counts as a tradeoff, even if acceptance improves on the fifteen whole cases.

## Execution readiness still required

Root will reuse the demonstrated Linux runtime, cloud-only base/adapter recovery, persistent HF bucket and bounded shutdown controller. One isolated helper prepares the evidence; a separate critic checks the real artifact/runner path. No new dependencies or retrieval framework. Validate original TRAIN identity, split separation, deterministic selection, zero-support/conflict/near-copy behavior, exact payload integrity, longest actual prompt and failure preservation before launch.

The user-authorized cumulative limit is USD 25; the latest conservative total is USD 7.1103. This plan is not a new allocation or automatic top-up. Set the next job's concrete timeout and worst-case cumulative cost from measured setup/generation data, verify rate/funding and absence of active jobs, then freeze its admission record. All setup, export and shutdown count. No automatic retry, duplicate job, follow-on training or local model download.

Independent methodological reviewer `/root/philology_evaluation_review` passed the exploratory design and marked launch readiness partial. Its required witness, blind-packet and uncertainty safeguards are incorporated above. This review does not validate unreviewed code or admit a cloud job.

## Completed preparation checkpoint

The real source-only builder reproduced 69 attachments, and independent technical review passed seven tests plus exact artifact regeneration. All 69 query–witness pairings and 66 distinct witnesses received archive-based identity/alignment/overlap review. One concrete exclusion was found: case 016, TRAIN 134004028 contains Persian words belonging to following paragraph 134004029. Preserve the candidate unchanged and omit that attachment without repairing text or replacing it. This documented pre-generation exclusion supersedes the possible recomputation step above; there is no automatic replacement.

`admitted-evidence/evidence.jsonl` contains the resulting 68 attachments across all 24 cases, with 164/291 attested rare case-terms covered. SHA256: `6a22bd61461916199c0637fbab82f0a420b61f2abd4d8e88306a1bae3c434a7d`. The original 69-attachment candidate and its generator remain reproducible. The admitted audit records the exact omission and coverage recomputation. No other witness exclusion was identified. These are AI/archive checks, not edition collation or specialist-certified senses; case 005 still has no supplied example for `frārōnīh`.

No paid run follows automatically from evidence admission. Remaining work is the smallest reuse of the existing cloud inference path, exact prompts/token lengths, focused failure checks, independent runtime review and concrete budget admission. The completed diagnostic checkpoint is Git `60f35b5`; all GPUs remain off during this preparation.
