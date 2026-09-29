> **Superseded acquisition status, 20 September 2026:** the direct source-text collector has now saved all 126 Parsig records and their supporting text metadata. This earlier study/IDM guide is retained as history. Current coverage, language corrections and gaps are in [the data guide](../data/README.md).

# Parsig Database archive with IDM

Prepared 20 September 2026. Target: a local research archive of the public [Parsig Database](https://parsigdatabase.com/), with its source credits. An archive and a completed language study are separate results.

## Run the site grab

1. Open IDM's **Grabber**. Name the project `Parsig Database 2026-09-20` and start at `https://parsigdatabase.com/?lang=fa`. Choose its complete-website template.
2. Save into `[USER_HOME]\Documents\ChatGPT\Pahlavi language\sources\local\parsig-idm-2026-09-20`. Preserve original relative subfolders and enable local-link conversion for offline browsing.
3. Restrict discovery and downloads to Parsig's domain. Include its subdomains: the reader uses `mpdb.parsigdatabase.com`. Do not follow the footer into other scholarly websites.
4. Include pages, scripts, styles, fonts, images, PDFs and data responses; avoid an images-only filter. Explore first, then download the discovered files. Keep failed URLs in the report.
5. IDM offers **Process Javascript** for script-generated links. It can help discovery, but does not establish that this particular reader's dropdowns, requests and annotations will be captured. Use that option only for a site you trust, as IDM advises.

These settings follow IDM's [Grabber wizard documentation](https://www.internetdownloadmanager.com/support/idm-grabber/grabber_wizard.html) and [JavaScript guidance](https://www.internetdownloadmanager.com/support/idm-grabber/grabber_prjava.html). They have not been tested in this user's IDM installation. Suggested download load: one active file at a time and one connection per file, where available.

## The supplied lists

- [parsig-entry-pages.txt](parsig-entry-pages.txt): verified public entry pages, one URL per line. These are starting points, **not 126 independent text downloads**. To import the list use **Tasks → Import → From text file**, then review IDM's detected URLs. [Official import instructions](https://www.internetdownloadmanager.com/support/import_downloads.html)
- [parsig-record-checklist.md](parsig-record-checklist.md): every observed record ID and title. Use this to check the archive's actual contents.
- [Source inventory](../sources/parsig-live-inventory.json): machine-readable record list and separate reading coverage.

Importing the URL list downloads those pages; it does not make IDM traverse each corpus selection. Use the Grabber for discovery. No guessed per-record download URLs, passwords or authorization headers are included.

## What completeness must mean here

The live reader has **126 top-level records**: 40 Zoroastrian, 2 Zand, 25 private-inscription and 59 Manichaean records. Chapters, paragraphs, word annotations and edition/manuscript pages need their own coverage counts. Several records are selections or fragments. All currently published site contents would still be smaller than the whole historical language corpus.

Observed limitations of this site:

- Changing the text selection does not change the reader URL. Downloading that URL once does not enumerate its 126 selections.
- The frontend retrieves content from a separate data service. An unauthenticated request to the observed group-list endpoint returned HTTP 401. No manually extracted credential was used. Do not treat a saved error response as corpus data.
- The two critical-edition images tested for record 120 were embedded `data:` images, not independent HTTP image links. A conventional file-link list cannot represent those pages directly.
- The Book Pahlavi display depends on a legacy font. Retain the font and original script strings together; a page that looks blank or displays Arabic characters may have lost its rendering dependencies.

After the grab, check actual local content for these samples:

| Sample | Minimum evidence |
|---|---|
| 119, داروی خرسندی | Units 0–9, translation credits, and the annotation for occurrence `119000001003` |
| 120, اندرز بخت آفرید | Units 0–12; correction note on §11; both edition pages 81–82 |
| 207, صلیب هرات | Both faces, with uncertain names/date and commentary preserved |
| 302, زند خرده اوستا | All four offered selections, not just the first selected chapter |
| 506, Manichaean a | Units 1–5, fragment ending and manuscript references preserved |

Check with internet disconnected, or inspect the saved files directly: a saved HTML page that still loads live API data is not an offline archive. Reconcile all 126 records against the checklist, then count their chapters, paragraphs, translations, annotations, images and introduction pages. Hash retained files and record failures, missing content and duplicate responses. Do not mark any checkbox from an HTML filename alone.

If the samples are missing, keep the downloaded files. They remain useful for static documentation and rendering assets. Supplement the corpus through an authorized structured export or ordinary browser reading; do not repeatedly run a broad grab and assume success from file count.

## Attribution and study

Credit Pārsīg Database, its project lead فرزانه گشتاسب, the database team and each edition/translator. Preserve copyright and source notices. See [CREDITS.md](../CREDITS.md). The local archive folder is excluded from Git; this guide and checklist contain no copied corpus archive.

After acquisition, the knowledge-base work still requires contextual Farsi/English senses, grammatical analysis, variants and reading checks. Progress lives in the [dictionary plan](../dictionary/README.md) and [study ledger](../kb/study-status.md).
