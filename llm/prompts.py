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
1. Identify 3 high-growth career trajectories for current year that maximize my earning potential and leverage my leadership/technical hybrid background based on input skills. 
2. role suggested should be having good openings on job boards 
3. For each role suggested: 
   - Explain why the user fits 
   - List missing skills that are commonly listed for the job description
   - For each missing skill:
      - Provide a learning resource
      - Use ONLY well-known platforms
      - Use homepage or official documentation URLs
      - Do NOT invent deep or course-specific URLs
      - If unsure, use a Google search link
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
