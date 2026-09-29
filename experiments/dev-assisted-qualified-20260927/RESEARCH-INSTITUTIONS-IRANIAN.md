# Institutional exemplars for Pahlavi translation research

Primary-source review, 27 September 2026. Public institutional/project pages and an author research paper were inspected. No corpus files were downloaded, no account or Drive access was used, and no institution was contacted.

**The strongest analogues are MPCD for Zoroastrian Pahlavi analysis and Oxford's Invisible East for traceable documentary editions.** Their main contribution is an evidence structure: distinguish the manuscript, its reading, linguistic interpretation, translation and editorial uncertainty. The inspected sources do not supply a validated Pahlavi→Persian neural translator. Digital editing, automatic collation, searchable dictionaries and semi-automatic annotation must not be reported as demonstrated machine translation.

| Priority for our text-based task | Project and institution | Relevant contribution | Principal boundary |
|---|---|---|---|
| 1 | MPCD — Ruhr-Universität Bochum, Freie Universität Berlin, Universität zu Köln | Manuscript-grounded Zoroastrian Middle Persian corpus, linguistic annotation, dictionary, Avestan–Pahlavi interlinking | Corpus/dictionary project; complete current release, reuse terms and live API availability unverified |
| 2 | Invisible East Digital Corpus — University of Oxford | Actual Pahlavi documentary transcriptions and English translations, editorial provenance and uncertainty, downloadable structured-data interfaces | Documentary register; incomplete translation coverage; not modern-Persian gold |
| 3 | MIRTEXT / Digital Turfan Archive — BBAW and Staatsbibliothek zu Berlin, with Göttingen KOHD cooperation | Revised Manichaean Middle Persian/Parthian readings, manuscript/edition locators, explicit damage/conjecture notation | Distinct script, religious corpus and language mixtures; restrictive copyright notice |
| 4 | Corpus Avesticum Berolinense (CAB) — Freie Universität Berlin | Witness-based editions, apparatus, grammar, ritual context, some Pahlavi translation layers | Principally Avestan; not interchangeable with Middle Persian |
| 5 | Corpus Inscriptionum Iranicarum (CII) — international scholarly organization, main series published through SOAS | Critical epigraphic/documentary editions, plates, glossaries and multilingual versions | Primarily published books; no verified open corpus/API |

## 1. MPCD: closest match to the Pahlavi linguistic problem

The FU Berlin project page identifies the three university partners and the DFG long-term period **2021–2030**. It describes texts based directly on authoritative manuscripts. Its own work covers Zand, ritual directions, related treatises and Dēnkard 8–9. Planned word-level links connect Pahlavi Zand to Avestan originals in CAB. Those links concern ancient translation and commentary, not Pahlavi–modern Persian parallel sentences. [FU Berlin project description](https://www.geschkult.fu-berlin.de/en/e/iranistik/forschung/MPCD/index.html).

Bochum's dated March 2024 description gives a target of approximately **54 texts / 700,000 tokens / 7,000 dictionary lemmata**, with transliteration, transcription, manuscript photographs in development, and orthographical, morphological, syntactic and semantic annotation. It explicitly describes **semi-automatic annotation based on Universal Dependencies**. These are project-scale targets, not a verified count of fully released or human-adjudicated records today. [Bochum institutional description](https://ceres.rub.de/en/news/vacancy-phd-candidate-mfx-3-for-years-298725-hours-per-week-tvl-e13/).

The team's 2023 paper describes dictionary-to-corpus-to-folio navigation and REST/GraphQL APIs. TEI/CoNLL corpus exports and LLM integration appear as future developments; this is not evidence that a trained translator was released. Multiword expressions and technical meanings are explicit dictionary design concerns. The public article is licensed **CC BY-SA 4.0**; that license cannot be silently extended to its referenced corpus, manuscripts or dictionary. [Author paper and article license](https://elex.link/ojs/index.php/elex/article/view/27), [full paper inspected](https://elex.link/ojs/index.php/elex/article/download/27/14/91).

**Access finding:** the [project homepage](https://www.mpcorpus.org/) was discoverable but returned HTTP 403 in the browsing tool. The [institutionally linked morphology handbook](https://gitlab.dh.uni-koeln.de/mpcd/handbooks/-/wikis/Handbook%20Morphology) returned only a minimal shell. Neither result proves resources are private or unavailable to ordinary users. No current corpus-wide license or operational public API endpoint was verified. No authentication or workaround was attempted.

**Transfer recommendation — inference:** preserve source spelling and scholarly transcription as distinct fields; connect lemma/sense/grammar claims to attestations rather than replacing a difficult word with a contextually plausible synonym. Adopt the linking principle without assuming we need the same software stack.

## 2. Invisible East: directly inspectable Pahlavi editions and structured access

Oxford's project describes a multilingual historical corpus with metadata throughout and full transcriptions/translations for a smaller subset. It includes everyday documentary material as well as literary fragments. [Oxford institutional corpus page](https://invisibleeast.site.ox.ac.uk/digital-corpus). This public [filtered corpus search](https://www.invisible-east.org/corpus/?filter_fk_corpus=16) returned **115 records**, including explicitly labelled Middle Persian in Pahlavi script. This is a result count, not a count of translated training pairs. The corpus website and its search index disagree on total corpus size; do not freeze that total from this review.

A concrete inspected example is **Berk. 67, recto / IEDCID1024**: a fiscal document with four numbered transcription/English-translation lines, retained uncertainty markers, references to Weber 2013 and Benfey 2024, principal editor, revision date and permanent URL. Its “Gold” classification explicitly means external peer review through a journal/book. It does not mean every reading is certain. The page even has conflicting rendered date fields; archival metadata still needs validation. [Exact document record](https://www.invisible-east.org/corpus/1024/).

The FAQ distinguishes physical fragments from textual documents through a many-to-many relationship, acknowledges varied editorial transcription conventions, and records original scholarship. Its older counts are internally inconsistent, so use record-level evidence rather than treating the FAQ as a current inventory. [Project FAQ](https://www.invisible-east.org/about/faqs/).

**Access finding:** public record pages expose DOCX/JSON/XML export options. A versioned [Oxford-deposited JSON release, 1 June 2026](https://zenodo.org/records/20490171), is explicitly intended for computational research reuse; only its landing metadata was read. The [citation guidance](https://www.invisible-east.org/about/cite/) welcomes use of metadata, transcriptions and translations with attribution to shelfmarks, original editions and contributing editors. This is an explicit reuse statement. A precise standardized dataset license was **not visible** in the rendered Zenodo Rights section, and a read-only metadata-API attempt failed. Do not label it CC0 or CC BY, extend the statement to every manuscript image, or infer unrestricted redistribution/training rights. The [technical page](https://www.invisible-east.org/about/technical/) links software source; software licensing is a separate matter. No data export was activated.

**Transfer recommendation — inference:** use record IDs, edition provenance, editorial status and uncertainty-bearing aligned lines as the basic review unit. Documentary material could later test domain transfer after rights and overlap checks; it should not be mixed into literary Pahlavi data simply because the language label matches.

## 3. MIRTEXT and Turfan: readings must remain attached to their witnesses

The BBAW describes a fully digitized Turfan collection of about 40,000 fragments and collaboration with the Staatsbibliothek and Göttingen's KOHD. This is a multilingual manuscript total, not 40,000 Pahlavi texts. Its academy project ended **31 December 2022**; the surviving resource must not be advertised as evidence of an ongoing funded ML programme. [BBAW project/status](https://www.bbaw.de/forschung/turfanforschung), [Digital Turfan Archive account](https://turfan.bbaw.de/dta-i.html).

MIRTEXT supplies the published Manichaean Middle Persian and Parthian textual basis of a dictionary, checked against originals or reproductions. It connects edition references, manuscript references and readings; duplicate witnesses may be combined. The documentation distinguishes lost/conjectured letters `[]`, damaged but identifiable letters `()`, editorial comments `{}`, and other additions. Composite text is not identical to any single manuscript. References attach to the first word of a line and can disappear when that word is missing; full publication history is not supplied. No aligned Persian translation corpus is claimed. [MIRTEXT documentation](https://turfan.bbaw.de/texte/mirtext.html).

**Access finding:** documentation and manuscript images are publicly presented, but the inspected [Turfanforschung copyright notice](https://turfan.bbaw.de/impressum.html) retains author copyright and requires explicit consent for republication/use beyond the permitted scope or purpose. No open corpus license or public data API was verified. Image rights and edition rights need separate treatment. The bulk textual file was not opened or downloaded.

**Transfer recommendation — inference:** retain conjecture, damage and editorial-addition markers through normalization; track all witnesses of a composite passage. Keep Parthian and Manichaean Middle Persian tagged separately from Zoroastrian Book Pahlavi. Use shared texts/witnesses to define evaluation groups and prevent duplicate material entering different splits.

## 4. CAB: an apparatus and context model, mainly for a different language

CAB at FU Berlin edits **Avestan ritual texts in their performance context**, continuing the Avestan Digital Archive. Its rationale rejects collapsing every witness into a supposedly recoverable single original and instead relates versions to historical ritual settings. It describes translations, grammatical/semantic analysis, parallels, apparatus and manuscript access using TEI. [CAB scope and goals](https://cab.geschkult.fu-berlin.de/exist/apps/cab/pages/about/introduction.html).

The current [work-progress page](https://cab.geschkult.fu-berlin.de/exist/apps/cab/pages/about/workprogress.html) separates basis edition, critical edition/grammar, apparatus, automatic collation, manuscript transliterations and Pahlavi translation layers. Some cells are unavailable: for example Y0 lacks the Pahlavi-translation layer while Y1 has it. Therefore a project-wide capability is not proof of complete coverage. A public [Avestan dictionary beta](https://cab.geschkult.fu-berlin.de/dictionaries/CAB_Avestan_Dictionary.html) is also present; Avestan dictionary entries are not Middle Persian dictionary entries.

**Access finding:** the institutional data plan specifies TEI/Unicode, manuscript metadata, gaps/substitutions and stable URLs. It promises a Creative Commons license for generated files **without naming a variant**, and a **12-month embargo** for the constituted text of print volumes. Those are plan statements, not verified release-specific licenses. No corpus download, authenticated editor or operational public API was exercised. [Institutional project/data-handling plan](https://www.geschkult.fu-berlin.de/e/iranistik/forschung/CAB/projektbeschreibung/index.html).

**Transfer recommendation — inference:** store the evidence and alternative readings alongside a selected translation; display which linguistic analysis layers have actually been reviewed. Automatic collation should not be equated with automatic semantic adjudication. Zand links may illuminate Pahlavi commentary, but an Avestan source cannot become a modern Persian target automatically.

## 5. CII through SOAS: edition authority without an assumed open dataset

CII is a UK-based international scholarly organization documenting Iranian inscriptions and documents, rather than literary texts, through the early Safavid period. SOAS publishes its main series. [SOAS institutional page](https://www.soas.ac.uk/corpus-inscriptionum-iranicarum).

Its catalogue, updated 31 March 2026, lists Pahlavi royal inscriptions with Parthian/Greek versions, Kartīr material, Dura-Europos, ostraca/papyri/parchments, and Gignoux's Pahlavi/Parthian inscription glossary. These are concrete edition, plate and lexical resources. The catalogue does not itself provide token-level alignments, complete digital apparatus or a training corpus. Ancient multilingual versions should not be treated as sentence-exact modern translation equivalents. [Exact publication catalogue inspected](https://www.soas.ac.uk/sites/default/files/2026-04/CII%20publications%20Parts%201-4%20%26%20Suppl.pdf).

**Access finding:** the institutional page offers a public catalogue and a purchase route for volumes. No open corpus license, full-text download collection or API was established. A catalogue's public availability is not authorization to digitize and redistribute its listed books. Actual uncertainty conventions and translations must be checked in each acquired edition.

**Transfer recommendation — inference:** cite the exact edition and page/line, record later revisions separately, and use relevant epigraphic glossaries to corroborate inscriptional senses. Do not apply them as universal gold for later religious literature.

## A concrete workflow to borrow

These are recommendations inferred from the institutional evidence, not claims that the institutions use our proposed ML process:

1. **Make the source unit traceable:** work/document ID → manuscript/witness → folio/line or edition locator → immutable source text. Preserve both supplied transcription and any separately justified normalization.
2. **Separate evidence layers:** attested reading, conjecture/damage, lemma candidates, grammatical analysis, contextual gloss, reference translation and proposed Persian output. Distinguish commentary from translated source content.
3. **Build small evidence packets:** retrieve only relevant attested parallels and dictionary senses with citations. Record disagreement; do not resolve it by majority voting over models or editions.
4. **Adjudicate semantics explicitly:** reviewer status should distinguish AI screening, expert review and published peer review. Require source-based checks of negation, participants, modality, quantities, omissions and additions. Keep uncertain spans and multiple defensible renderings visible.
5. **Evaluate by work/witness and domain:** group duplicates, related editions and translated versions before splitting. Report literary, legal/documentary, epigraphic and Manichaean results separately. Hold a new test set out of retrieval and tuning, and score justified uncertainty as well as accuracy.
6. **Freeze access/provenance with any future release:** resource/version/date, exact item rights, attribution and permitted uses; then verify coverage and alignments before considering ingestion. None of this review imports external texts into training.

The immediate scientific gain is stronger evidence handling and expert adjudication, not another institution's brand name or a larger pooled text count. None of the five projects establishes that our current model, another LLM, or a modern-Persian pivot can reliably translate unseen Pahlavi.

## Scope and verification limits

All supporting links above are exact primary URLs visited during this review; URLs returning shells/errors are explicitly identified. Additional read-only probes were the [IEDC homepage](https://www.invisible-east.org/), [Turfan text index](https://turfan.bbaw.de/texte.html), and the unsuccessful [Zenodo record-metadata API](https://zenodo.org/api/records/20490171). The latter was metadata only, not a corpus-file request. No Google-hosted or Dropbox links embedded in source pages were followed.

This is a bounded five-project review, not an exhaustive institutional census. Site counts, planned features, live availability and licenses have different evidence levels. Unverified means unverified, not absent or prohibited. No bulk acquisition, API integration, license negotiation, model training or human-expert quality audit was performed.
