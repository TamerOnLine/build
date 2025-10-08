# streamlit/ui/tab_projects.py
from __future__ import annotations
from typing import List
import re

import pandas as pd
import streamlit as st
from core.io_utils import projects_df_to_list

from st_app.config.ui_defaults import (
    PROJECT_COLUMNS, PROJECTS_HELP_TITLE, PROJECTS_HELP_DESC, PROJECTS_HELP_URL
)

COLUMNS = PROJECT_COLUMNS
URL_SCHEME_RE = re.compile(r"^[a-z]+://", re.IGNORECASE)

def _s(x) -> str:
    return "" if x is None else str(x).strip()

def _norm_url(u: str) -> str:
    u = _s(u)
    if not u:
        return ""
    # If user typed a domain without scheme, prefix https://
    if not URL_SCHEME_RE.match(u) and "." in u.split("/")[0]:
        return f"https://{u}"
    return u

def _ensure_df(existing: List[List[str]] | None) -> pd.DataFrame:
    if existing and isinstance(existing, list):
        return pd.DataFrame(existing, columns=COLUMNS)
    return pd.DataFrame([{c: "" for c in COLUMNS}])

def _drop_trailing_blank_rows(rows: List[List[str]]) -> List[List[str]]:
    i = len(rows) - 1
    while i >= 0 and all(_s(c) == "" for c in rows[i]):
        i -= 1
    rows = rows[: i + 1]
    return rows or [["", "", ""]]

def _normalize_items(items: List[List[str]]) -> List[List[str]]:
    out: List[List[str]] = []
    for row in items:
        t, d, u = (row + ["", "", ""])[:3]
        t, d, u = _s(t), _s(d), _norm_url(_s(u))
        if t or d or u:
            out.append([t, d, u])
        else:
            out.append(["", "", ""])  # keep for potential editing; pruned later
    return _drop_trailing_blank_rows(out)

def render(profile: dict) -> dict:
    st.subheader("Projects")
    rev = st.session_state.get("profile_rev", 0)

    df = _ensure_df(profile.get("projects"))
    st.caption("List projects with a short description and (optionally) a link.")

    edited = st.data_editor(
        df,
        num_rows="dynamic",
        key=f"projects_editor_{rev}",
        width="stretch",
        column_config={
            "Title": st.column_config.TextColumn(width="large", help=PROJECTS_HELP_TITLE),
            "Description": st.column_config.TextColumn(width="large", help=PROJECTS_HELP_DESC),
            "URL": st.column_config.LinkColumn(help=PROJECTS_HELP_URL),
        },
    )

    rows = projects_df_to_list(edited)  # tolerant to missing cols/NaNs
    rows = _normalize_items(rows)

    if any(r[2] and not URL_SCHEME_RE.match(r[2]) for r in rows):
        st.caption("⚠️ Some URLs were auto-prefixed with https:// — please double-check.")

    profile["projects"] = rows
    return profile
