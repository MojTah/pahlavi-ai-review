# Final cloud preparation review — 26 September 2026

Status: **PREPARATION_ONLY_NOT_READY_FOR_PAID_LAUNCH**. Version **0.10.0**, MINOR: isolated cloud preparation/runtime package since the earlier 0.9.0 benchmark release; PAL-REF v1 is unchanged. Mode: **Agent Company**, under the user's existing delegation authorization. Lead owns integration and execution; runtime implementer owns only runtime.py/test_runtime.py; independent reviewers are read-only.

The user explicitly authorized Google Cloud configuration, a suitable VM order, and project budget setup. The canary remains limited to 30 minutes AND USD 3 including setup/download/idle/shutdown, inside the USD 25 total ceiling. No cloud purchase or billing mutation was completed.

## Live account blocker and handoff

Native browser inspection confirmed project `pahlavi-research-20260926` has no linked billing account. The link dialog reported no active billing accounts. After removing the Active filter, the only account was **My Billing Account**, Closed. Its account-management page showed **Reopen billing account disabled** and the banner: “Your account has been closed. You can no longer access Google Cloud. Contact Support for further assistance.” The exact closure cause was not provided by those pages; do not infer a declined payment or policy violation.

The account is still linked to the old project `onex2-326823`; it is not linked to Pahlavi Research. The user answered that there is no other active billing account and will reactivate this account through support. Recheck linked-resource charges before reopening; [Google's account-reopening documentation](https://docs.cloud.google.com/billing/docs/how-to/close-or-reopen-billing-account) states that linked projects can resume incurring charges. Do not alter that unrelated project without scoped authorization.

No budget, VM, paid disk, quota change, IAM change, credential extraction, payment or Drive action occurred. Intended project budget remains USD 25 with an early USD 20 alert; this is **not yet configured**. The `a2-ultragpu-1g` candidate, exact image, zone, quota, live all-in rate, provider deadline and cost reserve remain subject to launch admission.

The console now labels its budget page “Budgets & caps”. [Current spend-cap documentation](https://docs.cloud.google.com/billing/docs/how-to/budgets-spend-caps) explicitly excludes ongoing persistent compute/storage charges from pausing. This does not supply a hard spending cap for our A100 VM.

## Final fixes

- Both train and eval require the contract inside the verified bundle; an unrelated external contract is rejected before GPU admission.
- Full resume requires nonempty trainer state, optimizer, scheduler, RNG, adapter config and adapter weights, with checkpoint step matching the passing canary. All checkpoint files are hashed; a second resume record is refused.
- `resume-checkpoint.json` is included in the result allowlist. It preserves the approved resume contract, contract SHA256 and bundle-manifest SHA256 alongside checkpoint hashes; the original canary contract remains intact.
- Docker pip installation explicitly uses `--break-system-packages` only inside the disposable container. Official registry config for the pinned image identifies Ubuntu 24.04, Python 3.12 and apt-installed pip, without an observed PEP 668 override. This fixes a predicted build failure; no actual Linux build success is claimed.
- The runbook now uses the image's runtime entrypoint correctly and overrides it explicitly for bundle helper commands. Revised readiness requires a newly built and verified bundle, not edits inside an existing archive.

The base-image registry config digest inspected was `sha256:05e386c026b0e251378a79a93e878ed19829bbf556e57b90da61433cf6c7d43e`. Existing base-image and dependency pins remain unchanged. [pip documents the container-local override](https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-break-system-packages).

## Evidence boundaries

The initial final-review suite passed 18/18 offline tests in 2.801 seconds. External QA then found missing resume-contract provenance; that finding must be closed in the final artifact and rechecked below. The earlier CPU NF4/checkpoint experiment remains evidence only for a tiny Windows CPU path. No full-model weights, Linux container build, CUDA/A100 training, new translation score or local 8 GB quality/speed result was produced.

Before these fixes, independent QA rechecked every one of the 2,484 v1 TRAIN rows against the pinned source/tokenizer in two implementations; masks, exact answer round trips, and zero TRAIN/DEV work/id/text overlap passed. Root reverified the original frozen PAL-REF manifest without running inference or changing it. Final archive evidence follows after fixes freeze.

The intermediate v2 ZIP is retained for audit, SHA256 `7cc1116808638c59f0e9624b0c8861f79092d5f0edcd50572c83ba5fa774104a`; it is **superseded and not the deliverable** because QA found the resume-contract provenance omission after it was built. v1 also remains preserved.

## UI cleanup limitation

The native browser connection was used only for cloud billing inspection. Immediately after the final UI observation, `await sky.close()` failed with `sky.close is not a function`. The available window2 API has no documented close method. The JavaScript kernel was then successfully reset and no more UI actions were issued, but that reset is not evidence of a successful native connection close. The user was warned immediately; manual cancellation of the visible computer/browser-control session may be needed. Earlier browser-tool timeouts were not bypassed by reading credentials.

## Final archive, verification and independent gate

Final artifact: `resources/local/cloud-pilot-20260926-v3.zip`, 6,527,470 bytes. SHA256 `28e49760a5884db6d4327351c83021db85ef55c091f9c9a02aa8dd27eaa35d78`; manifest SHA256 `e402f63e8b2ecdf5266b4eb449979c60571cacc589214891ba2fb8aa42dfd132`. Runtime SHA256 `08c9a7062680610b9437e7289d198e569cf336696f6c96a061315cb43d0a7786`; bundle.py SHA256 `9721bcb2152b9f5e2fe1670b5ca280950dcfa2a81eefb13e132ac11dd2bbb1ce`. Directory/ZIP build verification PASS: 16 payload files, 2,484 TRAIN rows, 370,618 tokens, six DEV inputs. v1 data selection and benchmark boundaries are preserved.

Final lead execution: `python -X utf8 -B -m unittest discover -s cloud_pilot -p 'test_*.py'` with the existing translator path: **18/18 PASS**, 2.400 seconds. The runtime implementer reproduced the resume-contract regression before fixing it. Tests of admission use mocks and do not claim GPU behavior. `git diff --check` passed.

- Implementer agent/request ids: /root, /root/model_choice_review
- External QA agent/request id: /root/philology_evaluation_review
- External QA model and reasoning effort: inherited lead route without override; exact runtime labels not exposed
- External QA evidence: independently passed eight runtime tests; closed the resume-contract provenance finding; verified actual v3 ZIP/hash/counts and final code/Dockerfile byte matches; checked entrypoint/allowlist/container-only pip override; no edits or cloud access
- External QA verdict: pass
- External Judge agent/request id: /root/final_external_judge
- External Judge model and reasoning effort: inherited lead route without override; exact runtime labels not exposed
- External Judge evidence: independently verified actual v3 ZIP/hash/manifest/counts, eight executable/config source matches, false readiness status, eight runtime tests PASS in 0.094 seconds and clean diff whitespace; reviewed QA PASS and the final state/validation record, including billing and connection-close limitations
- External Judge verdict: pass
- Gate validation result: pass

Lead accepts the final preparation checkpoint after independent QA and Judge PASS. The AutoCode structural gate is checked before commit; it proves record completeness and distinct identities, not runtime readiness. No launch authority is inferred from this record. Both verdicts are PASS for preparation only; Linux/A100 execution, translation quality and monetary enforcement remain unproven.
