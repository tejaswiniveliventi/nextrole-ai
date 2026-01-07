# llm/career_ai.py

import os
import json
import re
from dotenv import load_dotenv
from openai import AzureOpenAI
from .prompts import NEXT_ROLE_PROMPT, STUDY_PLAN_PROMPT, SKILL_EXTRACTION_PROMPT

# Load environment variables
load_dotenv()

DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=AZURE_API_KEY,
    azure_endpoint=AZURE_ENDPOINT,
    api_version="2024-02-01"
)


class LLMClient:
    """
    LLM Client for making real calls to Azure OpenAI
    """

    def complete(self, prompt):
        """
        Calls the real LLM and returns parsed JSON
        """
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        raw_content = response.choices[0].message.content.strip()

        # Attempt to parse JSON from response
        try:
            return json.loads(raw_content)
        except json.JSONDecodeError:
            # Fallback: extract JSON block from text
            match = re.search(r"\{.*\}", raw_content, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    return {}
            else:
                return {}

    def extract_skills(self, resume_text):
        """
        Extract skills from resume text using LLM
        """
        prompt = SKILL_EXTRACTION_PROMPT + resume_text
        return self.complete(prompt)


class CareerAgent:
    """
    Autonomous Career AI Agent
    """

    def __init__(self, llm_client):
        self.llm = llm_client

    def analyze_profile(self, skills, career_goal=None):
        """
        Returns next role suggestions as JSON
        """
        prompt = NEXT_ROLE_PROMPT.format(
            skills=", ".join(skills),
            career_goal=career_goal or "Not specified"
        )
        return self.llm.complete(prompt)

    def decide_next_roles(self, analysis_result):
        """
        Extract suggested roles from LLM JSON
        """
        return analysis_result.get("suggested_roles", [])

    def generate_study_plan(self, selected_role):
        """
        Generate a phase-wise study plan for a selected role
        """
        prompt = STUDY_PLAN_PROMPT.format(role=selected_role)
        return self.llm.complete(prompt)


def create_career_agent():
    """
    Factory method to initialize the career agent
    """
    llm_client = LLMClient()
    return CareerAgent(llm_client)
