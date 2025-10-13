from __future__ import annotations

from typing import Dict, List

import streamlit as st

COLS = ["title", "school", "start", "end", "details", "url"]
EMPTY: Dict[str, str] = {k: "" for k in COLS}

STATE_KEY = "education_items"

def _coerce_in(value) -> List[Dict[str, str]]:
    """
    Normalize incoming profile['education'] data to a list of dictionaries.

    Args:
        value: Incoming education data from the profile.

    Returns:
        List[Dict[str, str]]: A list of normalized education entries.
    """
    if not value:
        return [EMPTY.copy()]
    if isinstance(value, list) and value and isinstance(value[0], dict):
        return [{k: (row.get(k) or "").strip() for k in COLS} for row in value]
    if isinstance(value, list) and value and isinstance(value[0], (list, tuple)):
        # Legacy [[title, school, start, end, details, url], ...]
        out = []
        for row in value:
            t, s, a, e, d, u = (list(row) + ["", "", "", "", "", ""])[:6]
            out.append({
                "title": str(t or "").strip(),
                "school": str(s or "").strip(),
                "start": str(a or "").strip(),
                "end": str(e or "").strip(),
                "details": str(d or "").strip(),
                "url": str(u or "").strip(),
            })
        return out
    return [EMPTY.copy()]

def _clean(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Clean and filter out empty education entries.

    Args:
        rows (List[Dict[str, str]]): The list of education items.

    Returns:
        List[Dict[str, str]]: A cleaned list with at least one non-empty entry.
    """
    out = []
    for r in rows:
        item = {k: (r.get(k) or "").strip() for k in COLS}
        if any(item.values()):
            out.append(item)
    return out or [EMPTY.copy()]

def render(profile: dict) -> dict:
    """
    Render the 'Education / Training' tab for the Streamlit app.

    Args:
        profile (dict): The current user profile dictionary.

    Returns:
        dict: Updated profile with the cleaned education section.
    """
    st.subheader("Education / Training")

    rev = st.session_state.get("profile_rev", 0)
    if STATE_KEY not in st.session_state:
        st.session_state[STATE_KEY] = _coerce_in(profile.get("education"))

    items: List[Dict[str, str]] = st.session_state[STATE_KEY]

    top = st.columns([1, 1, 6])
    with top[0]:
        if st.button("+ Add Education", key=f"edu_add_{rev}"):
            items.append(EMPTY.copy())
    with top[1]:
        if st.button("\u274C Clear All", key=f"edu_clear_{rev}"):
            items.clear()
            items.append(EMPTY.copy())

    for i, row in enumerate(list(items)):
        with st.container(border=True):
            st.markdown(f"**Entry #{i + 1}**")
            c1, c2 = st.columns(2)
            with c1:
                title = st.text_input(
                    "Degree / Program",
                    value=row.get("title", ""),
                    key=f"edu_title_{rev}_{i}",
                    placeholder="e.g., B.Sc. Computer Science",
                )
                start = st.text_input(
                    "Start",
                    value=row.get("start", ""),
                    key=f"edu_start_{rev}_{i}",
                    placeholder="YYYY or YYYY-MM",
                )
                details = st.text_area(
                    "Details",
                    value=row.get("details", ""),
                    key=f"edu_details_{rev}_{i}",
                    height=90,
                    placeholder="Notes, grade, focus",
                )
            with c2:
                school = st.text_input(
                    "School / Institution",
                    value=row.get("school", ""),
                    key=f"edu_school_{rev}_{i}",
                    placeholder="e.g., Arden University Berlin",
                )
                end = st.text_input(
                    "End",
                    value=row.get("end", ""),
                    key=f"edu_end_{rev}_{i}",
                    placeholder="YYYY or YYYY-MM",
                )
                url = st.text_input(
                    "URL",
                    value=row.get("url", ""),
                    key=f"edu_url_{rev}_{i}",
                    placeholder="Program/institution link",
                )

            items[i] = {
                "title": title.strip(),
                "school": school.strip(),
                "start": start.strip(),
                "end": end.strip(),
                "details": details.strip(),
                "url": url.strip(),
            }

            cc = st.columns([1, 1, 1, 6])
            with cc[0]:
                if st.button("\u2B06 Move up", key=f"edu_up_{rev}_{i}") and i > 0:
                    items[i - 1], items[i] = items[i], items[i - 1]
            with cc[1]:
                if st.button("\u2B07 Move down", key=f"edu_down_{rev}_{i}") and i < len(items) - 1:
                    items[i + 1], items[i] = items[i], items[i + 1]
            with cc[2]:
                if st.button("\u274C Delete", key=f"edu_del_{rev}_{i}"):
                    items.pop(i)
                    st.experimental_rerun()

    profile["education"] = _clean(items)

    with st.expander("Preview (JSON-like)", expanded=False):
        st.write(profile["education"])

    return profile
