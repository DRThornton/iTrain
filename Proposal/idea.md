# iTrain

## Team Members
- Coby Colaiacovo — ccolaiac@asu.edu
- Alexandra Jacapraro — ajacapra@asu.edu
- Dylan Mocaby — dmocaby@asu.edu
- Larry Smith — lrsmit36@asu.edu
- Dusty Thornton — dthornt6@asu.edu

## Problem Statement

### Who is the user?

**Primary users (buyer/admin):**
- Training managers / Learning & Development (L&D)
- Store or shift managers, supervisors, and team leads
- HR or onboarding coordinators, especially for high-turnover roles

**Secondary users (learner):**
- New hires
- Cross-trainees
- Employees preparing for certification, promotion, or policy refreshers

### What problem or pain point do they experience today?

- Training is passive and not diagnostic. Most training uses videos, slides, and quizzes, which mainly test memorization instead of real judgment.
- Managers cannot easily measure readiness. Supervisors often discover someone is unprepared only after mistakes happen, such as customer escalations, safety incidents, or compliance errors.
- Scenario-based training is expensive to build and maintain. Writing branching scenarios and grading rubrics takes subject matter expert time, and updating scenarios when policies change is difficult.
- Coaching is inconsistent across teams and locations. Different supervisors train differently, which leads to uneven standards and outcomes.
- High turnover makes training efficiency critical. In many frontline jobs, onboarding happens constantly, so organizations need training that scales with minimal manager effort.

## Why Now?

### Why does this problem matter in the next 3–5 years?

- Workforce churn and cross-training are increasing, so companies must onboard employees faster and more reliably.
- Compliance and safety expectations are rising, and documentation and audit trails matter more than before.
- Organizations are shifting toward skills-based performance and want evidence that employees can handle real situations, not just pass multiple-choice quizzes.
- Training budgets are under pressure, so teams need scalable solutions that reduce SME time while improving training quality.

### What changed that makes this possible now?

#### Technology
- Modern LLMs can generate realistic scenarios, understand free-text answers, and score responses against rubrics with explanations.
- Retrieval-Augmented Generation (RAG) makes it possible to ground the trainer in a company handbook or policies, reducing generic advice.
- Multimodal AI makes it possible to incorporate video transcripts and later even images or screenshots of real equipment and workflows.

#### Culture
- Learners increasingly expect interactive, conversational training instead of static LMS content.
- Companies are becoming more open to AI in internal workflows, especially when privacy controls are in place.

#### Regulatory / Risk Climate
- There is increasing emphasis on training evidence and standardization. Transcripts, rubric scores, and policy citations can support audits and internal accountability.

## Proposed AI-Powered Solution

### What does your product do for the user?

**Product concept:**  
A universal “choose-your-own-adventure” job simulator that turns existing training materials into interactive, scored scenario practice.

### Admin / Manager Workflow
1. Upload training content such as handbook PDFs, SOPs, onboarding documents, and optionally video transcript files.
2. Define a simple rubric or choose a template rubric.
3. Assign a training module to employees.
4. Retrieve a manager-only report after completion, including:
   - Per-scenario scores (`good`, `neutral`, `unsafe/incorrect`)
   - Explanation with supporting policy snippet references
   - Patterns such as common mistakes or most-missed policies

### Learner Workflow
1. The learner plays through realistic scenarios.
2. The learner answers in free text: *“What would you do next and why?”*
3. The system does not show pass/fail to the learner. It only states: **“Training complete.”**

### Where does AI/ML add unique value vs simple rules / heuristics?

AI adds unique value because learner responses are open-ended, and rigid rules cannot capture nuance such as correct escalation versus unsafe shortcuts.

AI can:
- Generate scenario variations from the same policy
- Interpret free-text explanations
- Score responses against a rubric with evidence-based rationales
- Personalize follow-up prompts based on what the learner just did through adaptive branching

A rule-based system would require hard-coding large decision trees and exact keywords, which would be costly and brittle.

## Initial Technical Concept

### What data would you need?

**Core data needed:**
- Company training content for the MVP, such as 1–3 sample handbooks or SOPs
- Scenario templates including role, setting, objective, constraints, and escalation rules
- A scoring rubric schema including criteria, weights, unacceptable actions, and “must mention” items
- Learner interaction logs, such as:
  - Scenario text shown
  - Learner response
  - Score and rationale
  - Completion metadata like time and attempt count

**Optional next-stage data:**
- Training videos converted to transcripts using ASR
- Historical incident reports or QA notes for more realistic scenarios, if available

### What model(s) might you use?

A practical stack could include:
- An embedding model for retrieval (RAG) over handbook and SOP chunks
- A GPT-style generative model for:
  - Scenario generation
  - Adaptive branching prompts
  - Rubric-based evaluation explanations
- An optional lightweight classifier for fast `good/neutral/bad` triage before deeper scoring

### How could your nanoGPT work feed into this?

For the course requirement, nanoGPT can contribute in a way that is realistic to build and demonstrate.

#### Option A: Custom Scenario Generator (Most Feasible)
Train or fine-tune nanoGPT on a small dataset of:
- Scenario prompts
- Branching choices
- Ideal response examples

Use nanoGPT to generate draft scenarios in a consistent style.  
Then use a separate evaluation/scoring component, such as rubric + retrieval + LLM-as-judge or rules, to grade learner responses.

#### Option B: Evaluation and Benchmarking
Use nanoGPT experiments to study:
- How training loss and validation loss change with dataset size and context length
- How sampling settings affect scenario quality

Build a small evaluation set with gold scenarios and expected rubric hits, then compare nanoGPT performance against a baseline.

#### Option C: Synthetic Data Generator
Use nanoGPT to generate synthetic scenario-response pairs to help bootstrap scoring rubrics and testing. These would be clearly labeled as synthetic.

## Scope for MVP

### What can you realistically build in ~6 weeks?

A realistic MVP would focus on one job family, text-only interaction, and simple manager reporting.

### Recommended MVP Constraints
- Support one handbook at a time
- Support one module with about 3–5 scenarios
- Use branching depth of 2–3 turns per scenario
- Provide scoring as `good`, `neutral`, or `bad` with a short explanation and cited handbook excerpts

### Concrete v1 Feature Statement
A user can upload a handbook text file and a rubric, then a learner can complete a 5-step branching scenario in the browser with free-text answers, and the system returns:
1. A completion screen to the learner
2. A manager-only report containing scores, rationales, and handbook citations

### Suggested Implementation Format
- A Streamlit or Gradio web app
- Reports stored as JSON with a downloadable PDF or text summary

## Risks and Open Questions

### 1. Scoring Validity and Consistency
- Will the system score the same answer consistently?
- Can managers trust the rubric mapping, especially for safety or compliance?
- Risk: if managers feel the model judged answers incorrectly, adoption may drop.

### 2. Hallucinations or Incorrect Policy Grounding
- Risk: the scenario or feedback may invent rules not actually in the handbook.
- The system will need strong grounding through retrieval citations and guardrails such as: *“If not found in policy, say insufficient evidence.”*

### 3. User Adoption and Workflow Fit
- Managers are busy, so if setup is difficult, they may not use it.
- Learners may dislike long free-text input unless the experience is smooth.
- The product may eventually need to integrate with existing LMS workflows.

**Other notable risks:**
- Privacy and IP concerns
- Prompt injection or gaming the system
- Content updates and versioning
- Bias and fairness

## Planned Data Sources

For a course MVP, where real company data may not be available, the project can use the following:

### Synthetic Data
- Create a small sample handbook for a fictional company, such as one focused on retail safety and customer service
- Generate scenarios and responses for testing and demos
- Clearly label all synthetic content

### Public Text Sources
- Public safety guidelines
- Workplace posters
- Standard operating procedures published online by agencies or organizations
- Publicly shared employee handbook templates, if licensing allows

### Kaggle / Hugging Face Datasets
- Customer support conversation datasets for dialogue realism
- QA or instruction datasets for response-style variety
- Summarization datasets if building handbook-to-policy-bullet preprocessing

### Optional Public APIs
None are required for version 1, but later versions could add integrations such as:
- LMS export
- HRIS systems
