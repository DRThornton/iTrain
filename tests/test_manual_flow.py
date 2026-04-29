import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "app"))

from agent import TrainingAgent
from tools.scoring import score_response
from app.tools.scenarios import extract_policies, looks_like_policy_line


def test_extract_policies_keeps_manual_cleaning_in_procedure_category():
    handbook_text = """
    Touch Screen Calibration
    Use a soft cloth without solvents or abrasive cleaners.
    """

    policies = extract_policies(handbook_text, document_type="procedural_manual")

    assert policies
    assert policies[0]["category"] == "procedure"
    assert "according to the manual" in policies[0]["prompt"].lower()
    assert "exact step" in policies[0]["prompt"].lower()


def test_looks_like_policy_line_rejects_truncated_manual_fragments():
    assert not looks_like_policy_line(
        "When finished, a dialog box will appear confirming the successful"
    )
    assert not looks_like_policy_line(
        "1. Use the 4 wires as instructed in the“Making 4 Wires Work"
    )


def test_score_response_marks_obviously_bad_manual_answer_as_bad():
    score = score_response(
        "I'd quit on the spot, and make sure to leave all messes uncleaned for my stupid boss",
        "When finished, remove the SD card and keep the work area clean.",
        {},
    )

    assert score["label"] == "bad"


def test_score_response_marks_soft_damp_cloth_answer_as_good():
    score = score_response(
        "Clean with a soft damp cloth.",
        "Use a soft, damp cloth to clean the screen.",
        {},
    )

    assert score["label"] == "good"


def test_score_response_marks_g_wire_terminal_c_answer_as_good():
    score = score_response(
        "Place the G wire on terminal C",
        "4. Remove the “G wire” from the terminal marked G.",
        {},
    )

    assert score["label"] == "good"


def test_score_response_marks_plus_key_answer_as_good():
    score = score_response(
        "Use the Plus Key to move to the next parameter",
        "Use the Plus Key to move to the next parameter (Set Point Differential).",
        {},
    )

    assert score["label"] == "good"


def test_score_response_marks_enter_key_answer_as_good():
    score = score_response(
        "Press the Enter Key to display the value of the selected parameter.",
        "Press the Enter Key to display the value of the selected parameter.",
        {},
    )

    assert score["label"] == "good"


def test_score_response_marks_defrost_indicator_answer_as_good():
    score = score_response(
        "The Defrost Symbol will illuminate letting you know defrost is in effect.",
        "The Defrost Symbol will illuminate letting you know defrost is in effect.",
        {},
    )

    assert score["label"] == "good"


def test_score_response_marks_date_time_step_answer_as_good():
    score = score_response(
        "step through all six date/time fields",
        "You must step through all six Date/Time fields to change any one field.",
        {},
    )

    assert score["label"] == "good"


def test_score_response_marks_defrost_light_turns_on_answer_as_good():
    score = score_response(
        "the defrost light turns on",
        "The Defrost Symbol will illuminate letting you know defrost is in effect.",
        {},
    )

    assert score["label"] == "good"


def test_training_agent_assigns_unique_follow_up_turn_ids():
    rubric = {}
    agent = TrainingAgent(rubric=rubric, max_turns=2)
    session = agent.start_session(
        """
        Installation Instructions
        Remove and Replace the Old Thermostat
        • Assemble tools: Flat blade screwdriver, wire cutters and wire strippers.
        • Turn off the power to the Heating/Air Conditioning system at the main fuse panel.
        """,
        manual_names=["manual.pdf"],
    )

    first_turn_id = session["current"]["id"]
    updated_session, result = agent.submit_response(session, learner_name="Demo User", response="Not sure")

    assert result is not None
    assert updated_session["current"]["kind"] == "follow_up"
    assert updated_session["current"]["id"] > session["total_primary_turns"]
    assert updated_session["current"]["id"] != first_turn_id
    assert updated_session["history"][0]["question_number"] == 1


def test_extract_policies_skips_visual_overview_page_text_without_step_context():
    handbook_text = """
    Get To Know Your Thermostat
    Dropdown Dashboard
    Press the HOME button to return to the Home Screen.
    Select Onboard to view room temperature.
    """

    policies = extract_policies(handbook_text, document_type="procedural_manual")

    assert policies == []


def test_extract_policies_merges_location_line_for_traulsen_style_manual_text():
    handbook_text = """
    3. INSTALLATION
    3A - LOCATION:
    Select a proper location for your Traulsen unit, away
    from extreme heat and allow proper clearance for air circulation.
    3B - PACKAGING:
    All Traulsen units are shipped from the factory bolted to a sturdy wooden pallet.
    """

    policies = extract_policies(handbook_text, document_type="procedural_manual")

    assert policies
    joined = " ".join(item["policy"].lower() for item in policies)
    assert "away from extreme heat" in joined
    assert "self-" not in joined


def test_extract_policies_uses_next_step_as_expected_policy_for_manual_sequence():
    handbook_text = """
    Installation Instructions
    Making 4 Wires Work When 5 Wires Are Required
    4. Remove the G wire from the terminal marked G.
    5. Place the G wire on terminal C.
    """

    policies = extract_policies(handbook_text, document_type="procedural_manual")

    assert policies
    assert policies[0]["policy"].lower().startswith("4. remove the g wire")
    assert policies[0]["expected_policy"].lower().startswith("5. place the g wire")
    assert "what step comes next" in policies[0]["prompt"].lower()


def test_score_response_marks_next_step_answer_as_good_when_sequence_expected():
    score = score_response(
        "Place the G wire on terminal C",
        "5. Place the G wire on terminal C.",
        {},
    )

    assert score["label"] == "good"
