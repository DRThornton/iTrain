# Phase 2 MVP Progress Report

## Objective and Current MVP Definition

Our project, **iTrain**, is an AI-assisted job training simulator that converts handbook-style policy documents into interactive scenario practice for learners and a manager-only performance report for supervisors.

For Phase 2, our concrete MVP target is:

- Accept a handbook as `.txt` or `.pdf`
- Extract actionable policy statements from that handbook
- Turn those policies into realistic text-based workplace scenarios
- Let a learner answer in free text through a browser interface
- Score each response against policy/rubric signals
- Ask a follow-up question when the learner's answer is incomplete
- Generate a manager-only JSON report with per-scenario results, rationale, and handbook citations

This MVP is intentionally narrow. It currently supports a single uploaded handbook at a time, a fixed sample rubric, and a lightweight evaluation workflow designed for a reproducible class demo.

## Main Technical Risks and Bottlenecks

The biggest technical risk is **scoring validity**. A general-purpose AI system can produce plausible training feedback, but for this product the feedback must stay grounded in the uploaded handbook and must not reward vague or unsafe answers.

Our main open bottlenecks are:

- Policy extraction from messy handbook PDFs is still heuristic and may miss or mis-rank some useful rules
- Scoring is currently keyword- and overlap-based, so it can miss nuance in learner responses
- The rubric is static and not yet customized per uploaded handbook
- We do not yet have a formal benchmark comparing raw general-purpose AI behavior against our current workflow on a shared evaluation set

## What Has Been Built So Far

We now have a working end-to-end prototype in Streamlit.

### Implemented Components

- **Handbook ingestion**
  - Accepts `.txt` and `.pdf` uploads
  - Extracts PDF text using `pypdf`
- **Policy extraction**
  - Cleans handbook text
  - Removes common PDF/admin noise
  - Detects headings and actionable policy lines
  - Prioritizes scenario-worthy rules such as safety, reporting, equipment, and sanitation
- **Scenario generation**
  - Builds initial scenario prompts from extracted policies
  - Uses category-aware prompting to turn rules into workplace situations
- **Agent-style workflow**
  - Tracks learner progress across turns
  - Detects weak categories
  - Generates follow-up prompts when the first answer is incomplete or not policy-specific
- **Scoring**
  - Uses a rubric with required concepts and unsafe actions
  - Produces `good`, `neutral`, or `bad` labels
  - Returns a short rationale plus the cited policy text
- **Manager reporting**
  - Aggregates results
  - Computes a weighted score and recommendation
  - Saves a report as JSON in `app/reports/`
- **Demo UI**
  - Learner view for answering scenarios
  - Manager view for inspecting the final report

## Technical Approach

This project is an **agent / AI workflow design** project rather than a trained predictive model.

### Baseline Behavior of a Raw General-Purpose AI System

A strong general-purpose AI can already:

- Answer open-ended safety or policy questions in natural language
- Generate realistic workplace scenarios
- Give plausible coaching-style feedback

However, a raw general-purpose AI is not sufficient for this task by itself because it does not automatically:

- Stay constrained to the uploaded handbook
- Select the best policy lines from noisy handbook text
- Maintain a structured learner session and follow-up flow
- Produce a consistent manager-facing report artifact
- Separate the learner experience from the manager evaluation flow

### Missing Capabilities Addressed by Our Workflow

We addressed those gaps through several targeted interventions:

- **Context engineering**
  - We convert long handbook text into cleaned candidate lines and section blocks before using it
- **Task-specific workflow design**
  - The system does not ask a generic question each turn; it selects scenario prompts from extracted policies
- **Rule-guided evaluation**
  - The scoring step uses rubric signals and unsafe-action detection instead of unconstrained free-form feedback
- **Memory/state**
  - The learner session tracks history, weak categories, current turn, and completion state
- **Specialized follow-up logic**
  - If the answer is incomplete, the system asks for policy-specific clarification before moving on
- **Structured reporting**
  - Results are transformed into a manager-only report with summary counts, recommendation, and citations

The key technical idea of the project is that instead of relying on one generic AI answer, we build a narrow workflow around ingestion, scenario generation, evaluation, and reporting.

## Evidence of Progress

We have meaningful working code and reproducible project structure in the repository.

### Working Code and Demo Evidence

Current prototype files include:

- `app/main.py` for the Streamlit demo interface
- `app/agent.py` for the session controller
- `app/tools/ingest.py` for handbook loading
- `app/tools/scenarios.py` for policy extraction and scenario creation
- `app/tools/scoring.py` for rubric-based scoring
- `app/tools/report.py` for manager report generation

### Demonstrated Output

The repository already includes a generated sample report:

- `app/reports/Demo_User_report.json`

That report shows an example completed learner session with:

- 8 evaluated turns total
- 4 `good`, 4 `neutral`, 0 `bad`
- weighted score of `8`
- recommendation of `pass`

The sample output also shows that the system is already producing:

- scenario prompts derived from handbook policies
- follow-up questions when answers need more policy detail
- score labels with rationales
- direct policy citations in the report

### Testing Progress

We also added automated tests for core logic, including:

- policy extraction from handbook text
- rejection of noisy PDF fragments
- scenario prompt construction
- follow-up generation
- report recommendation logic
- scoring behavior around unsafe actions and ambiguous `guess` language

This gives us evidence that the core workflow is not just a one-off manual demo.

## Iterations and What We Learned from Failures

A major lesson from Phase 2 was that **raw handbook text is messy** and cannot be used directly.

Our early failure mode was that handbook or PDF text included headings, fragments, administrative rules, or broken line wraps that made poor scenarios. We responded by adding:

- noise filtering
- section-based grouping
- heading detection
- merging of continuation lines
- scenario-worthiness scoring to down-rank non-actionable rules

A second lesson was that **single-pass scoring is too brittle**. Learners sometimes give a partially correct answer that is not clearly unsafe, but also not specific enough. Instead of ending the scenario immediately, we added a follow-up question mechanism to ask for more detail tied to the cited policy.

A third lesson was that **report structure matters**. A training tool is not useful unless supervisors can inspect what happened after the learner finishes. That led us to add a manager-only report summary with recommendations and focus areas.

## Before/After Evidence

### Before Intervention

Without our workflow, a general-purpose AI baseline would likely:

- answer questions in a plausible but generic way
- fail to preserve a structured learner session
- provide advice that is not tightly tied to the uploaded handbook
- give inconsistent manager-facing outputs across runs

### After Intervention

With our current workflow, the system now:

- extracts policy candidates from uploaded training content
- generates scenario prompts from those policies
- requests follow-up clarification when answers are weak
- stores structured per-turn evidence
- outputs a reusable manager report with citations and recommendation

This is meaningful progress toward the MVP because the core training loop now exists end-to-end.

## Current Limitations and Open Risks

The system is functional, but it is still an MVP prototype.

Current limitations include:

- scoring is heuristic rather than semantic
- rubric phrases are static and not yet generated from each uploaded handbook
- no quantitative benchmark set yet for measuring improvement against a raw AI baseline
- no persistence layer beyond saved JSON report files
- no authentication or true manager/learner access separation
- no downloadable PDF summary yet
- limited UI polish and no production deployment workflow

There is also a reproducibility gap in the current repo setup: dependencies are listed, but the full local test environment is not yet fully documented or packaged for one-command verification.

## Plan for Phase 3

Before the final MVP submission, we plan to focus on four areas.

### 1. Improve Evaluation Quality

- strengthen rubric-to-policy matching
- add a small benchmark set of expected answers and failure cases
- compare baseline vs improved workflow on the same scenarios

### 2. Improve Product Completeness

- allow easier handbook/rubric setup
- expand manager reporting and summary outputs
- improve demo flow and instructions for class reproducibility

### 3. Improve Technical Depth

- make scenario selection and scoring more robust
- add better evidence logging for experiments
- explore whether a stronger retrieval or LLM-backed scoring layer improves consistency while preserving policy grounding

### 4. Improve Deployment and Update Workflow

- create a simple launcher for non-technical users
- add a one-click way to start the Streamlit app
- explore an update utility that can pull the latest code from the team GitHub repository
- improve ease of classroom demos and teammate onboarding by reducing setup friction

## Conclusion

By Phase 2, we have built a working prototype that demonstrates real progress toward the original iTrain MVP. The system can ingest handbook content, generate policy-based scenarios, evaluate learner responses, issue follow-up prompts, and produce a structured manager report.

The prototype is not yet a fully validated training product, but it already demonstrates the central technical claim of the project: a targeted AI workflow can turn static handbook material into interactive, evidence-based scenario training in a way that a raw general-purpose AI system does not provide on its own.
