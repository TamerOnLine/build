# api/pdf_utils/blocks/left_panel_bg.py
from __future__ import annotations
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from .base import Frame, RenderContext
from .registry import register
from ..config import LEFT_BG, LEFT_BORDER

class LeftPanelBG:
    """
    ظٹط±ط³ظ… ط®ظ„ظپظٹط© ط§ظ„ط¹ظ…ظˆط¯ ط§ظ„ط£ظٹط³ط± ظ…ظ…طھط¯ط© ظ…ظ† ط£ط¹ظ„ظ‰ ط§ظ„طµظپط­ط© ط¥ظ„ظ‰ ط£ط³ظپظ„ظ‡ط§ ط¶ظ…ظ† ط¹ط±ط¶ ط§ظ„ط¹ظ…ظˆط¯.
    data:
      - pad_mm : ظ‡ط§ظ…ط´ ط¯ط§ط®ظ„ظٹ ط¨ط³ظٹط· (ط§ظپطھط±ط§ط¶ظٹ 4)
      - bg     : ظ„ظˆظ† ط§ظ„ط®ظ„ظپظٹط© (ط¥ظ„ط§ ط¥ط°ط§ ط¹ظڈط±ظ‘ظگظپ LEFT_BG ظپظٹ config)
      - border : ظ„ظˆظ† ط§ظ„ط­ط¯ظˆط¯ (ط§ط®طھظٹط§ط±ظٹط› ظٹط¹طھظ…ط¯ LEFT_BORDER ط¥ظ† ظˆط¬ط¯)
    """
    BLOCK_ID = "left_panel_bg"

    def render(self, c: Canvas, frame: Frame, data: dict, ctx: RenderContext) -> float:
        # ط§ظ„ط¥ط¹ط¯ط§ط¯ط§طھ
        pad_mm  = float((data or {}).get("pad_mm") or 4.0)
        pad     = pad_mm * mm
        bg_hex  = (data or {}).get("bg") or LEFT_BG or "#F7F8FA"
        br_hex  = (data or {}).get("border") or LEFT_BORDER  # ظ‚ط¯ ظٹظƒظˆظ† None

        # ط£ط¨ط¹ط§ط¯ ط§ظ„ط±ط³ظ…
        x      = frame.x
        w      = frame.w
        top_y  = frame.y
        page_h = float(ctx.get("page_h") or (297 * mm))  # A4 fallback
        h      = max(0.0, page_h - (2 * pad))

        # ط§ظ„ط±ط³ظ…
        c.saveState()
        try:
            c.setFillColor(colors.HexColor(bg_hex))
        except Exception:
            c.setFillColor(colors.HexColor("#F7F8FA"))

        # ط§ط³طھط®ط¯ظ… roundRect ظ…ظ† ReportLab ظ…ط¨ط§ط´ط±ط© ظ„طھط¬ظ†ط¨ ط§ط®طھظ„ط§ظپ طھظˆط§ظ‚ظٹط¹ util
        # ظ…ظ„ط§ط­ط¸ط©: radius ط¨ظˆط­ط¯ط§طھ ط§ظ„ظ†ظ‚ط§ط· (ظ„ظٹط³ mm)
        radius = 6  # ظ†ظ‚ط§ط·
        c.roundRect(x, top_y - h, w, h, radius, stroke=0, fill=1)

        # ط®ط· ط­ط¯ظˆط¯ ط§ط®طھظٹط§ط±ظٹ
        if br_hex:
            try:
                c.setStrokeColor(colors.HexColor(br_hex))
            except Exception:
                c.setStrokeColor(colors.HexColor("#E3E6EA"))
            c.setLineWidth(0.6)
            # ط®ط· ط±ظپظٹط¹ ط¹ظ„ظ‰ ط­ط§ظپط© ط§ظ„ط¹ظ…ظˆط¯ ط§ظ„ظٹط³ط±ظ‰
            c.line(x, top_y - h, x, top_y)

        c.restoreState()
        # ظ„ط§ ظ†ط؛ظٹظ‘ط± Yط› ط§ظ„ط®ظ„ظپظٹط© ظپظ‚ط·
        return frame.y

# طھط³ط¬ظٹظ„ ط¨ظ†ظپط³ ط£ط³ظ„ظˆط¨ ط§ظ„ظ†ط¸ط§ظ…
register(LeftPanelBG())

