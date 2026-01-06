import streamlit as st
from llm.career_ai import chunk_plan

st.title("📘 Study Plan")

# ---------------- Guard ----------------
if "selected_role" not in st.session_state:
    st.warning("Please select a role first.")
    st.stop()  # 🔑 Prevents loops

role_info = st.session_state["selected_role"]

st.header(role_info["role"])

# ---------------- Weekly Plan ----------------
plan_chunks = chunk_plan(
    role_info["learning_plan_90_days"],
    weeks=12
)

for idx, steps in enumerate(plan_chunks, start=1):
    #st.subheader(f"Phase {idx}")
    for step in steps:
        st.write("•", step)

# ---------------- Skills & Resources ----------------
st.subheader("🎓 Skills to Gain & Resources")

for ms in role_info["missing_skills"]:
    st.write(f"- **{ms['skill']}** → [Learn here]({ms['learning_link']})")

# ---------------- Navigation ----------------
if st.button("⬅ Back to Home"):
    st.switch_page("pages/home.py")
