# A bilingual study reading

This is a source-assisted exercise for the future **Pahlavi → Farsi / English** translator. It is not a new decipherment, a site-corpus extraction, or an independently reviewed translation pair.

## Source

Farsi et al., *ParsiPy*, PDF page 2, figure 1 and example; the same passage appears in the [authors' repository README](https://github.com/openscilab/parsipy/tree/3e388d8681004835dbda343653d4959bb9288371). The paper attributes it to the counsel of Ādurbād ī Mahraspandān. A database record ID, critical-edition line and manuscript folio were not supplied with the example we accessed. [Source details](sources.md#s18)

**Transcription, following the repository's typography:**

> ān uzīd frāmōš kun ud ān nē mad ēstēd rāy tēmār bēš ma bar

**Farsi — our proposed rendering:**

آنچه گذشته است فراموش کن و برای آنچه هنوز نیامده است اندوه و نگرانی به دل راه مده.

**English — our proposed rendering:**

Put the past out of mind, and do not distress yourself over what has yet to arrive.

These are our renderings informed by the paper's interpretation. The Farsi sentence is **not** represented as a translation obtained from Parsig Database. “هنوز / yet” expresses the contextual temporal interpretation; it is not a separate source token.

## How the reading works

| Unit | Proposed analysis | Translation consequence |
|---|---|---|
| `ān uzīd` | Something referred to as having passed | Translate the whole expression as “what has passed” |
| `frāmōš kun` | Expression with an imperative of doing/making | Farsi فراموش کن; English “put out of mind / forget” |
| `ud` | Coordination | Joins the two instructions |
| `ān nē mad ēstēd rāy` | Negated coming construction, with a following relational word | “Concerning what has not come”; preserve the scope of negation |
| `tēmār bēš ma bar` | Anxiety/distress expression with a prohibition | The final command is negative; inspect the verbal role of `bar` |

This clause-level analysis is provisional where a dictionary or critical edition has not been checked. In particular, the lexical history of `uzīd` and the relationship of the adjacent distress terms need a full lexical reference. The published whole-sentence interpretation supports the general meaning; it does not settle each morphological label.

## Lessons retained

1. Understand multiword expressions before translating individual entries.
2. Distinguish ordinary negation from a prohibition. Preserve the source's `ma` spelling; another edition's `mā` should be recorded as a convention/variant, not silently substituted.
3. A readable Farsi translation may add an idiomatic expression such as «به دل راه مده». Keep that separate from a literal alignment.
4. A POS output can contradict its own sentence interpretation. The published N label for final `bar` is a review flag, not a reason to translate it mechanically as a noun.
5. A printed script illustration is not a verified manuscript witness. The image was inspected, but no sign-by-sign collation was performed.

**Review status:** source-assisted, assistant analysis; independent philological review pending. Do not use as a held-out translation benchmark after studying it.
