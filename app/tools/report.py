import json
from datetime import datetime
from pathlib import Path


def build_manager_report(results, learner_name="Anonymous", focus_areas=None):
    summary = {
        "good": sum(1 for r in results if r["score"]["label"] == "good"),
        "neutral": sum(1 for r in results if r["score"]["label"] == "neutral"),
        "bad": sum(1 for r in results if r["score"]["label"] == "bad"),
    }

    recommendation = "pass"
    if summary["bad"] >= 1 or summary["neutral"] >= 2:
        recommendation = "review"
    if summary["bad"] >= 2:
        recommendation = "fail"

    report = {
        "learner_name": learner_name,
        "completed_at": datetime.utcnow().isoformat() + "Z",
        "summary": summary,
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
