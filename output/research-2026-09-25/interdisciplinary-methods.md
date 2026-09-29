# What other ancient-text projects can contribute

Checked 25 September 2026. Companion source records: `interdisciplinary-methods.json`. These are transfer hypotheses for Pahlavi, not claims that these systems already translate it.

The strongest common pattern is a collaboration between learned translation and explicit scholarly evidence. The [ancient-language survey](https://aclanthology.org/2023.cl-3.5/) supplied a citation map; its Sumerian and Hanja references were followed into the original papers and available artifacts. Task boundaries matter: deciphering signs, restoring gaps and translating an intact supplied passage need different tests.

| Source | Reusable idea | Evidence boundary |
|---|---|---|
| [MIT NeuroDecipher](https://people.csail.mit.edu/j_luo/assets/publications/NeuroDecipher.pdf) / [code](https://github.com/j-luo93/NeuroDecipher) | Linguistic constraints on character/cognate mapping | A decipherment model; it does not establish contextual passage translation. |
| [LMU eBL](https://www.assyriologie.uni-muenchen.de/forschung/ebl/index.html) / [source](https://github.com/ElectronicBabylonianLiterature/ebl-api) | Witnesses, scholarly editions, translations and lexical links as connected evidence | Fragment matching and digital editions are infrastructure, not proof of a translator. |
| [Coptic Scriptorium](https://copticscriptorium.org/documentation) / [pipeline](https://github.com/CopticScriptorium/coptic-nlp) | Preserve original and normalized text, morphology, syntax, translation and translator | Reuse the annotation design; a Coptic parser cannot simply parse Pahlavi. |
| [Coptic syntax-guided prompting](https://arxiv.org/html/2604.18758v1) / [code](https://github.com/gucorpling/in-context-coptic-translation) | Compare dictionary hints with verbalized syntactic relations using matched base models | Promising ablation design, but automatic metrics and no philologist evaluation limit confidence; see the separate evaluation audit for the reference-array check. |
| [Coptic–French NMT](https://arxiv.org/html/2508.10683v1) / [code](https://github.com/chaouin/coptic-french-nmt) | Specialized pretrained translation, multiple valid references and held-out books | Biblical domain; book holdout does not prove absence from pretraining. |
| [Sanskrit Heritage / Hyderabad tools](https://gallium.inria.fr/~huet/PUBLIC/C14-2011.pdf) | Lexicon, morphology and parser constrain possible readings while retaining alternatives | Pahlavi resources would need their own implementation and validation. |
| [Sumerian NMT](https://aclanthology.org/2020.coling-main.308.pdf) / [code](https://github.com/cdli-gh/Machine-Translation) | Conventional neural translation and linguistic expertise can help a historical language | Short administrative phrases are a narrow task; do not extrapolate to a general translator. |
| [H2KE Hanja translation](https://aclanthology.org/2022.findings-emnlp.91.pdf) | Transfer across related target versions and assess with specialist historians | Human evidence is a small Korean subset; multitarget benefits are conditional. |

For this project, “reading between the lines” should mean a testable ability to resolve omitted participants, reference, idioms and context-sensitive senses. It should not mean filling a gap with a plausible story. Preserve a distinction between the text's explicit meaning, a supported inference, and an unresolved alternative.

A staged implementation can use existing tools without constructing a complete symbolic grammar first: preserve input layers; retrieve attested senses and examples; supply neighboring passages; ask the translation model to account for roles and negation; have expert corrections identify the failing source span. Add morphology or dependency support where a controlled test shows a benefit. A full lexicon-and-grammar system remains eligible if measured gains justify its substantial scholarly work.

The important human contribution is not just final proofreading. Scholars define text identity, legitimate variants, institutional meanings and what evidence can resolve an ambiguity. Cultural and historical scholarship belongs in the corpus and evaluation design. No anthropological generalization about a community substitutes for interpreting a particular text.

Repository inspection here verified artifact availability and documented interfaces; no historical pipeline was installed or executed. Live default-branch source can change, and paper-era and current repository datasets may differ. Before implementation, pin revisions and confirm per-component licenses and data permissions.
