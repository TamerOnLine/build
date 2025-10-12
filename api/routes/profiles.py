from __future__ import annotations

from pathlib import Path
import os, json, re, base64, shutil
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field, field_validator

# ============================
# إعدادات المسارات (قابلة للبيئة)
# ============================
PROFILES_DIR = Path(
    os.getenv("PROFILES_DIR", str(Path.cwd() / "profiles"))
).resolve()
PROFILES_DIR.mkdir(parents=True, exist_ok=True)

PUBLIC_PROFILES_MOUNT = os.getenv("PUBLIC_PROFILES_MOUNT", "/profiles").rstrip("/")

# بنية المجلد لكل بروفايل
def _profile_dir(name: str) -> Path:
    return PROFILES_DIR / name

def _json_path(name: str) -> Path:
    return _profile_dir(name) / "profile.json"

def _png_path(name: str) -> Path:
    return _profile_dir(name) / "avatar.png"

def _public_avatar_url(name: str) -> str:
    return f"{PUBLIC_PROFILES_MOUNT}/{name}/avatar.png"

# ============================
# التحقق من الاسم
# ============================
_NAME_RE = re.compile(r"^[\w\-\.\u0600-\u06FF ]{1,100}$")
def _validate_name(name: str) -> str:
    if not isinstance(name, str) or not _NAME_RE.match(name):
        raise HTTPException(status_code=400, detail="Invalid profile name.")
    if "/" in name or "\\" in name or ".." in name:
        raise HTTPException(status_code=400, detail="Invalid profile name.")
    return name

# ============================
# النماذج
# ============================
class Header(BaseModel):
    name: str = Field("", max_length=120)
    title: str = Field("", max_length=160)

class Contact(BaseModel):
    email: EmailStr | None = None
    phone: str | None = None
    website: str | None = None
    github: str | None = None
    linkedin: str | None = None
    location: str | None = None

    @field_validator("email", mode="before")
    @classmethod
    def _empty_email_to_none(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

class Profile(BaseModel):
    header: Header | None = None
    contact: Contact | None = None
    skills: list[str] | None = None
    languages: list[str] | None = None
    projects: list[list[str]] | None = None
    education: list[list[str]] | None = None
    summary: list[str] | None = None

    # مفاتيح الصورة القادمة من الواجهة
    photo_b64: Optional[str] = None
    avatar_b64: Optional[str] = None

    # سيكتب دائمًا في JSON
    avatar_url: Optional[str] = None

    @field_validator("summary", mode="before")
    @classmethod
    def _summary_to_list(cls, v):
        if v is None:
            return None
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()]
        return [ln.strip() for ln in str(v).splitlines() if ln.strip()]

class SaveProfileRequest(BaseModel):
    name: str
    profile: Profile

# ============================
# أدوات الصورة
# ============================
def _strip_data_url_prefix(b64: str) -> str:
    if not b64:
        return b64
    b64 = b64.strip()
    if b64.lower().startswith("data:image"):
        return b64.split(",", 1)[1]
    return b64

def _save_png_from_b64(name: str, b64: Optional[str]) -> Optional[str]:
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

# ============================
# الراوتر
# ============================
router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.post("/save")
def save_profile(payload: SaveProfileRequest):
    """
    يحفظ داخل مجلد خاص بالبروفايل:
      profiles/<name>/profile.json
      profiles/<name>/avatar.png
    ويكتب avatar_url دائمًا داخل الـ JSON.
    """
    name = _validate_name(payload.name)

    # 1) جهّز البيانات
    data = payload.profile.model_dump(exclude_none=True)

    # 2) التقط Base64 من الواجهة
    photo_b64 = data.pop("photo_b64", None) or data.pop("avatar_b64", None)

    # 3) احفظ الصورة (إن وُجدت)
    new_avatar_url = _save_png_from_b64(name, photo_b64)

    # 4) avatar_url دائمًا
    jp = _json_path(name)
    existing_avatar_url = ""
    if jp.exists():
        try:
            existing = json.loads(jp.read_text(encoding="utf-8"))
            existing_avatar_url = str(existing.get("avatar_url") or "")
        except Exception:
            existing_avatar_url = ""
    data["avatar_url"] = new_avatar_url or existing_avatar_url or _public_avatar_url(name)

    # 5) اكتب JSON داخل نفس المجلد
    jp.parent.mkdir(parents=True, exist_ok=True)
    jp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    return {"ok": True, "name": name, "avatar_url": data["avatar_url"]}

@router.get("/get")
def get_profile(name: str = Query(...)):
    name = _validate_name(name)
    jp = _json_path(name)
    if not jp.exists():
        raise HTTPException(status_code=404, detail="Profile not found.")
    return {"name": name, "profile": json.loads(jp.read_text(encoding="utf-8"))}

@router.get("/load")
def load_profile(name: str = Query(...)):
    return get_profile(name)

@router.get("/list", response_model=list[str])
def list_profiles() -> list[str]:
    """
    يعيد أسماء المجلدات التي تحتوي profile.json
    """
    if not PROFILES_DIR.exists():
        return []
    names: list[str] = []
    for p in PROFILES_DIR.iterdir():
        if p.is_dir() and (p / "profile.json").exists():
            names.append(p.name)
    return sorted(names)

@router.delete("/delete")
def delete_profile(name: str = Query(...)):
    """
    يحذف مجلد البروفايل بالكامل: JSON + PNG
    """
    name = _validate_name(name)
    d = _profile_dir(name)
    if not d.exists():
        raise HTTPException(status_code=404, detail="Profile not found.")
    shutil.rmtree(d)
    return {"ok": True, "name": name}
