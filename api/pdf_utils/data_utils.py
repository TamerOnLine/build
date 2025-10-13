# api/pdf_utils/data_utils.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ============================================================================
# Helpers
# ============================================================================

def _csv_to_list(v: Any) -> List[str]:
    """
    Normalize a CSV string / list / tuple into a clean list[str].
    """
    if v is None:
        return []
    if isinstance(v, str):
        return [x.strip() for x in v.split(",") if x.strip()]
    if isinstance(v, (list, tuple)):
        out: List[str] = []
        for it in v:
            s = ("" if it is None else str(it)).strip()
            if s:
                out.append(s)
        return out
    return []


def _normalize_projects_list(items: Any) -> List[Dict[str, Optional[str]]]:
    """
    Accept projects as str / dict / [list/tuple] and return a uniform list of dicts:
    [{ "title": str, "desc": str, "url": Optional[str] }]
    """
    norm: List[Dict[str, Optional[str]]] = []
    seq: List[Any]
    if items is None:
        seq = []
    elif isinstance(items, (list, tuple)):
        seq = list(items)
    else:
        seq = [items]

    for it in seq:
        if it is None:
            continue
        if isinstance(it, str):
            norm.append({"title": it.strip(), "desc": "", "url": None})
        elif isinstance(it, dict):
            title = (it.get("title") or it.get("name") or "").strip()
            desc = (it.get("desc") or it.get("description") or "").strip()
            url = it.get("url") or it.get("link") or None
            norm.append({"title": title, "desc": desc, "url": url})
        elif isinstance(it, (list, tuple)):
            # [title, desc, url]
            t, d, u = (list(it) + ["", "", None])[:3]
            norm.append({
                "title": (t or "").strip(),
                "desc": (d or "").strip(),
                "url": (u or None),
            })
        # else: ignore unsupported types
    return norm


def _read_bytes_if_exists(pathlike: str | Path | None) -> bytes | None:
    """
    Safely read bytes from a file if it exists and is a valid file.
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


# ----------------------------------------------------------------------------
# Legacy helper kept for backward-compat: returns tuples (title, desc, url)
# Prefer _normalize_projects_list (dicts) for internal usage.
# ----------------------------------------------------------------------------
def _norm_projects(projects_list: List[Any]) -> List[Tuple[str, str, Optional[str]]]:
    """
    Normalize various forms of project entries into a consistent tuple format:
    (title, description, optional link).
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
            link = (it.get("link") or it.get("url") or "").strip() or None
        elif isinstance(it, str):
            title, desc, link = it.strip(), "", None
        else:
            title, desc, link = "", "", None

        if title or desc or link:
            out.append((title, desc, link))
    return out


# ============================================================================
# Public API
# ============================================================================

def build_ready_from_profile(profile: dict) -> Dict[str, Any]:
    """
    Convert a raw profile dict into a normalized, block-ready structure
    for PDF rendering.
    """
    p = profile or {}
    data: Dict[str, Any] = {}

    # Header
    header = p.get("header") or {}
    if header:
        data["header_name"] = header

    # Contact
    contact = p.get("contact") or {}
    if contact:
        data["contact_info"] = contact

    # Summary → text_section
    summary = p.get("summary")
    if summary:
        if isinstance(summary, (list, tuple)):
            joined = "\n".join(str(x) for x in summary if x is not None)
        else:
            joined = str(summary)
        if joined.strip():
            data["text_section"] = {"summary": joined}

    # Skills / Languages (accept CSV string)
    skills = _csv_to_list(p.get("skills"))
    if skills:
        data["key_skills"] = {"items": skills}

    langs = _csv_to_list(p.get("languages"))
    if langs:
        data["languages"] = {"items": langs}

    # Projects → prefer dicts internally, export tuples for existing block impls
    prjs_dicts = _normalize_projects_list(p.get("projects"))
    if prjs_dicts:
        data["projects"] = {"items": [(d["title"], d["desc"], d.get("url")) for d in prjs_dicts]}

    # Education (leave as-is unless you have a dedicated adapter)
    edu = p.get("education")
    if edu:
        if isinstance(edu, (list, tuple)):
            items = [e for e in edu if e is not None]
        else:
            items = [edu]
        data["education"] = {"items": items}

    # Social links unified
    links: List[str] = []
    if contact.get("email"):
        links.append(str(contact["email"]))
    if contact.get("website"):
        links.append(str(contact["website"]))

    gh = contact.get("github")
    if gh:
        gh = str(gh).strip()
        links.append(gh if "://" in gh else f"https://github.com/{gh}")

    li = contact.get("linkedin")
    if li:
        li = str(li).strip()
        links.append(li if "://" in li else f"https://linkedin.com/in/{li}")

    if links:
        data["social_links"] = {"items": links}
        data["links_inline"] = {"links": links}

    # Avatar passthrough (bytes/base64/url handled upstream)
    if "avatar" in p:
        data["avatar_circle"] = p["avatar"]

    return data


# ----------------------------------------------------------------------------
# Adapter to keep compatibility with older text-based block renderers
# ----------------------------------------------------------------------------
def _blocks_adapter(profile: dict) -> dict:
    """
    Make data compatible with older blocks that expect simple text lists:
      - projects: any input → paragraphs list
      - education: dicts → paragraphs list
      - skills/languages: accept CSV → list[str]
    """
    data = (profile or {}).copy()

    # skills / languages CSV → list
    if "skills" in data:
        data["skills"] = _csv_to_list(data.get("skills"))
    if "languages" in data:
        data["languages"] = _csv_to_list(data.get("languages"))

    # projects: normalize to dicts first, then convert to text paragraphs
    projects_norm = _normalize_projects_list(data.get("projects"))
    if projects_norm:
        data["projects"] = [
            f'{p.get("title","")} — {p.get("desc","")}\n{(p.get("url") or "")}'.strip()
            for p in projects_norm
        ]
    else:
        data["projects"] = []

    # education: if dicts → join lines
    edu = data.get("education") or []
    if edu and isinstance(edu, list) and edu and isinstance(edu[0], dict):
        out: List[str] = []
        for e in edu:
            lines = [
                e.get("title", ""),
                e.get("school", ""),
                f'{e.get("start","")} — {e.get("end","")}'.strip(),
                e.get("details", ""),
                e.get("url", ""),
            ]
            out.append("\n".join([ln for ln in lines if ln]))
        data["education"] = out

    return data
