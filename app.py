import streamlit as st

st.set_page_config(
    page_title="NextRole AI",
    page_icon="🚀",
    layout="wide"
)

# Define pages
home_page = st.Page(
    "pages/home.py",
    title="Home"
)

study_plan_page = st.Page(
    "pages/study_plan.py",
    title="Study Plan"
)

# Navigation
pg = st.navigation(
    [
        home_page,
        study_plan_page
    ]
)

pg.run()
