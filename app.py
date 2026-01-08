import logging
import streamlit as st
from config_loader import load_config
STREAMLIT_SERVER_MAX_UPLOAD_SIZE=10
# Configure basic logging for the app
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("nextrole_ai")

config = load_config()
logger.info("Starting NextRole AI web app")

st.set_page_config(
    page_title=config["ui"]["app_title"],
    page_icon=config["ui"]["app_icon"],
    layout="wide"
)

home_page = st.Page("pages/home.py", title="Home")
study_plan_page = st.Page("pages/study_plan.py", title="Study Plan")

navigation = st.navigation([home_page, study_plan_page])
navigation.run()
logger.info("Streamlit navigation started")
