from app.tools.report import build_manager_report


def make_result(label: str):
    return {
        "scenario_id": 1,
        "prompt": "prompt",
        "response": "response",
        "score": {"label": label, "rationale": "why", "citation": "policy"},
    }


def test_build_manager_report_passes_on_strong_good_results():
    report = build_manager_report(
        [make_result("good"), make_result("good"), make_result("neutral")]
    )

    assert report["weighted_score"] == 4
    assert report["recommendation"] == "pass"
    assert report["completed_at"].endswith("Z")


def test_build_manager_report_reviews_borderline_results():
    report = build_manager_report(
        [make_result("good"), make_result("neutral"), make_result("neutral")]
    )

    assert report["weighted_score"] == 2
    assert report["recommendation"] == "review"


def test_build_manager_report_fails_when_bad_outweighs_good():
    report = build_manager_report(
        [make_result("good"), make_result("neutral"), make_result("bad")]
    )

    assert report["weighted_score"] == -1
    assert report["recommendation"] == "fail"
