# Local readiness record

5 October 2026. Local source, measurement and SDK preview checks pass. External QA and Astra pass the bounded local handoff, including explicit closure of the stale test-evidence binding in REVIEW-RECONCILIATION.md. QA-CLOSURE.json, VALIDATION-v2.json and ASTRA-CLOSURE.json control current applicability; original records remain preserved. No paid execution is admitted.

| Evidence | Result | Executed by |
|---|---|---|
| Frozen 30-message input/token replay and mutation rejection | 6 tests PASS; 480–5156 input tokens | Main; QA independently repeated |
| Runtime CPU/mock first-attempt, precision, journal, recovery/export and SDK checks | 24 tests PASS, 34.028s | Runtime implementer |
| Closed recovery, decoded token/text, identity/provenance, review and fixed-screen checks | 19 tests PASS, 54.517s | Main |
| Separate read-only runner checks | 5 tests PASS | External QA |
| Same-ID real SDK spec/receipt byte reconstruction and scorer preview loader | PASS | External QA |
| Both current source pin maps; frozen source replay; Git diff whitespace check | PASS | Main |
| Real GPU/model canary, paid launch and independent remote result recovery | Not exercised | Future authorized server execution only |

Scoring tests initially could not reopen Windows TemporaryDirectory0700 directories under restricted execution. Only the synthetic test harness was changed to fresh project-local UUID directories, preserved for audit. Four remaining fixture-parent references were then repaired. Complete rerun passes. Original draft pin maps v1/v2 remain; no real prompt/runtime/scorer/spec/receipt bytes changed during this repair. No installation, privilege or credential workaround was used.

Prepared run `6b54f5bc4e984dbe9a4b53e89e4bf5d8`; status `LOCAL_PREVIEW_ONLY_PAID_HOLD`. `preview.json` binds the source-only input/contract and exact spec/receipt/helper/child. The source files live under ignored resources/local; no model weights are present in the new package. Code-specific pins bind the new closed protocol; the old dictionary experiment and semantic rubric remain unchanged. Narrow .gitattributes entries preserve these new byte-hashed files across Windows/Linux checkout; this changes no model prompt, scientific control or runtime behavior.

The proposed USD5.01 compute/120-minute native allowance remains subject to exact authorization and refreshed live funding/rate/cumulative/idle/private/source-readback gates. No claim exists and no provider submission occurred. No Git remote is configured; a local commit must not be described as a GitHub update. See EXECUTION.md for the exact boundary and one-shot handoff.
