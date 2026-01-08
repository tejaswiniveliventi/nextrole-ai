import json
import re
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
from prompts import SKILL_EXTRACTION_PROMPT, NEXT_ROLE_WITH_LINKS_PROMPT

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2024-02-01"
)

DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")


def extract_skills(resume_text):
    """
    Extracts skills from resume text using AI.
    Returns a comma-separated string.
    """
    prompt = SKILL_EXTRACTION_PROMPT + resume_text
    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": "You are an AI that extracts professional skills."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()


def get_next_roles_with_links(skills_text, career_goal=None):
    """
    Returns AI suggested next roles with missing skills, 90-day plan, and links.
    """
    prompt_input = skills_text
    if career_goal:
        prompt_input += f"\nUser's career interest: {career_goal}"

    prompt = NEXT_ROLE_WITH_LINKS_PROMPT.format(skills=prompt_input)
    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": "You are a career advisor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )

    raw_text = response.choices[0].message.content

    # --- Safe JSON parsing ---
    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        match = re.search(r"(\{.*\})", raw_text, re.DOTALL)
        if match:
            try:
                result = json.loads(match.group(1))
            except:
                return {"error": "Failed to parse AI response."}
        else:
            return {"error": "Failed to parse AI response."}

    return result


def chunk_plan(plan_steps, weeks=12):
    """
    Split learning steps into weekly chunks for 90-day plan.
    """
    week_size = max(1, len(plan_steps) // weeks)
    return [plan_steps[i:i + week_size] for i in range(0, len(plan_steps), week_size)]


def recommend_roles(extracted_skills):
    # A simple mapping of skills to roles (this can be expanded)
    role_mapping = {
        "Python": ["Data Scientist", "Software Engineer"],
        "Java": ["Java Developer", "Backend Engineer"],
        "Machine Learning": ["Machine Learning Engineer", "Data Scientist"],
        # Add more mappings as needed
    }

    recommended_roles = set()
    for skill in extracted_skills:
        if skill in role_mapping:
            recommended_roles.update(role_mapping[skill])

    return list(recommended_roles)  # Return unique recommended roles
