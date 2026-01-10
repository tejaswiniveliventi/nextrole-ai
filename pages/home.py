import logging
import streamlit as st
from config_loader import load_config
from llm import create_career_agent
from utils import extract_text_from_pdf
from utils.style_builder import apply_styles, render_skill_badges, format_html_template
from services.table_storage_tracker import get_progress_tracker

logger = logging.getLogger(__name__)

config = load_config()

def show_home():
    apply_styles()
    
    # Initialize or get user ID
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = f"user_{hash(str(st.session_state.get('_client_state', '')))}"
    
    # Professional header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(config["ui"]["home_title"])
        st.markdown(f"<p class='intro-text'>{config['ui']['home_subtitle']}</p>", unsafe_allow_html=True)
    with col2:
        st.write("")  # spacer
        
    st.divider()
    
    agent = create_career_agent()
    tracker = get_progress_tracker()

    # Input section with professional cards
    st.markdown("### 📋 Assessment Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(format_html_template("input_label_template", label=config['ui']['resume_upload_label']), unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            label="",
            type=["pdf","docx"],
            label_visibility="collapsed",
            key="resume_uploader"
        )
        
        st.markdown(format_html_template("input_label_template", label=config['ui']['manual_skills_label']), unsafe_allow_html=True)
        manual_skills = st.text_input(
            label="",
            placeholder="e.g., Python, Data Analysis, Machine Learning",
            label_visibility="collapsed",
            key="manual_skills_input"
        )
    
    with col2:
        st.markdown(format_html_template("input_label_template", label=config['ui']['career_goal_label']), unsafe_allow_html=True)
        career_goal = st.text_input(
            label="",
            placeholder="e.g., Transition to Data Science",
            label_visibility="collapsed",
            key="career_goal_input"
        )

    # Normalize skills into a list and persist in session state across reruns
    skills = st.session_state.get("skills", [])

    if uploaded_file:
        with st.spinner(config["ui"]["extracting_skills_text"]):
            resume_text = extract_text_from_pdf(uploaded_file)
            extracted = agent.llm.extract_skills(resume_text)
           # if isinstance(extracted, list):
            #    st.write("inhereited list:", extracted)  # Debug line
             #   skills = extracted["skills"]
              #  current_role = extracted["current_role", ""]
               # experience_level = extracted["experience_level", ""]
            #elif isinstance(extracted["skills"], str) and extracted:
            skills = extracted["skills"]#[s.strip() for s in extracted["skills"].split(",") if s.strip()]
            current_role = extracted["current_role"]
            experience_level = extracted["experience_level"]
            logger.info("Skills extracted from uploaded resume: %s", skills)
            # update persisted skills immediately
            if skills:
                st.session_state["skills"] = skills

    if manual_skills:
        manual_list = [s.strip() for s in manual_skills.split(",") if s.strip()]
        skills = skills + [s for s in manual_list if s not in skills]

    if skills:
        st.markdown(format_html_template("success_box", message=config['ui']['skills_ready_text']), unsafe_allow_html=True)
        st.session_state["skills"] = skills
        
        # Display skills as professional badges
        st.markdown("**Your Skills:**")
        skills_html = render_skill_badges(skills, missing=False)
        st.markdown(f"<div style='margin: 15px 0;'>{skills_html}</div>", unsafe_allow_html=True)
  
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.divider()
        if st.button(
            config["ui"]["find_roles_button"],
            type="primary",
            use_container_width=True
        ):
            if not skills:
                st.warning(config["ui"]["no_skills_warning"])
                return

            with st.spinner(config["ui"]["finding_roles_text"]):
                
                result = agent.analyze_profile(skills, career_goal, experience_level=experience_level, current_role=current_role)
                roles = result.get("roles", [])
                
                if not roles:
                    st.warning("No suitable roles found — the model returned no valid roles.")
                    # display raw LLM response in an expander for debugging (truncated)
                    raw = getattr(agent.llm, "last_raw_response", None)
                    if raw:
                        with st.expander("LLM raw response (truncated)"):
                            st.code(raw[:2000])
                else:
                    st.session_state["roles"] = roles

    if "roles" in st.session_state:
        st.divider()
        st.markdown(format_html_template("roles_section", header=config['ui']['roles_header']), unsafe_allow_html=True)
        st.markdown("---")
        
        for idx, role in enumerate(st.session_state["roles"]):
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"### {role['role']}")
                    st.markdown(role.get("summary", ""), help="Role overview and description")

                    if role.get("required_skills"):
                        st.markdown("**Required Skills:**")
                        skills_html = render_skill_badges(role.get("required_skills", []), missing=False)
                        st.markdown(f"<div>{skills_html}</div>", unsafe_allow_html=True)

                    missing = role.get("missing_skills", [])
                    if missing:
                        st.markdown("**Skills to Develop:**")
                        skills_html = render_skill_badges(missing, missing=True)
                        st.markdown(f"<div>{skills_html}</div>", unsafe_allow_html=True)
                    else:
                        st.success("✓ You have all required skills")
                
                with col2:
                    st.write("")  # spacer
                    if st.button(
                        config["ui"]["select_role_button"],
                        key=f"select_{idx}",
                        use_container_width=True
                    ):
                        # Track role selection in Cosmos DB
                        tracker.save_role_selection(st.session_state["user_id"], role)
                        st.session_state["selected_role"] = role
                        st.switch_page("pages/study_plan.py")

show_home()
