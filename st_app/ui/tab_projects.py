from __future__ import annotations
from typing import List
import copy, re
import streamlit as st

from st_app.config.ui_defaults import (
    PROJECTS_HELP_TITLE,
    PROJECTS_HELP_DESC,
    PROJECTS_HELP_URL,
)

URL_SCHEME_RE = re.compile(r"^[a-z]+://", re.IGNORECASE)

def _s(x) -> str:
    return "" if x is None else str(x).strip()

def _norm_url(u: str) -> str:
    u = _s(u)
    if not u:
        return ""
    # prefix https:// إذا كان شبيهًا بنطاق بدون مخطط
    if not URL_SCHEME_RE.match(u) and "." in u.split("/")[0]:
        return f"https://{u}"
    return u

def _normalize_items(items: List[List[str]]) -> List[List[str]]:
    out: List[List[str]] = []
    for row in items:
        t, d, u = (row + ["", "", ""])[:3]
        t, d, u = _s(t), _s(d), _norm_url(u)
        if t or d or u:
            out.append([t, d, u])
    return out


def render(profile: dict) -> dict:
    st.subheader("Projects")
    st.caption("Add projects with a detailed multi-paragraph description and optional link.")

    rev = st.session_state.get("profile_rev", 0)
    key_items = f"projects_items_{rev}"

    current = copy.deepcopy(profile.get("projects") or [])
    if key_items not in st.session_state:
        st.session_state[key_items] = current if current else []

    # زر إضافة مشروع
    if st.button("➕ Add project", key=f"btn_add_proj_{rev}"):
        st.session_state[key_items].append(["", "", ""])
        st.rerun()

    items = st.session_state[key_items]

    if not items:
        st.info("No projects yet. Click **Add project** to start.")
    else:
        with st.form(key=f"projects_form_{rev}", clear_on_submit=False):
            remove_indexes = []

            for i, row in enumerate(items):
                title, desc, url = (row + ["", "", ""])[:3]
                with st.container(border=True):
                    st.text_input(
                        "Title",
                        value=title,
                        key=f"proj_title_{rev}_{i}",
                        help=PROJECTS_HELP_TITLE,
                        placeholder="e.g., CVEngine — Dynamic Resume Generator",
                    )

                    # ✅ وصف متعدد الفقرات
                    st.text_area(
                        "Description (multi-paragraph)",
                        value=desc,
                        key=f"proj_desc_{rev}_{i}",
                        help=PROJECTS_HELP_DESC,
                        placeholder=(
                            "Describe your project in detail:\n"
                            "- Purpose and scope\n"
                            "- Key features or technologies\n"
                            "- Achievements or results"
                        ),
                        height=180,
                    )

                    st.text_input(
                        "URL (optional)",
                        value=url,
                        key=f"proj_url_{rev}_{i}",
                        help=PROJECTS_HELP_URL,
                        placeholder="e.g., https://github.com/TamerOnLine/CVEngine",
                    )

                    st.markdown("")
                    if st.form_submit_button(
                        "🗑️ Delete this project",
                        type="secondary",
                        use_container_width=True,
                        key=f"rm_{rev}_{i}",
                    ):
                        remove_indexes.append(i)

            # حذف المشاريع المحددة
            if remove_indexes:
                for idx in sorted(remove_indexes, reverse=True):
                    items.pop(idx)

            st.markdown("---")
            submitted = st.form_submit_button("💾 Save projects")

        if submitted:
            rows = _normalize_items(
                [
                    [
                        _s(st.session_state.get(f"proj_title_{rev}_{i}", "")),
                        _s(st.session_state.get(f"proj_desc_{rev}_{i}", "")),
                        _s(st.session_state.get(f"proj_url_{rev}_{i}", "")),
                    ]
                    for i in range(len(items))
                ]
            )
            changed = rows != (profile.get("projects") or [])
            profile["projects"] = rows
            st.session_state[key_items] = copy.deepcopy(rows)

            if changed:
                st.session_state["profile_rev"] = rev + 1
                st.success("Projects updated.")
            else:
                st.info("No changes detected.")

    return profile
