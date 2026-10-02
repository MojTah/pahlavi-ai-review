# Reviewed plain-target candidates

1 October 2026. **Local candidate engineering passed; no training or cloud admission.** Classic + Critic: root is the sole writer; the source readers and engineering critic were read-only. This continues the [readable resource](../usable-resource-20261001/README.md), without replacing its archival records or changing the fixed merit.

## What changed

All 11 named target questions now have source-bound dispositions in [target-decisions.json](target-decisions.json):

- Six narrow repairs: five historical delimiter/empty-apparatus fixes and the spacing of the MacKenzie `abus` gloss. No meaning letters, source forms or sense choices were changed.
- Three documentary records retain their published damage/restoration notation, unchanged, in their existing explicitly annotated-fragment task. They are not admitted as clean complete prose.
- Two historical rows are held as standalone examples because the editorial addition spans their boundary. Their original records remain preserved; no joined training pair was invented.

The MacKenzie English printed page (PDF26/printed4) supports `(woman) having just given birth`; `(woman)` remains a usage qualifier. The separate long-vowel `ābus` entry was not merged with `abus`. Printed-page and raw-source hashes are recorded. These scoped source checks do not certify every word in the corpus or substitute for a specialist review.

The resulting inventory has **9,971 candidates**, including all **7,438 lexical groups**. The original seven release holds remain excluded. Lexical instructions now request complete plain-text inventories and preserve distinct entries, senses, alternatives, qualifiers and compound relationships. Original source/context/provenance and archival targets remain intact. Nonlexical instructions are reused from the frozen package; the three named fragments retain their existing uncertainty condition.

## Executed verification

[prepare.py](prepare.py) uses the already-installed tokenizer/Jinja runtime and existing package helpers. It produced actual token IDs, attention masks and assistant-only labels for every candidate with the frozen Gemma template, without loading model weights. The maximum is **1,144/2,048 tokens**; no truncation, unknown token, duplicate complete prompt or target round-trip failure occurred. The 2,525 unaffected nonlexical token records match their predecessors.

Five local tests and exact byte replay passed. The independent critic checked all candidates and eight rejection mutations; see [REVIEW.md](REVIEW.md). The [candidate manifest](candidate-manifest.json) pins inputs, builder, template, output hashes and task-specific token counts. Local outputs are under `resources/local/plain-target-preparation-20261001/data/`: `learning-projections.jsonl`, `all-candidates.jsonl`, `holds.jsonl`, `row-audit.jsonl` and `manifest.json`. These private/local files are not embedded in Git.

| Candidate task | Groups |
|---|---:|
| Historical Persian | 2,230 |
| Lexical Persian | 2,606 |
| MacKenzie lexical English | 3,412 |
| MMP lexical English | 1,420 |
| Pedagogical Persian | 240 |
| Documentary English | 53 |
| Edition spans English | 4 |
| Inscription Persian | 6 |

This is a full candidate inventory, **not a chosen training stream**. There is no selected exposure schedule or new loss-weight recipe. It contains 1,916,655 complete sequence tokens, of which 122,942 are assistant-content labels and 19,942 are terminator labels. Dictionary answer cleanup does not imply a comparable reduction in training cost: prompts dominate these short tasks, and the earlier full pool had 1,936,762 sequence tokens under a different instruction and two additional rows. Counts are not model accuracy, new meanings or effective sentence coverage.

Run from the project root using the shared Python interpreter (no installation needed):

```powershell
& '[USER_HOME]\.venvs\codex-science\Scripts\python.exe' -B -X utf8 experiments/plain-target-preparation-20261001/test_prepare.py
& '[USER_HOME]\.venvs\codex-science\Scripts\python.exe' -B -X utf8 experiments/plain-target-preparation-20261001/prepare.py --check
```

## What remains before the next experiment

[COMPARISON-DRAFT.md](COMPARISON-DRAFT.md) specifies source alone, source plus complete relevant dictionaries, and the same plus independently supported occurrence analysis with retained Gemma step280. It is **DRAFT / NOT READY**, not an executable packet. The current 15 analysis candidates come from one textbook lineage, 14 were previously selected, and zero cases satisfy full pilot qualification. Obtain independently supported analyses/references, exposure checks and additional work families before freezing cases, supplementary scoring and prompts. The old fixed merit remains unchanged.

Do not infer training readiness, an automatic analyzer, generalization or semantic certification from the local engineering pass. No training, paid inference, authentication, model download or app Goal change occurred. The smaller next implementation is to reuse existing prompt/scoring tools after concrete cases qualify; no speculative comparison framework was added.
