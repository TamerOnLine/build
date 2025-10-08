from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

def _norm_projects(projects_list: List[Any]) -> List[Tuple[str, str, Optional[str]]]:
    """
    Normalize various forms of project entries into a consistent tuple format:
    (title, description, optional link).

    Args:
        projects_list (List[Any]): A list of project entries.

    Returns:
        List[Tuple[str, str, Optional[str]]]: Normalized list of project tuples.
    """
    out: List[Tuple[str, str, Optional[str]]] = []
    for it in projects_list or []:
        if isinstance(it, (list, tuple)) and it:
            title = (it[0] or "").strip() if len(it) > 0 else ""
            desc = (it[1] or "").strip() if len(it) > 1 else ""
            link = (it[2] or "").strip() if len(it) > 2 else None
        elif isinstance(it, dict):
            title = (it.get("title") or "").strip()
            desc = (it.get("desc") or it.get("description") or "").strip()
            link = (it.get("link") or "").strip() or None
        else:
            title, desc, link = "", "", None
        if title or desc or link:
            out.append((title, desc, link))
    return out

def _read_bytes_if_exists(pathlike: str | Path | None) -> bytes | None:
    """
    Safely read bytes from a file if it exists and is a valid file.

    Args:
        pathlike (str | Path | None): The path to the file.

    Returns:
        bytes | None: The file contents as bytes, or None if not found/readable.
    """
    if not pathlike:
        return None
    p = Path(pathlike)
    if p.exists() and p.is_file():
        try:
            return p.read_bytes()
        except Exception:
            return None
    return None

def build_ready_from_profile(profile: dict) -> Dict[str, Any]:
    """
    Convert a raw profile dict into a normalized format for block rendering.

    Args:
        profile (dict): Raw user profile data.

    Returns:
        Dict[str, Any]: Transformed block-ready profile data.
    """
    p = profile or {}
    data: Dict[str, Any] = {}

    # Header and contact blocks
    if "header" in p:
        data["header_name"] = p["header"]

    contact = p.get("contact") or {}
    if contact:
        data["contact_info"] = contact

    # Summary
    if "summary" in p and p["summary"]:
        if isinstance(p["summary"], (list, tuple)):
            joined = "\n".join(str(x) for x in p["summary"])
        else:
            joined = str(p["summary"])
        data["text_section"] = {"summary": joined}

    # Skills
    if "skills" in p and p["skills"]:
        items = p["skills"]
        data["key_skills"] = {
            "items": [str(x) for x in (items if isinstance(items, (list, tuple)) else [items])]
        }

    # Languages
    if "languages" in p and p["languages"]:
        items = p["languages"]
        data["languages"] = {
            "items": [str(x) for x in (items if isinstance(items, (list, tuple)) else [items])]
        }

    # Projects
    if "projects" in p and p["projects"]:
        prjs = p["projects"]
        norm = _norm_projects(list(prjs) if isinstance(prjs, (list, tuple)) else [prjs])
        data["projects"] = {"items": norm}

    # Education
    if "education" in p and p["education"]:
        edu = p["education"]
        items = [str(x) for x in edu] if isinstance(edu, (list, tuple)) else [str(edu)]
        data["education"] = {"items": items}

    # Social links
    links = []
    if contact.get("email"):
        links.append(str(contact["email"]))
    if contact.get("website"):
        links.append(str(contact["website"]))
    gh = contact.get("github")
    if gh:
        gh = str(gh)
        links.append(gh if "://" in gh else f"https://github.com/{gh}")
    li = contact.get("linkedin")
    if li:
        li = str(li)
        links.append(li if "://" in li else f"https://linkedin.com/in/{li}")

    if links:
        data["social_links"] = {"items": links}
        data["links_inline"] = {"links": links}

    # Avatar
    if "avatar" in p:
        data["avatar_circle"] = p["avatar"]

    return data

