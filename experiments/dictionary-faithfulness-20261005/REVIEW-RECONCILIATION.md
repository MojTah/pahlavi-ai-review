# Test evidence revision reconciliation

5 October2026. Astra passed source/design and implementation/measurement but correctly held local readiness because Main's request/QA record cited an older test-file checkpoint. Production runtime, scorer, frozen source messages, contract, spec and receipt are unchanged. The mismatch is in synthetic test evidence, not model outputs or merit.

| Revision | Scoring-test SHA256 | Pin-map SHA256 | Applicable evidence |
|---|---|---|---|
| v1, original TemporaryDirectory fixture | f2c72459bc1b27b05396ee13decab894b5203e2cb4bdffffc543b2a7e98966f8 | 85e3075a1974105ec68c7c307f3f6fc25b357de56ce54b35ce68bd22ef9c9752 | Windows0700 fixture access failed; no substantive full-suite PASS |
| v2, project-local fixture | fd6ac6d310d3015f31ea8079baf259e655cf26d4c97f1e7e54defed371c371cc | 83fe9cd77b89f67eeac89afc757c0f40645e7f5c812331a4a6a0b1f7da912ca9 | 15 tests passed, four fixture-parent AttributeErrors; QA snapshot read this revision |
| v3, current project-local fixture with stable parent | cfb7fcb0b0b43d6c9a6f813d11552057233d6fb42065b185cc2e59e5d80c35ea | 939fd14a2840c37c4645af4c9af722d440738bc5afed3928ebedb931049f5b8e | Complete19-test run PASS,54.517s, Main session26983 |

The v3 change adds `self.fixture_parent = self.root` and replaces four remaining `Path(self.temporary.name)` references with `self.fixture_parent`. It changes no assertions, production code or scientific decision. Current final-pins.json already binds v3 correctly; old v1/v2 maps are preserved explicitly. No re-pinning occurred after the passing run.

Main incorrectly reused the older QA-reported hash when writing VALIDATION.json and requesting Astra review. Those original records remain to show this error. VALIDATION-v2.json corrects applicability; QA-CLOSURE.json and Astra's follow-up must close the exact current checkpoint. Do not treat the older test hashes as applicable PASS evidence or silently relabel the original PARTIAL verdict. Source/design and implementation findings remain valid at their unchanged identities; local handoff waits for this closure.
