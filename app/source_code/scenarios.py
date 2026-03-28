import random
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

        if any(w in lower for w in [
            "must", "should", "never", "always", "report", "clean",
            "sanitize", "wear", "follow", "do not", "notify"
        ]):
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
            chosen.append({
                "policy": line,
                "category": category
            })
            seen.add(key)

    return chosen


def choose_policy_by_category(policies, preferred_categories):
    for category in preferred_categories:
        for item in policies:
            if item["category"] == category:
                return item

    return policies[0] if policies else {
        "policy": "Follow company procedures and act safely.",
        "category": "general"
    }


def build_workday_scenarios(policies):
    opening = choose_policy_by_category(
        policies,
        ["opening_shift", "sanitation", "safety", "general"]
    )
    customer = choose_policy_by_category(
        policies,
        ["customer_service", "policy", "reporting", "general"]
    )
    escalation = choose_policy_by_category(
        policies,
        ["safety", "equipment", "reporting", "sanitation", "general"]
    )

    scenarios = [
        {
            "id": 1,
            "policy": opening["policy"],
            "category": opening["category"],
            "prompt": (
                "You are starting your shift for the day. While getting ready for work, "
                "you notice that your area is not fully prepared and there may be a cleanliness "
                "or readiness issue before customers arrive. What do you do first, and why?"
            )
        },
        {
            "id": 2,
            "policy": customer["policy"],
            "category": customer["category"],
            "prompt": (
                "Later in the shift, a customer approaches you with a problem and wants help right away. "
                "You feel pressure to respond quickly, but you are not completely sure what the correct "
                "store procedure is. How do you handle the situation?"
            )
        },
        {
            "id": 3,
            "policy": escalation["policy"],
            "category": escalation["category"],
            "prompt": (
                "Near the end of the workday, you notice a situation that could become unsafe or should be "
                "reported before it gets worse. Other employees are busy, and it would be easy to ignore it. "
                "What do you do next, and why?"
            )
        }
    ]

    return scenarios


def generate_scenarios(handbook_text: str, num_scenarios: int = 3):
    policies = extract_policies(handbook_text)

    if not policies:
        policies = [{
            "policy": "Follow company procedures and prioritize safety.",
            "category": "general"
        }]

    scenarios = build_workday_scenarios(policies)
    return scenarios[:num_scenarios]