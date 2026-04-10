from app.tools.scenarios import (
    build_section_blocks,
    build_block_prompt,
    build_follow_up_scenario,
    build_initial_scenarios,
    build_policy_specific_prompt,
    extract_candidate_statements,
    extract_policies,
    looks_like_policy_line,
    split_into_candidate_lines,
    scenario_worthiness_score,
)


def test_build_initial_scenarios_uses_policy_terms_for_equipment_prompt():
    handbook_text = """
    Employees must inspect ladders before use and report damaged ladders immediately.
    Employees must store chemical containers in the marked cabinet after each shift.
    Employees should document any machine guard issue before restarting equipment.
    """

    policies = extract_policies(handbook_text)
    scenarios = build_initial_scenarios(policies)

    prompts = " ".join(item["prompt"].lower() for item in scenarios)

    assert "what should you do" in prompts or "what action should you take" in prompts
    assert "you find a sharp tool" in prompts or "you are about to" in prompts or "you notice" in prompts
    assert "customer" not in prompts


def test_build_follow_up_scenario_references_policy_text():
    scenario = {
        "id": 1,
        "kind": "scenario",
        "category": "equipment",
        "policy": "Employees must not leave sharp tools unattended.",
        "prompt": "placeholder",
    }

    follow_up = build_follow_up_scenario(scenario, next_id=2)

    assert follow_up["kind"] == "follow_up"
    assert "sharp tools" in follow_up["prompt"].lower()
    assert "equipment right away" in follow_up["prompt"].lower()


def test_looks_like_policy_line_rejects_narrative_pdf_fragments():
    assert not looks_like_policy_line(
        "within a store. It is, in most cases, the fi rst department a customer sees. With Americans eating"
    )
    assert not looks_like_policy_line(
        "educated as to what is expected each and every day. Produce managers, full and part time"
    )


def test_extract_policies_keeps_actionable_rules_and_skips_fragments():
    handbook_text = """
    within a store. It is, in most cases, the fi rst department a customer sees. With Americans eating
    Employees must clean spills immediately or block the area and report the hazard.
    educated as to what is expected each and every day. Produce managers, full and part time
    Employees must not leave sharp tools unattended.
    """

    policies = extract_policies(handbook_text)
    policy_text = " ".join(item["policy"].lower() for item in policies)

    assert "clean spills immediately" in policy_text
    assert "sharp tools unattended" in policy_text
    assert "within a store" not in policy_text
    assert "educated as to what" not in policy_text


def test_looks_like_policy_line_rejects_incomplete_or_display_fragments():
    assert not looks_like_policy_line(
        "your name badge visible and easy to read. Having a clean apron indicates a"
    )
    assert not looks_like_policy_line(
        "In order to achieve these things, everyone within your department must be well informed and"
    )


def test_build_policy_specific_prompt_creates_actionable_safety_scenario():
    prompt = build_policy_specific_prompt(
        "Employees must clean spills immediately or block the area and report the hazard.",
        "sanitation",
    )

    lowered = prompt.lower()
    assert "you notice a spill on the floor" in lowered
    assert "what action should you take right away" in lowered


def test_build_policy_specific_prompt_creates_actionable_policy_scenario():
    prompt = build_policy_specific_prompt(
        "Employees must never guess about refund policy. They should check the policy or ask a manager.",
        "policy",
    )

    lowered = prompt.lower()
    assert "refund decision" in lowered
    assert "what should you do next before making a decision" in lowered


def test_build_block_prompt_uses_section_context_for_heat_illness():
    prompt = build_block_prompt(
        "HEAT ILLNESS PREVENTION PROGRAM",
        "Physical factors that can contribute to heat related illness shall be taken into consideration before work begins.",
        "safety",
    )

    lowered = prompt.lower()
    assert "heat-related illness" in lowered
    assert "what immediate action should you take" in lowered


def test_scenario_worthiness_penalizes_admin_or_posting_rules():
    annual_summary = "The annual summary must be posted no later than February 1st of the year following the year covered"
    unsafe_conditions = "Every employee has a personal responsibility to adhere to safety rules and report unsafe conditions"

    assert scenario_worthiness_score(annual_summary, "opening_shift") < 1
    assert scenario_worthiness_score(unsafe_conditions, "safety") > 1


def test_extract_policies_skips_admin_rules_from_large_manual_style_text():
    handbook_text = """
    The annual summary must be posted no later than February 1st of the year following the year covered.
    atmosphere (if ventilation fails or for other reasons), the trained rescue team or service must be standing by.
    Every employee has a personal responsibility to adhere to safety rules and report unsafe conditions.
    Immediately report all accidents, incidents, near misses, property damage, and potentially unsafe conditions.
    """

    policies = extract_policies(handbook_text)
    policy_text = " ".join(item["policy"].lower() for item in policies)

    assert "annual summary" not in policy_text
    assert "trained rescue team or service" not in policy_text
    assert "report unsafe conditions" in policy_text


def test_extract_policies_prefers_section_based_worker_actions():
    handbook_text = """
    INTRODUCTION
    This manual explains the safety program.
    HEAT ILLNESS PREVENTION PROGRAM
    Physical factors that can contribute to heat related illness shall be taken into consideration before work begins.
    INCIDENT INVESTIGATION AND REPORTING PROGRAM
    Immediately report all accidents, incidents, near misses, property damage, and potentially unsafe conditions.
    """

    policies = extract_policies(handbook_text)

    assert policies
    assert any(item["heading"] == "HEAT ILLNESS PREVENTION PROGRAM" for item in policies)
    assert any(item["heading"] == "INCIDENT INVESTIGATION AND REPORTING PROGRAM" for item in policies)


def test_split_into_candidate_lines_merges_continuation_lines():
    handbook_text = """
    Perform only work they are qualified and trained to do. Notify the supervisor if unqualified for
    assigned work or if additional training is needed.
    """

    candidates = split_into_candidate_lines(handbook_text)

    assert len(candidates) == 1
    assert "assigned work or if additional training is needed" in candidates[0].lower()


def test_extract_policies_benefits_from_merged_pdf_style_lines():
    handbook_text = """
    Perform only work they are qualified and trained to do. Notify the supervisor if unqualified for
    assigned work or if additional training is needed.
    """

    policies = extract_policies(handbook_text)

    assert policies
    assert "assigned work or if additional training is needed" in policies[0]["policy"].lower()


def test_build_section_blocks_groups_lines_under_headings():
    handbook_text = """
    HOUSEKEEPING PROGRAM
    Keep work areas clean and organized.
    Report spills immediately.
    INCIDENT INVESTIGATION AND REPORTING PROGRAM
    Immediately report all accidents to your supervisor.
    """

    blocks = build_section_blocks(handbook_text)

    assert len(blocks) >= 2
    assert blocks[0]["heading"] == "HOUSEKEEPING PROGRAM"
    assert any("report spills immediately" in line.lower() for line in blocks[0]["lines"])


def test_extract_candidate_statements_skips_intro_sections():
    handbook_text = """
    Message from the President
    Safety is important to our company.
    HOUSEKEEPING PROGRAM
    Keep work areas clean and organized. Report spills immediately.
    """

    candidates = extract_candidate_statements(handbook_text)
    joined = " ".join(item["policy"].lower() for item in candidates)

    assert "safety is important to our company" not in joined
    assert "report spills immediately" in joined
