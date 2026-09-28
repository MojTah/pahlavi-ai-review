# Writing-system and language-boundary review

RESULT: PASS for this bounded review, with the coverage and access limits below. This is not a claim of complete language knowledge or independent manuscript decipherment.

Reviewer: script_review. Started 2026-09-24 03:44:20 UTC; completed 2026-09-24 03:52:51 UTC (8 minutes 31 seconds). Expected duration 10 minutes; warning 15; hard stop 20. No core files changed. No installations, models, external writes, or Drive access.

## Overall finding

`kb/writing-system.md` and `kb/language-and-corpus.md` are substantially sound. The four reading layers, heterogram examples, warning against treating the 2014 proposal as adopted Unicode, and preservation of uncertain readings should remain. The main improvements are explicit language boundaries, practical encoding examples, and tighter attribution of historical or manuscript-date claims. These notes support reading edited texts; they do not demonstrate autonomous decipherment of Book Pahlavi manuscripts.

## Recommended additions and corrections

1. **Make the scope explicit at the top of language-and-corpus.** Suggested wording: “This project studies Middle Persian (Pahlavi), particularly the literary and documentary traditions represented in the collected sources. Old Persian is the earlier Achaemenid language stage; modern Farsi is a New Persian variety. The stages are historically related, but their texts and grammars must be labelled separately.” Maggi and Orsatti, section 2.1, printed p. 7 / PDF p. 30, directly distinguishes the three stages and associates Old Persian with Achaemenid and Middle Persian with Sasanian rule. Their pp. 19–20 document major phonological and inflectional changes. Avoid describing Pahlavi as simply present-day Persian in a different alphabet. [Publisher preview](https://api.pageplace.de/preview/DT0400.9780191056413_A35505953/preview-9780191056413_A35505953.pdf).

2. **Preserve language, script, and tradition as separate labels.** The current table does this well, but Manichaean writing deserves a concrete warning: it is used for Middle Persian, Parthian, Sogdian, Early New Persian, Bactrian and Uighur. Script alone does not identify language. Even within a single leaf, distinct languages can alternate. Do not merge a mixed Manichaean collection into a Pahlavi training corpus solely because its glyphs share a Unicode block. Durkin-Meisterernst, “Manichean Script,” opening paragraphs and discussion of M 172 in the Description section. [Article](https://www.iranicaonline.org/articles/manichean-script/).

3. **Qualify Pāzand as a transmitted linguistic reading.** The existing description is a useful first approximation, but changing script did not always preserve the exact earlier wording or pronunciation: later transmission can adapt forms towards contemporary Persian and replace difficult expressions. Suggested addition: “A Pāzand witness supplies a particular transmitted reading; its vowels and grammatical forms are evidence to compare, not an automatic decoding key for every Book Pahlavi witness.” Maggi and Orsatti, printed p. 19, footnote 9 / PDF p. 42. This also supports checking language rather than assigning all Avestan-script material to Avestan.

4. **Keep the heterogram table; add one concrete segmentation warning.** Sims-Williams explicitly supports `MN → az`, `MLKʾ → šāh`, `ʿL → ō`, and the `A/O` convention. With `MLKʾn`, the boundary between the heterographic and phonetic parts is convention-dependent; the alternative `MLKAn` preserves a distinction important to the editor. Uppercase/lowercase is linguistic annotation, not cosmetic styling. Lowercasing all transliterations would erase evidence. [Terminology and Conventions](https://www.iranicaonline.org/articles/ideographic-writing-i-terminology-and-conventions/), paragraphs beginning “In transliterating” and “Since the Aramaic letters.”

5. **Do not label every attached letter an ordinary spoken suffix.** The existing `YNSBWNyt → stānēd` and `GBRʾn → mardān` examples are confirmed. Attached material may express inflection or provide a reading cue; compounds can mix a heterogram and phonetic writing. Identification must use the edition's conventions and clause context. Aramaic spellings should not be counted as spoken Aramaic tokens in the Middle Persian sentence. Durkin-Meisterernst, “Huzwāreš,” Nature of huzwāreš, especially the two opening paragraphs. [Article](https://www.iranicaonline.org/articles/huzwares/).

6. **Show what ambiguity means without pretending to resolve it.** A Book Pahlavi sign may correspond to g/d/y; two occurrences can also participate in a digraph reading. This prevents a one-glyph/one-letter lookup from being a sufficient reader. Meyers, printed p. 9 / PDF p. 10, gives the example. It is a script illustration, not a general replacement rule and not evidence that the proposal's code points are standardized. [2014 proposal](https://www.unicode.org/L2/L2014/14077-book-pahlavi.pdf). The current KB correctly avoids adopting the proposal's character count as a universal alphabet count.

7. **Promote the legacy-font warning into writing-system.md.** Local corpus checks establish a concrete hazard: `corpus/119.json`, unit `119000000`, begins with Arabic-block code points whose displayed Pahlavi value depends on Ham-dibirih; the separate transcription begins `pad nām ī yazdān`. Unit `302001000` has the same encoding pattern. Conversely, unit `506000001` contains actual Manichaean-block characters plus zero-width non-joiners. A Unicode-range detector would therefore misidentify the Book Pahlavi display as Arabic-script language. Retain the raw string, font identity, source unit and rendering evidence. Derive searchable transcription separately. The font record explicitly states that no validated conversion exists. Local evidence: `resources/parsig-font.json`; `sources/local/parsig-2026-09-20/corpus/{119,302,506}.json`; public source [Parsig Database](https://parsigdatabase.com/).

8. **Preserve editorial markers with their layer and convention.** Local unit `119000001` contains `*čārag`; `119000003` contains `[sang]`. Their presence is directly verified, but this review did not locate a definitive convention key for those particular normalized entries. Therefore do not automatically translate every asterisk as “unattested” or every bracket as physical damage. Brackets can distinguish supplied source reading from translator expansion, and those are different layers. Store the edition's explanation when known; otherwise mark the convention unresolved. This is a practical preservation recommendation, not a newly resolved philological reading.

9. **Retain the Psalter's date distinctions and add a conflict note if giving dates.** Gignoux's article describes an often-cited sixth/seventh-century manuscript date, while discussing earlier translation language and successive copying. Maggi and Orsatti, printed p. 18, footnote 8 / PDF p. 41, instead report radiocarbon dating no earlier than the late eighth/ninth century, citing a 2010 lecture by Dieter Weber. The measurement report itself was not inspected here. Do not silently promote either to an undisputed date of composition. The current KB's instruction to distinguish composition and manuscript dates is correct. [Gignoux, Pahlavi Psalter](https://www.iranicaonline.org/articles/pahlavi-psalter/), opening and historical discussion; Oxford locators above.

## Unicode check and limits

- The published Unicode 17.0 chapter 10, sections 10.5–10.6, documents Manichaean, Inscriptional Pahlavi and Psalter Pahlavi separately; section 10.7 treats Avestan. Book Pahlavi is mentioned historically; this is not a Book Pahlavi encoding specification. [Version-pinned chapter](https://unicode.org/versions/Unicode17.0.0/core-spec/chapter-10/).
- On this review date, [latest](https://www.unicode.org/versions/latest/) redirected to a Unicode 18.0 page dated 16 September 2026, but the fetched page still included preliminary-draft status text. Direct version-18 character-data retrieval timed out; version-18 charts/core requests were cancelled after no timely response. **Do not replace the KB's cautious statement with a blanket claim about current Book Pahlavi adoption.** An implementation decision needs a verified versioned UCD/charts snapshot.
- No font mapping, OCR system, renderer, normalization pipeline or manuscript-decipherment accuracy was validated by this review.

## Coverage actually performed

| Item | Material read or checked in this pass | Limit |
|---|---|---|
| Two assigned KB files | Complete current text | Review only; no core edits |
| Sources and supplied-PDF study notes | Source identities, page locators, existing limitations | Existing notes are not a substitute for fresh full-book reading |
| Sims-Williams, terminology | Main article prose and convention examples | Bibliography not independently studied |
| Durkin-Meisterernst, Huzwāreš | Main article prose, especially nature and linguistic-reality discussion | Referenced books not read by proxy |
| Durkin-Meisterernst, Manichean Script | Opening, Description, Orthographic conventions; through Origin opening | Manuscript plates not independently deciphered |
| Gignoux, Pahlavi Psalter | Main article prose and relevant bibliographic locators | Underlying C14 report not accessed |
| Ludwig Paul, Early New Persian | Introduction, definitions, varieties, manuscript transmission opening | Not the complete grammar portion; [source](https://www.iranicaonline.org/articles/persian-language-1-early-new-persian/) |
| Maggi and Orsatti preview | Printed pp. 7–8 and 18–20 extracted/read; PDF pp. 30, 41–43 rendered and visually inspected | Incidental introductory PDF pp. 26–28 inspected; whole handbook/chapter not completed |
| Meyers 2014 proposal | PDF pp. 9–11 text read; PDF p. 10 visually inspected | Historical script evidence only; no adoption inference |
| Parsig samples | Specific units 119000000/1/3, 302001000, 506000001; raw script/transcription comparison and code-point classes | Not complete records, new corpus-reading coverage, or independent decipherment |
| Unicode | 17.0 chapter/code-chart listing, latest landing page | Version-18 normative data access unresolved |

## Integration and remaining work

Lead should integrate items 1–8 into the two KB files as short evidence-linked additions. Item 9 is a discrepancy note only if manuscript chronology is discussed. Keep book/record reading coverage separate from this script-method audit. Before claiming translation competence, evaluate unseen edited passages with source-separated answers and expert adjudication; before claiming manuscript reading, test images independently of supplied transcriptions. Those evaluations were outside this bounded review.

Artifacts created: this report and page images under `tmp/review-2026-09-24/script/`. Public source downloads retained: none. One local Python output-encoding failure was repaired with explicit UTF-8 output; no repeated production run or corpus mutation occurred.
