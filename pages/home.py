import streamlit as st
from llm import extract_skills, get_next_roles_with_links
from utils import extract_text_from_pdf

st.title("NextRole AI 🚀")
st.write("Turn your resume into your next career opportunity.")

# ---------------- Inputs ----------------
uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
manual_skills = st.text_input("Or enter skills manually (comma separated)")
career_goal = st.text_input("Career Interest (optional)")

skills = ""

# ---------------- Skill Extraction ----------------
if uploaded_file:
    resume_text = extract_text_from_pdf(uploaded_file)
    skills = extract_skills(resume_text)

if manual_skills:
    skills = ", ".join(filter(None, [skills, manual_skills]))

skills = ", ".join([s.strip() for s in skills.split(",") if s.strip()])

if skills:
    st.success(f"Skills detected: {skills}")

# ---------------- Role Discovery ----------------
if st.button("Find My Next Role"):
    if not skills:
        st.warning("Please upload a resume or enter skills.")
    else:
        with st.spinner("Finding best roles for you..."):
            result = get_next_roles_with_links(skills, career_goal)
            st.session_state["roles"] = result["suggested_roles"]

# ---------------- Role Selection ----------------
if "roles" in st.session_state:
    st.subheader("Select a role to generate your study plan")

    role_names = [r["role"] for r in st.session_state["roles"]]
    selected_role_name = st.radio("Available roles", role_names)

    if st.button("Show Study Plan"):
        selected_role = next(
            r for r in st.session_state["roles"]
            if r["role"] == selected_role_name
        )

        st.session_state["selected_role"] = selected_role
        st.switch_page("pages/study_plan.py")
