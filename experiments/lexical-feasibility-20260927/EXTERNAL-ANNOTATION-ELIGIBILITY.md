# External annotation eligibility — 27 September 2026

**Decision:** Oxford's published Pahlavi record pages are operationally suitable for a small, attributed source-witness inspection now. The exact June 2026 Zenodo release is **CC BY 4.0**. MPCD does **not** yet supply a verified accessible annotation witness through the routes checked here; do not substitute its preliminary working translations or its empty UD release scaffolding for published linguistic annotation.

No TRAIN overlap was established in this review. Therefore **no new external item is approved as a TRAIN-overlapping annotation witness**, and nothing is admitted to training. Root can select a few already archived Oxford records by matching TRAIN-only source/work identifiers, then inspect the cited published layers. No held-out answers should enter that selection.

## Oxford Invisible East: rights verified, small-record access demonstrated

An unauthenticated GET of [Zenodo record metadata](https://zenodo.org/api/records/20490171) succeeded with **HTTP 200**, returning 5,271 bytes of metadata, not the corpus file. Relevant exact fields were:

```json
{
  "id": 20490171,
  "metadata": {
    "doi": "10.5281/zenodo.20490171",
    "publication_date": "2026-06-01",
    "version": "1.2",
    "access_right": "open",
    "license": {"id": "cc-by-4.0"},
    "creators": [{"name": "Invisible_East", "affiliation": "University of Oxford"}]
  }
}
```

This resolves the license uncertainty left by the rendered landing page in `RESEARCH-INSTITUTIONS-IRANIAN.md`; that earlier report was not edited. The [release landing page](https://zenodo.org/records/20490171) describes a complete JSON export intended for computational research reuse. Its corpus-file link and archive endpoints were **not followed**.

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) permits sharing and adaptation, including commercial use, subject to attribution, the license link, and indication of changes; it gives no warranty over other rights. This verified declaration applies to **that release**, not automatically to every later live revision, independently hosted manuscript image, or source edition. Oxford's separate [citation guidance](https://www.invisible-east.org/about/cite/) explicitly welcomes use of metadata, transcriptions and translations, asking for shelfmarks, original publications and the contributing editor's credit. This supports the narrow inspection proposed here without inventing a blanket license for all related materials.

**Operational example — one record only, research-exposed:** [IEDCID1024 / Bancroft Library Berk. 67, recto](https://www.invisible-east.org/corpus/1024/). The public page returned metadata plus four numbered Pahlavi transcription lines and corresponding English translation lines. It displays:

- Middle Persian / Pahlavi-script language identification and a document shelfmark;
- classification **Gold**, explicitly defined as external peer review through journal/book publication;
- principal editor Thomas Benfey, source-publication references and a last-updated date;
- uncertainty and lacuna markers retained in both linguistic layers;
- DOCX, JSON and XML export controls, which were not activated.

The cited publications are Weber 2013, pp. 174–176, and Benfey 2024, pp. 398–404. Published review status does not eliminate disputed readings. This example demonstrates available layers and access, not verified TRAIN overlap, modern-Persian target correctness, morphology/dependency annotation, or an untouched test item. It was already exposed in the previous institutional review and must remain labelled **research-exposed**.

**Reuse the archive:** `data/README.md` records 158 Oxford Middle Persian catalogue records already saved at `sources/local/public-texts-2026-09-20/invisible-east/middle-persian.json`, of which 14 contain transcription and translation and 10 transliteration. These are local archive counts, not counts inferred from today's filtered webpage. Do not recollect the corpus. The June licensed release and September archive have different dates; byte/item equivalence was not checked and should not be claimed.

**Exact routes and proof level:** `/corpus/1024/` is directly demonstrated public record access. `/corpus/downloaddata/json/` is explicitly named in the Zenodo metadata as the export source, but it is a **bulk** route and was not requested. A per-record export endpoint was not guessed from the UI. No public linguistic-annotation API beyond these observed interfaces was verified.

## MPCD: usable project evidence, no released annotated witness verified

The [FU Berlin institutional page](https://www.geschkult.fu-berlin.de/en/e/iranistik/forschung/MPCD/index.html) remains accessible. It documents manuscript-grounded Pahlavi analysis and Avestan–Zand interlinking. Its illustration of Yasna 59.18–19 is a **project illustration**, not a fetched annotated record or a verified TRAIN match.

The linked [MPCD homepage](https://www.mpcorpus.org/) returned **HTTP 403** through the web tool. The institutionally linked [morphology handbook](https://gitlab.dh.uni-koeln.de/mpcd/handbooks/-/wikis/Handbook%20Morphology) returned **HTTP 500** on a direct public read; a prior rendered read produced only a shell. No authentication, guessed endpoint, repeated bypass attempt or token/translation collection followed.

The existing `sources/external-access-gaps.json` supplies a separate, dated operational observation from **20 September 2026**: a normal browser received HTTP 200 from the exact metadata route `https://www.mpcorpus.org/api/texts/?page_size=200`, reporting 102 texts. This is **prior metadata-only proof**, not a current successful call or access to annotations. The same record preserves this editorial caution:

> Preliminary corpus; preannotations can be erroneous or hypothetical. Working translations should not be quoted without consulting the responsible philologist.

The notice is quoted from our preserved access record, not independently reread from the blocked site today. It is a material scientific-use limit; no contact or permission request was made. The [2023 author paper](https://elex.link/ojs/index.php/elex/article/view/27) describes REST/GraphQL architecture and future TEI/CoNLL exports/LLM integration. Architecture descriptions do not establish a released endpoint for a particular text. Its article license is not a license for the underlying corpus or dictionary.

**Alternate public release check:** [UniversalDependencies/UD_Middle_Persian-MPCD](https://github.com/UniversalDependencies/UD_Middle_Persian-MPCD) is public. Its README declares CC BY-SA 4.0 and an initial UD 2.18 release, but still contains placeholder descriptive sections. A fresh, unauthenticated [recursive tree metadata request](https://api.github.com/repos/UniversalDependencies/UD_Middle_Persian-MPCD/git/trees/master?recursive=1) returned HTTP 200 with:

```text
tree: c153be545a37dc780b8b6cdad7053257a6d2d674
truncated: false
files: CONTRIBUTING.md, LICENSE.txt, README.md, eval.log, stats.xml
CoNLL-U files: 0
```

The tree matches the repository's previously recorded state. Metadata-response SHA256: `cde001c1096cab9b030892d4833482d8527431996c7c0764eabca83194c0199c` (1,438 bytes). The [tags metadata](https://api.github.com/repos/UniversalDependencies/UD_Middle_Persian-MPCD/tags) listed only `r2.1`; no archive was fetched. The GitHub license-file and README-file web views failed to render, although the repository's rendered README supplied the declaration. **The declared repository license cannot make nonexistent annotation files usable or license the separate MPCD working corpus.** This check covers the current default tree, not an exhaustive search of every historical branch.

**MPCD disposition:** corpus/dictionary license remains unverified; currently accessible handbook/schema content was not obtained; current public token-level annotation/export route was not established. This is a bounded access finding, not proof that MPCD has no annotation internally or no access in an ordinary browser. Stop here rather than infer undocumented routes.

## Concrete next inspection boundary

| Resource | Inspect a few published witnesses now? | Conditions and exclusions |
|---|---|---|
| Oxford existing local archive and cited public records | **Yes, for research/source checking** | Root first verifies source/edition overlap using TRAIN identifiers only; choose at most five records with nonempty published layers and retain editor/edition citations. Mark all seen examples research-exposed. No bulk acquisition or dataset admission. |
| Oxford as gold morphology or modern Persian translation | **No** | Demonstrated layers are transcription/English translation and metadata, not adjudicated grammatical analyses or Persian gold. |
| MPCD live preannotations/working translations | **Not established as ready** | Need an actually accessible exact witness, status and applicable terms. Honor the archived caution; do not quote working translations as published evidence. |
| UD Middle Persian–MPCD current tree | **No usable annotation passages** | Zero CoNLL-U files despite release metadata. |
| Published MPCD methodology | **Yes, as methods evidence** | Useful for schema design; not a replacement for missing sentence-level annotations. |

Only one arbitrary public text record was revisited. No other passage was sampled; no held-out reference set, credentials, accounts, Drive/Dropbox material, corpus download, model call or training action was used. The only written artifact is this eligibility note. Existing source archives and shared plans remain unchanged.
