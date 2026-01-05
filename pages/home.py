import streamlit as st
from llm import extract_skills, get_next_roles_with_links
from utils import extract_text_from_pdf

ALL_SKILLS = [
    "Python", "SQL", "Power BI", "Tableau", "Excel", "ETL", "Data Analysis",
    "Machine Learning", "Deep Learning", "AWS", "Azure", "Leadership",
    "Project Management", "Salesforce", "DAX", "Data Visualization"
]

def show_home_page():
    st.title("NextRole AI 🚀")
    st.write("Turn your resume into your next career opportunity")
    st.markdown("---")

    st.write(
        "**Problem:** Skills don’t clearly translate into career opportunities.\n"
        "**Solution:** NextRole AI analyzes your resume or manually entered skills and recommends realistic next roles, "
        "skill gaps, and a 90-day learning roadmap using AI."
    )

    # --- Resume Upload ---
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
    career_goal = st.text_input("Career Interest (optional)")

    resume_skills = ""
    if uploaded_file:
        resume_text = extract_text_from_pdf(uploaded_file)
        with st.spinner("🔍 Extracting skills from resume..."):
            resume_skills = extract_skills(resume_text)
            resume_skills = ", ".join([s.strip() for s in resume_skills.split(",") if s.strip()])

    # --- Manual skill entry ---
    st.write("### Or manually add your skills")
    manual_skills = st.multiselect(
        "Select or type your skills:",
        options=ALL_SKILLS,
        default=[],
        help="Start typing to find skills or add your own"
    )

    # --- Combine skills ---
    combined_skills_list = []
    if resume_skills:
        combined_skills_list += [s.strip() for s in resume_skills.split(",") if s.strip()]
    if manual_skills:
        combined_skills_list += [s.strip() for s in manual_skills if s.strip()]
    skills = ", ".join(sorted(set(combined_skills_list)))

    if skills:
        st.write("**Your Skills:**")
        cols = st.columns(4)
        for idx, skill in enumerate(skills.split(",")):
            with cols[idx % 4]:
                st.success(skill)

    # --- Generate suggested roles ---
    if st.button("Find My Next Role"):
        if not skills:
            st.warning("Please provide skills via resume upload or manual input.")
        else:
            with st.spinner("🔍 Mapping your next roles..."):
                result = get_next_roles_with_links(skills, career_goal)

            if "error" in result:
                st.error(result["error"])
            else:
                st.write("## Suggested Roles")
                role_options = [role_info["role"] for role_info in result.get("suggested_roles", [])]

                selected_role_name = st.selectbox("Pick a role to track your progress:", options=role_options)
                if selected_role_name:
                    for role_info in result.get("suggested_roles", []):
                        if role_info["role"] == selected_role_name:
                            st.session_state["selected_role"] = role_info
                            st.session_state["page"] = "study_plan"
                            st.experimental_rerun()
