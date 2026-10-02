# Independent Astra gate review — e4fd2bd

2026-09-30. Reviewer: `/root/astra_gate_review`. Scope: `cloud_pilot/training_admission.py`, five wrapped training builders, their tests, and inference preparation callers. No implementation edits, Git writes, authentication, network requests, provider launch, model download, or training.

**Result: PARTIAL. One reproducible provider-boundary validation gap for serialized CLI specifications. Native builder objects pass the local gate checks. This review is not approval of an actual scientific contract or authorization for inference/training.**

## Finding GATE-001 — P2: serialized drafts pass admission, then fail SDK serialization after consuming their claim

Location: `cloud_pilot/training_admission.py:202-218,227-245`; CLI evidence: `cloud_pilot/hf_train.py:192-194` and `cloud_pilot/hf_continue.py:431-433`.

`admit` compares specifications through `plain(spec)`, accepting either native `Volume` objects or their JSON dictionaries. It returns the caller's representation unchanged. A specification emitted by the CLI and loaded back from JSON therefore passes complete, unchanged synthetic evidence. `submit` creates the exclusive claim before discovering that the installed SDK requires each volume to implement `to_dict()`. Its pure `_create_job_spec` serializer raises `AttributeError: 'dict' object has no attribute 'to_dict'`. The claim remains and a repeat attempt is refused, although no request was sent.

This is a local API-boundary validation/recovery defect, not a paid-job safety bypass. Direct in-memory builder returns with native `Volume` objects work. The admission README prescribes `submit(api, spec, preparation, evidence_root)` without defining whether saved CLI specifications are supported. Consequently the narrow required fix is to reject unsupported representations before claiming, or explicitly reconstruct native volumes and validate SDK serialization before claiming. Do not remove retained claims after ambiguous provider calls.

Reproduction below uses only the installed SDK's pure serializer. It never creates `HfApi`, reads credentials, or contacts the provider. Fixture approvals are synthetic, not real authorization.

```python
import json
from cloud_pilot.test_training_admission import AdmissionChecks
from cloud_pilot import hf_train, training_admission as gate
from huggingface_hub.hf_api import _create_job_spec

class OfflineSDKBoundary:
    def run_job(self, **spec):
        spec.pop('namespace')
        return _create_job_spec(secrets=None, **spec)

test = AdmissionChecks()
test.setUp()  # unique resources/local/training-admission-tests directory
test.spec, test.prep = hf_train.specification('v5.zip', 'a'*64, 'b'*32)
test.evidence()
admitted = gate.admit(test.spec, test.prep, test.root)
assert len(OfflineSDKBoundary().run_job(**admitted)['volumes']) == 2
spec, prep = json.loads(json.dumps(gate.plain([test.spec, test.prep])))
gate.admit(spec, prep, test.root)  # succeeds
try:
    gate.submit(OfflineSDKBoundary(), spec, prep, test.root)
except AttributeError as error:
    assert "to_dict" in str(error)
else:
    raise AssertionError('Expected observed SDK serialization failure')
assert (test.root / ('submission-' + prep['training_admission']['job_sha256'] + '.json')).exists()
try:
    gate.submit(OfflineSDKBoundary(), spec, prep, test.root)
except ValueError as error:
    assert 'already claimed' in str(error)
else:
    raise AssertionError('Expected retained claim to block repeat')
```

## Verified behavior

- The five actual builders (`hf_train`, `hf_continue`, `hf_contextual`, `hf_mixed`, `hf_nllb`) create blocked commands. The focused existing suite exercised refusal before original runtime code, missing/changed evidence, invalid status/types, duplicate JSON keys, path traversal, changed spec/provenance, provider-call counts, and retained claims after unknown results.
- Independent positive-path checks generated each real native specification, constructed synthetic complete evidence for that exact job, and ran `admit`. Each resulting embedded runtime guard executed successfully after replacing only its absolute input-evidence path with the corresponding scratch location. The original training/bootstrap suffix was not executed. Admitted command lengths were 18,863, 34,949, 64,108, 79,488 and 16,108 characters respectively, below the enforced argument limit.
- Source tracing confirms original spec/provenance capture occurs before refusal injection; caller mutations are compared against that snapshot. Job identity includes input-volume settings. All five use read-only `/input`; guard evidence is expected beneath `/input/training-admission/<job_sha256>`.
- Runtime guard pins both the receipt bytes and contract hash and validates every declared artifact before the intended command. Provider submission validates before the sole API call and claims with exclusive creation. Native SDK serialization succeeded in the independent positive check.
- Normal inference preparations call `hf_preflight` directly rather than a wrapped training builder. Shared helpers remain callable. Focused inference preparation checks cover baseline, train-recall, train-fit, dev-assisted, dev-diagnostic and NLLB-seen.

## Test evidence and limits

Runtime: `[USER_HOME]\.venvs\codex-science\Scripts\python.exe -B`, with the already installed `resources/local/hf-client-venv/Lib/site-packages` on the import path. No dependencies installed.

`python -B -m unittest cloud_pilot.test_training_admission cloud_pilot.test_hf_train cloud_pilot.test_hf_continue cloud_pilot.test_hf_contextual -q`: **35 passed**. Five independent all-valid real-builder admission/runtime-guard checks also passed. The serializer/retained-claim reproduction above failed exactly as described.

A broader 33-test inference/NLLB run produced 26 passes and seven sandbox `PermissionError` errors on `tempfile.TemporaryDirectory` contents/cleanup. Redirecting its temporary root to `resources/local/astra-gate-tests` reproduced those permission errors. Those tests are unverified here, not asserted to be product regressions. All seven separately selected preparation checks then passed (six inference wrappers plus NLLB training preparation). No filesystem permissions were changed or cleanup forced.

Documented limitations are not new findings: evidence records assert reviewed facts without authenticating reviewers/humans or certifying result completeness; copied evidence roots do not share a provider-wide lock; remote staging/readback is manual; deliberate bypass cannot be prevented; directly submitted blocked drafts can still incur provider startup cost. No actual completed acquisition, scientific training decision, Astra contract approval, human authorization, cloud mount, GPU runtime, or model learning was established by these local fixtures.
