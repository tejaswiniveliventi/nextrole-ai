import streamlit as st
from llm import extract_skills, get_next_roles_with_links
from prompts import SKILL_TRANSLATOR_PROMPT, SKILL_EXTRACTION_PROMPT
from resume_parser import extract_text_from_pdf

# --- Page Config ---
st.set_page_config(page_title="NextRole AI", page_icon="🚀", layout="wide")
ALL_SKILLS = [
    "Python", "SQL", "Power BI", "Tableau", "Excel", "ETL", "Data Analysis",
    "Machine Learning", "Deep Learning", "AWS", "Azure", "Leadership",
    "Project Management", "Salesforce", "DAX", "Data Visualization"
]
# --- Header ---
st.title("NextRole AI 🚀")
st.caption("Turn your resume into your next career opportunity")
st.divider()

# --- Problem / Solution ---
st.markdown(
    """
**Problem:** Skills don’t clearly translate into career opportunities.  
**Solution:** NextRole AI analyzes your resume and recommends realistic next roles,
skill gaps, and a 90-day learning roadmap using AI.
"""
)


# --- Resume Upload ---
uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
st.markdown("### Or manually add your skills")
selected_skills = st.multiselect(
    "Select or type your skills:",
    options=ALL_SKILLS,
    default=[],
    help="Start typing to find skills or add your own"
)
career_goal = st.text_input("Career Interest (optional)")

skills = ""
if uploaded_file:
    resume_text = extract_text_from_pdf(uploaded_file)
    with st.spinner("🔍 Extracting skills from resume..."):
        skills = extract_skills(resume_text)
    skill_list = [s.strip() for s in skills.split(",") if s.strip()]
else:
    # Use manually entered skills
    skill_list = selected_skills
    skills = ", ".join(skill_list)
if skill_list:
    st.markdown("**Your Skills:**")
    cols = st.columns(4)
    for idx, skill in enumerate(skill_list):
        with cols[idx % 4]:
            st.info(skill)

st.divider()

# --- Next Role Suggestions ---
if st.button("Find My Next Role"):
    if not skills:
        st.warning("Please upload a resume first.")
    else:
        with st.spinner("🔍 Mapping your next roles..."):
            # Include career goal if provided
            prompt_input = skills
            if career_goal:
                prompt_input += f"\nUser's career interest: {career_goal}"

            result = get_next_roles_with_links(prompt_input)

        # Check for errors
        if "error" in result:
            st.error("⚠️ Something went wrong while analyzing your resume.")
            st.text(result["raw_output"])
        else:
            st.markdown("## 🚀 Suggested Roles")

            for role_info in result.get("suggested_roles", []):
                with st.container():
                    st.subheader(f"🧑‍💼 {role_info['role']}")

                    # 🎯 Why this fits
                    st.markdown(f"<h4 style='margin-bottom:4px;'> 🎯 Why this fits you", unsafe_allow_html=True)
                    st.write(role_info["why_fit"])

                    # 🧠 Skill gaps & links
                    st.markdown(f"<h4 style='margin-bottom:4px;'> 🧠 Skill gaps & learning resources",unsafe_allow_html=True)
                    for ms in role_info["missing_skills"]:
                        st.markdown(f"- **{ms['skill']}** ")#→ [📚 Learn here]({ms['learning_link']})")

                    # 🗓️ 90-day plan
                    st.markdown(f"<h4 style='margin-bottom:4px;'> 🗓️ 90-Day Learning Plan",unsafe_allow_html=True)
                    for step in role_info["learning_plan_90_days"]:
                        st.write("•", step)

                st.divider()

# --- Footer ---
st.caption(
    "Powered by Azure OpenAI • Built for Microsoft Imagine Cup 2026 • MVP by a solo student developer"
)
