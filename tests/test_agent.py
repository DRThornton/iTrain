import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "app"))

from agent import TrainingAgent


def test_start_session_tracks_actual_primary_turn_count():
    rubric = {
        "must_mention_any": ["report to supervisor"],
        "bad_actions": ["ignore", "guess", "leave it"],
    }
    agent = TrainingAgent(rubric=rubric, max_turns=5)

    session = agent.start_session(
        """
        Housekeeping
        Employees must clean spills immediately or block the area and report the hazard.

        Vehicle Safety
        Ignition keys must not be left with the equipment after hours or when a vehicle is parked in a public location.
        """
    )

    assert session["total_primary_turns"] == 2
    assert session["current"] is not None
    assert len(session["queue"]) == 1
