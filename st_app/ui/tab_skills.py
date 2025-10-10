from __future__ import annotations
import streamlit as st
from core.io_utils import to_lines
from st_app.config.ui_defaults import (
    SKILLS_TEXTAREA_LABEL,
    SKILLS_TEXTAREA_HEIGHT,
)

def render(profile: dict) -> dict:
    """
    Render the 'Skills' tab and return the updated profile dictionary.
    Mimics tab_basic.py style — transparent defaults and placeholders only.
    """
    st.subheader("Skills")
    rev = st.session_state.get("profile_rev", 0)

    # Get current skills safely
    skills = profile.get("skills") or []

    with st.form(key=f"skills_form_{rev}", clear_on_submit=False):
        skills_text = st.text_area(
            SKILLS_TEXTAREA_LABEL,
            value="\n".join(skills),
            key=f"skills_text_{rev}",
            height=SKILLS_TEXTAREA_HEIGHT,
            placeholder="e.g., Python, FastAPI, Docker, PostgreSQL...",
            help="Enter one skill per line. Leave empty if not ready.",
        )

        submitted = st.form_submit_button("Save skills")

    if submitted:
        new_skills = to_lines(skills_text)
        profile["skills"] = new_skills
        st.success("Skills updated." if new_skills != skills else "No changes detected.")

    return profile
