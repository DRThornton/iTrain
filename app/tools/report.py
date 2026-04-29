import json
from datetime import UTC, datetime
from pathlib import Path

try:
    from app.tools.runtime import default_reports_dir
except ImportError:  # pragma: no cover - supports direct app/ execution
    from tools.runtime import default_reports_dir


def _safe_stem(name: str) -> str:
    return name.replace(" ", "_")


def build_manager_report(
    results,
    learner_name="Anonymous",
    focus_areas=None,
    manual_names=None,
    document_type=None,
    extracted_policy_debug=None,
):
    summary = {
        "good": sum(1 for r in results if r["score"]["label"] == "good"),
        "neutral": sum(1 for r in results if r["score"]["label"] == "neutral"),
        "bad": sum(1 for r in results if r["score"]["label"] == "bad"),
    }

    weighted_score = (summary["good"] * 2) + (summary["neutral"] * 0) + (summary["bad"] * -3)

    recommendation = "review"
    if weighted_score >= 4:
        recommendation = "pass"
    elif weighted_score < 0:
        recommendation = "fail"

    report = {
        "learner_name": learner_name,
        "completed_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "manual_names": manual_names or [],
        "document_type": document_type or "safety_handbook",
        "summary": summary,
        "weighted_score": weighted_score,
        "recommendation": recommendation,
        "focus_areas": focus_areas or [],
        "results": results,
        "debug": {
            "extracted_policy_debug": extracted_policy_debug or [],
        },
    }
    return report


def render_manager_summary_markdown(report):
    summary = report["summary"]
    manuals = ", ".join(report.get("manual_names", [])) or "None provided"
    focus_areas = ", ".join(report.get("focus_areas", [])) or "None"
    lines = [
        f"# iTrain Manager Summary",
        "",
        f"**Learner:** {report['learner_name']}",
        f"**Completed:** {report['completed_at']}",
        f"**Document type:** {report.get('document_type', 'safety_handbook')}",
        f"**Manuals used:** {manuals}",
        f"**Recommendation:** {report['recommendation']}",
        f"**Weighted score:** {report['weighted_score']}",
        f"**Focus areas:** {focus_areas}",
        "",
        "## Score Summary",
        "",
        f"- Good: {summary['good']}",
        f"- Neutral: {summary['neutral']}",
        f"- Bad: {summary['bad']}",
        "",
        "## Question Results",
        "",
    ]

    for item in report["results"]:
        question_number = item.get("question_number")
        label = f"Question {question_number}" if question_number is not None else "Turn"
        if item.get("kind") == "follow_up" and question_number is not None:
            label = f"Question {question_number} Follow-up"
        lines.extend(
            [
                f"### {label}",
                "",
                f"**Prompt:** {item['prompt']}",
                "",
                f"**Response:** {item['response']}",
                "",
                f"**Score:** {item['score']['label']}",
                f"**Why:** {item['score']['rationale']}",
                f"**Citation:** {item['score']['citation']}",
                "",
            ]
        )

    return "\n".join(lines).strip() + "\n"


def save_report(report, reports_dir=None):
    report_dir = Path(reports_dir) if reports_dir is not None else default_reports_dir()
    report_dir.mkdir(parents=True, exist_ok=True)
    safe_name = _safe_stem(report["learner_name"])
    json_path = report_dir / f"{safe_name}_report.json"
    markdown_path = report_dir / f"{safe_name}_summary.md"

    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    markdown_path.write_text(render_manager_summary_markdown(report), encoding="utf-8")

    return {
        "json": str(json_path),
        "markdown": str(markdown_path),
    }
