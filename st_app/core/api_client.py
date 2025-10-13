from __future__ import annotations
import os
import json
import requests
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

# --------------------------------------------
# Build API base from .env (host + prefix + version)
# You can still override with:
#   - st.session_state["API_BASE"]
#   - or env var API_BASE
# --------------------------------------------
API_HOST   = os.getenv("API_HOST", "http://127.0.0.1:8000").rstrip("/")
API_PREFIX = os.getenv("APP_API_PREFIX", "/api").strip("/")
API_VER    = os.getenv("APP_API_VERSION", "v1").strip("/")

_env_api_base = os.getenv("API_BASE")  # optional override via env
_ss_api_base  = st.session_state.get("API_BASE")  # optional override via session

if _ss_api_base:
    API_BASE = _ss_api_base.rstrip("/")
elif _env_api_base:
    API_BASE = _env_api_base.rstrip("/")
else:
    # Compose from HOST + /prefix + /version
    API_BASE = f"{API_HOST}/{API_PREFIX}/{API_VER}".replace("//", "/")
    # keep scheme slashes
    if API_BASE.startswith("http:/") and not API_BASE.startswith("http://"):
        API_BASE = API_BASE.replace("http:/", "http://", 1)
    if API_BASE.startswith("https:/") and not API_BASE.startswith("https://"):
        API_BASE = API_BASE.replace("https:/", "https://", 1)

# ================================
# HTTP helpers
# ================================
def _join(endpoint: str) -> str:
    return f"{API_BASE.rstrip('/')}/{endpoint.lstrip('/')}"

def api_post(endpoint: str, payload: dict) -> dict:
    resp = requests.post(_join(endpoint), json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()

def api_get(endpoint: str) -> dict:
    resp = requests.get(_join(endpoint), timeout=60)
    resp.raise_for_status()
    return resp.json()

# ================================
# Theme utils
# ================================
def normalize_theme_name(name: str) -> str:
    s = (name or "").strip().lower()
    return s.replace("_", "-").replace(" ", "-")

def choose_layout_inline(layout_file: str) -> dict:
    if not layout_file:
        return {}
    try:
        if os.path.isfile(layout_file):
            with open(layout_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    except Exception:
        return {}

def inject_headshot_into_layout(layout: dict, photo_bytes: bytes | None) -> dict:
    if not isinstance(layout, dict):
        return layout
    if photo_bytes:
        layout["headshot_injected"] = True
    return layout

# ================================
# PDF generation
# ================================
def api_generate_pdf(payload: dict) -> bytes:
    # يضبط URL النهائي عبر API_BASE + endpoint
    url = _join("generate-form-simple")
    print("[api_client] POST", url)  # debug: يظهر في التيرمنال عند الضغط على Generate PDF
    resp = requests.post(url, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.content


# ================================
# Profiles
# ================================
def save_profile(profile_name: str, payload: dict) -> dict:
    url = _join("profiles/save")
    data = {"name": profile_name, "profile": payload}
    resp = requests.post(url, json=data, timeout=60)
    resp.raise_for_status()
    return resp.json()

# ================================
# Payload shapers
# ================================
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
