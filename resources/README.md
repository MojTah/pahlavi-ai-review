# Credited resource library

Checked **20 September 2026**. These resources support continued study and the eventual Pahlavi-to-Farsi-and-English translator. Entries describe possible uses; they are not an adopted software stack. No toolbox was installed or executed for this catalog.

Author credits: [CREDITS.md](../CREDITS.md). Reusable citations: [references.bib](references.bib). Exact repository versions and downloaded-file hashes: [manifest.json](manifest.json). The [main source register](../kb/sources.md) covers the language scholarship.

Twenty selected reference files are retained locally under `resources/local/`, including documentation, license notices and the ParsiPy study bundle. These local copies are excluded from Git; the tracked manifest records their exact public source URLs and hashes. The catalog, bibliography and six license notices are included in Git.

A further local font reference is retained separately: [Parsig Ham-dibirih font record](parsig-font.json). Its metadata and checksum are recorded; no redistribution license or validated Unicode conversion is established.

## Python tools

| Resource | Language / role | Repository license | Study status |
|---|---|---|---|
| [ParsiPy](https://github.com/openscilab/parsipy) | Directly relevant to Pahlavi: tokenization, stem analysis, POS tagging, reading-to-spelling conversion | MIT | Full paper read; selected implementation and lexical data inspected |
| [Hazm](https://github.com/roshan-research/hazm) | Modern Farsi normalization, segmentation, lemmatization and parsing | MIT | README features/examples and license consulted |
| [DadmaTools](https://github.com/Dadmatech/DadmaTools) | Modern Farsi processing, including ezafe detection and spelling tools | Apache-2.0 | README task/normalizer documentation, license, paper abstract and citation consulted |
| [Stanza](https://github.com/stanfordnlp/stanza) | Multilingual analysis; documented Farsi and English models | Apache-2.0 | README, license, model documentation and paper citation consulted |
| [SentencePiece](https://github.com/google/sentencepiece) | General tokenization with a Python interface | Apache-2.0 | README overview and license; paper abstract/citation consulted |
| [SacreBLEU](https://github.com/mjpost/sacrebleu) | Reproducible translation evaluation | Apache-2.0 | README features and license; paper citation consulted |

The licenses listed apply to the inspected repositories. Separately obtained models, corpora and manuscript images may have their own terms. Full license notices are retained in [licenses/](licenses/). The machine record preserves GitHub's unclassified Stanza license result alongside the explicit Apache-2.0 statement in its actual license file.

### ParsiPy

**Credit:** OpenSciLab and contributors; research by Farhan Farsi, Parnian Fazel, Sepand Haghighi, Sadra Sabouri, Farzaneh Goshtasb, Nadia Hajipour, Ehsaneddin Asgari and Hossein Sameti. [Paper](https://aclanthology.org/2025.alp-1.17/)

**Use in our study:** examine spelling alternatives, heterographic correspondences and analytical conventions. A retained local reference bundle contains the inspected modules and four data files, with the upstream README and MIT notice. It is a selected snapshot, not the complete software or Parsig Database.

**Limit:** the inspected tool begins from a linguistic reading. It does not solve manuscript recognition or translation into either target language. See our [detailed audit and learning notes](../kb/parsig-database.md), including source-code/documentation differences and unverified annotations.

### Hazm

**Credit:** Alireza Nourian, Roshan Research and contributors. The license retains the 2013 Alireza Nourian copyright notice. [Documentation](https://www.roshan-ai.ir/hazm/)

**Possible use:** process modern Farsi reference translations and examine word boundaries and verbal forms. The README describes text normalization, tokenization, lemmatization, POS tagging and dependency parsing.

**Study implication:** preserve the original translation before normalization. Changes to diacritics, character forms and half-spaces belong in a separate derived field. A modern Farsi normalizer should not be applied indiscriminately to Pahlavi transliterations. Current README says Python 3.12+; runtime compatibility has not been tested here.

### DadmaTools

**Credit:** Dadmatech and contributors. The V2 paper credits Sadegh Jafari, Farhan Farsi, Navid Ebrahimi, Mohamad Bagher Sajadi and Sauleh Eetemadi. [V2 paper](https://aclanthology.org/2025.abjadnlp-1.5/)

**Possible use:** compare Farsi analyses, especially segmentation and ezafe, and study its configurable normalization. The README exposes individual processing tasks; the paper describes shared-model adapters.

**Study implication:** automatic spell correction or informal-to-formal rewriting can change an editor's wording. Keep such output distinct from the source translation. Modern Farsi ezafe detection does not establish the analysis of Middle Persian `ī`. Only the paper abstract and citation were read in this resource pass; the full V2 paper remains queued.

### Stanza

**Credit:** Stanford NLP Group and contributors. The system paper authors are Peng Qi, Yuhao Zhang, Yuhui Zhang, Jason Bolton and Christopher D. Manning. [Paper](https://aclanthology.org/2020.acl-demos.14/)

**Possible use:** obtain comparable token, lemma and dependency representations on the Farsi and English sides. Its [model documentation](https://stanfordnlp.github.io/stanza/performance.html) lists English and Persian resources, including Persian PerDT and Seraji.

**Limit:** a language name in a code table is not evidence of a downloadable, validated model. A ready Pahlavi model and its suitability have not been established in this study. Its 2020 paper was identified and credited, not read in full here.

### SentencePiece

**Credit:** Taku Kudo, John Richardson and project contributors; repository hosted under Google's organization. [Paper](https://aclanthology.org/D18-2012/)

**Possible use:** learn a vocabulary of subword units from a future licensed corpus. It provides BPE and unigram approaches and a Python interface.

**Study implication:** subword units are computational pieces, not philological lemmas or manuscript word boundaries. Preserve source strings independently of any model's normalization. Learn a tokenizer from the training portion only when an evaluation is eventually conducted. No tokenizer was trained in this project.

### SacreBLEU

**Credit:** Matt Post and contributors. [A Call for Clarity in Reporting BLEU Scores](https://aclanthology.org/W18-6319/)

**Possible use:** compute reproducible BLEU, chrF/chrF++ and TER comparisons once reviewed reference translations exist. The project records metric settings in a signature so results can be interpreted and repeated.

**Study implication:** report Farsi and English separately. Word/character overlap cannot by itself establish correct agents, negation, technical senses or damaged-text interpretation. Multiple acceptable translations and human philological review remain necessary. No translation quality score has been measured here.

## Language and corpus resources already in the knowledge base

| Resource | Credit and reason to retain it |
|---|---|
| [Parsig Database](https://parsigdatabase.com/) | Farzaneh Goshtasb, Nadia Hajipour and the database team; user's priority corpus. Live access now works; the [live study](../kb/parsig-live-study.md) records six read records. Whole-site study remains incomplete. |
| [MPCD project](https://www.geschkult.fu-berlin.de/en/e/iranistik/forschung/MPCD/index.html) | Zoroastrian Middle Persian Corpus and Dictionary project and its institutional collaborators; manuscript-linked lexicography. Live corpus access was unavailable. |
| [Universal Dependencies: Middle Persian](https://universaldependencies.org/pal/index.html) | UD Middle Persian/MPCD contributors; grammatical annotation documentation already consulted. |
| [TITUS Kārnāmag](https://titus.uni-frankfurt.de/texte/etcs/iran/miran/mpers/kap/kap001.htm) | D. N. MacKenzie, Elio Provasi, Jost Gippert and TITUS; edited transcription used for earlier worked readings. |

These are additional resources for study, not substitutes for reading the requested website. Continue from [the study status](../kb/study-status.md).
