# Philological requirements for faithful Pahlavi translation

Checked 2026-09-25. Public scholarly sources and official institutional credentials were inspected. No contact, Drive access, model execution, or restricted-book download occurred. The companion JSON contains twelve substantive source records and explicit limitations.

**Main finding:** a translator needs to preserve the distinction between what is written, how an editor reads it, and what that reading means in context. Correctly supplied text can still admit competing linguistic interpretations. A supplied scholarly transcription has already resolved some of those choices; it must not be treated as a neutral copy of the script. This follows especially from [Skjærvø on writing systems](https://www.iranicaonline.org/articles/iran-vi3-writing-systems/) and [Rezania's representation study](https://gitlab.dh.uni-koeln.de/mpcd/handbooks/-/raw/4644d2750d737f4e3a7116223885f05710f83a7b/transcription/Rezania_2020__A_Suggestion_for_the_Transliteration_of_Middle_Persian_Texts_.pdf?inline=true).

## Evidence and its practical consequence

| ID | Substantive source | Consequence for this translator |
|---|---|---|
| PH01 | [MPCD methodology](https://www.mpcorpus.org/methodology/) | Reuse its separation of transliteration, transcription, lemma, grammar and contextual meaning; distinguish expert from automatic annotations. |
| PH02 | [Rezania 2020: three-layer transliteration](https://gitlab.dh.uni-koeln.de/mpcd/handbooks/-/raw/4644d2750d737f4e3a7116223885f05710f83a7b/transcription/Rezania_2020__A_Suggestion_for_the_Transliteration_of_Middle_Persian_Texts_.pdf?inline=true) | Search normalization can intentionally collapse distinctions. Keep recoverable originals and identify the conversion convention. |
| PH03 | [Durkin-Meisterernst: HUZWĀREŠ](https://www.iranicaonline.org/articles/huzwares/) | Interpret heterograms as Middle Persian lexical representations with Iranian complements, not ordinary foreign words to translate literally. |
| PH04 | [Skjærvø: Writing Systems](https://www.iranicaonline.org/articles/iran-vi3-writing-systems/) | Context-sensitive reading remains relevant after accurate text entry. Script type and phonemic reading are separate facts. |
| PH05 | [MacKenzie: FRAHANG Ī PAHLAWĪG](https://www.iranicaonline.org/articles/frahang-i-pahlawig/) | Historical dictionaries can inherit previous errors. Retain editions and attestations instead of counting repeated glosses as independent confirmation. |
| PH06 | [Middle Persian UD documentation](https://universaldependencies.org/pal/index.html) | Explicitly inspect argument roles, omitted participants, agreement and discourse links; word order alone is insufficient. |
| PH07 | [Jügel 2015: corpus-based ergativity study](https://www.harrassowitz-verlag.de/Die_Entwicklung_der_Ergativkonstruktion_im_Alt-_und_Mitteliranischen/title_1085.ahtml) | Grammar reference for case, agreement, clitics and omission. Only publisher synopsis was inspected, not the whole book. |
| PH08 | [Khanizadeh: Iranian Pahlavi Yasna](https://www.cambridge.org/core/journals/bulletin-of-the-school-of-oriental-and-african-studies/article/zoroastrian-ritual-and-exegetical-traditions-the-case-of-the-iranian-pahlavi-yasna/D862FF6E8BFF7892D1A2828D04DC1768) | A documented dispute about omitted objects and reflexive antecedents changes a colophon's attribution; keep grammatical alternatives accountable. |
| PH09 | [Kreyenbroek: Zoroastrian exegesis](https://www.iranicaonline.org/articles/exegesis-i/) | Inherited translation, explanatory paraphrase and different authorities' opinions must remain distinct. |
| PH10 | [Macuch: Mādayān ī Hazār Dādestān](https://www.iranicaonline.org/articles/madayan-i-hazar-dadestan/) | Legal cases need institutional meanings, party roles and conditional scope; manuscript order and competing opinions also matter. |
| PH11 | [Cereti: Pahlavi literature](https://www.iranicaonline.org/articles/middle-persian/pahlavi-literature/) | Genre, register and the dates of composition, compilation and copying are separate metadata. |
| PH12 | [Shaked: Gētīg and Mēnōg](https://www.iranicaonline.org/articles/getig-and-menog/) | Preserve contextual theological distinctions; material versus spiritual does not automatically mean evil versus good. |

## Proposed representation and annotation contract

These are design inferences from the sources, not a demand to invent complete annotations for every input. Unknown fields should remain unknown. Use expert annotations where available and identify inferred ones.

- **Passage identity:** work, section, witness, edition, editor/translator, original sequence and provenance. Record whether text is a direct witness transcription, a reconstructed edition, or unattributed user input.
- **Input layer:** script/language variety, exact supplied text, transliteration convention and any phonemic transcription. Keep token/span alignments across representations. Do not erase capitalization that marks heterograms or silently replace one editor's convention with another.
- **Reading choices:** lemma candidates, heterogram status, Iranian complement, alternative readings, emendations, gaps, supplied text, and the scholar/evidence responsible for each choice.
- **Clause meaning:** predicate, participants, coreference, explicit versus omitted arguments, negation scope, modality, time/aspect and relation to neighboring clauses. A morphological tag is evidence for an interpretation, not the interpretation itself.
- **Sense and register:** contextual sense ID, technical concept, phrase-level idiom, proper name/title, genre and date/layer. A definition may be more faithful than a misleading familiar equivalent.
- **Textual voices:** speaker/authority; quotation, inherited translation, commentary, paraphrase and editorial explanation. Preserve links to Avestan passages where relevant.
- **Target rendering:** English and Farsi translations aligned with the chosen reading; legitimate alternatives; words supplied for readability; unresolved ambiguity and supporting references.

This does not require a rigid parser between input and translation. It specifies information the system should preserve or expose when it affects meaning. A model may propose readings, but a generated gloss must retain its status as a proposal.

## What remains ambiguous, and how experts resolve it

**Written form versus reading.** The heterographic and historically ambiguous writing system can support multiple interpretations. Experts compare grammatical fit, parallel passages, attested vocabulary and editorial evidence. When the input is already a phonemic transcription, evaluate that given reading first and label any proposed correction. PH02–PH05 support this distinction.

**Who acted, and on what.** Omitted subjects/objects, pronominal reference and ergative constructions can leave alternatives. The UD description warns that active/passive interpretation can require context; the Yasna study demonstrates such adjudication in actual colophons. Do not add an agent merely because English prefers one. PH06–PH08.

**Which textual voice is speaking.** A Zand passage can preserve inherited Avestan structure and then explain it in more idiomatic Middle Persian. A faithful translation should represent the supplied commentary, including disagreement, rather than silently substitute the modern translator's reconstruction of the Avestan original. PH09.

**Which institution or concept is intended.** The lawbook distinguishes pledging the substance of property from pledging its usufruct. Collapsing both into a loose modern label loses the legal relation. Likewise, importing an unrelated theological scheme into gētīg/mēnōg distorts meaning. Use attested domain definitions and keep uncertainties explicit. PH10, PH12.

**Which text is being translated.** A variant or editorial supplement is not simply a spelling error. Compare witnesses and editions where possible; some sources survive in a single incomplete witness, so certainty may be unavailable. Register and genre also vary within the surviving literature. PH08, PH10–PH11.

## Proposed error taxonomy for expert review

| Code | Material translation error | Annotation/evidence needed |
|---|---|---|
| READ | Wrong reading, or an editorial reading presented as certain | Supplied form, reading candidates, convention and evidence |
| HET | Literal Aramaic interpretation; lost Iranian complement | Heterogram/phonetic segmentation and Iranian lemma |
| ROLE | Agent/patient, possessor or beneficiary reversed | Predicate arguments and coreference |
| ELL | Invented participant or content while expanding ellipsis | Explicit versus inferred constituents; neighboring context |
| GRAM | Changed polarity, modal force, temporal relation or aspect | Clause scope and grammatical alternatives |
| TERM | Flattened legal, ritual or theological term | Attested sense, domain and definition |
| VOICE | Commentary fused with quotation or another authority | Textual layers and attribution |
| VAR | Variant, lacuna or conjecture silently repaired | Witness and editorial apparatus |
| REG | Anachronistic or genre-inappropriate interpretation | Date/layer and genre/register |
| NAME | Proper name, title or patronymic misread as ordinary vocabulary | Entity identity and relational analysis |

This is a proposed taxonomy, not an existing validated scoring instrument. Annotators should also record acceptable alternatives and irreducible ambiguity. A translation is not erroneous merely because it differs from one scholarly edition's preferred wording.

## Authorities, reference works and one-hop checks

Institutional credentials were verified through [Harvard for Skjærvø](https://nelc.fas.harvard.edu/people/p-oktor-skjaervo), [Göttingen for MacKenzie and Kreyenbroek](https://www.uni-goettingen.de/en/132806.html), [FU Berlin for Macuch](https://www.geschkult.fu-berlin.de/en/e/iranistik/mitarbeiter/ehemalige/macuch/index.html), [BBAW for Durkin-Meisterernst](https://turfan.bbaw.de/mitarbeiter-en.html), [SOAS for Khanizadeh](https://www.soas.ac.uk/about/mehrbod-khanizadeh), [Bochum for Jügel](https://ceres.rub.de/de/person/tjuegel/) and [Rezania](https://khk.ceres.rub.de/de/person/kianoosh-rezania/), [Sapienza for Cereti](https://research.uniroma1.it/user/5306), and [Hebrew University for Shaked](https://iias.huji.ac.il/people/shaul-shaked). Historical affiliations do not imply present availability.

The MPCD bibliography was followed one hop to Rezania's original 2020 article; the UD citation was followed to Jügel's 2015 publisher record. MPCD's methodology names MacKenzie's *A Concise Pahlavi Dictionary* (1971) and Durkin-Meisterernst's *Dictionary of Manichaean Middle Persian and Parthian* (2004). Göttingen independently identifies MacKenzie's dictionary as a standard reference; its [Oxford bibliography](https://academic.oup.com/edited-volume/34676/chapter/295531748) records the corrected 1986 reprint. These books were identified as reference resources, not read in full or treated as interchangeable across corpora.

Harvard's teaching-material link failed during this check. No claim here depends on having read Skjærvø's primer. Several MPCD pages were available through indexed page text while direct opening failed; their descriptions establish scholarly methodology, not live corpus export completeness.

The most useful next philological deliverable is a small, adjudicated set of authentic passages exhibiting the errors above, with alternate readings and reasons. Its purpose is to test faithful interpretation, not to force scholarly uncertainty into a single synthetic answer.
