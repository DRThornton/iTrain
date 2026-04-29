from app.tools.benchmark import (
    format_benchmark_summary,
    load_benchmark_cases,
    run_benchmark,
)


def test_benchmark_cases_all_match_expected_results():
    summary = run_benchmark()

    assert summary["total"] > 0
    assert summary["failed"] == 0, format_benchmark_summary(summary)


def test_benchmark_dataset_covers_scoring_and_extraction_behaviors():
    cases = load_benchmark_cases()
    kinds = {case["kind"] for case in cases}

    assert "scoring" in kinds
    assert "document_type" in kinds
    assert "policy_line" in kinds
