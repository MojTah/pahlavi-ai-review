# Parsig Database: live study

Studied **20 September 2026**, through the public [Parsig Database](https://parsigdatabase.com/). Source credit: **Pārsīg Database**, led by **فرزانه گشتاسب**, and the editors and translators identified below. These are source-assisted study notes and our analysis, not independent manuscript decipherment or validated training data.

## Coverage that can be checked

Access now works. Read the homepage, about page, search guide, complete displayed grammatical-tag tables, abbreviation list and bibliography. Read both text-introduction indexes, and the individual introduction to *Dārūg ī hunsandīh*. Reading a bibliography does not mean reading its cited publications.

The [text reader](https://parsigdatabase.com/surf/?lang=fa) exposes these top-level options:

| Collection | Group ID | Selectable records |
|---|---|---:|
| Zoroastrian Middle Persian | 1 | 40 |
| Zand of the Avesta | 3 | 2 |
| Private Sasanian and post-Sasanian inscriptions | 2 | 25 |
| Manichaean texts | 5 | 59 |
| Total | | **126** |

The [inventory](../sources/parsig-live-inventory.json) preserves every observed title and ID. Its saved titles, order and IDs match a checksum calculated from the browser-captured options. This verifies transcription of the index, not linguistic correctness or corpus completeness.

**Historical live-reading checkpoint:** six records / 44 displayed units were read at the stage documented below; record 107 subsequently brought the earlier total to seven / 52. **Current coverage, 24 September:** all 126 saved records / 4,507 units have documented paragraph-layer reading. See [the review](review-2026-09-24.md) and [exact ledger](../sources/parsig-complete-study-2026-09-24.json). Manuscripts, all word annotations and all linked editions remain outside that completion claim. A record may contain excerpts, fragments, quotations or headings rather than a complete ancient work.

| Record | Reader selection and units actually read | Edition / displayed translation credits |
|---|---|---|
| 101, آمدن بهرام ورجاوند | Chapter `101000`, units 0–3 | Jamasp-Asana 1913, pp.160–161; Farsi: گشتاسب و حاجی‌پور، 1398; English for §§1–2: Skjærvø 2011, p.166 |
| 119, داروی خرسندی | Chapter `119000`, units 0–9; individual introduction also read | Jamasp-Asana 1913, p.154; Farsi: گشتاسب و حاجی‌پور، 1398; English: Ichaporia 2001, as displayed; page-number conflict below |
| 120, اندرز بخت آفرید | Chapter `120000`, units 0–12 and correction note; [analysis](baxt-afrid-study.md) | Jamasp-Asana 1913, pp.81–82; Farsi: گشتاسب و حاجی‌پور، 1398 |
| 207, صلیب هرات | Chapters `207001` and `207002`, unit 1 on each face | Farsi and notes: نصراله‌زاده، 1398، ج1، ص260–261 |
| 302, زند خرده اوستا | `302001` اشم وهو: 0–1; `302002` اهونور: 0–1; `302003` گومیز کردن: 0–3; `302004` نان خوردن: 0–1 | Dhabhar 1927, pp.1–3; Farsi: حاجی‌پور، 1400; English: Dhabhar 1963 and Musavi 2021, as displayed |
| 506, Manichaean selection **a** | Chapter `506000`, units 1–5 | Boyce 1975, pp.29–30; manuscript M5794/I/R–V; Farsi: مصطفوی کاشانی، 1400 |

To reproduce: open the text reader, select collection → text → chapter → numbered section or همه, then press جستجو. The reader URL alone does not preserve the selected record. The selected manuscript tab for 506 offered M5794-I-R and M5794-I-V; those images were not collated.

## Annotation conventions learned directly

The [search guide](https://parsigdatabase.com/help_search/?lang=fa) distinguishes a MacKenzie-style **transcription** from a **transliteration** tied to the critical edition's spelling. Persian word meanings are contextual glosses, not exhaustive dictionary definitions. The guide says compounds receive the whole compound as lemma; verbal entries include the infinitive, past stem and present stem, in that order. Verify an individual record rather than assuming a single string format.

| Source notation or field | Meaning stated by the guide | Consequence for our study |
|---|---|---|
| `*` in transcription | Editorial correction | Keep corrected reading and editorial status together |
| `*` in a lemma | Hypothetical form | The same symbol has a different role in another field |
| `[]` | Added words | Do not turn additions into unmarked manuscript text |
| `<>` | Deleted words | Retain the rejected material and the deletion decision |
| `{}` | Explanatory or interpretive clauses, especially in Zand | Keep commentary distinguishable from the translated base text |
| Edition reference | Page, then line | A chapter reference cannot replace it |
| Book reference | Work abbreviation, chapter/section | Retain both kinds of locator |
| Heterogram annotation | A described 0/1 distinction; guide says this layer is not currently visible | Do not claim to have inspected it through the reader |

The guide distinguishes substring matches in the vocabulary list from exact-input variant/frequency results. Collocation search permits one to three preceding and following words. We read these instructions; only the text reader and one word query were exercised in this checkpoint.

The [tag guide](https://parsigdatabase.com/help_tags/?lang=fa) credits **Bijankhan et al. 2011** and **Ghayoomi 2014**, adapted for Pahlavi. Its displayed tables include A adjective, D adverb, j conjunction, T determiner, N noun, U number, P postposition, E preposition, Z pronoun and V verb. Different positions encode type, polarity, number, person, clitics and category-specific properties. These are the site's codes, not Universal Dependencies labels.

Two documentation cautions remain: the prose lists eleven principal categories, including ezafe and verbal particles, while the displayed tables contain the ten headings listed above, including number. Also, the verb table groups passive under “transitivity” and optative/conditional under “aspect.” Preserve the source schema; a later linguistic mapping would require explicit review. We have not reconciled every code with live records.

The [abbreviation table](https://parsigdatabase.com/library_signs/?lang=fa) and [bibliography](https://parsigdatabase.com/library_res/?lang=fa) connect work-level references to editions. They are reference aids, not evidence that every cited text is fully loaded.

## One verified word annotation

Query: [word search](https://parsigdatabase.com/search/?lang=fa), Zoroastrian texts → داروی خرسندی → transcription `hunsandīh`.

| Field | Observed value |
|---|---|
| Occurrence ID | `119000001003` |
| Transcription | `hunsandīh` |
| Transliteration | `hwnsndyh` |
| Persian gloss | خرسندی، قناعت |
| Category | اسم — noun |
| Lemma field | `hunsand` |
| Edition locator | `Jamasp-Asana1913:154/2` |
| Work locator | `DH:1` |

The vocabulary view returned unbracketed occurrences in §§1 and 2, and a bracketed occurrence in the supplied title, §0. The exact variant/frequency view showed the two unbracketed occurrences. This is a concrete reason to preserve editorial brackets and query mode. The site's lemma for the abstract noun is `hunsand`; retain that observed field separately from our derivational analysis or a future dictionary headword.

## Reading lessons and a bilingual exercise

### Bahrām Warzāwand, record 101

The text combines an anticipated arrival, complaints about conquest and taxation, and hopes for reversal. Its hostile religious and political rhetoric belongs to the historical speaker; it is not a neutral account or our endorsement. The opening is a question expressing anticipation. In the messenger passage, a form of going is naturally rendered with رفتن in current Farsi; simply copying its resemblance to شدن can change the sense.

There are substantial differences between the supplied Farsi and English interpretations. For example, the second unit's negative comparative is interpreted in Farsi as nothing being worse than the hostile figure, while the English version speaks of the homeland's condition. Record this as an alignment issue pending comparison with the editions, not as two interchangeable sentence-level reference answers. The correction and supplement signs remain part of the evidence.

### Remedy of Contentment, record 119

The [introduction](https://parsigdatabase.com/book/119?lang=fa) identifies an eight-section counsel framed as an allegorical prescription; the reader additionally numbers a title/invocation and closing, producing units 0–9. It cites the MK manuscript at folios 151v–152r and Jamasp-Asana p.154. The medicinal vocabulary functions as a moral metaphor involving patience, prayer and trust.

Brief study excerpt, §4:

> az im-rōz tā fradāg weh šāyēd būdan dāng-ē sang.

**Our Farsi study rendering:** یک دانگ به وزنِ این اندیشه: «از امروز تا فردا ممکن است وضع بهتر شود.»

**Our English study rendering:** One dāng by weight of this thought: “Things may be better tomorrow than today.”

The framing “of this thought” makes the recipe metaphor explicit; it is our explanatory addition. `az … tā …` frames the interval; `weh` is comparative “better”; `šāyēd` with `būdan` expresses possibility. A translation promising that things **will** improve would strengthen the modality beyond this reading. `dāng-ē sang` supplies the recurring measured portion; no modern mass conversion is introduced.

The first section's Farsi and English versions differ on the scope of negation and what is curable or prescribed. The displayed English citations run pp.752–756, but the site's bibliography and introduction list Ichaporia's article on pp.572–577. Preserve this unresolved citation discrepancy; the original article has not been checked. The English closing also contains words beyond the displayed one-word transcription, so the closing is not a literal token alignment.

### Herat cross, record 207

Read both faces and the supplied note. The front preserves doubtful personal names, competing readings of the written verb, and a date read as either **507 or 517**. The note reports both a seeing interpretation and a possible writing interpretation for the disputed verb. The back retains incomplete and uncertain forms. Do not select one name or date automatically, assign a calendar era, or replace question marks and gaps with fluent invented details. An English translation should keep those unresolved alternatives visible.

### Four Zand selections, record 302

The Ašəm Vohū note analyses a causative element in `ahlāyēnīdār`, motivating a meaning connected with promoting righteousness. The Ahunwar selection interleaves the base rendering, explanations, alternative interpretations and an attributed commentator. Its note treats the written construction `gōwēd ē` as optative; splitting or discarding the final element could destroy that analysis.

The third selection records a dispute over the function of `-ān`; the supplied explanation does not simply label every occurrence as plural. Its ritual repetition counts also differ between the displayed versions. The meal-prayer passage illustrates past creation clauses with a clitic agent, useful for revisiting [the grammar notes](grammar.md). Familiar Persian words require contextual care: the gloss of `gōspand` is wider than modern “sheep,” and `ābādīh` receives an interpretive explanation concerning productive land and its yield.

These are **four selections**, not the complete Khorda Avesta. Parallel material is identified in Yasna by the site's notes; do not count parallel passages as independent evidence in a future evaluation split.

### Manichaean selection a, record 506

The speaker compares the religion with earlier traditions, emphasizing its geographical and linguistic reach, written works, community and teaching. Observe the numbered argumentative structure, comparative vocabulary and contrasts between past and prospective statements. Technical terms for religious offices and classes need specialist meanings rather than generic modern Persian guesses.

Although the opening promises ten advantages, only five numbered units are offered here, and the fifth breaks off. “All displayed units read” therefore does not mean “a complete ancient composition read.” The manuscript locator M5794/I/R–V and Boyce pages should stay attached to the selection. The Farsi translator is **حسین مصطفوی کاشانی**; no English translation was displayed for these units.

### Sayings of Baxt-āfrīd, record 120

Read all 13 displayed units and the revised-reading note. The [detailed study](baxt-afrid-study.md) analyses comparative forms, repeated/supplied verbs, idiomatic oath-taking and the polarity-changing revision in §11. [Twelve dictionary entries](../dictionary/entries.json) record these families and related evidence from record 119. Both critical-edition images were loaded; their text was not collated.

## Findings that affect the future translator

- Six Manichaean records are explicitly labeled mixed Middle Persian–Parthian: **504 aq, 505 ar, 526 cj, 538 cu, 542 dg, 556 dv**. Segment language must be checked before treating their contents as Middle Persian examples.
- Translation availability varies. The [Zoroastrian index](https://parsigdatabase.com/books/1/?lang=fa) lists Farsi-only, Farsi/English and Farsi/French records. It also marks some works as partial, including the Kārnāmag at chapters 1–3. A site's “complete” loading label is not our study-completion status.
- Plain text extraction of the Book Pahlavi display produced Arabic-code-point strings, while the transcription remained legible. Treat that extracted script layer as encoding-dependent until its font mapping is verified. The Manichaean display used Manichaean Unicode characters, with joining characters; preserve them before normalization.
- Keep source translation, literal analysis and our natural rendering distinct. Preserve additions, damaged text, variant readings and differing edition choices. The notes here are not expert-reviewed reference translations.
- The site's stated research-use permission requires attribution. Its footer also retains copyright. Neither the ParsiPy software license nor free public access establishes unrestricted commercial training or redistribution rights for every edition, translation and image.

Next: continue short Book Pahlavi counsel texts, then a continuous narrative and further Manichaean material; inspect selected word annotations and manuscript witnesses alongside each reading. Update the inventory's per-record coverage only after reading the corresponding displayed material. Whole-site study remains incomplete.
