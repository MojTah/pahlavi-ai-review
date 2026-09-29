# Independent lexical expansion review

Mode: Classic + Critic. Root accepts this bounded source-resource export. It is not a training release or linguistic certification.

- Lead agent/request id: /root
- Critic agent/request id: /root/nllb_final_preflight_review
- Critic model and reasoning effort: Inherited parent settings without override; exact runtime identifiers were not exposed to the critic.
- Independent from lead: yes
- Evidence reviewed: expand.py, cpd_extract.py, collection-decisions.json, pinned v4 observations/groups/quarantines, catalogue, content-review overlays and TRAIN2237.
- Verification evidence: Critic executed final read-only expansion in 3.97 seconds and independently ran CPD's pinned full-corpus self-check. Root exported after PASS and ran deterministic --check successfully, matching every output byte and unchanged input hash.
- Critic verdict: pass

All 42,904 source observations are accounted for once: 31,918 resource records retain grouped provenance; 10,083 observations remain held. All 1,485 observations from the four identified protected collection families remain held. Every resource has training_admitted=false, expert_certified=false and whole_work_split_clearance=false. Historical TRAIN2237 is unchanged.

Recovered observations: 3,101 CPD entries, 1,990 explicit-MP MMP lexical entries, 328 markup-bearing entries and 122 definition/cross-reference records. CPD preserves ordered forms/senses, nested examples and unresolved associations; two malformed records stay held. The MMP nonempty-shape count of 1,991 includes one punctuation-only meaning, so only 1,990 pass the informative-text condition.

Resolved critic findings: bind all 31 collection decisions into output; carry each source qualification into resource records; explicitly mark ACP's catalogue-English/observed-German conflict; include effective source language and target-language declaration/conflict status in duplicate keys. The earlier ledger had no actual cluster spanning different declared source-language arrays, so the final key change is preventative. The final ledger contains 129 exact-text clusters with 270 member records. Provenance is retained; no destructive merge or semantic-equivalence assertion is made.

Reviewed bindings:

- expand.py: e05b9733b680c1e5378ceb7d7106c7ae978b7f3fbb5566a47bda49ec5edede7b
- cpd_extract.py: 1d1c247109e7f45356b36bddcf62056c288a5275ac6b25209e6af4e4864a998f
- collection-decisions.json: ce1b1c348678e5f6e5592d120f9b2c604bd64630cac0fd0166ce59e283f90c3f
- lexical-resources.jsonl: 3f963c94c00f79cf8c04421fcd55a539649c1b2a62eb4ac029ae195c1d73871c

This verdict covers the lexical export. Separate pedagogical and archive packets require their own verification; this review does not certify them, resolve manuscript overlaps, admit training examples or authorize paid training.
