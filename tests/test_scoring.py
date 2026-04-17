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
