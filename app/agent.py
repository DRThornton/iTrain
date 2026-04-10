from tools.report import build_manager_report, save_report
from tools.scenarios import build_follow_up_scenario, build_initial_scenarios, extract_policies
from tools.scoring import score_response


class TrainingAgent:
    """Simple controller that chooses the next training step from learner performance."""

    def __init__(self, rubric, max_turns=5):
        self.rubric = rubric
        self.max_turns = max_turns

    def start_session(self, handbook_text: str):
        policies = extract_policies(handbook_text)
        scenarios = build_initial_scenarios(policies, max_scenarios=self.max_turns)
        current = scenarios[0] if scenarios else None

        return {
            "policies": policies[:10],
            "queue": scenarios[1:],
            "current": current,
            "history": [],
            "weak_categories": [],
            "completed": False,
        }

    def _count_primary_turns(self, session) -> int:
        return sum(1 for item in session.get("history", []) if item.get("kind", "scenario") != "follow_up")

    def submit_response(self, session, learner_name: str, response: str):
        if session.get("completed") or session.get("current") is None:
            return session, None

        scenario = session["current"]
        score = score_response(response, scenario["policy"], self.rubric)
        session["history"].append(
            {
                "scenario_id": scenario["id"],
                "kind": scenario.get("kind", "scenario"),
                "category": scenario["category"],
                "prompt": scenario["prompt"],
                "policy": scenario["policy"],
                "response": response,
                "score": score,
            }
        )

        if score["label"] != "good" and scenario["category"] not in session["weak_categories"]:
            session["weak_categories"].append(scenario["category"])

        primary_turns_completed = self._count_primary_turns(session)
        remaining_primary_turns = self.max_turns - primary_turns_completed
        should_follow_up = (
            score["label"] != "good"
            and scenario.get("kind") != "follow_up"
            and remaining_primary_turns >= 0
        )

        if should_follow_up:
            next_id = max(item["scenario_id"] for item in session["history"]) + 1
            session["current"] = build_follow_up_scenario(scenario, next_id)
            message = "The agent wants one follow-up response before moving on."
        elif session["queue"] and remaining_primary_turns > 0:
            session["current"] = session["queue"].pop(0)
            message = "The agent selected the next scenario."
        else:
            session["current"] = None
            session["completed"] = True
            message = "Training evidence is complete."

        report = None
        if session["completed"]:
            results = []
            for item in session["history"]:
                results.append(
                    {
                        "scenario_id": item["scenario_id"],
                        "prompt": item["prompt"],
                        "response": item["response"],
                        "score": item["score"],
                    }
                )

            report = build_manager_report(
                results,
                learner_name=learner_name,
                focus_areas=session["weak_categories"],
            )
            path = save_report(report, reports_dir="app/reports")
            report["saved_to"] = path

        return session, {"score": score, "message": message, "report": report}
