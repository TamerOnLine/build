from __future__ import annotations
from typing import Any, Dict, List, Tuple, Optional

# ---------- Utilities ----------
def _as_list(x: Any) -> List[str]:
    if x is None:
        return []
    if isinstance(x, (list, tuple, set)):
        return [str(i) for i in x if i is not None]
    return [str(x)]

def _as_text(x: Any) -> str:
    if x is None:
        return ""
    if isinstance(x, (list, tuple)):
        return "\n".join(str(i) for i in x if i is not None)
    return str(x)

def _trimmed(d: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in d.items() if v not in (None, "", [], {})}

def _linkify_contact(contact: Dict[str, Any]) -> List[str]:
    out: List[str] = []
    if not isinstance(contact, dict):
        return out
    email = contact.get("email")
    if email:
        out.append(str(email))
    website = contact.get("website")
    if website:
        out.append(str(website))
    gh = contact.get("github")
    if gh:
        gh = str(gh)
        out.append(gh if "://" in gh else f"https://github.com/{gh}")
    li = contact.get("linkedin")
    if li:
        li = str(li)
        out.append(li if "://" in li else f"https://linkedin.com/in/{li}")
    return out

def _as_projects(items: Any) -> List[List[str]]:
    """
    Normalize project entries to a list of 3-item lists:
    [[name, description, url], ...]
    """
    if items is None:
        return []
    out: List[List[str]] = []
    if isinstance(items, (list, tuple)):
        for it in items:
            if isinstance(it, (list, tuple)) and len(it) >= 2:
                name = str(it[0])
                desc = str(it[1])
                url  = str(it[2]) if len(it) >= 3 and it[2] is not None else ""
                out.append([name, desc, url])
            elif isinstance(it, dict):
                name = str(it.get("name", ""))
                desc = str(it.get("desc", it.get("description", "")))
                url  = str(it.get("url", ""))
                if name or desc or url:
                    out.append([name, desc, url])
            else:
                s = str(it)
                if s:
                    out.append([s, "", ""])
    else:
        s = str(items)
        if s:
            out.append([s, "", ""])
    return out

# ---------- Default mapping rules ----------
DEFAULT_RULES: Dict[str, Any] = {
    "header_name": lambda p: p.get("header") or {},
    "contact_info": lambda p: p.get("contact") or {},
    "text_section": lambda p: {
        "summary": _as_text(p.get("summary"))
    } if p.get("summary") is not None else {},
    "key_skills": lambda p: {
        "items": _as_list(p.get("skills"))
    } if p.get("skills") is not None else {},
    "languages": lambda p: {
        "items": _as_list(p.get("languages"))
    } if p.get("languages") is not None else {},
    "projects": lambda p: {
        "items": _as_projects(p.get("projects"))
    } if p.get("projects") is not None else {},
    "education": lambda p: {
        "items": _as_list(p.get("education"))
    } if p.get("education") is not None else {},
    "social_links": lambda p: {
        "items": _linkify_contact(p.get("contact") or {})
    },
    "links_inline": lambda p: {
        "links": _linkify_contact(p.get("contact") or {})
    },
    "avatar_circle": lambda p: p.get("avatar") or {},
}

def _merge_rules(base: Dict[str, Any], override: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not override:
        return base
    merged = dict(base)
    for k, v in override.items():
        if isinstance(v, str):
            merged[k] = lambda p, key=v: _trimmed({"value": p.get(key)})
        elif isinstance(v, dict):
            src = v.get("from")
            fn  = v.get("fn")
            if not src:
                continue
            if fn == "text":
                merged[k] = lambda p, s=src: _trimmed({"value": _as_text(p.get(s))})
            elif fn == "list":
                merged[k] = lambda p, s=src: _trimmed({"items": _as_list(p.get(s))})
            elif fn == "projects":
                merged[k] = lambda p, s=src: _trimmed({"items": _as_projects(p.get(s))})
            else:
                merged[k] = lambda p, s=src: _trimmed({"value": p.get(s)})
    return merged

def map_profile_to_ready(
    profile: Dict[str, Any],
    *,
    ui_lang: Optional[str] = None,
    rtl_mode: Optional[bool] = None,
    map_rules_override: Optional[Dict[str, Any]] = None,
) -> Tuple[Dict[str, Any], List[str]]:
    """
    Converts a raw profile into a standardized "ready" dictionary for rendering blocks.
    Returns (ready, warnings).
    """
    p = profile or {}
    warnings: List[str] = []

    rules = _merge_rules(DEFAULT_RULES, map_rules_override)
    ready: Dict[str, Any] = {}

    for block_id, fn in rules.items():
        try:
            val = fn(p)
            if val not in (None, {}, [], ""):
                ready[block_id] = val
        except Exception as e:
            warnings.append(f"mapper for '{block_id}' failed: {e}")

    if ui_lang:
        ready["_ui_lang"] = ui_lang
    if rtl_mode is not None:
        ready["_rtl"] = bool(rtl_mode)

    return ready, warnings

