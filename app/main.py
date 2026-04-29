import streamlit as st

from agent import TrainingAgent
from tools.ingest import load_handbook
from tools.report import render_manager_summary_markdown
from tools.runtime import resource_path
from tools.scoring import load_rubric


st.set_page_config(page_title="iTrain MVP", layout="wide")

st.title("iTrain MVP")
st.write("Interactive job-training scenario demo with a simple agent-style training flow")

if "agent_session" not in st.session_state:
    st.session_state.agent_session = None
if "detected_policies" not in st.session_state:
    st.session_state.detected_policies = []
if "last_feedback" not in st.session_state:
    st.session_state.last_feedback = None
if "report" not in st.session_state:
    st.session_state.report = None
if "learner_name" not in st.session_state:
    st.session_state.learner_name = "Demo User"
if "manual_names" not in st.session_state:
    st.session_state.manual_names = []
if "document_type" not in st.session_state:
    st.session_state.document_type = None


def current_question_number(session) -> int:
    history = session.get("history", [])
    current = session.get("current")
    completed_primary_turns = sum(1 for item in history if item.get("kind", "scenario") != "follow_up")
    if current is None:
        return completed_primary_turns
    if current.get("kind") == "follow_up":
        return max(1, completed_primary_turns)
    return completed_primary_turns + 1


def turn_label(item) -> str:
    question_number = item.get("question_number")
    if question_number is None:
        return "Turn"
    if item.get("kind") == "follow_up":
        return f"Question {question_number} Follow-up"
    return f"Question {question_number}"


def load_default_handbook() -> str:
    with resource_path("app", "data", "sample_handbook.txt").open("r", encoding="utf-8") as f:
        return f.read()


with st.sidebar:
    st.header("Setup")
    learner_name = st.text_input("Learner name", value=st.session_state.learner_name)
    uploaded_handbook = st.file_uploader("Upload handbook (.txt or .pdf)", type=["txt", "pdf"])
    use_sample_handbook = st.checkbox("Use bundled sample handbook (demo mode)", value=False)
    rubric_path = str(resource_path("app", "data", "sample_rubric.json"))
    show_debug = st.checkbox("Show extracted policy debug", value=False)

    if st.button("Load Training Module"):
        try:
            if uploaded_handbook is not None:
                handbook_text = load_handbook(uploaded_handbook)
                manual_names = [uploaded_handbook.name]
            elif use_sample_handbook:
                handbook_text = load_default_handbook()
                manual_names = ["sample_handbook.txt"]
            else:
                st.session_state.agent_session = None
                st.session_state.detected_policies = []
                st.session_state.last_feedback = None
                st.session_state.report = None
                st.session_state.manual_names = []
                st.session_state.document_type = None
                st.error("Upload a handbook to start training, or enable bundled sample handbook demo mode.")
                st.stop()

            rubric = load_rubric(rubric_path)
            agent = TrainingAgent(rubric=rubric, max_turns=5)
            session = agent.start_session(handbook_text, manual_names=manual_names)

            st.session_state.agent_session = session
            st.session_state.detected_policies = session["policies"]
            st.session_state.last_feedback = None
            st.session_state.report = None
            st.session_state.learner_name = learner_name
            st.session_state.manual_names = manual_names
            st.session_state.document_type = session.get("document_type")
            if uploaded_handbook is not None:
                st.success("Training module loaded from uploaded document.")
            else:
                st.success("Training module loaded from bundled sample handbook.")
        except Exception as e:
            st.error(f"Error loading handbook: {e}")

tabs = st.tabs(["Learner View", "Manager View"])

with tabs[0]:
    st.subheader("Learner View")

    if show_debug and st.session_state.detected_policies:
        st.write("### Extracted Policies (Debug)")
        st.json(st.session_state.detected_policies)

    session = st.session_state.agent_session

    if session is None:
        st.info("Load a training module from the sidebar to begin.")
    else:
        history = session.get("history", [])
        current = session.get("current")
        document_type = session.get("document_type", "safety_handbook")
        completed_primary_turns = sum(1 for item in history if item.get("kind", "scenario") != "follow_up")
        total_primary_turns = session.get("total_primary_turns", 0)
        question_number = current_question_number(session)

        st.write(f"Completed questions: **{completed_primary_turns} / {total_primary_turns}**")
        if document_type == "procedural_manual":
            st.caption("Detected mode: Procedural manual. Prompts focus on the next documented step or check.")
        else:
            st.caption("Detected mode: Safety handbook. Prompts focus on workplace actions, escalation, and policy use.")

        if st.session_state.last_feedback is not None:
            feedback = st.session_state.last_feedback
            st.write("### Agent Feedback")
            st.write(f"**Latest score:** {feedback['score']['label']}")
            st.write(feedback["score"]["rationale"])
            st.caption(feedback["message"])

        if current is None:
            st.success("Training complete.")
        else:
            st.markdown(f"### Question {question_number} of {total_primary_turns}")
            if current.get("kind") == "follow_up":
                st.info(f"Follow-up for Question {question_number}. You are still working on the same question before moving on.")
            st.write(current["prompt"])
            if current.get("kind") != "follow_up" and current.get("hint"):
                st.caption(current["hint"])

            answer = st.text_area("Your response", key=f"answer_{current['id']}", height=140)

            if st.button("Submit Response"):
                rubric = load_rubric(rubric_path)
                agent = TrainingAgent(rubric=rubric, max_turns=5)
                updated_session, result = agent.submit_response(
                    session,
                    learner_name=learner_name,
                    response=answer.strip(),
                )
                st.session_state.agent_session = updated_session
                st.session_state.last_feedback = result
                st.session_state.report = result["report"] if result is not None else None
                st.session_state.learner_name = learner_name
                st.rerun()

        if history:
            st.write("### Completed Turns")
            for item in history:
                st.markdown(f"#### {turn_label(item)}")
                st.write(item["prompt"])
                st.write(f"**Response:** {item['response']}")
                st.write(f"**Score:** {item['score']['label']}")

with tabs[1]:
    st.subheader("Manager View")

    if st.session_state.report is None:
        st.info("No completed report yet.")
    else:
        report = st.session_state.report

        summary = report["summary"]
        st.write("### Summary")
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        metric_col1.metric("Good", summary["good"])
        metric_col2.metric("Neutral", summary["neutral"])
        metric_col3.metric("Bad", summary["bad"])
        metric_col4.metric("Weighted Score", report["weighted_score"])

        if report.get("manual_names"):
            st.write(f"**Manuals used:** {', '.join(report['manual_names'])}")
        if report.get("document_type"):
            st.write(f"**Detected document type:** {report['document_type']}")
        st.write(f"**Recommendation:** {report['recommendation']}")
        if report.get("focus_areas"):
            st.write(f"**Focus areas:** {', '.join(report['focus_areas'])}")
        saved_to = report.get("saved_to", {})
        if isinstance(saved_to, dict):
            if saved_to.get("json"):
                st.write(f"**Saved JSON report:** `{saved_to['json']}`")
            if saved_to.get("markdown"):
                st.write(f"**Saved summary report:** `{saved_to['markdown']}`")
        elif saved_to:
            st.write(f"**Saved report:** `{saved_to}`")

        results = report["results"]
        follow_up_count = sum(1 for item in results if item.get("kind") == "follow_up")
        st.write("### Run Highlights")
        st.write(f"**Questions answered:** {len({item.get('question_number') for item in results if item.get('question_number') is not None})}")
        st.write(f"**Follow-ups needed:** {follow_up_count}")
        if results:
            good_rate = round((summary["good"] / len(results)) * 100)
            st.write(f"**Good response rate:** {good_rate}%")

        st.write("### Saved Summary Preview")
        st.markdown(render_manager_summary_markdown(report))

        st.write("### Detailed Results")
        for item in results:
            label = turn_label(item)
            with st.expander(f"{label} - {item['score']['label']}", expanded=item["score"]["label"] != "good"):
                st.write(f"**Prompt:** {item['prompt']}")
                st.write(f"**Learner response:** {item['response']}")
                st.write(f"**Score:** {item['score']['label']}")
                st.write(f"**Rationale:** {item['score']['rationale']}")
                st.write(f"**Handbook citation:** {item['score']['citation']}")

        if show_debug and report.get("debug", {}).get("extracted_policy_debug"):
            st.write("### Debug Report")
            st.json(report["debug"])
