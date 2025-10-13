"""PDF resume builder (v1.4 + safe fonts).

Generates resume PDFs using ReportLab with optional RTL/Arabic shaping.
Adds dynamic font availability checks & safe fallbacks to avoid KeyError.
"""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from reportlab.lib.colors import HexColor, black
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics


# ========== Font/RTL helpers (trimmed for brevity, keep your originals) ==========
def _is_arabic(s: str) -> bool:
    if not s:
        return False
    for ch in str(s):
        if "\u0600" <= ch <= "\u06FF":
            return True
    return False


def _pick_line_font(st, prefer_ar="NotoNaskhArabic", prefer_lat="DejaVuSans"):
    regs = set(pdfmetrics.getRegisteredFontNames())
    if prefer_ar in regs and prefer_lat in regs:
        return prefer_ar if _is_arabic(st) else prefer_lat
    if prefer_ar in regs:
        return prefer_ar
    if prefer_lat in regs:
        return prefer_lat
    return st  # fallback to whatever the caller gave


def _safe_set_font(c: canvas.Canvas, name: str, size: int) -> None:
    """Try setFont; fallback gracefully to DejaVuSans or Helvetica."""
    try:
        c.setFont(name, size)
        return
    except Exception:
        pass
    regs = set(pdfmetrics.getRegisteredFontNames())
    fb = "DejaVuSans" if "DejaVuSans" in regs else "Helvetica"
    c.setFont(fb, size)


def _resolve_font_name(name: str) -> str:
    """Return an available font name or a safe fallback."""
    regs = set(pdfmetrics.getRegisteredFontNames())
    if name in regs:
        return name
    if name and name + "-Bold" in regs:
        return name
    if "NotoNaskhArabic" in regs:
        return "NotoNaskhArabic"
    if "DejaVuSans" in regs:
        return "DejaVuSans"
    return "Helvetica"


from reportlab.lib.units import mm

def _ensure_single_column_layout(layout: dict | None, profile: dict) -> dict:
    """Ensure a valid single-column layout if columns/flow are missing."""
    layout = (layout or {}).copy()
    columns = layout.get("columns") or []
    flow = layout.get("flow") or []
    if not columns:
        columns = [{"id": "main", "width": "100%"}]
        layout["columns"] = columns
    if not flow:
        blocks: list[str] = []
        if (profile.get("header") or profile.get("header_name")):
            blocks.append("header_name")
        if profile.get("skills"):
            blocks.append("key_skills")
        if profile.get("projects"):
            blocks.append("projects")
        if profile.get("languages"):
            blocks.append("languages")
        if not blocks:
            blocks = ["header_name"]
        layout["flow"] = [{"column": columns[0]["id"], "blocks": blocks}]
    else:
        # normalize blocks to strings
        for step in layout["flow"]:
            if isinstance(step.get("blocks"), (list, tuple)):
                step["blocks"] = [str(b).strip() for b in step["blocks"] if str(b).strip()]
    return layout


# ========== Helpers ==========
def _block_name_arg(b: Any) -> Tuple[str, Optional[str]]:
    """
    Robustly parse a block entry. Accepts:
      - "block"
      - "block:arg"
      - {"name": "block", "arg": "..."}
      - ("block", "arg")
    Returns: (name, arg or None)
    """
    if b is None:
        return "", None
    if isinstance(b, str):
        if ":" in b:
            n, a = b.split(":", 1)
            return n.strip(), a.strip() or None
        return b.strip(), None
    if isinstance(b, dict):
        return (str(b.get("name", "")).strip(), (b.get("arg") or None))
    if isinstance(b, (list, tuple)):
        name = str(b[0]).strip() if len(b) > 0 else ""
        arg = (str(b[1]).strip() if len(b) > 1 and b[1] is not None else None)
        return name, arg
    return "", None


def _normalize_blocks_list(blocks: Any) -> List[Any]:
    """
    Ensure blocks is a list of entries (strings or dicts).
    """
    if blocks is None:
        return []
    if isinstance(blocks, list):
        return blocks
    if isinstance(blocks, tuple):
        return list(blocks)
    return [blocks]


def _text_to_lines(val: Any) -> List[str]:
    if val is None:
        return []
    if isinstance(val, list):
        return [str(x).strip() for x in val if str(x).strip()]
    return [ln.strip() for ln in str(val).splitlines() if ln.strip()]


def _projects_to_rows(val: Any) -> List[Tuple[str, str, str]]:
    rows: List[Tuple[str, str, str]] = []
    if not isinstance(val, list):
        return rows
    for it in val:
        t = d = u = ""
        if isinstance(it, (list, tuple)):
            t = (it[0] or "") if len(it) > 0 else ""
            d = (it[1] or "") if len(it) > 1 else ""
            u = (it[2] or "") if len(it) > 2 else ""
        elif isinstance(it, dict):
            t = it.get("title", "")
            d = it.get("description", "")
            u = it.get("url", "")
        if t or d or u:
            rows.append((t.strip(), d.strip(), u.strip()))
    return rows


def _wrap_text(
    c: canvas.Canvas,
    text: str,
    max_w: float,
    font: str = "Helvetica",
    size: int = 10,
) -> List[str]:
    _safe_set_font(c, font, size)
    words = text.split()
    lines: List[str] = []
    cur: List[str] = []
    for w in words:
        trial = " ".join(cur + [w]) if cur else w
        tw = pdfmetrics.stringWidth(trial, font, size)
        if tw <= max_w or not cur:
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def _draw_paragraph(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    text: str,
    lead: float,
    font: str,
    size: int,
    rtl: bool = False,
) -> float:
    lines = []
    for raw in text.splitlines():
        st = raw.strip()
        if not st:
            continue
        fnt = _pick_line_font(st, prefer_ar="NotoNaskhArabic", prefer_lat=font)
        part = _wrap_text(c, st, w, fnt, size)
        lines.extend(part if part else [st])

    for ln in lines:
        if rtl:
            tw = pdfmetrics.stringWidth(ln, font, size)
            c.drawRightString(x + w, y, ln)
        else:
            c.drawString(x, y, ln)
        y -= lead
    return y


def _pct_to_w(pct: Any, full_w: float) -> float:
    try:
        if isinstance(pct, (int, float)):
            return float(pct)
        if isinstance(pct, str) and pct.endswith("%"):
            return (float(pct[:-1]) / 100.0) * full_w
    except Exception:
        pass
    return full_w


def _deep_update(target: dict, source: dict) -> dict:
    for k, v in (source or {}).items():
        if isinstance(v, dict) and isinstance(target.get(k), dict):
            _deep_update(target[k], v)
        else:
            target[k] = v
    return target


def _load_theme_from_disk(theme_name: Optional[str]) -> dict:
    # Dummy theme loader — replace with your theme loader as needed
    theme = {
        "colors": {"primary": "#0F172A", "text": "#0B0F19", "accent": "#2563EB", "bg": "#FFFFFF"},
        "fonts": {"base": "DejaVuSans", "bold": "DejaVuSans-Bold", "heading": "DejaVuSans-Bold"},
        "sizes": {
            "h1": 20, "h2": 12, "h3": 11,
            "lead_h1": 26, "lead_h2": 16, "lead_h3": 14,
            "body": 10, "lead_body": 14,
        }
    }
    return theme


# ========== Blocks ==========
def _block_header_name(
    c: canvas.Canvas,
    x: float, y: float, w: float,
    profile: Dict[str, Any],
    st: Dict[str, Any],
    rtl: bool,
) -> float:
    header = profile.get("header") or profile.get("header_name") or {}
    name = (header.get("name") or "").strip()
    title = (header.get("title") or "").strip()
    _safe_set_font(c, st["font_head"], st["sizes"]["h1"])
    (c.drawRightString if rtl else c.drawString)(x + (w if rtl else 0), y, name)
    y -= st["sizes"]["lead_h1"]
    if title:
        _safe_set_font(c, st["font_bold"], st["sizes"]["h2"])
        (c.drawRightString if rtl else c.drawString)(x + (w if rtl else 0), y, title)
        y -= st["sizes"]["lead_h2"]
    return y - st["sp_after_header"]


def _block_contact_info(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    profile: Dict[str, Any],
    st: Dict[str, Any],
    rtl: bool,
) -> float:
    contact = profile.get("contact") or {}
    if not contact:
        return y
    _safe_set_font(c, st["font_bold"], st["sizes"]["h3"])
    (c.drawRightString if rtl else c.drawString)(x + (w if rtl else 0), y, "Contact")
    y -= st["sizes"]["lead_h3"]
    _safe_set_font(c, st["font"], st["sizes"]["body"])
    for _, v in contact.items():
        if v:
            y = _draw_paragraph(
                c, x, y, w, f"• {v}", st["sizes"]["lead_body"], st["font"], st["sizes"]["body"], rtl
            )
    return y - st["sp_after_list"]


def _block_social_links(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    profile: Dict[str, Any],
    st: Dict[str, Any],
    rtl: bool,
) -> float:
    contact = profile.get("contact") or {}
    links: List[str] = []
    for k in ("email", "website", "github", "linkedin"):
        v = (contact.get(k) or "").strip()
        if v:
            links.append(v)
    if not links:
        return y
    _safe_set_font(c, st["font_bold"], st["sizes"]["h3"])
    (c.drawRightString if rtl else c.drawString)(x + (w if rtl else 0), y, "Links")
    y -= st["sizes"]["lead_h3"]
    _safe_set_font(c, st["font"], st["sizes"]["body"])
    for v in links:
        y = _draw_paragraph(
            c, x, y, w, f"• {v}", st["sizes"]["lead_body"], st["font"], st["sizes"]["body"], rtl
        )
    return y - st["sp_after_list"]


def _block_key_skills(
    c: canvas.Canvas, x: float, y: float, w: float, profile: Dict[str, Any], st: Dict[str, Any], rtl: bool
) -> float:
    items = profile.get("skills") or profile.get("key_skills") or []
    items = [i for i in items if i]
    if not items:
        return y
    _safe_set_font(c, st["font_bold"], st["sizes"]["h3"])
    (c.drawRightString if rtl else c.drawString)(x + (w if rtl else 0), y, "Skills")
    y -= st["sizes"]["lead_h3"]
    _safe_set_font(c, st["font"], st["sizes"]["body"])
    y = _draw_paragraph(c, x, y, w, " • ".join(items), st["sizes"]["lead_body"], st["font"], st["sizes"]["body"], rtl)
    return y - st["sp_after_par"]


def _block_languages(
    c: canvas.Canvas, x: float, y: float, w: float, profile: Dict[str, Any], st: Dict[str, Any], rtl: bool
) -> float:
    items = profile.get("languages") or []
    items = [i for i in items if i]
    if not items:
        return y
    _safe_set_font(c, st["font_bold"], st["sizes"]["h3"])
    (c.drawRightString if rtl else c.drawString)(x + (w if rtl else 0), y, "Languages")
    y -= st["sizes"]["lead_h3"]
    _safe_set_font(c, st["font"], st["sizes"]["body"])
    y = _draw_paragraph(c, x, y, w, " • ".join(items), st["sizes"]["lead_body"], st["font"], st["sizes"]["body"], rtl)
    return y - st["sp_after_par"]


def _block_projects(
    c: canvas.Canvas, x: float, y: float, w: float, profile: Dict[str, Any], st: Dict[str, Any], rtl: bool
) -> float:
    items = _projects_to_rows(profile.get("projects") or profile.get("projects_rows") or [])
    if not items:
        return y
    _safe_set_font(c, st["font_bold"], st["sizes"]["h3"])
    (c.drawRightString if rtl else c.drawString)(x + (w if rtl else 0), y, "Projects")
    y -= st["sizes"]["lead_h3"]
    _safe_set_font(c, st["font"], st["sizes"]["body"])
    for (t, d, u) in items:
        para = t
        if d:
            para += f" — {d}"
        if u:
            para += f"\n{u}"
        y = _draw_paragraph(c, x, y, w, para, st["sizes"]["lead_body"], st["font"], st["sizes"]["body"], rtl)
    return y - st["sp_after_list"]


def _block_education(
    c: canvas.Canvas, x: float, y: float, w: float, profile: Dict[str, Any], st: Dict[str, Any], rtl: bool
) -> float:
    items = _text_to_lines(profile.get("education") or [])
    if not items:
        return y
    _safe_set_font(c, st["font_bold"], st["sizes"]["h3"])
    (c.drawRightString if rtl else c.drawString)(x + (w if rtl else 0), y, "Education")
    y -= st["sizes"]["lead_h3"]
    _safe_set_font(c, st["font"], st["sizes"]["body"])
    for ln in items:
        y = _draw_paragraph(c, x, y, w, ln, st["sizes"]["lead_body"], st["font"], st["sizes"]["body"], rtl)
    return y - st["sp_after_list"]


def _block_text_section(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    text: str,
    st: Dict[str, Any],
    rtl: bool,
    title: Optional[str] = None,
) -> float:
    if title:
        _safe_set_font(c, st["font_bold"], st["sizes"]["h3"])
        (c.drawRightString if rtl else c.drawString)(x + (w if rtl else 0), y, title)
        y -= st["sizes"]["lead_h3"]
    y = _draw_paragraph(
        c, x, y, w, text, st["sizes"]["lead_body"], st["font"], st["sizes"]["body"], rtl
    )
    return y - st["sp_after_par"]


def _block_left_panel_bg(
    c: canvas.Canvas,
    x: float,
    y_top: float,
    w: float,
    page_h: float,
    st: Dict[str, Any],
    pad_mm: float = 6,
    bg: str = "#F8FAFC",
) -> None:
    pad = pad_mm * mm
    c.saveState()
    c.setFillColor(HexColor(bg))
    c.rect(x - pad, 0, w + 2 * pad, page_h, stroke=0, fill=1)
    c.restoreState()


# Map of block names → renderer
BLOCKS: Dict[str, Callable[..., float]] = {
    "header_name": _block_header_name,
    "contact_info": _block_contact_info,
    "social_links": _block_social_links,
    "key_skills": _block_key_skills,
    "languages": _block_languages,
    "projects": _block_projects,
    "education": _block_education,
    "text_section": lambda c, x, y, w, profile, st, rtl: _block_text_section(
        c, x, y, w, (profile.get("text_section") or profile.get("summary") or ""), st, rtl, None
    ),
    "left_panel_bg": lambda *args, **kwargs: None,  # drawn specially
}


# ========== Builder ==========
def build_resume_pdf(*, data: Dict[str, Any]) -> bytes:
    profile = ensure_profile_schema(data.get("profile") or {})
    layout = _ensure_single_column_layout(data.get("layout_inline"), profile)
    rtl = bool(data.get("rtl_mode"))
    theme_inline = data.get("theme_inline") or _load_theme_from_disk(
        data.get("theme_name")
    )

    style: Dict[str, Any] = {
        "colors": {"primary": "#0F172A", "text": "#000", "accent": "#2563EB", "bg": "#FFF"},
        "fonts": {"base": "Helvetica", "bold": "Helvetica-Bold", "heading": "Helvetica-Bold"},
        "sizes": {
            "h1": 18, "h2": 12, "h3": 11,
            "lead_h1": 22, "lead_h2": 18, "lead_h3": 16,
            "body": 10, "lead_body": 14,
        },
        "sp_after_header": 6,
        "sp_after_par": 6,
        "sp_after_list": 6,
    }

    _deep_update(style, theme_inline)
    _deep_update(style, layout.get("overrides") or {})

    base = _resolve_font_name(style["fonts"].get("base", "Helvetica"))
    bold = _resolve_font_name(style["fonts"].get("bold", "Helvetica-Bold"))
    head = _resolve_font_name(style["fonts"].get("heading", bold or base))

    st: Dict[str, Any] = {
        "primary": HexColor(style["colors"]["primary"]),
        "text": HexColor(style["colors"]["text"]),
        "accent": HexColor(style["colors"]["accent"]),
        "bg": HexColor(style["colors"]["bg"]),
        "font": base,
        "font_bold": bold,
        "font_head": head,
        "sizes": style["sizes"],
        "sp_after_header": style.get("sp_after_header", 6),
        "sp_after_par": style.get("sp_after_par", 6),
        "sp_after_list": style.get("sp_after_list", 6),
    }

    page = layout.get("page") or {}
    margins = page.get("margin_mm", {"top": 22, "bottom": 18, "left": 18, "right": 18})
    pw, ph = A4
    left, right, top, bottom = (
        float(margins.get("left", 18)) * mm,
        float(margins.get("right", 18)) * mm,
        float(margins.get("top", 22)) * mm,
        float(margins.get("bottom", 18)) * mm,
    )

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    if st["bg"] != black:
        c.setFillColor(st["bg"])
        c.rect(0, 0, pw, ph, stroke=0, fill=1)
        c.setFillColor(st["text"])

    usable_w = pw - left - right
    cols_def = layout.get("columns") or [{"id": "main", "width": "100%"}]
    cols: Dict[str, Tuple[float, float]] = {}
    x_cursor = left
    for col in cols_def:
        cw = _pct_to_w(col.get("width", "100%"), usable_w)
        cols[col["id"]] = (x_cursor, cw)
        x_cursor += cw

    flow = layout.get("flow") or [
        {"column": "main", "blocks": ["header_name", "text_section:summary", "projects", "education"]}
    ]
    y_top = ph - top
    y_pos: Dict[str, float] = {cid: y_top for cid in cols}

    def ensure_space(cid: str, h: float = 60) -> None:
        if y_pos[cid] - h < bottom:
            c.showPage()
            if st["bg"] != black:
                c.setFillColor(st["bg"])
                c.rect(0, 0, pw, ph, stroke=0, fill=1)
                c.setFillColor(st["text"])
            y_pos.update({k: y_top for k in cols})

    for sec in flow:
        cid = sec.get("column", "main")
        x, w = cols.get(cid, (left, usable_w))

        # تطبيع blocks ثم التعامل مع left_panel_bg إن وُجد
        blocks = _normalize_blocks_list(sec.get("blocks") or [])

        def _is_left_bg(entry: Any) -> bool:
            nm, _ = _block_name_arg(entry)
            return nm == "left_panel_bg"

        if any(_is_left_bg(b) for b in blocks):
            over = layout.get("overrides", {}).get("left_panel_bg", {}).get("data", {})
            _block_left_panel_bg(
                c, x, y_top, w, ph, {"font": st["font"], "sizes": st["sizes"]}, pad_mm=over.get("pad_mm", 6),
                bg=over.get("bg", "#F8FAFC")
            )

        y = y_pos[cid]
        for blk in blocks:
            name, arg = _block_name_arg(blk)
            ensure_space(cid)
            if name == "header_name":
                y = _block_header_name(c, x, y, w, profile, st, rtl)
            elif name == "contact_info":
                y = _block_contact_info(c, x, y, w, profile, st, rtl)
            elif name == "social_links":
                y = _block_social_links(c, x, y, w, profile, st, rtl)
            elif name == "key_skills":
                y = _block_key_skills(c, x, y, w, profile, st, rtl)
            elif name == "languages":
                y = _block_languages(c, x, y, w, profile, st, rtl)
            elif name == "projects":
                y = _block_projects(c, x, y, w, profile, st, rtl)
            elif name == "education":
                y = _block_education(c, x, y, w, profile, st, rtl)
            elif name == "text_section":
                src = arg or ((layout.get("map_rules") or {}).get("text_section") or {}).get("from")
                val = profile.get(src, "")
                if isinstance(val, list):
                    val = " ".join(val)
                y = _block_text_section(c, x, y, w, val, st, rtl)
            elif name in BLOCKS:
                y = BLOCKS[name](c, x, y, w, profile, st, rtl)

        y_pos[cid] = y

    c.showPage()
    c.save()
    return buf.getvalue()


# ========== Schema normalizer (ensure_profile_schema) ==========
def ensure_profile_schema(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Minimal schema-normalizer so builder can render:
      - skills / languages: CSV string or list → list[str]
      - projects: accept list of tuples/dicts/strings → list[tuple(title, desc, url)]
      - education: accept list[str] or str → list[str]
    """
    p = (profile or {}).copy()

    def _csv(v):
        if v is None:
            return []
        if isinstance(v, str):
            return [x.strip() for x in v.split(",") if x.strip()]
        if isinstance(v, (list, tuple)):
            return [str(x).strip() for x in v if str(x).strip()]
        return []

    p["skills"] = _csv(p.get("skills"))
    p["languages"] = _csv(p.get("languages"))

    # projects → rows
    rows: List[Tuple[str, str, Optional[str]]] = []
    raw = p.get("projects") or []
    if not isinstance(raw, list):
        raw = [raw]
    for it in raw:
        t = d = u = ""
        if it is None:
            continue
        if isinstance(it, str):
            t = it.strip()
        elif isinstance(it, dict):
            t = (it.get("title") or it.get("name") or "").strip()
            d = (it.get("desc") or it.get("description") or "").strip()
            u = (it.get("url") or it.get("link") or "").strip()
        elif isinstance(it, (list, tuple)):
            t = (it[0] or "") if len(it) > 0 else ""
            d = (it[1] or "") if len(it) > 1 else ""
            u = (it[2] or "") if len(it) > 2 else ""
        if t or d or u:
            rows.append((t, d, (u or None)))
    p["projects"] = rows

    # education
    edu = p.get("education")
    if edu is None:
        p["education"] = []
    elif isinstance(edu, (list, tuple)):
        p["education"] = [str(x).strip() for x in edu if str(x).strip()]
    else:
        p["education"] = [str(edu).strip()] if str(edu).strip() else []

    # optional contact normalization (keep as-is if already dict)
    if not isinstance(p.get("contact"), dict):
        p["contact"] = {}

    # header passthrough
    if not isinstance(p.get("header"), dict):
        p["header"] = {}

    return p
