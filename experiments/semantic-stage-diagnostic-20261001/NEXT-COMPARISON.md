# Direct translation versus the model's own analysis

2 October 2026, America/Halifax. **LOCAL PREPARATION / NOT READY FOR EXECUTION.** Classic + Critic; Main is the sole writer. This follows the completed stage diagnostic and the external Astra PARTIAL verdict. No new inference job, training or weights download is admitted.

## The decision this comparison could inform

Does an explicit analysis pass improve complete Pahlavi-to-Persian translation from the retained step280 checkpoint when the model must produce that analysis itself? The previous R/S results supplied correct meanings and cannot answer this question. This is a comparison of two inference workflows, not identification of an internal reasoning mechanism or a new model-accuracy benchmark.

| Arm | Inputs and steps | Scored output |
|---|---|---|
| Direct | Qualified complete source and common context/evidence; one Persian translation attempt | Complete Persian translation |
| Own analysis | Exactly the same source/context/evidence; generic analysis attempt, then translation with that first analysis appended verbatim | Complete Persian translation |

Both arms use the same checkpoint, precision, tokenizer, common final translation instruction, decoding policy and final-output budget. The second arm deliberately adds one model call and its tentative analysis. Its final call retains access to the original source/evidence and may recognize errors in its analysis. No human correction, oracle meanings, preferred sense derived from the reference, case-specific leading question, example answer or reviewer repair enters either arm. Any dictionary evidence must be the identical independently bound inventory in both arms; if bindings cannot be qualified, declare source-only inputs for both before freeze. Do not selectively omit inconvenient senses.

The analysis instruction must be generic across cases and mark unknown readings explicitly. Preserve its exact first text, including contradictions and uncertainty; do not parse it into a manually corrected representation. References, expected roles and grading constraints remain reviewer-only. This tests a usable workflow rather than the ability to restate supplied answers.

## Readiness inventory, not an admitted panel

The read-only inventory reviewer found these three stable source-bound pairs. Main verified their current derived source/target spans and hashes and the underlying primary bytes. Exact identities, paths and checksums are in [next-readiness.json](next-readiness.json). These are leads, not three independent expert-certified test cases.

| Lead | Existing qualified scope | Remaining qualification |
|---|---|---|
| MP5651, Qal‘eh Iraj O.2, shelfmark8079 | Complete five-line edition pair; Cereti et al.2022,463–464; source55 / English60 codepoints | Terse striking/payment syntax and editorial `(ī)` need prospective uncertainty dispositions. The paired English is provisional evidence, not Persian gold or an independent grammatical analysis. Do not invent a recipient, cause or penalty. |
| KANHERI-ARTICLE-01-ARRIVAL, parsig:201001001 | Complete30-codepoint finite clause; Persian22-codepoint reference; article PDF10 / printed116 visually rechecked | Only the bounded arrival clause is qualified. Date, prayer, proper-name apposition and other parent meanings remain outside it. Same previously used Kanheri lineage. |
| MP0602, Āmol Doc.1 | Complete nine-line edition pair; Weber2015b,103–104; source247 / English407 codepoints | Obligation, discontinuous syntax, technical units and editorial explanations need reference/scope review. Collection location is uncertain. Broader Central Iran/Hastijan grouping is unresolved, so an independent-family count is not established. |

All three exact IDs occur in the later selected1,536-row pool. That is exposure evidence for the continuations that actually consumed those rows, not proof that step280 consumed them. Their exact IDs are absent from the earlier historical2,237-row control; Main also found no exact or six-word complete-clause containment in its normalized source strings. This bounded screen does not establish unseen status: alternate spellings, formulas, related wording, pretrained exposure and earlier inference exposure remain uncertain. Label any resulting panel familiar development diagnosis unless stronger provenance establishes otherwise.

S22EXP-002–005 are pedagogical reserves only. Their textbook pairs and narrow constructions are published, but their receipts leave underlying manuscript/work lineage unresolved. Main rechecked printed77–78 images without resolving that lineage. They do not fill authentic-work or independent-family eligibility. Do not equate240 teaching rows with240 complete sentences, or53 documentary units with53 whole passages.

No complete independently qualified grammatical analysis was found for the three leads. Such an analysis would be necessary for a verified-analysis assistance arm or grammatical training supervision. It is **not** an oracle input required by this new own-analysis comparison. The new comparison still needs independently qualified complete references and uncertainty/scoring dispositions. Preserve the old three-condition draft and its holds; do not quietly weaken it or count this new question as its completion.

## Uniform measurement and failure accounting

Reuse the existing semantic merit in [BLIND-REVIEW.md](../dose-acquisition-20260930/live-execution/BLIND-REVIEW.md): accepted means all substantive meaning retained without substantive correction; substantive omission/addition/mistranslation is meaning_error; material role reversal, polarity/obligation reversal, essential name/quantity error or invented event-changing content is critical_error; unresolved adjudication is uncertain, never a pass. Allow source-supported alternatives and score meaning rather than reference-string or JSON equality. Names, quantities, tense/aspect, roles, scope and uncertainty must be qualified case by case before generation. Technical-format checks cannot certify these meanings.

Two fresh assessors receive shuffled final translations and the same qualified reference evidence, without arm/checkpoint labels or analyses. Preserve raters separately and retain disagreements. AI agreement is provisional and does not replace specialist calibration. Analysis adequacy is a separate secondary assessment; generic child/parent direction alone cannot fully satisfy a frozen son-specific endpoint. Do not pool component support with complete-translation acceptance or rewrite earlier benchmark counts.

Freeze N cases and three scheduled call slots per case: direct translation, own analysis, staged translation. Keep every first output and failure. A hard analysis failure leaves the staged translation unavailable rather than generating a repaired/replacement analysis. A capped analysis remains saved and may be passed verbatim only if this handling is frozen before execution; the pipeline is technically incomplete even if its final wording is semantically assessable. Unknowns, abstentions, caps, missing outputs and uncertain references stay in the fixed N denominator. No hidden retry or post-result case exclusion.

Analysis validity and cap handling are **not yet frozen and block execution readiness**. Before generation, distinguish hard failures from usable tentative/uncertain analysis, define the chosen handling of caps, and preserve final semantic quality separately from pipeline technical completeness. No requirement for valid JSON or confident complete analysis is implied by the present plain-text design.

Report per-rater paired complete-translation labels, newly accepted and regressed cases, critical errors, uncertainty preservation and technical completeness. Also report each arm's end-to-end elapsed time and generated-token/model-call counts, including the analysis call. Estimate timed GPU cost using the freshly verified provider rate; token counts are descriptive, not a per-token bill. Report shared bootstrap, model-loading and export overhead once, total provider cost separately, and any per-arm dollar allocation with its assumptions; keep estimates distinct from provider invoices. A secondary component score cannot turn a failed complete translation into a pass. Freeze any operational continuation threshold after source qualification and before outputs; a tiny selected panel cannot establish statistical gain, generalization or model promotion. A positive exploratory signal would justify a subsequent controlled confirmation proposal, not automatic training.

## Smallest next implementation

First resolve the specific reference/uncertainty and family questions above, or replace an unsuitable lead with another qualified complete clause. Select by declared source/structure criteria, not known output success. Bind complete source and reviewer-only reference evidence; record actual exposure and group related witnesses. Then freeze cases, common prompts, failure handling and decision rules and obtain exact-artifact Astra review.

Only when concrete cases qualify should the existing tokenizer, generation, persistence and blind-scoring tools be extended minimally for the two-call dependency. Do not build a new training/retrieval framework now. A later launch also needs actual prompt-capacity checks including the maximum analysis, relevant runtime interruption/persistence checks, live funded balance/rate/idle-job checks and the maintained authorization gate. No current credit, GPU runtime or invoice has been verified by this preparation.

## Evidence checks

The following read-only check verifies every recorded file binding and the exact three derived pairs without reading protected answer files or loading model weights:

```powershell
@'
import hashlib, json
from pathlib import Path
p = Path('experiments/semantic-stage-diagnostic-20261001/next-readiness.json')
m = json.loads(p.read_text(encoding='utf8'))
for name, expected in m['artifact_sha256'].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == expected, name
ids = {r['id'] for r in m['leads']}
rows = {}
for line in Path(m['derived_pairs']).read_text(encoding='utf8').splitlines():
    row = json.loads(line)
    if row['id'] in ids:
        assert row['id'] not in rows
        rows[row['id']] = row['learning']
assert set(rows) == ids
for lead in m['leads']:
    for field in ('source', 'target'):
        value = rows[lead['id']][field]
        assert len(value) == lead[field + '_codepoints']
        assert hashlib.sha256(value.encode('utf8')).hexdigest() == lead[field + '_sha256']
assert not m['paid_run_admitted'] and not m['training_admitted']
assert m['frozen_cases'] == 0
print('PASS: source/reference bindings intact; three leads, zero admitted cases/jobs.')
'@ | & '[USER_HOME]\.venvs\codex-science\Scripts\python.exe' -B -X utf8 -
```

## Independent local planning review

Lead agent/request id: /root
Critic agent/request id: /root/plain_package_critic
Critic model and reasoning effort: Inherited lead settings; no new model or effort override requested
Evidence reviewed: This prospective plan, next-readiness.json, ten pinned local files and three derived pair metadata records
Verification evidence: Independent byte-hash, exact-line, source/target codepoint and hash checks; root direct read-only check and link checks; two clarified failure/cost limitations
Independent from lead: yes
Critic verdict: pass

The critic returned PASS for local prospective planning, with execution HOLD. Its two clarifications are integrated: timed GPU-rental accounting and explicitly unresolved analysis-validity/cap handling. No protected answers, completed model outputs, ratings, credentials, network or model calls were part of this review. Main separately verified the original primary bytes and bounded historical source screen. This review is not Astra approval of an executable packet, specialist certification or paid-run admission. The completed stage result and its Astra PARTIAL verdict remain unchanged. Version impact NONE.
