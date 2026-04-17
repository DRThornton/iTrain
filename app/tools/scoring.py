import json
import re
from pathlib import Path


def load_rubric(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


UNSAFE_RESPONSE_PATTERNS = [
    (r"\bhide\b", "hide instead of reporting the issue"),
    (r"\bcover it with (?:some )?dirt\b", "cover the hazard instead of correcting it"),
    (r"\bkeep working\b", "keep working without correcting the hazard"),
    (r"\b(?:can't|cannot) hurt (?:us|me|them)\b", "dismiss the hazard as harmless"),
    (r"\b(?:do not|don't) need to tell\b", "refuse to report the issue"),
    (r"\bwhat they don't know can't hurt them\b", "intentionally avoid reporting the issue"),
    (r"\b(?:do not|don't) need (?:gloves|ppe|protective equipment)\b", "refuse required protective equipment"),
    (r"\bgloves are for girls\b", "refuse required protective equipment"),
    (r"\bunless\b.+\btoo uncomfortable\b", "skip required protective equipment when it feels uncomfortable"),
    (r"\bjust avoid the hazard\b", "avoid the hazard without fixing or reporting it"),
]


def detect_policy_good_matches(response_lower: str, policy_lower: str):
    matches = []

    policy_synonyms = [
        (
            ["protective equipment", "body protection", "limb protection", "ppe"],
            ["ppe", "protective equipment", "proper gear", "correct gear", "safety gear", "gloves"],
            "protective equipment",
        ),
        (
            ["gloves"],
            ["gloves"],
            "gloves",
        ),
        (
            ["report", "notify"],
            ["report", "notify", "tell my supervisor", "tell the supervisor", "escalate"],
            "report",
        ),
        (
            ["near miss", "near misses"],
            ["near miss", "near misses"],
            "near miss",
        ),
        (
            ["clean up", "dispose", "spill", "trash"],
            ["clean", "clean up", "dispose", "block off", "block the area"],
            "cleanup step",
        ),
    ]

    for policy_terms, response_terms, label in policy_synonyms:
        if any(term in policy_lower for term in policy_terms) and any(term in response_lower for term in response_terms):
            matches.append(label)

    return matches


def detect_unsafe_matches(response_lower: str):
    matches = []
    for pattern, label in UNSAFE_RESPONSE_PATTERNS:
        if re.search(pattern, response_lower):
            matches.append(label)
    return matches


def phrase_is_negated(response_lower: str, phrase: str) -> bool:
    escaped = re.escape(phrase.lower())
    negation_patterns = [
        rf"\bnever\s+{escaped}\b",
        rf"\bdo not\s+{escaped}\b",
        rf"\bdon't\s+{escaped}\b",
        rf"\bshould not\s+{escaped}\b",
        rf"\bmust not\s+{escaped}\b",
        rf"\bwithout\s+{escaped}(?:ing)?\b",
    ]
    return any(re.search(pattern, response_lower) for pattern in negation_patterns)


def detect_rubric_bad_matches(response_lower: str, rubric: dict):
    matches = []
    for phrase in rubric.get("bad_actions", []):
        lower_phrase = phrase.lower()
        if lower_phrase in response_lower and not phrase_is_negated(response_lower, lower_phrase):
            matches.append(phrase)
    return matches


def tokenize_significant_words(text: str):
    return [word for word in re.findall(r"[a-z][a-z\-']+", text.lower()) if len(word) > 3]


def normalize_for_comparison(text: str):
    normalized = text.lower()
    normalized = re.sub(r"^\s*[\u2022\-]?\s*\d+[\).\s-]*", "", normalized)
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return " ".join(normalized.split())


def is_policy_parroting(response: str, policy: str) -> bool:
    response_lower = response.lower().strip()
    policy_lower = policy.lower().strip()

    if not response_lower:
        return False

    normalized_response = normalize_for_comparison(response)
    normalized_policy = normalize_for_comparison(policy)
    if normalized_response and normalized_policy and normalized_response in normalized_policy:
        if not re.search(r"\b(i|i'd|i'll|i would|i will|my|we|we'd|we will|let's)\b", response_lower):
            return True

    trimmed_response = response_lower.strip(" .,!?:;\"'")
    trimmed_policy = policy_lower.strip(" .,!?:;\"'")
    if trimmed_response and trimmed_response in trimmed_policy:
        if not re.search(r"\b(i|i'd|i'll|i would|i will|my|we|we'd|we will|let's)\b", trimmed_response):
            return True

    response_words = tokenize_significant_words(response_lower)
    policy_words = tokenize_significant_words(policy_lower)
    if not response_words or not policy_words:
        return False

    response_set = set(response_words)
    policy_set = set(policy_words)
    overlap_ratio = len(response_set & policy_set) / max(len(response_set), 1)
    has_application_language = bool(
        re.search(r"\b(i|i'd|i'll|i would|i will|my|we|we'd|we will|let's)\b", response_lower)
    )
    return overlap_ratio >= 0.75 and not has_application_language


def score_response(response: str, policy: str, rubric: dict):
    response_lower = response.lower()
    policy_lower = policy.lower()

    matched_good = []
    matched_bad = []

    for phrase in rubric.get("must_mention_any", []):
        if phrase.lower() in response_lower:
            matched_good.append(phrase)

    matched_bad.extend(detect_rubric_bad_matches(response_lower, rubric))

    matched_good.extend(
        phrase for phrase in detect_policy_good_matches(response_lower, policy_lower) if phrase not in matched_good
    )
    matched_bad.extend(
        phrase for phrase in detect_unsafe_matches(response_lower) if phrase not in matched_bad
    )

    confusion_patterns = [
        r"\bi guess\b",
        r"\bi am confused\b",
        r"\bi'm confused\b",
        r"\bunclear\b",
        r"\bneed more clarification\b",
        r"\bnot sure what (?:the )?scenario is\b",
    ]
    expresses_confusion = any(re.search(pattern, response_lower) for pattern in confusion_patterns)

    if expresses_confusion:
        matched_bad = [phrase for phrase in matched_bad if phrase.lower() != "guess"]

    policy_words = [w.strip(".,") for w in policy_lower.split() if len(w) > 4]
    overlap = []
    for word in policy_words:
        if word in response_lower and word not in overlap:
            overlap.append(word)

    parroting_policy = is_policy_parroting(response, policy)

    if not response.strip():
        label = "bad"
        rationale = "No response was provided, so readiness could not be demonstrated."
    elif matched_bad:
        label = "bad"
        rationale = f"The answer includes potentially unsafe or incorrect action(s): {', '.join(matched_bad)}."
    elif parroting_policy:
        label = "neutral"
        rationale = "The answer mostly repeats the handbook wording, but it does not clearly show how the learner would apply the policy."
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
        "citation": policy,
    }
