# TRAIN20 inference diagnostic: bounded readiness review

Lead agent/request id: /root
Critic agent/request id: /root/nllb_final_preflight_review
Critic model and reasoning effort: inherited GPT-6 Astra and parent reasoning effort
Independent from lead: yes
Critic verdict: pass with notes
Evidence reviewed: Frozen runtime, wrapper, controller, exact package, source-control/token map, generated server command, unchanged admission guard and PLAN.
Verification evidence: Runtime writer passed two tests in10.405 seconds; root passed four package/lifecycle tests in1.483 seconds; independent critic passed all six tests in11.287 seconds, verified every package member, decompressed/compiled the actual command and checked helper dependencies and failure paths.

The critic reports no must-fix findings. Exact real canaries select shortest parent014 and padded parents013+014; local tiny-model checks exercise FP32/BF16 loss, masked padding, target shifts, separate control/content denominators, reload, deadline and retained failures. Runtime sequence remains40 likelihood calls then20 first generations, preceded by two unscored forwards. No training, changed tokens, DEV generation or optimizer loading.

| Artifact | SHA256 |
|---|---|
| cloud_pilot/nllb_seen.py | 9a582bcb82a771f5f2a0debc4dd823e618d3dc82f8394234f4182a6a4f07763e |
| cloud_pilot/test_nllb_seen.py | c8dd91952b1aed2588061b49e4054eda365855f74606f478f530a8e14940cd00 |
| cloud_pilot/hf_nllb_seen.py | c53d0eea5c9e307b0f31b0898f412478d5b90f49997d6f1e331201f85092cd5c |
| cloud_pilot/test_hf_nllb_seen.py | 87ba473cbb06f1e77b86f008614971e5659ad68a5fe0b902381a973b60e64433 |
| control.py | a4fa486f4ef3ebd2432a47710487553b0762951b49ca6b0e35dae93418e05fc3 |
| package.zip | c57c25f27ef023d139ae939d3e9c56f8ec8408ed9586de20dd94dacce9a8195e |
| package-manifest.json | e8baa7636bf51ac4e821859e2016178f453afcb9e48eb886bbc08926a954a4a3 |

The eight declared inference files total5,515,046,606 bytes and are copied only on the server from a read-only mount. The source cloud model and optimizer remain untouched. Recovery accepts only the small declared output files, a closed manifest, committed provider inventory and matching hashes. Caps remain first-attempt failures; technically completed coverage does not imply semantic success.

Root owns submission and observation. One POST, exclusive journal, ambiguous-response reconciliation, known-job cleanup and native15-minute timeout are retained. Compute600/internal780 seconds reserve180 seconds for small export and120 seconds of native headroom. The unchanged guard reservesUSD3.208353 conservatively; the proposed actual diagnostic bound remainsUSD0.875005 withinUSD1. No automatic recharge or paid resubmission.

This is local preparation approval only. It does not prove Linux/GPU execution or provider persistence. Before launch root must freeze the clean commit, verify the actual package cloud roundtrip, fresh account/rate/balance/cumulative usage and absence of active/duplicate jobs. Inside the same bounded job both real forwards and measured remaining-time admission must pass before the scored schedule. Evidence is recovered and terminal status confirmed afterward. No semantic/model promotion follows from readiness.
