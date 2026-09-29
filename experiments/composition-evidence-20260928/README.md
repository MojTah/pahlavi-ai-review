# Additional composition evidence: local acquisition checkpoint

28 September 2026. Exploratory source work after the negative NLLB familiar-passage result. Classic + Critic; root is sole writer. Previous goal turn made progress by completing and auditing a real diagnostic; this turn adds concrete source evidence and resolves why a potential data pool was excluded. No paid run, weights download, Drive access, credential change, corpus admission or benchmark change.

## Seven printed pedagogical pairs

`candidates.jsonl` stages seven whole-clause Pahlavi/Persian examples from Amouzgar and Tafazzoli, *Zaban-e Pahlavi, adabiyat va dastur-e an*, Moin, fourth printing1382 SH, S22. Root visually inspected PDF79–81; candidates are on PDF80–81/printed77–78. Source PDF SHA256 `207aeda5eae48227902f0f208f9b24fd5623627dd4ca589b217268e69596df92`.

These are printed pedagogical pairs, **not established manuscript attestations**. They cover participant assignment, past transitive agreement and perfect constructions. They were not the earlier12 contextual-expression targets. No word meaning or Persian target was invented from model output. Typographic spacing is disclosed; training serialization has not been selected.

Independent source-image reviewer `/root/seen20_blind_a` checked both page images and higher-resolution source renders. All source words/macrons/parentheses and target words matched; it requested restoration of the printed terminal period for S22CLAUSE-004. Root applied that correction. The reviewer confirmed that006 prints `ترا`, not a silently modernized `تو را`. Source and image hashes and PDF/printed page mapping matched. This is image-transcription verification, not philological or use-permission certification.

`check_candidates.py` reuses `scripts/audit_training_corpus.py` normalization and frozen dataset hashes. Its small runnable controls distinguish exact, embedded and unrelated sources. Across original TRAIN2613, DEV402, TEST1019 and qualified TRAIN2237, the seven candidates have **zero exact, contiguous-source or token-similarity≥0.8 flags**. The report emits only source IDs/work IDs and similarities; no held-out answer enters the comparison. It does not detect every variant or establish unknown manuscript/work lineage. All candidates remain `STAGED_NOT_TRAIN_ADMITTED`.

Independent critic `/root/nllb_final_preflight_review` reproduced the screen in memory exactly. It found a missing code/helper hash binding; root added both and regenerated. The critic verified the final bindings and returned PASS. No new review of translation meaning is claimed.

| Final evidence | SHA256 |
|---|---|
| candidates.jsonl | b0525e52490f7fc4f58d0e4cb9808be59fbdaae9aab4ba17845bf672bdfd06b9 |
| check_candidates.py | fd4396182661b4bf124ef539c408cb103f691540d9f891140b697dba9018ef83 |
| source-copy-screen.json | 3d980d3557818c42aba5e419c82fe5d28415c156700ecfb476562fb23ce8dc3c |
| imported audit helper | 9c616eae976683ce16e5428af10b3e4425aa4d72e0f8ac4e33020f5238325abc |

Reproduce with the shared project Python: `python -X utf8 -B experiments/composition-evidence-20260928/check_candidates.py`. Local PDF/images and immutable corpus files are required. The result is a screening record, not an admission decision.

##277 unadmitted translated-field records: reasons recovered

The existing source inventory identified339 outside-heldout records absent from the original TRAIN allocation:277 with Persian fields and62 untranslated headings. Joining the277 IDs against the frozen curation exceptions accounts for every ID. Root independently reproduced the agent's join and retained it in `provenance-recovery.json`.

| First-rejection reason | Rows |
|---|---:|
| Source edition unresolved |110|
| Mixed/possible Avestan source |79|
| Work139 identity requires review |45|
| Translator attribution unresolved plus no usable published pair |28|
| Shared target across distinct sources |13|
| Unsupported source encoding, work225 |2|

These are the parser's first rejection reasons, not complete semantic diagnoses. Source-edition failures occur before target validation, and translator-credit failures before target-empty/script checks. Therefore neither the110 nor28 can be admitted by relaxing a regex. The separate247 quarantined TRAIN rows are not a new unused corpus.

Among110 edition failures,95 are in inscription collections201–224. Work205 contributes32; work222 contributes16. Thirteen further records have code-like titles and mostly sequence-zero IDs, so headings require special attention. Among28 attribution failures, work151 contributes16, work535 nine, and150/537/546 one each. The independently verified source inventory, curation exception file and dataset manifest remain unchanged.

## Bounded actual provenance follow-up

Root inspected the16 attribution-failed work151 records and two other unassigned work151 records that retain the separate shared-target problem. Several are short speech formulas, while others contain fuller comparisons or modal statements; not all18 are independent new clauses. The archived introduction identifies Tafazzoli1379 and Anklesaria1913 bibliographically, but does not resolve the exact missing translator credit/page for each row. Do not inherit nearby attributions automatically.

For205001001 and205002001, the archived source transcriptions lack a trailing edition citation while their Persian targets cite Nasrollahzadeh1398, volume1, pp.208 and213. The archived work205 introduction describes32 inscriptions and refers to that book pp.199–207 for history. This supports a precise book-recovery route, not full source-edition/target identity. Root checked the introduction hashes: work151 `4112f8b744a19ee094587a954f7455336d93f7f5c4e54bade928caff5d471ea0`, work205 `630a955b576c82d54df05efe169def99a83efd5934976e38c4d42220ab3564c9`.

The public [UC Irvine Sasanika Darband page](https://sites.uci.edu/sasanika/darband-wall-inscription/) supplies another numbered transcription witness and selected English translations. The [Kanheri page](https://sites.uci.edu/sasanika/ka%E1%B9%87heri-caves/) names Nasrollahzadeh's2019 private-inscription corpus. These are useful edition/identity leads; an English rendering is not a new Persian target, and different orthography/witnesses must not be silently merged. The relevant book is *کتیبه‌های خصوصی فارسی میانه ساسانی و پساساسانی (گورنوشته، یادبودی)*, volume1, Cyrus Nasrollahzadeh,1398/2019. Its required printed pages were not inspected here.

Research reviewer `/root/finetuning_kb_research` found no already verified new manuscript-attested Persian parallel corpus in the supplied books. Asefi's Berk.25 edition, S23 PDF8/printed9, has a useful obligation/transfer passage with English translation; a Persian target would require independent qualification. S26 is English Nyberg under a Persian wrapper; S28's Persian follows an Arabic version with different structure. These are not mechanically usable direct Persian parallel sets.

## User steering: finish the full data resource before training

The user clarified MacKenzie's *Concise Pahlavi Dictionary* and requested the largest reliable available training set before another run. Follow [DATASET-READINESS.md](../../DATASET-READINESS.md). These seven examples are one acquisition result, not a reason to restart training. Dictionary acquisition and the unresolved provenance pools now belong in one consolidated readiness decision; no additional per-source training cycle.

Lead agent/request id: /root
Critic agent/request id: /root/nllb_final_preflight_review
Critic model and reasoning effort: inherited GPT-6 Astra and parent reasoning effort
Independent from lead: yes
Critic verdict: pass
Evidence reviewed: Frozen source-copy screen, candidate/source bindings, first-rejection provenance join and current split boundaries. Separate image reviewer checked printed examples.
Verification evidence: Independent exact replay of seven candidate screens, final code/helper/candidate hash verification, all277 exception IDs accounted for; root separately reproduced the provenance join. Scope excludes linguistic certification and training admission.
