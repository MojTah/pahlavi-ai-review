"""Validate the retained corpus and build static pages for offline reading."""
import hashlib
import html
import json
import shutil
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "sources/local/parsig-2026-09-20"
STYLE = """body{font:18px/1.7 Georgia,serif;max-width:1080px;margin:2rem auto;padding:0 1rem;color:#263a36;background:#faf8f2}
a{color:#165e55}header{border-bottom:1px solid #bdcbc3;margin-bottom:2rem}h1{line-height:1.3}h2{margin-top:2rem}
article{padding:1rem 0;border-bottom:1px solid #ccd6cd}.layer{white-space:pre-wrap;overflow-wrap:anywhere}
label,small,.meta{font-family:system-ui,sans-serif;font-size:14px;color:#51645e}input{font:inherit;padding:.5rem;width:90%}
li{padding:.35rem}summary{cursor:pointer} .script{font-family:Parsig,serif;font-size:28px;direction:rtl}
.manichaean{font-family:Manichaean,serif;font-size:28px;direction:rtl}
@font-face{font-family:Parsig;src:url('../assets/Ham-dib2.ttf')} .note{border-left:3px solid #d4ba66;padding-left:1rem}
@font-face{font-family:Manichaean;src:url('../assets/NotoSansManichaean-Regular.ttf')}
"""


def esc(value):
    return html.escape(str(value), quote=True)


def strings(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n\n".join(strings(x) for x in value)
    if isinstance(value, dict):
        return strings(value.get("Section", value.get("Note", "")))
    return ""


def page(title, body):
    return ('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{esc(title)}</title><style>{STYLE}</style><body>{body}</body></html>')


class PlainHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    def handle_starttag(self, tag, attrs):
        if tag in ["p", "br", "div", "li", "tr"]:
            self.parts.append("\n")


def plain_html(value):
    parser = PlainHTML()
    parser.feed(value)
    return "".join(parser.parts).strip()


def main():
    manifest = json.loads((ARCHIVE / "manifest.json").read_text("utf-8"))
    for entry in manifest.values():
        raw = (ARCHIVE / entry["file"]).read_bytes()
        assert len(raw) == entry["bytes"] and hashlib.sha256(raw).hexdigest() == entry["sha256"], entry["url"]
    def cached(endpoint):
        entry = manifest.get(endpoint)
        return json.loads((ARCHIVE / entry["file"]).read_text("utf-8")) if entry else []
    inventory = json.loads((ROOT / "sources/parsig-live-inventory.json").read_text("utf-8"))
    expected = {r["id"]: (g, r) for g in inventory["groups"] for r in g["records"]}
    paths = sorted((ARCHIVE / "corpus").glob("*.json"))
    actual = {p.stem for p in paths}
    assert actual <= expected.keys(), "Unknown records in archive"
    (ARCHIVE / "reader").mkdir(exist_ok=True)
    (ARCHIVE / "assets").mkdir(exist_ok=True)
    shutil.copyfile(ROOT / "resources/local/parsig-font/Ham-dib2.ttf", ARCHIVE / "assets/Ham-dib2.ttf")
    manichaean = next((ARCHIVE / "site-assets").glob("NotoSansManichaean-*.ttf"), None)
    if manichaean:
        shutil.copyfile(manichaean, ARCHIVE / "assets/NotoSansManichaean-Regular.ttf")
    summaries = []
    paragraph_ids = set()
    layer_counts = Counter()
    for path in paths:
        raw = path.read_bytes()
        book = json.loads(raw)
        group, record = expected[book["book_id"]]
        assert book["title"] == record["title"]
        body = [f'<header><a href="../index.html">All texts</a><h1 dir="auto">{esc(book["title"])}</h1>'
            f'<p>{esc(group["title_en"])} · Record {esc(book["book_id"])}</p>'
            '<p class="meta">Source: Pārsīg Database and the editors/translators cited in each passage. '
            'Local source copy; collection does not establish reading or expert review.</p></header>']
        for language in ["fa", "en"]:
            introduction = strings(cached(f'book/bookdetailhtml/{book["book_id"]}/{language}'))
            if introduction:
                body.append(f'<details><summary>Introduction ({language})</summary><div class="layer" dir="auto">{esc(plain_html(introduction))}</div></details>')
        count = 0
        for chapter in book["chapters"]:
            body.append(f'<h2 dir="auto">{esc(chapter["title"])} <small>{esc(chapter["id"])}</small></h2>')
            versions = cached(f'book/bookversionlist/{book["book_id"]}/{chapter["id"]}')
            for version in versions:
                image_links = []
                for item in cached(f'book/bookversionlistdata/{version["Code"]}'):
                    image = next((ARCHIVE / "images").glob(str(item["Code"]) + ".*"), None)
                    if image:
                        image_links.append(f'<li><a href="../images/{esc(image.name)}">Page {esc(item["Sequence"])} · image {esc(item["Code"])}</a></li>')
                if image_links:
                    body.append(f'<details><summary>{esc(version["Title"])} — {len(image_links)} local pages</summary><ul>{"".join(image_links)}</ul></details>')
            for paragraph in chapter["paragraphs"]:
                code = str(paragraph["Code"])
                assert code not in paragraph_ids, "Duplicate paragraph identity"
                paragraph_ids.add(code)
                count += 1
                body.append(f'<article id="p{esc(code)}"><h3>§ {esc(paragraph["Sequence"])} <small>{esc(code)}</small></h3>')
                for key, value in paragraph.items():
                    if key in ["Code", "Sequence", "ChapterCode"]:
                        continue
                    text = strings(value)
                    if not text:
                        continue
                    layer_counts[key] += 1
                    css = ("manichaean" if book["group_id"] == "5" else "script") if key == "Text" else "note" if key == "Note" else ""
                    body.append(f'<section><h4>{esc(key)}</h4><div class="layer {css}" dir="auto">{esc(text)}</div></section>')
                body.append('</article>')
        (ARCHIVE / "reader" / f'{book["book_id"]}.html').write_text(page(book["title"], "\n".join(body)), encoding="utf-8")
        summaries.append({"id": book["book_id"], "title": book["title"], "group": group["title_en"],
            "chapters": len(book["chapters"]), "paragraphs": count, "sha256": hashlib.sha256(raw).hexdigest(),
            "reading_status": record["study_status"]})
    body = ['<header><p class="meta">PĀRSĪG · LOCAL RESEARCH ARCHIVE</p><h1>Middle Persian text reader</h1>',
        f'<p>{len(summaries)} of {len(expected)} records · {len(paragraph_ids)} numbered units</p>',
        '<p>Original transcriptions, translations, notes and credits retained. Use your browser’s Find command within a text.</p>',
        '<p class="meta">Source: Parsig Database, led by فرزانه گشتاسب, and its credited contributors. '
        'This offline archive is a study source, not a completed dictionary or independently reviewed translation.</p></header>',
        '<label for="filter">Find a text by title, collection or ID</label><br><input id="filter" type="search"><ul id="books">']
    for row in summaries:
        body.append(f'<li><a dir="auto" href="reader/{row["id"]}.html">{esc(row["title"])}</a> '
            f'<small>{row["id"]} · {esc(row["group"])} · {row["paragraphs"]} units</small></li>')
    body += ['</ul><p id="matches" aria-live="polite"></p>',
        '<script>const rows=[...document.querySelectorAll("#books li")];'
        'document.querySelector("#filter").addEventListener("input",e=>{let n=0;for(const row of rows){'
        'row.hidden=!row.textContent.toLowerCase().includes(e.target.value.toLowerCase());if(!row.hidden)n++}'
        'document.querySelector("#matches").textContent=n+" matching texts"});</script>']
    (ARCHIVE / "index.html").write_text(page("Parsig offline research reader", "\n".join(body)), encoding="utf-8")
    report = {"source": "https://parsigdatabase.com/", "expected_records": len(expected), "collected_records": len(summaries),
        "missing_records": sorted(set(expected) - actual), "chapters": sum(r["chapters"] for r in summaries),
        "numbered_units": len(paragraph_ids), "units_with_layer": dict(layer_counts),
        "verified_response_files": len(manifest), "response_bytes": sum(e["bytes"] for e in manifest.values()),
        "records": summaries, "reading_status_unchanged_by_collection": True}
    (ARCHIVE / "coverage.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k != "records"}))


if __name__ == "__main__":
    main()
