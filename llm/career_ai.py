# llm/career_ai.py

import os
import json
import re
import streamlit as st
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

import logging
logger = logging.getLogger(__name__)
logger.info("LLM client module initialized")

class LLMClient:
    """
    LLM Client for making real calls to Azure OpenAI
    """

    def complete(self, prompt):
        """
        Calls the real LLM and returns parsed JSON
        """
        logger.debug("Sending prompt to LLM (len=%d)", len(prompt))
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        raw_content = response.choices[0].message.content.strip()
        self.last_raw_response = raw_content
        logger.debug("Received raw response from LLM (len=%d)", len(raw_content))

        # Attempt to parse JSON from response directly
        try:
            parsed = json.loads(raw_content)
            logger.debug("Parsed JSON response successfully")
            return parsed
        except json.JSONDecodeError:
            logger.warning("LLM returned non-JSON response; attempting heuristic extraction")

        # Try to extract JSON from fenced code blocks (```json ... ``` or ``` ... ```)
        fence_match = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", raw_content, re.DOTALL | re.IGNORECASE)
        if fence_match:
            try:
                parsed = json.loads(fence_match.group(1))
                logger.debug("Parsed JSON from fenced code block")
                return parsed
            except json.JSONDecodeError:
                logger.exception("Failed to parse JSON from fenced code block; continuing fallback")

        # Try to find a JSON object {...} non-greedily
        obj_match = re.search(r"\{.*?\}", raw_content, re.DOTALL)
        if obj_match:
            try:
                parsed = json.loads(obj_match.group())
                logger.debug("Parsed JSON from first JSON object in response")
                return parsed
            except json.JSONDecodeError:
                logger.exception("Failed to parse JSON from first object; continuing fallback")

        # Try to find a top-level JSON array [ ... ]
        arr_match = re.search(r"\[.*?\]", raw_content, re.DOTALL)
        if arr_match:
            try:
                parsed = json.loads(arr_match.group())
                logger.debug("Parsed JSON array from response")
                return parsed
            except json.JSONDecodeError:
                logger.exception("Failed to parse JSON array from response")

        # Last resort: log the raw response for debugging and return empty dict
        logger.error("No parsable JSON found in LLM response. Raw content: %s", raw_content[:1000])
        return {}

    def extract_skills(self, resume_text):
        """
        Extract skills from resume text using LLM
        """
        logger.info("Extracting skills from resume text (chars=%d)", len(resume_text) if resume_text else 0)
        prompt = SKILL_EXTRACTION_PROMPT + resume_text
        result = self.complete(prompt)
        logger.debug("Skill extraction result: %s", str(result)[:200])
        return result


class CareerAgent:
    """
    Autonomous Career AI Agent
    """

    def __init__(self, llm_client):
        self.llm = llm_client

    def analyze_profile(self, skills, career_goal=None, experience_level=None, current_role=None):
        """
        Returns next role suggestions as JSON. `skills` should be a list of skill strings.
        Accepts optional `experience_level` (student/entry/mid/senior) and `current_role` to provide more context to the model.
        """
        skills_str = ", ".join(skills) if isinstance(skills, (list, tuple)) else str(skills)
        prompt = NEXT_ROLE_PROMPT.format(
            skills=skills_str,
            career_goal=career_goal or "Not specified",
            experience_level=experience_level or "Not specified",
            current_role=current_role or "Not specified"
        )

        logger.debug("Analyzing profile with experience_level=%s current_role=%s", experience_level, current_role)

        result = self.llm.complete(prompt)

        # If response didn't include roles, retry once with a strict JSON-only instruction
        if not result or not isinstance(result, dict) or "roles" not in result:
            logger.warning("LLM did not return 'roles' in first response; retrying with strict JSON instruction")
            retry_prompt = prompt + "\n\nIMPORTANT: Reply with valid JSON only (no surrounding text) matching the requested schema exactly."
            result = self.llm.complete(retry_prompt)

            if not result or not isinstance(result, dict) or "roles" not in result:
                logger.error("LLM failed to provide roles after retry. Raw response (truncated): %s", str(getattr(self.llm, 'last_raw_response', ''))[:1000])

        return result

    def decide_next_roles(self, analysis_result):
        """
        Extract suggested roles from LLM JSON
        """
        return analysis_result.get("roles", [])

    def generate_study_plan(self, selected_role, current_skills=None):
        """
        Generate a phase-wise study plan for a selected role, focusing on missing skills.
        `selected_role` is expected to be a dict with keys: "role", and optionally "missing_skills".
        """
        role_name = selected_role.get("role") if isinstance(selected_role, dict) else str(selected_role)
        missing = selected_role.get("missing_skills", []) if isinstance(selected_role, dict) else []
        current_skills = current_skills or []

        prompt = STUDY_PLAN_PROMPT.format(
            role=role_name,
            current_skills=", ".join(current_skills),
            missing_skills=", ".join(missing)
        )
        return self.llm.complete(prompt)


def create_career_agent():
    """
    Factory method to initialize the career agent
    """
    llm_client = LLMClient()
    return CareerAgent(llm_client)
