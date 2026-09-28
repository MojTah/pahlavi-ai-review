# Grammar and translation-method review

RESULT: PASS for this bounded audit; not a claim of complete grammatical knowledge or independently validated translation accuracy.

UTC start: 2026-09-24T03:43:05Z. UTC end: 2026-09-24T03:51:33Z.

## Outcome

The core warnings in `kb/grammar.md` and `kb/reading-method.md` are sound: distinguish written evidence from a proposed reading; do not equate an enclitic's host with its syntactic role; check past-transitive participants; and retain uncertainty. I did not confirm a gross linguistic error in the existing statements. I found consequential omissions and wording that is safe only if its limited scope is remembered. The highest-value additions concern ambiguous bare verbal forms, omitted auxiliaries, mood/person ambiguity, and late object marking.

No knowledge-base file was changed by this reviewer. The following are proposed additions for lead integration.

## Proposed corrections and additions

### 1. Do not require an overt auxiliary to recognize a finite past

Location: `kb/grammar.md:51`; `kb/reading-method.md:14`.

The wording “past expressions combine a participle with auxiliaries” needs the omission rule. In the ordinary third-singular preterite, the present auxiliary is absent. A bare form such as **šud** can be a finite predicate. Add an explicit check for a zero auxiliary before deciding the clause lacks a verb.

Evidence: Maggi and Orsatti, printed p. 25 / PDF 48, section 2.10.5 and table 2.4. The displayed contrast between **šud hēm** and **šud** was checked visually. Nyberg, printed p. 282 / PDF 291, section 7.1, gives the same basic omission pattern.

### 2. A past-stem-shaped form is not necessarily finite

Location: `kb/reading-method.md:14`.

Test finite preterite, participial adjective, short infinitive and converb analyses before assigning tense or agency. A converb can express an action anterior to its main event; a modal can govern a short infinitive.

Evidence: Jügel 2015, English Summary, printed XXIX–XXX / PDF 3–4, referring to book sections 4.2.1–3 and 4.3.1–4. This is an addition from the author's summary, not study of the full referenced chapters.

### 3. Label the mood table by tradition and expose overlapping endings

Location: `kb/grammar.md:51` and the indicative table above it.

The statement that **-ād** is useful for third-person recognition is not false, but it is not an exclusive person decoder. Oxford table 2.3 gives **-ād** for both third-singular and second-plural subjunctive in its Manichaean paradigm. The same table places **-ēd** in third-singular and second-plural indicative, and second-plural imperative. **-ēm** likewise occurs in first-singular and first-plural indicative. Add: “An ending can leave person, number or mood unresolved; use the text tradition, clitics and clause context.” Later Zoroastrian restriction of productive subjunctives does not retroactively govern all Middle Persian corpora.

Evidence: Maggi and Orsatti, printed p. 24 / PDF 47, table 2.3, its footnote 16, and section 2.10.3; table visually checked. Nyberg printed pp. 280–281 / PDF 289–290, sections 5.1–5.7, uses different transcription conventions and also discusses overlapping functions.

### 4. Make the tense labels and their limitations explicit

Location: `kb/grammar.md:51`.

The three current examples denote different constructions, but the learner is not told which. Oxford's terminology is: preterite with present **h-**; past preterite with **būd** plus the appropriate auxiliary; perfect with present **ēst-**; pluperfect with **ēstād** plus the appropriate auxiliary. Its examples include **šud hēm**, **šud būd hēm**, **šud ēstēm**, and **šud ēstād hēm**. This is a morphological classification, not a rigid one-to-one mapping to English tense labels. Oxford itself allows both English simple-past and present-perfect renderings of the preterite.

Evidence: Maggi and Orsatti, printed p. 25 / PDF 48, table 2.4, visually checked. Nyberg, printed p. 283 / PDF 292, sections 7.7–7.10, additionally shows modal, counterfactual and future-perfect contexts requiring separate treatment.

### 5. Preserve the distinction between stem class and time reference

Location: `kb/grammar.md:55` and heading “Past transitive clauses.”

Retain “past-stem transitive constructions”: modality or non-past time reference does not itself remove that alignment. A missing ending does not prove third-singular agent agreement.

Evidence: Jügel 2015, English Summary, printed XXVIII / PDF 2, on stem-based alignment regardless of tense/mood; printed XXX–XXXI / PDF 4–5, on zero agreement and ambiguous third-person forms.

### 6. Add the attested object-marking exception for rāy

Location: `kb/grammar.md:64`.

Current advice against mechanically importing modern Persian **rā** is good. It should not imply that object marking never occurs in Pahlavi. Proposed wording: “**rāy** commonly expresses a beneficiary, purpose or cause; some later passages use it to mark an object. Decide from the edition, period and construction.”

Evidence: Maggi and Orsatti, printed p. 21 / PDF 44, example 11, explicitly identifies an object-marking use in a late text. Nyberg, printed pp. 282–283 / PDF 291–292, section 7.5, provides comparable instances in his **rād** transcription. Do not rewrite Nyberg's source spelling silently.

Related unresolved scholarly difference: Oxford p. 21 discusses object-marking **ō** more broadly, while Jügel's English Summary, printed XXVIII / PDF 2, rejects most such analyses for Middle Persian. Do not turn either account into an unconditional **ō = direct object** rule.

### 7. Give the clitic-position rule and allow resumed participants

Location: `kb/grammar.md:26`; `kb/reading-method.md:15`.

Add that an enclitic commonly attaches near the beginning of its clause, so a conjunction or connective may carry a pronoun whose syntactic dependency lies elsewhere. Also mark whether an independent noun phrase and a clitic refer to the same participant. Counting them as two different agents can invent an event or person.

Evidence: Maggi and Orsatti, printed p. 22 / PDF 45, footnote 15; Nyberg, printed p. 279 / PDF 288, section 3.2, and printed p. 282 / PDF 291, sections 7.3–7.4, all visually checked where the older OCR is unreliable. Nyberg's absolute statements about hosts should not be copied as modern universal rules.

### 8. Expand linking beyond possession, and distinguish resumptive syntax

Location: `kb/grammar.md:30`; `kb/reading-method.md:17`.

The current “not always of” warning is correct. Add the actual possibilities: **ī** can link a head to a noun phrase, adjective, prepositional phrase or clause. **kē** and **čē** also function as relativizers; an English who/what animate–inanimate split must not be mechanically imposed. A relative clause may contain a pronoun resuming the head, so the relativizer and that pronoun should not automatically become two target-language participants.

Evidence: Maggi and Orsatti, printed p. 23 / PDF 46, section 2.10.2, examples 12–16. UD contributors, “Coordination & subordination,” on resumptive expressions. The latter is a current corpus project's analysis and annotation convention.

### 9. Preserve more than the indicative proposition

Location: `kb/grammar.md:61` and final paragraph.

Keep **nē** versus prohibitive **ma/mā**. Add **nēst**, negative existential/copular predication, and exhortative **ēw/hēb** as recognition items. A morphological present can refer to the future; the particle plus indicative can express an exhortation. Record the scope of negation and whether a rendering is a command, wish, condition, obligation or assertion. Do not translate every **be** as a modern Persian subjunctive prefix.

Evidence: UD contributors, “Tags” and “Degree and Polarity”; Maggi and Orsatti, printed p. 24 / PDF 47, section 2.10.3. Nyberg printed p. 281 / PDF 290, section 5.8, supports the existing warning that **-išn** can function predicatively with necessity rather than as an ordinary lexical noun. No new claim about every use of **be** or **hamē** is established here.

### 10. Avoid conflating derivation and grammatical voice

Location: `kb/grammar.md:92`.

“Passive/inchoative formation” is usable as a loose recognition aid but blurs two levels. Prefer “intransitivizing derivation; can yield passive or middle readings depending on its base and context.” Keep the existing instruction to identify the actual stem. Oxford separately treats the so-called inchoatives in **-s-**, and passive derivation in **-īh-**; these should not be combined into one universal suffix rule.

Evidence: Maggi and Orsatti, printed p. 25 / PDF 48, section 2.10.4; Nyberg, printed p. 282 / PDF 291, section 6.1; UD “Diathesis” gives a broader account of **-īh**. The sources differ in grammatical framing. Do not present that disagreement as a spelling error in the original knowledge base.

## Short translation checklist

1. Identify edition, tradition, exact locus and whether the evidence is script, transliteration or transcription.
2. Test finite and non-finite analyses, including omitted auxiliaries, before assigning tense.
3. Recover the complete verb phrase, particles, negation scope and modal force.
4. Separate semantic participants from their written hosts, case forms and agreement markers.
5. Check clitic reference and resumptive/doubled participants across the whole clause.
6. Resolve each linking or relative construction; do not map every ī to “of.”
7. Check noun number from context; absence of a plural ending or overt agreement is inconclusive.
8. Produce literal and idiomatic Farsi/English versions, marking supplied material and unresolved alternatives.

This checklist is a review procedure, not an automatic parser or a translation-accuracy test.

## Sources and exact study coverage in this review

- **Maggi, Mauro, and Paola Orsatti (2018), “From Old to New Persian,” Oxford Handbook of Persian Linguistics.** Read printed pp. 21–26 / PDF 44–49 in the locally retained publisher preview. Visually checked printed pp. 24–25 / PDF 47–48, including tables 2.3–2.4. Printed p. 26 was text-read; its rendered image was not inspected. [Publisher preview](https://api.pageplace.de/preview/DT0400.9780191056413_A35505953/preview-9780191056413_A35505953.pdf). Local source: `sources/oxford-persian-linguistics-preview.pdf`.
- **Nyberg, Henrik Samuel (1974), A Manual of Pahlavi II, grammatical survey.** Read printed pp. 279–284 / PDF 288–293; visually verified printed pp. 279, 281, 282, 283 / PDF 288, 290, 291, 292. Remaining page text came from noisy OCR and was not used to establish unverified exact forms. This is a recheck of a selected survey, not complete dictionary study. [Local source](../../../sources/A-Manual-of-Pahlavi-II-Dictionary.pdf); no independently verified public download URL asserted.
- **Jügel, Thomas (2015), Die Entwicklung der Ergativkonstruktion im Alt- und Mitteliranischen, English Summary.** Read the retrieved text for printed XXVII–XXXIII / PDF 1–7, and the beginning of XXXIV / PDF 8. [University-hosted author's summary](https://www.geschkult.fu-berlin.de/e/iranistik/publikationen/iranica/iranica21/iranica-21-english-summary.pdf). The complete monograph was not read. The summary explicitly cautions that its compressed claims need the full chapter discussion. A direct local download failed with a connection reset; no local PDF was retained. Additional page-fetch attempts were stopped after stalling, not treated as successful reading.
- **Universal Dependencies/MPCD contributors, UD for Middle Persian.** Read the entire current page, including tokenization, morphology, agreement, syntax and coordination sections. [Project documentation](https://universaldependencies.org/pal/index.html). It is evidence of the contributors' analysis, not a universally binding grammar. No treebank was downloaded or tested.
- Discovery-only searches located Jügel's BE article and a Skjærvø primer listing. Neither work was retrieved or read in this review; they are not counted as new study.

## Limitations and next step

This review supports targeted knowledge-base improvements. It does not demonstrate unaided reading of new manuscripts or complete translation competence. No blind passage test, expert scoring, full Nyberg dictionary study, or full Jügel monograph study occurred. The next useful validation is a held-out set of short passages covering zero auxiliaries, past-transitive clitics, relative resumption and modal/negative constructions, compared with the exact scholarly editions while retaining disagreements.

New valid source-PDF downloads: 0 bytes. Scratch contains selected local-source page renders and extracted text only. No packages, account access, Drive access or external writes were used.
