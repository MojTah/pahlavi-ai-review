# Book-access follow-up — 2026-09-27

Scope: bounded public publisher, author and university/library access checks. No accounts, payments, whole-book PDF downloads, corpus ingestion or changes to training/evaluation data. This records access and inspected coverage, not a review of entire books.

## Useful access confirmed

**P. Oktor Skjærvø, Pahlavi Primer (2020) / Introduction to Pahlavi.** The [author's profile](https://harvard.academia.edu/POktorSkjaervo) links a [public HTML preview](https://www.academia.edu/72410048/Pahlavi_Primer_2020_1_). No login or PDF download was used. This third-party author route establishes readable access, not an open licence.

Inspected Lesson 1: script, spelling, transliteration/transcription, grammar and glossary (printed markers through p.10). Extracted native glyphs are visibly corrupted; they are unsuitable as script labels.

Parent-requested targeted follow-up found these five forms with senses. Page locators below follow extracted printed markers, not PDF-image verification. [Same author-linked preview](https://www.academia.edu/72410048/Pahlavi_Primer_2020_1_).

| Form | Sense; precise section locator |
|---|---|
| xrad | wisdom; Lesson 15, Text 15.4, Dk.9.60.4–5, p.305 |
| frazend (frazand) | offspring, child; Lesson 7 glossary, p.97 |
| xwāstag | property; Lesson 19, “Time,” MHD.41.4 example, p.419 |
| ruwān | soul; Lesson 5, relative pronouns, AWN.99.3 example, p.52 |
| hunsandīh | agreement; Lesson 19, “Time,” MHD.6.6 example, pp.419–420 |

Compared with [local Nyberg checks](scholarly-checks.json), the first four corroborate generic senses at the candidate spellings. This does not prove universal d/t, g/k or w/v normalization. The fifth is a different contextual sense, not confirmation of the proposed contentedness label or Nyberg form equivalence. No contextual Persian label was adjudicated.

The [official Harvard faculty page](https://nelc.fas.harvard.edu/people/p-oktor-skjaervo) confirms the scholar and links teaching materials at `https://www.fas.harvard.edu/~iranian/`. That legacy link failed: web retrieval reported HTTP 404; an ordinary unauthenticated GET reported HTTP 403. I stopped using it. The working author-linked 2020 preview is distinct from the older 2007 Introduction circulated elsewhere.

## Publisher grammar: identified, chapter text unavailable

**Desmond Durkin-Meisterernst, Grammatik des Westmitteliranischen (Parthisch und Mittelpersisch), Grammatica Iranica 1 (2014).** [Official publisher record](https://austriaca.at/7556-8); [official contents](https://austriaca.at/7556-8inhalt). Print ISBN 978-3-7001-7556-8; online ISBN 978-3-7001-7605-3. Script chapter: pp. 29–84; morphology starts p. 149 and the next chapter starts p. 261.

The publisher describes combined Middle Persian/Parthian coverage, including inscriptions and Manichaean evidence; it explicitly excludes ninth-century scholastic Zoroastrian literature. Thus coverage must be checked against each project text even after access is obtained. This is publisher-description evidence, not inspection of its grammatical arguments. [Official chapter record and description](https://austriaca.at/?arp=0x002fa4ec).

Exact access diagnostics:

| Observed publisher URL | Actual result |
|---|---|
| `https://austriaca.at/0xc1aa5572%200x002fa4ec.pdf` | Web tool: empty HTML text. Ordinary HEAD: HTTP 200, `text/html; charset=UTF-8`, length 627. One ordinary GET: 627 bytes of HTML/JavaScript invoking `loginDialogDiv`; not a PDF. |
| `https://austriaca.at/0xc1aa5572%200x002fa4ee.pdf` | Web tool: empty HTML text. Ordinary HEAD: HTTP 200, `text/html; charset=UTF-8`, length 627. No further GET attempted after the first chapter revealed the login flow. |
| `https://austriaca.at/?arp=0x002fa4ee` | Web-tool chapter-abstract click: cache-miss failure. |

No login flow was invoked and no chapter body was read. A `.pdf` URL and HTTP 200 alone did not establish access. A library-held or publisher-authorized copy is the unresolved route for these chapters.

## MacKenzie: strong historical provenance, no working lookup established on27 September

**28 September update:** a working public MPCD/Kosh entry lookup and its full XML are now verified in the [new access receipt](../mackenzie-access-20260928/README.md). This supersedes the lookup gap below, not the historical link failures or the unresolved full-edition/extraction qualification.

**Later28 September, at the user's request:** actual English and Persian print scans were acquired for local reading; [PDF receipts](../mackenzie-access-20260928/pdf-access.json) preserve their identities. The English scan includes the corrected1986 copyright page. Reading/extraction review remains partial and no blanket reuse license is established. This supersedes the earlier absence of a local MacKenzie PDF, without rewriting the27 September decision below.

**D. N. MacKenzie, A Concise Pahlavi Dictionary, Oxford University Press, 1971; preferably the 1986 reprint with Addenda and Corrigenda.** Durkin-Meisterernst's [Iranica biography](https://www.iranicaonline.org/articles/mackenzie-david-neil/) explicitly records MacKenzie's consent to digitization, the Cologne search service and incorporation into TITUS. This supports the provenance of that historical digitization; it does not license any unrelated scanned copy or establish current bulk/training rights.

The old Cologne URL `https://www.uni-koeln.de/phil-fak/indologie/lil/cpd-search.html` returned HTTP 404 in an ordinary GET. The cited TITUS directory `https://titus.uni-frankfurt.de/texte/etcs/iran/miran/mpers/` returned HTTP 403. The [TITUS general catalogue](https://titus.uni-frankfurt.de/texte/texte2.htm) remains readable, but a current MacKenzie dictionary-entry endpoint was not established in this bounded search. Cologne's present `cpd.uni-koeln.de` is the **Critical Pāli Dictionary**, not this Pahlavi dictionary; it must not be substituted.

The [Smithsonian catalogue](https://www.si.edu/object/siris_sil_864678) verifies a library record, not open book access. A Parsianjoman scan is known, but its hosting authorization was not established; it was neither downloaded nor offered as an authorized edition.

## Concrete next access request

For an immediate reading route, use the author-linked **Skjærvø Pahlavi Primer (2020)** preview above. For the user's offer to locate a book, the first precise unresolved title is **MacKenzie, A Concise Pahlavi Dictionary, the 1986 corrected reprint**. A legitimate copy would permit inspecting cited entries and their notes; a separate decision is still needed before systematic extraction. Second priority is access to the script and morphology chapters of **Durkin-Meisterernst (2014)**. No book is currently admitted as training supervision, and no benchmark or index was modified.
