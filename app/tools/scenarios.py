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
    "opening_shift": "How would you make the area ready for work before customers arrive?",
    "general": "What company procedure would you follow first, and why?",
}


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


def split_into_candidate_lines(handbook_text: str):
    raw_lines = handbook_text.splitlines()
    cleaned = []

    for raw in raw_lines:
        line = " ".join(raw.strip().split())
        if not is_noise_line(line):
            cleaned.append(line)

    return cleaned


def classify_policy(line: str) -> str:
    l = line.lower()

    if any(word in l for word in ["wash", "sanitize", "clean", "hygiene", "gloves"]):
        return "sanitation"
    if any(word in l for word in ["customer", "guest", "service", "help"]):
        return "customer_service"
    if any(word in l for word in ["spill", "hazard", "safe", "safety", "injury"]):
        return "safety"
    if any(word in l for word in ["manager", "supervisor", "report", "notify"]):
        return "reporting"
    if any(word in l for word in ["refund", "policy", "return"]):
        return "policy"
    if any(word in l for word in ["equipment", "knife", "box cutter", "tool"]):
        return "equipment"
    if any(word in l for word in ["clock in", "uniform", "late", "ready for work", "shift"]):
        return "opening_shift"

    return "general"


def extract_policies(handbook_text: str):
    candidates = split_into_candidate_lines(handbook_text)

    scored = []
    for line in candidates:
        category = classify_policy(line)

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

        if 35 <= len(line) <= 180:
            score += 1

        scored.append((score, line, category))

    scored.sort(key=lambda x: x[0], reverse=True)

    chosen = []
    seen = set()

    for score, line, category in scored:
        key = (category, line.lower())
        if key not in seen:
            chosen.append({"policy": line, "category": category})
            seen.add(key)

    return chosen


def build_initial_scenarios(policies):
    prompts = {
        "opening_shift": (
            "You are starting your shift for the day. While getting ready for work, "
            "you notice that your area is not fully prepared and there may be a cleanliness "
            "or readiness issue before customers arrive. What do you do first, and why?"
        ),
        "customer_service": (
            "A customer approaches you with a problem and wants help right away. "
            "You feel pressure to respond quickly, but you are not completely sure what the correct "
            "store procedure is. How do you handle the situation?"
        ),
        "safety": (
            "Near the end of the workday, you notice a situation that could become unsafe if nobody acts. "
            "What do you do next, and why?"
        ),
        "reporting": (
            "You notice an issue that should be documented or escalated before it gets worse. "
            "Other employees are busy. What do you do?"
        ),
        "general": (
            "You encounter a work situation where following company procedure matters more than moving fast. "
            "How do you respond?"
        ),
    }

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
                        "prompt": prompts.get(category, prompts["general"]),
                    }
                )
                used_categories.add(category)
                next_id += 1
                break

        if len(scenarios) >= 3:
            break

    if not scenarios:
        scenarios.append(
            {
                "id": 1,
                "kind": "scenario",
                "category": "general",
                "policy": "Follow company procedures and prioritize safety.",
                "prompt": prompts["general"],
            }
        )

    return scenarios


def build_follow_up_scenario(previous_scenario, next_id):
    category = previous_scenario["category"]
    follow_up_prompt = FOLLOW_UP_TEMPLATES.get(category, FOLLOW_UP_TEMPLATES["general"])

    return {
        "id": next_id,
        "kind": "follow_up",
        "category": category,
        "policy": previous_scenario["policy"],
        "prompt": (
            "Follow-up: Your earlier answer needs more policy-specific detail. "
            + follow_up_prompt
        ),
    }
