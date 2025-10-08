# api/pdf_utils/text.py
"""
Shim layer to keep old blocks working.
Provides wrap_text / draw_paragraph / draw_par aliases + helpers.
Handles RTL via api.pdf_utils.rtl.rtl when requested.
"""

from typing import List, Any
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from api.pdf_utils.rtl import rtl as _rtl_unified  # unified RTL

# ---------- core word-wrap ----------
def wrap_text(
    c: canvas.Canvas,
    text: str,
    max_w: float,
    font: str = "Helvetica",
    size: int = 10,
) -> List[str]:
    c.setFont(font, size)
    words = str(text or "").split()
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

# ---------- paragraph drawing ----------
def draw_paragraph(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    text: str,
    leading: float,
    font: str = "Helvetica",
    size: int = 10,
    is_rtl: bool = False,
) -> float:
    if not text:
        return y
    raw = str(text)
    if is_rtl:
        raw = _rtl_unified(raw)
    lines = wrap_text(c, raw, w, font, size)
    for ln in lines:
        if is_rtl:
            c.drawRightString(x + w, y, ln)
        else:
            c.drawString(x, y, ln)
        y -= leading
    return y

# ---------- aliases expected by legacy blocks ----------
def draw_par(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    text: str,
    leading: float,
    font: str = "Helvetica",
    size: int = 10,
    is_rtl: bool = False,
) -> float:
    """Alias for draw_paragraph (legacy blocks import draw_par)."""
    return draw_paragraph(c, x, y, w, text, leading, font, size, is_rtl)

# some blocks might import pct_to_w; provide both names
def pct_to_width(val: Any, full_w: float) -> float:
    s = str(val or "").strip()
    if s.endswith("%"):
        try:
            return full_w * (float(s[:-1]) / 100.0)
        except Exception:
            return full_w
    try:
        return float(s)
    except Exception:
        return full_w

def pct_to_w(val: Any, full_w: float) -> float:
    """Alias for pct_to_width."""
    return pct_to_width(val, full_w)

def deep_update(target: dict, source: dict) -> dict:
    if not isinstance(target, dict) or not isinstance(source, dict):
        return target
    for k, v in source.items():
        if isinstance(v, dict) and isinstance(target.get(k), dict):
            deep_update(target[k], v)
        else:
            target[k] = v
    return target

def hex_color(s: str):
    return HexColor(s)

__all__ = [
    "wrap_text",
    "draw_paragraph",
    "draw_par",       # alias
    "pct_to_width",
    "pct_to_w",      # alias
    "deep_update",
    "hex_color",
]

