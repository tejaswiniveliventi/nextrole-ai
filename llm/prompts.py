# llm/prompts.py

SKILL_EXTRACTION_PROMPT = """
Extract a clean list of professional skills from the resume text below.
Return ONLY a comma-separated list of skills.
No explanations.

Resume:
"""

NEXT_ROLE_WITH_LINKS_PROMPT = """
You are a career intelligence assistant.  
Input is a list of professional skills.

Your task:
1. Suggest up to 3 realistic next roles
2. For each role:
   - Explain why the user fits
   - List missing skills
   - For each missing skill provide ONE helpful link (YouTube or official site) for learning
   - Give a simple 90-day learning plan

Respond in strict JSON only:

{{
  "suggested_roles": [
    {{
      "role": "Role name",
      "why_fit": "Plain text explanation.",
      "missing_skills": [
          {{
            "skill": "Skill name",
            "learning_link": "https://..."
          }}
      ],
      "learning_plan_90_days": ["Step 1", "Step 2"]
    }}
  ]
}}

Rules:
- Do NOT include HTML or Markdown outside JSON
- Provide only ONE link per missing skill

Skills text:
{skills}
"""
