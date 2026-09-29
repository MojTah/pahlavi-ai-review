# Kosh: all visible dictionaries, bounded source acquisition

28 September2026. User explicitly requests all dictionaries on the opened MPCD/Kosh page and a before/after account of genuinely new training material. Existing TRAIN2237, all evaluation partitions and cloud spending remain unchanged. Acquisition goes into a separate ignored raw archive, not training.

**Current ownership:** the user subsequently assigned further site downloads to another chat and directed this chat to focus fully on clean, correct data. Do not rerun `acquire.py` here. Use the frozen three-collection snapshot for local qualification; accept later deliveries only with their own receipts and explicit dataset version.

## Readiness and execution scope

- One acquisition execution/repair owner: root. Research/audit agents are report-only; a separate isolated writer produced only the local census script. Classic + Critic; no new environment or dependency for acquisition/census.
- Exact command: shared `codex-science` Python runs `experiments/kosh-acquisition-20260928/acquire.py`; `--self-check` performs no network work.
- The31 collection names come from live `https://www.mpcorpus.org/kosh/`. REST structure and `size` are publicly documented. The user's all-selected page displayed only8 result tables at observation, not proof that only8 collections exist.
- Reuse `scripts/collect_public_texts.py` for rate-limited, hash-verified acquisition/cache. Write only `sources/local/public-texts-2026-09-20/kosh-all-dictionaries-20260928/` plus this experiment's records. No credentials, proxy changes, uploads, deletion or paid server.
- Real canary: `acpv1_7`, wildcard/trc/size20, returned20 structured entries. Size10000 returned2602 unique IDs and2602 XML fields,937594 bytes. This proves one bulk request, not uniform collection behavior.
- Expected duration: minutes. At most31 new requests, sequential, existing rate limiter. Per-response bound10MB; stop admitting at600 seconds or100MB cumulative (one10MB response can cross that admission threshold). Existing35-second socket timeout applies; root monitors and stops stalled reads. No automatic retries; stop on401/403/429 or three consecutive failure/empty results.
- Hash-check cached identities before reuse. Preserve successful bodies and failure receipts; the existing helper does not retain incomplete/oversize bodies. Safe stop between requests; resume reuses successful files and does not silently retry failures. Historical datasets are untouched. Limits above control request admission, not a strict network-byte or wall-clock cutoff during a read.
- Done: recorded disposition per collection or explicit stop reason, exact counts/hashes and limitations. Below10000 is not independent completeness proof; empty is unconfirmed;10000 is capped.

## Required before/after report

Separate downloaded entries, exact duplicates, quarantined/held-out work-derived content, newly qualified lexical supervision, and new attested whole-sentence translations. Website/PDF editions share lineage. Unchanged2237 historical pairs are the baseline; raw totals are never called admitted training growth. Meaning/form relationships must come from full XML, not the lossy simplified sense field.

## Executed acquisition and novelty census

**PARTIAL, stopped on access denial.** [Acquisition receipts](acquisition-report.json) preserve three successful collections (1122545 bytes), CPD HTTP500, then CPD_DE HTTP403 at12:41:15 UTC. The remaining26 collections were not requested. No automatic retry or access workaround followed. The requested catalogue has31 collections; three successes do not establish that the whole catalogue or those print editions have been captured completely.

`novelty.py --confirmed-acquisition-finished` ran locally after acquisition exited. [Census output](novelty-summary.json) pins its code, normalization helper, acquisition report and every successful raw input. It checks only the frozen TRAIN source text; no DEV/TEST answers are read.

| Downloaded collection | Raw entries | Unique full transcription values | Found as a contiguous TRAIN token sequence | Not found by that comparison |
|---|---:|---:|---:|---:|
| Cantera Pahlavi Vidēvdād1–7 (`acpv1_7`) |2602 |1653 |637 |1016 |
| Afnan philosophical lexicon (`afnan`) |324 |315 |30 |285 |
| Ardāwirāznāmag (`awn`) |366 |506 |219 |287 |
| Union, deduplicating transcription values across collections |3292 |2315 |772 |1543 |

The per-collection unique-form totals do not sum to the union because some forms recur across dictionaries. There are3435 raw transcription values (some entries contain several), collapsing to2315 normalized full values. That is1120 repeated-value occurrences, not1120 useless entries: identical forms can have different senses or citations. All3292 XML fields parsed; none are byte-identical. Exact XML includes IDs/formatting, so this does **not** prove absence of semantic duplicates or shared source lineage.

The1543 unmatched values are about66.7% of the2315 form union, not a percentage increase in the training set. Full comma/parenthesis/variant expressions are retained rather than guessed into separate words. Spelling systems, grouped forms, language and source errors can inflate apparent novelty. This is an orthographic comparison, not a lemma/sense or translation-quality result.

| Actual qualified dataset change from this acquisition | Before | After | Increase |
|---|---:|---:|---:|
| Historical Pahlavi–Persian pairs |2237 |2237 |0 |
| Newly qualified lexical pairs |0 |0 |0 |
| Newly qualified attested whole-sentence pairs |0 |0 |0 |

No semantic admission review has yet cleared these sources; zero admission is not a conclusion that the material is unusable. Samples show German lexical meanings in `acpv1_7`, English in `afnan`/`awn`, and citations/variant groupings that need preservation. They are not automatically Persian targets. Structured website capture avoids running our own OCR, but does not certify the original digitization or source scholarship. In particular, full XML must preserve the form/sense relation and quoted contexts; parsing successfully proves structure only.

Every collection remains lineage-unresolved. Collection-name flags identify `hkr`, `sns`, `wz` and related `mz` for conservative held-out investigation; the other names are not cleared by absence of a flag. Next, qualify the acquired material by language, edition/work, meaning and task type, while reporting the unresolved catalogue access gap. Preserve the original TRAIN2237 and fixed benchmark. A new model run remains gated by the consolidated dataset freeze.

## Alternate institutional export research

The official [mp-corpus-parser README at a pinned revision](https://github.com/middlepersian/mp-corpus-parser/blob/ed1a47eb9224fea017ceaec592e5d3410326fcbd/README.md) documents UTF-8 CSV/TSV token annotations (`id`, transcription, lemma, POS/features, dependency fields, meaning). Its notebook reads an author's local `export_files`; the research did not establish a public corpus download URL or a required login. The [2025 institutional poster](https://dhday7.ub.rub.de/poster_2025MPCD.html) describes roughly800000 tokens; that is not a count downloaded here or a corpus of Persian sentence pairs. No alternative complete public Kosh dictionary dump was identified. `/root/finetuning_kb_research` performed this read-only route check; no credentials, contact, download retries or invented API were used.

## Verification and independent review

Subsequent local quality audits found20 placeholder meanings in ACP and9 missing AWN meanings, plus grouped forms that must not be flattened. They also found857 repeated form-group/meaning rows within collections, despite zero byte-identical XML strings. The [bounded cleaning handoff](QUALITY-HANDOFF.md) preserves exact findings, schemas, provenance limits and the user's proposed Gemini delegation. This is preparation, not a claim that Gemini has run or that cleaning/admission is complete.

Acquisition SHA256: `d42145e42529421003887abda4bb82ef8434d1675e228cf337992ff4d04238c8`; reused fetch helper: `30d9e56dcb98f9d84c84e9f180d3c75b34f635d3539aa572f9ed5bb6d56b2da0`.

Census SHA256: `bc3ccdaf1e76d831400fbc9b1f60ebf023ed1f5ac3437f39e01d36c3e8984f29`; normalization helper: `9c616eae976683ce16e5428af10b3e4425aa4d72e0f8ac4e33020f5238325abc`.

Lead agent/request id: /root
Implementer agent/request id: /root/nllb_source_method (census only; root owns acquisition and integration)
Critic agent/request id: /root/nllb_final_preflight_review
Critic model and reasoning effort: inherited GPT-6 Astra and parent reasoning effort
Independent from lead: yes
Critic verdict: pass
Evidence reviewed: Acquisition scope, stop/size/schema gates, receipts, path/hash checks, normalization denominator, exact-XML semantics, held-out answer isolation and zero training admission.
Verification evidence: Both runnable self-checks passed. Critic-required over-cap rejection and bounded-limit wording were corrected before acquisition. Root executed acquisition and the full census; the independent critic executed only offline self-checks and did not independently recompute the live totals. PASS covers bounded acquisition and mechanical census, not completeness, linguistic quality or data readiness.
