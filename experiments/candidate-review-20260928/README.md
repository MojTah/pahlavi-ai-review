# Candidate meaning and lineage review

28 September 2026. User requests actual content review, multiple independent passes, preservation of polysemy, parallel agents, and extensive use of Gemini Pro where useful. This follows the unified-corpus integrity audit; it does not rerun that audit as a substitute for linguistic work.

Mode: Classic + Critic. Root owns scripts, packets and integration. Read-only reviewers examined unused Parsig passages, seven S22 examples and six Persian dictionary collections. Gemini completed three inline judgments, but two attachment-based attempts failed; the user then stopped further Gemini use. Root completed the 200-case comparison locally. Original material and all models/evaluations stay unchanged. No paid GPU job, model-weight download, credential change or service-eligibility patch occurred here. Version impact: NONE (review artifacts, no model or training-data release).

`prepare.py` verifies three frozen Kosh inputs, tests uncertainty-marker detection and creates ten packets of 20 comparison cases. The 200 same-form/different-wording cases involve 455 source groups; they are not 200 proven polysemous lemmas. Cases retain complete form groups, published meanings, original XML, source IDs/URLs and catalogue attribution. Six punctuation-only target groups receive explicit holds, not invented meanings. These include Persian `(؟)` and quoted/trailing-punctuation variants missed by the earlier exact placeholder list.

The local preparation is expected to take under10 seconds and10 MB. One writer, no network. Existing output/receipt paths cause refusal. The immutable packet manifest records code/input/output hashes. Per-provider results will be saved separately; prepared packets are not claims of executed Gemini work. Model judgments cannot themselves approve training, clear lineage, certify rights or establish expert correctness.

Only contextual evidence can resolve whether a difference is paraphrase, a different sense/part of speech, historical language variation, uncertainty or an actual source error. Identical spellings do not require identical targets. No source spelling, diacritic, printed translation or uncertainty marker is silently changed.

## Completed checkpoint

- [Content findings](CONTENT-REVIEW.md): 20 selected Parsig passages, all seven S22 teaching pairs, six dictionary collections, and new source-scope/uncertainty findings.
- [Root decisions v2](decisions-v2.tsv): every one of the 200 comparison cases, with a specific reason and qualification. Labels: `P` = paraphrase candidate, `D` = different **published** meanings/roles, `C` = context required, `F` = form/phrase scope review. No label certifies the source's linguistic correctness or authorizes merging.
- [Executed summary v2](review-summary-v2.json): 49 P, 46 D, 103 C, two F; 455 distinct source groups / 471 distinct observations. The F cases involve three compound-scope observations. One observation participates in both POLY195 and POLY196; these are not independent examples.
- The joined, provenance-linked overlay is `resources/local/candidate-review-20260928/root-review-v2.jsonl`. All 200 rows explicitly deny training admission, correctness certification and automatic merging. Six unusable-primary-gloss holds remain in the separate prepared overlay.
- [Gemini evidence](GEMINI-ATTEMPTS.md) separates three actual judgments from failed/unsent attempts and records the Windows cleanup limitation.

Run the read-only check with the shared Python runtime:

```powershell
& '[USER_HOME]\.venvs\codex-science\Scripts\python.exe' -X utf8 experiments/candidate-review-20260928/check_review.py
```

It checks frozen code/input/packet hashes, complete case coverage, exact overlay reproduction, source lineage IDs and unchanged TRAIN2237. It does not turn AI judgments into ground truth. `--write` was used once and refuses to overwrite the frozen review.

The independent critic read all 200 decisions and checked 23 against source glosses/XML. V2 resolves its two linguistic wording findings: POLY192 moves from D to C because دور/عصر can overlap as period/era; POLY059 no longer infers historical politeness from an imperative label. V1 decisions, summary, local overlay and verification-source bytes remain preserved. No original-source bytes or training data were revised.
