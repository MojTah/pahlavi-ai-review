# Complete auxiliary-record review — 2026-09-29

All **307 released auxiliary records** were individually read with their supplied source, target and context: 240 pedagogy-fa, 57 documentary-en, 6 inscription-fa and 4 edition-spans-en. This extends the earlier 21-record spot check. It is an AI/provisional source-fidelity review, **not expert linguistic certification**, independent manuscript decipherment, or proof that every possible failure is absent.

## Outcome

No unexplained extraction/alignment mismatch was found in the released fields. All input/source hashes checked agree with their recorded hashes. Five differences from intermediate/raw text are existing, explicitly declared derivations; all five reconcile exactly and were reviewed rather than silently normalized away. No source, frozen record, reference, benchmark, training artifact or merit result was changed. No training/inference or network operation was run.

One semantic interpretation question remains for the MP2100 greeting. It is **not a confirmed translation defect** and does not justify inventing or replacing its target. Source uncertainty remains binding in the documentary examples listed below. This review does not turn source-bound targets into universally complete, context-free translation gold.

## Coverage and evidence

| Released set | Records read | Source evidence actually checked | Mechanical check |
|---|---:|---|---|
| pedagogy-fa | 240 | All 18 relevant S22 page images: PDF 70–77 and 79–88, printed pages 67–74 and 76–85. Every released form/gloss and context was compared with its page; pronoun/paradigm columns, tense, role, negation, variant bundles and numerical values checked. | Source PDF hash, origin hash and source/target transcription equality; three declared target derivations separately reconciled. Visual checking is not represented as automated OCR proof. |
| documentary-en | 57 | Raw archived scholarly TEI and Invisible East JSON/HTML, across 43 distinct raw files. Every released bilingual record was read; raw layers reconstructed independently from XML line breaks/inline uncertainty or original HTML list items. | Exact source/target reconstruction at declared blocks, lines and bounded substrings; two declared English spelling repairs separately reconciled. |
| inscription-fa | 6 | Kanheri article PDF page images 10–14. All six released spans checked, including three distinct occurrences of the repeated invocation, the arrival scope, dated arrival, and patronymic name. | PDF/origin hashes and exact parent character spans, with whitespace normalization only. |
| edition-spans-en | 4 | Asefi actual PDF text and page images 8, 14, 20 and 23. Every selected span checked for source/target scope, amounts, dates, receipt direction and omitted adjacent damaged matter. | PDF/origin hashes and exact parent character spans, with whitespace normalization only. |

**27 PDF page images were inspected in this pass.** All required archived inputs and those images were accessible. The documentary TEI/HTML is a scholarly edition, not an original manuscript photograph. No independent palaeographic decipherment was performed; this is an explicit evidence boundary for every documentary row, not a claim that the manuscripts are unavailable everywhere. No new OCR/rendering or source download was needed.

The metadata-only `auxiliary-audit.json` contains all 307 unique IDs, canonical and learning hashes, raw paths/hashes, precise source and target locators, mechanical outcomes, evidence levels, reservations, and accessibility boundaries. It does not duplicate the corpus text. `auxiliary_check.py` reproduces the mechanical part only; `record_read` and semantic flags document this completed review and are not inferred by that script.

## Five reconciled existing derivations

| Record | Difference | Review outcome |
|---|---|---|
| `openampd:MP0046:full` | Raw English `transction` becomes `transaction`. | Existing declared spelling repair; exactly one occurrence; amounts, gap markup and negated further demand are unchanged. |
| `openampd:MP0416:full` | Raw English `Spandaimad` becomes `Spandarmad`. | Existing declared repair agrees with the raw Pahlavi named day; date, damaged year and quantities preserved. |
| `S22GRAM-043` | Removes the table's list-ending wording from the lexical target. | PDF 73 / printed 70 distinguishes the list ending from the form's gloss; complete original remains in its parent. |
| `S22GRAM-045` | Restores the missing letter in the extracted Persian comparative spelling. | Visible PDF 73 gloss supports the released spelling; this repairs transcription, not the book's interpretation. |
| `S22GRAM-046` | Same repair for the superlative. | Visible PDF 73 gloss supports the released spelling. |

## Semantic reservations, not automatic data corrections

- **`openampd:MP2100:greeting` — interpretation pending.** Both released layers exactly match raw TEI blocks `MP2100_trc-p1` and `MP2100_trans-p1`, lines 4–6. The source contains `hamē`; the English greeting has no separately explicit temporal counterpart. Greetings may convey scope idiomatically, so missing one English word is not sufficient to establish an error. The narrow question is whether full temporal scope is conveyed by this published greeting when used as an exact semantic reference. No literal target is proposed, and no automatic exclusion is recommended. Root/qualified reviewer should classify any gold-use restriction after independent inspection. Raw file: `sources/local/public-texts-2026-09-20/berkeley/raw/644c70757410c66369455f60b1c8c33d3e1bfb81d73ed3d576084ac57ee093de.source`; SHA-256 `1a47953b3d336cf4d746e82ae9ee7cbbd8b2f97dd9fa596bac8cbe1f2083c126`.
- **`iedc:IEDC1262:folio0`**: the recipient is visibly restored/questioned in source; its English rendering does not repeat the same question marker. **`iedc:IEDC1265:folio0`**: competing reading/meaning alternatives survive, but the uncertainty on the final name is not mirrored identically in English. **`iedc:IEDC1040:folio0`**: the source questions its measure term while the corresponding English term lacks the same marker. **`openampd:MP6003:full`**: source unclear letters and target questions are not symmetrically annotated. These reproduce the archives; they are not fresh pipeline losses. Their source-side uncertainty must accompany them, and their uncertain readings must not be described as resolved.
- Longer legal/administrative interpretations in **MP1024**, **MP1023**, **MP2150** and **MP2561** remain philological judgments of the editions. The relevant released IDs are in the ledger. Source correspondence, retained quantities and broad participant/action scope were reviewed, but difficult technical terms and syntactic interpretations were not independently certified.

## Specific high-risk checks

S22 source homographs with distinct paradigm persons remain conditioned by their row contexts. Direct/oblique pronouns, the agent/patient distinction in past transitives, passive teaching readings, optional parentheses, editorial zero auxiliary notation, imperative/prohibitive contrasts and multiple local senses remain explicit. Lexical and grammatical forms are not relabeled as independent attested sentences. **The previous kū/ka omission claim remains withdrawn:** PDF 75 separates the next ka entry; no extra kū gloss was inferred.

MP0603's final source word is **āwišt** following a newline. It is not a lexical nāwišt; there is no demonstrated negation reversal. MP0437's split written numeral is not treated as an automatic quantity error. Documentary numbers, fractions, dates, named roles and marked damage were checked with whole-passage context, allowing published explanatory translations and reordered line groupings rather than requiring one-to-one line or word matching.

Kanheri's three invocation occurrences share wording but retain distinct witness IDs. They do not become three novel phrase types or independent evidence for a model's generalization. The Article 01 parent date discrepancy is outside the released opening/arrival spans. Article 02's released dated arrival agrees with its own source and Persian date. The Article 06 patronymic is supported by its own printed pairing.

S23 span boundaries exclude the neighboring parent problems: the Berk.25 selected receipt transaction begins after its damaged agent; Berlin26 is explicitly a temporal fragment and removes footnote numerals from dates; Berk.11 exports the receipt clause without the parent quantity disagreement; Berk.122 exports a period modifier without the neighboring disputed animal count. This validates selected scope only, not the omitted parent material.

## Reproduction and limits

Run the checker locally with the configured science Python. It reads frozen/source inputs and writes only the allowed metadata ledger. It independently reconstructs documentary text and checks declared transformations; a script rerun is **not** a fresh semantic review. Metadata flags distinguish observed raw fidelity, declared derivation, interpretation pending and unresolved source readings. This review deliberately makes no all-errors-found, expert-approved, source-rights clearance, training-readiness or performance claim.

## Frozen input hashes

- `resources/local/data-qualification-20260928/ready-v1/pedagogy-fa.jsonl` — `d96d95610ac354222029d30ae0252425df57859ab8f23bfd14d68a6b71a8edd6`
- `resources/local/data-qualification-20260928/ready-v1/documentary-en.jsonl` — `d604e2b66e8c38de18b5e0675fbc9a58f739efd6c845d3cf0a3661542796924b`
- `resources/local/data-qualification-20260928/ready-v1/inscription-fa.jsonl` — `c56c346750d23910a96ab6be3dab6f1bfc153bfa9286c5517581fa8dbe6de6cc`
- `resources/local/data-qualification-20260928/ready-v1/edition-spans-en.jsonl` — `62bed1c4712b464326c82e2dc0e7bb2cdbd754a88a23471ef7208d05a1ca2bf1`

Report and ledger contain brief examples and metadata only; the source corpus remains in its original locations.
