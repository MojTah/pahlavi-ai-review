# Local source-only training inventory — 27 September 2026

The inspected Parsig archive does **not provide a substantial new untranslated corpus**. Its 62 rows without either a Farsi or English translation field contain just **260 whitespace terms**. All are chapter-initial, sequence-zero records in work 151 (Mēnōg ī Xrad), each three or five terms long; the inspected openings are numbered-question headings. None belongs to the frozen TRAIN partition. Removing translation targets from the existing 2,237 qualified examples changes the training objective but supplies no new source material.

This is an inventory, not approval for continued pretraining (CPT). Other locally archived collections may supply material, but their language, representation, rights, deduplication and holdout eligibility have not been established by this bounded inspection.

| Pool | Source rows | Works | Whitespace terms | Characters | Exact unique source strings |
| --- | ---: | ---: | ---: | ---: | ---: |
| Raw Parsig transcription export | 4,507 | 126 | 109,854 | 641,882 | 4,489 |
| Frozen TRAIN partition, raw source counterparts | 2,613 | 78 | 55,475 | 330,186 | 2,608 |
| Frozen DEV partition, raw source counterparts | 402 | 4 | 12,444 | 68,687 | 402 |
| Frozen TEST partition, raw source counterparts | 1,019 | 12 | 30,784 | 178,953 | 1,019 |
| Raw records outside all held-out works; **not automatically admitted** | 2,952 | 110 | 62,665 | 372,924 | 2,937 |
| Outside held-out works but absent from TRAIN manifest; **unadmitted** | 339 | 60 | 7,190 | 42,738 | 329 |
| Qualified TRAIN, exact cleaned payload | 2,237 | 76 | 37,492 | 207,146 | 2,235 |
| Raw rows with neither Farsi nor English translation field | 62 | 1 | 260 | 1,434 | 62 |

Exact source-string deduplication reduces the full raw archive to **109,720 terms / 641,048 characters**, and the qualified payload to **37,488 terms**. Raw export strings retain citation and editorial material; cleaned qualified payloads do not have identical counting boundaries. These are Python whitespace-item and Unicode-character counts, **not model tokens**, lexical word counts or validated amounts of Middle Persian running prose.

## Translation availability and qualifications

Of the raw 4,507 source rows, 3,529 have a populated Farsi field only, 916 have both Farsi and a classified English translation layer, zero have English only, and 62 have neither. Thus 4,445 have Farsi and 916 have English. These are same-paragraph field associations, **not expert-validated aligned pairs**. The existing collection README documents attribution-only and defective fields; populated fields cannot be counted as usable supervision without review.

All 2,613 TRAIN-partition raw counterparts have populated Farsi fields, including 469 with English too. All 2,237 qualified examples have a Farsi target; 376 raw counterparts also carry English. The 339 unadmitted rows outside held-out works comprise 272 Farsi-only, five Farsi-and-English, and the 62 short untranslated headings. They are not 339 new untranslated passages. There are 473 raw records unassigned to any frozen partition in total; 134 occur in held-out works and remain excluded.

Raw language labels divide into 325 rows labeled Middle Persian, 4,107 labeled Middle Persian with possible quoted Avestan, and 75 labeled mixed Middle Persian/Parthian. Those labels do not resolve editorial Persian, quotations, damaged text, headings, or legacy-script representation. Original-script and transcription layers must not be concatenated as independent passages. Exact deduplication also misses citation variants, near duplicates, parallel editions and cross-archive copies.

## Split and permission boundary

The existing dataset manifest is authoritative: 2,613 TRAIN / 402 DEV / 1,019 TEST records. Its allocation groups works, duplicate groups and normalized-source similarities of at least 0.90. The union of DEV/TEST and PALREF work exclusions is 16 works; the raw archive contains **1,555 rows / 47,189 terms** from those works. Source-only CPT must exclude those works and their parallel witnesses too: dropping answers does not prevent leakage from held-out source text. Being outside this union is only a first filter, not evidence of eligibility.

The narrowest already reviewed source pool is the 2,237 qualified TRAIN payload, all recycled paired material. The broader 2,613 TRAIN allocation is only a split/identity boundary and does not undo subsequent quarantine, representation controls or source-quality requirements. No new CPT corpus or training admission was created.

Every Parsig export row records “Parsig attribution-required research use; underlying edition rights retained.” That label does not establish a blanket license for all underlying editions, commercial redistribution or every training use. Rights and representations remain explicit preparation gates.

## Evidence and reproducibility

Counts were computed in memory with the standard library, with exact SHA-256 checks against the existing export, dataset manifest/partition files and qualified TRAIN pin. Dataset DEV/TEST records were projected only to IDs and work IDs; no held-out translation content was inspected or emitted. No benchmark reference file, model output or engine weight was opened. No tokenizer, package, network or cloud action occurred.

The companion `UNLABELED-DATA-INVENTORY.json` records all source paths, full hashes, per-pool counts, untranslated IDs, work exclusions, counting definitions and limits. Its SHA-256 is `7eba461256dfcf44e324dde31d2b119cac1b4fae866ca0a53e705217389ba060`.

| Authoritative input | SHA-256 |
| --- | --- |
| `sources/local/parsig-2026-09-20/exports/text-units.jsonl` | `c42e0a5a0d4d108218a0481ca073c07c6bb00cdcba0bffb462b67bb6d7a60789` |
| Translator dataset `6f442563…/manifest.json` | `190bc7906fa10396dc07b8e92b7bfcfe25694f6295e0f9592306b1ef7410186a` |
| `experiments/train-audit-20260927/qualified-v1/train.jsonl` | `15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc` |
