---
name: itrain
description: Streamlit-based employee training simulator MVP for handbook-driven scenario practice and manager reporting. Use when working in the iTrain repository to understand the app flow, run the project, improve scenario generation or scoring, add tests, or make focused UI and report changes without introducing unnecessary infrastructure.
---

# iTrain Skill

Use this repository as a lightweight MVP, not a production platform.

## Run The App

Run the Streamlit app from the repo root:

```powershell
py -m streamlit run app/main.py
```

Primary dependency setup:

```powershell
py -m pip install -r requirements.txt
```

## Project Purpose

Build a browser-based job training demo that:

- loads a handbook from `.txt` or `.pdf`
- extracts likely policy statements from the handbook
- creates a short set of workplace scenarios
- collects free-text learner responses
- scores those responses against a rubric
- generates a manager-only JSON report

Keep recommendations aligned with the current MVP unless the user explicitly asks for a broader redesign.

## Key Files

- `app/main.py`: Streamlit entry point and overall user flow
- `app/agent.py`: agent-style controller that chooses the next training step
- `app/tools/ingest.py`: handbook ingestion for text and PDF files
- `app/tools/scenarios.py`: policy extraction and scenario generation helpers
- `app/tools/scoring.py`: rubric loading and response scoring
- `app/tools/report.py`: report summarization and JSON persistence
- `app/data/sample_handbook.txt`: default demo handbook
- `app/data/sample_rubric.json`: default scoring rubric
- `docs/InstructionsForDemoUse.txt`: short demo run instructions
- `README.md`: product vision and MVP framing

## Current Behavior

The current implementation is a lightweight agent-style MVP built on heuristic tools.

- The agent presents one scenario at a time and can ask a follow-up before moving on.
- Scenario generation is based on extracted handbook lines and fixed workday prompts.
- Scoring uses phrase matches, simple overlap checks, and explicit bad-action detection.
- Reports are saved as JSON under `app/reports`.
- The learner sees completion feedback, while the manager sees scores, rationale, and citations.

Do not describe the current app as fully AI-powered unless you are clearly separating the intended vision from the implemented MVP.

## Working Style

Prefer small, concrete improvements over architecture churn.

- Preserve Streamlit unless the user explicitly asks to migrate away from it.
- Keep code readable and beginner-friendly.
- Favor incremental changes that support demos, class review, and local execution.
- Add tests when touching logic-heavy code, especially scoring, policy extraction, and reporting.
- Avoid introducing databases, auth, background jobs, or external services unless requested.

## Common Tasks

When asked to improve the project, prioritize these areas:

1. Scoring quality and rubric handling
2. Scenario quality and policy extraction reliability
3. Report clarity for managers
4. Input validation and error handling
5. Test coverage for core modules
6. Streamlit UX polish that does not overcomplicate the app

## Validation

After changes, validate with the lightest relevant check available.

- Run targeted tests if they exist.
- If there are no tests, run the Streamlit app or exercise the touched module directly when practical.
- Call out gaps plainly if validation could not be completed.
