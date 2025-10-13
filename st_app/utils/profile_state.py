# st_app/utils/profile_state.py
# --- utils: init helpers ---------------------------------------------------
import streamlit as st
from copy import deepcopy

def _ensure_list(key, default=None):
    if key not in st.session_state or not isinstance(st.session_state[key], list):
        st.session_state[key] = deepcopy(default or [])

def _bwd_projects(items):
    """Back-compat: description/link -> desc/url"""
    out = []
    for it in items or []:
        if not isinstance(it, dict):
            continue
        out.append({
            "title": it.get("title", ""),
            "desc": it.get("desc") or it.get("description", ""),
            "url": it.get("url") or it.get("link") or "",
        })
    return out

def _bwd_education(items):
    """Back-compat: degree -> title"""
    out = []
    for e in items or []:
        if not isinstance(e, dict):
            continue
        out.append({
            "title":   e.get("title") or e.get("degree", ""),
            "school":  e.get("school", ""),
            "start":   e.get("start", ""),
            "end":     e.get("end", ""),
            "details": e.get("details", ""),
            "url":     e.get("url") or e.get("link") or "",
        })
    return out

# نادِ هذه مرة عند تحميل البروفايل من الـAPI
def init_profile_in_state(profile: dict):
    _ensure_list("projects", [])
    _ensure_list("education", [])
    st.session_state.projects  = _bwd_projects(profile.get("projects", []))
    st.session_state.education = _bwd_education(profile.get("education", []))
