# app.py

import streamlit as st
from pages import home, study_plan

# Initialize page state
if "page" not in st.session_state:
    st.session_state["page"] = "home"

# Navigation
if st.session_state["page"] == "home":
    home.show_home_page()
elif st.session_state["page"] == "study_plan":
    study_plan.show_study_plan()
