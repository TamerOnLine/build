# st_app/ui/tab_summary.py
from __future__ import annotations
import streamlit as st
from typing import Dict, Any

from st_app.config.ui_defaults import (
    PH_SUMMARY,
    SUMMARY_TEXTAREA_HEIGHT,
)

def render(profile: Dict[str, Any]) -> Dict[str, Any]:
    st.subheader("Summary / About Me")
    rev = st.session_state.get("profile_rev", 0)

    # 1) طبّع القيمة الحالية: قد تكون نصًا أو قائمة أسطر
    current_raw = profile.get("summary") or ""
    if isinstance(current_raw, list):
        current = " ".join(str(x) for x in current_raw if str(x).strip()).strip()
    else:
        current = str(current_raw).strip()

    with st.form(key=f"summary_form_{rev}", clear_on_submit=False):
        # 2) خذ من session_state، وإلا استخدم قيمة البروفايل الحالية
        summary_init = st.session_state.get("summary", current)

        summary_text = st.text_area(
            "Professional Summary",
            value=summary_init,
            height=SUMMARY_TEXTAREA_HEIGHT,
            placeholder=PH_SUMMARY,
            key=f"summary_{rev}",   # 3) مفتاح مستقر مرتبط بـ rev
        )
        submitted = st.form_submit_button("Save summary")

    if submitted:
        new_val = summary_text.strip()
        if new_val != current:
            # 4) حدّث البروفايل وحالة الجلسة وزِد المراجعة
            profile["summary"] = new_val
            st.session_state["summary"] = new_val
            st.session_state["profile_rev"] = rev + 1
            st.success("Summary updated.")
        else:
            st.info("No changes detected.")

    return profile
