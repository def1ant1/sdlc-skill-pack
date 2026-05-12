# Assistant Workspace

Primary top-level app surface for unified operator workflows.

## Panels
- Conversation
- Working Plan
- Artifacts
- Knowledge / Memory

All panels share one Streamlit session context (`st.session_state.workspace`).

## Navigation model
- Assistant Home
- Plan Builder
- Workflow Studio
- Skill Library
- Knowledge Base
- Task & Schedule Center

## Run

```bash
streamlit run apps/assistant-workspace/streamlit_app.py
```
