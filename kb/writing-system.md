# Writing system

## Four levels of a reading

1. **Witness:** the actual manuscript, inscription, or reliable facsimile.
2. **Transliteration:** an editor's representation of the written signs and spellings.
3. **Transcription:** the proposed Middle Persian linguistic reading.
4. **Translation:** an interpretation in another language.

Keep these levels in separate fields. A plausible translation does not establish the original spelling. [Sims-Williams, terminology and conventions](https://www.iranicaonline.org/articles/ideographic-writing-i-terminology-and-conventions/)

## Heterograms

Pahlavi can represent a Persian word with an Aramaic-derived spelling. The reader supplies the Persian word, and Persian endings may be attached. This is a writing convention, not sufficient evidence that a whole Aramaic word was spoken in the Persian sentence. Capital letters conventionally mark heterographic elements. [Durkin-Meisterernst, Huzwāreš](https://www.iranicaonline.org/articles/huzwares/)

| Written representation | Middle Persian reading | Meaning |
|---|---|---|
| `MN` | az | from |
| `MLKʾ`, or `MLKA` in another convention | šāh | king |
| `ʿL`, or `OL` | ō | to |
| `GBRʾn` | mardān | men |
| `YNSBWNyt` | stānēd | takes |

The first three mappings and the alternative conventions are documented by [Sims-Williams](https://www.iranicaonline.org/articles/ideographic-writing-i-terminology-and-conventions/); the inflected examples by [Durkin-Meisterernst](https://www.iranicaonline.org/articles/huzwares/). Do not mix the two transliteration systems silently.

Case distinctions in **MLKʾn / MLKAn** preserve convention-specific boundaries between heterographic and phonetic material. Attached writing can indicate inflection or a reading cue. Do not lowercase the entire transliteration or assume every attached letter is a separately pronounced suffix. [S1](sources.md#s1), convention examples; [S2](sources.md#s2), nature of huzwāreš.

## Why Book Pahlavi requires more than an alphabet

It runs right to left. Different historical letters can share shapes; connected forms and ligatures add ambiguity. Short vowels are often absent, and historical spelling can differ from the linguistic reading. The 2014 encoding proposal's character table and manuscript examples illustrate these problems. Its proposed characters and counts are **not** evidence of current Unicode standardisation. [Meyers, pp. 8–15, fig. 4.2](https://www.unicode.org/L2/L2014/14077-book-pahlavi.pdf)

Practical consequence: learn recurrent whole-word spellings alongside individual signs. Never label an Inscriptional Pahlavi font sample as Book Pahlavi merely because both names contain “Pahlavi.”

Manichaean writing offers a clearer comparison for linguistic readings and avoids the Pahlavi heterographic system. It nevertheless has its own conventions and cannot mechanically resolve every Book Pahlavi ambiguity. [Manichaean script](https://www.iranicaonline.org/articles/manichean-script/)

## Reading notation

This knowledge base retains scholarly vowel marks such as **ā, ī, ū, ē, ō**. Read each source's notation key: the Oxford chapter uses **c/j** where other editions may use **č/ǰ**. A transcription is not an audio recording. [Maggi and Orsatti, p. 20, n. 11](https://api.pageplace.de/preview/DT0400.9780191056413_A35505953/preview-9780191056413_A35505953.pdf)

Keep `ʾ`, `ʿ`, `A`, `O`, and plain apostrophes distinct in source transcriptions. Preserve uncertainty marks, supplied text, and manuscript variants. Do not run a blanket character replacement over an edition.

The saved Parsig units `119000001` and `119000003` contain **\*čārag** and **[sang]**. The markers are verified, but this review has not established their particular notation key. Do not assume every asterisk means unattested language or every bracket means physical manuscript damage. Source restoration and a translator's explanatory addition are separate layers.

## Legacy font data in the collected corpus

Saved units `119000000` and `302001000` use Arabic-block code points to display Pahlavi through **Ham-dibirih**; `506000001` instead contains Manichaean Unicode characters. Unicode block alone therefore cannot identify the language of these raw fields. Retain the raw text, font identity and source unit, and use the supplied transcription separately for linguistic reading. No validated conversion or OCR pipeline has been established. [Font evidence](../resources/parsig-font.json); [reviewed unit evidence](../sources/reviews/2026-09-24/script-review.md).

## Checks from the supplied scans and editions

The Persian primer distinguishes **historical spelling** from **pseudo-historical or analogical spelling**. A written form may preserve an earlier sound or imitate a spelling pattern rather than represent contemporary pronunciation directly. Its tables also show connected signs and ligatures, with some distinguishing marks introduced later. A character substitution table alone cannot recover the reading. [S22](sources.md#s22), printed 45–61 / PDF 48–64.

A sign resembling the numeral one may function as indefinite **-ē** in the relevant construction. Determine its grammatical role before recording an arithmetic quantity. [S22](sources.md#s22), printed 58 and 73 / PDF 61 and 76.

In the documentary editions, tiny differences affect animals, totals, names and dates. Keep the image pointer, transliteration, transcription and translation separately. Examples include the proposed 17 → 27 revision for TB4 and the unresolved three/four conflict across the editorial layers of Berk. 122. These are specific readings, not general numeral-replacement rules. See [the discrepancy register](supplied-pdf-study.md#source-discrepancies-retained-for-review).

Nyberg's OCR is a search aid, not a diplomatic text. The Persian-wrapped copy of his manual runs in reverse page order and has no text layer. Neither OCR order nor the PDF filename should determine a word's linguistic form or the work's language. [Source identities and pagination](supplied-pdf-study.md#coverage-and-identity).
