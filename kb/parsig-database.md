> **Superseded acquisition status, 20 September 2026:** the direct source-text collector has now saved all 126 Parsig records and their supporting text metadata. This earlier study/IDM guide is retained as history. Current coverage, language corrections and gaps are in [the data guide](../data/README.md).

# Parsig Database: coverage and findings

Source requested by Mojtaba: [parsigdatabase.com](https://parsigdatabase.com/). Checked **20 September 2026**. This record separates study of the database itself from study of related publications.

## Coverage

| Material | What was actually done |
|---|---|
| Live homepage and about page | **Access restored on 20 September 2026**; rendered content and credits read |
| Guides and reference pages | Search guide, displayed tag tables, abbreviations and bibliography read; cited publications not thereby read |
| Text inventory | 126 selectable records across four collections; all titles and IDs retained in the [inventory](../sources/parsig-live-inventory.json); two introduction indexes read |
| Paragraph-layer reading | As of 24 September, all 126 records / 4,507 units of the saved 20 September snapshot have documented source-assisted reading; unresolved interpretations remain. [Exact coverage](../sources/parsig-complete-study-2026-09-24.json) |
| Word annotation | One occurrence inspected with edition and work locators; vocabulary and exact variant views checked |
| Direct requests | Initially failed; current HTTPS root and robots.txt return HTTP 200. Sitemap URL returns the HTML application shell, not an XML sitemap |
| Public archive | Earlier availability index reported snapshot `20260615145828`; replay returned HTTP 503; archived contents remain unread |
| ParsiPy paper, 2025 | All 13 PDF pages read, including appendices; figures/tables on PDF pages 2, 7 and 12 inspected visually |
| Project lead's update, published 2 February 2025 | Complete letter read |
| Public ParsiPy repository | README and license read; four processing modules and their data loader inspected; four data files parsed and counted; selected lexical rows studied |

The repository is related research software, **not a mirror of the website**. Its word lists do not contain the site's complete texts and bilingual translations. Downloading or counting entries is not equivalent to learning every entry.

## What the publications establish

Farsi et al.'s **2025 research snapshot** reports 120 documents, 93,518 words, 8,839 unique tokens and 4,641 distinct lemmas. It describes transcriptions, spelling-preserving transliterations, grammatical annotations, heterograms, and Persian/English translations. These are reported historical counts, not a census of the current website. Its P2T module predicts spelling representations from readings; it does not translate sentences into Farsi or English. Reported results include 29.764% word error for rule-based P2T and 89.4% lemmatizer accuracy. Neither measures translation quality. [S18: paper, §§4–6](sources.md#s18)

The project lead's 2025 letter reports the addition of Manichaean Middle Persian material, Persian translations, nine annotation layers and links to Turfan manuscript images. The current reader independently exposes 59 Manichaean records; its live conventions and limits are recorded in the [new study](parsig-live-study.md). Counts of annotation layers differ with how a publication or page groups the fields; do not silently equate them. [S19: project update](sources.md#s19)

## What the public files establish

Inspected repository snapshot: `3e388d8681004835dbda343653d4959bb9288371`. Counts below are from local parsing, not a paper claim. [S20: source repository](sources.md#s20)

| File | Observed content |
|---|---|
| `roots.json` | 3,305 entries; 3,032 distinct strings |
| `stems.csv` | 6,924 distinct spelling pairs; 3,515 distinct stem strings |
| `emission.csv` | 7,260 data rows; token-associated numeric columns for tagging |
| `transition.csv` | 14 data rows; state/tag transition values |

Among the stem strings, **1,509** have multiple distinct nonempty spellings. There are **13** rows with empty transliterations. Nonbreaking spaces occur in **427 distinct stem strings** and **185 root entries**; three stem rows are not in Unicode NFC form. These are processing observations, not automatic judgments that the philological data are wrong. Exact hashes and counting definitions are in [the inspection record](../sources/parsipy-inspection.json).

Selected rows associate `šāh` with both phonetic and heterographic spellings, including `šh`, `MLK` and `MLKA`. Multiple spellings also occur for common verbs. These associations have no witness locator in this two-column file. Retain them as candidates for checking, not interchangeable spellings guaranteed for every passage.

## Critical reading notes

These are our analysis of the evidence, not claims of independent scholarly review.

- **Keep the two directions separate.** A tool that predicts a spelling from a known reading has already been given information that a manuscript reader must recover.
- **Preserve uncertainty marks.** The inspected tokenizer removes asterisks, square/angle brackets and `(w)`, replaces hyphens with spaces, then splits whitespace. Its output therefore cannot replace the original editorial text. The paper describes a SentencePiece tokenizer, so the inspected implementation should not be assumed identical to the evaluated system.
- **Do not pick the first spelling as truth.** The inspected P2T implementation returns the first matching stem row. That behavior loses alternative attestations and provides no witness-based selection.
- **Stem is not always dictionary lemma.** The public root list separately includes `kun`, `kard`, `mad` and `ēst`. A lookup may help identify a verbal form without connecting its present and past stems to a dictionary headword.
- **Read annotations critically.** The README marks `uzīd` as N where the paper's example marks V. Both example outputs mark final `bar` as N; the phrase's imperative interpretation requires checking that label. See [the worked reading](bilingual-reading.md).
- **Use specialist grammar for historical distinctions.** The paper's broad case and Aramaic-vocabulary overview does not replace the distinctions between grammatical stages, heterograms and actual loanwords in [our grammar](grammar.md) and [writing notes](writing-system.md).
- **Reproduce evaluation before relying on scores.** The POS tables distinguish macro class measures from micro precision. Their accuracy values should not be casually read as ordinary token accuracy. Document-level separation of training and test texts is not established here.

## Access recovery and next reading

The user took over the Throne routing change manually and then requested another access attempt. The live website and rendered corpus now work. This verifies access, not the exact VPN rule or network route; the assistant did not change the VPN configuration.

The initial five live readings are historical coverage, superseded by the later [collection](../data/README.md) and [24 September reading review](review-2026-09-24.md). All saved paragraph layers have now been read, but the complete website, all annotations, manuscripts and related publications have not. Preserve source IDs, language distinctions and editorial uncertainty. No translator implementation or model training was performed.
