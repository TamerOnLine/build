from __future__ import annotations
import streamlit as st

def render(profile: dict) -> dict:
    st.subheader("Key Skills")

    rev = st.session_state.get("profile_rev", 0)

    skills_list = profile.get("skills") or []
    skills_text = "\n".join(skills_list)

    skills_text = st.text_area(
        "List your main skills (one per line)",
        value=skills_text,
        height=140,
        placeholder="e.g., FastAPI\nStreamlit\nPostgreSQL\nDocker\nGitHub Actions",
        help="Each non-empty line will be saved as a separate skill.",
        key=f"skills_text_{rev}",
    )

    c1, c2, _ = st.columns([1, 1, 6])
    with c1:
        if st.button("💾 Save skills", key=f"skills_save_{rev}", width="stretch"):
            new_skills = [ln.strip() for ln in skills_text.splitlines() if ln.strip()]
            profile["skills"] = new_skills
            st.success("Skills updated.")
    with c2:
        if st.button("🧹 Clear", key=f"skills_clear_{rev}", width="stretch"):
            profile["skills"] = []
            st.experimental_rerun()

    with st.expander("Preview (list)", expanded=False):
        st.write(profile.get("skills") or [])

    return profile
