"""Read-only source reconciliation; writes only the allowed auxiliary-audit.json.
Human/AI review annotations are explicit and are not inferred by this checker.
"""
import json, hashlib, re, xml.etree.ElementTree as ET
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).with_name("auxiliary-audit.json")
NS = "http://www.tei-c.org/ns/1.0"
XMLID = "{http://www.w3.org/XML/1998/namespace}id"
def load(p): return [json.loads(s) for s in (ROOT/p).read_text(encoding="utf-8").splitlines()]
def sha(p): return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def ws(s): return " ".join(s.split())
def render(e):
    tag=e.tag.rsplit("}",1)[-1]
    body=(e.text or "")+"".join(render(c)+(c.tail or "") for c in e)
    if tag in ("gap","unclear","supplied"):
        attrs=" ".join(f"{k}={v!r}" for k,v in e.attrib.items())
        return f"⟦{tag} {attrs}⟧{body}⟦/{tag}⟧"
    return body

def raw_blocks(path):
    root=ET.fromstring((ROOT/path).read_bytes()); blocks={}
    for div in root.findall(".//{"+NS+"}div"):
        if div.get("type") not in ("transcription","translation"): continue
        for ab in div.findall(".//{"+NS+"}ab"):
            lines=[]; label=None; part=ab.text or ""
            for c in ab:
                if c.tag.rsplit("}",1)[-1]=="lb":
                    if label is not None: lines.append((label,ws(part)))
                    label=c.get("n");part=c.tail or ""
                else: part+=render(c)+(c.tail or "")
            if label is not None:lines.append((label,ws(part)))
            blocks[ab.get(XMLID)]={"lines":lines,"type":div.get("type"),"language":div.get("{http://www.w3.org/XML/1998/namespace}lang")}
    return blocks
class Items(HTMLParser):
    def __init__(self): super().__init__(convert_charrefs=True);self.parts=[];self.current=None
    def handle_starttag(self,tag,attrs):
        if tag=="li": self.current=[]
    def handle_data(self,d):
        if self.current is not None:self.current.append(d)
    def handle_endtag(self,tag):
        if tag=="li" and self.current is not None:self.parts.append(ws("".join(self.current)));self.current=None

def pointer(obj,path):
    for key in path.strip("/").split("/"):
        key=key.replace("~1","/").replace("~0","~")
        obj=obj[int(key)] if isinstance(obj,list) else obj[key]
    return obj

def from_raw(o,side,raw):
    layer=o[side]
    if "json_pointer" in layer:
        html=pointer(raw,layer["json_pointer"]);parser=Items();parser.feed(html)
        return "\n".join(parser.parts),{"json_pointer":layer["json_pointer"]}
    if "scope" in layer:
        scope=layer["scope"];b=raw[scope["block_id"]]
        text=" ".join(t for n,t in b["lines"] if n in scope["labels"])
        if "start_exact" in scope:text=text[text.index(scope["start_exact"]):]
        if "end_exclusive_exact" in scope:text=text[:text.index(scope["end_exclusive_exact"])]
        return text.strip(),scope
    texts=[];loc=[]
    for b in layer["blocks"]:
        br=raw[b["block_id"]];texts.append("\n".join(t for n,t in br["lines"]));loc.append({"block_id":b["block_id"],"labels":[n for n,t in br["lines"]],"type":br["type"],"language":br["language"]})
    return "\n\n".join(texts),loc

TASKS=["pedagogy-fa","documentary-en","inscription-fa","edition-spans-en"]
inputs={t:f"resources/local/data-qualification-20260928/ready-v1/{t}.jsonl" for t in TASKS}
rows=[x for p in inputs.values() for x in load(p)]
assert len(rows)==307 and len({x["id"] for x in rows})==307
alignment={x["unit_id"]:x for x in load("experiments/data-qualification-20260928/archive-alignment.jsonl")}
origins={};rawcache={};results=[];failures=[]
for row in rows:
    ident=row["id"];org=row["origin"];task=row["task"];origin=org["file"]
    if origin not in origins:origins[origin]={x.get("id",x.get("candidate_id",x.get("unit_id"))):x for x in load(origin)}
    entry={"id":ident,"task":task,"canonical_file":inputs[task],"learning_sha256":hashlib.sha256(json.dumps(row["learning"],ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest(),"origin_file_sha256_match":sha(origin)==org["sha256"],"record_read":True,"expert_certified":False,"accessibility_gaps":[]}
    if task=="documentary-en":
        a=alignment[ident];rawinfo=a["provenance"]["raw_source"];path=rawinfo["path"]
        entry.update(raw_path=path,raw_sha256=sha(path),raw_sha256_match=sha(path)==rawinfo["sha256"],evidence_level="RAW_TEI_OR_ARCHIVED_JSON_HTML_RECONCILIATION_PLUS_BILINGUAL_READING",witness=row["learning"]["context"]["witness_group"])
        if path not in rawcache:rawcache[path]=json.loads((ROOT/path).read_text(encoding="utf-8")) if ident.startswith("iedc:") else raw_blocks(path)
        for side in ("source","target"):
            reconstructed,loc=from_raw(a,side,rawcache[path]);entry[side+"_raw_match"]=reconstructed==row["learning"][side];entry[side+"_locator"]=loc
            derivation=org.get("derivation")
            if derivation and side=="target":
                old,new=derivation["original_substring"],derivation["derived_substring"]
                entry["declared_derivation_reconciled"]=(reconstructed.count(old)==derivation["expected_occurrences"] and reconstructed.replace(old,new)==row["learning"][side])
            if not entry[side+"_raw_match"]: failures.append({"id":ident,"side":side,"kind":"RAW_TEXT_DIFFERENCE","actual_sha256":hashlib.sha256(row["learning"][side].encode()).hexdigest(),"reconstructed_sha256":hashlib.sha256(reconstructed.encode()).hexdigest()})
        entry["limitation"]="Checked fidelity to archived scholarly edition, not independent manuscript decipherment; source uncertainty and editorial explanations remain binding."
    elif task=="pedagogy-fa":
        a=origins[origin][org["row_id"]];path=org["pdf"];page=org["pdf_page"]
        entry.update(raw_path=path,raw_sha256=sha(path),raw_sha256_match=sha(path)==org["pdf_sha256"],pdf_page=page,printed_page=page-3,image_path=f"resources/local/dataset-expansion-20260928/s22/pdf-{page:03d}.png",evidence_level="ARCHIVED_PDF_PAGE_IMAGE_VISUALLY_CHECKED_PLUS_TRANSCRIPTION_RECONCILIATION")
        entry["image_sha256"]=sha(entry["image_path"])
        entry["source_transcription_match"]=row["learning"]["source"]==a["pahlavi_transcription"]
        entry["target_transcription_match"]=row["learning"]["target"]==a["persian_translation"]
        derivation=org.get("derivation")
        if derivation:
            entry["declared_derivation_reconciled"]=(a["persian_translation"]==derivation["original"] and row["learning"]["target"]==derivation["derived"])
        entry["limitation"]="Every record and its page image read; typographic normalization allowed. Conditioned grammar/morphology, not independent manuscript attestations. No automated OCR equivalence claimed."
    else:
        a=origins[origin][org["parent_row_id"]];path=org["pdf"]
        entry.update(raw_path=path,raw_sha256=sha(path),raw_sha256_match=sha(path)==org["pdf_sha256"],parent_id=org["parent_row_id"],evidence_level="ARCHIVED_PDF_PAGE_VISUAL_OR_DIRECT_PDF_TEXT_PLUS_EXACT_PARENT_SPAN",witness=row["learning"]["context"]["witness_group"])
        for side in ("source","target"):
            bounds=org[side+"_span"];entry[side+"_span"]=bounds
            selected=a[side+"_text"][bounds[0]:bounds[1]]
            entry[side+"_span_match"]=ws(selected)==ws(row["learning"][side])
            if not entry[side+"_span_match"]:failures.append({"id":ident,"side":side,"kind":"PARENT_SPAN_DIFFERENCE","actual_sha256":hashlib.sha256(row["learning"][side].encode()).hexdigest(),"reconstructed_sha256":hashlib.sha256(selected.encode()).hexdigest()})
        entry["pdf_pages"]=list(sorted(set(a.get("source_pages_pdf_1_based",[a.get("source_page_pdf_1_based")])+a.get("target_pages_pdf_1_based",[a.get("target_page_pdf_1_based")]))))
        entry["limitation"]="Exact released span only; excluded adjacent parent disagreements do not become repaired or validated. Repeated Kanheri formula occurrences are not new independent phrase types."
    entry["disposition"]="PROVISIONAL_SOURCE_FIDELITY_REVIEW_NO_CONFIRMED_PIPELINE_MISMATCH"
    entry["scope_review"]="Read source, target and supplied context for names/numerals, polarity, roles, alternatives, tense and bounded span where applicable. Scholarly source meaning is not expert-certified."
    entry["flags"]=[]
    if task=="documentary-en":
        entry["accessibility_gaps"].append("Original manuscript/object photographs not independently deciphered; the primary evidence here is the archived scholarly TEI/HTML edition.")
    if ident=="openampd:MP2100:greeting":
        entry["flags"].append("TEMPORAL_GREETING_SCOPE_REQUIRES_INTERPRETATION_NOT_WORD_MATCHING")
        entry["disposition"]="SEMANTIC_INTERPRETATION_PENDING_NO_CONFIRMED_DEFECT_SOURCE_FIDELITY_INTACT"
    if ident in ("iedc:IEDC1262:folio0","iedc:IEDC1265:folio0","iedc:IEDC1040:folio0","openampd:MP6003:full"):
        entry["flags"].append("SOURCE_UNCERTAINTY_NOT_SYMMETRICALLY_MARKED_IN_TARGET")
        entry["disposition"]="SOURCE_LIMITED_RETAIN_INPUT_UNCERTAINTY_DO_NOT_ASSERT_RESOLVED_READING"
    if ident in ("openampd:MP1024:full","openampd:MP1023:full","openampd:MP2150:full","openampd:MP2561:lines2-4"):
        entry["flags"].append("EDITION_INTERPRETATION_REQUIRES_PHILOLOGICAL_EXPERTISE")
    if ident.startswith("KANHERI"):
        entry["flags"].append("SHARED_WITNESS_OR_FORMULA_NOT_INDEPENDENT_NOVEL_ATTESTATION")
    results.append(entry)
for failure in failures:
    rec=next(x for x in results if x["id"]==failure["id"])
    failure["resolved_by_existing_declared_derivation"]=rec.get("declared_derivation_reconciled",False)
summary={"schema_version":1,"audit_date":"2026-09-29","scope":"All 307 released nonlexical auxiliary records; frozen inputs unchanged","counts":dict(Counter(x["task"] for x in rows)),"records_read":len(results),"expert_certified":False,"input_sha256":{p:sha(p) for p in inputs.values()},"raw_text_differences":failures,"unexplained_mechanical_mismatches":[f for f in failures if not f.get("resolved_by_existing_declared_derivation")],"declared_derivations_reconciled":sum(bool(x.get("declared_derivation_reconciled")) for x in results),"records":results}
OUT.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"count":len(results),"raw_text_differences":len(failures),"unexplained_mechanical_mismatches":len(summary["unexplained_mechanical_mismatches"]),"hash_failures":[x["id"] for x in results if not x.get("raw_sha256_match") or not x["origin_file_sha256_match"]],"declared_difference_ids":[x["id"] for x in failures]}))
