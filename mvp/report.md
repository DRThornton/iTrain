# iTrain MVP Report

**Course:** MAE 301  
**Project:** iTrain  
**Team Members:**  
- Coby Colaiacovo, ccolaiac@asu.edu  
- Alexandra Jacapraro, ajacapra@asu.edu  
- Dylan Mocaby, dmocaby@asu.edu  
- Larry Smith, lrsmit36@asu.edu  
- Dusty Thornton, dthornt6@asu.edu  

---

## 1. Executive Summary

iTrain is an AI-assisted job training simulator that turns workplace handbooks and policy documents into interactive training scenarios. Many companies still train employees with slides, videos, handbooks, and short quizzes. Those methods can show whether someone remembers information, but they do not always show whether the employee can make the right decision in a real workplace situation.

Our MVP lets a manager upload a handbook or policy document. The system extracts important policies, turns them into scenario-based questions, lets a learner answer in free text, and then evaluates the learner’s response based on policy and rubric signals.

At the end of the training, the learner only sees that the training is complete. The manager receives a structured report with scores, rationales, policy citations, a weighted score, and a recommendation. This gives supervisors a better way to understand whether someone is actually ready instead of only knowing that they finished a training module.

---

## 2. User and Use Case

The primary users for iTrain are training managers, HR onboarding coordinators, store managers, shift leads, and supervisors. These are the people responsible for making sure employees understand workplace policies and can apply them correctly.

The secondary users are learners, such as new hires, cross-trained employees, or employees completing a refresher module. This type of product is especially useful for high-turnover jobs because managers often have to train new employees quickly and consistently.

A typical use case would look like this:

A store manager uploads a workplace safety or customer service handbook into iTrain. The system reads the document, extracts important policy statements, and creates realistic training scenarios from those policies. A new employee opens the training module in the browser and responds to each scenario in free text. If the employee gives a vague or incomplete answer, the system asks a follow-up question. After the learner finishes, the manager can review a report showing how the learner performed, which policies they understood, and where they may need more coaching.

This is useful because managers do not just need to know that an employee clicked through training. They need to know whether the employee can apply the right policy when a real problem happens.

---

## 3. System Design

The MVP is built as a Streamlit web app. The system follows a structured workflow from uploaded training content to learner practice to manager reporting. The project is best described as an AI workflow system rather than a single trained machine learning model.

### High-Level Architecture

Handbook Upload  
↓  
Text Extraction and Cleaning  
↓  
Policy Extraction  
↓  
Scenario Generation  
↓  
Learner Free-Text Response  
↓  
Scoring and Follow-Up Logic  
↓  
Manager Report  

### Main System Components

#### Handbook Ingestion

The user can upload a `.txt` or `.pdf` handbook. PDF text is extracted using `pypdf`. The system then cleans the extracted text so it is easier to use. This matters because raw PDF text can include broken lines, headings, page numbers, and formatting issues that make scenario generation harder.

#### Policy Extraction

After the handbook is cleaned, the system identifies actionable policy statements. These are rules that could become useful training scenarios, especially policies related to safety, reporting, equipment, sanitation, customer service, and escalation procedures.

#### Scenario Generation

The system turns selected policy statements into realistic workplace scenarios. The goal is not just to repeat the policy, but to place the learner in a situation where they have to decide what to do.

#### Learner Interaction

The learner answers each scenario in free text. This is important because real workplace decisions are usually not simple multiple-choice questions. The system tracks the learner’s progress across turns and can ask a follow-up question if the first answer is incomplete or not specific enough.

#### Scoring

The scoring system labels responses as good, neutral, or bad. It uses rubric signals, required concepts, unsafe action detection, and overlap with the cited policy text. The system also gives a short rationale explaining why the response received that score.

#### Manager Report

After the learner finishes, the system generates a manager-only JSON report. The report includes scenario results, score labels, rationales, cited policy text, a weighted score, and a final recommendation.

---

## 4. Data

The main data source for iTrain is handbook-style training content. For the class MVP, the project uses sample or synthetic handbook material instead of private company documents. This was the safest and most realistic choice for a course project because real company training documents could include private policies, internal procedures, or employee-related information.

The MVP supports:

- `.txt` handbook files
- `.pdf` handbook files
- extracted policy lines
- scenario prompts based on those policies
- learner response logs
- generated JSON manager reports

The data pipeline is:

1. Upload a handbook
2. Extract raw text
3. Clean formatting and remove noise
4. Identify useful policy statements
5. Convert policies into scenarios
6. Record learner responses
7. Score responses and save report data

Since this is an AI workflow project, there is no traditional train, validation, and test split. We are not training a large supervised model from scratch. Instead, the system uses uploaded handbook content, policy extraction, scenario generation, rubric-based scoring, and reporting logic.

The biggest data limitation is that the sample data is small and controlled. This helps with building a reliable demo, but it does not fully prove how the system would perform on long, messy, real-world company handbooks. A future version would need to test more handbook types, industries, and policy formats.

---

## 5. Models and Technical Approach

iTrain uses an agent-style workflow instead of relying on one single model response. A general-purpose AI system can already generate scenarios or give training advice, but that is not enough for this product. A raw AI response does not automatically stay grounded in the uploaded handbook, maintain a learner session, ask structured follow-up questions, or produce a consistent manager-facing report.

Our workflow adds structure around the task.

### Policy-Based Scenario Generation

The system selects important policy lines from the uploaded handbook and turns them into scenario prompts. This keeps the training tied to the actual handbook instead of producing generic workplace advice.

### Rule-Guided Scoring

The MVP uses a rubric-based scoring layer. It looks for required concepts, weak or vague answers, unsafe actions, and overlap with the cited policy. This makes the scoring more consistent than simply asking a general AI model to judge the response with no structure.

### Follow-Up Logic

If a learner gives an incomplete answer, the system can ask for more detail instead of immediately moving on. This makes the training feel more like coaching and gives the learner a chance to explain their reasoning more clearly.

### State Tracking

The system tracks the current scenario, learner responses, score labels, rationales, weak areas, and completion status. This allows the app to produce a complete manager report at the end instead of treating every answer as a separate one-time interaction.

### Reporting Layer

The system saves the results into a structured JSON report. This report is important because managers need something they can review after the learner finishes. The report gives them a summary of performance, not just individual answers.

Overall, the technical focus of the project is not training a brand-new model. The main technical contribution is building a narrow AI workflow around handbook ingestion, scenario generation, learner interaction, response evaluation, follow-up logic, and manager reporting.

---

## 6. Evaluation

The MVP was evaluated through sample training sessions and automated tests for the core logic. The main goal was to check whether the system could complete the full workflow from handbook upload to manager report.

The Phase 2 prototype already produced a sample report with 8 evaluated turns, including 4 good responses, 4 neutral responses, 0 bad responses, a weighted score of 8, and a final recommendation of pass.

### Evaluation Flow

A sample learner session follows this process:

1. The system presents a scenario based on a handbook policy.
2. The learner types what they would do.
3. The system evaluates whether the answer includes the required policy concepts.
4. If the response is incomplete, the system asks a follow-up question.
5. The final score, rationale, and citation are saved into the manager report.

### Example 1: Incomplete Safety Response

**Scenario:**  
A learner is placed in a workplace safety situation based on a handbook policy.

**Learner Response:**  
“I would fix the issue and keep working.”

**System Result:**  
Neutral

**Reasoning:**  
The answer shows that the learner wants to take action, but it does not clearly mention reporting the hazard, notifying a supervisor, documenting the issue, or following the required safety procedure.

**Why this matters:**  
This is a good example of why free-text training can be more useful than a basic quiz. The response is not completely wrong, but it is also not strong enough for a real workplace safety situation.

### Example 2: Strong Escalation Response

**Scenario:**  
A learner is placed in a situation where they need to respond to a customer or workplace issue.

**Learner Response:**  
“I would notify my supervisor, document what happened, and follow the company policy before taking further action.”

**System Result:**  
Good

**Reasoning:**  
The answer includes escalation, documentation, and awareness of company policy.

**Why this matters:**  
The system can recognize when the learner gives a more complete response that matches the expected workplace process.

### What Worked Well

The MVP successfully showed that the system can:

- accept uploaded handbook content
- extract useful policy information
- generate scenario-based training prompts
- collect free-text learner responses
- ask follow-up questions
- score responses as good, neutral, or bad
- produce a manager report with rationales and citations

The strongest part of the MVP is that the full end-to-end workflow works. It is not just a chatbot giving advice. It has a specific training structure and produces a useful manager-facing output.

### What Needs Improvement

The biggest weakness is that the scoring is still mostly heuristic. It can catch clear good, neutral, or unsafe responses, but it may miss more nuanced answers. For example, a learner could give a correct answer using different wording, and the system may not fully recognize it. A future version would need stronger semantic scoring and a larger benchmark set to test scoring consistency.

---

## 7. Limitations and Risks

The current MVP works as a prototype, but there are several important limitations.

### Scoring Accuracy

The system uses rubric and keyword-style signals, so it may not always understand nuanced answers. This is one of the biggest limitations because training evaluations should be fair, consistent, and reliable.

### Small Dataset

The project uses sample or synthetic handbook data. This makes the demo easier to control, but real company handbooks are usually longer, messier, and more specific.

### Policy Extraction Issues

PDFs can be difficult to process. The system may miss important policies or select weak policy lines that do not make strong scenarios.

### Static Rubric

The rubric is not fully customized for every uploaded handbook yet. This limits how specific the evaluation can be for different companies or roles.

### No Production-Level Authentication

The MVP separates learner and manager views conceptually, but it does not include real login, permissions, or privacy controls.

### Hallucination Risk

Any AI-generated scenario or explanation could include unsupported details if the system is not properly grounded in the handbook. This is why policy citations and handbook-based scoring are important.

### Privacy Risk

If this product were used by a real company, it would need stronger protections for company documents, learner responses, and performance reports.

---

## 8. Next Steps

With 2 to 3 more months, the next version of iTrain would focus on making the system more accurate, easier to use, and more realistic for companies.

### Improve Scoring

The biggest next step would be improving the evaluation system. We would add stronger semantic scoring so the system can understand correct answers even when learners use different wording. We would also build a benchmark set with example good, neutral, and bad answers to measure performance more formally.

### Add Better Retrieval

A stronger retrieval system would help the app pull the most relevant handbook sections for each scenario. This would improve citations and reduce generic or unsupported feedback.

### Generate Custom Rubrics

Instead of using a static rubric, the system should generate or suggest rubric criteria based on the uploaded handbook. Managers could review and edit the rubric before assigning the training.

### Improve the Manager Dashboard

The current JSON report proves the reporting concept, but managers would benefit from a cleaner dashboard. A future version could show common mistakes, weak policy areas, pass/fail trends, and recommended coaching actions.

### Improve the Learner Experience

The learner side should feel smoother and more realistic. This could include clearer instructions, better scenario pacing, and more natural follow-up questions.

### Deploy the App

The MVP currently works as a local Streamlit prototype. A future version should be deployed so managers and learners can access it through a web link without setting up code locally.

---

## 9. Conclusion

iTrain shows how AI can make workplace training more interactive and more useful. Instead of relying only on static handbooks and basic quizzes, the system turns policy documents into realistic practice scenarios. Learners get a chance to explain what they would actually do, and managers get a report that shows how ready the learner is.

The MVP is not a finished commercial product, but it proves the core idea. A handbook can be uploaded, policies can be extracted, scenarios can be generated, learner answers can be scored, and a manager report can be created. The biggest improvements needed are better scoring, stronger retrieval, and more real-world testing. Still, the project shows a clear path toward a training tool that could help companies onboard employees faster, coach workers more consistently, and better understand whether employees are ready for real workplace situations.