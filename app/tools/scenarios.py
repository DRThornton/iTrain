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


ADMIN_FRAGMENT_PATTERNS = [
    r"\breturn to work\b",
    r"\bworkers?\s+comp(?:ensation)?\b",
    r"\bmodified duty\b",
    r"\blost time\b",
    r"\bapplicable workers\b",
    r"\buser will need to\b",
    r"\busers?[’'] guide\b",
    r"\buse this report\b",
    r"\bthis form will always be filled out\b",
    r"\bnear miss form\b",
    r"\bincident investigation form\b",
    r"\bshall be given to\b",
    r"\bshall initiate hse-\b",
    r"\bhse-\d",
    r"\bstep\s+\d+\b",
    r"\bthe following\b\s*$",
    r"\breveal evidence of what\b",
    r"\brequirements must be outlined in detail\b",
    r"\bsite safety manager should utilize\b",
    r"\bregarding medications?\b",
    r"\bchest x-ray\b",
    r"\bpulmonary function testing\b",
    r"\belectrocardiogram\b",
    r"\bpre-employment screening\b",
    r"\bmedical care\b",
    r"\bmedical personnel\b",
    r"\bnon-emergency medical\b",
    r"\blockers? or closets?\b",
    r"\btelephone numbers\b",
    r"\bevacuation route maps\b",
    r"\bdirect-reading instruments?\b",
    r"\bselection of respiratory equipment\b",
    r"\bnote limitations concerning the worker's ability to use protective equipment\b",
    r"\ba reading of zero should be reported as\b",
    r"\bhalf masks cover the face\b",
    r"\bdo not provide eye\b",
    r"\bbuckets, brushes, clothing, tools, and other contaminated equipment should be collected\b",
    r"\bwork\s+or\s+work[-\s]related activity\b",
    r"\bmust be considered work-related\b",
    r"\bin addition to the required module\b",
    r"\brequired module\b",
    r"\bsite safety plan\b",
    r"\bair-purifying respirators\b",
    r"\bon the other hand\b",
    r"\bresponse to spills, leaks, and release of hazardous materials must be set\b",
    r"\boverhead power lines\b.*\belectrical equipment used\b",
    r"\bguards must be fully apprised\b",
    r"\brequires the use of safety signs/tags to warn employees of electrical hazards\b",
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


SECTION_POSITIVE_PATTERNS = [
    r"\bhousekeeping\b",
    r"\breporting\b",
    r"\bincident\b",
    r"\binjury\b",
    r"\bheat illness\b",
    r"\bspill\b",
    r"\bvehicle\b",
    r"\bequipment\b",
    r"\bladder\b",
    r"\btools?\b",
    r"\bfall protection\b",
    r"\belectrical\b",
    r"\bemergency\b",
    r"\bprotective equipment\b",
    r"\bppe\b",
    r"\bhazard\b",
]


def is_noise_line(line: str) -> bool:
    l = line.strip()
    lower = l.lower()

    if len(l) < 25:
        if is_heading_line(l):
            return False
        if any(re.search(pattern, lower) for pattern in POLICY_SIGNAL_PATTERNS):
            return False
        if len(l.split()) <= 5 and (lower.startswith(EXPLANATORY_CONTINUATION_STARTS) or (lower[:1].islower() and len(l) >= 4)):
            return False
        return True

    if "........" in l:
        return True

    if re.search(r"\b1\.800\.", l):
        return True

    if re.search(r"p\.\s*o\.\s*bo", lower):
        return True

    if sum(c.isdigit() for c in l) > 8:
        return True

    for pattern in NOISE_PATTERNS:
        if re.search(pattern, lower):
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

    heading_joiners = {"and", "as", "at", "by", "for", "from", "in", "of", "on", "the", "to", "with"}

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

    normalized_words = [re.sub(r"[^A-Za-z]", "", word) for word in alpha_words]
    significant_words = [word for word in normalized_words if word and word.lower() not in heading_joiners]
    titled_significant_words = [
        word for word in alpha_words if re.sub(r"[^A-Za-z]", "", word).lower() not in heading_joiners and word[:1].isupper()
    ]
    if (
        len(alpha_words) <= 8
        and significant_words
        and len(titled_significant_words) == len(significant_words)
        and not stripped.endswith(".")
    ):
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


def classify_section(heading: str, lines) -> str:
    section_text = f"{heading} {' '.join(lines[:8])}"
    return classify_policy(section_text)


def score_policy_line(line: str, heading: str = "") -> int:
    category = classify_policy(f"{heading} {line}")
    score = scenario_worthiness_score(line, category, heading=heading)
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

    if 45 <= len(line) <= 180:
        score += 1

    return score


def select_best_policy_line(lines, heading: str):
    best_line = None
    best_score = None

    for line in lines:
        if not looks_like_policy_line(line):
            continue

        line_score = score_policy_line(line, heading=heading)
        if best_score is None or line_score > best_score:
            best_score = line_score
            best_line = line

    return best_line, best_score or 0


def block_scenario_worthiness(heading: str, lines, category: str) -> int:
    heading_lower = heading.lower()
    text = " ".join(lines[:10]).lower()

    score = 0
    score += sum(3 for pattern in SECTION_POSITIVE_PATTERNS if re.search(pattern, heading_lower))
    score -= sum(5 for pattern in SECTION_NEGATIVE_PATTERNS if re.search(pattern, heading_lower))
    score += sum(1 for pattern in SCENARIO_POSITIVE_PATTERNS if re.search(pattern, text))
    score -= sum(2 for pattern in SCENARIO_NEGATIVE_PATTERNS if re.search(pattern, text))

    if any(word in heading_lower for word in ["responsibilities", "purpose", "scope", "commitment"]):
        score -= 5
    if any(word in heading_lower for word in ["training", "awareness", "responsibilities"]):
        score -= 2

    if category in {"safety", "reporting", "equipment", "sanitation", "policy"}:
        score += 2
    if category == "general":
        score -= 2
    if category == "opening_shift":
        score -= 3
    if category == "customer_service":
        score -= 2

    return score


def build_trigger_from_section(heading: str, policy: str, category: str) -> str:
    heading_lower = heading.lower()
    policy_lower = normalize_policy_text(policy).lower()

    if "under ar ppe" in policy_lower or "wear under ar ppe" in policy_lower:
        return "You are getting dressed for arc-flash work and need to choose what to wear underneath your AR PPE"
    if "must not rely solely on ppe" in policy_lower or "not rely solely on ppe alone" in policy_lower:
        return "You are planning work around an electrical hazard and need controls beyond just PPE"
    if "select appropriate ppe" in policy_lower:
        return "You are choosing PPE for a task with electrical hazards"
    if "arc flashes are less likely to occur when equipment is properly maintained" in policy_lower:
        return "You are preparing to work near equipment with potential arc-flash hazards"
    if any(
        phrase in policy_lower
        for phrase in ["separate two similar pieces of equipment", "park each at a different spot on site"]
    ):
        return "You need to stage or park two similar pieces of equipment in the same work area"
    if "opening the hatch" in policy_lower:
        return "You are about to open a hatch on equipment that may expose you to hazardous material"
    if "disposable outer garments" in policy_lower:
        return "You are entering an area where contamination is possible"
    if "decontaminate" in policy_lower and "clean zone" in policy_lower:
        return "You are about to move equipment from a contaminated area into the clean zone"
    if any(
        phrase in policy_lower
        for phrase in ["spark arrestors", "refuel in safe areas", "do not fuel engines while vehicle is running"]
    ):
        return "You are preparing to use or refuel an engine in a hazardous work area"
    if "ignition keys" in policy_lower:
        return "You finish using a vehicle or piece of equipment and are about to leave it parked"
    if "suspected exposures" in policy_lower:
        return "You believe someone may have been exposed to a hazardous substance on the site"
    if any(phrase in policy_lower for phrase in ["notify project hse staff", "notify project hse", "problems or concerns"]):
        return "You notice a problem or concern on the project that needs to be reported"
    if any(phrase in policy_lower for phrase in ["unsafe acts", "unsafe act", "unsafe conditions", "unsafe condition"]):
        return "You notice an unsafe act or unsafe condition on the project"
    if any(phrase in policy_lower for phrase in ["loose items", "loose accessories", "do not wear jewelry"]):
        return "You are getting ready to work and notice clothing or personal items that could create a hazard"
    if any(
        phrase in policy_lower
        for phrase in ["report all incidents", "report any accident", "report accurately and immediately every accident"]
    ):
        return "An incident happens on the project and it needs to be reported correctly"
    if any(
        phrase in policy_lower
        for phrase in ["losses of tools", "incidents of security", "missing tools", "missing equipment"]
    ):
        return "You discover missing tools, equipment, materials, or a security issue on the project"
    if any(
        phrase in policy_lower
        for phrase in ["checked at the beginning of each shift", "inspection before use", "inspect before use"]
    ):
        return "You are preparing to use a vehicle or piece of equipment at the start of the shift"
    if any(
        phrase in policy_lower
        for phrase in ["unqualified for assigned work", "additional training is needed", "qualified and trained to do"]
    ):
        return "You are assigned work that you are not fully qualified or trained to perform"
    if "visibility is low" in policy_lower:
        return "You are getting ready to use a vehicle in low-visibility conditions"
    if "heat related illness" in policy_lower or "heat illness" in heading_lower:
        return "A crew member begins showing signs of heat-related illness during hot conditions on site"
    if any(word in policy_lower for word in ["ppe", "protective equipment", "body protection", "limb protection"]):
        return "You are assigned a task that requires the correct protective equipment"
    if any(
        phrase in policy_lower
        for phrase in ["out of service", "tagged", "damaged equipment", "damaged tool", "damaged tools"]
    ):
        return "You are about to use equipment or tools and notice a potential safety problem"
    if "vehicle" in policy_lower or "seat belt" in policy_lower:
        return "You are about to operate a company vehicle or powered equipment"
    if any(word in policy_lower for word in ["equipment", "tool", "tools", "machine", "ladder"]):
        return "You are about to use equipment or tools and notice a potential safety problem"
    if any(word in policy_lower for word in ["accident", "injury", "illness", "near miss"]):
        return "An incident or injury occurs on site and you need to respond correctly"
    if "spill" in policy_lower or "housekeeping" in heading_lower:
        return "You notice spilled material and clutter creating a hazard in an active work area"
    if any(word in heading_lower for word in ["incident", "injury", "reporting"]):
        return "An incident or injury occurs on site and you need to respond correctly"
    if "vehicle" in heading_lower:
        return "You are about to operate a company vehicle or powered equipment"
    if "ladder" in heading_lower:
        return "You are getting ready to use a ladder and notice something that could make it unsafe"
    if "fall protection" in heading_lower:
        return "You are preparing to work where a fall hazard is present"
    if "electrical" in heading_lower or "lockout" in heading_lower:
        return "You need to work near electrical equipment or machinery that could be hazardous"
    if "ppe" in heading_lower or "protective equipment" in heading_lower:
        return "You are assigned a task that requires the correct protective equipment"
    if any(word in heading_lower for word in ["equipment", "tools", "crane", "lift"]):
        return "You are about to use equipment or tools and notice a potential safety problem"
    if any(word in policy_lower for word in ["unsafe conditions", "unsafe condition", "hazards"]):
        return "You notice an unsafe condition in the work area"

    return sentence_case(extract_trigger_text(policy))


def build_block_prompt(heading: str, policy: str, category: str) -> str:
    trigger = build_trigger_from_section(heading, policy, category)
    escalation = extract_escalation_text(policy)

    if category == "sanitation":
        return f"{trigger}. What should you do first to control the hazard and keep the area safe?"
    if category == "safety":
        question = f"{trigger}. What immediate action should you take?"
        if escalation:
            question += f" When would you {escalation}?"
        else:
            question += " Who should be notified?"
        return question
    if category == "reporting":
        return f"{trigger}. Who needs to be informed, and what details should you report?"
    if category == "policy":
        return f"{trigger}. You are not fully sure what the rule allows. What should you do before moving forward?"
    if category == "equipment":
        return f"{trigger}. What should you do right away to keep yourself and others safe?"
    if category == "opening_shift":
        return f"{trigger}. What needs to be handled before work continues?"
    if category == "customer_service":
        return f"{trigger}. How would you handle the situation without guessing or creating more risk?"
    return f"{trigger}. Based on company procedure, what should you do first?"


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


EXPLANATORY_CONTINUATION_STARTS = (
    "and ",
    "or ",
    "but ",
    "to ",
    "for ",
    "of ",
    "with ",
    "by ",
    "from ",
    "if ",
    "when ",
    "while ",
    "where ",
    "that ",
    "which ",
    "who ",
    "the ",
    "a ",
    "an ",
    "each ",
    "mesh ",
    "all mesh ",
    "guardrail ",
    "personal ",
    "warning ",
    "qualified ",
    "developed ",
    "maintained ",
    "approved ",
    "available",
    "copy ",
    "training must ",
    "the employer must ",
    "there may be times ",
    "for example",
    "or more by ",
)


def previous_line_needs_continuation(prev_lower: str) -> bool:
    trimmed_prev = prev_lower.rstrip(" .;,:!?")

    if re.search(r"\b(to|for|of|and|or|the|a|an|if|when|with|your|their|are|is|was|were|be|been)\s*$", prev_lower):
        return True

    if any(
        trimmed_prev.endswith(fragment)
        for fragment in [
            "importance",
            "qualified",
            "6 feet",
            "safe openings",
            "training must",
            "has been trained",
            "warning line system",
            "control",
            "arc",
            "endanger",
            "unpredictably",
        ]
    ):
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

    curr_is_continuation = curr_starts_lower or curr_lower.startswith(EXPLANATORY_CONTINUATION_STARTS)

    if re.search(r"[.:!?]$", prev) and len(prev.split()) >= 8:
        return previous_line_needs_continuation(prev_lower) and curr_is_continuation

    if previous_line_needs_continuation(prev_lower):
        if curr_is_continuation or curr_lower.startswith(("assigned ", "additional ", "the employee ", "their ", "your ")):
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
        return curr_is_continuation

    if len(prev.split()) < 8:
        return curr_is_continuation

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

    if "report unsafe condition" in l or "report unsafe conditions" in l:
        if any(term in l for term in ["supervisor", "notify", "immediately", "project"]):
            return "reporting"
        return "safety"
    if any(
        phrase in l
        for phrase in [
            "suspected exposures",
            "unsafe acts",
            "unsafe act",
            "notify pcl",
            "notify project hse",
            "report all incidents",
            "report any accident",
            "report accurately and immediately every accident",
            "identify and report hazards",
            "notify your supervisor",
        ]
    ):
        return "reporting"
    if any(word in l for word in ["ppe", "protective equipment", "body protection", "limb protection"]):
        return "equipment"
    if any(word in l for word in ["wash", "sanitize", "clean", "hygiene", "gloves"]):
        return "sanitation"
    if any(word in l for word in ["customer", "guest"]) or (
        "help" in l and any(word in l for word in ["customer", "guest", "public", "client"])
    ):
        return "customer_service"
    if any(word in l for word in ["refund", "policy", "return", "procedure"]):
        return "policy"
    if any(word in l for word in ["manager", "supervisor", "notify", "document", "escalat"]):
        return "reporting"
    if any(phrase in l for phrase in ["accident", "incidents", "incident", "near miss", "near misses"]):
        return "reporting"
    if any(word in l for word in ["equipment", "knife", "box cutter", "tool", "ladder", "machine", "slicer"]):
        return "equipment"
    if any(word in l for word in ["spill", "hazard", "safe", "safety", "injury", "emergenc"]):
        return "safety"
    if any(word in l for word in ["clock in", "uniform", "late", "ready for work", "opening", "before work", "start of shift"]):
        return "opening_shift"

    return "general"


def select_policy_category(policy: str, heading: str, block_category: str) -> str:
    policy_category = classify_policy(policy)
    if policy_category != "general":
        return policy_category

    combined_category = classify_policy(f"{policy} {heading}")
    if combined_category != "general":
        return combined_category

    return block_category


def looks_like_policy_line(line: str) -> bool:
    normalized = normalize_policy_text(line)
    lower = normalized.lower()
    stripped_lower = re.sub(r"^[\u2022\-]\s*", "", lower)

    if len(normalized) < 35 or len(normalized) > 220:
        return False

    if any(re.search(pattern, lower) for pattern in NARRATIVE_FRAGMENT_PATTERNS):
        return False

    if any(re.search(pattern, lower) for pattern in ADMIN_FRAGMENT_PATTERNS):
        return False

    if any(
        phrase in stripped_lower
        for phrase in [
            "health, safety, and environment must be taken into consideration when purchasing equipment",
            "personally owned ppe must be approved by project management prior to use on a project site",
            "collect environmental/environmental spill facts, must be completed",
            "documented reports are to be submitted in three days",
        ]
    ):
        return False

    if normalized.count("(") > normalized.count(")"):
        return False

    # Mid-sentence PDF fragments often start lowercase and lack a clear actor/action opening.
    if normalized[:1].islower() and not re.match(r"^(?:[•\-]\s*)?(?:if|when|all|employees?|workers?|operators?|supervisors?|site personnel)\b", lower):
        return False

    if stripped_lower.startswith(
        (
            "supervisor and/or",
            "the supervisor shall",
            "the qualified person must",
            "the qualified person shall",
            "foreman/supervisor",
            "supervisor ",
            "guards must be fully apprised",
            "locate the station in the clean area adjacent",
            "the ongoing monitoring of atmospheric chemical hazards",
            "the type of equipment used and the overall level of protection should be reevaluated",
            "exclusion zone; rather, they should observe site conditions from the clean area",
        )
    ):
        return False

    if stripped_lower.startswith(("avoid loose items", "in addition to the required module")):
        return False

    if re.search(r"\b(fi\s+rst|depart\s+ment)\b", lower):
        return False

    # Reject merged PDF fragments that splice numbered checklist items into one line.
    if re.search(r"\b\d+\s*-\s*[a-z]", lower):
        return False

    if re.search(r"\b(and|or|to|a|an|the|are|is|be|been|being|for|with|of)\s*$", lower):
        return False

    if normalized.endswith(";"):
        return False

    if ":" in normalized and len(normalized.split(":")[-1].strip().split()) < 4:
        return False

    if any(lower.endswith(fragment) for fragment in ["the following", "filled out in", "outlined in detail", "evidence of what"]):
        return False

    if re.search(r"(?:,\s*|(?:\bto|\bfor|\bof|\band|\bor)\s+)$", lower):
        return False

    if any(
        lower.endswith(fragment)
        for fragment in [
            "to your",
            "the trade",
            "medical",
            "servicing",
            "as soon",
            "initial",
            "equipment",
            "look",
            "care",
            "see",
            "occur",
            "who",
            "placed",
            "protective",
            "powered",
            "inadequate",
            "all",
            "set",
            "eye",
            "because",
            "his",
            "hazardous",
            "walking",
            "ensure",
            "same",
            "motor",
            "completed",
            "control",
            "importance",
            "unpredictably",
            "flammable",
        ]
    ):
        return False

    if lower.endswith("equipment used"):
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
    if lower.startswith(("the superintendent/supervisor must ensure", "each supervisor must receive training")):
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
    scored = []
    for block in build_section_blocks(handbook_text):
        heading = block["heading"]
        heading_lower = heading.lower()
        if any(re.search(pattern, heading_lower) for pattern in SECTION_NEGATIVE_PATTERNS):
            continue

        block_category = classify_section(heading, block["lines"])
        best_lines_by_category = {}

        for line in block["lines"]:
            if not looks_like_policy_line(line):
                continue

            category = select_policy_category(line, heading, block_category)
            line_score = score_policy_line(line, heading=heading)
            existing = best_lines_by_category.get(category)
            if existing is None or line_score > existing[1]:
                best_lines_by_category[category] = (line, line_score)

        if not best_lines_by_category:
            continue

        for category, (policy_line, line_score) in best_lines_by_category.items():
            block_score = 0 if heading == "General" else block_scenario_worthiness(heading, block["lines"], category)
            total_score = line_score + block_score
            if total_score < 4:
                continue

            scored.append((total_score, policy_line, category, heading))

    scored.sort(key=lambda x: x[0], reverse=True)

    chosen = []
    seen = set()

    for score, line, category, heading in scored:
        key = (heading.lower(), category)
        if key not in seen:
            prompt = build_best_prompt(heading, line, category)
            if not prompt:
                continue
            chosen.append(
                {
                    "policy": line,
                    "category": category,
                    "heading": heading,
                    "score": score,
                    "prompt": prompt,
                    "hint": build_policy_hint(line, category),
                }
            )
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


def build_policy_hint(policy: str, category: str) -> str:
    focus_terms = extract_focus_terms(policy, limit=2)
    focus = join_terms(focus_terms)

    hint_templates = {
        "sanitation": "Handbook cue: focus on controlling the hazard, cleaning it correctly, and protecting other people nearby.",
        "safety": "Handbook cue: focus on the first step that reduces risk and when the situation should be escalated.",
        "reporting": "Handbook cue: focus on who needs to be informed and what key facts should be communicated.",
        "policy": "Handbook cue: focus on checking the rule before acting instead of improvising.",
        "equipment": "Handbook cue: focus on safe equipment or PPE use and how you prevent others from being exposed.",
        "customer_service": "Handbook cue: focus on helping the customer without guessing or creating additional risk.",
        "opening_shift": "Handbook cue: focus on what must be ready or corrected before work continues.",
    }

    if category in hint_templates:
        return hint_templates[category]

    return f"Handbook cue: think about the company procedure for {focus} before you answer."


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


def tokenize_prompt_words(text: str):
    return [word for word in re.findall(r"[a-z][a-z0-9\-']+", text.lower()) if len(word) > 3]


def extract_trigger_text(policy: str) -> str:
    normalized = normalize_policy_text(policy)
    lower = normalized.lower()

    direct_policy_patterns = [
        (
            r"under ar ppe|wear under ar ppe",
            "you are getting dressed for arc-flash work and need to choose what to wear underneath your ar ppe",
        ),
        (
            r"must not rely solely on ppe|not rely solely on ppe alone",
            "you are planning work around an electrical hazard and need controls beyond just ppe",
        ),
        (
            r"select appropriate ppe",
            "you are choosing ppe for a task with electrical hazards",
        ),
        (
            r"arc flashes are less likely to occur when equipment is properly maintained",
            "you are preparing to work near equipment with potential arc-flash hazards",
        ),
        (
            r"separate two similar pieces of equipment|park each at a different spot on site",
            "you need to stage or park two similar pieces of equipment in the same work area",
        ),
        (
            r"opening the hatch",
            "you are about to open a hatch on equipment that may expose you to hazardous material",
        ),
        (
            r"disposable outer garments",
            "you are entering an area where contamination is possible",
        ),
        (
            r"decontaminate.+clean zone",
            "you are about to move equipment from a contaminated area into the clean zone",
        ),
        (
            r"spark arrestors|refuel in safe areas|do not fuel engines while vehicle is running",
            "you are preparing to use or refuel an engine in a hazardous work area",
        ),
        (
            r"unqualified for assigned work|additional training is needed|qualified and trained to do",
            "you are assigned work that you are not fully qualified or trained to perform",
        ),
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


def prompt_specificity_score(prompt: str, policy: str) -> int:
    lower_prompt = prompt.lower()
    focus_terms = extract_focus_terms(policy, limit=4)
    score = 0

    score += sum(2 for term in focus_terms if term in lower_prompt)

    if "you run into a situation involving" in lower_prompt:
        score -= 6
    if any(
        phrase in lower_prompt
        for phrase in [
            "you are about to use equipment or tools and notice a potential safety problem",
            "you are about to operate a company vehicle or powered equipment",
            "an incident or injury occurs on site and you need to respond correctly",
        ]
    ):
        score -= 2

    if any(
        phrase in lower_prompt
        for phrase in [
            "clean zone",
            "hatch",
            "refuel",
            "park two similar pieces of equipment",
            "hazardous substance",
            "unsafe condition",
            "problem or concern",
            "low-visibility",
        ]
    ):
        score += 2

    return score


def is_usable_prompt(prompt: str) -> bool:
    lower = prompt.lower()

    if "you run into a situation involving" in lower:
        return False
    if prompt.count("(") > prompt.count(")"):
        return False
    if re.search(r"\bcontact with\b", lower):
        return False
    if re.search(r"\b[a-z]\?$", lower):
        return False

    return True


def prompt_signature(prompt: str) -> str:
    lower = prompt.lower()

    normalized_patterns = [
        (
            r"you are assigned a task that requires the correct protective equipment\..+",
            "generic_protective_equipment",
        ),
        (
            r"you are about to use equipment or tools and notice a potential safety problem\..+",
            "generic_equipment_safety",
        ),
        (
            r"you are preparing to work where a fall hazard is present\..+",
            "generic_fall_hazard",
        ),
        (
            r"you notice an unsafe condition in the work area\..+",
            "generic_unsafe_condition",
        ),
    ]

    for pattern, signature in normalized_patterns:
        if re.match(pattern, lower):
            return signature

    normalized = re.sub(r"[^a-z0-9]+", " ", lower)
    return " ".join(normalized.split())


def prompts_are_too_similar(existing_prompt: str, candidate_prompt: str) -> bool:
    existing_signature = prompt_signature(existing_prompt)
    candidate_signature = prompt_signature(candidate_prompt)

    if existing_signature == candidate_signature:
        return True

    existing_words = set(tokenize_prompt_words(existing_signature))
    candidate_words = set(tokenize_prompt_words(candidate_signature))
    if not existing_words or not candidate_words:
        return False

    overlap = len(existing_words & candidate_words) / max(min(len(existing_words), len(candidate_words)), 1)
    return overlap >= 0.85


def build_best_prompt(heading: str, policy: str, category: str) -> str | None:
    candidates = []
    heading_prompt = build_block_prompt(heading, policy, category)
    policy_prompt = build_policy_specific_prompt(policy, category)

    for candidate in [heading_prompt, policy_prompt]:
        if is_usable_prompt(candidate):
            candidates.append((prompt_specificity_score(candidate, policy), candidate))

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]


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


def build_policy_specific_prompt(policy: str, category: str, heading: str = "") -> str:
    if heading:
        return build_block_prompt(heading, policy, category)

    rule = build_structured_rule(policy, category)
    trigger = sentence_case(rule["trigger"])
    escalation = rule["escalation"]

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


def build_initial_scenarios(policies, max_scenarios: int = 5):
    prepared_items = []
    for item in policies:
        prompt = item.get("prompt") or build_best_prompt(item.get("heading", ""), item["policy"], item["category"])
        if not prompt:
            continue
        prepared_items.append({**item, "prompt": prompt})

    scenarios = []
    used_categories = set()
    used_policy_keys = set()
    next_id = 1

    def can_add_prompt(candidate_prompt: str) -> bool:
        return not any(prompts_are_too_similar(existing["prompt"], candidate_prompt) for existing in scenarios)

    for item in prepared_items:
        if len(used_categories) >= 3:
            break
        if item["category"] in used_categories:
            continue
        if not can_add_prompt(item["prompt"]):
            continue

        policy_key = (item["category"], item["policy"])
        scenarios.append(
            {
                "id": next_id,
                "kind": "scenario",
                "category": item["category"],
                "policy": item["policy"],
                "heading": item.get("heading"),
                "hint": item.get("hint"),
                "prompt": item["prompt"],
            }
        )
        used_categories.add(item["category"])
        used_policy_keys.add(policy_key)
        next_id += 1

        if len(scenarios) >= max_scenarios:
            break

    for item in prepared_items:
        if len(scenarios) >= max_scenarios:
            break

        policy_key = (item["category"], item["policy"])
        if policy_key in used_policy_keys:
            continue
        if not can_add_prompt(item["prompt"]):
            continue

        scenarios.append(
            {
                "id": next_id,
                "kind": "scenario",
                "category": item["category"],
                "policy": item["policy"],
                "heading": item.get("heading"),
                "hint": item.get("hint"),
                "prompt": item["prompt"],
            }
        )
        used_policy_keys.add(policy_key)
        next_id += 1

    if not scenarios:
        fallback_policy = "Follow company procedures and prioritize safety."
        scenarios.append(
            {
                "id": 1,
                "kind": "scenario",
                "category": "general",
                "policy": fallback_policy,
                "heading": "General",
                "hint": build_policy_hint(fallback_policy, "general"),
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
