import streamlit as st
import requests

st.set_page_config(page_title="Resume–Role Fit Evaluator")

st.title("🧠 Resume–Role Fit Evaluator")
st.markdown("Check how well a resume fits a job description and get a learning path!")

resume_text = st.text_area("✍️ Paste Resume Text")
job_description = st.text_area("💼 Paste Job Description")

if st.button("🚀 Evaluate Fit"):
    if resume_text and job_description:
        with st.spinner("Evaluating..."):
            response = requests.post(
                "http://127.0.0.1:8000/evaluate-fit",
                json={
                    "resume_text": resume_text,
                    "job_description": job_description
                }
            )
            if response.status_code == 200:
                result = response.json()
                st.success(f"✅ Fit Score: {result['fit_score']} ({result['verdict']})")

                st.markdown("### ✅ Matched Skills")
                st.write(", ".join(result["matched_skills"]))

                st.markdown("### ❌ Missing Skills")
                st.write(", ".join(result["missing_skills"]))

                st.markdown("### 📚 Recommended Learning Tracks")
                for track in result["recommended_learning_track"]:
                    st.subheader(f"📌 {track['skill']}")
                    for step in track["steps"]:
                        st.write(f"- {step}")
            else:
                st.error("Failed to evaluate fit. Check the FastAPI server.")
    else:
        st.warning("Please provide both resume and job description.")
