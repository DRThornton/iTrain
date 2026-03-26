import streamlit as st

from source_code.ingest import load_handbook
from source_code.report import build_manager_report, save_report
from source_code.scenarios import generate_scenarios
from source_code.scoring import load_rubric, score_response


st.set_page_config(page_title="iTrain MVP", layout="wide")

st.title("iTrain MVP")
st.write("Interactive job-training scenario demo")

if "scenarios" not in st.session_state:
    st.session_state.scenarios = []
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "report" not in st.session_state:
    st.session_state.report = None

with st.sidebar:
    st.header("Setup")
    learner_name = st.text_input("Learner name", value="Demo User")
    uploaded_handbook = st.file_uploader("Upload handbook (.txt or .pdf)", type=["txt", "pdf"])
    rubric_path = "app/data/sample_rubric.json"

    if st.button("Load Training Module"):
        try:
            if uploaded_handbook is not None:
                handbook_text = load_handbook(uploaded_handbook)
            else:
                with open("app/data/sample_handbook.txt", "r", encoding="utf-8") as f:
                    handbook_text = f.read()

            scenarios = generate_scenarios(handbook_text, num_scenarios=3)
            st.session_state.scenarios = scenarios
            st.session_state.answers = {}
            st.session_state.report = None
            st.success("Training module loaded.")
        except Exception as e:
            st.error(f"Error loading handbook: {e}")

tabs = st.tabs(["Learner View", "Manager View"])

with tabs[0]:
    st.subheader("Learner View")

    if not st.session_state.scenarios:
        st.info("Load a training module from the sidebar to begin.")
    else:
        for scenario in st.session_state.scenarios:
            st.markdown(f"### Scenario {scenario['id']}")
            st.write(scenario["prompt"])
            answer = st.text_area(
                "Your response",
                key=f"answer_{scenario['id']}",
                height=120
            )
            st.session_state.answers[scenario["id"]] = answer

        if st.button("Complete Training"):
            rubric = load_rubric(rubric_path)
            results = []

            for scenario in st.session_state.scenarios:
                answer = st.session_state.answers.get(scenario["id"], "").strip()
                result = score_response(answer, scenario["policy"], rubric)

                results.append({
                    "scenario_id": scenario["id"],
                    "prompt": scenario["prompt"],
                    "response": answer,
                    "score": result
                })

            report = build_manager_report(results, learner_name=learner_name)
            path = save_report(report, reports_dir="app/reports")
            report["saved_to"] = path
            st.session_state.report = report

            st.success("Training complete.")

with tabs[1]:
    st.subheader("Manager View")

    if st.session_state.report is None:
        st.info("No completed report yet.")
    else:
        report = st.session_state.report

        st.write("### Summary")
        st.json(report["summary"])
        st.write(f"**Recommendation:** {report['recommendation']}")
        st.write(f"**Saved report:** `{report['saved_to']}`")

        st.write("### Detailed Results")
        for item in report["results"]:
            st.markdown(f"#### Scenario {item['scenario_id']}")
            st.write(f"**Learner response:** {item['response']}")
            st.write(f"**Score:** {item['score']['label']}")
            st.write(f"**Rationale:** {item['score']['rationale']}")
            st.write(f"**Handbook citation:** {item['score']['citation']}")