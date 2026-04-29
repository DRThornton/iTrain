import json
from pathlib import Path

from app.tools.scenarios import detect_document_type, looks_like_policy_line
from app.tools.scoring import score_response


DEFAULT_BENCHMARK_PATH = Path(__file__).resolve().parents[1] / "data" / "benchmark_cases.json"


def load_benchmark_cases(path: str | Path = DEFAULT_BENCHMARK_PATH):
    benchmark_path = Path(path)
    payload = json.loads(benchmark_path.read_text(encoding="utf-8"))
    return payload.get("cases", [])


def evaluate_benchmark_case(case: dict):
    kind = case["kind"]

    if kind == "scoring":
        result = score_response(case["response"], case["policy"], case.get("rubric", {}))
        actual = result["label"]
    elif kind == "document_type":
        result = detect_document_type(case["text"])
        actual = result["document_type"]
    elif kind == "policy_line":
        result = {"accepted": looks_like_policy_line(case["text"])}
        actual = result["accepted"]
    else:
        raise ValueError(f"Unsupported benchmark case kind: {kind}")

    return {
        "id": case["id"],
        "kind": kind,
        "expected": case["expected"],
        "actual": actual,
        "passed": actual == case["expected"],
        "details": result,
        "tags": case.get("tags", []),
    }


def run_benchmark(cases: list[dict] | None = None):
    benchmark_cases = cases if cases is not None else load_benchmark_cases()
    results = [evaluate_benchmark_case(case) for case in benchmark_cases]
    passed = sum(1 for result in results if result["passed"])

    by_kind = {}
    for result in results:
        kind_stats = by_kind.setdefault(result["kind"], {"passed": 0, "total": 0})
        kind_stats["total"] += 1
        if result["passed"]:
            kind_stats["passed"] += 1

    return {
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "by_kind": by_kind,
        "results": results,
    }


def format_benchmark_summary(summary: dict):
    lines = [
        f"Benchmark results: {summary['passed']}/{summary['total']} passed",
    ]
    for kind, stats in sorted(summary["by_kind"].items()):
        lines.append(f"- {kind}: {stats['passed']}/{stats['total']} passed")

    failures = [result for result in summary["results"] if not result["passed"]]
    if failures:
        lines.append("Failures:")
        for failure in failures:
            lines.append(
                f"- {failure['id']}: expected {failure['expected']!r}, got {failure['actual']!r}"
            )

    return "\n".join(lines)


if __name__ == "__main__":
    print(format_benchmark_summary(run_benchmark()))
