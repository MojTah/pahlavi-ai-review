"""Apply the unchanged PAL-REF scorer to its forty Pahlavi-to-Persian cases."""
import argparse
import importlib.util
import json
from pathlib import Path


def score(directory):
    path = Path(__file__).resolve().parents[1] / "benchmarks/pal-reference-v1/benchmark.py"
    spec = importlib.util.spec_from_file_location("frozen_palref", path)
    benchmark = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(benchmark)
    frozen, all_cases = benchmark.verify()
    directory = Path(directory).resolve()
    if directory.is_relative_to(benchmark.ROOT):
        raise ValueError("Results must remain outside the frozen benchmark")
    cases = {key: case for key, case in all_cases.items()
             if (case["source_language"], case["target_language"]) == ("pal", "fa")}
    assert len(cases) == 40
    # Only report this evaluated direction; original files and scoring stay unchanged.
    benchmark.DIRECTIONS = ("pal>fa",)
    result = benchmark.score(directory, frozen, cases)
    result["scope"] = "PAL-REF v1 pal>fa projection: forty cases; other directions not evaluated"
    assert result["directions"]["pal>fa"]["total"] == 40
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    print(json.dumps(score(parser.parse_args().directory), ensure_ascii=False, indent=2))
