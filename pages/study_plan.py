import logging
import streamlit as st
from config_loader import load_config
from llm import create_career_agent
from utils.style_builder import apply_styles, render_skill_badges, format_html_template
from services.table_storage_tracker import get_progress_tracker

logger = logging.getLogger(__name__)

config = load_config()

def show_study_plan():
    apply_styles()
    
    if "selected_role" not in st.session_state:
        st.warning(config["ui"]["no_role_selected"])
        return

    role = st.session_state["selected_role"]
    tracker = get_progress_tracker()
    user_id = st.session_state.get("user_id", "anonymous")
    
    # Professional header with role info
    colors = config.get("ui", {}).get("colors", {})
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, {colors.get("primary", "#1E3A8A")} 0%, {colors.get("secondary", "#0EA5E9")} 100%); color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px;'>
        <h1 style='margin: 0; color: white;'>{role['role']}</h1>
        <p style='margin: 10px 0 0 0; color: rgba(255,255,255,0.9); font-size: 18px;'>{role.get('summary', 'Career pathway plan')}</p>
    </div>
    """, unsafe_allow_html=True)

    # Skills overview
    col1, col2 = st.columns(2)
    
    with col1:
        if role.get("required_skills"):
            st.subheader("Required Skills")
            skills_html = render_skill_badges(role.get("required_skills", []), missing=False)
            st.markdown(f"<div style='margin: 10px 0;'>{skills_html}</div>", unsafe_allow_html=True)

    with col2:
        if role.get("missing_skills"):
            st.subheader("Skills to Develop")
            skills_html = render_skill_badges(role.get("missing_skills", []), missing=True)
            st.markdown(f"<div style='margin: 10px 0;'>{skills_html}</div>", unsafe_allow_html=True)

    st.divider()
    
    # Get study plan
    current_skills = st.session_state.get("skills", [])
    agent = create_career_agent()
    phases = agent.generate_study_plan(role, current_skills=current_skills) 
   
    # Display phases
    st.markdown("## 📚 Learning Roadmap")
    
    phase_card = config.get("ui", {}).get("phase_card", {})
    
    for idx, phase in enumerate(phases.get("phases", []), start=1):
        header = config["study_plan"]["phase_header"].format(number=idx)
        duration = phase.get("duration", "")
        
        st.markdown(f"""
        <div style='background-color: {phase_card.get("background_color", "#F8FAFC")}; border-left: {phase_card.get("border_left_width", 4)}px solid {phase_card.get("border_left_color", "#0EA5E9")}; padding: {phase_card.get("padding", 16)}px; border-radius: {phase_card.get("border_radius", 6)}px; margin: 20px 0;'>
            <div style='color: {colors.get("primary", "#1E3A8A")}; font-size: 20px; font-weight: 600; margin-bottom: 15px;'>
                {header} {f"• {duration}" if duration else ""}
            </div>
        """, unsafe_allow_html=True)
        
        # Phase content
        st.markdown(f"<div style='color: {colors.get('text_primary', '#1E293B')}; line-height: 1.8;'>", unsafe_allow_html=True)
        
        focus_items = phase.get("focus", [])
        if focus_items:
            st.markdown("**Learning Focus:**")
            for item in focus_items:
                st.markdown(f"• {item}")
        
        skills_targeted = phase.get("skills_targeted", [])
        if skills_targeted:
            st.markdown("**Target Skills:**")
            skills_html = render_skill_badges(skills_targeted, missing=False)
            st.markdown(f"<div style='margin: 10px 0;'>{skills_html}</div>", unsafe_allow_html=True)
        
        deliverable = phase.get("deliverable")
        if deliverable:
            st.markdown(f"""
            <div style='background-color: #FFF3E0; border-left: 4px solid {colors.get("warning", "#F59E0B")}; padding: 15px; border-radius: 4px; margin-top: 12px;'>
                <strong>🎯 Deliverable:</strong> {deliverable}
            </div>
            """, unsafe_allow_html=True)
        
        # Progress tracking UI
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            completion_pct = st.slider(
                f"Phase {idx} progress",
                0, 100, 0,
                key=f"phase_{idx}_progress",
                label_visibility="collapsed"
            )
        
        with col2:
            hours = st.number_input(
                f"Hours",
                0, 1000, 0,
                key=f"phase_{idx}_hours",
                label_visibility="collapsed"
            )
        
        with col3:
            if st.button(
                "✓ Mark Done" if completion_pct == 100 else "Save",
                key=f"phase_{idx}_save",
                use_container_width=True
            ):
                # Track phase progress
                tracker.save_phase_progress(
                    user_id,
                    role.get("role"),
                    idx,
                    {
                        "status": "completed" if completion_pct == 100 else "in_progress",
                        "completion_percentage": completion_pct,
                        "hours_spent": hours,
                        "skills_learned": skills_targeted,
                    }
                )
                st.success(f"Phase {idx} progress saved!")
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button(
            config["ui"]["back_button"],
            use_container_width=True,
            type="secondary"
        ):
            st.switch_page("pages/home.py")

show_study_plan()
