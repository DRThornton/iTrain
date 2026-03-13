1. Project Title
	iTrain

2. Team Members (names, emails)
	Coby Colaiacovo <ccolaiac@asu.edu>,
Alexandra Jacapraro <ajacapra@asu.edu>,
Dylan Mocaby <dmocaby@asu.edu>,
Larry Smith <lrsmit36@asu.edu>,
Dusty Thornton <dthornt6@asu.edu>

3. Problem Statement
Who is the user?
Primary user (buyer/admin):
Training managers / Learning & Development (L&D)


Store/shift managers, supervisors, team leads


HR / onboarding coordinators (especially for high-turnover roles)


Secondary user (learner):
New hires, cross-trainees, and employees preparing for certification, promotion, or policy refreshers.


What problem or pain point do they experience today?
Training is passive and not diagnostic. Most training is videos, slides, quizzes → it checks memorization, not real judgment.


Managers can’t easily measure readiness. Supervisors often only find out someone is unprepared after mistakes happen (customer escalations, safety incidents, compliance errors).


Scenario-based training is expensive to build and maintain. Writing branching scenarios and grading rubrics takes SMEs time; updating scenarios when policies change is painful.


Inconsistent coaching across locations/teams. Different supervisors train differently → uneven standards and outcomes.


High turnover makes training efficiency critical. In many frontline jobs, onboarding repeats constantly; organizations need training that scales with minimal manager effort.



4. Why Now?
Why does this problem matter in the next 3–5 years?
Workforce churn and cross-training are increasing → companies must onboard faster and more reliably.


Compliance and safety expectations are rising (and documentation/audit trails matter more).


Organizations are shifting toward skills-based performance: they want evidence someone can handle real situations, not just pass a multiple-choice quiz.


Training budgets are pressured → teams need scalable solutions that reduce SME time while improving training quality.


What changed that makes this possible now?
Technology
Modern LLMs can generate realistic scenarios, understand free-text answers, and score them against rubrics with explanations.


Retrieval-Augmented Generation (RAG) enables grounding the trainer in a company’s handbook/policies (reducing “generic advice”).


Multimodal AI makes it feasible to incorporate video transcripts (and later, images/screenshots of real equipment or workflows).


Culture
Learners increasingly expect interactive, conversational training, especially compared to static LMS content.


Companies are more open to AI in internal workflows, as long as privacy controls exist.


Regulatory / risk climate
More emphasis on training evidence and standardization: transcripts + rubric scores + policy citations become valuable for audits and internal accountability.



5. Proposed AI-Powered Solution
What does your product do for the user?
Product concept: a universal “choose-your-own-adventure” job simulator that turns existing training materials into interactive, scored scenario practice.
Admin/Manager workflow
Upload training content (handbook PDFs, SOPs, onboarding docs, optionally video transcript files).


Define a simple rubric (or pick a template rubric).


Assign a training module to employees.


Retrieve a manager-only report after completion:


per-scenario scores (good / neutral / unsafe/incorrect)


explanation + supporting policy snippet references


patterns (common mistakes, most-missed policy)


Learner workflow
The learner plays through realistic scenarios.


They answer in free text: “What would you do next and why?”


The system does not display pass/fail; it only states “Training complete.”


Where does AI/ML add unique value vs simple rules / heuristics?
AI adds unique value because:
Learner responses are open-ended → rigid rules won’t capture nuance (e.g., correct escalation vs unsafe shortcuts).


AI can:


generate scenario variations from the same policy (“same concept, different situation”)


interpret free-text explanations


score against a rubric with evidence-based rationales


personalize follow-up prompts based on what the learner just did (adaptive branching)


A rule-based system would require hard-coding huge decision trees and exact keywords—costly and brittle.

6. Initial Technical Concept
What data would you need (or already have)?
You need:
Company training content (for the MVP: 1–3 sample handbooks/SOPs)


Scenario templates (structure: role, setting, objective, constraints, escalation rules)


A scoring rubric schema (criteria, weights, unacceptable actions, “must mention” items)


Learner interaction logs:


scenario text shown


learner response


score + rationale


completion metadata (time, attempt count)


Optional/next stage data
Training videos → transcripts via automatic speech recognition (ASR)


Historical incident reports or QA notes (for more realistic scenarios), if available.


What model(s) might you use?
A practical stack:
Embedding model for retrieval (RAG) over handbook + SOP chunks.


GPT-style generative model for:


scenario generation


adaptive branching prompts


rubric-based evaluation explanations


Optional classifier (lightweight) for fast “good/neutral/bad” triage before deeper scoring.


How could your nanoGPT work feed into this?
For the course requirement, nanoGPT can contribute in a way you can actually build and demonstrate:
Option A (most feasible for a 6-week MVP): Custom scenario generator
Train/fine-tune nanoGPT on a small dataset of:


scenario prompts


branching choices


“ideal response” examples


Use nanoGPT to generate draft scenarios in a consistent style.


Then use a separate evaluation/scoring component (rubric + retrieval + LLM-as-judge or rules) to grade learner responses.


Option B: Evaluation & benchmarking
Use nanoGPT experiments to learn:


how training loss/validation loss changes with dataset size/context length


how sampling settings affect scenario quality


Build a simple evaluation set (“gold” scenarios + expected rubric hits) and report nanoGPT performance vs a baseline.


Option C: Synthetic data generator
Use nanoGPT to generate synthetic scenario-response pairs to bootstrap scoring rubrics/testing (clearly labeled as synthetic).



7. Scope for MVP
What can you realistically build in ~6 weeks?
A realistic MVP is one job family, text-only, with simple manager reporting.
Recommended MVP constraints:
Support one handbook at a time (TXT/PDF-to-text)


Support one module with ~3–5 scenarios


Branching depth: 2–3 turns per scenario


Scoring: good/neutral/bad + short explanation + cited handbook excerpts


Very concrete v1 feature statement
“A user can upload a handbook text file and a rubric, then a learner can complete a 5-step branching scenario in the browser with free-text answers, and our system returns (1) a completion screen to the learner and (2) a manager-only report containing scores, rationales, and handbook citations.”
Implementation format that plays well in class:
A Streamlit or Gradio web app


Reports stored as JSON + downloadable PDF/text summary



8. Risks and Open Questions (Top 3)
Scoring validity / consistency


Will the system score the same answer consistently?


Can managers trust the rubric mapping (especially for safety/compliance)?


Risk: “model judged it wrong” → reduces adoption.


Hallucinations / incorrect policy grounding


Risk: scenario or feedback invents rules not in the handbook.


Need strong grounding (retrieval citations) and guardrails (“if not found in policy, say insufficient evidence”).


User adoption + workflow fit


Managers are busy; if setup is hard, they won’t use it.


Learners may dislike long free-text input unless the experience is smooth.


Needs to integrate with existing LMS workflows eventually.


(Other notable risks you can mention if you want a longer list: privacy/IP concerns, prompt injection/gaming, content update/versioning, bias/fairness.)

9. Planned Data Sources
For a course MVP (where real company data may not be available), you can use:
Synthetic data (you create)


Write a small “sample handbook” for a pretend company (retail safety + customer service).


Generate scenarios/responses for testing and demos (clearly labeled synthetic).


Public text sources (handbook-like content)


Public safety guidelines, workplace posters, standard operating procedures posted online by agencies/organizations.


Publicly shared employee handbook templates (if license allows).


Kaggle / Hugging Face Datasets (for language/examples)


Customer support conversation datasets (for dialogue realism)


QA/Instruction datasets (for response-style variety)


Summarization datasets (if you build “handbook → policy bullets” preprocessing)


Optional public APIs


None required for v1, but later you could add integrations (LMS export, HRIS, etc.).

