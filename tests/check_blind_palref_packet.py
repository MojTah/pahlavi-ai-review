"""Local fixture check; does not assess or execute a translation model."""
import importlib.util
import json
from collections import Counter
from pathlib import Path
import uuid

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("packets", ROOT / "scripts/prepare_blind_palref_comparison.py")
packets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packets)


def check():
    old = ROOT / "experiments/palref-v1/trained-20260927"
    scratch = ROOT / "resources/local" / ("palref-check-" + uuid.uuid4().hex)
    scratch.mkdir()
    output = scratch / "fixture"
    result = packets.prepare(old, old, output)
    assert result["status"] == "FIXTURE_SAME_RUN_NOT_NEW_RESULT"
    read = lambda path: [json.loads(line) for line in path.read_text("utf-8").splitlines()]
    original = {row["id"]: row for row in read(old / "predictions.jsonl")}
    mapping = read(output / "lead-only/mapping.jsonl")
    assert len(mapping) == len({row["id"] for row in mapping}) == 160
    expected = Counter((name, cid) for name in ("previous", "candidate") for cid in original)
    for reviewer in ("A", "B"):
        folder = output / ("reviewer-" + reviewer)
        assert {path.name for path in folder.iterdir()} == {"packet.jsonl", "INSTRUCTIONS.md"}
        decode = {row["id"]: row for row in mapping if row["reviewer"] == reviewer}
        rows = read(folder / "packet.jsonl")
        assert len(rows) == len({row["id"] for row in rows}) == 80
        assert Counter((row["condition"], row["prediction_id"]) for row in decode.values()) == expected
        for row in rows:
            source = original[decode[row["id"]]["prediction_id"]]
            assert row["text"] == source["text"] and row["status"] == source["status"]
            assert row["output_sha256"] == packets.sha(source["text"].encode("utf-8"))
            assert packets.sha(row["source_text"].encode("utf-8")) == source["input_sha256"]
            assert not {"condition", "prediction_id", "model_id", "adapter_sha256_or_none"} & row.keys()
    changed = scratch / "changed"
    changed.mkdir()
    predictions = list(original.values())
    predictions[0]["input_sha256"] = "0" * 64
    (changed / "predictions.jsonl").write_bytes(packets.lines(predictions))
    (changed / "run.json").write_bytes((old / "run.json").read_bytes())
    rejected = scratch / "rejected"
    try:
        packets.prepare(old, changed, rejected)
    except ValueError as error:
        assert "input changed" in str(error)
    else:
        raise AssertionError("Changed input accepted")
    assert not rejected.exists()
    print(json.dumps({"status": "PASS_FIXTURE_ONLY", "outputs": 160, "scratch": str(scratch)}))


if __name__ == "__main__":
    check()
