# st_app/app.py
from __future__ import annotations

from pathlib import Path
import sys
import os
import json
from typing import Any, Dict
from urllib.parse import urlsplit

import requests
import streamlit as st
from dotenv import load_dotenv

# ------------------------------------------------------------
# مسار المشروع الرئيسي
# ------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ------------------------------------------------------------
# تحميل الإعدادات من .env وتهيئة API_BASE + api_origin
# ------------------------------------------------------------
load_dotenv(dotenv_path=ROOT / ".env")
API_BASE = (
    os.getenv("API_BASE")
    or os.getenv("STREAMLIT_API_BASE")
    or "http://127.0.0.1:8000/api/v1"
)

def _api_origin_from_base(api_base: str) -> str:
    """Extract origin (scheme + host) from API_BASE like http://127.0.0.1:8000/api/v1"""
    parts = urlsplit(api_base)
    return f"{parts.scheme}://{parts.netloc}"

st.session_state.setdefault("api_origin", _api_origin_from_base(API_BASE))

# ------------------------------------------------------------
# استيراد الأدوات والمكونات
# ------------------------------------------------------------
from st_app.utils.profile_state import init_profile_in_state
from st_app.ui.tab_projects import render_projects_section
from st_app.ui.tab_education import render_education_section
from st_app.ui.tab_languages import render_languages_tab
from st_app.ui.tab_headshot import render_headshot_tab


# ------------------------------------------------------------
# الحالة الافتراضية للبروفايل
# ------------------------------------------------------------
def _default_profile() -> Dict[str, Any]:
    return {
        "header": {"name": "", "title": ""},
        "summary": [],
        "skills": [],
        "contact": {
            "email": "",
            "phone": "",
            "website": "",
            "github": "",
            "linkedin": "",
            "location": "",
        },
        "projects": [],
        "education": [],
        "languages": [],
        "avatar_url": "",
    }




def ensure_session_state() -> None:
    profiles_dir = Path.cwd() / "profiles"  # المجلد المحلي للبروفايلات
    latest_profile = None

    if profiles_dir.exists():
        # ابحث عن أحدث ملف profile.json داخل أي مجلد بروفايل
        all_profiles = sorted(
            profiles_dir.glob("*/profile.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if all_profiles:
            latest_profile = all_profiles[0].parent.name  # اسم المجلد = اسم البروفايل

    # احفظ الاسم في الجلسة (أحدث بروفايل أو القيمة الافتراضية "tamer")
    st.session_state.setdefault("profile_name", latest_profile or "tamer")
    st.session_state.setdefault("profile", _default_profile())
    st.session_state.setdefault("profile_loaded", False)



# ------------------------------------------------------------
# الشريط الجانبي (Sidebar)
# ------------------------------------------------------------
def render_sidebar() -> None:
    with st.sidebar:
        st.header("⚙️ Settings")

        st.text_input("Profile name", key="profile_name")

        col1, col2 = st.columns(2)
        if col1.button("Reload from API"):
            reload_from_api()

        if col2.button("Save to API", type="primary"):
            save_to_api()

        with st.expander("Current Profile (JSON)", expanded=False):
            st.code(
                json.dumps(st.session_state.profile, ensure_ascii=False, indent=2),
                language="json",
            )


# ------------------------------------------------------------
# تحميل / حفظ البروفايل عبر API
# ------------------------------------------------------------
def reload_from_api() -> None:
    try:
        resp = requests.get(
            f"{API_BASE}/profiles/get",
            params={"name": st.session_state.profile_name},
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json() or {}
            st.session_state.profile = data.get("profile", {}) or _default_profile()
            init_profile_in_state(st.session_state.profile)
            st.success("✅ Profile loaded from API")
        else:
            st.info("ℹ️ No saved profile found; starting with empty profile.")
            st.session_state.profile = _default_profile()
            init_profile_in_state(st.session_state.profile)
    except Exception as e:
        st.error(f"API load failed: {e}")


def save_to_api() -> None:
    profile = st.session_state.profile
    projects = st.session_state.get("projects_for_api", [])
    education = st.session_state.get("education_for_api", [])
    languages = st.session_state.get("languages_for_api", profile.get("languages", []))

    profile["projects"] = projects
    profile["education"] = education
    profile["languages"] = languages

    # 👇 تطبيع حقول الاتصال: حوّل السلاسل الفارغة إلى None
    contact = profile.get("contact", {}) or {}
    for k in ("email", "phone", "website", "github", "linkedin", "location"):
        v = contact.get(k)
        if isinstance(v, str) and not v.strip():
            contact[k] = None
    profile["contact"] = contact

    try:
        payload = {"name": st.session_state.profile_name, "profile": profile}
        r = requests.post(f"{API_BASE}/profiles/save", json=payload, timeout=20)
        if r.status_code == 200:
            st.success("✅ Profile saved successfully")
        else:
            st.error(f"Save failed: {r.status_code} — {r.text}")
    except Exception as e:
        st.error(f"Error saving: {e}")



# ------------------------------------------------------------
# تبويبات واجهة المستخدم
# ------------------------------------------------------------
def render_header_tab() -> None:
    st.subheader("Header")
    c1, c2 = st.columns([1, 1])
    st.session_state.profile["header"]["name"] = c1.text_input(
        "Full name", value=st.session_state.profile["header"].get("name", "")
    )
    st.session_state.profile["header"]["title"] = c2.text_input(
        "Title / Role", value=st.session_state.profile["header"].get("title", "")
    )


def render_summary_tab() -> None:
    st.subheader("Summary")
    text = st.text_area(
        "Write a short professional summary (one point per line)",
        value="\n".join(st.session_state.profile.get("summary", []) or []),
        height=120,
    )
    st.session_state.profile["summary"] = [
        ln.strip() for ln in text.splitlines() if ln.strip()
    ]


def render_skills_tab() -> None:
    st.subheader("Key Skills")
    skills_csv = st.text_input(
        "Skills (comma-separated)",
        value=",".join(st.session_state.profile.get("skills", []) or []),
        placeholder="Python, FastAPI, PostgreSQL, ReportLab, Streamlit",
    )
    st.session_state.profile["skills"] = [
        s.strip() for s in skills_csv.split(",") if s.strip()
    ]


def render_contact_tab() -> None:
    st.subheader("Contact Information")
    c1, c2 = st.columns([1, 1])
    st.session_state.profile["contact"]["email"] = c1.text_input(
        "Email", value=st.session_state.profile["contact"].get("email", "")
    )
    st.session_state.profile["contact"]["phone"] = c2.text_input(
        "Phone", value=st.session_state.profile["contact"].get("phone", "")
    )

    c3, c4 = st.columns([1, 1])
    st.session_state.profile["contact"]["website"] = c3.text_input(
        "Website", value=st.session_state.profile["contact"].get("website", "")
    )
    st.session_state.profile["contact"]["github"] = c4.text_input(
        "GitHub", value=st.session_state.profile["contact"].get("github", "")
    )

    c5, c6 = st.columns([1, 1])
    st.session_state.profile["contact"]["linkedin"] = c5.text_input(
        "LinkedIn", value=st.session_state.profile["contact"].get("linkedin", "")
    )
    st.session_state.profile["contact"]["location"] = c6.text_input(
        "Location", value=st.session_state.profile["contact"].get("location", "")
    )


# ------------------------------------------------------------
# التشغيل الرئيسي
# ------------------------------------------------------------
def main() -> None:
    st.set_page_config(page_title="Resume Builder", layout="wide", page_icon="🧩")
    ensure_session_state()
    render_sidebar()

    st.title("Resume Builder")

    # تحميل أولي للبروفايل من الـ API
    if not st.session_state.profile_loaded:
        reload_from_api()
        st.session_state.profile_loaded = True

    # التبويبات
    tab_header, tab_summary, tab_skills, tab_contact, tab_projects, tab_education, tab_languages, tab_headshot = st.tabs(
        [
            "Header",
            "Summary",
            "Skills",
            "Contact",
            "Projects",
            "Education",
            "Languages",
            "Headshot",
        ]
    )

    with tab_header:
        render_header_tab()

    with tab_summary:
        render_summary_tab()

    with tab_skills:
        render_skills_tab()

    with tab_contact:
        render_contact_tab()

    with tab_projects:
        projects_for_api = render_projects_section()
        st.session_state["projects_for_api"] = projects_for_api

    with tab_education:
        education_for_api = render_education_section()
        st.session_state["education_for_api"] = education_for_api

    with tab_languages:
        languages_for_api = render_languages_tab()
        st.session_state["languages_for_api"] = languages_for_api

    with tab_headshot:
        render_headshot_tab()




if __name__ == "__main__":
    main()
