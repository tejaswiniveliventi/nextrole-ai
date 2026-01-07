import streamlit as st
from config_loader import load_config

config = load_config()

st.set_page_config(
    page_title=config["ui"]["app_title"],
    page_icon=config["ui"]["app_icon"],
    layout="wide"
)

home_page = st.Page("pages/home.py", title="Home")
study_plan_page = st.Page("pages/study_plan.py", title="Study Plan")

navigation = st.navigation([home_page, study_plan_page])
navigation.run()
