# api/routes/profiles.py
from __future__ import annotations

import base64
import json
import os
import re
import shutil
from pathlib import Path
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, EmailStr, Field, field_validator

from api.settings import get_settings

# ============================================================
# إعداد المجلدات من الإعدادات
# ============================================================

settings = get_settings()
PROFILES_DIR: Path = settings.profiles_dir
PUBLIC_PROFILES_MOUNT: str = settings.public_profiles_mount

# تأكد من وجود مجلد التخزين
PROFILES_DIR.mkdir(parents=True, exist_ok=True)


def _profile_dir(name: str) -> Path:
    return PROFILES_DIR / name


def _json_path(name: str) -> Path:
    return _profile_dir(name) / "profile.json"


def _png_path(name: str) -> Path:
    return _profile_dir(name) / "avatar.png"


def _public_avatar_url(name: str) -> str:
    return f"{PUBLIC_PROFILES_MOUNT}/{name}/avatar.png"


# ============================================================
# التحقق من الاسم
# ============================================================

_NAME_RE = re.compile(r"^[\w\-\.\u0600-\u06FF ]{1,100}$")


def _validate_name(name: str) -> str:
    if not isinstance(name, str) or not _NAME_RE.match(name):
        raise HTTPException(status_code=400, detail="Invalid profile name.")
    if "/" in name or "\\" in name or ".." in name:
        raise HTTPException(status_code=400, detail="Invalid profile name.")
    return name


# ============================================================
# نماذج البيانات (Pydantic)
# ============================================================

class Header(BaseModel):
    name: str = Field("", max_length=120)
    title: str = Field("", max_length=160)


class Contact(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    github: Optional[str] = None
    linkedin: Optional[str] = None
    location: Optional[str] = None


class Project(BaseModel):
    title: str = ""
    desc: str = ""
    url: Optional[str] = None


class Education(BaseModel):
    title: str = ""
    school: str = ""
    start: str = ""
    end: str = ""
    details: str = ""
    url: Optional[str] = None


class Profile(BaseModel):
    header: Header = Header()
    contact: Contact = Contact()
    skills: list[str] = []
    languages: list[str] = []
    summary: list[str] = []              # المشروع يعتمدها قائمة نصوص
    projects: list[Project] = []
    education: list[Education] = []
    # الصورة: نُفضّل ملف خارجي (URL). الحقول b64 مدعومة اختياريًا للخلفية.
    avatar_url: Optional[str] = None
    photo_b64: Optional[str] = None
    avatar_b64: Optional[str] = None

    # --- Normalizers ---------------------------------------------------------
    @field_validator("projects", mode="before")
    @classmethod
    def _coerce_projects(cls, v):
        """
        يسمح بشكل [[title, desc, url], ...] أو قائمة قواميس.
        """
        if isinstance(v, list) and v and isinstance(v[0], list):
            out = []
            for row in v:
                t, d, u = (row + ["", "", None])[:3]
                out.append({"title": (t or ""), "desc": (d or ""), "url": u or None})
            return out
        return v

    @field_validator("education", mode="before")
    @classmethod
    def _coerce_education(cls, v):
        """
        يسمح بشكل [[title, school, start, end, details, url], ...]
        أو قائمة قواميس.
        """
        if isinstance(v, list) and v and isinstance(v[0], list):
            out = []
            for row in v:
                t, s, a, e, d, u = (row + ["", "", "", "", "", None])[:6]
                out.append({
                    "title": t or "", "school": s or "", "start": a or "",
                    "end": e or "", "details": d or "", "url": u or None
                })
            return out
        return v


class SaveProfileRequest(BaseModel):
    name: str
    profile: Profile


# ============================================================
# وظائف مساعدة (الصورة)
# ============================================================

def _strip_data_url_prefix(b64: str) -> str:
    if not b64:
        return b64
    b64 = b64.strip()
    if b64.lower().startswith("data:image"):
        return b64.split(",", 1)[1]
    return b64


def _save_png_from_b64(name: str, b64: Optional[str]) -> Optional[str]:
    """
    حفظ الصورة كملف خارجي profiles/{name}/avatar.png وإرجاع الـ URL العام.
    لو لم تُمرَّر قيمة صالحة، يعاد None.
    """
    if not b64:
        return None
    raw = _strip_data_url_prefix(b64)
    try:
        img_bytes = base64.b64decode(raw)
    except Exception:
        return None
    d = _profile_dir(name)
    d.mkdir(parents=True, exist_ok=True)
    _png_path(name).write_bytes(img_bytes)
    return _public_avatar_url(name)


# ============================================================
# تعريف المسارات (Routes)
# ============================================================

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("/save")
def save_profile(payload: SaveProfileRequest):
    """
    حفظ ملف JSON الخاص بالبروفايل في profiles/<name>/profile.json
    ومعالجة الصورة (إما من avatar_url أو من photo_b64/avatar_b64 كملف خارجي).
    """
    name = _validate_name(payload.name)
    data = payload.profile.model_dump(exclude_none=False)

    # تطبيع contact وضمان وجود المفاتيح
    contact = data.get("contact") or {}
    for k in ("email", "phone", "website", "github", "linkedin", "location"):
        contact.setdefault(k, None)
    data["contact"] = contact

    # معالجة الصورة: إن وُجدت Base64 نُنشئ avatar.png، وإلا نستخدم avatar_url إن أُرسل
    photo_b64 = data.pop("photo_b64", None) or data.pop("avatar_b64", None)
    new_avatar_url = _save_png_from_b64(name, photo_b64)

    jp = _json_path(name)
    existing_avatar_url = ""
    if jp.exists():
        try:
            existing = json.loads(jp.read_text(encoding="utf-8"))
            existing_avatar_url = str(existing.get("avatar_url") or "")
        except Exception:
            existing_avatar_url = ""

    # أولوية: المولّد من B64 → المرسل كـ URL → الموجود سابقًا → المسار الافتراضي
    data["avatar_url"] = (
        new_avatar_url
        or (data.get("avatar_url") or "").strip()
        or existing_avatar_url
        or _public_avatar_url(name)
    )

    # كتابة JSON
    jp.parent.mkdir(parents=True, exist_ok=True)
    jp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    return {"ok": True, "name": name, "avatar_url": data["avatar_url"]}


@router.get("/get")
def get_profile(name: str = Query(...)):
    """إرجاع بروفايل محفوظ حسب الاسم."""
    name = _validate_name(name)
    jp = _json_path(name)
    if not jp.exists():
        raise HTTPException(status_code=404, detail="Profile not found.")
    return {"name": name, "profile": json.loads(jp.read_text(encoding="utf-8"))}


@router.get("/load")
def load_profile(name: str = Query(...)):
    """مرادف لـ /get لأغراض التوافق."""
    return get_profile(name)


@router.get("/list", response_model=List[str])
def list_profiles(settings=Depends(get_settings)):
    """
    إرجاع أسماء البروفايلات التي لديها فعليًا ملف profiles/<name>/profile.json.
    - لو المجلد فارغ: ترجع [].
    - لو توجد مجلدات بدون profile.json: تُتجاهل.
    """
    p: Path = settings.profiles_dir
    if not p.exists():
        return []

    names: list[str] = []
    for d in p.iterdir():
        if d.is_dir() and (d / "profile.json").is_file():
            names.append(d.name)
    return sorted(names)


@router.delete("/delete")
def delete_profile(name: str = Query(...)):
    """حذف البروفايل ومجلده بالكامل."""
    name = _validate_name(name)
    d = _profile_dir(name)
    if not d.exists():
        raise HTTPException(status_code=404, detail="Profile not found.")
    shutil.rmtree(d)
    return {"ok": True, "name": name}
