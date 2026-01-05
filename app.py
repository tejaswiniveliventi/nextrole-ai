import streamlit as st
from llm import get_next_roles
from prompts import SKILL_TRANSLATOR_PROMPT, SKILL_EXTRACTION_PROMPT
from resume_parser import extract_text_from_pdf

st.set_page_config(page_title="NextRole AI", page_icon="🚀", layout="wide")

st.title("NextRole AI 🚀")
st.subheader("Upload your resume and discover your next career move")

# --- Resume Upload ---
uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
career_goal = st.text_input("Career Interest (optional)")

skills = ""
if uploaded_file:
    resume_text = extract_text_from_pdf(uploaded_file)
    
    # Extract skills
    skill_prompt = SKILL_EXTRACTION_PROMPT + resume_text
    skills = get_next_roles(skill_prompt)
    
    # Show extracted skills as badges
    st.markdown("**Extracted Skills:**")
    skill_list = [s.strip() for s in skills.split(",") if s.strip()]
    for skill in skill_list:
        st.markdown(f"- ✅ {skill}")

# --- Next Role Suggestions ---
if st.button("Find My Next Role"):
    if not skills:
        st.warning("Please upload a resume first.")
    else:
        user_input = f"""
        Extracted skills: {skills}
        Career goal: {career_goal}

        {SKILL_TRANSLATOR_PROMPT}
        """
        with st.spinner("Mapping your next roles..."):
            result_json = get_next_roles(user_input)

        st.markdown("## Suggested Roles")
        try:
            import json
            result = json.loads(result_json)
            for role_info in result.get("suggested_roles", []):
                st.markdown(f"### {role_info['role']}")
                st.markdown(f"**Why a fit:** {role_info['why_fit']}")
                st.markdown(f"**Missing Skills:** {', '.join(role_info['missing_skills'])}")
                st.markdown("**90-Day Learning Plan:**")
                for step in role_info['learning_plan_90_days']:
                    st.markdown(f"- {step}")
                st.markdown("---")
        except:
            st.text(result_json)  # fallback if JSON parsing fails
