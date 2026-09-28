"""Collect the public grammatical-search index, preserving occurrence IDs.

This is an attested-form index, not a lemma dictionary or a full word-detail
export. Queries reproduce the site's category + All properties/books/chapters.
"""
import argparse
import json
import time
from pathlib import Path

from collect_parsig import ARCHIVE, ROOT, Collector, StopRun, digest, save_json, stamp


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", help="One observed group ID for a canary")
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    if not 1 <= args.limit <= 100:
        parser.error("Use a limit between 1 and 100")
    lock = ARCHIVE / "collector.lock"
    with lock.open("x", encoding="utf-8") as handle:
        handle.write(stamp())
    collector = None
    status = "FAILED"
    try:
        collector = Collector(args.limit)
        groups = collector.get("surf/allbookgroups/fa")
        categories = collector.get("tags/allwordcategorys/fa")
        paragraphs = {str(p["Code"]) for file in (ARCHIVE / "corpus").glob("*.json")
            for chapter in json.loads(file.read_text("utf-8"))["chapters"] for p in chapter["paragraphs"]}
        forms, occurrences = {}, {}
        queries = []
        for group in groups:
            group_id = str(group["Code"])
            if args.group and group_id != args.group:
                continue
            for category in categories:
                endpoint = f"tags/textproperty/{category['Code']}/All/{group_id}/All/All"
                rows = collector.get(endpoint)
                queries.append({"endpoint": endpoint, "rows": len(rows)})
                for row in rows:
                    form = row["Transcription"]
                    form_key = group_id + ":" + form
                    form_record = forms.setdefault(form_key, {"group_id": group_id, "source_form": form, "occurrence_ids": []})
                    for book in row["BookList"]:
                        for occurrence in book["TextList"]:
                            code = str(occurrence["TextCode"])
                            item = occurrences.setdefault(code, {"id": code, "book_id": str(book["BookCode"]),
                                "source_sequence": occurrence["Sequence"], "forms": [], "category_ids": [],
                                "paragraph_id_from_site_id": code[:-3], "paragraph_present": code[:-3] in paragraphs})
                            if form not in item["forms"]:
                                item["forms"].append(form)
                            if str(category["Code"]) not in item["category_ids"]:
                                item["category_ids"].append(str(category["Code"]))
                            if code not in form_record["occurrence_ids"]:
                                form_record["occurrence_ids"].append(code)
                print(json.dumps({"group": group_id, "category": str(category["Code"]), "forms_returned": len(rows)}), flush=True)
        report = {"source": "https://parsigdatabase.com/tags/?lang=fa", "collected_utc": stamp(),
            "group_filter": args.group, "scope": "Public grammatical-search results for each offered category; not full word detail, lemma or sense coverage.",
            "categories": categories, "queries": queries, "form_group_pairs": len(forms), "occurrences": len(occurrences),
            "occurrences_without_collected_paragraph": sum(not x["paragraph_present"] for x in occurrences.values()),
            "occurrences_with_multiple_source_forms": sum(len(x["forms"]) > 1 for x in occurrences.values())}
        suffix = "-group-" + args.group if args.group else ""
        save_json(ARCHIVE / ("vocabulary" + suffix + ".json"), {"report": report, "forms": list(forms.values()), "occurrences": list(occurrences.values())})
        print(json.dumps(report, ensure_ascii=True), flush=True)
        status = "COMPLETE_FOR_REQUESTED_INDEX"
    except (StopRun, KeyboardInterrupt) as error:
        status = "STOPPED_RESUMABLE"
        print(str(error), flush=True)
    except Exception as error:
        print(json.dumps({"error_type": type(error).__name__, "message": str(error)}), flush=True)
        raise SystemExit(1)
    finally:
        record = {"utc": stamp(), "phase": "vocabulary_index", "group": args.group, "status": status}
        if collector:
            record.update({"requests": collector.requests, "cache_reuses": collector.reused,
                "elapsed_seconds": round(time.monotonic() - collector.started, 2),
                "script_sha256": digest(Path(__file__).read_bytes()), "collector_sha256": digest((ROOT / "scripts/collect_parsig.py").read_bytes())})
        with (ARCHIVE / "runs.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")
        lock.unlink()
        print(json.dumps(record), flush=True)


if __name__ == "__main__":
    main()
