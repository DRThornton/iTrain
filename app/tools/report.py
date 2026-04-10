import json
from datetime import datetime
from pathlib import Path


def build_manager_report(results, learner_name="Anonymous", focus_areas=None):
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
        "completed_at": datetime.utcnow().isoformat() + "Z",
        "summary": summary,
        "weighted_score": weighted_score,
        "recommendation": recommendation,
        "focus_areas": focus_areas or [],
        "results": results,
    }
    return report


def save_report(report, reports_dir="app/reports"):
    Path(reports_dir).mkdir(parents=True, exist_ok=True)
    filename = f"{report['learner_name'].replace(' ', '_')}_report.json"
    path = Path(reports_dir) / filename
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return str(path)
