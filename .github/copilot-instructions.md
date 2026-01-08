# NextRole AI - Copilot Instructions

## Project Overview
**NextRole AI** is a Streamlit-based career guidance application that uses Azure OpenAI to analyze user skills and recommend career paths. It extracts skills from PDFs, generates role suggestions, and creates personalized study plans.

## Architecture

### Core Components

1. **Frontend (Streamlit)** - `app.py` + `pages/`
   - Multi-page navigation: Home page (skill input) → Study Plan page
   - State managed via `st.session_state` for skills, selected role, and career context
   - Pages reference: [home.py](pages/home.py) and [study_plan.py](pages/study_plan.py)

2. **LLM Layer** - `llm/` directory
   - **LLMClient** ([career_ai.py](llm/career_ai.py#L32)): Wraps Azure OpenAI with JSON parsing resilience
   - **CareerAgent** ([career_ai.py](llm/career_ai.py#L102)): Orchestrates three LLM operations:
     - `extract_skills()`: Parses resume text → skill list
     - `analyze_profile()`: Analyzes skills + context → 3-5 role suggestions
     - `generate_study_plan()`: Creates phase-wise learning plan for missing skills
   - Prompts: [prompts.py](llm/prompts.py) - system prompts for each operation

3. **Configuration** - TOML-based (no database)
   - [config.toml](config.toml): UI labels, colors, sizes, max upload limits (10MB PDFs)
   - [config_loader.py](config_loader.py): Loads and validates config at startup

4. **Utilities**
   - [resume_parser.py](utils/resume_parser.py): PDF text extraction (via `pypdf`)
   - [repository.py](memory/repository.py): In-memory progress tracking (placeholder for future persistence)

## Data Flow

```
User Input (Home)
  ↓
Resume PDF + Manual Skills + Career Goal + Experience Level
  ↓
LLMClient.extract_skills() → Skill array
  ↓
CareerAgent.analyze_profile(skills, context) → {roles: [...]}
  ↓
Select Role → Store in session_state["selected_role"]
  ↓
CareerAgent.generate_study_plan() → {phases: [...]}
  ↓
Display Study Plan (Study Plan Page)
```

## Key Patterns & Conventions

### JSON Resilience (Critical)
LLMClient uses multi-stage fallback for JSON parsing ([career_ai.py#L52-L88](llm/career_ai.py#L52-L88)):
1. Direct JSON parse
2. Extract from ```json ... ``` fences
3. Regex search for `{...}` objects
4. Regex search for `[...]` arrays
5. Log raw response, return `{}`

**Why**: Azure OpenAI sometimes wraps JSON in markdown fences. Always test with this in mind.

### Session State Pattern (Home → Study Plan)
- [home.py](pages/home.py#L40): Stores `skills`, context (experience_level, current_role) in `st.session_state`
- [study_plan.py](pages/study_plan.py#L8): Reads `st.session_state["selected_role"]` to build study plan
- Page switching: `st.switch_page("pages/home.py")` to reset flow

### Prompt Format Injection
Prompts use `.format()` placeholders: `{skills}`, `{career_goal}`, `{missing_skills}`, etc. ([career_ai.py#L110-L113](llm/career_ai.py#L110-L113))
- Always sanitize user input before injection
- Career goal and skills are comma-separated strings

### Configuration-Driven UI
All user-facing strings (labels, headers, placeholders) come from `config.toml` under `[ui]`, `[home]`, `[study_plan]` sections. Never hardcode UI text.

## Developer Workflows

### Run the App
```bash
streamlit run app.py
```
Starts on `http://localhost:8501`. Hot-reload enabled.

### Environment Setup
Required `.env` variables (Azure OpenAI):
```
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_DEPLOYMENT_NAME=...
```

### Dependencies
- **streamlit**: UI framework
- **openai**: Azure OpenAI SDK
- **pypdf**: Resume PDF parsing
- **python-dotenv**: Load .env
- **tomli**: Config file parsing (TOML)

### Testing & Debugging
- Logging configured in [app.py](app.py#L7-L10): Set `logging.basicConfig(level=logging.DEBUG)` for detailed traces
- LLMClient logs raw responses on JSON parse failure (see `logger.error` in [career_ai.py#L87](llm/career_ai.py#L87))
- Trace session state: `st.write(st.session_state)` to debug user context

## Integration Points

1. **Azure OpenAI**: Single point at [career_ai.py#L17-L21](llm/career_ai.py#L17-L21). Temperature=0.4 (low randomness for consistent career advice).
2. **User Input Validation**: 
   - PDF max 10MB ([config.toml](config.toml#L6))
   - Skills normalized to arrays (duplicates implicit from LLM output)
3. **Error Handling**: 
   - PDF extraction failures return empty string, gracefully handled in [home.py](pages/home.py#L45-L49)
   - LLM response failures logged, UI shows "No roles found"

## Important Notes for Contributors

- **No database**: Session state is ephemeral. Refresh = data loss. [repository.py](memory/repository.py) is a placeholder.
- **LLM is the core**: All intelligence comes from prompts. Tuning [prompts.py](llm/prompts.py) has high impact.
- **Config-first**: Add new UI elements in `config.toml` first, then reference in Python.
- **Logging**: Use `logging.getLogger(__name__)` in all modules. Helps production debugging.
