from __future__ import annotations
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors
from reportlab.lib.units import mm

from ..config import UI_LANG
from .base import Frame, RenderContext
from .registry import register

class SkillsGrid:
    BLOCK_ID = "skills_grid"
    """
    شبكة مهارات بسيطة (قائمة نقطية موزعة على أعمدة).
    data:
      - items أو skills : list[str]
      - columns         : 2/3 (افتراضي 2)
      - title           : عنوان اختياري
      - row_h_mm        : ارتفاع السطر (افتراضي 6)
    """

    def render(self, c: Canvas, frame: Frame, data: dict, ctx: RenderContext) -> float:
        items = [str(s).strip() for s in (data.get("items") or data.get("skills") or []) if str(s).strip()]
        cols = max(1, int(data.get("columns", 2)))
        title = (data.get("title") or "").strip()
        row_h = float(data.get("row_h_mm", 6)) * mm

        cur_y = frame.y

        # عنوان اختياري
        if title:
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(frame.x, cur_y - 5 * mm, title)
            cur_y -= 10 * mm

        if not items:
            return cur_y

        col_w = frame.w / cols
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)

        rows = (len(items) + cols - 1) // cols
        idx = 0
        for _ in range(rows):
            for cidx in range(cols):
                if idx >= len(items):
                    break
                cx = frame.x + cidx * col_w
                c.drawString(cx, cur_y - 4 * mm, f"• {items[idx]}")
                idx += 1
            cur_y -= row_h

        return cur_y - (4 * mm)

register(SkillsGrid())


