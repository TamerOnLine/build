from __future__ import annotations
import streamlit as st

def render(profile: dict) -> dict:
    st.subheader("Professional Summary")

    rev = st.session_state.get("profile_rev", 0)

    # Read existing list and present as multiline text
    summary_list = profile.get("summary") or []
    summary_text = "\n".join(summary_list)

    summary_text = st.text_area(
        "Short introduction about yourself",
        value=summary_text,
        height=140,
        placeholder="e.g., Passionate software developer with 5+ years of experience...",
        help="Write multiple lines. Each line will become a separate bullet/paragraph.",
        key=f"summary_text_{rev}",
    )

    c1, c2, _ = st.columns([1, 1, 6])
    with c1:
        if st.button("💾 Save summary", key=f"summary_save_{rev}", width="stretch"):
            # split to list[str]
            lines = [ln.strip() for ln in summary_text.splitlines() if ln.strip()]
            profile["summary"] = lines
            st.success("Summary updated.")
    with c2:
        if st.button("🧹 Clear", key=f"summary_clear_{rev}", width="stretch"):
            profile["summary"] = []
            st.experimental_rerun()

    with st.expander("Preview (list)", expanded=False):
        st.write(profile.get("summary") or [])

    return profile
