# st_app/ui/tab_basic.py
from __future__ import annotations
from typing import Any
import copy
import streamlit as st

from st_app.config.ui_defaults import (
    PH_FULL_NAME, PH_TITLE, MAX_NAME, MAX_TITLE
)

def _trim(x: Any) -> str:
    return "" if x is None else str(x).strip()

def render(profile: dict) -> dict:
    """
    Render 'Basic Info' tab and return the (possibly) updated profile dict.
    Uses a form; bumps profile_rev on real changes (same idea as tab_contact).
    Also saves stable copies into session_state (name/title/profile) so the sidebar
    can always read latest values regardless of rev bumps.
    """
    st.subheader("Basic Info")
    rev = st.session_state.get("profile_rev", 0)

    # initial values from profile.header
    header = dict(profile.get("header") or {})
    name_init  = _trim(header.get("name"))
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
        # لا تغيير على البروفايل إن لم يتم الإرسال
        return profile

    # -------- After submit: read current values --------
    name  = _trim(st.session_state.get(f"name_{rev}", name_init))
    title = _trim(st.session_state.get(f"title_{rev}", title_init))

    changed = (name != name_init) or (title != title_init)

    # اكتب القيم داخل profile["header"] دائمًا
    new_profile = copy.deepcopy(profile)
    new_profile.setdefault("header", {})
    new_profile["header"]["name"]  = name
    new_profile["header"]["title"] = title

    # ✅ ثبّت نسخ بدون rev داخل session_state لالتقاطها من الشريط الجانبي بسهولة
    st.session_state["name"] = name
    st.session_state["title"] = title
    st.session_state["profile"] = new_profile  # ليتأكد sidebar من أحدث نسخة

    # آلية Contact نفسها: نرفع rev فقط إذا كان هناك تغيير
    if changed:
        st.session_state["profile_rev"] = rev + 1
        st.success("Basic info updated.")
    else:
        st.info("No changes detected.")

    return new_profile
