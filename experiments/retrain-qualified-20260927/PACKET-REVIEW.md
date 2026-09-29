# Blind packet preparation review

Lead agent/request id: /root
Implementer agent/request id: /root/train_review_07
Critic agent/request id: /root/final_external_judge
Critic model and reasoning effort: inherited session settings; no override
Independent from lead: yes
Critic verdict: pass
Evidence reviewed: `scripts/prepare_blind_palref_comparison.py`, frozen comparison protocol, actual local CLI fixture and input-token mismatch rejection.
Verification evidence: independent execution verified all 160 mappings, 80 outputs per reviewer, exact forty-case-by-two-condition coverage, separate opaque IDs and shuffled orders, exact sources, both published references, meaning checks, output texts/statuses/hashes, unchanged rubric and reviewer-folder isolation. A changed input-token count failed before output creation. Implementer separately exercised seven invalid-input/overwrite scenarios. Root's repeatable fixture check verifies coverage, hashes and changed-input rejection.

Helper SHA256: `f0fbcf7cbc54d75865ae340f9b873594ac59ab209df30b5399fc1feacfa0d806`.

Run the local check from the project root:

```powershell
& resources/local/hf-client-venv/Scripts/python.exe -B -X utf8 tests/check_blind_palref_packet.py
```

Each check preserves its small fixture in a fresh `resources/local/palref-check-*` directory. No model runs, weight downloads, network actions or semantic quality claims occur. The fixture reuses the previous output in both roles and is explicitly marked as a fixture. Actual candidate identity, final 280 steps, cloud recovery and executed first-attempt history remain separate prerequisites. The helper checks supplied optional attempt metadata without inventing absent evidence.

Use the helper only after root verifies the actual new result against its cloud manifest. Reviewers receive their own `reviewer-A` or `reviewer-B` folder only; the mapping and model/run identity stay in `lead-only`. Scoring is unchanged and occurs after reviews are frozen. All AI judgments remain provisional.
