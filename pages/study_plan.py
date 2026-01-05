# pages/study_plan.py

import streamlit as st
from llm.career_ai import chunk_plan

def show_study_plan():
    if "selected_role" not in st.session_state:
        st.warning("Please select a role on the home page first.")
        return

    role_info = st.session_state["selected_role"]
    st.title(f"🗓️ Study Plan: {role_info['role']}")

    plan_chunks = chunk_plan(role_info["learning_plan_90_days"], weeks=12)

    for week_idx, week_steps in enumerate(plan_chunks, start=1):
        st.subheader(f"Week {week_idx}")
        for step in week_steps:
            st.write("•", step)

    st.write("### 🏆 Suggested Certifications / Learning Links")
    for ms in role_info["missing_skills"]:
        st.write(f"- {ms['skill']}: [📚 Learn here]({ms['learning_link']})")

    if st.button("Back to Home"):
        st.session_state["page"] = "home"
