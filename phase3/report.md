# Phase 3 MVP Report: iTrain

## 1. Executive Summary

iTrain is an AI-assisted job training simulator for turning static workplace handbooks, safety manuals, and procedure documents into interactive scenario practice. The problem is that many organizations already have policies and manuals, but employees often receive them as passive reading material. Managers also have limited evidence of whether a learner can apply the policy in a realistic situation.

The MVP solves that by creating a narrow training workflow around a single uploaded handbook. A supervisor or instructor loads a `.txt` or `.pdf` document, the system extracts actionable policy statements, turns those policies into workplace scenarios, asks the learner for free-text responses, scores those responses against policy/rubric signals, asks follow-up questions when answers are incomplete, and produces a manager-facing report with citations.

The current MVP actually does the following:

- Runs as a Streamlit browser app.
- Accepts uploaded `.txt` and `.pdf` training documents.
- Includes a bundled sample handbook for demo mode.
- Detects whether the document is more like a safety handbook or procedural manual.
- Extracts and ranks scenario-worthy rules from handbook text.
- Generates up to five primary training questions.
- Scores learner answers as `good`, `neutral`, or `bad`.
- Triggers follow-up questions for non-good first answers.
- Saves a structured manager report as JSON and Markdown in `app/reports/`.

This is not a production learning management system yet. It is a working MVP that demonstrates the core product idea end to end: handbook content can be transformed into scenario-based training evidence instead of remaining a static document.

## 2. User & Use Case

The primary learner persona is a frontline employee, new hire, trainee, or cross-trained worker who needs to understand workplace rules well enough to act correctly on the job. The learner may not need a long lecture; they need practice deciding what to do when something goes wrong or when a documented procedure must be followed carefully.

The manager persona is a supervisor, trainer, safety lead, or instructor who needs quick evidence of whether a learner can apply the handbook. The manager is not only looking for completion. They need to know whether the learner reports hazards, avoids guessing, follows procedure, and knows when to escalate.

A typical use case looks like this:

1. A supervisor opens iTrain and uploads a safety handbook, customer-service policy, or procedure manual.
2. iTrain extracts actionable rules and builds short workplace scenarios.
3. The learner answers each scenario in their own words.
4. If the answer is unsafe or vague, iTrain asks one follow-up question tied to the same policy.
5. When the session finishes, the manager reviews a summary report showing scores, focus areas, learner responses, rationales, and handbook citations.

This use case is useful for classroom demos, onboarding practice, safety refreshers, and early validation of whether a handbook can become an interactive training module.

## 3. System Design

High-level architecture:

```text
                  +-----------------------------+
                  | Uploaded .txt/.pdf handbook |
                  | or bundled sample handbook  |
                  +-------------+---------------+
                                |
                                v
                  +-----------------------------+
                  | app/tools/ingest.py         |
                  | - load text files           |
                  | - extract PDF text via pypdf|
                  +-------------+---------------+
                                |
                                v
                  +-----------------------------+
                  | app/tools/scenarios.py      |
                  | - clean noisy lines         |
                  | - detect document type      |
                  | - extract policy candidates |
                  | - rank scenario-worthy text |
                  | - build scenario prompts    |
                  +-------------+---------------+
                                |
                                v
                  +-----------------------------+
                  | app/agent.py                |
                  | TrainingAgent session state |
                  | - current scenario          |
                  | - queue                     |
                  | - weak categories           |
                  | - follow-up control         |
                  +------+------+---------------+
                         |     ^
                         v     |
                  +-----------------------------+
                  | Learner free-text response  |
                  +-------------+---------------+
                                |
                                v
                  +-----------------------------+
                  | app/tools/scoring.py        |
                  | - rubric signals            |
                  | - unsafe action detection   |
                  | - policy overlap checks     |
                  | - good/neutral/bad label    |
                  +-------------+---------------+
                                |
                      non-good? | yes
                                v
                  +-----------------------------+
                  | Follow-up scenario builder  |
                  +-------------+---------------+
                                |
                         complete session
                                |
                                v
                  +-----------------------------+
                  | app/tools/report.py         |
                  | - manager JSON report       |
                  | - manager Markdown summary  |
                  +-------------+---------------+
                                |
                                v
                  +-----------------------------+
                  | Streamlit Manager View      |
                  +-----------------------------+
```

The model-like logic currently sits in three places:

- `app/tools/scenarios.py` acts as the document understanding and scenario generation layer.
- `app/tools/scoring.py` acts as the answer evaluation layer.
- `app/agent.py` acts as the workflow controller that decides whether to continue, ask a follow-up, or generate the final report.

Data flows from the uploaded handbook into cleaned policy candidates, then into scenario prompts, then into scored learner turns, and finally into a manager report. The system keeps the learner and manager experiences separate in the UI, but it does not yet implement authentication or true access control.

## 4. Data

The MVP uses three kinds of data.

First, it uses runtime handbook data. A user can upload one `.txt` or `.pdf` handbook at a time. Text files are read directly. PDF files are converted to text with `pypdf`. The bundled sample handbook is `app/data/sample_handbook.txt`, a small 584-byte demo file containing seven retail safety and customer-service policies.

Second, it uses a static sample rubric in `app/data/sample_rubric.json`. The rubric contains required concepts such as reporting to a supervisor, asking a manager, customer safety, cleaning spills, blocking the area, and following emergency procedures. It also contains bad-action phrases such as ignoring, guessing, leaving a hazard, walking away, and doing nothing.

Third, the repository includes supporting manuals in `docs/`. These documents were used for manual testing and development. The folder contains OSHA PDFs, a construction safety manual, a Johnson Controls thermostat manual, a food equipment owner manual, and demo-use notes. Together, the `docs/` files total about 31.0 MB.

Cleaning and preparation are handled in code instead of through a separate training pipeline:

- Lines are stripped and normalized.
- Blank lines, page numbers, URLs, table-of-contents fragments, dates, and other PDF noise are filtered out.
- Headings are detected so lines can be grouped into section blocks.
- Broken or incomplete manual fragments are rejected.
- Safety and procedural-manual documents are classified differently.
- Candidate policy lines are ranked by scenario-worthiness.
- Prompts are de-duplicated so the first five scenarios do not all ask the same kind of question.

There is no supervised train/validation/test split because the current MVP does not train a machine learning model. Instead, evaluation uses unit tests plus a small benchmark file, `app/data/benchmark_cases.json`, with 11 cases covering scoring behavior, document-type detection, and policy-line acceptance/rejection.

## 5. Models

The current MVP is best described as an agent workflow and rule-guided AI system, not as a trained neural model. It does not currently call an external frontier model API at runtime, and it does not include a fine-tuned model, nanoGPT variant, or supervised classifier.

The decision to avoid an external model in this MVP was intentional. The project goal for this phase was to prove the workflow: convert handbook text into structured practice, maintain a learner session, evaluate answers consistently, trigger follow-ups, and produce manager evidence. A deterministic workflow is easier to demo, test, and debug for a class MVP.

The main model-like components are:

- Document type detection: pattern-based classification into `safety_handbook` or `procedural_manual`.
- Policy extraction: heuristic filtering, section grouping, policy-signal detection, and scenario-worthiness ranking.
- Scenario generation: template and rule-based prompt construction grounded in the extracted policy.
- Response scoring: rubric phrase matching, unsafe-action detection, policy overlap, manual-step checks, and copy-paste/parroting detection.
- Agent workflow: session state that controls current prompt, queue, weak categories, follow-ups, and report generation.

Prompting and workflow design matter even without an LLM. The system constrains each scenario to a cited policy, asks follow-ups only when the first answer is not `good`, and stores the evidence needed for a manager report. In a future version, this workflow could sit on top of a frontier LLM or retrieval-augmented model, but the MVP keeps the control logic explicit.

## 6. Evaluation

The current evaluation combines automated tests, a benchmark set, and qualitative review of generated reports.

Quantitative results from the current repo:

- `py -m app.tools.benchmark`: 11/11 benchmark cases passed.
- Benchmark breakdown: scoring 7/7, document type detection 2/2, policy-line classification 2/2.
- `py -m pytest tests`: 102/102 tests passed with one cache warning.
- A full unscoped `py -m pytest` currently fails during collection because pytest tries to enter generated `pytest-cache-files-*` folders in the repository root and hits Windows permission errors. Running the actual `tests` folder succeeds.

The tests cover the main MVP behaviors:

- Agent session progression and follow-up behavior.
- Safety-handbook and procedural-manual scenario extraction.
- Manual-step prompt generation.
- Policy noise filtering.
- Good, neutral, and bad scoring outcomes.
- Unsafe action detection.
- Manager report generation and Markdown rendering.
- Benchmark summary formatting.

Qualitatively, the sample report in `app/reports/Demo_User_report.json` shows a complete learner session using the bundled handbook. It contains five primary questions and five follow-ups. The report summary shows 5 good, 1 neutral, and 4 bad scored turns, with a weighted score of -2 and a `fail` recommendation. This is useful evidence because it shows the system can identify unsafe first answers, ask targeted follow-ups, and record when the learner improves their answer.

One important error-analysis example is the sample answer "I would run away" for an upset customer scenario. The current scorer labels that as `neutral`, not `bad`, because it is not in the explicit unsafe-action list and does not directly contradict the policy. That is a helpful limitation to surface: the MVP catches many obvious unsafe phrases, but it does not yet understand all semantically poor responses.

## 7. Limitations & Risks

The largest limitation is scoring validity. The current scorer is rule-based and phrase-based. It can recognize many expected concepts and unsafe actions, but it can miss paraphrases, sarcasm, vague answers, or semantically wrong responses that do not match the current patterns.

The second major limitation is PDF quality. Handbook PDFs often contain broken lines, repeated headers, table-of-contents fragments, weird character encoding, and incomplete sentences. The current cleaner handles many of these cases, but messy PDFs can still lead to weak or irrelevant scenarios.

The third limitation is rubric flexibility. The sample rubric is static. The system can extract policies from a new handbook, but it does not yet generate a custom rubric from that handbook or let a manager approve policy-specific scoring criteria.

Other risks include:

- No authentication or real role-based access control between learner and manager views.
- Reports are saved locally without encryption or retention controls.
- Uploaded handbook content may contain confidential company policy.
- A learner could memorize keyword patterns rather than demonstrate true job readiness.
- The system may overstate confidence if users treat `good`, `neutral`, and `bad` as certified safety judgments.
- The current benchmark is small and mostly developer-authored.
- The UI is suitable for a demo but not yet a polished training product.

The MVP should therefore be presented as a prototype training assistant, not a validated compliance or certification system.

## 8. Next Steps

With two to three more months, the best technical next step would be stronger semantic evaluation. I would add a retrieval-augmented or LLM-backed scoring layer that compares a learner response against the cited policy while still requiring structured JSON output, citations, and deterministic fallback checks for unsafe actions. This would help catch cases like "I would run away" without losing the current transparency.

The second priority would be a larger evaluation set. I would expand `benchmark_cases.json` into a real benchmark with dozens of safety, customer-service, and procedural-manual examples, including good paraphrases, vague answers, copy-paste answers, unsafe answers, and tricky near-misses. I would also compare the current workflow against a raw general-purpose AI baseline on the same cases.

The third priority would be manager-controlled setup. A manager should be able to review extracted policies, remove bad ones, edit scenario prompts, and approve the rubric before assigning the module to learners.

The fourth priority would be product hardening. That includes login separation for learners and managers, a persistent database instead of local report files, privacy controls for uploaded handbooks, clearer export options, and deployment instructions for non-technical users.

Finally, I would improve the demo experience: cleaner onboarding text, better progress indicators, downloadable reports, and a small set of polished example handbooks that show safety and procedural-manual modes side by side.
