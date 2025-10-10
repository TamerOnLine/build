from __future__ import annotations
import streamlit as st
from core.io_utils import to_lines
from st_app.config.ui_defaults import (
    LANGUAGES_TEXTAREA_LABEL,
    LANGUAGES_TEXTAREA_HEIGHT,
    LANG_COLUMNS
)

def render(profile: dict) -> dict:
    """
    Render the 'Languages' tab with transparent defaults (no prefilled values).
    Mirrors tab_basic form behavior.
    """
    st.subheader("Languages")
    rev = st.session_state.get("profile_rev", 0)

    # current languages (empty by default = transparent)
    langs = profile.get("languages") or []

    with st.form(key=f"languages_form_{rev}", clear_on_submit=False):
        langs_text = st.text_area(
            LANGUAGES_TEXTAREA_LABEL,
            value="\n".join(langs),
            key=f"languages_text_{rev}",
            height=LANGUAGES_TEXTAREA_HEIGHT,
            placeholder=f"e.g., {LANG_COLUMNS}",
            help="One per line: Language — Level (e.g., Arabic — Native, English — B1).",
        )
        submitted = st.form_submit_button("Save languages")

    if submitted:
        new_langs = to_lines(langs_text)
        changed = new_langs != langs
        profile["languages"] = new_langs

        if changed:
            st.session_state["profile_rev"] = rev + 1
            st.success("Languages updated.")
        else:
            st.info("No changes detected.")

    return profile
