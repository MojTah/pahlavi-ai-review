# Expanded source-resource package review

Mode: Classic + Critic. Root accepts the source-resource checkpoint, not a training release. Application version impact: NONE; this is a separately versioned curation artifact.

- Lead agent/request id: /root
- Critic agent/request id: /root/nllb_final_preflight_review
- Critic model and reasoning effort: Inherited parent settings without override; exact runtime identifiers were not exposed to the critic.
- Independent from lead: yes
- Evidence reviewed: 53 archive candidates and report; four Parsig recovery candidates and report; final check_package.py, pinned historical S22 input, frozen lexical manifest and candidate-source bindings. Separate visual critic /root/nllb_source_method reviewed all113 S22 positions.
- Verification evidence: All57 archive/Parsig candidates independently matched originals. Final checker passed in2.64seconds with63 bound evidence files. S22's one macron discrepancy was corrected and the single-field delta verified; all113 positions match linked page images within stated normalization. Root froze package-manifest.json after both final PASS results.
- Critic verdict: pass

## Archive and format verification

The critic checked all53 archive objects, raw/derived hashes, JSON pointers,84 Berkeley transcription/translation XML layers and Oxford folio HTML. Counts reconcile:46 Berkeley paired documents minus4 holds gives42;14 Oxford documents minus3 holds gives11, containing13 folios. The seven named exclusions are absent. No document count is mislabeled as a sentence count.

All four Parsig candidates preserve exact export line offsets/hashes, publisher response indices, source/target strings and ancillary layers. Citation removal reconstructs each original field exactly. Three literal `<pad>` display substitutions and one citation-trailer removal reverse exactly. These are display/metadata views; no training tokenizer transformation has been chosen.

The first integration checker used the original seven S22 examples without pinning their hash. The critic caught this gap; root added the frozen SHA and manifest binding before writing the final manifest. Final checker SHA256: `833a144987e11c528b7d870f77b445df7df6869b5603b6987c903ee3ec002da2`.

## Complete S22 visual pass

The independent visual critic compared all113 new source/target positions with11 linked page images, PDF77 and79–88. The initial `S22SUP-055` extraction `kēšān` had an unprinted e-macron. Root independently viewed PDF86 and corrected it to printed `kešān`, with the Persian gloss unchanged. Reversing that one field change reproduces the full initial packet SHA, confirming no other packet bytes changed.

Initial supplement SHA: `62d47f82eb2b25714bbf62ea394b5722d8246ae741073b5e88a4e7c88e7f47da`.
Corrected supplement SHA: `a328fe6b7075c58e3e27125f26d90d1ad5c3a17bb0c2aa8e9c17d412aa72ec78`.

The critic also verified no dash-expanded cells, retention of singular/plural context alternatives, grouped meanings/past-participle readings, contextual necessity of kunišn, literal glosses, zero markers and parenthesized participants. Derivational records remain distinct from full predicates and manuscript attestations.

## Limits

Root subsequently executed both real `--write` commands against their frozen paths: each refused before mutation, and each completion receipt stayed byte-identical. A normal package replay passed against the frozen manifest. AutoCode's Critic gate validator and Git whitespace checks passed. No remote is configured, so the checkpoint is local only.

The package preserves all original training/source/evaluation artifacts; new training admissions are zero. Checks establish source identity, faithful bounded transcription and explicit bookkeeping. They do not establish specialist-certified translation, complete quotation/formula clearance, a universal maximum dataset or readiness for paid training. Remaining concrete extraction and source-alignment work is listed in README.md.
