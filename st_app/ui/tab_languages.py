from __future__ import annotations

import streamlit as st

from core.io_utils import to_lines

from st_app.config.ui_defaults import (
    LANGUAGES_TEXTAREA_LABEL, LANGUAGES_TEXTAREA_HEIGHT
)

def render(profile: dict) -> dict:
    """
    Render the Languages tab in the Streamlit UI.

    Args:
        profile (dict): The user's profile data.

    Returns:
        dict: Updated profile dictionary with parsed languages.
    """
    st.subheader("Languages")
    rev = st.session_state.get("profile_rev", 0)

    key = f"languages_text_{rev}"
    default = "\n".join(profile.get("languages") or [])
    st.session_state.setdefault(key, default)

    langs_text = st.text_area(
        LANGUAGES_TEXTAREA_LABEL,
        key=key,
        height=LANGUAGES_TEXTAREA_HEIGHT,
    )

    profile["languages"] = to_lines(langs_text)
    return profile
