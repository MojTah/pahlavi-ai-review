# Kanheri article: direct source qualification

**Result: all six inscriptions accounted for; no newly independent usable witness found.** Five published transcription/translation blocks were recovered directly from the article. The sixth inventory entry, the article’s inscription5, has no readable published transcription or Persian translation. Six clear scope occurrences collapse to **four distinct source/target types**; they remain pending independent review and training release. One additional movement clause is explicitly restricted because the author describes a conjectural reading in the commentary.

This is an earlier scholarly article, not the unavailable1398/2019book. The article itself can establish source-supported supervision for its defensible scopes; it does not verify the later edition’s exact wording or clear all95 source-edition holds.

## Source and inspection

Source: Cyrus Nasrollahzadeh, **کتیبه‌های پهلوی ساسانی در غار کانهری در هند**, زبان و زبان‌شناسی. The first PDF page gives received17/01/1395 and accepted05/10/1395. The author’s publication listing identifies2017; the UCI page’s bibliography differs. Preserve the earlier-article identity rather than silently settle every bibliographic discrepancy. The hosted filename says volume12,issue24,107–138, but the PDF has33pages and visibly ends printed139.

- [Institutional source page](https://sites.uci.edu/sasanika/ka%E1%B9%87heri-caves/).
- [Ordinary public PDF](https://sites.uci.edu/sasanika/files/2026/05/LSI_Volume-12_Issue-24_Pages-107-138.pdf).
- Local PDF: `sources/local/public-texts-2026-09-20/qualification-source-search-20260928/raw/b385981ef422d96884dc19c958c274bf2e9efb0aefd923d83dbb71a2ae9fca1f.pdf`.
- PDF SHA256: `720d3db41ea76865c65d4a6875f0c03bf785dcae1a37f20dd6365a6e1501800f`.
- Visual inspection: PDF9–14/printed115–120 for all six main entries; PDF20/printed126 and PDF23/printed129 for material commentary; PDF27/printed133 for the numbered drawings4/5. Renders and hashes are bound per record under the assigned source archive’s `inspection/kanheri/` folder.

Published Latin transcription was extracted and visually checked. Numbered raw blocks are retained, including the first inscription’s unusual12–23 transcription numbering and doubled `ud ud`. Plain source fields only remove printed line numbers and join linebreaks. Persian was manually transcribed from page images with normalized whitespace/joiners and omitted vocalization marks; wording, numerals, brackets, parentheses, ellipses and question marks are retained. This is not a claim of diplomatic typography. No spelling, date, person name or disputed reading was silently corrected. An independent visual reviewer should compare the frozen fields against the source images.

## Witness decisions

| Article inscription | Exact pages: PDF / print | Existing Parsig match | Decision |
|---|---|---|---|
|1 | Transcription and target10/116; introduction9/115; uncertainty discussion14/120 |201001001 | Hold full block: source gives300+70+8=378, but printed Persian says376. Introductory prose says378; Parsig repeats376. Opening prayer is conjectural; restorations, uncertain names and terminal damage remain. The opening formula and the separate complete arrival clause are source-supported unaffected scopes. |
|2 | Transcription11/117; target11–12/117–118; damaged ending20/126 |201002001 | Hold full block: restored `murw[āg]?`, bracketed kinship interpretations and names. The printed dated arrival clause is clear within its scope:378,Ābān,Mihr,coreligionists’ arrival. Opening formula also clear. |
|3 | Transcription12–13/118–119; target13/119; commentary20/126 |201003001 | Hold full block and restrict its movement clause: commentary explicitly reads `gyāg` by analogy with1–2 and notes that the photo could begin withm. That uncertainty is absent from the main transcription. Unresolved `Yazadān’/hšlc`/Persian `یزدان-؟` also remains. Opening formula alone is clear. |
|4 | Transcription/target13/119; disagreement23/129 |**201005001** | Numbering alias, not an addition. The article’s fourth inscription is the text that the site calls fifth. Patronymic target is the author’s contested interpretation: West took Šahrayār and Māhfarrōbay as two people; the author infers person-and-father from analogy/damage. Keep as restricted scholarship, not a single undisputed relationship label. |
|5 | Description13/119; drawing27/133 |No usable counterpart | No published transcription or Persian translation; only damaged letters/drawing. Preserve an inventory/hold record with null source and target. Do not import201005001 here: its text belongs to article4. |
|6 | Transcription/target14/120 |201006001 | Source-supported **patronymic name phrase**, not a full sentence: Ābāngušnasp ī Farroxān. The article reports two physical occurrences, but one published text type is represented; do not double-count independent supervision. |

The5→4 alias is established by the actual source string and translation, not merely a similar title. Local201005001 has `sāl se-sad nawad ī yazdgird šahryār māh-farrōbay` and the same Persian father reading. It therefore does not demonstrate an additional fourth-inscription discovery. The real unreadable fifth supplies no usable translation pair.

## Qualified scopes and counting

The JSONL contains six parent records and seven nested source-bound scopes. Exact character spans are recorded into each parent source/target; assertions verify them.

- Three occurrences of **pad nām ī yazad → به نام ایزد** collapse to one formula type with three provenance links.
- One inscription1 **hamdēnīgān … āmad hēnd** arrival clause excludes the conflicted date and uncertain prayer/name list.
- One inscription2 dated arrival clause excludes its later names and reconstructed ending. Its shared arrival formula overlaps inscription1; these are related witnesses/formulas, not independent experimental observations.
- One inscription6 name phrase repeats the full clear parent scope and is counted once, not as parent-plus-child additions.
- Inscription3’s dated movement clause is preserved separately as a **restricted conjectural scope**, excluded from the clear-type count.

Thus there are **four distinct clear scope types from six occurrences**, comprising one formula, two related finite-clause types and one name phrase. This does not mean four novel contexts, four new full inscriptions, or six independent learning examples. Five usable article witness families were already present in Parsig; **new usable witness count=0**. The concrete gain is independent direct-edition evidence and defensible scope boundaries for existing material. These small formulaic additions alone do not demonstrate a solution to model quality.

## Edition, leakage and release boundaries

`source_text` and `target_text` come from this article. The existing site’s source/target fields were read only to establish non-protected201 overlap and disagreements. Examples retained separately: the article’s doubled `ud ud` versus the site’s single one; the site’s extraī afterMihrayār in inscription2; article `murw[āg]?`/مروا versus site `murw(?)`/مور; the unresolved terminal inscription3 name. The site attributes its translations to the2019book, but that book was not inspected: these are **article-versus-site differences**, not verified article-versus-book findings.

Known protected work IDs were checked against `data/unified-corpus/build.py:24`;201 is not among the fixed16. No protected answers were accessed. This metadata screen does not replace final release-wide witness/duplicate checks. The public institutional PDF establishes access; an explicit reuse license was not established, so corpus redistribution remains a rights question. No data were admitted to training and no previous corpus, candidate, benchmark or source receipt was changed.

## Validation and handoff

Validation performed with the existing codex-science Python and standard-library assertions: six unique parent IDs; expected five source/target blocks plus one null/null unreadable entry;5textual witness matches; exact nested source/target span reconstruction;6eligible scope occurrences/4distinct pairs;1restricted scope; preserved378/376 contradiction, doubled `ud ud`, uncertainty markers and4→201005001 alias; all referenced PDF/image hashes; all training flagsfalse. **PASS.** This is structural evidence plus one agent’s visual extraction, not independent semantic certification.

Frozen candidate SHA256: `d01b002f17641f3d62a98e67538bd79ba12712624ca62cd5645ba82ec7bec242`. No new downloads, accounts, paid jobs, model execution or external delegation were used for this extraction. Independent visual/lineage review is the next concrete gate before any release decision.
