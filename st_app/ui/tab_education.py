# streamlit/ui/tab_education.py
from __future__ import annotations
from typing import Any, List
import re

import pandas as pd
import streamlit as st

from st_app.config.ui_defaults import EDU_COLUMNS, DATE_HINT, EDU_URL_HELP



URL_RE = re.compile(r"^[a-z]+://", re.IGNORECASE)

def _s(x: Any) -> str:
    return "" if x is None else str(x).strip()

def _norm_url(u: str) -> str:
    u = _s(u)
    if not u:
        return ""
    # auto-prefix if it looks like a domain without scheme
    if not URL_RE.match(u) and "." in u.split("/")[0]:
        return f"https://{u}"
    return u

def _ensure_education_rows(ed) -> List[List[str]]:
    rows: List[List[str]] = []
    if isinstance(ed, list):
        for it in ed:
            if isinstance(it, (list, tuple)):
                vals = list(it) + [""] * (6 - len(it))
                r = [_s(v) for v in vals[:6]]
                rows.append(r)
            elif isinstance(it, dict):
                rows.append([
                    _s(it.get("title")),
                    _s(it.get("school")),
                    _s(it.get("start")),
                    _s(it.get("end")),
                    _s(it.get("details")),
                    _s(it.get("url")),
                ])
            else:
                rows.append(["", "", "", "", _s(it), ""])
    # Ensure at least one blank row for UX
    if not rows:
        rows = [["", "", "", "", "", ""]]
    return rows

def _drop_trailing_blank_rows(rows: List[List[str]]) -> List[List[str]]:
    # remove trailing rows that are fully blank
    i = len(rows) - 1
    while i >= 0 and all(_s(c) == "" for c in rows[i]):
        i -= 1
    rows = rows[: i + 1]
    return rows or [["", "", "", "", "", ""]]

def _normalize_rows(rows: List[List[str]]) -> List[List[str]]:
    norm: List[List[str]] = []
    for r in rows:
        title, school, start, end, details, url = (r + [""] * 6)[:6]
        norm.append([
            _s(title),
            _s(school),
            _s(start),
            _s(end),
            _s(details),
            _norm_url(url),
        ])
    return norm

def render(profile: dict) -> dict:
    st.subheader("Education / Training")
    rev = st.session_state.get("profile_rev", 0)

    ed_rows = _ensure_education_rows(profile.get("education", []))
    df_edu = pd.DataFrame(ed_rows, columns=EDU_COLUMNS)

    st.caption("Use the table below to edit your education entries:")
    edited = st.data_editor(
        df_edu,
        num_rows="dynamic",
        key=f"education_editor_{rev}",
        width='stretch',
        column_config={
            "Title / Program": st.column_config.TextColumn(width="large", help="Degree, program, or course name."),
            "School": st.column_config.TextColumn(width="large", help="Institution or platform (e.g., Coursera)."),
            "Start": st.column_config.TextColumn(help=DATE_HINT),
            "End": st.column_config.TextColumn(help=f"{DATE_HINT} or 'Present'"),
            "Details": st.column_config.TextColumn(width="large", help="Optional: highlights, modules, GPA, etc."),
            "URL": st.column_config.LinkColumn(help=EDU_URL_HELP),
        },
    )

    rows = edited.fillna("").values.tolist()
    rows = _normalize_rows(rows)
    rows = _drop_trailing_blank_rows(rows)

    # Soft hints (no blocking)
    if any(r[2] and not re.search(r"\d{4}", r[2]) for r in rows):  # Start year present?
        st.caption("⚠️ Some Start values look unusual; use formats like 06/2024 or 2024–2025.")
    if any(r[5] and not URL_RE.match(r[5]) for r in rows):
        st.caption("⚠️ Some URLs were auto-prefixed with https:// — please double-check.")

    profile["education"] = rows
    st.info("Tip: Leave URL empty if not applicable.")
    return profile
