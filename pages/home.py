import streamlit as st
from config_loader import load_config
from llm import create_career_agent
from utils import extract_text_from_pdf

config = load_config()
agent = create_career_agent()
def show_home():
    st.title(config["ui"]["home_title"])
    st.write(config["ui"]["home_subtitle"])

    uploaded_file = st.file_uploader(
        config["ui"]["resume_upload_label"],
        type=["pdf"]
    )

    manual_skills = st.text_input(
        config["ui"]["manual_skills_label"]
    )

    career_goal = st.text_input(
        config["ui"]["career_goal_label"]
    )

    skills = ""

    if uploaded_file:
        with st.spinner(config["ui"]["extracting_skills_text"]):
            resume_text = extract_text_from_pdf(uploaded_file)
            skills = agent.llm.extract_skills(resume_text)

    if manual_skills:
        skills = manual_skills if not skills else skills + ", " + manual_skills

    if skills:
        st.success(config["ui"]["skills_ready_text"])

    if st.button(config["ui"]["find_roles_button"]):
        if not skills:
            st.warning(config["ui"]["no_skills_warning"])
            return

        with st.spinner(config["ui"]["finding_roles_text"]):
            result = agent.analyze_profile(skills, career_goal)
       # st.write(result)
        roles = result.get("roles", [])
        if not roles:
            st.warning("No suitable roles found.")
        else:
            st.session_state["roles"] = roles

    if "roles" in st.session_state:
        st.subheader(config["ui"]["roles_header"])

        for role in st.session_state["roles"]:
            st.write(role["role"])
            st.write(role["summary"])

            if st.button(
                config["ui"]["select_role_button"],
                key=role["role"]
            ):
                st.session_state["selected_role"] = role
                st.switch_page("pages/study_plan.py")

show_home()
