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

import re

_AR_RE = re.compile(r"[\u0600-\u06FF]")

def _is_arabic(s: str) -> bool:
    return bool(_AR_RE.search(s or ""))

from reportlab.pdfbase import pdfmetrics

def _pick_line_font(st, prefer_ar="NotoNaskhArabic", prefer_lat="DejaVuSans"):
    regs = set(pdfmetrics.getRegisteredFontNames())
    ar = prefer_ar if prefer_ar in regs else (st["font"] if st["font"] in regs else "Helvetica")
    la = prefer_lat if prefer_lat in regs else (st["font"] if st["font"] in regs else "Helvetica")
    return ar, la


# ========== RTL / Arabic Support ==========
try:
    import arabic_reshaper  # type: ignore
    from bidi.algorithm import get_display  # type: ignore

    def _rtl_process(s: str) -> str:
        if not s:
            return ""
        reshaped = arabic_reshaper.reshape(s)
        return get_display(reshaped)

except Exception:

    def _rtl_process(s: str) -> str:
        return s or ""


# ========== Font helpers (safety) ==========

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


# ========== Helpers ==========
def _block_name_arg(b: Any) -> Tuple[str, Optional[str]]:
    """
    Robustly parse a block entry. Accepts:
      - "header_name"
      - "text_section:summary"
      - {"block_id": "header_name", "arg": "summary"}  # optional arg
      - {"name": "header_name"}
    Returns: (name, arg) or ("", None) if not resolvable.
    """
    if isinstance(b, dict):
        name = (b.get("block_id") or b.get("name") or "").strip()
        arg = b.get("arg")
        if isinstance(arg, str):
            arg = arg.strip() or None
        else:
            arg = None
        return name, arg

    bs = str(b).strip()
    if not bs:
        return "", None
    if ":" in bs:
        name, arg = bs.split(":", 1)
        return name.strip(), (arg.strip() or None)
    return bs, None


def _normalize_blocks_list(blocks: Any) -> List[Any]:
    """
    Ensure blocks is a list; keep original items (string or dict).
    We don't coerce to strings here—just guarantee it's a list.
    """
    if blocks is None:
        return []
    if isinstance(blocks, list):
        return blocks
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
    words = str(text).split()
    lines: List[str] = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if c.stringWidth(test, font, size) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


def _draw_paragraph(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    text: str,
    leading: float,
    font: str = "Helvetica",
    size: int = 10,
    rtl: bool = False,
) -> float:
    if not text:
        return y

    ar_font, la_font = _pick_line_font(st={"font": font})

    for raw in str(text).splitlines():
        is_ar = _is_arabic(raw)

        render = _rtl_process(raw) if (rtl and is_ar) else raw

        line_font = ar_font if is_ar else la_font

        lines = _wrap_text(c, render, w, line_font, size)

        for ln in lines:
            _safe_set_font(c, line_font, size)
            if rtl and is_ar:
                c.drawRightString(x + w, y, ln)
            else:
                c.drawString(x, y, ln)
            y -= leading

    return y



def _pct_to_w(pct: Any, full_w: float) -> float:
    s = str(pct or "").strip()
    if s.endswith("%"):
        try:
            return full_w * (float(s[:-1]) / 100.0)
        except Exception:
            return full_w
    try:
        return float(s)
    except Exception:
        return full_w


def _deep_update(target: dict, source: dict) -> dict:
    if not isinstance(target, dict) or not isinstance(source, dict):
        return target
    for k, v in source.items():
        if isinstance(v, dict) and isinstance(target.get(k), dict):
            _deep_update(target[k], v)
        else:
            target[k] = v
    return target


# ========== Theme Loader ==========

def _load_theme_from_disk(theme_name: Optional[str]) -> dict:
    if not theme_name:
        return {}
    root = Path(__file__).resolve().parents[2]
    path = root / "themes" / f"{theme_name}.theme.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


# ========== Blocks ==========

def _block_header_name(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    profile: Dict[str, Any],
    st: Dict[str, Any],
    rtl: bool,
) -> float:
    head = profile.get("header") or {}
    name = head.get("name", "")
    title = head.get("title", "")
    c.setFillColor(st["primary"])
    _safe_set_font(c, st["font_head"], st["sizes"]["h1"])
    if name:
        (c.drawRightString if rtl else c.drawString)(x + (w if rtl else 0), y, name)
        y -= st["sizes"]["lead_h1"]
    c.setFillColor(st["text"])
    _safe_set_font(c, st["font_bold"], st["sizes"]["h2"])
    if title:
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
    links = [v for k, v in contact.items() if k in ("github", "linkedin", "website") and v]
    if not links:
        return y
    _safe_set_font(c, st["font_bold"], st["sizes"]["h3"])
    (c.drawRightString if rtl else c.drawString)(x + (w if rtl else 0), y, "Social")
    y -= st["sizes"]["lead_h3"]
    for link in links:
        y = _draw_paragraph(
            c, x, y, w, f"• {link}", st["sizes"]["lead_body"], st["font"], st["sizes"]["body"], rtl
        )
    return y - st["sp_after_list"]


def _block_key_skills(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    profile: Dict[str, Any],
    st: Dict[str, Any],
    rtl: bool,
) -> float:
    skills = _text_to_lines(profile.get("skills"))
    if not skills:
        return y
    _safe_set_font(c, st["font_bold"], st["sizes"]["h3"])
    (c.drawRightString if rtl else c.drawString)(x + (w if rtl else 0), y, "Key Skills")
    y -= st["sizes"]["lead_h3"]
    for s in skills:
        y = _draw_paragraph(
            c, x, y, w, f"• {s}", st["sizes"]["lead_body"], st["font"], st["sizes"]["body"], rtl
        )
    return y - st["sp_after_list"]


def _block_languages(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    profile: Dict[str, Any],
    st: Dict[str, Any],
    rtl: bool,
) -> float:
    langs = _text_to_lines(profile.get("languages"))
    if not langs:
        return y
    _safe_set_font(c, st["font_bold"], st["sizes"]["h3"])
    (c.drawRightString if rtl else c.drawString)(x + (w if rtl else 0), y, "Languages")
    y -= st["sizes"]["lead_h3"]
    for s in langs:
        y = _draw_paragraph(
            c, x, y, w, f"• {s}", st["sizes"]["lead_body"], st["font"], st["sizes"]["body"], rtl
        )
    return y - st["sp_after_list"]


def _block_projects(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    profile: Dict[str, Any],
    st: Dict[str, Any],
    rtl: bool,
) -> float:
    projects = _projects_to_rows(profile.get("projects"))
    if not projects:
        return y
    _safe_set_font(c, st["font_bold"], st["sizes"]["h3"])
    (c.drawRightString if rtl else c.drawString)(x + (w if rtl else 0), y, "Projects")
    y -= st["sizes"]["lead_h3"]
    for (title, desc, url) in projects:
        main = title
        if desc:
            main += f" — {desc}"
        if url:
            main += f" ({url})"
        y = _draw_paragraph(
            c, x, y, w, f"• {main}", st["sizes"]["lead_body"], st["font"], st["sizes"]["body"], rtl
        )
    return y - st["sp_after_list"]


def _block_education(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    profile: Dict[str, Any],
    st: Dict[str, Any],
    rtl: bool,
) -> float:
    edu = _text_to_lines(profile.get("education"))
    if not edu:
        return y
    _safe_set_font(c, st["font_bold"], st["sizes"]["h3"])
    (c.drawRightString if rtl else c.drawString)(x + (w if rtl else 0), y, "Education")
    y -= st["sizes"]["lead_h3"]
    for s in edu:
        y = _draw_paragraph(
            c, x, y, w, f"• {s}", st["sizes"]["lead_body"], st["font"], st["sizes"]["body"], rtl
        )
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
    c.setFillColor(HexColor(bg))
    c.rect(x - pad, 0, w + pad * 2, page_h, stroke=0, fill=1)
    c.setFillColor(st["text"])


BLOCKS: Dict[str, Callable] = {
    "header_name": _block_header_name,
    "contact_info": _block_contact_info,
    "social_links": _block_social_links,
    "key_skills": _block_key_skills,
    "languages": _block_languages,
    "projects": _block_projects,
    "education": _block_education,
}


# ========== Main Builder ==========

# ✅ طبّع بيانات الـprofile قبل أي استخدام لها
try:
    from api.pdf_utils.schema import ensure_profile_schema  # optional but recommended
except Exception:
    def ensure_profile_schema(x: Dict[str, Any]) -> Dict[str, Any]:
        return x

def build_resume_pdf(*, data: Dict[str, Any]) -> bytes:
    profile = ensure_profile_schema(data.get("profile") or {})
    layout = data.get("layout_inline") or {}
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
        margins["left"] * mm,
        margins["right"] * mm,
        margins["top"] * mm,
        margins["bottom"] * mm,
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

        # ✅ طَبّق التطبيع على blocks ثم تعامل مع left_panel_bg سواء كان نص أو dict
        blocks = _normalize_blocks_list(sec.get("blocks") or [])

        def _is_left_bg(entry: Any) -> bool:
            nm, _ = _block_name_arg(entry)
            return nm == "left_panel_bg"

        if any(_is_left_bg(b) for b in blocks):
            over = layout.get("overrides", {}).get("left_panel_bg", {}).get("data", {})
            _block_left_panel_bg(
                c,
                x,
                y_pos[cid],
                w,
                ph,
                st,
                pad_mm=over.get("pad_mm", 6),
                bg=over.get("bg", "#F8FAFC"),
            )
            blocks = [b for b in blocks if not _is_left_bg(b)]

        y = y_pos[cid]
        for b in blocks:
            ensure_space(cid, 80)
            name, arg = _block_name_arg(b)  # ✅ آمن مع dict أو string
            if not name:
                continue

            if name == "text_section":
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
