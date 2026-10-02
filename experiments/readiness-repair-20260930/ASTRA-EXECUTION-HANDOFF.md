# Independent Astra execution-handoff review

30 September 2026. Reviewer `/root/astra_runtime_plan_recheck`, independent of the implementation writer and lead. **PASS for the local handoff only; no blocking finding. NOT_SUBMITTED / NOT_AUTHORIZED remain the correct states.** This report is not human paid authorization, remote admission, scientific outcome approval or an actual training-contract review.

## Scope and direct evidence

Reviewed `prepare_execution.py`, its three tests, `EXECUTION-HANDOFF.md` and the actual four-file `execution-proposal` for run ID `7352dda33542431abb025b1443087aed`. Existing inference implementation and the previously reviewed scientific/runtime contract remain unchanged. I authored only this report; no credentials, network, cloud client, upload, model-weight download or job were used.

- Independently ran `python.exe -B -X utf8 experiments/readiness-repair-20260930/test_prepare_execution.py -v` with the shared science interpreter: **3 tests passed in 18.094 seconds**. No prior 18-test runtime or submission-gate suite was repeated.
- The real preparation test wraps the installed SDK serializer while socket connections and `HfApi` construction are blocked. It verifies four-file output, two-file transfer inventory, unchanged frozen scientific files and byte-preserving rejection of a reused destination. A changed timeout and missing/changed reviewed pin are rejected before creating output.
- Separately verified the concrete proposal under the same network/client blocks: reconstructed the pinned reviewed specimen, passed `equivalent` and actual SDK serialization, checked every proposal file's inventory length/hash, checked both transfer files' actual bytes, and confirmed the 28 prompt rows contain exactly `case_id` and `prompt`. The proposal has precisely job specification, receipt, handoff manifest and prompt-only copy.

## Boundary assessment

`verify_reviewed` checks the fixed runtime-check digest, all its source bindings, reviewed specification/receipt bytes and exact reconstruction before creating the destination. The fresh decoded program must equal the original after replacing exactly one run-ID literal. Derived command hashes and lengths are recalculated. Full receipt equality then permits only the fresh identity/output prefix and those derived fields; full SDK-specification equality permits only encoded command, trial label and output-volume path changes. Prompts, adapters, dependencies, helper bytes, timing, generation, flavor, other mounts and environment are not override parameters.

The destination and each file use exclusive creation. Existing output is refused and preserved. A write failure can leave a partial new directory; it is not silently retried or overwritten. Local exclusivity does not prove the cloud prefix is unused or create a provider-wide duplicate lock. The handoff retains that live check explicitly.

The exact transfer inventory is the 15,474-byte prompt-only copy (SHA-256 `02c5ecc82e187847377d5891c31fcb9fc5fb0d3714ea4aa66e686c0a3fabce3c`) and the existing 6,372,448-byte qualified bundle (SHA-256 `41fbbe703b7eb3cfc471c83e344ede16c1e92cae8a604b91f638a57d856477b9`). The bundle is verified in place and not copied. Diagnostic reference answers, binding/census/reviewer metadata, job documents and local weights are excluded from transfer. The existing bundle's reviewed training/tokenizer provenance is not represented as prompt-only content or retrieval context.

The prompt inventory path in this concrete proposal is relative to the repository root, consistent with the CLI invocation; resolve it from that root and recheck its digest before any separately authorized staging. No transfer or launch automation was added.

## Reviewed identities

| File | SHA-256 |
|---|---|
| `prepare_execution.py` | `ac5132099c65c3b89ba05cd3053e16ddc600f7291c2d2b7ebc707f12f5771f4d` |
| `test_prepare_execution.py` | `eac942016be551bba032caa36f62382a174d95ee55624401a944450519a9b16c` |
| `EXECUTION-HANDOFF.md` | `b4d92bc1266012d0ab33b76ad0d5a4814e4cc8255f73a81eb83f2e46739b3072` |
| `execution-proposal/job-spec.json` | `15ee39c4c7692b8f515a6412b64a39428410f8ce9fa9e23f113ba1311b7f23ff` |
| `execution-proposal/job-receipt.json` | `1c11f4b12099475fccee19e59363f2f3ca9f21d9ad77ce26f0903dbcfba7177d` |
| `execution-proposal/handoff.json` | `8ac3af55f4ab6dd9f6c7580b0d79d35a6884ab1c9cf5239f49ead361f19716b5` |

Current credit/rate, idle/conflicting jobs, exact remote inputs/adapters, fresh output prefix, provider acceptance, full GPU execution and persistence remain unverified. USD5.51 is a rounded proposed allowance above the earlier USD5.50004 planning figure, not a measured current charge or account spending cap. Separate authorization and live gates still precede any submission. An ambiguous provider result must not cause automatic resubmission. This local PASS supplies no authority to retrain or alter the scientific panel.

Final integration accuracy: reviewed the added concrete run/files, independent test result, repository-relative path instruction, review identities and narrowly pending live scope in `EXECUTION-HANDOFF.md`, plus the version0.11.3 local-PASS/pending-approval summaries in root `README.md` and `PROJECT_STATE.md`. These accurately represent this review and retain NOT_SUBMITTED / NOT_AUTHORIZED. The AutoCode validator pass is lead-reported integration evidence, not an additional independent execution by this reviewer. Refreshed the document hash above; no code/proposal change or repeated test was required for this documentation integration.
