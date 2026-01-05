from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import json
from prompts import (
    SKILL_EXTRACTION_PROMPT,
    SKILL_TRANSLATOR_PROMPT,
    NEXT_ROLE_WITH_LINKS_PROMPT
)

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2024-02-01"
)

DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")


def extract_skills(resume_text):
    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": "You extract skills from resumes."},
            {"role": "user", "content": SKILL_EXTRACTION_PROMPT + resume_text}
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()


def get_next_roles_with_links(skills, career_goal=None):
    prompt_input = skills
    if career_goal:
        prompt_input += f"\nUser's career interest: {career_goal}"
        
    prompt = NEXT_ROLE_WITH_LINKS_PROMPT.format(skills=prompt_input)

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": "You are an AI career advisor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "error": "Model returned invalid response",
            "raw_output": content
        }
