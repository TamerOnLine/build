"""
api/pdf_utils/schema.py
-----------------------
Utility functions for validating and normalizing resume profile data
before PDF generation.
"""

from __future__ import annotations
from typing import Any, Dict, List


def ensure_profile_schema(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a profile dictionary to ensure required sections exist
    and have proper data types.

    Sections normalized:
    - header
    - contact
    - skills
    - languages
    - projects
    - education
    """
    data = dict(profile or {})

    # Header normalization
    header = data.get("header", {})
    if not isinstance(header, dict):
        header = {"name": str(header), "title": ""}
    header.setdefault("name", "Unnamed")
    header.setdefault("title", "")
    data["header"] = header

    # Contact normalization
    contact = data.get("contact", {})
    if not isinstance(contact, dict):
        contact = {"email": str(contact)}
    contact.setdefault("email", "")
    contact.setdefault("phone", "")
    contact.setdefault("website", "")
    data["contact"] = contact

    # Skills normalization
    skills = data.get("skills", [])
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]
    elif not isinstance(skills, list):
        skills = [str(skills)]
    data["skills"] = skills

    # Languages normalization
    languages = data.get("languages", [])
    if isinstance(languages, str):
        languages = [l.strip() for l in languages.split(",") if l.strip()]
    elif not isinstance(languages, list):
        languages = [str(languages)]
    data["languages"] = languages

    # Projects normalization
    projects = data.get("projects", [])
    if isinstance(projects, str):
        projects = [projects]
    elif isinstance(projects, dict):
        projects = [projects]
    elif not isinstance(projects, list):
        projects = []
    data["projects"] = projects

    # Education normalization
    education = data.get("education", [])
    if isinstance(education, str):
        education = [education]
    elif not isinstance(education, list):
        education = []
    data["education"] = education

    return data


# Optional helper to validate structure (for debugging)
def validate_profile_keys(profile: Dict[str, Any]) -> List[str]:
    """Return a list of missing top-level keys in the profile."""
    required = ["header", "contact", "skills", "languages", "projects", "education"]
    return [k for k in required if k not in profile]
