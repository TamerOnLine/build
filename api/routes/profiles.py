from pathlib import Path
import os, json, re
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr

# ===================================================================
# المجلد الافتراضي لتخزين ملفات البروفايلات
# ===================================================================
DEFAULT_PROFILES_DIR = Path(os.getenv("PROFILES_DIR", "profiles")).resolve()
PROFILES_DIR: Path = DEFAULT_PROFILES_DIR


def _ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


# ===================================================================
# التحقق من اسم الملف (يمنع محاولات التلاعب مثل ../../)
# ===================================================================
_NAME_RE = re.compile(r"^[\w\-\.\u0600-\u06FF ]{1,100}$")

def _validate_name(name: str) -> str:
    if not isinstance(name, str) or not _NAME_RE.match(name):
        raise HTTPException(status_code=400, detail="Invalid profile name.")
    if "/" in name or "\\" in name or ".." in name:
        raise HTTPException(status_code=400, detail="Invalid profile name.")
    return name


def _path_for(name: str) -> Path:
    return (PROFILES_DIR / f"{name}.json").resolve()


# ===================================================================
# واجهات FastAPI
# ===================================================================
router = APIRouter(prefix="/profiles", tags=["profiles"])


class Contact(BaseModel):
    email: EmailStr | None = None
    phone: str | None = None
    website: str | None = None
    github: str | None = None
    linkedin: str | None = None
    location: str | None = None


class Profile(BaseModel):
    contact: Contact | None = None
    skills: list[str] | None = None
    languages: list[str] | None = None
    projects: list[list[str]] | None = None
    education: list[list[str]] | None = None
    summary: str | None = None


class SaveProfileRequest(BaseModel):
    name: str
    profile: Profile


@router.post("/save")
def save_profile(payload: SaveProfileRequest):
    name = _validate_name(payload.name)
    _ensure_dir(PROFILES_DIR)
    path = _path_for(name)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload.profile.model_dump(), f, ensure_ascii=False, indent=2)
    return {"ok": True, "name": name}


@router.get("/get")
def get_profile(name: str = Query(...)):
    name = _validate_name(name)
    path = _path_for(name)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Profile not found.")
    with path.open("r", encoding="utf-8") as f:
        return {"name": name, "profile": json.load(f)}

@router.get("/load")
def load_profile(name: str = Query(...)):
    # Alias لنفس وظيفة get_profile — حتى يعمل /load مثل /get
    return get_profile(name)


# ✅ التصحيح هنا: يرجع قائمة فقط بدل {"profiles": [...]} 
@router.get("/list", response_model=list[str])
def list_profiles() -> list[str]:
    if not PROFILES_DIR.exists():
        return []
    return sorted(p.stem for p in PROFILES_DIR.glob("*.json"))


@router.delete("/delete")
def delete_profile(name: str = Query(...)):
    name = _validate_name(name)
    path = _path_for(name)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Profile not found.")
    path.unlink()
    return {"ok": True, "name": name}


__all__ = ["router", "PROFILES_DIR"]
