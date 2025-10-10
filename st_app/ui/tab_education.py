from __future__ import annotations
from typing import List, Any
import copy, re
import streamlit as st
from st_app.config.ui_defaults import (
    EDU_COLUMNS,
    EDU_HELP_TITLE,
    EDU_HELP_SCHOOL,
    EDU_HELP_START,
    EDU_HELP_END,
    EDU_HELP_DETAILS,
    EDU_HELP_URL,
    DATE_HINT,
    EDU_URL_HELP,
)

URL_RE = re.compile(r"^[a-z]+://", re.IGNORECASE)

def _s(x: Any) -> str:
    return "" if x is None else str(x).strip()

def _norm_url(u: str) -> str:
    u = _s(u)
    if not u:
        return ""
    if not URL_RE.match(u) and "." in u.split("/")[0]:
        return f"https://{u}"
    return u

def _normalize_items(items: List[List[str]]) -> List[List[str]]:
    out: List[List[str]] = []
    for row in items:
        t, s_, start, end, details, url = (row + ["", "", "", "", "", ""])[:6]
        t, s_, start, end, details, url = _s(t), _s(s_), _s(start), _s(end), _s(details), _norm_url(url)
        if any([t, s_, start, end, details, url]):
            out.append([t, s_, start, end, details, url])
    return out

def render(profile: dict) -> dict:
    st.subheader("Education / Training")
    st.caption("Add entries one by one. Use multi-paragraph details if needed.")

    rev = st.session_state.get("profile_rev", 0)
    key_items = f"edu_items_{rev}"
    current = copy.deepcopy(profile.get("education") or [])

    if key_items not in st.session_state:
        st.session_state[key_items] = current if current else []

    if st.button("➕ Add entry", key=f"btn_add_edu_{rev}"):
        st.session_state[key_items].append(["", "", "", "", "", ""])
        st.rerun()

    items = st.session_state[key_items]

    if not items:
        st.info("No education entries yet. Click **Add entry** to start.")
    else:
        with st.form(key=f"education_form_{rev}", clear_on_submit=False):
            remove = []
            for i, row in enumerate(items):
                title, school, start, end, details, url = (row + ["", "", "", "", "", ""])[:6]
                with st.container(border=True):
                    st.text_input(
                        "Title / Program",
                        value=title,
                        key=f"edu_title_{rev}_{i}",
                        placeholder=f"e.g., {EDU_HELP_TITLE}",
                        help="Degree, program, or course name.",
                    )
                    st.text_input(
                        "School",
                        value=school,
                        key=f"edu_school_{rev}_{i}",
                        placeholder=f"e.g., {EDU_HELP_SCHOOL}",
                        help="Institution or academy.",
                    )
                    st.text_input(
                        "Start",
                        value=start,
                        key=f"edu_start_{rev}_{i}",
                        placeholder=f"e.g., {EDU_HELP_START}",
                        help=DATE_HINT,
                    )
                    st.text_input(
                        "End",
                        value=end,
                        key=f"edu_end_{rev}_{i}",
                        placeholder=f"e.g., {EDU_HELP_END}",
                        help=f"{DATE_HINT} or 'Present'",
                    )
                    st.text_area(
                        "Details (multi-paragraph)",
                        value=details,
                        key=f"edu_details_{rev}_{i}",
                        placeholder=f"e.g., {EDU_HELP_DETAILS}",
                        help="Write multiple lines/paragraphs if needed.",
                        height=150,
                    )
                    st.text_input(
                        "URL (optional)",
                        value=url,
                        key=f"edu_url_{rev}_{i}",
                        placeholder=f"e.g., {EDU_HELP_URL}",
                        help=EDU_URL_HELP,
                    )
                    if st.form_submit_button(
                        "🗑️ Delete this entry",
                        type="secondary",
                        use_container_width=True,
                        key=f"rm_edu_{rev}_{i}",
                    ):
                        remove.append(i)

            if remove:
                for idx in sorted(remove, reverse=True):
                    items.pop(idx)

            st.markdown("---")
            submitted = st.form_submit_button("💾 Save education")

        if submitted:
            rows = _normalize_items(
                [
                    [
                        _s(st.session_state.get(f"edu_title_{rev}_{i}", "")),
                        _s(st.session_state.get(f"edu_school_{rev}_{i}", "")),
                        _s(st.session_state.get(f"edu_start_{rev}_{i}", "")),
                        _s(st.session_state.get(f"edu_end_{rev}_{i}", "")),
                        _s(st.session_state.get(f"edu_details_{rev}_{i}", "")),
                        _s(st.session_state.get(f"edu_url_{rev}_{i}", "")),
                    ]
                    for i in range(len(items))
                ]
            )
            changed = rows != (profile.get("education") or [])
            profile["education"] = rows
            st.session_state[key_items] = copy.deepcopy(rows)

            if changed:
                st.session_state["profile_rev"] = rev + 1
                st.success("Education updated.")
            else:
                st.info("No changes detected.")
    return profile
