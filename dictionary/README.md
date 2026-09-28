# Corpus-based Pahlavi dictionary

**Deferred pending Mojtaba’s requested discussion.** Earlier objective: study every text record currently exposed by Parsig Database and build an explained Middle Persian–Farsi–English dictionary from that evidence. Completeness will be measured against the recorded site snapshot, not claimed for the whole historical language.

This extends the [knowledge base](../README.md). It does not train or permanently change the assistant's model. Future work can retrieve these files, compare examples and apply the recorded analyses.

Current output: [16 explained entries](entries.json) with Farsi/English senses, attested forms, source sections, uncertainty and reading prompts. They draw on records 107, 119 and 120; the new [Baxt-āfrīd study](../kb/baxt-afrid-study.md) documents the latter. They are source-assisted drafts and have not been independently reviewed.

## What an entry must contain

- Headword, language and part of speech, with homographs kept separate when the evidence requires it.
- Farsi and English senses in the attested context, distinguishing published glosses from our explanations.
- Observed inflected forms, compounds, derivational relationships and spelling alternatives.
- Edition, text, section and occurrence references; access date and source/translator credits.
- Uncertainty, editorial corrections, damaged text and unresolved alternatives.
- An explanation of why the sense and grammatical interpretation fit, plus a short reading check.

Keep the exact source field alongside any normalized lookup key. Do not erase brackets, vowel length, heterograms, clitics or manuscript distinctions. Six site records carry mixed Middle Persian–Parthian labels; do not merge their language identities.

## Evidence stages

| Stage | What it establishes |
|---|---|
| Inventoried | A record or form exists in the observed source |
| Collected | A local source copy has provenance and a checksum |
| Read | The displayed passage and its available notes/translations were examined |
| Analysed | A sense or construction was explained against its context, with alternatives recorded |
| Checked | A reading exercise or comparison was completed and corrections recorded |
| Expert reviewed | A qualified independent reviewer approved the particular entry; not yet available |

Collection, indexing and duplicate removal can be mechanical. They do not promote an item to analysed or checked. Dictionary lookups and self-check exercises do not establish blind translation accuracy.

## Current scope

Dictionary development is deferred. The 16 draft entries were prepared before Mojtaba narrowed the task to data collection. They remain unreviewed study material.

Parsig text acquisition subsequently completed for all 126 records, with separate provenance-preserving data exports. See [the current collection guide](../data/README.md) and [acquisition log](../downloads/collection-run.md). All source records are collected; most have not been read or analysed. No full per-word annotation coverage, training or translator implementation is claimed.
