# Corrected readiness and analysis review

Lead agent/request id: /root
Critic agent/request id: /root/nllb_final_preflight_review
Critic model and reasoning effort: inherited GPT-6 Astra and parent reasoning effort
Independent from lead: yes
Critic verdict: pass with notes
Evidence reviewed: Runtime precision delta, original/repaired archives, namespace-only wrapper delta, unchanged controller/budget guard, preserved first ERROR, analysis and neutral review adapter, prospective amendment.
Verification evidence: Root actual CUDA/CPU runtime3tests11.046seconds and lifecycle4tests1.524seconds passed. Critic independently passed all7 in11.931seconds and analysis2tests in0.600seconds. The original failed evidence reader passes and refuses semantic packet preparation.

No code blockers found. Byte/AST comparison establishes that only likelihood_metrics and its package manifest changed within the server package. Model/data/token/generation/schedule identities remain identical. Independent FP32 log-softmax/gather is checked against explicit FP32 CE at unchanged1e-5 tolerance; raw native loss/dtype/discrepancy are retained. CUDA regression includes actual padded model forwarding, full vocabulary, FP64 and a tampered-reference rejection. CPU-only readiness was insufficient for the original native CUDA path; this omission and the failed attempt are retained.

| Artifact | SHA256 |
|---|---|
| cloud_pilot/nllb_seen.py | 0477faeb52b2639e5121afc0e649b3c32bb471f4343b2803967115a37574a585 |
| cloud_pilot/test_nllb_seen.py | ff99b789a4658514fbfb4ad2bc504b7635bc846a2e439c8baaafc3954fa42181 |
| cloud_pilot/hf_nllb_seen.py | 7c6bfd0534596298673754f69d54f662472662481f89a42c055699bd28bdd04b |
| package.zip | e7a63808e2e081ca053211804512ec6850bf4a4bea957fdfbe9af67f24cd1733 |
| package-manifest.json | b967694343bf4dddab48ac3c701b9b9ace5eb1cd8ae50b28fdab03e64ceaec4e |
| scripts/review_nllb_seen.py | cdcf3264a5df4c2b2e5a6024ac6cd626e89df73abf8ff9ff706eaef07a1c4531 |
| cloud_pilot/test_review_nllb_seen.py | 60857fceaba8d584dfde92bc8c534556f8a85488de7406cb0b7d72fbb1c45e5c |

Analysis retains explicit approved original/repair identities, validates arithmetic, source/target bindings, first attempts, failures and20parent/16work denominators. Each neutral packet retains20outputs/28qualified scopes; no model/condition/likelihood metadata is disclosed. Exact schema, hashes and spans are checked; separate reviewer scores and local scopes never become pooled quality or promotion evidence.

Fresh source commit, actual new package roundtrip and provider account/rate/balance/usage/idle checks still gate one corrected bounded launch. The old3.208353 guard,600/780/900second bounds and small-only recovery are unchanged. Combined first+corrected allocation1.25 and funded total25 are recorded in PLAN.md. This review does not confirm A100 numerical behavior; two real canaries and measured headroom still precede all scored calls. A second distinct real failure invalidates readiness. No automatic paid retry, new training or model promotion is authorized by this review.
