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
