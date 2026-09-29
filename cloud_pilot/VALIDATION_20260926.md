# Cloud preparation checkpoint — 26 September 2026

**PREPARATION_ONLY_NOT_READY_FOR_PAID_LAUNCH.** This is a reviewed preparation checkpoint, not a completed cloud setup or scientific model result. AutoCode mode: Agent Company, because isolated runtime and bundle implementation plus independent QA/Judge reduced integration risk; the user explicitly authorized subagents. One writer per module was maintained; the lead integrated the environment recipe, downloader and documentation.

## Delivered artifact

- Local archive: `resources/local/cloud-pilot-20260926-v1.zip` (6,527,084 bytes; intentionally excluded from Git with the other local data).
- Archive SHA256: `c852c5335102bf082c26f278a518a199699936b24c997e722ed2f0466a9bddcd`.
- Manifest: 16 payload files; directory and ZIP verification PASS. The manifest contains exact per-file hashes.
- TRAIN: 2,609 forward rows → 2,487 distinct stripped pairs → 2,484 retained rows. Three literal editorial `<pad>` collisions are explicitly excluded with IDs, reasons and source/target hashes, without rewriting source data.
- Canonical training serialization: 370,618 tokens per epoch; longest row 1,113 tokens; no truncation. Every supervised answer decoded exactly to its source target plus turn terminator during preparation. This supersedes the earlier 361,269-token completed-chat audit for this training path.
- DEV: six historical input-only diagnostic records, with canonical prompts. No reference answers or frozen benchmark cases are packaged. These six cases do not replace the planned 24-case philological panel.
- Runtime SHA256: `7220474d5446a8e93c014e52f8fd329fed1993256254c37694d5fe750c8421d5`.
- Bundle tool SHA256: `f66d8dec28c385393a5ecb2ed14276f21482f36743242685c981ec697598147f`.
- Contract SHA256: `db48368c26342d3be6d344a7f164ca8ff2f43dd42c105fffcf502844a0c3c517`.
- Downloader SHA256: `22dbdd04580cb27f8ca1154afad9fa3dfdebd16c6d25f8df1b28700cf041e5fd`.
- Linux lock SHA256: `e80c606b6c9b89ae9f611459dca2b228749c227ace10edce0999414c9e7a8fd7`.

## Direct execution evidence

Lead ran `python -X utf8 -B -m unittest discover -s cloud_pilot -p 'test_*.py'` with `PAHLAVI_TRANSLATOR` pointing to the existing translator: **10/10 PASS**, 1.318 seconds. Running outside the Windows sandbox was explicitly approved by automatic approval review because Python's mode-700 temporary-directory ACL failed inside the sandbox. Earlier ACL failures occurred before the archive operations; they were not recorded as successful archive tests. Four empty inaccessible scratch directories remain ignored under `cloud_pilot/tmp*/`; no project data were deleted.

Checks exercise exact answer masking, boundary changes, control-token/length rejection, DEV reference/prompt rejection, deterministic archives, corruption, unexpected/traversal/duplicate ZIP members, missing/false-success result status, both upstream checksum algorithms, revision/file-list validation, and original holdout rejection even after manifest hashes are regenerated. The three documented source exclusions were separately exercised against the actual pinned source and official tokenizer.

The runtime implementer directly executed tiny Gemma4 NF4/BF16 CPU forward/backward using the current Transformers/PEFT/bitsandbytes APIs: finite loss 4.825189, 7,808 trainable LoRA parameters, nonzero finite gradients, and exact cached/uncached greedy output parity. An unconfigured public DynamicCache avoids the observed zero-shared-layer cache-construction defect; eager attention is used consistently. No vendor code is patched.

The implementer also executed a real tiny Trainer canary stopped after one optimizer step, saving optimizer/scheduler/checkpoint state while retaining the planned four-step scheduler. A fresh model/Trainer resumed to four steps and matched uninterrupted training over every trainable adapter tensor: maximum difference **0.0**. Saved evidence is `checkpoint-resume-evidence.json`; the original test checkpoints remain under the recorded project-local `tmp` directory. This proves a small Windows CPU path, not full-size memory use, Linux, CUDA or A100 throughput.

`benchmark.py verify`: **PASS**, 40 passages / 160 cases, original manifest `a3932f7510f101376cc91c47bb23f3c9872656c41f563701fa3dcb2b6c89a5e8`, `expert_adjudicated=false`. The frozen benchmark was neither changed nor used for inference/training.

The downloader's metadata-only command checked the exact public model revision and found eight required files totaling **62,578,654,714 bytes**. No model weights were downloaded. It requires an explicit `--download`, original upstream checksums, sufficient disk headroom and all indexed shards before emitting verified provenance. The observed local free space was below the full snapshot size.

`uv pip compile` resolved 57 packages with hashes for Linux amd64 / Python 3.12 using the official PyPI and PyTorch CUDA 12.8 indexes. No project packages were installed locally. A managed-Python probe encountered Windows permissions, so the available Python 3.11 interpreter was used by the resolver; the requested target was still Python 3.12 and `--no-build` was set. This is dependency resolution evidence only. The pinned base container was not pulled/built; its Python/OS and the complete lock installation remain unverified.

## Cloud observations and incomplete work

Created the empty GCP project `pahlavi-research-20260926` (Pahlavi Research) under the user's cloud-preparation authorization. The console visibly reported **no linked billing account**. No VM, paid disk, GPU lease, billing link, payment, IAM change or Drive action was performed.

The authorized free Cloud Shell directly reported Linux x86-64, Ubuntu 24.04.5 LTS, Python 3.12.3, Docker 29.8.0 and approximately 12 GB free temporary space. An isolated `/tmp/pahlavi-preflight-20260926` environment was created. Installation of the pinned CPU library variants began; its final exit status was not observed. The code-only runtime ZIP upload stalled and failed when the browser session no longer owned the tab. Therefore **no Linux runtime smoke, container build, full weight load or GPU test is claimed**. No training corpus or benchmark answers were submitted through that upload attempt.

Browser recovery was bounded after the stalled upload. A final 10-second attempt to recover a suspended cloud tab timed out and reset the browser kernel. Native Windows control was never opened. Browser-tab closure could not be verified; three suspended billing/Cloud Shell tabs were visible in the final inventory. They may require manual closure. No credentials were read or copied.

Docker Desktop had previously failed while creating its inference-service socket, before the user's Quit action. A non-destructive rename attempt failed without changing the socket, and the documented disable command could not reach the stopped backend. No reset, deletion or reinstall was performed; further local Docker repair was deliberately stopped.

The full run remains blocked on exact host image/container validation, original weights, actual A100/local-model capacity and speed, billing/quota, region-specific all-in quote, provider-enforced deadline, transfer/export round trips and the separately adjudicated 24-case panel. The maximum authorized canary remains **30 minutes AND USD 3**, including setup/download/idle/shutdown and inside the **USD 25 total ceiling**. Budget alerts and Python deadlines do not guarantee billing cessation. The old six-hour/Runpod estimate is not a GCP launch allowance.

## Independent review and gate

- Implementer agent/request ids: /root, /root/model_choice_review, /root/cloud_transfer_review
- External QA agent/request id: /root/philology_evaluation_review
- External QA model and reasoning effort: inherited lead route without override; exact runtime model/effort labels not exposed to the agent
- External QA evidence: independently ran eight non-filesystem checks, independently rejected each of eight false readiness gates before GPU, rejected eval inputs outside the verified bundle before GPU; reviewed runtime hash 7220474d5446a8e93c014e52f8fd329fed1993256254c37694d5fe750c8421d5 and the repaired holdout/readiness/eval boundaries. Lead's two filesystem-test passes are explicitly distinguished from QA's own execution.
- External QA verdict: pass
- External Judge agent/request id: /root/external_judge
- External Judge model and reasoning effort: inherited lead route without override; exact runtime model/effort labels not exposed to the agent
- External Judge evidence: independently verified the actual c852c533... archive and its 2484 rows / 370618 tokens / 6 DEV inputs; independently ran both downloader tests and false-readiness refusal; inspected saved CPU checkpoint/resume evidence, source, environment pins, transfer/budget documentation and QA PASS.
- External Judge verdict: pass
- Gate validation result: pass

QA conclusion: “PASS فقط برای تحویل PREPARATION_ONLY_NOT_READY.” Judge conclusion: “PASS for preparation-only handoff; NOT_READY for paid launch.” Both distinguish preparation integrity from translation quality, real Linux/GPU compatibility and a guaranteed spending cap. The lead accepts that limited checkpoint. The AutoCode validator checks record structure and distinct review identities only; it is not operational proof.
