import streamlit as st
from config_loader import load_config
from llm import create_career_agent

config = load_config()
agent=create_career_agent()
def show_study_plan():
    if "selected_role" not in st.session_state:
        st.warning(config["ui"]["no_role_selected"])
        return

    role = st.session_state["selected_role"]

    st.title(
        config["ui"]["study_plan_title"].format(role=role["role"])
    )

    phases = agent.generate_study_plan(role)
   
    for idx, phase in enumerate(phases["phases"], start=1):
        header = config["study_plan"]["phase_header"].format(number=idx) +" ("+phase["duration"]+")"
        st.subheader(header)
        for item in phase["focus"]:
            st.write(item)

    if st.button(config["ui"]["back_button"]):
        st.switch_page("pages/home.py")

show_study_plan()
