from __future__ import annotations

from typing import Any, List, Optional, Tuple, Annotated
from pydantic import BaseModel, EmailStr, Field, HttpUrl, field_validator

# -------------------------------------------------
# General Limits
# -------------------------------------------------
MAX_SUMMARY = 12
MAX_SKILLS = 40
MAX_LANGUAGES = 12
MAX_PROJECTS = 40
MAX_EDUCATION = 20
MAX_STR_LEN = 2000
MAX_TITLE_LEN = 120
MAX_DESC_LEN = 600

# -------------------------------------------------
# Registry-based dynamic lists and defaults
# -------------------------------------------------
from .registry import (
    THEME_NAMES, LAYOUT_NAMES, UI_LANGS, RTL_LANGS,
    DEFAULT_THEME, DEFAULT_LAYOUT, DEFAULT_UI,
)

ThemeNameStr = Annotated[str, Field(json_schema_extra={"enum": THEME_NAMES})]
LayoutNameStr = Annotated[str, Field(json_schema_extra={"enum": LAYOUT_NAMES})]
UILangStr = Annotated[str, Field(json_schema_extra={"enum": UI_LANGS})]

# -------------------------------------------------
# Helper functions
# -------------------------------------------------
def _empty_to_none(v: Any) -> Any:
    """
    Converts empty strings to None.

    Args:
        v (Any): Input value.

    Returns:
        Any: None if input is empty string; otherwise, the original value.
    """
    if v is None:
        return None
    if isinstance(v, str) and v.strip() == "":
        return None
    return v

def _assert_list_max(items: List[Any], max_items: int, field_name: str):
    if len(items) > max_items:
        raise ValueError(f"{field_name} exceeds max items ({len(items)} > {max_items})")

def _assert_str_max(s: str, max_len: int, field_name: str):
    if len(s) > max_len:
        raise ValueError(f"{field_name} text too long ({len(s)} > {max_len} chars)")

# -------------------------------------------------
# Data Models
# -------------------------------------------------
class Header(BaseModel):
    name: str = Field(..., min_length=1, max_length=MAX_TITLE_LEN)
    title: str = Field(..., min_length=1, max_length=MAX_TITLE_LEN)

class Contact(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    github: Optional[HttpUrl] = None
    linkedin: Optional[HttpUrl] = None
    website: Optional[HttpUrl] = None

    @field_validator("github", "linkedin", "website", mode="before")
    @classmethod
    def _clean_urls(cls, v):
        return _empty_to_none(v)

class Avatar(BaseModel):
    photo_b64: str
    photo_mime: Optional[str] = "image/png"

class Profile(BaseModel):
    header: Header
    contact: Contact = Contact()
    summary: List[str] = []
    skills: List[str] = []
    languages: List[str] = []
    projects: List[Tuple[str, str, Optional[HttpUrl]]] = []
    education: List[str] = []
    avatar: Optional[Avatar] = None

    @field_validator("projects", mode="before")
    @classmethod
    def _clean_project_links(cls, v):
        if not isinstance(v, list):
            return v
        cleaned: list[tuple[str, str, Optional[str]]] = []
        for item in v:
            if isinstance(item, (list, tuple)):
                title = item[0] if len(item) > 0 else ""
                desc = item[1] if len(item) > 1 else ""
                link = item[2] if len(item) > 2 else None
                link = _empty_to_none(link)
                cleaned.append((title, desc, link))
            else:
                cleaned.append(item)
        return cleaned

    @field_validator("summary")
    @classmethod
    def _limit_summary_count(cls, v: List[str]):
        _assert_list_max(v, MAX_SUMMARY, "summary")
        return v

    @field_validator("skills")
    @classmethod
    def _limit_skills_count(cls, v: List[str]):
        _assert_list_max(v, MAX_SKILLS, "skills")
        return v

    @field_validator("languages")
    @classmethod
    def _limit_languages_count(cls, v: List[str]):
        _assert_list_max(v, MAX_LANGUAGES, "languages")
        return v

    @field_validator("education")
    @classmethod
    def _limit_education_count(cls, v: List[str]):
        _assert_list_max(v, MAX_EDUCATION, "education")
        return v

    @field_validator("projects")
    @classmethod
    def _limit_projects_count(cls, v: List[Tuple[str, str, Optional[HttpUrl]]]):
        _assert_list_max(v, MAX_PROJECTS, "projects")
        return v

    @field_validator("summary", "skills", "languages", "education")
    @classmethod
    def _limit_each_item_length(cls, v: List[str], info):
        fname = info.field_name
        for i, s in enumerate(v):
            if isinstance(s, str):
                _assert_str_max(s, MAX_STR_LEN, f"{fname}[{i}]")
        return v

    @field_validator("projects")
    @classmethod
    def _limit_project_fields(cls, v: List[Tuple[str, str, Optional[HttpUrl]]]):
        for i, (title, desc, _link) in enumerate(v):
            _assert_str_max(title, MAX_TITLE_LEN, f"projects[{i}].title")
            _assert_str_max(desc, MAX_DESC_LEN, f"projects[{i}].description")
        return v

class GenerateFormRequest(BaseModel):
    theme_name: ThemeNameStr = Field(default=DEFAULT_THEME)
    layout_name: LayoutNameStr = Field(default=DEFAULT_LAYOUT)
    ui_lang: UILangStr = Field(default=DEFAULT_UI)
    rtl_mode: bool | None = None
    profile: Profile

    @field_validator("layout_name", mode="before")
    @classmethod
    def empty_to_single_column(cls, v):
        v = v or "single-column"
        if v not in LAYOUT_NAMES:
            raise ValueError(f"layout_name must be one of {LAYOUT_NAMES}")
        return v

    @field_validator("theme_name")
    @classmethod
    def _check_theme(cls, v: str):
        if v not in THEME_NAMES:
            raise ValueError(f"theme_name must be one of {THEME_NAMES}")
        return v

    @field_validator("ui_lang")
    @classmethod
    def _check_lang(cls, v: str):
        if v not in UI_LANGS:
            raise ValueError(f"ui_lang must be one of {UI_LANGS}")
        return v

    @field_validator("rtl_mode")
    @classmethod
    def auto_rtl_by_lang(cls, v, info):
        if isinstance(v, bool):
            return v
        ui_lang = info.data.get("ui_lang", DEFAULT_UI)
        return ui_lang in RTL_LANGS

