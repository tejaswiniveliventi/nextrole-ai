# pages/home.py

import streamlit as st
from llm import extract_skills, get_next_roles_with_links
from utils import extract_text_from_pdf

def show_home_page():
    st.set_page_config(page_title="NextRole AI", page_icon="🚀", layout="wide")

    st.title("NextRole AI 🚀")
    st.write("Turn your resume into your next career opportunity.")

    st.write("**Problem:** Skills don’t clearly translate into career opportunities.")
    st.write("**Solution:** NextRole AI analyzes your resume and recommends realistic next roles, skill gaps, and a 90-day learning roadmap using AI.")

    # --- Resume Upload ---
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

    # --- Manual skill input ---
    manual_skills = st.text_input("Or enter skills manually (comma separated)")

    # --- Career goal ---
    career_goal = st.text_input("Career Interest (optional)")

    # Extract skills from resume or use manual
    skills = ""
    if uploaded_file:
        resume_text = extract_text_from_pdf(uploaded_file)
        try:
            skills = extract_skills(resume_text)
        except Exception as e:
            st.error(f"Error extracting skills: {e}")

    if manual_skills:
        # Merge with extracted skills if any
        skills = ", ".join(filter(None, [skills, manual_skills]))

    skills = ", ".join([s.strip() for s in skills.split(",") if s.strip()])

    # Display extracted skills
    if skills:
        st.write("**Extracted Skills:**")
        cols = st.columns(4)
        skill_list = [s.strip() for s in skills.split(",")]
        for idx, skill in enumerate(skill_list):
            with cols[idx % 4]:
                st.markdown(f"- {skill}")

    # --- Next Role Suggestions ---
    if st.button("Find My Next Role"):
        if not skills:
            st.warning("Please upload a resume or enter skills manually.")
        else:
            with st.spinner("Mapping your next roles..."):
                try:
                    result = get_next_roles_with_links(skills, career_goal)
                    if "error" in result:
                        st.error(result["error"])
                        return

                    st.write("## Suggested Roles")
                    for role_info in result.get("suggested_roles", []):
                        st.subheader(role_info["role"])
                        st.write("🎯 Why this fits you:")
                        st.write(role_info["why_fit"])

                        st.write("🧠 Skill gaps & learning resources:")
                        for ms in role_info["missing_skills"]:
                            st.write(f"- {ms['skill']} → [📚 Learn here]({ms['learning_link']})")

                        st.write("🗓️ 90-Day Learning Plan:")
                        for step in role_info["learning_plan_90_days"]:
                            st.write("•", step)

                        # Select a role to track progress
                        if st.button(f"Track progress for {role_info['role']}",key=f"track_{role_info}"):
                            st.session_state["selected_role"] = role_info
                            st.session_state["skills"] = skills
                            st.session_state["career_goal"] = career_goal
                            st.session_state["page"] = "study_plan"
                            st.rerun()
                            #st.session_state["refresh_toggle"] = not st.session_state.get("refresh_toggle", False)
                except Exception as e:
                    st.error(f"Failed to get next roles: {e}")
