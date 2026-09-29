# Independent evidence preparation review

Lead agent/request id: /root
Critic agent/request id: /root/final_external_judge
Critic model and reasoning effort: inherited session settings; no override
Independent from lead: yes
Critic verdict: pass with notes
Evidence reviewed: dev_evidence.py, test_dev_evidence.py, PLAN.md, pinned TRAIN/source-only inputs, candidate-evidence/evidence.jsonl and candidate-evidence/audit.json.
Verification evidence: seven tests passed independently in 3.041 seconds; regenerated evidence and audit matched byte-for-byte; all69 attachments matched TRAIN IDs, payloads and hashes; all24 queries unchanged; traced reads only TRAIN, source-only inputs and three helper source files. Actual CLI refused an existing output directory without changing artifacts. Root separately executed the real CLI successfully.

Implementer: `/root/hf_jobs_immediate_review`, with seven tests passing in 2.94 seconds. Only dev_evidence.py and its test file were assigned. Root owns experiment artifacts.

| Artifact | SHA256 |
| --- | --- |
| dev_evidence.py | 611d190d4075a9b4fc99c374c9bbbfa6068d9e48170246b4a4db33a2f5ce0a08 |
| test_dev_evidence.py | 2e1486fe8ebb6c12558202f23e80718ba329be472d4189bf4d68280b760fbe4b |
| candidate-evidence/evidence.jsonl | 1b25ffea5f0817523f78d20138a1aac201f72e76867369e4bd0ae29d36228cd3 |
| candidate-evidence/audit.json | 7301f60e5428f5a3d5620becf3e313e21dcd6b39b89c796d716eadda28c28e7f |

Separate methodological and witness reviewer `/root/philology_evaluation_review` passed the exploratory design and admitted 68 attachments after excluding exactly case016→134004028. It checked all69 pairings and all66 distinct witnesses against original TRAIN and archived transcriptions/translations after citation removal and whitespace normalization. Available archive locators/citations exist for all witnesses. Read-only verification scripts exited0. No edits or external actions by either reviewer.

The excluded Persian ending belongs to and repeats the following paragraph134004029, whose source starts `ayāb ka`. Raw locations: `sources/local/parsig-2026-09-20/corpus/134.json:1901` and `:1927`; section134004:28–29; Anklesaria1957 p.25; Rashid-Mohassel1370 p.6. Preserve the defective original; omit the attachment without correction or replacement.

The inspected503000003 and514000003/005 share vocabulary or doctrine with DEV517 but do not reproduce its cosmological narrative or answer-equivalent passage. This is no detected passage overlap, not proof of independent textual ancestry. Two Bundahišn source transcriptions cite forthcoming work; their archived Persian targets retain Bahar page references. Ordinary ambiguity and fragments are preserved. Case005 does not receive evidence for frārōnīh.

Root's admitted derivative preserves all other fields and examples and recomputes the affected coverage: 68 attachments,24 cases,164/291 covered attested rare case-terms. Audit and data are in admitted-evidence/. The source candidate stays unchanged. These limits and the single removal are recorded before any assisted model output. Final prompts, inference implementation, runtime canaries and cost admission are still pending; this receipt does not authorize a paid launch by itself.
