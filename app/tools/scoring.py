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
    (r"\bquit on the spot\b", "abandon the task instead of following the procedure"),
    (r"\bleave all mess(?:es)? uncleaned\b", "leave the work area in a worse condition"),
    (r"\bignore the manual\b", "ignore the documented procedure"),
    (r"\bget rid of the equipment\b", "discard equipment without following the procedure"),
    (r"\bthrow (?:it|the equipment) away\b", "discard equipment without following the procedure"),
    (r"\bbreak it\b", "damage equipment instead of following the procedure"),
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
            ["report", "notify", "tell my supervisor", "tell the supervisor", "tell my foreman", "tell the foreman", "escalate"],
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
        (
            ["separate two similar pieces of equipment", "park each at a different spot", "do not use them at the same time"],
            ["different spots", "park them in different spots", "separate them", "park them apart", "do not use them at the same time"],
            "separate equipment",
        ),
        (
            ["tight quarters", "provide a second person"],
            ["second person", "spotter", "ground guide", "guide me", "guide me through", "another person"],
            "second-person guide",
        ),
        (
            ["4 wires", "5 wires"],
            ["follow the manual", "follow the directions", "check the manual", "verify the wiring", "use the correct wiring"],
            "manual wiring step",
        ),
        (
            ["soft, damp cloth", "clean the screen", "touch screen"],
            ["soft cloth", "damp cloth", "clean the screen", "touch screen"],
            "screen cleaning step",
        ),
        (
            ["who to call for service", "service"],
            ["service contact", "who to call", "contact service", "call for service"],
            "service contact step",
        ),
        (
            ["turn off the power", "power is off", "main fuse panel", "breaker"],
            ["turn off the power", "shut the power off", "power off", "switch off the breaker", "turn off the breaker"],
            "power-off step",
        ),
        (
            ["assemble tools", "screwdriver", "wire cutters", "wire strippers"],
            ["assemble tools", "gather tools", "get the tools", "screwdriver", "wire cutters", "wire strippers"],
            "tool-prep step",
        ),
        (
            ["label and disconnect wires", "mark them with the letter of the terminal"],
            ["label the wires", "mark the wires", "disconnect the wires", "tape the ends", "keep track of the terminal", "reconnect them properly", "reconnect properly", "reconnect them later"],
            "wire-labeling step",
        ),
        (
            ["terminal designations", "refer to the chart", "wiring diagrams"],
            ["check the terminal labels", "refer to the chart", "check the wiring diagram", "match the terminals"],
            "terminal-check step",
        ),
        (
            ["terminal marked g", "g wire"],
            ["remove the g wire", "disconnect the g wire", "take the g wire off", "place the g wire on terminal c", "terminal c"],
            "g-wire step",
        ),
        (
            ["loosen the screws", "subbase to the wall", "lift away"],
            ["loosen the screws", "remove the thermostat from the wall", "lift it away", "take it off the wall"],
            "thermostat-removal step",
        ),
        (
            ["select the access point", "connect to from the list"],
            ["select the access point", "choose the access point", "pick the network", "select the wifi", "choose the wifi"],
            "wifi-selection step",
        ),
        (
            ["plus key", "next parameter"],
            ["plus key", "use the plus key", "move to the next parameter", "next parameter"],
            "plus-key step",
        ),
        (
            ["enter key", "display the value"],
            ["press the enter key", "enter key", "display the value", "show the value"],
            "enter-key step",
        ),
        (
            ["modify key", "value will flash", "field will flash"],
            ["press the modify key", "modify key", "value will flash", "field will flash"],
            "modify-key step",
        ),
        (
            ["keypad unlock led", "keypad is now live"],
            ["keypad led will turn on", "unlock led will turn on", "keypad is now live", "led will turn on"],
            "keypad-led step",
        ),
        (
            ["defrost symbol", "defrost is in effect"],
            ["defrost symbol will illuminate", "defrost symbol lights up", "defrost is in effect", "defrost symbol will light up", "defrost light will light up", "defrost light will illuminate"],
            "defrost-indicator step",
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


def detect_manual_bad_matches(response_lower: str, policy_lower: str):
    matches = []

    contradiction_patterns = [
        (
            ["soft cloth", "damp cloth", "clean the screen"],
            [r"\babrasive cleaners?\b", r"\bsolvents?\b", r"\brough cloth\b"],
            "use cleaning materials the manual says to avoid",
        ),
        (
            ["turn off the power", "power is off", "main fuse panel", "breaker"],
            [r"\bleave the power on\b", r"\bkeep the power on\b"],
            "skip the required power-off step",
        ),
        (
            ["label and disconnect wires", "mark them with the letter of the terminal"],
            [r"\bdon't label\b", r"\bskip labeling\b"],
            "skip wire labeling the manual requires",
        ),
    ]

    for policy_terms, bad_patterns, label in contradiction_patterns:
        if any(term in policy_lower for term in policy_terms) and any(re.search(pattern, response_lower) for pattern in bad_patterns):
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


def has_procedural_application_language(response_lower: str) -> bool:
    return bool(
        re.search(
            r"\b(i|i'd|i would|i will|we|we'd|we would|we will)\b", response_lower
        )
        or re.search(
            r"^(?:clean|use|place|put|remove|disconnect|loosen|lift|select|choose|press|enter|connect|gather|assemble|check|illuminate|flash|turn)\b",
            response_lower.strip(),
        )
        or re.search(
            r"\b(?:clean|use|place|put|remove|disconnect|loosen|lift|select|choose|press|enter|connect|gather|assemble|check|illuminate|flash|turn on|lights up)\b",
            response_lower,
        )
    )


def is_short_procedural_answer(response_lower: str) -> bool:
    words = re.findall(r"[a-z][a-z\-']+", response_lower)
    if not words:
        return False
    return len(words) <= 12 and has_procedural_application_language(response_lower)


def score_response(response: str, policy: str, rubric: dict):
    response_lower = response.lower()
    policy_lower = policy.lower()

    matched_good = []
    matched_bad = []

    for phrase in rubric.get("must_mention_any", []):
        if phrase.lower() in response_lower:
            matched_good.append(phrase)

    matched_bad.extend(detect_rubric_bad_matches(response_lower, rubric))
    matched_bad.extend(
        phrase for phrase in detect_manual_bad_matches(response_lower, policy_lower) if phrase not in matched_bad
    )

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
    procedural_application = has_procedural_application_language(response_lower)

    if not response.strip():
        label = "bad"
        rationale = "No response was provided, so readiness could not be demonstrated."
    elif matched_bad:
        label = "bad"
        rationale = f"The answer includes potentially unsafe or incorrect action(s): {', '.join(matched_bad)}."
    elif parroting_policy and not (matched_good and (procedural_application or is_short_procedural_answer(response_lower))):
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
