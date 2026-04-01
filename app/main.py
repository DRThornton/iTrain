import streamlit as st

from agent import TrainingAgent
from tools.ingest import load_handbook
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


def load_default_handbook() -> str:
    with open("app/data/sample_handbook.txt", "r", encoding="utf-8") as f:
        return f.read()


with st.sidebar:
    st.header("Setup")
    learner_name = st.text_input("Learner name", value=st.session_state.learner_name)
    uploaded_handbook = st.file_uploader("Upload handbook (.txt or .pdf)", type=["txt", "pdf"])
    rubric_path = "app/data/sample_rubric.json"
    show_debug = st.checkbox("Show extracted policy debug", value=False)

    if st.button("Load Training Module"):
        try:
            if uploaded_handbook is not None:
                handbook_text = load_handbook(uploaded_handbook)
            else:
                handbook_text = load_default_handbook()

            rubric = load_rubric(rubric_path)
            agent = TrainingAgent(rubric=rubric, max_turns=5)
            session = agent.start_session(handbook_text)

            st.session_state.agent_session = session
            st.session_state.detected_policies = session["policies"]
            st.session_state.last_feedback = None
            st.session_state.report = None
            st.session_state.learner_name = learner_name
            st.success("Training module loaded.")
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

        st.write(f"Completed turns: **{len(history)}**")

        if st.session_state.last_feedback is not None:
            feedback = st.session_state.last_feedback
            st.write("### Agent Feedback")
            st.write(f"**Latest score:** {feedback['score']['label']}")
            st.write(feedback["score"]["rationale"])
            st.caption(feedback["message"])

        if current is None:
            st.success("Training complete.")
        else:
            st.markdown(f"### Turn {current['id']}")
            if current.get("kind") == "follow_up":
                st.info("The agent requested a follow-up before advancing.")
            st.write(current["prompt"])

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
                st.markdown(f"#### Turn {item['scenario_id']}")
                st.write(item["prompt"])
                st.write(f"**Response:** {item['response']}")
                st.write(f"**Score:** {item['score']['label']}")

with tabs[1]:
    st.subheader("Manager View")

    if st.session_state.report is None:
        st.info("No completed report yet.")
    else:
        report = st.session_state.report

        st.write("### Summary")
        st.json(report["summary"])
        st.write(f"**Recommendation:** {report['recommendation']}")
        if report.get("focus_areas"):
            st.write(f"**Focus areas:** {', '.join(report['focus_areas'])}")
        st.write(f"**Saved report:** `{report['saved_to']}`")

        st.write("### Detailed Results")
        for item in report["results"]:
            st.markdown(f"#### Scenario {item['scenario_id']}")
            st.write(f"**Learner response:** {item['response']}")
            st.write(f"**Score:** {item['score']['label']}")
            st.write(f"**Rationale:** {item['score']['rationale']}")
            st.write(f"**Handbook citation:** {item['score']['citation']}")
