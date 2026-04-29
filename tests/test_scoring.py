from app.tools.scoring import score_response


def test_score_response_does_not_mark_confused_guess_language_as_bad():
    rubric = {
        "must_mention_any": ["ask a manager"],
        "bad_actions": ["ignore", "guess", "leave it"],
    }

    score = score_response(
        "I am confused by this scenario, so I guess I would ask a manager for clarification.",
        "Employees must never guess about refund policy. They should ask a manager.",
        rubric,
    )

    assert score["label"] != "bad"


def test_score_response_keeps_real_bad_guess_action():
    rubric = {
        "must_mention_any": ["ask a manager"],
        "bad_actions": ["ignore", "guess", "leave it"],
    }

    score = score_response(
        "I would guess and give the customer a refund.",
        "Employees must never guess about refund policy. They should ask a manager.",
        rubric,
    )

    assert score["label"] == "bad"


def test_score_response_marks_intentionally_hidden_reporting_response_as_bad():
    rubric = {
        "must_mention_any": ["report to supervisor"],
        "bad_actions": ["ignore", "guess", "leave it"],
    }

    score = score_response(
        "I would hide.",
        "The trade contractor must notify PCL of all incidents including near misses.",
        rubric,
    )

    assert score["label"] == "bad"


def test_score_response_marks_hazard_cover_up_as_bad():
    rubric = {
        "must_mention_any": ["clean spill"],
        "bad_actions": ["ignore", "guess", "leave it"],
    }

    score = score_response(
        "I would cover it with some dirt and keep working. The hazard can't hurt us now.",
        "Clean up and dispose of combustible trash.",
        rubric,
    )

    assert score["label"] == "bad"


def test_score_response_marks_reporting_avoidance_as_bad():
    rubric = {
        "must_mention_any": ["report to supervisor"],
        "bad_actions": ["ignore", "guess", "leave it"],
    }

    score = score_response(
        "I don't need to tell him. What they don't know can't hurt them.",
        "Report any unsafe acts and unsafe conditions to the PCL project.",
        rubric,
    )

    assert score["label"] == "bad"


def test_score_response_marks_ppe_refusal_as_bad():
    rubric = {
        "must_mention_any": ["report to supervisor"],
        "bad_actions": ["ignore", "guess", "leave it"],
    }

    score = score_response(
        "I would put on the protective equipment unless I feel like it's too uncomfortable.",
        "Limb and body protection must be worn and equipment designed to protect employees from injury to their limbs and body must be used.",
        rubric,
    )

    assert score["label"] == "bad"


def test_score_response_recognizes_ppe_language_as_good_for_protective_equipment_policy():
    rubric = {
        "must_mention_any": ["report to supervisor"],
        "bad_actions": ["ignore", "guess", "leave it"],
    }

    score = score_response(
        "I would ensure I am wearing the correct PPE as required.",
        "Limb and body protection must be worn and equipment designed to protect employees from injury to their limbs and body must be used.",
        rubric,
    )

    assert score["label"] == "good"


def test_score_response_downgrades_policy_copy_paste_to_neutral():
    rubric = {
        "must_mention_any": ["clean spill", "block the area"],
        "bad_actions": ["ignore", "guess", "leave it"],
    }

    score = score_response(
        "Must clean spills immediately or block the area and report the hazard.",
        "Employees must clean spills immediately or block the area and report the hazard.",
        rubric,
    )

    assert score["label"] == "neutral"


def test_score_response_does_not_mark_negated_policy_guess_language_as_bad():
    rubric = {
        "must_mention_any": ["ask a manager"],
        "bad_actions": ["ignore", "guess", "leave it"],
    }

    score = score_response(
        "Must never guess about refund policy.",
        "Employees must never guess about refund policy. They should check the policy or ask a manager.",
        rubric,
    )

    assert score["label"] != "bad"


def test_score_response_keeps_applied_answer_above_copy_paste():
    rubric = {
        "must_mention_any": ["clean spill", "block the area"],
        "bad_actions": ["ignore", "guess", "leave it"],
    }

    score = score_response(
        "I would clean the spill right away, block the area, and report the hazard.",
        "Employees must clean spills immediately or block the area and report the hazard.",
        rubric,
    )

    assert score["label"] == "good"


def test_score_response_downgrades_follow_up_policy_copy_paste_with_embedded_numbers():
    rubric = {
        "must_mention_any": ["report to supervisor"],
        "bad_actions": ["ignore", "guess", "leave it"],
    }

    score = score_response(
        "Document the equipment inspection before use on each shift 12 - Vehicles must have service & parking brakes, brake lights",
        "2 - Document the equipment inspection before use on each shift 12 - Vehicles must have service & parking brakes, brake lights",
        rubric,
    )

    assert score["label"] == "neutral"


def test_score_response_accepts_ground_guide_for_tight_quarters_policy():
    rubric = {
        "must_mention_any": ["report to supervisor"],
        "bad_actions": ["ignore", "guess", "leave it"],
    }

    score = score_response(
        "I would make sure I have a ground guide to assist me.",
        "When an equipment operator must negotiate in tight quarters, provide a second person to ensure safe movement.",
        rubric,
    )

    assert score["label"] == "good"


def test_score_response_accepts_parking_apart_for_separation_policy():
    rubric = {
        "must_mention_any": ["report to supervisor"],
        "bad_actions": ["ignore", "guess", "leave it"],
    }

    score = score_response(
        "I would park them in different spots and keep them separated.",
        "Separate two similar pieces of equipment; park each at a different spot on site and do not use them at the same time.",
        rubric,
    )

    assert score["label"] == "good"


def test_score_response_marks_refusing_cleanup_as_bad():
    score = score_response(
        "I will not clean it.",
        "Employees must clean spills immediately or block the area and report the hazard.",
        {},
    )

    assert score["label"] == "bad"


def test_score_response_marks_refusing_to_report_hazard_as_bad():
    score = score_response(
        "I would make the hazard worse and not tell anyone.",
        "Employees must clean spills immediately or block the area and report the hazard.",
        {},
    )

    assert score["label"] == "bad"


def test_score_response_marks_put_it_away_as_good_for_sharp_tool_policy():
    score = score_response(
        "I will put it away.",
        "Employees must not leave sharp tools unattended.",
        {},
    )

    assert score["label"] == "good"


def test_score_response_marks_pick_it_up_as_good_for_sharp_tool_policy():
    score = score_response(
        "I would pick it up.",
        "Employees must not leave sharp tools unattended.",
        {},
    )

    assert score["label"] == "good"


def test_score_response_marks_guessing_refund_decision_as_bad():
    score = score_response(
        "I will tell them they can for sure get a refund.",
        "Employees must never guess about refund policy. They should check the policy or ask a manager.",
        {},
    )

    assert score["label"] == "bad"


def test_score_response_marks_refund_without_checking_policy_as_bad():
    score = score_response(
        "I would just give them a refund without checking the policy.",
        "Employees must never guess about refund policy. They should check the policy or ask a manager.",
        {},
    )

    assert score["label"] == "bad"


def test_score_response_marks_yelling_at_customer_as_bad():
    score = score_response(
        "I yell at them, I refuse to listen to rude people.",
        "If a customer is upset, remain calm, listen respectfully, and contact a supervisor if needed.",
        {},
    )

    assert score["label"] == "bad"


def test_score_response_marks_not_telling_supervisor_as_bad():
    score = score_response(
        "I would not tell the supervisor and would handle it myself.",
        "Unsafe actions must be reported to a supervisor immediately.",
        {},
    )

    assert score["label"] == "bad"


def test_score_response_marks_leaving_sharp_tool_as_bad():
    score = score_response(
        "I would leave the sharp tool where it is.",
        "Employees must not leave sharp tools unattended.",
        {},
    )

    assert score["label"] == "bad"


def test_score_response_marks_refund_without_checking_anything_as_bad():
    score = score_response(
        "I would approve the refund without checking anything.",
        "Employees must never guess about refund policy. They should check the policy or ask a manager.",
        {},
    )

    assert score["label"] == "bad"


def test_score_response_marks_look_up_policy_as_good():
    score = score_response(
        "I would look up the policy.",
        "Employees must never guess about refund policy. They should check the policy or ask a manager.",
        {},
    )

    assert score["label"] == "good"


def test_score_response_marks_keep_yelling_as_bad():
    score = score_response(
        "I would keep yelling until they leave.",
        "If a customer is upset, remain calm, listen respectfully, and contact a supervisor if needed.",
        {},
    )

    assert score["label"] == "bad"
