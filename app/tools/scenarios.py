import re


NOISE_PATTERNS = [
    r"^\s*$",
    r"^\d+\s*$",
    r"^page\s+\d+",
    r"^\d+\.\d+\.\d+",
    r"^\d{1,2}/\d{1,2}/\d{2,4}",
    r"localhost:\d+",
    r"www\.",
    r"@\w+",
    r"^\s*table of contents\s*$",
]


FOLLOW_UP_TEMPLATES = {
    "sanitation": "What exact cleanup or sanitation step would you take first, and who would you notify if the issue could affect others?",
    "customer_service": "How would you help the customer while making sure you follow the correct procedure instead of guessing?",
    "safety": "What immediate action would reduce the safety risk, and when would you escalate it?",
    "reporting": "Who should be informed, and what details would you communicate so the issue is handled correctly?",
    "policy": "How would you verify the correct policy before acting, and what would you tell the customer or coworker in the meantime?",
    "equipment": "What would you do with the equipment right away to keep others safe?",
    "opening_shift": "How would you make the area ready for work before work begins?",
    "general": "What company procedure would you follow first, and why?",
}


ROLE_WORDS = {
    "customer",
    "customers",
    "guest",
    "guests",
    "employee",
    "employees",
    "coworker",
    "coworkers",
    "manager",
    "supervisor",
    "team",
    "member",
    "members",
}


ACTION_FILLERS = {
    "damaged",
    "document",
    "inspect",
    "issue",
    "marked",
    "report",
    "restart",
    "store",
    "must",
    "should",
    "never",
    "always",
    "immediately",
    "promptly",
    "carefully",
    "before",
    "after",
    "about",
    "their",
    "there",
    "while",
}


POLICY_SIGNAL_PATTERNS = [
    r"\bmust\b",
    r"\bshould\b",
    r"\bshall\b",
    r"\bdo not\b",
    r"\bdon't\b",
    r"\bnever\b",
    r"\breport\b",
    r"\bnotify\b",
    r"\bcontact\b",
    r"\bclean\b",
    r"\bsanitize\b",
    r"\bwear\b",
    r"\bcheck\b",
    r"\bfollow\b",
    r"\bcall\b",
    r"\bblock\b",
    r"\bask\b",
    r"\buse\b",
]


NARRATIVE_FRAGMENT_PATTERNS = [
    r"\bit is\b",
    r"\bin most cases\b",
    r"\bfirst department\b",
    r"\bwithin a store\b",
    r"\bwith americans\b",
    r"\beducated as to\b",
    r"\bin order to achieve\b",
]


SCENARIO_POSITIVE_PATTERNS = [
    r"\bunsafe condition",
    r"\bunsafe conditions",
    r"\bunsafe action",
    r"\bunsafe actions",
    r"\bspill",
    r"\bhazard",
    r"\binjury",
    r"\billness",
    r"\baccident",
    r"\bnear miss",
    r"\bequipment",
    r"\btool",
    r"\bmachine",
    r"\bladder",
    r"\bseat belt",
    r"\bvehicle",
    r"\bqualified",
    r"\btrained",
    r"\bsupervisor",
    r"\bwork area",
    r"\bclean up",
    r"\bhousekeeping",
]


SCENARIO_NEGATIVE_PATTERNS = [
    r"\bannual summary\b",
    r"\bposted no later than\b",
    r"\bfebruary\b",
    r"\byear following\b",
    r"\bsummary\b",
    r"\bposting\b",
    r"\bposter\b",
    r"\brecordkeeping\b",
    r"\btable of contents\b",
    r"\bpolicy statement\b",
    r"\btraining program\b",
    r"\bmanual\b",
    r"\bsection\b",
    r"\bchapter\b",
    r"\brescue team or service\b",
    r"\bservice must be standing\b",
]


SECTION_NEGATIVE_PATTERNS = [
    r"\btable of contents\b",
    r"\brecordkeeping\b",
    r"\binspection forms\b",
    r"\bchecklists\b",
    r"\bpolicy statement\b",
    r"\bintroduction\b",
    r"\bmessage from the president\b",
]


def is_noise_line(line: str) -> bool:
    l = line.strip()

    if len(l) < 25:
        return True

    if "........" in l:
        return True

    if re.search(r"\b1\.800\.", l):
        return True

    if re.search(r"p\.\s*o\.\s*bo", l.lower()):
        return True

    if sum(c.isdigit() for c in l) > 8:
        return True

    for pattern in NOISE_PATTERNS:
        if re.search(pattern, l.lower()):
            return True

    return False


def clean_handbook_lines(handbook_text: str):
    raw_lines = handbook_text.splitlines()
    cleaned = []

    for raw in raw_lines:
        line = " ".join(raw.strip().split())
        if not is_noise_line(line):
            cleaned.append(line)

    return cleaned


def split_into_candidate_lines(handbook_text: str):
    return merge_candidate_lines(clean_handbook_lines(handbook_text))


def is_heading_line(line: str) -> bool:
    stripped = line.strip()
    if len(stripped) < 4 or len(stripped) > 110:
        return False

    words = stripped.split()
    alpha_words = [word for word in words if re.search(r"[A-Za-z]", word)]
    if not alpha_words:
        return False

    upper_words = [
        word
        for word in alpha_words
        if sum(ch.isupper() for ch in word) >= max(1, sum(ch.isalpha() for ch in word) * 0.6)
    ]
    title_words = [word for word in alpha_words if word[:1].isupper()]

    if len(alpha_words) <= 12 and len(upper_words) >= max(2, len(alpha_words) // 2):
        return True

    if len(alpha_words) <= 8 and len(title_words) == len(alpha_words) and not stripped.endswith("."):
        return True

    return False


def build_section_blocks(handbook_text: str):
    lines = clean_handbook_lines(handbook_text)
    blocks = []
    current_heading = "General"
    current_lines = []

    for line in lines:
        if is_heading_line(line):
            if current_lines:
                blocks.append({"heading": current_heading, "lines": merge_candidate_lines(current_lines)})
                current_lines = []
            current_heading = line
            continue

        current_lines.append(line)

    if current_lines:
        blocks.append({"heading": current_heading, "lines": merge_candidate_lines(current_lines)})

    return blocks


def extract_candidate_statements(handbook_text: str):
    candidates = []

    for block in build_section_blocks(handbook_text):
        heading = block["heading"]
        heading_lower = heading.lower()
        if any(re.search(pattern, heading_lower) for pattern in SECTION_NEGATIVE_PATTERNS):
            continue

        for line in block["lines"]:
            candidates.append({"policy": line, "heading": heading})

    return candidates


def is_new_statement(line: str) -> bool:
    stripped = line.strip()
    lower = stripped.lower()

    if re.match(r"^[\u2022\-]\s*", stripped):
        return True
    if re.match(r"^\d+[\).\s-]", stripped):
        return True
    if re.match(r"^[a-z]\.\s+", lower):
        return True
    if any(re.match(pattern, lower) for pattern in POLICY_SIGNAL_PATTERNS):
        return True
    if lower.startswith(("if ", "when ", "only ", "all ", "every ", "employees ", "employee ")):
        return True

    return False


def should_merge_with_previous(previous: str, current: str) -> bool:
    prev = previous.strip()
    curr = current.strip()
    prev_lower = prev.lower()
    curr_lower = curr.lower()
    curr_starts_lower = bool(curr[:1]) and curr[:1].islower()

    if not prev or not curr:
        return False

    if len(prev) >= 260:
        return False

    if is_new_statement(curr):
        return False

    if re.search(r"[.:!?]$", prev) and len(prev.split()) >= 8:
        return False

    if re.search(r"\b(to|for|of|and|or|the|a|an|if|when|with|your|their)\s*$", prev_lower):
        if curr_starts_lower or curr_lower.startswith(("assigned ", "additional ", "the employee ", "their ", "your ")):
            return True
        return False

    if curr_lower.startswith(
        (
            "their ",
            "your ",
            "the ",
            "a ",
            "an ",
            "to ",
            "for ",
            "if ",
            "when ",
            "while ",
            "only ",
            "all ",
            "any ",
            "this ",
            "that ",
            "those ",
            "these ",
            "who ",
        )
    ):
        return curr_starts_lower

    if len(prev.split()) < 8:
        return curr_starts_lower

    return False


def merge_candidate_lines(lines):
    merged = []

    for line in lines:
        if merged and should_merge_with_previous(merged[-1], line):
            merged[-1] = f"{merged[-1].rstrip()} {line.lstrip()}"
        else:
            merged.append(line)

    return merged


def classify_policy(text: str) -> str:
    l = text.lower()

    if any(word in l for word in ["wash", "sanitize", "clean", "hygiene", "gloves"]):
        return "sanitation"
    if any(word in l for word in ["customer", "guest"]) or (
        "help" in l and any(word in l for word in ["customer", "guest", "public", "client"])
    ):
        return "customer_service"
    if any(word in l for word in ["spill", "hazard", "safe", "safety", "injury", "emergenc"]):
        return "safety"
    if any(word in l for word in ["refund", "policy", "return", "procedure"]):
        return "policy"
    if any(word in l for word in ["equipment", "knife", "box cutter", "tool", "ladder", "machine", "slicer"]):
        return "equipment"
    if any(word in l for word in ["manager", "supervisor", "report", "notify", "document", "escalat"]):
        return "reporting"
    if any(word in l for word in ["clock in", "uniform", "late", "ready for work", "opening", "before work", "start of shift"]):
        return "opening_shift"

    return "general"


def looks_like_policy_line(line: str) -> bool:
    normalized = normalize_policy_text(line)
    lower = normalized.lower()

    if len(normalized) < 35 or len(normalized) > 220:
        return False

    if any(re.search(pattern, lower) for pattern in NARRATIVE_FRAGMENT_PATTERNS):
        return False

    if re.search(r"\b(fi\s+rst|depart\s+ment)\b", lower):
        return False

    if re.search(r"\b(and|or|to|a|an|the)\s*$", lower):
        return False

    if ":" in normalized and len(normalized.split(":")[-1].strip().split()) < 4:
        return False

    signal_count = sum(1 for pattern in POLICY_SIGNAL_PATTERNS if re.search(pattern, lower))
    if signal_count == 0:
        return False

    words = re.findall(r"[a-z][a-z\-']+", lower)
    if len(words) < 6:
        return False

    long_words = [word for word in words if len(word) >= 4]
    if len(long_words) < 3:
        return False

    action_match = re.search(
        r"\b(?:must|should|shall|do not|don't|never|report|notify|contact|clean|sanitize|wear|check|follow|call|block|ask|use)\b\s+([a-z][a-z\-']+)",
        lower,
    )
    if not action_match:
        return False

    title_case_ratio = sum(1 for word in normalized.split() if word[:1].isupper()) / max(len(normalized.split()), 1)
    if title_case_ratio > 0.6 and signal_count < 2:
        return False

    if any(phrase in lower for phrase in ["name badge visible", "clean apron indicates"]):
        return False

    return True


def scenario_worthiness_score(line: str, category: str, heading: str = "") -> int:
    lower = normalize_policy_text(line).lower()
    heading_lower = heading.lower()
    score = 0

    score += sum(2 for pattern in SCENARIO_POSITIVE_PATTERNS if re.search(pattern, lower))
    score -= sum(3 for pattern in SCENARIO_NEGATIVE_PATTERNS if re.search(pattern, lower))
    score += sum(2 for pattern in SCENARIO_POSITIVE_PATTERNS if re.search(pattern, heading_lower))
    score -= sum(4 for pattern in SECTION_NEGATIVE_PATTERNS if re.search(pattern, heading_lower))

    if category in {"safety", "reporting", "equipment", "sanitation", "policy"}:
        score += 2
    if category == "general":
        score -= 1
    if category == "opening_shift":
        score -= 2

    if any(word in lower for word in ["report", "notify", "stop", "leave", "block", "wear", "clean", "ask"]):
        score += 1

    if any(word in lower for word in ["annual", "summary", "post", "poster", "record", "calendar", "february"]):
        score -= 4

    if any(phrase in lower for phrase in ["rescue team or service", "trained rescue team"]):
        score -= 5

    return score


def extract_policies(handbook_text: str):
    candidates = extract_candidate_statements(handbook_text)

    scored = []
    for candidate in candidates:
        line = candidate["policy"]
        heading = candidate["heading"]
        context_text = f"{heading} {line}"

        if not looks_like_policy_line(line):
            continue

        category = classify_policy(context_text)
        scenario_score = scenario_worthiness_score(line, category, heading=heading)
        if scenario_score < 1:
            continue

        score = 0
        lower = line.lower()

        if any(
            w in lower
            for w in [
                "must",
                "should",
                "never",
                "always",
                "report",
                "clean",
                "sanitize",
                "wear",
                "follow",
                "do not",
                "notify",
            ]
        ):
            score += 2

        if category != "general":
            score += 2

        if 45 <= len(line) <= 180:
            score += 1

        score += scenario_score

        scored.append((score, line, category, heading))

    scored.sort(key=lambda x: x[0], reverse=True)

    chosen = []
    seen = set()

    for score, line, category, heading in scored:
        key = (category, line.lower())
        if key not in seen:
            chosen.append({"policy": line, "category": category, "heading": heading})
            seen.add(key)

    return chosen


def normalize_policy_text(policy: str) -> str:
    cleaned = re.sub(r"^\s*\d+[\).\s-]*", "", policy.strip())
    return cleaned.rstrip(".")


def sentence_case(text: str) -> str:
    text = text.strip()
    if not text:
        return text
    return text[0].upper() + text[1:]


def extract_policy_action(policy: str) -> str:
    text = normalize_policy_text(policy)
    lower = text.lower()

    patterns = [
        r"\bif\b.+?,\s*(.+)",
        r"\bwhen\b.+?,\s*(.+)",
        r"\b(?:must|should|shall|need to|are required to|is required to|have to)\s+(.+)",
        r"\b(?:must not|should not|may not|never|do not|don't)\s+(.+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, lower)
        if match:
            action = match.group(1).strip(" .")
            if action:
                return action

    return lower


def clean_action_text(action: str) -> str:
    cleaned = action.strip(" .")
    cleaned = re.sub(r"^(employees?|team members?|staff)\s+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(if needed|when needed)\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bmust be\b", "be", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ,.")
    return cleaned


def extract_focus_terms(policy: str, limit: int = 3):
    text = normalize_policy_text(policy).lower()
    words = re.findall(r"[a-z][a-z\-']+", text)

    stop_words = {
        "about",
        "after",
        "and",
        "area",
        "before",
        "correct",
        "follow",
        "from",
        "have",
        "immediately",
        "needed",
        "other",
        "policy",
        "procedures",
        "procedure",
        "should",
        "store",
        "their",
        "then",
        "they",
        "when",
        "with",
        "work",
        "workers",
        "would",
    }

    focus_terms = []
    for word in words:
        if len(word) < 4:
            continue
        if word in stop_words or word in ROLE_WORDS or word in ACTION_FILLERS:
            continue
        if word not in focus_terms:
            focus_terms.append(word)
        if len(focus_terms) >= limit:
            break

    return focus_terms


def join_terms(terms):
    if not terms:
        return "the situation"
    if len(terms) == 1:
        return terms[0]
    return f"{terms[0]} and {terms[1]}"


def extract_trigger_text(policy: str) -> str:
    normalized = normalize_policy_text(policy)
    lower = normalized.lower()

    direct_policy_patterns = [
        (r"unsafe actions? must be reported", "you notice someone taking an unsafe action in the work area"),
        (r"customer safety over speed", "a customer needs help, but moving too fast could create a safety or service problem"),
    ]

    for pattern, trigger in direct_policy_patterns:
        if re.search(pattern, lower):
            return trigger

    for pattern in [r"\bif\s+(.+?),\s*", r"\bwhen\s+(.+?),\s*"]:
        match = re.search(pattern, lower)
        if match:
            return match.group(1).strip(" .")

    action = extract_policy_action(policy)

    trigger_patterns = [
        (r"clean spills?", "you notice a spill on the floor"),
        (r"block the area", "an area becomes unsafe for others"),
        (r"sharp tools? unattended", "you find a sharp tool left out in the work area"),
        (r"refund policy", "someone asks you to make a refund decision you are not sure about"),
        (r"contact a supervisor", "a customer problem starts to escalate"),
        (r"report(?:ed)? to a supervisor", "you notice an issue that needs to be escalated"),
        (r"follow .*emergency procedures", "an emergency situation starts to unfold"),
        (r"wear .*gloves", "you are about to handle a task that requires protective equipment"),
        (r"sanitize|clean", "you notice a cleanliness issue in your area"),
    ]

    for pattern, trigger in trigger_patterns:
        if re.search(pattern, action):
            return trigger

    focus_terms = extract_focus_terms(policy)
    focus = join_terms(focus_terms[:2])
    return f"you run into a situation involving {focus}"


def extract_escalation_text(policy: str) -> str | None:
    lower = normalize_policy_text(policy).lower()

    patterns = [
        r"\b(report(?:ed)? to [^.]+)",
        r"\b(report [^.]+)",
        r"\b(notify [^.]+)",
        r"\b(contact [^.]+)",
        r"\b(ask [^.]+)",
        r"\b(call for help)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, lower)
        if match:
            escalation = clean_action_text(match.group(1))
            escalation = re.sub(r"\breported to\b", "report it to", escalation, flags=re.IGNORECASE)
            escalation = re.sub(r"\breport to\b", "report it to", escalation, flags=re.IGNORECASE)
            escalation = re.sub(r"\bimmediately\b", "", escalation, flags=re.IGNORECASE)
            escalation = re.sub(r"\s+", " ", escalation).strip(" ,.")
            return escalation

    return None


def build_structured_rule(policy: str, category: str) -> dict:
    normalized_policy = normalize_policy_text(policy)
    action = clean_action_text(extract_policy_action(policy))
    focus_terms = extract_focus_terms(policy)
    trigger = extract_trigger_text(policy)
    escalation = extract_escalation_text(policy)

    return {
        "policy": normalized_policy,
        "category": category,
        "action": action,
        "focus_terms": focus_terms,
        "trigger": trigger,
        "escalation": escalation,
    }


def build_policy_specific_prompt(policy: str, category: str) -> str:
    rule = build_structured_rule(policy, category)
    trigger = sentence_case(rule["trigger"])
    action = rule["action"]
    escalation = rule["escalation"]
    focus = join_terms(rule["focus_terms"][:2])

    if category == "customer_service":
        return (
            f"{trigger}. The customer expects help right away. "
            f"What should you do first to handle the situation correctly, and how would you respond without guessing?"
        )

    if category == "sanitation":
        return (
            f"{trigger}. What action should you take right away to fix the issue and keep the area safe for others?"
        )

    if category == "safety":
        question = f"{trigger}. What immediate action should you take?"
        if escalation:
            question += f" When would you {escalation}?"
        else:
            question += " Who else needs to know?"
        return question

    if category == "reporting":
        details = "what details would you communicate"
        if escalation:
            return f"{trigger}. What should you do first, and how would you {escalation}?"
        return (
            f"{trigger}. What should you do first, and {details}?"
        )

    if category == "policy":
        return (
            f"{trigger}. You are not fully sure what the rule allows. "
            "What should you do next before making a decision?"
        )

    if category == "equipment":
        return (
            f"{trigger}. What should you do right away, and how do you keep others safe?"
        )

    if category == "opening_shift":
        return (
            f"{trigger} while getting ready to start work. "
            "What needs to be taken care of before you continue with the shift?"
        )

    return (
        f"{trigger}. Based on company procedure, what should you do first?"
    )


def build_initial_scenarios(policies):
    preferred_categories = [
        "opening_shift",
        "customer_service",
        "safety",
        "reporting",
        "policy",
        "equipment",
        "sanitation",
        "general",
    ]

    scenarios = []
    used_categories = set()
    next_id = 1

    for category in preferred_categories:
        for item in policies:
            if item["category"] == category and category not in used_categories:
                scenarios.append(
                    {
                        "id": next_id,
                        "kind": "scenario",
                        "category": item["category"],
                        "policy": item["policy"],
                        "prompt": build_policy_specific_prompt(item["policy"], item["category"]),
                    }
                )
                used_categories.add(category)
                next_id += 1
                break

        if len(scenarios) >= 3:
            break

    if not scenarios:
        fallback_policy = "Follow company procedures and prioritize safety."
        scenarios.append(
            {
                "id": 1,
                "kind": "scenario",
                "category": "general",
                "policy": fallback_policy,
                "prompt": build_policy_specific_prompt(fallback_policy, "general"),
            }
        )

    return scenarios


def build_follow_up_scenario(previous_scenario, next_id):
    category = previous_scenario["category"]
    follow_up_prompt = FOLLOW_UP_TEMPLATES.get(category, FOLLOW_UP_TEMPLATES["general"])
    normalized_policy = normalize_policy_text(previous_scenario["policy"])

    return {
        "id": next_id,
        "kind": "follow_up",
        "category": category,
        "policy": previous_scenario["policy"],
        "prompt": (
            "Follow-up: Your earlier answer needs more policy-specific detail. "
            f'The handbook guidance here is: "{normalized_policy}". '
            + follow_up_prompt
        ),
    }
