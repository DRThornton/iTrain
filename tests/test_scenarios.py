from app.tools.scenarios import (
    build_section_blocks,
    build_block_prompt,
    build_follow_up_scenario,
    build_initial_scenarios,
    build_policy_specific_prompt,
    extract_candidate_statements,
    extract_policies,
    looks_like_policy_line,
    prompts_are_too_similar,
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


def test_build_initial_scenarios_include_one_line_handbook_hint():
    handbook_text = """
    Employees must clean spills immediately or block the area and report the hazard.
    """

    policies = extract_policies(handbook_text)
    scenarios = build_initial_scenarios(policies)

    assert scenarios
    assert scenarios[0]["hint"].startswith("Handbook cue:")
    assert "clean spills immediately" not in scenarios[0]["hint"].lower()
    assert "controlling the hazard" in scenarios[0]["hint"].lower()


def test_build_initial_scenarios_backfills_when_categories_are_limited():
    policies = [
        {
            "policy": "Policy A",
            "category": "equipment",
            "heading": "Equipment",
            "hint": "hint",
            "prompt": "You are about to use a ladder and notice a damaged rung. What should you do right away?",
        },
        {
            "policy": "Policy B",
            "category": "safety",
            "heading": "Safety",
            "hint": "hint",
            "prompt": "You notice an unguarded floor opening. What immediate action should you take?",
        },
        {
            "policy": "Policy C",
            "category": "equipment",
            "heading": "Equipment",
            "hint": "hint",
            "prompt": "You are preparing to park two similar pieces of equipment in the same work area. What should you do?",
        },
        {
            "policy": "Policy D",
            "category": "equipment",
            "heading": "Equipment",
            "hint": "hint",
            "prompt": "You are choosing PPE for a task with electrical hazards. What should you do right away?",
        },
    ]

    scenarios = build_initial_scenarios(policies, max_scenarios=5)

    assert len(scenarios) == 4
    assert [item["policy"] for item in scenarios] == ["Policy A", "Policy B", "Policy C", "Policy D"]


def test_build_initial_scenarios_skips_near_duplicate_prompt_shapes():
    policies = [
        {
            "policy": "Policy A",
            "category": "equipment",
            "heading": "Equipment",
            "hint": "hint",
            "prompt": "You are assigned a task that requires the correct protective equipment. What should you do right away to keep yourself and others safe?",
        },
        {
            "policy": "Policy B",
            "category": "equipment",
            "heading": "Equipment",
            "hint": "hint",
            "prompt": "You are assigned a task that requires the correct protective equipment. What should you do right away to keep yourself and others safe?",
        },
        {
            "policy": "Policy C",
            "category": "safety",
            "heading": "Safety",
            "hint": "hint",
            "prompt": "You notice an unsafe condition in the work area. What immediate action should you take?",
        },
    ]

    scenarios = build_initial_scenarios(policies, max_scenarios=5)

    assert len(scenarios) == 2
    assert [item["policy"] for item in scenarios] == ["Policy A", "Policy C"]


def test_prompts_are_too_similar_for_generic_duplicate_ppe_prompts():
    assert prompts_are_too_similar(
        "You are assigned a task that requires the correct protective equipment. What should you do right away to keep yourself and others safe?",
        "You are assigned a task that requires the correct protective equipment. What should you do right away to keep yourself and others safe?",
    )


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


def test_extract_policies_prefers_selected_line_category_over_broad_section_heading():
    handbook_text = """
    INCIDENT INVESTIGATION AND REPORTING PROGRAM
    Limb and body protection must be worn and equipment designed to protect employees from injury to their limbs and body must be used.
    """

    policies = extract_policies(handbook_text)

    assert policies
    assert policies[0]["category"] == "equipment"
    assert "protective equipment" in policies[0]["prompt"].lower()


def test_extract_policies_uses_policy_text_before_heading_for_equipment_prompts():
    handbook_text = """
    VEHICLE SAFETY PROGRAM
    Tools or equipment must be tagged "OUT OF SERVICE", and the damage must be reported before use.
    """

    policies = extract_policies(handbook_text)
    scenarios = build_initial_scenarios(policies)

    assert scenarios
    prompt = scenarios[0]["prompt"].lower()
    assert "equipment or tools" in prompt
    assert "company vehicle" not in prompt


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


def test_split_into_candidate_lines_merges_qualified_person_continuation():
    handbook_text = """
    A fall protection plan must be prepared by a qualified
    person and developed specifically for the site where the work is being performed.
    """

    candidates = split_into_candidate_lines(handbook_text)

    assert len(candidates) == 1
    assert "qualified person and developed specifically for the site" in candidates[0].lower()


def test_split_into_candidate_lines_merges_sentence_detail_after_period():
    handbook_text = """
    To work properly, a safety net must have safe openings.
    Mesh openings must not exceed 36 square inches, and must not be longer than 6 inches on any side.
    """

    candidates = split_into_candidate_lines(handbook_text)

    assert len(candidates) == 1
    assert "mesh openings must not exceed 36 square inches" in candidates[0].lower()


def test_split_into_candidate_lines_merges_hoist_area_requirement_with_protection_detail():
    handbook_text = """
    Each worker in a hoist area must be protected from falling 6 feet
    or more by guardrail systems or personal fall arrest systems.
    """

    candidates = split_into_candidate_lines(handbook_text)

    assert len(candidates) == 1
    assert "or more by guardrail systems or personal fall arrest systems" in candidates[0].lower()


def test_split_into_candidate_lines_merges_arc_ppe_explanation():
    handbook_text = """
    Additionally, employers should stress the importance
    of what employees wear under AR PPE, since the arc
    flash, or the molten metal created, can unpredictably
    penetrate seams, closures, or flaps and ignite flammable
    """

    candidates = split_into_candidate_lines(handbook_text)

    assert len(candidates) == 1
    assert "under ar ppe, since the arc flash" in candidates[0].lower()
    assert "ignite flammable" in candidates[0].lower()


def test_split_into_candidate_lines_merges_ppe_control_explanation():
    handbook_text = """
    Employers must not rely solely on PPE alone to control
    hazards when other effective control options are
    available.
    """

    candidates = split_into_candidate_lines(handbook_text)

    assert len(candidates) == 1
    assert "control hazards when other effective control options are available" in candidates[0].lower()


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


def test_looks_like_policy_line_rejects_inline_numbered_pdf_fragments():
    assert not looks_like_policy_line(
        "2 - Document the equipment inspection before use on each shift 12 - Vehicles must have service & parking brakes, brake lights"
    )


def test_extract_policies_skips_return_to_work_admin_fragments():
    handbook_text = """
    Report an employee's return to work to the applicable workers.
    Employees must clean spills immediately or block the area and report the hazard.
    """

    policies = extract_policies(handbook_text)
    policy_text = " ".join(item["policy"].lower() for item in policies)

    assert "return to work" not in policy_text
    assert "clean spills immediately" in policy_text


def test_looks_like_policy_line_rejects_form_and_process_reference_fragments():
    assert not looks_like_policy_line(
        "Incident Investigation form, the user will need to identify the type of incident that occurred: Injury, Loss, or incident is a Near Miss, HSE-13-02, Near Miss Form, should be used."
    )
    assert not looks_like_policy_line(
        "Use this report for environmental or environmental spill incidents. This form will always be filled out in"
    )
    assert not looks_like_policy_line(
        "protective equipment requirements. The requirements must be outlined in detail"
    )


def test_build_block_prompt_uses_policy_specific_vehicle_access_trigger():
    prompt = build_block_prompt(
        "6.2.7.2 Vehicle Access",
        "Ignition keys must not be left with the equipment after hours or when a vehicle is parked in a public location.",
        "equipment",
    )

    lowered = prompt.lower()
    assert "about to leave it parked" in lowered
    assert "company vehicle or powered equipment" not in lowered


def test_build_block_prompt_uses_policy_specific_reporting_trigger_over_ppe_heading():
    prompt = build_block_prompt(
        "Wear appropriate PPE; (HSE-07)",
        "Report any unsafe acts and/or unsafe conditions to the PCL project",
        "safety",
    )

    lowered = prompt.lower()
    assert "unsafe act or unsafe condition" in lowered
    assert "requires the correct protective equipment" not in lowered


def test_classify_policy_prefers_reporting_for_unsafe_condition_reporting_rule():
    policies = extract_policies(
        """
        General Safety Rules for Employees
        2. Report Unsafe Conditions. Immediately report any unsafe condition, act, or equipment to your supervisor.
        """
    )

    assert policies
    assert policies[0]["category"] == "reporting"
    assert "who needs to be informed" in policies[0]["prompt"].lower()


def test_looks_like_policy_line_rejects_truncated_pdf_tail_fragments():
    assert not looks_like_policy_line(
        "Trade contractors are responsible for verifying that their workers have the appropriate PPE and are trained in its use and maintenance. The Trade"
    )
    assert not looks_like_policy_line(
        "Operators of vehicles/equipment shall be made aware of the servicing,"
    )
    assert not looks_like_policy_line(
        "Notify project HSE staff and supervisors regarding medications, medical"
    )


def test_looks_like_policy_line_rejects_supervisor_process_directives():
    assert not looks_like_policy_line(
        "Supervisor and/or site safety manager should utilize daily JSA form to identify any housekeeping"
    )
    assert not looks_like_policy_line(
        "The Qualified Person must determine if the repair adjustment meets manufacturer equipment"
    )


def test_looks_like_policy_line_rejects_medical_surveillance_and_reference_lines():
    assert not looks_like_policy_line(
        "Provide additional testing (e.g., chest X-ray, pulmonary function testing, electrocardiogram) for ability to wear protective equipment where necessary."
    )
    assert not looks_like_policy_line(
        "Pulmonary function testing. Measurement should include forced expiratory volume in 1 second"
    )
    assert not looks_like_policy_line(
        "Lockers or closets for clean clothing and personal item storage."
    )
    assert not looks_like_policy_line(
        "Note limitations concerning the worker's ability to use protective equipment (e.g., individuals who"
    )
    assert not looks_like_policy_line(
        "Air-purifying respirators, on the other hand, do not have a separate air source."
    )
    assert not looks_like_policy_line(
        "A reading of zero should be reported as \"no instrument response\" and may indicate the instrument needs attention."
    )


def test_looks_like_policy_line_rejects_mid_sentence_pdf_fragments():
    assert not looks_like_policy_line(
        "out for potential safety hazards, and should immediately inform their supervisors of any new"
    )
    assert not looks_like_policy_line(
        "established, the hazards associated with these chemicals must be determined. This is done by"
    )
    assert not looks_like_policy_line(
        "Buckets, brushes, clothing, tools, and other contaminated equipment should be collected, placed"
    )


def test_looks_like_policy_line_rejects_incomplete_tail_fragments_from_manuals():
    assert not looks_like_policy_line(
        "Seat belts must be worn in all Company vehicles, equipment, and powered"
    )
    assert not looks_like_policy_line(
        "Personal Protective Equipment - ensure that personnel wear the required personal protective"
    )
    assert not looks_like_policy_line(
        "Response to spills, leaks, and release of hazardous materials must be set"
    )
    assert not looks_like_policy_line(
        "Overhead power lines, downed electrical wires, and buried cables all pose a danger of shock or electrocution if workers contact or sever them during site operations. Electrical equipment used"
    )
    assert not looks_like_policy_line(
        "Response to spills, leaks, and release of hazardous materials must be set"
    )
    assert not looks_like_policy_line(
        "In addition to the required module, observers should be trained in hazard"
    )
    assert not looks_like_policy_line(
        "Work or Work-Related Activity - an injury or illness must be considered work-related"
    )
    assert not looks_like_policy_line(
        "Guards must be fully apprised of the hazards involved before entering the area."
    )
    assert not looks_like_policy_line(
        "23. The worker should request a PSI and a JHA, if applicable, from his"
    )
    assert not looks_like_policy_line(
        "Communications Equipment - only use intrinsically safe equipment in areas where a hazardous"
    )
    assert not looks_like_policy_line(
        "When an equipment operator must negotiate in tight quarters, provide a second person to ensure"
    )
    assert not looks_like_policy_line(
        "Exclusion Zone; rather, they should observe site conditions from the clean area, e.g., using"
    )
    assert not looks_like_policy_line(
        "8. Tools and material shall be secured to prevent movement when transported in the same"
    )
    assert not looks_like_policy_line(
        "Transportation, Federal Motor Vehicle Safety Standards) shall be installed in all motor"
    )
    assert not looks_like_policy_line(
        "13-01E, Collect Environmental/Environmental Spill Facts, must be completed. Documented reports are to be submitted in three days."
    )
    assert not looks_like_policy_line(
        "Weather conditions during clean up operations;"
    )


def test_build_block_prompt_uses_reporting_trigger_for_suspected_exposure_rule():
    prompt = build_block_prompt(
        "Emergency",
        "Require workers to report any suspected exposures, regardless of degree.",
        "reporting",
    )

    lowered = prompt.lower()
    assert "may have been exposed" in lowered
    assert "who needs to be informed" in lowered


def test_build_block_prompt_uses_loose_items_trigger():
    prompt = build_block_prompt(
        "General Safety Rules for Employees",
        "Do not wear jewelry, unsecured long hair, loose accessories, or loose clothing around equipment.",
        "safety",
    )

    lowered = prompt.lower()
    assert "clothing or personal items" in lowered


def test_looks_like_policy_line_rejects_unclosed_example_fragment():
    assert not looks_like_policy_line(
        "Stress work practices that minimize contact with hazardous substances (e.g., do not walk"
    )


def test_extract_policies_prefers_policy_specific_equipment_prompt_for_separation_rule():
    policies = extract_policies(
        """
        Equipment
        Separate two similar pieces of equipment; park each at a different spot on site and do not use them at the same time.
        """
    )

    assert policies
    prompt = policies[0]["prompt"].lower()
    assert "park two similar pieces of equipment" in prompt or "stage or park two similar pieces of equipment" in prompt
    assert "potential safety problem" not in prompt


def test_extract_policies_prefers_policy_specific_sanitation_prompt_for_clean_zone_rule():
    policies = extract_policies(
        """
        Decontamination
        Completely decontaminate such equipment before moving it into the clean zone.
        """
    )

    assert policies
    prompt = policies[0]["prompt"].lower()
    assert "clean zone" in prompt
    assert "potential safety problem" not in prompt


def test_extract_policies_uses_distinct_policy_specific_ppe_prompts():
    under_prompt = build_block_prompt(
        "PPE: Arc-Rated, Rubber Insulated, and Fire-Resistant",
        "Additionally, employers should stress the importance of what employees wear under AR PPE.",
        "equipment",
    ).lower()
    beyond_prompt = build_block_prompt(
        "PPE selection and use",
        "Employers must not rely solely on PPE alone to control electrical hazards.",
        "equipment",
    ).lower()
    select_prompt = build_block_prompt(
        "Standards Association Workplace Electrical Safety",
        "Employers must select appropriate PPE for their workers.",
        "equipment",
    ).lower()

    assert "underneath your ar ppe" in under_prompt
    assert "beyond just ppe" in beyond_prompt
    assert "choosing ppe" in select_prompt
