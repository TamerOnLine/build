from __future__ import annotations

from typing import Dict, List

import streamlit as st
from st_app.utils.profile_state import _ensure_list


COLS = ["title", "desc", "url"]
EMPTY: Dict[str, str] = {k: "" for k in COLS}

STATE_KEY = "projects_items"

def _coerce_in(value) -> List[Dict[str, str]]:
    """
    Normalize incoming profile['projects'] data to a list of dictionaries.

    Args:
        value: Incoming projects data from the profile.

    Returns:
        List[Dict[str, str]]: A list of normalized project entries.
    """
    if not value:
        return [EMPTY.copy()]
    if isinstance(value, list) and value and isinstance(value[0], dict):
        return [{k: (row.get(k) or "").strip() for k in COLS} for row in value]
    if isinstance(value, list) and value and isinstance(value[0], (list, tuple)):
        # Legacy [[title, desc, url], ...]
        out = []
        for row in value:
            t, d, u = (list(row) + ["", "", ""])[:3]
            out.append({
                "title": str(t or "").strip(),
                "desc": str(d or "").strip(),
                "url": str(u or "").strip(),
            })
        return out
    return [EMPTY.copy()]

def _clean(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Clean and filter out empty project entries.

    Args:
        rows (List[Dict[str, str]]): The list of project items.

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
    Render the 'Projects' tab for the Streamlit app.

    Args:
        profile (dict): The current user profile dictionary.

    Returns:
        dict: Updated profile with the cleaned projects section.
    """
    st.subheader("Projects")

    rev = st.session_state.get("profile_rev", 0)
    if STATE_KEY not in st.session_state:
        st.session_state[STATE_KEY] = _coerce_in(profile.get("projects"))

    items: List[Dict[str, str]] = st.session_state[STATE_KEY]

    top = st.columns([1, 1, 6])
    with top[0]:
        if st.button("+ Add Project", key=f"proj_add_{rev}"):
            items.append(EMPTY.copy())
    with top[1]:
        if st.button("\u274C Clear All", key=f"proj_clear_{rev}"):
            items.clear()
            items.append(EMPTY.copy())

    for i, row in enumerate(list(items)):
        with st.container(border=True):
            st.markdown(f"**Project #{i + 1}**")
            c1, c2 = st.columns(2)
            with c1:
                title = st.text_input(
                    "Title",
                    value=row.get("title", ""),
                    key=f"proj_title_{rev}_{i}",
                    placeholder="e.g., DeepClone",
                )
                url = st.text_input(
                    "URL",
                    value=row.get("url", ""),
                    key=f"proj_url_{rev}_{i}",
                    placeholder="https://github.com/...",
                )
            with c2:
                desc = st.text_area(
                    "Description",
                    value=row.get("desc", ""),
                    key=f"proj_desc_{rev}_{i}",
                    height=90,
                    placeholder="What it does / your role",
                )

            items[i] = {
                "title": title.strip(),
                "desc": desc.strip(),
                "url": url.strip(),
            }

            cc = st.columns([1, 1, 1, 6])
            with cc[0]:
                if st.button("\u2B06 Move up", key=f"proj_up_{rev}_{i}") and i > 0:
                    items[i - 1], items[i] = items[i], items[i - 1]
            with cc[1]:
                if st.button("\u2B07 Move down", key=f"proj_down_{rev}_{i}") and i < len(items) - 1:
                    items[i + 1], items[i] = items[i], items[i + 1]
            with cc[2]:
                if st.button("\u274C Delete", key=f"proj_del_{rev}_{i}"):
                    items.pop(i)
                    st.experimental_rerun()

    profile["projects"] = _clean(items)

    with st.expander("Preview (JSON-like)", expanded=False):
        st.write(profile["projects"])

    return profile

# --- Projects ---------------------------------------------------------------
def render_projects_section():
    st.header("Projects")

    _ensure_list("projects", [])
    colA, colB = st.columns([1,1], vertical_alignment="center")

    if colA.button("Add Project", key="prj_add", use_container_width=True):
        st.session_state.projects.append({"title":"", "desc":"", "url":""})

    if colB.button("Clear All", key="prj_clear_all", type="secondary", use_container_width=True):
        st.session_state.projects.clear()


    for i, it in enumerate(st.session_state.projects):
        with st.container(border=True):
            st.markdown(f"**Project #{i+1}**")
            c1, c2 = st.columns([1,1])
            it["title"] = c1.text_input("Title", value=it.get("title",""), key=f"prj_title_{i}")
            it["desc"]  = c2.text_area("Description", value=it.get("desc",""), key=f"prj_desc_{i}")
            it["url"]   = st.text_input("URL", value=it.get("url",""), key=f"prj_url_{i}", placeholder="https://github.com/...")

            b1, b2, b3 = st.columns([1,1,1])
            if b1.button("↑ Move up",   key=f"prj_up_{i}", use_container_width=True) and i>0:
                st.session_state.projects[i-1], st.session_state.projects[i] = st.session_state.projects[i], st.session_state.projects[i-1]
                st.rerun()
            if b2.button("↓ Move down", key=f"prj_dn_{i}", use_container_width=True) and i<len(st.session_state.projects)-1:
                st.session_state.projects[i+1], st.session_state.projects[i] = st.session_state.projects[i], st.session_state.projects[i+1]
                st.rerun()
            if b3.button("✖ Delete",    key=f"prj_del_{i}", use_container_width=True):
                st.session_state.projects.pop(i)
                st.rerun()

    with st.expander("Preview (JSON-like)", expanded=False):
        st.code(st.session_state.projects, language="json")

    # ترجع القائمة بصيغة الـAPI مباشرة
    return [{"title": p["title"].strip(),
             "desc":  p["desc"].strip(),
             "url":   (p["url"].strip() or None)} for p in st.session_state.projects]
