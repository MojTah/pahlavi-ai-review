# Legacy DEV evidence reproduction repair

30 September 2026. Bounded local repair of runtime audit F12; no training, inference, cloud, model weights, Git mutation, or historical artifact writes.

## Root cause and change

`dev_evidence.build` calls `dev_diagnostic.read_inputs`, which actually calls the imported live `bundle.reject_controls` for each DEV source. The bundle dependency is therefore executable validation, not merely historical identity. Its frozen hash still identified the retained original-v5 helper (`9721bcb2152b9f5e2fe1670b5ca280950dcfa2a81eefb13e132ac11dd2bbb1ce`), while the imported live helper is the qualified20260927 version (`60094706124ee58b78a2b73b6a43c30eb9310a2a1d3786f83749e95b597b1a2d`).

The old and current `reject_controls` function ASTs are identical, including the string/nonempty, control-token regex, and tokenizer-special checks. Both use the same imported `re` standard library. No other bundle function is called by this evidence build. The repair pins the actual reviewed live helper and documents that the pin describes a current rebuild. TRAIN, DEV-input, and diagnostic-helper pins remain unchanged.

## Verification

Executed `[USER_HOME]\.venvs\codex-science\Scripts\python.exe -B -X utf8 -m unittest cloud_pilot.test_dev_evidence -v`: **7 tests passed**, 4.087 seconds test duration.

The full frozen-build regression now serializes all rebuilt records with the production JSONL serialization and proves exact byte equality against `experiments/dev-assisted-20260927/candidate-evidence/evidence.jsonl`, additionally checking its fixed SHA256 `1b25ffea5f0817523f78d20138a1aac201f72e76867369e4bd0ae29d36228cd3`. Coverage remains 24 supported cases and 69 attachments. This is the original candidate evidence; later admitted/qualified evidence is a separately filtered derivation and is not the builder's output.

An independent in-memory comparison of the full rebuilt audit (including the evidence digest) against the historical audit found exactly two changed keys: `source_helpers_sha256` and `generator_sha256`. All selection algorithm, exclusions, coverage, identities, data hashes, and other audit fields match. The historical generator remains `611d190d4075a9b4fc99c374c9bbbfa6068d9e48170246b4a4db33a2f5ce0a08`; a new audit truthfully reports the repaired generator. The regression explicitly checks different historical/current provenance and validates the new helper hashes against live files.

Tampering checks reject altered TRAIN, DEV inputs, diagnostic helper, and now bundle helper before evidence selection. Existing fresh-output and exclusive-write checks pass.

## File hashes and limits

| File | SHA256 |
|---|---|
| `cloud_pilot/dev_evidence.py` | `ce00f247d519ff1a39a591c99bef88acd796e3ec70723a28b0b697e2833bafc8` |
| `cloud_pilot/test_dev_evidence.py` | `e15614cf4b6736a7345e37b4c58ff7a72f9442ca76ae0bf90da612bb748c815f` |
| historical candidate evidence | `1b25ffea5f0817523f78d20138a1aac201f72e76867369e4bd0ae29d36228cd3` |
| historical candidate audit | `7301f60e5428f5a3d5620becf3e313e21dcd6b39b89c796d716eadda28c28e7f` |

Historical evidence and audit were only read and remain unchanged. No on-disk evidence rebuild was emitted. The production evaluator reads frozen evidence without calling this builder, so this repair does not establish an inference-quality improvement. Future bundle edits will still require review and a changed pin; arbitrary drift is not admitted. Astra review remains required before future training.
