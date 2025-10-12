from __future__ import annotations

import json
import base64
import re
import streamlit as st

from core.paths import THEMES_DIR, LAYOUTS_DIR
from core.schema import ensure_profile_schema
from core.io_utils import list_json_names
from core import api_client as api  # عميل الـ API

from st_app.config.ui_defaults import (
    DEFAULT_API_BASE,
    UI_LANG_OPTIONS,
    DEFAULT_THEME_FALLBACK,
)

# -------------------------
# Helpers
# -------------------------

def _clean_name(name: str) -> str:
    n = (name or "").strip()
    if n.lower().endswith(".json"):
        n = n[:-5]
    return n or "my_profile"

def _apply_photo_b64_to_session(profile: dict) -> None:
    b64 = profile.get("photo_b64") or profile.get("avatar_b64")
    if not b64:
        return
    try:
        st.session_state.photo_bytes = base64.b64decode(b64)
        st.session_state.photo_mime = "image/png"
    except Exception:
        st.session_state.photo_bytes = None
        st.session_state.photo_mime = None

def _s(x) -> str:
    return "" if x is None else str(x).strip()

def _ss_get_multi(prefix: str, rev: int) -> str:
    """
    يحاول قراءة قيمة من session_state لعدة إصدارات:
    rev الحالي ثم السابق. (يمكن إضافة -2 إذا رغبت)
    """
    for r in (rev, rev - 1):
        if r is not None and r >= 0:
            v = st.session_state.get(f"{prefix}_{r}")
            if v is not None:
                return _s(v)
    return ""

def _norm_url(u: str) -> str:
    if not u:
        return ""
    u = u.strip()
    if u.startswith(("http://", "https://")):
        return u
    return f"https://{u}"

def _norm_phone(p: str) -> str:
    p = re.sub(r"[^\d+\-\s()]", "", p or "")
    return re.sub(r"\s+", " ", p).strip()

# -------------------------
# Collection (one-click save)
# -------------------------

def collect_latest_profile(profile: dict) -> dict:
    """
    يجمع أحدث القيم من التبويبات مرة واحدة.
    يقرأ من rev الحالي والسابق لتفادي مشكلة تبدّل المفاتيح بعد رفع rev داخل التبويبات،
    ويستعين بالمفاتيح الثابتة (name/title) كخطة أمان، ثم بما في profile.
    """
    rev = st.session_state.get("profile_rev", 0)
    profile = ensure_profile_schema(profile or {})

    # --- Basic (header) ---
    # جرّب rev الحالي/السابق، ثم المفاتيح الثابتة، ثم الموجود في profile
    def _ss_get_name_title() -> tuple[str, str]:
        for r in (rev, rev - 1):
            if r is not None and r >= 0:
                nm = st.session_state.get(f"name_{r}")
                tt = st.session_state.get(f"title_{r}")
                if nm or tt:
                    return (_s(nm), _s(tt))
        # المفاتيح الثابتة (تثبّت داخل tab_basic بعد الحفظ)
        nm = st.session_state.get("name")
        tt = st.session_state.get("title")
        return (_s(nm), _s(tt))

    name, title = _ss_get_name_title()
    if not name:
        name = _s(profile.get("header", {}).get("name", ""))
    if not title:
        title = _s(profile.get("header", {}).get("title", ""))

    profile.setdefault("header", {})
    profile["header"].update({"name": name, "title": title})

    # --- Contact ---
    contact0 = profile.get("contact", {}) or {}
    email    = _ss_get_multi("email", rev)    or contact0.get("email", "")
    phone    = _norm_phone(_ss_get_multi("phone", rev)    or contact0.get("phone", ""))
    website  = _ss_get_multi("website", rev)  or contact0.get("website", "")
    github   = _ss_get_multi("github", rev)   or contact0.get("github", "")
    linkedin = _ss_get_multi("linkedin", rev) or contact0.get("linkedin", "")
    location = _ss_get_multi("location", rev) or contact0.get("location", "")

    if github and "://" not in github and "/" not in github.strip("/"):
        github = f"https://github.com/{github}"
    github = _norm_url(github) if github else ""

    if linkedin and "://" not in linkedin and "/" not in linkedin.strip("/"):
        linkedin = f"https://www.linkedin.com/in/{linkedin}"
    linkedin = _norm_url(linkedin) if linkedin else ""

    website = _norm_url(website) if website else ""
    email_json = email if email.strip() else None  # EmailStr | None

    profile.setdefault("contact", {})
    profile["contact"].update(
        {
            "email": email_json,
            "phone": phone,
            "website": website,
            "github": github,
            "linkedin": linkedin,
            "location": location,
        }
    )

    # --- Skills ---
    sk_text = _ss_get_multi("skills_text", rev)
    if sk_text != "":
        profile["skills"] = [ln.strip() for ln in sk_text.splitlines() if ln.strip()]

    # --- Languages ---
    lg_text = _ss_get_multi("languages_text", rev)
    if lg_text != "":
        profile["languages"] = [ln.strip() for ln in lg_text.splitlines() if ln.strip()]

    # --- Summary ---
    sm_text = _ss_get_multi("summary", rev)
    if sm_text:
        profile["summary"] = sm_text
    else:
        profile.pop("summary", None)

    # --- Projects ---
    projects = []
    i = 0
    while True:
        # تحقق من وجود صف بأي rev (الحالي أو السابق)
        has_any = any(
            f in st.session_state
            for f in (f"proj_title_{rev}_{i}", f"proj_desc_{rev}_{i}", f"proj_url_{rev}_{i}",
                      f"proj_title_{rev-1}_{i}", f"proj_desc_{rev-1}_{i}", f"proj_url_{rev-1}_{i}")
        )
        if not has_any:
            break

        t = _ss_get_multi(f"proj_title_{i}", rev)
        d = _ss_get_multi(f"proj_desc_{i}",  rev)
        u = _ss_get_multi(f"proj_url_{i}",   rev)
        if u and not re.match(r"^[a-z]+://", u, re.I) and "." in u.split("/")[0]:
            u = f"https://{u}"
        if t or d or u:
            projects.append([t, d, u])
        i += 1
    if projects:
        profile["projects"] = projects
    else:
        profile.pop("projects", None)

    # --- Education ---
    education = []
    i = 0
    while True:
        has_any = any(
            f in st.session_state
            for f in (
                f"edu_title_{rev}_{i}", f"edu_school_{rev}_{i}", f"edu_start_{rev}_{i}",
                f"edu_end_{rev}_{i}", f"edu_details_{rev}_{i}", f"edu_url_{rev}_{i}",
                f"edu_title_{rev-1}_{i}", f"edu_school_{rev-1}_{i}", f"edu_start_{rev-1}_{i}",
                f"edu_end_{rev-1}_{i}", f"edu_details_{rev-1}_{i}", f"edu_url_{rev-1}_{i}"
            )
        )
        if not has_any:
            break

        t = _ss_get_multi(f"edu_title_{i}",   rev)
        s = _ss_get_multi(f"edu_school_{i}",  rev)
        a = _ss_get_multi(f"edu_start_{i}",   rev)
        e = _ss_get_multi(f"edu_end_{i}",     rev)
        d = _ss_get_multi(f"edu_details_{i}", rev)
        u = _ss_get_multi(f"edu_url_{i}",     rev)
        if u and not re.match(r"^[a-z]+://", u, re.I) and "." in u.split("/")[0]:
            u = f"https://{u}"
        if any([t, s, a, e, d, u]):
            education.append([t, s, a, e, d, u])
        i += 1
    if education:
        profile["education"] = education
    else:
        profile.pop("education", None)

    # --- Photo / Avatar ---
    # تبويب الصورة يضع avatar_b64 في الـ session
    if st.session_state.get("avatar_b64"):
        profile["avatar_b64"] = st.session_state["avatar_b64"]
    # لو في photo_bytes من المعالج، خزّنه كـ photo_b64
    if st.session_state.get("photo_bytes"):
        profile["photo_b64"] = base64.b64encode(st.session_state["photo_bytes"]).decode("ascii")

    # تنظيم نهائي
    profile = ensure_profile_schema(profile)
    return profile

# -------------------------
# Sidebar UI
# -------------------------

def render_sidebar() -> dict:
    with st.sidebar:
        st.header("Controls")

        # ===== API base =====
        base_no_api = st.text_input("API Base URL", value=DEFAULT_API_BASE, key="api_base")
        api.BASE = f"{base_no_api.rstrip('/')}/api"

        # ===== Print/UI settings =====
        ui_lang = st.selectbox("UI Language", UI_LANG_OPTIONS, index=0, key="ui_lang")
        rtl_mode = st.toggle("RTL mode", value=(ui_lang == "ar"), key="rtl_mode")

        theme_files = list_json_names(THEMES_DIR)
        theme_name = st.selectbox("Theme", theme_files or [DEFAULT_THEME_FALLBACK], key="theme_name")

        layout_files = list_json_names(LAYOUTS_DIR)
        layout_file = st.selectbox(
            "Layout",
            ["(none)"] + layout_files,
            index=1 if layout_files else 0,
            key="layout_file",
            help="اختر ملف لايـاوت من /layouts.",
        )

        st.markdown("---")
        st.subheader("Profiles (via API)")

        # ===== List profiles =====
        try:
            existing_profiles = api.list_profiles()
        except Exception as e:
            st.error(f"API list error: {e}")
            existing_profiles = []

        col_p_load, col_p_save = st.columns(2)

        # ---- Load ----
        with col_p_load:
            selected_profile = st.selectbox(
                "Select profile",
                ["(none)"] + existing_profiles,
                index=0,
                key="selected_profile_api",
            )
            if st.button("Load Profile", key="btn_load_profile_api"):
                if selected_profile and selected_profile != "(none)":
                    try:
                        loaded = api.load_profile(selected_profile)
                        st.session_state.profile = ensure_profile_schema(loaded)
                        _apply_photo_b64_to_session(st.session_state.profile)
                        st.session_state.profile_rev = st.session_state.get("profile_rev", 0) + 1
                        st.success("Profile loaded.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Load failed: {e}")

        # ---- Save ----
        with col_p_save:
            profile_name_in = st.text_input("Save as (name only)", value="my_profile", key="save_profile_as_api")
            if st.button("Save Profile", key="btn_save_profile_api"):
                try:
                    name = _clean_name(profile_name_in)
                    # ✅ اجمع أحدث القيم من الواجهة مباشرة (rev و rev-1 والمفاتيح الثابتة)
                    current = st.session_state.get("profile", {})
                    payload = collect_latest_profile(ensure_profile_schema(current))
                    api.save_profile(name, payload)
                    st.success(f"Saved (API): {name}.json")
                except Exception as e:
                    st.error(f"Save failed: {e}")

        st.markdown("---")
        # ---- Import JSON ----
        up = st.file_uploader("Import profile (.json)", type=["json"], key="uploader_profile_api")
        if up is not None and st.button("Import now", key="btn_import_now_api"):
            try:
                imported = json.loads(up.getvalue().decode("utf-8"))
                st.session_state.profile = ensure_profile_schema(imported)
                _apply_photo_b64_to_session(st.session_state.profile)
                st.session_state.profile_rev = st.session_state.get("profile_rev", 0) + 1
                st.success("Imported profile applied to the form.")
                st.rerun()
            except Exception as e:
                st.error(f"Import failed: {e}")

        # ---- Export JSON ----
        if st.button("Export current as JSON", key="btn_export_json_api"):
            st.download_button(
                "Download JSON",
                data=json.dumps(
                    ensure_profile_schema(st.session_state.get("profile", {})),
                    ensure_ascii=False,
                    indent=2,
                ).encode("utf-8"),
                file_name="profile_export.json",
                mime="application/json",
                key="download_export_json_api",
            )

    return {
        "base_url": base_no_api,
        "ui_lang": ui_lang,
        "rtl_mode": rtl_mode,
        "theme_name": theme_name,
        "layout_file": layout_file,
    }
