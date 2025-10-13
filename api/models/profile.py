# api/models/profile.py
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, field_validator

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

    @field_validator("email", "website", "github", "linkedin", "phone", "location", mode="before")
    @classmethod
    def _empty_to_none(cls, v):
        if v is None:
            return None
        s = str(v).strip()
        return None if s == "" else s

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
    summary: List[str] = []
    skills: List[str] = []
    languages: List[str] = []
    projects: List[Project] = []
    education: List[Education] = []
    avatar: Optional[str] = None
    avatar_url: Optional[str] = None

    @field_validator("summary", "skills", "languages", mode="before")
    @classmethod
    def _coerce_str_list(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            s = v.strip()
            return [] if s == "" else [s]
        if isinstance(v, (list, tuple)):
            out = []
            for it in v:
                s = ("" if it is None else str(it)).strip()
                if s:
                    out.append(s)
            return out
        return []

    @field_validator("projects", mode="before")
    @classmethod
    def _coerce_projects(cls, v):
        if isinstance(v, list) and v and isinstance(v[0], list):
            out = []
            for row in v:
                t, d, u = (row + ["", "", None])[:3]
                out.append({"title": t or "", "desc": d or "", "url": (u or None)})
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
                    "details": d or "", "url": (u or None)
                })
            return out
        return v

