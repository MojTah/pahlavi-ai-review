"""Read-only, resumable archive of endpoints used by Parsig's public reader.

Uses Python's standard library. The site's own public client authorization is
held in memory and sent only to its exact HTTPS API host; never logged.
"""
import argparse
import base64
import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = "https://mpdb.parsigdatabase.com/"
CLIENT = ROOT / "sources/local/parsig-2026-09-20/site-assets/main.a548495a.js"
ARCHIVE = ROOT / "sources/local/parsig-2026-09-20"


def stamp():
    return datetime.now(timezone.utc).isoformat()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(raw)
    temporary.replace(path)


def save_json(path, value):
    save(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


class StopRun(Exception):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError("Redirect refused; authorization stays on the original host")


class Collector:
    def __init__(self, limit):
        self.limit = limit
        self.requests = 0
        self.reused = 0
        self.last = 0
        self.started = time.monotonic()
        self.manifest_path = ARCHIVE / "manifest.json"
        self.manifest = json.loads(self.manifest_path.read_text("utf-8")) if self.manifest_path.exists() else {}
        self.bytes = sum(x["bytes"] for x in self.manifest.values())
        client_raw = CLIENT.read_bytes()
        self.client_sha = digest(client_raw)
        match = re.search(r'''Authorization\s*:\s*["'](Basic [A-Za-z0-9+/=]+)["']''', client_raw.decode("utf-8"))
        if not match:
            raise RuntimeError("Site client authorization format changed")
        self.authorization = match[1]
        self.opener = urllib.request.build_opener(NoRedirect)

    def get(self, endpoint):
        if not re.fullmatch(r"[A-Za-z0-9_/-]+", endpoint) or ".." in endpoint:
            raise ValueError("Unexpected endpoint characters")
        # Only endpoints already observed in the site's own public client.
        prefix = endpoint.rsplit("/", 1)[0]
        allowed = ("surf/", "book/bookdetail", "book/bookversion", "book/allbooks/", "book/booksofbookgroup/", "pages/", "tags/", "sentence/detail/")
        if not endpoint.startswith(allowed):
            raise ValueError("Endpoint outside observed read-only reader scope")
        key = digest(endpoint.encode())
        target = ARCHIVE / "responses" / (key + ".json")
        if endpoint in self.manifest:
            item = self.manifest[endpoint]
            raw = target.read_bytes()
            if digest(raw) != item["sha256"] or len(raw) != item["bytes"]:
                raise RuntimeError("Cached response checksum failed: " + endpoint)
            self.reused += 1
            return json.loads(raw)
        if self.requests >= self.limit or self.bytes >= 500_000_000 or time.monotonic() - self.started > 5400:
            raise StopRun("Request, byte or time boundary reached; resume uses verified cache")
        time.sleep(max(0, .55 - (time.monotonic() - self.last)))
        request = urllib.request.Request(API + endpoint, headers={
            "Authorization": self.authorization, "Accept": "application/json",
            "User-Agent": "ParsigLocalResearchArchive/0.1 (read-only; sequential)"})
        self.last = time.monotonic()
        self.requests += 1
        with self.opener.open(request, timeout=40) as response:
            content_type = response.headers.get("Content-Type", "")
            if "json" not in content_type:
                raise RuntimeError("Expected JSON: " + endpoint)
            raw = response.read(50_000_001)
        if len(raw) > 50_000_000 or self.bytes + len(raw) > 500_000_000:
            raise StopRun("Response would exceed the local archive limit")
        value = json.loads(raw)
        if not isinstance(value, (list, dict)):
            raise RuntimeError("Unexpected response shape: " + endpoint)
        save(target, raw)
        self.manifest[endpoint] = {"url": API + endpoint, "file": str(target.relative_to(ARCHIVE)).replace("\\", "/"),
            "bytes": len(raw), "sha256": digest(raw), "retrieved_utc": stamp(), "content_type": content_type}
        self.bytes += len(raw)
        save_json(self.manifest_path, self.manifest)
        if self.requests % 25 == 0:
            print(json.dumps({"requests": self.requests, "cached": len(self.manifest), "bytes": self.bytes, "endpoint": endpoint}), flush=True)
        return value

    def corpus(self, wanted):
        groups = self.get("surf/allbookgroups/fa")
        inventory = json.loads((ROOT / "sources/parsig-live-inventory.json").read_text("utf-8"))
        expected = {(g["id"], r["id"]): r["title"] for g in inventory["groups"] for r in g["records"]}
        found = {}
        for group in groups:
            books = self.get(f"surf/bookgroupsbook/{group['Code']}/fa")
            for book in books:
                found[(str(group["Code"]), str(book["Code"]))] = book["Title"]
        if found != expected:
            save_json(ARCHIVE / "inventory-drift.json", {"expected": [[*k,v] for k,v in expected.items()], "actual": [[*k,v] for k,v in found.items()]})
            raise RuntimeError("Live inventory differs from the frozen 126-record list")
        for (group, code), title in found.items():
            if wanted and code not in wanted:
                continue
            chapters = self.get(f"surf/bookschapter/{code}/fa")
            result = {"book_id": code, "group_id": group, "title": title, "chapters": []}
            for chapter in chapters:
                chapter_code = str(chapter["Code"])
                options = self.get(f"surf/chaptersparagraph/{chapter_code}")
                paragraphs = self.get(f"surf/paragraph/{code}/{chapter_code}/All")
                if {str(p['Code']) for p in paragraphs} != {str(p['Code']) for p in options}:
                    raise RuntimeError("Paragraph inventory mismatch: " + chapter_code)
                if len({str(p['Code']) for p in paragraphs}) != len(paragraphs):
                    raise RuntimeError("Duplicate paragraph IDs: " + chapter_code)
                if any(str(p["ChapterCode"]) != chapter_code for p in paragraphs):
                    raise RuntimeError("Chapter identity mismatch: " + chapter_code)
                result["chapters"].append({"id": chapter_code, "title": chapter["Title"], "paragraphs": paragraphs})
            save_json(ARCHIVE / "corpus" / (code + ".json"), result)
            print(json.dumps({"book": code, "chapters": len(chapters), "paragraphs": sum(len(c['paragraphs']) for c in result['chapters'])}), flush=True)

    def supporting(self, wanted, images=False):
        for language in ["fa", "en"]:
            for code in ["1", "9", "201", "202", "203", "204", "301", "601", "602", "603", "604", "701", "702", "703", "801"]:
                self.get(f"pages/datapages/{code}/{language}")
            for code in ["601", "602", "603", "604", "701", "702", "703"]:
                self.get(f"pages/htmlpages/{code}/{language}")
            self.get(f"pages/menu/{language}")
            self.get(f"book/allbooks/{language}")
        self.get("pages/wordsummery")
        categories = self.get("tags/allwordcategorys/fa")
        for category in categories:
            self.get(f"tags/wordpropertytype/{category['Code']}/fa")
        for path in sorted((ARCHIVE / "corpus").glob("*.json")):
            book = json.loads(path.read_text("utf-8"))
            code = book["book_id"]
            if wanted and code not in wanted:
                continue
            for language in ["fa", "en"]:
                self.get(f"book/bookdetaildata/{code}/{language}")
                self.get(f"book/bookdetailhtml/{code}/{language}")
            for chapter in book["chapters"]:
                versions = self.get(f"book/bookversionlist/{code}/{chapter['id']}")
                for version in versions:
                    pages = self.get(f"book/bookversionlistdata/{version['Code']}")
                    if images:
                        for page in pages:
                            pic = self.get(f"book/bookversiongetpic/{page['Code']}")
                            if pic and pic[0].get("Picture"):
                                value = pic[0]["Picture"]
                                payload = value.split(",", 1)[1] if value.startswith("data:") else value
                                raw = base64.b64decode(payload, validate=True)
                                extension = ".jpg" if raw.startswith(b"\xff\xd8\xff") else ".png" if raw.startswith(b"\x89PNG\r\n\x1a\n") else ".bin"
                                save(ARCHIVE / "images" / (str(page["Code"]) + extension), raw)
            print(json.dumps({"supporting_book": code}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=["corpus", "supporting", "images"])
    parser.add_argument("--books", help="Comma-separated IDs for a bounded canary")
    parser.add_argument("--limit", type=int, default=2000, help="Maximum new requests; cached responses do not count")
    args = parser.parse_args()
    if not 1 <= args.limit <= 2000:
        parser.error("limit must be between 1 and 2000")
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    lock = ARCHIVE / "collector.lock"
    # Exclusive create prevents two collection owners. A failed run removes it in finally.
    with lock.open("x", encoding="utf-8") as handle:
        handle.write(stamp())
    collector = None
    status = "FAILED"
    try:
        collector = Collector(args.limit)
        wanted = set(args.books.split(",")) if args.books else None
        if args.phase == "corpus":
            collector.corpus(wanted)
        else:
            collector.supporting(wanted, images=args.phase == "images")
        status = "COMPLETE_FOR_REQUESTED_PHASE"
    except (StopRun, KeyboardInterrupt) as error:
        status = "STOPPED_RESUMABLE"
        print(str(error), flush=True)
    except Exception as error:
        # Do not emit request objects, headers or credentials in exceptions.
        print(json.dumps({"error_type": type(error).__name__, "message": str(error)}), flush=True)
        raise SystemExit(1)
    finally:
        record = {"utc": stamp(), "phase": args.phase, "books": args.books, "status": status}
        if collector:
            record.update({"requests": collector.requests, "cache_reuses": collector.reused,
                "cache_responses": len(collector.manifest), "cache_bytes": collector.bytes,
                "elapsed_seconds": round(time.monotonic() - collector.started, 2),
                "script_sha256": digest(Path(__file__).read_bytes()), "client_sha256": collector.client_sha})
        with (ARCHIVE / "runs.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")
        lock.unlink()
        print(json.dumps(record), flush=True)


if __name__ == "__main__":
    main()
