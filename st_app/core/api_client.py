from __future__ import annotations
import os, json, requests, streamlit as st

# ============================================================
# إعداد عنوان الـ API
# ============================================================
DEFAULT_API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000/api")
API_BASE = st.session_state.get("API_BASE", DEFAULT_API_BASE)

# ============================================================
# أدوات الاتصال بالـ API
# ============================================================
def api_post(endpoint: str, payload: dict) -> dict:
    url = f"{API_BASE.rstrip('/')}/{endpoint.lstrip('/')}"
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    return resp.json()

def api_get(endpoint: str) -> dict:
    url = f"{API_BASE.rstrip('/')}/{endpoint.lstrip('/')}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

# ============================================================
# دوال إضافية للثيم والتخطيط
# ============================================================
def normalize_theme_name(name: str) -> str:
    s = (name or "").strip().lower()
    s = s.replace("_", "-").replace(" ", "-")
    return s

def choose_layout_inline(layout_file: str) -> dict:
    """اختيار أو تحميل تخطيط JSON (اختياري)"""
    import json as _json
    if not layout_file:
        return {}
    try:
        if os.path.isfile(layout_file):
            with open(layout_file, "r", encoding="utf-8") as f:
                return _json.load(f)
        return {}
    except Exception:
        return {}

def inject_headshot_into_layout(layout: dict, photo_bytes: bytes | None) -> dict:
    """حقن الصورة داخل التخطيط (اختياري)"""
    if not isinstance(layout, dict):
        return layout
    if photo_bytes:
        layout["headshot_injected"] = True
    return layout

# ============================================================
# توليد PDF
# ============================================================
def api_generate_pdf(payload: dict) -> bytes:
    url = f"{API_BASE.rstrip('/')}/generate-form-simple"
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    return resp.content

# ============================================================
# حفظ البروفايل
# ============================================================
def save_profile(profile_name: str, payload: dict) -> dict:
    url = f"{API_BASE.rstrip('/')}/profiles/save"
    data = {"name": profile_name, "profile": payload}
    resp = requests.post(url, json=data)
    resp.raise_for_status()
    return resp.json()

# ============================================================
# تنظيف القيم قبل الحفظ
# ============================================================
def _none_if_empty(x):
    x = (x or "").strip()
    return None if x == "" else x

def _coerce_str_list(v):
    if v is None:
        return []
    if isinstance(v, str):
        s = v.strip()
        if s == "":
            return []
        return [ln.strip() for ln in s.splitlines() if ln.strip()]
    if isinstance(v, (list, tuple)):
        out = []
        for it in v:
            s = ("" if it is None else str(it)).strip()
            if s:
                out.append(s)
        return out
    return []

# ============================================================
# بناء الحمولة قبل الحفظ
# ============================================================
def build_profile_payload(profile: dict) -> dict:
    contact = profile.get("contact") or {}
    clean_contact = {
        "email":    _none_if_empty(contact.get("email")),
        "phone":    _none_if_empty(contact.get("phone")),
        "website":  _none_if_empty(contact.get("website")),
        "github":   _none_if_empty(contact.get("github")),
        "linkedin": _none_if_empty(contact.get("linkedin")),
        "location": _none_if_empty(contact.get("location")),
    }

    return {
        "header":    profile.get("header") or {},
        "contact":   clean_contact,
        "summary":   _coerce_str_list(profile.get("summary")),
        "skills":    _coerce_str_list(profile.get("skills")),
        "languages": _coerce_str_list(profile.get("languages")),
        "projects":  profile.get("projects") or [],
        "education": profile.get("education") or [],
        "avatar":    profile.get("avatar") or None,
    }

# ============================================================
# توليد حمولة PDF
# ============================================================
def build_payload(profile: dict) -> dict:
    return {
        "header": profile.get("header") or {},
        "contact": profile.get("contact") or {},
        "summary": profile.get("summary") or [],
        "skills": profile.get("skills") or [],
        "languages": profile.get("languages") or [],
        "projects": profile.get("projects") or [],
        "education": profile.get("education") or [],
        "avatar": profile.get("avatar") or None,
    }

# ============================================================
# Debug
# ============================================================
if __name__ == "__main__":
    example = {
        "header": {"name": "Tamer", "title": "Software Developer"},
        "contact": {"email": "", "phone": "12345"},
        "summary": "",
        "skills": ["FastAPI", "Streamlit"],
        "languages": "",
        "projects": [],
        "education": [],
    }
    payload = build_profile_payload(example)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
