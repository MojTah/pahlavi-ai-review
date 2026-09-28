# Local source copies

Eight PDFs are retained locally: three public reference downloads and five specifically authorized user-supplied copies. Their source locations, byte lengths, SHA-256 hashes and study coverage are recorded in [manifest.json](manifest.json). The five supplied files represent four works because the two Nyberg files reproduce the same manual.

- `oxford-persian-linguistics-preview.pdf`: publisher-distributed preview, not the complete book.
- `book-pahlavi-proposal-2014.pdf`: historical Unicode proposal with script and manuscript examples.
- `parsipy-2025.pdf`: complete 13-page toolkit paper; read in full.

The five user-supplied files are registered as [S22–S26](../kb/sources.md#user-supplied-pdfs). Their Drive originals were not modified. The local copies support this study without further Drive access. [Study coverage and findings](../kb/supplied-pdf-study.md) distinguish complete article reading, selected book study, OCR extraction and visual inspection. No source PDF is committed to Git.

[parsipy-inspection.json](parsipy-inspection.json) records the public repository snapshot, file hashes, and structural counts. Temporary software/data copies remain under ignored `tmp/`; the repository's license was retained with that local copy. No downloaded code was executed. These files are not an export of Parsig Database.

[parsig-live-inventory.json](parsig-live-inventory.json) records the 126 text options observed in the live website on 20 September 2026, their IDs, collection and actual study coverage. A browser-to-file checksum verifies the saved titles and IDs. It contains metadata and coverage, not a copy of the corpus. [The live study](../kb/parsig-live-study.md) records editions, translation credits, conventions and unresolved readings.

PDFs and temporary extraction/rendering files are excluded from Git. Copyright remains with the respective rights holders. The authored knowledge base uses brief attributed examples and original synthesis; it does not relicense these source documents.
