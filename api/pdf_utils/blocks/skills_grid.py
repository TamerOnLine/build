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
    ط´ط¨ظƒط© ظ…ظ‡ط§ط±ط§طھ ط¨ط³ظٹط·ط© (ظ‚ط§ط¦ظ…ط© ظ†ظ‚ط·ظٹط© ظ…ظˆط²ط¹ط© ط¹ظ„ظ‰ ط£ط¹ظ…ط¯ط©).
    data:
      - items ط£ظˆ skills : list[str]
      - columns         : 2/3 (ط§ظپطھط±ط§ط¶ظٹ 2)
      - title           : ط¹ظ†ظˆط§ظ† ط§ط®طھظٹط§ط±ظٹ
      - row_h_mm        : ط§ط±طھظپط§ط¹ ط§ظ„ط³ط·ط± (ط§ظپطھط±ط§ط¶ظٹ 6)
    """

    def render(self, c: Canvas, frame: Frame, data: dict, ctx: RenderContext) -> float:
        items = [str(s).strip() for s in (data.get("items") or data.get("skills") or []) if str(s).strip()]
        cols = max(1, int(data.get("columns", 2)))
        title = (data.get("title") or "").strip()
        row_h = float(data.get("row_h_mm", 6)) * mm

        cur_y = frame.y

        # ط¹ظ†ظˆط§ظ† ط§ط®طھظٹط§ط±ظٹ
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
                c.drawString(cx, cur_y - 4 * mm, f"â€¢ {items[idx]}")
                idx += 1
            cur_y -= row_h

        return cur_y - (4 * mm)

register(SkillsGrid())

