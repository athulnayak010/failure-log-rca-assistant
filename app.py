import streamlit as st
from log_parser import parse_log_file
from rca_engine import analyze_logs

st.set_page_config(page_title="Failure Log RCA Assistant", layout="wide")

st.title("Failure Log RCA Assistant")
st.caption("Paste or upload failed test logs → get grouped symptoms + top 3 probable root causes")

# --- Input section ---
st.subheader("1. Provide Failed Test Logs")

input_method = st.radio("Choose input method:", ["Upload a .txt file", "Paste text directly"])

log_text = None

if input_method == "Upload a .txt file":
    uploaded_file = st.file_uploader("Upload log file (.txt)", type=["txt"])
    if uploaded_file is not None:
        log_text = uploaded_file.read().decode("utf-8")
else:
    log_text = st.text_area("Paste your failed test log lines here:", height=250,
                              placeholder="[2026-09-10 09:12:03] TEST FAILED: test_login - TimeoutError: ...")

# --- Analyze button ---
if st.button("🚀 Analyze Logs", type="primary"):
    if not log_text or log_text.strip() == "":
        st.warning("Please upload or paste some log data first.")
    else:
        # Save temp file so we can reuse existing parser function
        with open("temp_uploaded_logs.txt", "w", encoding="utf-8") as f:
            f.write(log_text)

        with st.spinner("Parsing logs..."):
            parsed_logs = parse_log_file("temp_uploaded_logs.txt")

        st.success(f"Parsed {len(parsed_logs)} log line(s)")

        with st.spinner("Running AI root cause analysis..."):
            result = analyze_logs(parsed_logs)

        if "error" in result:
            st.error("AI response could not be parsed as JSON.")
            st.code(result.get("raw_output", ""))
        else:
            st.divider()

            # --- Symptom groups ---
            st.subheader("2. Grouped Symptom Summary")
            for group in result.get("symptom_groups", []):
                with st.expander(f"📌 {group['group_name']} — {group['count']} occurrence(s)"):
                    st.write("**Example affected tests:**")
                    for test in group.get("example_tests", []):
                        st.write(f"- {test}")

            st.divider()

            # --- Root causes ---
            st.subheader("3. Top 3 Probable Root Causes")
            for cause in result.get("root_causes", []):
                confidence = cause.get("confidence", "Unknown")
                color = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}.get(confidence, "⚪")

                st.markdown(f"### {color} Rank {cause.get('rank')}: {cause.get('cause')}")
                st.write(f"**Confidence:** {confidence}  |  **Affected tests:** {cause.get('affected_tests_count')}")
                st.write(f"**Reasoning:** {cause.get('reasoning')}")
                st.write("**Suggested next debugging steps:**")
                for step in cause.get("next_debugging_steps", []):
                    st.write(f"- {step}")
                st.divider()

st.caption("Built with Python + Streamlit | AI: openai/gpt-oss-120b via Groq API")