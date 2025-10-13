# api/pdf_utils/layout.py
from __future__ import annotations
from typing import Dict, Any, List
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from .blocks.base import Frame, RenderContext
from .blocks.registry import get as get_block
from .config import UI_LANG

def _page_size_points(size: str, orientation: str):
    if size.upper() == "A4":
        w, h = 595.2756, 841.8898
    else:
        w, h = 595.2756, 841.8898
    if orientation.lower() == "landscape":
        w, h = h, w
    return w, h

def _parse_pct_or_abs(value: str, total: float) -> float:
    v = str(value).strip()
    if v.endswith("%"):
        return float(v[:-1]) / 100.0 * total
    return float(v)

def compute_columns(layout: Dict[str, Any]) -> Dict[str, Any]:
    page = layout.get("page", {})
    size = page.get("size", "A4")
    orient = page.get("orientation", "portrait")
    margin = page.get("margin_mm", {"top": 22, "right": 18, "bottom": 18, "left": 18})
    gutter_mm = float(page.get("gutter_mm", 6))

    page_w, page_h = _page_size_points(size, orient)
    m_top = margin.get("top", 22) * mm
    m_right = margin.get("right", 18) * mm
    m_bottom = margin.get("bottom", 18) * mm
    m_left = margin.get("left", 18) * mm

    content_w = page_w - m_left - m_right
    content_h = page_h - m_top - m_bottom

    cols_def: List[Dict[str, Any]] = layout.get("columns", []) or [{"id": "main", "width": "100%"}]
    columns: List[Dict[str, Any]] = []
    x_cursor = m_left
    for c in cols_def:
        cid = c.get("id") or f"col_{len(columns)+1}"
        w = c.get("w")
        x = c.get("x")
        width = float(w) if w is not None else _parse_pct_or_abs(c.get("width", "100%"), content_w)
        columns.append({"id": cid, "x": float(x) if x is not None else x_cursor, "y": page_h - m_top, "w": width})
        x_cursor += width + gutter_mm * mm

    return {
        "page_w": page_w,
        "page_h": page_h,
        "margins": (m_top, m_right, m_bottom, m_left),
        "columns": columns,
        "content_w": content_w,
        "content_h": content_h,
    }

def render_with_layout(c: Canvas, layout: Dict[str, Any], data_map: Dict[str, Any], ui_lang: str | None = None):
    geom = compute_columns(layout)
    flow = layout.get("flow", [])
    overrides = layout.get("overrides", {})

    ctx: RenderContext = {
        "ui_lang": ui_lang or UI_LANG,
        "rtl_mode": (ui_lang or UI_LANG) == "ar",
        "page_h": geom["page_h"],
        "page_top_y": geom["page_h"] - geom["margins"][1],
    }

    for group in flow:
        col_id = group.get("column", "main")
        col = next((co for co in geom["columns"] if co["id"] == col_id), None)
        if not col:
            continue
        frame = Frame(x=col["x"], y=col["y"], w=col["w"])
        for block_id in group.get("blocks", []):
            bid, _, suffix = block_id.partition(":")
            block = get_block(bid)
            base_data = data_map.get(block_id) or data_map.get(bid) or {}
            ov = (overrides.get(block_id) or overrides.get(bid) or {}).get("data") or {}
            merged = {**base_data, **ov}
            new_y = block.render(c, frame, merged, ctx)
            frame = Frame(x=frame.x, y=new_y, w=frame.w)
