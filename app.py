import streamlit as st
from pages import home, study_plan

# --- Page setup ---
st.set_page_config(page_title="NextRole AI", page_icon="🚀", layout="wide")

# --- Session state ---
if "page" not in st.session_state:
    st.session_state["page"] = "home"
if "selected_role" not in st.session_state:
    st.session_state["selected_role"] = None

# --- Page router ---
if st.session_state["page"] == "home":
    home.show_home_page()
elif st.session_state["page"] == "study_plan":
    study_plan.show_study_plan_page()
