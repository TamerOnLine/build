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
    return start or end  # one side only

def _as_projects(items: Any) -> List[List[str]]:
    """
    Normalize 'projects' into [[name, desc, url], ...].
    Accepts:
      - list/tuple of [name, desc, url?]
      - dicts with keys: name/title, desc/description, url
      - scalars -> [scalar, "", ""]
    """
    out: List[List[str]] = []
    if not items:
        return out

    def _triple(name: Any, desc: Any, url: Any) -> List[str]:
        n, d, u = _to_str(name), _to_str(desc), _to_str(url)
        if n or d or u:
            return [n, d, u]
        return []

    for it in (items or []):
        if isinstance(it, (list, tuple)):
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
        else:
            s = _to_str(it)
            if s:
                out.append([s, "", ""])
    return out

def map_education_rows_to_items(edu_rows: List[Any]) -> List[str]:
    """
    Convert education entries into multiline strings.
    Accepts rows as:
      - [title, school, start, end, details, url]
      - dict with keys: title, school, start, end, details, url
      - anything else will be coerced to a single-line string.
    Output lines per item: title, school, "start – end" (if both given), details, url
    """
    items: List[str] = []
    for row in edu_rows or []:
        title = school = start = end = details = url = ""

        if isinstance(row, dict):
            title   = _to_str(row.get("title"))
            school  = _to_str(row.get("school"))
            start   = _to_str(row.get("start"))
            end     = _to_str(row.get("end"))
            details = _to_str(row.get("details"))
            url     = _to_str(row.get("url"))
        elif isinstance(row, (list, tuple)):
            vals = [ _to_str(v) for v in list(row) ] + [""] * 6
            title, school, start, end, details, url = vals[:6]
        else:
            s = _to_str(row)
            if s:
                items.append(s)
            continue

        period = _join_range(start, end)
        lines = [x for x in [title, school, period, details, url] if x]
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

    # header_name
    hdr = p.get("header") or {}
    name, title = _to_str(hdr.get("name")), _to_str(hdr.get("title"))
    if name or title:
        ov["header_name"] = {"data": {"name": name, "title": title}}

    # contact_info - MUST be {"items": {...}}
    contact = dict(p.get("contact") or {})
    if contact:
        ov["contact_info"] = {"data": {"items": contact}}

    # key_skills expects "skills"
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

    # social_links يمكن استخدامها كاستقدام contact كمدخل مباشر (مثلاً github/linkedin/website...)
    if contact:
        ov["social_links"] = {"data": contact}

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
