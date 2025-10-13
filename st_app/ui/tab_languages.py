from __future__ import annotations
import streamlit as st

def render_languages_tab():
    st.subheader("Languages")
    text = st.text_area(
        "One language per line (optionally with level)",
        value="\n".join(st.session_state.profile.get("languages", []) or []),
        height=120,
    )
    langs = [ln.strip() for ln in text.splitlines() if ln.strip()]
    st.session_state.profile["languages"] = langs

    st.caption("Example:\nArabic (Native)\nEnglish (B2)\nGerman (A2)")
    return langs
