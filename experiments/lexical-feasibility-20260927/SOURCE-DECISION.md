# Source follow-up: useful evidence without immediate retraining

27 September 2026. The preceding goal turn made progress: the committed feasibility packet, independent review and additional-source inventory changed the available training hypotheses. This follow-up resolves a public-use question, identifies a practical extraction subset, and obtains a second scholarly reading route. No external data are admitted to training.

## New evidence and decision

The live [TITUS text catalogue](https://titus.uni-frankfurt.de/texte/texte2.htm) and [retrieval guide](https://titus.uni-frankfurt.de/texte/textex.htm) allow scholarly use of publicly downloadable material with source/editor/date attribution and exclude commercial use. The [FAQ](https://titus.uni-frankfurt.de/faq/faq2.htm) puts the separate [user declaration](https://titus.uni-frankfurt.de/titusstd.htm) in the password/member-access context; its conditions should not automatically be applied to every public HTML page. Individual pages still restrict republication. This supports the private local research probe below; it is not a declaration that unrestricted redistribution, every cloud use or commercial model release is licensed. No account or permission request was submitted.

The [identity audit](TITUS-IDENTITY-ADMISSION.md) selects the entire archived Denkard IV numbered root as the first tractable transcription study. Five other candidate roots need metadata, representation or constituent-parallel resolution; Arda Viraz and Denkard VII remain later research candidates. Denkard V's heading says Book5 but its edition citation says Book7: the contradiction is recorded, not repaired by guesswork. All sixteen work exclusions remain binding, including insufficiently identified124 and517.

An in-memory structural probe of **all111 archived Denkard IV pages** recovered **196 source spans /4,665 whitespace terms**, with no empty pages, no exact repeated span strings, and matching raw-file hashes. This improves on counting10,484 raw-page terms containing navigation/editorial material. It does not prove semantic uniqueness, source purity, edition completeness or absence of held-out parallels. No derivative source corpus was saved, uploaded or used by a model. The smaller actual size is evidence against justifying a paid CPT run from inflated page-text counts.

The [book follow-up](BOOK-ACCESS-FOLLOWUP.md) found Skjærvø's author-linked2020 primer in readable public HTML. Four targeted forms provide generic lexical corroboration. The legal-context use of `hunsandīh` concerns agreement, so it does not certify the proposed contentedness label in our different passage. Extracted page markers and corrupted script glyphs require caution; no whole-book reading or image-verified pagination is claimed. Root directly checked the accessible `frazend`, `xrad` and `hunsandīh` passages as well. These research-exposed examples are not new sealed test material.

**Decision:** finish preparation of the genuinely unrun Gemma/Qwen plain/assisted DEV comparison in parallel. Do not wait indefinitely for a missing dictionary, retrain on fourteen unadjudicated labels, or launch CPT on the strength of raw archive counts. Keep the two deeper learning-regime hypotheses alive for a later controlled contrast supported by actual eligible data. Existing instruction-only results and earlier small-Qwen results are preserved, not repeated or presented as new experiments.

## Reproducible local probe

This is an extraction feasibility check, not a general cleaner. It reads only archived Denkard IV raw pages and their local metadata, preserves character data and editorial signs, and selects the explicit `miphts16` spans. The existing source files are unchanged. It does not load benchmark answers, predictions or models.

```powershell
@'
from pathlib import Path
from html.parser import HTMLParser
import json,re,hashlib,collections
class SourceSpans(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True); self.depth=0; self.anchor=None; self.parts=[]; self.items=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='a' and a.get('name'): self.anchor=a['name']
  if t=='span' and self.depth: self.depth+=1
  elif t=='span' and a.get('id')=='miphts16': self.depth=1; self.parts=[]; self.locator=self.anchor
  if self.depth and t=='br': self.parts.append('\n')
 def handle_endtag(self,t):
  if t=='span' and self.depth:
   self.depth-=1
   if self.depth==0: self.items.append((self.locator,''.join(self.parts)))
 def handle_data(self,s):
  if self.depth: self.parts.append(s)
p=Path('sources/local/public-texts-2026-09-20/titus')
d=json.loads((p/'documents.json').read_text(encoding='utf-8'))
rows=[]
for r in sorted(d,key=lambda r:r['url']):
 if not re.search(r'/dk4/dk4\d+\.htm$',r['url']): continue
 b=(p/r['file']).read_bytes(); assert hashlib.sha256(b).hexdigest()==r['sha256']
 q=SourceSpans(); q.feed(b.decode('utf-8')); q.close(); assert q.depth==0
 assert q.items and all(x[0] and x[1].strip() for x in q.items)
 rows.append((r,q.items))
assert [r['url'].rsplit('/',1)[-1] for r,_ in rows]==[f'dk4{i:03d}.htm' for i in range(1,112)]
counts=(len(rows),sum(len(items) for _,items in rows),sum(len(t.split()) for _,items in rows for _,t in items))
assert counts==(111,196,4665), counts
assert all(c==1 for c in collections.Counter(t for _,items in rows for _,t in items).values())
print('PASS: pages, source spans, whitespace terms =',counts)
'@ | & resources/local/hf-client-venv/Scripts/python.exe -B -X utf8 -
```

The exact-count checks establish reproducibility on this snapshot. They are not linguistic tests or training admission. Source-span samples from the first,37th,74th and111th numbered pages were inspected; whole-corpus philological collation was not performed.
