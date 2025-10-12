# api/routes/profiles.py
from __future__ import annotations
from pathlib import Path
import os, json, re, base64, shutil
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field, field_validator
from api.models.profile import Profile

# ============================
# إعداد المسارات (قابلة للتغيير)
# ============================
PROFILES_DIR = Path(
    os.getenv("PROFILES_DIR", str(Path.cwd() / "profiles"))
).resolve()
PROFILES_DIR.mkdir(parents=True, exist_ok=True)
PUBLIC_PROFILES_MOUNT = os.getenv("PUBLIC_PROFILES_MOUNT", "/profiles").rstrip("/")

def _profile_dir(name: str) -> Path: return PROFILES_DIR / name
def _json_path(name: str) -> Path: return _profile_dir(name) / "profile.json"
def _png_path(name: str) -> Path: return _profile_dir(name) / "avatar.png"
def _public_avatar_url(name: str) -> str: return f"{PUBLIC_PROFILES_MOUNT}/{name}/avatar.png"

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
# النماذج الكائنية
# ============================
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
    summary: list[str] = []
    projects: list[Project] = []
    education: list[Education] = []
    avatar_url: Optional[str] = None
    photo_b64: Optional[str] = None
    avatar_b64: Optional[str] = None

    # ===== توافق خلفي مع الصيغة القديمة list[list[str]] =====
    @field_validator("projects", mode="before")
    @classmethod
    def _coerce_projects(cls, v):
        if isinstance(v, list) and v and isinstance(v[0], list):
            out = []
            for row in v:
                t, d, u = (row + ["", "", None])[:3]
                out.append({"title": t or "", "desc": d or "", "url": u or None})
            return out
        return v

    @field_validator("education", mode="before")
    @classmethod
    def _coerce_education(cls, v):
        if isinstance(v, list) and v and isinstance(v[0], list):
            out = []
            for row in v:
                t, s, a, e, d, u = (row + ["", "", "", "", "", None])[:6]
                out.append({
                    "title": t or "", "school": s or "", "start": a or "", "end": e or "",
                    "details": d or "", "url": u or None
                })
            return out
        return v

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
    يحفظ البروفايل داخل:
      profiles/<name>/profile.json
      profiles/<name>/avatar.png
    """
    name = _validate_name(payload.name)

    # 1) اجلب كل الحقول بدون استبعاد None
    data = payload.profile.model_dump(exclude_none=False)

    # 2) contact: ضَمَن المفاتيح دائماً
    contact = data.get("contact") or {}
    for k in ("email", "phone", "website", "github", "linkedin", "location"):
        contact.setdefault(k, None)
    data["contact"] = contact

    # 3) احفظ الصورة إن وُجدت (كما هو)
    photo_b64 = data.pop("photo_b64", None) or data.pop("avatar_b64", None)
    new_avatar_url = _save_png_from_b64(name, photo_b64)

    # 4) ثبّت avatar_url (كما هو)
    jp = _json_path(name)
    existing_avatar_url = ""
    if jp.exists():
        try:
            existing = json.loads(jp.read_text(encoding="utf-8"))
            existing_avatar_url = str(existing.get("avatar_url") or "")
        except Exception:
            existing_avatar_url = ""
    data["avatar_url"] = new_avatar_url or existing_avatar_url or _public_avatar_url(name)

    # 5) احفظ JSON النهائي (سيحتوي contact بالمفاتيح كلها)
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
    if not PROFILES_DIR.exists():
        return []
    names: list[str] = []
    for p in PROFILES_DIR.iterdir():
        if p.is_dir() and (p / "profile.json").exists():
            names.append(p.name)
    return sorted(names)

@router.delete("/delete")
def delete_profile(name: str = Query(...)):
    name = _validate_name(name)
    d = _profile_dir(name)
    if not d.exists():
        raise HTTPException(status_code=404, detail="Profile not found.")
    shutil.rmtree(d)
    return {"ok": True, "name": name}
