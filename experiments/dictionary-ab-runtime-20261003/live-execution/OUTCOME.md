# Dictionary help: a positive familiar-DEV screen, with remaining failures

5 October 2026. Both separate blinded AI reviewers accept **2/15 passages without dictionary help and 5/15 with it** on retained Gemma4 31B step280. All 30 first attempts were technically complete, independently recovered and validated before scoring. No new training. This is a prompt/evidence improvement on 15 familiar development passages, not a demonstrated improvement to model weights or unseen accuracy.

| Fixed rubric result | Reviewer A: without → with | Reviewer B: without → with |
| --- | --- | --- |
| Accepted whole passages | 2 → 5 | 2 → 5 |
| Meaning error | 8 → 6 | 6 → 7 |
| Critical error | 4 → 4 | 5 → 3 |
| Uncertain | 1 → 0 | 2 → 0 |

Both identify the same five newly accepted cases: 002, 007, 009, 014 and 015; the same two lost acceptances: 003 and 010. Net gain is three. Newly accepted cases occur in `parsig:103`, `parsig:112` and `parsig:138`; net work-level gains are zero, one and two respectively. Neither reviewer records an accepted-to-critical regression. The exact previously frozen net-gain, multiple-named-work and critical-error guards pass for both (`CONTINUATION_SCREEN_PASS`). This screen authorizes no automatic training, paid job, model promotion or weight download.

Three severity/uncertainty label disagreements remain: 014:A meaning/critical, 009:A meaning/uncertain, and 017:B critical/meaning. The two reviews remain unchanged. Agreement on acceptance is not independent expert confirmation; both reviewers are provisional AI assessors and can share biases.

The regressions are substantive additions, not punctuation-only issues. For 003, the correctly translated new garment is additionally equated with a garment of light. For 010, the ceremonial unity formula is additionally glossed as all power. Both reviewers reject those unsupported meanings. In 017, both still identify the reversal of the supplied `nē rēman` exemption, while differing on severity. Removing all parentheses would not by itself prove that meaning is fixed.

**Interpretation and next local step:** supplying dictionary evidence helps several passages, while generating extra glosses and preserving negation remain unreliable. Review the five gains, two regressions and remaining critical cases against the supplied senses and sentence constraints. Prepare a minimal intervention addressing unsupported glosses and contextual sense/negation selection, keeping the same merit. Treat that intervention as a hypothesis requiring its own prospective test; do not choose another training run from this small screen alone. Protected/expert-qualified confirmation and broader evaluation remain unresolved.

Technical evidence: job `6ac124c7fbc85ba68237d56f` completed on 3 October, running818seconds; 103 files/1,282,165bytes recovered with provider inventory and closed hashes verified. Maximum attempt29.20seconds, zero output caps. The actual scorer rechecked all token decoding, original input/adapter identity and complete30accounting. The narrow manifest-validator repair and 15 passed tests are documented in [RECOVERY-REPAIR.md](RECOVERY-REPAIR.md); the original outputs, reference merit and prior pins remain preserved.

Durable score: [comparison.json](comparison.json), [SEMANTIC-CHECKS.json](SEMANTIC-CHECKS.json), [RECOVERY-CHECKS.json](RECOVERY-CHECKS.json). Private raw evidence, packets, mappings and original reviews remain under `resources/local/dictionary-ab-results-20261005/d68800b3b35c44a4a97adc0c5129a3de/`. Actual job charges/current balance were not refreshed. No additional GPU compute, recharge or local model download occurred during this recovery. No Git remote is configured; local commits are not GitHub updates.

Astra's latest returned response summarized progress and pending semantic review; it supplied no formal recovery-code verdict. This is preserved as PARTIAL, not relabeled PASS. The distinct local recovery critic's PASS and actual verification remain separately recorded. A bounded Astra review of this completed result is the next oversight checkpoint.
