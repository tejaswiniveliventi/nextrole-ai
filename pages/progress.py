import logging
import streamlit as st
from config_loader import load_config
from services.table_storage_tracker import get_progress_tracker
from utils.style_builder import apply_styles

logger = logging.getLogger(__name__)
config = load_config()

def show_progress():
    apply_styles()
    
    st.title("📊 Your Career Progress")
    st.markdown("Track your journey towards your career goals")
    
    # Get or create user ID from session
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = st.text_input(
            "Enter your profile ID to view progress",
            placeholder="e.g., user_123",
            key="progress_user_id"
        )
    
    user_id = st.session_state.get("user_id", "")
    
    if not user_id or user_id == "":
        st.info("💡 Enter a profile ID to view your progress history")
        return
    
    tracker = get_progress_tracker()
    
    if not tracker.is_available():
        st.warning("⚠️ Progress tracking is currently unavailable. Cosmos DB connection not configured.")
        st.info("To enable progress tracking, set COSMOS_CONNECTION_STRING environment variable.")
        return
    
    # Display user statistics
    stats = tracker.get_user_stats(user_id)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Roles Explored", stats.get("total_roles_explored", 0), help="Number of career paths analyzed")
    
    with col2:
        st.metric("Phases Completed", stats.get("total_phases_completed", 0), help="Study phases finished")
    
    with col3:
        st.metric("Hours Studied", stats.get("total_hours_studied", 0), help="Total study time logged")
    
    with col4:
        st.metric("Skills Learned", len(stats.get("skills_learned", [])), help="Unique skills mastered")
    
    st.divider()
    
    # Roles history
    roles_history = stats.get("roles_history", [])
    if roles_history:
        st.subheader("🎯 Roles You've Explored")
        for idx, role_item in enumerate(roles_history, 1):
            with st.container(border=True):
                st.markdown(f"**{idx}. {role_item['role']}**")
                st.caption(f"Explored on {role_item['timestamp'][:10]}")
    
    st.divider()
    
    # Skills milestones
    milestones = stats.get("milestones", [])
    if milestones:
        st.subheader("🏆 Skills Achievements")
        
        # Group by skill
        skills_dict = {}
        for milestone in milestones:
            skill = milestone['skill']
            if skill not in skills_dict:
                skills_dict[skill] = []
            skills_dict[skill].append(milestone)
        
        for skill, skill_milestones in skills_dict.items():
            with st.container(border=True):
                latest = skill_milestones[0]
                level_emoji = {"beginner": "🌱", "intermediate": "🌿", "advanced": "🌳"}.get(latest['level'], "✨")
                st.markdown(f"{level_emoji} **{skill}** — {latest['level'].title()}")
                st.caption(f"Last updated: {latest['timestamp'][:10]}")
    
    st.divider()
    
    # Recent activity
    st.subheader("📝 Recent Activity")
    history = tracker.get_user_progress_history(user_id, limit=10)
    
    if history:
        for item in history:
            item_type = item.get("type")
            timestamp = item.get("timestamp", "")[:10]
            
            if item_type == "role_selection":
                st.info(f"✅ Selected role: **{item.get('role_name')}** ({timestamp})")
            elif item_type == "phase_progress":
                phase_num = item.get("phase_number")
                status = item.get("status")
                completion = item.get("completion_percentage", 0)
                st.success(f"📈 Phase {phase_num}: {status} ({completion}% complete) — {item.get('hours_spent')} hours ({timestamp})")
            elif item_type == "skill_milestone":
                skill = item.get("skill")
                level = item.get("proficiency_level")
                st.success(f"🎓 Completed skill: **{skill}** ({level}) ({timestamp})")
    else:
        st.info("No activity recorded yet. Start by taking a career assessment!")
    
    st.divider()
    
    # Option to reset or go back
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Home"):
            st.switch_page("pages/home.py")
    
    with col2:
        if st.button("🔄 Change Profile ID"):
            st.session_state["user_id"] = ""
            st.rerun()

show_progress()
