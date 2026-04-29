from pathlib import Path

from app.tools.report import build_manager_report, render_manager_summary_markdown, save_report


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


def test_build_manager_report_includes_manual_names_and_debug_payload():
    debug_items = [{"policy": "Report spills immediately.", "category": "safety"}]
    report = build_manager_report(
        [make_result("good")],
        manual_names=["custom_manual.pdf"],
        document_type="procedural_manual",
        extracted_policy_debug=debug_items,
    )

    assert report["manual_names"] == ["custom_manual.pdf"]
    assert report["document_type"] == "procedural_manual"
    assert report["debug"]["extracted_policy_debug"] == debug_items


def test_render_manager_summary_markdown_includes_core_sections():
    report = build_manager_report(
        [make_result("good"), make_result("neutral")],
        learner_name="Demo User",
        manual_names=["manual.pdf"],
        document_type="procedural_manual",
        focus_areas=["procedure"],
    )

    markdown = render_manager_summary_markdown(report)

    assert "# iTrain Manager Summary" in markdown
    assert "**Learner:** Demo User" in markdown
    assert "**Manuals used:** manual.pdf" in markdown
    assert "## Question Results" in markdown
    assert "**Score:** good" in markdown


def test_save_report_writes_json_and_markdown_files():
    report = build_manager_report([make_result("good")], learner_name="Demo User")
    output_dir = Path("app/reports/test_output")
    output_dir.mkdir(parents=True, exist_ok=True)

    saved = save_report(report, reports_dir=output_dir)

    assert set(saved.keys()) == {"json", "markdown"}
    assert (output_dir / "Demo_User_report.json").exists()
    assert (output_dir / "Demo_User_summary.md").exists()
