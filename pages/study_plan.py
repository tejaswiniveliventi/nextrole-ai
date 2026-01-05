import streamlit as st
from llm import chunk_plan

def show_study_plan_page():
    role = st.session_state.get("selected_role")
    if not role:
        st.session_state["page"] = "home"
        st.experimental_rerun()

    st.title(f"🧑‍💼 {role['role']}")
    st.write("🎯 Why this fits you")
    st.write(role["why_fit"])

    st.write("🗓️ Your 90-Day Week-by-Week Plan")
    weekly_plan = chunk_plan(role["learning_plan_90_days"], weeks=12)
    for week_idx, steps in enumerate(weekly_plan, start=1):
        st.markdown(f"### Week {week_idx}")
        for step in steps:
            checkbox_key = f"week{week_idx}_{step}"
            st.checkbox(step, key=checkbox_key)

    st.subheader("🧠 Skill gaps & Suggested Certifications")
    for ms in role["missing_skills"]:
        st.markdown(f"- **{ms['skill']}** → [📚 Learn here]({ms['learning_link']})")

    if st.button("← Back to Role Selection"):
        st.session_state["page"] = "home"
        st.experimental_rerun()
