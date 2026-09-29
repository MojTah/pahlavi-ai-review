# Independent typed-release integration review

Reviewer: `/root/nllb_final_preflight_review`. Implementer and execution owner: `/root`. Date: 2026-09-28. I own only this review file for this task.

## Current verdict

PASS for the completed local typed release, including its actual persisted bytes. All ten saved outputs match the completion manifest; the seven new learning-output hashes exactly match this critic's preflight expectations. No blocking projection or persistence defect remains in the reviewed snapshot. This is not a model-run, paid-runtime or training authorization, and not expert linguistic certification.

Final source inspected and executed: `freeze_release.py` SHA256 `893f5922dd7f2f36426a56640ab6b1c35e4aca3e4be5834af7b336798dcd2d44`. The no-argument build passed with exit 0 in 3.53 seconds. An additional independent, in-memory projection check passed in 4.04 seconds against that final source and its 144 bound evidence files. Root subsequently performed the single local write. This critic never called output-writing mode and verified root's saved release as recorded below.

## Persisted release verification

The read-only `freeze_release.py --check` passed with exit 0 in 3.59 seconds. A separate direct-byte audit passed in 0.87 seconds without relying on the builder's output-writing path. It verified the exact directory file set, all ten output SHA256 values, byte lengths and JSONL record counts, unique IDs and learning-field whitelists for the seven additions, the script identity, and all 144 input checksums. The historical-control copy is byte-for-byte identical to the original 2,237-row file. All 12 benchmark bindings, including the manifest, pass byte-hash checks without parsing or displaying answer content.

The ten payloads total 14,873,104 bytes. Completion receipt `experiments/data-qualification-20260928/release-v1.json` has SHA256 `763e49a9e11b35c0565bed14869e1b09c53e09a28431f026abc7610f4bf2bed0`. The seven learning-output hashes are listed below; the other payload identities are historical control `15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc`, 2,317-row exclusions `8bd3aad462b9e9dd7802337acbd15f94b2d4edd3bf3115972749b9ce0a58abf0`, and 37-row surface repetition ledger `d62951c5adf43a652e4c39a28ca2356925901b4722da9115bf72cc0cd22be0d4`.

Training remains unlaunched, and the manifest explicitly rejects adding the different task counts into a sentence-pair total. No output was mutated during this audit. Root owns the separate overwrite-refusal check; this critic does not claim execution of that negative test.

## Findings resolved before freeze

1. The initial S22 projection dropped `semantic_qualification`. This removed row-specific person/number from homographic forms: S22SUP-001/-004 share `wēn-ēm/om/am` but have singular/plural targets, and -015/-016 share `raft estēm`. The revised projection retains the grammatical qualification in `learning.context.grammatical_context`. It explicitly replaces stale extraction wording for S22GRAM-043/-045/-046. These are conditioned auxiliary grammar examples, not source-only translation pairs.
2. The initial CPD projection read its component manifest without enforcing its qualified-output checksum. It now supplies that manifest checksum to the byte-bound reader.
3. Two known documentary spelling defects initially required holds. The final release instead applies the independently approved exact overlay: MP0046 `transction` to `transaction`, and MP0416 `Spandaimad` to source-supported `Spandarmad`, one target occurrence each. All other characters, editorial uncertainty and original packets remain unchanged. The correction record travels in provenance; the units remain annotated documentary evidence, not certain complete prose.

## Static scope checks

- Persian form bundles and complete source-scoped meaning inventories remain together. CPD form bundles, structured direct senses, grammatical components, annotations and language identity are retained without a form/sense Cartesian expansion. Component provenance stays outside the learning view.
- All 888 S22 glossary records remain outside this builder. The grammar hold S22GRAM-070 and three explicit target derivations are preserved. Original S22 packets retain their published evidence.
- Documentary fragments select `.text`, never `context_lines`. Full units retain TEI uncertainty markup when available. The Oxford source schema legitimately stores its editorial signs directly in `.text`; the absence of the TEI-specific key there is not a defect.
- Kanheri exports exact character-verified eligible child scopes, not uncertain parent blocks. The independent inscription review supports six eligible occurrences, four pair types, and no new independent witness. Existing witness identity remains in context.
- The original 2,237-row control is checksum-locked. Benchmark verification operates on byte hashes without parsing or displaying reference answers. The fixed 16 protected work IDs are present. The only additional passage copy screen uses source transcriptions.
- The output schema distinguishes task types and says their counts are not additive translation pairs. The freeze refuses existing output paths, rechecks bound inputs, and writes the completion receipt after payloads. No model, tokenizer download or training launch occurs.

## Executed final checks and counts

| Typed component | Qualified occurrences/inventories |
|---|---:|
| Persian source-scoped lexical inventories | 2,676 |
| CPD English source-scoped lexical inventories | 3,506 |
| Manichaean Middle Persian English lexical inventories | 1,426 |
| S22 conditioned grammar and teaching examples | 240 |
| Annotated documentary English units | 57 |
| Kanheri Persian child spans | 6 |
| S23 English edition spans | 4 |
| Historical control, unchanged | 2,237 |

These counts have different grains and must not be added into a count of independent sentence translations. The six Kanheri occurrences have four distinct source/target pair types. The four S23 additions are two predicate scopes with contextual/omitted agents and two temporal modifiers; no whole held parent is exported.

Independent in-memory assertions checked every Persian form/meaning field against its qualified component; every CPD form/sense/annotation field; all 1,426 MMP selected target strings and grammatical contexts against the approved overlay; all S22 source strings, unchanged targets and retained grammatical qualifications; both homographic singular/plural regression pairs; all 57 documentary source/target reconstructions including the exact two corrections; and every accepted Kanheri/S23 character span. All learning objects contain exactly `source`, `target` and `context`; all run-authorization flags are false. S23 has exactly the four independently reviewed eligible IDs, excluding the already-covered seal and disputed revised-name span.

The exclusion ledger has 2,317 unique IDs: 123 Persian lexical holds, 720 CPD holds, 564 MMP holds, all 888 S22 glossary entries, all four Parsig format-recovery candidates, 14 archive held contexts, one S22 glyph hold, one uncertain Kanheri child, and two excluded S23 children. Held parent evidence remains in the bound source packets and is not a learning row. The 37 duplicate groups are now explicitly labeled surface source/target repetitions, with no instruction to merge different grammatical contexts. The 207 Persian shared-form bundles are separately hash-bound as source grouping evidence.

All 144 input bindings were independently rehashed after building. This includes the unchanged historical control, fixed benchmark files, source packets, reviewed overlays, underlying XML/PDF evidence and selected image evidence. Benchmark checks used byte hashes only; no answer content was parsed or displayed for review. No new protected-source containment hit appeared. That last result retains the bounded-screen limitation below.

## Evidence identities

| Evidence | SHA256 |
|---|---|
| Final builder | `893f5922dd7f2f36426a56640ab6b1c35e4aca3e4be5834af7b336798dcd2d44` |
| Persian component receipt | `571a2e04d805ffbb4cc4efff433fb07fd9d55e703b3a6c00d31d8279d91ebba4` |
| MMP independent QA | `0060601634b982d782a0453e42b0e1a5d8be83ab9fbde212e7bbd05a4ac1b693` |
| S23 independent review | `da4fd944957e20b55fa903be9c6cb8fd010d0f4b244cefcb7b9a198351015273` |
| Archive derived overlay | `189ec7c27b4667bb8b73e12d91e8fefd838ecbd051a97ec9668acfa030564baa` |
| Historical control | `15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc` |

Serialized learning-output hashes from the independent in-memory build, all subsequently matched to actual saved files:

| Output | SHA256 |
|---|---|
| lexical-fa.jsonl | `7979a688dc73a67f646920a668fbdeed6d1e21eb3f10f3810a59de9c427290fe` |
| lexical-en.jsonl | `4d8c2489eca369d0d11a3364f5844cb5440d32eb53777c4ad138f5aff16c0f48` |
| lexical-mmp-en.jsonl | `8411819339113f16ba45dab1c67ce8a044cb6ec5df3d589e912772ba207ff2aa` |
| pedagogy-fa.jsonl | `d96d95610ac354222029d30ae0252425df57859ab8f23bfd14d68a6b71a8edd6` |
| documentary-en.jsonl | `d604e2b66e8c38de18b5e0675fbc9a58f739efd6c845d3cf0a3661542796924b` |
| inscription-fa.jsonl | `c56c346750d23910a96ab6be3dab6f1bfc153bfa9286c5517581fa8dbe6de6cc` |
| edition-spans-en.jsonl | `62bed1c4712b464326c82e2dc0e7bb2cdbd754a88a23471ef7208d05a1ca2bf1` |

## Limits to preserve in final reporting and training design

The duplicate ledger compares source and target while ignoring grammatical context: it is a surface-pair repetition ledger, not permission to collapse different conditioned cells. Do not interpret alternate editions, nested spans or repeated formula occurrences as independent examples.

The passage copy screen checks a candidate of at least five words contained in a protected source row. This is a bounded normalization/containment screen, not proof against every embedded, edited or paraphrased protected passage. Work and witness review remains essential; generic lexical exposure also limits unseen-vocabulary claims.

The four earlier Parsig format-recovery candidates now have explicit held dispositions. Accurate formatting recovery alone does not establish translation correctness.

The component reviews provide source-extraction and scope evidence; this integration review does not independently certify every dictionary sense or scholarly reading. MMP's independent semantic QA was targeted rather than a second full semantic adjudication. Source qualification is not a promise of error-free data or of a numerical improvement in translation quality. Source licenses, attribution and rights for any proposed use remain binding; a provenance pointer must not be expanded into an unreviewed model context. The historical control retains its own original schema, so a future serializer must whitelist its actual source/target fields rather than indiscriminately serialize rows. Training mixture, token lengths and held-out evaluation applicability remain later design decisions.
