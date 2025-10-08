from __future__ import annotations
import copy
import json
from typing import Any, Dict, List

DEFAULT_PROFILE: Dict[str, Any] = {
    "header": {"name": "", "title": ""},
    "contact": {"email": "", "phone": "", "website": "", "github": "", "linkedin": "", "location": ""},
    "skills": [],
    "languages": [],
    "projects": [],
    "education": [],
    "summary": "",
}

def _to_str(x: Any) -> str:
    return "" if x is None else str(x).strip()

def _as_list(x: Any) -> List[Any]:
    return list(x) if isinstance(x, list) else []

def _normalize_projects(prj: Any) -> List[List[str]]:
    """
    Normalize projects into [[title, desc, url], ...].
    Accepts list of lists/tuples/dicts/scalars.
    Dict keys supported: title/name, description/desc, url.
    """
    out: List[List[str]] = []
    if not isinstance(prj, list):
        return out

    for row in prj:
        title = desc = url = ""
        if isinstance(row, (list, tuple)):
            title = _to_str(row[0]) if len(row) > 0 else ""
            desc  = _to_str(row[1]) if len(row) > 1 else ""
            url   = _to_str(row[2]) if len(row) > 2 else ""
        elif isinstance(row, dict):
            # support both {title, description} and {name, desc}
            title = _to_str(row.get("title") or row.get("name"))
            desc  = _to_str(row.get("description") or row.get("desc"))
            url   = _to_str(row.get("url"))
        else:
            title = _to_str(row)
            desc = url = ""
        if title or desc or url:
            out.append([title, desc, url])
    return out

def _normalize_summary(s: Any) -> str:
    """
    Accepts:
      - str -> trimmed
      - list -> join stringified items with a space
      - dict -> compact JSON
      - other -> ""
    """
    if isinstance(s, str):
        return s.strip()
    if isinstance(s, list):
        return " ".join(_to_str(i) for i in s if _to_str(i))
    if isinstance(s, dict):
        # compact; ensure non-ASCII preserved if later dumped
        return json.dumps(s, ensure_ascii=False, separators=(",", ":"))
    return ""

def ensure_profile_schema(p: dict | None) -> dict:
    """Normalize incoming 'profile' into our DEFAULT_PROFILE structure."""
    base = copy.deepcopy(DEFAULT_PROFILE)

    if not isinstance(p, dict):
        return base

    # Allow nesting like {"profile": {...}}
    if "profile" in p and isinstance(p["profile"], dict):
        p = p["profile"]

    # header/contact: merge dicts
    for k in ("header", "contact"):
        src = p.get(k)
        if isinstance(src, dict):
            # keep only known keys; ignore unknowns silently
            for kk in base[k].keys():
                val = src.get(kk)
                base[k][kk] = _to_str(val) if isinstance(val, (str, int, float)) else base[k][kk]

    # lists (keep only if lists)
    base["skills"] = _as_list(p.get("skills"))
    base["languages"] = _as_list(p.get("languages"))
    base["education"] = _as_list(p.get("education"))

    # projects
    base["projects"] = _normalize_projects(p.get("projects"))

    # summary
    base["summary"] = _normalize_summary(p.get("summary"))

    # ✅ احتفظ بـ photo_b64 إن وُجد
    if isinstance(p.get("photo_b64"), str):
        base["photo_b64"] = p["photo_b64"]

    return base
