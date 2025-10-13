from __future__ import annotations

import copy
from typing import Any

import streamlit as st

from st_app.config.ui_defaults import (
    PH_FULL_NAME,
    PH_TITLE,
    MAX_NAME,
    MAX_TITLE,
)

def _trim(x: Any) -> str:
    """
    Return a trimmed string version of the input.

    Args:
        x (Any): The input value to be trimmed.

    Returns:
        str: A stripped string if input is not None; otherwise, an empty string.
    """
    return "" if x is None else str(x).strip()

def render(profile: dict) -> dict:
    """
    Render the 'Basic Info' tab in a Streamlit app.

    Args:
        profile (dict): The current profile data.

    Returns:
        dict: The updated profile dictionary after potential changes.

    Notes:
        - Uses a form to update basic profile info (name and title).
        - Updates session state on real changes to ensure consistency.
    """
    st.subheader("Basic Info")
    rev = st.session_state.get("profile_rev", 0)

    # Initial values from profile.header
    header = dict(profile.get("header") or {})
    name_init = _trim(header.get("name"))
    title_init = _trim(header.get("title"))

    # -------- UI Form --------
    with st.form(key=f"basic_info_form_{rev}", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            st.text_input(
                "Full Name",
                value=name_init,
                key=f"name_{rev}",
                placeholder=f"e.g., {PH_FULL_NAME}",
                help="Your full name as it should appear on the PDF.",
                max_chars=MAX_NAME,
            )
        with c2:
            st.text_input(
                "Title",
                value=title_init,
                key=f"title_{rev}",
                placeholder=f"e.g., {PH_TITLE}",
                help="One-line professional title or tagline.",
                max_chars=MAX_TITLE,
            )

        submitted = st.form_submit_button("Save basic info")

    if not submitted:
        return profile

    # -------- After submit: read current values --------
    name = _trim(st.session_state.get(f"name_{rev}", name_init))
    title = _trim(st.session_state.get(f"title_{rev}", title_init))

    changed = (name != name_init) or (title != title_init)

    new_profile = copy.deepcopy(profile)
    new_profile.setdefault("header", {})
    new_profile["header"]["name"] = name
    new_profile["header"]["title"] = title

    st.session_state["name"] = name
    st.session_state["title"] = title
    st.session_state["profile"] = new_profile

    if changed:
        st.session_state["profile_rev"] = rev + 1
        st.success("Basic info updated.")
    else:
        st.info("No changes detected.")

    return new_profile
