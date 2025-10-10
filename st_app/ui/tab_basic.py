# streamlit/ui/tab_basic.py
from __future__ import annotations
from typing import Tuple, Dict, Any
import copy
import streamlit as st

from st_app.config.ui_defaults import (
    PH_FULL_NAME, PH_TITLE, MAX_NAME, MAX_TITLE
)




def _trim(s: Any) -> str:
    return "" if s is None else str(s).strip()

def render(profile: dict) -> dict:
    """
    Render 'Basic Info' tab and return the (possibly) updated profile dict.
    Mutates 'profile' minimally; uses a form to avoid partial reruns.
    """
    st.subheader("Basic Info")
    rev = st.session_state.get("profile_rev", 0)

    # Ensure header exists without clobbering other keys
    header = dict(profile.get("header") or {})
    name_init = _trim(header.get("name"))
    title_init = _trim(header.get("title"))

    changed = False
    with st.form(key=f"basic_info_form_{rev}", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input(
                "Full Name",
                value=name_init,
                key=f"name_{rev}",
                placeholder=f"e.g., {PH_FULL_NAME}",
                help="Your full name as it should appear on the PDF.",
                max_chars=MAX_NAME,
            )
        with c2:
            title = st.text_input(
                "Title",
                value=title_init,
                key=f"title_{rev}",
                placeholder=f"e.g., {PH_TITLE}",
                help="One-line professional title or tagline.",
                max_chars=MAX_TITLE,
            )

        submitted = st.form_submit_button("Save basic info")

    if submitted:
        name = _trim(st.session_state.get(f"name_{rev}", name_init))
        title = _trim(st.session_state.get(f"title_{rev}", title_init))

        if name != name_init or title != title_init:
            changed = True
            # bump rev so other keyed widgets can refresh if you rely on this pattern
            st.session_state["profile_rev"] = rev + 1

        # write back into profile
        profile = copy.deepcopy(profile)  # avoid surprising outer mutation
        profile.setdefault("header", {})
        profile["header"]["name"] = name
        profile["header"]["title"] = title

        if changed:
            st.success("Basic info updated.")
        else:
            st.info("No changes detected.")

    return profile
