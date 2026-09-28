# Pahlavi knowledge base and source collection

Version **0.9.0** · Source snapshot **20 September 2026** · Study review **24 September 2026** · Fixed benchmark **26 September 2026 UTC**

**New: [PAL-REF v1 — fixed translation benchmark](benchmarks/pal-reference-v1/README_FA.md).** Forty passages from five held-out works preserve published Pahlavi transcription, Persian and English references. There are 80 primary forward-translation cases and 80 separately reported reverse cases. References, source evidence, meaning-review criteria and run conditions are frozen by SHA-256 and Git. This is a published-reference benchmark with consistency screening, not fresh independent specialist certification. No model was run or given a new quality score during its construction. See the [validation record](benchmarks/VALIDATION_20260926.md).

**Current result: source-assisted paragraph reading covers all 126 records / 334 chapters / 4,507 units in the saved Parsig snapshot.** Read the [review report](kb/review-2026-09-24.md), [study status](kb/study-status.md) and [exact coverage ledger](sources/parsig-complete-study-2026-09-24.json). This covers the saved transcriptions, offered translation/commentary layers and notes, including incomplete and nontranslation fields. It is not a claim of complete Pahlavi mastery or expert-validated translation accuracy.

The review corrects grammar, vocabulary and script guidance, adds connected and short-text studies, and records unit-level edition/translation disagreements. The 45-entry glossary and 16 contextual dictionary entries remain limited study aids. Other archives and whole dictionaries are not fully studied. Translator implementation and training live in the separate Pahlavi Translator project; this repository now supplies the fixed reference benchmark.

For downloaded data, use the [collection guide](data/README.md), [historical collection-status snapshot](data/collection-status.json) and [document index](data/document-index.jsonl). Raw Parsig counts include 4,445 nonempty Farsi fields and 916 English / 843 French translation units; content review shows why field presence is not usable-pair coverage. Source originals, hashes and credits are preserved locally, outside Git. A Git checkout alone does not contain the downloaded corpus.

## Start here

For the next model comparisons, see the [evidence-based testing strategy (Persian)](plans/translation-test-strategy-20260926-fa.md). It reconciles all seven main project chats, the research package and the later experiment outcomes. The proposed first comparison is Gemma 3 12B/27B with and without verified evidence; no new run is admitted by that report.

| Need | Reference |
|---|---|
| Read the live site's conventions and first text studies | [Parsig live study](kb/parsig-live-study.md) · [126-record inventory](sources/parsig-live-inventory.json) |
| Use the five supplied PDFs and check what was read | [Supplied-PDF study](kb/supplied-pdf-study.md) |
| Read administrative clauses in Farsi and English | [Documentary readings and quantity checks](kb/documentary-readings.md) |
| Find credited Python tools and supporting resources | [Resource library](resources/README.md) · [Credits](CREDITS.md) |
| Follow the requested Parsig Database study | [Coverage and findings](kb/parsig-database.md) |
| See a passage translated into both target languages | [Bilingual study reading](kb/bilingual-reading.md) |
| Preserve requirements for the eventual translator | [Translation study plan](kb/translation-study.md) |
| Understand what “Pahlavi” means | [Language and corpus](kb/language-and-corpus.md) |
| Separate written signs from spoken words | [Writing system](kb/writing-system.md) |
| Parse a sentence | [Grammar](kb/grammar.md) |
| Look up 45 contextual vocabulary entries | [Glossary](kb/glossary.md) |
| See the method applied | [Worked readings](kb/worked-readings.md) |
| Practise and check understanding | [Twelve exercises](kb/practice.md) |
| Translate a new passage carefully | [Reading method](kb/reading-method.md) |
| Find the underlying scholarship | [Sources and access status](kb/sources.md) |
| See limitations and the next study sequence | [Study status](kb/study-status.md) |

The notes distinguish **source-supported description**, **my analysis**, and **constructed practice**. Transcriptions preserve meaningful vowel marks. Check a reading against its witness and edition before scholarly or public reuse.

This folder is the durable reference. A future task should begin with this index and the study status. Search it with an editor's folder search; both “Pahlavi” and “Middle Persian” are useful terms.
