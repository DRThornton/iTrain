import textwrap


def split_into_policy_lines(handbook_text: str):
    lines = []
    for raw in handbook_text.splitlines():
        line = raw.strip()
        if len(line) > 20:
            lines.append(line)
    return lines


def generate_scenarios(handbook_text: str, num_scenarios: int = 3):
    policies = split_into_policy_lines(handbook_text)
    scenarios = []

    for i, policy in enumerate(policies[:num_scenarios], start=1):
        scenario_text = textwrap.dedent(f"""
        Scenario {i}:
        A worker is in a situation related to this policy:
        "{policy}"

        What would you do next, and why?
        """).strip()

        scenarios.append({
            "id": i,
            "policy": policy,
            "prompt": scenario_text
        })

    return scenarios