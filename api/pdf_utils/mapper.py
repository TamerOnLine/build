from __future__ import annotations
from typing import Any, Dict, Iterable, List, Sequence, Tuple

EN_DASH = "\u2013"  # "–"

def _to_str(x: Any) -> str:
    return "" if x is None else str(x).strip()

def _as_list(x: Any) -> List[str]:
    """
    Coerce x to a list[str] (dropping None), stripping whitespace.
    - None -> []
    - scalar -> [str(scalar)]
    - iterable -> [str(i) for i in iterable if i is not None]
    """
    if x is None:
        return []
    if isinstance(x, (list, tuple, set)):
        return [_to_str(i) for i in x if i is not None and _to_str(i)]
    s = _to_str(x)
    return [s] if s else []

def _join_range(start: str, end: str) -> str:
    start, end = _to_str(start), _to_str(end)
    if start and end:
        return f"{start} {EN_DASH} {end}"
    return start or end

def _as_projects(v: Any) -> List[List[str]]:
    """
    Normalize projects to a list of [title, desc, url].
    Accepts: str | dict | [t,d,u] | iterable of those.
    """
    if v is None:
        return []
    seq: Iterable[Any]
    if isinstance(v, (list, tuple)):
        seq = v
    else:
        seq = [v]
    out: List[List[str]] = []
    for it in seq:
        if it is None:
            continue
        if isinstance(it, str):
            t = _to_str(it)
            if t:
                out.append([t, "", ""])
        elif isinstance(it, (list, tuple)):
            # pad to 3
            vals: List[str] = [_to_str(v) for v in list(it)[:3]]
            while len(vals) < 3:
                vals.append("")
            triple = _triple(vals[0], vals[1], vals[2])
            if triple:
                out.append(triple)
        elif isinstance(it, dict):
            name = it.get("name", "") or it.get("title", "")
            desc = it.get("desc", "") or it.get("description", "")
            url  = it.get("url", "")
            triple = _triple(name, desc, url)
            if triple:
                out.append(triple)
    return out

def _triple(a: str, b: str, c: str) -> List[str] | None:
    a, b, c = _to_str(a), _to_str(b), _to_str(c)
    if any([a, b, c]):
        return [a, b, c]
    return None

def map_education_rows_to_items(edu: Sequence[Any]) -> List[str]:
    """
    Map education rows into multi-line strings for a legacy text block.
    Accepts: dicts or [title, school, start, end, details, url].
    """
    items: List[str] = []
    for row in edu or []:
        if isinstance(row, dict):
            title  = _to_str(row.get("title"))
            school = _to_str(row.get("school"))
            years  = _join_range(row.get("start"), row.get("end"))
            details = _to_str(row.get("details"))
            url = _to_str(row.get("url"))
        elif isinstance(row, (list, tuple)):
            vals = list(row) + ["", "", "", "", "", ""]
            title  = _to_str(vals[0])
            school = _to_str(vals[1])
            years  = _join_range(vals[2], vals[3])
            details = _to_str(vals[4])
            url = _to_str(vals[5])
        else:
            continue
        lines = [x for x in [title, school, years, details, url] if x]
        if lines:
            items.append("\n".join(lines))
    return items

def profile_to_overrides(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map a 'profile' dict to render-time overrides expected by the layout layer.
    Returns a dict like:
      {
        "header_name": {"data": {"name": "...", "title": "..."}},
        "contact_info": {"data": {"items": {...}}},
        "key_skills": {"data": {"skills": [...]}},
        "languages": {"data": {"languages": [...]}},
        "projects": {"data": {"items": [[name, desc, url], ...]}},
        "text_section:summary": {"data": {"section": "summary", "text": "..."}},
        "social_links": {"data": {...}},
        "avatar_circle": {"data": {"photo_b64": "...", "max_d_mm": 42}},
        "education": {"data": {"items": ["line1\\nline2...", ...]}},
      }
    """
    p = profile or {}
    ov: Dict[str, Any] = {}

    # header
    header = p.get("header") or {}
    if header:
        name = _to_str(header.get("name"))
        title = _to_str(header.get("title"))
        ov["header_name"] = {"data": {"name": name, "title": title}}

    # contact → dict (used by contact_info + social_links)
    contact_raw = p.get("contact") or {}
    contact = {k: _to_str(v) for k, v in contact_raw.items()}

    if contact:
        ov["contact_info"] = {"data": contact}

    # skills expects "skills"
    skills = _as_list(p.get("skills"))
    if skills:
        ov["key_skills"] = {"data": {"skills": skills}}

    # languages expects "languages"
    languages = _as_list(p.get("languages"))
    if languages:
        ov["languages"] = {"data": {"languages": languages}}

    # projects expects "items": [[title,desc,url], ...]
    projs = _as_projects(p.get("projects"))
    if projs:
        ov["projects"] = {"data": {"items": projs}}

    # summary -> text_section:summary
    summary = _to_str(p.get("summary"))
    if summary:
        ov["text_section:summary"] = {"data": {"section": "summary", "text": summary}}

    # social_links (may reuse contact merged map)
    if contact:
        ov["social_links"] = {"data": contact}

    # prefer avatar_url (external file) first
    avatar_url = _to_str(p.get("avatar_url"))
    if avatar_url:
        ov["avatar_circle"] = {"data": {"url": avatar_url, "max_d_mm": 42}}
    else:
        # avatar_b64 -> avatar_circle.photo_b64
        avatar_b64 = _to_str(p.get("avatar_b64"))
        if avatar_b64:
            ov["avatar_circle"] = {"data": {"photo_b64": avatar_b64, "max_d_mm": 42}}

    # education -> list of multiline strings
    edu = p.get("education") or []
    ed_items = map_education_rows_to_items(edu)
    if ed_items:
        ov["education"] = {"data": {"items": ed_items}}

    return ov
