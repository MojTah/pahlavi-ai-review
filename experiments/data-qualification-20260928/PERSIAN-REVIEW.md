# Independent review of the Persian lexical release

Reviewer: `/root/seen20_blind_b`. Scope: the six Persian-target lexical families and their extraction/qualification pipeline. No benchmark answers, network, external models or training were used. Only this report is reviewer-owned.

**PASS for the frozen source-scoped lexical component:** 2,676 qualified inventories, 123 held groups and 207 exact shared-form bundles. Independent replay, direct original-XML reconstruction and in-memory fault tests passed. The concrete pre-freeze findings below are resolved by the frozen review overlays. No blocking defect remains in the reviewed scope; this does not authorize training or certify every published definition as correct.

## Independent source reconstruction

All 2,799 resource groups, covering 2,839 original observation memberships, were checked directly against the six original downloaded Kosh responses. Each response's byte SHA256 was verified against the observation receipt; each entry XML was matched to the observation and parsed independently. This comparison did not call `expand.forms_from` or its normalization helper. Independently implemented NFC/whitespace normalization gave **zero form or whole-sense mismatches**.

| Collection | Resource groups | Raw records | Family attribution |
|---|---:|---:|---|
| da | 102 | 103 | Navvābī, Draxt ī āsūrīg; Middle Persian transmission with Parthian layer |
| dk8 | 480 | 483 | Naẓarī-Fārsānī, Dēnkard Book VIII |
| dmx | 1,030 | 1,039 | Tafazzoli, Mēnōg ī xrad glossary; related to Parsig151 |
| gbd | 773 | 797 | Bahar, Bundahišn glossary; related to Parsig137 |
| raf | 285 | 285 | Reẓāyī-Bāġbīdī, Ādurfarnbay Farroxzādān responsa; not Saxwan ī ēw-čand merely because an author overlaps |
| yz | 129 | 141 | Navvābī, Yādgār ī Zarīrān; not Yādgār ī Wuzurgmihr; Parthian layer retained |

The nine raw records absent from resource membership are the previously quarantined missing meanings/forms: one DA record, three DK8 records and five YZ records. The 40 extra memberships are duplicate provenance, not 40 new inventories. A qualifier output must reconcile both resource and observation levels.

Form structure was checked across all inputs: 2,776 one-member arrays and 23 two-member arrays. There are 261 groups with literal comma-bearing form strings and 237 with a terminal stem hyphen. Commas/stem markers must remain literal; they are not instructions to create extra training examples. The output must retain the full source form bundle, and compound meanings must not be distributed to bare alternative members.

## Concrete pre-freeze findings sent to the lead

1. **Compound scope:** GBD486 has `[ān, hān rāy]` with `بدان علّت`; the bare pronoun must not be taught the causal phrase's whole meaning. GBD530 has `[farrah, xᵛarrah - ōmandīh]` with `فرهمندی`; the suffix-derived meaning must not be assigned to bare farrah. GBD483 `[hān, ān ēvag]` with `دیگری، آن یک` likewise needs attachment resolution. These supplement the known GBD11/15/16 compound holds. All six are held in the frozen output.
2. **Verbal uncertainty:** DMX435 has `اعتقد` and explicitly says `شاید`; DMX722 says `شاید نوعی باز باشد`. These are not caught by punctuation-only uncertainty checks. Both complete inventories are held by the frozen DMX overlay; no confident-looking sense was selectively admitted.
3. **Completeness:** DMX474 and DMX554 have unclosed explanatory parentheses. Both are held unchanged pending page-level completeness checks, without claiming the plant/ritual-object definitions themselves are false.
4. **Language identity:** GBD9 literally has the English form `calamity` and `ظاهراً معنی موج می دهد`. Catalogue-level `pal` cannot clear this individual form. It is held in the frozen output.
5. **Avoid false lexical uncertainty:** GBD6's `شاید` can itself be a modal gloss. A keyword-wide hold would confuse meaning with editorial doubt. The final GBD reviewer retains it without declaring the unfamiliar headword erroneous. The output preserves the published form and gloss, and this reviewer confirms that no source correction or stronger certainty claim was introduced; independent print verification of that individual meaning is not claimed.

No source correction was inferred by this reviewer. Orthographic suspicions are different from proven semantic errors. The lead's root holds were individually checked against their literal XML wording, including DA66 `wat`/`بند`, DK8 `غاضب`, `kāstan`/`کاشتن`, RAF `آمرزیده، محروم`, the negation-sensitive RAF40/41 entries and YZ91's form plus starred gloss. These remain source questions, not permission to silently replace text.

## Preserved distinctions checked

- RAF144/145 keep `mādayān`'s nominal versus adjectival inventories and distinct source records.
- DK8 197/202 keep creation versus giving senses of `frāz dādan`; their actual attestations are `_`, so they must not be described as two verified contextual quotations.
- YZ95/106 keep `zatan` with killing/striking versus striking alone; same form does not authorize a winning-gloss vote.
- RAF246 retains the full `warzīdan, warz-` inventory. Unvowelled `کشتن` is not automatically interpreted as killing.
- DK8 394/399 preserve `kištan, kār-` versus `kuštan, kuš-` and the Persian vowel distinction.
- The actual XML form `xʷartīk, xʷardīk` remains one literal bundle string; stem-bearing forms receive the same treatment.

## Split and learning-field boundaries

Collection-decision metadata identifies the protected aliases `hkr`→117, `sns`→138, and `wz`/`mz`→152. They are outside the six-family whitelist. The 16 protected-family metadata list was consulted only as metadata; no protected answers were inspected. Final checks found **zero protected-alias observations, source pointers or shared-bundle members** in the qualified output. Exact catalogue title/author/language/Zotero metadata agrees for all six families, with DA/YZ transmission strata preserved.

Generic source-scoped definitions are the permitted evidence type. Attestation text, manuscript/page references and grammar provenance must not become additional lexical or sentence examples. The intended learning whitelist is only the literal form bundle, the complete published meaning inventory and the source title. A lexical work's title/author is not a claim that its glossary and a separate translation are independent attestations, nor does it identify an uncredited translator.

## Final replay and independent tests

The lead announced the freeze before this final verification. The command below passed against the frozen receipt and all three output files without writing them:

`[USER_HOME]\.venvs\codex-science\Scripts\python.exe -B experiments/data-qualification-20260928/qualify_persian.py --check`

| Collection | Qualified | Held |
|---|---:|---:|
| da | 93 | 9 |
| dk8 | 463 | 17 |
| dmx | 984 | 46 |
| gbd | 739 | 34 |
| raf | 277 | 8 |
| yz | 120 | 9 |
| Total | 2,676 | 123 |

Independent checks, separate from the pipeline's own replay:

- Reconstructed every qualified form array and complete sense directly from the six original response XMLs: **2,676 inventories / 2,716 observation memberships, zero differences** under declared NFC/whitespace normalization. Qualified and held resource IDs form an exact, disjoint partition of all2,799 input groups.
- Verified all43 root,46 DMX and34 GBD hold entries are absent from qualification. Overlapping review holds are not double-counted. Checked known placeholder, uncertain, compound and newly identified verbal-uncertainty cases explicitly.
- Verified the learning object has exactly three keys: `forms_as_published`, `complete_meaning_inventory_as_published`, `source_scope`. Original attestations and grammar remain in `non_learning_provenance` and agree with raw XML.
- Verified207 shared-form bundles by an independently built exact-member index. Every key is an entire literal XML form member of every referenced inventory; no comma string or stem string was split. All member IDs resolve, with no duplicate member within a bundle. The qualified output retains252 comma-bearing bundles and229 terminal-stem-marker groups. These auxiliary bundles are review indexes, not permission to distribute a compound gloss to individual words.
- Rechecked all named polysemy controls above: both records/senses survive without a winning-gloss vote or diacritic conflation. Exact raw definition strings survive intact.
- **Fault injection: nonlearning isolation.** In memory only, appended a distinctive sentinel to every parsed attestation and grammar field and reran assembly. All2,676 learning objects remained exactly equal to the frozen originals, while the sentinel appeared in nonlearning provenance. This exercises actual field flow rather than merely searching code text.
- **Fault injection: changed meaning.** In memory only, changed a parsed sense while retaining the frozen resource record. Assembly rejected it with the expected `AssertionError: kosh:da:1`.
- **Fault injection: unsupported sense structure.** In memory only, inserted an unexpected nested element into a sense. Assembly rejected it instead of silently dropping that scope.
- Rehashed all frozen outputs and the root code after these tests: unchanged. Python bytecode writing was disabled. No original, root code, release data or other report was modified by this reviewer.

## Frozen receipt

| Artifact | SHA256 |
|---|---|
| qualify_persian.py | `45d68849c6d5babaff2fec1679ee39bbf4a3e6b3d1d4eea58e3138b85b022dee` |
| persian-summary-v1.json | `571a2e04d805ffbb4cc4efff433fb07fd9d55e703b3a6c00d31d8279d91ebba4` |
| qualified.jsonl | `57e01d50cba13053a4401d1a64b6ab93c650b32c6aaed94123630bea85415cde` |
| held.jsonl | `aafec5d9b2a188bbdcfff08fd3fcb7bc77853eebd240ef16f0b531a9ee832288` |
| shared-form-bundles.jsonl | `dd254968e792b2bee665676f5264390646fbee3cdfcad9d9a2a5c00bc9a07e59` |
| persian-root-review.json | `231a8ca704d518a168c94048929e4b82a0c0fb5bac7c7783dfcb60d1a3f4f647` |
| dmx-review.json | `f5dfd81afb1f8ee5108692a135e82eabe50862411a4ffed9492cf852f2e3d369` |
| gbd-review.json | `0bb24e0b1bd36aabe0c3ff918b3a472944734c6434c8ae08ae2fd066bde5ead6` |

The full upstream input bindings are recorded in the frozen summary. Reuse of this approval requires the same hashes. The automatic punctuation checks alone are not a general semantic qualifier: the reviewed overlays are necessary, especially for verbal uncertainty and compound attachment. New or changed source inventories require renewed review.

This review establishes literal extraction and bounded qualification controls. It does not establish complete scholarly correctness of every published definition, collation against every print page, an exhaustive dictionary inventory, or permission to start training.
