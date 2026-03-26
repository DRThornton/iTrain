import json
from pathlib import Path


def load_rubric(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def score_response(response: str, policy: str, rubric: dict):
    response_lower = response.lower()
    policy_lower = policy.lower()

    matched_good = []
    matched_bad = []

    for phrase in rubric.get("must_mention_any", []):
        if phrase.lower() in response_lower:
            matched_good.append(phrase)

    for phrase in rubric.get("bad_actions", []):
        if phrase.lower() in response_lower:
            matched_bad.append(phrase)

    policy_words = [w for w in policy_lower.split() if len(w) > 4]
    overlap = [w for w in policy_words if w in response_lower]

    if matched_bad:
        label = "bad"
        rationale = f"The answer includes potentially unsafe or incorrect action(s): {', '.join(matched_bad)}."
    elif matched_good or len(overlap) >= 2:
        label = "good"
        evidence = matched_good if matched_good else overlap[:3]
        rationale = f"The answer aligns with the policy and includes relevant actions/concepts: {', '.join(evidence)}."
    else:
        label = "neutral"
        rationale = "The answer is not clearly unsafe, but it does not strongly show the expected policy-based action."

    return {
        "label": label,
        "rationale": rationale,
        "citation": policy
    }